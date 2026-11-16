---
name: run-spec-correct
description: "Turn the review findings that keep recurring across /run-spec runs into checks that make the mistake impossible. Reads the Findings buffer, lists only the mistake classes seen at least twice with their evidence and the highest fix level that works, and files follow-up issues only for the classes the owner selects. Use for /run-spec-correct."
disable-model-invocation: true
---

# Run-spec correct

The same review findings come back run after run, and each one is fixed or dismissed alone. Change the repository so the next agent cannot make them.

Assume every contributor is an agent that sees only the files it opened, copies the nearest example, and takes the shortest path that compiles. Design the repository so a change that looks right from one file is right for the whole repository.

Source: adapted from `/correct` of pstack (`cursor/plugins` at `bf0c7cd80abdbf7fe47b634978a7d1b4071f71a7`, MIT licence, Lauren Tan). Its mistakes come from the Findings buffer, not from chat corrections.

You report first. You file an issue only for a class the owner selects, and you change no code.

## 1. Read the buffer

The **Findings buffer** is the file `run-spec/findings.tsv` under the git common directory of the current repository:

```
BUFFER="$(cd "$(git rev-parse --git-common-dir)" && pwd)/run-spec/findings.tsv"
```

When the command fails because the directory is not a git repository, say so and stop.

When `$BUFFER` is missing or holds no line, print `The Findings buffer is empty: no findings recorded at <BUFFER>.`, then stop. File nothing and write nothing.

Each line holds tab-separated `key=value` fields in this order: `slug` (the run), `head` (the run's last commit), `round` (`<N>`, or `user-<k>` for a change the owner asked for after the report), `axis` (`acceptance`, `standards`, `security`, `uxaix`, `design`, `hygiene` or `user`), `location` (`file:line`, or `-`), `finding` (the finding as the reviewer wrote it) and `outcome` (`fixed`, `dismissed`, `follow-up`, `needs-human` or `unproven`). Skip a line that lacks one of the seven, and say how many you skipped.

## 2. Group the lines into mistake classes

A **mistake class** is a set of findings that one rule or one check could have prevented, whatever the file, the run or the wording. Group by cause, not by words: an `import` inside a function in two files is one class, and two findings in one file about different rules are two.

One buffer line is one occurrence. A line with outcome `dismissed` or `unproven` counts for nothing: the fixer found no defect, or could not reproduce one, so there is no mistake to prevent. A class counts once it has happened twice. List only those. Never name a finding that belongs to no such class.

When no class has two occurrences, print `No mistake class has two occurrences in <BUFFER> (<n> lines read).`, then stop. File nothing and ask nothing.

## 3. Pick the fix level of each class

Fix each class at the highest level that works. The levels, highest first:

1. **Architecture.** Eliminate the mistake. Give each piece of state one owner and each task one supported way. Hide internals so the wrong import fails. Replace hand-synced lists with one source of truth. Delete the old ways and the dead code an agent would copy.
2. **Types.** Enforce it with types so the bad state cannot be written.
3. **Lint.** When the bad code still compiles, add a lint or CI check whose error names the file, type or function to use instead. When the pattern is already common, fail only when a change adds more.
4. **Test.** Test the behavior. Fix or delete a test that still passes when the behavior it checks breaks, or that fails when only the internals change.
5. **Docs.** Write docs or agent rules last, only for a judgment call. Nothing fails when an agent skips them.

Name one level per class. For each level above it, give one reason it does not work in this repository. Ground each reason in what you read: the files at `location` as they are on the current HEAD (say when one is gone), and the repository's own tooling (language, type checker, linter, test runner, CI). A level you cannot rule out is the level you pick. Docs is the pick only when every higher level has a reason.

## 4. Report

Print one block per class, numbered from 1, most occurrences first, then stop and ask. Nothing is filed before the owner replies.

```
### Class <n>: <the mistake, as a claim> (<count> occurrences)
Evidence:
- <slug> round <round> <axis> <location> <outcome>: <finding, unchanged>
Level: <Architecture | Types | Lint | Test | Docs>: <the change, naming the file, type or function>
Why not higher:
- <level>: <reason>
```

After the blocks, print `Left out: <k> lines that belong to no class listed above.`, a count that names no finding, then `Which classes should become issues? Reply with class numbers, such as 1 3, or all, or none.`

## 5. File the selected classes

The owner's reply is their request for an issue, so the gate of `follow-up-issue` is met. Reply `none`, or a number the report did not list, files nothing for it. File one issue per selected class, through the `follow-up-issue` skill, with this content:

- **Title.** The mistake as a defect claim in the present tense, for example "Agents leave comments in code and nothing fails when they do".
- **Context.** First line `Filed by run-spec-correct.`, then the buffer path.
- **Finding.** The class's evidence lines, each with its `head`.
- **Reason and Options.** The level and the reasons from the report, the chosen level first.
- **Acceptance criteria.**
  - `- [ ] The new check fails on the recorded past mistake: <how to reproduce it>, and passes with the fix in place.`
  - `- [ ] One command runs the check locally and wherever the repository checks changes. An exception sits on the offending line with a reason, an expiry date and a human's approval.`

The recorded past mistake is the code the finding describes. A `fixed` line's `head` already holds the fix, so name the earlier code: the file at `location` in the commit before the fix, found with `git log -S'<text>' -- <file>`. When that commit is gone, write the smallest snippet the finding describes. A criterion nobody can re-run is no criterion. Reproduce the mistake on a copy in a temporary directory: never edit a file of the repository for it.

Print one line per issue with its link or path, then stop. Never edit the buffer, change code, or run the new check yourself.
