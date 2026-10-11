---
name: test-suite-review
description: Review a codebase's unit tests, cut the ones that add volume without protecting the domain, and reinforce where it is exposed, ending green with at least 80% genuine coverage.
disable-model-invocation: true
---

# Test Suite Review

The goal is a smaller, faster unit suite that protects the domain better. A test earns its place by failing when behaviour the domain cares about breaks. A test that never could fail that way is **padding**: it costs build time and machine resources on every run and buys nothing.

Every change needs **evidence**. A test with no evidence against it stays exactly as it is, and a module whose tests are sound is reported as sound and left alone.

Coverage is a consequence here, never a target to trim toward. **Genuine coverage** is the coverage the sound tests give once the padding is gone. The review removes padding and nothing else, so the number lands wherever the sound tests put it.

## Guardrails

These hold from the first step to the last:

- **Target.** Final coverage, measured as the quality gate measures it, is the higher of 80% and the genuine coverage. A suite at 90% with 88% genuine ends at 88% or above, never trimmed toward 80%. A suite at 80% with 70% genuine is **reinforced**: the review finds where the domain is unprotected and writes the tests that bring it to 80%. Ending above the target is welcome.
- **Carrier.** A test is removed only when a named **carrier**, another test that stays, still fails on the behaviour the removed test protected.
- **Green.** The suite is green at baseline and green after every batch. A test that is red or flaky at baseline is recorded and left out of scope, since nothing can be proved about it.
- **Tests only.** Production code is not edited. Where a better test needs a production change (a missing seam), that is a finding for the report.
- **Unit tests only.** Integration, contract, and end-to-end tests are inventoried and left alone unless the user widens the scope.
- **Excluded means untouched.** Every path the project excludes from Sonar analysis, test analysis, or coverage is outside this review: its tests are not candidates and its files are not edited.
- **Worktree.** Every edit happens in a git worktree based on the branch that is checked out when the skill starts, the **source branch**. The source checkout changes only at the merge in step 10.

## Steps

### 1. Baseline

Record the source branch and its `HEAD`. If the working tree has uncommitted changes, ask the user to commit or stash them first: the worktree starts from `HEAD` and would miss them.

Find the test command, the coverage tool, and the build tool from the environment (build files, CI workflows, `Makefile`, package scripts). Read [ECOSYSTEMS.md](ECOSYSTEMS.md) for the stack's tools.

Find the exclusion scope: if the repo configures Sonar or any coverage exclusion, read [SONAR-SCOPE.md](SONAR-SCOPE.md) and resolve, before measuring, both the excluded paths and the coverage reports the quality gate reads.

Find how the repo separates unit tests from the rest: a naming rule (`*IT`, `*.integration.test.*`), a tag or marker, a directory, or a separate build task. Where the repo draws no line, classify a test as a unit test when it starts no framework context, container, database, or network, and write that rule into the report.

Run the suite with coverage the way the quality gate does, then rerun every failure once: a test that fails then passes is flaky. Record in the report file (`.test-suite-review/report.md`, kept untracked):

- pass, fail, skip, and flaky counts; test count per module
- wall time for the suite, per module, and the 20 slowest tests
- the unit-test rule in use, and the count of tests on each side of it
- line and branch coverage, overall and per module, over the resolved scope and from the same reports the quality gate reads, naming those reports
- mutation score per module, where step 4 will use a mutation tool

Done when the report holds every number above and the suite's red and flaky tests are listed by name.

### 2. Choose where to look

Rank modules by what review can win: test count, wall time, and tests per production line. Take the top of the ranking first; on a small codebase take everything. State the ranking and the cut in the report.

Done when every module is marked in scope or out of scope, with the reason.

### 3. Survey

Read [TEST-SMELLS.md](TEST-SMELLS.md). For each in-scope module, inspect every unit test against it. Where the harness supports sub-agents, dispatch one read-only sub-agent per module, in parallel, with TEST-SMELLS.md pasted in full and the module's test and source paths; otherwise survey the modules in sequence. Sub-agents read and report; every command that runs tests stays in the main thread.

Each survey returns, per candidate: the test's id, the **smell**, the quoted lines that show it, the proposed action (delete, merge, parameterize, rewrite at a higher seam), and the **carrier**. It also returns the module's keep-list hits and a count of tests inspected.

Done when every in-scope module has a returned survey and the tests inspected sum to the baseline test count for those modules.

### 4. Prove, then measure what is genuine

A survey is a reading; proof is a run. Check each candidate with the proof TEST-SMELLS.md names for its smell:

- Where the stack's mutation tool can report which tests kill each mutant (ECOSYSTEMS.md says which can), run it once per module, scoped to the production classes the candidates cover, and keep that **kill matrix**. A candidate is proved when every mutant it kills is also killed by its carrier; a candidate that is the only killer of any mutant goes to the keep-list.
- With a mutation tool that reports only a score, or with none, use per-test coverage plus a read of the carrier's assertions, and mark the candidate **lower confidence**.

