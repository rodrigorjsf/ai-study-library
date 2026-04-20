# Analysis: Prompt Engineering Guide

> **Status**: Current
> **Source document**: [Prompt Engineering Guide](docs/prompt-engineering-guide.md)
> **Analysis date**: 2026-03-27
> **Scope**: Comprehensive prompt engineering techniques analysis for agent infrastructure

---

## 1. Executive Summary

The `prompt-engineering-guide.md` is the most extensive and dense document in the project, cataloging over 58 prompt engineering techniques with quantitative benchmarks, token costs, and applicability in multi-agent architectures. Its importance for agent infrastructure is direct: every SKILL.md, every sub-agent prompt, every rule in `.claude/rules/`, every hook, and every memory entry is ultimately a prompt — and the effectiveness of these artifacts depends on the correct (or incorrect) application of the techniques cataloged in this guide.

The most relevant finding for the project is the **paradigm inversion**: advanced reasoning models (o1, R1, Claude with extended thinking) perform worse with classic techniques like few-shot and explicit CoT. This directly impacts the writing of skills and sub-agent prompts — techniques that work in conversational prompts can be counterproductive in agentic contexts. The guide also documents the transition from "prompt engineering" to "context engineering," aligning perfectly with `research-context-engineering-comprehensive.md` and validating the progressive disclosure approach advocated in `a-guide-to-agents.md`.

For the `agent-engineering-toolkit`, this document serves as the **technical reference base** for all prompting decisions across both skill sets (plugin and standalone). Every technique cataloged here has direct application in at least one of the artifacts that skills generate: AGENTS.md, CLAUDE.md, SKILL.md, rules, hooks, or sub-agent prompts.

---

## 2. Technique-by-Technique Analysis

### 2.1 Role Prompting

**What it is and how it works.** Instructs the model to adopt a professional persona before executing the task. Adjusts probability distribution toward vocabulary, depth, and style typical of the persona. Minimal cost: 10-30 tokens. Best cost-benefit ratio for style control among all techniques.

**When to use.** Tone and style control; domain specialization; creating agents with a defined identity. In multi-agent systems, it is the fundamental specialization mechanism — each sub-agent receives a role via system prompt.

**When NOT to use.** Role prompting does not improve factual accuracy in frontier models. For reasoning tasks, 2-shot CoT consistently outperforms role prompts (Schulhoff et al., 2024). Do not use as a substitute for specific instructions.

**Application in skills (SKILL.md).** Define the executing agent's role on the very first line of SKILL.md. Example: "You are a software architecture analyst specializing in TypeScript repositories." Keep to 1-2 sentences — brevity is essential given the attention budget.

```markdown
# Example in SKILL.md — Role Prompting
You are a configuration engineer specializing in AI agent infrastructure.
Your task is to analyze the repository and generate an optimized AGENTS.md.
```

**Application in hooks (pre/post prompts).** Hooks are short by nature. Role prompting in hooks should be implicit, not explicit — the action context already defines the role. Example pre-commit hook: "Verify that changes follow project conventions" (reviewer role is implicit). Avoid spending tokens on "You are an experienced code reviewer..." in 2-3 line hooks.

**Application in sub-agents.** This is the strongest use case for role prompting. Each sub-agent receives a specialized persona that directs its behavior. Per the guide: "In Anthropic's research system, each sub-agent receives a specialized role via system prompt."

```markdown
# Example of sub-agent delegation
Delegate to the sub-agent with the following role:
"You are a dependency analyst. Examine package.json, go.mod, or
Cargo.toml and return: primary language, framework, package manager,
and critical dependencies in JSON format."
```

**Application in rules (.claude/rules/).** Rules should not use role prompting. They are direct, factual instructions — adding a persona wastes tokens and adds no value in limited-scope rules.

**Application in memory.** Memory entries are factual and descriptive. Role prompting is irrelevant for memory — never use.

---

### 2.2 Zero-Shot Prompting

**What it is and how it works.** The model receives only the instruction, with no examples. Relies on pre-trained knowledge. Modern models achieve ~85% accuracy on simple tasks. Lowest token cost among all techniques.

**When to use.** Tasks the model already does well natively: simple classification, translation, summarization, brainstorming. When token efficiency is a priority (hooks, rules, memory).

**When NOT to use.** Complex multi-step reasoning; tasks requiring very specific output formats; ambiguous classifications; tasks outside common training patterns.

**Application in skills.** Most phase instructions in SKILL.md should be zero-shot. Well-written skills provide sufficient context for the model to execute without examples. Reserve few-shot only for phases with critical output formats.

```markdown
# Zero-shot example in a skill phase
## Phase 2: Structure Analysis
Examine the repository's directory structure.
Identify: languages used, frameworks, architectural patterns.
Return findings in bullet list format.
```

**Application in hooks.** Hooks should be predominantly zero-shot. They are short, execute specific tasks, and tokens are precious. "Verify that the commit message follows conventional commits format" is sufficient — no examples needed.

**Application in sub-agents.** Sub-agents with simple, well-defined tasks can operate in zero-shot. For complex tasks or those with specific output formats, consider few-shot.

