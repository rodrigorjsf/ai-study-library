---
rubric_id: discovery-exit
rubric_version: discovery-exit-1.0
stage: discovery
gate: exit
owner: human
status: default
changes_require: human decision
critic: discovery-critic
decider: discovery-orchestrator
finding_prefix: DISC-G-NNN
max_rounds: 3
---

# Discovery exit-gate rubric (discovery-exit-1.0)

## 1. Purpose and how it is used

This file is the published contract for the Discovery exit gate. It is seeded by `install.sh` into `docs/pipeline/gates/discovery-exit-rubric.md` and is human-owned from then on. It must exist before a Discovery run starts: if it is missing, `discovery-orchestrator` and `discovery-critic` stop with `blocked` (`needed_from: human:harness-author`) and never improvise criteria.

The gate has three layers, applied in this order:

1. **Deterministic checklist (§2).** Run by script or plain shell, written to `01-discovery/gate/verify-report.json`. Any failure is a BLOCKER and goes back to consolidation; **no critic round is spent** until it passes. The shared traceability report (`trace/report-discovery-exit.json`) must also show zero blocking gaps.
2. **Critic rubric (§3, §4).** `discovery-critic` writes a blind pre-mortem from `gate/premortem-brief.md` first, then judges the frozen package **only** against the criteria below: binary pass/fail per criterion, each with an evidence pointer (file + heading or ID). Anything not tied to a criterion is an `observation` and never gates. The critic may propose rubric changes only as observations.
3. **Decision rule (§5).** `discovery-orchestrator` applies it mechanically to `findings.json` + verify report + trace report. The critic's `PASS | REVISE | ESCALATE` is advisory; the finder is never the decider.

Severity follows product-pipeline-conventions §6.1: rubric mapping first, judgment second. A must-meet failure is always a BLOCKER and only a human may override it. Raising a severity above the rubric default needs a `failure_scenario`; every BLOCKER and MAJOR carries one. Finding IDs use `DISC-G-NNN` and stay stable across rounds.

## 2. Deterministic checklist

All checks are BLOCKER on failure unless marked otherwise. Evidence is the line in `gate/verify-report.json` for that ID.

| ID | Check | Evidence | Severity |
|---|---|---|---|
| X-D1 | `handoff.md` frontmatter validates (common envelope + Discovery fields, conventions §3.2–§3.3); enums valid; `status` equals `gate/verdict.json.verdict`. | schema validation output | BLOCKER |
| X-D2 | All 21 body sections present, or `n/a — <reason>` where permitted. | heading scan | BLOCKER |
| X-D3 | IDs match the Discovery prefix regex, are unique, and every `traces_to` / `evidence_ids` / `test_id` resolves. | ID registry diff | BLOCKER |
| X-D4 | No `TBD` / `TODO` / `???` in sections 1–11 and 15–17. | grep output | BLOCKER |
| X-D5 | Every EVD has `evidence_type`, `strength`, `source`; desk EVD have URL + `accessed` date; real EVD have file + locator. | ledger scan | BLOCKER |
| X-D6 | No ASM `supported_by_real` without ≥1 linked `real_*` EVD of strength `do`/`commit`; no ASM lists a `synthetic` EVD. | ledger join | BLOCKER |
| X-D7 | `evidence_mode: desk_only` ⇒ `recommendation ≠ proceed`. | frontmatter check | BLOCKER |
| X-D8 | Counts: OPP ≥3; SOL ≥3 (+SOL-000) for the target opportunity; ≥1 ASM per risk category for the leading direction; NG ≥3; exactly one primary MET with formula, population, window, baseline-or-`unknown`; ≥1 guardrail; ≥1 KILL with threshold and date/trigger. | count table | BLOCKER |
| X-D9 | Every leap-of-faith ASM has a `test_id` resolving to a TST with a non-empty threshold. | join output | BLOCKER |
| X-D10 | Every numeric token in sections 8–11 sits next to a source pointer or `[assumption]`. | heuristic lint hit list | Heuristic: hits are listed for critic confirmation; a confirmed hit is a BLOCKER under M6 |
| X-D11 | Solution-word lint on PRB/OPP/HMW ("app", "platform", "AI", "dashboard", "automate", …) and Mom Test phrase lint ("would", "might", "love", "easy to use") on EVD statements. | lint hit list | **Warning only**, passed to the critic for M1 / M3 judgment |
| X-D12 | Every finding `location` in `findings.json` resolves to a real file and anchor (hallucinated-evidence guard). | resolver output | BLOCKER |

