# tools/harness-kb/tests/test_guide.py
from pathlib import Path
import pytest

from harness_kb.chunking import Chunk
from harness_kb.search import BM25SearchIndex
from harness_kb import guide as guide_module


@pytest.fixture(autouse=True)
def _reset_index_cache():
    guide_module._index_cache = None
    yield
    guide_module._index_cache = None


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
