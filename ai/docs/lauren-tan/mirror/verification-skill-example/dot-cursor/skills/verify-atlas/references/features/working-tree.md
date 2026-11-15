# Working tree

Working-tree review as diff cards: switch repo/scope, stage files, and hand commit/push/PR off to the agent.

## Sub-features

- diff-cards: per-file diff cards in the Working tree tab
- repo-scope-switch: switch repo and staged/unstaged scope
- stage-file: stage / unstage from a card
- commit-push-pr-handoff: prompt chips that ask the agent to commit, push, or open a PR

## How to get to it (user POV)

Open the Working tree app from the app panes or its shortcut. Dirty files appear as cards. Stage from the card header.

## Driving it with control-atlas

Use a disposable dirty file in a fixture repo. Avoid committing to shared branches in automation accounts.

Assert card titles match `git status` paths. Prefer `eval`/CLI corroboration over pixels alone.

## Gotchas

- Empty tree is valid when clean. Do not treat an empty Working tree tab as a driver failure.
- PR handoff needs a remote and provider auth; skip with reason when missing.
