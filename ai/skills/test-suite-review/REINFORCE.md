# Reinforce

Reached when genuine coverage is under 80%: the suite reported a number its tests did not earn, and the distance has to be closed with tests that protect the domain. A reinforcement test written only to execute lines is padding, and the review would remove it.

## 1. Understand the domain

Read what states the domain's rules: the glossary (`GLOSSARY.md`, `CONTEXT.md`), ADRs, specs and issues, API contracts, and the names of the modules themselves. From the code, list the **domain rules**: calculations, validations, state transitions, authorisation decisions, limits, and the error behaviour each interface promises.

Done when each in-scope module has its domain rules listed in the report, in the domain's own terms.

## 2. Find where the domain is exposed

Lay the genuine-coverage report over the domain rules. A rule is **exposed** when its code is uncovered, or covered only by padding, or covered by a test whose assertions would pass with the rule broken (a surviving mutant shows this).

Rank the exposed rules:

1. rules with branches, boundaries, or arithmetic
2. rules that changed recently or sit in files that keep coming up in `git log`
3. rules whose failure costs most (money, permissions, data loss)
4. everything else

Glue, configuration, generated code, and trivial accessors are not domain rules. Where they are a large share of the uncovered lines, say so in the report and recommend a coverage exclusion to the user; do not test them to reach the number.

Done when every exposed rule is ranked, with the lines it would cover.

## 3. Plan tests at the seams

For each exposed rule, top of the ranking first, plan one test or one parameterized test:

- at the module's **seam**, through its public interface, so the test survives a refactor
- named for the behaviour, in the domain's terms
- one row per equivalence class and per boundary, each expected value an independent literal or a worked example
- real collaborators; fakes only at system boundaries (external services, time, randomness, sometimes the database or filesystem)

Stop planning when genuine coverage plus the planned tests reaches the target.

A rule that cannot be reached through any seam without a production change is a **finding**: record the missing seam. If the findings are what keeps the target out of reach, stop and take that to the user at the gate, since reaching 80% then needs production changes this review does not make.

## 4. Prove each test when it is written

In the worktree, each reinforcement test is written one at a time: see it green, then see it **red** by breaking the rule it protects (run the mutation tool on the rule's class, or change the rule by hand and restore it). A test that stays green with its rule broken protects nothing and is rewritten.

Done when every reinforcement test has gone red on its own rule and coverage is at or above the target.
