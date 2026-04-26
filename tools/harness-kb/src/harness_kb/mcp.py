# tools/harness-kb/src/harness_kb/mcp.py
from __future__ import annotations
from typing import Any, Callable

from harness_kb import docs, graph, wiki, guide


def _safe(fn: Callable[..., Any], not_found_exceptions=(FileNotFoundError, KeyError)):
    def wrapped(args: dict) -> dict | list:
        try:
            return fn(args)
        except not_found_exceptions as e:
            return {"error": "not_found", "detail": str(e)}
        except ValueError as e:
            return {"error": "invalid_argument", "detail": str(e)}
    return wrapped


def _h_themes(_: dict):
    return [{"name": t.name, "doc_count": t.doc_count} for t in docs.list_themes()]


def _h_docs_list(args: dict):
    return [{"path": d.path, "theme": d.theme, "title": d.title, "size_tokens": d.size_tokens}
            for d in docs.list_docs(theme=args.get("theme"))]


def _h_docs_get(args: dict):
    return {"path": args["path"], "content": docs.get_doc(args["path"])}


def _h_docs_section(args: dict):
    return {"path": args["path"], "heading": args["heading"],
            "content": docs.get_section(args["path"], args["heading"])}


def _h_docs_search(args: dict):
    hits = docs.search_docs(args["query"], limit=args.get("limit", 10), theme=args.get("theme"))
    return [{"path": h.path, "heading": h.heading, "score": h.score, "snippet": h.snippet} for h in hits]


def _h_wiki_list(_: dict):
    return [{"name": n} for n in wiki.list_wiki_pages()]


def _h_wiki_get(args: dict):
    return {"name": args["name"], "content": wiki.get_wiki_page(args["name"])}


def _h_graph_query(args: dict):
    return [{"label": n.label, "id": n.id, "community": n.community}
            for n in graph.bm25_query(args["text"], limit=args.get("limit", 10))]


def _h_graph_explain(args: dict):
    return graph.explain(args["label"])


def _h_graph_path(args: dict):
    p = graph.shortest_path(args["from"], args["to"])
    return {"path": p, "length": len(p) - 1}


def _h_graph_find(args: dict):
    return [{"label": n.label, "id": n.id, "community": n.community}
            for n in graph.find_nodes(args["pattern"])]


def _h_graph_community(args: dict):
    return [{"label": n.label, "id": n.id} for n in graph.community_nodes(args["name"])]


def _h_guide_toc(_: dict):
    return [{"level": s.level, "heading": s.heading, "anchor": s.anchor} for s in guide.toc()]


def _h_guide_section(args: dict):
    return guide.get_section(args["heading"])


def _h_guide_get(args: dict):
    return guide.get_full(confirm=bool(args.get("confirm", False)))


def _h_guide_search(args: dict):
    hits = guide.search_guide(args["query"], limit=args.get("limit", 10))
    return [{"path": h.path, "heading": h.heading, "score": h.score, "snippet": h.snippet} for h in hits]


_tool_handlers: dict[str, Callable[[dict], Any]] = {
    "harness_kb_themes":          _safe(_h_themes),
    "harness_kb_docs_list":       _safe(_h_docs_list),
    "harness_kb_docs_get":        _safe(_h_docs_get),
    "harness_kb_docs_section":    _safe(_h_docs_section),
    "harness_kb_docs_search":     _safe(_h_docs_search),
    "harness_kb_wiki_list":       _safe(_h_wiki_list),
    "harness_kb_wiki_get":        _safe(_h_wiki_get),
    "harness_kb_graph_query":     _safe(_h_graph_query),
    "harness_kb_graph_explain":   _safe(_h_graph_explain),
    "harness_kb_graph_path":      _safe(_h_graph_path),
    "harness_kb_graph_find":      _safe(_h_graph_find),
    "harness_kb_graph_community": _safe(_h_graph_community),
    "harness_kb_guide_toc":       _safe(_h_guide_toc),
    "harness_kb_guide_section":   _safe(_h_guide_section),
    "harness_kb_guide_get":       _safe(_h_guide_get),
    "harness_kb_guide_search":    _safe(_h_guide_search),
}

ALL_TOOL_NAMES = list(_tool_handlers.keys())


