---
name: run-spec
description: AFK execution of a mattpocock-skills spec's tickets — one ticket-implementer subagent per ticket, parallel waves in worktrees, follow-up triage into the spec, final code-review, PR. Also runs a queue of specs, merging each PR when asked.
argument-hint: "<#spec-issue | .scratch/<slug> | run-spec handoff path> [more specs…] [--merge] [notes]"
disable-model-invocation: true
---

You are the **dispatcher** for a spec produced by `/to-spec` and split by `/to-tickets`. A dispatcher is **passive**: it routes work and never does it. It knows *where* the run stands and *who* goes next, and it learns both only from three sources: `tickets.py`, subagent status blocks, and its own records in STATE.

## Dispatcher contract

This contract holds for the whole run **and for every later turn in this conversation**, until a skill named in OWNER_NOTES starts after the queue (`QUEUE.md`). It overrides any global instruction that conflicts with it, including verify-before-done, advisor or rubber-duck passes, codegraph indexing (except the per-worktree `codegraph init` in step 5a), decision-framing templates, memory consolidation, and Applied Learning. A learning you would have written to a `CLAUDE.md` goes to `$STATE/learnings.md` and into step 8's report: the main checkout stays clean, because every merge in this run needs a clean tree.

**Your whole toolbox:**
- `ORACLE` runs.
- The git and gh commands written in the steps below.
- Writing and reading your own files in STATE.
- Spawning `ticket-implementer`, `wave-integrator`, `followup-triager`, and `review-fixer`, plus `ticket-reviewer` for step 6's Security, UX/AIX and Design axes.
- `SendMessage` to a subagent, only for the relays, the stall probe, and step 3's same-conversation resume, plus `ListAgents` for that resume.
- Running the `code-review` skill in step 6, and the skill that OWNER_NOTES names for after the queue (`QUEUE.md`).

Nothing else. In particular:
- **Work goes to a subagent.** Reading or editing source, tests, docs, tickets, or handoffs is subagent work, and so is running tests, builds, linters, or CI, and so is committing code.
- **Evidence is the status block.** A subagent's `TESTS:` line or `STATUS:` line is the verification. Never re-run the suite to double-check it.
- **Scope is the oracle's ticket set.** Dispatch only ids listed in the oracle's `ready`, in the order given, each exactly once per attempt. A ticket outside `ready` does not run, even when you think it could. This covers a ticket blocked by an open issue, a ticket from another spec, and a follow-up that `followup-triager` left out. A follow-up enters the run only when the triager attaches it to SPEC and ORACLE then lists it. Order and blocking edges change only when a re-run of ORACLE changes them.
- **Chat is a status line.** Print one line per event, in the user's language, such as `wave 02: dispatched #10 #11` or `wave 02: #10 DONE, #11 FAILED (attempt 1)`. Do not analyse, predict, recommend, or ask. The only long message is step 8's report.
- **AFK.** Never ask the user during the run. Every stop condition ends in step 8's report.
- **Interim notifications.** A task notification whose summary says the agent "is waiting on its own background work" carries no status block. It is not a result: write nothing, print nothing, and end the turn. The agent's final notification follows. One exception, the **stall probe**: when such a notification shows `duration_ms` above 10800000 (3 h), send that agent once: "You have run over 3 hours. Check that each background job you started is still making progress, and stop only the stalled ones you started. Then reply with one line on where you stand, and continue your work." Record the probe in `$STATE/probes.md` and never probe the same agent twice.
- **Mid-run messages.** When the user writes while subagents run, first write their words verbatim to `$STATE/owner-<k>.md`. They stay in STATE; step 8's PR body carries one line only for a decision that changed the code. Then act by kind:
  - A question about progress → answer in one status line, from STATE and the latest notifications.
  - A caution or instruction for the running agents ("careful with Docker", "stop the tests and finish") → send it verbatim to each running subagent it concerns, and print one line naming them.
  - "Pause" or "stop" → spawn nothing new. Let the running subagents return, finish step 5c and 5d for them, then go to step 8 with halt reason `paused by owner`. A later `/run-spec` resumes from STATE.
  - Anything that changes scope or order → print one line saying it applies through the tracker on the next `/run-spec`, and continue.
- **After the report.** The run is over. If the user then asks for a code change (for example a decision on a finding), write their words verbatim to `$STATE/user-<k>.md`. Spawn `review-fixer` with `FINDINGS` pointing at that file. Relay its status block. If the user explicitly asks for a mechanical action (merge the PR, close an issue, delete a branch), run exactly that command. Nothing else.

