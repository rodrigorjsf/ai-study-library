---
title: harness-kb — Portable Knowledge-Stack Tool (Sub-project B)
date: 2026-04-25
status: design-approved
target_dir: ai-study-library/tools/harness-kb/
related_subproject: A (research-doc HumanLayer reframe — shipped on main; the reframed research doc is the source for harness-kb's bundled playbook)
---

# harness-kb — Portable Knowledge-Stack Tool (Sub-project B)

## Goal

Provide a portable, version-pinned Python package — `harness-kb` — that gives any project's LLM agents typed access to the harness-engineering knowledge stack: the `ai/docs/` corpus, the `graphify-out/` knowledge graph, the auto-generated wiki, and a comprehensive playbook adapted from the research doc shipped in sub-project A.

Consumer projects install one package (`pipx install harness-kb`) and run one command (`harness-kb init`) to wire the tool into their CLAUDE.md so agents always reach for it when working on agent / harness / context-engineering topics. No external skill, no external repo, no network calls at runtime.

This spec is the second half of the harness-engineering knowledge-stack effort. Sub-project A (shipped) made the research doc portable; sub-project B (this spec) wraps that doc and the rest of the knowledge stack into a distributable tool.

## Scope

### In scope

- A new Python package living at `ai-study-library/tools/harness-kb/`.
- Hybrid CLI + MCP surface backed by one shared retrieval core.
- Bundled, frozen-at-build-time data: `ai/docs/` + `graphify-out/graph.json` + `graphify-out/wiki/` + adapted research doc + BM25 index + manifest.
- BM25 + section-level retrieval over `ai/docs/` and the playbook.
- Native graph operations (path, explain, find, community, keyword query) via `networkx` reading the bundled `graph.json`.
- A `harness-kb init` command that injects (idempotent) a ~30-line guidance section into a consumer project's CLAUDE.md.
- Documentation files inside the tool directory: README, architecture, CLI reference, MCP reference, CLAUDE.md injection rationale, build/release ritual, changelog.
- A maintainer build pipeline (`harness-kb build`) that re-bundles data from a parent `ai-study-library/` checkout, including a deterministic adaptation step that rewrites `/graphify` references in the research doc to `harness-kb` references.
- Test suite covering CLI dispatch, MCP tool round-trip, BM25 search correctness, graph traversal correctness, CLAUDE.md injection idempotency, build pipeline smoke.

### Out of scope (v0.1.0)

- PyPI / private-index publication. Local `pipx install ./tools/harness-kb` only.
- CI/CD release workflow. Add later when distribution becomes a need.
- Embedding-based semantic search. The graph already covers concept-level semantic retrieval; BM25 covers literal-text lookup; embeddings would duplicate effort and add 100-500 MB of model dependency.
- Web UI / desktop UI.
- Natural-language graph query (the `/graphify query` LLM-powered surface). The tool exposes a deterministic `graph query` that does case-insensitive substring match over node labels; agents can do their own NL→label translation.
- Auto-sync between the source `dev/research/...md` and the bundled adapted copy. The build pipeline performs the adaptation deterministically on each release.

## Architecture Overview

### Components

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

### Boundaries

- CLI and MCP are thin surfaces over four retrieval modules (docs, graph, wiki, guide) plus init.
- Build is maintainer-only; not exposed in installed package's user-facing surface.
- Data is read-only at runtime; refresh = upgrade package version.
- No network calls at runtime. Tool only reads its bundled data and only writes to the consumer project's CLAUDE.md (and only with explicit `init` invocation).
- **No persistent config file.** All runtime behavior is controlled by CLI flags (or MCP tool arguments). The tool deliberately has no `~/.harness-kb/config.toml` or equivalent. This keeps consumer setup zero-touch beyond `pipx install` + `harness-kb init`.

### Data Flow

- **Build time** (maintainer): `harness-kb build --source ../../` reads `ai/docs/` + `graphify-out/`, optionally runs `/graphify update` first, copies docs + graph + wiki into `harness_kb/data/`, copies and adapts the research doc into `data/guide/harness-engineering-playbook.md`, computes BM25 index over chunked sections, writes manifest with version + source commit SHA.
- **Install time** (consumer): `pipx install harness-kb` (or `pipx install ./tools/harness-kb` for local). Data ships inside the wheel.
- **Runtime** (agent): CLI invocation OR MCP server reads from packaged data dir.
- **Init time** (consumer): `harness-kb init --project /path/to/project` injects the guidance section into `<project>/CLAUDE.md`.

## CLI Surface

```text
harness-kb --help                              global help
harness-kb --version                           version + bundled-data SHA

# Discovery
harness-kb themes                              list 17 ai/docs themes + counts
harness-kb docs list [--theme <name>]          list docs (optionally filter by theme)
harness-kb wiki list                           list wiki page titles

# Retrieval
harness-kb docs get <path>                     full doc content
harness-kb docs section <path> <heading>       one section by H2/H3 heading
harness-kb wiki get <page-name>                wiki page content

# Search
harness-kb docs search <query> [--limit N] [--theme <name>]
                                               BM25 hits, ranked, format: path#heading | score | snippet
harness-kb graph query <text>                  case-insensitive substring over node labels
harness-kb graph explain <node-label>          node + 1-hop neighbors
harness-kb graph path <from> <to>              shortest path between two nodes
harness-kb graph find <regex>                  regex match over node labels
harness-kb graph community <name>              all nodes in a community

# Playbook (the heavy adapted research doc)
harness-kb guide                               warn + suggest toc/section first
harness-kb guide --confirm                     full content (~30K tokens)
harness-kb guide toc                           H2/H3 outline only
harness-kb guide section <heading>             one section by heading
harness-kb guide search <query>                BM25 over the playbook only

# Setup
harness-kb init [--project <path>] [--dry-run] inject CLAUDE.md section in project (default: cwd)
harness-kb uninit [--project <path>]           remove the injected section

# Server
harness-kb --mcp                               launch stdio MCP server
```

## MCP Tool Schema

All tools namespaced `harness_kb_*`. The surface has 16 tools — a deliberate choice favoring a rich typed surface (one tool per operation) over a lean dispatch surface (e.g. `harness_kb_docs` with a `verb` parameter). Rationale: agents reason better about discrete typed tools with explicit schemas than about omnibus tools with conditional argument validity. The token cost of 16 tool descriptions is small relative to the context savings from precise, schema-validated retrieval. Revisit if registry-token cost becomes a measured problem.

| Tool | Args | Returns |
|---|---|---|
| `harness_kb_themes` | — | `[{name, doc_count}]` |
| `harness_kb_docs_list` | `theme?: str` | `[{path, theme, title, size_tokens}]` |
| `harness_kb_docs_get` | `path: str` | `{path, content}` |
| `harness_kb_docs_section` | `path: str, heading: str` | `{path, heading, content}` |
| `harness_kb_docs_search` | `query: str, limit?: int=10, theme?: str` | `[{path, heading, score, snippet}]` |
| `harness_kb_wiki_list` | — | `[{name}]` |
| `harness_kb_wiki_get` | `name: str` | `{name, content}` |
| `harness_kb_graph_query` | `text: str` | `[{label, id, community}]` |
| `harness_kb_graph_explain` | `label: str` | `{node, neighbors: [{label, edge_type, weight}]}` |
| `harness_kb_graph_path` | `from: str, to: str` | `{path: [labels], length}` |
| `harness_kb_graph_find` | `pattern: str` | `[{label, id, community}]` |
| `harness_kb_graph_community` | `name: str` | `[{label, id}]` |
| `harness_kb_guide_toc` | — | `[{level, heading, anchor}]` |
| `harness_kb_guide_section` | `heading: str` | `{heading, content, token_estimate}` |
| `harness_kb_guide_get` | `confirm: bool` | full content if confirm=true; else `{warning, toc, token_estimate}` |
| `harness_kb_guide_search` | `query: str, limit?: int=10` | `[{heading, score, snippet}]` |

`init` and `uninit` are CLI-only (one-time setup, not agent-callable at runtime).

### Error Handling

Missing path / node / heading returns `{error: "not_found", detail: "..."}`. No exceptions propagate to the agent. CLI exit code 1 on error, 0 on success.

## Bundled Data Layout

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

### Chunking Strategy (BM25 unit of retrieval)

- Each `ai/docs/*.md` (and the playbook) split at H2/H3 headings.
- Sections >800 tokens further split at paragraph boundaries with 50-token overlap.
- Each chunk has `path`, `heading` (most recent H2/H3), char range. Search returns chunks; `docs_section` / `guide_section` returns the H2/H3 section verbatim (no overlap merging).

### Bundle Size Estimate

ai/docs ~272K words ≈ 2-3 MB; graph.json ≈ 500 KB-1 MB; wiki ≈ 200-500 KB; playbook ≈ 110 KB; BM25 index pickled ≈ 1-2 MB. Total wheel ~5-8 MB.

## Build Pipeline

`harness-kb build` (maintainer-only command, gated behind a `--maintainer` flag or excluded from the installed CLI's help):

1. **Discover source.** Use `--source <path>` flag or detect parent `ai-study-library/` checkout by walking up from cwd until a directory with `ai/docs/` and `graphify-out/` is found.
2. **Check graph freshness.** `/graphify` is a Claude Code slash command and cannot be invoked from a Python subprocess reliably. The build pipeline therefore does NOT auto-refresh the graph. Instead it inspects `<source>/graphify-out/manifest.json` mtimes against `<source>/ai/docs/` mtimes; if any `ai/docs/` file is newer than the manifest, the build aborts with a clear error: `"graph stale: run '/graphify update' inside Claude Code from <source>, then re-run 'harness-kb build'"`. `--no-staleness-check` opts out for hotfix builds.
3. **Validate source health.** `graph.json` parseable; `ai/docs/` contains all 17 expected themes; `dev/research/2026-04-25-harness-engineering-research.md` exists.
4. **Stage data.** Copy `ai/docs/` → `data/ai_docs/`, `graph.json` → `data/graph/`, `wiki/` → `data/wiki/`.
5. **Adapt the playbook.** Run `harness_kb/build/adapt_guide.py` over the research doc; replacements:
   - `/graphify query "<text>"` → `harness-kb graph query "<text>"`
   - `/graphify path "A" "B"` → `harness-kb graph path "A" "B"`
   - `/graphify explain "Node"` → `harness-kb graph explain "Node"`
   - `/graphify --mcp` → `harness-kb --mcp`
   - `graphify-out/graph.json` → `harness-kb graph` (and structurally relocate "see graphify-out/" prose to "see `harness-kb`")
   - `graphify-out/wiki/...` → `harness-kb wiki get <name>` (where the wiki name is identifiable; otherwise generic "see harness-kb wiki")
   - Frontmatter `sources:` entries:
     - `ai/docs/ (...)` → unchanged (the corpus is bundled at `data/ai_docs/`; the relative reference still resolves under the package install)
     - `https://github.com/humanlayer/humanlayer (...)` → unchanged (already a URL, portable)
     - `graphify-out/ (...)` → `harness-kb graph + harness-kb wiki (knowledge graph + auto-generated wiki bundled in this package)`
     - any other local-path entry → either rewrite to a bundle-relative description (`harness-kb ...`) or remove if no portable equivalent exists; record the decision in `adapt_guide.py` as an explicit rule
   - `ai/docs/<path>` paths in body unchanged (still resolve inside the bundle)
   - `graphify-out/wiki/<name>.md` paths → `harness-kb wiki get <name>` where `<name>` is the URL-decoded page basename without `.md` extension; if the basename is ambiguous, fall back to `harness-kb wiki list` reference
   - Output validation: `grep -c "/graphify" data/guide/harness-engineering-playbook.md` must be 0; `grep -c "harness-kb" data/guide/harness-engineering-playbook.md` must be > 0
6. **Build BM25 index.** Walk `data/ai_docs/` + `data/guide/`, chunk per strategy, tokenize (unicodedata + simple whitespace), serialize `bm25_corpus.pkl`, `bm25_index.pkl`, `chunks.json`.
7. **Write manifest.** Pull source git commit SHA, bump tool version per `--version` flag or `pyproject.toml`, capture build_date, doc_count, graph_node_count, themes.
8. **Validate post-build.** Load index from disk, run 3 smoke queries, confirm hits. Run 2 graph operations against `data/graph/graph.json`, confirm results.
9. **(Optional with `--publish`)** Build wheel + upload to PyPI / private index. Deferred — out of scope for v0.1.0.

## Versioning

- Tool version in `pyproject.toml` follows semver: major.minor.patch.
- Data SHA stored in `manifest.json` = `git rev-parse HEAD` of source repo at build time.
- `harness-kb --version` prints both: `harness-kb 0.3.0 (data=ai-study-library@a1b2c3d, built 2026-04-25)`.
- Bumping data alone = patch release (0.3.0 → 0.3.1).
- Adding/changing CLI/MCP shape = minor (0.3 → 0.4).
- Breaking install/path layout = major (0 → 1).

## CLAUDE.md Injection

`harness-kb init` writes the following block. Idempotent: detect existing `<!-- harness-kb v` markers, replace; otherwise append.

```markdown
<!-- harness-kb v{version} BEGIN -->
## Harness Knowledge Base (`harness-kb`)

This project has access to `harness-kb` — a portable, version-pinned knowledge base of agent / harness / context-engineering reference material drawn from the `ai-study-library` corpus. **Always consult `harness-kb` before implementing, designing, or reasoning about any of the following themes:**

- agent-protocols (MCP, A2A, ACP, ANP)
- agentic-engineering (RPI, harness patterns, plan-implement workflows)
- analysis (study notes on LLM agent papers and posts)
- claude (Claude-specific guides: prompting, harnesses, long-running agents)
- claude-code (Claude Code: hooks, skills, plugins, settings, IDE)
- context-engineering (smart zone, progressive disclosure, attention sinks, context rot)
- cursor (Cursor IDE: rules, hooks, subagents, plugins, agent tools)
- general-llm (LLM behavior, evaluation, structured outputs)
- harness-engineering (canonical patterns, references, skills, agents, hooks, evals)
- human-layer-project (HumanLayer codebase as case study)
- long-context-research (Lost-in-the-Middle, recall curves, chunking)
- mcp (Model Context Protocol: primitives, runtime, governance)
- shared (cross-cutting reference material)
- spec-driven-development (Spec Kit, Constitutional Foundation, SDD tools)
- structured-outputs (tool use, JSON schema, strict mode, prefilling)
- tool-calling (tool design, programmatic tool calling, search)

### How to use it

**Discovery:**

    harness-kb themes                          # what topics are available
    harness-kb docs list --theme <name>        # docs in a theme
    harness-kb wiki list                       # graph-derived wiki pages

**Retrieval (prefer section over full doc to save context):**

    harness-kb docs section <path> "<heading>" # one section
    harness-kb docs search "<query>"           # ranked BM25 hits
    harness-kb wiki get <page-name>            # wiki page

**Graph queries (concept-level reasoning):**

    harness-kb graph query "<text>"            # fuzzy substring over node labels
    harness-kb graph explain "<node-label>"    # node + 1-hop neighbors
    harness-kb graph path "<from>" "<to>"      # path between concepts
    harness-kb graph community "<name>"        # all nodes in a community

**Native MCP server (preferred for agents — typed tools, persistent context):**

    harness-kb --mcp

Configure in `.claude/settings.json` under `mcpServers` if Claude Code is the harness, or via the equivalent block for other agent runtimes.

### Comprehensive playbook (heavy — ~1500 lines, ~30K tokens)

When you want **complete coverage** of harness-engineering concepts, examples, primary-source references, and 281 pre-built graph queries before writing any artifact or memory, consult the playbook:

    harness-kb guide toc                       # outline first (cheap)
    harness-kb guide section "<H2>"            # one section at a time (preferred)
    harness-kb guide search "<query>"          # find relevant sections
    harness-kb guide --confirm                 # full file — only when you genuinely need it all

Loading the full playbook costs ~30K tokens. Default to `toc` + targeted `section` retrieval.

### When to consult

- Before writing skills, hooks, agents, plugins, rules, or any harness artifact.
- Before designing context-management strategies (always-loaded memory, progressive disclosure, subagent dispatch).
- Before implementing tool-use schemas, structured-output contracts, or MCP servers.
- When debugging recurring agent failures — check whether a known pattern (smart-zone violation, lost-in-the-middle, context rot) explains the symptom.
- When choosing between architectural options (heavy-stack vs lean-shell, MCP vs A2A, hooks vs slash commands).

### Examples

    # Find docs about back-pressure
    harness-kb docs search "back-pressure"

    # What's in the smart-zone concept space?
    harness-kb graph explain "Dumb Zone / Smart Zone (Context Threshold)"

    # How are skills and progressive disclosure connected?
    harness-kb graph path "Agent Skills Standard" "Progressive Disclosure (Skills Context Management)"

`harness-kb --version` shows the bundled data snapshot. To upgrade the snapshot: upgrade the package.
<!-- harness-kb v{version} END -->
```

### Init Behavior Rules

- Default project = current working directory. `--project <path>` overrides.
- If `<project>/CLAUDE.md` does not exist: create it with this block as the sole content.
- If exists and contains `<!-- harness-kb v` markers: replace the block (idempotent upgrade). Both BEGIN and END markers must be present for replacement; if only one is found, abort with an error rather than corrupt the file.
- If exists without markers: ensure the file ends with exactly one trailing newline, then append a blank line, then append the block. The block itself ends with one trailing newline.
- `--dry-run`: print what would change, do not write.
- `uninit`: remove the marked block; leave the rest of CLAUDE.md untouched.

## Repo Layout

```text
tools/harness-kb/
├── pyproject.toml              package metadata, deps: click, networkx, rank_bm25, mcp (Python SDK)
├── README.md                   tool docs: objective, install, CLI, MCP, init usage, examples
├── CHANGELOG.md                release notes; data SHA per version
├── LICENSE                     (user choice — MIT/Apache-2.0/etc.)
├── docs/
│   ├── architecture.md         components, data flow, boundary contract
│   ├── cli-reference.md        full CLI surface
│   ├── mcp-reference.md        MCP tool schemas
│   ├── claude-md-injection.md  what `init` writes + rationale
│   └── build.md                maintainer build pipeline + release ritual
├── src/
│   └── harness_kb/
│       ├── __init__.py         version constant
│       ├── __main__.py         `python -m harness_kb` entry
│       ├── cli.py              click command group + subcommands
│       ├── mcp.py              stdio MCP server, tool registration
│       ├── docs.py             ai/docs retrieval module
│       ├── graph.py            graph.json query module
│       ├── wiki.py             wiki retrieval module
│       ├── guide.py            playbook retrieval module
│       ├── init.py             CLAUDE.md injection logic
│       ├── search.py           shared BM25 search backend
│       ├── chunking.py         shared chunking strategy
│       ├── manifest.py         manifest.json loader / version helper
│       ├── build.py            maintainer-only: build pipeline (excluded from runtime imports)
│       └── data/               bundled snapshot
├── tests/
│   ├── test_cli.py             CLI smoke tests via Click's CliRunner
│   ├── test_mcp.py             MCP tool dispatch tests
│   ├── test_docs.py            list / get / section / search round-trips
│   ├── test_graph.py           path / explain / find / community
│   ├── test_wiki.py
│   ├── test_guide.py           toc / section / search / get-with-confirm
│   ├── test_init.py            CLAUDE.md injection idempotency, dry-run, uninit
│   ├── test_adapt_guide.py     adaptation rules: every /graphify reference rewritten correctly
│   ├── test_build.py           build pipeline smoke (uses fixture mini-source)
│   └── fixtures/
│       └── mini-source/        tiny ai-study-library replica for build tests
└── .github/
    └── workflows/
        └── ci.yml              (deferred) — lint + test + (later) build+publish
```

### Documentation Files

Each must exist before v0.1.0 ships:

| File | Length | Audience | Contents |
|---|---|---|---|
| `README.md` | ~150 lines | first-time users | objective, install, quickstart (CLI + MCP + init), example session, link to detailed docs |
| `docs/architecture.md` | ~80 lines | contributors | components table, data flow, boundary contract |
| `docs/cli-reference.md` | ~100 lines | users | every subcommand with args + example output |
| `docs/mcp-reference.md` | ~100 lines | agent integrators | every tool schema + example request/response |
| `docs/claude-md-injection.md` | ~50 lines | users | what `init` writes verbatim + idempotency rules |
| `docs/build.md` | ~80 lines | maintainer | build pipeline steps + release checklist |
| `CHANGELOG.md` | grows | users + maintainer | per-version: tool changes + bundled data SHA |

## Testing

- **Coverage target:** ~80%.
- **Critical paths:**
  - BM25 retrieval correctness (synthetic corpus): build index → known query → expected ranked hits.
  - Graph traversal correctness (synthetic graph): path between known nodes; explain returns expected neighbors.
  - CLAUDE.md injection idempotency: write → re-init → no diff. Append-without-marker on existing CLAUDE.md leaves prior content intact. uninit removes only the marked block.
  - MCP tool dispatch round-trip: each tool callable, returns expected schema, handles missing inputs gracefully.
  - Adaptation rules: build-time `adapt_guide.py` rewrites every `/graphify` reference; output has zero `/graphify` strings and at least one `harness-kb` reference per category.
  - Build smoke test using `tests/fixtures/mini-source/` (a 3-doc, 5-node minimal replica of `ai-study-library/`).

## Success Criteria

- `pipx install ./tools/harness-kb` succeeds on a fresh checkout.
- `harness-kb --version` prints semver + data SHA.
- `harness-kb themes` lists all 17 themes.
- `harness-kb docs search "smart zone"` returns at least one ranked hit pointing to a real `ai/docs/` section.
- `harness-kb graph explain "Subagent as Context Firewall"` returns the node and its 1-hop neighbors.
- `harness-kb guide toc` lists the playbook's H2/H3 headings.
- `harness-kb guide --confirm` is the only way to get the full ~110 KB content; the bare `harness-kb guide` warns and returns `toc` instead.
- `harness-kb --mcp` launches a stdio MCP server that responds to `tools/list` with all 16 documented tools.
- `harness-kb init --project /tmp/test-proj --dry-run` previews the injection without writing; without `--dry-run`, it writes idempotently.
- The bundled adapted playbook contains zero `/graphify` references and at least one `harness-kb` reference per adaptation category.
- All tests pass; coverage ≥ 80%.
- A consumer project that has only `pipx install harness-kb` (no internet, no ai-study-library checkout) can answer "what does the smart-zone concept mean" via `harness-kb docs search "smart zone"` followed by `harness-kb docs section <path> "<heading>"`.

## Risk and Rollback

- **Risk:** wheel size grows beyond expected ~5-8 MB if ai/docs expands. Mitigation: monitor in CI, accept as cost; agent-side BM25 retrieval keeps runtime context use small even if bundle grows.
- **Risk:** adaptation script misses a `/graphify` reference variant. Mitigation: post-build validation greps for residuals; CI smoke test asserts zero count.
- **Risk:** consumer's CLAUDE.md is corrupted by init. Mitigation: idempotent markers + `--dry-run` + `uninit` + tests for every injection branch (no file, file without marker, file with marker, multiple markers).
- **Risk:** graph.json schema drifts in upstream graphify and breaks `networkx` loading. Mitigation: `manifest.py` records the graph schema version; load-time check raises a clear error if mismatched; bundle-time validation catches it before release.
- **Rollback:** removing harness-kb from a consumer project is `pipx uninstall harness-kb` + `harness-kb uninit` (run before uninstall). The injected CLAUDE.md block is the only persistent change to the consumer.

## Open Questions for Implementation

- Whether the bundled BM25 index should serialize with `pickle` (faster load, Python-version-tied) or JSON (slower, portable). Default: pickle for v0.1.0; revisit if cross-version install issues surface.
- Tokenizer for BM25: simple whitespace+punctuation split vs `nltk` word_tokenize vs spaCy. Default: simple whitespace+punctuation split (no extra deps); revisit if recall is poor.
- Whether `harness-kb --mcp` should surface a logo/banner on startup. Default: silent (MCP stdio servers should not print to stderr without need).
