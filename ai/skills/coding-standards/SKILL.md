---
name: coding-standards
description: Generate or update CODING_STANDARDS.md at the repo root from the conventions the codebase actually follows.
disable-model-invocation: true
---

# Coding Standards

`CODING_STANDARDS.md` is the **reviewer's** file: it is read when a diff is reviewed, by a human or by an agent in any harness. It holds the **judgement** calls this codebase has settled on, one heading per domain. It is the one home for the repository's coding standards: standards declared in project rule files are **exported** into it, and those files keep only a pointer.

Three rules decide what goes in:

- **Evidence.** Every rule is backed by what the codebase does today: a count of sites that follow it and an exemplar `path:line`. A convention you would like the repo to have is a proposal for the user, kept out of the file until they accept it.
- **Mechanical or judgement.** A **mechanical** rule is a fixed pattern a tool can check (an import shape, a banned API, a naming regex, a file location). A **judgement** rule needs a reader ("matches the surrounding style", "the seam sits at the module interface"). This file owns judgement. A mechanical rule belongs to tooling, and sits in this file only while no check enforces it yet.
- **Single source of truth.** A rule lives in one place. What a linter, formatter, or CI job already enforces stays in its config, named by a pointer. A coding standard declared in a **project** rule file (`AGENTS.md`, `CLAUDE.md`, a rules directory) is exported here and removed from where it was. A **user-level** rule lives outside the repository, so it stays there and gets a **pointer**: its path and a one-line description.

## Steps

### 1. Pick the branch

Look for `CODING_STANDARDS.md` at the repo root.

- Present: this is the **update** branch. Read [UPDATE.md](UPDATE.md) now; it adds work to steps 5, 7 and 8.
- Absent: this is the **create** branch.

### 2. Collect what is already written

Read [HARNESS-RULE-FILES.md](HARNESS-RULE-FILES.md) and check every location it lists, in the repository and at user level. For each rule file found, record its path, its level (project or user), its activation (always loaded, glob-scoped, on demand, manual), and which of its statements are coding standards as opposed to commands, workflow, or navigation. Also read `CONTRIBUTING.md`, the domain glossary (`GLOSSARY.md`, `CONTEXT.md`), ADRs, and any style doc under `docs/`.

Then list the **enforced set**: every linter, formatter, type-checker, static-analysis, pre-commit, and CI config in the repo, with what each one checks.

Done when every repository and user-level location in HARNESS-RULE-FILES.md is recorded as present or absent, every rule file found has its path, level, activation, and its coding-standard statements marked, and every tooling config in the repo is in the enforced set.

### 3. Map the domains

Read [DOMAINS.md](DOMAINS.md). Mark each domain in its catalog as present (with the paths that prove it) or absent. A language, framework, or layer the catalog does not name but the repo contains is a domain too: add it.

Done when every catalog domain carries a verdict and every top-level source directory belongs to at least one present domain.

### 4. Survey each present domain

Find the conventions the code follows. Where the harness supports sub-agents, dispatch one read-only sub-agent per present domain, in parallel, each given that domain's row from DOMAINS.md; otherwise survey the domains in sequence.

Each survey returns candidate rules, and each candidate carries its **evidence**:

- the count: N of M sites follow it
- two exemplars as `path:line`
- every counter-example found, as `path:line`

Every coding-standard statement step 2 marked in a **project** rule file is a candidate too. It carries its source as `path:line` and is checked against the code like any other: a statement the code contradicts becomes a step 6 question.

