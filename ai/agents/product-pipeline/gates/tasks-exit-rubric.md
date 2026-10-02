---
rubric_id: tasks-exit
rubric_version: tasks-exit-1.0
stage: tasks
gate: exit
owner: human
status: default
changes_require: human decision
critic: tasks-critic
decider: tasks-orchestrator
finding_prefix: TASKS-G-NNN
max_rounds: 3
---

# Tasks exit-gate rubric (tasks-exit-1.0)

## 1. Purpose and how it is used

This file is the published contract for the Tasks exit gate. `install.sh` seeds it into `docs/pipeline/gates/tasks-exit-rubric.md`; after that it is human-owned. `tasks-orchestrator` confirms it exists before entry; if it is missing, the stage is `blocked` (`needed_from: human:harness-author`). No persona writes or edits it.

The gate has three layers, applied in order:

1. **Deterministic checklist (§2, D1–D18).** Run by script or plain shell in phase P5 VERIFY and written to `04-tasks/gate/verify-report.json`, with the `shared-traceability-keeper` exit report (`trace/report-tasks-exit.json`). Any failure is a BLOCKER and goes to the owning worker; **no critic round is spent**. A critic handed a failing or missing verify report returns `rejected`.
2. **Critic rubric (§3, §4).** `tasks-critic` writes a delivery pre-mortem from `plan/slices.json`, `plan/dag.json` and the upstream cold-read summaries **before** reading `handoff.md`'s own risk narrative, then judges the frozen backlog **only** against the criteria below: binary pass/fail per criterion with an evidence pointer, plus an end-to-end spot-check of ≥5 tasks (brief → pointers → upstream AC → named test). The dry-run report (`dry-run/report.md`) and the shared reviews are inputs to the critic, not separate gates. Anything not tied to a criterion is an `observation`; new criteria are proposed only as observations.
3. **Decision rule (§5).** `tasks-orchestrator` applies it mechanically. The critic's `PASS | REVISE | ESCALATE` is advisory.

Severity follows product-pipeline-conventions §6.1: rubric mapping first, judgment second. Must-meet failure = BLOCKER, never lowered except by a human override. Raising severity needs a `failure_scenario` ("an agent executing T-S03-02 would …"); every BLOCKER and MAJOR carries one. Finding IDs use `TASKS-G-NNN`, stable across rounds.

## 2. Deterministic checklist

Every check is BLOCKER on failure. Evidence is the line for that ID in `gate/verify-report.json` (D17 cites the keeper report).

| ID | Check | Severity |
|---|---|---|
| D1 | Schema files exist; `tasks.json`, `slices.json`, `dag.json`, `flags.json`, `migrations.json` validate against schema v1.0; required `handoff.md` headings present; every `briefs/<id>.md` exists and was regenerated from the current `tasks.json` (hash match). | BLOCKER |
| D2 | IDs unique and match their regexes; no ID from a previous `handoff_version` renumbered or reused; every referenced upstream ID resolves in the upstream JSON. | BLOCKER |
| D3 | DAG acyclic; every `depends_on` resolves; critical path recomputed and matching `handoff.md`; no dependency on a later milestone's task unless typed `SS`. | BLOCKER |
| D4 | Path reality: every `files.modify` path exists at `base_ref`; every `files.create` path does not exist yet and sits under an existing or planned directory; every `context_pointers` `file:line` range exists. | BLOCKER |
| D5 | Parallel safety: every pair of concurrently runnable `parallel_safe` tasks has disjoint file sets. | BLOCKER |
| D6 | Coverage (100% rule): every Must FR and Must AC → ≥1 task; every AC → ≥1 named test; every task → ≥1 upstream ID or enabling item (ADR, FF, ledger item, risk); no orphans. | BLOCKER |
| D7 | Every task has ≥1 GWT AC, ≥1 verification command with expected result, non-empty `files`, `split_pattern`, `size.fits_one_pr: true`, `dod`, `stop_conditions`. | BLOCKER |
| D8 | Walking skeleton: `MS-1` contains a slice touching every container in the architecture's skeleton definition, with build + deploy + ≥1 E2E test, first in topological order (brownfield: slice 1 still proves the new path end to end). | BLOCKER |
| D9 | Risk-first: every open architecture risk and rabbit hole has a spike or mitigation task preceding the dependent value tasks, or an owned acceptance; each spike has a question, timebox, output (`decision` or `adr_request`) and disposable code. | BLOCKER |
| D10 | Test-first: within each slice the task creating an AC test precedes or equals the implementing task; every service boundary has a row in `contract-decisions.csv`. | BLOCKER |
| D11 | Release safety: every flag has a removal task; every migration is expand → migrate → contract across separate tasks, or has an approved-downtime `DL-T-` entry; every milestone has rollback steps and signals to watch. | BLOCKER |
| D12 | Every fitness function in `03-architecture/evolution/fitness-functions.yaml` has an implementing task in CI or observability. | BLOCKER |
| D13 | Cross-cutting tasks present when routing fired: SAST/SCA/secret scanning/SBOM or a waiver; restore, load and alert/runbook tasks for SLO-bearing journeys; instrumentation + event-QA per PRD event; a11y DoD on every UI task; privacy tasks (deletion jobs, DSAR) when personal data exists. | BLOCKER |
| D14 | Ownership: no task spans two `owner_boundary` values. | BLOCKER |
| D15 | Ambiguity lint (PRD banned-term list plus "handle gracefully", `TBD`) on task titles, objectives and ACs. | BLOCKER |
| D16 | Proportionality to `scale_mode`: task count and ACs per task within budget or each excess justified; no task below the size floor. | BLOCKER |
| D17 | Keeper exit report: 0 forward gaps on Must items, 0 unjustified orphans. | BLOCKER |
| D18 | `open-questions.json` has 0 `blocking: yes`; every ledger row targeted at `tasks` resolved (task, DoD item) or re-deferred with a reason. | BLOCKER |

