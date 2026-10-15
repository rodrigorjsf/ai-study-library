# Research Brief — Issue #189: Subagent result envelope with git-status fallback

_Produced by an opus-deep investigator during run 20260522-035008 (aborted). Saved for reuse by the restart so the investigator pass need not be repeated. Line numbers were valid against `development` tip `d37ad16`; PR #205 touches only the agent-file `tools:` frontmatter line, so the cited `src/` and `SKILL.md` ranges remain valid._

## 1. relevantFiles

**Subagent role definitions (8 files — all need an envelope contract):**
- `plugins/orchestrate/agents/investigator-{standard,deep}.md` — return section "Return a structured brief" with fields `relevantFiles`, `patterns`, `risks`, `approach`, `notes` (standard: lines 58-71).
- `plugins/orchestrate/agents/implementer-{standard,deep}.md` — "Return a structured summary": `status` (`completed`/`blocked`), `filesChanged`, `verification`, `notes` (standard: lines 55-67; deep: lines 76-88 — structures are identical across variants).
- `plugins/orchestrate/agents/reviewer-{standard,deep}.md` — `status` (`passed`/`failed`), `filesChanged`, `verification`, `notes` (standard: lines 67-76).
- `plugins/orchestrate/agents/conflict-resolver-{standard,deep}.md` — `status` (`resolved`/`failed`), `filesChanged`, `verification`, `notes` (standard: lines 53-63).

**MCP server (where the validator + worktree-fallback belong):**
- `plugins/orchestrate/orchestrate-mcp/src/tools/` — new tool file(s); mirror `worktree.ts` / `run-command.ts`.
- `plugins/orchestrate/orchestrate-mcp/src/index.ts` — register new tools (pattern at lines 117-198); bump `version` at line 65.
- `plugins/orchestrate/orchestrate-mcp/src/git.ts` — exposes `gitExecFile`; no git-status helper exists.
- `plugins/orchestrate/orchestrate-mcp/test/` — new vitest file(s).

**Skill + docs:**
- `plugins/orchestrate/skills/orchestrate/SKILL.md` — consumption points (see section 2).
- `plugins/orchestrate/README.md` (lines 38, 59 mention return contract) and `CONTEXT.md` (glossary `### Orchestrate run vocabulary`, lines 126-150).

## 2. How the orchestrator consumes subagent output today (all prose-parsed)

SKILL.md section 3 has four prose-parsing points the envelope must replace:
- Step 4 (lines 237-243): reads implementer `blocked` status + `filesChanged`.
- Step 5 (lines 244-248): reads reviewer `failed` status + `filesChanged`.
- Step 6 (lines 249-265): stages the union of implementer + reviewer `filesChanged`.
- Step 8a (lines 312-324): reads conflict-resolver `resolved`/`failed` status.

Investigator's brief (step 3) is passed verbatim to the implementer — lower-stakes but should still be enveloped for consistency.

## 3. Schema + validator pattern to mirror

`run-command.ts` and `worktree.ts` are the canon: zod `z.object` is the single source of truth, TS types via `z.infer` (run-command.ts:30-31, 144-148). Every schema field carries a `.describe()`. Outputs are discriminated by a `status` enum; never throw. Reuse:
- `parsePorcelainZ` (`worktree.ts:457-481`) — already parses `git status --porcelain -z` into real path strings, handles renames. The worktree-fallback tool should reuse it directly.
- The fallback runs `gitExecFile(["status", "--porcelain", "-z", "--untracked-files=all"], worktreePath)` then `parsePorcelainZ` — same shape as `removeWorktree` (worktree.ts:397-413).

## 4. Test conventions (`orchestrate-mcp/test/`)

vitest; `describe`/`it`/`expect`/`afterEach`. Temp dirs via `fs.mkdtempSync(path.join(os.tmpdir(), "orchestrate-..."))`; a `created[]` array + `afterEach` `rmrf` for cleanup (run-command.test.ts:40-53). A `makeProject`/`project` helper builds fixtures. worktree.test.ts shows real-git-repo fixtures (`createTempRepo`). Tests cover every `status`/`errorCode` branch. Route through `/tdd`.

## 5. Central design decision (surface, do not pre-decide)

AC says "the orchestrator never parses subagent prose" and "envelope format is the implementer's choice." The orchestrator is the Claude Code LLM session running SKILL.md, not the MCP server. Two readings:
- Strict: the validator + worktree-fallback must be new MCP tools (e.g. `validate_envelope`, `list_changed_files`) — only a tool boundary truly removes LLM prose-parsing.
- Loose: a fenced-JSON envelope the orchestrator-LLM extracts per SKILL.md instructions still satisfies "machine-checkable."

Recommended: the MCP-tool route — it is the only enforceable interpretation, fits the existing "every capability is a tool" architecture, and is independently testable via vitest (the loose route has no test surface). The implementer should confirm this reading.

## 6. risks

- Identical variant pairs: all 8 agent files must change in sync — `-standard`/`-deep` share the return structure today; a divergence would break routing.
- `dist/` is committed: run `npm run build` after any `src/` change — vitest tests `src/`, so green tests do not prove the shipped bundle.
- Step 8a is easy to forget — it is a separate prose-parse point from step 6.
- Truncation detection: a truncated fenced JSON block is invalid JSON → already caught by `JSON.parse`; a truncated tool-call return is harder — the validator must treat a partial/missing required field as invalid, never silently accept.
- Fallback fidelity: worktree `git status` includes untracked build artifacts. The fallback's recovered file set may be a superset of the real change set; SKILL.md's "never `git add -A`" warning stays load-bearing.
- `README.md` line 59 ("Every tool returns a discriminated `status`") — new tools must conform.

## 7. approach

1. `/tdd`: write the envelope zod schema(s) + a `validateEnvelope` function in a new `src/tools/` file (valid / truncated-or-partial / missing → discriminated result). Mirror run-command.ts schema style.
2. Add the worktree-fallback tool (`list_changed_files` or similar): `gitExecFile` status + reuse `parsePorcelainZ`. Discriminated `status` output.
3. Register both in `index.ts`; bump server `version`.
4. Update all 8 agent `.md` files: replace the free-form "What you return" with the defined envelope (a fenced JSON block matching the schema).
5. Update SKILL.md steps 4, 5, 6, 8a to call the validator and, on missing/invalid, the worktree-fallback tool; state the orchestrator never reads prose for status/files.
6. Update `README.md` and add a `CONTEXT.md` glossary entry (e.g. "Result envelope") in the `### Orchestrate run vocabulary` section.
7. `npm run build` to refresh `dist/`.

## notes

- No git-status helper exists in `src/`; `git.ts` only exposes `gitExecFile`, `optionInjectionError`, `cleanGitError`, `GitExecError`.
- index.ts has a documented TS2589 SDK workaround (`AnyToolHandler` cast) — new tools must follow the same `ToolHandler` → `as unknown as AnyToolHandler` registration pattern (index.ts:76-115).
- Keep `CONTEXT.md` glossary entries in the established format.
- Commit atomically by concern (schema/tool, agent defs, SKILL.md, docs as separate commits).