**Application in rules.** Rules are zero-shot by definition. They are direct instructions: "Use 2-space indentation", "API handlers live in src/api/handlers/". Do not include examples in rules — wastes tokens loaded in every session.

**Application in memory.** Memory entries are zero-shot — they are facts, not instructions with examples.

---

### 2.3 Few-Shot Prompting

**What it is and how it works.** Provides 2-5+ input-output pairs as a "mini training set." The model identifies the mapping and generalizes. Anthropic recommends 3-5 diverse examples encapsulated in XML tags. The order of examples matters significantly.

**When to use.** Specific and critical output formats; structured data extraction; patterns the model does not correctly infer in zero-shot; tone/style calibration that role prompting alone cannot resolve.

**When NOT to use.** With advanced reasoning models (o1, R1) — examples hurt performance. After 5-10 examples, returns are diminishing. In always-loaded context artifacts (rules, root CLAUDE.md) — fixed cost on every request.

**Application in skills.** Few-shot is valuable in phases that generate artifacts with specific formats. Use in the output generation phase, not in analysis phases. Encapsulate examples in XML tags per Anthropic's recommendation.

```markdown
## Phase 4: AGENTS.md Generation
Generate the file following this format. Examples:

<example>
<input>React project with TypeScript, using pnpm workspaces</input>
<output>
# Project
React component library for accessible data visualization.
Uses pnpm workspaces.

## Conventions
For TypeScript conventions, see docs/TYPESCRIPT.md
</output>
</example>

<example>
<input>Go API with PostgreSQL, using make</input>
<output>
# Project
REST API for inventory management built with Go and PostgreSQL.

## Build
Run `make build` to compile. Run `make test` for all tests.
</output>
</example>
```

**Application in hooks.** Rarely necessary. If the hook needs to validate a format, a single example may be more efficient than a long textual description. Keep to at most 1 example.

**Application in sub-agents.** Useful when the sub-agent needs to return data in a specific structured format. Include 1-2 examples in the delegation prompt. Remember that examples compete with the limited context window budget of sub-agents.

**Application in rules.** Avoid. Rules are loaded in every session. Each example adds 50-200+ tokens of fixed cost. If a rule needs an example, consider converting it to a skill (on-demand loading).

**Application in memory.** Not applicable. Memory stores facts, not demonstrative examples.

---

### 2.4 System Prompts vs User Prompts

**What it is and how it works.** System prompt defines a persistent behavioral framework (identity, constraints, rules). User prompt carries the dynamic task (data, questions, contextual examples). Queries at the end of the prompt improve quality by up to 30%.

**When to use.** Always — it is the fundamental structure of every production prompt.

**When NOT to use.** It is not an optional technique, but rather an architectural decision about where to place each piece of information.

**Application in skills.** SKILL.md functions as the system prompt for skill execution. The phases are the progressive "user prompt." Keep the role and constraints at the top of SKILL.md, contextual data and specific instructions in the phases.

**Application in hooks.** Hooks are essentially short user prompts that operate under the session's system prompt. Do not attempt to redefine the system prompt within a hook.

**Application in sub-agents.** The system/user separation is critical for sub-agents. The delegation prompt must clearly define: (1) role and constraints (system-like), (2) specific task and data (user-like).

```markdown
# Sub-agent prompt with clear separation
## Context (system-like)
You are a test analyst. Examine only test files.
Never modify code — only analyze and report.

## Task (user-like)
Analyze the test patterns in `tests/` and return:
- Testing framework used
- Test file naming pattern
- Approximate coverage by code area
```

**Application in rules.** Rules are injected into the system prompt by Claude Code. Each rule should be written as a system prompt instruction — direct, factual, no conversation.

**Application in memory.** Memory is injected as additional context in the system prompt. It should contain facts and decisions, not task instructions.

---

### 2.5 Chain-of-Thought (CoT)

**What it is and how it works.** Encourages the model to generate intermediate reasoning steps before the final answer. Three variants: Few-Shot CoT (examples with reasoning), Zero-Shot CoT ("Let's think step by step"), Auto-CoT. On GSM8K, PaLM 540B jumped from 17.9% to 58.1% with CoT.

**When to use.** Multi-step reasoning; complex code analysis; architectural decisions requiring trade-off evaluation; debugging problems.

**When NOT to use.** Advanced reasoning models (o1, R1) — only 2-3% marginal improvement with 20-80% more time. Small models (<100B) — "fluent but illogical" chains. Simple one-step tasks. In limited-context artifacts (rules, hooks).

**Application in skills.** Use implicit CoT in analysis phases — instruct the model to "analyze each aspect before concluding." Use XML tags `<thinking>` and `<answer>` for structured separation when the phase requires complex reasoning.

```markdown
## Phase 3: Convention Analysis
For each convention found in the repository:
<thinking>
1. Identify the evidence (file, pattern, configuration)
2. Assess whether it is an explicit or inferred convention
3. Determine if it is relevant for AGENTS.md or better suited for progressive disclosure
</thinking>
<answer>
List only the conventions that passed the relevance filter.
</answer>
```

**Application in hooks.** Do not use CoT in hooks. Hooks must be fast and direct. If a hook needs complex reasoning, it should be a skill or a sub-agent.

