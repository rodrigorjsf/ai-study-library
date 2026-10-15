# Cursor IDE — Official Documentation

This directory contains official documentation and blog guidance mirrored from [cursor.com](https://cursor.com). The documents cover both Cursor IDE artifact definitions and official workflow guidance for effective agent usage.

AI agents should treat these documents as authoritative references when generating, reviewing, or validating Cursor artifacts (rules, skills, hooks, MCP servers, subagents, and plugins).

> **Mirror status (2026-10-11):** The eleven `cursor.com/docs/*` pages below were re-mirrored verbatim on 2026-10-11 from the raw-markdown endpoints Cursor now serves (append `.md` to any docs URL; index at <https://cursor.com/llms.txt>). Only the trailing site-navigation "Sitemap" footer was removed. Each file carries a `> Source:` line under its H1. `best-practices/` is a project summary of a blog post and carries a currency check instead.

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
  - [Upstream areas not mirrored here](#upstream-areas-not-mirrored-here)

## Directory Overview

| Directory | Document(s) | What it covers |
|-----------|-------------|----------------|
| [`hooks/`](./hooks/hooks-guide.md) | `hooks-guide.md` | Lifecycle hooks that observe, block, or modify the agent loop via JSON stdio scripts |
| [`mcp/`](./mcp/mcp-guide.md) | `mcp-guide.md` | Model Context Protocol — connecting Cursor to external tools and data sources |
| [`plugin/`](./plugin/plugins.md) | `plugins.md`, `plugin-full-reference.md` | Plugins that bundle rules, skills, agents, commands, MCP servers, and hooks into distributable packages; Agent Plugins open standard vs Cursor Plugins; team marketplaces |
| [`rules/`](./rules/rules.md) | `rules.md` | System-level instructions (Project Rules, User Rules, Team Rules, AGENTS.md) that guide agent behavior |
| [`skills/`](./skills/agent-skills-guide.md) | `agent-skills-guide.md` | Agent Skills standard — portable, version-controlled capability packages for agents |
| [`subagents/`](./subagents/subagents-guide.md) | `subagents-guide.md` | Subagents — specialized assistants the agent can delegate tasks to in isolated context windows |
| [`best-practices/`](./best-practices/agent-best-practices.md) | `agent-best-practices.md` | Official Cursor blog guide on agent workflows, planning, context management, and best practices |
| [`tools/`](#tools) | ↓ 4 guides | Built-in agent tools: terminal, browser, search, and worktrees |

### tools/ sub-directories

| Directory | Document | What it covers |
|-----------|----------|----------------|
| [`tools/terminal/`](./tools/terminal/terminal-guide.md) | `terminal-guide.md` | Stub page: pointer to Run Modes for sandbox and approvals, plus shell-theme troubleshooting (`CURSOR_AGENT`) |
| [`tools/browser/`](./tools/browser/browser-guide.md) | `browser-guide.md` | Browser automation, session persistence, security, enterprise origin allowlists |
| [`tools/search/`](./tools/search/search-guide.md) | `search-guide.md` | Instant Grep, privacy, the Explore subagent, multi-root workspaces |
| [`tools/worktrees/`](./tools/worktrees/worktrees-guide.md) | `worktrees-guide.md` | Worktrees in the Agents Window, setup scripts, discovery and cleanup, `/worktree` and `/best-of-n` skills in the IDE |

## best-practices/

**Source:** [cursor.com/blog/agent-best-practices](https://cursor.com/blog/agent-best-practices)

Official Cursor guide covering techniques for working effectively with Cursor's agent — harness architecture, plan mode, context management, rules vs skills, TDD workflows, parallel agents, cloud agents, and debug mode.

→ [`best-practices/agent-best-practices.md`](./best-practices/agent-best-practices.md)

## hooks/

**Source:** [cursor.com/docs/hooks](https://cursor.com/docs/hooks)

Hooks are spawned processes that communicate over stdio using JSON. They fall into three categories — Agent hooks (`preToolUse`, `postToolUse`, `beforeShellExecution`, `stop`, etc.), Tab hooks (`beforeTabFileRead`, `afterTabFileEdit`), and App lifecycle hooks (`workspaceOpen`) — and can observe, block, or modify behavior. The guide covers `hooks.json` configuration, command- and prompt-based hooks, cloud agent support, JSON schemas for input/output, partner integrations, and team distribution.

→ [`hooks/hooks-guide.md`](./hooks/hooks-guide.md)

## mcp/

**Source:** [cursor.com/docs/mcp](https://cursor.com/docs/mcp)

Model Context Protocol (MCP) enables Cursor to connect to external tools and data sources. Covers transport methods (STDIO, SSE, Streamable HTTP), `mcp.json` configuration, OAuth, MCP Apps, enterprise admin controls, tool approval via Run Modes, and the Cursor MCP client capabilities.

→ [`mcp/mcp-guide.md`](./mcp/mcp-guide.md)

## plugin/

**Source:** [cursor.com/docs/plugins](https://cursor.com/docs/plugins), [cursor.com/docs/reference/plugins](https://cursor.com/docs/reference/plugins)

Plugins bundle rules, skills, agents, commands, MCP servers, and hooks into shareable packages. Cursor loads two formats: Agent Plugins (open standard, `plugin.json` at the plugin root) and Cursor Plugins (`.cursor-plugin/plugin.json`). Covers team marketplaces, installing and managing plugins from Customize, the manifest format, variables, component discovery, multi-plugin repositories, and submitting to the Cursor Marketplace.

→ [`plugin/plugins.md`](./plugin/plugins.md)
→ [`plugin/plugin-full-reference.md`](./plugin/plugin-full-reference.md)

## rules/

**Source:** [cursor.com/docs/rules](https://cursor.com/docs/rules)

Rules provide system-level instructions to Agent. Covers the four kinds of rules (Project Rules, User Rules, Team Rules, AGENTS.md), the four project-rule application types (Always Apply, Apply Intelligently, Apply to Specific Files, Apply Manually), the `.cursor/rules/` directory of `.mdc` files, frontmatter fields, glob patterns, and best practices for writing effective rules.

→ [`rules/rules.md`](./rules/rules.md)

## skills/

**Source:** [cursor.com/docs/skills](https://cursor.com/docs/skills)

Agent Skills is an open standard for extending AI agents with specialized, portable capabilities. Covers the `SKILL.md` entry point, frontmatter fields (including `paths`), built-in Cursor skills, skill directories, how Cursor discovers and invokes skills, syncing personal skills to Cloud Agents, and the relationship to the [Agent Skills standard](../shared/skills-standard/README.md).

→ [`skills/agent-skills-guide.md`](./skills/agent-skills-guide.md)

## subagents/

**Source:** [cursor.com/docs/subagents](https://cursor.com/docs/subagents)

Subagents let the main agent delegate tasks to specialized assistants, each operating in its own context window. Covers foreground vs background modes, built-in subagents, `.cursor/agents/` configuration format, model configuration and usage pools, isolated project copies, cloud subagents (`/in-cloud`, `/autopilot`), and subagents vs. skills trade-offs.

→ [`subagents/subagents-guide.md`](./subagents/subagents-guide.md)

## tools/

**Source:** `cursor.com/docs/agent/tools/*` — there is no upstream index page at that path (it returned 404 on 2026-10-11); per-tool sources are in the table below.

Built-in tools available to the Cursor agent. Each subdirectory covers one tool:

| Tool | Source | What it covers |
|------|--------|----------------|
| [`terminal/`](./tools/terminal/terminal-guide.md) | [/docs/agent/tools/terminal](https://cursor.com/docs/agent/tools/terminal) | Pointer to Run Modes; shell-theme troubleshooting |
| [`browser/`](./tools/browser/browser-guide.md) | [/docs/agent/tools/browser](https://cursor.com/docs/agent/tools/browser) | Browser automation, session persistence, security, enterprise origin allowlist |
| [`search/`](./tools/search/search-guide.md) | [/docs/agent/tools/search](https://cursor.com/docs/agent/tools/search) | Instant Grep, privacy, Explore subagent |
| [`worktrees/`](./tools/worktrees/worktrees-guide.md) | [/docs/configuration/worktrees](https://cursor.com/docs/configuration/worktrees) | Agents Window worktrees, setup scripts, cleanup, `/worktree`, `/best-of-n` |

## Upstream areas not mirrored here

As of 2026-10-11 the upstream index (<https://cursor.com/llms.txt>) lists these areas that have no local copy in this directory. The index lists each page as a `.md` URL; raw markdown was confirmed for the pages mirrored here (blog posts under `/blog/*` do not serve it).

| Upstream area | Entry point | Why it matters to the mirrored docs |
|---------------|-------------|-------------------------------------|
| Run Modes and agent security | <https://cursor.com/docs/agent/security/run-modes> | Now holds the sandbox, allowlist, Auto-review, AppArmor, and network content that used to be on the Terminal page |
| Customize page | <https://cursor.com/docs/customize-cursor> | The UI where plugins, MCP servers, rules, skills, subagents, and hooks are installed and managed |
| Agents Window, Projects, Agent Review, Plan/Debug/Design modes | <https://cursor.com/docs/agent/agents-window> | The worktrees page now leads with the Agents Window workflow |
| Canvas tool | <https://cursor.com/docs/agent/tools/canvas> | New entry under agent tools, next to terminal, browser, and search |
| CLI | <https://cursor.com/docs/cli/overview> | Headless mode, ACP, slash commands, permissions, configuration |
| SDK (TypeScript, Python, bridge) | <https://cursor.com/docs/sdk/typescript> | Programmatic agents |
| Cloud Agents (setup, automations, self-hosted, API) | <https://cursor.com/docs/cloud-agent> | Hooks, skills, and subagents each have cloud-agent sections |
| Bugbot, Security agents, Approval agents | <https://cursor.com/docs/bugbot> | Review agents referenced by the built-in skills |
| Origin (Git hosting, CLI, API) | <https://cursor.com/docs/origin> | Product area with no local copy |
| Grok Bot | <https://cursor.com/docs/grok-bot> | Product area with no local copy |
| Integrations, Account/Enterprise, Admin and Analytics APIs | <https://cursor.com/docs/api> | Team and enterprise controls referenced from rules, MCP, and plugins |