Traceability (keeper `exit` mode): 100% of OPP/SOL/ASM/TST/MET/KILL carry IDs and parent links (OUT → OPP → SOL → ASM → TST); no orphans; IDs stable against the previous version. A blocking gap is a BLOCKER and returns to consolidation before any critic round.

## 3. Must-meet criteria

Each FAIL is a BLOCKER. For a must-meet that passes, the critic writes "no BLOCKER because…" with the evidence pointer.

| ID | Criterion | Pass evidence | Fail example |
|---|---|---|---|
| M1 | Problem statement is solution-free and complete. | PRB-001 names segment + circumstance + current workaround + cost; no solution nouns or verbs; cites EVD or ASM. | "Clinicians need an AI scribe app." |
| M2 | One measurable outcome. | OUT-001 ↔ MET-001 with formula, population, window, source, and baseline or `unknown — instrumentation needed`; ≥1 guardrail; not a vanity metric. | "Increase engagement." |
| M3 | Evidence integrity. | No ASM status exceeds what its evidence supports (desk ≤ `supported_by_desk`; `supported_by_real` needs real + `do`/`commit`); synthetic evidence never supports; `desk_only` caps respected; contradicting evidence reported. | "Validated (5 synthetic interviews)." |
| M4 | Risk coverage and testability. | Register covers all 5 risk categories for the leading direction; every leap of faith has a pre-registered test (threshold, sample, method, decision rule); pre-mortem reasons map to an ASM/RSK with an adequate test or mitigation. | Feasibility and ethical rows missing; "test with users" with no threshold. |
| M5 | Divergence before convergence. | ≥3 alternative frames recorded in DEC-*; ≥3 OPP, none a solution in disguise; ≥3 materially different SOL compared on the same criteria. | Three UI variants of the stakeholder's idea. |
| M6 | Numbers are honest. | Every number sourced or `[assumption]`; spot-checked citations (about 20% of desk citations, min 3, max 8) resolve and support the claim; bottom-up sizing with ranges and TAM ⊇ SAM ⊇ SOM, or `n/a — internal` with cost of problem. | "SOM = 1% of $40B (Gartner)" with no URL. |
| M7 | Recommendation follows the evidence. | Recommendation in enum; recommendation rule obeyed (untested value leap of faith or `desk_only` → at most `proceed_with_conditions`; refuted value/viability with no alternative → `pivot`/`kill`); kill criteria pre-declared (metric, threshold, date); decision-quality checks answered (alternatives on same criteria, base rates, calibrated confidence, dissent explored); critic states `concur | dissent`. | `proceed` with an untested value leap of faith and no conditions. |
| M8 | Self-contained for a fresh session. | Cold read of `handoff.md` alone yields outcome, problem, segment, recommendation, non-goals and open blockers, matching the files; every `must_answer_before.prd` item has an owner. | A key decision lives only in chat or in an unlinked worker file. |

**Run-scoped additions (re-entry only).** On a loop-back re-entry run, each item from the loop-back rejection record accepted at entry check E-S8 becomes an additional must-meet criterion for that run only, numbered M9, M10, … and listed in `gate/entry-gate.md`. Failure is a BLOCKER. In a first run there are no M9+ items and the critic evaluates M1–M8 only.

Other BLOCKER triggers that are not separate criteria (conventions §6.1): a triggered kill criterion presented as `proceed`; a cross-cutting legal or safety red flag left undispositioned; a shared-reviewer refusal criterion hit.

## 4. Should-meet criteria

Each FAIL takes the pre-assigned severity below.

