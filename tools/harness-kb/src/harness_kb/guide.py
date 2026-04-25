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
