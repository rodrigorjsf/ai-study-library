# Plan — Agentic Personas Pipeline (Idea → Discovery → PRD → Architecture → Tasks)

## Decisions (agreed with user)

- Language: **everything in English** (research doc + persona files).
- Contexts: **Discovery, PRD, Architecture, Tasks** + a master pipeline orchestrator with gates.
- Granularity: **complete, ~7–10 personas per context**; orchestrators activate only what a given idea needs.
- Research budget: **large workflow, ~15–25 agents**.

## Hard constraint discovered (drives the architecture)

Claude Code subagents **cannot spawn subagents** (`ai/docs/claude-code/subagents/creating-custom-subagents.md:47,295,666`).
Only an agent running as the **main thread** (`claude --agent <name>`) can delegate, restricted via `tools: Agent(a, b, …)`.

Consequence — orchestration topology:
- Each **context orchestrator** is a main-thread agent (`claude --agent discovery-orchestrator`, etc.) whose
  `tools` lists `Agent(<its workers>)`.
- The **pipeline orchestrator** cannot nest context orchestrators. Two options, to be decided by research +
  plan review: (A) pipeline orchestrator is a main-thread agent that delegates directly to *all* workers,
  stage by stage, using each context's playbook (embedded via `skills:`); or (B) stages are run as separate
  main-thread sessions chained through **on-disk handoff artifacts** (`docs/pipeline/<run>/01-discovery/…`)
  with the pipeline orchestrator acting as gatekeeper/integrator. Default lean: **B** (context isolation,
  resumable, auditable), with A documented as an alternative.
- Workers are plain subagents: read-mostly tools, write only their own artifact file, return a compact
  structured brief (not the whole artifact) to the orchestrator.

## Phase 1 — Raw research (Workflow, ~18–22 agents)

Stage 1 — parallel researchers (one per axis), each returns structured findings with citations:

1. Discovery & product strategy — Cagan (*Inspired*, *Empowered*, *Transformed*), Torres (*Continuous Discovery Habits*, Opportunity Solution Tree), Fitzpatrick (*The Mom Test*), Christensen/Ulwick (JTBD, ODI), Maurya (*Running Lean*), Osterwalder (Value Proposition / Business Model Canvas), Blank (Customer Development), Savoia (*The Right It*), market sizing (TAM/SAM/SOM).
2. PRD / requirements — PRD anatomy (Cagan, Amazon PR/FAQ "Working Backwards"), Shape Up (pitches, appetite), Lean UX hypotheses, Wiegers (*Software Requirements*), IEEE 29148, Volere, NFR catalogs (ISO/IEC 25010), success metrics (HEART, North Star, OKRs), Kano/RICE prioritization.
3. UX / design / accessibility & content — Nielsen heuristics, WCAG 2.2, service design, user journey mapping.
4. Architecture core — Richards & Ford (*Fundamentals of SA*, *SA: The Hard Parts*), Bass/Clements/Kazman (*SA in Practice*, ATAM, quality attribute scenarios), Rozanski & Woods (viewpoints/perspectives), C4 (Brown), arc42, ADRs (Nygard), evolutionary architecture/fitness functions, Hohpe (*The Software Architect Elevator*).
5. Domain & data — DDD (Evans, Vernon, *Learning DDD* Khononov), Event Storming (Brandolini), data modeling, Kleppmann (*DDIA*), API design (API-first, OpenAPI, Lauret *Design of Web APIs*), integration patterns (Hohpe/Woolf).
6. Cross-cutting quality — security (OWASP ASVS, STRIDE/threat modeling, Shostack), privacy/compliance (LGPD/GDPR, privacy by design), reliability/SRE (Google SRE books, SLOs), observability, performance/capacity, cost/FinOps, AWS/Azure/GCP Well-Architected pillars.
7. Delivery planning / tasks — Patton (*User Story Mapping*), Cohn (*User Stories Applied*, *Agile Estimating*), INVEST, SPIDR splitting, vertical slicing / walking skeleton (Cockburn), BDD/Gherkin, Adzic (*Specification by Example*, *Impact Mapping*), DoR/DoD, dependency/critical path, Reinertsen (*Principles of Product Development Flow*), *Accelerate*/DORA.
8. Test strategy & QA — Crispin & Gregory (*Agile Testing*), test pyramid/trophy, risk-based testing, contract testing, acceptance test design.
9. Multi-agent role design — MetaGPT (SOP roles), ChatDev, AgentVerse, CAMEL, Anthropic "Building effective agents" + multi-agent research system, orchestrator-workers / evaluator-optimizer, LLM-as-judge, reflection/critic patterns, failure modes of multi-agent systems (MAST taxonomy), plus this repo's `ai/docs/` corpus (spec-driven development, harness engineering, subagent best practices).
10. Review / challenge roles — red team, devil's advocate, pre-mortem (Klein), Six Thinking Hats, design review / architecture review boards, "disagree and commit", what makes a reviewer *refuse* (gates, blocking criteria).
11. Real-world org roles & RACI — which roles exist in real companies at each stage (PM, PMM, UX researcher, designer, tech lead, staff engineer, solution/enterprise architect, security architect, SRE, data architect, QA lead, delivery manager/TPM, EM), their mindsets, accountability boundaries, handoffs.
12. Claude Code subagent authoring — frontmatter fields, description-triggering, tool scoping, `--agent` main-thread orchestration, skills preload, output contracts, prompt best practices (from repo corpus + official docs).

