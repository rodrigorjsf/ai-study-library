---
name: product-pipeline-conventions
description: Shared contracts for the Idea->Discovery->PRD->Architecture->Tasks agentic pipeline — run layout, handoff schemas, ID scheme, status/refusal taxonomy, severity, gate verdicts, return-brief format, traceability and carry-forward rules. Preloaded by all product-pipeline personas.
user-invocable: false
---

# Product pipeline conventions

This skill holds the contracts that every product-pipeline persona shares. Persona files cite it by section (for example "see conventions §5"). If a persona file and this skill disagree on a shared contract (a path, a field name, an enum spelling, an ID prefix), this skill wins. Stage-specific detail (rubric criteria, the full `prd.md` or arc42 skeleton, worker SOPs) lives in the stage skills and persona files.

Source of truth: `dev/research/2026-10-02-agentic-pipeline-personas-research.md` (Parts I, IV, V) and the harmonized syntheses in `dev/research/agentic-pipeline-personas/synthesis/`.

---

## §1 Pipeline topology and session model

**Chain.** `00-intake` (idea brief) → **Discovery** → **PRD** → **Architecture** → **Tasks** → (implementation run, an extension point). Tasks reads both the PRD and the Architecture handoffs.

**One orchestrator per stage, each in a fresh session.**

| Stage | Session command | Stage folder |
|---|---|---|
| Discovery | `claude --agent discovery-orchestrator` | `01-discovery/` |
| PRD | `claude --agent prd-orchestrator` | `02-prd/` |
| Architecture | `claude --agent arch-orchestrator` | `03-architecture/` |
| Tasks | `claude --agent tasks-orchestrator` | `04-tasks/` |

Rules that follow from the Claude Code runtime:

1. **The orchestrator is the main thread.** With `--agent`, its prompt replaces the default system prompt; `CLAUDE.md` and project memory still load.
2. **Only orchestrators delegate.** Subagents cannot spawn subagents. Each orchestrator lists its workers in `tools: Agent(<name>, ...)`, and those names must match the agent files exactly. Every worker, critic and shared reviewer is invoked by the stage orchestrator.
3. **Workers cannot talk to each other or ask questions mid-run.** When one lens needs another's output (privacy's data classification feeds security; SRE's capacity model feeds FinOps; analytics' tracking plan and SRE's telemetry spec feed privacy), the orchestrator runs them in sequence and passes file paths. A worker that lacks something returns `blocked` with `open_questions` (§5, §7) instead of guessing.
4. **Only the orchestrator talks to the human.** It has `AskUserQuestion`; workers do not. Each orchestrator runs **at most one clarifying round** at its entry gate, plus escalation on HOLD (§9) and human-only decisions (§10). Answers go into `gate/decision-log.md` with IDs.
5. **Handoff on disk is the only memory.** A stage knows nothing about earlier sessions except what is in `docs/pipeline/<run-id>/`. Anything that exists only in chat does not exist. No persona uses the `memory` frontmatter field.
6. **A stage may span several sessions.** The orchestrator keeps a resumable plan file with a status per brief: `01-discovery/plan.md` in Discovery, `<NN-stage>/work/plan.md` elsewhere. On resume it reads the plan and does not re-run completed briefs.
7. **Upstream is immutable.** No stage edits another stage's folder. Defects upstream are reported (`REJECTED_UPSTREAM`, §5) and a human routes the rework.
8. **An entry-gate block is not a prior version.** When the entry gate ends the session (`blocked`, `rejected` or `out_of_scope` before any work phase), the orchestrator writes `handoff.md` with `status` equal to the verdict **and** `blocked_at: entry`, plus `gate/verdict.json`, and nothing downstream may consume it. On the next session, a `handoff.md` with `blocked_at: entry` does **not** trigger the re-entry path: the orchestrator moves it, with `gate/entry-gate.md` and `gate/verdict.json`, to `history/blocked-entry-<N>/` and runs the stage as a first run. Only a handoff written after the exit gate (no `blocked_at`, or `blocked_at: exit`) starts a re-entry run.

**Stage skeleton (identical in every stage).**

1. **ENTRY gate.** Layer 1 is a deterministic script (files exist, schemas validate, `inputs_hash` recomputes, upstream `status ∈ {GO, GO_WITH_CONDITIONS}`, no blocking open questions, upstream conditions and ledger rows for this stage imported). Layer 2 is orchestrator judgment on substance. Outcomes: `accept`, `accept_with_assumptions`, `blocked`, `rejected` (written `REJECTED_UPSTREAM`), `out_of_scope`. Recorded in `gate/entry-gate.md` as `check | result | evidence`.
2. **Work phases.** Independent reading, analysis and review run in parallel; coupled decisions (framing, architecture style, slicing) stay in one head, usually the orchestrator.
3. **EXIT gate.** (a) deterministic checklist (Bash script; the orchestrator runs the checks itself when the project ships no validator, and records `method: manual` in `gate/verify-report.json`) → `gate/verify-report.json`; (b) `shared-traceability-keeper` in `exit` mode; (c) the independent stage critic on frozen artifacts; (d) the orchestrator applies the decision rule (§6). At most 3 critic rounds (§9).
4. **Handoff.** `shared-traceability-keeper` in `final` mode, then `handoff.md` + machine files + `gate/verdict.json`, then ledger rows. The session must not end unless `gate/verdict.json` exists and `handoff.md` `status` equals its `verdict` (the orchestrator self-checks this; a project may also enforce it with an optional `Stop` hook).

The downstream entry gate re-checks the minimum subset of the upstream exit gate (a consumer-side Definition of Ready). Each exit gate declares `expected_at_next_gate`: what the next exit gate must show.

**Effort scaling.** Every stage sets a scale mode before delegating (`lite | standard | deep` in Discovery, `small | standard | large` elsewhere) and spawns only the personas that mode and the routing triggers call for. Over-delegation is an anti-pattern.

---

## §2 Run directory layout and write scope

All paths are relative to the repo root.

