# Analysis: Extend Claude with Skills

> **Status**: Current
> **Source document**: [Anthropic — Extend Claude with Skills](docs/skills/extend-claude-with-skills.md)
> **Analysis date**: 2026-03-27
> **Scope**: Analysis of Claude Code skills extensibility system and SKILL.md specification

---

## 1. Executive Summary

The document "Extend Claude with Skills" is the official Anthropic documentation that defines the Claude Code extensibility system through skills. It establishes the SKILL.md format as the fundamental unit of extension, following the open Agent Skills standard (agentskills.io), and details the entire chain from creating a simple skill to advanced patterns such as dynamic context injection and sub-agent execution. The document serves as the canonical reference for anyone looking to extend Claude Code's capabilities.

The strategic importance of this document lies in positioning skills as the primary progressive disclosure mechanism of Claude Code. Unlike CLAUDE.md (which is loaded in its entirety at startup), skills load only the description at the beginning of the session and the full content only on demand. This directly solves the "context rot" problem documented by Anthropic — the performance degradation as context grows. Skills are, therefore, the architectural solution to the dilemma between instruction richness and context efficiency.

The document also reveals the convergence between skills and the broader ecosystem of plugins, sub-agents, and hooks, positioning skills as the intermediate layer between static instructions (CLAUDE.md/rules) and deterministic automations (hooks). The integration with `context: fork`, `allowed-tools`, and `hooks` in the frontmatter shows that skills are not merely instruction documents, but complete orchestration units.

---

## 2. Key Concepts and Mechanisms

### 2.1 SKILL.md Format and Frontmatter

The core format is a Markdown file with YAML frontmatter:

```yaml
---
name: my-skill
description: What this skill does and when to use it
disable-model-invocation: true
allowed-tools: Read, Grep
context: fork
agent: Explore
---

Instructions in Markdown here...
```

**Frontmatter fields and their implications:**

| Field | Context Impact | Behavioral Impact |
|-------|---------------|-------------------|
| `name` | Minimal (~10 tokens) | Defines the `/name` command |
| `description` | Loaded at startup (if model-invocable) | Determines auto-discovery by Claude |
| `disable-model-invocation` | Removes description from context | Prevents automatic invocation |
| `user-invocable` | Keeps description in context | Removes from `/` menu |
| `allowed-tools` | None | Grants permissions during execution |
| `context` | Fork isolates completely | Creates sub-agent with its own context |
| `agent` | Determines sub-agent system prompt | Defines available tools and model |
| `model` | No direct impact | Model override for the skill |
| `effort` | No direct impact | Controls effort level (low to max) |
| `hooks` | None | Automations in the skill lifecycle |

### 2.2 Three-Level Loading Model

The document reveals a three-level progressive disclosure model:

1. **Metadata** (~100 tokens): `name` + `description` — loaded at startup for ALL model-invocable skills
2. **Instructions** (SKILL.md body): Loaded on demand when the skill is invoked
3. **Resources** (supporting files): Loaded on demand by Claude when needed

This model is directly aligned with the concept of "just in time documentation" described in the context optimization document.

### 2.3 Location Hierarchy and Priority

```
Enterprise (highest priority)
  > Personal (~/.claude/skills/)
    > Project (.claude/skills/)
      > Plugin (namespace plugin-name:skill-name)
```

**Critical point**: Plugins use a prefixed namespace, avoiding conflicts. However, enterprise, personal, and project skills compete for the same namespace — the highest priority one wins silently.

### 2.4 Variable Substitution

The system supports dynamic substitutions:

- `$ARGUMENTS` / `$ARGUMENTS[N]` / `$N` — positional arguments
- `${CLAUDE_SESSION_ID}` — session identifier
- `${CLAUDE_SKILL_DIR}` — skill directory (crucial for bundled scripts)

### 2.5 Dynamic Context Injection

The `` !`<command>` `` syntax is a preprocessing mechanism that executes shell commands BEFORE sending to Claude:

```yaml
---
name: pr-summary
context: fork
agent: Explore
---

- PR diff: !`gh pr diff`
- Changed files: !`gh pr diff --name-only`
```

