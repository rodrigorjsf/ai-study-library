# Shell pane

xterm shell tab: run commands, multiple terminals, buffer search, agent read-only terminals, quit-with-background-terminals dialog.

## Sub-features

- interactive-terminal: user-owned shell
- multi-terminal: create, split, and switch terminals
- buffer-search: search the scrollback
- agent-readonly-terminal: terminal panes owned by a tool call
- quit-background-dialog: warn on quit when shells still run

## How to get to it (user POV)

Open Terminal from the app panes or its shortcut. Type a command and Enter. Create another via the plus control.

## Driving it with control-atlas

Type a deterministic command (`echo atlas-fixture-42`), assert the string in a snapshot or via buffer search.

Agent-readonly: trigger a shell tool call, assert the pane is not freely editable.

## Gotchas

- Do not rely on shell prompt format. Assert on command output you control.
- Quit dialog needs an intentional background process; clean up after.