```
docs/pipeline/<run-id>/
  00-intake/
    idea-brief.md                 # human-authored, or captured by discovery-orchestrator in its clarifying round
    evidence/                     # raw human-supplied evidence (transcripts, tickets, reviews, exports)
    validation-results/           # re-entry only: results of human-run validation tests
  01-discovery/
    plan.md                       # delegation plan + per-brief status (resume point)
    briefs/<persona>-r<N>.md      # every brief sent, verbatim
    work/                         # problem-frame.md, evidence-synthesis.md, evidence-ledger.json,
                                  # market-landscape.md, viability.md, solution-directions.md, validation-plan.md
    reviews/<persona>.md (+ reviews/<persona>/)   # shared-pool findings and lens artifacts
    gate/                         # entry-gate.md, verify-report.json, premortem-brief.md, premortem-r<N>.md,
                                  # critique-r<N>.md, findings.json, verdict.json, decision-log.md, escalation-memo.md
    rejections/                   # incoming rejection records from downstream stages (routed by a human)
    history/handoff-v<N>.md       # prior versions on re-entry
    handoff.md, handoff.data.json
  02-prd/
    handoff.md, prd.md, requirements.json, nfr.json, metrics.json, scope.json,
    ux/ (flows.md, state-matrix.csv, strings.csv, optional blueprint.md),
    glossary.md, feasibility.json, risks.json, release-criteria.md, open-questions.json,
    reviews/, gate/, work/ (plan.md, <worker>/*)
  03-architecture/
    handoff.md, architecture.md (arc42), exec-summary.md,
    drivers/ (characteristics.md, qas.yaml, utility-tree.md, constraints.md, scale-envelope.md),
    decisions/ (ADR-NNNN-<slug>.md, index.json),
    views/ (c4/, runtime.md, deployment.md, dfd.md, ownership.md),
    domain/, data/ (logical-model.md, inventory.csv, consistency-and-storage.md, migration-strategy.md, contracts/),
    contracts/ (openapi/, asyncapi/, goals-canvas.md, errors.md, versioning-policy.md),
    integration/, evolution/ (fitness-functions.yaml, walking-skeleton.md, spikes.json, rollout.md, implementability.md),
    risks.json, open-questions.json, assumptions.json, reviews/, gate/, work/
  04-tasks/
    handoff.md, tasks.json, tasks.md, briefs/<task-id>.md,
    plan/ (story-map.md, slices.json, dag.json, dag.mmd, spikes.json, raid.json),
    test/ (test-strategy.md, test-matrix.csv, contract-decisions.csv),
    release/ (release-plan.md, flags.json, migrations.json),
    policy/ (dod.md, dor.md, execution-policy.md),
    open-questions.json, dry-run/report.md, reviews/, gate/, work/
  traceability.md                 # run-wide human matrix
  trace/                          # matrix.json, id-registry.json, report-<stage>-<mode>.json
  crosscutting/ledger.md          # carry-forward ledger (§10)
gates/<stage>-exit-rubric.md      # versioned rubrics, published before the stage starts; changing one is a human decision
org/                              # optional static inputs: tech-radar.*, standards.md, platform-catalog.md
```

**Path resolution.** Paths such as `01-discovery/...`, `trace/...` and `crosscutting/...` are relative to `docs/pipeline/<run-id>/`. The `gates/` and `org/` folders are **shared by all runs** and live at `docs/pipeline/gates/` and `docs/pipeline/org/`, so `gates/<stage>-exit-rubric.md` always means `docs/pipeline/gates/<stage>-exit-rubric.md` (`discovery`, `prd`, `arch`, `tasks`). `install.sh` seeds default rubrics there; after that they are human-owned.

Every stage `gate/` folder holds at least `entry-gate.md`, `verify-report.json`, `findings.json`, `critique-r<N>.md`, `verdict.json` and `decision-log.md`. `work/` drafts are not consumed downstream.

**Write scope (single writer per file).** The `Write` tool cannot be path-restricted, so these rules are **instruction-level**: every persona must honor them. A project may add a `PreToolUse` hook to enforce them (see the README); if it does, the agent files must live in `.claude/agents/`, not in a plugin, because plugin agents ignore hooks.

| File or folder | Single writer | Notes |
|---|---|---|
| `00-intake/idea-brief.md` | human, or `discovery-orchestrator` in its clarifying round | Nobody else writes `00-intake/` |
| `<NN-stage>/work/<artifact>` | the stage worker that owns that artifact | Each worker writes only its own output paths from the brief |
| `<NN-stage>/handoff.md`, machine handoff files, `plan.md`, `briefs/`, `gate/entry-gate.md`, `gate/verdict.json`, `gate/decision-log.md`, escalation memo | stage orchestrator | Orchestrator write scope: own stage folder + `crosscutting/ledger.md` (Discovery also `00-intake/idea-brief.md`) |
| Stage machine files written by workers (for example `requirements.json`, `drivers/qas.yaml`, `tasks.json`) | the authoring worker named in the stage roster | The orchestrator consolidates by linking, not rewriting. Promoting a frozen worker file to the stage root by verbatim copy (`cp`) is allowed; editing it is not |
| `gate/critique-r<N>.md`, `gate/premortem-r<N>.md`, `gate/findings.json` | stage critic | The stage critic is the only writer: it merges deterministic, shared-reviewer and dry-run findings into `findings.json`, keeping each finding's `reviewer` field |
| `gate/verify-report.json` | deterministic validator script | Run via Bash by the orchestrator |
| `<NN-stage>/reviews/<persona>.md` and `reviews/<persona>/*` | that shared persona | Rewritten each round |
| `traceability.md`, `trace/**` | `shared-traceability-keeper` only | Stages contribute links only through `traces_to` fields and reviewer `trace_links` |
| `crosscutting/ledger.md` | orchestrator of the current session | Reviewers return `carry_forward`; the orchestrator appends |

Nobody gets `Edit` on another persona's artifact. Reviewers and critics **propose**; the authoring worker integrates.

---

## §3 Handoff schemas

### §3.1 Design rules

- **Self-contained for a cold reader.** The next orchestrator reads only the upstream `handoff.md`, its machine companions, `traceability.md`/`trace/`, the ledger, and files those cite.
- **Machine files are the source of truth; Markdown is a view.** Gates parse JSON/YAML; they do not reinterpret prose.
- **Short entry point.** `handoff.md` body at most 2 pages (Discovery at most about 8 pages excluding tables, BLUF at most 15 lines).
- **Link, don't copy.** Reference upstream by ID and path. Quote verbatim only constraints (contract fragments, data-model rules).
- **Version and hash.** `handoff_version` increments on every re-issue. `inputs_hash` covers every file in `artifacts`; the next entry gate recomputes it and compares it with the upstream `gate/verdict.json.inputs_hash`.
- **IDs are immutable** (§4).

