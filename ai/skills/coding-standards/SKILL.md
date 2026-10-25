---
name: coding-standards
description: Generate or update CODING_STANDARDS.md at the repo root from the conventions the codebase actually follows, researched against current best practice and security for its language and ecosystem, with deterministic checks for every mechanical rule.
disable-model-invocation: true
---

# Coding Standards

`CODING_STANDARDS.md` is the **reviewer's** file: it is read when a diff is reviewed, by a human or by an agent in any harness. It holds the **judgement** calls this codebase has settled on, one heading per domain. It is the one home for the repository's coding standards: standards declared in project rule files are **exported** into it, and those files keep only a pointer.

Four rules decide what goes in:

- **Evidence.** Every rule is backed by what the codebase does today: a count of sites that follow it and an exemplar `path:line` that shows it. A practice the code does not follow yet (from the user, the literature or the web research) is a **proposal**, kept out of the file until the user accepts it.
- **Mechanical or judgement.** A **mechanical** rule is a fixed pattern a tool can check (an import shape, a banned API, a naming regex, a file location). A **judgement** rule needs a reader ("matches the surrounding style", "the seam sits at the module interface"). This file owns judgement. A mechanical rule belongs to tooling, and sits in this file only while no check enforces it yet.
- **Single source of truth.** A rule lives in one place. What a linter, formatter, test or CI job already enforces stays in its config, named by a pointer. A coding standard declared in a **project** rule file (`AGENTS.md`, `CLAUDE.md`, a rules directory) is exported here and removed from where it was. A **user-level** rule lives outside the repository, so it stays there and gets a **pointer**: its path and a one-line description.
- **The repo's language.** Write the file in the language the repo's rule files set for durable documents (a `CLAUDE.md` that says docs are pt-BR means a pt-BR file); English where they set none. Identifiers, paths, flags and quoted code stay verbatim.

The work is large: where the harness supports sub-agents (and a workflow tool, when the user opted into one), fan the surveys, the research and the drafting out to them, give each a JSON schema for its answer, and keep the classification, the questions and the gate in the main thread.

## Steps

### 1. Pick the branch

Look for `CODING_STANDARDS.md` at the repo root.

- Present: this is the **update** branch. Read [UPDATE.md](UPDATE.md) now; it adds work to steps 6, 8 and 9.
- Absent: this is the **create** branch.

### 2. Collect what is already written

Read [HARNESS-RULE-FILES.md](HARNESS-RULE-FILES.md) and check every location it lists, in the repository and at user level. For each rule file found, record its path, its level (project or user), its activation (always loaded, glob-scoped, on demand, manual), and which of its statements are coding standards as opposed to commands, workflow, or navigation. Also read `CONTRIBUTING.md`, the domain glossary (`GLOSSARY.md`, `CONTEXT.md`), ADRs, and any style doc under `docs/`.

Then list the **enforced set**: every linter, formatter, type-checker, static-analysis, pre-commit hook, CI config, and every repo-level test that asserts something about the code or the config (an architecture or boundary test, a test that parses a Dockerfile), with what each one checks. A repo with no guardrail at all (no hook, no CI job running its check command) is a finding for the step 9 report.

Done when every repository and user-level location in HARNESS-RULE-FILES.md is recorded as present or absent, every rule file found has its path, level, activation, and its coding-standard statements marked, and every tooling config and repo-level check is in the enforced set.

### 3. Map the domains and the ecosystem

Read [DOMAINS.md](DOMAINS.md). Mark each domain in its catalog as present (with the paths that prove it) or absent. A language, framework, or layer the catalog does not name but the repo contains is a domain too: add it.

Then take the **ecosystem inventory** the research needs: the languages and their versions, the build and package tools, the frameworks and major libraries, the runtime and deployment targets (containers, hosts, serverless), and every **outside system** the code talks to or trusts (each API, database, message channel, model or agent runtime, identity provider, file the user uploads, backup target), read from the manifests, the config loader, the adapters and the deploy files.

Done when every catalog domain carries a verdict, every top-level source directory belongs to at least one present domain, and every outside system is listed with the paths that reach it.

### 4. Survey each present domain

Find the conventions the code follows. Dispatch one read-only sub-agent per present domain (group small domains so the fan-out stays reasonable), each given that domain's row from DOMAINS.md and the questions it must answer; otherwise survey in sequence.

