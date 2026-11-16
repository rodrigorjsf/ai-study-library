---
name: verify-todo
description: Start, check, drive and stop the todo command line app in this repository, and find the Feature map entry that proves each feature. Use when verifying a change to todo.py.
---

# Verify the todo app

`todo.py` is a command, not a service. No process stays running between two commands, so there is nothing to start in the background and nothing to kill afterwards.

Run every command from the repository root, with the standard library only: `python3 -I -S todo.py <command>`.

## Start

Create a throwaway store and point the app at it, so a probe never touches `.todo.json`:

`export TODO_STORE=$(mktemp)`

## Check

`python3 -I -S todo.py list` exits 0 and prints nothing on a fresh store. Any other result means the app is broken before your change is judged.

## Drive

Reach each feature through its command, as a user would:

- `python3 -I -S todo.py add <text>` adds an item and prints `added <id>`.
- `python3 -I -S todo.py list` prints one line per item, `<id> [ ] <text>` or `<id> [x] <text>`.
- `python3 -I -S todo.py done <id>` finishes an item and prints `done <id>`.

The [Feature map](feature-map.md) lists these features with the command that proves each one.

## Evidence

A command and its stdout are the evidence. A Feature map entry's proving command is the evidence for its feature: its exit code is the verdict, and it needs no screenshot, because the app has no screen.

## Stop

Nothing runs, so nothing stops. Remove the store with `rm -f "$TODO_STORE"`.