### §3.2 Common envelope (every `handoff.md` frontmatter)

Every stage writes these fields with these names, so one Layer-1 script serves every entry gate.

```yaml
stage: discovery | prd | architecture | tasks
run_id: <run-id>
schema_version: "1.0"
handoff_version: <int>                 # increments on every re-issue; IDs never renumbered
status: GO | GO_WITH_CONDITIONS | HOLD | BLOCKED | REJECTED_UPSTREAM | KILL_RECOMMENDED  # KILL_RECOMMENDED: PRD onward only
blocked_at: entry | exit                # only when status is BLOCKED/REJECTED_UPSTREAM; `entry` = stopped before any work phase (§1 rule 8)
created_at: <ISO-8601>
rubric_version: <stage>-exit-<x.y>     # discovery-exit-1.0, prd-exit-1.0, arch-exit-1.0, tasks-exit-1.0
rounds_used: <n>                       # Discovery writes this as exit_gate.rounds
max_rounds: 3                          # initial critic round + max 2 revision loops
upstream: {...}                        # stage-specific (below)
inputs_hash: "sha256:..."              # over all files in `artifacts`
conditions:                            # only with GO_WITH_CONDITIONS, <= 3 (schema in §6.3)
  - {id: CND-<infix>-NNN, finding: <STAGE>-G-NNN, owner_stage: <stage|implementation|human>, due_gate: <gate|milestone>, text: "..."}
expected_at_next_gate: ["<deliverable the next exit gate must show>"]
carry_forward: [<ledger IDs deferred, with target stage>]
kill_criteria: [<KILL-NNN + status: not_triggered | triggered | unknown>]
human_decisions_pending: []            # must be empty unless status is HOLD or BLOCKED
known_issues: [<MINOR finding IDs>]
open_questions_blocking: 0             # PRD/Architecture/Tasks carry it inside `counts`
artifacts:                             # every file the handoff relies on
  - {path: <relative path>, sha256: "..."}
```

### §3.3 `01-discovery/handoff.md` (+ `handoff.data.json`) — read by the PRD entry gate

Extra frontmatter: `artifact: discovery-handoff`, `stage_dir`, `previous_version`, `produced_by`, `upstream: [{path: 00-intake/idea-brief.md, sha256}]`, `entry_gate {result, path}`, `exit_gate {verdict, rounds, max_rounds, verdict_path, findings_path, open_major_ids}` (`status` mirrors `exit_gate.verdict`), `evidence_mode: real_evidence | desk_only`, `effort_tier: lite | standard | deep`, `recommendation: proceed | proceed_with_conditions | pivot | kill`, `recommendation_confidence`, `critic_stance: concur | dissent`, `decision_owner`, `human_decision {status: pending | go | go_with_conditions | pivot | kill, by, date, note}`, `time_box`, `primary_outcome`, `target_segment`, `target_opportunity`, `leading_direction`, `must_answer_before {prd: [Q-*], architecture: [Q-*]}`, `shared_reviews [{persona, status, lens_verdict, path}]`, `carry_forward_ledger`, `trace_report`, `non_goals`, `id_prefixes`. Discovery conditions also keep `source`. Discovery never writes `KILL_RECOMMENDED`: kill is a recommendation plus a human decision there.

**Gate verdict ≠ product decision.** `exit_gate.verdict` judges the package; `recommendation` and `human_decision` judge the bet. A well-evidenced kill recommendation is a successful Discovery.

Body sections, in order: 1 BLUF (≤15 lines); 2 Outcome (OUT-001); 3 Problem statement and frame; 4 Target segment and JTBD (four forces); 5 Evidence summary (counts by type × strength; prominent no-real-evidence statement in `desk_only`); 6 Opportunity Solution Tree; 7 Solution directions and leading-direction rationale; 8 Assumption and risk register; 9 Market and alternatives; 10 Viability; 11 Metrics and kill criteria; 12 Glossary, constraints, hotspots; 13 Feasibility flags for Architecture (as questions); 14 Cross-cutting screening; 15 Pre-mortem and critic verdict; 16 Non-goals (≥3); 17 Open questions; 18 Human validation plan; 19 Guidance for the PRD stage; 20 Changes since previous version; 21 Artifact manifest.

`handoff.data.json` mirrors every register (`outcome, problems, frames, segments, jobs, opportunities, solutions, assumptions, evidence, tests, risks, metrics, kill_criteria, alternatives, terms, flags, non_goals, open_questions, decisions, conditions`); every item has `id, statement, traces_to, source`.

**PRD entry checks against it:** envelope + Discovery fields present; `status ∈ {GO, GO_WITH_CONDITIONS}` **and** `recommendation ∈ {proceed, proceed_with_conditions}` **and** `human_decision.status ∈ {go, go_with_conditions}` (`pending` → blocked; `pivot` → blocked for Discovery re-entry; `kill` → stop); `inputs_hash` equals `01-discovery/gate/verdict.json.inputs_hash`; `trace/matrix.json` records this `handoff_version`; `must_answer_before.prd` all answered and `open_questions_blocking = 0`; conditions with `due_gate: prd-*` and ledger rows with `target_stage: prd` imported; `evidence_mode` honoured and no `supported_by_real` status resting on synthetic or opinion evidence.

### §3.4 `02-prd/handoff.md` — read by the Architecture and Tasks entry gates

Extra frontmatter: `upstream {path, upstream_status, upstream_handoff_version, human_decision, inputs_hash, evidence_mode, discovery_recommendation}`, `scale_mode`, `appetite {budget, source}`, `prioritization_method` (exactly one of MoSCoW | RICE | WSJF | Kano), `id_prefixes`, `counts {fr, fr_must, nfr, ac, open_questions_blocking, assumptions}`.

Body sections, in order: 1 Cold-read summary; 2 Changes from Discovery; 3 Scope summary; 4 **Inputs for Architecture** (NFR highlights, rabbit holes, constraints with sources, external systems, personal-data classes, API consumers, volumes and growth); 5 **Inputs for Tasks** (priorities, ACs per Must, release criteria, event requirements); 6 Gate record; 7 Open questions and assumptions; 8 Artifact index.

Required machine files: `requirements.json` (EARS statements, fit criteria, ACs, `traces_to`), `nfr.json` (ISO/IEC 25010:2023, 9 rows, target or `n/a` + reason), `metrics.json`, `scope.json`, `glossary.md`, `feasibility.json`, `risks.json`, `release-criteria.md`, `open-questions.json`, plus `ux/flows.md`, `ux/state-matrix.csv`, `ux/strings.csv` when there is a UI.

