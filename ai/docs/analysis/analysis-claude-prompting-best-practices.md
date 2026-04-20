# Analysis: Claude Prompting Best Practices

> **Status**: Current
> **Source document**: [claude-prompting-best-practices.md](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)
> **Analysis date**: 2026-03-27
> **Scope**: Official Anthropic prompt engineering guide for Claude 4.6 models — general prompting principles, long context handling, agentic systems, subagent orchestration, and anti-patterns

**Analyzed document**: `claude-prompting-best-practices.md`
**Complementary document**: `prompt-engineering-guide.md`

---

## 1. Executive Summary

The document `claude-prompting-best-practices.md` is Anthropic's official guide for prompt engineering with the Claude 4.6 models (Opus, Sonnet, and Haiku 4.5). It covers everything from fundamental principles of clarity and structuring to advanced techniques for agentic systems, including subagent orchestration, multi-window context management, and autonomous behavior control. The document distinguishes itself from generic prompting guides by being prescriptive and specific to the Claude family, featuring concrete prompt examples, API configurations, and model version migration patterns.

The most relevant finding for this project is that the document formalizes, from Anthropic's side, principles that converge strongly with the other four anchor sources of the project: instruction budget, progressive disclosure, minimalism, and the transition from "prompt engineering" to "context engineering." The section on agentic systems is particularly valuable, as it provides guidance directly applicable to writing skills, path-scoped rules, and subagent prompts — the central artifacts of this repository.

The `prompt-engineering-guide.md` complements by offering an academic and quantitative view with 58+ documented techniques, comparative benchmarks, and a decision matrix by model type and task. The intersection between the two documents reveals that many classical techniques (extensive few-shot, explicit CoT) can be counterproductive in advanced reasoning models like Claude Opus 4.6, requiring a more sophisticated and model-aware approach when writing agent infrastructure.

---

## 2. Key Findings and Principles

### 2.1 General Prompting Principles

| Principle | Description | Key Citation |
|-----------|-------------|--------------|
| Clarity and direction | Explicit instructions outperform vague ones. Explicitly ask for "above and beyond," don't expect inference. | *"Think of Claude as a brilliant but new employee who lacks context on your norms and workflows."* |
| Golden rule | Test the prompt with a colleague without context. If it confuses the human, it will confuse the model. | *"Show your prompt to a colleague with minimal context on the task and ask them to follow it."* |
| Motivational context | Explaining the "why" improves adherence. Claude generalizes from the explanation. | *"Your response will be read aloud by a text-to-speech engine, so never use ellipses..."* |
| Examples (few-shot) | 3-5 diverse, relevant examples in `<example>` tags produce the best format and tone results. | *"Include 3-5 examples for best results."* |
| XML structuring | XML tags disambiguate complex prompts that mix instructions, context, examples, and inputs. | *"Use consistent, descriptive tag names across your prompts."* |
| Role assignment | A single role sentence in the system prompt focuses behavior and tone. | `"You are a helpful coding assistant specializing in Python."` |

### 2.2 Long Context

The document establishes critical rules for prompts with 20k+ tokens:

- **Long data at the top**: Extensive documents and inputs should precede the query, instructions, and examples. Queries at the end improve quality by up to 30%.
- **XML structuring**: Multiple documents in `<document index="n">` with `<source>` and `<document_content>`.
- **Grounding in citations**: Asking Claude to extract relevant citations before executing the task reduces noise — `<quotes>` followed by `<info>` pattern.

### 2.3 Output and Formatting

Four format control strategies:

1. **Tell it what to do, not what not to do**: Instead of "Do not use markdown," use "Your response should be composed of smoothly flowing prose paragraphs."
2. **XML format indicators**: Tags like `<smoothly_flowing_prose_paragraphs>` to section the output.
3. **Mirror the desired style**: The prompt style influences the response style — removing markdown from the prompt reduces markdown in the output.
4. **Detailed instructions for specific preferences**: A `<avoid_excessive_markdown_and_bullet_points>` block with granular rules.

