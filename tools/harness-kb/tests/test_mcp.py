# tools/harness-kb/tests/test_mcp.py
import pytest
from harness_kb.mcp import build_server, _tool_handlers, ALL_TOOL_NAMES


def test_all_16_tools_registered():
    assert len(ALL_TOOL_NAMES) == 16
    expected = {
        "harness_kb_themes",
        "harness_kb_docs_list", "harness_kb_docs_get",
        "harness_kb_docs_section", "harness_kb_docs_search",
        "harness_kb_wiki_list", "harness_kb_wiki_get",
        "harness_kb_graph_query", "harness_kb_graph_explain",
        "harness_kb_graph_path", "harness_kb_graph_find",
        "harness_kb_graph_community",
        "harness_kb_guide_toc", "harness_kb_guide_section",
        "harness_kb_guide_get", "harness_kb_guide_search",
    }
    assert set(ALL_TOOL_NAMES) == expected


def test_handler_for_each_tool():
    for name in ALL_TOOL_NAMES:
        assert name in _tool_handlers
        assert callable(_tool_handlers[name])


def test_each_tool_has_real_input_schema():
    from harness_kb.mcp import _TOOL_SCHEMAS
    assert set(_TOOL_SCHEMAS.keys()) == set(ALL_TOOL_NAMES), \
        "tool handlers and schemas must cover the same set of tools"
    for name, (desc, schema) in _TOOL_SCHEMAS.items():
        assert isinstance(desc, str) and desc.strip(), f"missing description for {name}"
        assert schema.get("type") == "object", f"{name} schema must be object"
        assert "additionalProperties" in schema, f"{name} schema must declare additionalProperties"
        assert schema["additionalProperties"] is False, \
            f"{name} schema must not allow additional properties"
        # Tools that take no arguments still have an empty properties dict
        assert "properties" in schema, f"{name} schema must declare properties"


def test_themes_handler(monkeypatch):
    from harness_kb import docs
    class T:
        def __init__(self, n, c): self.name = n; self.doc_count = c
    monkeypatch.setattr(docs, "list_themes", lambda: [T("agent-protocols", 5), T("claude-code", 3)])
    out = _tool_handlers["harness_kb_themes"]({})
    assert out == [{"name": "agent-protocols", "doc_count": 5},
                   {"name": "claude-code", "doc_count": 3}]


def test_docs_get_handler_returns_error_on_missing(monkeypatch):
    from harness_kb import docs
    def boom(p): raise FileNotFoundError(p)
    monkeypatch.setattr(docs, "get_doc", boom)
    out = _tool_handlers["harness_kb_docs_get"]({"path": "nope"})
    assert "error" in out
    assert out["error"] == "not_found"


def test_guide_get_without_confirm_returns_warning(monkeypatch):
    from harness_kb import guide
    monkeypatch.setattr(guide, "get_full", lambda confirm: {"warning": "warn", "toc": [], "token_estimate": 100} if not confirm else {"content": "x"})
    out = _tool_handlers["harness_kb_guide_get"]({"confirm": False})
    assert "warning" in out


def test_graph_query_schema_has_dfs_and_budget():
    """harness_kb_graph_query schema should expose dfs and budget properties."""
    from harness_kb.mcp import _TOOL_SCHEMAS
    _desc, schema = _TOOL_SCHEMAS["harness_kb_graph_query"]
    props = schema["properties"]
    assert "text" in props, "Missing 'text' property"
    assert "dfs" in props, "Missing 'dfs' property"
    assert "budget" in props, "Missing 'budget' property"
    assert props["dfs"]["type"] == "boolean"
    assert props["budget"]["type"] == "integer"


def test_graph_query_handler_returns_traversal_result():
    """_h_graph_query should return a dict with traversal, nodes, edges, rendered keys."""
    result = _tool_handlers["harness_kb_graph_query"]({"text": "agent harness components"})
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    for key in ("traversal", "start_labels", "nodes", "edges", "rendered", "truncated"):
        assert key in result, f"Missing key {key!r} in result"


def test_build_server_returns_object():
    server = build_server()
    assert server is not None


def test_async_list_tools_dispatch():
    # Exercises the _list_tools async handler that MCP clients actually call via the
    # server's request-handler registry.  We retrieve the registered handler for
    # ListToolsRequest directly (server.request_handlers is a public dict keyed on
    # request-type classes) and invoke it with asyncio.run — no extra dependency needed.
    import asyncio
    from mcp.types import ListToolsRequest, Tool

    server = build_server()
    handler = server.request_handlers[ListToolsRequest]

    req = ListToolsRequest(method="tools/list")
    result = asyncio.run(handler(req))

    # The handler returns a ServerResult wrapping ListToolsResult; tools live at .root.tools
    tools = result.root.tools
    assert isinstance(tools, list), "expected a list of Tool objects"
    assert len(tools) == 16, f"expected 16 tools, got {len(tools)}"
    assert all(isinstance(t, Tool) for t in tools), "all items must be Tool instances"
    tool_names = {t.name for t in tools}
    assert tool_names == set(ALL_TOOL_NAMES)
