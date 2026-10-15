# Comparing audited repositories

## 1. Checklist table

Rows are the criteria the concepts chapter derived from the literature (for example: readable source of
truth, LLM dependency, hybrid and token-economic retrieval, forgetting, injected content fenced as untrusted,
local server auth and Origin checks, survives a change of harness, machine and person). Cells are short
verdicts with evidence. Use **Partial** whenever the code only half does it.

## 2. Weighted scorecard

| Criterion | Weight | Repo A | Repo B | Evidence for **both** sides |
|---|---|---|---|---|

- Criteria the user cares about; split a criterion by harness when the harnesses behave differently
  (usability in Claude Code is not usability in Cursor).
- Every row lists the strongest point **against** each repository, not only for it. A column that is only
  positive for one side and only negative for the other is the first thing a reviewer attacks.
- Compare like with like: counts on the same basis (harnesses **with capture** against harnesses with
  capture), defaults against defaults, hardened against hardened.
- Mark rows that are judgement without hands-on testing.

## 3. Sensitivity

A table of alternative weightings (equal weights, each pair of criteria alone, the user's likely profile)
with both totals and the winner. Recompute every number; state ties as ties.

## 4. Scenario recommendations

One row per realistic deployment (enterprise with data constraints, mixed harnesses, solo developer, air-gapped,
multi-user hosts), each with the choice and its preconditions.

## 5. Adversarial review

Before publishing, hand the chapter and the findings files to a critic (an advisor, or a subagent told to
break the verdict) and ask it to attack: scoring bias, unfair comparisons, missing criteria (maturity,
maintainer concentration, release cadence), factual mismatches with the findings, arithmetic. Apply every
objection that holds, rescore, and say in the chapter header that the verdict survived a review and how the
margin changed.

## 6. What none of them solves

Close with the risks that remain whatever the choice, and a pilot with measurable criteria (tokens injected
per session, stale context injected, cost, time to resume a task across harnesses).
