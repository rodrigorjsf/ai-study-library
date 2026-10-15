# Analysis: Research on Subagent Best Practices

> **Status**: Current
> **Source document**: [`docs/subagents/research-subagent-best-practices.md`](../subagents/research-subagent-best-practices.md)
> **Analysis date**: 2026-03-27
> **Scope**: Analysis of the research document on subagent best practices, covering delegation patterns, community patterns, anti-patterns, and prompt engineering for agent system prompts

---

## 1. Executive Summary

The research document on subagent best practices is the most comprehensive of the five analyzed documents, compiling information from official Anthropic documentation, community repositories (97k+ stars on everything-claude-code), prompt engineering guides, and emerging ecosystem patterns. It synthesizes 17 sections covering from the official specification to complete agent definition templates, with a practical focus on anti-patterns to avoid and proven success patterns.

The most valuable findings include: (1) the critical importance of the `description` field as the sole routing signal for automatic delegation; (2) the "Confidence-Based Filtering" pattern that reduces noise in subagent outputs; (3) the observation that read-only agents dominate in community repositories; (4) the effective system prompt structure (Role → Process → Checklist → Output Format → Approval Criteria); and (5) the 10 documented anti-patterns representing the most common failures. The document also maps the bidirectional relationship between skills and subagents (`context: fork` in skills vs `skills` field in subagents) and provides model selection analysis with justification by task type.

The unique contribution of this document relative to official documentation is the compilation of community patterns, anti-pattern analysis, and the explicit bridge between subagents and prompt engineering techniques applicable to agent system prompts.

---

## 2. Key Concepts and Mechanisms

### 2.1 Automatic Delegation

Claude decides when to delegate based on three factors:

1. Task description in the user's request
2. `description` field in subagent configurations
3. Current conversation context

To encourage proactive delegation, include phrases like **"use proactively"** in the description field.

### 2.2 Bidirectional Relationship Skills ↔ Subagents

| Approach | System Prompt | Task | Also Loads |
|----------|---------------|------|------------|
| Skill with `context: fork` | From agent type (Explore, Plan, etc.) | SKILL.md content | CLAUDE.md |
| Subagent with `skills` field | Subagent's markdown body | Claude's delegation message | Preloaded skills + CLAUDE.md |

**Skill running in a subagent**:

```yaml
---
name: deep-research
description: Research a topic thoroughly
context: fork
agent: Explore
---
Research $ARGUMENTS thoroughly...
```

**Subagent that loads skills**:

```yaml
---
name: api-developer
description: Implement API endpoints
skills:
  - api-conventions
  - error-handling-patterns
---
```

### 2.3 Dynamic Context Injection

The `` !`<command>` `` syntax in skills executes shell commands before the content is sent to Claude:

```yaml
---
name: pr-summary
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---
## Pull request context
- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`

## Your task
Summarize this pull request...
```

Commands execute immediately (pre-processing); output replaces the placeholder.

### 2.4 Effective System Prompt Structure

Based on analysis of official examples and community patterns:

```
1. Role Definition -- "You are a [specific role] specializing in [domain]"
2. Responsibilities -- Clear bullets of what the agent does
3. Process Steps -- Numbered: gather context -> analyze -> act -> verify -> report
4. Checklist/Criteria -- Categorized by severity (CRITICAL -> LOW)
5. Output Format -- Exact expected format
6. Approval/Success Criteria -- When to approve vs when to flag
```

### 2.5 Model Selection

| Alias | Maps To | Best For |
|-------|---------|----------|
| `haiku` | Claude Haiku 4.5 | Fast tasks, exploration, simple analysis |
| `sonnet` | Claude Sonnet 4.6 | Standard tasks, reviews, daily work |
| `opus` | Claude Opus 4.6 | Complex reasoning, architecture, planning |
| `inherit` | Same as main conversation | Default behavior |
| `sonnet[1m]` | Sonnet with 1M context | Long sessions with large codebases |
| `opus[1m]` | Opus with 1M context | Long sessions with complex reasoning |

**Principle**: Opus for architecture, Sonnet for everything else. Haiku only for mechanical and exploration tasks.

### 2.6 Effort Levels

| Level | Behavior | Best For |
|-------|----------|----------|
| `low` | Minimal thinking, fast responses | Simple, mechanical tasks |
| `medium` | Balanced thinking | Standard tasks |
| `high` | Deep thinking | Complex problems |
| `max` | No thinking token restriction (Opus 4.6 only) | Hardest problems |

### 2.7 Community Patterns (everything-claude-code, 97k+ stars)

| Agent | Model | Tools | Pattern |
|-------|-------|-------|---------|
| `code-reviewer` | sonnet | Read, Grep, Glob, Bash | Read-only with confidence filtering |
| `architect` | opus | Read, Grep, Glob | Read-only with trade-off analysis |
| `security-reviewer` | sonnet | Read, Write, Edit, Bash, Grep, Glob | Full-capability security audit |
| `debugger` | inherit | Read, Edit, Bash, Grep, Glob | Analysis + fix workflow |
| `typescript-reviewer` | implied | Read, Grep, Glob, Bash | Language-specific review |

**Observed patterns**:

1. Read-only agents dominate (majority restricted to Read, Grep, Glob, Bash)
2. Language-specific reviewers with technology-specific checklists
3. Opus reserved for `architect`; Sonnet for everything else
4. Detailed checklists with priority (CRITICAL → LOW)
5. Structured output format with tables and summaries

### 2.8 Confidence-Based Filtering

```markdown
## Confidence-Based Filtering

