# Issue tracker: Local Markdown

Issues and specs for this repository live as Markdown files under `.scratch/`.

## Conventions

- One spec per directory: `.scratch/<slug>/`.
- The spec is `.scratch/<slug>/spec.md`.
- Tickets are `.scratch/<slug>/issues/<NN>-<title>.md`, numbered from `01`, each opening with `# NN — <title>`.
- Triage state is a `Status:` line near the top of a ticket file: `ready-for-agent` runs it, `resolved` marks it done.
- Blocking is a `Blocked by:` line with ticket numbers, or `none`.
- Comments and run reports append to the bottom of the ticket file under a `## Comments` heading.

## When a skill says "publish to the issue tracker"

Create a new file under `.scratch/<slug>/`.

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path.
