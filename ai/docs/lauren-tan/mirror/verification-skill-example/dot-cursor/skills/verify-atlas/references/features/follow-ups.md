# Follow-ups and parallel sessions

Queue follow-ups during a running turn, reorder and edit them, start multitasking, and watch spawned subthreads in the tray.

## Sub-features

- follow-up-queue: queue messages while a turn is streaming
- queue-reorder-edit: reorder, edit, or delete queued items
- multitask-spawn: spawn parallel subthreads from a running turn
- subthread-tray: tray listing spawned subthreads with status

## How to get to it (user POV)

While a turn is streaming, type another prompt and submit. It lands in the queued-messages tray.

Open the tray to reorder or edit. Multitask controls appear when the product treatment is enabled.

## Driving it with control-atlas

```bash
node .cursor/skills/verify-atlas/control-atlas.mjs send "long running task..."
node .cursor/skills/verify-atlas/control-atlas.mjs send "follow up while that runs"
node .cursor/skills/verify-atlas/control-atlas.mjs snapshot
```

Queued tray: `[aria-label="Queued follow-ups"]`. Assert the follow-up is present before the first turn settles.

Multitask: enable the gate, trigger spawn, assert rows in the subthread tray with distinct ids.

## Gotchas

- Optimistic cloud create + immediate follow-up is covered in `multi-surface-journeys.md`; do not double-count.
- Editing a queued item after the parent turn finishes may promote it to a normal send. Snapshot timing matters.
