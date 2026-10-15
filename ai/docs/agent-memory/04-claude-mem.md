# 04 — claude-mem (thedotmack): conceitos, arquitetura e vantagens em projetos agênticos

> **Estudo (pt-BR) — 2026-10-14.** Repositório: https://github.com/thedotmack/claude-mem, analisado no commit
> `fef3402e674bebbf72a23aeb735e91c92cd34afd` (v13.39.0, Apache-2.0). Leitura estática e somente leitura: nada foi
> executado. Referências `arquivo:linha` são relativas à raiz do repositório.
>
> **Diagramas interativos (archify):** [arquitetura](html/claude-mem-arquitetura.html) ·
> [ciclo de sessão](html/claude-mem-sessao.html)

← [03 — ai-memory: segurança](03-ai-memory-seguranca.md) | [05 — claude-mem: segurança →](05-claude-mem-seguranca.md)

---

## 1. Em uma frase

**O claude-mem captura cada ação do agente por hooks, manda essa ação para um segundo LLM ("observador") que a
comprime em "observações" estruturadas, guarda tudo em SQLite + Chroma e injeta um índice compacto no início da
próxima sessão, com detalhes sob demanda via MCP.**

| Ficha | Valor |
|---|---|
| Linguagem | TypeScript sobre Bun (cerca de 128 mil linhas em `src/`) |
| Licença | Apache-2.0 no core. **Atenção:** o plugin `claude-mem-cowork` do mesmo marketplace é `PolyForm-Noncommercial-1.0.0` `[verificado: cowork/.claude-plugin/plugin.json:10]` |
| Criado / versão | 2025-08-31 / v13.39.0 (2026-10-13), com **366 versões** no CHANGELOG |
| Popularidade | 100 749 estrelas, 8 828 forks, 257 contribuidores (paginado) |
| Testes | 888 arquivos de teste, 8 workflows de CI |
| Runtime | Worker Bun residente + subprocesso Python `chroma-mcp` via `uvx` + subprocessos do Agent SDK |
| Dependência de LLM | **obrigatória**: sem observador não há memória |

---

## 2. Conceitos centrais (conferidos no código)

| Conceito | O que é, em linguagem simples | Evidência |
|---|---|---|
| **Observação** | Um registro gerado por LLM com `type`, `title`, `facts`, `narrative`, `concepts`, `files_read`, `files_modified` | `src/services/sqlite/SessionStore.ts:1521-1538`; `src/sdk/prompts.ts:39-54` |
| **Tipos de observação (modos)** | Definidos por JSON: bugfix, feature, refactor, decision, discovery, security_alert… São 36 modos (`code`, 29 idiomas, `law-study`, `email-investigation`…) | `plugin/modes/code.json:5-102` |
| **"Compressão"** | Cada evento de ferramenta vira um prompt para o LLM observador, que **precisa** responder em XML `<observation>`. No Stop, responde `<summary>` | `src/sdk/prompts.ts:441-448`; `src/sdk/parser.ts:62,121,210` |
| **Resumo de sessão** | `request`, `investigated`, `learned`, `completed`, `next_steps` | `SessionStore.ts:1222-1236` |
| **Progressive disclosure** | Três camadas: índice (ids + títulos) → timeline em volta → registros completos só dos ids escolhidos | `src/servers/mcp-server.ts:488,589,641,660` |
| **Injeção no SessionStart** | Por padrão, 50 observações e as últimas 10 sessões entram como `additionalContext` | `src/cli/handlers/context.ts:68-71,125,290` |
| **File Read Gate** | Hook PreToolUse em `Read`: se o arquivo tem ≥ 32 KB e já tem observações, **nega** a leitura inteira e sugere `smart_outline`/`smart_unfold`. **Ligado por padrão** | `src/cli/handlers/file-context.ts:22-31,391` |
| **Tags `<private>`** | Conteúdo entre `<private>…</private>` é removido antes do LLM e do banco (no worker, ver [05](05-claude-mem-seguranca.md)) | `src/utils/tag-stripping.ts:6-20` |
| **Smart file tools** | `smart_search`, `smart_outline`, `smart_unfold` com tree-sitter (cerca de 25 gramáticas) | `mcp-server.ts:851,889,934` |
| **Viewer UI** | App React servido pelo worker com SSE ao vivo (`/stream`) | `ViewerRoutes.ts:168-172` |
| **Skills embarcadas** | 13 skills: mem-search, handoff, make-plan, learn-codebase… | `plugin/skills/` |

