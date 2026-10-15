# Research Brief — Issue #191: orchestrate per-run directory layout

_Produced by an opus-deep investigator during run 20260522-035008 (aborted). Saved for reuse by the restart so the investigator pass need not be repeated. Line numbers were valid against `development` tip `d37ad16`; PR #205 touches only the agent-file `tools:` frontmatter line, so the cited `src/` and `SKILL.md` ranges remain valid._

## relevantFiles

- `plugins/orchestrate/orchestrate-mcp/src/tools/render.ts` — `render_dashboard/graph/report`; flat ephemeral paths.
- `plugins/orchestrate/orchestrate-mcp/src/hooks/context-watchdog.ts` — watchdog reads run-state, writes context-flag flat.
- `plugins/orchestrate/orchestrate-mcp/src/hooks/context-watchdog-cli.ts` — hook entry; receives only `transcript_path` + `cwd` on stdin.
- `plugins/orchestrate/orchestrate-mcp/src/tools/spawn-successor.ts` — successor launcher; today touches no ephemeral path.
- `plugins/orchestrate/orchestrate-mcp/src/index.ts` — tool registration; `renderInputSchema`/`spawnSuccessorInputSchema` wired here.
- `plugins/orchestrate/orchestrate-mcp/src/handoff-config.ts` — `loadHandoffConfig`; `handoff.json` stays flat (the pattern model for a new resolver).
- New file: `plugins/orchestrate/orchestrate-mcp/src/run-dir.ts` (resolver — see approach).
- Tests: `test/render.test.ts`, `test/context-watchdog.test.ts`, plus new `test/run-dir.test.ts`.
- `plugins/orchestrate/skills/orchestrate/SKILL.md`, `references/run-state.md`, `references/context-handoff.md`.
- `plugins/orchestrate/README.md`, `CONTEXT.md`.

## Where flat ephemeral paths are resolved today

- render.ts — `ARTIFACT_DEFAULTS` (lines 89-93: `.orchestrate/dashboard.html|graph.html|report.html`); `readAndValidateRunState` builds `path.join(repoPath, ".orchestrate", "run-state.json")` (line 146); `artifactPath` defaults at lines 762, 781, 800.
- context-watchdog.ts — `runStatePath` (line 182), `flagPath` = `.orchestrate/context-flag.json` (line 197), flag write (lines 234-235), `ContextFlag` interface (lines 158-165).
- context-watchdog-cli.ts — line 38 passes only `cwd`; there is no `runId` surface on the hook event today.
- spawn-successor.ts — lines 204-205 use only `repoPath`; it loads `handoff.json` (config, stays flat). It does not resolve an ephemeral path.

`run-state.json` and `context-flag.json` are computed independently by each consumer via inline `path.join` — there is no shared path module. `commands.json`, `routing.json`, `handoff.json` resolve the same way and must stay flat.

## patterns

- Each tool file: `z.object` schema is the single source of truth, TS types via `z.infer`; discriminated `status: "ok"|"error"` with `errorCode` enum; pure functions separated from I/O; "never throws — structured result" convention.
- Tests use vitest (`describe/it/expect/afterEach`); `fs.mkdtempSync(path.join(os.tmpdir(), "orchestrate-<x>-"))` scaffolding, a `created[]` array cleaned in `afterEach`, a `project()` helper. Mirror this for the resolver tests.
- `loadHandoffConfig(repoPath)` (handoff-config.ts) is the model shape for a resolver: a small pure function taking `repoPath`, returning structured data, never throwing.
- `dist/` is committed; `npm run build` (esbuild) must run after any `src/` change.

## risks

- Path-isolation invariant: the resolver must reject `runId` values containing `/`, `\`, `..`, or a leading `.` — otherwise two ids could escape into a shared/parent path. Make `runId` validation part of the resolver.
- context-watchdog runId discovery (blocking design decision): the hook event carries only `transcript_path` + `cwd` — no `runId`. Decide how the watchdog learns the active run: scan `.orchestrate/runs/*/run-state.json` for the `in-progress` one, or read a top-level pointer file. ADR-0008's driver-session matching is a separate slice (#196) — do not pull it in. Keep the watchdog's safe no-op behavior.
- Resume discovery in SKILL.md: section 1 currently reads one flat `run-state.json`. With per-run dirs the skill must discover which `runs/<runId>/` to resume. Decide and document; do not absorb `/orchestrate <PRD#>` partitioning (sibling issue #195).
- spawn_successor `runId`: it needs a `runId` so the successor resumes the correct run — likely threaded into `resumePrompt`.
- `render_*` precedence: when both `runId` and an explicit `outputPath` are passed, explicit `outputPath` should win.
- Backward compatibility: existing `test/render.test.ts` and `test/context-watchdog.test.ts` write flat `.orchestrate/run-state.json` fixtures — they need updating to the per-run layout.

## approach

1. Create `src/run-dir.ts` — a `resolveRunPaths(repoPath, runId)` returning `{ runDir, runStatePath, contextFlagPath, dashboardPath, graphPath, reportPath }`, all under `.orchestrate/runs/<runId>/`. Validate `runId` (reject traversal chars). Keep config-file paths out of this module.
2. TDD the resolver first (`test/run-dir.test.ts`): valid mapping, two distinct ids never share a path, rejection of malicious ids.
3. Thread `runId` through `render_*` — add `runId` to `renderInputSchema`; route `readAndValidateRunState` and artifact-default paths through the resolver; keep explicit `outputPath` override winning.
4. Thread `runId` through context-watchdog — resolve `runStatePath` + `flagPath` via the resolver; resolve the discovery question for `context-watchdog-cli.ts`.
5. `spawn_successor` — accept `runId` and propagate it so the successor resumes the right run.
6. Update SKILL.md + references to read/write per-run paths, including the resumed-run path.
7. Update docs, then `npm run build`, then version bumps.

## notes

- SKILL.md ephemeral-path mentions to update: lines 73, 78, 135, 181-186, 202-207, 343-353, 405. Config-file mentions (54, 104) stay.
- run-state.md: lines 1-7 ("lives at `.orchestrate/run-state.json`") and 90. context-handoff.md: lines 5, 13, 22, 24, 30, 50.
- README.md: `.gitignore` snippet lines 112-114 (`.orchestrate/run-state.json` / `context-flag.json` / `*.html`) must become `.orchestrate/runs/`; lines 24, 32, 95, 202 mention `run-state.json`.
- CONTEXT.md glossary already defines "Run directory" (lines 136-138) from ADR-0008 — verify the shipped layout matches it, do not re-author.
- ADR-0008 (`docs/adr/0008-*.md`) is the design rationale; concurrent-run watchdog binding and cleanup are explicitly other slices (#196, #197).
