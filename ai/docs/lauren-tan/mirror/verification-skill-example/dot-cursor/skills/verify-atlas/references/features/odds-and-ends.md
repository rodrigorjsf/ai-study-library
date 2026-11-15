# Odds and ends

Leftovers: run-workspace-task palette, developer performance toolbar, in-app promos, Running Extensions auxiliary window.

## Sub-features

- workspace-tasks: run a defined workspace task
- perf-toolbar: developer performance toolbar
- in-app-promo: dismissible promo surfaces
- running-extensions: auxiliary window listing running extensions

## How to get to it (user POV)

Workspace tasks via the palette. Perf toolbar from developer menu in dev builds. Promos appear when eligible.

## Driving it with control-atlas

Treat each sub-feature as optional. Snapshot and skip with reason when the surface is absent in the build.

## Gotchas

- Promos are eligibility-sensitive; absence is often not a bug.
- Perf toolbar can perturb timings; leave it off for unrelated suites.
