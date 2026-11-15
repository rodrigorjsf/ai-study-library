# Queue, merge and owner notes

Read this file when `$ARGUMENTS` names more than one spec, carries `--merge`, or carries free-text notes. It extends steps 1 and 7. Everything else in the dispatcher contract still holds.

## Parse the arguments (step 1)

- **QUEUE**: the spec tokens at the start of `$ARGUMENTS`, in order, up to the first word that is not a spec token. A spec token is a form step 1 accepts: `#N`, `N`, `.scratch/<slug>`, its `spec.md`, or a `ticket-implementer` handoff path. A `#N` after the first non-spec word is part of the notes, never a spec.
- **OWNER_NOTES**: the rest of `$ARGUMENTS`, verbatim, with `--merge` removed.
- **MERGE**: true when `--merge` appears, or when OWNER_NOTES explicitly asks for the PRs to be merged ("merge the PRs", "faça o merge dos PRs"). Anything less explicit leaves it false.

`$GITDIR/run-spec/queue.md` records the queue: a `MERGE: true|false` line, an `OWNER_NOTES:` line, then one line per spec in QUEUE order, `<spec> pending`, `<spec> held <PR URL> <WORK>` or `<spec> done <PR URL> <WORK>`.
- When the file exists and its spec lines name the same specs in the same order, this run resumes that queue: skip every spec it marks `done`, and keep those lines as they are. When the current branch is the WORK of a `done` line, run `git switch DEFAULT` first.
- Otherwise write it anew, every spec `pending`.

Then run steps 2–7 for the first spec not marked `done`. Each spec gets its own SPEC, slug, STATE and WORK. After each spec's step 7, rewrite its line: `done <PR URL> <WORK>` when its PR merged or MERGE is false, `held <PR URL> <WORK>` when its merge was held, so a later run retries it.

## Merge a spec's PR (step 7, MERGE true)

A merge is **held** when any gate below fails. A held merge leaves the PR open, adds `merge held: <reason>` to the report, and stops the queue, because a later spec may build on this one. The rest of QUEUE goes into the report as `not started`.

1. **Run gate.** The run has no halt reason (a RED halt, `agent <label> lost`, or `paused by owner`), no skipped tickets, and no stuck ids. The newest Acceptance (step 7) exists and holds no FAIL or UNVERIFIED line, and the last `review-<N>-fix.md`, when one exists, does not read `STATUS: RED`. Otherwise hold: a spec merges only when every criterion passed on a green branch.
2. **CI gate.** Run this from MAIN with `run_in_background`, then end the turn: its completion notification carries the exit code and the output. A `no checks reported` answer right after the PR opens can mean the checks have not registered yet, so the command retries it every 30 s for up to 2 minutes when `.github/workflows/` exists:
   ```
   timeout 1800 bash -c 'for try in 1 2 3 4 5; do out=$(gh pr checks <n> --watch --interval 30 2>&1); code=$?; case $out in *"no checks reported"*) if [ -d .github/workflows ] && [ $try -lt 5 ]; then sleep 30; continue; fi; echo "no checks"; exit 0;; esac; printf "%s\n" "$out" | tail -n 5; exit $code; done'
   ```
   Exit 0 passes. Any other exit holds the merge: a failed check, or 124 for the 30-minute timeout. A final `no checks` passes.
3. **Merge.** `gh pr merge <n> --merge`. If it fails (branch protection, a conflict, a required review), hold the merge with gh's one-line error. On success, run `git switch DEFAULT`, `git pull --ff-only`, `git branch -d WORK`, and `git push origin --delete WORK`.
4. Print one line: `spec <SPEC>: PR #<n> merged`.

The merge closes the tickets through their `Closes #N` lines. The spec issue stays open for the owner to close.

## Next spec in the queue

After the report for one spec, take the next spec of QUEUE that `queue.md` does not mark `done`. If MERGE was false, first run `git switch DEFAULT`, so the next spec branches from DEFAULT and not from the last spec's WORK. Then go back to step 1's SPEC rules and run steps 2–7 for it. A ticket blocked by an earlier spec's ticket that is still open (its PR was not merged) waits in the oracle as blocked, and the report lists it as stuck.

## After the queue

Once every spec in QUEUE has been reported, print one line listing each spec with its PR and merge outcome.

If OWNER_NOTES ask for a skill or command to run after the queue (for example `/gauntlet-loop-claude-code`), invoke it with the Skill tool and pass OWNER_NOTES verbatim as its arguments. The dispatcher contract ends when that skill starts, and its own instructions take over. Without such a request, later turns fall under the contract's "After the report" rule.