### 2.4 Tool Use

Key findings about tool use with Claude 4.6:

- **Explicitness and action**: Claude may suggest instead of implement if the prompt is ambiguous. Use "Change this function" instead of "Can you suggest some changes."
- **`<default_to_action>` block**: For proactive behavior by default.
- **`<do_not_act_before_instructions>` block**: For conservative behavior.
- **Overtriggering calibration**: Claude 4.6 is more responsive to the system prompt than previous versions. Aggressive language like "CRITICAL: You MUST use this tool when..." causes overtriggering. Use normal language: "Use this tool when..."
- **Native parallelism**: Claude 4.6 natively executes tool calls in parallel. A `<use_parallel_tool_calls>` block raises the rate to ~100%.

### 2.5 Thinking and Reasoning

- **Adaptive thinking** (`thinking: {type: "adaptive"}`) is the default for Claude 4.6 — the model dynamically decides when and how much to think.
- **Overthinking in Opus 4.6**: The model does excessive exploration at high effort. Solution: "Choose an approach and commit to it. Avoid revisiting decisions unless you encounter new information that directly contradicts your reasoning."
- **General instructions outperform prescriptive steps**: "think thoroughly" produces better reasoning than a manually written step-by-step plan.
- **Few-shot examples with thinking**: Placing `<thinking>` tags inside examples teaches the reasoning pattern.
- **Self-check**: "Before you finish, verify your answer against [test criteria]" works reliably for code and mathematics.

### 2.6 Agentic Systems

This is the richest section and the most directly applicable to the project:

**Long-horizon reasoning and state tracking**:

- Claude maintains orientation in extended sessions by focusing on incremental progress.
- Use structured files for state (`tests.json`) and free text for progress (`progress.txt`).
- Git as a state tracking mechanism between sessions.
- Context persistence prompt: *"Your context window will be automatically compacted as it approaches its limit... do not stop tasks early due to token budget concerns."*

**Multi-context-window workflows**:

1. First window: setup (tests, scripts). Future windows: iteration over the todo list.
2. Tests in structured format (`tests.json`) created before starting.
3. Quality-of-life scripts (`init.sh`) to avoid repetitive work.
4. New window vs. compaction: Claude 4.6 efficiently discovers filesystem state.
5. Verification tools (Playwright MCP, computer use).

**Autonomy/safety balancing**:

- Classify actions by reversibility: local/reversible = execute; destructive/shared = ask for confirmation.
- Concrete example: "Do not use destructive actions as a shortcut. For example, don't bypass safety checks (e.g. --no-verify)."

**Subagent orchestration**:

- Claude 4.6 recognizes and delegates to subagents natively, without explicit instruction.
- Risk: **subagent overuse** — "Claude Opus 4.6 has a strong predilection for subagents and may spawn them in situations where a simpler, direct approach would suffice."
- Criteria for subagents: parallelizable tasks, isolated context, independent workstreams. For simple tasks: work directly.

**Agentic anti-patterns**:

- **Overeagerness**: Opus 4.5/4.6 tends to overengineer. Block with instructions on scope, documentation, defensive coding, and minimal abstractions.
- **Hard-coding**: Claude may focus on making tests pass instead of general solutions. Prompt: "Tests are there to verify correctness, not to define the solution."
- **Code hallucinations**: `<investigate_before_answering>` block — never speculate about unread code.
- **Excessive file creation**: Claude uses files as scratchpad. Add a cleanup prompt at the end.

---

## 3. Points of Attention

### 3.1 Nuances Easy to Get Wrong

