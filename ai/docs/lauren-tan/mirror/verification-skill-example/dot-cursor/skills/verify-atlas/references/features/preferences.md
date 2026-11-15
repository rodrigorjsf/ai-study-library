# Preferences

Full-screen preferences overlay and its tab set.

## Sub-features

- settings-overlay: full-screen overlay opened from the gear or Cmd/Ctrl+,
- settings-nav: left nav of tabs (General, Appearance, Models, Plan & Usage, ...).
- settings-search: in-overlay search (Cmd/Ctrl+K while settings is open).
- theme-picker: quick theme control on Appearance.

## How to get to it (user POV)

Click the gear next to the account avatar, or press Cmd/Ctrl+,. Pick a tab from the left nav. Type in the preferences search box to jump. Escape or the close control dismisses.

## Driving it with control-atlas

```bash
node .cursor/skills/verify-atlas/control-atlas.mjs press "Meta+Comma"
node .cursor/skills/verify-atlas/control-atlas.mjs snapshot
node .cursor/skills/verify-atlas/control-atlas.mjs press "Escape"
```

- Overlay root: look for a dialog/region named Preferences in the a11y tree.
- Tabs: click by visible name. Plan & Usage may be absent for some account states.
- While settings is open, Cmd/Ctrl+K is preferences search, not the global palette (see `multi-surface-journeys.md`).

## Gotchas

- Closing settings mid-suite can leave focus nowhere useful. `new-session` or `home` recovers.
- Some tabs are entitlement-gated. Skip with an explicit account reason.
