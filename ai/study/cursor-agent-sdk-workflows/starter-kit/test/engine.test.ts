// Testes offline do engine (sem rede): `npm test`.
import assert from "node:assert/strict";
import { rmSync } from "node:fs";
import { join } from "node:path";
import { afterEach, test } from "node:test";
import { calls, script } from "@cursor/sdk";
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
});

test("schema: re-prompt até submit_result válido; 'mcp' entra na allowlist", async () => {
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
});

test("fallback de modelo vira warning; strictModel falha", async () => {
  const warnings: string[] = [];
  script.push(() => ({ result: "x", model: { id: "outro" } }));
  const wf = defineWorkflow({ meta: { name: "f", description: "f" }, run: (ctx) => ctx.agent("p", { model: { id: "pedido" } }) });
  const r = await runWorkflow(wf, {}, { cwd, onEvent: (e) => e.type === "warning" && warnings.push(e.message) });
  assert.equal(r.status, "finished");
  assert.match(warnings[0]!, /pediu pedido, rodou outro/);

  script.push(() => ({ result: "x", model: { id: "outro" } }));
  const strict = defineWorkflow({ meta: { name: "f2", description: "f" }, run: (ctx) => ctx.agent("p", { model: { id: "pedido" }, strictModel: true }) });
  assert.equal((await runWorkflow(strict, {}, { cwd })).status, "failed");
});

test("etapa que falha em todas as tentativas derruba o workflow (não é pulada)", async () => {
  script.push(() => ({ status: "error", error: { message: "a" } }), () => ({ status: "error", error: { message: "b" } }));
  const wf = defineWorkflow({ meta: { name: "e", description: "e" }, defaults: { model: { id: "m" } }, run: (ctx) => ctx.agent("x") });
  const r = await runWorkflow(wf, {}, { cwd });
  assert.equal(r.status, "failed");
  assert.match(r.error!, /falhou após 2 tentativa/);
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
  const r2 = await runWorkflow(wf, {}, { cwd, resumeRunId: r1.runId });
  assert.equal(calls.length, created);
  assert.deepEqual(r2.result, r1.result);
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
