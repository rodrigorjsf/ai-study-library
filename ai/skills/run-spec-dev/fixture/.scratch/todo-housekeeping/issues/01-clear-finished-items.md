# 01 — Clear finished items

Status: ready-for-agent
Blocked by: none

## Parent

`.scratch/todo-housekeeping/spec.md`

## What to build

A `clear` command that removes every finished item from the store and reports how many it removed. It exercises the Feature map entries for listing and finishing items.

## Acceptance criteria

- [ ] `python3 -I -S todo.py clear` removes every finished item from the store, prints `removed <n>` with the number removed, and exits 0
- [ ] `python3 -I -S todo.py clear` on a store with no finished items prints `removed 0`, leaves the store unchanged, and exits 0
- [ ] After `clear`, `python3 -I -S todo.py list` prints only the unfinished items, each with its original id
