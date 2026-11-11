// Fake mínimo do @cursor/sdk: testa o controle de fluxo do engine sem rede nem conta Cursor.
// Ativado por tsconfig.test.json (paths: "@cursor/sdk" -> este arquivo).
export const calls: any[] = [];
export const script: Array<(o: any, msg: string, n: number) => any> = [];
export class RateLimitError extends Error { isRetryable = false; }
export const Agent = {
  async create(o: any) {
    calls.push(o);
    let n = 0;
    return {
      async send(msg: string) {
        const behave = script.shift() ?? (() => ({ status: "finished", result: "ok" }));
        const r = await behave(o, msg, n++);
        return { cancel: async () => {}, wait: async () => ({ id: "r", status: "finished", model: o.model, ...r }) };
      },
      async getUsage() { return { usage: { totalTokens: 100 }, cost: { chargedCents: 7, rawCostCents: 7 }, runs: [] }; },
      close() {},
    };
  },
};
export const Cursor = {};