_TOOL_SCHEMAS: dict[str, tuple[str, dict]] = {
    "harness_kb_themes": (
        "List ai/docs themes with doc counts.",
        {"type": "object", "properties": {}, "additionalProperties": False},
    ),
    "harness_kb_docs_list": (
        "List bundled docs, optionally filtered by theme.",
        {"type": "object", "properties": {"theme": {"type": "string"}}, "additionalProperties": False},
    ),
    "harness_kb_docs_get": (
        "Return the full content of a bundled doc by relative path under ai_docs/.",
        {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"], "additionalProperties": False},
    ),
    "harness_kb_docs_section": (
        "Return one H2/H3 section of a bundled doc by heading.",
        {"type": "object",
         "properties": {"path": {"type": "string"}, "heading": {"type": "string"}},
         "required": ["path", "heading"], "additionalProperties": False},
    ),
    "harness_kb_docs_search": (
        "BM25 search over chunked ai/docs sections; returns ranked hits with snippets.",
        {"type": "object",
         "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "default": 10},
                        "theme": {"type": "string"}},
         "required": ["query"], "additionalProperties": False},
    ),
    "harness_kb_wiki_list": (
        "List names of bundled wiki pages.",
        {"type": "object", "properties": {}, "additionalProperties": False},
    ),
    "harness_kb_wiki_get": (
        "Return the content of one wiki page by name (basename without .md).",
        {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"], "additionalProperties": False},
    ),
    "harness_kb_graph_query": (
        "BM25-ranked search over node labels in the bundled graph.",
        {"type": "object",
         "properties": {"text": {"type": "string"}, "limit": {"type": "integer", "default": 10}},
         "required": ["text"], "additionalProperties": False},
    ),
    "harness_kb_graph_explain": (
        "Return a node and its 1-hop neighbors.",
        {"type": "object", "properties": {"label": {"type": "string"}}, "required": ["label"], "additionalProperties": False},
    ),
    "harness_kb_graph_path": (
        "Return the shortest path between two nodes by label.",
        {"type": "object",
         "properties": {"from": {"type": "string"}, "to": {"type": "string"}},
         "required": ["from", "to"], "additionalProperties": False},
    ),
    "harness_kb_graph_find": (
        "Regex search over node labels.",
        {"type": "object", "properties": {"pattern": {"type": "string"}}, "required": ["pattern"], "additionalProperties": False},
    ),
    "harness_kb_graph_community": (
        "Return all nodes in a community by community name.",
        {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"], "additionalProperties": False},
    ),
    "harness_kb_guide_toc": (
        "Return the playbook's H2/H3 outline.",
        {"type": "object", "properties": {}, "additionalProperties": False},
    ),
    "harness_kb_guide_section": (
        "Return one section of the playbook by heading.",
        {"type": "object", "properties": {"heading": {"type": "string"}}, "required": ["heading"], "additionalProperties": False},
    ),
    "harness_kb_guide_get": (
        "Return the full playbook content if confirm=true; otherwise a warning + TOC + token estimate.",
        {"type": "object",
         "properties": {"confirm": {"type": "boolean", "default": False}},
         "additionalProperties": False},
    ),
    "harness_kb_guide_search": (
        "BM25 search restricted to the playbook.",
        {"type": "object",
         "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "default": 10}},
         "required": ["query"], "additionalProperties": False},
    ),
}


def build_server():
    """Construct an MCP Server with all tools registered."""
    from mcp.server import Server
    from mcp.types import Tool, TextContent

    server = Server("harness-kb")

    @server.list_tools()
    async def _list_tools() -> list[Tool]:
        return [
            Tool(name=name, description=desc, inputSchema=schema)
            for name, (desc, schema) in _TOOL_SCHEMAS.items()
        ]

    @server.call_tool()
    async def _call_tool(name: str, arguments: dict) -> list[TextContent]:
        import json as _json
        handler = _tool_handlers.get(name)
        if handler is None:
            payload = {"error": "unknown_tool", "detail": name}
        else:
            payload = handler(arguments or {})
        return [TextContent(type="text", text=_json.dumps(payload, ensure_ascii=False))]

    return server


def run_stdio_server() -> None:
    import asyncio
    from mcp.server.stdio import stdio_server

    server = build_server()

    async def _main():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())

    asyncio.run(_main())