Stage 2 — adversarial verification (per researcher, pipelined): check citations exist and claims match sources; flag UNVERIFIED.

Stage 3 — synthesis agent: role catalog per context (dedupe, merge, assign responsibilities, inputs/outputs, acceptance + refusal criteria, handoff contracts) → structured JSON consumed by Phase 2.

## Phase 2 — Consolidation (files in repo)

- `dev/research/2026-10-02-agentic-pipeline-personas-research.md` — raw research, verified, with sources.
- `ai/agents/product-pipeline/` (new folder):
  - `README.md` — pipeline overview, topology (diagram), how to run (`claude --agent …`), handoff artifact layout, gate rules, RACI matrix.
  - `pipeline-orchestrator.md`
  - `discovery/` — `discovery-orchestrator.md` + workers
  - `prd/` — `prd-orchestrator.md` + workers
  - `architecture/` — `architecture-orchestrator.md` + workers
  - `tasks/` — `tasks-orchestrator.md` + workers
  - Note: Claude Code loads `.claude/agents/` recursively? → verify; if not, README documents flattening/install step.

### Persona file template (each worker)

```yaml
---
name: <context>-<role>            # lowercase-hyphen, unique
description: <when to delegate — trigger-oriented, mentions inputs/outputs>
tools: Read, Grep, Glob, Write    # least privilege; WebSearch/WebFetch only where research is the job
model: opus | sonnet | haiku      # by reasoning depth
maxTurns: <n>
---
```
Body sections: Identity & mindset · Mission · Scope (owns / does NOT own) · Inputs required · Process (steps) ·
Output contract (artifact path + return brief schema) · Acceptance criteria (checklist) ·
**Refusal criteria** (blocking: return `status: rejected` with reasons instead of producing work) ·
Anti-patterns · Collaboration/handoffs · References.

Orchestrators add: roster & activation rules, delegation protocol, consolidation, gate checks,
conflict resolution, iteration limits, escalation to human.

## Phase 3 — Verification

- [ ] Every persona file parses (YAML frontmatter valid; `name` unique; required fields present).
- [ ] Every orchestrator's `Agent(...)` list matches existing worker names.
- [ ] Every worker has ≥1 acceptance and ≥1 refusal criterion; every artifact referenced as input is produced upstream.
- [ ] Independent review agent audits the set (gaps, overlaps, contradictions) → fix.
- [ ] Update root README (structure section), commit, push to branch, offer PR.

## Advisor review — changes adopted (supersede conflicting text above)

a. **Topology B confirmed.** The "pipeline orchestrator" becomes **`pipeline-gatekeeper`**: main-thread agent that
   reads `docs/pipeline/<run>/0N-<stage>/`, checks gate criteria + traceability, writes a gate verdict and the
   next-stage brief. Stages are chained by the human or a small shell script
   (`claude --agent discovery-orchestrator` → `claude --agent pipeline-gatekeeper` → …). Option A documented only
   as "lite mode" with a reduced roster.
b. **Layout:** source in `ai/agents/product-pipeline/<context>/`, but every file has a **globally unique,
   context-prefixed name** (filename = `name`). README gives a flat install (`cp`/`ln -s` into `.claude/agents/`).
   Recursive loading of nested folders is **unverified** → test empirically in Phase 3 and record it.
c. **Roster size (reconciles user's "complete" with advisor's over-scoping warning):** 5–7 **core** personas per
   context + a **shared cross-cutting pool** (security, privacy/compliance, accessibility/UX quality, SRE/operability,
   FinOps, analytics) defined once and invoked by any stage → effective 7–10 per context, no duplication.
   Each context also gets a **stage critic/red-team** (evaluator-optimizer) and the pipeline gets a
   **traceability owner** (opportunity → requirement → ADR/quality scenario → task).
d. **Refusal taxonomy** in every persona: `blocked` (missing/insufficient input), `rejected` (upstream work fails
   gate), `out_of_scope`; plus max-iteration limits and escalate-to-human rules.
e. **Research axes merged → 9 researchers:** delivery+test merged; org roles/RACI folded into every axis as a
   required `roles[]` output (mindset, accountabilities, acceptance, refusal); multi-agent + subagent-authoring
   mostly local corpus reads.
f. **Handoff artifact schemas** (frontmatter + required sections per artifact) produced by the integrator; Tasks
   output aligned with `ai/docs/spec-driven-development` (spec → plan → tasks) so coding agents can consume it.
   Explicit in/out decisions: product analytics (in, shared pool), legal/compliance (in as privacy/compliance
   reviewer, no legal advice), GTM/PMM (out — documented as extension point).
g. **Phase 3 adds a dry run** on a toy idea through Discovery → PRD (incl. a deliberately underspecified idea to
   confirm refusals fire).
h. `Write` can't be path-limited → write-path rule is **instruction-level**, with an optional PreToolUse hook
   example in the README.
i. **Models:** sonnet default; opus for orchestrators, gatekeeper, critics; no haiku for judgment roles.

**Workflow (~17–20 agents):** 9 researchers → 3 batched citation verifiers (claims/citations only) →
4 per-context synthesizers → 1 integrator (dedupe, shared pool, RACI, schemas, traceability) → (Phase 2)
4 per-context writers using a fixed template → 1 cross-set auditor.

