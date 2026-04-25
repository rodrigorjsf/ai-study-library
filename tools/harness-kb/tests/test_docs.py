# tools/harness-kb/tests/test_docs.py
import json
from pathlib import Path
import pytest

from harness_kb.chunking import Chunk
from harness_kb.search import BM25SearchIndex
from harness_kb import docs as docs_module


@pytest.fixture(autouse=True)
def _reset_index_cache():
    docs_module._index_cache = None
    yield
    docs_module._index_cache = None


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
              text="MCP Model Context Protocol overview"),
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
