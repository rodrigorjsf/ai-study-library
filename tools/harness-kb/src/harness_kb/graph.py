# tools/harness-kb/src/harness_kb/graph.py
from __future__ import annotations
import json
import re
from dataclasses import dataclass
from pathlib import Path

import networkx as nx

from harness_kb.manifest import get_data_dir


@dataclass
class GraphNode:
    label: str
    id: str
    community: str | None


@dataclass
class GraphNeighbor:
    label: str
    edge_type: str
    weight: float


_graph_cache: tuple[nx.Graph, dict[str, str]] | None = None


def _load_graph() -> tuple[nx.Graph, dict[str, str]]:
    """Return (graph, label_to_id_map). Graph uses node IDs."""
    global _graph_cache
    if _graph_cache is not None:
        return _graph_cache
    payload = json.loads((get_data_dir() / "graph" / "graph.json").read_text())
    g = nx.Graph()
    label_to_id: dict[str, str] = {}
    for node in payload.get("nodes", []):
        nid = node["id"]
        g.add_node(nid, label=node.get("label", nid), community=node.get("community"))
        label_to_id[node.get("label", nid)] = nid
    for link in payload.get("links", []):
        g.add_edge(
            link["source"], link["target"],
            edge_type=link.get("edge_type", ""),
            weight=float(link.get("weight", 1.0)),
        )
    _graph_cache = (g, label_to_id)
    return _graph_cache


def _id_for_label(label: str) -> str:
    _, l2id = _load_graph()
    if label not in l2id:
        raise KeyError(f"node label not found: {label}")
    return l2id[label]


def _node_to_dataclass(g: nx.Graph, nid: str) -> GraphNode:
    data = g.nodes[nid]
    return GraphNode(label=data.get("label", nid), id=nid, community=data.get("community"))


def keyword_query(text: str) -> list[GraphNode]:
    g, _ = _load_graph()
    needle = text.lower()
    out: list[GraphNode] = []
    for nid, data in g.nodes(data=True):
        if needle in data.get("label", "").lower():
            out.append(_node_to_dataclass(g, nid))
    return out


def explain(label: str) -> dict:
    g, _ = _load_graph()
    nid = _id_for_label(label)
    node = _node_to_dataclass(g, nid)
    neighbors: list[dict] = []
    for nbr_id in g.neighbors(nid):
        edge = g[nid][nbr_id]
        neighbors.append({
            "label": g.nodes[nbr_id].get("label", nbr_id),
            "id": nbr_id,
            "edge_type": edge.get("edge_type", ""),
            "weight": float(edge.get("weight", 1.0)),
        })
    return {"node": {"label": node.label, "id": node.id, "community": node.community}, "neighbors": neighbors}


def shortest_path(from_label: str, to_label: str) -> list[str]:
    g, _ = _load_graph()
    src = _id_for_label(from_label)
    dst = _id_for_label(to_label)
    try:
        ids = nx.shortest_path(g, src, dst)
    except nx.NetworkXNoPath:
        raise ValueError(f"no path between {from_label!r} and {to_label!r}")
    return [g.nodes[nid].get("label", nid) for nid in ids]


def find_nodes(pattern: str) -> list[GraphNode]:
    g, _ = _load_graph()
    rx = re.compile(pattern)
    return [_node_to_dataclass(g, nid) for nid, data in g.nodes(data=True)
            if rx.search(data.get("label", ""))]


def community_nodes(name: str) -> list[GraphNode]:
    g, _ = _load_graph()
    return [_node_to_dataclass(g, nid) for nid, data in g.nodes(data=True)
            if data.get("community") == name]
