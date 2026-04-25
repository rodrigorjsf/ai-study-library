# harness-kb Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `harness-kb` — a portable, version-pinned Python package that bundles the `ai/docs/` corpus, the `graphify-out/` knowledge graph, the auto-generated wiki, and an adapted research playbook, exposing them through both a CLI and an MCP server.

**Architecture:** Single Python package at `tools/harness-kb/` with thin CLI (Click) and MCP (mcp Python SDK) surfaces over four retrieval modules (`docs`, `graph`, `wiki`, `guide`) plus an `init` module for CLAUDE.md injection. Bundled data ships inside the wheel under `src/harness_kb/data/`. Maintainer-only `build` pipeline (and `adapt_guide`) re-bundles data from a parent `ai-study-library/` checkout.

**Tech Stack:** Python 3.10+; click 8.x; networkx 3.x; rank_bm25 0.2.x; mcp (Python SDK) latest; pytest 8.x; pipx for install.

**Companion spec:** `docs/superpowers/specs/2026-04-25-harness-kb-design.md`. Refer to spec for full architectural rationale, hard rules, and out-of-scope items. Plan tasks reference spec sections explicitly.

---

## Locked-In Type Contracts

The following dataclasses and function signatures are referenced across multiple tasks. Implementers MUST use these exact names and shapes. Each appears in the task that owns it; this section is a quick reference.

```python
# manifest.py
@dataclass
class Manifest:
    version: str
    source_commit_sha: str
    build_date: str
    doc_count: int
    graph_node_count: int
    themes: list[str]

# chunking.py
@dataclass
class Chunk:
    path: str          # relative path under data root, e.g. "ai_docs/agent-protocols/mcp-overview.md"
    heading: str       # most recent H2/H3 heading text
    char_start: int
    char_end: int
    token_count: int
    text: str

# search.py
@dataclass
class SearchHit:
    path: str
    heading: str
    score: float
    snippet: str

# docs.py
@dataclass
class DocInfo:
    path: str          # e.g. "agent-protocols/mcp-overview.md" (relative under ai_docs/)
    theme: str
    title: str
    size_tokens: int

# graph.py
@dataclass
class GraphNode:
    label: str
    id: str
    community: str | None

@dataclass
class GraphNeighbor:
    label: str
    edge_type: str
    weight: float

# guide.py
@dataclass
class GuideSection:
    level: int         # 2 for H2, 3 for H3
    heading: str
    anchor: str        # GitHub-flavored slug
```

---

## Pre-flight

### Pre-flight Task A: Commit spec + plan to main

**Files:**

- `docs/superpowers/specs/2026-04-25-harness-kb-design.md` (already on disk, untracked)
- `docs/superpowers/plans/2026-04-25-harness-kb-implementation.md` (this file, untracked)

- [ ] **Step 1: Stage the spec and plan files**

```bash
cd /home/rodrigo/Workspace/ai-study-library
rtk git add docs/superpowers/specs/2026-04-25-harness-kb-design.md \
         docs/superpowers/plans/2026-04-25-harness-kb-implementation.md
```

- [ ] **Step 2: Commit on main**

```bash
rtk git commit -m "$(cat <<'EOF'
docs: add spec and plan for harness-kb (Sub-project B)

Specifies the harness-kb portable knowledge-stack tool that bundles
ai/docs + graphify-out + wiki + an adapted playbook, exposing both
CLI and MCP surfaces. Sub-project B of the harness-engineering
knowledge stack effort. Plan is the v0.1.0 implementation roadmap.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 3: Verify commit**

```bash
rtk git log -1 --stat
```

Expected: shows both files added.

### Pre-flight Task B: Scaffold tools/harness-kb/ skeleton

**Files (created):**

- `tools/harness-kb/pyproject.toml`
- `tools/harness-kb/README.md` (skeleton)
- `tools/harness-kb/CHANGELOG.md`
- `tools/harness-kb/LICENSE` (MIT)
- `tools/harness-kb/.gitignore`
- `tools/harness-kb/src/harness_kb/__init__.py`
- `tools/harness-kb/src/harness_kb/__main__.py`
- `tools/harness-kb/src/harness_kb/data/.gitkeep`
- `tools/harness-kb/tests/__init__.py`
- `tools/harness-kb/tests/conftest.py`

- [ ] **Step 1: Create directory tree**

```bash
mkdir -p /home/rodrigo/Workspace/ai-study-library/tools/harness-kb/{src/harness_kb/data,src/harness_kb/build,docs,tests/fixtures}
touch /home/rodrigo/Workspace/ai-study-library/tools/harness-kb/src/harness_kb/data/.gitkeep
```

- [ ] **Step 2: Write pyproject.toml**

```toml
# tools/harness-kb/pyproject.toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "harness-kb"
version = "0.1.0"
description = "Portable knowledge base of agent / harness / context-engineering reference material."
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [{name = "Rodrigo França", email = "rodrigo_rjsf@hotmail.com"}]
dependencies = [
    "click>=8.1,<9",
    "networkx>=3.2,<4",
    "rank-bm25>=0.2.2,<0.3",
    "mcp>=1.0,<2",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0,<9",
    "pytest-cov>=4.1,<5",
]

[project.scripts]
harness-kb = "harness_kb.cli:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
harness_kb = ["data/**/*", "data/**/.gitkeep"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"
```

- [ ] **Step 3: Write `__init__.py` with version constant**

```python
# tools/harness-kb/src/harness_kb/__init__.py
__version__ = "0.1.0"
```

- [ ] **Step 4: Write `__main__.py`**

```python
# tools/harness-kb/src/harness_kb/__main__.py
from harness_kb.cli import main

if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Write README.md skeleton**

```markdown
# harness-kb

Portable knowledge base of agent / harness / context-engineering reference material.

> **Status:** v0.1.0 in development. See [spec](../../docs/superpowers/specs/2026-04-25-harness-kb-design.md) and [implementation plan](../../docs/superpowers/plans/2026-04-25-harness-kb-implementation.md).

Full README is filled in by Task 13.
```

- [ ] **Step 6: Write CHANGELOG.md**

```markdown
# Changelog

## v0.1.0 (unreleased)

- Initial release. CLI + MCP surface over bundled ai/docs + graphify-out + wiki + adapted playbook.
```

- [ ] **Step 7: Write LICENSE (MIT)**

```text
MIT License

Copyright (c) 2026 Rodrigo França

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

- [ ] **Step 8: Write `.gitignore`**

```text
__pycache__/
*.pyc
.pytest_cache/
*.egg-info/
build/
dist/
.coverage
htmlcov/
```

- [ ] **Step 9: Write `tests/__init__.py` (empty) and `tests/conftest.py`**

```python
# tools/harness-kb/tests/__init__.py
```

```python
# tools/harness-kb/tests/conftest.py
import sys
from pathlib import Path

# Allow `from harness_kb import ...` in tests without installing the package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
```

- [ ] **Step 10: Verify scaffold**

```bash
cd /home/rodrigo/Workspace/ai-study-library/tools/harness-kb
python -c "from harness_kb import __version__; print(__version__)"
```

Expected: `0.1.0` (assumes `tests/conftest.py` is loaded by pytest; for raw `python -c`, you may need to set PYTHONPATH=src or run from inside `src/`).

```bash
python -c "import sys; sys.path.insert(0, 'src'); from harness_kb import __version__; print(__version__)"
```

Expected: `0.1.0`.

- [ ] **Step 11: Commit**

```bash
cd /home/rodrigo/Workspace/ai-study-library
rtk git add tools/harness-kb/
rtk git commit -m "$(cat <<'EOF'
feat(harness-kb): scaffold package skeleton

Adds tools/harness-kb/ with pyproject.toml, version constant, and
empty placeholders for the four retrieval modules + build pipeline.
No functional code yet — Task 1 starts manifest.py.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 1: manifest.py

**Goal:** Implement `Manifest` dataclass + load/save/locate-data helpers. Used by every other module to find the bundled data dir and read package metadata.

**Files:**

- Create: `tools/harness-kb/src/harness_kb/manifest.py`
- Create: `tools/harness-kb/tests/test_manifest.py`

- [ ] **Step 1: Write the failing tests**

```python
# tools/harness-kb/tests/test_manifest.py
import json
from pathlib import Path
import pytest
from harness_kb.manifest import Manifest, load_manifest, get_data_dir


def test_manifest_dataclass_fields():
    m = Manifest(
        version="0.1.0",
        source_commit_sha="abc123",
        build_date="2026-04-25",
        doc_count=42,
        graph_node_count=476,
        themes=["agent-protocols", "claude-code"],
    )
    assert m.version == "0.1.0"
    assert m.themes == ["agent-protocols", "claude-code"]


def test_load_manifest_from_dir(tmp_path: Path):
    payload = {
        "version": "0.1.0",
        "source_commit_sha": "abc123",
        "build_date": "2026-04-25",
        "doc_count": 42,
        "graph_node_count": 476,
        "themes": ["agent-protocols"],
    }
    (tmp_path / "manifest.json").write_text(json.dumps(payload))
    m = load_manifest(tmp_path)
    assert m.version == "0.1.0"
    assert m.doc_count == 42


def test_load_manifest_missing_file_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_manifest(tmp_path)


def test_get_data_dir_returns_package_data_path():
    d = get_data_dir()
    assert d.is_dir()
    assert d.name == "data"
    assert d.parent.name == "harness_kb"
```

- [ ] **Step 2: Run tests, verify red**

```bash
cd /home/rodrigo/Workspace/ai-study-library/tools/harness-kb
python -m pytest tests/test_manifest.py -v
```

Expected: ImportError or ModuleNotFoundError on `harness_kb.manifest`.

- [ ] **Step 3: Implement manifest.py**

```python
# tools/harness-kb/src/harness_kb/manifest.py
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Manifest:
    version: str
    source_commit_sha: str
    build_date: str
    doc_count: int
    graph_node_count: int
    themes: list[str]


def get_data_dir() -> Path:
    return Path(__file__).parent / "data"


def load_manifest(data_dir: Path | None = None) -> Manifest:
    if data_dir is None:
        data_dir = get_data_dir()
    manifest_path = data_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"manifest.json not found at {manifest_path}")
    payload = json.loads(manifest_path.read_text())
    return Manifest(**payload)


def save_manifest(manifest: Manifest, data_dir: Path) -> None:
    payload = {
        "version": manifest.version,
        "source_commit_sha": manifest.source_commit_sha,
        "build_date": manifest.build_date,
        "doc_count": manifest.doc_count,
        "graph_node_count": manifest.graph_node_count,
        "themes": manifest.themes,
    }
    (data_dir / "manifest.json").write_text(json.dumps(payload, indent=2))
```

- [ ] **Step 4: Run tests, verify green**

```bash
python -m pytest tests/test_manifest.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
cd /home/rodrigo/Workspace/ai-study-library
rtk git add tools/harness-kb/src/harness_kb/manifest.py tools/harness-kb/tests/test_manifest.py
rtk git commit -m "feat(harness-kb): manifest dataclass + load/save helpers

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: chunking.py

**Goal:** Split markdown content at H2/H3 boundaries, then sub-split sections >800 tokens at paragraph boundaries with 50-token overlap. Returns `Chunk` objects keyed by `(path, heading)`.

**Files:**

- Create: `tools/harness-kb/src/harness_kb/chunking.py`
- Create: `tools/harness-kb/tests/test_chunking.py`

- [ ] **Step 1: Write the failing tests**

```python
# tools/harness-kb/tests/test_chunking.py
from harness_kb.chunking import Chunk, chunk_markdown, count_tokens


def test_count_tokens_simple():
    assert count_tokens("hello world") == 2
    assert count_tokens("") == 0


def test_chunk_markdown_one_section():
    text = "# Title\n\n## Section A\n\nSome content here."
    chunks = chunk_markdown(text, "doc.md")
    assert len(chunks) == 1
    assert chunks[0].heading == "Section A"
    assert chunks[0].path == "doc.md"
    assert "Some content here." in chunks[0].text


def test_chunk_markdown_h3_under_h2():
    text = "## Section A\n\nIntro.\n\n### Sub A1\n\nDetail."
    chunks = chunk_markdown(text, "doc.md")
    headings = [c.heading for c in chunks]
    assert "Section A" in headings
    assert "Sub A1" in headings


def test_chunk_markdown_long_section_subsplit():
    body = "para. " * 1000  # ~1000 tokens
    text = f"## Big Section\n\n{body}"
    chunks = chunk_markdown(text, "doc.md", max_tokens=300, overlap_tokens=20)
    assert len(chunks) > 1
    for c in chunks:
        assert c.heading == "Big Section"
        assert c.token_count <= 320  # max + overlap tolerance


def test_chunk_markdown_no_headings_returns_one_chunk():
    text = "Just plain text with no headings.\n\nMore text."
    chunks = chunk_markdown(text, "doc.md")
    assert len(chunks) == 1
    assert chunks[0].heading == ""


def test_chunk_char_ranges_contiguous():
    text = "## A\n\nfirst.\n\n## B\n\nsecond."
    chunks = chunk_markdown(text, "doc.md")
    for c in chunks:
        assert c.char_end > c.char_start
        assert text[c.char_start:c.char_end] == c.text
```

- [ ] **Step 2: Run tests, verify red**

```bash
cd /home/rodrigo/Workspace/ai-study-library/tools/harness-kb
python -m pytest tests/test_chunking.py -v
```

Expected: ImportError on `harness_kb.chunking`.

- [ ] **Step 3: Implement chunking.py**

```python
# tools/harness-kb/src/harness_kb/chunking.py
from __future__ import annotations
import re
from dataclasses import dataclass


@dataclass
class Chunk:
    path: str
    heading: str
    char_start: int
    char_end: int
    token_count: int
    text: str


_WORD_RE = re.compile(r"\w+", re.UNICODE)


def count_tokens(text: str) -> int:
    return len(_WORD_RE.findall(text))


def _find_headings(text: str) -> list[tuple[int, int, str]]:
    """Return [(start_offset, level, heading_text)] for H2/H3 headings."""
    out = []
    for m in re.finditer(r"^(#{2,3})\s+(.+?)\s*$", text, re.MULTILINE):
        out.append((m.start(), len(m.group(1)), m.group(2).strip()))
    return out


def _split_long_section(
    text: str, base_offset: int, max_tokens: int, overlap_tokens: int
) -> list[tuple[int, int, str]]:
    """Split a section's body at paragraph boundaries; return [(start, end, text)]."""
    paragraphs = re.split(r"\n\s*\n", text)
    out = []
    cur_para_buf: list[str] = []
    cur_token_count = 0
    cur_start = 0

    for para in paragraphs:
        ptokens = count_tokens(para)
        if cur_token_count + ptokens > max_tokens and cur_para_buf:
            chunk_text = "\n\n".join(cur_para_buf)
            chunk_start = base_offset + text.find(chunk_text, cur_start)
            chunk_end = chunk_start + len(chunk_text)
            out.append((chunk_start, chunk_end, chunk_text))
            # overlap: keep last paragraphs whose token count sums up to ~overlap_tokens
            kept: list[str] = []
            kept_tokens = 0
            for p in reversed(cur_para_buf):
                if kept_tokens >= overlap_tokens:
                    break
                kept.insert(0, p)
                kept_tokens += count_tokens(p)
            cur_para_buf = kept[:]
            cur_token_count = kept_tokens
            cur_start = chunk_end - base_offset
        cur_para_buf.append(para)
        cur_token_count += ptokens

    if cur_para_buf:
        chunk_text = "\n\n".join(cur_para_buf)
        chunk_start = base_offset + text.find(chunk_text, cur_start)
        chunk_end = chunk_start + len(chunk_text)
        out.append((chunk_start, chunk_end, chunk_text))

    return out


def chunk_markdown(
    text: str, path: str, max_tokens: int = 800, overlap_tokens: int = 50
) -> list[Chunk]:
    headings = _find_headings(text)

    if not headings:
        return [Chunk(
            path=path, heading="", char_start=0, char_end=len(text),
            token_count=count_tokens(text), text=text,
        )]

    chunks: list[Chunk] = []
    for i, (h_start, _level, h_text) in enumerate(headings):
        next_start = headings[i + 1][0] if i + 1 < len(headings) else len(text)
        # body of this heading = text from end-of-heading-line through next heading
        line_end = text.find("\n", h_start)
        if line_end < 0:
            line_end = h_start
        body_start = line_end + 1
        body = text[body_start:next_start]
        body_tokens = count_tokens(body)

        if body_tokens <= max_tokens:
            chunks.append(Chunk(
                path=path,
                heading=h_text,
                char_start=h_start,
                char_end=next_start,
                token_count=count_tokens(text[h_start:next_start]),
                text=text[h_start:next_start],
            ))
        else:
            # split body, keep heading prepended on first sub-chunk
            sub = _split_long_section(body, body_start, max_tokens, overlap_tokens)
            for j, (s, e, t) in enumerate(sub):
                if j == 0:
                    full_start = h_start
                    full_text = text[h_start:e]
                else:
                    full_start = s
                    full_text = t
                chunks.append(Chunk(
                    path=path,
                    heading=h_text,
                    char_start=full_start,
                    char_end=e,
                    token_count=count_tokens(full_text),
                    text=full_text,
                ))
    return chunks
```

- [ ] **Step 4: Run tests, verify green**

```bash
python -m pytest tests/test_chunking.py -v
```

Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
cd /home/rodrigo/Workspace/ai-study-library
rtk git add tools/harness-kb/src/harness_kb/chunking.py tools/harness-kb/tests/test_chunking.py
rtk git commit -m "feat(harness-kb): markdown chunking by H2/H3 with overlap subsplit

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: search.py (BM25 backend)

**Goal:** Wrap `rank_bm25.BM25Okapi` with build / save / load / search. Returns `SearchHit` per chunk.

**Files:**

- Create: `tools/harness-kb/src/harness_kb/search.py`
- Create: `tools/harness-kb/tests/test_search.py`

- [ ] **Step 1: Write the failing tests**

```python
# tools/harness-kb/tests/test_search.py
from pathlib import Path
import pytest
from harness_kb.chunking import Chunk
from harness_kb.search import BM25SearchIndex, SearchHit, tokenize


def test_tokenize_basic():
    assert tokenize("Hello, World!") == ["hello", "world"]
    assert tokenize("") == []


def _sample_chunks() -> list[Chunk]:
    return [
        Chunk(path="a.md", heading="A", char_start=0, char_end=10, token_count=2,
              text="back-pressure mechanisms in agent harnesses"),
        Chunk(path="b.md", heading="B", char_start=0, char_end=10, token_count=2,
              text="smart zone context window threshold"),
        Chunk(path="c.md", heading="C", char_start=0, char_end=10, token_count=2,
              text="progressive disclosure of skills"),
    ]


def test_search_returns_relevant_hits():
    idx = BM25SearchIndex.build(_sample_chunks())
    hits = idx.search("back-pressure", limit=5)
    assert len(hits) >= 1
    assert hits[0].path == "a.md"
    assert hits[0].heading == "A"


def test_search_respects_limit():
    idx = BM25SearchIndex.build(_sample_chunks())
    hits = idx.search("a", limit=2)
    assert len(hits) <= 2


def test_search_with_path_filter():
    idx = BM25SearchIndex.build(_sample_chunks())
    hits = idx.search("zone", path_filter="b.md")
    for h in hits:
        assert h.path.startswith("b.md")


def test_search_round_trip_via_save_load(tmp_path: Path):
    chunks = _sample_chunks()
    idx = BM25SearchIndex.build(chunks)
    idx.save(tmp_path / "index.pkl", tmp_path / "chunks.json")

    loaded = BM25SearchIndex.load(tmp_path / "index.pkl", tmp_path / "chunks.json")
    hits = loaded.search("smart zone")
    assert any("smart zone" in h.snippet.lower() for h in hits)


def test_search_empty_query_returns_empty():
    idx = BM25SearchIndex.build(_sample_chunks())
    assert idx.search("") == []


def test_snippet_contains_query_term_or_context():
    idx = BM25SearchIndex.build(_sample_chunks())
    hits = idx.search("disclosure")
    assert hits[0].path == "c.md"
    assert "disclosure" in hits[0].snippet.lower() or hits[0].snippet
```

- [ ] **Step 2: Run tests, verify red**

```bash
python -m pytest tests/test_search.py -v
```

Expected: ImportError on `harness_kb.search`.

- [ ] **Step 3: Implement search.py**

```python
# tools/harness-kb/src/harness_kb/search.py
from __future__ import annotations
import json
import pickle
import re
from dataclasses import dataclass
from pathlib import Path

from rank_bm25 import BM25Okapi

from harness_kb.chunking import Chunk


@dataclass
class SearchHit:
    path: str
    heading: str
    score: float
    snippet: str


_TOKEN_RE = re.compile(r"[\w]+", re.UNICODE)


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text)]


