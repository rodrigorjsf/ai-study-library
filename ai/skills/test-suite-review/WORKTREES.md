# Worktrees

Where to create the worktree, per harness. Fetched from the official docs on 2026-10-11; confirm against the installed version, since these conventions move.

## Settle the location, in this order

1. **Configuration.** A worktree location or creation hook configured for this harness, in the repo or at user level.
2. **The harness's documented default**, from the table below.
3. **The repo's own habit.** `git worktree list` shows where this repo's other worktrees live; follow that parent directory.
4. **Ask.** When none of the above settles it, or the harness is not in the table, ask the user where the worktree should be created and wait.

Whatever the location, the worktree is created on a new branch (`test-suite-review/<date>`) that starts at the source branch's `HEAD`. Check it: `git -C <worktree> merge-base --is-ancestor <source HEAD> HEAD`.

## Per harness

| Harness | Location | Base | Notes |
|---|---|---|---|
| Claude Code | `.claude/worktrees/<name>/` at the repo root; a `WorktreeCreate` hook replaces this, including the location | `worktree.baseRef`: `"fresh"` (default) branches from the remote default branch, `"head"` from the current `HEAD` | See below. Source: https://code.claude.com/docs/en/worktrees |
| Codex | `$CODEX_HOME/worktrees`, or the **Worktree root** set in Settings > Worktrees | the `HEAD` of the branch chosen in the composer, detached | Create a branch in the worktree before committing. Source: https://learn.chatgpt.com/docs/environments/git-worktrees |
| Cursor | not stated in the docs; managed by Cursor's worktree manager | not stated | See below. Source: https://cursor.com/docs/configuration/worktrees |

### Claude Code

The default base is the remote default branch, which is not the source branch. So:

- With `worktree.baseRef` set to `"head"` in settings, or a `WorktreeCreate` hook configured: enter a worktree with the `EnterWorktree` tool, then verify its base.
- Otherwise: create it with git at the default location, `git worktree add .claude/worktrees/test-suite-review -b test-suite-review/<date> HEAD`, then call `EnterWorktree` with that path.

Inside the worktree, Claude Code blocks edits and git commands that target the main checkout, so step 10's merge runs after `ExitWorktree`. Ignored files the build needs (`.env`) are copied when listed in `.worktreeinclude`; copy them by hand for a worktree made with `git worktree add`. If `.claude/worktrees/` is not in `.gitignore`, tell the user.

### Cursor

Setup commands for a new worktree come from `.cursor/worktrees.json` (`setup-worktree-unix`, `setup-worktree-windows`, `setup-worktree`); run them in the worktree. Cursor's periodic cleanup keeps the newest worktrees up to a machine-wide cap (`cursor.worktreeMaxCount`, default 25) and can delete worktrees created with plain `git worktree add`. The docs give no default directory, so settle the location by rule 3 or 4, and finish the review in one sitting so cleanup cannot remove a worktree with unmerged work.

### Codex

Ignored files listed in `.worktreeinclude` at the repo root are copied into managed worktrees. Codex keeps the 15 most recent managed worktrees by default and deletes older ones.

### Any other harness

Use rules 1, 3, and 4. A plain `git worktree add <path> -b test-suite-review/<date> HEAD` works everywhere git does.

## Removing the worktree

After the merge and the post-merge run: leave the worktree with the harness's own exit (`ExitWorktree` in Claude Code), then `git worktree remove <path>` and `git branch -d test-suite-review/<date>`. `-d` refuses an unmerged branch, which is the check you want. A worktree a harness manages (Codex, Cursor's manager) is removed through the harness.
