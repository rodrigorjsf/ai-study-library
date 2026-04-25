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
