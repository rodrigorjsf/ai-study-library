# run-spec

The AFK flow that runs a spec's tickets through implementers, reviewers and a final review, and ends in one pull request.

## Language

### Verification

**Readiness report**:
A per-run statement of how well the target repository can be verified before any ticket runs: what its check commands cover, whether an App recipe exists, and which acceptance criteria name a surface. It informs; it never stops a run.
_Avoid_: Prontidão, preflight, health check

**Check commands**:
The typecheck, lint and test commands the repository owner declares for run-spec in `docs/agents/run-spec.md`. Agents run these instead of guessing them per ticket.
_Avoid_: Verify commands, profile, scripts

**Surface**:
The observable place an acceptance criterion is checked through, named in backticks in the criterion: a command, a route, a file or a screen.
_Avoid_: Entry point (when meaning the criterion's check), observable

**App recipe**:
A committed, project-local skill that tells an agent how to start, check, drive and stop the target application, so no agent rebuilds it per round.
_Avoid_: Runtime oracle, verify script, launch instructions

**Feature map**:
The part of an App recipe that lists the application's features from the user's point of view, how a user reaches each one, and what result proves it works.
_Avoid_: Site map, feature list

**Proven finding**:
A review finding that carries a command whose output shows the defect, or, for a written-rule finding, the line of the rule it breaks. Only proven findings can block.
_Avoid_: Verified finding, confirmed finding

**Unproven finding**:
A review finding without that proof. It is advisory and never starts a review round.
_Avoid_: Weak finding, opinion

**Run metrics**:
One record per finished run of a spec: findings per axis, dismissals, rounds, unverified criteria, unproven findings, and whether the run's pull request was later reverted.
_Avoid_: Trust ledger, ledger, scorecard

**Findings buffer**:
The per-repository log every run appends its review findings and dismissals to, read later to find mistake classes that recur across runs.
_Avoid_: Findings log, learnings

**Mistake class**:
A set of review findings that one rule or one check could have prevented, whatever their file, run or wording. It is listed once it has two occurrences in the Findings buffer; a `dismissed` or `unproven` line is no occurrence.
_Avoid_: Pattern, theme, category

**Fix level**:
How firmly a check stops a mistake class, from the highest that works: architecture, types, a lint whose error names the fix, a test, docs. A class gets the highest level that works, with the reason each higher level does not.
_Avoid_: Severity, priority
