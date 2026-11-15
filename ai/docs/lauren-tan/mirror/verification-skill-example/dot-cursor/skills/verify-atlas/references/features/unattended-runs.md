# Unattended runs

Launch a run that babysits the branch's PR, then review findings in the thread tray, suggestion tabs, or the PR's Unattended view.

## Sub-features

- start-run: launch a unattended run for the current branch/PR
- findings-tray: findings listed on the thread
- suggestion-tabs: per-finding suggestion tabs
- pr-unattended-view: PR tab section for the run

## How to get to it (user POV)

From a branch with an open PR, start Unattended from the session overflow or PR tab.

## Driving it with control-atlas

Needs a disposable PR the suite owns. Start a run, wait for at least one finding or a clean empty state, then cancel/stop.

## Gotchas

- Runs cost quota and mutate PR comments in some configurations. Prefer fixtures and stop promptly.
