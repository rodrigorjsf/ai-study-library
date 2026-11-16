# Spec: Todo housekeeping

## Problem Statement

A todo list only grows. Finished items stay in `todo.py list` forever, the confirmation after finishing an item reads like the item was merely marked, and there is no way to see only what is left to do.

## Solution

`todo.py` gets a `clear` command that removes finished items, says `finished` when an item is finished, and lists only unfinished items on request.

## User Stories

1. As a user, I want `python3 -I -S todo.py clear` to delete every finished item, so that the list stays short.
2. As a user, I want `clear` to tell me how many items it removed, so that I know it did something.
3. As a user, I want `python3 -I -S todo.py done <id>` to answer `finished <id>`, so that the confirmation says what happened.
4. As a user, I want `python3 -I -S todo.py list --open` to print only unfinished items, so that I see what is left.
5. As a Windows user, I want `py -3 -I -S todo.py list --open` to print the same lines as on Linux, so that the app behaves the same on both.
6. As a user, I want an id never to be reused after `clear`, so that "item 3" keeps meaning the same item.

## Implementation Decisions

- An item keeps its id when other items are removed.
- An id is never reused: an item added after `clear` gets an id higher than every id issued before, finished or removed.
- `clear` writes the store once, after removing every finished item.
- `list --open` is a flag of `list`. `list` without it prints every item, as today.

## Testing Decisions

- The seam is the command line: `python3 -I -S todo.py <command>` against a throwaway store named by `TODO_STORE`. `test_todo.py` drives it through a subprocess.
- The Feature map entries of the `verify-todo` recipe prove each feature a ticket touches.

## Out of Scope

- Editing item text.
- Deleting one unfinished item.
- Colors, or any output other than plain lines.
