# MCP Reference

`harness-kb --mcp` launches a stdio MCP server. The 16 tools below are namespaced `harness_kb_*` and exposed via `tools/list`. Each tool's input schema is JSON Schema with `additionalProperties: false`.

## Tools

### `harness_kb_themes`

List ai/docs themes with doc counts.

Input schema: no parameters.

Returns: `[{name: string, doc_count: integer}]`

Example exchange:

    tool: harness_kb_themes  {}
    → [{"name": "harness-engineering", "doc_count": 12}, {"name": "context-engineering", "doc_count": 8}, ...]

### `harness_kb_docs_list`

List bundled docs, optionally filtered by theme.

Input schema: `theme?: string`

Returns: `[{path: string, theme: string, title: string, size_tokens: integer}]`

Example exchange:

    tool: harness_kb_docs_list  {"theme": "mcp"}
    → [{"path": "mcp/primitives.md", "theme": "mcp", "title": "MCP Primitives", "size_tokens": 2800}, ...]

### `harness_kb_docs_get`

Return the full content of a bundled doc by relative path under ai_docs/.

Input schema: `path: string` (required)

Returns: `{path: string, content: string}`

Example exchange:

    tool: harness_kb_docs_get  {"path": "harness-engineering/rpi-pattern.md"}
    → {"path": "harness-engineering/rpi-pattern.md", "content": "# RPI Pattern\n..."}

### `harness_kb_docs_section`

Return one H2/H3 section of a bundled doc by heading.

Input schema: `path: string` (required), `heading: string` (required)

Returns: `{path: string, heading: string, content: string}`

Example exchange:

    tool: harness_kb_docs_section  {"path": "context-engineering/smart-zone.md", "heading": "Context Threshold"}
    → {"path": "context-engineering/smart-zone.md", "heading": "Context Threshold", "content": "## Context Threshold\n..."}

### `harness_kb_docs_search`

BM25 search over chunked ai/docs sections; returns ranked hits with snippets.

Input schema: `query: string` (required), `limit?: integer` (default 10), `theme?: string`

Returns: `[{path: string, heading: string, score: number, snippet: string}]`

Example exchange:

    tool: harness_kb_docs_search  {"query": "back-pressure", "limit": 3}
    → [{"path": "harness-engineering/patterns.md", "heading": "Back-pressure", "score": 4.2, "snippet": "..."}, ...]

### `harness_kb_wiki_list`

List names of bundled wiki pages.

Input schema: no parameters.

Returns: `[{name: string}]`

Example exchange:

    tool: harness_kb_wiki_list  {}
    → [{"name": "Context Engineering"}, {"name": "Harness Patterns"}, ...]

### `harness_kb_wiki_get`

Return the content of one wiki page by name (basename without .md).

Input schema: `name: string` (required)

Returns: `{name: string, content: string}`

Example exchange:

    tool: harness_kb_wiki_get  {"name": "Context Engineering"}
    → {"name": "Context Engineering", "content": "# Context Engineering\n..."}

### `harness_kb_graph_query`

Case-insensitive substring search over node labels in the bundled graph.

Input schema: `text: string` (required)

Returns: `[{label: string, id: string, community: string}]`

Example exchange:

    tool: harness_kb_graph_query  {"text": "smart zone"}
    → [{"label": "Dumb Zone / Smart Zone (Context Threshold)", "id": "n42", "community": "context-engineering"}]

### `harness_kb_graph_explain`

Return a node and its 1-hop neighbors.

Input schema: `label: string` (required)

Returns: `{node: {label, id, community}, neighbors: [{label: string, edge_type: string, weight: number}]}`

Example exchange:

    tool: harness_kb_graph_explain  {"label": "Agent Skills Standard"}
    → {"node": {"label": "Agent Skills Standard", "id": "n17", "community": "harness-engineering"}, "neighbors": [...]}

### `harness_kb_graph_path`

Return the shortest path between two nodes by label.

Input schema: `from: string` (required), `to: string` (required)

Returns: `{path: [string], length: integer}`

Example exchange:

    tool: harness_kb_graph_path  {"from": "Agent Skills Standard", "to": "Progressive Disclosure (Skills Context Management)"}
    → {"path": ["Agent Skills Standard", "Skill Loading Strategy", "Progressive Disclosure (Skills Context Management)"], "length": 2}

### `harness_kb_graph_find`

Regex search over node labels.

Input schema: `pattern: string` (required)

Returns: `[{label: string, id: string, community: string}]`

Example exchange:

    tool: harness_kb_graph_find  {"pattern": "Context.*Threshold"}
    → [{"label": "Dumb Zone / Smart Zone (Context Threshold)", "id": "n42", "community": "context-engineering"}]

### `harness_kb_graph_community`

Return all nodes in a community by community name.

Input schema: `name: string` (required)

Returns: `[{label: string, id: string}]`

Example exchange:

    tool: harness_kb_graph_community  {"name": "context-engineering"}
    → [{"label": "Smart Zone", "id": "n42"}, {"label": "Context Rot", "id": "n55"}, ...]

### `harness_kb_guide_toc`

Return the playbook's H2/H3 outline.

Input schema: no parameters.

Returns: `[{level: integer, heading: string, anchor: string}]`

Example exchange:

    tool: harness_kb_guide_toc  {}
    → [{"level": 2, "heading": "Harness Patterns", "anchor": "harness-patterns"}, ...]

### `harness_kb_guide_section`

Return one section of the playbook by heading.

Input schema: `heading: string` (required)

Returns: `{heading: string, content: string, token_estimate: integer}`

Example exchange:

    tool: harness_kb_guide_section  {"heading": "RPI Pattern"}
    → {"heading": "RPI Pattern", "content": "## RPI Pattern\n...", "token_estimate": 1200}

### `harness_kb_guide_get`

Return the full playbook content if confirm=true; otherwise a warning + TOC + token estimate.

Input schema: `confirm?: boolean` (default false)

Returns (confirm=false): `{warning: string, toc: [...], token_estimate: integer}`
Returns (confirm=true): `{content: string}`

Example exchange:

    tool: harness_kb_guide_get  {"confirm": false}
    → {"warning": "Full playbook is ~30K tokens. Use guide_toc or guide_section first.", "toc": [...], "token_estimate": 30000}

### `harness_kb_guide_search`

BM25 search restricted to the playbook.

Input schema: `query: string` (required), `limit?: integer` (default 10)

Returns: `[{path: string, heading: string, score: number, snippet: string}]`

Example exchange:

    tool: harness_kb_guide_search  {"query": "subagent dispatch", "limit": 5}
    → [{"path": "guide/harness-engineering-playbook.md", "heading": "Subagent Dispatch", "score": 3.8, "snippet": "..."}, ...]
