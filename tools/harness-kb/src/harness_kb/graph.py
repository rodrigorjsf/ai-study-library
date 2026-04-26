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


_graph_cache: tuple[nx.Graph, dict[str, str], list[tuple[str, list[str]]]] | None = None


def _load_graph() -> tuple[nx.Graph, dict[str, str], list[tuple[str, list[str]]]]:
    """Return (graph, label_to_id_map, bm25_corpus).

    bm25_corpus is a list of (node_id, tokenized_label) pairs, parallel to BM25 index.
    """
    global _graph_cache
    if _graph_cache is not None:
        return _graph_cache
    payload = json.loads((get_data_dir() / "graph" / "graph.json").read_text())
    g = nx.Graph()
    label_to_id: dict[str, str] = {}
    bm25_corpus: list[tuple[str, list[str]]] = []
    for node in payload.get("nodes", []):
        nid = node["id"]
        label = node.get("label", nid)
        g.add_node(nid, label=label, community=node.get("community"))
        label_to_id[label] = nid
        bm25_corpus.append((nid, re.findall(r"\w+", label.lower())))
    for link in payload.get("links", []):
        g.add_edge(
            link["source"], link["target"],
            edge_type=link.get("edge_type", ""),
            weight=float(link.get("weight", 1.0)),
        )
    _graph_cache = (g, label_to_id, bm25_corpus)
    return _graph_cache


def _id_for_label(label: str) -> str:
    _, l2id, _corpus = _load_graph()
    if label not in l2id:
        raise KeyError(f"node label not found: {label}")
    return l2id[label]


def _node_to_dataclass(g: nx.Graph, nid: str) -> GraphNode:
    data = g.nodes[nid]
    return GraphNode(label=data.get("label", nid), id=nid, community=data.get("community"))


def keyword_query(text: str) -> list[GraphNode]:
    g, _l2id, _corpus = _load_graph()
    needle = text.lower()
    out: list[GraphNode] = []
    for nid, data in g.nodes(data=True):
        if needle in data.get("label", "").lower():
            out.append(_node_to_dataclass(g, nid))
    return out


def bm25_query(text: str, limit: int = 10) -> list[GraphNode]:
    """BM25-ranked search over graph node labels (tokenized on \\w+, lowercased).

    Returns up to `limit` GraphNode objects in descending score order. Returns an
    empty list on no positive-score hits or empty input.
    """
    if not text or not text.strip():
        return []

    from rank_bm25 import BM25Okapi  # lazy import to avoid startup cost

    g, _l2id, corpus = _load_graph()
    if not corpus:
        return []

    node_ids = [nid for nid, _tokens in corpus]
    tokenized_corpus = [tokens for _nid, tokens in corpus]

    bm25 = BM25Okapi(tokenized_corpus)
    query_tokens = re.findall(r"\w+", text.lower())
    if not query_tokens:
        return []

    scores = bm25.get_scores(query_tokens)

    ranked = sorted(
        ((score, nid) for score, nid in zip(scores, node_ids) if score > 0.0),
        key=lambda x: x[0],
        reverse=True,
    )

    return [_node_to_dataclass(g, nid) for _score, nid in ranked[:limit]]


def explain(label: str) -> dict:
    g, _l2id, _corpus = _load_graph()
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
    g, _l2id, _corpus = _load_graph()
    src = _id_for_label(from_label)
    dst = _id_for_label(to_label)
    try:
        ids = nx.shortest_path(g, src, dst)
    except nx.NetworkXNoPath:
        raise ValueError(f"no path between {from_label!r} and {to_label!r}")
    return [g.nodes[nid].get("label", nid) for nid in ids]


def find_nodes(pattern: str) -> list[GraphNode]:
    g, _l2id, _corpus = _load_graph()
    rx = re.compile(pattern)
    return [_node_to_dataclass(g, nid) for nid, data in g.nodes(data=True)
            if rx.search(data.get("label", ""))]


def community_nodes(name: str) -> list[GraphNode]:
    g, _l2id, _corpus = _load_graph()
    return [_node_to_dataclass(g, nid) for nid, data in g.nodes(data=True)
            if data.get("community") == name]