**Architecture entry checks against it:** envelope; `status`; `human_decisions_pending = []`; `inputs_hash` vs `02-prd/gate/verdict.json`; the files above exist and validate; trace records the PRD `handoff_version`; PRD conditions with `owner_stage: architecture` and `expected_at_next_gate` imported as inherited must-meet criteria (M9+).

### §3.5 `03-architecture/handoff.md` — read by the Tasks entry gate

Extra frontmatter: `upstream {path, upstream_status, upstream_handoff_version, inputs_hash}`, `scale_mode`, `greenfield`, `architecture_style`, `style_adr`, `quanta`, `driving_characteristics` (3-7), `scale_envelope`, `org_constraints {provided, absent_assumed}`, `one_way_doors [{adr, human_ack: DL-A-NNN | pending}]`, `walking_skeleton`, `slicing_units`, `frozen_contracts`, `id_prefixes`, `counts`.

Body sections, in order: 1 Cold-read summary; 2 Deltas against the PRD (architecture never changes scope); 3 Decisions at a glance (ADR | decision | reversibility | drivers | Confirmation FF); 4 **Inputs for Tasks** (walking skeleton, slicing units, frozen contracts, migration ordering, fitness functions to ticket, spikes with the ADRs they unblock, ownership lanes, per-component concern tags `security | privacy | a11y | sre | finops | analytics`); 5 Gate record; 6 Open questions, assumptions and risks; 7 Artifact index.

**Tasks entry checks against PRD + Architecture:** both envelopes and statuses; Architecture's `upstream.inputs_hash` equals the current PRD hash; PRD JSON as in §3.4; Architecture files `views/c4/*`, `decisions/*`, `drivers/qas.yaml`, `evolution/fitness-functions.yaml`, `contracts/openapi|asyncapi/*`, `data/logical-model.md`, `data/migration-strategy.md`, `risks.json`, `views/deployment.md`, `views/ownership.md`, `evolution/walking-skeleton.md`, `evolution/spikes.json`, `open-questions.json`; contracts re-validate; every Must FR maps to a component; components are acyclic; pending `one_way_doors` listed; conditions with `due_gate: tasks-*` and ledger rows targeted at `tasks` imported. Rejected on: unvalidated contracts, destructive migrations without expand/contract, cross-BC workflows without a saga or consistency decision, cyclic components, `NEEDS CLARIFICATION`/TBD.

### §3.6 `04-tasks/handoff.md` — read by the implementation run (extension point)

Extra frontmatter: `upstream {prd: {path, status_read, inputs_hash}, arch: {path, status_read, inputs_hash}}`, `codebase {mode: greenfield | brownfield, repo_root, base_ref, has_walking_skeleton}`, `scale_mode`, `appetite`, `counts`, `critical_path`, `max_parallel_agents` (WIP limit), `first_executable`.

Body sections, in order: 1 Cold-read summary; 2 How to execute (≤10 lines, pointing to `policy/execution-policy.md`); 3 Milestones and critical path; 4 Changes from upstream (no design decision introduced here; new decisions are `adr_request` or spikes); 5 Cross-cutting coverage (one line per lens); 6 Gate record; 7 Open questions, assumptions, risks; 8 Artifact index.

`tasks.json` is the source of truth; `tasks.md` and `briefs/<task-id>.md` are rendered from it. Task contract fields: `id, title, kind, phase, slice, milestone, traces_to {fr, ac, nfr, adr, component, contract_op, fitness_fn, ledger, risk}, objective, split_pattern, scope {in, out}, files {modify, create, must_not_change}, context_pointers, quoted_constraints, acceptance [GWT bound to a named test], test_first, verification [{cmd, expect}], depends_on [{id, type: FS|SS, reason}], parallel_safe, size, nfr_constraints, concerns, release {flag, migration, rollback}, dod, stop_conditions, autonomy, owner_boundary, status, passes, evidence`.

---

## §4 ID scheme (owned by `shared-traceability-keeper`)

The keeper writes the conventions into `trace/id-registry.json` in `reserve` mode (Discovery Phase 0) and validates them at every boundary. Personas mint IDs only under prefixes their brief assigns.

| Rule | Detail |
|---|---|
| Format | `PREFIX-NNN`. Exceptions: ADRs `ADR-NNNN`; tasks `T-Snn-NN`; milestones `MS-n`; slices `SL-nn`; flags `FLG-nn`; migrations `MIG-nn`; Tasks open questions `TQ-nn`. Regex per prefix lives in the registry |
| Immutability | No renumbering; no reuse after deletion or supersession. A dropped item keeps its ID with `status: dropped`, a rationale and an approver (`DEC-`/`DL-` ID). A reversed ADR stays, marked `superseded by ADR-NNNN` |
| Inheritance | Upstream IDs are referenced, never re-minted |
| **Stage infix for shared prefixes** | Discovery mints bare IDs. A later stage minting under a prefix an earlier stage already uses adds `-P-` (PRD), `-A-` (Architecture) or `-T-` (Tasks). Known shared prefixes: `RSK, ASM, Q, NG, CON, TST, SPK, DL, CND`. Examples: `ASM-P-002`, `NG-P-001`, `RSK-A-004`, `Q-A-003`, `DL-A-002`, `CND-A-001`, `SPK-T-02`, `TST-T-014`, `RSK-T-003` |
| Spikes | `SPK-NNN` is first minted by Architecture; Tasks schedules those and mints its own as `SPK-T-nn` |
| Decision logs | Discovery `DEC-NNN`; PRD/Architecture/Tasks `DL-P-NNN`, `DL-A-NNN`, `DL-T-NNN` |
| Conditions | Discovery `CND-NNN`; later stages `CND-P-NNN`, `CND-A-NNN`, `CND-T-NNN` |
| Gate findings | `DISC-G-NNN`, `PRD-G-NNN`, `ARCH-G-NNN`, `TASKS-G-NNN`, stable across rounds |
| Lens findings | `<LENS>-<D|P|A|T>-NNN`, e.g. `SEC-A-003`, `PRV-P-002`, `TRC-T-010` |
| Ledger rows | `LED-NNN` |

**Stage-first prefixes.**

