# Create a formal check

A test checks the cases that someone thought to write. A formal check covers every case in a stated scope: every order of steps in a model, every input up to a bound, or every input. This procedure finds the part of the system where that matters most, checks one property of it, and leaves a check that the next agent can rerun after a change. Write for an agent who reads it cold, mid-change, and has never seen your work. The owner must be able to trust the result and act on it without learning the checking language.

Source: adapted from pstack's `create-formal-verification-skill` (`cursor/plugins` at `bf0c7cd80abdbf7fe47b634978a7d1b4071f71a7`, MIT licence, Lauren Tan). The licence text and the source are in [`NOTICE`](NOTICE). To bring a check back in line after the code changes, follow [`maintain-formal-check.md`](maintain-formal-check.md).

## Where it runs

Nothing in `ai/skills/run-spec-dev/` is installed, so no slash command starts this procedure. Open it by path.

- **Claude Code:** read this file with the `Read` tool and run every command with `Bash`.
- **Cursor:** name this file by path in the prompt and run every command in the agent terminal.

Both harnesses run the same commands from the repository root, with Node and `mise` on the machine.

## Choose the target from the code

Answer from the codebase, and ask the owner only what you cannot observe. If the owner named an area or a bug, start there.

A good target is a promise the code makes, where a break harms users and tests rarely reach the case that breaks it. Choose the strongest such target in the repository, not the one that is easiest to check.

## Let the question choose the tool

Pick the tool that answers the question at the lowest cost: a model checker, a proof assistant, an SMT-backed verifier, or another tool. Whether events can happen in a bad order usually suits a model checker over a small model of the design, and TLA+ is the default for that in any language. Whether the code itself behaves for every input, as with memory safety, overflow, or a data-structure invariant, usually suits a verifier that runs on the code. If no verifier runs on this language, say so, and test the real code with generated inputs, not a hand model of the function. A property that must hold at every size, where a bound is not enough, can need a proof. Prefer a tool that the repository's developers can install and run, and tell the owner why you chose it.

## What makes it good

- **True to the source.** Every part of the model points to text or code that a reviewer can open: a line of `ai/skills/run-spec/SKILL.md`, or a function. What the model treats as one indivisible step is one indivisible step there. Names come from this repository.
- **Able to fail.** A check that you have never seen fail proves nothing. Show each invariant failing on a broken variant of the model, such as a removed guard or a reordered step.
- **Findings stay findings.** When the current text or code breaks a property, report it with the counterexample in the source's own words. Do not weaken the property or the model until it passes, and do not change the product unless the owner asks.
- **Honest about scope.** Say what is checked, under which bounds and assumptions, and what is left out. A pass covers the model or the bound, not the whole system.
- **Readable without the tool.** State each property and its harm in one plain sentence each. Tell a counterexample as a short sequence of steps in the source's words, not in TLA+ action names.
- **Cheap to rerun.** One command, a pinned tool version, and a run short enough that the next agent will use it on every relevant change.
- **Kept in step with the source.** Record which text each invariant restates, and the commit at which you last confirmed that the model describes it. When the covered text changes after that commit, the next agent can see that the check needs another look.

## Set up TLC and Java

The check runs on Node 22.18 or later (`node --version`), `mise`, and a network connection on the first run.

The `statechart` command installs Java and TLC through `mise` the first time it cannot find them. To fetch them ahead of time, run this once from any directory:

```sh
mise install java@temurin-25 'http:tla2tools[url=https://github.com/tlaplus/tlaplus/releases/download/v1.7.4/tla2tools.jar,checksum=sha256:936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88]@1.7.4'
```

The command pins TLC 1.7.4 by checksum, the same pin that `statechart/scripts/run.ts` carries. Check that `mise` provides a Java with `mise exec -- java -version`. To use a TLC and a Java you already have, set `TLA2TOOLS` to the path of `tla2tools.jar` and `JAVA` to a Java 11 or later binary, and `statechart` skips `mise`.

## Write the check

Put the check under `ai/skills/run-spec-dev/formal/models/`, three files for each model:

- `<Model>.tla`, the model. Write each rule that the owner agrees to as an `INVARIANT`, and write `Next` as a disjunction of named actions that use the source's own nouns. Read the `statechart` skill for the rest of the spec rules before you write it.
- `<Model>.cfg`, the TLC config, with small constants so that the state space stays small.
- `<Model>.matches`, the record that ties the model to its source, in this form with tabs between the fields:

```
matches skill at commit <full sha>
<Invariant>	<path>:<line>	<how to break it>
```

The first line names the commit at which you confirmed that the model describes the source. The `<sha>` is the checked-out commit that holds the covered text, with no uncommitted change to it. Each later line holds one invariant, the `path:line` of the text it restates at that commit, and the one-line change that makes it fail. The paths in the second field are the covered files. Restate each invariant from the text at that commit, never from memory and never from an issue's illustrative list.

## Read every result with `statechart`

Read [`statechart/SKILL.md`](statechart/SKILL.md) and run its command on the model:

```sh
ai/skills/run-spec-dev/formal/statechart/scripts/statechart <Model>.tla --config <Model>.cfg --out <dir>
```

It shows each invariant violation as its shortest path in plain words. When the check passes, it draws a chart of how the system moves between states. Work in a scratch folder outside the repository for the output, and copy into the repository only the files the ticket asks for. The skill owns its options and its rules for views and labels, so follow its text and copy none of it into the model's files.

## Prove it before you hand off

For each invariant, copy the model into the scratch folder, make the change that the invariant guards against (the `<how to break it>` field), and run the command. TLC must report `Invariant <Name> is violated`. Keep that output with the change that produced it. Then run the real model and confirm that it passes, or fails only on the findings you will report.

A check that was never run on a break is a draft. If the model misses a break or a step does not run, fix the model, not the break.

## Hand off

Tell the owner what you checked, which tool you used and why, the bounds, what the check found in plain words, how to run it, and what it does not cover. Give one counterexample as steps in the source's own words. Suggest a second target only if you found a close one. Point the next agent at `maintain-formal-check.md` for bringing the model back in line after changes that did not recheck it.