## 3. Must-meet criteria

Each FAIL is a BLOCKER. A passing must-meet is recorded with its evidence pointer.

| ID | Criterion | Pass evidence |
|---|---|---|
| M1 | **Vertical slices, not layers.** | Every slice ends in user-observable behaviour proven by an E2E or acceptance test; no "DB tasks / API tasks / UI tasks" slicing with behaviour arriving only in the last slice; horizontal tasks exist only inside a slice or in Setup/Foundational. |
| M2 | **No hidden design decisions.** | No task picks a library, schema shape, protocol or pattern absent from the ADRs and contracts; every such need is a spike or an `adr_request`. |
| M3 | **Executable cold.** | `dry-run/report.md` shows every sampled task can be started by an agent holding only its brief, without a blocking question. Any blocking question is a finding. |
| M4 | **Acceptance is an oracle.** | Each AC is behavioural, declarative and bound to a named test at the lowest effective level (`test/test-matrix.csv`); tests verify the upstream AC rather than restating the implementation; no task instructs "update tests to pass". |
| M5 | **Sequencing buys information early.** | Walking skeleton first; the riskiest unknowns retired before the value that depends on them; milestone exit criteria demonstrable, not "% complete". |
| M6 | **Trunk stays releasable.** | Every task merges without exposing incomplete behaviour (flag or dark path); schema changes backward-compatible for one release. |
| M7 | **Fidelity to upstream.** | No new scope (gold plating), no dropped Must, no AC reinterpretation without a "Changes from upstream" entry; terminology matches the PRD glossary and contract names. |
| M8 | **Pre-mortem dispositioned.** | The critic's pre-mortem ("the implementation stalled at milestone 2 — why?") yields ≥5 delivery failure reasons across ≥3 categories; each top-5 reason maps to a task, a tripwire in `raid.json`, or an explicit acceptance. An unmapped top-5 reason fails M8. |
| M9+ | **Inherited conditions.** | Each upstream condition with `due_gate: tasks-exit` (imported at entry check E9 into `04-tasks/gate/entry-gate.md`) is satisfied. One numbered item per condition (M9, M10, …). |

Other BLOCKER triggers (conventions §6.1): an undispositioned shared-reviewer refusal hit (fixed, condition, or human override in the decision log); a concrete failure scenario showing a coding agent would build the wrong thing or be unable to proceed; a triggered inherited kill criterion.

## 4. Should-meet criteria

