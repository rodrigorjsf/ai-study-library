# Prompt box

The prompt input for an active thread: mode and model, mentions, attachments, history, and submit.

## Sub-features

- mode-pill: switch Ask / Agent / Plan (or product-equivalent modes).
- model-pill: pick the model for this turn.
- mentions: `@` file, folder, thread, or doc mentions that attach context.
- attachments: image and file chips above the prompt.
- prompt-history: up/down through prior prompts for this thread.
- voice-input: gated mic control that inserts a transcript.
- submit-chords: Enter vs Cmd/Ctrl+Enter depending on the Submit with Cmd+Enter setting.
- slash-commands: editable slash commands that expand into prompts or git actions.

## How to get to it (user POV)

Focus the prompt at the bottom of the session panel. Click the mode or model pill to change either. Type `@` to open mentions. Drop or attach files. Press the configured submit chord to send.

## Driving it with control-atlas

```bash
node .cursor/skills/verify-atlas/control-atlas.mjs type "summarize @README"
node .cursor/skills/verify-atlas/control-atlas.mjs press "Enter"
node .cursor/skills/verify-atlas/control-atlas.mjs wait-settle
```

- Prompt root: `[data-component="prompt-box"]` (or the live equivalent from `snapshot`).
- Mode cycle with prompt focus: `press "Shift+Tab"` when the feature supports it; otherwise click the mode pill.
- Mentions: `type "@READ"` then `press "Enter"` on the selected row. Assert a mention chip before submit.
- Images: `upload-image /path/to/fixture.png` rather than OS drag. File context: `add-context path/to/file`.
- Submit: `send "..."` for the default chord; pass `--meta` when Submit with Cmd+Enter is enabled.

## Gotchas

- Prompt focus is required for mode cycling and history. Click the editor if a previous action stole focus.
- Mention menus are async; snapshot the live rows before choosing.
- OS drag of Finder/Explorer files is manual. Use `upload-image` / `add-context` and mark native drag as a gap.