| Nuance | Risk | Mitigation |
|--------|------|------------|
| Aggressive language (ALL-CAPS, "CRITICAL", "MUST") | Overtriggering in Claude 4.6 — excessively literal and eager behavior | Use normal, conversational language. The prompting guide confirms: *"Aggressive formatting (ALL-CAPS, 'NEVER', 'ABSOLUTELY NOT') + recent Claude models: produces worse results."* |
| Deprecated prefill responses | Prefills in the last assistant turn no longer work in Claude 4.6 | Migrate to direct instructions, structured outputs, or tool calling |
| Word "think" with thinking disabled | Claude Opus 4.5 is particularly sensitive — may activate unintended reasoning | Use alternatives: "consider", "evaluate", "reason through" |
| Anti-laziness prompts from previous versions | Claude 4.6 is already proactive by default; prompts that encouraged thoroughness now cause overthinking | Remove or soften instructions like "If in doubt, use [tool]" |
| Explicit CoT with reasoning models | The prompt engineering guide documents that explicit CoT *hurts* reasoning models (o1, R1) with 2-3% marginal improvement and 20-80% more latency | For Claude 4.6 with adaptive thinking, prefer general instructions ("think thoroughly") over prescriptive steps |
| Few-shot with advanced reasoning models | Examples can constrain the internal reasoning process | Trust adaptive thinking; examples are more useful for format/tone than for reasoning |

### 3.2 Application Pitfalls in Agent Infrastructure

- **Documenting file structure in CLAUDE.md/AGENTS.md**: The prompting guide recommends grounding in citations, but the CLAUDE.md and AGENTS.md guides warn that paths change constantly and poison the context. The correct solution is to describe capabilities, not structure.
- **Confusing system prompt with user prompt**: The engineering guide is explicit — role and constraints in the system prompt (persistence between turns), few-shot examples in the user prompt (flexibility per task). In skills and rules, this translates to: stable conventions in path-scoped rules, dynamic instructions in the SKILL.md body.
- **Ignoring the token cost of examples in subagents**: The guide documents that each example adds 50-200+ tokens, and "in multi-agent systems, examples compete with the limited context window budget of subagents." Subagents should have lean prompts.

---

## 4. Use Cases and Scope

### 4.1 System Prompts vs User Prompts

| Element | System Prompt | User Prompt |
|---------|---------------|-------------|
| Role/persona | Yes — persistent between turns | No |
| Format constraints | Yes | Punctual refinement |
| Few-shot examples | No (unless fixed) | Yes — flexibility per task |
| Document context | No | Yes — dynamically injected |
| Security guardrails | Yes — always active | No |
| Specific query | No | Yes — at the end, after documents |

### 4.2 Single-turn vs Multi-turn

- **Single-turn**: Focus on clarity, few-shot examples, XML structuring. All information in the prompt.
- **Multi-turn**: Focus on state tracking, context awareness, compaction. The prompt needs to instruct about persistence and state recovery.
- **Multi-window**: Adds setup scripts, structured tests, and `progress.txt`. First window differs from subsequent ones.

### 4.3 Simple vs Complex Tasks

| Complexity | Recommended Techniques | Thinking Configuration |
|------------|----------------------|------------------------|
| Simple (classification, QA) | Zero-shot, direct instructions | Thinking disabled or effort low |
| Moderate (code generation, analysis) | Few-shot + XML tags, role prompting | Adaptive thinking, effort medium |
| Complex (refactoring, research, multi-step) | Prompt chaining, subagent orchestration, structured state | Adaptive thinking, effort high |
| Extreme (migrations, deep research) | Multi-window, parallel subagents, competing hypotheses | Opus 4.6, adaptive thinking, effort max |

---

## 5. Applicability to Agent Infrastructure

### 5.1 Skills (SKILL.md)

The document's best practices translate directly to SKILL.md writing:

**Phase-based structuring with implicit XML**:
The document recommends XML tags to disambiguate sections. In SKILL.md, the phases (`Phase 1: Codebase Analysis`, `Phase 2: Scope Detection`, etc.) serve as equivalent semantic separators. Each phase should have a single, clear objective, following the prompt chaining principle:

> *"With adaptive thinking and subagent orchestration, Claude handles most multi-step reasoning internally. Explicit prompt chaining is still useful when you need to inspect intermediate outputs or enforce a specific pipeline structure."*

**Hard Rules as system prompt guardrails**:
The `<RULES>` block at the beginning of SKILL.md functions as the skill's system prompt — constraints that must always be met. The recommendation of *"Tell Claude what to do instead of what not to do"* applies partially: prohibition rules (`NEVER`) are acceptable when the cost of violation is high (e.g., "NEVER exceed 200 lines per file"), but should be complemented with positive alternatives.

**Motivational context in instructions**:
The `init-claude` SKILL.md already exemplifies this principle with:
> *"Research shows that auto-generated comprehensive configuration files reduce agent task success by ~3% while increasing cost by 20%+"*

This motivation helps Claude understand *why* it should be minimalist, not just that it should be.

**Examples in references/**:
Instead of placing few-shot examples directly in SKILL.md (consuming budget), `references/` is used as progressive disclosure — loaded only when the relevant phase is executed. This aligns with: *"In-context examples are one of the most reliable ways to steer Claude's output format, tone, and structure"* without paying the token cost permanently.

**Practical recommendations for SKILL.md**:

```markdown
# Recommended pattern for phase instructions

### Phase N: [Phase Name]

[Motivational context — why this phase exists and what happens if done incorrectly]

[Direct and specific instruction — what to do, not what not to do]

[Conditional reference — "Read `references/X.md` if the project uses Y"]

[Success criterion — explicit verification of the result]
```

### 5.2 Hooks

Hooks execute before or after agent actions. The applicable prompting patterns are:

**Absolute clarity and direction**:
Hooks should be the shortest and most explicit prompts in the system. There is no room for ambiguity. The principle *"be specific about the desired output format and constraints"* is critical here.

**Mandatory structured output**:
Hooks frequently need machine-processable output. The document recommends two steps: free reasoning first, structured formatting after. For hooks, formatting should be the only step — no reasoning, just verification and output.

**Anti-overtriggering**:
The document warns that Claude 4.6 is more responsive to the system prompt. Hooks that use language like "ALWAYS run this check" may trigger in irrelevant contexts. Use specific conditions: "Run this check only when files in `src/api/` are modified."

### 5.3 Subagents

The document provides direct guidance on subagents — this is the richest section for this project:

**Subagent prompts must be self-contained**:
The *"context isolation"* principle from LangChain is reinforced by the document. Each subagent receives a complete prompt with role, task, and output format. Do not depend on inherited context from the orchestrator.

**Role prompting as a specialization mechanism**:
The prompt engineering guide is explicit: *"Role prompting is the fundamental specialization mechanism in multi-agent architectures."* Each subagent should have a clear role in the frontmatter (`description`) and in the delegation prompt.

**Scope control to avoid overuse**:

```text
# Recommended pattern for subagent delegation prompt
Analyze [specific scope]. Return ONLY [output format].
Do not [boundary — what is out of scope].
```

The document warns: *"Claude Opus 4.6 has a strong predilection for subagents and may spawn them in situations where a simpler, direct approach would suffice."* This means SKILL.md must be explicit about when to delegate vs. when to work directly.

**Token budget in subagents**:
The engineering guide documents that few-shot examples consume 50-200+ tokens each and *"compete with the limited context window budget of subagents."* Subagents should receive zero-shot instructions with structured output, not extensive examples.

**Structured output format**:
The document recommends structured outputs for inter-agent communication. The project already implements this with JSON formats in subagent output (e.g., `codebase-analyzer` returning structured analysis).

### 5.4 Rules (`.claude/rules/`)

Path-scoped rules are the equivalent of specialized system prompts by context. Applicable best practices:

**Precise scope = relevant context**:
The principle that *"every token in your AGENTS.md file gets loaded on every single request"* does not apply to rules — they only load when paths match. This is pure progressive disclosure. Each rule should cover a single topic, as the project already does (`git-commits.md`, `agent-files.md`, `plugin-skills.md`).

**Specific and actionable instructions**:
The context optimization document cites: *"Vague instructions consume attention without guiding behavior."* Rules like `"model: sonnet — never haiku (too weak for analysis) or opus (too costly)"` are examples of actionable specificity.

**Conversational tone, not aggressively imperative**:
The AGENTS.md guide recommends *"light touch, no 'always,' no all-caps forcing. Just a conversational reference."* The best practices document confirms: aggressive language causes overtriggering in Claude 4.6. Rules should use direct but not harsh language.

**Recommended pattern for rules**:

```markdown
---
paths:
  - "path/to/scope/**"
---
# [Single Topic]

- [Specific and actionable instruction]
- [Instruction with motivation when non-obvious]
- [Constraint with positive alternative]
```

### 5.5 Memory

The document provides specific guidance for memory management in agentic systems:

**Structured formats for state data**:
> *"Use structured formats for state data: When tracking structured information (like test results or task status), use JSON or other structured formats"*

**Free text for progress notes**:
> *"Use unstructured text for progress notes: Freeform progress notes work well for tracking general progress and context"*

**Git as a memory mechanism**:
> *"Git provides a log of what's been done and checkpoints that can be restored."*

**Memory and context awareness**:
Anthropic's memory tool is described as a natural complement to context awareness. The instruction *"save your current progress and state to memory before the context window refreshes"* is directly applicable to skills that operate in multi-window mode.

**Memory file structuring**:

- State files: JSON with defined schema (e.g., `tests.json` with `id`, `name`, `status` fields)
- Progress files: Free text with timestamps and next steps
- Naming convention: descriptive and predictable so Claude can discover them via filesystem exploration

---

## 6. Applicability of the Prompt Engineering Guide

### 6.1 Mapping Between Best Practices and Reasoning Techniques

| Technique (Eng. Guide) | Corresponding Best Practice | Relationship |
|------------------------|----------------------------|--------------|
| **Role Prompting** | "Give Claude a role" | Direct alignment — both recommend a role in the system prompt. The academic guide adds: role prompting does not improve factual accuracy; value is in style. |
| **Zero-Shot** | Default instruction style in best practices | Basis of nearly all instructions. Best practices assumes zero-shot as default and adds few-shot only for format. |
| **Few-Shot** | "Use examples effectively" (3-5 in `<example>` tags) | Direct alignment. The academic guide adds nuance: *"the order of examples matters significantly"* (Lu et al., 2021) and *"the label space matters more than label correctness"* (Min et al., 2022). |
| **Chain-of-Thought** | "Leverage thinking capabilities", "Manual CoT as a fallback" | Complementary — best practices recommends adaptive thinking as default, manual CoT only when thinking is disabled. The academic guide validates: explicit CoT is counterproductive in advanced reasoning models. |
| **Self-Consistency** | "Ask Claude to self-check" | Indirectly related — self-check is a lightweight form of self-consistency (verification, not majority voting). The cost of full self-consistency (5-30x tokens) is prohibitive for skills/subagents. |
| **Tree of Thoughts** | "Research and information gathering" with competing hypotheses | Complementary — the structured research prompt (*"develop several competing hypotheses"*) implements a lightweight version of ToT. The full cost of ToT (5-20x API calls) is impractical for most skills. |
| **ReAct** | The entire tool use + thinking framework | Fundamental alignment — Claude 4.6 with adaptive thinking and tools natively implements ReAct (Thought → Action → Observation). Best practices doesn't mention ReAct by name because *it is the model's default behavior*. |
| **Prompt Chaining** | "Chain complex prompts", subagent orchestration | Direct alignment. Best practices notes: *"With adaptive thinking and subagent orchestration, Claude handles most multi-step reasoning internally."* Explicit chaining is for inspection and control, not capability. |
| **Structured Output** | "Control the format of responses", XML tags | Direct alignment. The academic guide adds critical data: *"Forcing JSON during reasoning degrades accuracy by 10-15%"* — reason freely first, format afterward. |
| **RAG Patterns** | "Long context prompting", documents at top + query at end | Complementary — best practices implements RAG patterns without naming them. The academic guide's *"dual prompt structure"* maps directly to system prompt + user prompt with context. |
| **Meta-Prompting** | Not directly mentioned | Gap — meta-prompting (LLM generating/optimizing prompts) is not covered by best practices, but is relevant to this project (skills that generate CLAUDE.md are a form of meta-prompting). |
| **Constitutional AI** | "Balancing autonomy and safety", self-correction chaining | Indirectly related — the generate → review → refine pattern is a practical implementation of the Constitutional AI critique → revision loop. |
| **Step-Back Prompting** | Not directly mentioned | Applicable to skills: before generating a CLAUDE.md, ask "What are the fundamental principles of a good CLAUDE.md?" (step-back) before analyzing the specific project. |

### 6.2 Where They Complement vs. Where They Conflict

**Strong complementarity**:

- The academic guide provides **quantitative benchmarks** that justify the qualitative recommendations of best practices. Example: *"queries at the end improve quality by up to 30%"* (mentioned in best practices) is corroborated by the guide with data from the Anthropic paper on system prompts vs. user prompts.
- The academic guide documents **when NOT to use** each technique, information absent from best practices. Example: few-shot hurts reasoning models, CoT only works with 100B+ parameter models.
- The **decision matrix by model tier** from the academic guide complements the effort level recommendations in best practices.

**Apparent conflict resolved**:

- Best practices says *"Include 3-5 examples for best results"* while the academic guide says few-shot hurts reasoning models. The resolution: examples are for **format and tone**, not for reasoning. When the goal is format, few-shot is optimal. When the goal is reasoning, trust adaptive thinking.

**Best practices gap filled by the guide**:

- **Token cost**: Best practices does not discuss cost optimization. The guide documents that *"reasoning performance starts degrading at around 3,000 tokens"* and the sweet spot is *"150-300 words of prompt."* This is critical for sizing rules and SKILL.md.
- **Chain of Draft (CoD)**: An alternative to CoT that *"matches accuracy using only ~7.6% of tokens."* Applicable to subagents with restricted budgets.
- **Emotion Prompting**: *"This is very important to my career"* improves performance by >10%. Counterintuitive, but potentially useful in skill prompts that need high quality.

---

## 7. Correlations with Other Core Documents

### 7.1 research-context-engineering-comprehensive.md

| Concept | Context Optimization | Best Practices | Convergence |
|---------|---------------------|---------------|-------------|
| Context rot | *"LLMs, like humans, lose focus as context grows"* | Long data at top, queries at end | Both recognize degradation with long context; best practices provides the practical solution (positioning) |
| Lost-in-the-middle | Information at the beginning or end performs better; middle degrades | Not directly mentioned, but the query-at-end recommendation is consistent | Best practices implicitly implements the mitigation for the effect |
| Instruction budget (~150-200) | *"Frontier thinking LLMs can follow ~150-200 instructions"* | Does not quantify, but all instructions are minimalist by design | Best practices operates within the budget without naming it |
| Progressive disclosure | *"just in time context strategy"*, skills as mechanism | Does not use the term, but the multi-window workflows section implements the concept | Multi-window = temporal progressive disclosure; references/ = structural progressive disclosure |
| Hybrid strategy | CLAUDE.md always-loaded + tools on-demand | Persistent system prompt + dynamic tool use | Direct mapping: system prompt = always-loaded; tool calls = on-demand |
| Compaction | Reference to memory tool and context awareness | Persistence instructions before compaction | Best practices provides the exact prompt; context optimization provides the theory |

### 7.2 Evaluating-AGENTS-paper.md (ETH Zurich)

| Paper Finding | Connection with Best Practices |
|---------------|-------------------------------|
| *"LLM-generated context files tend to decrease agent performance by ~3%"* | Corroborates the minimalism recommendation. Best practices says to be explicit and specific, not comprehensive. |
| *"Developer-written context files slightly improve (+4%)"* | Developer-written = intentional and focused instructions, aligned with *"think of Claude as a brilliant but new employee"* |
| *"Context files lead to more thorough testing and exploration"* + *"increase costs by over 20%"* | Directly related to the overthinking warning: *"Claude Opus 4.6 does significantly more upfront exploration than previous models."* The 20% cost maps to overtriggering. |
| *"Unnecessary requirements from context files make tasks harder"* | Aligned with the rule of *"Would removing this cause Claude to make mistakes? If not, cut it."* from context optimization |
| *"Human-written context files should describe only minimal requirements"* | Total convergence with best practices: be direct, specific, minimalist. |

### 7.3 a-guide-to-agents.md and a-guide-to-agents.md

| Guide Principle | Equivalent in Best Practices |
|-----------------|------------------------------|
| *"One-sentence project description acts like a role-based prompt"* | *"Give Claude a role"* — system prompt with a single role sentence |
| *"Stale documentation poisons context... describe capabilities, not structure"* | *"Ground responses in quotes"* — ground in real data, not descriptions that may be outdated |
| *"Progressive disclosure: give the agent only what it needs right now"* | Multi-window workflows: first window setup, future windows iteration. Conditional references/ in SKILL.md. |
| *"No 'always', no all-caps forcing. Just a conversational reference."* | *"Claude is much better at appropriate refusals now. Clear prompting without prefill should be sufficient."* + overtriggering calibration |
| *"Instruction budget: ~150-200 instructions"* | All minimalism recommendations; effort parameter as substitute for over-prompting |
| *"Never auto-generate your AGENTS.md"* | Total convergence with the ETH Zurich paper and the intentionality principle |

---

## 8. Strengths and Limitations

### 8.1 Strengths

1. **Prescriptive and practical**: Each recommendation comes with a copyable example prompt. It is not theory — it is a cookbook.
2. **Updated for Claude 4.6**: Covers specific migrations (deprecated prefill, adaptive thinking, effort parameter), making it indispensable for production operations.
3. **Robust agentic section**: Multi-window workflows, state tracking, subagent orchestration, and anti-patterns (overeagerness, hard-coding, hallucinations) cover real agent development scenarios.
4. **Explicit behavior calibration**: Provides both the "accelerator" (`<default_to_action>`) and the "brake" (`<do_not_act_before_instructions>`), recognizing that different use cases need different proactivity levels.
5. **Convergence with independent research**: Recommendations align with findings from the ETH Zurich paper, context optimization research, and community guides, without citing those sources. This suggests robust principles, not isolated opinions.

### 8.2 Limitations

1. **Absence of cost metrics**: The document does not discuss token optimization, cost per request, or cost vs. quality trade-offs. The prompt engineering guide fills this gap with quantitative data.
2. **Does not mention negative techniques**: Does not explicitly document which classical techniques *not* to use with Claude 4.6 (e.g., explicit CoT with adaptive thinking, extensive few-shot for reasoning). The academic guide is necessary for this counterpoint.
3. **Focused on API, not config files**: Recommendations are for API prompts, not for CLAUDE.md/AGENTS.md. Translation to config files requires cross-referencing with other anchor documents.
4. **Examples centered on coding**: Most examples are software development. Non-code applications (research, writing, analysis) have less coverage.
5. **Migrations specific to Claude 4.5 → 4.6**: Significant portions of the document are migration guides that will have a limited lifespan when new models emerge.
6. **Does not cover meta-prompting**: A technique directly relevant to this project (generating CLAUDE.md is a form of meta-prompting) is not covered.

---

## 9. Practical Recommendations

### 9.1 For Writing Skills (SKILL.md)

1. **Open with motivational context**: Before the instructions, explain *why* the skill exists and what problem it solves. Claude generalizes better with motivation.
2. **Phases as explicit prompt chaining**: Each phase = one single objective. Explicit success criteria at the end of each phase. Inspect intermediate output between phases.
3. **Hard Rules as system prompt**: `<RULES>` block with critical constraints at the top. Use prohibitions (`NEVER`) only for high-cost violations. Complement with positive alternatives.
4. **References/ as on-demand few-shot**: Examples and reference guides in separate files, loaded conditionally. Do not pollute the main SKILL.md with extensive examples.
5. **Calibrate language for Claude 4.6**: Avoid ALL-CAPS and aggressive language. "Use X" instead of "You MUST ALWAYS use X." Exception: security/integrity constraints may use strong language.
6. **Self-check at the end**: Validation phase that reads `references/validation-criteria.md` and verifies each criterion. Aligned with: *"Before you finish, verify your answer against [test criteria]."*
7. **Size target**: SKILL.md body up to 500 lines (project convention), but the shorter the better. Each instruction must pass the test: "Would removing this cause Claude to make mistakes?"

### 9.2 For Hooks

1. **Ultra-short and specific prompts**: Hooks are the most constrained prompts in the system. One instruction, one output format, one trigger condition.
2. **Structured output without reasoning**: Hooks should not ask Claude to "think" — only verify and return structured results.
3. **Explicit trigger conditions**: Instead of "Always check X," use "Check X when files matching `path/pattern` are modified."
4. **Neutral language**: Zero aggressive language. Claude 4.6 will comply with specific conditions without emotional reinforcement.

### 9.3 For Subagents

1. **Self-contained prompt with role, task, and format**: Do not depend on inherited context. The subagent must be able to execute with its prompt alone.
2. **Zero-shot instructions, not few-shot**: The subagent token budget is limited. Use direct instructions with structured output, not examples.
3. **Narrow and explicit scope**: "Return ONLY [output format]. Do not [boundary]." Avoid open-ended tasks that lead to over-exploration.
4. **model: sonnet for analysis, not opus**: Project convention. Opus is too expensive for subagents. Sonnet with clear instructions handles most analyses.
5. **Limited maxTurns**: 15-20 turns to avoid infinite loops. Aligned with the principle of *"choose an approach and commit to it."*
6. **Read-only tools**: `Read, Grep, Glob, Bash` — analysis subagents should not modify the system. Aligned with *"consider the reversibility and potential impact of your actions."*

### 9.4 For Rules (`.claude/rules/`)

1. **One rule, one topic, one file**: Following the principle that each instruction should be specific and actionable.
2. **Precise paths in frontmatter**: `paths: ["src/api/**"]` instead of broad paths. The more precise the path, the less context wasted.
3. **Conversational tone**: *"Use 2-space indentation"* instead of *"YOU MUST ALWAYS USE 2-SPACE INDENTATION."* Claude 4.6 is more responsive and does not need aggressive language.
4. **Include motivation when non-obvious**: If a rule exists for a counterintuitive reason, explain the why. *"Claude is smart enough to generalize from the explanation."*
5. **Target: 5-20 lines per rule file**: Rules are micro-system-prompts. They should be scannable at a glance.

### 9.5 For Memory

1. **Separate structured state from progress notes**: JSON for machine data (tests, task status). Free text for human context (decisions, next steps).
2. **Predictable naming**: `tests.json`, `progress.txt`, `state.json` — names that Claude discovers via filesystem exploration.
3. **Persistence instruction before compaction**: In long-horizon skills, include: *"Save your current progress and state to memory before the context window refreshes."*
4. **Git as implicit memory**: Atomic commits with descriptive messages serve as a state log between sessions. Claude 4.6 *"performs especially well in using git to track state across multiple sessions."*
5. **Do not store absolute paths**: Paths change. Store descriptions of capabilities and states, not file locations.
