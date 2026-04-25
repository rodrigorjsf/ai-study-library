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