| Stage | Prefixes |
|---|---|
| Discovery | `OUT, PRB, FRM, SEG, JOB, OPP, SOL, ASM, EVD, TST, RSK, MET, KILL, ALT, TERM, FLAG(-FEAS/-A11Y/-SEC/-PRIV), NG, Q, DEC, CND` |
| PRD | `G, J, FL, FR, BR, CON, NFR, AC, M, EV, RC, GL` (acceptance criteria as `AC-FR-NNN-n`) |
| Architecture | `QAS, ADR, C, CMP, BC, AGG, EVT, ENT, OP, MSG, SAGA, FF, SPK, TD, SP, TP` |
| Tasks | `MS, SL, T, FLG, MIG, TQ` (task-level ACs as `AC-T-Snn-NN-n`) |
| Cross-cutting (lens proposals) | `THR, SEC-NFR, ABU, LIN, OBL, SLO, SLI` |

**Traceability links** are explicit only: `traces_to` fields in machine artifacts and `trace_links: [{from, to, type}]` in reviewer files. Link types: `derives | satisfies | refines | realizes | verifies | mitigates | implements`. Links are never inferred from text similarity. When an upstream item's text hash changes, its downstream links become `suspect`.

**Blocking gaps per stage** (keeper, `exit` mode):

| Stage | Chain checked | Blocking gap |
|---|---|---|
| Discovery | EVD → OPP/OUT; ASM/RSK → OPP; MET → OUT; SOL → OPP | Target OPP without evidence (or explicit assumption-only status); MET without OUT |
| PRD | OPP/OUT → G → FR/NFR/BR → AC; G → M → EV; FR → FL/J | Must OPP with no G/FR and no drop record; FR without upstream link; Must FR without AC; Must G without M |
| Architecture | FR/NFR → QAS → ADR → C/CMP → OP/MSG; QAS → FF; RSK → ADR/SPK; THR/LIN → control | Must FR without C/OP or "no interface" note; NFR without QAS; ADR without driver; orphan component; `mitigate` threat without control |
| Tasks | FR/AC/NFR/QAS/FF/THR/LIN/OBL/SLO/ledger → T → TST | Must FR/AC without task and test; mitigation, obligation or SLO alert without task; task with no upstream link unless typed `enabling`; test without task |

Keeper modes: `reserve` (Discovery Phase 0), `entry` (every entry gate), `exit` (before every critic round), `final` (after the verdict, before the handoff is written; records `handoff_version` in `trace/matrix.json`). Its report `trace/report-<stage>-<mode>.json` is a required critic input.

---

## §5 Status and refusal taxonomy

Every persona return and every reviewer file carries `status: done | blocked | rejected | out_of_scope`.

| Status | Applies when | What to return | Who acts next |
|---|---|---|---|
| `done` | The work ran to its done criteria. A reviewer may be `done` with `lens_verdict: fail`; a critic is `done` whatever its recommendation | Return brief (§7) with artifact paths | Orchestrator consolidates or routes findings |
| `blocked` | A **required input is missing or insufficient**; the persona will not run on guesses. Typical: a brief missing required fields; no problem, segment or decision owner (Discovery); no appetite and no permission to default (PRD); no deployment target, or no jurisdiction with personal data (Architecture); no `repo_root`/`base_ref` (Tasks); a pending human-only decision | Refusal block with `needed_from` and a specific `suggested_question`; list each missing item | Orchestrator answers from files, asks the human once, or routes upstream. Otherwise writes `status: BLOCKED` with `missing: [{item, needed_from, suggested_question}]` |
| `rejected` | Present work **fails a quality bar the persona owns**. Typical: problem stated as a solution; synthetic evidence presented as validation; unmeasurable NFRs; contradictory Musts; destructive migration without expand/contract; unvalidated contracts; duplicate or renumbered IDs; deterministic failures handed to a critic | Refusal block naming the failed rule and the evidence location; `target: current_draft` or `upstream:<stage>` | Inside a stage: RECYCLE to the authoring worker. At entry: orchestrator writes `REJECTED_UPSTREAM` with an `upstream_rework_request` (each failed check, evidence location, `rerun_stage`); a human routes it |
| `out_of_scope` | The request belongs to **another stage, lens, a human or an extension point** (requirements at Discovery; architecture or estimates at PRD; scope changes at Architecture; technology choices outside ADRs or implementation code at Tasks; legal determinations; GTM, positioning, pricing) | `owner: <stage | lens | human:<role> | extension:gtm>`; do the in-scope remainder if any | Logged and routed; wrong-stage-depth checks become carry-forward (§10), never blockers |

**Not refusals:**

- `accept_with_assumptions` — entry passes with recorded defaults; each default is an `ASM-` item with owner and `confirm_by`, listed in the cold-read summary.
- Reclassification — e.g. Discovery turns unsupported "users love it" claims into hypotheses and logs a `DEC-` entry instead of refusing the run.
- `KILL_RECOMMENDED` — an inherited kill criterion triggered (PRD onward); the human confirms.

**Machine-readable refusal block** (every worker, and every entry gate):

```yaml
status: blocked | rejected | out_of_scope
rule_id: "<persona refusal criterion ID>"
evidence: "<file#ID or file:line>"
needed_from: "<stage | role | human>"
suggested_question: "..."
```

Never repair upstream content to avoid a refusal. Never silently fill a gap ("mind reading"); either refuse or record an `[assumption]` (§8).

---

## §6 Severity scale, gate verdicts and conditions

### §6.1 Severity

Assigned **by rubric mapping first, judgment second**.

| Severity | Definition | Gate effect | Loop behaviour | Closes as |
|---|---|---|---|---|
| `BLOCKER` | Deterministic check failed; must-meet criterion failed; a lens refusal criterion was hit; concrete failure scenario showing the next stage cannot proceed or would build the wrong thing; triggered kill criterion; undispositioned legal or safety red flag | Verdict cannot be GO or GO_WITH_CONDITIONS | RECYCLE while rounds remain, else HOLD | `fixed_verified` at the cited location, or human `overridden` with rationale |
| `MAJOR` | Should-meet criterion pre-assigned MAJOR failed; a lens acceptance criterion failed; materially raises downstream rework but downstream can proceed under a stated condition | GO_WITH_CONDITIONS allowed if ≤3 and each has `owner_stage` + `due_gate` | Can trigger a revision round; downgrading needs a recorded reason | fixed, carried as a condition, or overridden |
| `MINOR` | Clarity, style, nice-to-have; no downstream impact | Never blocks | **Never** triggers a round | Listed in `known_issues` |
| `NOTE` (= `observation`) | Not tied to any rubric criterion. The shared pool says NOTE, stage rubrics say observation; they are synonyms | Ignored for gating | — | May feed a proposed rubric change, decided by a human outside the loop |

