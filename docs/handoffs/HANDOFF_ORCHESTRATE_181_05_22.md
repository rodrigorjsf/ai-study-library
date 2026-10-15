# Handoff: Re-run /orchestrate for PRD #181

**Created:** 2026-05-22
**Branch:** `fix/orchestrate-rebuild-dist` (merged — switch to `development` before continuing)
**Goal of next session:** run `/orchestrate:orchestrate 181` to autonomously implement PRD #181's remaining backlog.

---

## Summary

PRD #181 hardens the `orchestrate` plugin against eleven defects. An earlier `/orchestrate 181` run was deliberately **stopped before it started** — feeding the PRD's own fix-backlog through the still-buggy plugin is a dogfooding catch-22. Three foundational fixes were landed manually first (PRs #201 + #202, both merged into `development`). The next session resumes the original goal: run `/orchestrate 181` against the now-less-buggy plugin to implement the remaining 12 issues.

---

## Work Completed (this session)

- [x] Stopped the `/orchestrate 181` run cleanly — no umbrella branch created, `.orchestrate/run-state.json` untouched.
- [x] **#184** SSH-safe git fetch — `src/git.ts` `core.sshCommand=` → `core.sshCommand=ssh` + vitest regression test. PR #201.
- [x] **#185** namespace subagent types — `orchestrate:` prefix in `SKILL.md` + `README.md`. PR #201.
- [x] **#188** wave-base umbrella-ref freshness step — new wave-loop step in `SKILL.md`. PR #201.
- [x] `chore(release)` orchestrate 1.0.2 (PR #201), then **1.0.3** (PR #202) after a stale-bundle fix.
- [x] Caught and fixed a stale `dist/index.js` — #184's fix was in `src/` but the committed esbuild bundle was not rebuilt. PR #202 rebuilt it.
- [x] Code review (6-agent `ce-code-review`): P1 test bug + P2 + P3 fixed; pre-existing P1 filed as #200.
- [x] Filed #203 (CI guard for stale `dist/`).
- [x] Runtime "before" test: invoked `create_worktree` MCP tool → `fetchStatus: "failed"` — confirmed the bug is live in the **installed 1.0.2** plugin.

PRs #201 and #202 are **merged** into `development` (tip `14ba6e4`). Issues #184/#185/#188 are **closed**.

---

## Current State

### What's done
- `development` carries orchestrate **1.0.3** with all three fixes, including a rebuilt `dist/index.js` (verified contains `core.sshCommand=ssh`).

### Blocker — must clear before the run
- The **installed plugin cache is still 1.0.2** (`~/.claude/plugins/cache/agent-engineering-toolkit/orchestrate/` has only `1.0.1/` and `1.0.2/`). Merging a PR does not update the installed plugin. Until `/plugin marketplace update` runs, `/orchestrate` executes the buggy 1.0.2 bundle.

### Owed verification
- Runtime "after" test: re-invoke `create_worktree` once 1.0.3 is loaded and confirm `fetchStatus: "ok"`. The "before" half (`failed`) is already done.

---

## Next Steps

### Immediate (do in order)

1. **Update the plugin to 1.0.3.** In the new session run:
   ```
   /plugin marketplace update
   /reload-plugins
   ```
   Then confirm `~/.claude/plugins/cache/agent-engineering-toolkit/orchestrate/1.0.3/` exists and its `orchestrate-mcp/dist/index.js` contains `core.sshCommand=ssh`.

2. **Verify the runtime fix.** Invoke the `create_worktree` MCP tool against this repo (SSH `origin`): `baseRef: HEAD`, a throwaway `branch`, a `worktreePath` under `/tmp`, `repoPath` = repo root. Expect `fetchStatus: "ok"`. Clean up with `remove_worktree` (`force: true`) + `git branch -D <throwaway>`. If `fetchStatus` is still `failed`, the plugin did not update — do not proceed.

3. **Run `/orchestrate:orchestrate 181`.** Backlog is the 12 open `ready-for-agent` issues, all PRD #181 children: #186, #187, #189, #190, #191, #192, #193, #194, #195, #196, #197, #198. The `181` argument names the parent PRD (progress-comment target). Expected wave shape (`plan_waves` recomputes it): Wave 0 = #186/#187/#189/#190/#191; Wave 1 = #192/#193/#194/#195/#196/#197; Wave 2 = #198.

### Blocked On
- Step 3 is blocked on steps 1–2.

---

## Things to Know (hazards for the run)

- **Only 3 of 11 PRD defects are fixed.** #184 (SSH fetch / F-005), #185 (namespacing / F-006), #188 (stale umbrella / F-008) are done. The other 8 defects are still live in the 1.0.3 plugin — the remaining 12 backlog issues fix them. The run will be cleaner than before but **not defect-free**; stay vigilant.
- **TDD-in-sandbox is unsolved.** Subagents have no Bash and the repo has no `.orchestrate/commands.json`, so the `run_tests`/`run_typecheck`/`run_build`/`run_lint` capability tools return `not-configured`. Subagents will write vitest tests they cannot execute — the PRD's `/tdd` red-green delivery contract cannot be enforced inside the orchestrate sandbox. To make test verification real, the orchestrator must either (a) supply a `commands.json` pointing at `npm --prefix plugins/orchestrate/orchestrate-mcp ...` plus a per-worktree `npm ci`, or (b) accept that test code ships unverified and review it manually. Decide this before Wave 0.
- **`dist/` is a committed build artifact.** Any slice touching `plugins/orchestrate/orchestrate-mcp/src/**` must run `npm run build` and commit the regenerated `dist/`. Vitest runs against `src/`, so green tests do NOT prove the bundle is correct — this exact miss caused PR #202. (#203 proposes a CI guard.)
- **Parent-PRD pollution (F-004) is unfixed but harmless here.** PRD #181 itself is labelled `needs-triage`, not `ready-for-agent`, so the backlog query will not enrol it as a slice.
- **A fresh run overwrites `.orchestrate/run-state.json`** (currently a `completed` PRD-143 run). Expected for the flat-layout 1.0.x plugin; the per-run-directory layout is issue #191, not yet built.
- **Subagent spawn names must be namespaced** — `orchestrate:implementer-deep` etc. (#185 fixed the skill text; the orchestrator follows it).
- **Branch off `origin/development`**, not the local ref (local drifts behind).

---

## Related Resources

- **Merged PRs:** #201 (foundational fixes), #202 (bundle rebuild).
- **Open issues filed this session:** #200 (pre-existing P1 — inherited `GIT_SSH_COMMAND` overrides the SSH hardening in `gitEnv()`), #203 (CI guard for stale `dist/`). Both `needs-triage`, not in the run backlog.
- **PRD:** issue #181. **Backlog:** issues #186–#198 (minus the 3 closed).

### Commands to start

```bash
git checkout development && git pull origin development
ls ~/.claude/plugins/cache/agent-engineering-toolkit/orchestrate/   # expect 1.0.3 after update
```

---

## Open Questions

- [ ] How to make the `/tdd` delivery contract real inside the orchestrate sandbox (supply `commands.json` + `npm ci`, or accept unverified test code)? Resolve before Wave 0.
- [ ] Local branch `fix/orchestrate-rebuild-dist` is merged and can be deleted (`git branch -d`).

---

_Generated as a context-window handoff. Start a new session, update the plugin to 1.0.3, verify the runtime, then run `/orchestrate:orchestrate 181`._
