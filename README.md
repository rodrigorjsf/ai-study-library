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

- **Java Concurrency & `static`:** decision rule for `static` in high-RPM services on Java 25 — shared state, virtual threads, DynamoDB/Redis clients, and OpenTelemetry. Available for Claude Code and for Cursor as an `.mdc` project rule — both scoped by globs to Java sources and build files.

### 4. `ai/examples/`

Executable reference implementations for the rules above — a rule the build does not enforce is only a suggestion.

- **`java/static-concurrency-enforcement/`:** ArchUnit test suites (v1 and v2, the latter frozen against a baseline) plus an Error Prone `BugChecker` that covers the `synchronized` blocks ArchUnit cannot see in bytecode.

### 5. `ai/study/`

Structured study plans and educational resources.

- **Basics Study Plan:** A comprehensive guide covering Computer Science foundations (Algorithms, Data Structures), Backend Engineering, and System Design. It incorporates neuroscientific learning principles like Active Recall and Spaced Repetition, utilizing tools like NotebookLM as a cognitive partner.
- **Tools:** Generators for Product Requirement Documents (PRDs) and Technical Review guidelines.

## 🚀 Key Concepts

- **Active Learning:** The study plans encourage active engagement (teaching back, solving problems) rather than passive consumption.
- **Prompt Engineering:** The repository treats prompts as code, with versioning and optimization strategies for different model architectures.
- **Cognitive Amplification:** Using AI tools not just to generate code, but to deepen understanding of complex concepts.

## 🛠 Usage

1. **Study:** Follow the `basics-study-plan.md` for a rigorous CS and Engineering curriculum.
2. **Optimize:** Use the prompts in `ai/prompts/improvement/` to refine your instructions to AI agents.
3. **Reference:** Consult `ai/docs/` for model-specific interaction patterns and best practices.