`out_of_scope` is a classification, not a severity. A reviewer may raise severity above the rubric default only with a `failure_scenario`. Nobody but a human may lower a must-meet or refusal-criterion hit below BLOCKER. `failure_scenario` is required for every BLOCKER and MAJOR.

**Finding status:** `open | fixed_verified | overridden | downgraded | withdrawn`. **Finding record** (`gate/findings.json`): `id, round_raised, reviewer (<stage>-critic | deterministic | shared-<lens> | dry-run), severity, criterion, location, evidence, failure_scenario, suggested_direction (≤2 sentences, never replacement text), refusal_class (rejected | blocked | null), status, history [{round, status, note}]`. Every `location` must resolve to a real file and anchor; this is script-checked.

### §6.2 Gate verdict vocabulary

Written `status` (in `handoff.md`) and `verdict` (in `gate/verdict.json`) take exactly these values:

| Verdict | Rule (applied mechanically by the orchestrator) |
|---|---|
| `GO` | 0 deterministic failures, 0 trace blocking gaps, 0 open BLOCKER, 0 open MAJOR (Architecture also: no pending one-way-door acknowledgment) |
| `GO_WITH_CONDITIONS` | 0 BLOCKER; 1-3 MAJOR, each turned into a condition with `owner_stage` + `due_gate` (Architecture: pending one-way-door acks become conditions due at `tasks-entry`) |
| `HOLD` | After the final round a BLOCKER or over-cap MAJOR is still open; or no progress (same open BLOCKER/MAJOR IDs in two consecutive rounds); or an unresolved conflict between reviewers (or critic vs reviewer); or an unresolved human-only decision; or (Discovery) critic dissent on a triggered kill criterion |
| `KILL_RECOMMENDED` | An inherited kill criterion has triggered (PRD onward only); the human confirms |
| `BLOCKED` | Entry gate failed on missing input; no exit gate run |
| `REJECTED_UPSTREAM` | Entry gate rejected the upstream handoff |

`RECYCLE` (any open BLOCKER or >3 MAJOR while revision loops remain) is internal and **never written** as a final status. The critic's own recommendation (`PASS | REVISE | ESCALATE`) is advisory input; only the rule above produces the written status. The finder is never the decider.

`gate/verdict.json`:

```json
{ "stage": "prd", "gate": "exit", "round": 2, "max_rounds": 3,
  "verdict": "GO | GO_WITH_CONDITIONS | HOLD | BLOCKED | REJECTED_UPSTREAM | KILL_RECOMMENDED",
  "refusal_class": null, "blocking_ids": [], "conditions": [],
  "expected_at_next_gate": [], "escalation_memo": null, "rubric_version": "prd-exit-1.0",
  "inputs_hash": "sha256:..." }
```

Discovery writes the escalation memo as `gate/escalation-memo.md`; other stages embed it in `verdict.json.escalation_memo`. Either way, `verdict.json` must point at the memo.

### §6.3 Conditions format (canonical)

```yaml
conditions:          # only with GO_WITH_CONDITIONS; at most 3
  - id: CND-<infix>-NNN        # CND-NNN in Discovery, CND-P-/CND-A-/CND-T- later
    finding: <STAGE>-G-NNN     # the MAJOR finding this condition carries
    owner_stage: <discovery | prd | architecture | tasks | implementation | human>
    due_gate: <gate or milestone, e.g. prd-exit, architecture-exit, tasks-entry, tasks-exit, MS-1>
    text: "<binary, checkable statement of what must be true>"
```

Discovery conditions may add `source` (a finding or `ASM-` ID). The downstream entry gate imports every condition whose `due_gate` names it as an inherited must-meet criterion (M9+); failure is a BLOCKER.

---

## §7 Return brief (subagent → orchestrator)

The return brief is the only thing that enters the orchestrator's context. Files are the source of truth; the brief points at them. **Never paste the artifact**, never summarize another worker's output in place of linking it, and keep the whole brief within about 25 lines.

```yaml
status: done | blocked | rejected | out_of_scope
summary: <=10 lines (shared reviewers: <=5 lines) — what was produced, top findings or decisions, counts that matter
artifact: [<paths written, with #ID anchors where useful>]
counts: {<persona-relevant counts, e.g. items minted, blocker, major, minor, proposals, carry_forward, needs_human>}
blocking_ids: [<IDs that block the gate, if any>]
self_check: [{criterion, pass|fail, evidence}]        # workers: own acceptance criteria
open_questions: [{id, question, blocking: yes|no, needed_from | needed_by_stage}]
assumptions: [{id, assumption, risk_if_wrong}]
risks: [{id, risk, suggested_disposition}]
confidence: low | medium | high — <why>
refusal: null | {status, rule_id, evidence, needed_from, suggested_question}   # §5 block
```

Role-specific additions:

- **Shared reviewers:** `lens_verdict: pass | pass_with_findings | fail | n/a`, `lens_artifacts: [paths]` (§11).
- **Stage critics:** `critic_recommendation: PASS | REVISE | ESCALATE`, `round: N`; Discovery critic also `recommendation_stance: concur | dissent` with a counter-hypothesis ID.
- **Traceability keeper:** `coverage_must_pct`, `blocking_gaps`, `orphans`, `suspects`, `report_path`.
- **Discovery evidence synthesizer:** `evidence_mode_observed: real_evidence | desk_only`.

**Brief contract (orchestrator → worker)**, for reference: `objective, stage/role, inputs (paths only), output (path + template skill + ID prefixes), boundaries (explicit "do not"), tools_guidance, budget, done_criteria, known_context, return_format`. `known_context` carries decisions already made and overrides. Revision briefs add only `finding_ids` + `fix_condition` and nothing else. A brief missing required fields is refused as `blocked`. Every brief is saved verbatim (`briefs/` in Discovery, `work/` elsewhere).

---

## §8 Evidence and assumption tagging

**Evidence is a typed field, not prose.** Every evidence item (Discovery `EVD-*` in `work/evidence-ledger.json`) carries:

- `evidence_type ∈ {real_primary, real_secondary, desk_research, synthetic, assumption}`
- `strength ∈ {say, do, commit}` — `say` is opinion or intent; `do` is observed or recounted specific past behaviour or usage data; `commit` is time, reputation or money given up.
- `weak_signal: true` for future-tense, hypothetical, compliment or generic statements (Mom Test lint), which are downgraded to `strength: say`.
- a source pointer: file + line/row for supplied evidence; URL + access date for desk research.

**Assumption status:** `untested | assumed | supported_by_desk | supported_by_real | refuted`.

- `supported_by_real` requires `real_*` evidence of `do` or `commit` strength. Anything else claiming it is a BLOCKER.
- **Synthetic evidence never raises a status.** Synthetic users and LLM-generated personas may generate hypotheses or pilot an interview guide; they never validate.
- `evidence_mode: desk_only` (no real evidence supplied) caps every value assumption at `supported_by_desk` and the Discovery recommendation at `proceed_with_conditions`. Downstream stages inherit `evidence_mode` verbatim and must not upgrade it.
- The word "validated" is not used for anything without real evidence.

**Assumption tagging (all stages).**

- Any number, default, threshold or fact without a source is tagged `[assumption]` in prose and recorded as an `ASM-` item (with the stage infix) carrying `owner`, `risk_if_wrong` and `confirm_by`. Architecture also marks `core_domain: true|false`.
- Numbers (SLO targets, prices, capacity, market sizes, baselines) cite a source (a PRD field, a model row, a dated page) or are labelled `assumption`. No fabricated baselines; forecasts need drivers; market sizes are ranges.
- Design rules proposed by the pipeline, not taken from a source (budgets, size caps, WIP limits), are tagged `[heuristic]`.

**No invented sources.**

- Never invent a citation, URL, quote, interviewee, statistic, standard ID or legal article. Quotes are used only if verbatim in a supplied source.
- `framework_ref` values (ASVS, OWASP, SSDF, GDPR/LGPD/ANPD, WCAG, SRE references, price sources) must come from the lens skill's curated `refs/` allow-list or be tagged `UNVERIFIED`. Do not generate ASVS↔CWE pairs.
- Plausible but unconfirmed claims are tagged `UNVERIFIED` and never presented as fact.
- Separate observation from interpretation; report contradicting evidence; do not make prevalence claims from small-n qualitative data.
- Legal determinations are never made by a persona (§10); privacy and accessibility outputs carry a not-legal-advice disclaimer.

---

## §9 Critic loop rules

**Independence.**

- Each stage has one critic (`discovery-critic`, `prd-critic`, `arch-critic`, `tasks-critic`) running in a fresh context on **frozen** artifacts. Inputs: the artifacts, `gate/verify-report.json`, the keeper report, `reviews/*`, the rubric, and in rounds ≥2 the prior `findings.json` and `gate/decision-log.md`. **Excluded:** worker transcripts and the orchestrator's narrative of why the package is good.
- The critic writes its independent pre-mortem (or equivalent blind first step) **before** reading the authors' rationale: Discovery and Architecture read a stripped `premortem-brief.md` first; Tasks writes its pre-mortem before reading the authors' summary; PRD uses an Internal-FAQ lens.
- Skeptical by default; length is not evidence; binary pass/fail per criterion with an evidence pointer, never Likert scores. Devil's advocacy names a counter-hypothesis and the evidence that would distinguish it.
- If the deterministic checklist failed, the critic is not run (no round is spent); a critic handed structurally invalid input returns `rejected`.

**No rewriting.** The critic never fixes an artifact, never writes replacement text longer than one sentence (`suggested_direction` ≤2 sentences), never makes the gate decision, never adds criteria outside the published rubric (it may propose rubric changes as non-gating observations), and never issues specialist lens verdicts.

**Loop rules.**

1. **Contract first.** Findings only against criteria in `gates/<stage>-exit-rubric.md`, which is published before the stage starts. A new criterion is a human rubric change outside the loop.
2. **Severity-gated loops.** Only open BLOCKER/MAJOR findings trigger another round; MINORs never do.
3. **Monotonic findings.** After round 1 a new BLOCKER is admissible only if the revision caused it or new evidence is cited; otherwise the critic only closes or keeps existing findings. Finding IDs are stable across rounds.
4. **Cap.** Critic round 1 → revision 1 → round 2 → revision 2 → round 3 (final): `max_rounds: 3`.
5. **Disagree-and-commit.** A finding marked `overridden` in `gate/decision-log.md` (who, why) is never re-raised, in this stage or in re-entry runs.
6. **No-progress detector.** Unchanged open BLOCKER/MAJOR IDs across two consecutive rounds → HOLD immediately.
7. **Narrow revision briefs.** Only finding IDs, locations and fix conditions go to the owning worker; the worker revises its own file; deterministic checks re-run before the next critique.
8. **Hallucinated-evidence guard.** Every finding `location` must resolve; a critic citing nonexistent sections is itself a defect.

**Voting** (`deep`/`large` modes): two independent critic samples; a BLOCKER stands only if both raise it or one cites a deterministic failure.

**Escalation memo** (on HOLD). Contents: open BLOCKER/MAJOR IDs with the author's and the critic's positions; options (fix with more time or a human decision / override with rationale / descope / return upstream / pivot / kill); the orchestrator's recommended option; what re-entry would need. The orchestrator asks the human via `AskUserQuestion` and records the choice in `gate/decision-log.md`. The pipeline never silently passes.

---

## §10 Carry-forward ledger and human-only decisions

### §10.1 Carry-forward ledger

`docs/pipeline/<run-id>/crosscutting/ledger.md` is how a lens remembers across fresh sessions.

Row schema:

```
| ledger_id | lens | source_finding | target_stage | item | status | owner | decision_ref | resolved_by |
```

- `status ∈ {open, accepted-risk, deferred, resolved}`; `decision_ref` is a `DEC-`/`DL-` ID; `resolved_by` is the ID that resolved it (task, NFR, ADR, DoD item).
- **Single writer:** the orchestrator of the current session. Reviewers and workers return `carry_forward: [{id, target_stage, reason}]` and `needs_human` items; the orchestrator appends them with finding ID, source stage and target stage, and lists deferred ledger IDs in the handoff's `carry_forward`.
- **Entry duty:** every entry gate lists rows with `target_stage` = this stage. Every persona dispositions the rows where `lens` = itself: resolved (with an ID), still open, or re-deferred with a reason. An unaddressed row is a MAJOR finding with `check: <LENS>-LEDGER`. At Tasks every row targeted at `tasks` must become a task, a DoD item or an explicit re-deferral.
- **Wrong-stage depth** (for example asking for a threat model at Discovery or a tracking plan at PRD entry) is `out_of_scope` + a carry-forward row, never a blocker.