| ID | Criterion | Severity if fail |
|---|---|---|
| S1 | Alternatives landscape includes non-consumption / workaround and indirect competitors; vendor claims are labelled. | MAJOR |
| S2 | Four-forces table complete, each force with ASM IDs (adoption risk visible). | MAJOR |
| S3 | JTBD formats canonical: solution-agnostic jobs, ODI grammar, no survey-less opportunity scores. | MAJOR |
| S4 | Lean Canvas complete; unfair advantage defensible or "none yet"; unit economics as formula + break-even. | MAJOR |
| S5 | Pre-mortem top 5 each have a leading indicator and a disposition (change / tripwire / accept) in the register. | MAJOR |
| S6 | Every shared-reviewer finding dispositioned: fixed, deferred with target stage (ledger row), or disputed with a reason. | MAJOR |
| S7 | Feasibility flags present and phrased as questions (no technology decisions). | MAJOR |
| S8 | Non-goals plausible (scope a reader might assume), ≥3. | MINOR |
| S9 | Glossary covers all domain nouns in PRB/OPP/JOB; hotspots routed. | MINOR |
| S10 | Sources older than 3 years flagged; access dates present. | MINOR |
| S11 | Length budget: `handoff.md` ≤ ~8 pages excluding tables; BLUF ≤15 lines. Length is not a quality signal. | MINOR |

## 5. Decision rule

Applied mechanically by `discovery-orchestrator`. Written `status` / `verdict` values come from conventions §6.2.

| Verdict | Rule |
|---|---|
| `GO` | 0 deterministic failures, 0 trace blocking gaps, 0 open BLOCKER, 0 open MAJOR. |
| `GO_WITH_CONDITIONS` | 0 BLOCKER; 1–3 MAJOR, each converted to a condition `{id: CND-NNN, finding: DISC-G-NNN, source, owner_stage, due_gate, text}` (conventions §6.3). |
| `RECYCLE` (internal, never written) | Any open BLOCKER, or >3 MAJOR, while revision loops used < 2. |
| `HOLD` | After the round-3 critique a BLOCKER or over-cap MAJOR is still open; or no progress (same open BLOCKER/MAJOR IDs in two consecutive rounds); or an unresolved critic–reviewer conflict; or an unresolved human-only decision; or critic `dissent` on a triggered kill criterion. |
| `BLOCKED` | Entry gate failed on missing input; no exit gate run. |
| `REJECTED_UPSTREAM` | Entry gate rejected the input (for example malformed re-entry evidence). |

`KILL_RECOMMENDED` is **never** written at Discovery: kill is a recommendation plus a human decision (go / go-with-conditions / pivot / kill), recorded in `human_decision` and as DEC-*. MINOR findings never trigger a round; they go to `known_issues`. Observations are ignored for gating.

## 6. Loop limits and escalation

From conventions §9:

- **Cap:** critic round 1 → revision 1 → round 2 → revision 2 → round 3 (final). `max_rounds: 3`.
- **Severity-gated loops:** only open BLOCKER/MAJOR findings trigger another round.
- **Narrow revision briefs:** only finding IDs, locations and fix conditions go to the owning worker (`briefs/<persona>-r<N>.md`); deterministic checks and the keeper `exit` re-run before the next critique.
- **Monotonic findings:** after round 1 a new BLOCKER is admissible only if the revision caused it or new evidence is cited.
- **Disagree-and-commit:** a finding marked `overridden` in `gate/decision-log.md` is never re-raised, in this run or in re-entry runs.
- **No-progress detector:** unchanged open BLOCKER/MAJOR IDs across two consecutive rounds → HOLD immediately.
- **Voting (`deep` tier):** two independent critic samples in round 1; a BLOCKER stands only if both raise it or one cites a deterministic failure.
- **Escalation memo** (`gate/escalation-memo.md`, pointed to by `verdict.json`): open BLOCKER/MAJOR IDs with the critic's and the author's positions; options (fix with more time / human override with rationale / descope, e.g. narrow segment / pivot / kill); the orchestrator's recommended option; what re-entry would need. The orchestrator asks the human and records the choice in `decision-log.md`. The pipeline never silently passes.

## 7. Changelog

| Version | Date | Change | Decided by |
|---|---|---|---|
| discovery-exit-1.0 | 2026-10-02 | Default rubric seeded from the Discovery synthesis §5 and the `discovery-critic` / `discovery-orchestrator` persona files. Clarified X-D10 (heuristic, critic-confirmed under M6) and X-D11 (warning only); made E-S8 re-entry items explicit as run-scoped M9+. | default (awaiting human review) |

Any change to this file is a human decision taken outside the critic loop. Bump `rubric_version` on every change and record it here; runs record the version they were judged against.
