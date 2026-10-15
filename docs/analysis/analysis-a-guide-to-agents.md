# Analysis: A Complete Guide To AGENTS.md

> **Status**: Current
> **Source document**: [A Complete Guide To AGENTS.md](https://www.octomind.dev/blog/a-complete-guide-to-agents-md)
> **Analysis date**: 2026-03
> **Scope**: Minimalist configuration philosophy for AI agent context files in code repositories

## 1. Executive Summary

The guide "A Complete Guide To AGENTS.md" presents a minimalist configuration philosophy for AI agent context files in code repositories. The document starts from a central premise: massive AGENTS.md files are counterproductive. Instead of improving agent behavior, they create a "ball of mud" that confuses the model, wastes tokens, and becomes a maintenance nightmare. The proposed solution is radical in its simplicity: keep the root AGENTS.md at the absolute minimum (one-sentence description, package manager, build commands) and delegate everything else to progressive disclosure.

The most distinctive aspect of this guide is its **open standard and cross-tool** perspective. AGENTS.md is not tied to any specific tool — it is supported by multiple AI-assisted coding platforms (Codex, Qwen Code, Aider, among others). This has profound implications for projects that need to be compatible with multiple agents simultaneously. The guide explicitly acknowledges that Claude Code does not use AGENTS.md, suggesting symlinks as a bridge between the two worlds.

The articulation between the concept of "instruction budget" (150-200 maximum instructions) and the practice of progressive disclosure constitutes the backbone of the document. Each instruction added to AGENTS.md consumes part of a finite attention budget, and this budget is loaded on **every request**, regardless of relevance. The guide transforms this technical constraint into a design principle: the ideal configuration is one that loads the minimum necessary and points to where to find the rest.

---

## 2. Key Findings and Principles

### 2.1 The "Ball of Mud" Anti-Pattern

The guide identifies a natural feedback cycle that leads to uncontrolled growth:

> "1. The agent does something you don't like / 2. You add a rule to prevent it / 3. Repeat hundreds of times over months / 4. File becomes a 'ball of mud'"

This pattern is aggravated by two factors: (a) different developers add conflicting opinions without global review, and (b) auto-generation scripts, which the guide explicitly condemns:

> "Never use initialization scripts to auto-generate your AGENTS.md. They flood the file with things that are 'useful for most scenarios' but would be better progressively disclosed."

### 2.2 The Instruction Budget

Referencing Kyle's article from Humanlayer, the guide establishes:

> "Frontier thinking LLMs can follow ~ 150-200 instructions with reasonable consistency."

And adds the critical implication: every token in AGENTS.md is loaded on **every request**, creating a rigid budget problem. The guide synthesizes this in the statement: **"the ideal AGENTS.md file should be as small as possible."**

### 2.3 Stale Documentation Poisons the Context

The guide distinguishes between the impact of stale documentation on humans versus agents:

> "For human developers, stale docs are annoying, but the human usually has enough built-in memory to be skeptical about bad docs. For AI agents that read documentation on every request, stale information actively _poisons_ the context."

The specific recommendation is: **describe capabilities, not structures**. Instead of mapping file paths (which change constantly), describe what the project does and provide hints about where things might be. Domain concepts ("organization" vs "group" vs "workspace") are more stable than file paths.

### 2.4 The Absolute Minimum

The guide defines three items as essential content:

1. **One-sentence project description** — functions as a role-based prompt
2. **Package manager** — only if not npm
3. **Build/typecheck commands** — only if non-standard

> "That's honestly it. Everything else should go elsewhere."

### 2.5 Progressive Disclosure as an Architectural Principle

The guide presents progressive disclosure at three levels:

1. **References to separate files**: `"For TypeScript conventions, see docs/TYPESCRIPT.md"` — with a "light touch", no imperative language
2. **Nested references**: docs/TYPESCRIPT.md references docs/TESTING.md, creating a discoverable resource tree
3. **Agent skills**: commands or workflows the agent can invoke to learn something specific

### 2.6 AGENTS.md in Monorepos

The guide presents a two-level hierarchy:

| Level | Content |
|-------|---------|
| **Root** | Monorepo purpose, navigation between packages, shared tooling |
| **Package** | Package purpose, specific tech stack, package conventions |

With the critical caveat: **"Don't overload any level."**

---

## 3. Points of Attention

### 3.1 The Danger of Imperative Language

The guide makes a subtle but fundamental observation about tone. The example of referencing a separate file uses:

> "Notice the light touch, no 'always,' no all-caps forcing. Just a conversational reference."

This contradicts the intuition of many developers who believe that uppercase instructions or those with "NEVER"/"ALWAYS" are more effective. Research documented in the prompt engineering guide confirms that aggressive formatting (ALL-CAPS, "NEVER", "DON'T EVER") produces worse results in recent Claude models.

### 3.2 The Auto-Generation Trap

The guide is emphatic against auto-generation, but the practice is common. Codex, Qwen Code, and Claude Code offer built-in `/init` commands. The fact that the providers themselves recommend auto-generation creates a direct tension with this guide's principle. The "Evaluating AGENTS.md" paper empirically confirms that LLM-generated files **reduce** the success rate by 3% on average.

### 3.3 Stable Concepts vs Code Instances

The distinction between domain concepts (more stable) and file paths (unstable) is easy to overlook in practice. Many AGENTS.md files include detailed directory mappings such as:

> "authentication logic lives in `src/auth/handlers.ts`"

The guide warns that this creates vulnerability to renames. The proposed alternative — describing capabilities and "shape of the project" — requires more reflection from the author but produces more resilient documentation.

### 3.4 When Progressive Disclosure Fails

The guide does not explicitly address scenarios where progressive disclosure can be problematic: (a) agents that cannot navigate documentation hierarchies efficiently, (b) projects with smaller models that have limited navigation capability, (c) tasks that require holistic context from the start.

### 3.5 The Cross-Tool Compatibility Problem

AGENTS.md is described as an "open standard supported by many - though not all - tools." However, each tool interprets the file in a slightly different way. The need for symlinks between AGENTS.md and CLAUDE.md reveals that standardization is still incomplete. Instructions that work well with one tool may not have the same effect on another.

---

## 4. Use Cases and Scope

### 4.1 Multi-Tool Projects

AGENTS.md is especially valuable when the team uses multiple AI-assisted coding tools. A single configuration file that works with Codex, Qwen Code, Aider, and others reduces duplication and ensures consistency. The symlink recommendation (`ln -s AGENTS.md CLAUDE.md`) allows extending compatibility to Claude Code.

### 4.2 Open Source Projects

Open source repositories frequently receive contributions from developers using different tools. AGENTS.md as an open standard allows any contributor, regardless of tool, to receive consistent guidance.

### 4.3 Monorepos

The guide provides explicit support for monorepos with hierarchical AGENTS.md. This is particularly relevant for organizations with multiple teams working on distinct packages, where each package may have its own conventions.

### 4.4 Teams in Transition

Teams that are migrating between AI-assisted coding tools or that have not yet defined a standard tool benefit from the tool-agnostic nature of AGENTS.md.

### 4.5 Less Appropriate Scenarios

- Projects exclusively tied to Claude Code (where CLAUDE.md offers superior functionality)
- Projects that require deterministic enforcement (hooks are more suitable)
- Teams with the need for granular per-developer configuration (AGENTS.md is focused on project scope)

---

## 5. Applicability to Agent Infrastructure

### 5.1 Skills

The guide mentions agent skills as a form of progressive disclosure:

> "Many tools support 'agent skills' - commands or workflows the agent can invoke to learn how to do something specific."

**Implications for skill design:**

- Skills should be designed as self-contained units of knowledge that the agent loads on demand
- The skill description (visible at session start) functions as the progressive disclosure "pointer" — it must be concise enough not to inflate the instruction budget
- The full skill content should only be loaded when invoked, aligning with the principle of loading "only what it needs right now"
- Skills in a cross-tool context should be designed with neutral language, avoiding dependencies on tool-specific features

### 5.2 Hooks

The guide does not mention hooks directly, but the minimalism logic for AGENTS.md implies a conversion strategy:

- Instructions that **must** be followed without exception (such as "always run tests before commit") are candidates for conversion to hooks
- Hooks remove these instructions from the context budget — the instruction is enforced programmatically, without consuming tokens
- For cross-tool projects, hooks need to be implemented in a tool-specific way, but AGENTS.md can reference their existence: "Pre-commit hooks enforce test execution and linting"
- The guide's principle that "everything else should go elsewhere" applies strongly: what can be a hook should not be a textual instruction

### 5.3 Subagents

The minimalism principle of AGENTS.md applies directly to subagent context design:

- Subagents have smaller and more focused context windows — the instruction budget is even more critical
- The "one-sentence project description" recommendation translates to: each subagent should receive only the minimum context necessary for its specific task
- The context isolation strategy (each subagent with its own context) mirrors the AGENTS.md hierarchy in monorepos — each context "package" is independent
- Progressive disclosure for subagents means: the subagent receives minimal initial instructions and can fetch more context as needed

### 5.4 Rules

The `.claude/rules/` concept (Claude Code-specific) can be mapped to the cross-tool AGENTS.md pattern in monorepos:

- Path-scoped rules are the technical implementation of the guide's "relevant to one domain" principle
- For cross-tool projects, the same logic can be implemented via AGENTS.md in subdirectories, which is the native progressive disclosure mechanism of the open standard
- The fundamental difference: rules are path-triggered (loaded automatically when corresponding files are read), while subdirectory AGENTS.md depends on the agent navigating to that directory
- In cross-tool projects, subdirectory AGENTS.md is the closest universal alternative to rules

### 5.5 Memory

The relationship between AGENTS.md and memory systems is one of complementarity:

- **AGENTS.md**: static, versioned information shared by the team — conventions, tech stack, commands
- **Memory**: dynamic, personal, or emergent information — patterns discovered during usage, individual preferences, session-specific decisions
- The guide's principle that "the agent can generate its own just-in-time documentation during planning" connects directly to the concept of auto-memory
- Avoiding documenting structure in AGENTS.md complements the memory capability of generating ad-hoc mappings as needed

---

## 6. Applicability of the Prompt Engineering Guide

### 6.1 Role Prompting in the Project Description

The "one-sentence project description" from the guide functions as role prompting:

> "This single sentence gives the agent context about _why_ they're working in this repository. It anchors every decision they make."

The prompt engineering guide confirms that role prompting is the fundamental specialization mechanism in multi-agent architectures. The description in AGENTS.md acts as a persistent role prompt — defining the agent's "role" within the context of that repository. The cost is minimal (10-30 additional tokens) with a high cost-benefit ratio for style and scope control.

### 6.2 Zero-Shot vs Few-Shot in Instruction Writing

The prompt engineering guide shows that modern models have robust zero-shot capabilities (~85% accuracy on simple tasks). This reinforces the AGENTS.md guide's recommendation of not documenting what the agent already knows — many instructions are redundant with the model's parametric knowledge.

The few-shot recommendation (3-5 examples) from the prompt guide applies when AGENTS.md needs to demonstrate specific patterns. However, the examples should go in separate files (progressive disclosure), not in the root AGENTS.md, to avoid inflating the budget.

### 6.3 Chain-of-Thought and Planning

The prompt guide shows that CoT improves multi-step reasoning, but at a cost of 35-600% more tokens. For AGENTS.md, this means:

- Instructions in AGENTS.md should be direct (zero-shot), not procedural
- If the agent needs to "think step by step" about something, it should be part of a skill invoked on demand, not a permanent instruction
- The "Thread of Thought" technique (walking through context in manageable parts) is particularly relevant for agents navigating progressive disclosure trees

### 6.4 ReAct and Documentation Navigation

The ReAct pattern (Thought -> Action -> Observation) is exactly what happens when an agent navigates the progressive disclosure tree:

1. **Thought**: "I need to understand this project's TypeScript conventions"
2. **Action**: Reading `docs/TYPESCRIPT.md` (referenced in AGENTS.md)
3. **Observation**: Obtains the conventions and can act

This validates the effectiveness of progressive disclosure — modern agents are naturally equipped for this navigation pattern.

### 6.5 Structured Output and AGENTS.md Format

The prompt guide recommends XML tags for Claude and structured markdown as an efficient format. AGENTS.md as a markdown file aligns well with these principles. However, for cross-tool projects, avoiding Claude-specific XML tags ensures compatibility — markdown headers and tables are more universal.

### 6.6 Context Engineering vs Prompt Engineering

The prompt guide identifies the transition from prompt engineering to context engineering:

> "The LLM is a CPU, the context window is RAM, and you are the operating system." (Andrej Karpathy)

AGENTS.md is a context engineering artifact — it is not an individual prompt, but part of a context system that includes memory, tools, progressive documentation, and orchestration. The principle of "finding the simplest possible solution" applies directly to AGENTS.md design.

---

## 7. Correlations with Other Key Documents

### 7.1 Evaluating-AGENTS-paper.md

The ETH Zurich paper offers **direct empirical validation** of this guide's principles:

- **LLM-generated files reduce performance**: 3% average reduction in success rate + 20% cost increase. This confirms the guide's warning against auto-generation.
- **Human-written files have marginal gains**: only +4% on average. This reinforces that even well-written files have limited impact, justifying extreme minimalism.
- **Instructions are followed but make the task harder**: the paper shows that agents follow AGENTS.md instructions (e.g., use of `uv` when mentioned), but this increases steps and cost. The guide is correct in stating that "unnecessary requirements from context files make tasks harder."
- **Codebase overviews are not effective**: 100% of files generated by Sonnet-4.5 include overviews, but they do not reduce the time to find relevant files. This validates the guide's recommendation to describe capabilities, not structure.
- **Redundancy with existing documentation**: when all documentation is removed, LLM-generated context files improve performance by 2.7%. This suggests that AGENTS.md is more useful in projects with sparse documentation.

### 7.2 research-context-engineering-comprehensive.md

This document provides the **scientific foundation** for several of the guide's recommendations:

- **Context rot**: performance degradation with increased context (n^2 attention relationships) underpins the recommendation to keep AGENTS.md small.
- **Lost-in-the-middle effect**: information in the middle of long contexts is the most ignored. This implies that if AGENTS.md is long, the instructions in the middle will be the first to be ignored.
- **Instruction budget of ~200 lines**: the AGENTS.md guide cites Kyle's article from Humanlayer; the research deepens with Anthropic's explicit recommendation to "target under 200 lines per CLAUDE.md file."
- **Hybrid strategy (pre-loaded + on-demand)**: exactly the pattern the guide proposes — AGENTS.md loaded upfront as the essential minimum, detailed documentation loaded on demand.
- **Just-in-time documentation**: Anthropic's formal concept of maintaining "lightweight identifiers" and loading data dynamically maps directly to the guide's progressive disclosure.

### 7.3 claude-prompting-best-practices.md

Anthropic's official prompting guide correlates on several points:

- **"Be clear and direct"**: reinforces the recommendation for concise instructions in AGENTS.md, not vague ones
- **"Add context to improve performance"**: the one-sentence project description is exactly that — motivational context
- **"Put longform data at the top, queries at the end"**: for AGENTS.md, the most critical instructions should be at the beginning of the file
- **On aggressive formatting**: Claude Opus 4.5/4.6 responds worse to coercive language — "Where you might have said 'CRITICAL: You MUST use this tool when...', you can use more normal prompting like 'Use this tool when...'" — validating the "light touch" recommended by the guide
- **Subagent orchestration**: Claude Opus 4.6 orchestrates subagents proactively. For cross-tool projects, AGENTS.md should contain instructions that are effective regardless of whether a monolithic agent or a subagent orchestrator processes them

---

## 8. Strengths and Limitations

### 8.1 Strengths

1. **Universal principle**: minimalism is applicable regardless of tool, model, or programming language
2. **Empirical basis**: the instruction budget concept has research-backed foundations (Humanlayer, Anthropic)
3. **Practicality**: the guide offers a concrete prompt to refactor existing AGENTS.md files (section "Fix A Broken AGENTS.md")
4. **Cross-tool compatibility**: as an open standard, it works with multiple agents
5. **Scalability**: the progressive disclosure pattern scales naturally with project complexity
6. **Clear decision matrix**: the "When to use" table (Root / Separate file / Nested documentation) offers actionable guidance

### 8.2 Limitations

1. **Absence of metrics**: the guide does not offer quantitative metrics on the impact of AGENTS.md size on performance. The ETH Zurich paper partially fills this gap.
2. **JavaScript/TypeScript focus**: the examples are predominantly from the Node.js ecosystem (pnpm, npm, corepack). Python, Go, Rust, etc. projects have different idioms.
3. **Does not address deterministic enforcement**: hooks, linters, CI checks are not mentioned as alternatives for critical instructions.
4. **Excessive simplification of the minimum**: projects with complex architectures (microservices, event-driven, CQRS) may need more context at the root than three items.
5. **Dependency on agent navigation capability**: progressive disclosure assumes the agent is "fast at navigating documentation hierarchies", which varies across tools and models.
6. **Does not address versioning**: how AGENTS.md should evolve over time, who should review it, how often.
7. **Gap on cross-tool conflicts**: does not discuss how to handle when different tools interpret the same AGENTS.md in different ways.

---

## 9. Practical Recommendations

### 9.1 For New Projects

1. **Start with three lines**: project description, package manager (if not npm), build commands (if non-standard)
2. **Create the progressive disclosure tree from the start**: even if the referenced files are empty, the structure (`docs/CONVENTIONS.md`, `docs/TESTING.md`) signals intent
3. **Use symlinks for Claude Code**: `ln -s AGENTS.md CLAUDE.md` ensures compatibility
4. **Add to .gitignore**: do not ignore AGENTS.md — it should be shared by the team

### 9.2 For Existing Projects with Bloated AGENTS.md

1. **Use the guide's refactoring prompt**: copy the prompt from the "Fix A Broken AGENTS.md" section directly into the agent
2. **Identify contradictions first**: conflicting instructions cause arbitrary behavior
3. **Convert deterministic instructions to hooks**: anything that is "ALWAYS" or "NEVER" should probably be a hook, not an instruction
4. **Remove the obvious**: instructions like "write clean code" or "follow best practices" are token waste
5. **Test removal**: remove instructions one at a time and observe whether behavior changes — if it doesn't, the instruction was redundant

### 9.3 For Monorepos

1. **Root AGENTS.md**: only monorepo purpose, navigation between packages, and shared tooling
2. **Package AGENTS.md**: package purpose, specific stack, reference to detailed conventions
3. **Don't duplicate**: if an instruction applies to all packages, it goes in root — if it's specific, in the package
4. **Use `claudeMdExcludes`** (in Claude Code projects) to prevent other teams' CLAUDE.md from loading unnecessarily

### 9.4 For Cross-Tool Projects

1. **Keep AGENTS.md as the primary source**: use it as the reference point for all tools
2. **Avoid tool-specific features in AGENTS.md**: do not use XML tags, `@imports`, or path-scoped rules in AGENTS.md — these are tool-specific extensions
3. **Document equivalence**: maintain a note in the repository explaining how AGENTS.md relates to CLAUDE.md, .codex/configuration.md, etc.
4. **Test with multiple agents**: validate that instructions produce consistent behavior across different tools

### 9.5 For Ongoing Maintenance

1. **Review AGENTS.md alongside code reviews**: treat it as code — it deserves the same level of scrutiny
2. **Prune periodically**: at every sprint or release cycle, review whether instructions are still relevant
3. **Measure impact**: if possible, compare the agent's success rate with and without AGENTS.md on representative tasks
4. **Document exclusion decisions**: when removing something from AGENTS.md, record the reason (in a commit message or ADR) to prevent someone from adding it back