This transforms skills into real-time data pipelines, not just static documents.

### 2.6 Sub-Agent Execution (context: fork)

When `context: fork` is active:

1. An isolated context is created (zero impact on the main context)
2. The SKILL.md body becomes the sub-agent's prompt
3. The `agent` field defines the execution environment (Explore, Plan, general-purpose, or custom agent)
4. Results are summarized and returned to the main context

**Critical difference between the two directions:**

| Approach | System Prompt | Task | Also Loads |
|----------|--------------|------|------------|
| Skill with `context: fork` | From agent type | SKILL.md body | CLAUDE.md |
| Sub-agent with `skills` field | Sub-agent's markdown body | Delegation message | Preloaded skills + CLAUDE.md |

### 2.7 Character Budget for Descriptions

The document reveals a critical limitation: skill descriptions share a character budget that scales to 2% of the context window, with a fallback of 16,000 characters. This means that with many skills, some may be excluded from context. The `/context` command allows checking for warnings about excluded skills, and the `SLASH_COMMAND_TOOL_CHAR_BUDGET` variable allows override.

---

## 3. Points of Attention

### 3.1 Common Errors in Skill Authoring

1. **Vague descriptions**: "Helps with files" does not trigger auto-discovery. The description must contain keywords that the user would naturally say.

2. **Reference skills with `context: fork`**: The document explicitly warns — skills with `context: fork` require actionable instructions. If the skill contains only guidelines without a task, the sub-agent receives the guidelines but has no actionable prompt.

3. **Confusion between `disable-model-invocation` and `user-invocable`**: `user-invocable: false` does NOT block access via the Skill tool — it only hides from the `/` menu. To block programmatic invocation, `disable-model-invocation: true` is required.

4. **Excess model-invocable skills**: Each model-invocable skill consumes description budget. A project with 50+ skills may exceed the 16K character limit.

5. **Excessively long SKILL.md**: The document recommends keeping it under 500 lines, moving reference material to separate files.

### 3.2 Context Pitfalls

- **Descriptions always in context**: For model-invocable skills, the description is ALWAYS in context, consuming attention budget even when the skill is not used.
- **context: fork loads CLAUDE.md**: Even in isolated execution, the sub-agent loads CLAUDE.md — conflicting instructions in CLAUDE.md can affect skill behavior.
- **Uncaptured arguments**: If `$ARGUMENTS` does not appear in the body, arguments are APPENDED to the end as `ARGUMENTS: <value>` — potentially misaligning instructions.

### 3.3 Testing Gaps

- There is no built-in mechanism for testing/validating skills
- There is no way to view the final rendered prompt (after substitutions and dynamic injection)
- There are no metrics on how many times a skill is invoked automatically vs manually
- Auto-discovery behavior depends on description quality, which can only be tested empirically

---

## 4. Use Cases and Scope

### 4.1 When to Create a Skill vs Alternatives

| Need | Ideal Mechanism | Justification |
|------|----------------|---------------|
| Short persistent knowledge (<5 lines) | Rule (.claude/rules/) | Zero overhead, always in context |
| Medium persistent knowledge (5-50 lines) | CLAUDE.md | Loaded at startup, no invocation needed |
| On-demand knowledge (50-500 lines) | **Skill** | Progressive disclosure, JIT loading |
| Extensive knowledge with sub-documents | **Skill + supporting files** | Two-level disclosure hierarchy |
| Workflow with side effects | **Skill with `disable-model-invocation`** | Manual timing control |
| Isolated task with specific tools | **Skill with `context: fork`** | Context isolation |
| Deterministic automation | Hook | Guaranteed execution, no LLM |
| Post-action validation | Hook (post-tool) | Does not depend on model attention |

### 4.2 Examples of Skill Categories

**Reference Skills** (model-invocable, inline):

- Project API conventions
- Code style patterns
- Domain-specific knowledge

**Task Skills** (disable-model-invocation, inline or fork):

- Deploy (`/deploy`)
- Formatted commit (`/commit`)
- PR creation (`/create-pr`)

**Research Skills** (context: fork, agent: Explore):

