# 03 — List only open items

Status: ready-for-agent
Blocked by: 01

## Parent

`.scratch/todo-housekeeping/spec.md`

## What to build

A `--open` flag for `list` that hides finished items. One criterion needs a Windows host, which the run does not have, so it ends as an unverified row in the pull request's acceptance table with what it needs.

## Acceptance criteria

- [ ] `python3 -I -S todo.py list --open` prints only the unfinished items, each with its original id
- [ ] `python3 -I -S todo.py list` without `--open` still prints every item
- [ ] `py -3 -I -S todo.py list --open` prints the same lines on Windows 11 as on Linux
