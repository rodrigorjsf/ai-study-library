# harness-kb

Portable, version-pinned knowledge base of agent / harness / context-engineering reference material drawn from the `ai-study-library` corpus. Ships as a Python package with both a CLI and a stdio MCP server.

## What it is

Provide a portable, version-pinned Python package — `harness-kb` — that gives any project's LLM agents typed access to the harness-engineering knowledge stack: the `ai/docs/` corpus, the `graphify-out/` knowledge graph, the auto-generated wiki, and a comprehensive playbook adapted from the research doc shipped in sub-project A.

Consumer projects install one package (`pipx install harness-kb`) and run one command (`harness-kb init`) to wire the tool into their CLAUDE.md so agents always reach for it when working on agent / harness / context-engineering topics. No external skill, no external repo, no network calls at runtime.

The package bundles four assets: the `ai/docs/` corpus (~272K words across 16 themes), the `graphify-out/` knowledge graph (graph.json + community wiki pages), and the harness-engineering playbook adapted from the research doc (~1500 lines, ~30K tokens).

## Install

```bash
pipx install harness-kb
```

## Quickstart

Discovery:

    harness-kb --version
    harness-kb themes
    harness-kb docs list --theme harness-engineering

Search:

    harness-kb docs search "smart zone"
    harness-kb graph explain "Subagent as Context Firewall"
    harness-kb guide toc

Wire into a project's `CLAUDE.md` so agents always reach for the tool:

    cd /path/to/your/project
    harness-kb init

Run as an MCP server (preferred for agents):

    harness-kb --mcp

## What's bundled

The package ships four frozen assets inside the wheel: the `ai/docs/` corpus (~272K words, approximately 2-3 MB across 16 themes), the knowledge graph (`graph.json`, ~500 KB-1 MB) plus auto-generated wiki pages (~200-500 KB), and the harness-engineering playbook (~110 KB, adapted from the research doc). The BM25 index adds ~1-2 MB pickled. Total wheel size ~5-8 MB. Refresh = upgrade the package version; the `harness-kb --version` output names the source-repo commit SHA the bundle was built from.

## Documentation

- [Architecture](docs/architecture.md) — components, data flow, boundaries
- [CLI reference](docs/cli-reference.md) — every subcommand with examples
- [MCP reference](docs/mcp-reference.md) — every tool with schemas
- [CLAUDE.md injection](docs/claude-md-injection.md) — exactly what `harness-kb init` writes
- [Build](docs/build.md) — maintainer-facing build pipeline

## License

MIT. See [LICENSE](LICENSE).