| ID | Criterion | Severity if fail |
|---|---|---|
| S1 | Each split names a SPIDR/Lawrence pattern; splits favour pieces that can be deprioritized or thrown away. | MAJOR |
| S2 | Test allocation pushed down the pyramid: E2E limited to listed critical journeys; no ice-cream cone; high-risk items have ≥2 test levels or a compensating control. | MAJOR |
| S3 | All four agile testing quadrants considered, omissions justified; Q3 exploratory/UAT kept as a human activity. | MAJOR |
| S4 | Parallelism plan realistic: WIP limit stated; no serialization of independent work; no over-parallelization onto hot files. | MAJOR |
| S5 | Autonomy policy flags high-risk task classes (auth, payments, data migration, PII) for human review. | MAJOR |
| S6 | DoR has ≤8 objective items; DoD items verifiable by evidence, not opinion. | MINOR |
| S7 | Test data strategy: synthetic data or builders, deterministic seeds, no raw PII in fixtures. | MAJOR when personal data exists, else MINOR |
| S8 | Length budget: `handoff.md` ≤2 pages; each brief ≤ ~150 lines. | MINOR |

## 5. Decision rule

Applied mechanically by `tasks-orchestrator`. Written values from conventions §6.2.

| Verdict | Rule |
|---|---|
| `GO` | 0 deterministic failures, 0 trace blocking gaps, 0 open BLOCKER, 0 open MAJOR. |
| `GO_WITH_CONDITIONS` | 0 BLOCKER; 1–3 MAJOR, each converted to a condition `{id: CND-T-NNN, finding: TASKS-G-NNN, owner_stage, due_gate, text}`; `due_gate` may be a milestone (e.g. `MS-1`) when the owner is `implementation`. |
| `RECYCLE` (internal, never written) | Any open BLOCKER, or >3 MAJOR, while revision loops remain. |
| `HOLD` | BLOCKER or over-cap MAJOR still open after the round-3 critique; or no progress (same open BLOCKER/MAJOR IDs in two consecutive rounds); or an unresolved reviewer conflict; or an unresolved human-only decision (e.g. risk acceptance, approved downtime). |
| `KILL_RECOMMENDED` | An inherited kill criterion has triggered. The human confirms. |
| `BLOCKED` | Entry gate failed on missing input (including a missing rubric); no exit gate run. |
| `REJECTED_UPSTREAM` | Entry gate rejected the PRD or Architecture handoff (for example a destructive migration with no expand/contract in the architecture). |

MINOR findings never trigger a round and go to `known_issues`. Observations are ignored for gating.

## 6. Loop limits and escalation

From conventions §9:

- **Cap:** critic round 1 → revision 1 → round 2 → revision 2 → round 3 (final). `max_rounds: 3`.
- **Contract first:** the critic fails the backlog only against this rubric.
- **Severity-gated loops:** only open BLOCKER/MAJOR findings trigger a round.
- **Monotonic findings:** after round 1 a new BLOCKER is admissible only if `revision-induced` or `new-evidence`.
- **Narrow revision briefs:** finding IDs, locations and fix conditions only; briefs are regenerated and D1–D18 plus the keeper re-run before the next critique.
- **Disagree-and-commit:** findings `overridden` in `gate/decision-log.md` are never re-raised.
- **No-progress detector:** unchanged open BLOCKER/MAJOR IDs in two consecutive rounds → HOLD immediately.
- **Voting (`deep`/`large` modes):** two independent critic samples; a BLOCKER stands only if both raise it or one cites a deterministic failure.
- **Escalation memo** (embedded in `gate/verdict.json.escalation_memo`): open BLOCKER/MAJOR IDs; the positions of the author worker and the critic; options (fix with a human decision / override with rationale / descope / return upstream / kill); the orchestrator's recommendation; what re-entry would need. The human's choice is recorded in `gate/decision-log.md` as `DL-T-NNN`. The pipeline never silently passes.

## 7. Changelog

| Version | Date | Change | Decided by |
|---|---|---|---|
| tasks-exit-1.0 | 2026-10-02 | Default rubric seeded from the Tasks synthesis "Exit gate" section and the `tasks-critic` / `tasks-orchestrator` persona files. Condition format aligned with conventions §6.3 (`owner_stage` + `due_gate`, milestone allowed). | default (awaiting human review) |

Any change to this file is a human decision taken outside the critic loop. Bump `rubric_version` on every change and record it here.
