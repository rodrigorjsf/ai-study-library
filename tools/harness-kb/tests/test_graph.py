# tools/harness-kb/tests/test_graph.py
import json
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
            {"id": "smart_zone", "label": "Smart Zone", "community": "Context"},
            {"id": "context_rot", "label": "Context Rot", "community": "Context"},
            {"id": "subagent", "label": "Subagent as Context Firewall", "community": "Agents"},
            {"id": "skills", "label": "Agent Skills Standard", "community": "Skills"},
        ],
        "links": [
            {"source": "smart_zone", "target": "context_rot", "edge_type": "related", "weight": 1.0},
            {"source": "subagent", "target": "smart_zone", "edge_type": "supports", "weight": 0.8},
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
