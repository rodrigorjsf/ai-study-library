# Log pane

Read-only viewer for extension and log output channels, grouped by workspace, with auto-scroll, find, and copy path.

## Sub-features

- channel-list: grouped list of output channels
- channel-viewer: read-only log view with auto-scroll
- find-in-channel: find within the selected channel
- copy-path: copy the channel or log path

## How to get to it (user POV)

Open Output from the app panes. Pick a channel. Use find or copy path from the header.

## Driving it with control-atlas

Pick a channel that always exists in dev builds (for example a window/log channel). Assert non-empty content or an explicit empty state.

Copy path: activate Copy, then `eval` clipboard contents.

## Gotchas

- Channel names vary by platform and installed extensions. Snapshot the list before hard-coding a name.