Variables:
- `MAIN` — absolute repo root (`git rev-parse --show-toplevel`)
- `GITDIR` — absolute `git rev-parse --git-common-dir`
- `STATE` — `$GITDIR/run-spec/<slug>`. Untracked run records live here: `wt/` worktrees, `<id>-attempt<k>.md` failures, `<id>-resume<j>.md` resumes, `status-<id>.md` ticket status blocks, `wave-NN.md`, `triage-N.md`, `review-N.md` with its `review-N-base` and `review-N-fix.md`, `owner-<k>.md`, `probes.md`, `learnings.md`. Keeping worktrees inside `.git` means they never pollute the tree, `git status`, or test discovery.
- `WORK` — the work branch
- `DEFAULT` — the default branch: `git symbolic-ref --short refs/remotes/origin/HEAD` without `origin/`, falling back to `main` or `master`
- `<id>` — the oracle id with `#` stripped, used in every path and branch name
- `ORACLE` — `python3 ${CLAUDE_SKILL_DIR}/tickets.py --tracker <T> --spec <SPEC> --work-branch <WORK> --failures-dir $STATE`

## 1. Resolve the input

- **Tracker**: read `docs/agents/issue-tracker.md`.
  - Heading `# Issue tracker: GitHub` → `github`.
  - Heading `# Issue tracker: Local Markdown` → `local`.
  - Anything else, or a missing file → stop and report "run /setup-matt-pocock-skills first".
- **Queue**: `$ARGUMENTS` may name several specs, may carry `--merge`, and may end in free-text notes. When it holds more than one spec token, or `--merge`, or any notes, read [`QUEUE.md`](QUEUE.md) now. It sets QUEUE, MERGE and OWNER_NOTES, and SPEC is the first spec of QUEUE. Otherwise QUEUE is SPEC alone and MERGE is false.
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
2. Keep Claude Code's own worktree folder out of `git status`: `git check-ignore -q .claude/worktrees/ || echo '.claude/worktrees/' >> "$GITDIR/info/exclude"`. Then `git status --porcelain` must be empty. If not, stop and report the dirty paths. Never stash the user's work.
3. Get `slug`: run ORACLE with `--work-branch HEAD --failures-dir /dev/null`.
4. If the current branch is DEFAULT:
   - `spec/<slug>` exists → `git switch spec/<slug>` (resume).
   - Otherwise → `git switch -c spec/<slug>`.
5. On any other branch, stay.

`WORK` = the branch you end on. Then `mkdir -p $STATE/wt`.

Done when on WORK with a clean tree.

## 3. Recover orphans (resume after a crash)

**Same conversation first.** When the session dropped mid-run (a login, a usage limit, or a restart ended the turn) and the user says "continue" in this conversation, the stopped subagents usually still exist, with their context intact. Run `ListAgents`. Send each stopped subagent of the current wave, review, or triage one message: "The session was renewed. Check that no process you started is still running, then continue from where you stopped and finish with your status block." Then wait for their notifications as usual. A subagent `ListAgents` does not show is gone, for example after `/clear` or in a new conversation. In that case, and on every fresh `/run-spec`, run the recovery below.

Run step 2.1, then `git worktree prune`. Then check each branch matching `WORK--*`:

- **Merged orphan**: `git merge-base --is-ancestor <branch> WORK` succeeds, and the `Ticket:` trailer of the branch tip (`git log -1 --format='%(trailers:key=Ticket,valueonly)' <branch>`, with `#` stripped) equals `<id>`. An integrator was cut off after merging it. Remove its worktree if the path exists, then `git branch -d <branch>`. A branch with no commits of its own fails the trailer test and is an unfinished orphan.
- **Finished orphan**: `git log WORK..<branch> --format=%s` contains `chore(handoff):`. The ticket finished but was never integrated.
- **Unfinished orphan**: anything else. Its commits and uncommitted edits are kept and resumed, not discarded. `j` = the count of `$STATE/<id>-resume*.md` files + 1.
  - `j` ≤ 2: write `$STATE/<id>-resume<j>.md` with one line, `interrupted, resumed`. If `$STATE/wt/<id>` is gone, run `git worktree add $STATE/wt/<id> <branch>`. Queue the ticket for resume. A resume is not an attempt: the oracle counts only `-attempt` files.
  - `j` > 2: the ticket keeps getting cut off. Write `$STATE/<id>-attempt<k>.md` with `interrupted after two resumes` (`k` = its oracle `attempts` + 1), then remove the worktree and `git branch -D <branch>`.

