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
