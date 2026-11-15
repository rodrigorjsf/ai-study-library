# Session rows

A single session row: select, hover metadata, per-thread actions, and next/previous navigation.

## Sub-features

- row-select: click a row to focus its conversation.
- hover-tooltip: metadata tooltip on hover (project, runtime, updated-at).
- row-actions: pin, rename, fork, archive, move, open in window or web.
- keyboard-nav: next/previous thread chords; back/forward history.

## How to get to it (user POV)

Open the left rail. Click a row to select. Hover for the tooltip. Right-click (or the row overflow) for actions. Use the registered next/previous chords to move without the mouse.

## Driving it with control-atlas

```bash
node .cursor/skills/verify-atlas/control-atlas.mjs snapshot
# find a row in the a11y tree, then:
node .cursor/skills/verify-atlas/control-atlas.mjs aria-click "Sprint planning"
node .cursor/skills/verify-atlas/control-atlas.mjs wait-settle
```

- Rows live under `[data-component="left-rail"]` and expose a stable thread id attribute when present.
- Prefer `aria-click` / snapshot over brittle nth-child indexes.
- Rename: open the row menu, choose Rename, type, confirm. Assert the new label after `wait-settle`.
- Archive: archive once, assert the row leaves the active list, then restore if the suite needs the fixture.

## Gotchas

- Hover tooltips are timing-sensitive. Prefer action menus for deterministic proofs.
- Fork creates a new thread; do not assert the original row disappeared.
- Cloud rows can show optimistic placeholders before the server id lands (see `multi-surface-journeys.md`).
