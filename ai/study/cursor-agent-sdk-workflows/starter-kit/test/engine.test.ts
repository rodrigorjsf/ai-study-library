// Testes offline do engine (sem rede): `npm test`.
import assert from "node:assert/strict";
import { rmSync } from "node:fs";
import { join } from "node:path";
import { afterEach, test } from "node:test";
import { calls, script, stats } from "@cursor/sdk";
import { runWorkflow } from "../src/runtime/engine.js";
import { defineWorkflow } from "../src/runtime/workflow.js";

const cwd = join(import.meta.dirname, ".tmp");
const SCHEMA = { type: "object", required: ["tier"], properties: { tier: { enum: ["LOW", "MED", "HIGH"] } } };
const submit = (v: unknown) => (o: any) => {
  o.local.customTools.submit_result.execute(v, {});
  return {};
};
afterEach(() => {
  rmSync(cwd, { recursive: true, force: true });
  script.length = 0;
  calls.length = 0;
  Object.assign(stats, { active: 0, maxActive: 0, disposed: 0, usageReads: 0 });
});

test("schema: re-prompt até submit_result válido; 'mcp' entra na allowlist; contexto mdm carregado", async () => {
  script.push(() => ({}), submit({ tier: "BAD" }), submit({ tier: "MED" }));
  const wf = defineWorkflow({
    meta: { name: "s", description: "s" },
    defaults: { model: { id: "m" } },
    run: (ctx) => ctx.agent("classify", { schema: SCHEMA, tools: ["read"] }),
  });
  const r = await runWorkflow(wf, {}, { cwd });
  assert.equal(r.status, "finished");
  assert.deepEqual(r.result, { tier: "MED" });
  assert.deepEqual(calls[0].tools, ["read", "mcp"]);
  assert.deepEqual(calls[0].local.settingSources, ["project", "team", "mdm"]);
  assert.equal(stats.disposed, 1);
});

test("schema sem type object na raiz é rejeitado antes de criar agente", async () => {
  const wf = defineWorkflow({ meta: { name: "x", description: "x" }, defaults: { model: { id: "m" } }, run: (ctx) => ctx.agent("p", { schema: { type: "array" } }) });
  const r = await runWorkflow(wf, {}, { cwd });
  assert.equal(r.status, "failed");
  assert.equal(calls.length, 0);
});

test("argsSchema é validado antes de rodar", async () => {
  const wf = defineWorkflow({
    meta: { name: "a", description: "a", argsSchema: { type: "object", required: ["issue"], properties: { issue: { type: "number" } } } },
    defaults: { model: { id: "m" } },
    run: (ctx) => ctx.agent("p"),
  });
  const r = await runWorkflow(wf, { issue: "abc" }, { cwd });
  assert.equal(r.status, "failed");
  assert.match(r.error!, /args inválidos/);
  assert.equal(calls.length, 0);
});

test("etapa que falha em todas as tentativas derruba o workflow (não é pulada)", async () => {
  script.push(() => ({ status: "error", error: { message: "a" } }), () => ({ status: "error", error: { message: "b" } }));
  const wf = defineWorkflow({ meta: { name: "e", description: "e" }, defaults: { model: { id: "m" } }, run: (ctx) => ctx.agent("x") });
  const r = await runWorkflow(wf, {}, { cwd });
  assert.equal(r.status, "failed");
  assert.match(r.error!, /falhou após 2 tentativa/);
  assert.equal(stats.disposed, 2);
});

test("timeout: etapa falha, custo é contabilizado e o agente é descartado", async () => {
  script.push(() => ({ hang: true }));
  const wf = defineWorkflow({ meta: { name: "t", description: "t" }, defaults: { model: { id: "m" } }, run: (ctx) => ctx.agent("x", { timeoutMs: 50, retries: 0 }) });
  const r = await runWorkflow(wf, {}, { cwd });
  assert.equal(r.status, "failed");
  assert.match(r.error!, /timeout/);
  assert.equal(r.spentCents, 7);
  assert.equal(stats.disposed, 1);
});

test("resume: mesmo runId não cria agentes de novo", async () => {
  const wf = defineWorkflow({
    meta: { name: "r", description: "r" },
    defaults: { model: { id: "m" } },
    async run(ctx) {
      const p = await ctx.parallel([() => ctx.agent("a"), () => ctx.agent("b")]);
      const q = await ctx.pipeline([1, 2], (x: number) => ctx.agent(`s-${x}`), (prev: string, x: number) => `${prev}:${x}`);
      return { p, q };
    },
  });
  const r1 = await runWorkflow(wf, {}, { cwd });
  const created = calls.length;
  const r2 = await runWorkflow(wf, {}, { cwd, runId: r1.runId });
  assert.equal(calls.length, created);
  assert.deepEqual(r2.result, r1.result);
});

test("concorrência respeita o limite", async () => {
  const wf = defineWorkflow({
    meta: { name: "c", description: "c" },
    defaults: { model: { id: "m" } },
    run: (ctx) => ctx.parallel(Array.from({ length: 8 }, (_, i) => () => ctx.agent(`p${i}`))),
  });
  const r = await runWorkflow(wf, {}, { cwd, concurrency: 2 });
  assert.equal(r.status, "finished");
  assert.ok(stats.maxActive <= 2, `maxActive=${stats.maxActive}`);
});

test("teto de custo aborta, inclusive dentro de parallel", async () => {
  const wf = defineWorkflow({
    meta: { name: "b", description: "b" },
    defaults: { model: { id: "m" } },
    async run(ctx) {
      await ctx.agent("1");
      await ctx.agent("2");
      return ctx.parallel([() => ctx.agent("3"), () => ctx.agent("4")]);
    },
  });
  const r = await runWorkflow(wf, {}, { cwd, maxCents: 10 }); // o fake cobra 7¢ por etapa
  assert.equal(r.status, "failed");
  assert.match(r.error!, /Teto de custo/);
});