**Application in sub-agents.** CoT is valuable in analysis sub-agents. The sub-agent can reason extensively without impacting the main context (context: fork). Allow the sub-agent to "think" freely before returning the synthesized result.

**Application in rules.** Never use CoT in rules. Rules are direct instructions, not reasoning prompts.

**Application in memory.** Memory can record the conclusion of a CoT reasoning, but not the process. Store "We decided to use PostgreSQL because..." (result), not the analysis steps.

---

### 2.6 Tree of Thoughts (ToT)

**What it is and how it works.** Generalizes CoT by allowing exploration of multiple reasoning paths in a tree structure, with self-evaluation and backtracking. On Game of 24: 4% (CoT) vs 74% (ToT) — 18.5x improvement. Requires 5-20x more API calls.

**When to use.** Complex planning problems; architectural decisions with multiple viable paths; exploration of alternatives where backtracking is valuable.

**When NOT to use.** The vast majority of agent infrastructure tasks. Prohibitive cost for routine use. Linear problems where CoT suffices.

**Application in skills.** Rarely directly. Can be implemented indirectly via multi-phase skills that explore alternatives and then converge. Example: Phase 3a generates option A, Phase 3b generates option B, Phase 4 evaluates and chooses.

**Application in hooks.** Never. Cost and latency incompatible with hooks.

**Application in sub-agents.** Can be implemented as an orchestrator-workers pattern: an orchestrator agent delegates exploration of N paths to N sub-agents, then synthesizes. The cost is acceptable when the decision is high-impact.

**Application in rules.** Irrelevant for rules.

**Application in memory.** Irrelevant for memory.

---

### 2.7 ReAct (Reasoning + Action)

**What it is and how it works.** Iterative Thought-Action-Observation loop. The model reasons about the state, executes a tool, receives the result, and repeats. Outperformed baseline methods by 34% absolute on ALFWorld.

**When to use.** Tasks with tools and real-time data; fact verification; repository exploration; any task that benefits from environment interaction.

**When NOT to use.** Pure reasoning without external data; when no tools are available; simple factual tasks.

**Application in skills.** ReAct is the natural pattern for repository analysis skills. Each exploration phase is implicitly a ReAct cycle: read files, reason about the content, decide next action. Skills should facilitate this by providing guidance on which tools to use and which files to examine.

```markdown
## Phase 2: Repository Exploration
Use the following tools to investigate:
- `glob` to find files by pattern
- `grep` to search for code patterns
- `read` to examine file contents

For each finding, reason about its relevance before proceeding.
```

**Application in hooks.** Hooks can implement mini ReAct cycles: check → evaluate → report. Example: post-commit hook that verifies if tests pass, evaluates the result, reports.

**Application in sub-agents.** Exploration sub-agents are fundamentally ReAct agents. The delegation prompt should list the available tools and guide the exploration cycle.

**Application in rules.** Irrelevant. Rules are static, not interactive.

**Application in memory.** The result of ReAct cycles can be stored in memory to avoid re-exploration. Example: "The project uses Jest with configuration in jest.config.ts" — result of prior exploration.

---

### 2.8 Self-Consistency (Majority Voting)

**What it is and how it works.** Samples N diverse reasoning paths for the same problem and selects the most frequent answer by majority voting. +17.9% over CoT on GSM8K with as few as 3 samples.

**When to use.** High-reliability decisions where error is costly; ambiguous classifications.

**When NOT to use.** Open/creative generation; latency-sensitive applications; cost-constrained (5-30x normal cost).

**Application in skills.** Can be implemented in critical decision phases: generate analysis N times and converge. In practice, rarely justifiable for AGENTS.md/CLAUDE.md generation, but can be valuable in audit skills.

**Application in hooks.** Never. Prohibitive cost for hooks.

**Application in sub-agents.** Can be implemented by dispatching the same prompt to 3 sub-agents and synthesizing the responses. Useful for security analysis or high-criticality code review.

**Application in rules.** Irrelevant.

**Application in memory.** Irrelevant.

---

### 2.9 Prompt Chaining (Pipeline Decomposition)

**What it is and how it works.** Breaks complex tasks into sequential subtasks. Each step uses a focused prompt with a single objective. 2-5x higher cost than a single prompt, but with higher quality and debuggability.

**When to use.** Complex multi-step workflows; when inspecting intermediate outputs is necessary; when per-step quality matters more than speed.

**When NOT to use.** Simple tasks; when additive latency is unacceptable; when the model handles the task well in a single prompt.

**Application in skills.** Skills are fundamentally prompt chains. Each phase is a link in the chain: Explore → Analyze → Plan → Generate → Validate. The output of each phase feeds the input of the next. This is the most important pattern for the project.

```markdown
# SKILL.md structure as Prompt Chain
## Phase 1: Exploration (output: inventory of relevant files)
## Phase 2: Analysis (input: inventory; output: structured findings)
## Phase 3: Planning (input: findings; output: content plan)
## Phase 4: Generation (input: plan; output: final artifact)
## Phase 5: Validation (input: artifact; output: compliance report)
```

