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
