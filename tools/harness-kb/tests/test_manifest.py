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
