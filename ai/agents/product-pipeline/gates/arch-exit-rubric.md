---
rubric_id: arch-exit
rubric_version: arch-exit-1.0
stage: architecture
gate: exit
owner: human
status: default
changes_require: human decision
critic: arch-critic
decider: arch-orchestrator
finding_prefix: ARCH-G-NNN
max_rounds: 3
---

# Architecture exit-gate rubric (arch-exit-1.0)

## 1. Purpose and how it is used

This file is the published contract for the Architecture exit gate. `install.sh` seeds it into `docs/pipeline/gates/arch-exit-rubric.md` (the file name uses `arch`, not `architecture`; `run-stage.sh` maps the stage accordingly). After seeding it is human-owned. `arch-orchestrator` checks it exists at entry (E10) and records its `rubric_version`; if it is missing, the stage is `blocked` (`needed_from: human:harness-author`). No persona writes or edits it.

The gate has three layers, applied in order:

1. **Deterministic checklist (§2, D1–D21).** Run by script or plain shell in phase P7 VERIFY and written to `03-architecture/gate/verify-report.json`, with the `shared-traceability-keeper` exit report (`trace/report-architecture-exit.json`). Any failure is a BLOCKER; structural fixes come first and **no critic round is spent**. A critic handed a failing verify report returns `rejected`.
2. **Critic rubric (§3, §4).** `arch-critic` writes a blind pre-mortem from `exec-summary.md` + `drivers/qas.yaml`, does a cold read, an ATAM walk-through of every (H,H) scenario and risk-storming of the C4 views, then judges the frozen package (excluding `work/`) **only** against the criteria below: binary pass/fail per criterion with an evidence pointer, acknowledging the D-results. Anything not tied to a criterion is an `observation`; new criteria are proposed only as observations.
3. **Decision rule (§5).** `arch-orchestrator` applies it mechanically. The critic's `PASS | REVISE | ESCALATE` is advisory.

Severity follows product-pipeline-conventions §6.1: rubric mapping first, judgment second. Must-meet failure = BLOCKER, never lowered except by a human override. Raising severity needs a `failure_scenario`; every BLOCKER and MAJOR carries one. Finding IDs use `ARCH-G-NNN`, stable across rounds.

## 2. Deterministic checklist

Every check is BLOCKER on failure. Evidence is the line for that ID in `gate/verify-report.json` (D6 also cites the keeper report).

| ID | Check | Severity |
|---|---|---|
| D1 | All schema files exist; YAML/JSON validates; required headings present in `handoff.md`, `architecture.md` (12 arc42 sections, each with content or `n/a — reason`) and every ADR. | BLOCKER |
| D2 | IDs unique and prefix-valid; no upstream ID re-minted; no ADR number reused; every superseded ADR points to its successor. | BLOCKER |
| D3 | Every QAS has all six fields and a numeric or boolean `response_measure`; banned-adjective lint (`fast, scalable, highly available, secure, real-time, robust, seamless`) clean unless quantified; every PRD NFR maps to ≥1 QAS. | BLOCKER |
| D4 | Every ADR MADR-valid: `status`, ≥2 considered options (≥3 if `one-way`), a "because", ≥1 Bad consequence, `Confirmation`, ≥1 `drivers`, `reversibility`. | BLOCKER |
| D5 | Every driving characteristic has ≥1 `FF-` with `metric`, `threshold`, `trigger`, `owner_lane`. | BLOCKER |
| D6 | Keeper trace, both directions: every Must FR → ≥1 `C-`/`CMP-` and ≥1 `BC-`, and an `OP-`/`MSG-` or explicit "no interface" note; 0 orphan containers, components, BCs, operations or ADRs; every PRD rabbit hole → `ADR-` or `SPK-`. | BLOCKER |
| D7 | Every diagram element ID exists in the trace; every C4 element has type, technology and responsibility; every relationship labelled; legend present. | BLOCKER |
| D8 | `openapi/*.yaml` and `asyncapi/*.yaml` validate and pass lint: list operations paginate; errors use `application/problem+json`; unsafe operations have an idempotency key or waiver; every operation has a security scheme; AsyncAPI 3.0 `operations.action`, no 2.x `publish/subscribe`. | BLOCKER |
| D9 | ODCS contracts validate against the ODCS v3 schema. | BLOCKER |
| D10 | Glossary consistency: every public schema/resource name, event name and logical entity is a glossary term or declared alias. | BLOCKER |
| D11 | Data inventory: every PII/regulated element has owner BC, system of record, classification, retention, deletion mechanism, and coverage of logs, backups, event streams and analytics copies. | BLOCKER |
| D12 | Vague-consistency lint: `eventually consistent`, `ACID`, `real-time`, `exactly-once` qualified by a guarantee/isolation level, numeric staleness bound or mechanism. | BLOCKER |
| D13 | Dual-write lint: every producer that writes a DB and publishes a message references an outbox, CDC or event store in `integration/delivery.md`. | BLOCKER |
| D14 | When `org/tech-radar.*` exists, no `Hold` technology without an exception ADR. | BLOCKER |
| D15 | Threat model: every DFD element has ≥1 STRIDE row or `n/a` reason; no `disposition: TBD`; every `accept` has a `risk_owner`. | BLOCKER |
| D16 | Every external dependency has a timeout, a retry bound and a fallback. | BLOCKER |
| D17 | When FinOps was triggered, `cost_per_unit` exists at expected and peak scale with dated assumptions. | BLOCKER |
| D18 | Every SLI maps to a telemetry signal; every signal attribute has `pii: Y/N`. | BLOCKER |
| D19 | `risks.json`: every risk has likelihood, impact, and mitigation or owned acceptance; `SP-` and `TP-` lists present (empty only with a reason). | BLOCKER |
| D20 | `open-questions.json` has 0 `blocking: yes`; no `TBD`/`TODO`/`NEEDS CLARIFICATION` in required sections; no `one_way_doors[].human_ack: pending` unless status ≤ GO_WITH_CONDITIONS. | BLOCKER |
| D21 | Proportionality budget for `scale_mode`: ADR count, L3 diagrams and handoff page count within budget, or each excess justified. | BLOCKER |

