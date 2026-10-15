# Analysis: Automate Workflows with Hooks

> **Status**: Current
> **Source document**: [Automate Workflows with Hooks](https://docs.anthropic.com/en/docs/claude-code/hooks)
> **Analysis date**: 2026-03
> **Scope**: Practical guide for workflow automation via hooks in Claude Code

---

## 1. Executive Summary

The document "Automate Workflows with Hooks" serves as an introductory and practical guide to the Claude Code hooks system. Unlike the technical reference document, it focuses on **concrete use cases and copy-ready configurations**, covering everything from desktop notifications to auto-formatting code and protecting sensitive files. The document positions hooks as the layer of **deterministic control** over Claude Code behavior — ensuring that certain actions always happen, regardless of LLM judgment.

The guide introduces four types of hooks (`command`, `http`, `prompt`, `agent`) and 22 lifecycle events, but concentrates most examples on `command` hooks as they are the most accessible. The approach is progressive: it starts with a trivial notification hook, advances to automatic formatting and file protection, and ends with LLM-based hooks for decisions that require judgment. This progression mirrors the progressive disclosure strategy documented in the context optimization research.

The core value of the document for agent infrastructure lies in demonstrating that **behavioral instructions can be converted into deterministic hooks**, removing them from the LLM's attention budget while ensuring absolute enforcement. This connects directly with Anthropic's context engineering principles about maintaining the smallest possible set of high-signal tokens.

---

## 2. Key Concepts and Mechanisms

### 2.1 Hook Types

| Type | Mechanism | Use Case | Complexity |
|------|-----------|----------|------------|
| `command` | Executes shell command | Formatting, validation, notification | Low |
| `http` | POST to HTTP endpoint | Centralized auditing, external services | Medium |
| `prompt` | Single-turn LLM evaluation | Decisions that require judgment | Medium |
| `agent` | Subagent with tool access | Complex verification against the codebase | High |

### 2.2 Event Lifecycle

The document presents 22 events organized temporally:

**Session events:**

- `SessionStart` — session start/resume (matcher: `startup`, `resume`, `clear`, `compact`)
- `SessionEnd` — session termination (matcher: `clear`, `resume`, `logout`, etc.)

**Agentic loop events:**

- `UserPromptSubmit` — before Claude processes the prompt
- `PreToolUse` — before tool execution (can block)
- `PermissionRequest` — when permission dialog appears
- `PostToolUse` — after tool executes successfully
- `PostToolUseFailure` — after tool failure

**Subagent events:**

- `SubagentStart` / `SubagentStop` — spawn and termination of subagents

**Compaction events:**

- `PreCompact` / `PostCompact` — before and after compaction

**Control events:**

- `Stop` / `StopFailure` — when Claude finishes response
- `TaskCompleted` — when task is marked as complete
- `TeammateIdle` — when teammate is about to go idle

**Configuration events:**

- `ConfigChange` — when configuration file changes
- `InstructionsLoaded` — when CLAUDE.md or rules are loaded

**Worktree events:**

- `WorktreeCreate` / `WorktreeRemove` — creation and removal of worktrees

**MCP events:**

- `Elicitation` / `ElicitationResult` — MCP server input

### 2.3 Hook ↔ Claude Code Communication

```
┌──────────────┐     stdin (JSON)      ┌──────────────┐
│  Claude Code │ ─────────────────────> │  Hook Script │
│              │                        │              │
│              │ <───────────────────── │              │
│              │  stdout (JSON/text)    │              │
│              │  stderr (messages)     │              │
│              │  exit code (0/2/N)     │              │
└──────────────┘                        └──────────────┘
```

**Exit codes:**

- `0` — action proceeds; stdout is processed as JSON or context
- `2` — action blocked; stderr is feedback for Claude
- Any other — action proceeds; stderr appears in verbose mode

### 2.4 Matchers (Filters)

Matchers are regex expressions that filter when hooks fire. Each event filters on different fields:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "prettier --write ..." }
        ]
      }
    ]
  }
}
```

**Filter fields by event:**

- Tool events (`PreToolUse`, `PostToolUse`, etc.) → `tool_name`
- `SessionStart` → `source` (startup, resume, clear, compact)
- `SessionEnd` → `reason`
- `Notification` → `notification_type`
- `ConfigChange` → configuration source
- `SubagentStart`/`SubagentStop` → agent type

### 2.5 Configuration Scope

| Location | Scope | Shareable |
|----------|-------|-----------|
| `~/.claude/settings.json` | All projects | No (local) |
| `.claude/settings.json` | Single project | Yes (commit) |
| `.claude/settings.local.json` | Single project | No (gitignored) |
| Managed policy settings | Organizational | Yes (admin) |
| Plugin `hooks/hooks.json` | When plugin active | Yes (bundled) |
| Skill/Agent frontmatter | While component active | Yes (defined in file) |

---

## 3. Points of Attention

### 3.1 Common Pitfalls

**Infinite loop in Stop hook:**
The most critical documented error. If a Stop hook blocks Claude from stopping without checking if it's already in a continuation, it creates an infinite loop. The solution is to check `stop_hook_active`:

```bash
#!/bin/bash
INPUT=$(cat)
if [ "$(echo "$INPUT" | jq -r '.stop_hook_active')" = "true" ]; then
  exit 0  # Allow Claude to stop
