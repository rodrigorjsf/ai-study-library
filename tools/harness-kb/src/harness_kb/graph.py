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
    """Return (graph, label_to_id_map)."""
    global _graph_cache
    if _graph_cache is not None:
        return _graph_cache
    payload = json.loads((get_data_dir() / "graph" / "graph.json").read_text())
    g = nx.Graph()
    label_to_id: dict[str, str] = {}
    for node in payload.get("nodes", []):
        nid = node["id"]
        label = node.get("label", nid)
        g.add_node(
            nid,
            label=label,
            community=node.get("community"),
            source_file=node.get("source_file", ""),
            source_location=node.get("source_location", ""),
        )
        label_to_id[label] = nid
    for link in payload.get("links", []):
        g.add_edge(
            link["source"], link["target"],
            relation=link.get("relation", ""),
            confidence=link.get("confidence", ""),
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
    g, _l2id = _load_graph()
    needle = text.lower()
    out: list[GraphNode] = []
    for nid, data in g.nodes(data=True):
        if needle in data.get("label", "").lower():
            out.append(_node_to_dataclass(g, nid))
    return out


def _find_start_nodes(question: str, g: nx.Graph, max_starts: int = 3) -> list[str]:
    """Return up to `max_starts` node IDs whose labels best match question terms.

    Uses graphify's algorithm: terms = tokens from question.split() with len > 3,
    lowercased. Score = number of terms appearing as substring in label (lowercased).
    """
    terms = [t.lower() for t in question.split() if len(t) > 3]
    scored: list[tuple[int, str]] = []
    for nid, ndata in g.nodes(data=True):
        label = ndata.get("label", "").lower()
        score = sum(1 for t in terms if t in label)
        if score > 0:
            scored.append((score, nid))
    scored.sort(reverse=True)
    return [nid for _, nid in scored[:max_starts]]


def query(
    question: str,
    mode: str = "bfs",
    budget: int = 2000,
    max_starts: int = 3,
) -> dict:
    """Run a graphify-equivalent query. Returns:
      {
        "traversal": "BFS" | "DFS",
        "start_labels": [str, ...],
        "nodes": [{"label": str, "source_file": str, "source_location": Any}, ...],
        "edges": [{"source": str, "target": str, "relation": str, "confidence": str}, ...],
        "rendered": str,        # graphify-compatible text output
        "truncated": bool,
      }
    Empty start_labels means no terms matched any label; nodes/edges empty too.
    """
    g, _l2id = _load_graph()
    terms = [t.lower() for t in question.split() if len(t) > 3]
    start_nodes = _find_start_nodes(question, g, max_starts=max_starts)

    if not start_nodes:
        return {
            "traversal": mode.upper(),
            "start_labels": [],
            "nodes": [],
            "edges": [],
            "rendered": f"No matching nodes found for query terms: {terms}",
            "truncated": False,
        }

    subgraph_nodes: set[str] = set()
    subgraph_edges: list[tuple[str, str]] = []

    if mode == "dfs":
        visited: set[str] = set()
        stack: list[tuple[str, int]] = [(n, 0) for n in reversed(start_nodes)]
        while stack:
            node, depth = stack.pop()
            if node in visited or depth > 6:
                continue
            visited.add(node)
            subgraph_nodes.add(node)
            for neighbor in g.neighbors(node):
                if neighbor not in visited:
                    stack.append((neighbor, depth + 1))
                    subgraph_edges.append((node, neighbor))
    else:
        # BFS: explore all neighbors layer by layer up to depth 3.
        frontier = set(start_nodes)
        subgraph_nodes = set(start_nodes)
        for _ in range(3):
            next_frontier: set[str] = set()
            for n in frontier:
                for neighbor in g.neighbors(n):
                    if neighbor not in subgraph_nodes:
                        next_frontier.add(neighbor)
                        subgraph_edges.append((n, neighbor))
            subgraph_nodes.update(next_frontier)
            frontier = next_frontier

    # Rank output by relevance
    def relevance(nid: str) -> int:
        label = g.nodes[nid].get("label", "").lower()
        return sum(1 for t in terms if t in label)

    ranked_nodes = sorted(subgraph_nodes, key=relevance, reverse=True)

    start_labels = [g.nodes[n].get("label", n) for n in start_nodes]
    char_budget = budget * 4

    lines = [
        f"Traversal: {mode.upper()} | Start: {start_labels} | {len(subgraph_nodes)} nodes"
    ]
    for nid in ranked_nodes:
        d = g.nodes[nid]
        lines.append(
            f"  NODE {d.get('label', nid)} "
            f"[src={d.get('source_file', '')} loc={d.get('source_location', '')}]"
        )
    for u, v in subgraph_edges:
        if u in subgraph_nodes and v in subgraph_nodes:
            d = g.edges[u, v]
            lines.append(
                f"  EDGE {g.nodes[u].get('label', u)} "
                f"--{d.get('relation', '')} [{d.get('confidence', '')}]--> "
                f"{g.nodes[v].get('label', v)}"
            )

    output = "\n".join(lines)
    truncated = False
    if len(output) > char_budget:
        output = output[:char_budget] + (
            f"\n... (truncated at ~{budget} token budget - use --budget N for more)"
        )
        truncated = True

    nodes_out = [
        {
            "label": g.nodes[nid].get("label", nid),
            "source_file": g.nodes[nid].get("source_file", ""),
            "source_location": g.nodes[nid].get("source_location", ""),
        }
        for nid in ranked_nodes
    ]
    edges_out = [
        {
            "source": g.nodes[u].get("label", u),
            "target": g.nodes[v].get("label", v),
            "relation": g.edges[u, v].get("relation", ""),
            "confidence": g.edges[u, v].get("confidence", ""),
        }
        for u, v in subgraph_edges
        if u in subgraph_nodes and v in subgraph_nodes
    ]

    return {
        "traversal": mode.upper(),
        "start_labels": start_labels,
        "nodes": nodes_out,
        "edges": edges_out,
        "rendered": output,
        "truncated": truncated,
    }


def explain(label: str) -> dict:
    g, _l2id = _load_graph()
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
    g, _l2id = _load_graph()
    src = _id_for_label(from_label)
    dst = _id_for_label(to_label)
    try:
        ids = nx.shortest_path(g, src, dst)
    except nx.NetworkXNoPath:
        raise ValueError(f"no path between {from_label!r} and {to_label!r}")
    return [g.nodes[nid].get("label", nid) for nid in ids]


def find_nodes(pattern: str) -> list[GraphNode]:
    g, _l2id = _load_graph()
    rx = re.compile(pattern)
    return [_node_to_dataclass(g, nid) for nid, data in g.nodes(data=True)
            if rx.search(data.get("label", ""))]


def community_nodes(name: str) -> list[GraphNode]:
    g, _l2id = _load_graph()
    return [_node_to_dataclass(g, nid) for nid, data in g.nodes(data=True)
            if data.get("community") == name]