Weight recently changed code (walk `git log` for the domain's paths): where old and new code disagree, the recent pattern is the convention the team follows now.

Done when every present domain has returned a candidate list or an explicit "no convention found".

### 5. Classify every candidate

Give each candidate exactly one class:

| Class | Test | Destination |
|---|---|---|
| **enforced** | a config in the enforced set already checks it | dropped; the domain section names the config |
| **mechanical** | a tool could check it, none does | in the file, tagged `[check candidate]`, until the check exists; listed for the user as a proposed check |
| **judgement** | only a reader can apply it | in the file |
| **split** | the code disagrees with itself and no pattern clearly leads | a question for the user |
| **user-level** | only a user-level rule file states it | not copied; the domain section points at the rule file |

Then prune **no-ops**: a candidate that any competent reviewer of this language already applies by default says nothing. Delete it.

Done when every candidate carries one class and the no-op pass has run over every judgement and mechanical candidate.

### 6. Settle the splits

Put every **split**, and every contradiction between a written rule and the code, to the user in one numbered round. Give each question the evidence on both sides and your recommended answer, worded so "yes" accepts it. Wait for the answers.

Done when no candidate is still classed split.

### 7. Draft

Write the draft in this shape:

```markdown
# Coding Standards

Read at review time. Rules a tool enforces live in that tool's config and are not repeated here. A rule in a domain section overrides the Baseline.

## <Domain>

Enforced by tooling: `<config path>`.

- **<Rule name>.** <The rule, stated as the behaviour to produce.> _Why:_ <the reason a reviewer needs to apply it to a new case.> _See:_ `path/to/exemplar.ext:42`.
- **<Rule name>.** <The rule.> _Why:_ <reason.> _Detail:_ `.cursor/rules/<name>.mdc`, read when <the condition that calls for the detail>.

### User-level rules

- `~/.claude/rules/<name>.md` (outside this repo): <one line on what it governs>.

## Baseline
```

- One `##` heading per present domain, named as the team names it (`Java`, `Spring`, `Testing`, `Architecture`, `Code documentation`). Order them from most to least touched.
- State each rule as the target behaviour. A prohibition appears only as a hard guardrail, paired with what to do instead.
- Use the glossary's terms for domain concepts.
- A rule exported from a project rule file keeps its author's wording where that wording already states the behaviour.
- `_Detail:_` appears only on a rule whose source rule file is kept in step 9. State the condition for reading it, so a model opens the detail only when it needs that guidance.
- Under `### User-level rules`, list every user-level rule file that governs the domain as a pointer: path and one-line description. Omit the heading when it would be empty. These files exist only on machines that have them, so tell the user which of them the team appears to depend on.
- Counts stay in your report to the user; the file keeps the exemplar, which the codebase keeps true.
- Fill `## Baseline` from [BASELINE.md](BASELINE.md), dropping every baseline item a domain rule overrides or the enforced set already checks.
- Past roughly 1,000 lines, move the longest domain sections to `docs/standards/<domain>.md` and leave one pointer line per section stating when to read it.

Done when every surviving candidate appears exactly once, every rule has a name, a why, and an exemplar that resolves, every coding-standard statement from a project rule file is in the draft or was dropped by a named class, and every user-level rule file is pointed at from at least one section.

### 8. Gate

Show the user the draft, the proposed checks (every `[check candidate]`), and the step 9 change list: for every project rule file, the statements leaving it and whether the file is trimmed, deleted, or switched to on demand. Write `CODING_STANDARDS.md` once they approve.

### 9. Export from the project rule files

Run this after `CODING_STANDARDS.md` is written, so no standard is ever absent from both places. User-level files stay untouched.

For each project rule file that step 2 found:

- **Always-loaded file** (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `copilot-instructions.md`): remove the exported statements, keep everything else, and make the file carry exactly one pointer line: `CODING_STANDARDS.md` at the repo root, read when reviewing code.
- **Scoped rule file, short**: every statement in it fits a rule line in `CODING_STANDARDS.md` with nothing lost. Delete the file.
- **Scoped rule file, detailed**: it holds worked examples, procedures, or tables a rule line cannot carry. Keep the detail in the file, remove what the rule line now states, switch the file to on-demand activation by the mechanism HARNESS-RULE-FILES.md documents for its harness, and give the rule its `_Detail:_` pointer.
- A rule file that also holds non-standards content keeps that content and its current activation; only the standards leave.

Create no new harness rule file on your own. If step 2 found no always-loaded file, ask the user which to create and recommend `AGENTS.md`, the name most harnesses read.

Done when every always-loaded project rule file holds the pointer, every scoped project rule file that declared standards is deleted or on demand, and no standard is stated in two files.