- Codebase investigation (`/deep-research`)
- PR analysis (`/pr-summary`)
- Interactive documentation

**Visualization Skills** (inline, with bundled scripts):

- Codebase visualization
- Dependency graphs
- Interactive HTML reports

---

## 5. Applicability to Agent Infrastructure

### 5.1 Skills (Design Patterns, Composition, and Evolution)

**Fundamental design patterns identified:**

1. **Simple Skill**: SKILL.md with direct instructions, no supporting files
2. **Skill with Reference**: SKILL.md as index + reference files per domain
3. **Skill with Scripts**: SKILL.md with instructions + bundled executable scripts
4. **Skill as Pipeline**: `context: fork` + dynamic injection + agent type
5. **Skill as Orchestrator**: Instructions that delegate to multiple sub-agents

**Composition strategies:**

- **Manual chaining**: A skill instructs the user to invoke another after completion
- **Delegation to sub-agent with preloaded skills**: Sub-agent defined in `.claude/agents/` with a `skills` field that preloads relevant skills
- **Skills as plugin building blocks**: Plugin groups related skills with a shared namespace

**Evolution strategies:**

- Start with a simple, inline SKILL.md
- When exceeding 200 lines, extract into supporting files
- When side effects are critical, add `disable-model-invocation: true`
- When the main context is saturated, migrate to `context: fork`
- When complexity increases, create a plugin with multiple skills

**Reference skill template:**

```yaml
---
name: api-conventions
description: REST API conventions for this project. Use when creating or modifying endpoints, HTTP handlers, or API routes.
---

# API Conventions

## Response Pattern

All endpoints return:
- 200: Success with JSON body
- 400: Validation error with `{ error: string, fields: Record<string, string> }`
- 500: Internal error with `{ error: "Internal server error" }`

## Additional Resources

- Complete schemas: [reference/schemas.md](reference/schemas.md)
- Endpoint examples: [reference/examples.md](reference/examples.md)
```

**Task skill template with fork:**

```yaml
---
name: investigate-issue
description: Investigates a GitHub issue in depth
context: fork
agent: Explore
disable-model-invocation: true
allowed-tools: Bash(gh *), Read, Grep, Glob
---

# Issue Investigation

Investigate GitHub issue #$ARGUMENTS:

1. Read the complete issue: !`gh issue view $ARGUMENTS`
2. Identify relevant files using Grep and Glob
3. Analyze related code
4. Produce a report with:
   - Probable root cause
   - Affected files (absolute paths)
   - Recommended fix strategy
```

### 5.2 Hooks (Complement to Skills)

Skills and hooks are complementary:

- **Pre-skill hooks**: The `hooks` field in the frontmatter allows defining hooks that execute before/after the skill lifecycle
- **Hooks as enforcement**: Where CLAUDE.md/skills are "advisory" (the model can ignore them), hooks are deterministic
- **Converting instructions to hooks**: As documented in the context optimization research, "if Claude already does something correctly without the instruction, delete it or convert to a hook"

**Example of hook scoped to a skill:**

```yaml
---
name: deploy
description: Deploy to production
disable-model-invocation: true
hooks:
  PreToolExecution:
    - matcher: Bash
      hooks:
        - command: "echo 'Deploy started at $(date)' >> deploy.log"
---
```

### 5.3 Sub-Agents (context: fork and Composition)

The document establishes two skill–sub-agent integration flows:

**Skill → Sub-Agent (context: fork):**

- The skill DEFINES the task
- The agent type DEFINES the environment
- Ideal for self-contained tasks with a defined result

**Sub-Agent → Skills (preloaded skills):**

- The sub-agent (`.claude/agents/`) DEFINES the system prompt
- Preloaded skills provide reference knowledge
- Ideal for specialized agents that need multiple skills

**Composition patterns with sub-agents:**

```yaml
# Skill that uses Explore sub-agent for research
---
name: codebase-audit
description: Auditoria completa do codebase
context: fork
agent: Explore
---

# Codebase Audit
1. Use Glob to map the entire structure
2. Use Grep to identify problematic patterns
3. Generate report with prioritized findings
```

