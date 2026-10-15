# Analysis: Claude Hook Reference Doc

> **Status**: Current
> **Source document**: [claude-hook-reference-doc.md](https://docs.anthropic.com/en/docs/claude-code/hooks)
> **Analysis date**: 2025-06-01
> **Scope**: Complete technical reference for the Claude Code hook system — lifecycle events, handler types, decision patterns, and integration with skills, subagents, and MCP

## 1. Executive Summary

The **claude-hook-reference-doc.md** is the definitive technical reference for the Claude Code hook system — the mechanism that allows intercepting, validating, blocking, modifying, and extending agent behavior at specific points in its lifecycle. Unlike the introductory guide (`automate-workflow-with-hooks.md`), this document specifies with pinpoint precision each event, JSON input/output schema, exit codes, decision patterns, and hook types (command, HTTP, prompt, agent).

The hook system represents the most sophisticated implementation of the **deterministic enforcement** principle identified in context optimization research: by converting behavioral instructions into programmatic hooks, we remove rules from the model's attention budget while ensuring their 100% consistent application. The document covers 22 lifecycle events, 4 handler types (command, HTTP, prompt, agent), per-event decision mechanisms, asynchronous hooks, and integration with skills, subagents, worktrees, and MCP.

The richness of this document lies in the level of granular control it exposes: from the ability to modify tool inputs before execution (`updatedInput`), inject additional context into subagents (`SubagentStart.additionalContext`), to programmatically controlling permissions (`PermissionRequest.updatedPermissions`). For anyone building agent infrastructure, this is the document that transforms Claude Code from a passive assistant into a programmable platform.

## 2. Key Concepts and Mechanisms

### 2.1 Hook Lifecycle Architecture

The system operates at three nesting levels:

| Level | Component | Function |
|-------|-----------|----------|
| 1 | **Hook Event** | Lifecycle point (e.g., `PreToolUse`, `Stop`) |
| 2 | **Matcher Group** | Regex filter that determines when to fire |
| 3 | **Hook Handler** | What to execute on match (command/http/prompt/agent) |

### 2.2 The 22 Lifecycle Events

The document categorizes events into functional groups:

**Session Events:**

- `SessionStart` — Session start/resume. Only event with access to `CLAUDE_ENV_FILE` for persisting environment variables.
- `SessionEnd` — Session termination. Default timeout of 1.5s (configurable via `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS`).

**Agentic Loop Events (pre-execution):**

- `UserPromptSubmit` — Before Claude processes the user prompt. Can block or add context.
- `PreToolUse` — Before any tool executes. Richest control: allow/deny/ask + `updatedInput`.
- `PermissionRequest` — When the permission dialog would appear. Can auto-approve with `updatedPermissions`.

**Agentic Loop Events (post-execution):**

- `PostToolUse` — After successful tool execution. Can provide feedback and even replace MCP tool output.
- `PostToolUseFailure` — After tool failure. Additional context for Claude about the failure.

**Subagent Events:**

- `SubagentStart` — On subagent spawn. Can inject context into the subagent.
- `SubagentStop` — On subagent termination. Same control as `Stop`.

**Stop Events:**

- `Stop` — When Claude finishes responding. Can force it to continue.
- `StopFailure` — When the response fails due to an API error. No decision control.

**Team Events:**

- `TeammateIdle` — When a teammate is about to become idle.
- `TaskCompleted` — When a task is marked as complete. Can prevent completion.

**Configuration and Instruction Events:**

- `ConfigChange` — Settings change. Can block (except `policy_settings`).
- `InstructionsLoaded` — When CLAUDE.md or rules are loaded. Observation only.

**Compaction Events:**

- `PreCompact` — Before context compaction.
- `PostCompact` — After compaction, with access to the `compact_summary`.

**Worktree Events:**

- `WorktreeCreate` — Overrides default `git worktree` behavior. Must return an absolute path.
- `WorktreeRemove` — Worktree cleanup.

**MCP Events:**

- `Elicitation` — Intercepts input requests from MCP servers.
- `ElicitationResult` — Modifies responses to elicitations.

**Notification Event:**

- `Notification` — Fires on system notifications.

### 2.3 Four Hook Handler Types

| Type | Mechanism | Supported Events | Default Timeout |
|------|-----------|-----------------|----------------|
| `command` | Shell script via stdin/stdout | All 22 events | 600s |
| `http` | POST to HTTP endpoint | 8 agentic loop events | 30s |
| `prompt` | LLM single-turn for decisions | 8 agentic loop events | 30s |
| `agent` | Subagent with tool access | 8 agentic loop events | 60s |

The 8 events that support all types: `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `UserPromptSubmit`, `Stop`, `SubagentStop`, `TaskCompleted`.

### 2.4 Per-Event Decision System

The document reveals three distinct decision control patterns:

```
Pattern 1: Top-level decision
  → UserPromptSubmit, PostToolUse, PostToolUseFailure, Stop, SubagentStop, ConfigChange
  → { "decision": "block", "reason": "..." }

Pattern 2: hookSpecificOutput with permissionDecision
  → PreToolUse
  → { "hookSpecificOutput": { "permissionDecision": "allow|deny|ask" } }

Pattern 3: hookSpecificOutput with decision.behavior
  → PermissionRequest
  → { "hookSpecificOutput": { "decision": { "behavior": "allow|deny" } } }
```

### 2.5 Exit Code Mechanism

| Exit Code | Meaning | JSON Processing |
|-----------|---------|-----------------|
| 0 | Success — action allowed | Yes, stdout is parsed as JSON |
| 2 | Blocking error — action prevented | No, stderr used as message |
| Other | Non-blocking error — continues | No, stderr shown in verbose mode |

### 2.6 Configuration Locations (Scope Hierarchy)

| Location | Scope | Shareable |
|----------|-------|-----------|
| `~/.claude/settings.json` | All projects | No |
| `.claude/settings.json` | Single project | Yes (versionable) |
| `.claude/settings.local.json` | Single project | No (gitignored) |
| Managed policy settings | Organization | Yes (admin) |
| Plugin `hooks/hooks.json` | Active plugin | Yes |
| Skill/Agent YAML frontmatter | Active component | Yes |

### 2.7 Asynchronous Hooks

The `"async": true` flag (for `type: "command"` only) enables background execution:

- Claude continues working immediately
- Output delivered on the next turn via `systemMessage` or `additionalContext`
- Decision fields are ignored (action has already proceeded)
- No deduplication between multiple executions

### 2.8 Hooks in Skills and Agents

Hooks can be defined directly in the YAML frontmatter of skills and subagents:

- Scope limited to the component's lifecycle
- Automatic cleanup on termination
- `Stop` hooks in subagents are automatically converted to `SubagentStop`
- Support `"once": true` for single execution per session

## 3. Points of Attention

### 3.1 Critical Gotchas

| Point | Detail | Impact |
|-------|--------|--------|
| **Stop hook infinite loop** | If a Stop hook always returns `"block"`, Claude never stops | Session hangs; check `stop_hook_active` |
| **Exit code 2 ≠ block for all** | Events like `PostToolUse` and `SessionStart` ignore exit 2 as a decision | Inconsistent behavior if not checked |
| **JSON parsing with shell profile** | If the shell profile prints text on startup, it interferes with JSON parsing | Command hooks fail silently |
| **HTTP hooks don't block by status** | Non-2xx is a non-blocking error; to block, return 2xx with deny JSON | False sense of security |
| **policy_settings not blockable** | `ConfigChange` hooks with `"block"` are ignored for `policy_settings` | Intentional enterprise design |
| **SessionEnd 1.5s timeout** | Cleanup hooks may not complete in time | Use `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS` |
| **Matchers are regex, not glob** | `Edit|Write` uses `|` as regex OR, not shell glob | Unexpected patterns if not escaped |
| **Async hooks without decisions** | `decision`, `permissionDecision`, `continue` ignored in async | Use only for side-effects |

### 3.2 Security

- **Command hooks execute with full user permissions** — they can access, modify, or delete any file
- Shell variables must ALWAYS be quoted (`"$VAR"` not `$VAR`)
- Paths must be absolute, using `$CLAUDE_PROJECT_DIR`
- Inputs must be validated and sanitized
- Check for path traversal (`..` in file paths)
- Avoid processing `.env`, `.git/`, private keys

### 3.3 Execution Order

- All matching hooks for an event execute in parallel
- Identical handlers are deduplicated (by command string or URL)
- Hooks from multiple sources (user, project, plugin, skill) are combined
- `disableAllHooks: true` disables all except managed hooks

## 4. Use Cases and Scope

### 4.1 When to Use Each Event

| Scenario | Recommended Event | Hook Type |
|----------|-------------------|-----------|
| Block destructive commands | `PreToolUse` matcher `Bash` | command |
| Auto-approve safe commands | `PermissionRequest` | command/prompt |
| Lint after file edit | `PostToolUse` matcher `Edit\|Write` | command (async) |
| Load project context | `SessionStart` | command |
| Ensure tests pass before stopping | `Stop` | agent |
| Log MCP operations | `PreToolUse` matcher `mcp__.*` | command |
| PR validation before commit | `PreToolUse` matcher `Bash` | command |
| Inject guidelines into subagents | `SubagentStart` | command |
| Config change auditing | `ConfigChange` | command |
| Prevent premature task completion | `TaskCompleted` | command/prompt |
| Custom worktree cleanup (SVN/Perforce) | `WorktreeCreate` + `WorktreeRemove` | command |
| MCP response automation | `Elicitation` | command |

### 4.2 When NOT to Use Hooks

| Scenario | Better Alternative | Why |
|----------|-------------------|-----|
| Code style guidance | Rules (`.claude/rules/`) | Does not need deterministic enforcement |
| Project documentation | CLAUDE.md | Hooks don't add persistent context |
| Complex multi-step instructions | Skills | Hooks are for point actions, not workflows |
| Rules requiring model judgment | Rules + CoT | Command hooks are binary (allow/block) |

## 5. Applicability to Agent Infrastructure

### 5.1 Skills

**Hooks as skill extensions:**

- Skills can define hooks in their YAML frontmatter, creating self-contained workflows
- A "database migration" skill can have a `PreToolUse` hook that validates SQL commands before execution
- The `"once": true` flag is ideal for setup hooks that should run only on skill activation

**Pattern: Skill with hook-based validation**

```yaml
---
name: safe-db-migration
description: Run database migrations with safety checks
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-sql.sh"
  Stop:
    - hooks:
        - type: agent
          prompt: "Verify migration completed successfully. Check database state."
---
```

**Complementary lifecycle:**

- `SessionStart` hook can load state that skills need
- `PostToolUse` hook can validate outputs of scripts executed by skills
- `Stop` hook (agent type) can verify whether the skill completed correctly

### 5.2 Hooks (Design Patterns)

**Pattern 1: Layered Guardrail**

```
PreToolUse (command) → Fast, deterministic validation
  ↓ If "ask"
PermissionRequest (prompt) → LLM evaluation if ambiguous
  ↓ If "allow"
PostToolUse (command) → Result verification
  ↓
Stop (agent) → Final verification with tool access
```

**Pattern 2: Asynchronous Feedback Loop**

```
PostToolUse (async command) → Runs tests in background
  → Claude continues working
  → Result delivered as systemMessage on the next turn
  → Claude corrects if tests failed
```

**Pattern 3: Dynamic Context Injection**

```
SessionStart → Loads GitHub issues, CI state
SubagentStart → Injects guidelines specific to the subagent type
UserPromptSubmit → Adds metadata about the current project state
```

**Pattern 4: Multi-Source Hook Composition**

- User settings: global security hooks
- Project settings: linting and testing hooks
- Plugin hooks: formatting hooks
- Skill frontmatter: workflow-specific hooks

### 5.3 Subagents

**Hooks that affect subagents:**

- `SubagentStart` — Inject context and guidelines before the subagent starts working
- `SubagentStop` — Validate that the subagent completed satisfactorily (same pattern as `Stop`)
- `PreToolUse` with `agent_id` in input — Allows distinguishing subagent calls vs. main thread
- Hooks defined in agent frontmatter are scoped to the subagent's lifecycle

**`agent_id` and `agent_type` fields:**
The hook input includes `agent_id` and `agent_type` when executing in a subagent context, enabling conditional logic:

```bash
AGENT_TYPE=$(echo "$INPUT" | jq -r '.agent_type // empty')
if [ "$AGENT_TYPE" = "Explore" ]; then
  # Different rules for exploration agents
fi
```

### 5.4 Rules

**Hooks vs Rules — Decision Framework:**

| Criterion | Hook | Rule |
|-----------|------|------|
| Enforcement | Deterministic (programmatic) | Probabilistic (via model attention) |
| Context cost | Zero (outside the window) | Consumes budget tokens |
| Flexibility | Binary (allow/block) or LLM (prompt/agent) | Nuanced, contextual |
| When loaded | Always active (lifecycle) | Path-scoped, lazy |
| Maintenance | External scripts | Inline Markdown |
| Verifiability | Independently testable | Depends on model behavior |

**Principle derived from research-context-engineering-comprehensive:
> "Converting behavioral instructions that are enforced into hooks removes them from the attention budget while ensuring deterministic enforcement."

**Practical rule:** If the instruction can be verified programmatically and must ALWAYS be followed, use a hook. If it requires contextual judgment, use a rule.

### 5.5 Memory

**Hooks that interact with memory:**

- `SessionStart` can check whether MEMORY.md exists and is up to date
- `PostCompact` can save `compact_summary` for future reference
- `InstructionsLoaded` can audit which memory files were loaded and when
- `ConfigChange` with `skills` matcher can detect when skills that generate memory are modified

**Pattern: Auto-cleanup of memory via PostCompact:**

```bash
#!/bin/bash
INPUT=$(cat)
SUMMARY=$(echo "$INPUT" | jq -r '.compact_summary')
echo "$SUMMARY" >> ~/.claude/projects/my-project/compaction-history.log
```

## 6. Applicability of the Prompt Engineering Guide

### 6.1 Techniques Applicable to Hooks

| Technique | Hook Type | Application |
|-----------|-----------|-------------|
| **ReAct** | `type: "agent"` | Agent hooks naturally implement ReAct: reason about state, use tools to investigate, decide |
| **Chain-of-Thought** | `type: "prompt"` | Hook prompts can include "Analyze step by step before deciding" for better judgment |
| **Self-Consistency** | Multiple prompt hooks | Run 2-3 prompt hooks for the same event and require consensus (via wrapper script) |
| **Least-to-Most** | Hook composition | Decompose complex validations: hook 1 checks syntax → hook 2 checks security → hook 3 checks compliance |
| **Prompt Chaining** | Event pipeline | `PreToolUse` → `PostToolUse` → `Stop` form a natural validation chain |

### 6.2 Example: Stop Hook with CoT

```json
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "prompt",
        "prompt": "Analyze step by step whether Claude completed the task. Context: $ARGUMENTS\n\n1. What tasks were requested?\n2. Which ones were completed?\n3. Are there pending errors?\n4. Did tests pass?\n\nStep by step, determine whether it is safe to stop."
      }]
    }]
  }
}
```

### 6.3 When NOT to Use Advanced Techniques in Hooks

- **Tree of Thoughts**: Excessive for hooks — high latency, high cost
- **PAL**: Command hooks are already code; PAL is redundant
- **Few-shot CoT**: Hook prompts should be concise (30s timeout); long examples are counterproductive
- **Reflexion**: Hooks are stateless between executions; there is no memory of previous attempts

## 7. Correlations with Core Documents

### 7.1 research-context-engineering-comprehensive.md

| Context Principle | Implementation via Hooks |
|-------------------|--------------------------|
| Instruction budget (~150-200) | Hooks remove enforced rules from CLAUDE.md, freeing budget |
| Progressive disclosure | `InstructionsLoaded` tracks lazy loading; `SessionStart` injects JIT context |
| Context poisoning | Hooks prevent actions that could pollute context (e.g., blocking unnecessary tools) |
| Lost-in-the-middle | Hooks with `additionalContext` inject information at privileged positions |
| Compaction awareness | `PreCompact`/`PostCompact` allow reacting to compaction |

### 7.2 Evaluating-AGENTS-paper.md

| Paper Finding | Relationship with Hooks |
|---------------|------------------------|
| LLM-generated files reduce performance | Hooks enforce rules without adding text to the context |
| "More testing" increases with config files | `Stop` hooks with agent type explicitly validate tests |
| Instructions are followed — that's the problem | Hook enforcement is external to the model, avoiding the dilemma |

### 7.3 claude-prompting-best-practices.md

| Best Practice | Application in Hooks |
|---------------|---------------------|
| System prompts for hard constraints | Hooks implement constraints as code, more reliable than prompts |
| Structured output with JSON | All hook↔Claude communication uses structured JSON |
| Tool use patterns | `PreToolUse`/`PostToolUse` control exactly how tools are used |

### 7.4 a-guide-to-agents.md (merged guide)

| Guide Principle | Hooks as Implementation |
|-----------------|------------------------|
| Keep config minimal | Hooks allow a smaller CLAUDE.md by removing enforcement rules |
| Progressive disclosure | `InstructionsLoaded` hook monitors lazy loading |
| Don't auto-generate | Hooks are code, not generated text — always intentional |

## 8. Decision Framework

### Decision Tree: Hook vs Rule vs CLAUDE.md vs Skill

```
Does the instruction need to be ALWAYS followed without exception?
├── YES → Can it be verified programmatically?
│   ├── YES → Use HOOK (command type)
│   │   └── Is it a simple rule (regex match)?
│   │       ├── YES → PreToolUse/PermissionRequest with exit code
│   │       └── NO → PreToolUse/Stop with agent type
│   └── NO → Use RULE with strong language ("MUST", "NEVER")
│       └── Is it scoped to a specific path?
│           ├── YES → .claude/rules/ with paths: frontmatter
│           └── NO → Main CLAUDE.md
└── NO → Is it contextual guidance?
    ├── YES → Is it specific to a workflow?
    │   ├── YES → Use SKILL (SKILL.md)
    │   └── NO → Use RULE or CLAUDE.md
    └── NO → Probably doesn't need to be documented
