# Orchestrate run 20260522-035008 — structural blocker

**Run:** `/orchestrate 181`, runId `20260522-035008`, umbrella `orchestrate/umbrella-20260522-035008`.
**Status:** Wave 0 implementers ran; run halted on a foundational defect.

## New defect discovered (NOT in the PRD #181 backlog)

**Orchestrate subagents are granted capability MCP tools under the wrong name.**

The bundled subagent definitions (`plugins/orchestrate/agents/{investigator,implementer,reviewer,conflict-resolver}-{standard,deep}.md`) declare in frontmatter:

```
tools: Read, Edit, Write, Grep, Glob, mcp__orchestrate__run_tests, mcp__orchestrate__run_typecheck, mcp__orchestrate__run_build, mcp__orchestrate__run_lint
```

But the orchestrate plugin's MCP server registers its tools under `mcp__plugin_orchestrate_orchestrate__*` (e.g. `mcp__plugin_orchestrate_orchestrate__run_tests`). The `mcp__orchestrate__*` names in the agent frontmatter match nothing, so every spawned subagent receives **only** `Read, Edit, Write, Grep, Glob` — no capability tools.

Confirmed independently by the #186, #189, and #200 implementer subagents, all of which reported `run_tests`/`run_typecheck`/`run_build` unavailable.

### Impact

- Subagents cannot run tests, typecheck, or build. The `/tdd` red-green contract cannot execute inside the sandbox even with `.orchestrate/commands.json` wired — the wiring is correct, but the subagents can't reach the tools.
- Subagents touching `orchestrate-mcp/src/**` cannot regenerate the committed `dist/` bundle (no `run_build`).
- The implementer for #189 returned `status: blocked` solely because of this — a false failure.

Present in both the repo (`plugins/orchestrate/agents/`) and the installed cache (`~/.claude/plugins/cache/agent-engineering-toolkit/orchestrate/1.0.3/agents/`).

## Wave 0 slice states (source work on disk, all UNVERIFIED)

| Issue | Result | Notes |
|-------|--------|-------|
| #186 | completed | new `src/project-detector.ts` + test; CONTEXT.md, README.md. No dist change (module not yet imported by an esbuild entry). |
| #187 | no envelope (hit account session limit) | `partition-backlog.ts` + test created; index.ts, SKILL.md, CONTEXT.md modified. |
| #189 | blocked | envelope.ts + test, 8 agent files, SKILL.md, index.ts, worktree.ts, README, CONTEXT.md. **Scope creep:** also bumped plugin.json / marketplace.json versions (that is #198's job). |
| #190 | completed | 8 agent files (advisor policy in `## Boundaries`), CONTEXT.md. |
| #191 | no clean envelope (fragment) | `run-dir.ts` + test created; render.ts, context-watchdog.ts, spawn-successor.ts, index.ts, 3 test files, SKILL.md modified. |
| #200 | completed | git.ts fix + 2 test files. dist/ NOT rebuilt. |
| #203 | completed | new CI workflow `.github/workflows/orchestrate-mcp-dist-check.yml`, README. |

## Cross-slice file overlap (umbrella-merge conflict risk)

- `src/index.ts` — modified by #187, #189, #191
- `SKILL.md` — modified by #187, #189, #191
- `CONTEXT.md` — modified by #186, #187, #189, #190
- 8 agent definition files — modified by #189 AND #190

Wave 0 slices were assumed independent; they are not.
