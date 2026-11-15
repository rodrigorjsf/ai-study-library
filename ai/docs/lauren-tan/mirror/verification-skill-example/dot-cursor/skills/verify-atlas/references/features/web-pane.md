# Web pane

In-app browser tab: omnibar, navigation, find in page, favorites/history, multiple tabs, console, design mode, agent-control lock.

## Sub-features

- omnibar: URL entry and search
- nav-controls: back, forward, reload
- find-in-page: find within the page
- favorites-history: bookmarks and history drawers
- multi-tab: multiple browser tabs in the app
- dev-console: embedded console for the page
- agent-lock-overlay: overlay when the agent controls the page

## How to get to it (user POV)

Open Browser from the app panes. Type a URL in the omnibar and Enter. Use find with Cmd/Ctrl+F while the page is focused.

## Driving it with control-atlas

```bash
# open Browser via UI, then:
node .cursor/skills/verify-atlas/control-atlas.mjs snapshot
```

Prefer a local static fixture URL over the public internet for determinism.

Agent-lock: start a turn that drives the page, assert the lock overlay, abort, assert unlock.

## Gotchas

- External auth popups are system-browser and manual.
- Design mode and console may be gated; skip with reason when absent.