```

### Quick Decision Matrix

| Need | Mechanism | Example |
|------|-----------|---------|
| Block `rm -rf` | Hook command on `PreToolUse` | `block-rm.sh` |
| Run tests after edit | Async hook on `PostToolUse` | `run-tests-async.sh` |
| Ensure conventional commit format | Prompt hook on `PreToolUse[Bash]` | Prompt evaluating format |
| Preferred code style | Rule in `.claude/rules/` | `code-style.md` |
| How to run migrations | Skill | `db-migration/SKILL.md` |
| Project architecture | CLAUDE.md | Overview section |
| Auto-approve `npm test` | Hook command on `PermissionRequest` | Script with `updatedPermissions` |

## 9. Practical Recommendations

### 9.1 Essential Implementation Patterns

**1. Guard Script Template (reusable):**

```bash
#!/bin/bash
# Base template for command hooks
INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
TOOL_INPUT=$(echo "$INPUT" | jq -r '.tool_input // empty')
AGENT_TYPE=$(echo "$INPUT" | jq -r '.agent_type // empty')

# Your logic here
# exit 0 = allow, exit 2 = block (stderr), JSON stdout = fine control
```

**2. Separation of Concerns by Configuration:**

- `~/.claude/settings.json` — Global security hooks (block destructive commands)
- `.claude/settings.json` — Project quality hooks (lint, test, format)
- `.claude/settings.local.json` — Personal hooks (notifications, logging)
- Skill frontmatter — Workflow-specific hooks

**3. Stop Hook with Anti-Loop Protection:**

```bash
#!/bin/bash
INPUT=$(cat)
STOP_HOOK_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active')
if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
  exit 0  # Don't enter a loop
