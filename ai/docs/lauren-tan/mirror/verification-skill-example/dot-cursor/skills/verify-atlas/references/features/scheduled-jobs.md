# Scheduled jobs

Scheduled jobs sidebar panel: always-on cloud scheduled jobs and gated local scheduled tasks, including run histories.

## Sub-features

- automation-list: list of scheduled jobs with enable toggles
- create-edit: create and edit an automation
- run-history: per-automation run history
- local-schedules: gated local scheduled tasks

## How to get to it (user POV)

Open Scheduled jobs from the left rail. Create from the header button. Open a row for detail and history.

## Driving it with control-atlas

Create a no-op automation the suite owns, toggle it off, delete it in cleanup.

Run history may be empty; assert the empty state rather than fabricating runs.

## Gotchas

- Cloud scheduled jobs need entitlement. Local schedules are gated; skip with reason when absent.
- Do not leave enabled scheduled jobs that fire on real inboxes/calendars.
