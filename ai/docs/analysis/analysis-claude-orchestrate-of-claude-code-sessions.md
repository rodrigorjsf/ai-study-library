# Analysis: Orchestrating Agent Teams in Claude Code

> **Status**: Current
> **Source document**: [claude-orchestrate-of-claude-code-sessions.md](https://docs.anthropic.com/en/docs/claude-code/agent-teams)
> **Analysis date**: 2025-06-01
> **Scope**: Experimental agent teams mechanism — peer-to-peer coordination, shared task lists, team hooks, and comparison with traditional subagents

---

## 1. Executive Summary

The document on agent team orchestration (Agent Teams) describes an experimental Claude Code mechanism (v2.1.32+) that enables coordinating multiple Claude Code instances working in parallel. Unlike traditional subagents — which operate in a hub-and-spoke model reporting results only to the main agent — agent teams implement peer-to-peer communication between teammates, with a shared task list and self-coordination. The architecture consists of a team lead (main session), teammates (independent instances), task list (shared list with pending/in-progress/completed states and dependencies), and mailbox (inter-agent messaging system).

Token cost scales linearly with the number of teammates, as each one has its own context window. Anthropic recommends starting with 3-5 teammates and 5-6 tasks per teammate. Best use cases include parallel research, independent features, debugging with competing hypotheses, and cross-layer coordination (frontend/backend/tests). The mechanism introduces specific hooks (`TeammateIdle`, `TaskCompleted`) that enable automated quality gates.

The main architectural implication is that agent teams solve the inter-worker communication problem that subagents cannot solve, at the cost of greater complexity and token consumption. The decision between subagents and agent teams should be guided by the need for inter-worker communication: if workers only need to report results, subagents suffice; if they need to debate, challenge, and coordinate with each other, agent teams are the right choice.

---

## 2. Key Concepts and Mechanisms

### 2.1 Team Architecture

| Component | Function | Analogy |
|-----------|----------|---------|
| **Team Lead** | Main session that creates the team, spawns teammates, and coordinates work | Project manager |
| **Teammates** | Independent Claude Code instances with their own context | Specialized developers |
| **Task List** | Shared list with states and dependencies | Kanban board |
| **Mailbox** | Inter-agent messaging system | Team Slack |

### 2.2 Team Lifecycle

```
1. User requests team creation with task description
2. Lead analyzes and creates task list with dependencies
3. Lead spawns teammates with specific prompts
4. Teammates auto-claim tasks (file locking prevents race conditions)
5. Teammates communicate directly via messages
6. Lead synthesizes results
7. Lead requests teammate shutdown
8. Lead performs cleanup of shared resources
```

### 2.3 Display Modes

- **In-process**: all teammates run in the same terminal; `Shift+Down` to navigate
- **Split panes**: each teammate in a separate pane via tmux or iTerm2

### 2.4 Task Coordination

Tasks have three states (pending, in progress, completed) and support dependencies. The system automatically unblocks tasks when dependencies are completed. File locking prevents multiple teammates from attempting to claim the same task simultaneously.

### 2.5 Quality Control via Hooks

```json
{
  "hooks": {
    "TeammateIdle": [
      {
        "hooks": [
          { "type": "command", "command": "./scripts/check-teammate-output.sh" }
        ]
      }
    ],
    "TaskCompleted": [
      {
        "hooks": [
          { "type": "command", "command": "./scripts/validate-task-quality.sh" }
        ]
      }
    ]
  }
}
```

- `TeammateIdle`: executes when a teammate is about to become idle; exit code 2 sends feedback and keeps the teammate working
- `TaskCompleted`: executes when a task is to be marked as complete; exit code 2 prevents completion

### 2.6 Plan Approval

For critical tasks, it is possible to require teammates to plan before implementing:

```text
Spawn an architect teammate to refactor the authentication module.
Require plan approval before they make any changes.
```

The lead approves or rejects the plan autonomously based on criteria provided by the user.

---

## 3. Points of Attention

### 3.1 Token Cost

**The greatest operational risk.** Each teammate consumes tokens independently. With 5 teammates, the cost can be 5-6x higher than a single session (coordination overhead included). There is no inter-team compaction mechanism — each window is independent.

### 3.2 File Conflicts

Two teammates editing the same file causes overwriting. The documentation is explicit: "Break the work so each teammate owns a different set of files." There is no automatic merge or conflict detection.

### 3.3 Critical Experimental Limitations

- **No session resume**: `/resume` and `/rewind` do not restore in-process teammates
- **Task status can become stale**: teammates sometimes do not mark tasks as completed
- **One team per session**: it is not possible to manage multiple teams simultaneously
- **No nested teams**: teammates cannot spawn their own teams
- **Lead is fixed**: leadership cannot be transferred
- **Shutdown can be slow**: teammates finish the current request before stopping
- **Split panes do not work in VS Code terminal, Windows Terminal, or Ghostty**

### 3.4 The Lead-That-Implements Trap

The lead may start implementing tasks instead of delegating. Mitigation: "Wait for your teammates to complete their tasks before proceeding."

### 3.5 Context Budget

Each teammate loads CLAUDE.md, MCP servers, and skills on startup — but does NOT inherit the lead's conversation history. The spawn prompt must contain all necessary context for the task.

---

## 4. Use Cases and Scope

### 4.1 When to Use Agent Teams

| Scenario | Suitability | Justification |
|----------|-------------|---------------|
| Parallel code review (security + performance + tests) | High | Independent lenses, valuable synthesis |
| Debugging with competing hypotheses | High | Active debate prevents anchoring bias |
| Independent features in distinct modules | High | Each teammate owns distinct files |
| Frontend/backend/tests coordination | High | Cross-layer with manageable dependencies |
| Sequential tasks with strong dependencies | Low | Coordination overhead outweighs benefit |
| Edits to the same file | Low | Overwrite conflicts |
| Simple and quick tasks | Low | Disproportionate token cost |

### 4.2 Decision Criteria: Subagents vs Agent Teams

```
Question 1: Do the workers need to communicate with each other?
  NO → Subagents
  YES → Question 2

Question 2: Does the work involve debating/challenging findings?
  NO → Subagents with synthesis by the main agent
  YES → Agent Teams

Question 3: Is the token cost acceptable (5-6x)?
  NO → Subagents with sequential execution
  YES → Agent Teams
```

---

## 5. Applicability to Agent Infrastructure

### 5.1 Skills

- **Skills that delegate to subagents**: Agent teams are an alternative when the skill requires multiple coordinated perspectives (e.g., a design review skill that spawns architect + UX + devil's advocate)
- **Plugin-provided skills**: Plugin skills can initiate agent teams if the plugin is enabled and the experimental flag is active
- **Memory-informed skills**: Each teammate loads CLAUDE.md and auto memory independently, allowing memory-based skills to function in each context separately

### 5.2 Hooks

- **Hooks in agent team context**: `TeammateIdle` and `TaskCompleted` are hooks exclusive to agent teams, with no equivalent in subagents
- **Memory-triggered hooks**: No direct support, but `PostToolUse` can be used to trigger memory updates when teammates complete tasks
- **Plugin lifecycle hooks**: Plugin hooks are loaded by each teammate in the same way as in normal sessions

### 5.3 Subagents

- **Orchestration pattern**: Agent teams implement the Anthropic Orchestrator-Workers pattern with added peer-to-peer communication
- **Delegation**: The lead delegates via task list (not via Agent tool as with subagents); teammates auto-claim
- **Result synthesis**: The lead synthesizes findings from multiple teammates — different from subagents where each result returns individually
- **Parallel execution**: Agent teams are natively parallel with coordination; subagents can run in parallel but without communication
- **Worktree isolation**: Each teammate can operate in a separate worktree, but the feature is not explicitly documented for teams (only subagents have `isolation: worktree`)

### 5.4 Rules

- **Rules in teammate context**: Each teammate loads `.claude/rules/` like a normal session
- **Plugin-scoped rules**: Plugin rules are loaded normally by each teammate
- **Memory-informed rules**: Path-scoped rules are activated independently by each teammate as they work on different files

### 5.5 Memory

- **Memory architecture**: Each teammate has its own context window and loads auto memory independently
- **Indexing**: MEMORY.md (first 200 lines) is loaded at startup of each teammate
- **On-demand loading**: Memory topic files are loaded on-demand by each teammate
- **Cross-session persistence**: Limited — `/resume` does not restore teammates; however, auto memory persists between sessions
- **Memory hygiene**: With multiple teammates writing to auto memory simultaneously, there is risk of conflicts or redundancy

---

## 6. Applicability of the Prompt Engineering Guide

### 6.1 CoT for Subagent Reasoning Chains

Agent teams benefit from CoT in each teammate's spawn prompt: "Walk through the problem step by step before proposing solutions." CoT helps teammates ground their reasoning before communicating findings to the team, reducing noise in inter-agent communication.

### 6.2 ReAct for Subagents with Tool Access

Each teammate operates in a native ReAct loop (Thought → Action → Observation). The spawn prompt should encourage the explicit cycle: "First explore the relevant files, analyze the patterns, and only then propose changes." This is especially important because teammates do not inherit context from the lead.

### 6.3 Tree of Thoughts for Exploration Subagents

The "debugging with competing hypotheses" use case is a natural implementation of distributed Tree of Thoughts: each teammate explores a branch of the hypothesis tree. The debate between teammates functions as the evaluation and backtracking mechanism of ToT.

**Practical example**:

```text
Spawn 5 teammates to investigate different hypotheses about the crash.
Have them talk to each other to try to disprove each other's theories.
```

Each teammate is a node in the tree; peer-to-peer communication implements cross-evaluation.

### 6.4 Self-Consistency for Validation Across Multiple Subagents

Agent teams implement Self-Consistency naturally when multiple teammates investigate the same problem and converge (or diverge). The lead can synthesize via majority voting: if 3 out of 5 teammates point to the same root cause, confidence in the conclusion increases.

### 6.5 Reflexion for Iterative Subagent Improvement

The `TaskCompleted` and `TeammateIdle` hooks partially implement Reflexion: the hook can reject the conclusion (exit code 2), forcing the teammate to reflect and iterate. Combined with plan approval, this creates a generate → evaluate → refine loop.

### 6.6 Least-to-Most for Task Decomposition Across Subagents

The task list with dependencies naturally implements Least-to-Most: simple tasks are completed first, unblocking more complex tasks that depend on them. The lead can decompose a complex problem into subtasks ordered by dependency.

---

## 7. Correlations with Core Documents

### With "Creating Custom Subagents"

The relationship is one of direct complementarity. Subagents are for focused tasks with results reported to the caller; agent teams are for complex work with communication. The comparison table in the document is essential for decision-making. Individual subagents within agent teams inherit the same isolated context model as custom subagents.

### With "Research: Subagent Best Practices"

The best practices document emphasizes that subagents cannot spawn other subagents. Agent teams overcome this limitation by allowing direct communication between teammates, but at a higher cost. The documented anti-patterns (god agents, vague descriptions) apply equally to teammate spawning.

### With "How Claude Remembers a Project"

Agent teams load CLAUDE.md and auto memory in the same way as normal sessions. The critical limitation is that teammates do not inherit the lead's history, requiring the spawn prompt to contain all necessary context. Auto memory can be updated by multiple teammates, creating a risk of conflict.

### With "Create Plugins"

Plugins are loaded normally by each teammate. Plugin skills can be invoked in a team context. Plugin hooks (`TeammateIdle`, `TaskCompleted`) offer extensibility specific to agent teams.

### With "Research: LLM Context Optimization"

The most critical relationship is with the concept of "context rot." Each teammate starts with a clean context (preventing context rot), but the cost is linear. The Anthropic "attention budget" concept implies that the total attention cost of a team is the sum of individual budgets, with no efficient sharing.

---

## 8. Strengths and Limitations

### Strengths

1. **Peer-to-peer communication** solves problems that hub-and-spoke subagents cannot
2. **Shared task list** with dependencies and auto-claiming offers robust coordination
3. **File locking** prevents race conditions in task claiming
4. **Dedicated hooks** (TeammateIdle, TaskCompleted) enable automated quality gates
5. **Plan approval** provides a human-in-the-loop checkpoint before implementation
6. **Clean context per teammate** prevents context rot
7. **Adversarial debate** between teammates combats anchoring bias in debugging

### Limitations

1. **Experimental status** with significant limitations (no resume, one team per session)
2. **Linear token cost** with number of teammates (5x for 5 teammates)
3. **No automatic merge** for file conflicts
4. **Fixed lead** with no possibility of transfer
5. **No nested teams** (teammates cannot create sub-teams)
6. **Limited compatibility** for split panes (does not work in VS Code, Windows Terminal)
7. **Risk of stale task status** when teammates do not mark tasks as complete

---

## 9. Practical Recommendations

### 9.1 Getting Started with Agent Teams

1. **Start with research and review** (no code writing) to understand the dynamics
2. **Use 3 teammates** on the first experience; scale only when value is demonstrated
3. **Define detailed spawn prompts** including relevant files, criteria, and expected format
4. **Monitor actively** — check teammate progress regularly

### 9.2 Preventing Conflicts

```text
# Good: each teammate owns distinct modules
Teammate A: src/auth/ (all files)
Teammate B: src/api/ (all files)
Teammate C: tests/ (all files)

# Bad: multiple teammates in the same directory
Teammate A: src/auth/login.ts
Teammate B: src/auth/session.ts  # risk if they touch the same file
```

### 9.3 Quality Control

Implement `TaskCompleted` hooks with validation scripts:

```bash
#!/bin/bash
# validate-task-quality.sh
INPUT=$(cat)
TASK_NAME=$(echo "$INPUT" | jq -r '.task_name // empty')

# Run relevant tests
npm test -- --related 2>&1
if [ $? -ne 0 ]; then
  echo "Tests failed for task: $TASK_NAME" >&2
  exit 2  # Block task completion
fi
exit 0
```

### 9.4 Cost Optimization

- Use `sonnet` as the default model for teammates (not `opus`)
- Limit the number of tasks per teammate to 5-6
- Prefer subagents when inter-worker communication is not necessary
- Consider agent teams only when the benefit of parallelism + debate justifies the cost

### 9.5 Integration with Existing Infrastructure

- Add team-specific instructions to the project's `CLAUDE.md`
- Create skills that encapsulate common team creation patterns
- Use `SubagentStart`/`SubagentStop` hooks in `settings.json` for logging and metrics
- Document in auto memory the team patterns that worked well for the project