Each survey returns candidate rules, and each candidate carries its **evidence**:

- the rule, stated as the behaviour to produce, and why a reviewer needs it
- the count: N of M sites follow it, and how it was counted
- two exemplars as `path:line`
- every counter-example found, as `path:line`
- whether it is mechanical, and which config or test already enforces it, if any
- what recent commits do, where old and new code disagree

Every coding-standard statement step 2 marked in a **project** rule file is a candidate too. It carries its source as `path:line` and is checked against the code like any other: a statement the code contradicts becomes a step 7 question. Weight recently changed code (walk `git log` for the domain's paths): where old and new code disagree, the recent pattern is the convention the team follows now. A survey also returns, per question of its domain row, "no convention found" when the code has no consistent answer.

Done when every present domain has returned a candidate list or an explicit "no convention found".

### 5. Research current practice and security

Read [RESEARCH.md](RESEARCH.md). Dispatch one research sub-agent per topic it defines (the language and its tooling; each framework or runtime that shapes the code; security, one topic per group of outside systems from step 3; the platform: supply chain, build, deploy, data at rest), then a **coverage critic** over the aspect list in RESEARCH.md, then one gap researcher per missing aspect. Each research agent reads primary sources and compares every practice it finds with this repo, returning a **proposal** with its sources, the repo's state (followed, partially, not, not applicable) with `path:line` evidence, a severity, and the concrete check when the practice is mechanical.

A proposal the repo already follows, with evidence, becomes a step 4 candidate. Every other proposal waits for the gate.

Done when every topic and every aspect in RESEARCH.md returned proposals or an explicit "not applicable to this repo", and any aspect left unresearched (a capped gap, a failed agent) is named for the report.

### 6. Classify every candidate

Give each candidate exactly one class:

| Class | Test | Destination |
|---|---|---|
| **enforced** | a config in the enforced set already checks it | dropped; the domain section names the config |
| **mechanical** | a tool could check it, none does | in the file, tagged `[check candidate]`, until the check exists; listed for the user as a proposed check |
| **judgement** | only a reader can apply it | in the file |
| **split** | the code disagrees with itself and no pattern clearly leads | a question for the user |
| **user-level** | only a user-level rule file states it | not copied; the domain section points at the rule file |

Then prune **no-ops**: a candidate that any competent reviewer of this language already applies by default says nothing. Delete it. Drop a candidate whose counter-examples outweigh its count unless the recent code follows it (**weak evidence**), and keep each meaning once: a rule two surveys found lives in the domain where a reviewer would look for it.

Done when every candidate carries one class, the no-op, weak-evidence and duplicate passes have run, and the counts of each class are noted for the report.

### 7. Settle the splits

Put every **split**, and every contradiction between a written rule and the code, to the user in one numbered round. Give each question the evidence on both sides (counts and `path:line`) and your recommended answer, worded so "yes" accepts it, so "yes to all" is a valid reply. Wait for the answers. An answer that settles a split becomes a rule; one that asks for a check becomes a proposed check.

Done when no candidate is still classed split.

### 8. Draft

Write the draft **outside the repository** (a scratch directory) until the gate, in this shape, translated to the repo's language:

```markdown
# Coding Standards

Read at review time. Rules a tool enforces live in that tool's config and are not repeated here. A rule in a domain section overrides the Baseline.

## <Domain>

Enforced by tooling: `<config or test path>` (<what it guarantees>).

- **<Rule name>.** <The rule, stated as the behaviour to produce.> _Why:_ <the reason a reviewer needs to apply it to a new case.> _See:_ `path/to/exemplar.ext:42`.
- **<Rule name>.** <The rule.> _Why:_ <reason.> _Detail:_ `.cursor/rules/<name>.mdc`, read when <the condition that calls for the detail>.

### User-level rules

- `~/.claude/rules/<name>.md` (outside this repo): <one line on what it governs>.

## Baseline
```

- One `##` heading per present domain, named as the team names it (`Java`, `Spring`, `Testing`, `Architecture`, `Security`, `Code documentation`). Order them from most to least touched.
- State each rule as the target behaviour. A prohibition appears only as a hard guardrail, paired with what to do instead.
- Use the glossary's terms for domain concepts.
- A rule exported from a project rule file keeps its author's wording where that wording already states the behaviour.
- **Open every exemplar you cite** and make sure that line shows the rule: a survey often points at a bare `/**` opener or a declaration header. Replace one that does not.
- `_Detail:_` appears only on a rule whose source rule file is kept in step 10. State the condition for reading it, so a model opens the detail only when it needs that guidance.
- Under `### User-level rules`, list every user-level rule file that governs the domain as a pointer: path and one-line description. Omit the heading when it would be empty. These files exist only on machines that have them, so tell the user which of them the team appears to depend on.
- Counts stay in your report to the user; the file keeps the exemplar, which the codebase keeps true.
- Fill `## Baseline` from [BASELINE.md](BASELINE.md), dropping every baseline item a domain rule overrides or the enforced set already checks.
- Past roughly 1,000 lines, move the longest domain sections to `docs/standards/<domain>.md` and leave one pointer line per section stating when to read it.

Done when every surviving candidate appears exactly once, every rule has a name, a why, and an exemplar opened and shown to resolve, every coding-standard statement from a project rule file is in the draft or was dropped by a named class, and every user-level rule file is pointed at from at least one section.

### 9. Gate

Show the user, in one message:

- the draft (its path, its sections, the class counts from step 6);
- the **proposed checks**: every `[check candidate]`, with a recommended first batch of the cheap, deterministic ones (see [CHECKS.md](CHECKS.md));
- the **research proposals** the repo does not follow yet, grouped by severity, each one line with what it closes and its rough cost, and any aspect left unresearched; a confirmed defect found along the way (a secret missing from a log redaction list, an authorisation gap) is flagged as a bug to fix now;
- the step 10 change list: for every project rule file, the statements leaving it and whether the file is trimmed, deleted, or switched to on demand.

Ask which checks to implement now and what to do with each proposal (adopt as a rule, open issues, leave out). Write `CODING_STANDARDS.md` once the user approves the draft.

Done when the user has answered for the draft, the checks and the proposals.

### 10. Export from the project rule files

Run this after `CODING_STANDARDS.md` is written, so no standard is ever absent from both places. User-level files stay untouched.

For each project rule file that step 2 found:

- **Always-loaded file** (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `copilot-instructions.md`): remove the exported statements, keep everything else, and make the file carry exactly one pointer line: `CODING_STANDARDS.md` at the repo root, read when reviewing code.
- **Scoped rule file, short**: every statement in it fits a rule line in `CODING_STANDARDS.md` with nothing lost. Delete the file.
- **Scoped rule file, detailed**: it holds worked examples, procedures, or tables a rule line cannot carry. Keep the detail in the file, remove what the rule line now states, switch the file to on-demand activation by the mechanism HARNESS-RULE-FILES.md documents for its harness, and give the rule its `_Detail:_` pointer.
- A rule file that also holds non-standards content keeps that content and its current activation; only the standards leave.

Create no new harness rule file on your own. If step 2 found no always-loaded file, ask the user which to create and recommend `AGENTS.md`, the name most harnesses read.

Done when every always-loaded project rule file holds the pointer, every scoped project rule file that declared standards is deleted or on demand, and no standard is stated in two files.

### 11. Build the accepted checks

Read [CHECKS.md](CHECKS.md). For each check the user accepted: write first a test that runs the real tool on an offender and on a legitimate case, see it fail, then add the rule to the repo's own linter or a repo-level test, and fix any existing violation the check reveals (or scope it, if the user agreed). Add the exemplar check from CHECKS.md, so a cited `path:line` that stops existing fails the build. Then move every rule a new check now enforces out of the file: drop its bullet (or keep only its judgement part) and name the check in the section's "Enforced by tooling" line.

Follow the repo's own process for code changes (its TDD or review rules in the always-loaded file, its hooks and its check command) and run the full check command before calling this done.

Done when every accepted check fires on its offender and stays silent on the legitimate case, the full check command passes, and no bullet in the file restates what a check enforces.

### 12. Hand off the proposals

For each proposal the user adopted as work, open issues in the repo's tracker the way it writes them (a spec with one ticket per proposal when they belong together; a how-to issue for a step only the user can do, such as a console setting). Each issue carries the threat or gain in one sentence, the evidence at a pinned commit, the decision taken, and acceptance criteria a test can check. Write no real personal data into them.

Done when every adopted proposal has an issue, and the report lists the issue numbers, the checks built, the class counts, the aspects left unresearched, and every defect fixed along the way.
