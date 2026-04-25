# Architecture

## Goal

Provide a portable, version-pinned Python package — `harness-kb` — that gives any project's LLM agents typed access to the harness-engineering knowledge stack: the `ai/docs/` corpus, the `graphify-out/` knowledge graph, the auto-generated wiki, and a comprehensive playbook adapted from the research doc shipped in sub-project A.

Consumer projects install one package (`pipx install harness-kb`) and run one command (`harness-kb init`) to wire the tool into their CLAUDE.md so agents always reach for it when working on agent / harness / context-engineering topics. No external skill, no external repo, no network calls at runtime.

This spec is the second half of the harness-engineering knowledge-stack effort. Sub-project A (shipped) made the research doc portable; sub-project B (this spec) wraps that doc and the rest of the knowledge stack into a distributable tool.

## Components

| Component | Responsibility | Key Tech |
|---|---|---|
| `harness_kb.cli` | argparse/click CLI dispatcher; subcommands map 1:1 to MCP tools where possible | click |
| `harness_kb.mcp` | stdio MCP server; exposes typed tools | mcp Python SDK |
| `harness_kb.docs` | ai/docs retrieval: list, get, get_section, BM25 search | rank_bm25 + std lib |
| `harness_kb.graph` | graph.json query: path, explain, find_nodes, community, keyword_query | networkx |
| `harness_kb.wiki` | wiki retrieval: list, get | std lib |
| `harness_kb.guide` | playbook retrieval: toc, section, get (with confirm gate), search | std lib + rank_bm25 |
| `harness_kb.init` | CLAUDE.md injection / removal in consumer projects | std lib |
| `harness_kb.search` | shared BM25 backend used by docs.search and guide.search | rank_bm25 |
| `harness_kb.chunking` | shared chunking strategy for the BM25 corpus | std lib |
| `harness_kb.manifest` | manifest.json loader, version helper | std lib |
| `harness_kb.data/` | bundled snapshot: ai_docs/ + graph.json + wiki/ + guide/playbook + bm25_index + manifest | data files |
| `harness_kb.build` | maintainer-only: build pipeline (excluded from runtime imports) | std lib |

## Boundaries

- CLI and MCP are thin surfaces over four retrieval modules (docs, graph, wiki, guide) plus init.
- Build is maintainer-only; not exposed in installed package's user-facing surface.
- Data is read-only at runtime; refresh = upgrade package version.
- No network calls at runtime. Tool only reads its bundled data and only writes to the consumer project's CLAUDE.md (and only with explicit `init` invocation).
- **No persistent config file.** All runtime behavior is controlled by CLI flags (or MCP tool arguments). The tool deliberately has no `~/.harness-kb/config.toml` or equivalent. This keeps consumer setup zero-touch beyond `pipx install` + `harness-kb init`.

## Data Flow

- **Build time** (maintainer): `harness-kb build --source ../../` reads `ai/docs/` + `graphify-out/`, optionally runs `/graphify update` first, copies docs + graph + wiki into `harness_kb/data/`, copies and adapts the research doc into `data/guide/harness-engineering-playbook.md`, computes BM25 index over chunked sections, writes manifest with version + source commit SHA.
- **Install time** (consumer): `pipx install harness-kb` (or `pipx install ./tools/harness-kb` for local). Data ships inside the wheel.
- **Runtime** (agent): CLI invocation OR MCP server reads from packaged data dir.
- **Init time** (consumer): `harness-kb init --project /path/to/project` injects the guidance section into `<project>/CLAUDE.md`.

## Bundle layout

Inside the installed wheel, under `harness_kb/data/`:

```text
data/
├── manifest.json              {version, source_commit_sha, build_date, doc_count, graph_node_count, themes: [...]}
├── ai_docs/                   verbatim copy of ai-study-library/ai/docs/
│   ├── README.md
│   ├── agent-protocols/
│   ├── agentic-engineering/
│   └── … (all 17 themes)
├── graph/
│   ├── graph.json             verbatim from graphify-out/graph.json
│   └── GRAPH_REPORT.md        verbatim from graphify-out/GRAPH_REPORT.md
├── wiki/                      verbatim from graphify-out/wiki/
│   ├── index.md
│   └── … (all community pages)
├── guide/
│   └── harness-engineering-playbook.md   adapted from dev/research/2026-04-25-harness-engineering-research.md
└── index/
    ├── bm25_corpus.pkl        tokenized chunked corpus (covers ai_docs/ + guide/)
    ├── bm25_index.pkl         rank_bm25 BM25Okapi instance
    └── chunks.json            [{path, heading, char_start, char_end, token_count}] — chunk metadata
```