**IMPORTANT**: Do not flood the review with noise. Apply these filters:

- **Report** if you are >80% confident it is a real issue
- **Skip** stylistic preferences unless they violate project conventions
- **Skip** issues in unchanged code unless they are CRITICAL security issues
- **Consolidate** similar issues
- **Prioritize** issues that could cause bugs, security vulnerabilities, or data loss
```

This pattern significantly reduces noise and makes agent output actionable.

---

## 3. Points of Attention

### 3.1 The 10 Documented Anti-Patterns

| # | Anti-Pattern | Consequence | Mitigation |
|---|-------------|-------------|------------|
| 1 | Aggressive delegation prompts ("CRITICAL: You MUST...") | Overtriggering with Opus 4.6 | Use normal language ("Use this tool when...") |
| 2 | Too many skills/agents | Exceed context budget (2% per skill description) | Monitor via `/context` |
| 3 | Subagents for simple grep operations | Wasted tokens and latency | Guide toward direct tool use |
| 4 | Not restricting tools | Unintended modifications, wasted context | Minimum necessary allowlist |
| 5 | Vague descriptions | Inconsistent or absent delegation | "Use proactively when [trigger]" |
| 6 | God agents (does everything) | Loses purpose of specialization | One domain per agent |
| 7 | No output format specification | Inconsistent and hard-to-use results | Specify exact format in prompt |
| 8 | Ignoring parent context gap | Agent lacks necessary information | Everything in system prompt or via tools |
| 9 | No context gathering step | Analysis without grounding | Always start with "gather context" |
| 10 | No `maxTurns` | Agents run indefinitely consuming tokens | Set reasonable limit (10-30) |

### 3.2 Tool Description Cost in Context

Skill descriptions occupy ~2% of the context window. With many registered agents and skills, this cost accumulates. Use `/context` to check for excess warnings.

### 3.3 Claude Opus 4.6 and Excessive Responsiveness

Opus 4.6 is more responsive to system prompts, meaning aggressive language ("CRITICAL", "YOU MUST", "NEVER") causes overtriggering. The recommendation is to use normal language and trust the model's ability to interpret instructions without artificial emphasis.

### 3.4 Native vs Prescriptive Orchestration

The latest Claude models have native subagent orchestration. Anthropic's recommendation is: "Prefer general instructions over prescriptive steps" — "think thoroughly" often produces better reasoning than manually written step-by-step plans.

### 3.5 Plugin Security

Plugin agents CANNOT use `hooks`, `mcpServers`, or `permissionMode`. Supported fields: `name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, `isolation`.

---

## 4. Use Cases and Scope

### 4.1 Tool Profiles by Agent Type

| Agent Type | Recommended Tools | Justification |
|------------|------------------|---------------|
| Read-only reviewer | Read, Grep, Glob, Bash | Inspects without modifying |
| Code modifier | Read, Edit, Bash, Grep, Glob | Analyzes and fixes |
| Explorer/researcher | Read, Grep, Glob | Pure exploration, no side effects |
| Full-capability | Inherits all | Complex multi-step operations |

### 4.2 When to Use `context: fork` in Skills

- Result-oriented tasks that should run in isolation
- Deep research that would generate excessive output in the main context
- Tasks that benefit from a specific subagent (e.g., Explore for read-only)

### 4.3 When to Use Skill Preloading in Subagents

- Subagents that need specific domain knowledge
- API conventions, error handling patterns, style guides
- When knowledge should be in context from the start (not discovered on demand)

---

## 5. Applicability to Agent Infrastructure

### 5.1 Skills

- **Bidirectional relationship**: Skills can run in subagents (`context: fork`) AND subagents can load skills (`skills` field)
- **Dynamic injection**: `` !`command` `` enables real-time data in skill content
- **Descriptions as cost**: Each skill description consumes ~2% of the context budget
- **Disable-model-invocation**: `true` keeps descriptions out of context until manual invocation
- **Plugin skills**: Plugin skills are invocable by subagents with `plugin-name:skill-name` namespace

