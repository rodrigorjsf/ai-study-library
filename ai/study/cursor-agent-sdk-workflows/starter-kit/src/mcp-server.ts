#!/usr/bin/env node
// MCP server (stdio) que expõe os workflows ao chat do Cursor IDE (e de qualquer cliente MCP,
// inclusive Claude Code). Padrão assíncrono: start → jobId; wait com teto curto → estado parcial ou final.
// Isso evita depender do timeout de chamada de tool do cliente, que não é documentado pelo Cursor.
//
// Tools:
//   list_workflows                       → nome, descrição, quando usar, schema dos args
//   start_workflow {name, args}          → {jobId}
//   wait_workflow  {jobId, timeoutSec}   → estado (status, fase, últimos eventos, resultado)
//   get_workflow_status {jobId}          → estado sem esperar
//
// Os jobs rodam dentro deste processo. Se o Cursor reiniciar o servidor MCP, o job em andamento
// morre; relance com o mesmo runId (o journal evita repetir etapas concluídas) ou use `wf start`,
// que roda destacado do servidor.
//
// STATUS: código de referência. Typecheck contra @cursor/sdk@1.3.1 e @modelcontextprotocol/sdk; não executado.

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { readJob, startJob, waitJob } from "./runtime/jobs.js";
import { loadWorkflows } from "./runtime/registry.js";

const cwd = process.env.WF_CWD ?? process.cwd();
const maxCents = Number(process.env.WF_MAX_CENTS) || null;
const workflows = await loadWorkflows();

const server = new Server({ name: "cursor-workflows", version: "0.1.0" }, { capabilities: { tools: {} } });

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "list_workflows",
      description: "Lista os workflows determinísticos disponíveis neste repositório.",
      inputSchema: { type: "object", properties: {} },
    },
    {
      name: "start_workflow",
      description:
        "Inicia um workflow pelo nome. O workflow roda até o fim por conta própria (etapas, modelos e revisões " +
        "definidos em código). Retorna um jobId; depois chame wait_workflow até status != running. Disponíveis: " +
        [...workflows.values()].map((w) => `${w.meta.name} (${w.meta.whenToUse ?? w.meta.description})`).join("; "),
      inputSchema: {
        type: "object",
        required: ["name"],
        properties: { name: { type: "string", enum: [...workflows.keys()] }, args: { type: "object" } },
      },
    },
    {
      name: "wait_workflow",
      description: "Espera até timeoutSec (máx. 50) pelo fim do job e devolve o estado. Repita enquanto status = running.",
      inputSchema: {
        type: "object",
        required: ["jobId"],
        properties: { jobId: { type: "string" }, timeoutSec: { type: "number", maximum: 50 } },
      },
    },
    {
      name: "get_workflow_status",
      description: "Estado atual de um job, sem esperar.",
      inputSchema: { type: "object", required: ["jobId"], properties: { jobId: { type: "string" } } },
    },
  ],
}));

const text = (v: unknown) => ({ content: [{ type: "text" as const, text: JSON.stringify(v, null, 2) }] });

server.setRequestHandler(CallToolRequestSchema, async (req) => {
  const a = (req.params.arguments ?? {}) as Record<string, unknown>;
  switch (req.params.name) {
    case "list_workflows":
      return text([...workflows.values()].map((w) => ({ ...w.meta })));
    case "start_workflow": {
      const def = workflows.get(String(a.name));
      if (!def) return { ...text({ error: `workflow desconhecido: ${String(a.name)}` }), isError: true };
      const { jobId } = startJob(def, a.args ?? {}, { cwd, maxCents });
      return text({ jobId, next: "chame wait_workflow com este jobId" });
    }
    case "wait_workflow": {
      const secs = Math.min(Number(a.timeoutSec ?? 45), 50);
      return text((await waitJob(cwd, String(a.jobId), secs * 1000)) ?? { error: "job não encontrado" });
    }
    case "get_workflow_status":
      return text(readJob(cwd, String(a.jobId)) ?? { error: "job não encontrado" });
    default:
      return { ...text({ error: `tool desconhecida: ${req.params.name}` }), isError: true };
  }
});

await server.connect(new StdioServerTransport());
