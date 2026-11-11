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
