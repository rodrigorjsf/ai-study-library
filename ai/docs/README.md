# Documentation

A study library on working with AI coding agents: vendor documentation mirrors, saved articles and papers, our own research syntheses, and two studies written from them.

> **Last full audit: 2026-10-11.** Every document was checked against current sources. Start with [analysis/state-of-practice-2026-10.md](analysis/state-of-practice-2026-10.md) for what still holds and what does not.

## How to tell what you are reading

Each audited file says what it is in a block directly under its title:

| Block | Kind of file | What was done |
|---|---|---|
| `> Source: <url> — mirrored 2026-10-11` | **Vendor mirror** | The body is the current upstream page, verbatim. |
| `> **Revision 2026-10-11:**` | **Our synthesis** | Corrected inline as `~~old~~ → new [source]`. |
| `> **Currency check (2026-10-11):** <verdict>` | **Third-party snapshot** (article, paper, post) or an **analysis** of one | Body untouched. The verdict is `Current`, `Partially outdated`, `Superseded`, `Obsolete`, or `could not verify`, followed by what changed. |

A snapshot marked `Superseded` or `Obsolete` is kept for history. Read its block before relying on it.

## Start here

| If you want to… | Read |
|---|---|
| Know what advice is still good in October 2026 | [analysis/state-of-practice-2026-10.md](analysis/state-of-practice-2026-10.md) |
| Design an agent-driven delivery pipeline | [software-factory/05-unified-factory-study.md](software-factory/05-unified-factory-study.md) |
| Pick a Claude model and effort level for a role | [models/claude-5-5-model-selection.md](models/claude-5-5-model-selection.md) |
| Decide what an agent may do unattended, and how to enforce it | [software-factory/08-guardrails.md](software-factory/08-guardrails.md) |
| Choose a long-term memory tool for coding agents (ai-memory vs claude-mem, enterprise security, Cursor and Claude Code) | [agent-memory/README.md](agent-memory/README.md) (pt-BR) |

## Directory structure

| Directory | Kind | Contents |
|---|---|---|
| [`software-factory/`](software-factory/README.md) | Study | ZazenCodes' factory, Austin Marchese's harness engineering, Matt Pocock's skills v1.3, the local `/run-spec` flow, the unified study, the evidence on prototyping, a full assessment of wayfinder, a study of guardrails, and six video transcripts |
| [`agent-memory/`](agent-memory/README.md) | Study (pt-BR) | Agent memory concepts, architecture and security audit of ai-memory and claude-mem, Cursor/Claude Code integration, comparison, archify diagrams |
| [`models/`](models/claude-5-5-model-selection.md) | Study | Opus, Sonnet and Haiku 5.5: benchmarks per effort level, cost per task, role recommendations |
| `analysis/` | Analysis | The state-of-practice summary, plus one deep-extraction file per source document |
| `claude-code/` | Vendor mirror | Hooks, memory, plugins, skills, subagents, prompting |
| `claude/` | Vendor mirror | Anthropic's long-running-harness article; two superseded prompting duplicates |
| `cursor/` | Vendor mirror | Rules, hooks, MCP, plugins, skills, subagents, tools |
| `shared/` | Vendor mirror | Agent Skills open standard, skill authoring best practices |
| `structured-outputs/` | Vendor mirror | Structured outputs, strict tool use, defining tools, consistency |
| `tool-calling/` | Mirror + snapshots | Programmatic tool calling, tool search |
| `mcp/` | Mirror + snapshots | MCP specification (revision 2026-07-28), SDK and server READMEs, MCP vs A2A |
| `agent-protocols/` | Snapshots | A2A, agent communication protocols |
| `general-llm/` | Our syntheses | AGENTS.md guide, context engineering research, prompt engineering guide, the ETH AGENTS.md paper |
| `context-engineering/` | Snapshots | Context rot, progressive disclosure, 1M-token windows |
| `harness-engineering/` | Snapshots | Harness engineering articles |
| `agentic-engineering/` | Snapshots | Research-Plan-Implement, agent harness construction, the Claude cookbook |
| `spec-driven-development/` | Snapshots | Spec-driven development and its critique |
| `long-context-research/` | Snapshots | The lost-in-the-middle papers |
| `human-layer-project/` | Snapshot | HumanLayer repository analysis (obsolete: the repository was deprecated) |

## Claude Code (`claude-code/`)

