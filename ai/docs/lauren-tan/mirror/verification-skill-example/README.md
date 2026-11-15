# verification-skill-example

**Private reference.** Heavily fictionalized example of a project-local verification skill + behavior-level feature map for a large desktop app.

Nothing here is a real product. "Atlas" / "Harbor Labs" / `control-atlas` are made up. The shape is what matters.

## Layout

```text
.cursor/skills/verify-atlas/
  SKILL.md                          # launch, doctor, drive, prove, clean up
  # control-atlas.mjs               # CLI omitted on purpose; usage only in SKILL.md
  references/features/
    README.md                       # index, conventions, sweep order
    *.md                            # one file per feature area (~30)
```

## Why not a wiki?

A wiki is great for humans. Agents pay for every token they reread. A skill + feature map is:

- **Scoped.** Open one feature file for the change under test, not the whole corpus.
- **Actionable.** Each file answers the same four questions: what exists, how a user reaches it, how to drive it with the harness, what usually lies.
- **Sweepable.** `features/README.md` is a top-to-bottom regression order for "did we break the app broadly?"
- **Maintained as code.** Drift gets fixed in the same PR as the UI change, or by a maintain-verification pass.

## How an agent uses it

1. Match the change to one or more feature files.
2. Run `doctor` so the instance is fresh.
3. Drive every reachable entry point the file lists (and the success / cancel / error / empty / persistence paths the change can affect).
4. Capture evidence (screenshot, DOM assertion, clipboard, network, reload round-trip).
5. For broad sweeps, walk the README top to bottom, finish with `multi-surface-journeys.md`.

## Scale

This sample is sized like a large app: ~30 feature files across account/chrome, left rail/sessions, prompt/replies, layout, source control, app panes, hosted/remote, preferences/extensibility, and system UX. Keep entries behavior-level and short enough to run without reading source. Split a file when a section starts needing its own preconditions.

Driver scripts are intentionally omitted. The skill shows the command surface and example invocations only.
