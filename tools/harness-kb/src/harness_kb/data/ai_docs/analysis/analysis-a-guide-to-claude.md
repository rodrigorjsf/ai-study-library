# Analysis: A Complete Guide To CLAUDE.md

> **Status**: Current
> **Source document**: [A Complete Guide To CLAUDE.md](https://www.octomind.dev/blog/a-complete-guide-to-claude-md)
> **Analysis date**: 2026-03
> **Scope**: Minimalist configuration philosophy specific to the Claude Code ecosystem

## 1. Executive Summary

The guide "A Complete Guide To CLAUDE.md" presents a minimalist configuration philosophy specific to the Claude Code ecosystem. Although it shares fundamental principles with the AGENTS.md guide (minimalism, progressive disclosure, instruction budget), CLAUDE.md operates within a significantly richer and more sophisticated architecture. Claude Code offers native mechanisms such as subdirectory CLAUDE.md with automatic merge, `.claude/rules/` with path-scoping, `@imports`, skills with isolated context, deterministic hooks, and a self-managed memory system -- each representing a distinct layer of progressive disclosure that does not exist in the open AGENTS.md standard.

The document starts from the same central premise: massive CLAUDE.md files are counterproductive. The same "ball of mud" dynamic applies, with the additional factor that Claude Code processes CLAUDE.md at a specific position in the context hierarchy -- just below the system prompt. This means that an inflated CLAUDE.md competes directly with the space needed for the task, tools, and model reasoning. Anthropic's recommendation to keep each CLAUDE.md file under **200 lines** reinforces the urgency of minimalism.

The most distinctive aspect of this guide, in contrast with the AGENTS.md guide, is the depth of the progressive disclosure ecosystem available. While AGENTS.md fundamentally depends on markdown files in subdirectories and textual references, CLAUDE.md can delegate to rules (conditionally loaded by path), skills (with isolated context via `context: fork`), hooks (deterministic enforcement outside the context), subdirectory CLAUDE.md (automatic merge when the agent works in that directory), and @imports (modular composition). Each mechanism has a distinct profile of context cost, loading timing, and enforcement level. Mastering this taxonomy is the key to effective CLAUDE.md configuration.

---

## 2. Key Findings and Principles

### 2.1 The "Ball of Mud" Anti-Pattern in the Claude Code Context

The guide identifies the same feedback cycle as AGENTS.md:

> "1. The agent does something you don't like / 2. You add a rule to prevent it / 3. Repeat hundreds of times over months / 4. File becomes a 'ball of mud'"

In the Claude Code context, this problem is amplified by two additional factors: (a) Claude Code automatically loads the root CLAUDE.md in **every session**, with no possibility of conditional loading; and (b) different CLAUDE.md scopes (user, project, subdirectory) merge together, potentially creating non-obvious contradictions between levels.

The condemnation of auto-generation is equally emphatic:

> "Never use initialization scripts to auto-generate your CLAUDE.md. They flood the file with things that are 'useful for most scenarios' but would be better progressively disclosed."

This is particularly relevant because Claude Code natively offers the `/init` command to generate the CLAUDE.md, and Anthropic recommends this practice in its official documentation -- creating direct tension with this guide's principle.

### 2.2 The Instruction Budget

The reference to Kyle's article from Humanlayer is identical:

> "Frontier thinking LLMs can follow ~ 150-200 instructions with reasonable consistency."

However, in the Claude Code context, this budget is shared among multiple sources: root CLAUDE.md, subdirectory CLAUDE.md, `.claude/rules/` (loaded), and invoked skills content. The implication is that the effective budget for the root CLAUDE.md is **less** than 150-200, because part of the capacity will be consumed by rules and other instruction sources loaded during the session.

### 2.3 Stale Documentation Poisons the Context

The guide repeats the warning about stale documentation:

> "For AI agents that read documentation on every request, stale information actively _poisons_ the context."

In the Claude Code ecosystem, this has an additional implication: the self-managed memory system can create information that conflicts with the CLAUDE.md if it is not kept up to date. Claude may memorize patterns from a session that contradict stale instructions in the CLAUDE.md, creating a confusion cycle.

The specific recommendation remains: **describe capabilities, not structures**. In Claude Code, this is even more relevant because the agent has native tools (glob, grep, Read) to explore the project structure in real time, making static mappings doubly redundant.

### 2.4 The Absolute Minimum

Identical to AGENTS.md:

1. **One-sentence project description**
2. **Package manager** (if not npm)
3. **Build/typecheck commands** (if non-standard)

> "That's honestly it. Everything else should go elsewhere."

In Claude Code, "elsewhere" means a much richer ecosystem than simple markdown files.

### 2.5 Progressive Disclosure with Native Mechanisms

The guide presents progressive disclosure at three basic levels, but Claude Code extends this significantly:

1. **References to separate files**: `"For TypeScript conventions, see docs/TYPESCRIPT.md"` -- the agent loads on demand
2. **Nested references**: discoverable resource tree
3. **Agent skills**: described as "commands or workflows the agent can invoke to learn how to do something specific"

What the guide does not detail (but Claude Code documentation offers) are the additional mechanisms:

- **`.claude/rules/`**: modular rules, optionally with path-scoping via YAML frontmatter
- **Subdirectory CLAUDE.md**: automatic merge when Claude works in subdirectories
- **`@imports`**: modular composition with `@path/to/import` syntax (max 5 hops)
- **Skills with `context: fork`**: execution in isolated subagent context
- **Skills with `disable-model-invocation: true`**: descriptions kept out of context until manual invocation
- **Hooks**: deterministic enforcement completely outside the LLM context

### 2.6 CLAUDE.md in Monorepos

The two-level hierarchy is identical to AGENTS.md:

| Level | Content |
|-------|---------|
| **Root** | Monorepo purpose, navigation between packages, shared tooling |
| **Package** | Package purpose, specific tech stack, package conventions |

With the caveat: **"Don't overload any level."** In Claude Code, monorepos have additional support via `claudeMdExcludes` in settings.json to avoid loading CLAUDE.md from irrelevant teams.

---

## 3. Points of Attention

### 3.1 The Danger of Imperative Language

The guide makes the same observation about tone:

> "Notice the light touch, no 'always,' no all-caps forcing. Just a conversational reference."

This is particularly important in Claude Code because the official prompting documentation confirms that recent Claude models respond worse to coercive language:

> "Where you might have said 'CRITICAL: You MUST use this tool when...', you can use more normal prompting like 'Use this tool when...'" (claude-prompting-best-practices.md)

Claude Opus 4.6 is described as "more responsive to the system prompt than previous models", which means previously necessary instructions to force compliance now cause overtriggering.

### 3.2 The Tension Between Minimalism and a Rich Ecosystem

Claude Code offers so many configuration mechanisms that the real risk is not just an inflated CLAUDE.md, but a **fragmented configuration system** where instructions are scattered among CLAUDE.md, rules, skills, hooks, and memory without a clear view of the whole. The guide focuses on CLAUDE.md in isolation, but in practice the total complexity of the instruction system includes all of these sources.

### 3.3 Automatic Merge of Hierarchical CLAUDE.md

The guide mentions that subdirectory CLAUDE.md "merge with the root level", but does not address the implications of conflicts between levels. Anthropic's documentation warns:

> "If two rules contradict each other, Claude may pick one arbitrarily."

This means that a subdirectory CLAUDE.md that contradicts the root can cause unpredictable behavior. In monorepos with many teams, this is a subtle source of bugs.

### 3.4 The Hidden Cost of Rules Without Path-Scoping

Rules in the `.claude/rules/` directory without `paths:` frontmatter are loaded **unconditionally** -- equivalent to being in the root CLAUDE.md. Developers who move content from CLAUDE.md to rules thinking they are implementing progressive disclosure may, in fact, only be fragmenting the same always-loaded content.

### 3.5 The `/init` Trap

Claude Code's `/init` command generates a CLAUDE.md automatically. The "Evaluating AGENTS.md" paper shows that 100% of files generated by Sonnet-4.5 include codebase overviews, and that these overviews are not effective. The guide's recommendation against auto-generation applies with full force to Claude Code's `/init`.

### 3.6 Memory vs CLAUDE.md

Claude Code's auto-memory system creates an additional layer of "instructions" that can interfere with CLAUDE.md. If Claude memorizes a pattern during a session and the CLAUDE.md is updated later, the stale memory may prevail over the updated instruction. There is no automatic synchronization mechanism between CLAUDE.md and memory.

---

## 4. Use Cases and Scope

### 4.1 Exclusively Claude Code Projects

When the entire team uses Claude Code, CLAUDE.md is the primary configuration mechanism. The complete ecosystem (rules, skills, hooks, memory, subdirectory CLAUDE.md) is available, enabling the most sophisticated implementation of progressive disclosure.

### 4.2 Monorepos with Multiple Teams

The support for subdirectory CLAUDE.md with automatic merge, combined with `claudeMdExcludes`, makes CLAUDE.md especially suited for monorepos. Each team can maintain its own CLAUDE.md without affecting other teams, and the root CLAUDE.md provides common context.

### 4.3 Projects with Enforcement Requirements

Claude Code offers hooks for deterministic enforcement. For projects where certain rules **must** be followed (security, compliance, code standards), the combination of minimalist CLAUDE.md + hooks is the most robust approach. CLAUDE.md documents the "why", hooks ensure the "what".

### 4.4 Projects with Complex Workflows

Claude Code skills allow encapsulating complex workflows (deploy, database migration, code generation) as invocable units on demand. For projects with many workflows, skills replace the need to document procedures in the CLAUDE.md.

### 4.5 Open Source Projects with Claude Code Users

Open source repositories that want to offer an optimized experience for Claude Code users can include CLAUDE.md in addition to AGENTS.md. The reverse symlink (`ln -s CLAUDE.md AGENTS.md`) ensures that users of other tools also benefit.

### 4.6 Less Appropriate Scenarios

- Projects that need to support multiple tools equally (AGENTS.md is more universal)
- Teams in tool transition (the investment in rules, skills, hooks is Claude Code-specific)
- Projects with developers who do not use Claude Code (the configuration will not be utilized)

---

## 5. Applicability to Agent Infrastructure

### 5.1 Skills

The guide mentions skills as progressive disclosure:

> "Many tools support 'agent skills' - commands or workflows the agent can invoke to learn how to do something specific."

In Claude Code, skills have a sophisticated execution model that the guide does not detail:

**Impact on skill design:**

- **Description vs full content**: Claude sees skill descriptions at session start, but full content only loads when the skill is used. The description must be sufficient for Claude to know **when** to invoke the skill, without consuming unnecessary tokens.
- **`context: fork`**: skills with isolated context execute in independent subagents. This is the purest form of progressive disclosure -- the skill content has **zero** impact on the main context. CLAUDE.md should guide the use of these skills without duplicating their content.
- **`disable-model-invocation: true`**: skills that are not visible until manual invocation. Ideal for rare workflows that should not compete for the attention budget.
- **Dynamic content with `` !`command` ``**: skills can inject data in real time (e.g., `!`gh pr diff``), implementing JIT documentation at the skill level.
- **Relationship with CLAUDE.md**: CLAUDE.md should not document what skills already encapsulate. If a skill for deploy exists, CLAUDE.md does not need deploy instructions -- at most a reference: "For deploy, use the deploy skill."

### 5.2 Hooks

The guide does not mention hooks, but the logic of minimalism in CLAUDE.md implies a fundamental conversion strategy for the Claude Code ecosystem:

- **Hooks remove instructions from the context budget**: an instruction like "always run tests before commit" consumed as text in CLAUDE.md can be converted to a pre-commit hook that runs tests automatically. The hook is deterministic (guaranteed) and does not consume tokens.
- **The context optimization research principle**: "Converting behavioral instructions to deterministic hooks removes them from the context budget entirely while guaranteeing enforcement." This is explicitly documented in research-context-engineering-comprehensive.md.
- **Relevant hook types**:
  - `PreToolUse`: before tool execution (e.g., validate before git push)
  - `PostToolUse`: after execution (e.g., lint after editing a file)
  - `Notification`: alerts about behavior (e.g., notify when Claude tries to access production)
  - `SessionStart`/`SessionEnd`: session setup and cleanup
- **Hook vs instruction decision**: if the instruction is of the "ALWAYS" or "NEVER" type, it is a hook candidate. If it involves judgment or context ("prefer X when Y"), keep it as an instruction. Anthropic's documentation suggests: "If Claude already does something correctly without the instruction, delete it or convert it to a hook."

### 5.3 Subagents

The CLAUDE.md minimalism principle applies critically to subagent context design:

- **Context isolation**: subagents via `context: fork` receive their own context. The root CLAUDE.md is **not** automatically inherited by subagents in isolated context -- the subagent prompt must contain only what is necessary for its task.
- **One-sentence description as role prompt**: the same CLAUDE.md technique applies to each subagent's prompt -- one sentence defining scope and purpose.
- **Progressive disclosure for subagents**: subagents can have their own context hierarchies. An exploration subagent can receive references to documentation that it loads on demand.
- **Claude Opus 4.6 and native orchestration**: the prompting documentation warns that Opus 4.6 "has a strong predilection for subagents and may spawn them in situations where a simpler, direct approach would suffice." CLAUDE.md can include guidance on when subagents are and are not appropriate: "Use subagents when tasks can run in parallel, require isolated context, or involve independent workstreams."
- **Impact on instruction budget**: each subagent has its own instruction budget. Focused subagents with minimal instructions perform better than subagents overloaded with context.

### 5.4 Rules (`.claude/rules/`)

Rules are the progressive disclosure mechanism most directly tied to CLAUDE.md:

- **Rules without paths = always-loaded**: equivalent to being in the root CLAUDE.md. Moving content from CLAUDE.md to rules without path-scoping does not save context -- it merely fragments it.
- **Rules with paths = conditional**: `paths: ["src/api/**/*.ts"]` ensures the rule only loads when Claude reads API files. This is genuine progressive disclosure.
- **Relationship with CLAUDE.md**: the root CLAUDE.md should contain universal rules (applicable to any task). Path-scoped rules should contain domain rules (API, frontend, tests). Never duplicate: if it is in CLAUDE.md, it does not need to be in rules.
- **Modularity**: each file in `.claude/rules/` covers one topic with a descriptive filename. This facilitates maintenance compared to a monolithic CLAUDE.md.
- **Symlinks**: rules support symlinks for sharing between projects, enabling reuse of organizational conventions.
- **Recursive discovery**: rules in subdirectories of `.claude/rules/` are discovered recursively, enabling hierarchical organization: `.claude/rules/frontend/react.md`, `.claude/rules/backend/api.md`.

### 5.5 Memory

The relationship between CLAUDE.md and Claude Code's memory system is one of complementary layers:

- **CLAUDE.md**: static instructions, versioned, shared by the team, committed in Git
- **Self-managed memory**: dynamic information, emerging from sessions, which can be personal or project-level
- **MEMORY.md**: the first 200 lines are loaded at startup, functioning as an index. Additional topics load on demand.
- **Do not duplicate between CLAUDE.md and memory**: if something is a team decision, it goes in CLAUDE.md (or rules). If it is a pattern discovered during use, it goes in memory.
- **Conflict risk**: memory can contain information that contradicts an updated CLAUDE.md. Periodic memory review is necessary.
- **Compaction and memory**: when context is compacted, CLAUDE.md instructions are preserved (re-read from the file), but inline memory information can be lost. The compaction directive can be configured in CLAUDE.md itself: "When compacting, always preserve the full list of modified files and any test commands."
- **Boris Cherny on simplicity**: the Claude Code lead engineer described the memory architecture as "the simplest thing, which is a file that has some stuff. And it's auto-read into context." This reinforces that even memory follows the principle of maximum simplicity.

---

## 6. Applicability of the Prompt Engineering Guide

### 6.1 Role Prompting in the Project Description

The guide's "one-sentence project description" functions as role prompting, but in Claude Code it has an additional implication: this description is injected at the beginning of the context, right after the system prompt. The prompting guide confirms that role prompting in the system prompt "focuses Claude's behavior and tone for your use case."

In Claude Code, the description in CLAUDE.md occupies a position analogous to the system prompt for the project context. It is the mechanism with the best cost-benefit ratio (10-30 tokens) for anchoring the agent's behavior.

### 6.2 Structured Prompting and XML Tags in CLAUDE.md

Anthropic's prompting guide recommends XML tags for structuring complex prompts:

> "XML tags help Claude parse complex prompts unambiguously, especially when your prompt mixes instructions, context, examples, and variable inputs."

In the CLAUDE.md context, this means instructions can benefit from XML tags to separate sections:

```xml
<project>
React component library for accessible data visualization.
</project>

<build>
pnpm build && pnpm typecheck
</build>
```

However, the guide recommends a "light touch" and simple markdown. The choice between XML and markdown in CLAUDE.md depends on complexity: for the three minimum items, markdown suffices. For more elaborate CLAUDE.md files, XML tags can improve parsing.

The prompting documentation confirms that Claude was specifically trained to recognize XML, with a "15-20% performance boost" compared to other formats.

### 6.3 Few-Shot via Examples in Rules or Skills

The prompting guide recommends 3-5 diverse examples to stabilize format and behavior. In CLAUDE.md, examples consume valuable budget. The solution is to delegate examples to progressive disclosure:

- **Path-scoped rules**: API code examples go in `.claude/rules/api-patterns.md` with `paths: ["src/api/**"]`
- **Skills**: complex workflow examples are encapsulated in skills, loaded only when invoked
- **Referenced files**: `"For code examples, see docs/examples/PATTERNS.md"` keeps the CLAUDE.md lean

### 6.4 Chain-of-Thought and Procedural Instructions

The prompting guide shows that CoT improves multi-step reasoning but with significant token cost. For CLAUDE.md:

- Instructions should be declarative ("Use 2-space indentation"), not procedural ("First check the current indentation, then...")
- If the agent needs to follow a multi-step procedure, that procedure should be in a skill or referenced document
- Claude Opus 4.6 uses adaptive thinking internally -- explicit "think step by step" instructions are counterproductive and consume tokens: "Prefer general instructions over prescriptive steps. A prompt like 'think thoroughly' often produces better reasoning than a hand-written step-by-step plan."

### 6.5 ReAct and Claude Code Architecture

The ReAct pattern (Thought -> Action -> Observation) is Claude Code's central loop. CLAUDE.md feeds the "Thought" phase -- providing context for decisions. Well-written instructions in CLAUDE.md improve the quality of "Thought" without interfering with the natural ReAct cycle.

The practice of progressive disclosure aligns perfectly with ReAct: the agent navigates the documentation tree as a sequence of actions (read file) and observations (process content), building context incrementally.

### 6.6 Context Engineering as a Unifying Framework

The prompting guide identifies the transition from prompt engineering to context engineering. In Claude Code, CLAUDE.md is just one piece of a context system that includes:

1. Claude Code system prompt (fixed, not user-editable)
2. Root CLAUDE.md (always-loaded, editable)
3. Rules (conditionally loaded)
4. Skills (loaded on invocation)
5. Subdirectory CLAUDE.md (loaded on navigation)
6. Memory (loaded at startup + on demand)
7. Hooks (outside the context, programmatic enforcement)
8. Tools (glob, grep, Read -- real-time context gathering)

Anthropic's principle of "finding the simplest possible solution" applies to the design of this system as a whole, not just to CLAUDE.md.

### 6.7 Self-Consistency and Configuration Review

The prompting guide describes Self-Consistency as sampling multiple reasoning paths for the same task. In the context of CLAUDE.md maintenance, this suggests:

- Testing the same task with and without specific CLAUDE.md instructions
- If the result is identical, the instruction is redundant and should be removed
- If the result varies inconsistently, the instruction may be ambiguous and needs to be rewritten

### 6.8 Meta-Prompting and the Refactoring Prompt

The guide includes a ready-made prompt for refactoring inflated CLAUDE.md files. This is a direct application of meta-prompting -- using the LLM itself to optimize the instructions it receives. The prompting guide documents that meta-prompting with GPT-4 outperformed standard prompting by 17.1%.

---

## 7. Correlations with Other Key Documents

### 7.1 Evaluating-AGENTS-paper.md

The ETH Zurich paper, although focused on AGENTS.md, has direct implications for CLAUDE.md:

- **Evaluation included Claude Code**: the paper tested Claude Code with Sonnet-4.5 specifically, feeding instructions via CLAUDE.md. The result: Claude Code was the only agent that did **not** improve with human-written context files (Figure 3 of the paper).
- **LLM-generated overviews are ineffective**: 100% of files generated by Sonnet-4.5 included overviews. The Claude Code documentation itself "advocates for a high-level overview only and warns against listing components that are easily discoverable."
- **Increased cost**: context files increased Claude Code's cost from $1.15 to $1.30-$1.33 per instance (13-16% increase).
- **Instructions are followed**: the paper confirms that agents follow CLAUDE.md instructions (e.g., use of `uv` when mentioned), but this makes the task harder, requiring more steps.
- **Redundancy with existing documentation**: when all documentation is removed, context files become useful. For Claude Code, this suggests that CLAUDE.md adds more value in projects with little internal documentation.
- **Critical implication**: Claude Code is already a highly capable agent for exploring repositories with its native tools. Excessive CLAUDE.md may be adding "noise" to a system that already works well on its own.

### 7.2 research-context-engineering-comprehensive.md

This document provides the scientific basis and Anthropic documentation that underpins each principle of the guide:

- **Context rot**: performance degradation with increased context underpins minimalism. In Claude Code, each context source (CLAUDE.md, rules, skills, memory) contributes to total tokens. Management must be holistic.
- **Lost-in-the-middle effect**: critical instructions should be at the **beginning** or **end** of CLAUDE.md, never in the middle. For `.claude/rules/` rules, positioning depends on how Claude Code injects them into context (generally after the root CLAUDE.md).
- **Instruction budget of ~200 lines**: Anthropic's official recommendation: "Target under 200 lines per CLAUDE.md file." The guide is fully aligned.
- **Hybrid strategy**: Claude Code explicitly implements the hybrid model: "CLAUDE.md files are naively dropped into context up front, while primitives like glob and grep allow it to navigate its environment and retrieve files just-in-time." CLAUDE.md is the pre-loaded layer; everything else is on-demand.
- **Skills as progressive disclosure**: "Claude sees skill descriptions at session start, but the full content only loads when a skill is used." This is the technical implementation of the guide's principle.
- **Path-specific rules as conditional loading**: rules with `paths:` frontmatter "trigger only when Claude reads matching files, reducing noise and saving context."
- **Hooks as context savings**: "Converting behavioral instructions to deterministic hooks removes them from the context budget entirely while guaranteeing enforcement." This is the most impactful principle that the guide does not explicitly mention.
- **Compaction**: CLAUDE.md can instruct how compaction should work: "When compacting, always preserve the full list of modified files." This is a form of meta-instruction that survives compaction.
- **Contradictions**: "If two rules contradict each other, Claude may pick one arbitrarily." This makes periodic review of all instruction sources (CLAUDE.md, rules, memory) essential.

### 7.3 claude-prompting-best-practices.md

Anthropic's official prompting guide correlates deeply with CLAUDE.md:

- **"Be clear and direct"**: the golden rule principle ("Show your prompt to a colleague with minimal context on the task and ask them to follow it. If they'd be confused, Claude will be too") applies directly to instructions in CLAUDE.md.
- **"Add context to improve performance"**: the one-sentence description functions as motivational context. The prompting guide explains that providing motivation ("Your response will be read aloud by a text-to-speech engine") is more effective than direct prohibitions ("NEVER use ellipses"). For CLAUDE.md: "Use pnpm because we manage dependencies across packages in this monorepo" is better than "ALWAYS use pnpm."
- **Longform data position**: "Put longform data at the top... queries at the end can improve response quality by up to 30%." For CLAUDE.md, the project description (context) should come first, followed by operational instructions.
- **Anti-coercive language**: "Claude Opus 4.5 and Claude Opus 4.6 are also more responsive to the system prompt than previous models. If your prompts were designed to reduce undertriggering on tools or skills, these models may now overtrigger." For CLAUDE.md, instructions that used "CRITICAL" or "MUST" in previous models should be softened.
- **Subagent orchestration**: Opus 4.6 orchestrates subagents natively. CLAUDE.md can guide this orchestration: "Use subagents when tasks can run in parallel, require isolated context, or involve independent workstreams."
- **Overthinking**: "Claude Opus 4.6 does significantly more upfront exploration than previous models." This means CLAUDE.md does not need to instruct the agent to be "thorough" -- it already is. Excessive exploration instructions can cause waste.
- **Multi-context window workflows**: the recommendation to use "a different prompt for the very first context window" is compatible with CLAUDE.md -- setup instructions can differ from iteration instructions via skills or conditional rules.

---

## 8. Strengths and Limitations

### 8.1 Strengths

1. **Validated minimalism principle**: the ~200 lines recommendation is supported both by Anthropic's documentation and empirical research
2. **Rich progressive disclosure ecosystem**: Claude Code offers more delegation mechanisms (rules, skills, hooks, memory, @imports) than any other tool
3. **Practicality**: the refactoring prompt offers a concrete and immediate action
4. **Scalability**: subdirectory CLAUDE.md and monorepo support allow scaling to large projects
5. **Versioning**: CLAUDE.md is committed in Git, enabling review, history, and rollback
6. **Automatic merge**: hierarchical CLAUDE.md with native merge simplifies monorepos

### 8.2 Limitations

1. **Does not address hooks**: the guide does not mention converting instructions to hooks, which is one of the most impactful strategies for context savings
2. **Does not detail rules**: the `.claude/rules/` mechanism is merely one of the "separate file" forms mentioned, without distinction between always-loaded and path-scoped rules
3. **Does not address @imports**: the composition system via `@path/to/import` is not mentioned
4. **Does not address memory**: the interaction between CLAUDE.md and the auto-memory system is not discussed
5. **Focus on JavaScript/TypeScript**: predominantly Node.js examples
6. **Does not address compaction**: how CLAUDE.md instructions behave during context compaction
7. **Does not address the complete hierarchy**: user CLAUDE.md (`~/.claude/CLAUDE.md`), managed policy, settings hierarchy are not mentioned
8. **Oversimplification of the minimum**: for projects with complex architecture, three items may be insufficient, especially when Claude Code is used for tasks requiring deep architectural understanding

---

## 9. Practical Recommendations

### 9.1 Complete Configuration Architecture for Claude Code

Instead of thinking only about CLAUDE.md, design the complete instruction system:

| Layer | Mechanism | Loading | Enforcement | Ideal use |
|-------|-----------|---------|-------------|-----------|
| Core | Root CLAUDE.md | Always | Advisory | Description, package manager, build commands |
| Modular | `.claude/rules/` without paths | Always | Advisory | Universal modular rules by topic |
| Conditional | `.claude/rules/` with paths | On file access | Advisory | Domain rules (API, frontend, tests) |
| Hierarchical | Subdirectory CLAUDE.md | On navigation | Advisory | Package/module context |
| On-demand | Skills | On invocation | Advisory | Workflows, procedures, patterns |
| Isolated | Skills with `context: fork` | On invocation (isolated) | Advisory | Analysis, exploration, independent tasks |
| Deterministic | Hooks | Programmatic | Guaranteed | Linting, tests, validation, formatting |
| Emergent | Self-managed memory | Startup + on-demand | Advisory | Discovered patterns, cross-session context |
| Composition | @imports | When parent loads | Advisory | Instruction reuse across projects |

### 9.2 For New Projects

1. **Start with three lines in CLAUDE.md**: description, package manager, build commands
2. **Create `.claude/rules/` from the start**: even with few files, the structure signals intent
3. **Use path-scoping from day one**: API rules in `rules/api.md` with `paths: ["src/api/**"]`
4. **Convert critical rules to hooks immediately**: pre-commit tests, linting, formatting
5. **Do not use `/init`**: write the CLAUDE.md manually with the three minimum items

### 9.3 For Existing Projects with Inflated CLAUDE.md

1. **Audit all instruction sources**: CLAUDE.md + rules + memory + skills -- map the total
2. **Use the guide's refactoring prompt**: identify contradictions, extract essentials, group the rest
3. **Convert "ALWAYS"/"NEVER" to hooks**: deterministic enforcement removes from the context budget
4. **Move domain rules to path-scoped rules**: TypeScript rules with `paths: ["**/*.ts"]`
5. **Encapsulate workflows in skills**: deploy, migration, code generation as invocable skills
6. **Remove what Claude already knows**: standard language conventions, universal best practices
7. **Test incrementally**: remove an instruction, observe the behavior, repeat

### 9.4 For Monorepos

1. **Root CLAUDE.md**: monorepo purpose + shared tooling (3-5 lines)
2. **Package CLAUDE.md**: package purpose + stack + reference to detailed conventions
3. **`claudeMdExcludes`**: configure to avoid loading CLAUDE.md from other teams
4. **Shared rules**: use symlinks in `.claude/rules/` for organizational conventions
5. **Shared skills**: skills at root for workflows common to all packages

### 9.5 Relationship with AGENTS.md in Multi-Tool Projects

1. **AGENTS.md as primary source**: if the project supports multiple tools, maintain AGENTS.md as the universal reference
2. **CLAUDE.md as extension**: use CLAUDE.md for Claude Code-specific features (rules, skills, hooks)
3. **Symlink for common content**: `ln -s AGENTS.md CLAUDE.md` if the base content is identical
4. **Or independent CLAUDE.md**: if Claude Code needs specific instructions that do not apply to other tools
5. **Avoid duplication**: do not maintain identical instructions in both files without a symlink

### 9.6 For Continuous Maintenance

1. **Treat CLAUDE.md as code**: code review, Git history, PRs for significant changes
2. **Review periodically**: Anthropic's documentation recommends: "review it when things go wrong, prune it regularly, and test changes by observing whether Claude's behavior actually shifts"
3. **Synchronize with memory**: periodically check that auto-memory does not contradict CLAUDE.md
4. **Monitor cost**: track whether CLAUDE.md changes impact the token cost per session
5. **Document exclusions**: when removing something, record the reason to prevent re-addition
6. **Use Anthropic's heuristic**: "For each line, ask: 'Would removing this cause Claude to make mistakes?' If not, cut it."
