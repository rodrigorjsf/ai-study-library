---
rubric_id: prd-exit
rubric_version: prd-exit-1.0
stage: prd
gate: exit
owner: human
status: default
changes_require: human decision
critic: prd-critic
decider: prd-orchestrator
finding_prefix: PRD-G-NNN
max_rounds: 3
---

# PRD exit-gate rubric (prd-exit-1.0)

## 1. Purpose and how it is used

This file is the published contract for the PRD exit gate. `install.sh` seeds it into `docs/pipeline/gates/prd-exit-rubric.md`; after that it is human-owned. It must exist before a PRD run starts. If it is missing, `prd-orchestrator` and `prd-critic` stop with `blocked` (`needed_from: human:harness-author`). Neither ever writes or edits it.

The gate has three layers, applied in order:

1. **Deterministic checklist (§2, D1–D16).** Run by script or plain shell in phase P6 VERIFY and written to `02-prd/gate/verify-report.json`, together with the `shared-traceability-keeper` exit report (`trace/report-prd-exit.json`). Any failure is a BLOCKER, goes back to the owning worker, and **no critic round is spent**. A critic handed a failing verify report returns `rejected` without a judgment pass.
2. **Critic rubric (§3, §4).** `prd-critic` reads `handoff.md` + `prd.md` §1–2 cold first, then judges the frozen package **only** against the criteria below: binary pass/fail per criterion with an evidence pointer. It applies an Internal-FAQ / pre-mortem lens (S2) and a Nielsen heuristic lens on flows (S7). Anything not tied to a criterion is an `observation`; new criteria are proposed only as observations.
3. **Decision rule (§5).** `prd-orchestrator` applies it mechanically. The critic's `PASS | REVISE | ESCALATE` is advisory.

Severity follows product-pipeline-conventions §6.1: rubric mapping first, judgment second. Must-meet failure = BLOCKER, never lowered except by a human override. Raising severity needs a `failure_scenario`; every BLOCKER and MAJOR carries one. Finding IDs use `PRD-G-NNN`, stable across rounds.

## 2. Deterministic checklist

Every check is BLOCKER on failure. Evidence is the line for that ID in `gate/verify-report.json` (D11 also cites the keeper report).

| ID | Check | Evidence | Severity |
|---|---|---|---|
| D1 | All schema files exist; JSON validates against schema v1.0; required headings in `handoff.md` and `prd.md` present. | schema + heading scan | BLOCKER |
| D2 | IDs unique, match their prefix regex (e.g. `^FR-\d{3}$`); no ID from a previous `handoff_version` renumbered or reused. | ID registry diff | BLOCKER |
| D3 | Every FR statement matches an EARS pattern and contains exactly one `shall`. | regex output | BLOCKER |
| D4 | Banned-term lint clean (`fast, quick, user-friendly, intuitive, seamless, robust, flexible, scalable, easy, simple, as appropriate, etc., and/or, support, minimize, maximize, real-time, secure`) unless the term is quantified in the fit criterion. | lint output | BLOCKER |
| D5 | Every FR has a `fit_criterion` and a `priority` under the single declared method. | field scan | BLOCKER |
| D6 | Every Must FR has ≥1 positive and ≥1 negative/boundary AC, plus a `feasibility.verdict`. | join output | BLOCKER |
| D7 | `nfr.json` has all 9 ISO/IEC 25010:2023 characteristics (target, or `n/a` + reason); every performance NFR has percentile + load + measurement point. | field scan | BLOCKER |
| D8 | Exactly one primary metric with baseline (value + source, or `unknown` + instrumentation requirement), target and window; ≥1 guardrail with numeric threshold and breach action. | `metrics.json` scan | BLOCKER |
| D9 | ≥3 non-goals, each typed `never` or `not-now`; ≥1 `Won't` item; Must share ≤60% of items or estimated effort. | count table | BLOCKER |
| D10 | State matrix has no empty in-scope cells (`n/a` needs a reason); every error class has a recovery path and a `strings.csv` key; no `TBD`, `Lorem`, "Something went wrong". | matrix scan | BLOCKER |
| D11 | Keeper report: 0 orphan FRs; 0 Must goals without an FR; every Discovery Must opportunity covered or `dropped` with rationale and approver. | `trace/report-prd-exit.json` | BLOCKER |
| D12 | Every event in `metrics.json` maps to an FR ID and a metric; every PII-flagged property has a privacy-review reference. | join output | BLOCKER |
| D13 | Routed cross-cutting outputs present: ASVS level declared with rationale; privacy inventory and DPIA/RIPD screening; a11y conformance target; SLO NFRs for critical journeys. | `reviews/*` + `nfr.json` | BLOCKER |
| D14 | `open-questions.json` has 0 `blocking: yes`; no `TBD`/`TODO` in Must sections. | field scan | BLOCKER |
| D15 | Proportionality budget for `scale_mode`: FR count and ACs per FR within budget, or each excess justified. | count vs budget | BLOCKER |
| D16 | Implementation-noun lint: technology, database, framework and endpoint names in FR/NFR text only where `constraint_source` is non-null. | lint output | BLOCKER |