## Checklist

- [x] Plan reviewed by advisor agent (NEEDS CHANGES → adopted a–i)
- [x] User go-ahead
- [x] Phase 1 workflow run (18 agents)
- [x] Research doc written
- [x] Persona files written (35 + conventions skill + rubrics + scripts)
- [x] Verification + review fixes (lint, audit, Discovery dry runs)
- [x] README + commit/push (PR #2)

## Review

**Delivered:** 9 verified raw research notes, 5 syntheses, an integrated report (`dev/research/2026-10-02-agentic-pipeline-personas-research.md`), and 35 Claude Code subagents in `ai/agents/product-pipeline/`. Also a preloaded conventions skill, default exit rubrics, `trace_check.py`, and the install, run-stage and lint scripts.

**Static verification:** lint reports 35 personas, 0 errors and 3 length warnings (on the Discovery, Architecture and Tasks orchestrators). The audit pass fixed 6 cross-file inconsistencies.

**Dry runs** (headless `claude -p --agent discovery-orchestrator` in a scratch project):
1. **Vague idea:** BLOCKED at the entry gate (E-D2, E-S1..S4). No worker ran and nothing was invented. ✅
2. **Well-specified idea, first run:** the full stage ran (7 workers, 5 shared reviewers, 2 review rounds). It then blocked because `trace_check` was not shipped. → **Fixed:** the script now ships with the skill.
3. **Vague idea, second run:** the old entry stub would have triggered the re-entry path. → **Fixed** with §1 rule 8 (`blocked_at: entry`). The second run archived the stub and blocked again correctly. ✅
4. **Well-specified idea, resumed:** traceability reported 0 blocking gaps. Critic round 1 ran as two independent samples. The verdict was HOLD because human-only decisions were still open (kill thresholds, DPO protocol). That is correct: no human decision was invented. ✅

**Other gaps found and fixed:** the exit rubrics were referenced but never shipped (now `gates/`, seeded by `install.sh`). The skill described write-scope and Stop hooks that do not exist; it now says these rules are instruction-level and the hooks optional.

**Not yet exercised:** the PRD, Architecture and Tasks stages end to end. Running them needs a human go/kill decision on the Discovery output. `trace_check.py` rules for PRD, Architecture and Tasks have only been tested on synthetic fixtures.


## User clarification (2026-10-02)

Each stage has its **own orchestrator**, executed at **different times in fresh sessions/windows**.
→ Gate duties live inside each stage orchestrator: **entry gate** (validate upstream handoff on disk; refuse with
`rejected`/`blocked`) + **exit gate** (stage critic + own checklist before writing the handoff).
`pipeline-gatekeeper` is dropped as a required role; traceability owner stays as a shared worker.
Handoff files on disk are the only memory between stages → their schemas must be self-contained.

---

# Plan — Cursor Agent SDK workflows: relatório + starter kit (2026-11-11)

## Decisions (agreed with user)

- Idioma: **pt-BR**. Local: `ai/study/cursor-agent-sdk-workflows/`.
- Entrega: **blueprint + snippets** (código de referência; sessão sem acesso a cursor.com nem conta Cursor).
- Linguagem do runtime: **TypeScript**. Invocação principal: **MCP server + CLI** sobre o mesmo runtime.
- Eixo central: comparação com Claude Code dynamic workflows (`ai/docs/claude-code/workflows/workflows.md`).
- Considerar `.agents/` além de `.cursor/` e `.claude/` (pedido do usuário).

## Steps

- [x] Rodar `/deep-research` (Cursor SDK, auth/billing, invocação, exemplos)
- [x] Espelhar doc oficial de workflows do Claude Code
- [x] Levantar superfície exata da API do Cursor SDK (agente focado, pacote npm 1.3.1)
- [x] Escrever `00-relatorio-pesquisa.md`
- [x] Escrever `starter-kit/` (runtime, MCP, CLI, implement-issue, skills, docs 01–07, testes)
- [x] Revisão independente (advisor) e correções
- [x] Reestruturar para `.agents/` (skills, workflows do repo, AGENTS.md, link para Claude Code)
- [x] Commit + push em `claude/keen-faraday-yoqwhs`
- [x] Custos e cache: doc 08, memo entre runs, `settingSources` por etapa, uso por tipo de token, etapa de
      otimização de custo obrigatória na `/skill-to-workflow`, práticas na `workflow-authoring`

## Review

- Verificado: `tsc --noEmit` contra `@cursor/sdk@1.3.1` real; 8 testes offline (fake SDK) passam; MCP
  server exercitado por stdio (list/start/status, guarda de recursão); CLI `start`/`wait`/órfão testado num repo
  temporário; links relativos e diagramas Mermaid validados.
- Não verificado: nenhuma execução contra a API real do Cursor (cursor.com bloqueado; sem conta).
- Correções da revisão: checagem de fallback de modelo removida (o SDK devolve o modelo pedido); review exigido
  que falha encerra o run; guarda contra workflow recursivo; handlers de crash e jobs órfãos; runId gravado no
  início + resume pelo MCP; custo lido também em falha/timeout; worktree/commit/PR idempotentes; `wf login` não
  imprime a chave; MDM carregado; doc de segurança alinhada ao código; afirmações rebaixadas para [S]/[I].
- Custos/cache (pedido posterior): o SDK não expõe controle de prompt caching (só mede cache read/write); o kit
  favorece o cache (prefixo estável, conversas curtas), mede `cacheHitRatio` e economiza onde controla (código em
  vez de modelo, memo entre runs, contexto mínimo por etapa). 12 testes offline passam. Preços e relatos de
  fórum marcados [S]: cursor.com/forum/arxiv inacessíveis nesta sessão.

---

# Plan — Observabilidade V1 do starter kit (2026-11-11)

## Decisions (agreed with user)

- SQLite **por usuário**: `~/.cursor-workflows/metrics.db` (todos os repos; coluna `repo`). `WF_METRICS_DB` sobrescreve; `WF_METRICS=off` desliga.
- Dashboard **localhost sem dependências**: `node:http` + página com SVG gerado no cliente; API JSON.
- Prompts: **só hash + tamanho** (texto completo só com `WF_METRICS_STORE_PROMPTS=1`, para depuração local).
- Time: **local + export** CSV/JSON (`--anonymize` opcional); OTel fica para V2.
- Lib: `node:sqlite` (Node ≥ 22.13, já exigido pelo SDK); zero dependência nova.

## What the SDK gives (verified in @cursor/sdk 1.3.1 .d.ts)

- Por turno: `onDelta` → `turn-ended.usage` {input, output, cacheRead, cacheWrite, reasoning}; prompt do turno = input+cacheRead+cacheWrite (proxy de ocupação da janela).
- `summary-started/completed` (compactação de contexto), `step-completed.stepDurationMs`, `tool-call-started/completed`.
- `getUsage()` → total + `runs[]` por turno (local) com `cost.chargedCents/rawCostCents` (0 se incluído no plano; pode atrasar).
- Não há tamanho de janela nem preço no SDK → tabela `pricing` editável (Haiku 5.5: US$0,10/0,50 até 100k, 0,50/2,50 acima — tarifa da API Anthropic; repasse no Cursor não confirmado).

## Design

1. `src/observability/db.ts`: abre/migra o banco (`schema_version`), WAL, `busy_timeout` (MCP + CLI concorrentes).
2. Tabelas: `runs`, `steps` (uma linha por tentativa), `turns`, `metrics` (ctx.metric), `pricing`.
3. Engine emite eventos mais ricos (run-start/run-end, step-start com stepId/params/tools/settingSources, `turn`, `summary`, `tool-call`, step-end com errorKind/turns/peakPrompt/schemaReprompts/rawCents); `ctx.metric(name, value)`; convenção `result.status` → `runs.outcome` ("done" = entregue).
4. `src/observability/recorder.ts`: assina os eventos e grava; falha de gravação nunca derruba o workflow.
5. `pricing.ts`: estimativa por turno com faixa de contexto (turno acima do limite usa a tarifa alta); `est_cents` ao lado de `charged_cents`.
6. Views SQL: custo por workflow/modelo/esforço; custo por entrega; taxa de sucesso/retry/reprompt; economia memo/journal; cache por modelo; **custo e output por faixa de prompt (25k)**; turnos acima da faixa; etapas com muitos turnos e baixa entrega.
7. CLI: `wf stats`, `wf metrics export`, `wf pricing list|set`; `npm run dash` (porta 4317).
8. Docs: `docs/09-observabilidade.md`; links em README/08/03; skills (authoring: `ctx.metric` + `status`; converter: definir métricas de entrega); relatório §5.2.
9. Testes offline: fake SDK emite `turn-ended`; verifica linhas no banco, views, estimativa com faixa, export, falha de gravação não derruba run.

## Revised after advisor review (verified in the SDK bundle)

- `turn-ended` = uso de um **turno inteiro do agente** (vários passos/chamadas ao modelo), não de uma chamada:
  `input+cacheRead+cacheWrite` é volume cobrado, não ocupação da janela. Proxy rotulado: `avg_prompt_per_step =
  prompt / passos` (limite inferior do contexto por chamada); faixas de 25k sobre ele. Faixa de preço por turno: cortada.
- Custo: **`rawCostCents` do Cursor é o sinal principal** (`chargedCents` é 0 para uso incluído); `pricing` só como
  fallback calculado em consulta. Custo por token × faixa de contexto revela empiricamente se a faixa do Haiku é repassada.
- `getUsage().runs[]` vai para tabela própria (`usage_runs`), sem junção por posição com turnos; total da tentativa é a
  verdade; `unattributed` como sinal. `cost_final` + `wf metrics reconcile` (`Agent.getUsage(agentId)` estático).
- Linhas de tentativa só inseridas (nunca upsert de totais); runs retomados = nova execução (`exec_id`) do mesmo `run_id`;
  hits de journal/memo viram linhas de custo zero com `cached`.
- `outcome_status` cru + `outcome_class` (delivered/failed/error/unknown) + `human_verdict` (`wf metrics mark`); custo por
  entrega = gasto total / entregas.
- Privacidade: label default vira hash; args e repo por hash (+ nome da pasta); sem e-mail; export anonimizado por
  padrão; dir 0700 / arquivo 0600; dashboard só 127.0.0.1, checa Host, sem CORS, banco read-only.
- SQLite: WAL, `busy_timeout`, escrita em `BEGIN IMMEDIATE`, migração por `PRAGMA user_version`; `node:sqlite` carregado
  por import dinâmico só com métricas ligadas; filtra apenas o ExperimentalWarning do SQLite. Avisar sobre WAL em
  /mnt/c e rede.
- Correlação: `model_key` canônico (id + params ordenados), hash da versão do workflow, covariável de dificuldade via
  `ctx.metric` (ex.: tier), cache read separado.
- Cortes V1: sem `wf pricing set` (tabela seed + SQL), tool calls agregadas por nome, dashboard com 4 painéis.

## Steps

- [x] Advisor review deste plano
- [x] Implementar 1–7 com testes (21 testes offline passam)
- [x] Docs e skills (8): docs/09, README, 03/07/08, workflow-authoring, skill-to-workflow, AGENTS.md, relatório §5.2
- [x] Verificação: typecheck; `wf stats` e receitas SQL contra banco de demonstração; dashboard via curl (403 para
      Host estranho, sem CORS) e Playwright (claro/escuro/mobile, sem erros nem overflow); MCP smoke
- [x] Commit/push

## Review (observabilidade)

- Revisão do plano mudou o que o schema mede: `turn-ended` = turno inteiro (não chamada); custo bruto do Cursor
  como sinal principal; `usage_runs` sem junção por posição; inserções sem upsert; privacidade (label hash, export
  anonimizado, 0600, dashboard 127.0.0.1 + Host).
- Não verificado: execução contra a API real; `Agent.getUsage(agentId)` para agentes locais já descartados
  (reconcile informa falhas); repasse da faixa de preço do Haiku no Cursor (o banco mede empiricamente).

---

# Plan — Validate locally and publish `cursor-workflows-starter` (2026-11-11)

Source prompt: `ai/study/cursor-agent-sdk-workflows/PROMPT-publicar-repositorio.md` (commit `81d7356`).

## Decisions (agreed with user)

- Repo `rodrigorjsf/cursor-workflows-starter` (name free; distinct from the private Go `cursor-workflow-orchestrator`).
  Public, MIT, `package.json` keeps `"private": true`.
- `README.md` in pt-BR + short `README.en.md` with a "docs are pt-BR" banner.
- Public scope: kit + research report in `docs/research/`; third-party doc mirrors replaced by official URLs with
  access date; the publish prompt is cited only in `PROVENANCE.md`.
- Provenance: the 7 study commits **plus `81d7356`** (the publish prompt).
- History: one clean initial commit citing the SHAs.
- Paid tests: US$ 2.00 total; every block announced with an estimate and run only after the user's "ok";
  every run with `--max-cents` **and** `--max-tokens`; `WF_METRICS_DB=~/tmp/wf-verify.db`.
- Credential: user runs `NO_OPEN_BROWSER=1 npm run wf -- login` in their own terminal; agent only checks
  `whoami` and file mode; key revoked in the dashboard at the end.
- Sandbox: agent creates private `rodrigorjsf/wf-sandbox` (tiny Node project + test + issue `complexity:low`);
  end-to-end run with `openPr: true` to prove resume idempotence.
- Back to ai-study-library: direct commits on `main`; doc mirrors in their own commit.
- Node: `mise install node@22` (latest 22.x), used only via `mise exec`; global default untouched
  (default is 22.11.0 < 22.13 and its npm is broken).
- Windows-side checks (Cursor IDE MCP/skills, dashboard in the Windows browser): guided checklist run by the user.
- **Account:** user creates a **personal Free** account for Phase 2 (decided 2026-11-11 after Phase 1: the docs do
  not say whether the SDK runs on Free; legacy Start, a paid plan, excludes it). Work Enterprise (non-admin) is not
  used; admin-only items stay open questions for the admin pitch.

## Findings absorbed before any spend

- Budget cap ignores plan-included usage: `engine.ts:311-314` adds only `chargedCents` (0 when included).
  Fix test-first: cap counts `rawCostCents`, falling back to `chargedCents`; update docs 02 §3 and 07.

## Working trees

- `~/tmp/wf-kit-check`: pristine copy of the kit, local git baseline, fixes as local commits (diff review only).
- `~/tmp/wf-docs-live/`: live doc pages (untrusted data).
- `~/code/cursor-workflows-starter`: assembled in Phase 4 from the fixed tree.
- The kit in this repo stays a snapshot; the study README points to the new repo as the maintained version.

## Steps

- [x] Phase 1.1 Environment evidence (node/npm via mise 22.x, gh, git, Cursor IDE build, filesystem)
- [x] Phase 1.2 Clean install: `npm ci` (platform binaries), typecheck, tests (expect 21)
- [x] Phase 1.3 Live docs: discover real paths (`llms.txt`/sitemap), fetch, log 404s; Workflow with one
      refutation-biased verifier per [S]/[I] claim citing the fetched line; forum topics from doc 08
- [x] Phase 1.4 Refresh mirrors in `ai/docs/cursor/` (commit `4aaa4f8`; root `docs/cursor/` left alone: syntheses, `ai/docs` wins)
- [x] Ask the Phase 2 account question with Phase 1 evidence
- [x] Pre-spend fix: budget cap on max(raw, charged) (test-first); also zod ^4.6.7 (GHSA-mrhx-c7xc-m3w5)
- [x] Doc corrections from the 74 doc verdicts (workflow), then Phase 2 corrections
- [x] Phase 2 paid blocks on Premium (Blocks 1, 3–7, 9, 10); ~US$ 0.36 estimated; IDE/Windows checks pending
- [x] Phase 3 repo structure → user approval → independent review
- [x] Phase 4 assemble, validate (npm ci/typecheck/test, links, gitleaks), confirm, publish, CI green, release v0.1.0
- [x] Phase 5 back-port link and summary here; Review section

## Phase 3 — public repository plan (agreed with user 2026-11-11)

Source tree: `~/tmp/wf-kit-check` (kit at a69f2a2 + local fixes, 31 offline tests). Target: `~/code/cursor-workflows-starter`.

Decisions:
- Include the verification workflows under `scripts/verify/` with a setup script for a throwaway probe repo, run via
  `WORKFLOWS_DIR=scripts/verify`.
- Release `v0.1.0` as a **pre-release**: SDK and end-to-end verified on Premium; Cursor IDE invocation unverified.
- MIT license, holder "Rodrigo França". One bug issue template asking plan, model and SDK version.
- `verificacoes-locais.md` gets the 74 doc-claim verdicts in pt-BR with official URLs and access date.

Structure:
- Root: README.md (pt-BR, honest status, quick start, safety warning), README.en.md, LICENSE, CHANGELOG.md, PROVENANCE.md
  (8 commits incl. 81d7356, both sessions, primary sources with access date), SECURITY.md, AGENTS.md, CLAUDE.md,
  package.json (private), package-lock.json, tsconfig*.json, .gitignore, .gitattributes (`* text=auto eol=lf`),
  .node-version.
- .agents/skills, .agents/workflows/README.md, .cursor/mcp.json, .mcp.json, src/, workflows/, test/, scripts/,
  docs/01..09 + docs/img, docs/research/{relatorio-pesquisa.md, verificacoes-locais.md}.
- .github/workflows/ci.yml (ubuntu, Node 22.x, npm ci, typecheck, test, `permissions: contents: read`, no secrets),
  .github/ISSUE_TEMPLATE/bug.md.

Rules:
- No third-party doc mirrors; every link leaving the kit points to an official URL (with access date) or to
  ai-study-library at a69f2a2.
- Never commit .workflows/, metrics-export/, *.db, auth.json or keys; gitleaks + git grep for crsr_/sk-/token shapes.
- Commits authored with the GitHub noreply email; one clean initial commit citing the SHAs and PROVENANCE.md.

## Phase 4 — assemble, validate, publish

- [x] Independent multi-lens review of this plan; apply adjustments; show them to the user
- [x] Docs: 74-claim table in verificacoes-locais.md; link rewrite in relatorio-pesquisa.md; README status; CHANGELOG
- [x] Assemble ~/code/cursor-workflows-starter; npm ci, typecheck, test; relative-link check; gitleaks; clean status
- [x] Show summary and ask for confirmation before `gh repo create --public`
- [x] Push, topics, CI green, pre-release v0.1.0

## Adjustments from the independent review (4 lenses, 33 findings, 2026-11-11)

Code (test-first where testable):
- Node floor: `queries.ts` uses `?1` numbered params that break `npm test`/`stats`/`dash` on Node 22.13–22.19;
  bind plain `?` twice; regression test; CI matrix `["22.13.0", "22.x"]`; `.node-version` = `22`.
- `implement-issue`: before commit, fail if staged content has secret shapes (`crsr_`, `sk-`, the saved key) or
  files named `auth.json`/`.env*` (an injected LOW/MED step skips review and its diff is pushed).
- `workflow.ts` sandbox JSDoc: reads are NOT restricted; writes limited for shell calls; needs bubblewrap; untested.
- Startup check of `process.versions.node` in `cli.ts` and `mcp-server.ts` (the IDE may spawn another Node).
- `setup-probe-repo.sh`: pass paths via env (spaces); new `scripts/verify/setup-sandbox-repo.sh` so the end-to-end
  numbers can be replicated (Cursor ToS: published benchmarks must be replicable).

Docs sweep (grep against verificacoes §1–§11 before assembly):
- grok-4.7 did run (MED, no params) in the e2e `corrigir-1`; only the HIGH/REVIEW variant is unexecuted.
- Sandbox: untested, needs bubblewrap, does not restrict reads, may not cover `edit`; the out-of-repo write goes into
  docs/07, README and SECURITY.md; SCOPE_RULE is advisory only.
- "Gasto limitado" is not a guarantee: one step is unbounded; the cents cap is inert when getUsage is unavailable.
- The recursion guard protects against accidents; it is not a security boundary.
- Supported OS: tested only on Linux x64 (WSL2); implement-issue needs bash.
- Claude Code side: name the PreToolUse matcher for `mcp__workflows__start_workflow`; separate MCP-registration
  nodes for Cursor and Claude Code in the 03/04 diagrams.
- §11: forum rows paraphrased (no verbatim post text, no usernames); at most one short quote per row.
- New §12 "Não executado": IDE MCP/skills/`/run-workflow`, Windows-browser dashboard, sandbox, MED/HIGH/review
  paths, team/MDM and `~/.claude` hooks, admin policies, monthly cap, Haiku context tier (needs credit).
- Environment line per block (plan, SDK 1.3.1, model, settingSources; the 58 skills came from the author's machine).

New files content:
- README Status: date, SDK version, plans tested (Free blocked, Premium works), Linux/WSL2 only, test count from the
  final run, what was measured (links to §), the e2e scope (LOW only), the incident, pending list from §12.
- SECURITY.md: never-commit list; incident + advisory SCOPE_RULE; auth.json plaintext 0600, 90 days, readable by any
  step, revoke after testing; `project` settings run the target repo's hooks/MCP; sandbox caveats; private reporting.
- LICENSE MIT + note that `@cursor/sdk` is proprietary (Cursor ToS, paid plan); `"license": "MIT"` in package.json.
- .gitignore: `*.db`, `*.db-wal`, `*.db-shm`, `*.sqlite*`, `auth.json`, `.env`, `.env.*`, `.probe/`, `.claude/skills/`.
- Bug template with a redaction notice (no key, whoami output, metrics.db, unanonymized exports).
- Report sources: official URL first, ai-study-library@a69f2a2 snapshot second.

Assembly and gates:
- `git -c core.autocrlf=false archive` into ~/code/cursor-workflows-starter; `git init -b main`; .gitattributes
  before the first add; local user.email = GitHub noreply; check `git log --format="%ae %ce"` before push.
- Gates: npm ci/typecheck/test on 22.13.0 and 22.23.4; link check; gitleaks; PII grep (home paths, hostnames, emails
  other than noreply); clone with `core.autocrlf=true` and assert `w/lf`.
- After `gh repo create`: enable private vulnerability reporting; topics; CI green; pre-release v0.1.0 with notes
  built from §12.
- Entrega final: repo/release URLs, CI conclusion, counts per section, cost as list-price estimate (35,33 ¢ in the
  DB + ~0,82 ¢ probes; cost_source=estimate), pending list.
- Phase 5: fix tasks/lessons.md (RunResult.model), banner on the study's starter-kit/README.md and report
  (superseded snapshot, known defects), commit and push.

Open for the user: re-run the LOW end-to-end on the exact tree to publish (est. 2–30 ¢); publish with the IDE and
Windows checks pending (pre-release) or wait for them.

## Review (publish cursor-workflows-starter, 2026-11-11)

- Published: https://github.com/rodrigorjsf/cursor-workflows-starter (public, MIT, topics, private vulnerability
  reporting on); initial commit cb16a2b; CI green on Node 22.13.0 and 22.x; pre-release
  https://github.com/rodrigorjsf/cursor-workflows-starter/releases/tag/v0.1.0.
- Live docs: 74 claims checked (27 confirmed, 38 partial, 3 refuted, 6 inconclusive); mirrors refreshed in
  ai/docs/cursor (4aaa4f8); root docs/cursor left alone.
- Real API: the Free plan blocks the SDK (plan_required on Agent.create); Premium works. Measured: RunResult.model is
  the resolved id, inputTokens includes cache, settingSources is opt-in for AGENTS.md/hooks/MCP, a Claude Code
  PreToolUse deny is honored in SDK runs, getUsage is feature_unavailable for local agents even on Premium.
- Kit bugs fixed (35 offline tests): recursion guard, cents cap (raw vs charged; getUsage fallback), token formulas,
  npm run models, Node 22.13–22.19 SQL, login-shell tests, model defaults; added secret gate, plan_required abort,
  Node check, resolved model in schema v2, verify scripts.
- Incident: an unsandboxed fix step edited the mise npm wrapper outside the repo; reverted on request; the final e2e
  on the published tree (wf-sandbox PR #6, repo now public) wrote nothing outside the repo.
- Spend: 39.64 ¢ list-price estimate in ~/tmp/wf-verify.db + ~0.82 ¢ probes; the real charge is only on the dashboard.
- Pending (verificacoes §12): Cursor IDE MCP/skills/run-workflow, Windows browser dashboard, sandbox, MED/HIGH paths,
  team/MDM hooks, admin policies, monthly cap, macOS/Windows.

---

# Plan — `implement-issue` follows the mattpocock tdd / codebase-design / code-review / pr skills (2026-11-11)

Repo: `~/code/cursor-workflows-starter` (public). Work on branch `feat/implement-issue-skills`, PR to `main`
(PR body written with the `pr` template), CI green, merge only with the user's ok, then pre-release `v0.2.0`.
Source skills: mattpocock-skills 1.3.1 (MIT, Matt Pocock); the `pr` template credits `show-me` (Dex Horthy).
Instructions are paraphrased in pt-BR, not copied; credits go to a `CREDITS.md` and the docs.

## Decisions (agreed with user)

- Seams (tdd "confirm seams with the user"): MED/HIGH run twice. Run 1 plans, comments the seams on the issue
  (idempotent marker) and returns `status: "seams-proposed"`; run 2 is `--resume <runId>` with `approveSeams: true`
  (or `seams: [...]` edited), so the planner replays from the journal. LOW is automatic (one slice).
- Review always runs, with three separate axes in parallel: Standards and Spec (code-review skill) plus Security.
  Reports stay separate, never merged or re-ranked.
- HIGH uses "Design it twice": 3 read-only designers with different constraints + a judge that picks or combines.
  MED uses one planner with the codebase-design vocabulary.

## Flow (code decides; agents do one small task each)

1. Triage (code): issue, tier by label or classifier (unchanged). Code lists context files that exist
   (`GLOSSARY.md`, `docs/adr/`, `CODING_STANDARDS.md`, `CONTRIBUTING.md`, `AGENTS.md`) and passes the paths.
2. Plan: LOW none (one implicit slice); MED planner; HIGH 3 designers in `ctx.parallel` + judge (fails with
   `design-failed` if fewer than 2 designs). Output `{seams[], slices[{behavior, seam, testIdea}], testCommand}`.
   Slice caps: LOW 1, MED 3, HIGH 5 (dropped slices logged). Seam approval as above.
3. TDD loop per slice (code-enforced red → green):
   - before each step the code stages everything, so `git diff` + untracked = files the step touched;
   - `teste-N`: write ONE test at the seam through the public interface; only test files may change
     (`testGlobs` arg, sensible default) → else one retry, then `tdd-violation`;
   - code runs the tests: they must FAIL (red) → if green, one retry, then `test-not-red`; keep the red output;
   - `codigo-N`: minimal code to pass; test files may not change → else one retry, then `tdd-violation`;
   - code runs the tests: must pass, up to 2 fix rounds (no test edits) → else `tests-failed`; keep green output.
4. Review (always): diff since the worktree base computed by code and passed in the prompt (truncated); reviewers
   get read-only tools, no shell. Standards = repo standards files + Fowler smell baseline (judgement calls, repo
   overrides); Spec = the issue (missing / scope creep / wrong, quoting the issue); Security. Blocking = Standards
   `hard`, Spec `missing`/`wrong`, Security `blocking`. One fix/refactor round (tests must stay green), re-review
   only the axes that blocked; still blocking → `review-blocking`. Non-blocking findings go to the PR body.
5. PR (pr skill): cheap agent writes Summary (smallest visual) + Merge Danger (door, blast radius); code assembles
   the template with Evidence = real red → green outputs per slice, plus non-blocking review findings; secret gate;
   commit; push; PR (idempotent: skip if it exists).
6. Statuses: `done`, `seams-proposed`, `design-failed`, `tdd-violation`, `test-not-red`, `tests-failed`,
   `review-failed`, `review-blocking`, `tests-failed-after-review`, `secret-blocked`. Metrics per slice and per axis.

## Tests (test-first, fake SDK, fake `gh` on PATH, temp git repo, real `node --test` as the test command)

LOW happy path (red, green, 3 axes, PR body with Evidence); MED seams-proposed then resume with approveSeams
(planner not re-run, comment not duplicated); red step touching non-test file; test not red; green step touching
tests; review blocking → fix → clean; review still blocking; HIGH runs 3 designers + judge. Existing 35 stay green.

## Real-API checks (cost policy: plan-included models; caps on every run)

`wf-sandbox`: one LOW issue (est. 250–400k tokens) and one MED issue in two runs (est. 0.5–1M tokens), each with
`--resume`, marker-file check for writes outside the repo, results in `verificacoes-locais.md`.

## Docs

docs/05 (TDD-enforced slices pattern), docs/06 (this conversion as the worked example of /skill-to-workflow),
README/README.en (implement-issue description), run-workflow SKILL.md (`seams-proposed` handling), CHANGELOG 0.2.0,
CREDITS.md, verificacoes-locais.md (new runs).

### Advisor adjustments (adopted)

1. Resume vs red/green: per-slice progress and captured red/green outputs persist in
   `<cwd>/.workflows/runs/<runId>/tdd-progress.json`; on resume, completed slices skip agents and checks, and the
   PR Evidence is built from that file. Tests: resume after `done` makes 0 agent calls and keeps 1 PR; resume after
   a crash in slice 2 skips slice 1.
2. Optional `setupCommand` (e.g. `npm ci`) runs once in the worktree; then the suite must be green before slice 1,
   else `baseline-red`. Invariant: suite green at the start of every slice.
3. Touched files per step via tree snapshots (`git add -A && git write-tree` before and after, then
   `git diff --name-only A B`); steps are told not to run git.
4. Review fix: Spec `missing` → extra TDD slices (cap 2); Standards/Security → refactor round (no test-file changes,
   suite stays green). The Spec reviewer is told which slices the cap dropped; the PR lists them.
5. Two-run seams: confirm CLI `--resume` and MCP `resumeRunId` accept new args; `seams` edited → re-plan with the
   approved seams in the prompt; the issue comment carries the exact relaunch command (CLI and chat);
   `seams-proposed` maps to a new `pending` outcome class; run-workflow SKILL.md handles it.
6. Tests: git identity in the temp repo; check nested `node --test` exit codes; glob → regex helper compatible with
   Node 22.13; fake `gh` (issue view with comments, issue comment, pr view, pr create); bare repo as origin.
7. /skill-to-workflow step 4: per-step cost table and per-path estimate in the workflow header; read-only steps
   (planner, designers, judge, reviewers, PR writer) use `settingSources: []`; inventory and implicit-decision tables
   in docs/06.
8. Credits: check the `show-me` license; cite license and URL for both sources.
9. Live runs only from the final branch tree; create `complexity:medium` in wf-sandbox; HIGH stays pending (§12, PR,
   CHANGELOG).

## Steps

- [x] Advisor review of this plan
- [ ] Branch; offline tests first (red), then the workflow (green); typecheck; both Nodes
- [ ] Docs and credits
- [ ] Real-API LOW and MED runs on wf-sandbox; evidence
- [ ] PR (pr template), CI green, user ok to merge, v0.2.0 pre-release, back-port summary to ai-study-library