### 5.2 Hooks

- **PreToolUse for guardrails**: Command validation before execution (e.g., block SQL write)
- **PostToolUse for quality**: Linter after edits, tests after changes
- **Stop → SubagentStop**: Automatic conversion at runtime
- **SubagentStart/SubagentStop**: Lifecycle hooks in settings.json for setup/cleanup
- **Four types**: `command` (shell), `http` (POST), `prompt` (Claude evaluation), `agent` (verifier subagent)
- **Exit codes**: 0 = allow, 2 = block (stderr becomes feedback to Claude)

### 5.3 Subagents

- **Anti-nesting**: Subagents cannot spawn other subagents
- **Hub-and-spoke**: Results return only to the caller
- **Resumption**: SendMessage with agent ID preserves history
- **Isolation**: worktree for risky operations, automatic cleanup
- **Delegation**: description is the routing signal; "use proactively" improves delegation
- **Agent(type)**: Restricts which subagents can be spawned in `--agent` mode
- **CLI-defined**: JSON via `--agents` for temporary sessions and automation

### 5.4 Rules

- **In subagent context**: `.claude/rules/` loaded normally
- **Path-scoped**: Activated as the subagent reads matching files
- **Plugin-scoped**: Loaded by the subagent along with the plugin
- **Conflicts**: If rules contradict the subagent's system prompt, the system prompt prevails
- **Hierarchy**: Managed > project > user, same order within the subagent

### 5.5 Memory

- **Three scopes**: user (cross-project), project (versionable), local (not committable)
- **MEMORY.md index**: First 200 lines at startup
- **Topic files**: Loaded on demand
- **Prompt instructions**: "Read memory before starting, update after finishing"
- **Automatic curation**: Subagent instructed to curate MEMORY.md if exceeding 200 lines
- **Auto-enable**: Read, Write, Edit automatically enabled when memory is active

---

## 6. Prompt Engineering Guide Applicability

### 6.1 CoT for Subagent Reasoning Chains

The document emphasizes that the subagent's system prompt is ALL it has. CoT in the system prompt improves reasoning quality, especially for reviews and debugging. The recommended structure:

```markdown
When invoked:
1. Gather context -- understand what you're working with
2. Analyze -- apply criteria systematically
3. Reason step by step about each finding
4. Verify -- confirm conclusions with evidence
5. Report -- structured output
```

**Warning**: With Opus 4.6, "think thoroughly" often outperforms prescriptive CoT steps. Explicit CoT is more effective with Sonnet and Haiku.

### 6.2 ReAct for Subagents with Tool Access

The ReAct pattern is the fundamental loop of every subagent with tools. The best community examples (code-reviewer, debugger) implement ReAct implicitly:

1. **Thought**: "I need to understand the recent changes"
2. **Action**: `git diff --staged`
3. **Observation**: Output analysis
4. **Repeat**: Next tool or conclusion

The system prompt should structure the workflow to naturally encourage this cycle.

### 6.3 Tree of Thoughts for Exploration Subagents

Multiple parallel subagents implement distributed ToT:

- Each subagent explores a branch (hypothesis, module, approach)
- The main agent evaluates and synthesizes results
- Natural implementation via: "Research authentication, database, and API modules in parallel using separate subagents"

### 6.4 Self-Consistency for Validation Across Multiple Subagents

The Confidence-Based Filtering pattern is a form of Self-Consistency internal to the subagent. For Self-Consistency across subagents:

- Run multiple review subagents on the same code
- Compare findings: issues reported by multiple runs have higher confidence
- Cost multiplied by the number of executions

### 6.5 Reflexion for Iterative Subagent Improvement

Persistent memory implements cross-session Reflexion:

- Subagent learns from previous reviews (stored in MEMORY.md)
- Recurring patterns are documented and consulted
- Each session improves the knowledge base

Within a session, subagent chaining implements Reflexion:

```
reviewer -> fixer -> reviewer (validation)
```

### 6.6 Least-to-Most for Task Decomposition Across Subagents

The "Explore → Plan → Code → Verify" pattern is a Least-to-Most implementation:

1. Explore subagent (simplest task: map)
2. Plan subagent (intermediate: plan)
3. general-purpose subagent (most complex: implement)
4. Reviewer subagent (final validation)

---

## 7. Correlations with Main Documents

### With "Creating Custom Subagents"

This research document is the direct practical complement to the official documentation. Where the official docs present fields and options, the research provides:

- Concrete community examples (27+ agents from everything-claude-code)
- Anti-patterns not covered by official docs
- Prompt engineering patterns specific to agent system prompts
- Cost analysis by model with justification

### With "Orchestrate Teams of Claude Code Sessions"

