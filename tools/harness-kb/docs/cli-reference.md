# CLI Reference

`harness-kb --help` prints the same content authoritatively. This file is the human-readable index.

## Global flags

### `--version`

Print the package version and the bundled-data commit SHA + build date.

Example:

    $ harness-kb --version
    harness-kb 0.1.0 (data=ai-study-library@abc1234, built 2026-04-25)

### `--mcp`

Launch the stdio MCP server. See [MCP reference](mcp-reference.md).

## Subcommands

### `themes`

List all ai/docs themes with doc counts. No arguments.

Example:

    $ harness-kb themes
    [{"name": "harness-engineering", "doc_count": 12}, ...]

### `docs list`

List bundled docs, optionally filtered by theme.

Options: `--theme <name>` — filter to a single theme.

Example:

    $ harness-kb docs list --theme context-engineering
    [{"path": "context-engineering/smart-zone.md", "theme": "context-engineering", "title": "Smart Zone", "size_tokens": 3200}, ...]

### `docs get`

Return the full content of a bundled doc by its relative path under `ai_docs/`.

Args: `<path>` — relative path (e.g. `harness-engineering/rpi-pattern.md`).

Example:

    $ harness-kb docs get harness-engineering/rpi-pattern.md
    # RPI Pattern
    ...

### `docs section`

Return one H2 or H3 section of a doc by heading text.

Args: `<path>` `<heading>` — heading is case-insensitive substring match.

Example:

    $ harness-kb docs section context-engineering/smart-zone.md "Context Threshold"
    ## Context Threshold
    ...

### `docs search`

BM25 search over chunked ai/docs sections. Returns ranked hits with path, heading, score, and snippet.

Args: `<query>`. Options: `--limit N` (default 10), `--theme <name>`.

Example:

    $ harness-kb docs search "back-pressure" --limit 3
    [{"path": "...", "heading": "Back-pressure", "score": 4.2, "snippet": "..."}, ...]

### `wiki list`

List all bundled wiki page names (basenames without `.md`). No arguments.

Example:

    $ harness-kb wiki list
    ["Context Engineering", "Harness Patterns", ...]

### `wiki get`

Return the content of one wiki page by name.

Args: `<name>` — page name as returned by `wiki list`.

Example:

    $ harness-kb wiki get "Context Engineering"
    # Context Engineering
    ...

### `graph query`

Case-insensitive substring search over node labels in the bundled graph.

Args: `<text>` — search text.

Example:

    $ harness-kb graph query "smart zone"
    [{"label": "Dumb Zone / Smart Zone (Context Threshold)", "id": "n42", "community": "context-engineering"}, ...]

### `graph explain`

Return a node and its 1-hop neighbors (label, edge type, weight).

Args: `<label>` — exact or close node label.

Example:

    $ harness-kb graph explain "Agent Skills Standard"
    {"node": {"label": "Agent Skills Standard", ...}, "neighbors": [...]}

### `graph path`

Return the shortest path between two nodes by label.

Args: `<from_label>` `<to_label>`.

Example:

    $ harness-kb graph path "Agent Skills Standard" "Progressive Disclosure (Skills Context Management)"
    {"path": ["Agent Skills Standard", "...", "Progressive Disclosure (Skills Context Management)"], "length": 3}

### `graph find`

Regex search over node labels.

Args: `<pattern>` — Python regex pattern.

Example:

    $ harness-kb graph find "Context.*Threshold"
    [{"label": "Dumb Zone / Smart Zone (Context Threshold)", "id": "n42", "community": "context-engineering"}, ...]

### `graph community`

Return all nodes in a named community.

Args: `<name>` — community name as shown in graph metadata.

Example:

    $ harness-kb graph community "context-engineering"
    [{"label": "Smart Zone", "id": "n42"}, ...]

### `guide`

Without a subcommand: prints a warning and returns TOC + token estimate. `--confirm` prints the full playbook (~30K tokens).

Options: `--confirm` — bypass the warning gate and emit full content.

Example:

    $ harness-kb guide
    {"warning": "Full playbook is ~30K tokens. Use 'guide toc' or 'guide section' first.", "toc": [...], "token_estimate": 30000}

### `guide toc`

Return the playbook's H2/H3 outline as structured JSON (level, heading, anchor). No arguments.

Example:

    $ harness-kb guide toc
    [{"level": 2, "heading": "Harness Patterns", "anchor": "harness-patterns"}, ...]

### `guide section`

Return one section of the playbook by heading.

Args: `<heading>` — heading text (case-insensitive substring match).

Example:

    $ harness-kb guide section "RPI Pattern"
    {"heading": "RPI Pattern", "content": "...", "token_estimate": 1200}

### `guide search`

BM25 search restricted to the playbook. Returns ranked hits with heading, score, and snippet.

Args: `<query>`. Options: `--limit N` (default 10).

Example:

    $ harness-kb guide search "subagent dispatch" --limit 5
    [{"path": "guide/harness-engineering-playbook.md", "heading": "Subagent Dispatch", "score": 3.8, "snippet": "..."}, ...]

### `init`

Inject the `harness-kb` guidance block into a project's `CLAUDE.md`. Idempotent: re-running replaces the existing block.

Options: `--project <path>` (default cwd), `--dry-run` (print without writing).

Example:

    $ harness-kb init --project /path/to/project
    updated /path/to/project/CLAUDE.md

### `uninit`

Remove the injected `harness-kb` block from a project's `CLAUDE.md`. Leaves all other content untouched.

Options: `--project <path>` (default cwd).

Example:

    $ harness-kb uninit --project /path/to/project
    removed harness-kb block from /path/to/project/CLAUDE.md
