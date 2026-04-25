# Changelog

## v0.1.0 (unreleased)

### Added
- `manifest.py`: `Manifest` dataclass + load/save helpers + `get_data_dir()`.
- `chunking.py`: H2/H3-aware markdown chunking with paragraph subsplit and 50-token overlap.
- `search.py`: BM25 search backend with build/save/load and snippet generation.
- `docs.py`: ai/docs retrieval (list themes, list docs, get, get_section, search).
- `graph.py`: graph queries (keyword, explain, shortest_path, find_nodes, community_nodes).
- `wiki.py`: wiki list + get.
- `guide.py`: playbook retrieval (toc, section, get with confirm gate, search).
- `init.py`: idempotent CLAUDE.md injection (and uninject) with version markers.
- `cli.py`: Click CLI exposing all retrieval surfaces + init/uninit + --mcp + --version.
- `mcp.py`: stdio MCP server registering all 16 tools.
- `build/adapt_guide.py`: deterministic /graphify → harness-kb adaptation rules.
- `build/build.py`: full build pipeline (validate, stage, adapt, index, manifest, post-validate).
- Documentation: README, architecture, cli-reference, mcp-reference, claude-md-injection, build.