Drop every candidate that fails its proof.

Then compute **genuine coverage**: coverage over the resolved scope with every proved padding test left out (run the suite with those tests excluded, or derive it from per-test coverage). Compute it a second time with the lower-confidence candidates left out as well. Record both beside the baseline, with the lines only padding covered.

Done when every candidate is marked proved, lower confidence, or dropped, and the report holds baseline coverage, genuine coverage, and the target.

### 5. Reinforce where the domain is exposed

When genuine coverage is under 80%, read [REINFORCE.md](REINFORCE.md) and plan the domain tests that close the distance. When it is at or above 80%, plan a reinforcement test only for domain logic the survey found unprotected and important; the plan may be empty.

Done when the planned reinforcement, added to genuine coverage, reaches the target, or the report states exactly what blocks it.

### 6. Gate

Give the user the plan and wait for approval:

- coverage: baseline, genuine, target, and expected at the end
- per module: tests today, tests after, by action; expected time saved; mutation score expected after
- the reinforcement tests: which domain rule each protects and at which seam
- lower-confidence candidates in their own list, so the user can strike them
- modules found sound, in one line each
- where the worktree will be created, and that step 10 merges it into the source branch

Leave out any module where the plan would change a handful of tests and save no measurable time: the churn is not worth the diff.

### 7. Open the worktree

Read [WORKTREES.md](WORKTREES.md) and create the worktree where this harness and this repo put worktrees, on a new branch starting at the source branch's `HEAD`. If WORKTREES.md's rules cannot settle the location, ask the user where to create it and wait for the answer before going on.

Before anything else runs in the worktree, check for CodeGraph (`command -v codegraph`). When it is installed, run `codegraph init` at the worktree root: the index is machine-local and a new worktree starts without one, so this is what makes the code graph available for discovery there. Use it from then on to locate code and trace callers. When it is not installed, go on without it. The `.codegraph/` database stays out of every commit.

Then set up the worktree so the suite can run there (dependencies, ignored files the build needs), move the report file into it, and rerun the step 1 measurement.

Done when the worktree's branch points at the source `HEAD` recorded in step 1, CodeGraph is indexed there or recorded as not installed, and the suite's counts and coverage in the worktree match the baseline.

### 8. Apply in batches

All work from here to step 9 happens inside the worktree. A **batch** is one module, or one smell within a large module, and lands as one commit so it can be reverted alone. Reinforcement batches go first, so coverage never dips below the target on the way.

Within a batch, write first and delete second: add the reinforcement, parameterized, or higher-seam test, see it green, then remove the tests it replaces.

After each batch run the module's tests, then check:

- green
- every line a sound test covered at baseline is still covered; every line that lost coverage is listed and was covered only by padding
- mutation score for the touched classes at or above its baseline, where a tool exists

A batch that fails any check is reverted and recorded in the report with the reason; the next batch proceeds.

Done when every approved batch is committed or recorded as reverted.

### 9. Verify the whole

In the worktree, run every test in the codebase (unit and the rest) with coverage, as the quality gate does, and record the numbers beside the baseline.

Done when everything is green and coverage is at or above the target. If either fails, revert batches newest-first, or add reinforcement, until both hold. If the target cannot be reached, stop here: report why, leave the worktree in place, and let the user decide. Nothing is merged.

### 10. Merge into the source branch

Leave the worktree and merge its branch into the source branch from the source checkout. If the source branch moved since step 1, the merge brings both together; a conflict, or a source checkout with uncommitted changes, stops the step and goes to the user.

After the merge, run every test in the codebase with coverage once more on the source branch: this run is the proof. If it is red or under the target, report it and ask the user before reverting the merge.

Then copy the report to `.test-suite-review/report.md` in the source checkout and remove the worktree and its branch the way WORKTREES.md describes for the harness.

Done when the source branch contains the merge, the post-merge run is green at or above the target, and the worktree is gone.

### 11. Recommend speed

With the step 1 timings in hand, read the stack's speed levers in [ECOSYSTEMS.md](ECOSYSTEMS.md). Recommend each lever the timings justify, with the measurement that justifies it and the expected gain. These change build and CI configuration, so they go in the report as recommendations and are applied only on the user's request.

### 12. Show the ledger

Finish the report file and show it to the user. It opens with three statements, each backed by the step 10 run:

- every test in the codebase passes: the command, and the pass, fail, and skip counts
- coverage of the whole codebase: baseline, genuine, target, and final, with the final at 80% or above
- the merge: source branch, merge commit, and the worktree's removal

Then the **ledger**, one row per change:

- every removed or merged test, with its smell and its carrier
- every reinforcement test, with the domain rule it protects
- every line that lost coverage, with the padding that had covered it
- reverted batches and dropped candidates
- before and after: test count, wall time, mutation score

And last: findings that need production changes (missing seams, shallow modules), and the speed recommendations.

Done when every test that existed at baseline and is gone now appears in the ledger with a carrier, and every test added appears with its domain rule.
