# Transcript

The transcript: sticky-bottom scroll, outline, in-chat find, message navigation, and drafts that survive switching threads.

## Sub-features

- sticky-scroll: stick to bottom while streaming; release on manual scroll-up
- conversation-outline: outline of turns / headings for long threads
- in-chat-find: find within the open transcript
- message-nav: jump previous/next user or assistant turn
- draft-persistence: drafts and queues survive switching threads and return
- cloud-stream-recovery: resume a cloud stream after switching away and back

## How to get to it (user POV)

Open any thread with messages. Scroll the transcript; the jump-to-bottom control appears after you scroll up during a stream.

Open the outline from the session header overflow when the thread is long enough.

Cmd/Ctrl+F focuses in-chat find while the session panel is focused.

## Driving it with control-atlas

```bash
node .cursor/skills/verify-atlas/control-atlas.mjs send "write a long checklist"
node .cursor/skills/verify-atlas/control-atlas.mjs wait-settle
node .cursor/skills/verify-atlas/control-atlas.mjs snapshot
```

Assert messages with `data-message-id` plus both `data-message-role` and `data-message-kind`.

Draft persistence: type an unsent draft, switch threads via the left rail, switch back, assert the draft text.

Cloud recovery: start a cloud turn, switch away mid-stream, switch back, assert the stream resumes without duplicating the human turn.

## Gotchas

- Sticky-bottom is easy to break with a stray wheel event from automation. Prefer `scroll` helpers over raw wheel bursts when proving stickiness.
- In-chat find is not workspace search. Focus context matters.