**Application in hooks.** Hooks can implement mini-chains of 2-3 steps: check → decide → act.

**Application in sub-agents.** The orchestrator-workers pattern is distributed prompt chaining. The orchestrator decomposes, delegates to workers, and synthesizes results.

**Application in rules.** Rules can reference other rules or docs creating a resolution chain, but they are not chains in the technical sense.

**Application in memory.** Irrelevant directly, but memory can store intermediate results from long chains for retrieval in future sessions.

---

### 2.10 Structured Output (JSON, XML, Schemas)

**What it is and how it works.** Techniques to force outputs into machine-readable formats. Critical finding: forcing JSON during reasoning degrades accuracy by 10-15%. The recommended practice is free reasoning first, formatting after. XML has a 15-20% performance boost in Claude due to specific training.

**When to use.** Outputs consumed by systems; inter-agent communication; data extraction; when format compliance is mandatory.

**When NOT to use.** During reasoning (degrades accuracy). For outputs that humans will read directly (Markdown is better).

**Application in skills.** Use structured output for communication between phases and between skills. Within the skill, separate reasoning from formatting: first analyze freely, then format in JSON/YAML.

```markdown
## Phase 2: Analysis
Freely analyze the conventions found. Then, structure the findings:

<analysis_output>
{
  "language": "TypeScript",
  "framework": "Next.js",
  "package_manager": "pnpm",
  "conventions": [
    {"rule": "2-space indentation", "evidence": "prettier.config.js", "confidence": "high"}
  ]
}
</analysis_output>
```

**Application in hooks.** Validation hooks can require structured output for programmatic processing (e.g., list of violations in JSON).

**Application in sub-agents.** Critical. Sub-agents should return results in structured format so the orchestrator can synthesize. JSON is preferred because it is less prone to inappropriate modification by the model. Per the long-running agents guide: "Feature list in JSON (not Markdown) — model is less prone to modify JSON inappropriately."

**Application in rules.** Rules can specify expected output formats: "Always return linting errors in JSON format with fields: file, line, rule, message."

**Application in memory.** Memory uses Markdown by design (human readability). Do not use JSON for memory.

---

### 2.11 RAG Prompting Patterns

**What it is and how it works.** Combines external document retrieval with generation. Patterns: context injection, dual prompt structure, N-shot RAG, CoT RAG, agentic RAG.

**When to use.** When the model needs information not in its training data; factual grounding; project-specific documentation.

**When NOT to use.** When the information is common and the model already knows it; when search results will be poor; purely generative tasks.

**Application in skills.** Skills implement RAG implicitly: the exploration phases retrieve context (read files, search for patterns) that feed the generation phases. The `references/` section of each skill is essentially a pre-curated RAG corpus.

```markdown
## Phase 1: Context Retrieval
Read the following reference files to guide your analysis:
- references/evidence-based-conventions.md
- references/progressive-disclosure-patterns.md

Then, examine the repository to collect specific evidence.
```

**Application in hooks.** Hooks can implement agentic RAG: decide whether they need to retrieve context before acting.

**Application in sub-agents.** Research sub-agents are RAG agents by nature: they retrieve, analyze, synthesize.

**Application in rules.** Rules can guide the model to retrieve context before acting: "Before modifying files in src/api/, read docs/API_CONVENTIONS.md."

**Application in memory.** Claude Code's auto memory is a RAG system: MEMORY.md as index, topic files as corpus, on-demand loading as retrieval.

---

### 2.12 Meta-Prompting

**What it is and how it works.** Prompts that generate prompts. Three meanings: scaffolding (LLM as conductor of specialists), practical optimization (strong model generates prompts for cheap model), structural (formalization via category theory). +17.1% vs standard prompting.

**When to use.** Optimization of existing prompts; generation of specialized prompts for multiple domains; when manual prompts reach a quality plateau.

**When NOT to use.** For simple tasks; when optimization cost is not justified; single-use prompts.

**Application in skills.** Meta-prompting is the essence of initialization skills. The skill that generates AGENTS.md is a meta-prompt: a prompt that analyzes the repository and generates instructions (prompts) for future agents.

```markdown
# The initialization skill is fundamentally meta-prompting:
# Prompt (SKILL.md) → analyzes repo → generates AGENTS.md → which will be a prompt for future agents
```

**Application in hooks.** Prompt optimization hooks can use meta-prompting: a hook that reviews and suggests improvements to prompts before commit.

**Application in sub-agents.** The orchestrator-workers pattern is meta-prompting: the orchestrator generates specific prompts for each worker dynamically.

**Application in rules.** Irrelevant directly.

**Application in memory.** Irrelevant directly.

---

### 2.13 Relevant Frontier Techniques

#### Constitutional AI and Self-Critique

**Application in skills.** Validation phases implement self-critique: the model reviews its own output against principles. Use an explicit "constitution" in the validation phase.

```markdown
## Phase 5: Validation
Review the generated AGENTS.md against these principles:
- Is each instruction specific and verifiable?
- Is the file under 200 lines?
- Were volatile information items excluded?
- Was progressive disclosure applied correctly?
If any principle was violated, revise the artifact.
```

#### Step-Back Prompting

