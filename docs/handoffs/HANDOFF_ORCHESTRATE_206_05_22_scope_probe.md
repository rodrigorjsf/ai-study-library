# Handoff: project-scope MCP propagation probe (#206)

**Created:** 2026-05-22
**Supersedes:** `HANDOFF_ORCHESTRATE_181_05_22_restart.md` — its plan ("restart `/orchestrate 181`") is invalid; the restart is blocked by #206.
**Goal of next session:** run ONE empirical probe, report the binary outcome, then stop for a user decision. Do **not** restart `/orchestrate 181`.

---

## Why a restart is needed

`/orchestrate 181` was blocked by **#206**: spawned subagents list the capability MCP tools in their grant but cannot call them (`Error: No such tool available`). The plugin's MCP server transport connects to the main session only and does not propagate into subagent runtimes. Full evidence: `docs/analysis/orchestrate-181-probe-blocker.md`.

The user chose to test a workaround: does an MCP server registered at **project scope** (rather than plugin scope) become callable from a spawned subagent? MCP config is read at session boot, so this requires a fresh session.

## State left for the next session

- `/.mcp.json` exists at the repo root, declaring a project-scope test server **`orch-test`** — same `dist/index.js` as the plugin's `orchestrate` server, registered at project scope instead of plugin scope. **Untracked. Do NOT commit it** — it is a probe artifact.
- On session start, Claude Code will prompt to trust the project MCP server. **Approve `orch-test`** when prompted, or the probe cannot run.
- `development` tip: `43a551a`. No `run-state.json` (no run in progress). Probe worktree already cleaned up.
- Issue **#206** open (`bug`, `ready-for-agent`, Parent PRD #181).

## The probe — run exactly this, change nothing else

Spawn a **`general-purpose`** subagent (model **sonnet**) — vanilla, no `tools:` restriction, so the only variable under test is MCP scope. Prompt it to:

1. List verbatim every tool name it can see containing the substring `orch` (captures both `mcp__orch*test__*` test-server tools and the plugin's `mcp__plugin_orchestrate_orchestrate__*` tools). Note: the exact namespacing of the hyphen in `orch-test` is unknown — it may render as `mcp__orch-test__*` or `mcp__orch_test__*`. Take the name from the subagent's reported list.
2. Call the `orch-test` server's `run_tests` tool with `repoPath: "/home/rodrigo/Workspace/agent-engineering-toolkit"` (this repo has `.orchestrate/commands.json` committed and `plugins/orchestrate/orchestrate-mcp/node_modules` installed — `run_tests` should return `status: passed`, 161 tests).
3. Paste the RAW result verbatim — JSON or error string — in a code block.

It is a diagnostic probe: the subagent must not edit files.

## Outcome interpretation — pre-committed

- **PASS** (subagent calls the `orch-test` tool successfully, real `passed`/`failed` status): project scope IS the lever. #206 has a viable fix direction. The next decision — how to ship it without breaking plugin self-containment (orchestrate skill writes a `.mcp.json` at run start? plugin contributes a project `.mcp.json`?) — is a separate design call. **Surface it to the user; do not pick an approach autonomously.**
- **FAIL** (subagent gets `No such tool available` for the `orch-test` tool too): project scope is NOT the lever. Option B is dead. **Escalate to the user** to choose between Option A (main-thread verification redesign) and Option C (manual PRD #181 resolution) from `docs/analysis/orchestrate-181-probe-blocker.md`.

## Cleanup after the probe (either outcome)

- Remove the test server: `claude mcp remove orch-test --scope project` (deletes the root `.mcp.json` entry). Do not leave it registered.

## Active goal (carries forward)

Any new orchestrate-plugin defect found during this work → new GitHub issue (Parent PRD #181, `ready-for-agent`, AFK-triaged), folded into the run. PRD #181 is "done" only when every orchestrate-plugin problem is resolved with tests and documented evidence. #206 is one such problem and must be resolved before the PRD can close.