fi
# ... rest of logic
```

**Invalid JSON from echo in shell profile:**
When `~/.zshrc` or `~/.bashrc` contains unconditional `echo`, the output contaminates the hook's stdout:

```text
Shell ready on arm64        ← text from profile
{"decision": "block"}       ← JSON from hook
```

Solution:

```bash
if [[ $- == *i* ]]; then
  echo "Shell ready"
fi
```

**Case-sensitive matcher:**
Matchers are case-sensitive regex. `"bash"` does not match `"Bash"`.

**PermissionRequest does not fire in headless mode:**
`PermissionRequest` hooks do not work with `-p` (non-interactive mode). Use `PreToolUse` as an alternative.

**PostToolUse cannot undo:**
The tool has already executed. The hook can only provide feedback, not revert the action.

### 3.2 Security Considerations

- Command hooks execute with **full system user permissions**
- Always validate and sanitize JSON inputs from stdin
- Always quote shell variables (`"$VAR"` not `$VAR`)
- Check for path traversal (`..` in file paths)
- Use absolute paths (`$CLAUDE_PROJECT_DIR`)
- Avoid processing sensitive files (`.env`, `.git/`, keys)

### 3.3 Execution Order

- All hooks matching an event run **in parallel**
- Identical hooks (same command) are **automatically deduplicated**
- Default timeout: 10 minutes (configurable per hook)
- Async hooks do not block execution and cannot control behavior

### 3.4 Deny Rules Priority

Returning `"allow"` in a `PreToolUse` hook **does not override** permission deny rules. Deny rules, including managed settings, always take priority over hook approvals.

---

## 4. Use Cases and Scope

### 4.1 When Hooks Are the Right Tool

| Scenario | Hook | Rule | CLAUDE.md | Skill |
|----------|------|------|-----------|-------|
| Format code after editing | **Hook** (determinism) | - | - | - |
| Block editing of .env | **Hook** (enforcement) | - | - | - |
| Notify when awaiting input | **Hook** (side-effect) | - | - | - |
| Preferred code style | - | - | **CLAUDE.md** | - |
| API pattern to follow | - | **Rule** | - | - |
| Complex deploy | - | - | - | **Skill** |
| Verify tests before stopping | **Hook** (gate) | - | - | - |
| Re-inject context after compaction | **Hook** (lifecycle) | - | - | - |
| Audit config changes | **Hook** (observability) | - | - | - |

### 4.2 Primary Documented Patterns

**1. Notification (pure side-effect):**

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "notify-send 'Claude Code' 'Needs attention'"
          }
        ]
      }
    ]
  }
}
```

**2. Auto-formatting (post-processing):**

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write"
          }
        ]
      }
    ]
  }
}
```

**3. File protection (pre-validation with blocking):**
Separate script that checks protected patterns and exits with code 2 to block.

**4. Context re-injection after compaction:**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "compact",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Reminder: use Bun, not npm. Run bun test before committing.'"
          }
        ]
      }
    ]
  }
}
```