**Application in skills.** Useful in analysis phases: before examining repository details, ask a higher-level abstraction question. "What is the general purpose of this repository?" before "What are the code conventions?"

#### Rephrase and Respond (RaR)

**Application in skills.** Useful when the phase prompt is complex: instructing the model to rephrase the task before executing ensures correct comprehension.

#### Skeleton-of-Thought (SoT)

**Application in skills.** Suitable for long document generation phases: generate outline first, expand later. Aligns naturally with the Plan → Generate pattern of skills.

---

## 3. Points of Attention

### 3.1 Common Misapplications

| Error | Consequence | Correction |
|-------|-------------|------------|
| Few-shot in rules | Fixed cost of 50-200+ tokens per example in every session | Move examples to skills or reference docs |
| Explicit CoT in hooks | Unnecessary latency in operations that should be fast | Hooks should be zero-shot and direct |
| Role prompting in rules | Tokens wasted without accuracy gains | Rules are instructions, not personas |
| Structured output during reasoning | 10-15% accuracy degradation | Separate free reasoning from formatting |
| Complex techniques (ToT, SC) on simple tasks | 5-30x cost without proportional benefit | Start with the simplest technique |
| Explicit CoT with reasoning models | Performance worse than zero-shot | Test before assuming CoT helps |
| Aggressive formatting (ALL-CAPS, "NEVER") | Worse results in recent Claude models | Direct tone without excessive emphasis |

### 3.2 When Simpler is Better

The guide repeatedly emphasizes: **"Start with the simplest possible solution and only increase complexity when demonstrably necessary."** For agent infrastructure, this means:

1. **Rules**: always zero-shot, always direct, no examples
2. **Hooks**: zero-shot, 1-3 sentences, no elaborate reasoning
3. **Memory**: raw facts, no prompting techniques
4. **Skills**: prompt chaining (multi-phase) with zero-shot by default, few-shot only when format is critical
5. **Sub-agents**: role + zero-shot by default, few-shot for specific return format

### 3.3 The Over-Engineering Paradox

The more prompting techniques are stacked in an infrastructure artifact, the more tokens are consumed, the more the attention budget is diluted, and the more the model tends to ignore instructions. `a-guide-to-agents.md` and `research-context-engineering-comprehensive.md` converge on this point: the "ideal AGENTS.md is small, focused, and points to other resources." Sophisticated prompting techniques should be used surgically, not by default.

---

## 4. Applicability Matrix Across Documents

This matrix maps each main technique from the prompt engineering guide to the principles of each of the project's 5 documents.

### 4.1 Technique → Document Mapping

| Technique | Evaluating-AGENTS-paper | research-context-engineering-comprehensive | claude-prompting-best-practices | a-guide-to-agents | a-guide-to-agents (CLAUDE.md) |
|-----------|------------------------|---------------------------------------------|-------------------------------|-------------------|-------------------------------|
| **Role Prompting** | Confirms that role prompting in AGENTS.md defines scope effectively | Consumes minimal attention budget (10-30 tokens) | Recommended in system prompt for persistence across turns | Project one-liner is implicit role prompting | CLAUDE.md can define project persona |
| **Zero-Shot** | Most effective instructions in AGENTS.md are zero-shot | Maximizes attention budget efficiency | Recommended as starting point before adding complexity | "Ideal AGENTS.md should be as small as possible" — zero-shot is the path | Rules and CLAUDE.md should be zero-shot |
| **Few-Shot** | Examples in AGENTS.md cost fixed tokens; avoid | Each example consumes 50-200+ tokens of limited budget | Recommends 3-5 examples in XML tags for format tasks | "Move specific rules to separate files" — avoid examples in root | Skills can use few-shot; CLAUDE.md should not |
| **System vs User** | AGENTS.md is fundamentally a system prompt | Instruction positioning affects adherence (lost-in-middle) | Place role in system, examples in user, queries at end | Root/package hierarchy is system/user hierarchy | CLAUDE.md/rules/skills hierarchy mirrors system/user |
| **Chain-of-Thought** | Not documented in AGENTS.md configs | CoT consumes significant tokens; use only when necessary | Recommends `<thinking>` and `<answer>` tags for Claude | Not relevant for static AGENTS.md | Analysis skills can use CoT in exploration phases |
| **ReAct** | Exploration loop is implicit in AGENTS.md evaluation | ReAct cycles progressively consume context | Foundation of Claude Code's agentic loop | Agents "are fast at navigating documentation hierarchies" — ReAct | Claude Code operates in native ReAct loop |
| **Prompt Chaining** | Multi-criteria evaluation is an implicit chain | Each chain link is a compaction opportunity | "Explicit chaining useful when you need to inspect intermediaries" | Progressive disclosure is a resolution chain | Multi-phase skills are prompt chains |
| **Structured Output** | Metrics in structured format for evaluation | JSON preferred for inter-agent state (less prone to modification) | XML has 15-20% boost in Claude; JSON for inter-system | AGENTS.md is Markdown; intermediate outputs can be JSON | Rules can specify formats; memory uses Markdown |
| **RAG Patterns** | AGENTS.md as "pre-loaded context" is static RAG | Progressive disclosure + JIT = agentic RAG | "Agentic RAG: LLM decides when to retrieve" | "Let the agent generate JIT documentation" — agentic RAG | Skills with `references/` are pre-curated RAG |
| **Meta-Prompting** | Meta-analysis of AGENTS.md effectiveness | Automatic optimization significantly outperforms manual | Anthropic's prompt generator is meta-prompting | AGENTS.md refactoring prompt is a meta-prompt | Initialization skill generates prompts for future agents |
| **Self-Critique** | AGENTS.md quality validation | Critique-revision cycles cost 2-3x per response | Evaluate → revise loop is recommended pattern | "Find contradictions" in refactoring prompt | Validation phase in skills is self-critique |
| **Step-Back** | Ask "What is this repo for?" before analyzing | Abstraction reduces tokens spent on irrelevant exploration | 7-27% improvement over CoT | Project one-liner is an implicit step-back | Before generating CLAUDE.md, understand the project's purpose |

