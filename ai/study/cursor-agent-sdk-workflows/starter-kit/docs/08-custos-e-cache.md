# 08 · Custos, cache e boas práticas

Este documento reúne o que torna um workflow barato sem perder a garantia de execução. É a referência da
seção de custo das skills `workflow-authoring` e `/skill-to-workflow`.

> **Marcas de confiança:**
> - **[PKG]**: lido no pacote `@cursor/sdk@1.3.1`.
> - **[DOC]**: doc oficial espelhada no repositório de estudo.
> - **[S]**: resumo de busca ou relato de fórum, não confirmado na fonte.
> - **[I]**: inferência.
>
> Preços e comportamento de cache mudam com frequência. Confira a página *Models & Pricing* do Cursor antes de
> fazer contas.

## 1. De onde vem o custo

Cada chamada de um agente envia ao modelo, nesta ordem aproximada:

1. **Contexto fixo do harness:** system prompt do Cursor, definições de tools (nativas, MCP e custom tools),
   regras (`AGENTS.md`, `.cursor/rules`), descrições de skills e descrições de subagents.
2. **O prompt da etapa.**
3. **O histórico da conversa** (em agentes com vários turnos), incluindo os resultados de tools.
4. A **saída** gerada, que é o token mais caro.

Um agente faz vários turnos dentro de uma etapa (ler arquivo, rodar comando, editar…), e cada turno reenvia o
contexto acumulado. A maior parte do custo de um agente de código costuma ser **releitura de contexto**, não
escrita [I].

**Preços de referência** (modo Auto, segundo resumo da página de preços [S]):

| Tipo | Preço por milhão |
|---|---|
| Input e cache write | US$ 1,25 |
| Cache read | US$ 0,25, ou seja 5× mais barato |
| Output | US$ 6,00 |

Em Teams/Enterprise, modelos de terceiros pagam também a *Cursor Token Rate*, com isenção para modelos cujo cache
read custa menos de US$ 0,10/M [S].

## 2. Que caches existem, e quem controla cada um

| Camada | Quem controla | O que economiza | Como aproveitar |
|---|---|---|---|
| **Cache de prompt do provedor** (prefixo idêntico) | O Cursor e o provedor, de forma automática. O SDK **não** expõe opção de cache, só mede `cacheReadTokens`/`cacheWriteTokens` [PKG] | Input relido sai pelo preço de cache read | Prefixo estável (§4.4) e conversas curtas (§4.5) |
| **Cache entre turnos de um agente** | O SDK, automático por agente: uma chave estável mantém "o cache de blobs entre turnos do servidor" [PKG] | Retries e re-prompts na mesma conversa | O re-prompt de schema do kit já roda na mesma conversa |
| **Journal do run** | Este kit, automático | Etapas já concluídas ao retomar um run | `--resume <runId>` / `start_workflow {resumeRunId}` |
| **Memo entre runs** | Este kit, opcional (`memo: true`) | Etapa de leitura repetida com o repositório no mesmo estado: **custo zero** | §4.1 |
| Cache do scan do workspace | Config do SDK: `workspaceScanCacheTtlMs`, default 20 s, ou `CURSOR_RIPWALK_CACHE_TTL_MS` [PKG] | Tempo e CPU para achar regras e skills, não tokens | Aumente num MCP server de vida longa sobre um checkout estável |

**Diferença em relação ao Claude Code.** Nos dynamic workflows do Claude Code, agentes irmãos com o mesmo
modelo, tools, schema e cwd **compartilham o prefixo em cache**. O runtime segura os irmãos até o primeiro
começar a responder, para que eles leiam o cache em vez de gravá-lo de novo
(`CLAUDE_CODE_WORKFLOW_PREFIX_STAGGER_MS`; TTL de 5 min, ou 1 h com `subagentPromptCacheTtl`) [DOC].

No Cursor, não há controle equivalente, e há relato de que agentes irmãos **não** compartilham o prefixo: cada
um grava o mesmo bloco [S]. Por isso este kit **não** promete economia de cache entre agentes. Ele mede
(`cacheHitRatio`) para você decidir com dados.

## 3. Medir antes de otimizar

Todo run devolve `usage` com tokens por tipo e `cacheHitRatio`. Cada etapa emite `step-end` com o próprio
`usage` e `chargedCents`:

```json
{ "status": "finished", "spentCents": 42,
  "usage": { "inputTokens": 120, "outputTokens": 60, "cacheReadTokens": 360, "cacheWriteTokens": 120,
             "totalTokens": 660, "cacheHitRatio": 0.6 } }
```