## 3. Must-meet criteria

Each FAIL is a BLOCKER. A passing must-meet is recorded with its evidence pointer.

| ID | Criterion | Pass evidence |
|---|---|---|
| M1 | **Fidelity to Discovery.** No invented evidence and no silent scope change. | Every problem, segment and evidence claim cites a Discovery ID; every number has a source or `assumption: true`; `evidence_mode` inherited verbatim and no "validated" claim rests on non-real evidence; every delta listed under "Changes from Discovery" with a rationale. |
| M2 | **Every Must FR is verifiable.** | EARS statement, measurable fit criterion, ACs that give examples rather than restating the requirement; no subjective words in ACs. |
| M3 | **Non-goals are plausible and enforced.** | Each non-goal is scope a reader might reasonably have assumed; no FR, flow or event contradicts a non-goal. |
| M4 | **Success is defined before build.** | Primary metric can plausibly be moved by this scope, is not a vanity metric, and the guardrail's breach action is actionable. |
| M5 | **NFRs are measurable and design-free.** | Each NFR is a user-observable target (not "use Redis") convertible by Architecture into a six-part quality-attribute scenario. |
| M6 | **Scope fits the appetite.** | Musts fit the appetite per the feasibility note, or the cut set has been applied; rabbit holes are named and patched, or sent to Architecture as risks. |
| M7 | **Unhappy paths are covered.** | Each external input or integration has an "If…then" FR; each user-observable FR appears in a flow and each flow step maps to an FR (bidirectional). An open Nielsen severity-4 issue on a critical flow fails M7. |
| M8 | **Cold read.** | From `handoff.md` + `prd.md` §1–2 alone a fresh reader states what, for whom, why, how we will know, what not, and what is open; the critic's cold-read notes match the files. |
| M9+ | **Inherited conditions.** | Each upstream condition with `due_gate: prd-exit` (imported at entry check E7 and listed in `02-prd/gate/entry-gate.md`) is satisfied. One numbered item per condition (M9, M10, …). |

Other BLOCKER triggers (conventions §6.1): a shared-reviewer refusal criterion hit that is not dispositioned (fixed, carried as a condition, or human override in the decision log); a concrete failure scenario in which Architecture or Tasks cannot proceed or would build the wrong thing; a triggered inherited kill criterion.

## 4. Should-meet criteria