| File | Description |
|---|---|
| `claude-prompting-best-practices.md` | Anthropic's consolidated prompting guide, with per-model guidance for the current models |
| `hooks/automate-workflow-with-hooks.md` | Guide to setting up hooks |
| `hooks/claude-hook-reference-doc.md` | Reference: 33 lifecycle events, five handler types, JSON schemas |
| `memory/how-claude-remembers-a-project.md` | `CLAUDE.md` load order, imports, `CLAUDE.local.md`, native `AGENTS.md`, auto memory |
| `plugins/claude-create-plugin-doc.md` | Creating plugins (mirrors the successor page `plugins/create`) |
| `skills/extend-claude-with-skills.md` | Creating skills: `SKILL.md`, frontmatter, invocation |
| `skills/research-claude-code-skills-format.md` | Our research comparing skill and plugin formats across tools (partially outdated) |
| `subagents/creating-custom-subagents.md` | Subagent definitions: frontmatter, tools, model, effort, nesting |
| `subagents/claude-orchestrate-of-claude-code-sessions.md` | Agent teams |

## Cursor (`cursor/`)

See [`cursor/README.md`](cursor/README.md). It also lists upstream areas not mirrored here (Run Modes, CLI, SDK, Cloud Agents and others).

## General LLM (`general-llm/`)

| File | Description |
|---|---|
| `a-guide-to-agents.md` | Guide to the AGENTS.md convention |
| `Evaluating-AGENTS-paper.md` / `.pdf` | ETH Zurich study of repository context files. The `.md` is the full text of v3 (2026-09-29) and the `.pdf` is the v3 PDF; summarized in the state-of-practice summary (section 5) |
| `research-context-engineering-comprehensive.md` | **Hub file**: executive summary, recommendations, citations; links to the scoped files below |
| `research-context-rot-and-management.md` | Context rot, attention budget, compression |
| `research-whitespace-and-formatting.md` | Whitespace and formatting effects |
| `research-multilingual-performance.md` | English versus other languages, including Portuguese |
| `research-agent-workflows-and-patterns.md` | Multi-agent orchestration, tool use, memory |
| `prompt-engineering-guide.md` | Prompt engineering techniques, annotated for what current models reject |
| `persuasion-principles.md` / `Call_Me_A_Jerk….pdf` | Persuasion principles applied to LLM compliance |
| `subagents/research-subagent-best-practices.md` | Cross-tool subagent design patterns |

## Shared standards (`shared/`)

| File | Description |
|---|---|
| `skill-authoring-best-practices.md` | Anthropic's skill authoring guide |
| `skills-standard/README.md` | Index of the agentskills.io mirror |
| `skills-standard/agentskills-*.md` | Specification, best practices, scripts, descriptions, evaluation |

## Reading order by task

**Building a delivery pipeline with agents:** `software-factory/README.md` → `05-unified-factory-study.md` → `models/claude-5-5-model-selection.md`

**Setting up Claude Code:** `claude-code/memory/` → `claude-code/skills/` → `claude-code/subagents/` → `claude-code/hooks/`

**Setting up Cursor:** `cursor/README.md` → `cursor/rules/` → `cursor/hooks/`

**Creating skills for any tool:** `shared/skill-authoring-best-practices.md` → `shared/skills-standard/` → `claude-code/skills/` or `cursor/skills/` → the "Writing for agents" section of `software-factory/03-matt-pocock-skills-v1-3.md`

**Understanding context engineering:** `analysis/state-of-practice-2026-10.md` → `general-llm/research-context-engineering-comprehensive.md` → the scoped research files

**Prompting current models:** `claude-code/claude-prompting-best-practices.md` → `models/claude-5-5-model-selection.md` (section 5, behaviour per model)

**Protocols:** `mcp/mcp-specification.md` → `agent-protocols/` (read each currency block first; several are behind A2A v1.0)

## Known limits of this library

- Four captures in `mcp/` did not match the sources they named and were deleted on 2026-10-11; the state-of-practice summary lists them and what to read instead.
- Benchmark numbers come from vendor system cards and third parties. None were measured here.
- The `harness-kb` package (`tools/harness-kb/`) ships a frozen copy of this folder, staged by `harness-kb build`, which aborts when any doc here is newer than the knowledge-graph manifest. After the October audit that copy is stale: the graph must be refreshed and the package rebuilt (see `tools/harness-kb/docs/build.md`). This was not done as part of the audit, and the documented route is currently blocked: `graphify-out/` was removed from the repository, so the manifest the build checks no longer exists.
- An untracked `docs/` tree at the repository root holds an older, partly diverging copy (a May 2026 sync, plus `cursor/cli`, `cursor/sdk` and `compliance` folders that do not exist here). It was not touched.