### 4.2 Convergent Principles

Five principles emerge from the convergence across all documents:

1. **Aggressive minimalism**: All documents agree that less is more. The prompts guide confirms that simple techniques are sufficient for most tasks, and complex techniques have diminishing returns.

2. **Progressive disclosure as architecture**: The pattern of loading context on-demand appears as agentic RAG in the prompts guide, as JIT documentation in the research, as skills in Claude Code, and as file hierarchy in AGENTS.md.

3. **Separation of reasoning and formatting**: The prompts guide documents the 10-15% degradation when forcing format during reasoning. This validates the phased approach in skills: explore freely, then format.

4. **Start simple, add complexity with evidence**: The prompts guide, Anthropic, and the AGENTS.md guide converge: zero-shot first, advanced techniques only with evidence of need.

5. **Context is a finite resource**: The research's attention budget, the AGENTS.md guide's instruction budget, and the per-technique token cost in the prompts guide are facets of the same principle.

---

## 5. Context Engineering Implications

### 5.1 Attention Budget and Prompting Techniques

`research-context-engineering-comprehensive.md` establishes that the practical instruction budget per file is ~200 lines (~2,000-4,000 tokens). The prompt engineering guide adds specific per-technique costs:

| Technique | Token Cost | Budget Impact |
|-----------|-----------|---------------|
| Role prompting | 10-30 tokens | Negligible — use freely |
| Zero-shot | 0 extra tokens | None — always prefer |
| Few-shot (3 examples) | 150-600 tokens | 4-15% of a CLAUDE.md budget |
| Explicit CoT | 2-3x of base prompt | Significant — use only in skills |
| Self-Consistency | 5-30x of base cost | Prohibitive for static artifacts |
| Structured output | +10-20% (JSON) | Moderate — acceptable for inter-agent |

**Practical implication**: In always-loaded artifacts (CLAUDE.md, rules without path-scope), every token matters. Techniques that add tokens (few-shot, CoT) should be reserved for on-demand artifacts (skills, sub-agents).

### 5.2 Lost-in-the-Middle and Technique Positioning

The research documents that performance is highest when relevant information is at the beginning or end of the context. The prompts guide confirms that "queries at the end of the prompt improve quality by up to 30%."

**Implications for agent infrastructure:**

- **SKILL.md**: Role and constraints at the top (beginning of context). Final generation phase at the end. Intermediate analysis phases in the middle (less critical).
- **Rules**: Most critical instructions first. If a rule has multiple instructions, the most important one should open the file.
- **CLAUDE.md**: Fundamental conventions at the top. Secondary instructions in the middle. Environment/setup instructions at the end.
- **Sub-agent prompts**: Role at the top, tools in the middle, specific task at the end.

### 5.3 Progressive Disclosure as Cost Mitigation

The prompts guide documents that advanced techniques cost 2-30x more tokens. The research documents that context rot degrades performance with more tokens. The convergent solution is progressive disclosure:

```
Always-loaded (CLAUDE.md, global rules):
→ Zero-shot, implicit role, no examples
→ Budget: ~200 lines, ~3,000 tokens

On-demand (skills, rules with path-scope):
→ Zero-shot + selective few-shot + CoT in analysis phases
→ Budget: more generous (isolated or temporary context)

Isolated (sub-agents with context: fork):
→ All techniques available
→ Budget: full sub-agent context window
→ No impact on main context
```

### 5.4 Compaction and Prompting Techniques

When context is compacted, details of elaborate techniques (CoT chains, few-shot examples) are naturally discarded. This means:

- Critical information should be in static artifacts (not dependent on compaction)
- Elaborate techniques should be used in contexts that will not be compacted (sub-agents with context: fork)
- If an instruction is important enough to survive compaction, it should be a simple fact, not an elaborate example

---

## 6. Practical Recipes

### 6.1 Recipe: Writing a New Skill