- `cacheHitRatio = cacheRead / (input + cacheRead + cacheWrite)` é uma aproximação: o SDK não documenta se
  `inputTokens` já inclui a parte em cache [I]. Compare runs entre si, não com números de outros clientes.
- `chargedCents` é **0 para uso incluído no plano** [PKG]. Use tokens para comparar.
- Rotina sugerida: rode o workflow uma vez com `--max-cents` baixo e leia os `step-end` no stderr do CLI ou em
  `recent` do job. Ataque primeiro as **duas etapas mais caras**: costuma haver uma que relê o repositório
  inteiro, ou que roda num modelo caro sem necessidade.

## 4. Padrões, em ordem de impacto

### 4.1 Não chamar o modelo

- **Decisão objetiva é código:** label, contagem, exit code, tamanho do diff. Cada `if` que substitui um
  "decida se…" é uma chamada a menos.
- **Pule etapas condicionalmente:** plano só para MED/HIGH, review só para HIGH ou diff grande.
- **Resume pelo journal:** nunca relance um run falho do zero.
- **`memo: true` em etapas só de leitura** (`tools` só com read, grep, glob, ls, semSearch…): a mesma etapa com
  o repositório no mesmo estado (HEAD + mudanças locais + arquivos novos) devolve o resultado salvo, mesmo em
  outro run. O runtime recusa `memo` em etapa que pode escrever.

```ts
await ctx.agent(`${PLAN_INSTRUCTIONS}\n\n${issueBlock(issue)}`, {
  model: MODELS.MED, tools: ["read", "grep", "glob", "ls", "semSearch"], schema: PLAN_SCHEMA, memo: true,
});
```

### 4.2 Modelo certo por etapa

- **Tier por etapa, não por workflow.** Use um modelo barato para classificar, resumir e corrigir lint, e o de
  fronteira só para planejamento difícil e review.
- **Escalone na falha:** tente com o barato, valide **com código** e repita com o tier acima só se falhar.
- **Parâmetros:** prefira variantes com raciocínio baixo para tarefas mecânicas (`model.params`, por exemplo
  `reasoning_effort`; confira em `npm run models`). Evite `maxMode` salvo necessidade.

### 4.3 Contexto fixo mínimo por etapa

O contexto fixo é pago em **toda** chamada de **toda** etapa. Ele cresce com o que o agente carrega:

| Fonte de contexto | Como reduzir |
|---|---|
| `settingSources: "project"`: `AGENTS.md`, regras, **descrições de todas as skills do projeto**, hooks e **tools dos MCP servers do `.cursor/mcp.json`** | Por etapa, use `settingSources: ["team","mdm"]` (governança sem o projeto) quando a etapa não precisa das regras do repositório: classificar, resumir, revisar texto |
| `"user"`: `~/.cursor/agents`, `~/.cursor/skills`, `~/.claude/skills`, MCP do usuário | O kit **não** carrega `user` por padrão. Há relatos de 60 subagents de usuário somando cerca de 10 mil tokens por conversa (11,4 k → 1,4 k ao removê-los) [S] |
| Tool `task`: a descrição lista **todos os subagents disponíveis** [S] | Use allowlist de `tools` sem `"task"`, salvo se a etapa precisar delegar |
| Definições de tools | Allowlist de `tools`. `[]` = só texto (o kit acrescenta `mcp` quando há schema) |
| MCP servers por etapa | Passe `mcpServers` só na etapa que usa |
| `AGENTS.md` longo | Mantenha curto. Instruções de uma etapa específica vão no prompt dela |

### 4.4 Prefixo estável (para o cache de prompt)

O cache do provedor reaproveita só o **prefixo idêntico**. Então:

- **Instruções fixas primeiro, dados variáveis no fim.** Declare as instruções como constantes no topo do módulo
  (`const PLAN_INSTRUCTIONS = "..."`) e monte o prompt como `INSTRUÇÕES + "\n\n" + dados`. Veja
  `workflows/implement-issue.ts`.
- **Nada volátil no começo do prompt:** sem data, id de run, contador de rodada ou saída de teste antes das
  instruções. Isso também preserva o journal e o memo, que usam o prompt na chave.
- **Mesma configuração entre irmãos:** mesmo modelo, ordem de `tools`, schema e `settingSources` em etapas
  paralelas parecidas. Mudar qualquer um muda o prefixo [I, por analogia com o Claude Code].
