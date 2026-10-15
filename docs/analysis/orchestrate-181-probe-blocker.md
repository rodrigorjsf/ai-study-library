# Probe blocker — orchestrate subagents cannot call capability MCP tools

**Created:** 2026-05-22
**Context:** Step A empirical probe from `docs/handoffs/HANDOFF_ORCHESTRATE_181_05_22_restart.md`, run before restarting `/orchestrate 181`.
**Verdict:** The restart is blocked. PR #205 (orchestrate 1.0.4) fixed the capability-tool namespace but did **not** make the tools reachable from spawned subagents. This is a deeper defect than #204.
**Filed as:** #206 (`bug`, `ready-for-agent`, Parent PRD #181).

---

## What was tested

Per handoff Step A: create a throwaway worktree, spawn an `orchestrate:implementer-standard` subagent (model sonnet) using the same definition the real run uses, and have it call a capability MCP tool against that worktree.

- Probe worktree: `/tmp/orch-probe-181` (detached HEAD at `development` tip `43a551a`), `npm ci`'d in `plugins/orchestrate/orchestrate-mcp/`.
- Plugin version in cache and loaded: orchestrate **1.0.4** — `~/.claude/plugins/cache/agent-engineering-toolkit/orchestrate/1.0.4/agents/` has zero stale `mcp__orchestrate__` and all 8 agent defs carry the corrected `mcp__plugin_orchestrate_orchestrate__*` namespace.

## Empirical findings, in priority order

1. **The main session CAN call the capability tools.** The orchestrator called `mcp__plugin_orchestrate_orchestrate__run_tests` with `repoPath: /tmp/orch-probe-181` and got:
   ```
   {"status":"passed","capability":"tests","command":["npm","--prefix","plugins/orchestrate/orchestrate-mcp","run","test"],"exitCode":0, ... "Tests  161 passed (161)"}
   ```
   → The MCP server is live, the namespace `mcp__plugin_orchestrate_orchestrate__*` is correct, and `.orchestrate/commands.json` is wired correctly.

2. **The 1.0.4 agent definition on disk is correct.** `agents/implementer-standard.md` frontmatter:
   `tools: Read, Edit, Write, Grep, Glob, mcp__plugin_orchestrate_orchestrate__run_tests, mcp__plugin_orchestrate_orchestrate__run_typecheck, mcp__plugin_orchestrate_orchestrate__run_build, mcp__plugin_orchestrate_orchestrate__run_lint`
   → #204's namespace fix shipped correctly.

3. **The spawned subagent lists the 4 capability tools verbatim in its grant.** Asked for its literal tool list, the subagent returned:
   ```
   mcp__plugin_orchestrate_orchestrate__run_typecheck
   mcp__plugin_orchestrate_orchestrate__run_build
   mcp__plugin_orchestrate_orchestrate__run_tests
   mcp__plugin_orchestrate_orchestrate__run_lint
   ```
   → The subagent's frontmatter resolved; the process is running 1.0.4, not a stale 1.0.3.

4. **The subagent's actual call FAILS.** Calling `mcp__plugin_orchestrate_orchestrate__run_tests` with `repoPath: /tmp/orch-probe-181` returned, verbatim:
   ```
   Error: No such tool available: mcp__plugin_orchestrate_orchestrate__run_tests
   ```
   → The granted tool name is **listable but not callable** inside a spawned subagent. The plugin's MCP server transport is connected for the main session but is **not propagated into the subagent's runtime**.

## Conclusion

#204's namespace fix was **necessary but not sufficient**. The orchestrate plugin's core design — implementer/reviewer/conflict-resolver subagents self-verify their slice via the capability MCP tools (`run_tests` / `run_typecheck` / `run_build` / `run_lint`) — rests on a tool propagation that does not happen. Every spawned subagent can name the tools but cannot invoke them. No slice can self-verify. The restart of `/orchestrate 181` cannot proceed until this is resolved.

## Supporting research (inference, NOT verified)

A `claude-code-guide` agent consulted the Claude Code docs and concluded plugin MCP servers attach to the main session only and do not propagate to subagents, with no documented configuration to change this. **This is the agent's inference, not a direct documentation quote** — the docs do not explicitly cover subagent access to plugin MCP tools. Treat it as a plausible explanation to verify, not as ground truth. The probe above is the ground truth.

## Path forward — open, for the user to decide

The fix approach is deliberately not pre-committed here. Candidates:

- **A — Main-thread verification.** Redesign orchestrate so the orchestrator (main session, which *can* call the tools) verifies each slice worktree after the implementer returns, instead of subagents self-verifying. Substantive redesign across the orchestrate skill and all 8 agent definitions.
- **B — MCP scope workaround.** Empirically test whether declaring the MCP server at project scope (`.mcp.json` at the worktree root) or user scope makes the tools callable from subagents. Cheap to probe; may not work; has plugin-portability implications.
- **C — Manual resolution.** Abandon `/orchestrate` for PRD #181 and resolve the 14 issues manually. Foreclosed by the active goal, which requires all orchestrate-plugin problems resolved before PRD #181 can be declared done.