```markdown
# SKILL.md — Template Based on Prompting Techniques

# Skill Name
[Role prompting: 1 sentence defining who the agent is]
[Step-back: 1 sentence about the general purpose]

## Phase 1: Exploration [ReAct]
[Zero-shot: direct instructions on what to explore]
[List available tools: glob, grep, read]
[Guidance on the cycle: observe → reason → next action]

## Phase 2: Analysis [Implicit CoT]
[Zero-shot: analysis instructions]
[Separation of reasoning and formatting]
<thinking>
[Guidance on aspects to analyze]
</thinking>
<findings>
[Structured format for findings]
</findings>

## Phase 3: Planning [Prompt chaining — receives Phase 2 output]
[Zero-shot: planning instructions]
[Reference to docs/references/ for criteria — RAG]

## Phase 4: Generation [Few-shot if format is critical]
[1-2 examples in XML tags if needed]
[Output template]

## Phase 5: Validation [Self-critique / Constitutional AI]
[List of principles for self-evaluation]
[Revision instructions if principles were violated]
```

**Techniques used**: Role prompting (top), ReAct (exploration), CoT (analysis), Prompt chaining (multi-phase), Few-shot (generation, if needed), Self-critique (validation), Step-back (contextualization), Structured output (between phases).

### 6.2 Recipe: Sub-Agent Delegation Prompt

```markdown
# Sub-Agent Delegation Template

## Role [Role prompting]
You are a [specialization]. Your goal is [expected outcome].

## Constraints [System prompt behavior]
- Never modify files — only analyze and report
- Limit your analysis to [scope]
- Return results in JSON format

## Available Tools [ReAct enablement]
- `glob`: find files by pattern
- `grep`: search content in files
- `read`: read file contents

## Task [User prompt — at the end for 30% boost]
Analyze [target] and return:
[List of expected fields]

## Return Format [Structured output]
<result>
{
  "field1": "...",
  "field2": ["..."],
  "confidence": "high|medium|low"
}
</result>
```

**Principles applied**: Role at the top (role prompting at the beginning of context), constraints as system prompt, tools listed for ReAct, task at the end (lost-in-the-middle), structured output in JSON (inter-agent).

### 6.3 Recipe: Rule with Path-Scope

```markdown
# Rule Template — .claude/rules/[topic].md

---
paths:
  - "[glob pattern]"
---

# [Topic] — Rules

[Zero-shot: direct instructions, no examples]

- [Most critical instruction first — primacy positioning]
- [Secondary instruction]
- [Tertiary instruction]

[If external reference is needed — RAG pointer]
For details, see docs/[reference].md
```

**Principles applied**: Zero-shot exclusively (no examples to save tokens), most important instruction first (lost-in-the-middle), path-scope for progressive disclosure, reference to docs for JIT loading.

**Concrete example:**

```markdown
---
paths:
  - "src/api/**/*.ts"
---

# API Development Rules

- All endpoints must include input validation with Zod schemas
- Error responses follow the RFC 7807 format (Problem Details)
- Handlers live in src/api/handlers/, validators in src/api/validators/
- For authentication patterns, see docs/auth-patterns.md
```

### 6.4 Recipe: Memory Entry

```markdown
# Memory Entry Template

## [Topic] — [Date]

[Direct fact, no prompting techniques]
[Decision made + justification in 1 sentence]
[Reference to file/doc if relevant]
```

**Principles applied**: Pure zero-shot (memory is fact, not prompt), aggressive minimalism (every token counts in the 200-line MEMORY.md budget), factual information that survives compaction.

**Concrete example:**

```markdown
## Test Architecture — 2026-03-15

- Framework: Jest with ts-jest for TypeScript
- Naming pattern: `[module].test.ts` co-located with the code
- Shared fixtures in `tests/fixtures/`
- Main command: `pnpm test` (runs all), `pnpm test:watch` (watch mode)
- Decision: external mocks isolated in `tests/__mocks__/` per determinism requirement
```

### 6.5 Recipe: Hook Prompt

```markdown
# Hook Prompt Template

[Zero-shot: 1-3 sentences describing the verification]
[Success/failure criteria]
[Action on failure — if applicable]
```

**Principles applied**: Zero-shot exclusively (hooks must be fast), extreme minimalism (every hook token is a cost on every execution), no role prompting (role is implicit in the action context).

**Concrete example for pre-commit hook:**

```markdown
Verify that the commit message follows conventional commits format:
{type}({scope}): {description}

Valid types: feat, fix, docs, chore, refactor, test, perf, ci.
If the format is incorrect, reject the commit and suggest a correction.
```

---

## 7. Strengths and Limitations

### 7.1 Strengths of the Guide

1. **Comprehensive coverage**: 58+ techniques documented with quantitative benchmarks, not just qualitative descriptions. Enables informed decisions on cost-benefit of each technique.

2. **Counter-intuitive finding documented**: The paradigm inversion with reasoning models (classic techniques hurt performance) is essential to avoid over-engineering in skills and sub-agents. Without this information, the natural tendency would be to add CoT and few-shot everywhere.

3. **Quantified token costs**: Knowing that few-shot costs 50-200+ tokens per example or that Self-Consistency multiplies cost by 5-30x enables concrete attention budget planning.

4. **Decision matrices**: The comparative tables by task type and model tier are practical reference tools for technique selection.

5. **Multi-agent section**: The analysis of how techniques apply in multi-agent architectures is directly relevant to the project, which generates infrastructure for agents.

