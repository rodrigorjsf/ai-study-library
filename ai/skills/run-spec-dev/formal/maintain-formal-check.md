# Maintain a formal check

A formal check proves a property of what it describes. When the source changes and the check does not, the check can keep passing while it describes text that no longer exists. That pass is the dangerous case, because it looks like a proof. This procedure is the upkeep loop for a check that [`create-formal-check.md`](create-formal-check.md) produced: a model under `ai/skills/run-spec-dev/formal/models/` with its `<Model>.matches` record. It handles the changes that skipped the check: merges, edits made without it, and drift that builds up across many commits.

Source: adapted from pstack's `maintain-formal-verification-skill` (`cursor/plugins` at `bf0c7cd80abdbf7fe47b634978a7d1b4071f71a7`, MIT licence, Lauren Tan). The licence text and the source are in [`NOTICE`](NOTICE).

Nothing in `ai/skills/run-spec-dev/` is installed, so no slash command starts this procedure. In Claude Code, read this file with the `Read` tool and run commands with `Bash`. In Cursor, name this file by path in the prompt and run commands in the agent terminal. The setup for TLC and Java is in `create-formal-check.md`.

## Outcomes

Give each check one outcome, and say which:

- **in sync**: no change since the recorded commit alters what the check describes, and the check passes.
- **updated**: the source changed, the model now describes the new source, and the check passes.
- **bug**: the model describes the current source, and the source breaks the property. This is a finding about the source. It is not drift.
- **blocked**: the check could not be brought back in line or could not run. Say exactly why.

A check can be both updated and bug: the update makes the model describe the source again, and then the property fails on it.

## Edit scope

Edit only the check: the model, its config, its `.matches` record, and any chart or report stored beside them. Never edit `ai/skills/run-spec/` during a run of this procedure unless the owner asks you to. When a property fails on the current source, do not weaken the property or the model to make it pass. Report the failure.

## Pass

1. **Find the checks.** Each model has a `<Model>.tla`, a `<Model>.cfg` and a `<Model>.matches` in `ai/skills/run-spec-dev/formal/models/`. Read each one you find, or the one the owner named. For each check, collect:
   - the property, from each invariant line of the record;
   - the covered files, which are the paths in the second field of those lines;
   - the bounds and assumptions, from the config;
   - the command that runs it, from `create-formal-check.md`;
   - the commit on the first line, `matches skill at commit <sha>`.

   If no model exists, stop and point at `create-formal-check.md`. If the record has no commit, use the last commit that changed the model's files (`git log -1 --format=%H -- <model files>`), and say that you did.

2. **Run it as it is.** Run each check once before you change anything, and record the result. A pass here does not tell you that the source is correct. It tells you that the old description still holds. A failure here can be drift or a bug. Do not decide which until step 5.

3. **Read every change to covered text.** Run `git log --format='%h %s' <sha>..HEAD -- <covered files>` and `git diff <sha> HEAD -- <covered files>`, and read each commit message. Also look for text that moved: a covered rule that is renamed, split, or moved to another file or section is still covered. Also look for new text that touches the state that a check guards, such as a new step that writes the same status. For each change, decide which of these it is:
   - **No effect.** The change does not alter anything the model describes, such as wording, formatting, or sections that the model does not cover. Check this against the model, not against the commit message.
   - **The model no longer describes the source.** A step that was one indivisible action is now two, a branch was added or removed, a guard moved, a new path reaches the guarded state, or a counter has a different cap. The model must change.
   - **The promise changed on purpose.** The change alters what the skill promises, and evidence in the change says that this is intended: the text itself, the tests, the commit message, or the ticket. The invariant must change, and you must cite that evidence.
   - **The promise may be broken.** The text changed, and no evidence says that the promise changed. Treat a failure that follows as a bug candidate.

4. **Update from the source, not from the result.** Change the model so that each changed part again points to text that a reviewer can open, and keep one indivisible step in the source as one step in the model. Write the update from the source before you rerun, and do not shape it by what makes the check pass. Change an invariant only for a promise that changed on purpose. Write down the old wording, the new wording, and the evidence. Keep the bounds unless the change makes them wrong. If you must reduce a bound, say so in the report.

5. **Rerun and judge each result.**
   - **Pass:** the check can now pass on a description that has lost the ability to fail. Break the new model the way each changed invariant guards against, using its `<how to break it>` field or a new break for new text, and confirm that TLC reports `Invariant <Name> is violated`. Then drop the break.
   - **Fail:** replay the counterexample against the source, step by step, in the skill's own words. If a step cannot happen under the skill's text, the model is wrong. Fix the model, and say what was wrong. If every step can happen, it is a bug. Name the commit that introduced it, tell the counterexample as a sequence of steps in the source's words, and state the harm in one sentence. If a cheap test or reproduction against the real code shows the bug, add it to the report as evidence. Do not commit it to the product.

6. **Regenerate the charts.** When the model's folder holds a chart and a report that the `statechart` command made (`chart.mmd` and its report), run that command again on the updated model with the same `--config`, the same `--view` and a new `--out` folder, then replace the stored files with the new ones. Never edit a stored chart by hand. Read [`statechart/SKILL.md`](statechart/SKILL.md) for the command and its rules: each rule that breaks is marked on the chart. If a changed step or state no longer fits the view's labels, update the view file in the same change. A chart that was not regenerated after the model changed is stale, so say so in the report.

7. **Update the record.** Update the invariant lines of `<Model>.matches`: the `path:line` of each invariant at the commit you checked, and its `<how to break it>` field. Set the first line to `matches skill at commit <sha>` with the full sha of the commit that you checked. Do not move the commit for a blocked check, and say so in the report. Then follow `create-formal-check.md` once as the next agent would, so that you know its steps still run.

## Report

Tell the owner, for each check:

- the outcome, and the commits that you read;
- what changed in the model and why, with a short reason for each change: the source changed shape, or the promise changed on purpose (with the evidence);
- the rerun result, and the break that you used to show the updated check can still fail;
- the charts you regenerated, or the reason a chart stayed stale;
- each bug, in plain words: the counterexample as steps in the source's words, the harm, and the commit that introduced it;
- what the check still does not cover, including new text that it should cover and does not.

Say outright which failures were drift in the model and which were bugs in the source. For a check that passed before you updated it and fails after, say that the old pass was on a stale description.

Put the check updates in a change of their own, separate from any product fix.