fi
# Checks here
```

**4. Context Injection via SessionStart:**

```bash
#!/bin/bash
# Load dynamic context at session start
ISSUES=$(gh issue list --limit 5 --json title,number 2>/dev/null)
BRANCH=$(git branch --show-current 2>/dev/null)
LAST_COMMIT=$(git log --oneline -1 2>/dev/null)

cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "Current branch: $BRANCH\nLast commit: $LAST_COMMIT\nOpen issues: $ISSUES"
  }
}
EOF
```

### 9.2 Implementation Checklist

- [ ] Security hooks (PreToolUse for destructive commands) as first priority
- [ ] Quality hooks (PostToolUse async for tests) as second priority
- [ ] Stop hooks WITH `stop_hook_active` protection to avoid loops
- [ ] Use `$CLAUDE_PROJECT_DIR` in script paths
- [ ] Quote all shell variables
- [ ] Test with `claude --debug` to verify matching and execution
- [ ] Check `/hooks` menu to confirm final configuration
- [ ] Prompt/agent hooks only for the 8 supported events
- [ ] Appropriate timeouts: command (600s), prompt (30s), agent (60s), async (custom)
- [ ] Keep hook scripts versioned in `.claude/hooks/` with executable permissions

### 9.3 Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Synchronous hook for long-running tests | Blocks Claude for minutes | Use `"async": true` |
| Stop hook without `stop_hook_active` check | Infinite loop | Always check the field |
| HTTP hooks for critical security | Non-2xx doesn't block | Use command hooks for security |
| Agent hooks for simple validations | Unnecessary latency and cost | Command hook with jq is sufficient |
| Same hook in user + project settings | Deduplication by exact string only | Consolidate in one location |
| Hooks that print to stdout beyond JSON | Interferes with JSON parsing | Redirect debug output to stderr |
