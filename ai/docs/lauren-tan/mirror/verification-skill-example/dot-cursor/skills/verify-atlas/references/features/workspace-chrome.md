# Workspace chrome and first launch

The persistent authenticated frame plus first-launch onboarding.

## Sub-features

- root-layout: authenticated chrome that wraps sidebar, session panel, and app panes.
- titlebar: drag-only titlebar; platform menu bar on Windows/Linux.
- agent-header: top bar for the focused thread (title, project badge, overflow).
- first-launch-splash: logo splash before the setup wizard.
- setup-wizard: first-run flow for workspace pick, theme, and notifications.

## How to get to it (user POV)

After sign-in the shell is always present. New installs see the splash, then the wizard. Completing or skipping the wizard lands on an empty thread surface with the left rail visible.

## Driving it with control-atlas

```bash
node .cursor/skills/verify-atlas/control-atlas.mjs doctor
node .cursor/skills/verify-atlas/control-atlas.mjs home
node .cursor/skills/verify-atlas/control-atlas.mjs snapshot
```

- Assert `[data-component="root"]` plus `[data-component="left-rail"]` when signed in.
- First-launch paths need a clean user-data-dir without onboarding-complete markers.
- Skip native menu-bar items on macOS when the driver cannot reach them; say so.

## Gotchas

- Splash can be skipped by leftover onboarding flags in user-data-dir. Reset userdata when testing the wizard.
- Titlebar drag targets are not clickable content; do not use them as selectors for actions.