- **Schema estável:** o schema vira `inputSchema` da tool `submit_result`, que faz parte das definições de tools.

### 4.5 Conversas curtas

- **Um agente novo por etapa** (o padrão do kit) mantém o histórico pequeno. Numa conversa longa, cada turno relê
  todo o histórico. Há relatos de "consumo absurdo de cache read" exatamente por isso [S].
- **Reaproveite a conversa só para o que depende dela:** o re-prompt de schema, por exemplo.
- **Passe resumos entre etapas, não saídas inteiras:** use o resultado estruturado (schema) da etapa anterior e
  trunque saídas longas. O exemplo usa os últimos 4.000 caracteres da saída de teste.

### 4.6 Saídas enxutas

O output é o token mais caro. Peça só os campos que o código lê (schema mínimo) e nada de "explique seu
raciocínio" em etapas mecânicas.

### 4.7 Paralelismo consciente

N agentes em paralelo pagam N vezes o contexto fixo, e não há garantia de compartilhar cache entre eles [S].

- Faça fan-out só de itens realmente independentes.
- Agrupe itens pequenos numa etapa só: um agente para 5 arquivos pequenos, em vez de 5 agentes.
- Mantenha `concurrency` baixa quando o teto de custo for apertado.

### 4.8 Limites sempre

Laços de correção com teto, `timeoutMs` por etapa, `retries` pequeno (default 1), `--max-cents`/`--max-tokens`
por run, e polling barato no chat (modelo barato e esperas de 45–50 s; ver [04](04-invocacao-no-cursor-ide.md)).

## 5. Skills e subagents: o que custam no IDE e como ficam no workflow

| No IDE (skills e subagents) | No workflow convertido |
|---|---|
| A descrição de toda skill disponível fica no contexto; o corpo só entra quando a skill é usada [DOC] | Só o trecho necessário da skill entra, como **constante de instruções** da etapa (prefixo estável) |
| A descrição de todo subagent entra na tool Task [S]. Cada delegação abre um contexto novo e paga o contexto fixo de novo | Cada subagent vira uma etapa com modelo, tools e `settingSources` próprios e mínimos. Sem `"task"` na allowlist |
| `model: inherit`: tudo roda no modelo do chat, muitas vezes o mais caro | Modelo explícito por etapa (tier) |
| O modelo decide quantas vezes repetir | Laço com teto no código |
| Retomar = começar de novo | Journal + memo |

## 6. Checklist de custo

Use ao escrever um workflow e na etapa de otimização da `/skill-to-workflow`.

- [ ] Toda decisão objetiva é código (não é uma etapa de agente).
- [ ] Etapas opcionais têm condição explícita (tier, tamanho, flag).
- [ ] Cada etapa tem modelo explícito; o de fronteira só onde se justifica; há escalonamento na falha.
- [ ] Etapas só de leitura têm `tools` só de leitura e `memo: true`.
- [ ] Etapas que não precisam do repositório usam `settingSources: ["team","mdm"]` (ou `[]`).
- [ ] `tools` é uma allowlist; sem `"task"` se a etapa não delega; `mcpServers` só onde usa.
- [ ] Prompts: constante de instruções primeiro, dados no fim; nada volátil no começo.
- [ ] Schemas mínimos; nenhuma etapa mecânica pede explicação longa.
- [ ] Saídas grandes (logs, diffs) truncadas ou resumidas antes de virar prompt.
- [ ] Fan-out só de itens independentes; itens pequenos agrupados.
- [ ] Laços com teto; `timeoutMs` e `retries` definidos.
- [ ] Estimativa de custo por caminho (§7) registrada no topo do workflow.
- [ ] Primeiro run real com `--max-cents` baixo; `usage` por etapa revisado.

## 7. Estimar antes de rodar

Para cada caminho do workflow (ex.: LOW sem plano nem review; HIGH com plano, review e uma rodada de correção),
liste as etapas com:

```
custo ≈ Σ etapas × turnos_estimados × (contexto_fixo + prompt + histórico_médio) × preço_input/cache
        + Σ etapas × saída_estimada × preço_output
```

Na prática, a estimativa mais confiável é empírica: rode cada caminho uma vez com teto baixo, anote `usage` e
`spentCents` por etapa e registre a faixa num comentário no topo do workflow. A `/skill-to-workflow` gera esse
quadro no relatório de conversão.