6. **Synergistic and conflicting combinations**: Knowing that "Few-shot + reasoning models" hurts performance or that "CoT + Self-Consistency" amplifies is critical knowledge for prompt design.

### 7.2 Limitations of the Guide

1. **Focus on API prompts, not agent infrastructure**: The guide covers techniques for direct model prompts, but does not systematically map how each technique translates to infrastructure artifacts (AGENTS.md, rules, hooks, skills). This analysis fills that gap.

2. **Absence of agent infrastructure examples**: All examples are from conversational or API prompts. Missing are examples of how to apply role prompting in a SKILL.md or CoT in a skill phase.

3. **Academic domain benchmarks**: GSM8K, Game of 24, ALFWorld — benchmarks relevant for academic validity, but distant from practical tasks of AGENTS.md generation or repository analysis.

4. **Rapid evolution**: Many benchmarks are from 2022-2024. Models from 2026 may have different characteristics, especially reasoning models that change the dynamics of classic techniques.

5. **Absence of infrastructure combination guidance**: The guide lists synergistic and conflicting combinations, but does not guide on which combination to use for "generating an AGENTS.md" or "delegating analysis to a sub-agent."

6. **Computational cost not mapped to agent context**: Token costs are presented in absolute terms, but not in terms of the 200-line attention budget of a CLAUDE.md or the limited context of a sub-agent.

---

## 8. Recommendations

### 8.1 Priority Techniques for Agent Infrastructure

Ordered by impact and cost-benefit ratio for the project:

**Tier 1 — Always use:**

| Technique | Where | Justification |
|-----------|-------|---------------|
| **Zero-shot** | Rules, hooks, memory, simple skill phases | Minimal cost, proven effectiveness for direct instructions |
| **Role prompting** | Top of SKILL.md, sub-agent prompts | 10-30 tokens for complete agent specialization |
| **Prompt chaining** | Multi-phase skill structure | Fundamental decomposition pattern — the entire skill is a chain |
| **System vs User separation** | Sub-agent prompts, SKILL.md structure | Basic organization that improves adherence |

**Tier 2 — Use when necessary:**

| Technique | Where | Justification |
|-----------|-------|---------------|
| **Few-shot** (1-2 examples) | Generation phases with critical format | When output format cannot be inferred by zero-shot |
| **CoT** (implicit) | Analysis phases in skills, analysis sub-agents | When multi-step reasoning is necessary; never in rules/hooks |
| **Structured output** | Inter-phase communication, sub-agent returns | JSON for inter-agent, XML for Claude, Markdown for humans |
| **ReAct** (guidance) | Exploration phases in skills | List available tools and guide exploration cycle |
| **Self-critique** | Validation phases in skills | Review loop against explicit principles |
| **Step-back** | Beginning of analysis skills | Contextualize before detailing — minimal cost, significant gain |

**Tier 3 — Use exceptionally:**

| Technique | Where | Justification |
|-----------|-------|---------------|
| **Meta-prompting** | Skills that generate prompts/configs for other agents | The initialization skill is already meta-prompting by nature |
| **Self-Consistency** | High-criticality decisions via multiple sub-agents | 5-30x cost — justifiable only for irreversible decisions |
| **Tree of Thoughts** | Exploration of architectural alternatives | Implementable via orchestrator-workers, not via direct prompt |
| **RAG patterns** | Skills with `references/` as corpus | Already implemented implicitly in the references structure |

**Tier 4 — Avoid in agent infrastructure:**

| Technique | Reason |
|-----------|--------|
| **Emotion prompting** | Irrelevant for technical configuration artifacts |
| **Multimodal CoT** | Agent infrastructure is textual |
| **Directional Stimulus** | Requires a trained policy model — unjustified overhead |
| **Skeleton-of-Thought** | Latency optimization irrelevant for config generation |

### 8.2 Golden Rules Derived

1. **In always-loaded artifacts (root CLAUDE.md, global rules), use exclusively zero-shot.** Every extra token is a cost on every request. Few-shot and CoT belong in on-demand artifacts.

2. **In skills, use prompt chaining as structure and zero-shot as the phase default.** Add few-shot only in generation phases with critical format. Add CoT only in complex analysis phases.

3. **In sub-agents, invest in role prompting and structured return output.** The role defines behavior, the return format ensures integration. Task always at the end of the prompt.

4. **Never use techniques that cost 5x+ in artifacts that are not isolated (context: fork).** Self-Consistency and ToT only make sense in isolated sub-agent contexts.

5. **Test before assuming.** The finding that reasoning models perform worse with classic techniques invalidates assumptions. Measure, don't presume.

6. **Treat each technique as a token investment.** Calculate the marginal cost (extra tokens) against the marginal benefit (measurable improvement) before adding complexity.

---

## Cross-References

- `docs/general-llm/prompt-engineering-guide.md` — Analyzed document
- `docs/general-llm/research-context-engineering-comprehensive.md` — Context engineering, attention budget, progressive disclosure
- `docs/general-llm/a-guide-to-agents.md` — AGENTS.md minimalism, progressive disclosure, instruction budget
- `docs/analysis/` — Project analysis directory