### §10.2 Human-only decisions

No persona and no orchestrator may make these decisions:

- legal-basis confirmation; whether a DPIA/RIPD is mandatory; applicability of a regulatory regime (`confirmed-by:<human>`);
- risk acceptance for security or privacy blockers;
- the business SLO target; the cost ceiling and gross-margin target; product success targets;
- Discovery go / go-with-conditions / pivot / kill; any KILL downstream;
- one-way-door ADR acknowledgment;
- overrides of BLOCKERs; rubric changes; HOLD resolutions.

Each surfaces as `needs_human: [{id, decision, options, why_it_matters, blocking_stage}]`. When it gates a Must, the persona returns `blocked: awaiting human decision` and the orchestrator lists it in `human_decisions_pending` (which forces HOLD or BLOCKED). Human answers go into `gate/decision-log.md` (`DEC-` in Discovery, `DL-<infix>-` elsewhere) so later fresh sessions inherit them.

---

## §11 Shared reviewer invocation brief and output contract

Applies to the shared pool: `shared-security-architect`, `shared-privacy-compliance`, `shared-accessibility-reviewer`, `shared-sre-operability`, `shared-finops-analyst`, `shared-product-analytics`, `shared-traceability-keeper`. Any stage orchestrator may invoke them, by routing trigger (mandatory / conditional / never per stage) and at stage depth.

### §11.1 Invocation brief (orchestrator → shared persona)

A brief missing a required field is refused as `blocked`.

```yaml
run_id: <run-id>                                   # required
stage: discovery | prd | architecture | tasks      # required; selects the stage-depth row
mode: review | author-assist | entry | exit | final | reserve   # required; last four are keeper-only
depth: light | full                                # required; set by the routing trigger
trigger_reason: "<which routing rule fired>"       # required
round: 1                                           # required; >=2 means re-review of a revision
inputs:                                            # required: explicit paths, never "look around"
  - docs/pipeline/<run-id>/<NN-stage>/<draft files for this lens>
  - docs/pipeline/<run-id>/<previous-stage>/handoff.md
cross_lens_inputs: []                              # declared dependencies only (see §1 rule 3)
ledger: docs/pipeline/<run-id>/crosscutting/ledger.md   # required from PRD onward
trace: docs/pipeline/<run-id>/traceability.md           # required from PRD onward
rubric: gates/<stage>-exit-rubric.md               # required for review mode
prior_findings: <NN-stage>/reviews/<persona>.md    # required when round >= 2
decision_log: <NN-stage>/gate/decision-log.md      # overrides that must not be re-raised
output_dir: docs/pipeline/<run-id>/<NN-stage>/reviews/   # required
```

### §11.2 Output contract

**Findings file** `docs/pipeline/<run-id>/<NN-stage>/reviews/<persona>.md` (one per persona per stage, rewritten each round), YAML frontmatter that gates parse:

```yaml
---
persona: <shared-persona-name>
run_id: <run-id>
stage: <stage>
mode: <mode>
depth: light | full
round: <n>
status: done | blocked | rejected | out_of_scope
lens_verdict: pass | pass_with_findings | fail | n/a     # meaningful when status is done or rejected
inputs_hash: sha256:...                                 # hash of the input files actually read
findings:
  - id: <LENS>-<D|P|A|T>-NNN
    severity: BLOCKER | MAJOR | MINOR | NOTE
    refusal_class: rejected | blocked | null
    check: <acceptance/refusal criterion ID from the lens skill>
    location: "<file#anchor>"                           # must resolve
    evidence: "<quote or precise paraphrase>"
    failure_scenario: "<what goes wrong downstream>"     # required for BLOCKER/MAJOR
    recommendation: "<concrete fix, <= 2 sentences>"
    framework_ref: "<ID from refs/ allow-list> | UNVERIFIED"
    target: current_draft | upstream:<stage>
    status: open | fixed_verified | overridden | downgraded | withdrawn
proposals: [{id, kind: nfr | ac | task | dod | adr_request | spike, text, traces_to}]
carry_forward: [{id, target_stage, reason}]
needs_human: [{id, decision, options, why_it_matters, blocking_stage}]
conflicts_noted: []
trace_links: [{from, to, type}]
---
```

Body sections, in order: 1 Scope reviewed and not reviewed; 2 Lens verdict and summary (≤10 lines); 3 Findings table; 4 Lens artifacts produced; 5 Proposals; 6 Carry-forward; 7 Needs human; 8 Assumptions; 9 Not-legal-advice disclaimer (privacy and accessibility only).

Lens artifacts go under `reviews/<persona>/` (for example `threat-model.md`, `data-inventory.csv`, `slo.yaml`, `cost-model.csv`).

**Return brief:** §7 plus `lens_verdict`, `lens_artifacts`, and `counts {blocker, major, minor, proposals, carry_forward, needs_human}`.

### §11.3 Status semantics and lens rules

- `done`: the review ran; `lens_verdict` may still be `fail`. The orchestrator routes proposals to authors and passes findings to the stage critic, which merges them into `gate/findings.json` (§2).
- `blocked`: a required lens input is missing (no jurisdiction, no DFD, no scale expectation). Do not run the lens on guesses.
- `rejected`: a refusal criterion tagged `rejected` was hit. `target: current_draft` → the orchestrator recycles to the author; `target: upstream:<stage>` → a rejection record upstream.
- `out_of_scope`: route to `owner`; wrong-stage depth becomes carry-forward.
- **One lens per agent.** Reviewers run in parallel on the frozen draft and do not see each other's findings, except declared `cross_lens_inputs`.
- **Maker/checker.** Reviewers propose; the stage's authoring worker integrates; the stage critic judges. A persona that authored a lens artifact in `author-assist` mode never re-judges it in the same stage.
- **Conflicts are noted, not resolved.** Each persona states its position in `conflicts_noted`; the orchestrator carries both positions into `needs_human`. No persona silently overrides another.
- Severity, monotonic findings and no re-raising of overrides follow §6 and §9.
