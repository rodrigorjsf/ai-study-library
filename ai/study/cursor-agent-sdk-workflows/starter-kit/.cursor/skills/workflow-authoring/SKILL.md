---
name: workflow-authoring
description: Referência para escrever ou editar um workflow em workflows/*.ts com o runtime deste repositório (agent/parallel/pipeline/phase sobre o Cursor SDK). Use antes de criar ou alterar qualquer workflow.
---

# Escrever um workflow

Um workflow é um módulo TypeScript em `workflows/<nome>.ts` com `export default defineWorkflow({...})`.
O **código** decide o que roda, quando roda e quantas vezes roda. O modelo só executa cada etapa.
Se uma decisão pode ser tomada por código (label, contagem, teste passou ou não, tamanho do diff),
ela **tem** de ser tomada por código.

## Esqueleto

```ts
import { defineWorkflow } from "../src/runtime/workflow.js";

export default defineWorkflow<{ target: string }>({
  meta: {
    name: "meu-fluxo",                       // vira o nome da tool (MCP) e do comando (CLI)
    description: "Uma linha.",
    whenToUse: "Quando o usuário pedir X.",  // o agente do chat lê isto
    phases: [{ title: "Descobrir" }, { title: "Executar" }],
    argsSchema: { type: "object", required: ["target"], properties: { target: { type: "string" } } },
  },
  defaults: { model: { id: "composer-2" }, timeoutMs: 20 * 60_000 },
  async run(ctx) {
    ctx.phase("Descobrir");
    const found = await ctx.agent<{ files: string[] }>(`Liste os arquivos de ${ctx.args.target}.`, {
      tools: ["read", "grep", "glob", "ls"],
      schema: { type: "object", required: ["files"], properties: { files: { type: "array", items: { type: "string" } } } },
    });
    ctx.phase("Executar");
    return ctx.pipeline(found.files, (f: string) => ctx.agent(`Processe ${f}.`, { label: f, phase: "Executar" }));
  },
});
```

## API do contexto

| Chamada | O que faz |
|---|---|
| `ctx.agent(prompt, opts)` | Cria um agente novo do Cursor SDK e roda uma etapa. Com `schema`, devolve o objeto validado (o agente precisa chamar `submit_result`). Sem `schema`, devolve o texto final. **Lança erro** se falhar após `retries`. |
| `ctx.parallel(thunks)` | Barreira: roda em paralelo e espera todos. Item que falha vira `null`. Teto de custo aborta tudo. |
| `ctx.pipeline(items, ...stages)` | Sem barreira: cada item segue pelos estágios de forma independente. Estágio que falha descarta o item (`null`). |
| `ctx.phase(t)` / `ctx.log(m)` | Progresso, que aparece em `wait_workflow` e no CLI. |
| `ctx.args`, `ctx.cwd`, `ctx.runId` | Entrada, repositório e id do run. |
| `ctx.budget` | `spentCents()`, `spentTokens()`, `remainingCents()`, para rebaixar o modelo ou parar antes do teto. |

Opções de `agent()`: `model`, `schema`, `tools` (allowlist: `["read","grep","glob","ls"]` para etapas só de leitura),
`disallowedTools`, `cwd` (por exemplo um worktree), `agents` (subagents inline), `mcpServers`, `timeoutMs`, `retries`,
`schemaRetries`, `strictModel`, `label` e `phase`.

## Regras

1. **Determinismo para o resume.** O journal guarda cada etapa por hash de `prompt + opções`. Não ponha data/hora,
   valores aleatórios nem dados voláteis no prompt. Se precisar de data, receba por `args`.
2. **Use schema em toda etapa cujo resultado o código lê.** Texto livre só no fim, ou para o humano.
3. **Verificação é código.** Rode testes, lint e `git diff` com `execFileSync` dentro do workflow, não peça ao modelo
   "rode os testes e me diga se passou". Laços de correção sempre com teto (`for (round = 1; round <= N; ...)`).
4. **O modelo é escolhido no código.** Use um mapa `tier → ModelSelection`. Confirme os IDs com `npm run models`
   (a lista depende do plano e das restrições do admin). Use `strictModel: true` onde o modelo é requisito, porque
   o Cursor pode cair em outro modelo em silêncio.
5. **Escrita em paralelo só com isolamento.** Duas etapas simultâneas não podem editar os mesmos arquivos. Crie um
   `git worktree` por item e passe em `cwd`.
6. **Efeitos externos ficam no código.** Commit, push, abrir PR e comentar em issue são feitos com `gh` ou `git` no
   workflow, depois das verificações, não pelo agente.
7. **Nada de corte silencioso.** Se limitar cobertura (top-N, amostragem), registre com `ctx.log` o que ficou de fora.

## Padrões úteis

- **Roteamento por label/complexidade**: veja `workflows/implement-issue.ts`.
- **Verificação adversarial**: N revisores com lentes diferentes em `ctx.parallel`. Um achado só sobrevive com
  maioria. Use schema `{ refuted: boolean, evidence: string }`.
- **Loop até secar**: rodadas de busca até K rodadas seguidas sem achado novo, com deduplicação por chave no código.
- **Escalonamento de modelo**: tente com o modelo barato, valide com código e, se falhar, repita com o tier acima.

## Antes de entregar

- `npm run typecheck`
- Escreva um teste em `test/` com o fake SDK (`test/fake-sdk.ts`) cobrindo os ramos principais (tier, review
  condicional, falha de teste) e rode `npm test`.
- Rode uma vez de verdade com um teto baixo: `npm run wf -- run <nome> --args '{...}' --max-cents 100`.
