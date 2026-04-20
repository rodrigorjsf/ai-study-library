# Documentation

## Directory Structure

| Directory      | Scope            | Contents                                                            | When to Load                          |
| -------------- | ---------------- | ------------------------------------------------------------------- | ------------------------------------- |
| `claude-code/` | Claude Code      | Hooks, memory, plugins, skills, subagents, prompting                | Working on Claude Code artifacts      |
| `cursor/`      | Cursor IDE       | Rules, hooks, MCP, plugins, skills, subagents, tools                | Working on Cursor artifacts           |
| `general-llm/` | Any LLM/agent    | AGENTS.md guide, research, prompt engineering, context optimization | Research, cross-tool decisions        |
| `shared/`      | Cross-tool       | Agent Skills open standard, skill authoring best practices          | Building portable skills              |
| `analysis/`    | Project-internal | Deep extraction analysis of each source document                    | Understanding source doc implications |

## Claude Code (`claude-code/`)

| File                                                      | Description                                                              |
| --------------------------------------------------------- | ------------------------------------------------------------------------ |
| `claude-prompting-best-practices.md`                      | Official Anthropic prompting best practices for Claude models            |
| `hooks/automate-workflow-with-hooks.md`                   | Setting up Claude Code hooks for workflow automation                     |
| `hooks/claude-hook-reference-doc.md`                      | Technical reference: 14 event types, JSON schemas, handlers              |
| `memory/how-claude-remembers-a-project.md`                | CLAUDE.md load order, `@import`, `claudeMdExcludes`, memory system       |
| `plugins/claude-create-plugin-doc.md`                     | Creating Claude Code plugins: manifest, skills, agents, hooks bundling   |
| `skills/extend-claude-with-skills.md`                     | Tutorial: creating skills with SKILL.md, invocation, `$CLAUDE_SKILL_DIR` |
| `skills/research-claude-code-skills-format.md`            | Research comparing skills/plugins format across tools (Claude-focused)   |
| `subagents/creating-custom-subagents.md`                  | Creating specialized subagents: YAML frontmatter, tool restrictions      |
| `subagents/claude-orchestrate-of-claude-code-sessions.md` | Orchestrating multiple Claude Code sessions via subagents                |

## Cursor IDE (`cursor/`)

See [`cursor/README.md`](cursor/README.md) for detailed navigation of Cursor-specific documentation.

Covers: rules (4 types), hooks (JSON stdio), MCP integration, plugins (marketplace), skills (Agent Skills standard), subagents, and tools (terminal, browser, search, worktrees).

## General LLM (`general-llm/`)

| File                                            | Description                                                                                                                                     |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `a-guide-to-agents.md`                          | Complete guide to AGENTS.md open standard — cross-agent compatibility, path-scoped rules                                                        |
| `Evaluating-AGENTS-paper.md`                    | ETH Zurich study (Feb 2026): minimal files outperform comprehensive ones                                                                        |
| `Evaluating-AGENTS-paper.pdf`                   | Original PDF of the ETH Zurich paper                                                                                                            |
| `research-context-engineering-comprehensive.md` | **Hub file** — Executive summary, recommendations, myths/reality, confidence assessment, and full 55-citation list. Links to scoped child files |
| `research-context-rot-and-management.md`        | Context rot mechanisms, attention budget, lost-in-middle, poisoning, compression, RAG quality (Parts 1–8)                                       |
| `research-whitespace-and-formatting.md`         | Whitespace tokenization, structural cues, formatting impact on output quality (Part 9)                                                          |
| `research-multilingual-performance.md`          | English vs other languages: token cost, reasoning routing, Portuguese/Romance language benchmarks (Parts 10–11)                                 |
| `research-agent-workflows-and-patterns.md`      | Multi-agent orchestration, tool use patterns, memory systems, progressive disclosure implementation (Section 13)                                |
| `prompt-engineering-guide.md`                   | 58+ prompt engineering techniques with benchmarks and token costs (2022–2026)                                                                   |
| `subagents/research-subagent-best-practices.md` | Cross-tool subagent design patterns and best practices                                                                                          |

**Related documentation**: [skill-authoring-best-practices](shared/skill-authoring-best-practices.md) | [skills-standard](shared/skills-standard/README.md)

## Shared Standards (`shared/`)

| File                                                     | Description                                                |
| -------------------------------------------------------- | ---------------------------------------------------------- |
| `skill-authoring-best-practices.md`                      | Best practices for skill creation applicable to any agent  |
| `skills-standard/README.md`                              | Agent Skills open standard overview (agentskills.io)       |
| `skills-standard/agentskills-what-are-skills.md`         | Core concepts: structure, portability, why standard exists |
| `skills-standard/agentskills-specification.md`           | Complete file format, frontmatter, layout specification    |
| `skills-standard/agentskills-best-practices.md`          | Naming, description, and authoring guidelines              |
| `skills-standard/agentskills-using-scripts.md`           | Bundling and executing scripts in skills                   |
| `skills-standard/agentskills-optimizing-descriptions.md` | Writing descriptions that trigger reliable invocation      |
| `skills-standard/agentskills-evaluating-skills.md`       | Measuring and improving skill output quality               |

## Analysis (`analysis/`)

16 deep extraction files — one per source document. Each contains actionable findings, quality ratings, and recommendations for this project. Metadata headers identify source document, analysis date, and scope.

## Reading Order by Task

**Setting up Claude Code**: `general-llm/a-guide-to-agents.md` → `claude-code/memory/` → `claude-code/hooks/`

**Setting up Cursor**: `cursor/README.md` → `cursor/rules/` → `cursor/hooks/`

**Creating skills (any tool)**: `shared/skill-authoring-best-practices.md` → `shared/skills-standard/` → tool-specific: `claude-code/skills/` or `cursor/skills/`

**Understanding context optimization**: `general-llm/research-context-engineering-comprehensive.md` (hub + summary) → specific scope files (`research-context-rot-and-management.md`, `research-whitespace-and-formatting.md`, `research-multilingual-performance.md`, `research-agent-workflows-and-patterns.md`) → `general-llm/Evaluating-AGENTS-paper.md`

**Prompt engineering deep dive**: `claude-code/claude-prompting-best-practices.md` (Claude-focused) or `general-llm/prompt-engineering-guide.md` (58+ techniques, tool-agnostic)
