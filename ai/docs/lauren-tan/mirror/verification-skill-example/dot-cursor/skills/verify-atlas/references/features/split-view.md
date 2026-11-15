# Split view and app panes

Right app panes, tiling, collapsed icon rail, and per-thread tab memory.

## Sub-features

- app-panes: show/hide the right panel of app tabs.
- tile-split: split the thread area or an app tab into panes.
- tile-fullscreen: expand a tile or the editor panel.
- icon-rail: collapsed rail when the app panes is hidden.
- per-thread-tabs: which app tabs are open is remembered per thread.

## How to get to it (user POV)

Cmd/Ctrl+Alt+B toggles the app panes. Split and fullscreen chords are context-sensitive (see Gotchas). Open Files / Terminal / Browser from the panel or their direct shortcuts.

## Driving it with control-atlas

```bash
node .cursor/skills/verify-atlas/control-atlas.mjs press "Meta+Alt+KeyB"
node .cursor/skills/verify-atlas/control-atlas.mjs snapshot
```

- App panes root: `[data-component="app-panes"]`.
- Establish focus before overloaded chords (`Cmd/Ctrl+Shift+M`, `Cmd/Ctrl+W`).
- Dragging a sidebar thread into a tile target is not first-class in the driver; mark it manual and cover splits via the chord path instead.

## Gotchas

- `Cmd/Ctrl+Shift+M` and `Cmd/Ctrl+W` mean different things depending on focus. Establish layout first.
- Per-thread tab memory can look like "the panel forgot my tabs" when you switched threads. Switch back before filing a bug.
