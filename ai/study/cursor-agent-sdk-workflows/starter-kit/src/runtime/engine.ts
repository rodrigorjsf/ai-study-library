// Motor do runtime: executa um WorkflowDefinition com agentes do Cursor SDK.
//
// Garantias que o motor dá (e que skills/subagents não dão):
//  - A ordem, os ramos e os laços estão no código; o modelo não decide se uma etapa roda.
//  - Cada agent() termina com resultado validado ou lança erro (após retries) — nada é "pulado" em silêncio.
//  - Modelo por etapa. O SDK valida o ID contra o catálogo da conta antes da run ("Cannot use this model")
//    e a etapa falha; substituição feita do lado do servidor (política do admin) NÃO é detectável pelo SDK.
//  - Teto de custo/tokens por run; RateLimitError não retentável (teto da conta) aborta com mensagem clara.
//  - Journal para retomar sem repetir etapas concluídas.
//
// STATUS: código de referência. Typecheck contra @cursor/sdk@1.3.1; não executado contra a API real.

import { randomUUID } from "node:crypto";
import { join } from "node:path";
import { Agent, AgentBusyError, RateLimitError, type Run, type RunResult, type SDKAgent, type SettingSource } from "@cursor/sdk";
import { Ajv } from "ajv";
import { Journal } from "./journal.js";
import { type Capture, SUBMIT_TOOL, repromptMessage, schemaInstruction, submitResultTool } from "./structured.js";
import type { AgentCallOptions, Budget, WorkflowContext, WorkflowDefinition } from "./workflow.js";

export class BudgetExceededError extends Error {}
export class StepFailedError extends Error {}

/** Marca o ambiente: MCP servers iniciados pelos agentes das etapas herdam e recusam start_workflow. */
export const INSIDE_WORKFLOW_ENV = "WF_INSIDE_WORKFLOW";

export interface RunOptions {
  /** Diretório do repositório onde os agentes trabalham. */
  cwd: string;
  /** Chave do usuário (ou service account). Se omitida, o SDK usa CURSOR_API_KEY e depois o login salvo. */
  apiKey?: string;
  /** Id do run. Para retomar, passe o id de um run anterior (o journal evita repetir etapas concluídas). */
  runId?: string;
  maxCents?: number | null;
  maxTokens?: number | null;
  /** Agentes simultâneos. Default 4 (o Cursor não documenta limite numérico; seja conservador). */
  concurrency?: number;
  /**
   * Camadas de configuração carregadas pelos agentes das etapas. Default ["project","team","mdm"]:
   * AGENTS.md, .cursor/rules, skills (.agents/skills, .cursor/skills, ...), hooks e MCP do projeto,
   * mais regras/hooks do time e hooks Enterprise (MDM). Remova "project" em repositórios não confiáveis.
   */
  settingSources?: SettingSource[];
  /** Onde ficam journal e estado. Default <cwd>/.workflows/runs. */
  stateDir?: string;
  onEvent?: (e: WorkflowEvent) => void;
}

export type WorkflowEvent =
  | { type: "log"; message: string }
  | { type: "phase"; title: string }
  | { type: "step-start"; label: string; phase?: string; model?: string; attempt: number }
  | { type: "step-end"; label: string; ok: boolean; cached: boolean; chargedCents: number; model?: string }
  | { type: "warning"; message: string };

export interface RunOutcome<R> {
  runId: string;
  status: "finished" | "failed";
  result?: R;
  error?: string;
  spentCents: number;
  spentTokens: number;
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));
const ajv = new Ajv({ allErrors: true, strict: false });

export function newRunId(workflow: string): string {
  return `${workflow}-${randomUUID().slice(0, 8)}`;
}

class Semaphore {
  private active = 0;
  private readonly queue: Array<() => void> = [];
  constructor(private readonly limit: number) {}
  async acquire(): Promise<void> {
    if (this.active < this.limit) {
      this.active++;
      return;
    }
    // O slot é entregue diretamente pelo release(): `active` não cai e sobe de novo.
    await new Promise<void>((resolve) => this.queue.push(resolve));
  }
  release(): void {
    const next = this.queue.shift();
    if (next) next();
    else this.active--;
  }
}

