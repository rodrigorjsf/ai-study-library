# Prompt: validar localmente e publicar o starter kit

> **Como usar:** abra uma sessão local (Claude Code ou o agente do Cursor) no WSL, na raiz do `ai-study-library`, e
> cole tudo a partir da linha "Tarefa" abaixo.
>
> O prompt conduz o agente por fases com portões:
> 1. perguntas abertas;
> 2. verificações sem custo;
> 3. verificações com custo, só com sua aprovação;
> 4. plano revisado;
> 5. criação do repositório público, só com sua confirmação;
> 6. volta ao ai-study-library.
>
> Ele existe porque a sessão na nuvem que produziu o estudo não acessava cursor.com nem tinha conta Cursor. Várias
> afirmações ficaram marcadas como [S] (resumo de busca) ou [I] (inferência) e precisam ser verificadas localmente.

---

# Tarefa: validar localmente e publicar o "Cursor Workflows Starter Kit" como repositório público no meu GitHub

Você está numa sessão LOCAL (WSL) na raiz do repositório `ai-study-library`
(https://github.com/rodrigorjsf/ai-study-library, branch `main`). Siga o CLAUDE.md deste repositório: trabalhe comigo
em perguntas abertas e esboço ANTES de escrever o plano, peça revisão independente do plano antes de executá-lo,
cubra Cursor e Claude Code, prefixe comandos com `rtk` quando disponível e registre em "Applied Learning" o que
falhar repetidamente.

## Contexto

Uma sessão na nuvem pesquisou o Cursor SDK (`@cursor/sdk@1.3.1`) e montou um starter kit de workflows
determinísticos: runtime TS com agent/parallel/pipeline/phase, journal, memo, teto de custo, saída estruturada via
`submit_result`, MCP server, CLI `wf`, skills em `.agents/skills`, observabilidade em SQLite e dashboard localhost.

Essa sessão NÃO conseguiu:
- acessar cursor.com, forum.cursor.com nem arxiv.org;
- usar uma conta Cursor;
- rodar o Cursor IDE.

Por isso várias afirmações estão marcadas [S] (resumo de busca) ou [I] (inferência) e o kit nunca rodou contra a
API real. Sua primeira responsabilidade é transformar essas marcas em fatos verificados ou refutados. Só depois
criamos o repositório.

### Leia antes de tudo (nesta ordem)

1. `ai/study/cursor-agent-sdk-workflows/README.md`
2. `ai/study/cursor-agent-sdk-workflows/00-relatorio-pesquisa.md`. A §8 é a lista de incertezas.
3. `ai/study/cursor-agent-sdk-workflows/starter-kit/README.md` e `starter-kit/docs/01..09`. O manual de
   validação é o `docs/01-instalacao.md` §5 (teste de fumaça real); os outros docs descrevem o que cada parte
   promete.
4. `starter-kit/AGENTS.md` e `starter-kit/.agents/skills/*/SKILL.md`
5. `tasks/todo.md`: as seções "Plan — Cursor Agent SDK workflows", "Plan — Observabilidade V1" e as seções
   "Review"
6. `tasks/lessons.md`
7. As fontes locais usadas na pesquisa:
   - `ai/docs/claude-code/workflows/workflows.md`
   - `docs/cursor/sdk/cursor-agent-sdk-reference.md`
   - `docs/cursor/{hooks,subagents,skills,mcp,cli}/`

### Commits relacionados (proveniência; cite-os no novo repositório)

| SHA | Commit |
|---|---|
| f3dd5eefcadabf64848595460bf50a718396c908 | docs: mirror Claude Code dynamic workflows documentation |
| 6640d40252900648f02674d8f9c25d40f0e66c8c | tasks: plan for Cursor Agent SDK workflows study |
| e444790a3b936bbd6af918e5c434e138aa6c787c | study: Cursor Agent SDK deterministic workflows report and starter kit |
| 9a6b24fbb4d4eeea1a67f59afc6634840f4735f9 | study: apply advisor review and .agents layout to Cursor workflows starter kit |
| 1774f87fad3d52f4b92578bdd859fa45abac0df8 | study: cost and caching practices for Cursor workflows starter kit |
| 9855bdae0b2de5076b73732808c35344f409b862 | tasks: plan observability V1 for Cursor workflows starter kit |
| a69f2a21a78b7d5689fb21b6ed3c89d6890019db | study: observability V1 for Cursor workflows starter kit |

Links no formato `https://github.com/rodrigorjsf/ai-study-library/commit/<SHA>`.
Rode `git log --stat <SHA>` em cada um para entender o que entrou.

O commit que adicionou este arquivo de prompt também é proveniência: cite-o com `git log -1 --format=%H --
ai/study/cursor-agent-sdk-workflows/PROMPT-publicar-repositorio.md`.

## Fase 0: perguntas abertas (pare e me pergunte antes de seguir)

Pergunte, com recomendação em cada item:

1. **Nome do repositório e dono.** Sugestão: `rodrigorjsf/cursor-workflows-starter`. Confira com
   `gh repo view` se o nome está livre.
2. **Licença.** Sugestão: MIT.
3. **Idioma.** Os docs estão em pt-BR. Mantenho pt-BR e acrescento um README curto em inglês?
4. **Orçamento para testes reais** contra a API do Cursor. Sugestão: teto total de US$ 2,00, com `--max-cents` em
   todo run.
5. **Credencial.** `wf login` (navegador) ou `CURSOR_API_KEY`. Nunca imprima a chave.
6. **Repositório descartável de teste** para o teste ponta a ponta do `implement-issue`: um repo privado meu com
   uma issue simples rotulada `complexity:low`. Sugestão: criar um `wf-sandbox` privado.
7. **Escopo do conteúdo público:** só o kit, ou o kit mais o relatório de pesquisa (em `docs/research/`)?
8. **Volta ao ai-study-library:** registrar o link do novo repo via PR, ou commit direto na `main`?

## Fase 1: verificações SEM custo (rode tudo, registre evidências)

Para cada item, registre: comando, saída relevante (trecho), conclusão (confirmado, refutado ou inconclusivo) e
impacto nos docs.

1. **Ambiente.**
   - `node -v`: precisa ser ≥ 22.13.
   - `gh auth status`, `git --version`.
   - Se `cursor`/`agent` existirem no PATH, registre as versões.
   - Confirme que o repo está em disco Linux (não em `/mnt/c`), porque o modo WAL do SQLite falha em `/mnt/c`.
2. **Instalação limpa do kit**, numa cópia em `~/tmp/wf-kit-check`:
   - `npm ci`, `npm run typecheck`, `npm test`. A expectativa é 21 testes passando.
   - Confirme que `npm ci` baixa os binários de plataforma (`@cursor/sdk-linux-x64`, `@esbuild/linux-x64`).
3. **Docs oficiais ao vivo.** Espelhe com `curl -sSL https://cursor.com/docs/<página>.md`. Páginas:
   - `sdk/typescript`, `sdk/python`, `sdk/bridge`
   - `models-and-pricing`, `account/pricing`, `account/teams/pricing`
   - `account/enterprise/service-accounts`
   - `cli/overview`, `cli/headless`, `cli/reference/parameters`, `cli/reference/authentication`,
     `cli/reference/output-format`
   - `cloud-agent/api/endpoints`
   - `agent/hooks`, `subagents`, `skills`, `mcp`
   - `release-notes/sdk`, `changelog/sdk-updates-jun-2026`

   Compare com os espelhos locais (`docs/cursor/...`, `ai/docs/cursor/...`) e confirme ou refute cada [S]/[I] do
   relatório e dos docs 02, 07, 08 e 09. Em particular:
   1. as runs locais do SDK seguem plano, pools e Privacy Mode do IDE, e aparecem com a tag "SDK";
   2. "user keys bill the user; service-account keys bill the team"; e se o uso da chave de usuário entra no
      limite em dólares **por membro** (Teams/Enterprise);
   3. chaves Team Admin não são aceitas pelo SDK;
   4. preços do modo Auto (input/cache write US$ 1,25, cache read US$ 0,25, output US$ 6/M) e a isenção da
      Cursor Token Rate;
   5. se o Cursor aplica a faixa de contexto do Claude Haiku 5.5 (US$ 0,10/0,50 até 100k tokens de prompt e
      US$ 0,50/2,50 acima, na API Anthropic);
   6. se hooks de `.cursor/hooks.json` e hooks do Claude Code disparam em runs locais do SDK com
      `settingSources: ["project"]`;
   7. o comportamento de modelo bloqueado pelo admin nas runs do SDK: erro ou substituição silenciosa;
   8. timeout de chamada de tool MCP no Cursor IDE;
   9. limites de concorrência e rate limit por usuário.

   Também tente os tópicos do fórum citados no doc 08 (agentes irmãos sem prefixo de cache compartilhado;
   subagents e skills pré-carregados inflando tokens).
4. **Atualize os espelhos locais** que mudaram em `docs/cursor/` e `ai/docs/cursor/`, num commit separado no
   ai-study-library, conforme o CLAUDE.md.

## Fase 2: verificações COM custo (só após minha aprovação explícita do orçamento da Fase 0)

Use teto em tudo (`--max-cents`, `WF_MAX_CENTS`). Grave as métricas num banco separado:
`WF_METRICS_DB=~/tmp/wf-verify.db`. Antes de cada bloco, diga a estimativa de custo e espere meu "ok".

1. **Login e identidade.**
   - `npm run wf -- login` (ou `CURSOR_API_KEY`).
   - `npm run wf -- whoami`: confirme que só e-mail e validade são impressos.
   - Confira as permissões de `~/.cursor/sdk/auth.json`.
2. **Modelos.**
   - `npm run models`: registre os IDs reais.
   - Atualize os defaults de `WF_MODEL_*` em `workflows/implement-issue.ts` e `docs/02` se `auto-low`,
     `composer-2` ou `gpt-5.3-codex` não existirem.
   - Teste um ID inválido e confirme o erro "Cannot use this model".
3. **Sonda de granularidade.** Crie `scripts/probe-sdk.ts` no kit: um único `send` que leia 3–4 arquivos.
   1. Conte os eventos `turn-ended`, `step-completed` e `tool-call-started`.
   2. Compare o uso de `turn-ended` com `getUsage().usage` e `getUsage().runs[]` (quantos grupos? cada um é uma
      chamada ou um turno?).
   3. Registre se há `rawCostCents` e com que atraso chega.
   4. Teste `Agent.getUsage(agentId)` estático depois do `asyncDispose` (é disso que o `wf metrics reconcile`
      depende).
   5. Confirme que `RunResult.model` devolve o modelo pedido.
4. **Saída estruturada.** Uma etapa com `schema` e `tools: ["read"]`:
   - o `submit_result` aparece e é chamado;
   - o re-prompt na mesma conversa funciona (sem `AgentBusyError` persistente);
   - JSON inválido volta para correção.
5. **Contexto e governança.** Com `settingSources: ["project","team","mdm"]`:
   - um `AGENTS.md` com uma instrução marcadora é seguido pela etapa;
   - um hook de teste em `.cursor/hooks.json` dispara;
   - o `.cursor/mcp.json` do projeto é carregado e, **dentro da etapa**, o servidor `workflows` não expõe tools
     (`WF_INSIDE_WORKFLOW`).
6. **Cache.** Duas etapas irmãs idênticas em `ctx.parallel`. Compare `cacheReadTokens` da segunda com a primeira:
   o Cursor compartilha prefixo entre agentes? Registre o `cacheHitRatio`.
7. **Ponta a ponta.**
   - `implement-issue` no repo `wf-sandbox` com `--max-cents 50`: siga o checklist do `docs/01` §5, incluindo o
     resume com `--resume <runId>` sem repetir commit.
   - Depois, `npm run stats` e `wf metrics reconcile`.
8. **Cursor IDE** (abra pelo Windows, com o projeto no WSL):
   - habilite o MCP `workflows` em Settings → MCP;
   - confirme que `/run-workflow`, `/workflow-authoring` e `/skill-to-workflow` (de `.agents/skills/`) aparecem;
   - rode `/run-workflow implement-issue <n>` com um modelo barato no chat;
   - observe se `wait_workflow` (50 s) estoura algum timeout de tool;
   - rode `scripts/link-claude-skills.sh` e verifique se as skills aparecem duplicadas no Cursor.
9. **Claude Code:** com o `.mcp.json` do kit, confirme que as tools MCP aparecem e que `CLAUDE.md` → `@AGENTS.md`
   é lido.
10. **Dashboard no WSL.** Rode `npm run dash` e abra `http://localhost:4317` no navegador do Windows.
    - O servidor escuta em 127.0.0.1; confirme que o encaminhamento de localhost do WSL2 funciona (modo NAT e,
      se aplicável, rede espelhada).
    - Confirme que `Host` diferente de localhost recebe 403.
11. **Faixa de contexto (opcional, só se eu aprovar).** Uma etapa com Haiku 5.5 em repositório grande, para
    passar de 100k tokens de prompt por passo. Compare `cents_per_1k_tokens` entre faixas em `v_context_buckets`.

Consolide tudo em `docs/research/verificacoes-locais.md` no novo repo, com a tabela: item | método | resultado |
evidência | ação tomada.

Corrija os docs e o código conforme os resultados:
- troque [S]/[I] por fatos;
- remova o que foi refutado;
- ajuste defaults;
- se mudar comportamento, acrescente testes no `test/`.

## Fase 3: plano do novo repositório (esboço → minha aprovação → revisão independente)

Proponha a estrutura antes de criar arquivos. Ponto de partida:

```
cursor-workflows-starter/
├── README.md                # status honesto (o que foi verificado localmente e o que não), começo rápido, links
├── README.en.md             # resumo em inglês (se aprovado)
├── LICENSE
├── CHANGELOG.md             # 0.1.0 = estado do commit a69f2a2 + correções da verificação local
├── PROVENANCE.md            # origem: os commits acima com links, sessões e fontes primárias consultadas
├── SECURITY.md              # o que nunca commitar, como reportar
├── AGENTS.md, CLAUDE.md     # do kit
├── package.json, package-lock.json, tsconfig*.json, .gitignore
├── .agents/skills/ · .agents/workflows/ · .cursor/mcp.json · .mcp.json
├── src/ · workflows/ · test/ · scripts/
├── docs/01..09 + docs/img/
├── docs/research/
│   ├── relatorio-pesquisa.md       # 00-relatorio-pesquisa.md com os links relativos reescritos
│   └── verificacoes-locais.md      # resultado das Fases 1–2
└── .github/
    ├── workflows/ci.yml            # ubuntu, Node 22.x: npm ci, typecheck, test (sem segredos; testes offline)
    └── ISSUE_TEMPLATE/ (opcional)
```

Regras:

- **Não republique os espelhos de docs de terceiros** (`ai/docs/...`, `docs/cursor/...`): são conteúdo da Cursor e
  da Anthropic. No repo público, troque por links para as URLs oficiais e cite a data de acesso. Os docs
  escritos neste estudo podem ir.
- **Reescreva todo link relativo** que apontava para fora da pasta do kit (por exemplo `../../docs/...` no
  relatório) para URLs oficiais ou para o ai-study-library no commit `a69f2a2`.
- Garanta que nada disto vai para o repo: `.workflows/`, `metrics-export/`, bancos `*.db`, `~/.cursor/sdk/auth.json`
  e chaves (`crsr_`, `sk-`, tokens). Rode um scan de segredos (`gitleaks detect` se houver; senão um `git grep`
  com padrões) e mostre o resultado.
- **Histórico:** prefira um commit inicial limpo com a mensagem citando os SHAs e o `PROVENANCE.md`. Proponha
  `git subtree split --prefix=ai/study/cursor-agent-sdk-workflows/starter-kit` só se eu pedir para preservar o
  histórico.
- Mantenha `"private": true` no `package.json`. Não é para publicar no npm.
- Não inclua este arquivo de prompt no novo repositório; ele fica só no ai-study-library.

Antes de executar, peça revisão independente do plano (subagente revisor, conforme o CLAUDE.md) e me mostre os
ajustes.

## Fase 4: montar, validar e publicar (confirme comigo antes de criar o repositório público)

1. Monte o repositório em `~/code/<nome>` (fora do ai-study-library), com `git init -b main`.
2. Validações locais:
   - `npm ci`, `npm run typecheck`, `npm test`;
   - checagem de links relativos em todos os `.md`;
   - scan de segredos;
   - `git status` limpo.
3. **Mostre o resumo e PEÇA CONFIRMAÇÃO** para criar o repositório público. Inclua: árvore de arquivos, tamanho,
   resultado das verificações e o texto do README.
4. Crie e envie:

   ```bash
   gh repo create <dono>/<nome> --public \
     --description "Deterministic agent workflows on the Cursor SDK: code-orchestrated steps, per-step models, MCP/CLI invocation from Cursor IDE, cost controls and local observability" \
     --source . --remote origin --push
   gh repo edit <dono>/<nome> --add-topic cursor,cursor-sdk,ai-agents,agent-workflows,mcp,claude-code,llm-observability,typescript
   ```

5. Espere o CI terminar (`gh run watch`) e confirme que está verde. Se falhar, corrija, reproduza localmente e envie
   de novo.
6. Crie a release `v0.1.0` com as notas do `CHANGELOG.md`. Indique claramente o que foi verificado contra a API
   real e o que segue pendente.

## Fase 5: voltar ao ai-study-library

1. Em `ai/study/cursor-agent-sdk-workflows/README.md`, acrescente o link do novo repositório e o resumo das
   verificações locais (o que mudou nos fatos).
2. Atualize a seção "Review" correspondente em `tasks/todo.md`.
3. Siga a escolha da Fase 0, item 8 (PR ou commit direto na `main`). Commits no padrão do repositório.

## Entrega final (me responda com)

- URL do repositório e da release, e o status do CI.
- Tabela das verificações: confirmadas, refutadas e inconclusivas, com o que mudou nos docs e no código.
- Custo real gasto nos testes (do banco `~/tmp/wf-verify.db`: `SELECT ROUND(SUM(cost_cents),2) FROM v_attempts`).
- O que continua pendente e por quê.

Regras gerais:
- Nunca imprima nem commite chaves.
- Não gaste créditos sem meu "ok".
- Não crie nada público sem confirmação.
- Se algo divergir do relatório, a evidência local vence: corrija o documento e cite a fonte.