## 3. Must-meet criteria

Each FAIL is a BLOCKER. A passing must-meet is recorded with its evidence pointer.

| ID | Criterion | Pass evidence |
|---|---|---|
| M1 | **Few drivers, and the right ones.** | 3–7 ranked characteristics, each traced to PRD IDs or an explicit implicit-characteristic reason; every (H,H) utility leaf named; scale envelope stated; no "generic architecture" optimising every -ility; no (H,H) leaf the PRD clearly implies is missing. |
| M2 | **Trade-offs are real.** | Style and quantum decision scored against this system's QAS IDs, not generic pros and cons; rejected options state what is given up; with 1 quantum, the style is a modular monolith or service-based unless an ADR cites a specific granularity disintegrator. |
| M3 | **Every (H,H) scenario is walked through.** | For each (H,H) QAS the design names the tactic(s), explains why the response measure is plausible (stimulus → artifact → tactic through `views/runtime.md` and the ADRs), and records sensitivity and trade-off points. |
| M4 | **Domain and data integrity.** | Each aggregate has ≥1 real invariant citing a PRD/Discovery ID or `assumption`; one owner BC per entity; precise consistency claims; no shared-database integration across BCs; multi-aggregate transactions justified by a named invariant. |
| M5 | **Contracts are consumer-centric and evolvable.** | Every operation/message traces to a PRD use case and a named consumer; no storage model leaks into the contract; error model, versioning and idempotency defined; every cross-BC workflow has a saga or consistency decision with compensations that make business sense. |
| M6 | **Buildable and governable.** | Walking skeleton touches every container; new technologies fit the innovation budget or each has a timeboxed spike; every FF is executable in the stated CI/observability stack or has a task to create it; no big-bang cutover without rollback. |
| M7 | **Risks are honest.** | Top 5 pre-mortem reasons each dispositioned (design change / risk with tripwire / acceptance) in `risks.json`; every one-way door flagged and acknowledged (`DL-A-NNN`) or `pending`; core-domain assumptions ≤3, each with an owner and `confirm_by`. |
| M8 | **Cold read passes.** | From `handoff.md` + `architecture.md` §1–5 alone a fresh reader states the style, containers and responsibilities, the three most consequential decisions, the slicing units, and what is open. |
| M9+ | **Inherited items are met.** | Each PRD condition with `owner_stage: architecture` (or a `due_gate` naming an architecture gate) and each PRD `expected_at_next_gate` item, imported at entry E6/E7 into `03-architecture/gate/entry-gate.md`, is satisfied. One numbered item per condition (M9, M10, …). |

Other BLOCKER triggers (conventions §6.1): an undispositioned shared-reviewer refusal hit; a concrete failure scenario in which Tasks would build the wrong thing; a triggered inherited kill criterion.

## 4. Should-meet criteria

