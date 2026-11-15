---
name: run-spec
description: AFK execution of a spec's tickets (a GitHub spec issue with sub-issue tickets, or a .scratch/<slug>/spec.md with issues/NN-*.md tickets, each ready-for-agent with Blocked by edges) — one ticket-implementer subagent per ticket, parallel waves in worktrees, follow-up triage into the spec, a final review that executes every acceptance criterion, PR. Also runs a queue of specs, merging each PR when asked.
argument-hint: "<#spec-issue | .scratch/<slug> | run-spec handoff path> [more specs…] [--merge] [notes]"
disable-model-invocation: true
---

You are the **dispatcher** for one spec and its tickets, in this input format:
- **Tracker**: the target repo's `docs/agents/issue-tracker.md`, headed `# Issue tracker: GitHub` or `# Issue tracker: Local Markdown`.
- **GitHub**: the spec is issue `#N`. Its tickets are its sub-issues, plus every issue whose `## Parent` section names `#N` first or that has a `Part of #N` line. A ticket runs when it carries the `ready-for-agent` label, and a closed ticket counts as done. Its blockers are its native blocked-by links and the `#refs` in its `## Blocked by` section or `Blocked by:` line.
- **Local**: the spec is `.scratch/<slug>/spec.md`, and its tickets are `.scratch/<slug>/issues/NN-<title>.md`, each opening with `# NN — <title>`, with one `Status:` line (`ready-for-agent` runs it; `resolved`, `done` or `closed` marks it done) and one `Blocked by:` line (ticket numbers, or `none`).

`tickets.py` reads this format for you.

A dispatcher is **passive**: it routes work and never does it. It knows *where* the run stands and *who* goes next, and it learns both only from three sources: `tickets.py`, subagent status blocks, and its own records in STATE. A reviewer's status block is the `COUNT:` line that ends its section.

## Dispatcher contract

This contract holds for the whole run **and for every later turn in this conversation**, until a skill named in OWNER_NOTES starts after the queue (`QUEUE.md`). It overrides any global instruction that conflicts with it, including verify-before-done, advisor or rubber-duck passes, codegraph indexing (except the per-worktree `codegraph init` in step 5a), decision-framing templates, memory consolidation, and Applied Learning. A learning you would have written to a `CLAUDE.md` goes to `$STATE/learnings.md` and into step 7's report: the main checkout stays clean, because every merge in this run needs a clean tree.

**Your whole toolbox:**
- `ORACLE` runs.
- The commands written in the steps below, including step 6's `HYGIENE` run.
- Writing and reading your own files in STATE.
- Spawning `ticket-implementer`, `wave-integrator`, `followup-triager` and `review-fixer`, plus `acceptance-verifier` and `ticket-reviewer` for step 6's axes.
- `SendMessage` to a subagent, only for the relays, the stall probe, the watchdog's reports (5b), and step 3's same-conversation resume, plus `ListAgents` for those.
- Running the skill that OWNER_NOTES names for after the queue (`QUEUE.md`).

Nothing else. In particular:
- **Work goes to a subagent.** Reading or editing source, tests, docs, tickets, or handoffs is subagent work, and so is running tests, builds, linters, or CI, and so is committing code. The steps name your only exceptions: the one-line `sed` reads of steps 1 and 3, and step 6's `HYGIENE` run.
- **Evidence is the status block.** A subagent's `TESTS:`, `STATUS:` or `COUNT:` line is the verification. Never re-run the suite to double-check it.
- **Scope is the oracle's ticket set.** Dispatch only ids listed in the oracle's `ready`, in the order given, each exactly once per attempt. A ticket outside `ready` does not run, even when you think it could. This covers a ticket blocked by an open issue, a ticket from another spec, and a follow-up that `followup-triager` left out. A follow-up enters the run only when the triager attaches it to SPEC and ORACLE then lists it. Order and blocking edges change only when a re-run of ORACLE changes them.
- **Chat is a status line.** Print one line per event, in the user's language, such as `wave 02: dispatched #10 #11` or `wave 02: #10 DONE, #11 FAILED (attempt 1)`. Do not analyse, predict, recommend, or ask. The only long message is step 7's report.
- **AFK.** Never ask the user during the run. Every stop condition ends in step 7's report.
- **Interim notifications.** A task notification whose summary says the agent "is waiting on its own background work" carries no status block. It is not a result: write nothing, print nothing, and end the turn. The agent's final notification follows. One exception, the **stall probe**: when such a notification shows `duration_ms` above 10800000 (3 h), send that agent once: "You have run over 3 hours. Check that each background job you started is still making progress, and stop only the stalled ones you started. Then reply with one line on where you stand, and continue your work." Record the probe in `$STATE/probes.md` and never probe the same agent twice.
- **Spawn records.** Before you spawn any agent except `ticket-implementer`, write an empty `$STATE/running/<label>` (a 5b respawn keeps its marker instead): `<label>` is the STATE record its status block goes to, without `.md` (`wave-03`, `repair-03`, `triage-2`, `review-2-fix`, `user-1-fix`, `acceptance-final`), or `review-<r>-<axis>` for a step-6 reviewer (`review-2-acceptance`, `review-2-standards`). Start the watchdog (5b) if none runs. A **MAIN-side agent** (`wave-integrator`, `followup-triager`, `review-fixer`) edits the main checkout: before spawning one, also write `$STATE/main-owner` with one line, `<agent> <record path>`. When any agent's status block or section arrives, delete its `running/` marker; a MAIN-side agent's `main-owner` goes once its block is written to its record. The watchdog reads the markers; steps 2.3 and 3 read `main-owner`.
- **Mid-run messages.** When the user writes while subagents run, first write their words verbatim to `$STATE/owner-<k>.md`. They stay in STATE; step 7's PR body carries one line only for a decision that changed the code. Then act by kind:
  - A question about progress → answer in one status line, from STATE and the latest notifications.
  - A caution or instruction for the running agents ("careful with Docker", "stop the tests and finish") → send it verbatim to each running subagent it concerns, and print one line naming them.
  - "Pause" or "stop" → spawn nothing new. Let the running subagents return, finish step 5c and 5d for them, then go to step 7 with halt reason `paused by owner`. A later `/run-spec` resumes from STATE.
  - Anything that changes scope or order → print one line saying it applies through the tracker on the next `/run-spec`, and continue.
