# Handoff: restart `/orchestrate 181` (post-#207)

**Created:** 2026-05-22
**Supersedes:** `HANDOFF_ORCHESTRATE_206_05_22_scope_probe.md` (consumed — its probe ran, #206 closed) and the older `HANDOFF_ORCHESTRATE_181_05_22_restart.md` (its plan was invalidated by #206/#207).
**Goal of next session:** run `/orchestrate 181`. Both blockers that stopped earlier attempts (#206, #207) are resolved.

---

## Why the prior restarts were blocked — now cleared

- **#206** — subagent capability MCP tools listed-but-uncallable. Probed empirically; **did not reproduce**. Three this-session probes passed, including the real `orchestrate:implementer-standard` with its restricted `tools:` frontmatter. Closed as not-reproducible. Candidate hypothesis (unverified): tool-schema deferral in large-catalog harness contexts. Full evidence and the reopen criterion: `docs/analysis/orchestrate-181-probe-blocker.md`.
- **#207** — capability tools fail in fresh worktrees because `create_worktree` ran no dependency install. A `git worktree` checks out only tracked files, so `node_modules` was absent and every slice's `run_tests` failed with `vitest: not found` (exit 127). **Fixed and landed** — PR #208, squash-merged to `development` as `91e2552`. `create_worktree` now runs a configured `install` verb after `git worktree add`.

## Critical precondition before running `/orchestrate 181`

**The plugin cache is version-pinned.** The #207 fix ships in orchestrate **1.1.0**; the on-disk cache may still hold **1.0.4** (no fix).

1. Check the installed orchestrate plugin version — `/plugin`, or inspect `~/.claude/plugins/cache/agent-engineering-toolkit/orchestrate/`.
2. If it is still `1.0.4`, update the plugin so `1.1.0` is installed. **A run on 1.0.4 hits the #207 gap again** — every slice fails `run_tests` with `vitest: not found`.
3. Confirm `.orchestrate/commands.json` carries the `install` verb (it does on `development` — committed in #208: `["npm","--prefix","plugins/orchestrate/orchestrate-mcp","ci"]`).

## State

- `development` tip: `91e2552`. Local checkout synced. No worktrees, no `.orchestrate/run-state.json`, no run in progress.
- Backlog — 14 open `ready-for-agent` orchestrate issues, all Parent PRD #181:
  #186, #187, #189, #190, #191, #192, #193, #194, #195, #196, #197, #198, #200, #203.
- #206 and #207 are closed.

## The plan

The user already chose to run `/orchestrate 181` once #207 was landed manually. Run it. Reference notes:

- Expected wave structure (the skill's `plan_waves` recomputes this — use only as a sanity check):
  - Wave 0 (no blockers): #186, #187, #189, #190, #191, #200, #203
  - Wave 1: #192 (←186), #193 (←189), #194 (←187), #195 (←187,191), #196 (←191), #197 (←191)
  - Wave 2: #198 (the marketplace version cascade — blocked by all)
- #198 lists out-of-backlog blockers (#184, #185, #188) — already closed; the wave loop's processability check ignores blockers not in the backlog.
- This is a **dogfood run** — the orchestrate plugin orchestrating its own hardening. The run executes on the cached 1.1.0 plugin; slices modify source that only takes effect after merge + rebuild + cache refresh, so the run itself is stable (no self-modification mid-flight).
- `/goal` could not be set programmatically last session (it is a built-in CLI command, not invocable via the Skill tool). For an autonomous run, set `/goal` manually first, or drive the run turn by turn.

## Active goal (carries forward)

Any new orchestrate-plugin defect found during the run → new GitHub issue (Parent PRD #181, `ready-for-agent`, AFK-triaged), folded into the run. PRD #181 is "done" only when every orchestrate-plugin problem is resolved with tests and documented evidence.

## Deferred from the #207 review (advisory — not blocking)

The #208 multi-agent review raised three advisory items, consciously deferred, recorded in the PR #208 body. A future PRD #181 reviewer may re-raise them:

- `create_worktree` runs the checked-out ref's `install` command — the same exec-from-config trust model the capability tools already use.
- `runInstall` uses the 600s default timeout with no per-verb override — a slow `npm ci` on a cold cache could hit it.
- A worktree left on disk after `INSTALL_FAILED` keeps its branch, so a same-name retry needs a `remove_worktree` first.
