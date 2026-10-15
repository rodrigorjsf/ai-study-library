# Software factory

A study of four approaches to agent-driven software delivery, and of how they could combine into one harness. Written 2026-10-11.

A **software factory** is a pipeline that takes a feature request in and puts a merged change out, with agents doing the work between the deterministic steps.

> **The project these studies led to** lives in its own repository: `~/Workspace/software-factory` (GitHub: `rodrigorjsf/software-factory`). It holds a read-only snapshot of these studies, taken on 2026-10-11, plus the proposed scope and the open questions. Correct a study here, then copy it there again.

## Reading order

| # | Document | What it covers |
|---|---|---|
| 01 | [ZazenCodes — software factory](01-zazencodes-software-factory.md) | One skill, seven subagents, files as state, an auto-merge gate, a dashboard. The history of the term. |
| 02 | [Austin Marchese — harness engineering](02-austin-marchese-harness-engineering.md) | The base-harness / domain-harness split, eight components, interface and feedback as design objects. |
| 03 | [Matt Pocock — skills v1.3](03-matt-pocock-skills-v1-3.md) | Grilling, glossary, spec, tracer-bullet tickets, TDD, two-axis review, `pr`, `retro`, and the writing theory behind them. |
| 04 | [The `/run-spec` flow](04-run-spec-flow.md) | The local oracle-driven AFK flow, and where it has drifted from upstream. |
| 05 | [Unified factory study](05-unified-factory-study.md) | The comparison, the design principles, a combined pipeline, and the open questions. **Start here if you only read one.** |
| 06 | [Prototyping evidence](06-prototyping-evidence.md) | What the literature supports about prototyping before building, what is folklore, what is unknown for coding agents, and the verdict for the factory. |
| 07 | [Wayfinder assessment](07-wayfinder-assessment.md) | Wayfinder in full: its ticket types and vocabulary, its documented failure modes, and what the factory should adopt or guard against. |
| 08 | [Guardrails](08-guardrails.md) | What a guardrail is, the principles the sources agree on, the threats to an agent that ships code, the evidence on how well guardrails work, what Claude Code enforces and does not, and a six-layer design for the factory. |

## Primary material

- [transcripts/](transcripts/) — six videos, from YouTube's English auto-captions, with timestamps every ~30 seconds. Unedited: names are sometimes mis-heard ("Carpathy", "clawed code").

| Transcript | Video |
|---|---|
| [zazencodes-ai-software-factory-claude-code.md](transcripts/zazencodes-ai-software-factory-claude-code.md) | ZazenCodes, "Build Your Own AI Software Factory with Claude Code" (2026-10-07) |
| [matt-pocock-skills-v1-3.md](transcripts/matt-pocock-skills-v1-3.md) | Matt Pocock, "New Skills! v1.3 brings /pr, /implement-spec, and /retro" (2026-10-05) |
| [austin-marchese-harness-engineering.md](transcripts/austin-marchese-harness-engineering.md) | Austin Marchese, "Stop Prompting Claude. Start Harness Engineering." (2026-10-09) |
| [austin-marchese-loop-engineering.md](transcripts/austin-marchese-loop-engineering.md) | Austin Marchese, "Stop Prompting Claude. Start Loop Engineering." (2026-06-19) |
| [austin-marchese-stanford-graph-method.md](transcripts/austin-marchese-stanford-graph-method.md) | Austin Marchese, "Stanford's Graph Method Explained" (2026-08-20) |
| [austin-marchese-karpathy-method.md](transcripts/austin-marchese-karpathy-method.md) | Austin Marchese, "How to 10x Your Claude Code Projects (Karpathy's Method)" (2026-04-24) |

## Related

- [Claude 5.5 model selection](../models/claude-5-5-model-selection.md) — which model and effort for which factory role.
- [State of practice, October 2026](../analysis/state-of-practice-2026-10.md) — what in this library still holds and what does not.
- [harness-engineering/](../harness-engineering/), [spec-driven-development/](../spec-driven-development/), [agentic-engineering/](../agentic-engineering/) — earlier captured articles on the same themes.

## How the transcripts were made

YouTube already publishes captions, so no audio was transcribed. `youtube-transcript-api` fetched the English auto-generated track for each video, and a short script grouped the segments into ~30-second paragraphs:

```bash
uvx --from youtube-transcript-api youtube_transcript_api <video-id> --languages en --format json > <video-id>.json
```

`yt-dlp --write-auto-subs` returned HTTP 429 for two of the three videos on this machine. A local Whisper model (the route the `studio` project's `transcrever.py` takes, with word-level timing) is the fallback for a video with no captions; it needs `ffmpeg` and a ~1.6 GB model, neither of which was required here.