def _make_snippet(text: str, query_tokens: list[str], window: int = 80) -> str:
    if not query_tokens:
        return text[:window].strip()
    lower = text.lower()
    best_idx = -1
    for tok in query_tokens:
        i = lower.find(tok)
        if i >= 0 and (best_idx < 0 or i < best_idx):
            best_idx = i
    if best_idx < 0:
        return text[:window].strip()
    start = max(0, best_idx - window // 4)
    end = min(len(text), start + window)
    snippet = text[start:end].strip()
    if start > 0:
        snippet = "…" + snippet
    if end < len(text):
        snippet = snippet + "…"
    return snippet


class BM25SearchIndex:
    def __init__(self, chunks: list[Chunk], bm25: BM25Okapi):
        self.chunks = chunks
        self.bm25 = bm25

    @classmethod
    def build(cls, chunks: list[Chunk]) -> "BM25SearchIndex":
        tokenized = [tokenize(c.text) for c in chunks]
        bm25 = BM25Okapi(tokenized)
        return cls(chunks, bm25)

    @classmethod
    def load(cls, index_path: Path, chunks_path: Path) -> "BM25SearchIndex":
        with index_path.open("rb") as f:
            bm25 = pickle.load(f)
        chunk_dicts = json.loads(chunks_path.read_text())
        chunks = [Chunk(**d) for d in chunk_dicts]
        return cls(chunks, bm25)

    def save(self, index_path: Path, chunks_path: Path) -> None:
        index_path.parent.mkdir(parents=True, exist_ok=True)
        with index_path.open("wb") as f:
            pickle.dump(self.bm25, f)
        chunk_dicts = [
            {"path": c.path, "heading": c.heading, "char_start": c.char_start,
             "char_end": c.char_end, "token_count": c.token_count, "text": c.text}
            for c in self.chunks
        ]
        chunks_path.write_text(json.dumps(chunk_dicts))

    def search(
        self, query: str, limit: int = 10, path_filter: str | None = None
    ) -> list[SearchHit]:
        q_tokens = tokenize(query)
        if not q_tokens:
            return []
        scores = self.bm25.get_scores(q_tokens)
        idx_scored = list(enumerate(scores))
        if path_filter:
            idx_scored = [(i, s) for i, s in idx_scored if self.chunks[i].path.startswith(path_filter)]
        idx_scored.sort(key=lambda pair: pair[1], reverse=True)
        idx_scored = [(i, s) for i, s in idx_scored if s > 0][:limit]
        return [
            SearchHit(
                path=self.chunks[i].path,
                heading=self.chunks[i].heading,
                score=float(s),
                snippet=_make_snippet(self.chunks[i].text, q_tokens),
            )
            for i, s in idx_scored
        ]
```

- [ ] **Step 4: Run tests, verify green**

```bash
python -m pytest tests/test_search.py -v
```

Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
cd /home/rodrigo/Workspace/ai-study-library
rtk git add tools/harness-kb/src/harness_kb/search.py tools/harness-kb/tests/test_search.py
rtk git commit -m "feat(harness-kb): BM25 search backend with build/save/load/search

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: docs.py

**Goal:** Public retrieval surface for `data/ai_docs/`. Functions: `list_docs`, `get_doc`, `get_section`, `search_docs`, `list_themes`. Loads BM25 index from `data/index/`.

**Files:**

- Create: `tools/harness-kb/src/harness_kb/docs.py`
- Create: `tools/harness-kb/tests/test_docs.py`
- Create: `tools/harness-kb/tests/fixtures/mini_data/` (test fixture; populated by test setup)

- [ ] **Step 1: Write the failing tests**

```python
# tools/harness-kb/tests/test_docs.py
import json
from pathlib import Path
import pytest

from harness_kb.chunking import Chunk
from harness_kb.search import BM25SearchIndex
from harness_kb import docs as docs_module


@pytest.fixture
def fake_data_dir(tmp_path: Path, monkeypatch) -> Path:
    """Build a minimal data dir resembling the bundle and patch get_data_dir."""
    ai_docs = tmp_path / "ai_docs"
    (ai_docs / "agent-protocols").mkdir(parents=True)
    (ai_docs / "claude-code").mkdir(parents=True)
    (ai_docs / "agent-protocols" / "mcp-overview.md").write_text(
        "# MCP Overview\n\n## Intro\n\nModel Context Protocol overview.\n\n## Primitives\n\nResources, Prompts, Tools, Sampling."
    )
    (ai_docs / "claude-code" / "hooks.md").write_text(
        "# Hooks\n\n## Stop hook\n\nFires after assistant turn ends."
    )
    (ai_docs / "README.md").write_text("# ai/docs\n\nIndex.")

    index_dir = tmp_path / "index"
    index_dir.mkdir()
    chunks = [
        Chunk(path="ai_docs/agent-protocols/mcp-overview.md", heading="Intro",
              char_start=0, char_end=50, token_count=4,
              text="Model Context Protocol overview"),
        Chunk(path="ai_docs/agent-protocols/mcp-overview.md", heading="Primitives",
              char_start=50, char_end=120, token_count=4,
              text="Resources Prompts Tools Sampling"),
        Chunk(path="ai_docs/claude-code/hooks.md", heading="Stop hook",
              char_start=0, char_end=40, token_count=4,
              text="Stop hook fires after assistant turn"),
    ]
    idx = BM25SearchIndex.build(chunks)
    idx.save(index_dir / "bm25_index.pkl", index_dir / "chunks.json")

    monkeypatch.setattr(docs_module, "get_data_dir", lambda: tmp_path)
    return tmp_path


def test_list_themes(fake_data_dir):
    themes = docs_module.list_themes()
    names = {t.name for t in themes}
    assert "agent-protocols" in names
    assert "claude-code" in names


def test_list_themes_returns_doc_counts(fake_data_dir):
    themes = {t.name: t.doc_count for t in docs_module.list_themes()}
    assert themes["agent-protocols"] == 1
    assert themes["claude-code"] == 1


def test_list_docs_all(fake_data_dir):
    docs = docs_module.list_docs()
    paths = {d.path for d in docs}
    assert "agent-protocols/mcp-overview.md" in paths
    assert "claude-code/hooks.md" in paths


def test_list_docs_by_theme(fake_data_dir):
    docs = docs_module.list_docs(theme="claude-code")
    assert all(d.theme == "claude-code" for d in docs)
    assert len(docs) == 1


def test_get_doc_returns_full_content(fake_data_dir):
    content = docs_module.get_doc("agent-protocols/mcp-overview.md")
    assert "MCP Overview" in content
    assert "Primitives" in content


def test_get_doc_missing_raises(fake_data_dir):
    with pytest.raises(FileNotFoundError):
        docs_module.get_doc("nope/missing.md")


def test_get_section_returns_just_section(fake_data_dir):
    s = docs_module.get_section("agent-protocols/mcp-overview.md", "Primitives")
    assert "Primitives" in s
    assert "Resources, Prompts, Tools, Sampling" in s
    assert "Intro" not in s


def test_get_section_unknown_heading_raises(fake_data_dir):
    with pytest.raises(KeyError):
        docs_module.get_section("agent-protocols/mcp-overview.md", "NotAHeading")


def test_search_docs_returns_hits(fake_data_dir):
    hits = docs_module.search_docs("MCP")
    assert len(hits) >= 1
    assert any("mcp-overview" in h.path for h in hits)


def test_search_docs_with_theme_filter(fake_data_dir):
    hits = docs_module.search_docs("hook", theme="claude-code")
    assert all("claude-code" in h.path for h in hits)
```

- [ ] **Step 2: Run tests, verify red**

```bash
python -m pytest tests/test_docs.py -v
```

Expected: ImportError on `harness_kb.docs`.

- [ ] **Step 3: Implement docs.py**

```python
# tools/harness-kb/src/harness_kb/docs.py
from __future__ import annotations
import re
from dataclasses import dataclass
from pathlib import Path

from harness_kb.manifest import get_data_dir
from harness_kb.search import BM25SearchIndex, SearchHit
from harness_kb.chunking import count_tokens


@dataclass
class DocInfo:
    path: str
    theme: str
    title: str
    size_tokens: int


@dataclass
class ThemeInfo:
    name: str
    doc_count: int


_index_cache: BM25SearchIndex | None = None


def _ai_docs_dir() -> Path:
    return get_data_dir() / "ai_docs"


def _index_dir() -> Path:
    return get_data_dir() / "index"


def _load_index() -> BM25SearchIndex:
    global _index_cache
    if _index_cache is None:
        _index_cache = BM25SearchIndex.load(
            _index_dir() / "bm25_index.pkl",
            _index_dir() / "chunks.json",
        )
    return _index_cache


def list_themes() -> list[ThemeInfo]:
    base = _ai_docs_dir()
    themes: list[ThemeInfo] = []
    for entry in sorted(base.iterdir()):
        if entry.is_dir():
            count = sum(1 for _ in entry.rglob("*.md"))
            themes.append(ThemeInfo(name=entry.name, doc_count=count))
    return themes


def list_docs(theme: str | None = None) -> list[DocInfo]:
    base = _ai_docs_dir()
    out: list[DocInfo] = []
    pattern = f"{theme}/**/*.md" if theme else "**/*.md"
    for p in sorted(base.glob(pattern)):
        if not p.is_file():
            continue
        rel = p.relative_to(base).as_posix()
        if "/" not in rel:
            continue  # skip top-level README
        parts = rel.split("/", 1)
        out.append(DocInfo(
            path=rel,
            theme=parts[0],
            title=_extract_title(p.read_text()),
            size_tokens=count_tokens(p.read_text()),
        ))
    return out


def _extract_title(text: str) -> str:
    m = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def get_doc(path: str) -> str:
    full = _ai_docs_dir() / path
    if not full.exists():
        raise FileNotFoundError(f"doc not found: {path}")
    return full.read_text()


def get_section(path: str, heading: str) -> str:
    text = get_doc(path)
    headings = list(re.finditer(r"^(#{2,3})\s+(.+?)\s*$", text, re.MULTILINE))
    for i, m in enumerate(headings):
        if m.group(2).strip() == heading:
            start = m.start()
            end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
            return text[start:end].strip()
    raise KeyError(f"heading not found: {heading} in {path}")


def search_docs(query: str, limit: int = 10, theme: str | None = None) -> list[SearchHit]:
    idx = _load_index()
    path_filter = f"ai_docs/{theme}/" if theme else "ai_docs/"
    return idx.search(query, limit=limit, path_filter=path_filter)
```

- [ ] **Step 4: Run tests, verify green**

```bash
python -m pytest tests/test_docs.py -v
```

Expected: 10 passed.

- [ ] **Step 5: Commit**

```bash
cd /home/rodrigo/Workspace/ai-study-library
rtk git add tools/harness-kb/src/harness_kb/docs.py tools/harness-kb/tests/test_docs.py
rtk git commit -m "feat(harness-kb): docs retrieval (list/get/section/search/themes)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: graph.py

**Goal:** Read `data/graph/graph.json` (NetworkX-style with `nodes` and `links`). Provide path / explain / find / community / keyword query.

**Files:**

- Create: `tools/harness-kb/src/harness_kb/graph.py`
- Create: `tools/harness-kb/tests/test_graph.py`

- [ ] **Step 1: Write the failing tests**

```python
# tools/harness-kb/tests/test_graph.py
import json
from pathlib import Path
import pytest

from harness_kb import graph as graph_module
from harness_kb.graph import GraphNode


@pytest.fixture
def fake_graph(tmp_path: Path, monkeypatch) -> Path:
    graph_dir = tmp_path / "graph"
    graph_dir.mkdir()
    payload = {
        "directed": False,
        "graph": {},
        "multigraph": False,
        "nodes": [
            {"id": "smart_zone", "label": "Smart Zone", "community": "Context"},
            {"id": "context_rot", "label": "Context Rot", "community": "Context"},
            {"id": "subagent", "label": "Subagent as Context Firewall", "community": "Agents"},
            {"id": "skills", "label": "Agent Skills Standard", "community": "Skills"},
        ],
        "links": [
            {"source": "smart_zone", "target": "context_rot", "edge_type": "related", "weight": 1.0},
            {"source": "subagent", "target": "smart_zone", "edge_type": "supports", "weight": 0.8},
        ],
        "hyperedges": [],
    }
    (graph_dir / "graph.json").write_text(json.dumps(payload))
    monkeypatch.setattr(graph_module, "get_data_dir", lambda: tmp_path)
    graph_module._graph_cache = None
    return tmp_path


def test_keyword_query_substring_case_insensitive(fake_graph):
    results = graph_module.keyword_query("smart")
    labels = [r.label for r in results]
    assert "Smart Zone" in labels


def test_keyword_query_no_match(fake_graph):
    assert graph_module.keyword_query("nothingmatchesthis") == []


def test_explain_returns_node_and_neighbors(fake_graph):
    out = graph_module.explain("Smart Zone")
    assert out["node"]["label"] == "Smart Zone"
    neighbor_labels = {n["label"] for n in out["neighbors"]}
    assert "Context Rot" in neighbor_labels
    assert "Subagent as Context Firewall" in neighbor_labels


def test_explain_unknown_node_raises(fake_graph):
    with pytest.raises(KeyError):
        graph_module.explain("Not A Real Node")


def test_shortest_path_finds_path(fake_graph):
    path = graph_module.shortest_path("Subagent as Context Firewall", "Context Rot")
    assert path[0] == "Subagent as Context Firewall"
    assert path[-1] == "Context Rot"
    assert "Smart Zone" in path


def test_shortest_path_no_path_raises(fake_graph):
    with pytest.raises(ValueError):
        graph_module.shortest_path("Smart Zone", "Agent Skills Standard")


def test_find_nodes_regex(fake_graph):
    results = graph_module.find_nodes(r"^Smart")
    labels = [r.label for r in results]
    assert "Smart Zone" in labels
    assert "Context Rot" not in labels


def test_community_nodes(fake_graph):
    results = graph_module.community_nodes("Context")
    labels = {r.label for r in results}
    assert labels == {"Smart Zone", "Context Rot"}


def test_community_unknown_returns_empty(fake_graph):
    assert graph_module.community_nodes("nope") == []
```

- [ ] **Step 2: Run tests, verify red**

```bash
python -m pytest tests/test_graph.py -v
```

Expected: ImportError on `harness_kb.graph`.

- [ ] **Step 3: Implement graph.py**

```python
# tools/harness-kb/src/harness_kb/graph.py
from __future__ import annotations
import json
import re
from dataclasses import dataclass
from pathlib import Path

import networkx as nx

from harness_kb.manifest import get_data_dir


@dataclass
class GraphNode:
    label: str
    id: str
    community: str | None


@dataclass
class GraphNeighbor:
    label: str
    edge_type: str
    weight: float


_graph_cache: tuple[nx.Graph, dict[str, str]] | None = None


def _load_graph() -> tuple[nx.Graph, dict[str, str]]:
    """Return (graph, label_to_id_map). Graph uses node IDs."""
    global _graph_cache
    if _graph_cache is not None:
        return _graph_cache
    payload = json.loads((get_data_dir() / "graph" / "graph.json").read_text())
    g = nx.Graph()
    label_to_id: dict[str, str] = {}
    for node in payload.get("nodes", []):
        nid = node["id"]
        g.add_node(nid, label=node.get("label", nid), community=node.get("community"))
        label_to_id[node.get("label", nid)] = nid
    for link in payload.get("links", []):
        g.add_edge(
            link["source"], link["target"],
            edge_type=link.get("edge_type", ""),
            weight=float(link.get("weight", 1.0)),
        )
    _graph_cache = (g, label_to_id)
    return _graph_cache


def _id_for_label(label: str) -> str:
    _, l2id = _load_graph()
    if label not in l2id:
        raise KeyError(f"node label not found: {label}")
    return l2id[label]


def _node_to_dataclass(g: nx.Graph, nid: str) -> GraphNode:
    data = g.nodes[nid]
    return GraphNode(label=data.get("label", nid), id=nid, community=data.get("community"))


def keyword_query(text: str) -> list[GraphNode]:
    g, _ = _load_graph()
    needle = text.lower()
    out: list[GraphNode] = []
    for nid, data in g.nodes(data=True):
        if needle in data.get("label", "").lower():
            out.append(_node_to_dataclass(g, nid))
    return out


def explain(label: str) -> dict:
    g, _ = _load_graph()
    nid = _id_for_label(label)
    node = _node_to_dataclass(g, nid)
    neighbors: list[dict] = []
    for nbr_id in g.neighbors(nid):
        edge = g[nid][nbr_id]
        neighbors.append({
            "label": g.nodes[nbr_id].get("label", nbr_id),
            "id": nbr_id,
            "edge_type": edge.get("edge_type", ""),
            "weight": float(edge.get("weight", 1.0)),
        })
    return {"node": {"label": node.label, "id": node.id, "community": node.community}, "neighbors": neighbors}


def shortest_path(from_label: str, to_label: str) -> list[str]:
    g, _ = _load_graph()
    src = _id_for_label(from_label)
    dst = _id_for_label(to_label)
    try:
        ids = nx.shortest_path(g, src, dst)
    except nx.NetworkXNoPath:
        raise ValueError(f"no path between {from_label!r} and {to_label!r}")
    return [g.nodes[nid].get("label", nid) for nid in ids]


def find_nodes(pattern: str) -> list[GraphNode]:
    g, _ = _load_graph()
    rx = re.compile(pattern)
    return [_node_to_dataclass(g, nid) for nid, data in g.nodes(data=True)
            if rx.search(data.get("label", ""))]


def community_nodes(name: str) -> list[GraphNode]:
    g, _ = _load_graph()
    return [_node_to_dataclass(g, nid) for nid, data in g.nodes(data=True)
            if data.get("community") == name]
```

- [ ] **Step 4: Run tests, verify green**

```bash
python -m pytest tests/test_graph.py -v
```

Expected: 9 passed.

- [ ] **Step 5: Commit**

```bash
cd /home/rodrigo/Workspace/ai-study-library
rtk git add tools/harness-kb/src/harness_kb/graph.py tools/harness-kb/tests/test_graph.py
rtk git commit -m "feat(harness-kb): graph queries (path/explain/find/community/keyword)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: wiki.py

**Goal:** List + get wiki pages from `data/wiki/`. Page name = filename without `.md`, URL-decoded.

**Files:**

- Create: `tools/harness-kb/src/harness_kb/wiki.py`
- Create: `tools/harness-kb/tests/test_wiki.py`

- [ ] **Step 1: Write the failing tests**

```python
# tools/harness-kb/tests/test_wiki.py
from pathlib import Path
import pytest
from harness_kb import wiki as wiki_module


@pytest.fixture
def fake_wiki(tmp_path: Path, monkeypatch) -> Path:
    wiki_dir = tmp_path / "wiki"
    wiki_dir.mkdir()
    (wiki_dir / "index.md").write_text("# Index\n\nList of pages.")
    (wiki_dir / "Smart_Zone.md").write_text("# Smart Zone\n\nContext threshold.")
    (wiki_dir / "MCP_Runtime.md").write_text("# MCP Runtime\n\nServer + transport.")
    monkeypatch.setattr(wiki_module, "get_data_dir", lambda: tmp_path)
    return tmp_path


def test_list_wiki_pages(fake_wiki):
    pages = wiki_module.list_wiki_pages()
    assert "index" in pages
    assert "Smart_Zone" in pages
    assert "MCP_Runtime" in pages


def test_get_wiki_page_returns_content(fake_wiki):
    content = wiki_module.get_wiki_page("Smart_Zone")
    assert "Smart Zone" in content
    assert "Context threshold" in content


def test_get_wiki_page_missing_raises(fake_wiki):
    with pytest.raises(FileNotFoundError):
        wiki_module.get_wiki_page("NotAPage")
```

- [ ] **Step 2: Run tests, verify red**

```bash
python -m pytest tests/test_wiki.py -v
```

Expected: ImportError on `harness_kb.wiki`.

- [ ] **Step 3: Implement wiki.py**

```python
# tools/harness-kb/src/harness_kb/wiki.py
from __future__ import annotations
from pathlib import Path
from harness_kb.manifest import get_data_dir


def _wiki_dir() -> Path:
    return get_data_dir() / "wiki"


def list_wiki_pages() -> list[str]:
    return sorted(p.stem for p in _wiki_dir().glob("*.md"))


def get_wiki_page(name: str) -> str:
    p = _wiki_dir() / f"{name}.md"
    if not p.exists():
        raise FileNotFoundError(f"wiki page not found: {name}")
    return p.read_text()
```

- [ ] **Step 4: Run tests, verify green**

```bash
python -m pytest tests/test_wiki.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
cd /home/rodrigo/Workspace/ai-study-library
rtk git add tools/harness-kb/src/harness_kb/wiki.py tools/harness-kb/tests/test_wiki.py
rtk git commit -m "feat(harness-kb): wiki list + get

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: guide.py

**Goal:** Playbook retrieval. `toc()`, `get_section(heading)`, `get_full(confirm)`, `search_guide(query)`.

**Files:**

- Create: `tools/harness-kb/src/harness_kb/guide.py`
- Create: `tools/harness-kb/tests/test_guide.py`

- [ ] **Step 1: Write the failing tests**

```python
# tools/harness-kb/tests/test_guide.py
from pathlib import Path
import pytest

from harness_kb.chunking import Chunk
from harness_kb.search import BM25SearchIndex
from harness_kb import guide as guide_module


@pytest.fixture
def fake_guide(tmp_path: Path, monkeypatch) -> Path:
    guide_dir = tmp_path / "guide"
    guide_dir.mkdir()
    text = (
        "# Harness Engineering Playbook\n\n"
        "## Part I — Findings\n\n"
        "Findings body.\n\n"
        "### Smart Zone\n\n"
        "Smart-zone content.\n\n"
        "## Part II — Reference\n\n"
        "Reference body.\n"
    )
    (guide_dir / "harness-engineering-playbook.md").write_text(text)

    index_dir = tmp_path / "index"
    index_dir.mkdir()
    chunks = [
        Chunk(path="guide/harness-engineering-playbook.md", heading="Part I — Findings",
              char_start=0, char_end=80, token_count=4, text="Findings body Smart Zone"),
        Chunk(path="guide/harness-engineering-playbook.md", heading="Smart Zone",
              char_start=80, char_end=130, token_count=4, text="Smart-zone content threshold"),
        Chunk(path="guide/harness-engineering-playbook.md", heading="Part II — Reference",
              char_start=130, char_end=200, token_count=4, text="Reference body taxonomy"),
    ]
    idx = BM25SearchIndex.build(chunks)
    idx.save(index_dir / "bm25_index.pkl", index_dir / "chunks.json")

    monkeypatch.setattr(guide_module, "get_data_dir", lambda: tmp_path)
    return tmp_path


def test_toc_returns_h2_and_h3(fake_guide):
    toc = guide_module.toc()
    headings = [s.heading for s in toc]
    assert "Part I — Findings" in headings
    assert "Smart Zone" in headings
    assert "Part II — Reference" in headings
    levels = {s.heading: s.level for s in toc}
    assert levels["Part I — Findings"] == 2
    assert levels["Smart Zone"] == 3


def test_get_section(fake_guide):
    out = guide_module.get_section("Smart Zone")
    assert "Smart-zone content" in out["content"]
    assert out["heading"] == "Smart Zone"
    assert out["token_estimate"] > 0


def test_get_section_unknown_raises(fake_guide):
    with pytest.raises(KeyError):
        guide_module.get_section("Nope")


def test_get_full_without_confirm_returns_warning(fake_guide):
    out = guide_module.get_full(confirm=False)
    assert "warning" in out
    assert "toc" in out
    assert out["token_estimate"] > 0
    assert "content" not in out


def test_get_full_with_confirm_returns_content(fake_guide):
    out = guide_module.get_full(confirm=True)
    assert "content" in out
    assert "Harness Engineering Playbook" in out["content"]


def test_search_guide_returns_hits(fake_guide):
    hits = guide_module.search_guide("smart")
    assert len(hits) >= 1
    assert any("smart" in h.snippet.lower() for h in hits)
```

- [ ] **Step 2: Run tests, verify red**

```bash
python -m pytest tests/test_guide.py -v
```

Expected: ImportError on `harness_kb.guide`.

- [ ] **Step 3: Implement guide.py**

```python
# tools/harness-kb/src/harness_kb/guide.py
from __future__ import annotations
import re
from dataclasses import dataclass
from pathlib import Path

from harness_kb.manifest import get_data_dir
from harness_kb.search import BM25SearchIndex, SearchHit
from harness_kb.chunking import count_tokens


@dataclass
class GuideSection:
    level: int
    heading: str
    anchor: str


_PLAYBOOK_FILENAME = "harness-engineering-playbook.md"
_index_cache: BM25SearchIndex | None = None


def _guide_path() -> Path:
    return get_data_dir() / "guide" / _PLAYBOOK_FILENAME


def _index_dir() -> Path:
    return get_data_dir() / "index"


def _slugify(heading: str) -> str:
    s = heading.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", "-", s.strip())
    return s


def toc() -> list[GuideSection]:
    text = _guide_path().read_text()
    out: list[GuideSection] = []
    for m in re.finditer(r"^(#{2,3})\s+(.+?)\s*$", text, re.MULTILINE):
        level = len(m.group(1))
        h = m.group(2).strip()
        out.append(GuideSection(level=level, heading=h, anchor=_slugify(h)))
    return out


def get_section(heading: str) -> dict:
    text = _guide_path().read_text()
    matches = list(re.finditer(r"^(#{2,3})\s+(.+?)\s*$", text, re.MULTILINE))
    for i, m in enumerate(matches):
        if m.group(2).strip() == heading:
            start = m.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            content = text[start:end].strip()
            return {
                "heading": heading,
                "content": content,
                "token_estimate": count_tokens(content),
            }
    raise KeyError(f"heading not found in playbook: {heading}")


def get_full(confirm: bool) -> dict:
    text = _guide_path().read_text()
    if not confirm:
        return {
            "warning": (
                "Loading the full playbook costs ~30K tokens. "
                "Prefer `harness-kb guide toc` or `harness-kb guide section <heading>`."
            ),
            "toc": [
                {"level": s.level, "heading": s.heading, "anchor": s.anchor}
                for s in toc()
            ],
            "token_estimate": count_tokens(text),
        }
    return {"content": text, "token_estimate": count_tokens(text)}


def _load_index() -> BM25SearchIndex:
    global _index_cache
    if _index_cache is None:
        _index_cache = BM25SearchIndex.load(
            _index_dir() / "bm25_index.pkl",
            _index_dir() / "chunks.json",
        )
    return _index_cache


def search_guide(query: str, limit: int = 10) -> list[SearchHit]:
    return _load_index().search(query, limit=limit, path_filter="guide/")
```

- [ ] **Step 4: Run tests, verify green**

```bash
python -m pytest tests/test_guide.py -v
```

Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
cd /home/rodrigo/Workspace/ai-study-library
rtk git add tools/harness-kb/src/harness_kb/guide.py tools/harness-kb/tests/test_guide.py
rtk git commit -m "feat(harness-kb): playbook retrieval (toc/section/get-with-confirm/search)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 8: init.py (CLAUDE.md injection)

**Goal:** Render the injection block, inject into a project's CLAUDE.md (idempotent), uninject. Markers: `<!-- harness-kb v{version} BEGIN -->` and `<!-- harness-kb v{version} END -->`. Match BEGIN/END regardless of version string for replacement.

**Files:**

- Create: `tools/harness-kb/src/harness_kb/init.py`
- Create: `tools/harness-kb/tests/test_init.py`

- [ ] **Step 1: Write the failing tests**

```python
# tools/harness-kb/tests/test_init.py
from pathlib import Path
import pytest
from harness_kb.init import render_block, inject, uninject, _BEGIN_RE, _END_RE


def test_render_block_includes_version():
    block = render_block("0.1.0")
    assert "<!-- harness-kb v0.1.0 BEGIN -->" in block
    assert "<!-- harness-kb v0.1.0 END -->" in block
    assert "Harness Knowledge Base" in block
    assert "harness-kb themes" in block
    assert "harness-kb guide toc" in block


def test_inject_creates_file_when_absent(tmp_path: Path):
    project = tmp_path
    out = inject(project, version="0.1.0")
    md = (project / "CLAUDE.md").read_text()
    assert "<!-- harness-kb v0.1.0 BEGIN -->" in md
    assert "created" in out.lower()


def test_inject_appends_to_existing_no_marker(tmp_path: Path):
    project = tmp_path
    (project / "CLAUDE.md").write_text("# My Project\n\nExisting content.")
    inject(project, version="0.1.0")
    md = (project / "CLAUDE.md").read_text()
    assert md.startswith("# My Project")
    assert "Existing content." in md
    assert "<!-- harness-kb v0.1.0 BEGIN -->" in md


def test_inject_idempotent_replaces_existing_block(tmp_path: Path):
    project = tmp_path
    inject(project, version="0.1.0")
    first = (project / "CLAUDE.md").read_text()
    inject(project, version="0.1.0")
    second = (project / "CLAUDE.md").read_text()
    assert first == second


def test_inject_replaces_old_version_block(tmp_path: Path):
    project = tmp_path
    inject(project, version="0.1.0")
    inject(project, version="0.2.0")
    md = (project / "CLAUDE.md").read_text()
    assert "<!-- harness-kb v0.2.0 BEGIN -->" in md
    assert "<!-- harness-kb v0.1.0 BEGIN -->" not in md


def test_inject_dry_run_does_not_write(tmp_path: Path):
    project = tmp_path
    inject(project, version="0.1.0", dry_run=True)
    assert not (project / "CLAUDE.md").exists()


def test_inject_dry_run_returns_preview_text(tmp_path: Path):
    project = tmp_path
    out = inject(project, version="0.1.0", dry_run=True)
    assert "<!-- harness-kb v0.1.0 BEGIN -->" in out


def test_inject_unbalanced_markers_aborts(tmp_path: Path):
    project = tmp_path
    (project / "CLAUDE.md").write_text(
        "# Proj\n\n<!-- harness-kb v0.1.0 BEGIN -->\nstuff but no end marker"
    )
    with pytest.raises(RuntimeError):
        inject(project, version="0.2.0")


def test_uninject_removes_block(tmp_path: Path):
    project = tmp_path
    (project / "CLAUDE.md").write_text("# Proj\n\nKeep this.")
    inject(project, version="0.1.0")
    uninject(project)
    md = (project / "CLAUDE.md").read_text()
    assert "<!-- harness-kb" not in md
    assert "Keep this." in md


def test_uninject_no_marker_is_noop(tmp_path: Path):
    project = tmp_path
    (project / "CLAUDE.md").write_text("# Proj\n\nNo block here.")
    out = uninject(project)
    md = (project / "CLAUDE.md").read_text()
    assert "No block here." in md
    assert "no harness-kb block" in out.lower() or "noop" in out.lower()
```

- [ ] **Step 2: Run tests, verify red**

```bash
python -m pytest tests/test_init.py -v
```

Expected: ImportError on `harness_kb.init`.

- [ ] **Step 3: Implement init.py**

```python
# tools/harness-kb/src/harness_kb/init.py
from __future__ import annotations
import re
from pathlib import Path

_BEGIN_RE = re.compile(r"<!-- harness-kb v[^ ]+ BEGIN -->")
_END_RE = re.compile(r"<!-- harness-kb v[^ ]+ END -->")

_BODY_TEMPLATE = """<!-- harness-kb v{version} BEGIN -->
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
"""


def render_block(version: str) -> str:
    return _BODY_TEMPLATE.format(version=version)


def _find_block_span(text: str) -> tuple[int, int] | None:
    begin = _BEGIN_RE.search(text)
    end = _END_RE.search(text)
    if not begin and not end:
        return None
    if bool(begin) != bool(end):
        raise RuntimeError(
            "CLAUDE.md has unbalanced harness-kb markers; aborting to avoid corruption"
        )
    return (begin.start(), end.end())


def inject(project: Path, version: str, dry_run: bool = False) -> str:
    block = render_block(version)
    md_path = project / "CLAUDE.md"

    if not md_path.exists():
        if dry_run:
            return f"would create {md_path} with block:\n{block}"
        md_path.write_text(block)
        return f"created {md_path}"

    existing = md_path.read_text()
    span = _find_block_span(existing)

    if span is not None:
        new_content = existing[: span[0]] + block + existing[span[1]:]
        new_content = new_content.rstrip() + "\n"
    else:
        # ensure trailing newline, blank line, then append
        existing = existing.rstrip() + "\n"
        new_content = existing + "\n" + block

    if dry_run:
        return new_content

    md_path.write_text(new_content)
    return f"updated {md_path}"


def uninject(project: Path) -> str:
    md_path = project / "CLAUDE.md"
    if not md_path.exists():
        return "noop: no CLAUDE.md"
    existing = md_path.read_text()
    span = _find_block_span(existing)
    if span is None:
        return "noop: no harness-kb block found"
    new_content = existing[: span[0]].rstrip() + "\n" + existing[span[1]:].lstrip()
    md_path.write_text(new_content.rstrip() + "\n")
    return f"removed harness-kb block from {md_path}"
```

- [ ] **Step 4: Run tests, verify green**

```bash
python -m pytest tests/test_init.py -v
```

Expected: 10 passed.

- [ ] **Step 5: Commit**

```bash
cd /home/rodrigo/Workspace/ai-study-library
rtk git add tools/harness-kb/src/harness_kb/init.py tools/harness-kb/tests/test_init.py
rtk git commit -m "feat(harness-kb): CLAUDE.md injection (idempotent, dry-run, uninject)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 9: cli.py (Click)

**Goal:** Click command group with all subcommands (themes, docs list/get/section/search, wiki list/get, graph query/explain/path/find/community, guide toc/section/search/full, init/uninit, --mcp, --version).

**Files:**

- Create: `tools/harness-kb/src/harness_kb/cli.py`
- Create: `tools/harness-kb/tests/test_cli.py`

- [ ] **Step 1: Write the failing tests**

```python
# tools/harness-kb/tests/test_cli.py
from click.testing import CliRunner
from harness_kb.cli import main


def test_version_flag():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "harness-kb" in result.output
    assert "0.1.0" in result.output


def test_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "themes" in result.output
    assert "docs" in result.output
    assert "graph" in result.output
    assert "wiki" in result.output
    assert "guide" in result.output
    assert "init" in result.output


def test_themes_subcommand_help():
    runner = CliRunner()
    result = runner.invoke(main, ["themes", "--help"])
    assert result.exit_code == 0


def test_docs_search_help():
    runner = CliRunner()
    result = runner.invoke(main, ["docs", "search", "--help"])
    assert result.exit_code == 0
    assert "--limit" in result.output
    assert "--theme" in result.output


def test_init_dry_run(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["init", "--project", str(tmp_path), "--dry-run"])
    assert result.exit_code == 0
    assert "harness-kb" in result.output
    assert not (tmp_path / "CLAUDE.md").exists()


def test_uninit_noop_on_empty(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["uninit", "--project", str(tmp_path)])
    assert result.exit_code == 0
    assert "noop" in result.output.lower()


def test_mcp_flag_recognized(monkeypatch):
    """--mcp dispatches to the MCP runner; we check it doesn't crash on parse."""
    runner = CliRunner()
    called = {"count": 0}

    def fake_run_mcp():
        called["count"] += 1

    import harness_kb.cli as cli_mod
    monkeypatch.setattr(cli_mod, "_run_mcp_server", fake_run_mcp)
    result = runner.invoke(main, ["--mcp"])
    assert called["count"] == 1
    assert result.exit_code == 0
```

- [ ] **Step 2: Run tests, verify red**

```bash
python -m pytest tests/test_cli.py -v
```

Expected: ImportError on `harness_kb.cli`.

- [ ] **Step 3: Implement cli.py**

```python
# tools/harness-kb/src/harness_kb/cli.py
from __future__ import annotations
import json
import sys
from pathlib import Path

import click

from harness_kb import __version__, docs, graph, wiki, guide, init as init_module


def _print_json(payload) -> None:
    click.echo(json.dumps(payload, indent=2, ensure_ascii=False))


def _run_mcp_server() -> None:
    from harness_kb.mcp import run_stdio_server
    run_stdio_server()


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version and bundled data SHA.")
@click.option("--mcp", is_flag=True, help="Launch stdio MCP server.")
@click.pass_context
def main(ctx: click.Context, version: bool, mcp: bool) -> None:
    """harness-kb — portable knowledge base of agent/harness/context-engineering reference material."""
    if version:
        try:
            from harness_kb.manifest import load_manifest
            m = load_manifest()
            click.echo(f"harness-kb {__version__} (data=ai-study-library@{m.source_commit_sha[:7]}, built {m.build_date})")
        except FileNotFoundError:
            click.echo(f"harness-kb {__version__} (data not yet bundled)")
        return
    if mcp:
        _run_mcp_server()
        return
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command()
def themes() -> None:
    """List ai/docs themes with doc counts."""
    payload = [{"name": t.name, "doc_count": t.doc_count} for t in docs.list_themes()]
    _print_json(payload)


@main.group()
def docs_cmd():
    """Document retrieval commands."""


main.add_command(docs_cmd, name="docs")


@docs_cmd.command("list")
@click.option("--theme", default=None, help="Filter by theme name.")
def docs_list_cmd(theme: str | None) -> None:
    payload = [{"path": d.path, "theme": d.theme, "title": d.title, "size_tokens": d.size_tokens}
               for d in docs.list_docs(theme=theme)]
    _print_json(payload)


@docs_cmd.command("get")
@click.argument("path")
def docs_get_cmd(path: str) -> None:
    click.echo(docs.get_doc(path))


@docs_cmd.command("section")
@click.argument("path")
@click.argument("heading")
def docs_section_cmd(path: str, heading: str) -> None:
    click.echo(docs.get_section(path, heading))


@docs_cmd.command("search")
@click.argument("query")
@click.option("--limit", default=10, type=int)
@click.option("--theme", default=None)
def docs_search_cmd(query: str, limit: int, theme: str | None) -> None:
    hits = docs.search_docs(query, limit=limit, theme=theme)
    payload = [{"path": h.path, "heading": h.heading, "score": h.score, "snippet": h.snippet}
               for h in hits]
    _print_json(payload)


@main.group()
def wiki_cmd():
    """Wiki retrieval commands."""


main.add_command(wiki_cmd, name="wiki")


@wiki_cmd.command("list")
def wiki_list_cmd() -> None:
    _print_json(wiki.list_wiki_pages())


@wiki_cmd.command("get")
@click.argument("name")
def wiki_get_cmd(name: str) -> None:
    click.echo(wiki.get_wiki_page(name))


@main.group()
def graph_cmd():
    """Graph query commands."""


main.add_command(graph_cmd, name="graph")


@graph_cmd.command("query")
@click.argument("text")
def graph_query_cmd(text: str) -> None:
    payload = [{"label": n.label, "id": n.id, "community": n.community}
               for n in graph.keyword_query(text)]
    _print_json(payload)


@graph_cmd.command("explain")
@click.argument("label")
def graph_explain_cmd(label: str) -> None:
    _print_json(graph.explain(label))


@graph_cmd.command("path")
@click.argument("from_label")
@click.argument("to_label")
def graph_path_cmd(from_label: str, to_label: str) -> None:
    p = graph.shortest_path(from_label, to_label)
    _print_json({"path": p, "length": len(p) - 1})


@graph_cmd.command("find")
@click.argument("pattern")
def graph_find_cmd(pattern: str) -> None:
    payload = [{"label": n.label, "id": n.id, "community": n.community}
               for n in graph.find_nodes(pattern)]
    _print_json(payload)


@graph_cmd.command("community")
@click.argument("name")
def graph_community_cmd(name: str) -> None:
    payload = [{"label": n.label, "id": n.id} for n in graph.community_nodes(name)]
    _print_json(payload)


@main.group(invoke_without_command=True)
@click.option("--confirm", is_flag=True, help="Print the full playbook (~30K tokens).")
@click.pass_context
def guide_cmd(ctx: click.Context, confirm: bool):
    """Playbook retrieval commands."""
    if ctx.invoked_subcommand is None:
        out = guide.get_full(confirm=confirm)
        if "content" in out:
            click.echo(out["content"])
        else:
            _print_json(out)


main.add_command(guide_cmd, name="guide")


@guide_cmd.command("toc")
def guide_toc_cmd() -> None:
    payload = [{"level": s.level, "heading": s.heading, "anchor": s.anchor}
               for s in guide.toc()]
    _print_json(payload)


@guide_cmd.command("section")
@click.argument("heading")
def guide_section_cmd(heading: str) -> None:
    _print_json(guide.get_section(heading))


@guide_cmd.command("search")
@click.argument("query")
@click.option("--limit", default=10, type=int)
def guide_search_cmd(query: str, limit: int) -> None:
    hits = guide.search_guide(query, limit=limit)
    _print_json([{"path": h.path, "heading": h.heading, "score": h.score, "snippet": h.snippet}
                 for h in hits])


@main.command("init")
@click.option("--project", default=".", help="Project directory (default cwd).")
@click.option("--dry-run", is_flag=True, help="Print the change without writing.")
def init_cmd(project: str, dry_run: bool) -> None:
    out = init_module.inject(Path(project), version=__version__, dry_run=dry_run)
    click.echo(out)


@main.command("uninit")
@click.option("--project", default=".", help="Project directory (default cwd).")
def uninit_cmd(project: str) -> None:
    click.echo(init_module.uninject(Path(project)))


@main.command("build", hidden=True)
@click.option("--source", required=True, help="Path to ai-study-library/ checkout.")
@click.option("--out-dir", required=True, help="Output dir for the bundled data (typically src/harness_kb/data).")
@click.option("--version", default=__version__, help="Version string written into manifest.")
@click.option("--no-staleness-check", is_flag=True, help="Skip the graph-staleness check.")
def build_cmd(source: str, out_dir: str, version: str, no_staleness_check: bool) -> None:
    """Maintainer-only: rebuild bundled data from a parent ai-study-library/ checkout."""
    from harness_kb.build.build import build_data
    build_data(
        source=Path(source).resolve(),
        out_dir=Path(out_dir).resolve(),
        version=version,
        no_staleness_check=no_staleness_check,
    )
    click.echo(f"build complete: {out_dir}")
```

Add a corresponding test to `tests/test_cli.py` (Step 1) — this test should appear in the test file alongside the others:

```python
def test_build_subcommand_hidden_from_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert "build" not in result.output  # hidden=True keeps it out of --help


def test_build_subcommand_help_directly():
    runner = CliRunner()
    result = runner.invoke(main, ["build", "--help"])
    assert result.exit_code == 0
    assert "--source" in result.output
    assert "--out-dir" in result.output
```

- [ ] **Step 4: Run tests, verify green**

```bash
python -m pytest tests/test_cli.py -v
```

Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
cd /home/rodrigo/Workspace/ai-study-library
rtk git add tools/harness-kb/src/harness_kb/cli.py tools/harness-kb/tests/test_cli.py
rtk git commit -m "feat(harness-kb): Click CLI with all subcommands

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 10: mcp.py (stdio MCP server)

**Goal:** Stdio MCP server registering all 16 tools. Each tool wraps a function from the retrieval modules. Errors return `{error: "...", detail: "..."}` rather than raise.

**Files:**

- Create: `tools/harness-kb/src/harness_kb/mcp.py`
- Create: `tools/harness-kb/tests/test_mcp.py`

- [ ] **Step 1: Write the failing tests**

```python
# tools/harness-kb/tests/test_mcp.py
import pytest
from harness_kb.mcp import build_server, _tool_handlers, ALL_TOOL_NAMES


def test_all_16_tools_registered():
    assert len(ALL_TOOL_NAMES) == 16
    expected = {
        "harness_kb_themes",
        "harness_kb_docs_list", "harness_kb_docs_get",
        "harness_kb_docs_section", "harness_kb_docs_search",
        "harness_kb_wiki_list", "harness_kb_wiki_get",
        "harness_kb_graph_query", "harness_kb_graph_explain",
        "harness_kb_graph_path", "harness_kb_graph_find",
        "harness_kb_graph_community",
        "harness_kb_guide_toc", "harness_kb_guide_section",
        "harness_kb_guide_get", "harness_kb_guide_search",
    }
    assert set(ALL_TOOL_NAMES) == expected


def test_handler_for_each_tool():
    for name in ALL_TOOL_NAMES:
        assert name in _tool_handlers
        assert callable(_tool_handlers[name])


def test_each_tool_has_real_input_schema():
    from harness_kb.mcp import _TOOL_SCHEMAS
    assert set(_TOOL_SCHEMAS.keys()) == set(ALL_TOOL_NAMES), \
        "tool handlers and schemas must cover the same set of tools"
    for name, (desc, schema) in _TOOL_SCHEMAS.items():
        assert isinstance(desc, str) and desc.strip(), f"missing description for {name}"
        assert schema.get("type") == "object", f"{name} schema must be object"
        assert "additionalProperties" in schema, f"{name} schema must declare additionalProperties"
        assert schema["additionalProperties"] is False, \
            f"{name} schema must not allow additional properties"
        # Tools that take no arguments still have an empty properties dict
        assert "properties" in schema, f"{name} schema must declare properties"


def test_themes_handler(monkeypatch):
    from harness_kb import docs
    class T:
        def __init__(self, n, c): self.name = n; self.doc_count = c
    monkeypatch.setattr(docs, "list_themes", lambda: [T("agent-protocols", 5), T("claude-code", 3)])
    out = _tool_handlers["harness_kb_themes"]({})
    assert out == [{"name": "agent-protocols", "doc_count": 5},
                   {"name": "claude-code", "doc_count": 3}]


def test_docs_get_handler_returns_error_on_missing(monkeypatch):
    from harness_kb import docs
    def boom(p): raise FileNotFoundError(p)
    monkeypatch.setattr(docs, "get_doc", boom)
    out = _tool_handlers["harness_kb_docs_get"]({"path": "nope"})
    assert "error" in out
    assert out["error"] == "not_found"


def test_guide_get_without_confirm_returns_warning(monkeypatch):
    from harness_kb import guide
    monkeypatch.setattr(guide, "get_full", lambda confirm: {"warning": "warn", "toc": [], "token_estimate": 100} if not confirm else {"content": "x"})
    out = _tool_handlers["harness_kb_guide_get"]({"confirm": False})
    assert "warning" in out


def test_build_server_returns_object():
    server = build_server()
    assert server is not None
```

- [ ] **Step 2: Run tests, verify red**

```bash
python -m pytest tests/test_mcp.py -v
```

Expected: ImportError on `harness_kb.mcp`.

- [ ] **Step 3: Implement mcp.py**

```python
# tools/harness-kb/src/harness_kb/mcp.py
from __future__ import annotations
from typing import Any, Callable

from harness_kb import docs, graph, wiki, guide


def _safe(fn: Callable[..., Any], not_found_exceptions=(FileNotFoundError, KeyError)):
    def wrapped(args: dict) -> dict | list:
        try:
            return fn(args)
        except not_found_exceptions as e:
            return {"error": "not_found", "detail": str(e)}
        except ValueError as e:
            return {"error": "invalid_argument", "detail": str(e)}
    return wrapped


def _h_themes(_: dict):
    return [{"name": t.name, "doc_count": t.doc_count} for t in docs.list_themes()]


def _h_docs_list(args: dict):
    return [{"path": d.path, "theme": d.theme, "title": d.title, "size_tokens": d.size_tokens}
            for d in docs.list_docs(theme=args.get("theme"))]


def _h_docs_get(args: dict):
    return {"path": args["path"], "content": docs.get_doc(args["path"])}


def _h_docs_section(args: dict):
    return {"path": args["path"], "heading": args["heading"],
            "content": docs.get_section(args["path"], args["heading"])}


def _h_docs_search(args: dict):
    hits = docs.search_docs(args["query"], limit=args.get("limit", 10), theme=args.get("theme"))
    return [{"path": h.path, "heading": h.heading, "score": h.score, "snippet": h.snippet} for h in hits]


def _h_wiki_list(_: dict):
    return [{"name": n} for n in wiki.list_wiki_pages()]


def _h_wiki_get(args: dict):
    return {"name": args["name"], "content": wiki.get_wiki_page(args["name"])}


def _h_graph_query(args: dict):
    return [{"label": n.label, "id": n.id, "community": n.community}
            for n in graph.keyword_query(args["text"])]


def _h_graph_explain(args: dict):
    return graph.explain(args["label"])


def _h_graph_path(args: dict):
    p = graph.shortest_path(args["from"], args["to"])
    return {"path": p, "length": len(p) - 1}


def _h_graph_find(args: dict):
    return [{"label": n.label, "id": n.id, "community": n.community}
            for n in graph.find_nodes(args["pattern"])]


def _h_graph_community(args: dict):
    return [{"label": n.label, "id": n.id} for n in graph.community_nodes(args["name"])]


def _h_guide_toc(_: dict):
    return [{"level": s.level, "heading": s.heading, "anchor": s.anchor} for s in guide.toc()]


def _h_guide_section(args: dict):
    return guide.get_section(args["heading"])


def _h_guide_get(args: dict):
    return guide.get_full(confirm=bool(args.get("confirm", False)))


def _h_guide_search(args: dict):
    hits = guide.search_guide(args["query"], limit=args.get("limit", 10))
    return [{"path": h.path, "heading": h.heading, "score": h.score, "snippet": h.snippet} for h in hits]


_tool_handlers: dict[str, Callable[[dict], Any]] = {
    "harness_kb_themes":          _safe(_h_themes),
    "harness_kb_docs_list":       _safe(_h_docs_list),
    "harness_kb_docs_get":        _safe(_h_docs_get),
    "harness_kb_docs_section":    _safe(_h_docs_section),
    "harness_kb_docs_search":     _safe(_h_docs_search),
    "harness_kb_wiki_list":       _safe(_h_wiki_list),
    "harness_kb_wiki_get":        _safe(_h_wiki_get),
    "harness_kb_graph_query":     _safe(_h_graph_query),
    "harness_kb_graph_explain":   _safe(_h_graph_explain),
    "harness_kb_graph_path":      _safe(_h_graph_path),
    "harness_kb_graph_find":      _safe(_h_graph_find),
    "harness_kb_graph_community": _safe(_h_graph_community),
    "harness_kb_guide_toc":       _safe(_h_guide_toc),
    "harness_kb_guide_section":   _safe(_h_guide_section),
    "harness_kb_guide_get":       _safe(_h_guide_get),
    "harness_kb_guide_search":    _safe(_h_guide_search),
}

ALL_TOOL_NAMES = list(_tool_handlers.keys())


_TOOL_SCHEMAS: dict[str, tuple[str, dict]] = {
    "harness_kb_themes": (
        "List ai/docs themes with doc counts.",
        {"type": "object", "properties": {}, "additionalProperties": False},
    ),
    "harness_kb_docs_list": (
        "List bundled docs, optionally filtered by theme.",
        {"type": "object", "properties": {"theme": {"type": "string"}}, "additionalProperties": False},
    ),
    "harness_kb_docs_get": (
        "Return the full content of a bundled doc by relative path under ai_docs/.",
        {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"], "additionalProperties": False},
    ),
    "harness_kb_docs_section": (
        "Return one H2/H3 section of a bundled doc by heading.",
        {"type": "object",
         "properties": {"path": {"type": "string"}, "heading": {"type": "string"}},
         "required": ["path", "heading"], "additionalProperties": False},
    ),
    "harness_kb_docs_search": (
        "BM25 search over chunked ai/docs sections; returns ranked hits with snippets.",
        {"type": "object",
         "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "default": 10},
                        "theme": {"type": "string"}},
         "required": ["query"], "additionalProperties": False},
    ),
    "harness_kb_wiki_list": (
        "List names of bundled wiki pages.",
        {"type": "object", "properties": {}, "additionalProperties": False},
    ),
    "harness_kb_wiki_get": (
        "Return the content of one wiki page by name (basename without .md).",
        {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"], "additionalProperties": False},
    ),
    "harness_kb_graph_query": (
        "Case-insensitive substring search over node labels in the bundled graph.",
        {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"], "additionalProperties": False},
    ),
    "harness_kb_graph_explain": (
        "Return a node and its 1-hop neighbors.",
        {"type": "object", "properties": {"label": {"type": "string"}}, "required": ["label"], "additionalProperties": False},
    ),
    "harness_kb_graph_path": (
        "Return the shortest path between two nodes by label.",
        {"type": "object",
         "properties": {"from": {"type": "string"}, "to": {"type": "string"}},
         "required": ["from", "to"], "additionalProperties": False},
    ),
    "harness_kb_graph_find": (
        "Regex search over node labels.",
        {"type": "object", "properties": {"pattern": {"type": "string"}}, "required": ["pattern"], "additionalProperties": False},
    ),
    "harness_kb_graph_community": (
        "Return all nodes in a community by community name.",
        {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"], "additionalProperties": False},
    ),
    "harness_kb_guide_toc": (
        "Return the playbook's H2/H3 outline.",
        {"type": "object", "properties": {}, "additionalProperties": False},
    ),
    "harness_kb_guide_section": (
        "Return one section of the playbook by heading.",
        {"type": "object", "properties": {"heading": {"type": "string"}}, "required": ["heading"], "additionalProperties": False},
    ),
    "harness_kb_guide_get": (
        "Return the full playbook content if confirm=true; otherwise a warning + TOC + token estimate.",
        {"type": "object",
         "properties": {"confirm": {"type": "boolean", "default": False}},
         "additionalProperties": False},
    ),
    "harness_kb_guide_search": (
        "BM25 search restricted to the playbook.",
        {"type": "object",
         "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "default": 10}},
         "required": ["query"], "additionalProperties": False},
    ),
}


def build_server():
    """Construct an MCP Server with all tools registered."""
    from mcp.server import Server
    from mcp.types import Tool, TextContent

    server = Server("harness-kb")

    @server.list_tools()
    async def _list_tools() -> list[Tool]:
        return [
            Tool(name=name, description=desc, inputSchema=schema)
            for name, (desc, schema) in _TOOL_SCHEMAS.items()
        ]

    @server.call_tool()
    async def _call_tool(name: str, arguments: dict) -> list[TextContent]:
        import json as _json
        handler = _tool_handlers.get(name)
        if handler is None:
            payload = {"error": "unknown_tool", "detail": name}
        else:
            payload = handler(arguments or {})
        return [TextContent(type="text", text=_json.dumps(payload, ensure_ascii=False))]

    return server


def run_stdio_server() -> None:
    import asyncio
    from mcp.server.stdio import stdio_server

    server = build_server()

    async def _main():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())

    asyncio.run(_main())
```

- [ ] **Step 4: Run tests, verify green**

```bash
python -m pytest tests/test_mcp.py -v
```

Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
cd /home/rodrigo/Workspace/ai-study-library
rtk git add tools/harness-kb/src/harness_kb/mcp.py tools/harness-kb/tests/test_mcp.py
rtk git commit -m "feat(harness-kb): stdio MCP server with 16 typed tools

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 11: build/adapt_guide.py

**Goal:** Deterministic adaptation of the research doc. Replaces every `/graphify` reference with the corresponding `harness-kb` reference per the table in the spec.

**Files:**

- Create: `tools/harness-kb/src/harness_kb/build/__init__.py` (empty)
- Create: `tools/harness-kb/src/harness_kb/build/adapt_guide.py`
- Create: `tools/harness-kb/tests/test_adapt_guide.py`

- [ ] **Step 1: Write the failing tests**

```python
# tools/harness-kb/tests/test_adapt_guide.py
import pytest
from harness_kb.build.adapt_guide import adapt


def test_replace_graphify_query():
    src = '/graphify query "smart zone"'
    out = adapt(src)
    assert "/graphify" not in out
    assert 'harness-kb graph query "smart zone"' in out


def test_replace_graphify_path():
    src = '/graphify path "Node A" "Node B"'
    out = adapt(src)
    assert 'harness-kb graph path "Node A" "Node B"' in out


def test_replace_graphify_explain():
    src = '/graphify explain "Smart Zone"'
    out = adapt(src)
    assert 'harness-kb graph explain "Smart Zone"' in out


def test_replace_graphify_mcp():
    src = "see `/graphify --mcp` for integration"
    out = adapt(src)
    assert "/graphify" not in out
    assert "harness-kb --mcp" in out


def test_replace_graphify_out_path_to_graph_command():
    src = "Inspect `graphify-out/graph.json` to see nodes."
    out = adapt(src)
    assert "graphify-out/graph.json" not in out
    assert "harness-kb graph" in out


def test_replace_graphify_out_wiki_link():
    src = "See `graphify-out/wiki/Smart_Zone.md` for the page."
    out = adapt(src)
    assert "graphify-out/wiki" not in out
    assert "harness-kb wiki get Smart_Zone" in out


def test_ai_docs_paths_unchanged():
    src = "See `ai/docs/agent-protocols/mcp.md` for details."
    out = adapt(src)
    assert "ai/docs/agent-protocols/mcp.md" in out


def test_post_adapt_no_graphify_residual():
    src = (
        "Run /graphify query \"x\". Then /graphify path \"A\" \"B\". "
        "Inspect graphify-out/graph.json. See graphify-out/wiki/Index.md. "
        "Use /graphify --mcp."
    )
    out = adapt(src)
    assert "/graphify" not in out
    assert "graphify-out/" not in out
    assert "harness-kb" in out
```

- [ ] **Step 2: Run tests, verify red**

```bash
python -m pytest tests/test_adapt_guide.py -v
```

Expected: ImportError on `harness_kb.build.adapt_guide`.

- [ ] **Step 3: Implement adapt_guide.py**

```python
# tools/harness-kb/src/harness_kb/build/adapt_guide.py
from __future__ import annotations
import re

# Each rule: (regex, replacement). Order matters — most specific first.
_RULES: list[tuple[re.Pattern, str]] = [
    (re.compile(r"/graphify\s+query\s+"), r"harness-kb graph query "),
    (re.compile(r"/graphify\s+path\s+"), r"harness-kb graph path "),
    (re.compile(r"/graphify\s+explain\s+"), r"harness-kb graph explain "),
    (re.compile(r"/graphify\s+--mcp"), r"harness-kb --mcp"),
    # graphify-out/wiki/<Name>.md → harness-kb wiki get <Name>
    (re.compile(r"`?graphify-out/wiki/([A-Za-z0-9_\-+]+?)\.md`?"), r"`harness-kb wiki get \1`"),
    # graphify-out/graph.json (or graphify-out/) → harness-kb graph
    (re.compile(r"`?graphify-out/graph\.json`?"), r"`harness-kb graph` (bundled graph)"),
    (re.compile(r"`?graphify-out/`?(?=[\s.,)])"), r"`harness-kb graph + harness-kb wiki`"),
    # generic /graphify mention not caught above (fail-safe)
    (re.compile(r"/graphify\b"), r"harness-kb"),
]


def adapt(text: str) -> str:
    out = text
    for rx, repl in _RULES:
        out = rx.sub(repl, out)
    return out
```

- [ ] **Step 4: Run tests, verify green**

```bash
python -m pytest tests/test_adapt_guide.py -v
```

Expected: 8 passed.

- [ ] **Step 5: Commit**

```bash
cd /home/rodrigo/Workspace/ai-study-library
rtk git add tools/harness-kb/src/harness_kb/build/ tools/harness-kb/tests/test_adapt_guide.py
rtk git commit -m "feat(harness-kb): deterministic /graphify→harness-kb adaptation rules

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 12: build/build.py (full pipeline)

**Goal:** End-to-end build pipeline: validate source, copy ai_docs/graph/wiki, adapt + copy playbook, build BM25 index, write manifest, post-validate. Tested with `tests/fixtures/mini_source/`.

**Files:**

- Create: `tools/harness-kb/src/harness_kb/build/build.py`
- Create: `tools/harness-kb/tests/test_build.py`
- Create: `tools/harness-kb/tests/fixtures/mini_source/` (built by the test fixture)

- [ ] **Step 1: Write the failing tests**

```python
# tools/harness-kb/tests/test_build.py
import json
from pathlib import Path
import pytest
from harness_kb.build.build import build_data, BuildError


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


@pytest.fixture
def mini_source(tmp_path: Path) -> Path:
    src = tmp_path / "ai-study-library"
    _write(src / "ai" / "docs" / "agent-protocols" / "mcp.md",
           "# MCP\n\n## Intro\n\nModel Context Protocol.")
    _write(src / "ai" / "docs" / "claude-code" / "hooks.md",
           "# Hooks\n\n## Stop hook\n\nFires after turn.")
    # all 17 themes need to exist for validation; create stubs
    for theme in [
        "agent-protocols", "agentic-engineering", "analysis", "claude", "claude-code",
        "context-engineering", "cursor", "general-llm", "harness-engineering",
        "human-layer-project", "long-context-research", "mcp", "shared",
        "spec-driven-development", "structured-outputs", "tool-calling"
    ]:
        d = src / "ai" / "docs" / theme
        d.mkdir(parents=True, exist_ok=True)
        if not (d / "_stub.md").exists() and not any(d.glob("*.md")):
            _write(d / "_stub.md", f"# {theme}\n\n## Notes\n\nStub.")
    _write(src / "ai" / "docs" / "README.md", "# ai/docs index")

    graph_payload = {
        "directed": False, "graph": {}, "multigraph": False,
        "nodes": [{"id": "a", "label": "Smart Zone", "community": "Context"}],
        "links": [],
        "hyperedges": [],
    }
    _write(src / "graphify-out" / "graph.json", json.dumps(graph_payload))
    _write(src / "graphify-out" / "GRAPH_REPORT.md", "# Graph report")
    _write(src / "graphify-out" / "manifest.json", json.dumps({}))
    _write(src / "graphify-out" / "wiki" / "Smart_Zone.md", "# Smart Zone\n\nThreshold.")

    _write(src / "dev" / "research" / "2026-04-25-harness-engineering-research.md",
           "# Research\n\n## Findings\n\nUse `/graphify query \"x\"` to explore.\n\n## Reference\n\nSee `graphify-out/graph.json`.")
    return src


def test_build_writes_data_files(mini_source: Path, tmp_path: Path):
    out_dir = tmp_path / "out_data"
    build_data(source=mini_source, out_dir=out_dir, version="0.1.0", no_staleness_check=True)

    assert (out_dir / "manifest.json").exists()
    assert (out_dir / "ai_docs" / "agent-protocols" / "mcp.md").exists()
    assert (out_dir / "graph" / "graph.json").exists()
    assert (out_dir / "wiki" / "Smart_Zone.md").exists()
    assert (out_dir / "guide" / "harness-engineering-playbook.md").exists()
    assert (out_dir / "index" / "bm25_index.pkl").exists()
    assert (out_dir / "index" / "chunks.json").exists()


def test_build_adapts_playbook(mini_source: Path, tmp_path: Path):
    out_dir = tmp_path / "out_data"
    build_data(source=mini_source, out_dir=out_dir, version="0.1.0", no_staleness_check=True)
    pb = (out_dir / "guide" / "harness-engineering-playbook.md").read_text()
    assert "/graphify" not in pb
    assert "harness-kb" in pb


def test_build_writes_manifest_with_version_and_themes(mini_source: Path, tmp_path: Path):
    out_dir = tmp_path / "out_data"
    build_data(source=mini_source, out_dir=out_dir, version="0.1.0", no_staleness_check=True)
    m = json.loads((out_dir / "manifest.json").read_text())
    assert m["version"] == "0.1.0"
    assert len(m["themes"]) == 16
    assert "agent-protocols" in m["themes"]


def test_build_aborts_when_themes_missing(mini_source: Path, tmp_path: Path):
    # remove a required theme dir
    import shutil
    shutil.rmtree(mini_source / "ai" / "docs" / "agent-protocols")
    with pytest.raises(BuildError, match="missing themes"):
        build_data(source=mini_source, out_dir=tmp_path / "out_data", version="0.1.0", no_staleness_check=True)


def test_build_aborts_when_graph_stale(mini_source: Path, tmp_path: Path):
    # Make an ai/docs file newer than graphify-out/manifest.json
    import os, time
    docs_file = mini_source / "ai" / "docs" / "agent-protocols" / "mcp.md"
    manifest_file = mini_source / "graphify-out" / "manifest.json"
    older = time.time() - 100
    os.utime(manifest_file, (older, older))
    os.utime(docs_file, (time.time(), time.time()))
    with pytest.raises(BuildError, match="graph stale"):
        build_data(source=mini_source, out_dir=tmp_path / "out_data", version="0.1.0", no_staleness_check=False)
```

- [ ] **Step 2: Run tests, verify red**

```bash
python -m pytest tests/test_build.py -v
```

Expected: ImportError on `harness_kb.build.build`.

- [ ] **Step 3: Implement build.py**

```python
# tools/harness-kb/src/harness_kb/build/build.py
from __future__ import annotations
import datetime as _dt
import json
import shutil
import subprocess
from pathlib import Path

from harness_kb.build.adapt_guide import adapt
from harness_kb.chunking import chunk_markdown
from harness_kb.search import BM25SearchIndex
from harness_kb.manifest import Manifest, save_manifest


REQUIRED_THEMES = [
    "agent-protocols", "agentic-engineering", "analysis", "claude", "claude-code",
    "context-engineering", "cursor", "general-llm", "harness-engineering",
    "human-layer-project", "long-context-research", "mcp", "shared",
    "spec-driven-development", "structured-outputs", "tool-calling",
]
_RESEARCH_DOC_REL = "dev/research/2026-04-25-harness-engineering-research.md"
_PLAYBOOK_FILENAME = "harness-engineering-playbook.md"


class BuildError(Exception):
    pass


def _git_sha(source: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(source), "rev-parse", "HEAD"], text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _validate_source(source: Path) -> None:
    docs_root = source / "ai" / "docs"
    if not docs_root.exists():
        raise BuildError(f"source missing ai/docs/: {source}")
    missing = [t for t in REQUIRED_THEMES if not (docs_root / t).is_dir()]
    if missing:
        raise BuildError(f"missing themes: {missing}")
    if not (source / "graphify-out" / "graph.json").exists():
        raise BuildError("source missing graphify-out/graph.json")
    if not (source / _RESEARCH_DOC_REL).exists():
        raise BuildError(f"source missing research doc at {_RESEARCH_DOC_REL}")


def _check_graph_freshness(source: Path) -> None:
    graphify_manifest = source / "graphify-out" / "manifest.json"
    if not graphify_manifest.exists():
        raise BuildError("graph stale: graphify-out/manifest.json missing — run /graphify update first")
    manifest_mtime = graphify_manifest.stat().st_mtime
    docs_root = source / "ai" / "docs"
    for p in docs_root.rglob("*.md"):
        if p.stat().st_mtime > manifest_mtime:
            raise BuildError(
                f"graph stale: {p.relative_to(source)} is newer than graphify-out/manifest.json. "
                "Run '/graphify update' inside Claude Code from "
                f"{source}, then re-run 'harness-kb build'."
            )


def _stage_data(source: Path, out_dir: Path) -> None:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    # ai_docs
    shutil.copytree(source / "ai" / "docs", out_dir / "ai_docs")
    # graph
    (out_dir / "graph").mkdir()
    shutil.copy(source / "graphify-out" / "graph.json", out_dir / "graph" / "graph.json")
    rep = source / "graphify-out" / "GRAPH_REPORT.md"
    if rep.exists():
        shutil.copy(rep, out_dir / "graph" / "GRAPH_REPORT.md")
    # wiki
    wiki_src = source / "graphify-out" / "wiki"
    if wiki_src.exists():
        shutil.copytree(wiki_src, out_dir / "wiki")
    else:
        (out_dir / "wiki").mkdir()


def _adapt_and_copy_playbook(source: Path, out_dir: Path) -> None:
    src_doc = source / _RESEARCH_DOC_REL
    raw = src_doc.read_text()
    adapted = adapt(raw)
    if "/graphify" in adapted:
        raise BuildError("adaptation failed: residual /graphify references remain in playbook")
    if "harness-kb" not in adapted:
        raise BuildError("adaptation produced playbook with no harness-kb references — check rules")
    guide_dir = out_dir / "guide"
    guide_dir.mkdir(exist_ok=True)
    (guide_dir / _PLAYBOOK_FILENAME).write_text(adapted)


def _build_index(out_dir: Path) -> int:
    chunks = []
    for p in (out_dir / "ai_docs").rglob("*.md"):
        rel = p.relative_to(out_dir).as_posix()  # e.g. "ai_docs/.../foo.md"
        chunks.extend(chunk_markdown(p.read_text(), rel))
    pb = out_dir / "guide" / _PLAYBOOK_FILENAME
    if pb.exists():
        rel = pb.relative_to(out_dir).as_posix()
        chunks.extend(chunk_markdown(pb.read_text(), rel))
    idx = BM25SearchIndex.build(chunks)
    index_dir = out_dir / "index"
    index_dir.mkdir()
    idx.save(index_dir / "bm25_index.pkl", index_dir / "chunks.json")
    return len(chunks)


def _post_validate(out_dir: Path) -> None:
    pb = out_dir / "guide" / _PLAYBOOK_FILENAME
    if "/graphify" in pb.read_text():
        raise BuildError("post-build validation: /graphify residual in playbook")
    BM25SearchIndex.load(
        out_dir / "index" / "bm25_index.pkl",
        out_dir / "index" / "chunks.json",
    )


def build_data(
    source: Path,
    out_dir: Path,
    version: str,
    no_staleness_check: bool = False,
    no_graph_refresh: bool = True,  # always true; graph refresh is manual
) -> None:
    _validate_source(source)
    if not no_staleness_check:
        _check_graph_freshness(source)
    _stage_data(source, out_dir)
    _adapt_and_copy_playbook(source, out_dir)
    _build_index(out_dir)
    # write manifest
    docs_root = out_dir / "ai_docs"
    themes = sorted(p.name for p in docs_root.iterdir() if p.is_dir())
    doc_count = sum(1 for _ in docs_root.rglob("*.md"))
    graph_payload = json.loads((out_dir / "graph" / "graph.json").read_text())
    manifest = Manifest(
        version=version,
        source_commit_sha=_git_sha(source),
        build_date=_dt.date.today().isoformat(),
        doc_count=doc_count,
        graph_node_count=len(graph_payload.get("nodes", [])),
        themes=themes,
    )
    save_manifest(manifest, out_dir)
    _post_validate(out_dir)
```

- [ ] **Step 4: Run tests, verify green**

```bash
python -m pytest tests/test_build.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
cd /home/rodrigo/Workspace/ai-study-library
rtk git add tools/harness-kb/src/harness_kb/build/build.py tools/harness-kb/tests/test_build.py
rtk git commit -m "feat(harness-kb): build pipeline (validate, stage, adapt, index, manifest)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 13: docs/* + README + CHANGELOG

**Goal:** Write the six required doc files (README, architecture, cli-reference, mcp-reference, claude-md-injection, build) per the spec's table. No new code; pure documentation.

**Files:**

- Modify: `tools/harness-kb/README.md`
- Create: `tools/harness-kb/docs/architecture.md`
- Create: `tools/harness-kb/docs/cli-reference.md`
- Create: `tools/harness-kb/docs/mcp-reference.md`
- Create: `tools/harness-kb/docs/claude-md-injection.md`
- Create: `tools/harness-kb/docs/build.md`
- Modify: `tools/harness-kb/CHANGELOG.md`

- [ ] **Step 1: Write `README.md`**

Use this exact outline. Section bodies are filled by following the per-section instructions; the H1, H2 headings, and the lead sentence of each H2 are literal — copy them.

```markdown
# harness-kb

Portable, version-pinned knowledge base of agent / harness / context-engineering reference material drawn from the `ai-study-library` corpus. Ships as a Python package with both a CLI and a stdio MCP server.

## What it is

[2 paragraphs. First paragraph: copy the spec's "Goal" section verbatim. Second paragraph: one-sentence summary of the four bundled assets — ai/docs corpus, knowledge graph, wiki, and the harness-engineering playbook.]

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

[One paragraph listing the four assets with token/file estimates from the spec's "Bundle Size Estimate" section. Add: "Refresh = upgrade the package version; the `harness-kb --version` output names the source-repo commit SHA the bundle was built from."]

## Documentation

- [Architecture](docs/architecture.md) — components, data flow, boundaries
- [CLI reference](docs/cli-reference.md) — every subcommand with examples
- [MCP reference](docs/mcp-reference.md) — every tool with schemas
- [CLAUDE.md injection](docs/claude-md-injection.md) — exactly what `harness-kb init` writes
- [Build](docs/build.md) — maintainer-facing build pipeline

## License

MIT. See [LICENSE](LICENSE).
```

Target length: ~120-150 lines once the bracketed paragraphs are filled.

- [ ] **Step 2: Write `docs/architecture.md`**

Use this exact outline:

```markdown
# Architecture

## Goal

[Copy the spec's "Goal" section verbatim.]

## Components

[Copy the spec's "Architecture Overview > Components" table verbatim.]

## Boundaries

[Copy the spec's "Architecture Overview > Boundaries" bullet list verbatim, including the "No persistent config file" boundary.]

## Data Flow

[Copy the spec's "Architecture Overview > Data Flow" bullet list verbatim.]

## Bundle layout

[Copy the spec's "Bundled Data Layout" section verbatim, including the directory tree.]
```

Target length: ~80 lines.

- [ ] **Step 3: Write `docs/cli-reference.md`**

Use this exact outline. For each subcommand, follow the entry template literally.

```markdown
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

[Synopsis, args, example output. Pattern: 4-6 lines per entry.]

### `docs list`

[…]

### `docs get`

[…]

### `docs section`

[…]

### `docs search`

[…]

### `wiki list`

[…]

### `wiki get`

[…]

### `graph query`

[…]

### `graph explain`

[…]

### `graph path`

[…]

### `graph find`

[…]

### `graph community`

[…]

### `guide`

[Note: the bare `guide` command warns and returns `toc` + token estimate. `guide --confirm` prints the full content.]

### `guide toc`

[…]

### `guide section`

[…]

### `guide search`

[…]

### `init`

[…]

### `uninit`

[…]
```

Each `[…]` block: 4-6 lines covering synopsis, args/options, one example invocation with one-line representative output. Source the surface from `cli.py` (Task 9 implementation). Target total length: ~120-150 lines.

- [ ] **Step 4: Write `docs/mcp-reference.md`**

Use this exact outline. For each of the 16 tools registered in `mcp.py`'s `_TOOL_SCHEMAS`, follow the entry template.

```markdown
# MCP Reference

`harness-kb --mcp` launches a stdio MCP server. The 16 tools below are namespaced `harness_kb_*` and exposed via `tools/list`. Each tool's input schema is JSON Schema with `additionalProperties: false`.

## Tools

### `harness_kb_themes`

[Description, input schema, return shape, one example exchange.]

### `harness_kb_docs_list`

[…]

(continue for all 16 tools — match the entries in `_TOOL_SCHEMAS` in `mcp.py`)
```

Each entry: 5-8 lines. Source descriptions and schemas verbatim from `_TOOL_SCHEMAS` in Task 10's `mcp.py`. For each tool also write one example exchange showing a representative argument and the response shape. Target total length: ~150-180 lines.

- [ ] **Step 5: Write `docs/claude-md-injection.md`**

Use this exact outline:

```markdown
# CLAUDE.md Injection

`harness-kb init` writes a marked block into the consumer project's `CLAUDE.md` so agents always reach for the tool when working on the listed themes. The block is idempotent: running `init` again replaces the existing block with the current version's content.

## What gets written

The exact content (with `{version}` substituted at runtime by the package's `__version__`):

[Quote the entire `_BODY_TEMPLATE` from `init.py` (Task 8) verbatim, inside a fenced block.]

## Idempotency rules

[Copy the spec's "Init Behavior Rules" bullet list verbatim.]

## Removing the block

`harness-kb uninit --project <path>` removes the marked block and leaves the rest of `CLAUDE.md` untouched. Run this before `pipx uninstall harness-kb`.
```

Target length: ~50-60 lines (most of which is the quoted template).

- [ ] **Step 6: Write `docs/build.md`**

Maintainer-facing. Use this exact body (substitute markdown formatting as appropriate):

````markdown
# Building the harness-kb Data Bundle

Maintainer-only documentation. End users do not run anything in this file.

## Prerequisites

- A local checkout of `ai-study-library/` (the source repo).
- Python 3.10+ with `pip` available.
- For graph refresh: Claude Code installed (the `/graphify` slash command).

## Editable install

From `tools/harness-kb/`:

```bash
pip install -e .
```

This puts `harness-kb` on PATH for use in subsequent steps.

## Refresh the graph (only if `ai/docs/` has changed)

From inside Claude Code, with `<source-root>` as your working directory:

```
/graphify update .
```

`harness-kb build` will check `graphify-out/manifest.json` mtime against `ai/docs/` mtimes and abort if any doc is newer than the manifest. If you have a reason to skip the check, pass `--no-staleness-check`.

## Build the bundle

```bash
harness-kb build \
  --source <source-root> \
  --out-dir <repo>/tools/harness-kb/src/harness_kb/data \
  --version 0.1.0
```

The build performs: validate source → check freshness → stage data (ai_docs, graph, wiki) → adapt research doc into `data/guide/harness-engineering-playbook.md` → build BM25 index → write `manifest.json` → post-validate.

## Verify

```bash
cd tools/harness-kb
pytest -v
```

All tests must pass against the new bundle.

## Release Checklist

- [ ] Bump `__version__` in `src/harness_kb/__init__.py`.
- [ ] Bump `version` in `pyproject.toml`.
- [ ] Update `CHANGELOG.md` with the new version's changes and the data SHA.
- [ ] Rebuild data with `harness-kb build --version <new>`.
- [ ] Run `pytest -v` and confirm 100% pass.
- [ ] Tag: `git tag harness-kb-v<new>` (do not push without explicit user approval).

## Out of scope (v0.1.0)

- PyPI publishing (`python -m build && twine upload`).
- CI/CD release workflow.
````

~80 lines.

- [ ] **Step 7: Update CHANGELOG.md**

Add entries for the modules built so far. Sample format:

```markdown
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
```

- [ ] **Step 8: Verify all docs files exist and have content**

```bash
cd /home/rodrigo/Workspace/ai-study-library/tools/harness-kb
for f in README.md CHANGELOG.md docs/architecture.md docs/cli-reference.md docs/mcp-reference.md docs/claude-md-injection.md docs/build.md; do
  if [ ! -s "$f" ]; then echo "MISSING OR EMPTY: $f"; exit 1; fi
  echo "$f $(wc -l < "$f") lines"
done
```

Expected: each file present with at least 30+ lines.

- [ ] **Step 9: Commit**

```bash
cd /home/rodrigo/Workspace/ai-study-library
rtk git add tools/harness-kb/README.md tools/harness-kb/CHANGELOG.md tools/harness-kb/docs/
rtk git commit -m "docs(harness-kb): full documentation set (README + 5 docs + changelog)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 14: Bundle data — run build against parent ai-study-library

**Goal:** Run the build pipeline against the actual `ai-study-library/` repo and populate `src/harness_kb/data/`.

**Files:**

- Modify (populate): `tools/harness-kb/src/harness_kb/data/`

- [ ] **Step 1: Confirm graph is fresh**

```bash
cd /home/rodrigo/Workspace/ai-study-library
ls -lt graphify-out/manifest.json ai/docs/**/*.md 2>/dev/null | head -10
```

If any `.md` is newer than `manifest.json`, run `/graphify update .` from inside Claude Code first. (Cannot be invoked from this script — see spec.)

- [ ] **Step 2a: Editable install so `harness-kb` is on PATH**

```bash
cd /home/rodrigo/Workspace/ai-study-library/tools/harness-kb
pip install -e .
which harness-kb
```

Expected: a path under the active Python environment.

- [ ] **Step 2b: Run the build via the CLI**

```bash
cd /home/rodrigo/Workspace/ai-study-library/tools/harness-kb
harness-kb build \
  --source /home/rodrigo/Workspace/ai-study-library \
  --out-dir /home/rodrigo/Workspace/ai-study-library/tools/harness-kb/src/harness_kb/data \
  --version 0.1.0
```

Expected output: `build complete: <path>` (no exception). Build error message if graph stale: follow its instructions, then re-run with `--no-staleness-check` only as a last resort.

- [ ] **Step 3: Verify the bundle**

```bash
cd /home/rodrigo/Workspace/ai-study-library/tools/harness-kb
ls -la src/harness_kb/data/
cat src/harness_kb/data/manifest.json
```

Expected:
- `manifest.json` present, valid JSON, 16 themes, doc_count > 100, graph_node_count > 400.
- `ai_docs/`, `graph/`, `wiki/`, `guide/`, `index/` all populated.
- Bundle total size: `du -sh src/harness_kb/data/` should report 5-10 MB.

- [ ] **Step 4: Run a smoke search against the live bundle**

```bash
cd /home/rodrigo/Workspace/ai-study-library/tools/harness-kb
python -c "
import sys; sys.path.insert(0, 'src')
from harness_kb import docs, graph, wiki, guide
print('themes:', [t.name for t in docs.list_themes()][:3])
print('search hit count:', len(docs.search_docs('smart zone')))
print('graph keyword hit count:', len(graph.keyword_query('smart')))
print('wiki pages count:', len(wiki.list_wiki_pages()))
print('guide TOC entries:', len(guide.toc()))
"
```

Expected: themes list 16 items, search returns ≥ 1 hit, graph keyword returns ≥ 1 hit, wiki lists ≥ 5 pages, guide TOC has ≥ 10 entries.

- [ ] **Step 5: Run full test suite against live bundle**

```bash
cd /home/rodrigo/Workspace/ai-study-library/tools/harness-kb
python -m pytest -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
cd /home/rodrigo/Workspace/ai-study-library
rtk git add tools/harness-kb/src/harness_kb/data/
rtk git commit -m "feat(harness-kb): bundle v0.1.0 data snapshot

Built from ai-study-library/ HEAD. Includes all 16 ai/docs themes,
graphify graph + wiki, adapted playbook, BM25 index, manifest.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 15: Integration smoke test (pipx install)

**Goal:** Confirm the package installs and runs end-to-end via pipx from a local path.

**Files:**

- No new files; this is a verification task.

- [ ] **Step 1: pipx install from local path**

```bash
cd /home/rodrigo/Workspace/ai-study-library
pipx install ./tools/harness-kb --force
```

Expected: install succeeds; `harness-kb` is on PATH afterward.

- [ ] **Step 2: Verify version**

```bash
harness-kb --version
```

Expected: `harness-kb 0.1.0 (data=ai-study-library@<sha>, built <date>)`.

- [ ] **Step 3: Verify themes**

```bash
harness-kb themes
```

Expected: JSON list of 16 themes with `doc_count`.

- [ ] **Step 4: Verify docs search**

```bash
harness-kb docs search "smart zone" --limit 3
```

Expected: JSON array of 1-3 ranked hits.

- [ ] **Step 5: Verify graph query**

```bash
harness-kb graph query "smart"
```

Expected: JSON array including a node whose label contains "Smart".

- [ ] **Step 6: Verify wiki**

```bash
harness-kb wiki list | head -5
harness-kb wiki get index 2>&1 | head -10
```

Expected: list of pages; `index` page content prints.

- [ ] **Step 7: Verify guide**

```bash
harness-kb guide toc | head -20
```

Expected: JSON array of TOC entries (level/heading/anchor).

- [ ] **Step 8: Verify init dry-run**

```bash
TMPDIR=$(mktemp -d)
harness-kb init --project "$TMPDIR" --dry-run
ls "$TMPDIR"
```

Expected: dry-run text printed; `$TMPDIR` is empty (no CLAUDE.md created).

- [ ] **Step 9: Verify init writes**

```bash
TMPDIR=$(mktemp -d)
harness-kb init --project "$TMPDIR"
grep -c "harness-kb v0.1.0 BEGIN" "$TMPDIR/CLAUDE.md"
```

Expected: `1`.

- [ ] **Step 10: Verify init idempotent**

```bash
harness-kb init --project "$TMPDIR"
grep -c "harness-kb v0.1.0 BEGIN" "$TMPDIR/CLAUDE.md"
```

Expected: still `1`.

- [ ] **Step 11: Verify uninit**

```bash
harness-kb uninit --project "$TMPDIR"
grep -c "harness-kb v0.1.0 BEGIN" "$TMPDIR/CLAUDE.md" || echo "removed"
```

Expected: `removed`.

- [ ] **Step 12: Verify MCP server starts (smoke)**

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"smoke","version":"1.0"}}}' | timeout 3 harness-kb --mcp 2>&1 | head -5
```

Expected: a JSON-RPC response on stdout (or no error on stderr). If `timeout` is missing or the server idles silently, that is also acceptable — pass the step if no Python exception leaked.

- [ ] **Step 13: Cleanup**

```bash
pipx uninstall harness-kb
```

- [ ] **Step 14: No commit needed (no files changed)**

This task only runs verifications. If any step failed, stop and fix the underlying module before proceeding to Task 16.

---

## Task 16: Final verification + tag v0.1.0

**Goal:** Confirm the full success-criteria list from the spec, then tag the release.

- [ ] **Step 1: Run full test suite**

```bash
cd /home/rodrigo/Workspace/ai-study-library/tools/harness-kb
python -m pytest --cov=harness_kb --cov-report=term-missing -v
```

Expected: all tests pass; coverage ≥ 80%.

- [ ] **Step 2: Run spec success-criteria checklist**

For each criterion in the spec's "Success Criteria" section, confirm pass:

```bash
# Each command should produce reasonable output, not error.
pipx install ./tools/harness-kb --force
harness-kb --version
harness-kb themes | python -c "import sys, json; d=json.load(sys.stdin); print(len(d), 'themes'); assert len(d) == 16"
harness-kb docs search "smart zone" | python -c "import sys, json; d=json.load(sys.stdin); print(len(d), 'hits'); assert len(d) >= 1"
harness-kb graph explain "Subagent as Context Firewall" | head -10
harness-kb guide toc | python -c "import sys, json; d=json.load(sys.stdin); print(len(d), 'TOC entries'); assert len(d) >= 10"

