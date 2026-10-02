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
- [ ] User go-ahead
- [ ] Phase 1 workflow run
- [ ] Research doc written
- [ ] Persona files written
- [ ] Verification + review fixes
- [ ] README + commit/push

## Review

(to be filled after execution)