export async function runWorkflow<A, R>(
  def: WorkflowDefinition<A, R>,
  args: A,
  opts: RunOptions,
): Promise<RunOutcome<R>> {
  const runId = opts.runId ?? newRunId(def.meta.name);
  let spentCents = 0;
  let spentTokens = 0;

  if (def.meta.argsSchema) {
    const validate = ajv.compile(def.meta.argsSchema);
    if (!validate(args)) {
      return { runId, status: "failed", error: `args inválidos: ${ajv.errorsText(validate.errors)}`, spentCents, spentTokens };
    }
  }

  process.env[INSIDE_WORKFLOW_ENV] = "1";
  const stateDir = opts.stateDir ?? join(opts.cwd, ".workflows", "runs");
  const journal = new Journal(join(stateDir, runId, "journal.jsonl"));
  const sem = new Semaphore(opts.concurrency ?? 4);
  const emit = opts.onEvent ?? (() => {});
  const settingSources = opts.settingSources ?? ["project", "team", "mdm"];
  let currentPhase: string | undefined;

  const budget: Budget = {
    maxCents: opts.maxCents ?? null,
    maxTokens: opts.maxTokens ?? null,
    spentCents: () => spentCents,
    spentTokens: () => spentTokens,
    remainingCents: () => (opts.maxCents == null ? Infinity : Math.max(0, opts.maxCents - spentCents)),
  };

  function assertBudget(): void {
    if (budget.maxCents != null && spentCents >= budget.maxCents) {
      throw new BudgetExceededError(`Teto de custo atingido: ${spentCents}¢ de ${budget.maxCents}¢.`);
    }
    if (budget.maxTokens != null && spentTokens >= budget.maxTokens) {
      throw new BudgetExceededError(`Teto de tokens atingido: ${spentTokens} de ${budget.maxTokens}.`);
    }
  }

  /** Lê custo do agente. O custo "pode atrasar um pouco depois do fim da run": tenta de novo se vier vazio. */
  async function chargeUsage(agent: SDKAgent): Promise<number> {
    for (let i = 0; i < 3; i++) {
      const usage = await agent.getUsage().catch(() => undefined);
      if (usage?.cost || i === 2) {
        const charged = usage?.cost?.chargedCents ?? 0;
        spentCents += charged;
        spentTokens += usage?.usage.totalTokens ?? 0;
        return charged;
      }
      await sleep(1000);
    }
    return 0;
  }

  /** send() com tolerância a AgentBusyError (a run anterior ainda fechando). */
  async function send(agent: SDKAgent, message: string): Promise<Run> {
    for (let i = 0; ; i++) {
      try {
        return await agent.send(message);
      } catch (err) {
        if (err instanceof AgentBusyError && i < 5) {
          await sleep(1000 * (i + 1));
          continue;
        }
        throw err;
      }
    }
  }

  async function waitWithTimeout(run: Run, ms: number): Promise<RunResult> {
    let timer: NodeJS.Timeout | undefined;
    let timedOut = false;
    const timeout = new Promise<never>((_, reject) => {
      timer = setTimeout(() => {
        timedOut = true;
        reject(new StepFailedError(`timeout após ${ms} ms`));
      }, ms);
    });
    try {
      return await Promise.race([run.wait(), timeout]);
    } finally {
      clearTimeout(timer);
      // Espera o cancelamento terminar para a próxima tentativa não editar o mesmo cwd em paralelo.
      if (timedOut) await run.cancel().catch(() => {});
    }
  }

  async function agentCall<T>(prompt: string, callOpts: AgentCallOptions = {}): Promise<T> {
    const o: AgentCallOptions = { ...def.defaults, ...callOpts };
    const label = o.label ?? prompt.slice(0, 48);
    // Chave calculada de forma síncrona, antes de qualquer await.
    const key = journal.keyFor(prompt, {
      model: o.model,
      schema: o.schema,
      cwd: o.cwd,
      tools: o.tools,
      disallowedTools: o.disallowedTools,
      agents: o.agents,
    });
    const cached = journal.get(key);
    if (cached) {
      emit({ type: "step-end", label, ok: true, cached: true, chargedCents: 0, model: cached.model });
      return cached.result as T;
    }
    if (!o.model) throw new StepFailedError(`etapa "${label}" sem modelo: defina opts.model ou defaults.model`);
    if (o.schema && o.schema.type !== "object") {
      throw new StepFailedError(`etapa "${label}": schema precisa ter type "object" na raiz (vira o inputSchema de uma tool)`);
    }

    await sem.acquire();
    try {
      const attempts = 1 + (o.retries ?? 1);
      let lastError = "";
      for (let attempt = 1; attempt <= attempts; attempt++) {
        assertBudget();
        emit({ type: "step-start", label, phase: o.phase ?? currentPhase, model: o.model.id, attempt });
        const capture: Capture = { value: undefined, submitted: false };
        let agent: SDKAgent | undefined;
        let charged = 0;
        try {
          agent = await Agent.create({
            apiKey: opts.apiKey,
            name: `${def.meta.name}:${label}`,
            model: o.model,
            // Custom tools chegam ao modelo como o MCP server `custom-user-tools`: uma allowlist
            // sem "mcp" esconderia o submit_result.
            tools: o.schema && o.tools && !o.tools.includes("mcp") ? [...o.tools, "mcp"] : o.tools,
            disallowedTools: o.disallowedTools,
            agents: o.agents,
            mcpServers: o.mcpServers,
            local: {
              cwd: o.cwd ?? opts.cwd,
              settingSources,
              sandboxOptions: o.sandbox ? { enabled: true } : undefined,
              customTools: o.schema ? { [SUBMIT_TOOL]: submitResultTool(o.schema, capture) } : undefined,
            },
          });
          let result = await waitWithTimeout(await send(agent, o.schema ? prompt + schemaInstruction() : prompt), o.timeoutMs ?? 20 * 60_000);
          // Saída estruturada: re-prompt na MESMA conversa até o modelo chamar submit_result com JSON válido.
          let schemaTries = o.schemaRetries ?? 2;
          while (o.schema && result.status === "finished" && !capture.submitted && schemaTries-- > 0) {
            result = await waitWithTimeout(await send(agent, repromptMessage(capture)), o.timeoutMs ?? 20 * 60_000);
          }
          charged = await chargeUsage(agent);

          if (result.status !== "finished") {
            lastError = `run ${result.status}: ${result.error?.message ?? "sem detalhe"}`;
          } else if (o.schema && !capture.submitted) {
            lastError = `agente não entregou ${SUBMIT_TOOL} válido (${capture.lastError ?? "nenhuma chamada"})`;
          } else {
            const value = o.schema ? capture.value : (result.result ?? "");
            journal.record({ key, label, model: o.model.id, result: value, chargedCents: charged, totalTokens: 0 });
            emit({ type: "step-end", label, ok: true, cached: false, chargedCents: charged, model: o.model.id });
            return value as T;
          }
        } catch (err) {
          if (agent && charged === 0) charged = await chargeUsage(agent); // timeout/erro também custam
          if (err instanceof RateLimitError) {
            // Não retentável = teto de uso da conta/time: não adianta tentar de novo.
            if (!err.isRetryable) throw new BudgetExceededError(`Limite de uso do Cursor atingido: ${err.message}`);
            await sleep(2000 * 2 ** (attempt - 1));
          }
          lastError = err instanceof Error ? err.message : String(err);
        } finally {
          if (agent) await agent[Symbol.asyncDispose]().catch(() => {});
        }
        emit({ type: "step-end", label, ok: false, cached: false, chargedCents: charged, model: o.model.id });
      }
      throw new StepFailedError(`etapa "${label}" falhou após ${attempts} tentativa(s): ${lastError}`);
    } finally {
      sem.release();
    }
  }

  const ctx: WorkflowContext<A> = {
    args,
    runId,
    cwd: opts.cwd,
    budget,
    agent: agentCall,
    async parallel(thunks) {
      return Promise.all(
        thunks.map((t) =>
          t().catch((err: unknown) => {
            if (err instanceof BudgetExceededError) throw err; // teto de custo aborta o workflow inteiro
            emit({ type: "warning", message: `parallel: ${err instanceof Error ? err.message : String(err)}` });
            return null;
          }),
        ),
      );
    },
    async pipeline(items, ...stages) {
      return Promise.all(
        items.map(async (item, index) => {
          let prev: unknown = item;
          try {
            for (const stage of stages) prev = await stage(prev, item, index);
            return prev;
          } catch (err) {
            if (err instanceof BudgetExceededError) throw err;
            emit({ type: "warning", message: `pipeline item ${index}: ${err instanceof Error ? err.message : String(err)}` });
            return null;
          }
        }),
      );
    },
    phase(title) {
      currentPhase = title;
      emit({ type: "phase", title });
    },
    log(message) {
      emit({ type: "log", message });
    },
  };

  try {
    const result = await def.run(ctx);
    return { runId, status: "finished", result, spentCents, spentTokens };
  } catch (err) {
    return { runId, status: "failed", error: err instanceof Error ? err.message : String(err), spentCents, spentTokens };
  }
}
