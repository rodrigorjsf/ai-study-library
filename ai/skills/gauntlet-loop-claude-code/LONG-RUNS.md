# When the run outlives the session

Open this when a usage limit, a compaction or a new session interrupted the run (*Resuming*), when
the context or the day is about to end (*Pausing*), and when you write `$HANDOFF/HANDOFF.md` or the
prompt of a scheduled resume.

## Resuming

**Verify from disk before trusting any summary.** A compaction summary can be wrong: one reported
"no files modified" while revisers cut off mid-edit had left changes in the tree. Read the handoff,
then run `git status`, `git diff --stat`, `git log --oneline -1` (against the HEAD the handoff
records), `trend.py rows $HANDOFF` and the gate commands. Act on the newest decision on disk:

```
a workflow still running, or waiting at a usage limit -> wait for its task notification
a pass or a stop recorded             -> When the loop ends (main page)
a choice pending with the user        -> put it to the user again
a wave recorded, not closed           -> finish it from the stage its record names: unfinished
                                         groups, then the boundary check, the review and the
                                         close (FIX-WAVES.md §2, §3, §6)
a wave closed, next round not open    -> open the next round
a round open, verdicts or pick        -> relaunch it and grade the work as it stands, without
  answers missing                        revising it first (main page, Reading a round)
the latest round complete and         -> step 9 of Starting a loop (bounds and trend tests first)
  failing, no wave since it
nothing recorded                      -> start from the beginning
```

When the disk fits no row (HEAD differs from the handoff, edits no wave record explains), ask the
user.

Relaunching a round:

- **With `resumeFromRunId`** (`Workflow({ scriptPath, resumeFromRunId })`) only in the session that
  launched the run, or one reopened with `claude --resume`, and only when every missing file belongs
  to an agent that never completed. Completed agents return their saved results, agents that were
  still running start over, and after a failed agent, it and every agent the script starts after it
  run again.
- **Without it** in every other case: a fresh session, a verdict deleted as `INVALID`, or one a
  critic returned without writing (that critic completed, so a cached replay returns the old
  result and writes nothing). A critic whose
  verdict is on disk returns it at the cost of one check. A fresh session also needs the opt-in
  again (main page, *Run it under ultracode*).

A `$HANDOFF` whose verdicts are named `v<N>-<key>.json` and that has no `trend/rounds.json` is an
older loop: `trend.py rows` and `raw` read it, the other commands refuse it. Continue it in a new
`$HANDOFF` whose handoff cites the old one.

## Pausing

Pause when the context passes ~80%, the user names an end time, or the day ends with the loop
unfinished. A pause can be seen coming, so it waits for a boundary:

1. **Reach a boundary.** A round: its verdicts written (`trend.py check` exits 0); a round that will
   not finish in time can be stopped with `TaskStop` on its **task id** (not the `wf_…` run id),
   since its critics restart on relaunch, and then `trend.py check` lists the files to delete. A
   wave: every reviser finished and its checks are green, or the wave closed; the wave record names
   the stage. Revisers are never stopped mid-edit on purpose, because a stopped reviser leaves a
   half-applied change.
2. Commit and push the working tree, whatever its grade.
3. Update the handoff per *The handoff* below, and point the project memory at it.
4. When the user names a resume time, schedule a one-shot `CronCreate` (`recurring: false`) whose
   prompt is *The resume recipe* below. The job lives only in this session and fires only while it
   is open and idle; after the session ends, the handoff is the way back.

## The handoff

`$HANDOFF/HANDOFF.md`, written for someone with **no memory of this run** and kept current at every
milestone: a decision written nowhere else (a verdict, a grade, a design the user chose) exists only
in the run until something writes it out. It enters no worker's prompt.

| Section | Because |
|---|---|
| The original request, word for word | the last check reads it again; chat does not survive the session |
| The opt-in line (main page, *Starting a loop* step 2) | the evidence a compacted session needs before calling `Workflow` |
| The bounds: the round bound and the token budget the user agreed to | every stop choice quotes what is left |
| Where the work stands, piece by piece, with its current grade, and the HEAD it was left at | otherwise the next session re-judges it, and cannot tell a stray edit from the recorded state |
| The current wave, from FIX-WAVES.md §2: its base SHA, its groups with their files and findings, the stage reached (revisers, review cycle, closed) and, once closed, its end SHA | a session that resumes mid-wave finishes it instead of re-splitting it blind; the base SHA also decides Self-caused |
| A choice pending with the user, if any | a resume puts it to the user instead of guessing |
| The exact resume command, with absolute paths, script path and run id | a resume on a wrong path fails quietly |
| NEXT STEPS, numbered | an unwritten list is a list nobody has |
| Every user decision, word for word (those about the bar, the exit or the scope also go in the brief) | the brief carries the ones critics need; the rest, about cost and continuing, stay here |
| The trend table | the coordinator decides on it; a worker that sees it learns the round count |
| **The conclusions that cost real work** | measurements, rejected approaches, a check that was fixed and must not be reverted: the section left out most |

Point the project memory at the handoff so a fresh start finds it without being told.

## The resume recipe

The prompt of a scheduled resume (*Pausing* step 4) and the first message of a new session carry
three parts:

1. **Where:** the handoff path, the repository path, the branch and the HEAD it was left at.
2. **What to run:** *Resuming* in `gauntlet-loop-claude-code`'s LONG-RUNS.md, with the exact
   relaunch command from the handoff.
3. **The run's rules:** those of *Durable state and who owns it* on the skill's main page.