Then, in this order:
1. Integrate the finished orphans with steps 5d and 5e, using this wave's number and `-` as the worktree of any orphan whose directory is gone.
2. Run the resume queue in waves of at most P tickets, through steps 5a–5f. In 5a, skip `git worktree add`, the codegraph init and the install (the worktree exists), and set `BASE_SHA` = `git merge-base WORK <branch>`. Each prompt in 5b also carries `RESUME: true`.

A `$STATE/review-<N>.md` with findings but no `review-<N>-fix.md` means a review-fixer was cut off: step 6 respawns it before anything else.

Done when `git branch --list 'WORK--*'` is empty.

## 4. Read the frontier

Run ORACLE.
- `ready` and `remaining` both empty → step 6.
- `ready` empty, `remaining` not empty → the remaining tickets wait on a dependency cycle, or on an open ticket outside the run's scope (for example `needs-info` or `ready-for-human`). Tickets behind skipped ones are already marked skipped. Record the ids as **stuck** and go to step 6.
- Otherwise the wave is the first P ids of `ready`, taken in the oracle's order. The limit is deliberate: every ticket runs a full test suite on this one machine. The wave holds only these ids: no id from `remaining` that is not in `ready`, and no id you know from anywhere else.

`n` = the count of `$STATE/wave-*.md` files + 1, zero-padded to two digits.

## 5. Run one wave

**a. Set up each ticket** (`k` = its oracle `attempts` + 1):

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
- `HANDOFF_OUT` = `$STATE/wt/<id>/.handoffs/<slug>/<id>.md`
- `FAILURE_OUT` = `$STATE/<id>-attempt<k>.md`
- `CONTEXT_HANDOFFS` — each of these absolute paths that exists:
  - `$MAIN/.handoffs/<slug>/<b>.md` for each direct blocker `b`
  - the highest-numbered `$STATE/wave-*.md`
  - every `$STATE/<id>-attempt*.md`
  - if the ticket has no blockers: the newest file in `$MAIN/.handoffs/<slug>/`

**b. Dispatch.** Spawn one `ticket-implementer` per ticket, all in one message so they run in parallel. Each prompt is only `KEY: value` lines:
- `TRACKER`, `SPEC`
- `TICKET_ID` (oracle `id`, with `#`), `TICKET_REF` (oracle `ref`)
- `MAIN_REPO`, `WORKTREE`, `BRANCH`, `BASE_SHA`
- `HANDOFF_OUT`, `FAILURE_OUT`, `CONTEXT_HANDOFFS`
- `RESUME: true`, only for a ticket resumed by step 3

Then start the **watchdog** with `run_in_background`: `bash /home/rodrigo/.claude/skills/run-spec/watchdog.sh $STATE`. A subagent that dies sends no notification, so its exit is the only signal. When it prints `stalled: <id>`, run `ListAgents`; a ticket agent shown stopped gets step 3's resume message once (record it in `$STATE/probes.md`; a second stall of the same agent counts as FAILED with `FAILURE_OUT` = `stalled twice`). Then restart the watchdog while worktrees remain. It exits silently when the wave's worktrees are gone.

**c. Collect.** Write each status block verbatim to `$STATE/status-<id>.md`.
- **FAILED**: run `git worktree remove --force $STATE/wt/<id>` and `git branch -D WORK--<id>`. The failure handoff stays in STATE, so the oracle counts the attempt. After two attempts, the oracle skips the ticket and its dependents.
- **Missing or malformed status block**: counts as FAILED. If FAILURE_OUT is absent, write it yourself with one line: `no status returned`.

