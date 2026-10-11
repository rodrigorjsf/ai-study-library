# AI Study Library

This repository serves as a personal knowledge base and study companion for mastering AI engineering, model interactions, and core software development foundations. It integrates evidence-based learning strategies with practical resources for maximizing the utility of Large Language Models (LLMs).

## 📂 Project Structure

The library is organized into the following main sections:

### 1. `ai/docs/`

Documentation and best practices for interacting with specific AI models.

- **Claude:** Guides on interaction, effective harnessing of long-running agents, and prompting best practices.

### 2. `ai/prompts/`

A collection of optimized prompts and meta-prompts designed to improve the performance of various models.

- **Improvement:** Meta-prompts specifically crafted to refine and optimize inputs for Claude, Codex, Gemini, and Grok.

### 3. `ai/rules/`

Rules written to steer coding agents, organized by the tool that loads them — the guidance is shared, only the activation metadata differs.

- **Java Concurrency & `static`:** decision rule for `static` in high-RPM services on Java 25 — shared state, virtual threads, DynamoDB/Redis clients, and OpenTelemetry. Available for Claude Code and for Cursor as an `.mdc` project rule — both scoped by globs to Java sources and build files. See [`ai/rules/README.md`](ai/rules/README.md) for install paths, the Cursor rule-type/frontmatter mapping, and sourced notes on the `.mdc` frontmatter gotchas.

### 4. `ai/examples/`

Executable reference implementations for the rules above — a rule the build does not enforce is only a suggestion.

- **`java/static-concurrency-enforcement/`:** ArchUnit test suites (v1 and v2, the latter frozen against a baseline) plus an Error Prone `BugChecker` that covers the `synchronized` blocks ArchUnit cannot see in bytecode.

### 5. `ai/agents/`

Claude Code subagents.

- **`product-pipeline/`:** 35 research-backed personas that take an idea through Discovery → PRD → Architecture → Tasks. Each stage has its own orchestrator, run in a fresh session (`claude --agent <stage>-orchestrator`), plus specialists, a stage critic and a shared cross-cutting pool (security, privacy/LGPD, accessibility, SRE, FinOps, analytics, traceability). Each persona states acceptance criteria and refusal criteria (`blocked` / `rejected` / `out_of_scope`). The folder also ships a preloaded conventions skill, default gate rubrics and install/run/lint scripts. See [`ai/agents/product-pipeline/README.md`](ai/agents/product-pipeline/README.md); the research behind it is in [`dev/research/2026-10-02-agentic-pipeline-personas-research.md`](dev/research/2026-10-02-agentic-pipeline-personas-research.md).

### 6. `ai/study/`

Structured study plans and educational resources.

- **Basics Study Plan:** A comprehensive guide covering Computer Science foundations (Algorithms, Data Structures), Backend Engineering, and System Design. It incorporates neuroscientific learning principles like Active Recall and Spaced Repetition, utilizing tools like NotebookLM as a cognitive partner.
- **Tools:** Generators for Product Requirement Documents (PRDs) and Technical Review guidelines.

### 7. `ai/skills/`

Agent skills, each a self-contained `SKILL.md` folder. See [`ai/skills/README.md`](ai/skills/README.md) for the index, install steps, and flow diagrams.

- **`coding-standards`:** generates or updates `CODING_STANDARDS.md` at a repo root from the conventions the codebase actually follows, with one heading per domain. Harness-agnostic: it reads the rule files of Claude Code, Codex, Cursor, Copilot, Gemini CLI, and Windsurf, exports the standards declared in project rule files, and points at user-level rules.
- **`test-suite-review`:** reviews a codebase's unit tests, removes the ones that add volume without protecting the domain, reinforces where the domain is exposed, and ends green with at least 80% genuine coverage. It works in a git worktree, respects Sonar exclusions, and merges back with a ledger of every change.
- **`dream`**, **`pdf`**, **`study-plan-generator`:** memory consolidation, PDF to Markdown extraction, and study-plan generation.

## 🚀 Key Concepts

- **Active Learning:** The study plans encourage active engagement (teaching back, solving problems) rather than passive consumption.
- **Prompt Engineering:** The repository treats prompts as code, with versioning and optimization strategies for different model architectures.
- **Cognitive Amplification:** Using AI tools not just to generate code, but to deepen understanding of complex concepts.

## 🛠 Usage

1. **Study:** Follow the `basics-study-plan.md` for a rigorous CS and Engineering curriculum.
2. **Optimize:** Use the prompts in `ai/prompts/improvement/` to refine your instructions to AI agents.
3. **Reference:** Consult `ai/docs/` for model-specific interaction patterns and best practices.
