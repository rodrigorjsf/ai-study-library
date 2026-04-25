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
