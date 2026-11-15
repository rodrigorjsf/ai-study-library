# Live replies and tool cards

How a reply streams into the thread: assistant text, thinking, tool cards, and abort.

## Sub-features

- assistant-stream: token stream into the latest AI bubble.
- thinking-bubble: optional collapsed reasoning region.
- tool-call-cards: inline cards for edits, shell, fetch, and similar tools with status.
- abort-turn: stop the in-flight turn from the UI or chord.
- edit-review / terminal-review: review surfaces for proposed edits and command output.

## How to get to it (user POV)

Send a prompt that triggers tools. Watch the AI bubble grow, tool cards flip through status, then settle. Click Stop (or the abort chord) to cancel mid-turn.

## Driving it with control-atlas

```bash
node .cursor/skills/verify-atlas/control-atlas.mjs send "run the project tests and summarize failures"
node .cursor/skills/verify-atlas/control-atlas.mjs wait-settle
node .cursor/skills/verify-atlas/control-atlas.mjs snapshot
```

- Assert messages with `data-message-id` plus both `data-message-role` and `data-message-kind`. Do not count raw AI-role rows; tool rows may share a role attribute.
- Tool status: wait on `data-tool-status` values (`running` → `done` / `error`), not fixed sleeps.
- Abort: click the Stop control or press the registered abort chord while streaming, then assert no further tokens and a visible cancelled state.

## Gotchas

- Streaming is non-deterministic. `wait-settle` is mandatory.
- Thinking bubbles may be absent depending on model and settings; snapshot before asserting.
- Abort mid-tool can leave a partial card; that is expected. Assert cancelled, not clean success.