Section 15 (Agent Teams vs Subagents) provides the comparative table that aids decision-making. The key point not in the teams documentation: subagents are for focused tasks with summarized results; teams are for complex work with debate.

### With "How Claude Remembers a Project"

Section 11 (Persistent Memory) applies the CLAUDE.md/auto memory mechanisms specifically to subagents. The recommendation of `memory: project` as default aligns with the versioning philosophy from the memory documentation. The 200-line MEMORY.md limit is consistent between both documentations.

### With "Create Plugins"

Section 16 (Plugin-Shipped Agents) documents the security restrictions of agents in plugins. The directory structure (`agents/` in the plugin root) is consistent with plugin architecture. The supported field limitation is unique information from this document.

### With "Research: LLM Context Optimization"

The "attention budget" recommendations map directly to:

- Anti-pattern #2 (too many skills/agents consume context budget)
- Anti-pattern #4 (tool descriptions of unused tools)
- Model selection principle (haiku for simple tasks = lower token cost)
- Confidence-Based Filtering (reduces wasted output tokens)

The "lost in the middle" principle implies that system prompt structure matters: critical information at the beginning and end.

---

## 8. Strengths and Limitations

### Strengths

1. **Comprehensiveness**: 17 sections covering from official specification to community patterns
2. **Practicality**: Concrete anti-patterns with mitigations
3. **Complete template**: Appendix A with ready-to-use agent definition template
4. **Community data**: 97k+ stars from everything-claude-code validate the patterns
5. **Skills-subagents bridge**: Clear documentation of the bidirectional relationship
6. **Model selection table**: Justification by task type
7. **Confidence-Based Filtering**: Replicable pattern for any review agent
8. **Prompt engineering for agents**: Dedicated section with Anthropic principles

### Limitations

1. **Dating**: March 2026 date — experimental features may have changed
2. **No quantitative benchmarks**: No comparative performance metrics between patterns
3. **Focus on review/analysis**: Most examples are for review agents, with less coverage of implementation agents
4. **Absence of testing**: No section on how to systematically test subagents
5. **Community as source**: Community patterns may not reflect official best practices
6. **No real cost analysis**: Model recommendations are qualitative, without per-task cost data

---

## 9. Practical Recommendations

### 9.1 Checklist for Subagent Creation

```
[ ] name: unique identifier, lowercase with hyphens
[ ] description: includes "Use proactively when..." or "Use after..."
[ ] tools: minimum necessary (prefer Read, Grep, Glob, Bash for read-only)
[ ] model: sonnet as default, haiku for exploration, opus for architecture
[ ] maxTurns: defined (10-30 for most scenarios)
[ ] System prompt: follows Role -> Process -> Checklist -> Output Format
[ ] Confidence filter: included for review agents
[ ] Memory: defined if cross-session learning is valuable
[ ] Tested: manually invoked and output verified
```

### 9.2 Review Agent Pattern with Confidence Filtering

```markdown
---
name: domain-reviewer
description: >-
  [Domain] review specialist. Use proactively after changes to [scope].
tools: Read, Grep, Glob, Bash
model: sonnet
memory: project
maxTurns: 20
---

You are a [domain] specialist reviewing code for [criteria].

## Process
1. Run `git diff --staged` to see changes
2. Read agent memory for known patterns
3. Review each file against checklist
4. Apply confidence filter
5. Report findings in structured format
6. Update memory with new patterns

## Checklist
### Critical
- [Must-flag items]

### High
- [Should-flag items]

## Confidence Filter
- Report only if >80% confident
- Skip stylistic preferences unless violating conventions
- Consolidate similar issues
- Prioritize bugs, security, data loss

## Output Format
[SEVERITY] Issue title
File: path/to/file:line
Issue: Description
Fix: Suggested fix
```

### 9.3 Model Selection Strategy for the Project

```
Simple rule:
- Exploration, search, mechanical tasks -> haiku
- Reviews, debugging, implementation -> sonnet
- Architecture, complex planning -> opus
- When in doubt -> sonnet (best cost/quality ratio)
```

### 9.4 Migrating from Plugin Agent to Project Agent

When a plugin agent needs `hooks`, `mcpServers`, or `permissionMode`:

```bash
# Copy from plugin directory to project
cp path/to/plugin/agents/reviewer.md .claude/agents/reviewer.md

# Add restricted fields in frontmatter
# hooks:, mcpServers:, permissionMode: now work
```

### 9.5 Automating Context Budget Verification

Periodically run `/context` to verify whether skills and agents are consuming excessive budget. If warnings appear:

1. Reduce number of registered agents
2. Use `disable-model-invocation: true` on non-essential skills
3. Move rarely used skills to manual invocation
4. Consolidate agents with overlapping domains