### 2.1 Exemplo de "compressão"

Entrada (evento `PostToolUse` de um `Bash`):

```text
<parameters>{"command":"pnpm test src/auth"}</parameters>
<outcome>FAIL src/auth/jwt.test.ts … expected 401, received 500 … TypeError: secret is undefined</outcome>
```

Saída esperada do observador (formato definido em `src/sdk/prompts.ts`):

```xml
<observation>
  <type>bugfix</type>
  <title>JWT test fails: secret undefined in test env</title>
  <facts>jwt.test.ts expects 401 but gets 500; JWT_SECRET missing in test setup</facts>
  <files_read>src/auth/jwt.test.ts</files_read>
</observation>
```

**Note o custo:** cada ferramenta usada gera **uma chamada de LLM**, e o conteúdo da ferramenta (inclusive o que
o agente leu de um arquivo) **sai da máquina** rumo ao provedor.

---

## 3. Arquitetura

```mermaid
flowchart LR
  classDef client fill:#dbeafe,stroke:#1d4ed8,color:#0b1b3a
  classDef svc fill:#dcfce7,stroke:#15803d,color:#052e16
  classDef store fill:#fef3c7,stroke:#b45309,color:#3a2200
  classDef ext fill:#fee2e2,stroke:#b91c1c,color:#450a0a
  CC[Claude Code / Cursor / Codex…<br/>hooks]:::client
  L[Hook CLI<br/>launcher → Bun]:::svc
  SP[(Hook spool<br/>JSON bruto)]:::store
  subgraph W["Worker · Bun + Express · 127.0.0.1:37700+uid%100"]
    WK[Rotas HTTP]:::svc
    BUF[Buffer em RAM<br/>por sessão]:::svc
    OBS[Dispatcher do<br/>LLM observador]:::svc
  end
  DB[(SQLite WAL + FTS5)]:::store
  CH[(Chroma<br/>uvx chroma-mcp)]:::store
  MCP[MCP server stdio<br/>19 tools visíveis]:::svc
  LLM[Anthropic Haiku (padrão)<br/>Gemini · OpenRouter · Ollama]:::ext
  PH[PostHog<br/>telemetria ON]:::ext
  CC e1@--> L --> SP
  L -->|nudge / inject| WK
  SP -->|drain| WK --> BUF --> OBS e2@--> LLM
  OBS -->|XML parseado| DB
  OBS --> CH
  MCP -->|HTTP| WK
  WK -. padrão ligado .-> PH
  e1@{ animate: true }
  e2@{ animate: true }
```

### 3.1 Hooks registrados no Claude Code (`plugin/hooks/hooks.json`)

| Evento | Modo | Efeito |
|---|---|---|
| `Setup` | síncrono, 300 s | checagem de versão (`bun install --production`) |
| `SessionStart` | assíncrono + síncrono | sobe o worker; `GET /api/context/inject` → `additionalContext` |
| `UserPromptSubmit` | síncrono, 15 s | `POST /api/sessions/init` |
| `PreToolUse` (Read/Bash/Grep/Glob) | síncrono, 15 s | File Read Gate: timeline do arquivo ou `deny` |
| `PostToolUse` / `PostToolUseFailure` | **assíncrono** | grava no spool + `POST /api/spool/nudge` (orçamento de 250 ms) |
| `Stop` | assíncrono | pede o resumo |
| `SessionEnd` | assíncrono | encerra a sessão |

### 3.2 Pipeline do worker

