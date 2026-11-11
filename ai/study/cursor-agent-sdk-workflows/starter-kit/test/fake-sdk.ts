// Fake mínimo do @cursor/sdk: testa o controle de fluxo do engine sem rede nem conta Cursor.
// Ativado por tsconfig.test.json (paths: "@cursor/sdk" -> este arquivo).
export const calls: any[] = [];
/** Comportamento de cada send(), em ordem. Sem entrada: run "finished" com result "ok". */
export const script: Array<(o: any, msg: string, n: number) => any> = [];
export const stats = { active: 0, maxActive: 0, disposed: 0, usageReads: 0 };
export class CursorAgentError extends Error {
  isRetryable = false;
}
export class RateLimitError extends CursorAgentError {}
export class AgentBusyError extends CursorAgentError {}
export const Agent = {
  async create(o: any) {
    calls.push(o);
    stats.active++;
    stats.maxActive = Math.max(stats.maxActive, stats.active);
    let n = 0;
    return {
      async send(msg: string) {
        const behave = script.shift() ?? (() => ({ status: "finished", result: "ok" }));
        const r = await behave(o, msg, n++);
        if (r?.hang) return { cancel: async () => {}, wait: () => new Promise(() => {}) };
        return { cancel: async () => {}, wait: async () => ({ id: "r", status: "finished", model: o.model, ...r }) };
      },
      async getUsage() {
        stats.usageReads++;
        return { usage: { totalTokens: 100 }, cost: { chargedCents: 7, rawCostCents: 7 }, runs: [] };
      },
      async [Symbol.asyncDispose]() {
        stats.active--;
        stats.disposed++;
      },
      close() {},
    };
  },
};
export const Cursor = {};
