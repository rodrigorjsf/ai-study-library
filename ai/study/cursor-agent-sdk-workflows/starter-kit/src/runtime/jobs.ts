// Jobs: execução assíncrona com estado em disco, para que o chat do Cursor dispare um workflow
// longo e consulte o resultado depois (MCP e shell do agente têm timeouts; um workflow de
// implementação leva minutos). CLI e MCP leem o mesmo diretório, então um job iniciado por um
// pode ser consultado pelo outro.

import { randomUUID } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { type RunOptions, type WorkflowEvent, runWorkflow } from "./engine.js";
import type { WorkflowDefinition } from "./workflow.js";

export interface JobState {
  jobId: string;
  workflow: string;
  status: "running" | "finished" | "failed";
  runId?: string;
  startedAt: string;
  finishedAt?: string;
  phase?: string;
  /** Últimos eventos, para o agente do chat mostrar progresso. */
  recent: string[];
  result?: unknown;
  error?: string;
  spentCents?: number;
  spentTokens?: number;
}

export function jobsDir(cwd: string): string {
  const dir = join(cwd, ".workflows", "jobs");
  mkdirSync(dir, { recursive: true });
  return dir;
}

export function readJob(cwd: string, jobId: string): JobState | undefined {
  const file = join(jobsDir(cwd), `${jobId}.json`);
  return existsSync(file) ? (JSON.parse(readFileSync(file, "utf8")) as JobState) : undefined;
}

export function listJobs(cwd: string): JobState[] {
  return readdirSync(jobsDir(cwd))
    .filter((f) => f.endsWith(".json"))
    .map((f) => JSON.parse(readFileSync(join(jobsDir(cwd), f), "utf8")) as JobState);
}

function writeJob(cwd: string, job: JobState): void {
  writeFileSync(join(jobsDir(cwd), `${job.jobId}.json`), JSON.stringify(job, null, 2));
}

function describe(e: WorkflowEvent): string {
  switch (e.type) {
    case "log":
      return e.message;
    case "phase":
      return `== ${e.title}`;
    case "step-start":
      return `▶ ${e.label} [${e.model ?? "?"}]`;
    case "step-end":
      return `${e.ok ? "✓" : "✗"} ${e.label}${e.cached ? " (cache)" : ""}${e.chargedCents ? ` ${e.chargedCents}¢` : ""}`;
    case "warning":
      return `⚠ ${e.message}`;
  }
}

/** Inicia o workflow no processo atual e devolve o jobId imediatamente. */
export function startJob<A>(
  def: WorkflowDefinition<A, unknown>,
  args: A,
  opts: RunOptions,
  jobId: string = randomUUID().slice(0, 8),
): { jobId: string; done: Promise<JobState> } {
  // Data/hora ficam no job, não no workflow: o script precisa ser determinístico para o resume.
  const job: JobState = { jobId, workflow: def.meta.name, status: "running", startedAt: new Date().toISOString(), recent: [] };
  writeJob(opts.cwd, job);
  const done = runWorkflow(def, args, {
    ...opts,
    onEvent: (e) => {
      if (e.type === "phase") job.phase = e.title;
      job.recent = [...job.recent, describe(e)].slice(-20);
      writeJob(opts.cwd, job);
      opts.onEvent?.(e);
    },
  }).then((outcome) => {
    Object.assign(job, {
      status: outcome.status,
      runId: outcome.runId,
      result: outcome.result,
      error: outcome.error,
      spentCents: outcome.spentCents,
      spentTokens: outcome.spentTokens,
      finishedAt: new Date().toISOString(),
    });
    writeJob(opts.cwd, job);
    return job;
  });
  return { jobId, done };
}

/** Espera até `timeoutMs` pelo fim do job; devolve o estado atual (terminado ou não). */
export async function waitJob(cwd: string, jobId: string, timeoutMs: number): Promise<JobState | undefined> {
  const deadline = Date.now() + timeoutMs;
  for (;;) {
    const job = readJob(cwd, jobId);
    if (!job || job.status !== "running" || Date.now() >= deadline) return job;
    await new Promise((r) => setTimeout(r, 2000));
  }
}