1. O spool é drenado no boot, a cada nudge, por `fs.watch` e por uma varredura de 30 s
   (`src/services/worker/hook-spool-drain.ts:67,81`).
2. Filtros: projetos excluídos, `CLAUDE_MEM_SKIP_TOOLS`, padrões de Bash, `<private>`.
3. O evento entra num **buffer em RAM** (`SessionMessageBuffer.ts:26-40`). Esse buffer substituiu a fila durável
   `pending_messages`, então um crash perde o que estava pendente. A recuperação depende do transcript.
4. O provedor é escolhido. No padrão é o Claude Agent SDK `query()` **com todas as ferramentas desligadas**
   (`src/sdk/hardened-options.ts:220-222`): um observador injetado não consegue executar nada.
5. XML parseado → SQLite → Chroma → (Cloud Sync opcional) → SSE para o viewer.
6. A busca vai **primeiro ao Chroma**; o SQLite só completa categorias vazias. Não há fusão de scores
   (`SearchOrchestrator.ts:96-135`).

---

## 4. Integração com harnesses (contada no código)

`npx claude-mem install --ide <id>` conhece **17 ids** (`src/npx-cli/commands/ide-detection.ts:56-153`).

| Nível | Quantos | Harnesses |
|---|---|---|
| Captura nativa + injeção | 12 | **Claude Code** (plugin, 8 eventos), Codex CLI, **Cursor**, Windsurf, Kimi, Antigravity, OpenCode, OpenClaw, OMP, Pi, DeepSeek Harness, Grok Bot (via transcript) |
| Só MCP (busca, sem captura) | 4 | Copilot CLI, Goose, Roo Code, Warp |
| Shim de nuvem | 1 | Claude Cowork (exige o serviço pago cmem.ai) |
| Carona em outro adaptador | 3–4 | T3 Code, Qoder, Qwen Code. **Gemini CLI não tem adaptador** |

Os detalhes de **Claude Code e Cursor** estão em [07](07-integracao-cursor-claude-code.md).

---

## 5. Dependência de LLM e custo

| Aspecto | Achado | Evidência |
|---|---|---|
| Obrigatório? | **Sim.** Observações e resumos só existem via LLM | `ResponseProcessor.ts:434` |
| Provedor padrão | `claude` via Claude Agent SDK, auth `subscription` (**a cota do seu plano Claude**), modelo `claude-haiku-4-5-20251001` `[verificado]` | `SettingsDefaultsManager.ts:400` |
| Alternativas | Gemini, OpenRouter, Codex, OpenAI-compatible (**Ollama, LM Studio, vLLM**), gateway CMEM Pro | `provider-dispatch.ts:59` |
| Fallback de cota | `CLAUDE_MEM_QUOTA_FALLBACK_PROVIDER: 'claude'` `[verificado]`: se o provedor escolhido falhar, o trabalho **vai para a Anthropic** quando existe um login Claude | `SettingsDefaultsManager.ts:463` |
| Custo | **1 chamada de LLM por evento de ferramenta** não ignorado + 1 por Stop. A latência documentada é de 5–30 s por observação. **O repositório não traz um número de tokens por observação** | `docs/public/hooks-architecture.mdx:521` |
| Rodar 100% local | Possível (openai-compatible + Ollama + `DO_NOT_TRACK`), mas não é o padrão. Modelos pequenos podem falhar no contrato XML estrito; a resposta é descartada após 1 retry | `prompts.ts:443` |

---

## 6. Vantagens para projetos agênticos