**5. Selective auto-approval (permission control):**

```json
{
  "hooks": {
    "PermissionRequest": [
      {
        "matcher": "ExitPlanMode",
        "hooks": [
          {
            "type": "command",
            "command": "echo '{\"hookSpecificOutput\": {\"hookEventName\": \"PermissionRequest\", \"decision\": {\"behavior\": \"allow\"}}}'"
          }
        ]
      }
    ]
  }
}
```

**6. LLM-based verification (Stop hook with prompt):**

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Verify that all tasks are complete."
          }
        ]
      }
    ]
  }
}
```

---

## 5. Applicability to Agent Infrastructure

### 5.1 Skills

**Hook ↔ skill interaction:**

- Skills can define hooks in their YAML frontmatter — hooks scoped to the skill's lifecycle
- `PostToolUse` hooks can validate outputs of tools used by skills
- `PreToolUse` hooks can intercept tool calls within skills
- The `once: true` field allows skill hooks that execute only once per session

**Pattern: Skill with integrated safety hook:**

```yaml
---
name: deploy-production
description: Safe deploy to production
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-deploy-command.sh"
---
```

**Hooks as an alternative to instructions in skills:**
When a skill has enforcement rules (e.g., "never execute rm -rf"), converting those rules into `PreToolUse` hooks removes them from the skill's attention budget and ensures deterministic enforcement.

### 5.2 Hooks (Design Patterns)

**Guardian Pattern (Gate Pattern):**
`PreToolUse` and `Stop` hooks that act as quality gates — blocking actions that do not meet criteria.

```bash
#!/bin/bash
# gate-pattern: blocks commits without passing tests
INPUT=$(cat)
if [ "$(echo "$INPUT" | jq -r '.stop_hook_active')" = "true" ]; then
  exit 0
fi
npm test 2>&1 > /dev/null
if [ $? -ne 0 ]; then
  echo '{"decision": "block", "reason": "Tests failing. Fix them before finishing."}'
fi
```

**Observer Pattern:**
`PostToolUse`, `Notification`, `SessionEnd` hooks that log events without interfering with the flow.

**Context Injection Pattern:**
`SessionStart` and `UserPromptSubmit` hooks that add information to Claude's context.

**Composition Pattern:**
Multiple hooks on the same event for different concerns:

```json
{
  "PostToolUse": [
    {
      "matcher": "Edit|Write",
      "hooks": [
        { "type": "command", "command": "prettier --write ..." },
        { "type": "command", "command": "./lint-check.sh" }
      ]
    }
  ]
}
```

**Testing and Debugging:**

- `/hooks` to inspect configuration
- `Ctrl+O` (verbose mode) to see hook output in the transcript
- `claude --debug` for full execution details
- Test manually with `echo '{"tool_name":"Bash"}' | ./hook.sh; echo $?`

### 5.3 Subagents

**Hooks in subagent context:**

- `SubagentStart` hooks can inject additional context into the subagent via `additionalContext`
- `SubagentStop` hooks can prevent the subagent from stopping (same semantics as `Stop`)
- Subagent hooks defined in frontmatter automatically convert `Stop` to `SubagentStop`
- The `agent_id` field in the input distinguishes subagent calls vs. the main thread

**Pattern: Inject security guidelines into subagents:**

```json
{
  "hooks": {
    "SubagentStart": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "echo '{\"hookSpecificOutput\": {\"hookEventName\": \"SubagentStart\", \"additionalContext\": \"Follow OWASP Top 10 security guidelines\"}}'"
          }
        ]
      }
    ]
  }
}
```

**Isolation:**

- Hooks defined in global settings also apply to subagents
- Hooks defined in agent frontmatter are scoped to that agent's lifecycle
- `agent_type` in the input allows filtering hooks by subagent type

### 5.4 Rules

**Hooks vs Rules — when to use each:**

| Aspect | Hooks | Rules (`.claude/rules/`) |
|--------|-------|--------------------------|
| Nature | Deterministic, enforcement | Advisory, guidance |
| Execution | Automatic, in the lifecycle | Injected into context |
| Context impact | Zero (executes externally) | Consumes attention budget |
| Flexibility | Binary (allow/block) | Nuanced (judgment) |
| Path-scoping | Via regex matcher | Via frontmatter `paths:` |
| Reliability | 100% (if hook works) | Depends on the LLM following |

**Complementary pattern:**
Rules define the "why" and the guidance; hooks enforce the "what" deterministically.

Example: A rule says "Prefer rg over grep for better performance". A `PreToolUse` hook intercepts Bash calls with `grep` and suggests `rg`:

```bash
#!/bin/bash
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command')
if echo "$COMMAND" | grep -q '^grep '; then
  echo '{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "Use rg instead of grep for better performance"}}'
