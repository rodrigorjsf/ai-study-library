# 05 · Escrevendo workflows

A referência operacional, que o agente do Cursor também usa, está na skill
[`.cursor/skills/workflow-authoring/SKILL.md`](../.cursor/skills/workflow-authoring/SKILL.md). Este documento
explica o *porquê* das regras e traz receitas.

## Princípio

> Se uma decisão pode ser tomada por código, ela **tem** de ser tomada por código.

| Decisão | Por código | Por modelo |
|---|---|---|
| Qual modelo usar | Label da issue, tamanho do diff, `ctx.budget` | Só quando não há sinal objetivo: classificador barato com schema |
| Se uma etapa roda | `if` sobre dados | Nunca |
| Quantas vezes repetir | Laço com teto | Nunca |
| Se passou | Exit code de teste, lint, typecheck | Review como *segunda* camada, nunca a única |
| Efeitos externos (commit, PR) | Sempre | Nunca |

## Receitas

### Roteamento por label → modelo

```ts
const tier = issue.labels.map((l) => LABEL_TIERS[l.name]).find(Boolean)
  ?? (await ctx.agent<{ tier: Tier }>(classifyPrompt, { model: MODELS.CLASSIFY, schema: TIER_SCHEMA })).tier;
await ctx.agent(task, { model: MODELS[tier], cwd: worktree, schema: IMPL_SCHEMA });
```

### Review condicional por complexidade

```ts
if (tier === "HIGH" || diffLines > 300) {
  const reviews = await ctx.parallel(LENSES.map((lens) => () =>
    ctx.agent(reviewPrompt(lens), { model: MODELS.REVIEW, tools: ["read", "grep", "glob", "ls", "shell"], schema: REVIEW_SCHEMA })));
  const blocking = reviews.flatMap((r) => r?.findings ?? []).filter((f) => f.severity === "blocking");
  if (blocking.length) await ctx.agent(fixPrompt(blocking), { model: MODELS[tier], cwd: worktree, schema: IMPL_SCHEMA });
}
```

### Corrigir até passar (com teto)

```ts
let t = runTests(cmd, worktree);
for (let round = 1; !t.ok && round <= 2; round++) {
  await ctx.agent(`Testes falharam:\n${t.output}`, { model: MODELS.HIGH, cwd: worktree, schema: IMPL_SCHEMA });
  t = runTests(cmd, worktree);
}
if (!t.ok) return { status: "tests-failed", output: t.output };
```

### Fan-out com isolamento

```ts
await ctx.pipeline(files, async (file: string, _item, i) => {
  const wt = createWorktree(`wf/migrate-${i}`);           // git worktree add, no código
  return ctx.agent(`Migre ${file} para TS.`, { cwd: wt, label: file, phase: "Migrar", schema: IMPL_SCHEMA });
}, (r, file) => verify(file, r));                         // verificação por item, sem barreira
```

### Verificação adversarial

```ts
const votes = await ctx.parallel([0, 1, 2].map((v) => () =>
  ctx.agent(`Tente REFUTAR: ${claim}. Na dúvida, refuted=true.`, { label: `v${v}`, schema: VERDICT })));
const survives = votes.filter(Boolean).filter((x) => !x!.refuted).length >= 2;
```

### Escalonar o modelo por orçamento

```ts
const model = ctx.budget.remainingCents() < 100 ? MODELS.MED : MODELS.HIGH;
```

## Escrevendo bons prompts de etapa

- **Autocontidos:** a etapa não vê o histórico do chat nem as etapas anteriores. Passe no prompt tudo o que ela
  precisa, inclusive os resultados de etapas anteriores.
- **Uma responsabilidade por etapa.** "Planeje" e "implemente" são duas etapas. Isso ajuda os modelos pequenos.
- **Diga o que não fazer:** "não faça commit", "não edite os testes, salvo se estiverem errados".
- **Schema enxuto:** só os campos que o código vai ler.

## Testando

1. Crie `test/<nome>.test.ts`. O `tsconfig.test.json` troca `@cursor/sdk` por `test/fake-sdk.ts`.
2. No fake, `script.push(fn)` define o comportamento de cada `send()`:
   - `() => ({ result: "texto" })` simula texto livre;
   - `(o) => { o.local.customTools.submit_result.execute(obj, {}); return {}; }` simula saída estruturada;
   - `() => ({ status: "error" })` simula uma falha.
3. Cubra cada ramo: tier por label e sem label, review ligado e desligado, testes falhando até o teto.
4. Para etapas com `execFileSync` (`gh`, `git`), extraia funções e injete stubs por `args`, ou rode o teste num
   repositório temporário.

```bash
npm test && npm run typecheck
npm run wf -- run <nome> --args '{...}' --max-cents 100   # primeiro run real, com teto baixo
```