# Bare `guide` warns; --confirm prints content
harness-kb guide | python -c "import sys, json; d=json.load(sys.stdin); assert 'warning' in d; print('warn ok')"
harness-kb guide --confirm | wc -l   # expect ~1500 lines

# Adapted playbook has zero /graphify residuals
grep -c '/graphify' /home/rodrigo/Workspace/ai-study-library/tools/harness-kb/src/harness_kb/data/guide/harness-engineering-playbook.md
# expect: 0

grep -c 'harness-kb' /home/rodrigo/Workspace/ai-study-library/tools/harness-kb/src/harness_kb/data/guide/harness-engineering-playbook.md
# expect: ≥ 1

pipx uninstall harness-kb
```

- [ ] **Step 3: Tag the release**

```bash
cd /home/rodrigo/Workspace/ai-study-library
rtk git tag harness-kb-v0.1.0
rtk git log --oneline -5
```

Expected: tag visible; recent commits include all 14 task commits + 2 pre-flight commits.

- [ ] **Step 4: Optional — push tag**

Per system prompt rules, do NOT push without explicit user request. Stop here. Inform the user the v0.1.0 tag is local; they decide whether to push.

---

## Out of Scope (do not address in this plan)

- PyPI / private-index publishing.
- CI/CD workflow.
- Embedding-based semantic search.
- Natural-language graph query (LLM-backed).
- Web UI.
- Auto-sync between source `dev/research/...md` and bundled adapted copy.

## Open Questions for Executor

None. All branches of execution are specified.

## Post-execution

After Task 16, the user can:
- `pipx install ./tools/harness-kb` and use the tool locally.
- Run `harness-kb init` in any consumer project to wire CLAUDE.md.
- When `ai-study-library/` evolves, re-run Task 14 to rebuild the bundle and bump the version per the release checklist in `docs/build.md`.