fi
exit 0
```

### 5.5 Memory

**Hooks that manage memory:**

- `SessionStart` with matcher `compact` re-injects critical context lost during compaction
- `PostCompact` can save the `compact_summary` for external persistence
- `InstructionsLoaded` logs when CLAUDE.md or rules files are loaded (auditing)

**Hooks triggered by memory events:**

- `ConfigChange` with matcher `skills` detects changes in skill files
- `InstructionsLoaded` with matcher `path_glob_match` detects lazy loading of rules

**Pattern: Critical context resilient to compaction:**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "compact",
        "hooks": [
          {
            "type": "command",
            "command": "cat .claude/critical-context.txt"
          }
        ]
      }
    ]
  }
}
```

The contents of `.claude/critical-context.txt` are automatically added to Claude's context after each compaction, eliminating the need to maintain this information in CLAUDE.md (which is already loaded via its own mechanism).

---

## 6. Applicability of the Prompt Engineering Guide

### 6.1 ReAct for Agent-Based Hooks

The ReAct pattern (Thought → Action → Observation) is the core loop of `type: "agent"` hooks. The subagent spawned by an agent hook executes exactly this cycle:

1. **Thought**: analyzes the hook's prompt and context
2. **Action**: uses tools (Read, Grep, Glob) to investigate
3. **Observation**: evaluates results and returns a decision `{ok: true/false}`

**Practical application**: An agent hook that verifies if tests pass before allowing Claude to stop uses ReAct internally — reads test files, runs the test suite, observes results, decides.

### 6.2 Prompt Chaining for Hook Composition

Multiple hooks on the same event implement deterministic prompt chaining. The output of each hook does not feed directly into the next, but the cumulative effect on Claude Code creates a pipeline:

1. `PreToolUse` hook 1: validates command security → allows
2. `PreToolUse` hook 2: checks protected patterns → allows
3. Tool executes
4. `PostToolUse` hook 1: formats code
5. `PostToolUse` hook 2: runs linter

### 6.3 Constitutional AI for Stop Hooks

The Constitutional AI pattern (critique → revise) applies directly to `type: "prompt"` hooks on the `Stop` event:

```json
{
  "type": "prompt",
  "prompt": "Evaluate whether Claude completed all requested tasks. Principles: (1) All features were implemented (2) Tests were written and pass (3) No pending errors. If any principle was not met, respond {\"ok\": false, \"reason\": \"<explanation>\"}."
}
```

The "constitution" consists of the principles against which the LLM evaluates; the `ok: false` decision with `reason` is the revision that returns to the main Claude.

### 6.4 Structured Output for Hook ↔ Claude Code Communication

All hook communication is based on structured JSON. The prompt engineering guide recommendations apply:

- Separate reasoning from decision (the hook reasons internally, returns structured decision)
- Use well-defined fields (`permissionDecision`, `reason`, `additionalContext`)
- Avoid mixing free text with JSON

### 6.5 Least-to-Most for Complex Hook Decomposition

Complex hooks should be decomposed into smaller, focused scripts, each solving a subproblem. Instead of a mega-script that validates, formats, and tests:

```
hooks/
├── validate-security.sh      # Subproblem 1
├── format-code.sh             # Subproblem 2
├── run-tests.sh               # Subproblem 3
└── check-protected-files.sh   # Subproblem 4
```

Each script is simple, testable, and composable.

### 6.6 Role Prompting for Prompt/Agent Hooks