---

## Probe result — scope is NOT the lever; root cause re-diagnosed (2026-05-22)

Per `docs/handoffs/HANDOFF_ORCHESTRATE_206_05_22_scope_probe.md`, the project-scope workaround was probed empirically — followed by a control test that **overturns the original #206 conclusion**.

### Test 1 — project-scope call (the planned probe)

**Setup.** A `.mcp.json` at the repo root registered the test server `orch-test` at **project scope** — the same `dist/index.js` binary as the plugin's `orchestrate` server, only the registration scope changed (plugin → project). A vanilla `general-purpose` subagent (model sonnet, no `tools:` restriction) was spawned and asked to call the project-scope server's `run_tests`.

**Result.** The spawned subagent called `mcp__orch-test__run_tests` and received a real `{"status":"passed", ... "Tests  161 passed (161)"}`.

### Test 2 — plugin-scope call, SAME runtime (the control)

The same subagent process was resumed and asked to call the **plugin-scope** `mcp__plugin_orchestrate_orchestrate__run_tests` with the same `repoPath`.

**Result.** It also received a real `{"status":"passed", ... "Tests  161 passed (161)"}`. `CONTROL: plugin-scope CALLABLE`.

### Test 3 — real `orchestrate:implementer-standard`, restricted frontmatter

To isolate the `tools:` restriction, the **actual** `orchestrate:implementer-standard` agent (model sonnet) was spawned as a read-only diagnostic — same restricted `tools:` allow-list the real run uses — and asked to call the plugin-scope `run_tests`.

**Result.** It called `mcp__plugin_orchestrate_orchestrate__run_tests` and received a real `{"status":"passed", ... "Tests  161 passed (161)"}`. The agent's reported environment:

- Tool inventory contained the four `mcp__plugin_orchestrate_orchestrate__*` capability tools directly.
- `ToolSearch` was **not** in its inventory.
- **"no deferred-tools reminder present"** — its MCP tool schemas were loaded, not deferred.

### Conclusion — #206 does NOT reproduce; root cause still unconfirmed

All three probes run this session **pass**. The blocker doc's keystone finding #4 (`Error: No such tool available` from an `implementer-standard` subagent) **could not be reproduced**. Restricted `tools:` frontmatter is **not** the blocker either — the real `implementer-standard` lists the MCP tools *and* calls them.

| Probe (this session) | Subagent | Result |
|---|---|---|
| Test 1 | `general-purpose`, project-scope server | `passed`, 161 tests |
| Test 2 | `general-purpose`, plugin-scope server | `passed`, 161 tests |
| Test 3 | `orchestrate:implementer-standard`, plugin-scope server | `passed`, 161 tests |
| Blocker doc #4 (prior session) | `orchestrate:implementer-standard`, plugin-scope server | `Error: No such tool available` |

**Candidate hypothesis (UNVERIFIED) — tool-schema deferral.** The harness defers tool schemas in large-catalog contexts: a deferred tool's *name* is visible but its schema is unloaded, so a direct call fails. Recovery requires `ToolSearch`. This matches the blocker doc's exact signature — finding #3 (subagent *lists* the tools) + finding #4 (the *call* fails) = name-visible-but-uncallable. No orchestrate agent grants `ToolSearch`. In this session, Test 3's `implementer-standard` had a small, **non-deferred** catalog, so the failure mode did not arise.

This is the strongest available explanation but it is **not proven**: the deferred-subagent state could not be triggered on demand, so the mechanism cannot be confirmed and no red regression test can be written for it. The worktree-vs-main-repo difference was ruled out — `No such tool available` is a tool-registration error fired before `repoPath` is read.

**Hyphen namespacing.** `orch-test` resolved as `mcp__orch-test__*` (hyphen preserved), not `mcp__orch_test__*`.

**Cleanup done.** The `orch-test` server was removed (`claude mcp remove orch-test --scope project`) and the leftover empty `.mcp.json` deleted. No probe artifact remains.

## Path forward — re-opened for the user to decide

The "investigate + fix" path assumed a reproducible bug. #206 does not reproduce. No root cause is confirmed; no red test can be written. Three real options, none pre-committed:

- **Close #206 as not-reproducible**, then attempt the `/orchestrate 181` restart to confirm the run actually works now. Fastest path to unblocking PRD #181.
- **Ship a defensive `ToolSearch` grant** on the orchestrate agents so a future deferred-tools environment stays recoverable — but with no red test, this needs an explicit TDD-rule waiver, and `ToolSearch`'s validity as a grantable `tools:` entry is itself unverified.
- **Pause and architect a reliable reproduction** of the deferred-subagent state, then resolve #206 under proper TDD. Highest rigor, slowest.