```markdown
# Sub-agent that preloads skills (.claude/agents/security-reviewer.md)
---
skills:
  - owasp-security
  - api-conventions
allowed-tools: Read, Grep, Glob
---

You are a specialized security reviewer.
Analyze the code using the loaded conventions.
```

### 5.4 Rules (Complement and Substitute for Skills)

**Rules that reference skills:**

```markdown
# .claude/rules/api-development.md
---
paths:
  - "src/api/**/*.ts"
---

When creating API endpoints, invoke the `api-conventions` skill for pattern reference.
```

**When rules substitute skill content:**

- Short, universal instructions (<5 lines) → Rule
- Path-conditional instructions → Rule with `paths`
- Instructions that MUST be followed without exception → Rule (always in context when path matches)

**When skills substitute rules:**

- Extensive content (>50 lines) → Skill (avoids polluting context)
- On-demand content → Skill (JIT loading)
- Content with interactive workflows → Skill

### 5.5 Memory (Skills That Use and Generate Memory)

**Memory-informed skills:**

- A skill can instruct Claude to read `~/.claude/projects/<project>/memory/` before acting
- Auto-memory may contain preferences that influence skill behavior

**Skills that generate memory:**

- A workflow skill can instruct Claude to record decisions in auto-memory
- Audit skills can generate persistent findings via memory

**Example:**

```yaml
---
name: session-logger
description: Records session activities
---

Before executing any action, check previous notes in memory/:
- If there are pending decisions, list them for the user
- After each significant action, update the notes

Session log ${CLAUDE_SESSION_ID}: $ARGUMENTS
```

---

## 6. Applicability of the Prompt Engineering Guide

### 6.1 Chain-of-Thought (CoT) for Multi-Step Phases

Skills with multi-step workflows benefit from explicit CoT. According to the guide, CoT improves from 17.9% to 58.1% on reasoning tasks in GSM8K. For analysis skills:

```yaml
---
name: code-analysis
description: Deep code quality analysis
---

Analyze the code in $ARGUMENTS following this chain of reasoning:

1. **Comprehension**: Read the code and describe what it does in one sentence
2. **Structure**: Identify design patterns and dependencies
3. **Problems**: For each potential problem, explain:
   - What is wrong
   - Why it is problematic
   - How to fix it
4. **Prioritization**: Order problems by severity
5. **Recommendation**: Summarize the 3 most impactful actions
```

### 6.2 ReAct for Tool-Using Skills

The ReAct pattern (Thought → Action → Observation) is natural for skills that use tools. The guide documents a +34% success rate improvement on ALFWorld with ReAct:

```yaml
---
name: debug-issue
description: Interactive problem debugging
allowed-tools: Read, Grep, Glob, Bash(npm test *)
---

Follow the ReAct loop to debug $ARGUMENTS:

For each iteration:
1. **Thought**: What hypothesis am I testing? What evidence do I need?
2. **Action**: Execute a tool to collect evidence
3. **Observation**: What does the result tell me?

Repeat until:
- Root cause identified with concrete evidence
- Proposed fix verified by test
```

### 6.3 Tree of Thoughts (ToT) for Complex Decision Skills

For skills involving planning or decisions with multiple valid paths, ToT offers an 18.5x improvement over CoT (Game of 24). Applicable to architecture skills:

```yaml
---
name: architecture-decision
description: Structured evaluation of architectural decisions
context: fork
---

For the architectural decision about $ARGUMENTS:

1. **Generate 3 viable alternatives** (each with explicit trade-offs)
2. **Evaluate each alternative** on the axes:
   - Implementation complexity (1-5)
   - Long-term maintainability (1-5)
   - Expected performance (1-5)
   - Alignment with current stack (1-5)
3. **Eliminate** alternatives with score < 12
4. **Deep-dive** into remaining alternatives with risk analysis
5. **Recommend** with justification based on scores
```

### 6.4 Least-to-Most for Decomposition Skills

For skills that decompose complex problems into subproblems:

```yaml
---
name: refactor-module
description: Guided refactoring of complex modules
---

To refactor $ARGUMENTS:

1. **Identify the simplest problem**: What is the smallest change that improves the code?
2. **Solve it first**: Implement and verify
3. **Identify the next problem**: Now that the simplest is solved, what's next?
4. **Repeat** until the module is refactored
5. **Verify** that all tests pass after each change
```

### 6.5 Self-Consistency for Validation Skills

For skills that require high reliability, Self-Consistency (+12-18% over CoT) can be simulated:

```yaml
---
name: security-audit
description: Security audit with cross-validation
context: fork
---

To audit $ARGUMENTS:

1. **Analysis 1 (OWASP Top 10)**: Check each category
2. **Analysis 2 (Attack surface)**: Identify entry points and data flows
3. **Analysis 3 (Dependencies)**: Check for known vulnerabilities

4. **Consolidation**: Compare findings from all three analyses
   - Findings present in 2+ analyses: CONFIRMED
   - Findings in only 1 analysis: REQUIRES INVESTIGATION
5. **Final report**: Only confirmed critical/high findings
```

### 6.6 Reflexion for Iterative Improvement Skills

For skills that improve output through iteration:

```yaml
---
name: improve-docs
description: Iterative documentation improvement
---

To improve the documentation in $ARGUMENTS:

Improvement cycle (maximum 3 iterations):
1. **Generate**: Write/improve the documentation
2. **Critique**: Evaluate against criteria:
   - Completeness (are all parameters documented?)
   - Clarity (would a new developer understand?)
   - Examples (are there practical examples?)
3. **Reflect**: What can be improved?
4. If score < 8/10, **repeat** focusing on weak points
5. If score >= 8/10, finalize
```

---

## 7. Correlations with Core Documents

### 7.1 With research-context-engineering-comprehensive.md