In `type: "prompt"` and `type: "agent"` hooks, using role prompting improves evaluation accuracy:

```json
{
  "type": "prompt",
  "prompt": "You are a senior code reviewer specializing in security. Evaluate whether the following command is safe: $ARGUMENTS"
}
```

The specialized role directs the model's probability distribution toward more rigorous and well-founded decisions.

---

## 7. Correlations with Key Documents

### 7.1 Context Optimization

**Direct connection**: The context optimization research document states that "converting behavioral instructions into deterministic hooks removes them from the context budget". The hooks guide demonstrates exactly this:

- Rule "always format with Prettier" → `PostToolUse` hook with Prettier (0 context tokens)
- Rule "never edit .env" → `PreToolUse` hook with exit 2 (0 context tokens)

**Quantification**: Each rule converted to a hook saves ~20-50 tokens in CLAUDE.md, which in a 200-line file (~3000 tokens) represents 0.7-1.7% of the budget per rule.

### 7.2 Instruction Budget

**Direct connection**: The principle of keeping CLAUDE.md under 200 lines is enabled by hooks. Enforcement rules that previously consumed lines in CLAUDE.md now live in hooks:

| Before (CLAUDE.md) | After (Hook) | Savings |
|---------------------|--------------|---------|
| "NEVER edit .env or package-lock.json" | `PreToolUse` protect-files.sh | ~1 line |
| "Always run prettier after editing" | `PostToolUse` prettier | ~1 line |
| "Notify when awaiting input" | `Notification` notify-send | ~1 line |
| "Always run tests before committing" | `Stop` hook with npm test | ~2 lines |

### 7.3 Progressive Disclosure

**Direct connection**: Hooks implement temporal progressive disclosure:

- `SessionStart` loads initial context
- `PreToolUse`/`PostToolUse` execute at the exact moment of the action
- `InstructionsLoaded` reacts to lazy loading of rules
- `SessionStart` with matcher `compact` re-injects critical context just-in-time

Unlike CLAUDE.md (pre-loaded) and rules (loaded by path), hooks operate at **specific lifecycle points** — the most precise form of "just in time".

### 7.4 Context Poisoning

**Direct connection**: Hooks address two poisoning vectors identified in the research:

1. **Outdated instructions**: Hooks execute programmatic logic, they do not depend on the LLM "remembering" the instruction
2. **Contradictory instructions**: Hooks are deterministic — there is no ambiguity about which rule prevails

The `SessionStart` hook with matcher `compact` specifically solves the problem of **critical context loss during compaction** — a poisoning vector through omission.

### 7.5 Agent Config Evaluation

**Direct connection**: The principle that "configuration files work best when they focus on guidance, not enforcement" is implemented by the hooks/rules division:

- CLAUDE.md and rules: guidance, preferences, conventions (advisory)
- Hooks: enforcement, validation, blocking (deterministic)

---

## 8. Decision Framework

### 8.1 Decision Tree

```
Does the rule need to be followed 100% of the time?
├── YES → Can the rule be verified programmatically?
│   ├── YES → Use a HOOK
│   │   ├── Need to block before the action? → PreToolUse hook
│   │   ├── Need to process after the action? → PostToolUse hook
│   │   ├── Need to control when Claude stops? → Stop hook
│   │   └── Need to react to lifecycle events? → Appropriate event
│   └── NO → Use a prompt/agent type HOOK (LLM evaluation)
├── NO, but it's important → Is the rule specific to a path/area?
│   ├── YES → Use a RULE with paths: frontmatter
│   └── NO → Is the rule universal for the project?
│       ├── YES → Place in the project's CLAUDE.md
│       └── NO → Place in the subdirectory's CLAUDE.md
└── Is it a complex capability with multiple steps?
    └── YES → Use a SKILL
```

### 8.2 Decision Matrix

