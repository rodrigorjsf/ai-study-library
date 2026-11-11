// Tipos públicos do runtime de workflows sobre o Cursor SDK.
// Espelha a superfície do Workflow do Claude Code (agent/parallel/pipeline/phase/log/args/budget),
// mas roda como processo Node comum: o "script" é um módulo TypeScript que exporta defineWorkflow(...).
//
// STATUS: código de referência. Typecheck feito contra @cursor/sdk@1.3.1; não executado contra a API real.

import type { AgentDefinition, McpServerConfig, ModelSelection, ToolName } from "@cursor/sdk";

/** JSON Schema (subconjunto aceito pelo Ajv). */
export type JsonSchema = Record<string, unknown>;

export interface WorkflowPhase {
  title: string;
  detail?: string;
}

export interface WorkflowMeta {
  /** Nome estável; vira o nome do comando (CLI) e da tool (MCP). */
  name: string;
  /** Uma linha. Aparece na listagem do MCP e no `--help` do CLI. */
  description: string;
  /** Quando usar — texto para o agente do chat decidir chamar a tool. */
  whenToUse?: string;
  phases?: WorkflowPhase[];
  /** JSON Schema dos args; o runtime valida antes de rodar. */
  argsSchema?: JsonSchema;
}

export interface AgentCallOptions {
  /** Rótulo no log/progresso. */
  label?: string;
  /** Agrupa no progresso; use dentro de parallel/pipeline em vez de phase() global. */
  phase?: string;
  /**
   * Modelo desta etapa. Obrigatório para agentes locais no SDK; o runtime usa
   * `defaults.model` do workflow quando omitido.
   */
  model?: ModelSelection;
  /**
   * Com schema, o agente precisa chamar a tool `submit_result`; o retorno é o objeto validado.
   * Sem schema, o retorno é o texto final do agente.
   */
  schema?: JsonSchema;
  /** Diretório de trabalho (ex.: um git worktree criado pelo workflow). Default: cwd do run. */
  cwd?: string;
  /** Allowlist de tools nativas (ex.: ["read","grep","glob","ls"] para etapas read-only). */
  tools?: ToolName[];
  disallowedTools?: ToolName[];
  /** Subagents inline disponíveis para esta etapa (via tool `task`). */
  agents?: Record<string, AgentDefinition>;
  mcpServers?: Record<string, McpServerConfig>;
  /** Tempo máximo da etapa. Ao estourar, a run é cancelada. Default 20 min. */
  timeoutMs?: number;
  /** Tentativas extras quando a run termina em erro/cancelada. Default 1. */
  retries?: number;
  /** Re-prompts quando o agente não chama `submit_result` ou envia JSON inválido. Default 2. */
  schemaRetries?: number;
  /** Se true, falha quando o modelo efetivamente usado difere do pedido (fallback silencioso). */
  strictModel?: boolean;
}

export interface Budget {
  /** Teto em centavos cobrados (chargedCents). null = sem teto. */
  readonly maxCents: number | null;
  /** Teto de tokens totais. Útil porque uso incluído no plano reporta chargedCents = 0. */
  readonly maxTokens: number | null;
  spentCents(): number;
  spentTokens(): number;
  remainingCents(): number;
}

export interface WorkflowContext<A = unknown> {
  readonly args: A;
  readonly runId: string;
  readonly cwd: string;
  readonly budget: Budget;
  /** Executa uma etapa com um agente novo do Cursor SDK. Lança erro se falhar após as tentativas. */
  agent<T = string>(prompt: string, opts?: AgentCallOptions): Promise<T>;
  /** Barreira: roda tudo em paralelo e espera todos. Thunk que falha vira null. */
  parallel<T>(thunks: Array<() => Promise<T>>): Promise<Array<T | null>>;
  /**
   * Sem barreira: cada item atravessa os estágios de forma independente.
   * Estágio que lança erro descarta o item (null) e pula os estágios seguintes.
   */
  pipeline<I>(
    items: I[],
    ...stages: Array<(prev: any, item: I, index: number) => Promise<any> | any>
  ): Promise<any[]>;
  phase(title: string): void;
  log(message: string): void;
}

export interface WorkflowDefinition<A = unknown, R = unknown> {
  meta: WorkflowMeta;
  /** Defaults aplicados a toda chamada agent() que não sobrescrever. */
  defaults?: Pick<AgentCallOptions, "model" | "timeoutMs" | "retries" | "schemaRetries" | "tools">;
  run(ctx: WorkflowContext<A>): Promise<R>;
}

export function defineWorkflow<A = unknown, R = unknown>(def: WorkflowDefinition<A, R>): WorkflowDefinition<A, R> {
  return def;
}
