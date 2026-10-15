# Programmatic Tool Calling — Research Index

> **Index refreshed 2026-10-11** (previous capture ~2026-05-01). The Anthropic page was re-mirrored verbatim; the three third-party pieces are dated snapshots and each now opens with a `Currency check (2026-10-11)` block saying what no longer holds.

This directory contains research documents on Programmatic Tool Calling in AI agents, covering architecture patterns, implementations, and optimization techniques.

## Documents

| File | Source | Kind | Status on 2026-10-11 | Description |
|------|--------|------|----------------------|-------------|
| [programmatic-tool-calling-claude-api.md](./programmatic-tool-calling-claude-api.md) | Anthropic Docs (platform.claude.com) | Verbatim mirror | Current | Part 1: the dedicated **Programmatic tool calling** page (GA; `allowed_callers`, `caller`, container lifecycle, constraints, token efficiency). Part 2: the **Tool use with Claude** overview page (client vs server tools, how tool use works, pricing table). The earlier capture was a short summary of the overview only. |
| [tool-search-redefining-agent-tool-calling-epsilla.md](./tool-search-redefining-agent-tool-calling-epsilla.md) | Epsilla Insights (2026-04-19) | Dated snapshot | Partially outdated | Analysis of Tool Search as just-in-time tool discovery. Its Anthropic request example (`"type": "tool_search"`, `claude-sonnet-4`) does not match the documented API. |
| [cameronking4-programmatic-tool-calling-github.md](./cameronking4-programmatic-tool-calling-github.md) | GitHub (cameronking4) | Dated snapshot | Partially outdated | Proof of concept implementing PTC on Vercel AI SDK 5.0 + Next.js 16. Repository last pushed 2025-12-03; describes Anthropic's capability as "beta", which it no longer is. |
| [mcp-programmatic-tool-calling-opensandbox-dev.md](./mcp-programmatic-tool-calling-opensandbox-dev.md) | DEV Community (thangchung) | Dated snapshot | Partially outdated | .NET/C# implementation of MCP Code Mode using OpenSandbox and a local Python sandbox (`search`, `get_schema`, `execute`). Pattern still valid; the MCP protocol underneath changed in revision 2026-07-28. |

## Key Concepts

The statements in this section come from the Anthropic pages opened on 2026-10-11 (links at the end of each subsection). Figures quoted by the third-party articles (for example "80%+ token savings" or "98% reduction") are those authors' own and are **not** repeated here as facts.

### Programmatic Tool Calling (PTC)

Instead of one model round trip per tool call:

1. Claude writes **Python code** that calls your tools as async functions (several calls, loops, filtering).
2. The code runs in Anthropic's **code execution container**. When the code calls a tool, execution pauses and the API returns a `tool_use` block; you send back the result and the code continues.
3. Intermediate tool results **do not enter Claude's context**; only the final code output does.

How to enable it: include the code execution tool (version `code_execution_20260120` or later) and add `allowed_callers` to each tool that code may call. The response's `caller` field tells you whether a call came from the model directly or from code.

| Fact | Value |
|------|-------|
| Status | Generally available (page frontmatter `status: ga`) on the Claude API, Claude Platform on AWS, and Microsoft Foundry (Hosted on Anthropic deployments) |
| Zero data retention | Not eligible |
| Not supported on | Claude Haiku 4.5 (accepts the tool version but not programmatic calling) |
| Incompatible with | `strict: true` tools, forcing a specific tool through `tool_choice`, `disable_parallel_tool_use: true` |
| Cannot be called programmatically | MCP connector tools; the computer use and browser use toolsets |
| Measured savings (Anthropic's own evaluations) | ~38% fewer billed input tokens on a 75-tool benchmark; 20–40% typical on production requests with 10–49 tools; roughly 8% *more* cost on τ²-bench, where turns make only one or two sequential calls |

Source: <https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling>

### Tool Search

Instead of loading every tool definition up front:

1. You send every tool definition, but mark the rarely used ones `defer_loading: true`, and include a tool search tool.
2. Claude's context initially holds only the tool search tool and the non-deferred tools.
3. When Claude needs more, it searches; the API returns `tool_reference` blocks (up to 5 by default) and expands them into full definitions.

| Fact | Value |
|------|-------|
| Tool types | `tool_search_tool_regex_20251119` (Claude writes regex patterns) and `tool_search_tool_bm25_20251119` (natural-language queries) |
| Models | Claude Sonnet 4.5 / Opus 4.5 / Haiku 4.5 and later; Claude Opus 4.1 and earlier are not supported |
| Limits | 10,000 deferred tools per request; 200-character regex patterns; 500-character BM25 queries |
| When it pays off | 10+ tools, or definitions above ~10k tokens, or several MCP servers aggregated |
| Billing | Not metered as a separate server tool; loaded definitions count as ordinary input tokens |

Source (not mirrored in this directory): <https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool>

### The Context Bloat Problem

The tool search page gives the current reference figure: a typical multi-server setup (GitHub, Slack, Sentry, Grafana, Splunk) can consume **~55k tokens** of tool definitions before Claude does any work, tool search "typically reduces this by over 85 percent", and tool selection accuracy degrades once more than 30–50 tools are loaded. The per-server breakdown that this index previously listed (GitHub ~26K, Slack ~21K, Jira ~17K, Sentry ~3K) comes from the third-party articles and was not re-verified.

## Implementations Referenced

| Platform | Tool | Notes | Verified 2026-10-11? |
|----------|------|-------|----------------------|
| Anthropic Claude | `tool_search_tool_regex_20251119` / `tool_search_tool_bm25_20251119`; `code_execution_20260120`+ with `allowed_callers` | Server tools; see the two Anthropic pages above | Yes |
| OpenAI | `tool_search` | As described by the Epsilla article | No — no OpenAI source opened |
| Spring AI | `ToolSearchToolCallAdvisor` | As described by the Epsilla article | No — no Spring source opened |
| Vercel AI SDK | `withProgrammaticCalling()` | From the cameronking4 proof of concept (repository inactive since 2025-12-03) | Repository opened; code not run |
| .NET/C# MCP | `search` + `get_schema` + `execute` | OpenSandbox or local Python runner | Article opened; code not run |