| ID | Criterion | Severity if fail |
|---|---|---|
| S1 | Build-vs-buy recorded for every generic subdomain or non-differentiating capability above trivial size, with switching cost × likelihood of switching. | MAJOR |
| S2 | Ownership lanes line up with containers and BCs; no quantum needs two owners to change it at the same time. | MAJOR |
| S3 | Each runtime view for a top QAS includes the happy path and ≥1 failure path. | MAJOR |
| S4 | Well-Architected coverage index: security, reliability/operations, performance and cost each have a shared-reviewer verdict or `n/a` reason; reviewer conflicts dispositioned. | MAJOR |
| S5 | Reversibility discipline: vendor/engine specifics deferred when the PRD does not need them yet; sacrificial parts flagged. | MAJOR |
| S6 | C4 hygiene beyond D7: one message per diagram, consistent naming, acronyms expanded. | MINOR |
| S7 | `exec-summary.md` ≤1 page, stating options, cost, risk and reversibility in business terms. | MINOR |
| S8 | Length budget: `handoff.md` ≤2 pages, each ADR ≤2 pages, `architecture.md` within the scale-mode budget. | MINOR |

## 5. Decision rule

Applied mechanically by `arch-orchestrator`. Written values from conventions §6.2.

| Verdict | Rule |
|---|---|
| `GO` | 0 deterministic failures, 0 trace blocking gaps, 0 open BLOCKER, 0 open MAJOR, and no `pending` one-way-door acknowledgment. |
| `GO_WITH_CONDITIONS` | 0 BLOCKER; 1–3 MAJOR, each converted to a condition `{id: CND-A-NNN, finding: ARCH-G-NNN, owner_stage, due_gate, text}`; pending one-way-door acknowledgments listed as conditions with `due_gate: tasks-entry`. |
| `RECYCLE` (internal, never written) | Any open BLOCKER, or >3 MAJOR, while revision loops remain. |
| `HOLD` | BLOCKER or over-cap MAJOR still open after the round-3 critique; or no progress (same open BLOCKER/MAJOR IDs in two consecutive rounds); or a reviewer conflict not resolvable within lens rules; or an unresolved human-only decision (SLO target, risk acceptance of a security/privacy blocker, cost ceiling, legal basis). |
| `KILL_RECOMMENDED` | An inherited kill criterion has triggered (for example unit economics at expected scale break a viability kill criterion). The human confirms. |
| `BLOCKED` | Entry gate failed on missing input (including a missing rubric); no exit gate run. |
| `REJECTED_UPSTREAM` | Entry gate rejected the PRD handoff. |

MINOR findings never trigger a round and go to `known_issues`. Observations are ignored for gating.

## 6. Loop limits and escalation

From conventions §9:

- **Cap:** critic round 1 → revision 1 → round 2 → revision 2 → round 3 (final). `max_rounds: 3`.
- **Contract first:** the critic fails the architecture only against this rubric.
- **Severity-gated loops:** only open BLOCKER/MAJOR findings trigger a round.
- **Monotonic findings:** after round 1 a new BLOCKER must be `revision-induced` or `new-evidence`; otherwise it is downgraded to a note.
- **Narrow revision briefs:** finding IDs, locations and fix conditions only; D1–D21 and the keeper re-run before the next critique.
- **Disagree-and-commit:** findings `overridden` in `gate/decision-log.md` are never re-raised.
- **No-progress detector:** unchanged open BLOCKER/MAJOR IDs in two consecutive rounds → HOLD immediately.
- **Voting (`deep`/`large` modes):** two independent critic samples (`critique-r<N>-s<k>.md`); a BLOCKER stands only if both raise it or one cites a deterministic failure.
- **Escalation memo** (embedded in `gate/verdict.json.escalation_memo`): open BLOCKER/MAJOR IDs; the author's and the critic's positions; options (fix with a human decision / override with rationale / descope via PRD re-run / return upstream / kill); the orchestrator's recommendation; what re-entry would need. The human's choice goes into `gate/decision-log.md` as `DL-A-NNN` so a fresh Tasks session inherits it. The pipeline never silently passes.

## 7. Changelog

| Version | Date | Change | Decided by |
|---|---|---|---|
| arch-exit-1.0 | 2026-10-02 | Default rubric seeded from the Architecture synthesis "Exit gate" section and the `arch-critic` / `arch-orchestrator` persona files. | default (awaiting human review) |

Any change to this file is a human decision taken outside the critic loop. Bump `rubric_version` on every change and record it here.