| Criterion | Hook (command) | Hook (prompt/agent) | Rule | CLAUDE.md | Skill |
|-----------|---------------|--------------------|----|-----------|-------|
| 100% enforcement | Yes | ~95% | No | No | No |
| Zero context cost | Yes | No (API cost) | No | No | Partial |
| Judgment required | No | Yes | Yes | Yes | Yes |
| Setup complexity | Medium | Low | Low | Minimal | Medium-High |
| Auditable | Yes (logs) | Yes (transcript) | No | No | No |
| Shareable via git | Yes (.claude/settings.json) | Yes | Yes | Yes | Yes |
| Temporal scope | Lifecycle point | Lifecycle point | Always in context | Always in context | On demand |

### 8.3 Golden Rule

> **If the consequence of violating the rule is severe (security, data, compliance), use a hook.**
> **If the consequence is degraded but acceptable quality, use CLAUDE.md or rules.**
> **If the rule requires multiple execution steps, use a skill.**

---

## 9. Practical Recommendations

### 9.1 Starter Kit for New Projects

Minimum recommended configuration for `.claude/settings.json`:

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "notify-send 'Claude Code' 'Needs attention'"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write 2>/dev/null || true"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/protect-files.sh"
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "matcher": "compact",
        "hooks": [
          {
            "type": "command",
            "command": "cat \"$CLAUDE_PROJECT_DIR\"/.claude/critical-context.txt 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

### 9.2 Robust File Protection Script

```bash
#!/bin/bash
# .claude/hooks/protect-files.sh
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

PROTECTED_PATTERNS=(
  ".env"
  ".env.local"
  ".env.production"
  "package-lock.json"
  "yarn.lock"
  "pnpm-lock.yaml"
  ".git/"
  "*.pem"
  "*.key"
  "credentials"
)

for pattern in "${PROTECTED_PATTERNS[@]}"; do
  if [[ "$FILE_PATH" == *"$pattern"* ]]; then
    echo "Blocked: $FILE_PATH matches protected pattern '$pattern'" >&2
    exit 2
  fi
done

exit 0
```

### 9.3 Safe Stop Hook with Test Verification

```bash
#!/bin/bash
# .claude/hooks/verify-before-stop.sh
INPUT=$(cat)

# Prevent infinite loop
if [ "$(echo "$INPUT" | jq -r '.stop_hook_active')" = "true" ]; then
  exit 0
fi

# Check if there are modified files that need testing
MODIFIED=$(git diff --name-only 2>/dev/null | grep -E '\.(ts|js|py)$' | head -1)
if [ -z "$MODIFIED" ]; then
  exit 0  # No modified files, can stop
fi

# Run tests
if ! npm test 2>&1 > /dev/null; then
  echo '{"decision": "block", "reason": "Tests failing. Fix the tests before finishing."}'
  exit 0
fi

exit 0
```

### 9.4 Complete Audit for Compliance

```json
{
  "hooks": {
    "ConfigChange": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "jq -c '{timestamp: now | todate, event: \"config_change\", source: .source, file: .file_path}' >> ~/claude-audit.log"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -c '{timestamp: now | todate, event: \"bash_command\", command: .tool_input.command}' >> ~/claude-audit.log",
            "async": true
          }
        ]
      }
    ]
  }
}
```

### 9.5 HTTP Hook for Distributed Teams

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "hooks": [
          {
            "type": "http",
            "url": "http://localhost:8080/hooks/tool-use",
            "headers": {
              "Authorization": "Bearer $AUDIT_TOKEN"
            },
            "allowedEnvVars": ["AUDIT_TOKEN"]
          }
        ]
      }
    ]
  }
}
```

For teams that need centralized auditing, a local HTTP service receives all tool usage events. The `Authorization` header uses environment variable interpolation with `allowedEnvVars` for security.

### 9.6 Implementation Checklist

1. Identify enforcement rules in CLAUDE.md that can be converted to hooks
2. For each rule, determine the correct event (Pre/PostToolUse, Stop, etc.)
3. Write the hook script with proper JSON handling
4. Make the script executable (`chmod +x`)
5. Test manually with `echo '{...}' | ./hook.sh; echo $?`
6. Add to settings.json with appropriate matcher
7. Verify with `/hooks` in Claude Code
8. Test in a real scenario and verify with `Ctrl+O` (verbose mode)
9. Remove the corresponding rule from CLAUDE.md
10. Document the hook and its purpose