- **After the report.** The run is over. If the user then asks for a code change (for example a decision on a finding), write their words verbatim to `$STATE/user-<k>.md`, and run `[ -f $STATE/user-<k>-base ] || git rev-parse WORK > $STATE/user-<k>-base`. Spawn `review-fixer` with `MAIN_REPO`, `WORK_BRANCH`, `SPEC`, `ROUND: user-<k>`, `BASE: $(cat $STATE/user-<k>-base)`, `KIT`, `HYGIENE`, and `FINDINGS` pointing at that file. Write its status block to `$STATE/user-<k>-fix.md`. When it reads `STATUS: GREEN`, run step 7 again for that spec, without its merge and without the queue: the closing acceptance, the PR body, the push, the PR update and the report. Otherwise relay the block. If the user explicitly asks for a mechanical action (merge the PR, close an issue, delete a branch), run exactly that command. Nothing else.

Variables:
- `MAIN` — absolute repo root (`git rev-parse --show-toplevel`)
- `GITDIR` — absolute `git rev-parse --git-common-dir`
- `STATE` — `$GITDIR/run-spec/<slug>`. Untracked run records live here: `wt/` worktrees, `handoffs/<id>.md`, `reports/<id>.md` and `started-<id>` written by the implementers, `<id>-attempt<k>.md` failures, `<id>-resume<j>.md` resumes, `status-<id>.md` ticket status blocks, `stalled-<id>`, `wave-NN.md`, `repair-NN.md`, `triage-N.in` with its `triage-N.md`, `review-N.md` with its `review-N-base`, `review-N-fix.md` and `verify-N/` (holding the verifier's `started`), `acceptance-final.md` with `verify-final-<m>/`, `running/`, `main-owner`, `owner-<k>.md`, `user-<k>.md` with `user-<k>-base` and `user-<k>-fix.md`, `probes.md`, `learnings.md`, `pr-body.md`. Keeping worktrees inside `.git` means they never pollute the tree, `git status`, or test discovery.
- `WORK` — the work branch
- `DEFAULT` — the default branch: `git symbolic-ref --short refs/remotes/origin/HEAD` without `origin/`, falling back to `main` or `master`
- `<id>` — the oracle id with `#` stripped, used in every path and branch name
- `ORACLE` — `python3 ${CLAUDE_SKILL_DIR}/tickets.py --tracker <T> --spec <SPEC> --work-branch <WORK> --failures-dir $STATE`
- `HYGIENE` — `python3 ${CLAUDE_SKILL_DIR}/hygiene.py`, the hygiene gate: run from inside a checkout as `HYGIENE <base> <head> [--allow <path>]...`, it prints one line per comment line or Markdown file the range adds, and nothing when clean. Agents receive it as `HYGIENE: python3 <absolute skill dir>/hygiene.py`.
- `KIT` — `${CLAUDE_SKILL_DIR}`, the absolute skill directory. Agents receive it as `KIT: <absolute skill dir>` and read `guides/tdd.md` and `axes/*.md` under it.

## 1. Resolve the input

- **Tracker**: read `docs/agents/issue-tracker.md`.
  - Heading `# Issue tracker: GitHub` → `github`.
  - Heading `# Issue tracker: Local Markdown` → `local`.
  - A missing file → stop and report "`docs/agents/issue-tracker.md` is missing: it must exist, headed `# Issue tracker: GitHub` or `# Issue tracker: Local Markdown`".
  - Any other heading → stop and report "`docs/agents/issue-tracker.md` lacks the heading `# Issue tracker: GitHub` or `# Issue tracker: Local Markdown`".
- **Queue**: `$ARGUMENTS` may name several specs, may carry `--merge`, and may end in free-text notes. When it holds more than one spec token, or `--merge`, or any notes, read [`QUEUE.md`](QUEUE.md) now. It sets QUEUE, MERGE and OWNER_NOTES, and selects the spec token that SPEC comes from. Otherwise QUEUE is SPEC alone and MERGE is false.
- **SPEC** comes from `$ARGUMENTS`:
  - `#N` or `N` → `#N`.
  - A `.scratch/<slug>` directory or its `spec.md` → that path.
  - A handoff written by `ticket-implementer` → `sed -n 's/^Spec: *\([^ ]*\).*/\1/p' <file> | head -1`. That line is the only part of the handoff you read. Other handoffs, such as `/handoff` output, carry no `Spec:` line: stop and tell the user to run `/run-spec #N` or `/run-spec .scratch/<slug>`. Never infer SPEC from a title, filename, or body. A later reply like "go" or "create a branch" is not a SPEC.
  - Empty → stop and report.
- **Local mode**: `git ls-files --error-unmatch <spec-dir>/issues` must succeed. If the tickets are not committed, worktrees cannot see them: stop and report.
- **Wave size** `P`: the number on a `max-parallel: <N>` line of `docs/agents/run-spec.md`, when that file has one; otherwise 3. A repo whose suite is heavy (Docker, containers, long integration runs) sets it lower there, so parallel suites cannot starve the machine.

Done when TRACKER, SPEC and P are set.

## 2. Resolve the branch

1. If `git rev-parse -q --verify MERGE_HEAD` succeeds (a crash left a merge half-done), run `git merge --abort`.
2. Get `slug`: run ORACLE with `--work-branch HEAD --failures-dir /dev/null`.
3. Keep Claude Code's own worktree folder out of `git status`: `git check-ignore -q .claude/worktrees/ || echo '.claude/worktrees/' >> "$GITDIR/info/exclude"`. When `git status --porcelain` is not empty and `$STATE/main-owner` exists, the dirty paths are the partial work of the MAIN-side agent it names, which died: run `git stash push -u -m "run-spec: abandoned <agent> work"` and append `stashed abandoned <agent> work` to `$STATE/learnings.md`. Keep `main-owner`: step 3 re-runs its agent. Then `git status --porcelain` must be empty. If not, stop and report the dirty paths. Never stash in any other case: that is the user's work.
4. If the current branch is DEFAULT:
   - `spec/<slug>` exists → `git switch spec/<slug>` (resume).
   - Otherwise → `git switch -c spec/<slug>`.
5. On any other branch, stay.

`WORK` = the branch you end on. Then `mkdir -p $STATE/wt $STATE/handoffs $STATE/reports $STATE/running`.

Done when on WORK with a clean tree.

## 3. Recover (resume after a crash or a halt)

**Same conversation first.** When the session dropped mid-run (a login, a usage limit, or a restart ended the turn) and the user says "continue" in this conversation, the stopped subagents usually still exist, with their context intact. Run `ListAgents`. Send each stopped subagent of the current wave, review, or triage one message: "The session was renewed. Check that no process you started is still running, then continue from where you stopped and finish with your status block." Then wait for their notifications as usual. A subagent `ListAgents` does not show is gone, for example after `/clear` or in a new conversation. In that case, and on every fresh `/run-spec`, run the recovery below.

Run steps 2.1 and 2.3, then `git worktree prune`. On a fresh `/run-spec`, also run `rm -f $STATE/running/*`: no agent of an earlier session is still running.

**Red base.** `NN` = the number of the highest `$STATE/wave-*.md`, when one exists. When that file reads `STATUS: RED` and `$STATE/repair-NN.md` is missing or reads `STATUS: RED`, a halted wave left WORK red, and no ticket may branch from it. Spawn `wave-integrator` in repair mode, with `MAIN_REPO`, `WORK_BRANCH`, `WAVE: NN`, `HYGIENE`, and `MERGE` and `DISCARD` both empty. Write its status block verbatim to `$STATE/repair-NN.md`.
- `STATUS: GREEN` → continue below.
- `STATUS: RED` → halt with its `SUMMARY:` as the reason, and go to step 7.

Then run ORACLE and sort each branch matching `WORK--*` into the first class that fits:

- **Merged orphan**: `git merge-base --is-ancestor <branch> WORK` succeeds, and the `Ticket:` trailer of the branch tip (`git log -1 --format='%(trailers:key=Ticket,valueonly)' <branch>`, with `#` stripped) equals `<id>`. An integrator, or 5d's fast-forward, was cut off after merging it. Remove its worktree when the path exists, and `git branch -d <branch>`; item 3 below records it. A branch with no commits of its own fails the trailer test.
- **Failed orphan**: `$STATE/status-<id>.md` reads `STATUS: FAILED`. The implementer returned FAILED and 5c's cleanup was cut off: run 5c's FAILED path, removing the worktree only when its path exists. Its `FAILURE_OUT` is already in STATE.
- **Finished orphan**: the ticket finished but was never integrated. The implementer writes STATUS_OUT as its last file action, so `grep -q '^STATUS: DONE' $STATE/status-<id>.md` marks it.
- **Unfinished orphan**: anything else. When ORACLE does not list `<id>` in `remaining` (it is done or skipped), discard it with 5c's FAILED path (the worktree only when its path exists) and write no attempt. Otherwise its commits and uncommitted edits are kept and resumed. `j` = the count of `$STATE/<id>-resume*.md` files + 1.
  - `j` ≤ 2: write `$STATE/<id>-resume<j>.md` with one line, `interrupted, resumed`. If `$STATE/wt/<id>` is gone, run `git worktree add $STATE/wt/<id> <branch>`; otherwise run `touch $STATE/wt/<id>`, so the watchdog counts the resume as activity. Queue the ticket for resume. A resume is not an attempt: the oracle counts only `-attempt` files.
  - `j` > 2: the ticket keeps getting cut off. Write `$STATE/<id>-attempt<k>.md` with `interrupted after two resumes` (`k` = its oracle `attempts` + 1), then run 5c's FAILED path.

Then, in this order:
1. **Dead MAIN-side agent.** When `$STATE/main-owner` exists, the agent it names never returned, whether or not it left MAIN dirty. Delete the marker, then re-run that agent by its record:
   - `wave-<m>.md`, still missing → when finished orphans remain, item 2 re-runs it. Otherwise spawn `wave-integrator` in repair mode (`WAVE: <m>`, `MERGE` and `DISCARD` empty), so the suite runs on what it merged, and write its block to `$STATE/wave-<m>.md`. `STATUS: RED` → halt as 5d does.
   - `repair-NN.md` → the red-base rule above has re-run it.
   - `triage-<t>.md` → item 4 re-runs it.
   - `review-<r>-fix.md` → the top of step 6 re-runs it.
   - `user-<k>-fix.md` → spawn it again as "After the report" says.
2. Integrate the finished orphans with steps 5d and 5e, as a wave of their own, using `-` as the worktree of any orphan whose directory is gone.
3. **Unrecorded merges.** The ids the ORACLE run above lists as `done` whose `$STATE/status-<id>.md` reads `STATUS: DONE` and that no `MERGED:` line of a `wave-*.md` names (`#` stripped on both sides) were merged by an agent cut off before its record (a merged orphan, or a gone branch). When there are any, write `$STATE/wave-<n>.md` with `STATUS: GREEN` and `MERGED: <ids> (recovered)`.
4. Run owed triage (5e).
5. Run the resume queue in waves of at most P tickets, through steps 5a–5f. In 5a, skip `git worktree add`, the codegraph init and the install (the worktree exists), and set `BASE_SHA` = `git merge-base WORK <branch>`. Each prompt in 5b also carries `RESUME: true`.

Done when WORK is not a red base, no triage is owed, `$STATE/main-owner` is gone, and `git branch --list 'WORK--*'` is empty.

## 4. Read the frontier

Run ORACLE.
- `ready` and `remaining` both empty → step 6.
- `ready` empty, `remaining` not empty → the remaining tickets wait on a dependency cycle, or on an open ticket outside the run's scope (for example `needs-info` or `ready-for-human`). Tickets behind skipped ones are already marked skipped. Record the ids as **stuck** and go to step 6.
- Otherwise the wave is the first P ids of `ready`, taken in the oracle's order. The limit is deliberate: every ticket runs a full test suite on this one machine. The wave holds only these ids: no id from `remaining` that is not in `ready`, and no id you know from anywhere else.

## 5. Run one wave

A wave takes its number when it starts: `n` = the count of `$STATE/wave-*.md` files + 1, zero-padded to two digits. Step 3's orphan integration, its unrecorded merges, and each resume wave take their own.

**a. Set up each ticket** (`k` = its oracle `attempts` + 1). First run `rm -f $STATE/status-<id>.md $STATE/stalled-<id>`: an earlier attempt's status file or stall marker would hide this run from the watchdog and from step 3.

```
git worktree add $STATE/wt/<id> -b WORK--<id> WORK
```

Then index the new worktree for the implementer, before dispatch. This is the one codegraph step the contract allows, and it is skipped silently when `codegraph` is not installed:

```
command -v codegraph >/dev/null && (cd $STATE/wt/<id> && codegraph init >/dev/null 2>&1 && { git check-ignore -q .codegraph || echo '.codegraph/' >> "$(git rev-parse --git-common-dir)/info/exclude"; })
```

The `info/exclude` line keeps the untracked `.codegraph/` out of `git status` in repos whose `.gitignore` does not already ignore it. A failed init is not a failure of the ticket: the implementer falls back to Grep/Read.

Then install the dependencies a fresh worktree lacks. Offline works because the main checkout already filled the pnpm store; repos without `pnpm-lock.yaml` skip it:

```
[ -f $STATE/wt/<id>/pnpm-lock.yaml ] && (cd $STATE/wt/<id> && pnpm install --frozen-lockfile --offline >/dev/null 2>&1)
```

A failed install is not a failure of the ticket: the implementer installs on its own.

- `BASE_SHA` = `git rev-parse WORK`
- `HANDOFF_OUT` = `$STATE/handoffs/<id>.md`
- `REPORT_OUT` = `$STATE/reports/<id>.md`
- `STATUS_OUT` = `$STATE/status-<id>.md`
- `FAILURE_OUT` = `$STATE/<id>-attempt<k>.md`
- `CONTEXT_HANDOFFS` — each of these absolute paths that exists:
  - `$STATE/handoffs/<b>.md` for each direct blocker `b` (the oracle's `blockers`, `#` stripped)
  - the highest-numbered `$STATE/wave-*.md`
  - every `$STATE/<id>-attempt*.md`
  - if the ticket has no blockers: the newest file in `$STATE/handoffs/` (`ls -t $STATE/handoffs | head -1`)

**b. Dispatch.** Spawn one `ticket-implementer` per ticket, all in one message so they run in parallel. Each prompt is only `KEY: value` lines:
- `TRACKER`, `SPEC`, `SLUG: <slug>`
- `TICKET_ID` (oracle `id`, with `#`), `TICKET_REF` (oracle `ref`)
- `MAIN_REPO`, `WORKTREE`, `BRANCH`, `BASE_SHA`
- `HANDOFF_OUT`, `REPORT_OUT`, `STATUS_OUT`, `FAILURE_OUT`, `CONTEXT_HANDOFFS`
- `KIT`, `HYGIENE`
- `RESUME: true`, only for a ticket resumed by step 3

Then start the **watchdog**, unless one runs: `bash ${CLAUDE_SKILL_DIR}/watchdog.sh $STATE` with `run_in_background`. A subagent that dies sends no notification, so the watchdog's exit is the only signal. Keep exactly one running while `$STATE/wt/` holds a worktree or `$STATE/running/` holds a marker: when it exits, handle its line, then start it again while either exists. It sleeps one interval before each check and skips a ticket whose `status-<id>.md` exists.
- `stalled: <id>` (no file change and no process for 120 min): when `$STATE/stalled-<id>` exists, this is the agent's second stall: write `FAILURE_OUT` with `stalled twice` and collect the ticket as FAILED (5c). Otherwise run `touch $STATE/stalled-<id>`, which also mutes the watchdog for that id for 120 min, record the stall in `$STATE/probes.md`, run `ListAgents`, and send the agent step 3's resume message when it is stopped, or the stall probe when it runs and `probes.md` names no earlier probe of it.
- `overdue: <label>` (a `running/` marker untouched for 240 min): run `touch $STATE/running/<label>`, which restarts its deadline, record the event in `$STATE/probes.md`, and run `ListAgents`. An agent that runs gets the stall probe, unless `probes.md` names an earlier probe of it. A stopped or absent agent is respawned once: when its marker already reads `respawned`, halt with `agent <label> lost` and go to step 7. Otherwise run `echo respawned >> $STATE/running/<label>`, run steps 2.1 and 2.3, and spawn it again with the same keys.

**c. Collect.** Write each status block verbatim to `$STATE/status-<id>.md`, replacing the copy the implementer wrote there.
- **FAILED**: run `git worktree remove --force $STATE/wt/<id>` and `git branch -D WORK--<id>`. Then stop what the implementer started, from its registry (`container <name>` or `pid <pid> <args>` lines):
  ```
  [ -f $STATE/started-<id> ] && while read -r kind v args; do case $kind in container) docker rm -f "$v" ;; pid) [ "$(ps -o args= -p "$v")" = "$args" ] && kill "$v" ;; esac; done < $STATE/started-<id> >/dev/null 2>&1; rm -f $STATE/started-<id>
  ```
  The failure handoff stays in STATE, so the oracle counts the attempt. After two attempts, the oracle skips the ticket and its dependents.
- **Missing or malformed status block**: counts as FAILED. If FAILURE_OUT is absent, write it yourself with one line: `no status returned`.

**d. Integrate** the DONE tickets.
- **Exactly one, and `git merge-base WORK WORK--<id>` equals `git rev-parse WORK`** (WORK has not moved since that ticket's BASE_SHA):
  1. `git merge --ff-only WORK--<id>`.
  2. Remove its worktree and branch.
  3. Write `$STATE/wave-<n>.md` containing `STATUS: GREEN`, `MERGED: <id> (fast-forward)`.
- **Two or more, or one whose base WORK has moved past** (a resumed ticket, after step 3 integrated other orphans): spawn `wave-integrator` with:
  - `MAIN_REPO`, `WORK_BRANCH`, `WAVE: <n>`, `HYGIENE`
  - `MERGE` — one line per ticket, in ticket order: `<id> WORK--<id> $STATE/wt/<id> $STATE/handoffs/<id>.md`
  - `DISCARD` — empty

  Write its status block verbatim to `$STATE/wave-<n>.md`.
- **`MERGE_FAILED` ids** (each with `#` stripped): write `$STATE/<id>-attempt<k>.md` with the integrator's one-line reason. The attempt counts, and the ticket reruns on the new base.
- **`STATUS: RED`** → **halt**. Record the reason, skip step 6, and go to step 7. The next `/run-spec` repairs WORK in step 3 before any wave starts.

**e. Triage follow-ups.** Skip on a halt.
- `FOLLOWUPS` = the `$STATE/status-<id>.md` paths whose `FOLLOWUPS:` line is not `none`, one per id on the `MERGED:` line of `$STATE/wave-<n>.md`: strip each id's `#`, and skip a parenthesized note such as `(fast-forward)`. Leave out FAILED and MERGE_FAILED tickets: their branch is gone, so their follow-ups describe code that is not on WORK. Step 7 still lists their links.
- Triage runs here, after integration, never right after collect. In local mode a follow-up file reaches WORK only when its ticket merges, and the triager commits to WORK, which needs the clean tree that integration leaves.
- `t` = the count of `$STATE/triage-*.in` files + 1. Skip when FOLLOWUPS is empty or `t` > 4. The cap stops recursion: an absorbed ticket can file follow-ups of its own. Untriaged links still reach step 7 through the status files.
- Write `$STATE/triage-<t>.in`: the FOLLOWUPS paths, one per line, then `SOURCE: wave-<n>` (`SOURCE: review-<r>-fix` from step 6).
- Spawn `followup-triager` with `TRACKER`, `SPEC`, `MAIN_REPO`, `WORK_BRANCH`, `ROUND: <t>`, `FOLLOWUPS` (the paths of `triage-<t>.in`, one per line), and `ORACLE` (the full command, expanded). Write its status block verbatim to `$STATE/triage-<t>.md`, and print `triage <t>: attached <ATTACHED>`.
- `STATUS: RED` from the triager is not a halt: the follow-ups stay out of the run, and step 7 reports them.
- **Owed triage**, run by step 3 and at the top of step 6: a `triage-<t>.in` without its `triage-<t>.md` is spawned again from that file, with the same `t`. A `wave-<n>.md` that reads `STATUS: GREEN`, or `STATUS: RED` with a `repair-<n>.md` that reads `STATUS: GREEN`, or a `review-<r>-fix.md` with `follow-up` lines, whose FOLLOWUPS list is not empty and whose source no `.in` names on its `SOURCE:` line, gets this step now, while `t` ≤ 4. Past the cap nothing is owed.

**f. Check** that `git worktree list` shows nothing under `$STATE/wt/`. Then go back to step 4. ORACLE now lists the attached follow-ups as tickets of the spec, and they run in the next waves like any other ticket.

## 6. Final review

Six axes review the branch, and every section ends in a `COUNT:` line:

| Axis | Run by | Brief | Its `COUNT:` counts toward |
|---|---|---|---|
| Acceptance | `acceptance-verifier` | its own agent file | blocking: FAIL and scope creep. UNVERIFIED counts toward nothing |
| Standards | `ticket-reviewer` | `axes/standards.md` | blocking |
| Security | `ticket-reviewer` | `axes/security.md` | blocking: HIGH and MEDIUM. Advisory: `needs-human` |
| UX/AIX | `ticket-reviewer`, behind its gate | `axes/ux-aix.md` | advisory |
| Design | `ticket-reviewer` | `axes/design.md` | advisory |
| Hygiene | you, with `HYGIENE` | none | blocking |

The **blocking count** sums Acceptance's and Security's first number with Standards' and Hygiene's number. The **advisory count** sums Security's `needs-human` with UX/AIX's and Design's number. Only a blocking count starts a round; the fixer handles advisory findings, but they never start a round on their own.

Round 1 reviews the whole branch. Rounds 2 and 3 are **verification rounds**: the code-reading axes and Hygiene review only the commits since the previous fixer started, which no review has read yet. Acceptance re-runs every criterion every round. No final-review axis reads round 3's own fixes, the fixes of an advisory-only round, or the tickets round 3's triage attaches. Each fixer runs the hygiene gate over its own `BASE`, each attached ticket gets its per-ticket review, and step 7's closing acceptance executes every criterion on the final WORK.

`r` = the count of `$STATE/review-<N>.md` reports, not counting `review-<N>-fix.md`, + 1. First, finish what a cut-off run left:
- `review-<r-1>.md` has a blocking or advisory count above zero but no `review-<r-1>-fix.md`: its fixer was cut off. Run item 5 for round `r-1`.
- Then run owed triage (5e). When it attaches tickets, go to step 4.

Go to step 7 when:
- `r` > 3, or
- `r` ≥ 2 and `git rev-list --count $(cat $STATE/review-<r-1>-base)..WORK` is 0, because the previous fixer committed nothing and no ticket merged since, or
- `review-<r-1>.md` has a blocking count of zero, and either its advisory count is zero too, or it has a `review-<r-1>-fix.md` (an advisory-only round whose fixer already ran) and `git log $(cat $STATE/review-<r-1>-base)..WORK --format='%(trailers:key=Ticket,valueonly)'` prints nothing (no ticket that its triage attached has merged since). This makes a resume after a clean or advisory-only round go straight on.

1. **Prepare.** Give every reviewer its answers up front, so none of them asks:
   - `F`: round 1, `$(git merge-base WORK origin/DEFAULT)`, or `DEFAULT` with no remote. Rounds 2 and 3, `$(cat $STATE/review-<r-1>-base)`.
   - `VERIFY_ONLY`, rounds 2 and 3 only: `commits $(cat $STATE/review-<r-1>-base)..WORK; findings $STATE/review-<r-1>.md; fixes $STATE/review-<r-1>-fix.md`.
   - `KNOWN_DISMISSALS`: the `dismissed` lines of every `$STATE/review-*-fix.md` and `$STATE/user-*-fix.md`, inline, or `none`.
   - **UX/AIX gate**: run `git diff --name-only F...WORK | grep -E -q -f <(grep -v '^[[:space:]]*$' ${CLAUDE_SKILL_DIR}/axes/ux-aix.triggers)`. It succeeds when the diff touches a UI or agent-surface file. When it fails, do not spawn the UX/AIX reviewer; its section is `skipped: no UI or agent-surface files` and `COUNT: 0`.
   - `TICKETS`: the `ref` of every ticket the last ORACLE run lists with `done: true` and `in_scope: true`, space-separated.
   - `NOT_DONE`: the `id` of every ticket the last ORACLE run lists with `done: false` (skipped, stuck, or out of scope), space-separated, or `none`.
   - `mkdir -p $STATE/verify-<r>` and `rm -f $STATE/acceptance-final.md`: this round's Acceptance supersedes an earlier closing one.
2. **Spawn** every reviewer in one message, so they run in parallel. Each prompt is only `KEY: value` lines:
   - `acceptance-verifier`: `REPO: MAIN`, `SPEC`, `TICKETS`, `ROUND: <r>`, `F`, `OUT_DIR: $STATE/verify-<r>/`, `PREVIOUS: $STATE/verify-<r-1>/` (`none` in round 1), `SLUG: <slug>`, `KNOWN_DISMISSALS`, `NOT_DONE`.
   - `ticket-reviewer`, one per axis (Standards, Security, Design, and UX/AIX when its gate passed): `AXIS`, `AXIS_BRIEF` (the absolute path of `${CLAUDE_SKILL_DIR}/axes/standards.md`, `security.md`, `ux-aix.md` or `design.md`), `REPO: MAIN`, `DIFF: git diff F...WORK`, `COMMITS: git log F..WORK --oneline`, `SPEC`, `SCOPE: branch`, `ROUND: <r>`, `KNOWN_DISMISSALS`, plus `VERIFY_ONLY` in rounds 2 and 3.

   Then run **Hygiene**: `HYGIENE F WORK 2>&1`, adding `--allow <path>` for every path other than `none` on an `ALLOWED:` line of `$STATE/status-*.md`, `review-*-fix.md` and `user-*-fix.md`. Its section is `## Hygiene`, then each line it printed as `- <line>` (`- none` when it exits 0), then `COUNT: <lines printed>`.
3. **Record.** Build the report in `$STATE/review-<r>.partial`: truncate it when the round's agents are spawned (`: > $STATE/review-<r>.partial`), write the `## Hygiene` section and any `## UX/AIX` skipped line then, and append each other section verbatim as its agent returns (`cat >> $STATE/review-<r>.partial <<'EOF'`). When all six sections are in, `mv $STATE/review-<r>.partial $STATE/review-<r>.md`: a round's report exists only once complete, and no temporary file needs removing. In chat, print only `review <r>: Acceptance <fail>/<unverified>, Standards <x>, Security <z>, UX/AIX <w|skipped>, Design <v>, Hygiene <h>`, from the `COUNT:` lines. Never summarise, triage, or discuss individual findings; triaging them is the fixer's job.
4. **Route** by the round's counts:
   - Blocking and advisory both zero → go to step 7.
   - Blocking zero, advisory above zero → run item 5 once, and item 6's triage if it applies. Then go to step 7 without a new round, unless item 6's triage attached tickets: then item 6's route back to step 4 applies.
   - Otherwise → item 5.
5. **Fix.** Run `[ -f $STATE/review-<r>-base ] || git rev-parse WORK > $STATE/review-<r>-base`, which keeps the base of a fixer that was cut off, so the next verification round still reads its commits. Spawn `review-fixer` with `MAIN_REPO`, `WORK_BRANCH`, `SPEC`, `ROUND: <r>`, `BASE: $(cat $STATE/review-<r>-base)`, `FINDINGS: $STATE/review-<r>.md`, `KIT` and `HYGIENE`, and write its status block verbatim to `$STATE/review-<r>-fix.md`.
6. If `review-<r>-fix.md` has `follow-up` lines, run step 5e's triage with `FOLLOWUPS: $STATE/review-<r>-fix.md` and `SOURCE: review-<r>-fix` (same `t` and cap). When its `ATTACHED:` is not `none`, go back to step 4. The attached tickets run in new waves. The next pass through step 6 reviews them as round `r` + 1, from `review-<r>-base`; after round 3 it goes to step 7, whose closing acceptance executes their criteria. This holds after an advisory-only round too.
7. Otherwise, return to the top of step 6 for the next round.

The **remaining findings** are the lines of the last `review-<N>-fix.md` that are not `fixed`, including every `needs-human` line, a RED status if that fixer returned one, and the FAIL and UNVERIFIED lines of the newest Acceptance (step 7).

Done when a review is clean, or a stop condition above holds after the last fixer and its triage have returned.

## 7. Publish and report

**Closing acceptance.** Skip it on a halt. The **newest Acceptance** is `$STATE/acceptance-final.md` when it exists, else the `## Acceptance` section of the last `review-<N>.md`. Its `HEAD:` line names the WORK it ran on. Run the closing acceptance when that line (`sed -n 's/^HEAD: *//p' <its file>`) differs from `git rev-parse --short=7 WORK`, a missing line included, or when the newest fix file (`ls -t $STATE/review-*-fix.md $STATE/user-*-fix.md 2>/dev/null | head -1`) dismisses a FAIL (`grep -q '^- A[0-9]* dismissed .*→'`) and is newer than the newest Acceptance's file (`[ <fix file> -nt <its file> ]`). Each closing run has its own directory, `$STATE/verify-final-<m>/`: `c` = the count of `$STATE/verify-final-*/` directories, and `m` = `c` when `[ $STATE/verify-final-<c> -nt $STATE/acceptance-final.md ]` succeeds (that run was cut off before its section was written, or a later round removed its section; the new run reuses its directory and stops what it left), else `c` + 1. Run ORACLE, recompute step 6 item 1's `TICKETS`, `NOT_DONE` and `KNOWN_DISMISSALS` from it and from STATE, run `mkdir -p $STATE/verify-final-<m>`, and spawn `acceptance-verifier` with step 6 item 2's keys, but `ROUND: final`, `OUT_DIR: $STATE/verify-final-<m>/`, round 1's `F`, and `PREVIOUS:` the newest Acceptance's directory: `$STATE/verify-final-<m-1>/` when `acceptance-final.md` exists, else `$STATE/verify-<N>/` for the last `review-<N>.md`. Write its section verbatim to `$STATE/acceptance-final.md`, replacing any earlier closing section, so it holds the newest Acceptance, and print `acceptance final: <fail>/<unverified>`. A FAIL there is not delivered: the PR body lists it, it holds `--merge`, and it starts no round.

Write the PR body to `$STATE/pr-body.md`, built from STATE, in this order:
- `## Summary`: per DONE ticket, from `status-<id>.md`, `Closes #N` (GitHub tracker only), its SUMMARY and its `REPORT:` link. Replace every path the `RENAMED:` lines of `wave-*.md` renamed for that ticket with its new path. Then the output of `git diff --stat F...WORK`, with round 1's `F`, in a code block.
- `## Evidence`: the newest Acceptance, verbatim, then **Not verified**: its UNVERIFIED lines, or `none`.
- `## Merge Danger`: `**Door:** one-way` with `<id>: <why>` for each ticket whose `DOOR:` is one-way, else `**Door:** two-way`. Then `**Blast Radius:**` with `<id>: <BLAST>` per DONE ticket.
- FOLLOWUPS links from the same files and from `review-*-fix.md`
- triage results: every `ISSUES:` line of each `triage-*.md`, so each follow-up shows its verdict and whether it was attached
- skipped tickets, each with its failure-handoff path
- stuck ids, if any
- remaining review findings
- halt reason, if any
- one line per owner decision from `owner-*.md` that changed the code, never the messages themselves

With a remote `origin`:
1. `git push -u origin WORK`.
2. Open or update the PR:
   - no PR for WORK yet → `gh pr create --base DEFAULT --head WORK --title "<spec title>" --body-file $STATE/pr-body.md`
   - PR already exists (`gh pr list --head WORK --json number`) → `gh api -X PATCH repos/{owner}/{repo}/pulls/<n> -F body=@$STATE/pr-body.md`. `gh pr edit` fails on repos that still use Projects classic.
3. Merge the PR only when MERGE is true, following `QUEUE.md`. Otherwise never merge it.

Without a remote: skip push and PR, and say so.

Report to the user in their language, as a short list with no recommendations and no questions:
- PR URL or branch
- done / skipped / stuck counts, with ids
- halt reason
- review outcome: rounds run, finding counts, and the UNVERIFIED count, plus the path of the remaining findings (`$STATE/review-*-fix.md`). Do not restate individual findings.
- follow-up links, split into attached (each also counted above as done, skipped, or stuck) and left out (with its triage verdict, or `untriaged`)
- learnings: every `LEARNINGS:` line that is not `none` from `status-*.md`, every line of the fix files that carries `learning:` (`grep -sh 'learning:' $STATE/review-*-fix.md $STATE/user-*-fix.md`), plus the paths of `learnings.md` and `probes.md`, when they exist. An older status block without that line counts as `none`.

When QUEUE holds another spec, continue with `QUEUE.md`. Otherwise the skill ends here, and later turns fall under the contract's "After the report" rule.

Done when every ticket from the last ORACLE run appears in the report as done, skipped, or stuck.
