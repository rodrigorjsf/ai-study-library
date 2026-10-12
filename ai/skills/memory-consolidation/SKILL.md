---
name: memory-consolidation
description: Spawn the `dreamer` subagent to consolidate a project's memory in the background. Use after a feature, non-trivial fix, ADR/spec decision, or a session with several corrections.
---

# Memory consolidation via the `dreamer` subagent

At the trigger points of the global CLAUDE.md "Memory consolidation" rule (grilling closed, spec/tickets published, ADR created or amended, PR merged, feature or non-trivial fix done, 2+ user corrections) spawn, without asking, the **`dreamer`** subagent to consolidate that project's memory in the background. It runs the same reflective pass as `/dream`, but in an isolated subagent so the main thread stays unblocked.

`dreamer` cannot see the conversation or the working directory, so its spawn prompt must carry fully-resolved, `~`-expanded fields — it stops and reports if any is missing:

- **Scope** — `project`.
- **Memory directory** — `~/.claude/projects/<project-slug>/memory/` as an absolute path (`<project-slug>` = the repo's absolute path with `/` → `-` and a leading `-`).
- **Transcripts source** — that same project directory, `~/.claude/projects/<project-slug>/`, as an absolute path. Its `*.jsonl` files are the transcripts.
- **Current session notes** — a pre-extracted block of the durable signal from this session (the dreamer's only window into it).

- **Project root** (optional) — the repository's absolute path, so the dreamer can read the project's `CLAUDE.md` and check a memory against the file it names.

Use these labels exactly; the dreamer matches on them:

```markdown
Consolidate project memory.

- **Scope:** project
- **Memory directory:** /home/<user>/.claude/projects/<project-slug>/memory/
- **Transcripts source:** /home/<user>/.claude/projects/<project-slug>/
- **Project root:** /absolute/path/to/the/repository

## Current session notes

<what landed, with file paths and commit ids; which existing memories it may make stale;
durable facts the repository does not record; corrections the user made, or "none">
```

The transcripts source is the directory, not a glob: the dreamer lists and searches it itself. In the notes, leave out what the repository already records, and name any decision file so the dreamer can point to it instead of copying it.

Prefer the background `dreamer` during active work; use `/dream --project` for an inline, blocking pass.
