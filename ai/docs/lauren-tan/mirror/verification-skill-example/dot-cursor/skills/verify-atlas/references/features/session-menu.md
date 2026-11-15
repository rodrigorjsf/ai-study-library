# Session menu and feedback

Thread overflow actions (fork, copy, share, export, archive, pin, rename, open in window or web) plus per-turn feedback.

## Sub-features

- thread-overflow: ellipsis menu on the session header
- fork-thread: fork into a new thread from a chosen turn
- copy-share-export: copy transcript, share link, export markdown
- archive-pin-rename: lifecycle actions also reachable from the left rail row
- thumbs-feedback: per-turn thumbs up/down with optional comment

## How to get to it (user POV)

Open a thread. Click the header ellipsis for thread actions. Hover an assistant turn for thumbs controls.

## Driving it with control-atlas

```bash
node .cursor/skills/verify-atlas/control-atlas.mjs snapshot
# open header overflow via aria, exercise Rename then Escape
```

Prefer snapshot to find menu item names. Cancel destructive actions during read-only sweeps.

Fork: choose Fork from turn N, assert a new session row appears and the original is unchanged.

## Gotchas

- Share/export may require network entitlements. Skip with reason when the account cannot share.
- Thumbs controls are easy to miss in dense transcripts; scroll the target turn into view first.
