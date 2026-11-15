# Multi-surface journeys

Journeys that span several features. Per-surface selectors live in the linked files; read those first, then sequence the journey. Baseline preconditions in [the feature-map README](README.md) apply.

## Multi-thread isolation

Two threads live at once must not corrupt each other.

- Submit a long prompt in thread A. While A streams, switch to thread B and submit there. Switch back to A. A keeps streaming, B is unaffected, and each keeps its own conversation state and scroll position.
- Verify with rows keyed by `data-message-id` and classified by both `data-message-role` and `data-message-kind`. Drive switching from the left rail as in `session-rows.md`.

## Optimistic cloud create + queue

- Select a cloud target, submit the first prompt, then immediately submit a follow-up before the server returns. The follow-up enters the queued-messages tray.
- The client may preassign an id before the create RPC. If the server returns a different id, the follow-up still submits exactly once. Assert it is neither dropped nor duplicated in human-role messages.

## Power-user shortcut sweep

Run the global chords as one pass from the focus contexts each feature file supports. Confirm the selected thread and prompt draft survive.

- `left-rail.md`: Cmd/Ctrl+B
- `split-view.md`: app panes + tile chords (context-sensitive)
- `file-browser.md`, and other app files: direct app shortcuts
- `preferences.md`: inside settings, Cmd/Ctrl+K is preferences search
- `prompt-box.md`: Shift+Tab mode cycling with prompt focus

## Drag and drop across surfaces

Real OS and browser drag sources need native input. Keep those paths manual. Internal sidebar and tiling drags are also not first-class in the sample driver.

- Do not count `upload-image` / `add-context` / split chords as drag coverage.
- Mark the precise gap: which surface, which source, which target.
