# Cursor IDE — Official Documentation

This directory contains official documentation and blog guidance mirrored from [cursor.com](https://cursor.com). The documents cover both Cursor IDE artifact definitions and official workflow guidance for effective agent usage.

AI agents should treat these documents as authoritative references when generating, reviewing, or validating Cursor artifacts (rules, skills, hooks, MCP servers, subagents, and plugins).

## Table of Contents

- [Cursor IDE — Official Documentation](#cursor-ide--official-documentation)
  - [Table of Contents](#table-of-contents)
  - [Directory Overview](#directory-overview)
    - [tools/ sub-directories](#tools-sub-directories)
  - [hooks/](#hooks)
  - [mcp/](#mcp)
  - [plugin/](#plugin)
  - [rules/](#rules)
  - [skills/](#skills)
  - [subagents/](#subagents)
  - [tools/](#tools)

## Directory Overview

| Directory | Document(s) | What it covers |
|-----------|-------------|----------------|
| [`hooks/`](./hooks/hooks-guide.md) | `hooks-guide.md` | Lifecycle hooks that observe, block, or modify the agent loop via JSON stdio scripts |
| [`mcp/`](./mcp/mcp-guide.md) | `mcp-guide.md` | Model Context Protocol — connecting Cursor to external tools and data sources |
| [`plugin/`](./plugin/plugins.md) | `plugins.md` | Plugins that bundle rules, skills, agents, commands, MCP servers, and hooks into distributable packages |
| [`rules/`](./rules/rules.md) | `rules.md` | System-level instructions (Always, Auto-attached, Agent-requested, Manual) that guide agent behavior |
| [`skills/`](./skills/agent-skills-guide.md) | `agent-skills-guide.md` | Agent Skills standard — portable, version-controlled capability packages for agents |
| [`subagents/`](./subagents/subagents-guide.md) | `subagents-guide.md` | Subagents — specialized assistants the agent can delegate tasks to in isolated context windows |
| [`best-practices/`](./best-practices/agent-best-practices.md) | `agent-best-practices.md` | Official Cursor blog guide on agent workflows, planning, context management, and best practices |
| [`tools/`](#tools) | ↓ 4 guides | Built-in agent tools: terminal, browser, search, and worktrees |

### tools/ sub-directories

| Directory | Document | What it covers |
|-----------|----------|----------------|
| [`tools/terminal/`](./tools/terminal/terminal-guide.md) | `terminal-guide.md` | Terminal sandbox, allowlists, environment variables, auto-run modes, enterprise controls |
| [`tools/browser/`](./tools/browser/browser-guide.md) | `browser-guide.md` | Browser automation, design sidebar, session persistence, security, enterprise origin allowlists |
| [`tools/search/`](./tools/search/search-guide.md) | `search-guide.md` | Instant grep, semantic search, indexing, the Explore subagent, privacy |
| [`tools/worktrees/`](./tools/worktrees/worktrees-guide.md) | `worktrees-guide.md` | Parallel agents via Git worktrees, Best-of-N models, setup scripts, cleanup |

## best-practices/

**Source:** [cursor.com/blog/agent-best-practices](https://cursor.com/blog/agent-best-practices)

Official Cursor guide covering techniques for working effectively with Cursor's agent — harness architecture, plan mode, context management, rules vs skills, TDD workflows, parallel agents, cloud agents, and debug mode.

→ [`best-practices/agent-best-practices.md`](./best-practices/agent-best-practices.md)

## hooks/

**Source:** [cursor.com/docs/hooks](https://cursor.com/docs/hooks)

Hooks are spawned processes that communicate over stdio using JSON. They run at defined stages of the agent loop (`before_tool_call`, `after_tool_call`, etc.) and can observe, block, or mutate agent behavior. The guide covers hook registration, JSON schemas for input/output, partner integrations, and security considerations.

→ [`hooks/hooks-guide.md`](./hooks/hooks-guide.md)

## mcp/

**Source:** [cursor.com/docs/mcp](https://cursor.com/docs/mcp)

Model Context Protocol (MCP) enables Cursor to connect to external tools and data sources. Covers transport methods (STDIO, SSE, Streamable HTTP), server configuration, OAuth, tool approval flows, and the Cursor MCP client capabilities.

→ [`mcp/mcp-guide.md`](./mcp/mcp-guide.md)

## plugin/

**Source:** [cursor.com/docs/plugins](https://cursor.com/docs/plugins)

Plugins bundle rules, skills, agents, commands, MCP servers, and hooks into shareable packages. Covers the plugin manifest format, directory structure, how Cursor discovers and loads plugins, and how to publish to the Cursor Marketplace.

→ [`plugin/plugins.md`](./plugin/plugins.md)

## rules/

**Source:** [cursor.com/docs/rules](https://cursor.com/docs/rules)

Rules provide system-level instructions to Agent. Covers the four rule types (Always, Auto-attached, Agent-requested, Manual), `.cursor/rules/` directory structure, frontmatter fields, and best practices for writing effective rules.

→ [`rules/rules.md`](./rules/rules.md)

## skills/

**Source:** [cursor.com/docs/skills](https://cursor.com/docs/skills)

Agent Skills is an open standard for extending AI agents with specialized, portable capabilities. Covers the `SKILL.md` entry point, frontmatter fields, skill directories, how Cursor discovers and invokes skills, and the relationship to the [Agent Skills standard](../shared/skills-standard/README.md).

→ [`skills/agent-skills-guide.md`](./skills/agent-skills-guide.md)

## subagents/

**Source:** [cursor.com/docs/subagents](https://cursor.com/docs/subagents)

Subagents let the main agent delegate tasks to specialized assistants, each operating in its own context window. Covers subagent modes (fire-and-forget, synchronous), built-in subagents, `.cursor/agents/` configuration format, model selection, and subagents vs. skills trade-offs.

→ [`subagents/subagents-guide.md`](./subagents/subagents-guide.md)

## tools/

**Source:** [cursor.com/docs/agent/tools](https://cursor.com/docs/agent/tools)

Built-in tools available to the Cursor agent. Each subdirectory covers one tool:

| Tool | Source | What it covers |
|------|--------|----------------|
| [`terminal/`](./tools/terminal/terminal-guide.md) | [/docs/agent/tools/terminal](https://cursor.com/docs/agent/tools/terminal) | Sandbox execution, allowlists, env vars, auto-run modes, enterprise controls |
| [`browser/`](./tools/browser/browser-guide.md) | [/docs/agent/tools/browser](https://cursor.com/docs/agent/tools/browser) | Browser automation, design sidebar, session persistence, security |
| [`search/`](./tools/search/search-guide.md) | [/docs/agent/tools/search](https://cursor.com/docs/agent/tools/search) | Instant grep, semantic search, indexing, Explore subagent |
| [`worktrees/`](./tools/worktrees/worktrees-guide.md) | [/docs/configuration/worktrees](https://cursor.com/docs/configuration/worktrees) | Parallel agents, Best-of-N, setup scripts, cleanup |
