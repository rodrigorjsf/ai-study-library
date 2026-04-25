# tools/harness-kb/tests/test_adapt_guide.py
import pytest
from harness_kb.build.adapt_guide import adapt


def test_replace_graphify_query():
    src = '/graphify query "smart zone"'
    out = adapt(src)
    assert "/graphify" not in out
    assert 'harness-kb graph query "smart zone"' in out


def test_replace_graphify_path():
    src = '/graphify path "Node A" "Node B"'
    out = adapt(src)
    assert 'harness-kb graph path "Node A" "Node B"' in out


def test_replace_graphify_explain():
    src = '/graphify explain "Smart Zone"'
    out = adapt(src)
    assert 'harness-kb graph explain "Smart Zone"' in out


def test_replace_graphify_mcp():
    src = "see `/graphify --mcp` for integration"
    out = adapt(src)
    assert "/graphify" not in out
    assert "harness-kb --mcp" in out


def test_replace_graphify_out_path_to_graph_command():
    src = "Inspect `graphify-out/graph.json` to see nodes."
    out = adapt(src)
    assert "graphify-out/graph.json" not in out
    assert "harness-kb graph" in out


def test_replace_graphify_out_wiki_link():
    src = "See `graphify-out/wiki/Smart_Zone.md` for the page."
    out = adapt(src)
    assert "graphify-out/wiki" not in out
    assert "harness-kb wiki get Smart_Zone" in out


def test_ai_docs_paths_unchanged():
    src = "See `ai/docs/agent-protocols/mcp.md` for details."
    out = adapt(src)
    assert "ai/docs/agent-protocols/mcp.md" in out


def test_post_adapt_no_graphify_residual():
    src = (
        "Run /graphify query \"x\". Then /graphify path \"A\" \"B\". "
        "Inspect graphify-out/graph.json. See graphify-out/wiki/Index.md. "
        "Use /graphify --mcp."
    )
    out = adapt(src)
    assert "/graphify" not in out
    assert "graphify-out/" not in out
    assert "harness-kb" in out


def test_replace_graphify_out_graph_report():
    src = 'all 21 in `graphify-out/GRAPH_REPORT.md`'
    out = adapt(src)
    assert "graphify-out/GRAPH_REPORT.md" not in out
    assert "data/graph/GRAPH_REPORT.md" in out


def test_remove_graphify_out_graph_html_bullet_line():
    src = "### Knowledge Graph\n\n- `graphify-out/graph.html` — interactive visualization\n- next item\n"
    out = adapt(src)
    assert "graphify-out/graph.html" not in out
    assert "next item" in out


def test_remove_graphify_out_manifest_json_bullet_line():
    src = "### Knowledge Graph\n\n- `graphify-out/manifest.json` — corpus snapshot for incremental `--update`\n- next item\n"
    out = adapt(src)
    assert "graphify-out/manifest.json" not in out
    assert "next item" in out


def test_post_adapt_no_graphify_out_residual_new_patterns():
    # All three new graphify-out/ patterns in one shot
    src = (
        "all 21 in `graphify-out/GRAPH_REPORT.md`\n"
        "- `graphify-out/graph.html` — interactive visualization\n"
        "- `graphify-out/manifest.json` — corpus snapshot for incremental `--update`\n"
        "Other text here.\n"
    )
    out = adapt(src)
    assert "graphify-out/" not in out
    assert "data/graph/GRAPH_REPORT.md" in out
    assert "Other text here." in out
