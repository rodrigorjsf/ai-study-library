# tools/harness-kb/tests/test_graph.py
import json
import re
from pathlib import Path
import pytest

from harness_kb import graph as graph_module
from harness_kb.graph import GraphNode


@pytest.fixture(autouse=True)
def _reset_graph_cache():
    graph_module._graph_cache = None
    yield
    graph_module._graph_cache = None


@pytest.fixture
def fake_graph(tmp_path: Path, monkeypatch) -> Path:
    graph_dir = tmp_path / "graph"
    graph_dir.mkdir()
    payload = {
        "directed": False,
        "graph": {},
        "multigraph": False,
        "nodes": [
            {"id": "smart_zone", "label": "Smart Zone", "community": "Context",
             "source_file": "docs/smart.md", "source_location": "line:10"},
            {"id": "context_rot", "label": "Context Rot", "community": "Context",
             "source_file": "docs/context.md", "source_location": None},
            {"id": "subagent", "label": "Subagent as Context Firewall", "community": "Agents",
             "source_file": "docs/agents.md", "source_location": "line:5"},
            {"id": "skills", "label": "Agent Skills Standard", "community": "Skills",
             "source_file": "docs/skills.md", "source_location": None},
        ],
        "links": [
            {"source": "smart_zone", "target": "context_rot",
             "relation": "related", "confidence": "HIGH", "weight": 1.0},
            {"source": "subagent", "target": "smart_zone",
             "relation": "supports", "confidence": "MEDIUM", "weight": 0.8},
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


# ---------------------------------------------------------------------------
# query() tests — graphify-equivalent BFS/DFS traversal
# ---------------------------------------------------------------------------

def test_query_bfs_finds_natural_language_question(fake_graph):
    """BFS query should find nodes whose labels contain query terms."""
    result = graph_module.query("agent skills standard", mode="bfs")
    assert result["nodes"], (
        "query('agent skills standard') returned empty nodes — expected 'Agent Skills Standard'"
    )
    labels = [n["label"] for n in result["nodes"]]
    assert any("Agent Skills Standard" == lbl or "skills" in lbl.lower() for lbl in labels), (
        f"Expected a node containing 'skills' in labels: {labels!r}"
    )


def test_query_dfs_returns_dfs_traversal(fake_graph):
    """DFS mode should report DFS traversal and not exceed depth 6."""
    result = graph_module.query("subagent context firewall", mode="dfs")
    assert result["traversal"] == "DFS", f"Expected 'DFS', got {result['traversal']!r}"
    # Should find at least the start node (subagent) and its BFS-reachable neighbors
    assert result["nodes"], "DFS query returned empty nodes"


def test_query_no_matching_terms_returns_empty(fake_graph):
    """Query with no matching terms returns empty result dict."""
    result = graph_module.query("asdfqwerty")
    assert result["start_labels"] == [], f"Expected [], got {result['start_labels']!r}"
    assert result["nodes"] == [], f"Expected [], got {result['nodes']!r}"
    assert result["edges"] == [], f"Expected [], got {result['edges']!r}"
    assert "No matching nodes found for query terms:" in result["rendered"]
    assert result["truncated"] is False


def test_query_budget_truncates(fake_graph):
    """Small budget forces truncation of rendered output."""
    result = graph_module.query("context smart zone subagent", budget=10)
    assert result["truncated"] is True, "Expected truncated=True with budget=10"
    assert result["rendered"].endswith(
        "... (truncated at ~10 token budget - use --budget N for more)"
    ), f"Rendered doesn't end with truncation marker: {result['rendered'][-80:]!r}"


def test_query_rendered_format_matches_graphify(fake_graph):
    """Rendered output matches graphify's exact format."""
    # Use a term that matches only 1 start node (subagent) so BFS discovery
    # traverses to its neighbors and actually produces EDGE lines.
    result = graph_module.query("subagent firewall", mode="bfs", budget=2000)
    rendered = result["rendered"]
    assert rendered.startswith("Traversal: BFS | Start:"), (
        f"Rendered does not start with expected header: {rendered[:80]!r}"
    )
    assert "NODE " in rendered, "Rendered missing NODE lines"
    # subagent connects to smart_zone, which BFS discovers → EDGE lines appear
    assert "EDGE " in rendered, "Rendered missing EDGE lines"


def test_query_result_keys(fake_graph):
    """query() result has all required keys."""
    result = graph_module.query("smart zone context")
    for key in ("traversal", "start_labels", "nodes", "edges", "rendered", "truncated"):
        assert key in result, f"Missing key {key!r} in result"


def test_query_live_bundle():
    """Real corpus hit: 'five components of an agent harness' finds nodes without monkeypatching."""
    result = graph_module.query("five components of an agent harness")
    assert result["nodes"], (
        "query('five components of an agent harness') returned empty nodes against the live bundle"
    )