| Concept in Research | Implementation in Skills |
|---------------------|------------------------|
| "Context rot" — degradation with more tokens | Skills load content JIT, minimizing tokens in context |
| Finite "attention budget" | `disable-model-invocation` removes descriptions from the budget |
| "Lost in the middle" effect | SKILL.md is read from start to finish as a focused unit |
| Progressive disclosure in 3 levels | Metadata → SKILL.md → supporting files |
| "Just in time documentation" | Skills ARE the primary implementation of this concept |
| Instructions under 200 lines | Recommendation of SKILL.md under 500 lines (more permissive since it's JIT) |
| Sub-agents for context isolation | `context: fork` implements sub-agent with isolated context |
| Hooks as deterministic enforcement | `hooks` field in frontmatter enables hooks scoped to skills |

### 7.2 With skill-authoring-best-practices.md

The best practices document details the "how" of what "extend-claude-with-skills" defines as the "what":

- Naming: gerund preferred (processing-pdfs vs pdf-processor)
- Descriptions: third person, specific, with trigger keywords
- Progressive disclosure: SKILL.md as table of contents, references one level deep
- Workflows with checklists for complex skills
- Feedback loops (validate → fix → repeat)

### 7.3 With research-claude-code-skills-format.md

The research document complements with:

- Agent Skills Open Standard format vs Claude Code extensions
- Name validation rules (1-64 chars, kebab-case, no `--`)
- Plugin and marketplace structure for distribution
- Comparison with VS Code/Copilot (`.agents/skills/` vs `.claude/skills/`)
- Installation mechanism via `/plugin install` (not `npx skills add`)

### 7.4 With prompt-engineering-guide.md

The prompt engineering guide provides the technical arsenal for writing effective skills:

- CoT for multi-step workflows
- ReAct for tool-using skills
- Structured outputs for communication between skills and sub-agents
- Role prompting for sub-agent specialization
- The recommendation to "start simple, increase complexity when needed" applies directly to skill evolution

---

## 8. Strengths and Limitations

### 8.1 Strengths

1. **Native progressive disclosure**: The 3-level model (metadata → body → supporting files) is elegant and solves the context rot problem
2. **Invocation flexibility**: The fine-grained control between user-invocable, model-invocable, and both covers all scenarios
3. **Context isolation**: `context: fork` allows heavy skills without impacting the main context
4. **Dynamic injection**: `` !`command` `` transforms skills into real-time data pipelines
5. **Cross-agent compatibility**: The Agent Skills standard (agentskills.io) works in Claude Code, VS Code/Copilot, and OpenAI Codex
6. **Scope hierarchy**: Enterprise > Personal > Project > Plugin enables organizational governance
7. **Official bundled skills**: `/batch`, `/simplify`, `/debug` demonstrate the system's potential

### 8.2 Limitations

1. **No testing framework**: There is no built-in mechanism to test skills before deployment. The "empirical testing" cycle is unsatisfactory for production.
2. **Opaque description budget**: The 2% of context window / 16K chars limit is not visible until skills are silently excluded.
3. **No versioning**: Skills have no `version` field in Claude Code frontmatter (only in the Agent Skills spec). There is no rollback mechanism.
4. **No usage metrics**: There is no way to know how many times a skill was invoked, automatic vs manual, or whether the description is effective for auto-discovery.
5. **Dependency on description quality**: Auto-discovery is entirely dependent on the description — no fallback if the description is inadequate.
6. **CLAUDE.md loads in fork**: Even with `context: fork`, CLAUDE.md is loaded in the sub-agent. Conflicting instructions in CLAUDE.md can affect the skill.
7. **No native inter-skill composition**: There is no formal mechanism for one skill to invoke another. Composition is ad-hoc.
8. **500-line limit**: Although it is good practice, there is no automatic validation of this limit.

---

## 9. Practical Recommendations

### 9.1 For Authoring Individual Skills

1. **Start with the description**: Write the description BEFORE the body. If you cannot describe in 1024 chars when and how to use it, the skill is poorly defined.

2. **Use the 3-level rule**:
   - Level 1 (always present): Clear description with keywords (~100 tokens)
   - Level 2 (on demand): Focused SKILL.md, <500 lines
   - Level 3 (only when needed): Supporting files with reference material

3. **Prefer `disable-model-invocation: true` for workflows with side effects**: Deploy, commit, sending messages — never let Claude decide when to execute.

4. **Use `context: fork` for heavy tasks**: Any skill that reads many files, executes many commands, or produces extensive output should run in a sub-agent.

5. **Reference `${CLAUDE_SKILL_DIR}` for bundled scripts**: Instead of absolute paths, use the variable for portability.

### 9.2 For Organizing Skill Collections

1. **Monitor the description budget**: Use `/context` regularly. If skills are being excluded, consider:
   - Marking less-used skills as `disable-model-invocation: true`
   - Shortening descriptions
   - Increasing `SLASH_COMMAND_TOOL_CHAR_BUDGET`

2. **Group related skills in plugins**: Skills that share a domain should be in a plugin with its own namespace.

3. **Use the priority hierarchy consciously**: Personal skills (`~/.claude/skills/`) override project skills. Use this for personalization, not for conflict.

### 9.3 For Integration with Agent Infrastructure

1. **Convert CLAUDE.md instructions > 50 lines into skills**: Reduces always-present context and improves adherence.

2. **Use hooks for enforcement, skills for guidance**: If a rule MUST be followed without exception, implement as a hook. If it is a guideline that admits exceptions, implement as a skill.

3. **Design sub-agents with preloaded skills**: For specialized agents, define in `.claude/agents/` with a `skills` field to load relevant knowledge at sub-agent startup.

4. **Implement feedback loops in critical skills**: Deploy, migration, or destructive operation skills should include explicit validation steps (validate → fix → repeat).

### 9.4 Recommended Standard Skill Template

```yaml
---
name: skill-name
description: >
  [What it does] and [when to use it]. Use when [trigger keywords].
  Examples: [concrete scenarios that activate the skill].
disable-model-invocation: false  # or true for workflows with side effects
# context: fork  # uncomment for heavy tasks
# agent: Explore  # uncomment with context: fork
# allowed-tools: Read, Grep, Glob  # uncomment if needed
---

# [Skill Name]

## Objective
[One sentence describing the objective]

## Instructions
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Validation
- [ ] [Success criterion 1]
- [ ] [Success criterion 2]

## Additional Resources
- For details on [topic]: [reference/topic.md](reference/topic.md)
```