**d. Integrate** the DONE tickets.
- **Exactly one, and `git merge-base WORK WORK--<id>` equals `git rev-parse WORK`** (WORK has not moved since that ticket's BASE_SHA):
  1. `git merge --ff-only WORK--<id>`.
  2. Remove its worktree and branch.
  3. Write `$STATE/wave-<n>.md` containing `STATUS: GREEN`, `MERGED: <id> (fast-forward)`.
- **Two or more, or one whose base WORK has moved past** (a resumed ticket, after step 3 integrated other orphans): spawn `wave-integrator` with:
  - `MAIN_REPO`, `WORK_BRANCH`, `WAVE: <n>`
  - `MERGE` — one line per ticket, in ticket order: `<id> WORK--<id> $STATE/wt/<id> $STATE/wt/<id>/.handoffs/<slug>/<id>.md`
  - `DISCARD` — empty
  
  Write its status block verbatim to `$STATE/wave-<n>.md`.
- **`MERGE_FAILED` ids**: write `$STATE/<id>-attempt<k>.md` with the integrator's one-line reason. The attempt counts, and the ticket reruns on the new base.
- **`STATUS: RED`** → **halt**. Record the reason, skip step 6, and go to step 7.

**e. Triage follow-ups.** Skip on a halt.
- `FOLLOWUPS` = the `$STATE/status-<id>.md` paths of the ids on the `MERGED:` line of `$STATE/wave-<n>.md` whose `FOLLOWUPS:` line is not `none`. Leave out FAILED and MERGE_FAILED tickets: their branch is gone, so their follow-ups describe code that is not on WORK. Step 8 still lists their links.
- Triage runs here, after integration, never right after collect. In local mode a follow-up file reaches WORK only when its ticket merges, and the triager commits to WORK, which needs the clean tree that integration leaves.
- `t` = the count of `$STATE/triage-*.md` files + 1. Skip when FOLLOWUPS is empty or `t` > 4. The cap stops recursion: an absorbed ticket can file follow-ups of its own. Untriaged links still reach step 8 through the status files.
- Spawn `followup-triager` with `TRACKER`, `SPEC`, `MAIN_REPO`, `WORK_BRANCH`, `ROUND: <t>`, `FOLLOWUPS` (one path per line), and `ORACLE` (the full command, expanded). Write its status block verbatim to `$STATE/triage-<t>.md`, and print `triage <t>: attached <ATTACHED>`.
- `STATUS: RED` from the triager is not a halt: the follow-ups stay out of the run, and step 8 reports them.

**f. Check** that `git worktree list` shows nothing under `$STATE/wt/`. Then go back to step 4. ORACLE now lists the attached follow-ups as tickets of the spec, and they run in the next waves like any other ticket.

## 6. Final review

Five axes review the branch:

- **Standards** and **Spec**: from the `code-review` skill.
- **Security**, **UX/AIX** and **Design**: briefs in `${CLAUDE_SKILL_DIR}/axes/`.

Standards, Spec and Security's blocking findings are the **blocking axes**: only they decide whether another round runs. UX/AIX, Design and Security's `needs-human` findings are **advisory**. The fixer handles them, but they never start a round on their own.

Rounds 1 and 2 review the whole branch. Round 3 is a **verification round**: it reviews only the commits of round 2's fixer, which no review has read yet. The only code that ships unreviewed is then round 3's own small fixes, plus the fixes of an advisory-only round (item 3).

`r` = the count of `$STATE/review-<N>.md` reports, not counting `review-<N>-fix.md`, + 1. First, if `review-<r-1>.md` reports findings but has no `review-<r-1>-fix.md`, a fixer was cut off: run item 4 for round `r-1`, then come back here. Go to step 7 when:
- `r` > 3, or
- `r` = 3 and `git rev-list --count $(cat $STATE/review-2-base)..WORK` is 0, because round 2's fixer committed nothing, or
- `review-<r-1>.md` reports zero blocking findings, and it either reports no advisory findings either, or has a `review-<r-1>-fix.md` (an advisory-only round whose fixer already ran). This makes a resume after a clean or advisory-only round go straight on.

1. Run the review. Give every reviewer its answers up front, so none of them asks:
   - **Fixed point**:
     - Rounds 1–2: `F` = `$(git merge-base WORK origin/DEFAULT)`, or `DEFAULT` with no remote.
     - Round 3: `F` = `$(cat $STATE/review-2-base)`, and the spec is SPEC plus `$STATE/review-2.md` and `$STATE/review-2-fix.md`. Add to every axis brief: "Check only that each finding marked `fixed` is fixed, and that these commits break nothing. Report nothing outside these commits."
   - **Known dismissals**: when any `$STATE/review-*-fix.md` exists, add its `dismissed` lines to every brief: "Re-raise a known dismissal only with evidence its reason does not answer, and say which dismissal it reopens."
   - **UX/AIX gate**: run `git diff --name-only F...WORK | grep -E -q -f <(grep -v '^[[:space:]]*$' ${CLAUDE_SKILL_DIR}/axes/ux-aix.triggers)`. It succeeds when the diff touches a UI or agent-surface file. When it fails, do not spawn the UX/AIX reviewer, and record the axis as `skipped: no UI or agent-surface files`.
   - **Spawning**: run the `mattpocock-skills:code-review` skill with F and the spec. When it spawns its Standards and Spec axes, spawn the new axes in the same message, so all of them run in parallel. Use `subagent_type: ticket-reviewer` for all five. Each new-axis prompt is only `KEY: value` lines:
     - `AXIS`: Security, UX/AIX or Design
     - `AXIS_BRIEF`: the absolute path of `${CLAUDE_SKILL_DIR}/axes/security.md`, `ux-aix.md` or `design.md`
     - `REPO`: MAIN
     - `DIFF`: `git diff F...WORK`
     - `COMMITS`: `git log F..WORK --oneline`
     - `SPEC`
     - `ROUND`
     - `KNOWN_DISMISSALS`: a path, or `none`
     - in round 3, `VERIFY_ONLY` with the round-3 sentence above

   Take the reports as-is; the diff itself stays with the reviewers.
2. Write the report verbatim to `$STATE/review-<r>.md`: the skill's aggregated report, then `## Security`, `## UX/AIX` (or its `skipped` line) and `## Design`, each as its reviewer returned it. In chat, print only `review <r>: Standards <x>, Spec <y>, Security <z>, UX/AIX <w|skipped>, Design <v>`, taking `z`, `w` and `v` from each section's `COUNT:` line. Never summarise, triage, or discuss individual findings; triaging them is the fixer's job.
3. Route by what the round found:
   - Every section reports zero findings → go to step 7.
   - The blocking axes report zero findings (the skill's closing summary for Standards and Spec, plus `COUNT: 0 blocking` for Security), but advisory findings remain → run item 4 once, and item 5's triage if it applies. Then go to step 7 without a new round.
   - Otherwise → item 4.
4. Run `git rev-parse WORK > $STATE/review-<r>-base`, spawn `review-fixer` with `MAIN_REPO`, `WORK_BRANCH`, `SPEC`, `ROUND: <r>`, `FINDINGS: $STATE/review-<r>.md`, and write its status block to `$STATE/review-<r>-fix.md`.
5. If `review-<r>-fix.md` has `follow-up` lines, run step 5e's triage with `FOLLOWUPS: $STATE/review-<r>-fix.md` (same `t` and cap). When its `ATTACHED:` is not `none`, go back to step 4. The attached tickets run in new waves, and the next pass through step 6 reviews the branch as round `r` + 1. This holds after an advisory-only round too.
6. Otherwise, return to the top of step 6 for the next round.

The **remaining findings** are the lines of the last `review-<N>-fix.md` that are not `fixed`, including every `needs-human` line, plus a RED status if that fixer returned one.

Done when a review is clean, or the step 7 condition above holds after the last fixer and its triage have returned.

## 7. Clean the branch

If `git ls-files --error-unmatch .handoffs >/dev/null 2>&1` succeeds:

```
git rm -r -q .handoffs
git commit -m "chore(run-spec): drop handoffs for <slug>"
```

The handoffs stay in the branch history. The oracle still detects finished tickets from their `Ticket:` commit trailers.

## 8. Publish and report

Write the PR body to `$STATE/pr-body.md`, built from STATE:
- one line per DONE ticket: `Closes #N` (GitHub tracker only) plus its SUMMARY, from `status-<id>.md`, with every path the `RENAMED:` lines of `wave-*.md` renamed for that ticket replaced by its new path
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
- review outcome: rounds run and finding counts, plus the path of the remaining findings (`$STATE/review-*-fix.md`). Do not restate individual findings.
- follow-up links, split into attached (each also counted above as done, skipped, or stuck) and left out (with its triage verdict, or `untriaged`)
- learnings: every `LEARNINGS:` line that is not `none` from `status-*.md`, plus the paths of `learnings.md` and `probes.md`, when they exist. An older status block without that line counts as `none`.

When QUEUE holds another spec, continue with `QUEUE.md`. Otherwise the skill ends here, and later turns fall under the contract's "After the report" rule.

Done when every ticket from the last ORACLE run appears in the report as done, skipped, or stuck.
