#!/usr/bin/env node
// CLI `wf`: roda workflows no terminal, em CI, ou a partir do shell do agente do Cursor.
//
//   wf login                          # login do SDK no navegador (conta do próprio usuário)
//   wf whoami                         # mostra a chave/conta em uso
//   wf list
//   wf run <workflow> --args '<json>' [--max-cents N] [--resume <runId>]   # primeiro plano; imprime JSON no fim
//   wf start <workflow> --args '<json>'   # segundo plano; imprime {jobId}
//   wf status <jobId>
//   wf wait <jobId> [--timeout 240]       # espera até o timeout e imprime o estado
//
// STATUS: código de referência. Typecheck contra @cursor/sdk@1.3.1; não executado contra a API real.

import { spawn } from "node:child_process";
import { randomUUID } from "node:crypto";
import { parseArgs } from "node:util";
import { Cursor } from "@cursor/sdk";
import { runWorkflow } from "./runtime/engine.js";
import { listJobs, readJob, startJob, waitJob } from "./runtime/jobs.js";
import { loadWorkflows } from "./runtime/registry.js";

const { positionals, values } = parseArgs({
  allowPositionals: true,
  options: {
    args: { type: "string", default: "{}" },
    cwd: { type: "string", default: process.cwd() },
    "max-cents": { type: "string" },
    "max-tokens": { type: "string" },
    resume: { type: "string" },
    job: { type: "string" },
    timeout: { type: "string", default: "240" },
  },
});

const [command, name] = positionals;
const cwd = values.cwd!;
const out = (v: unknown) => process.stdout.write(JSON.stringify(v, null, 2) + "\n");
const runOpts = () => ({
  cwd,
  resumeRunId: values.resume,
  maxCents: values["max-cents"] ? Number(values["max-cents"]) : (Number(process.env.WF_MAX_CENTS) || null),
  maxTokens: values["max-tokens"] ? Number(values["max-tokens"]) : null,
  onEvent: (e: unknown) => process.stderr.write(JSON.stringify(e) + "\n"),
});

async function main(): Promise<number> {
  switch (command) {
    case "login": {
      const r = await Cursor.auth.login();
      out(r);
      return 0;
    }
    case "whoami": {
      out(await Cursor.me());
      return 0;
    }
    case "list": {
      const wfs = await loadWorkflows();
      out([...wfs.values()].map((w) => ({ name: w.meta.name, description: w.meta.description })));
      return 0;
    }
    case "run": {
      const def = (await loadWorkflows()).get(name ?? "");
      if (!def) throw new Error(`workflow desconhecido: ${name}`);
      const args = JSON.parse(values.args!);
      if (values.job) {
        // Modo filho de `wf start`: grava o estado do job em disco.
        const { done } = startJob(def, args, runOpts(), values.job);
        const job = await done;
        return job.status === "finished" ? 0 : 1;
      }
      const outcome = await runWorkflow(def, args, runOpts());
      out(outcome);
      return outcome.status === "finished" ? 0 : 1;
    }
    case "start": {
      const jobId = randomUUID().slice(0, 8);
      const child = spawn(process.execPath, [...process.execArgv, process.argv[1]!, "run", name ?? "", "--args", values.args!, "--cwd", cwd, "--job", jobId], {
        detached: true,
        stdio: "ignore",
        env: process.env,
      });
      child.unref();
      out({ jobId, hint: `wf wait ${jobId}` });
      return 0;
    }
    case "status": {
      out(readJob(cwd, name ?? "") ?? { error: "job não encontrado" });
      return 0;
    }
    case "wait": {
      out((await waitJob(cwd, name ?? "", Number(values.timeout) * 1000)) ?? { error: "job não encontrado" });
      return 0;
    }
    case "jobs": {
      out(listJobs(cwd).map(({ jobId, workflow, status, phase }) => ({ jobId, workflow, status, phase })));
      return 0;
    }
    default:
      process.stderr.write("uso: wf <login|whoami|list|run|start|status|wait|jobs> ...\n");
      return 2;
  }
}

main().then(
  (code) => process.exit(code),
  (err: unknown) => {
    process.stderr.write(`${err instanceof Error ? err.message : String(err)}\n`);
    process.exit(1);
  },
);
