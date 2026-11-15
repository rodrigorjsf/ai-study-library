# Left rail

Left sidebar: hide/show, resize, group, filter, paginate, reorder, and bulk-manage the session list.

## Sub-features

- sidebar-toggle: hide and show the left rail.
- sidebar-resize: drag the edge to change width; width persists per account.
- group-modes: Workspace / Repository / Environment grouping.
- filter-and-search: filter the session list by text and status chips.
- section-reorder: reorder sections inside a group mode.
- bulk-manage: multi-select archive / move / pin.
- onboarding-checklist: optional first-week checklist above the list.

## How to get to it (user POV)

Signed-in shell always shows the left rail unless hidden. Cmd/Ctrl+B toggles it. The New Thread control sits in the left-rail header. Right-click a section header for group-mode options.

## Driving it with control-atlas

```bash
node .cursor/skills/verify-atlas/control-atlas.mjs press "Meta+KeyB"    # toggle
node .cursor/skills/verify-atlas/control-atlas.mjs snapshot
node .cursor/skills/verify-atlas/control-atlas.mjs click '[data-action-id="new-session"]'
```

- Sidebar root: `[data-component="left-rail"]`.
- Toggle: `press "Meta+KeyB"` (macOS) / `press "Control+KeyB"` (Windows/Linux). Assert presence/absence of the left rail root.
- New Thread: click `data-action-id="new-session"` inside the left rail (analytics source `sidebar`) rather than the global chord when you need that source.
- Filter: focus the search box (`aria-label="Filter sessions"`), `type`, then assert visible rows.
- Section reorder and native drag: manual unless the driver grows first-class pointer drag. Do not substitute a service call and claim drag coverage.

## Gotchas

- Narrow layouts collapse the left rail into an icon rail. Snapshot before asserting row labels.
- Bulk-manage requires multi-select mode; entering it changes row hit targets.
- Onboarding checklist is account- and visit-sensitive; it can be absent without being a bug.
