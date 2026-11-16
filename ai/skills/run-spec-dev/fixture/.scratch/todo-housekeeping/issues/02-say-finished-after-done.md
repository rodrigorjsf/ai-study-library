# 02 — Say finished after done

Status: ready-for-agent
Blocked by: none

## Parent

`.scratch/todo-housekeeping/spec.md`

## What to build

The confirmation printed after finishing an item changes from `done <id>` to `finished <id>`. The Feature map entry that proves finishing an item still expects the old text, so this ticket also shows what an implementer does with a recipe step that no longer works: it reports the stale step as a follow-up and leaves the recipe untouched.

## Acceptance criteria

- [ ] `python3 -I -S todo.py done <id>` prints `finished <id>` for an existing item and exits 0
- [ ] `python3 -I -S todo.py done <id>` for an id that is not in the store prints `no such item: <id>` on stderr and exits 1
- [ ] `python3 -I -S todo.py list` marks the finished item `[x]`