| ID | Criterion | Severity if fail |
|---|---|---|
| S1 | Alternatives considered for the top 3 scope / product decisions (for example which Must was cut and why). | MAJOR |
| S2 | Internal-FAQ / pre-mortem lens: top 5 "why this fails" reasons (including ≥1 silent failure) each have a disposition: change / risk with tripwire / accept. | MAJOR |
| S3 | Prioritization inputs evidence-cited; RICE Confidence capped at 50% when Reach is not from Discovery evidence. | MAJOR |
| S4 | Proportionality: document size suits the appetite (no 40 ACs for a small batch). | MAJOR |
| S5 | Release criteria are binary and reference AC / NFR / metric IDs. | MAJOR |
| S6 | Glossary covers every domain noun used in ≥2 requirements; one term per concept across FRs, flows and strings. | MINOR |
| S7 | Heuristic inspection of flows (Nielsen H1, H3, H5, H9 on critical flows): no open severity-3/4 issue. | MAJOR (severity 4 → BLOCKER via M7) |
| S8 | Length budget: `handoff.md` ≤2 pages; `prd.md` within the scale-mode budget. | MINOR |

## 5. Decision rule

Applied mechanically by `prd-orchestrator` to `findings.json` + verify + trace. Written values from conventions §6.2.

| Verdict | Rule |
|---|---|
| `GO` | 0 deterministic failures, 0 trace blocking gaps, 0 open BLOCKER, 0 open MAJOR. |
| `GO_WITH_CONDITIONS` | 0 BLOCKER; 1–3 MAJOR, each converted to a condition `{id: CND-P-NNN, finding: PRD-G-NNN, owner_stage, due_gate, text}` (conventions §6.3). |
| `RECYCLE` (internal, never written) | Any open BLOCKER, or >3 MAJOR, while revision loops remain. |
| `HOLD` | BLOCKER or over-cap MAJOR still open after the round-3 critique; or no progress (same open BLOCKER/MAJOR IDs in two consecutive rounds); or an unresolved conflict between reviewers or between critic and reviewer; or an unresolved human-only decision (legal basis, DPIA/RIPD necessity, SLO business target, cost ceiling, risk acceptance). |
| `KILL_RECOMMENDED` | An inherited kill criterion has triggered. Only the human confirms. |
| `BLOCKED` | Entry gate failed on missing input; no exit gate run. |
| `REJECTED_UPSTREAM` | Entry gate rejected the Discovery handoff. |

MINOR findings never trigger a round and go to `known_issues`. Observations are ignored for gating.

## 6. Loop limits and escalation

From conventions §9:

- **Cap:** critic round 1 → revision 1 → round 2 → revision 2 → round 3 (final). `max_rounds: 3`, at most 2 revision loops.
- **Contract first:** the critic fails the PRD only against criteria in this file.
- **Severity-gated loops:** only open BLOCKER/MAJOR findings trigger a round.
- **Monotonic findings:** after round 1 a new BLOCKER is admissible only if the revision caused it or new evidence is cited; otherwise it is downgraded to a note.
- **Narrow revision briefs:** finding IDs, locations and fix conditions only; deterministic checks re-run before the next critique.
- **Disagree-and-commit:** findings `overridden` in `gate/decision-log.md` are never re-raised.
- **No-progress detector:** unchanged open BLOCKER/MAJOR IDs in two consecutive rounds → HOLD immediately.
- **Voting (`deep`/`large` modes):** two independent critic samples; a BLOCKER stands only if both raise it or one cites a deterministic failure.
- **Escalation memo** (embedded in `gate/verdict.json.escalation_memo`): open BLOCKER/MAJOR IDs; the author's and the critic's positions; options (fix with a human decision / override with rationale / descope / return upstream / kill); the orchestrator's recommendation; what re-entry would need. The human's choice is recorded in `gate/decision-log.md` as `DL-P-NNN` so later fresh sessions inherit it. The pipeline never silently passes.

## 7. Changelog

| Version | Date | Change | Decided by |
|---|---|---|---|
| prd-exit-1.0 | 2026-10-02 | Default rubric seeded from the PRD synthesis "Exit gate" section and the `prd-critic` / `prd-orchestrator` persona files. HOLD list aligned with conventions §6.2 (unresolved human-only decision added). | default (awaiting human review) |

Any change to this file is a human decision taken outside the critic loop. Bump `rubric_version` on every change and record it here.