| # | Vantagem | Evidência |
|---|---|---|
| 1 | **Memória semanticamente rica sem esforço**: o LLM transforma ruído de ferramenta em fatos tipados (decisão, bugfix, descoberta) | `plugin/modes/code.json` |
| 2 | **Economia de tokens na injeção**: índice compacto no SessionStart e detalhes só sob demanda (progressive disclosure, alinhada a [01 §5.2](01-conceitos-memoria-agentes.md#52-context-engineering-compactação-e-progressive-disclosure)) | `mcp-server.ts:488-660` |
| 3 | **Hooks de escrita assíncronos** apoiados em spool: não bloqueiam o agente | `hooks.json` (async) |
| 4 | **Busca semântica + keyword** (Chroma + FTS5), viewer ao vivo, export/import, dedup | `SearchOrchestrator.ts` |
| 5 | **Observador isolado**: sem ferramentas, sem MCP, sem settings; uma injeção não vira execução | `hardened-options.ts:15-26,220-222` |
| 6 | **Ecossistema enorme**: 100 mil estrelas, comunidade grande, 12 harnesses com captura | §4 |
| 7 | **File Read Gate** pode poupar contexto ao evitar reler arquivos grandes já conhecidos | `file-context.ts` |

## 7. Limitações e custos

| # | Limitação | Evidência |
|---|---|---|
| 1 | **Custo de LLM por chamada de ferramenta**, consumindo a cota do seu plano Claude por padrão | §5 |
| 2 | **Egresso de conteúdo por padrão** (tool I/O ao LLM) + **telemetria PostHog ligada por padrão** | [05](05-claude-mem-seguranca.md) |
| 3 | **Runtime pesado**: worker residente (`CLAUDE_MEM_IDLE_EXIT_SEC='0'`), Python `chroma-mcp`, subprocessos do SDK, gramáticas nativas; o instalador roda `curl \| bash` para Bun e uv | `setup-runtime.ts:138-182` |
| 4 | **Defaults que mudam o comportamento do agente**: o Read Gate nega leituras. A própria eval do projeto mostra **+20% de custo no Opus** em um caso | `file-context.ts:22-31` |
| 5 | **Memória com perda e não determinística**: fila em RAM, XML inválido descartado, observação depende do modelo | `SessionMessageBuffer.ts:26-40` |
| 6 | **Sem esquecimento**: não há TTL nem decaimento; só deduplicação | relatório de segurança §4 |
| 7 | **Churn altíssimo**: várias releases por dia, mais de 150 settings, funil comercial (CMEM Pro) dentro do instalador | `install.ts:1213-1222` |
| 8 | **Fonte de verdade opaca**: banco SQLite/Chroma, não arquivos legíveis; uma observação envenenada é difícil de auditar | §3 |

## 8. Afirmações do projeto que não se confirmaram no código

| Afirmação | Veredito | Evidência |
|---|---|---|
| "Claude-mem does not collect telemetry." (`SECURITY.md:157`) | **FALSA**: PostHog ligado por padrão `[verificado]` | `src/services/telemetry/consent.ts:62` |
| "4 MCP tools" (README) | **Desatualizada**: 24 definidas, 19 visíveis por padrão | `mcp-server.ts`; `mcp-tool-visibility.ts` |
| Worker em `localhost:37777` (docs) | **Desatualizada**: a porta é `37700 + uid%100` `[verificado]` | `SettingsDefaultsManager.ts:403` |
| "Hybrid semantic + keyword search" | **Exagerada**: Chroma primeiro, FTS5 só completa, sem fusão de scores | `SearchOrchestrator.ts:96-135` |
| Fila durável `pending_messages` (docs) | **Desatualizada**: fila em RAM | `SessionMessageBuffer.ts:26-40` |
| "~10x token savings" | **Sem evidência** no código ou em benchmark | README |
| Sync hospedado fora do repo Apache | **Contradita**: `services/sync-api` e `workers/sync-hub` estão no repo | `docs/ip-boundary.md` |
| "Endless mode" | **Inexistente** neste commit | `grep -ri endless src` |
| Tags removidas "at the hook layer" (`SECURITY.md`) | **Falsa**: a remoção é no worker; o hook grava o payload bruto no spool | [05](05-claude-mem-seguranca.md) |

---

← [03 — ai-memory: segurança](03-ai-memory-seguranca.md) | [05 — claude-mem: segurança →](05-claude-mem-seguranca.md)
