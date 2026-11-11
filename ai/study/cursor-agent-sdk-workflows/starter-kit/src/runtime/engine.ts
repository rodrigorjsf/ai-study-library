// Motor do runtime: executa um WorkflowDefinition com agentes do Cursor SDK.
//
// Garantias que o motor dá (e que skills/subagents não dão):
//  - A ordem, os ramos e os laços estão no código; o modelo não decide se uma etapa roda.
//  - Cada agent() termina com resultado validado ou lança erro (após retries) — nada é "pulado" em silêncio.
//  - Modelo por etapa, com verificação do modelo efetivamente usado (RunResult.model).
//  - Teto de custo/tokens por run; RateLimitError (inclui teto mensal da conta) aborta com mensagem clara.
//  - Journal para retomar sem repetir etapas concluídas.
//
// STATUS: código de referência. Typecheck contra @cursor/sdk@1.3.1; não executado contra a API real.

import { randomUUID } from "node:crypto";
import { join } from "node:path";
import { Agent, RateLimitError, type SDKAgent, type RunResult } from "@cursor/sdk";
import { Journal } from "./journal.js";
import { type Capture, SUBMIT_TOOL, repromptMessage, schemaInstruction, submitResultTool } from "./structured.js";
import type { AgentCallOptions, Budget, WorkflowContext, WorkflowDefinition } from "./workflow.js";

export class BudgetExceededError extends Error {}
export class StepFailedError extends Error {}

export interface RunOptions {
  /** Diretório do repositório onde os agentes trabalham. */
  cwd: string;
  /** Chave do usuário (ou service account). Se omitida, o SDK usa CURSOR_API_KEY e depois o login salvo. */
  apiKey?: string;
  /** Reaproveita o journal de um run anterior. */
  resumeRunId?: string;
  maxCents?: number | null;
  maxTokens?: number | null;
  /** Agentes simultâneos. Default 4 (o Cursor não documenta limite numérico; seja conservador). */
  concurrency?: number;
  /** Onde ficam journal e estado. Default <cwd>/.workflows/runs. */
  stateDir?: string;
  onEvent?: (e: WorkflowEvent) => void;
}

export type WorkflowEvent =
  | { type: "log"; message: string }
  | { type: "phase"; title: string }
  | { type: "step-start"; label: string; phase?: string; model?: string }
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

class Semaphore {
  private active = 0;
  private readonly queue: Array<() => void> = [];
  constructor(private readonly limit: number) {}
  async acquire(): Promise<void> {
    if (this.active < this.limit) {
      this.active++;
      return;
    }
    await new Promise<void>((resolve) => this.queue.push(resolve));
    this.active++;
  }
  release(): void {
    this.active--;
    this.queue.shift()?.();
  }
}

export async function runWorkflow<A, R>(
  def: WorkflowDefinition<A, R>,
  args: A,
  opts: RunOptions,
): Promise<RunOutcome<R>> {
  const runId = opts.resumeRunId ?? `${def.meta.name}-${randomUUID().slice(0, 8)}`;
  const stateDir = opts.stateDir ?? join(opts.cwd, ".workflows", "runs");
  const journal = new Journal(join(stateDir, runId, "journal.jsonl"));
  const sem = new Semaphore(opts.concurrency ?? 4);
  const emit = opts.onEvent ?? (() => {});
  let currentPhase: string | undefined;
  let spentCents = 0;
  let spentTokens = 0;

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

  async function waitWithTimeout(run: Awaited<ReturnType<SDKAgent["send"]>>, ms: number): Promise<RunResult> {
    let timer: NodeJS.Timeout | undefined;
    const timeout = new Promise<never>((_, reject) => {
      timer = setTimeout(() => {
        void run.cancel().catch(() => {});
        reject(new StepFailedError(`timeout após ${ms} ms`));
      }, ms);
    });
    try {
      return await Promise.race([run.wait(), timeout]);
    } finally {
      clearTimeout(timer);
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

    await sem.acquire();
    try {
      assertBudget();
      const attempts = 1 + (o.retries ?? 1);
      let lastError = "";
      for (let attempt = 1; attempt <= attempts; attempt++) {
        emit({ type: "step-start", label, phase: o.phase ?? currentPhase, model: o.model.id });
        const capture: Capture = { value: undefined, submitted: false };
        const agent = await Agent.create({
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
            // Carrega AGENTS.md, .cursor/rules, skills e hooks do projeto (opt-in no SDK local).
            settingSources: ["project", "team"],
            customTools: o.schema ? { [SUBMIT_TOOL]: submitResultTool(o.schema, capture) } : undefined,
          },
        });
        try {
          let run = await agent.send(o.schema ? prompt + schemaInstruction() : prompt);
          let result = await waitWithTimeout(run, o.timeoutMs ?? 20 * 60_000);
          // Saída estruturada: re-prompt na MESMA conversa até o modelo chamar submit_result com JSON válido.
          let schemaTries = o.schemaRetries ?? 2;
          while (o.schema && result.status === "finished" && !capture.submitted && schemaTries-- > 0) {
            run = await agent.send(repromptMessage(capture));
            result = await waitWithTimeout(run, o.timeoutMs ?? 20 * 60_000);
          }

          const usage = await agent.getUsage().catch(() => undefined);
          const charged = usage?.cost?.chargedCents ?? 0;
          const tokens = usage?.usage.totalTokens ?? result.usage?.totalTokens ?? 0;
          spentCents += charged;
          spentTokens += tokens;

          const usedModel = result.model?.id;
          if (usedModel && usedModel !== o.model.id) {
            const msg = `etapa "${label}": pediu ${o.model.id}, rodou ${usedModel} (fallback do Cursor)`;
            if (o.strictModel) throw new StepFailedError(msg);
            emit({ type: "warning", message: msg });
          }

          if (result.status !== "finished") {
            lastError = `run ${result.status}: ${result.error?.message ?? "sem detalhe"}`;
            emit({ type: "step-end", label, ok: false, cached: false, chargedCents: charged, model: usedModel });
            continue;
          }
          if (o.schema && !capture.submitted) {
            lastError = `agente não entregou ${SUBMIT_TOOL} válido (${capture.lastError ?? "nenhuma chamada"})`;
            emit({ type: "step-end", label, ok: false, cached: false, chargedCents: charged, model: usedModel });
            continue;
          }

          const value = o.schema ? capture.value : (result.result ?? "");
          journal.record({ key, label, model: usedModel, result: value, chargedCents: charged, totalTokens: tokens });
          emit({ type: "step-end", label, ok: true, cached: false, chargedCents: charged, model: usedModel });
          return value as T;
        } catch (err) {
          if (err instanceof RateLimitError && !err.isRetryable) {
            // Inclui o teto mensal de uso da conta/time: não adianta tentar de novo.
            throw new BudgetExceededError(`Limite de uso do Cursor atingido: ${err.message}`);
          }
          if (err instanceof StepFailedError && o.strictModel) throw err;
          lastError = err instanceof Error ? err.message : String(err);
        } finally {
          agent.close();
        }
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
