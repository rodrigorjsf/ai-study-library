# Feature map

Each entry names a feature as a user meets it, the command that reaches it, and a proving command that exits 0 only when the feature works. Run every proving command from the repository root. Each one creates its own throwaway store and removes it when it ends.

## Add an item

- Reach: `python3 -I -S todo.py add <text>`
- Proves: `( store=$(mktemp) && trap 'rm -f "$store"' EXIT && TODO_STORE=$store python3 -I -S todo.py add milk | grep -qx 'added 1' )`

## List items

- Reach: `python3 -I -S todo.py list`
- Proves: `( store=$(mktemp) && trap 'rm -f "$store"' EXIT && TODO_STORE=$store python3 -I -S todo.py add milk >/dev/null && TODO_STORE=$store python3 -I -S todo.py list | grep -qx '1 \[ \] milk' )`

## Finish an item

- Reach: `python3 -I -S todo.py done <id>`
- Proves: `( store=$(mktemp) && trap 'rm -f "$store"' EXIT && TODO_STORE=$store python3 -I -S todo.py add milk >/dev/null && TODO_STORE=$store python3 -I -S todo.py done 1 | grep -qx 'done 1' && TODO_STORE=$store python3 -I -S todo.py list | grep -qx '1 \[x\] milk' )`
