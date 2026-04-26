# tools/harness-kb/src/harness_kb/cli.py
from __future__ import annotations
import json
import sys
from pathlib import Path

import click

from harness_kb import __version__, docs, graph, wiki, guide, init as init_module


def _print_json(payload) -> None:
    click.echo(json.dumps(payload, indent=2, ensure_ascii=False))


def _run_mcp_server() -> None:
    from harness_kb.mcp import run_stdio_server
    run_stdio_server()


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version and bundled data SHA.")
@click.option("--mcp", is_flag=True, help="Launch stdio MCP server.")
@click.pass_context
def main(ctx: click.Context, version: bool, mcp: bool) -> None:
    """harness-kb — portable knowledge base of agent/harness/context-engineering reference material."""
    if version:
        try:
            from harness_kb.manifest import load_manifest
            m = load_manifest()
            click.echo(f"harness-kb {__version__} (data=ai-study-library@{m.source_commit_sha[:7]}, built {m.build_date})")
        except FileNotFoundError:
            click.echo(f"harness-kb {__version__} (data not yet bundled)")
        return
    if mcp:
        _run_mcp_server()
        return
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command()
def themes() -> None:
    """List ai/docs themes with doc counts."""
    payload = [{"name": t.name, "doc_count": t.doc_count} for t in docs.list_themes()]
    _print_json(payload)


@main.group()
def docs_cmd():
    """Document retrieval commands."""


main.add_command(docs_cmd, name="docs")


@docs_cmd.command("list")
@click.option("--theme", default=None, help="Filter by theme name.")
def docs_list_cmd(theme: str | None) -> None:
    payload = [{"path": d.path, "theme": d.theme, "title": d.title, "size_tokens": d.size_tokens}
               for d in docs.list_docs(theme=theme)]
    _print_json(payload)


@docs_cmd.command("get")
@click.argument("path")
def docs_get_cmd(path: str) -> None:
    click.echo(docs.get_doc(path))


@docs_cmd.command("section")
@click.argument("path")
@click.argument("heading")
def docs_section_cmd(path: str, heading: str) -> None:
    click.echo(docs.get_section(path, heading))


@docs_cmd.command("search")
@click.argument("query")
@click.option("--limit", default=10, type=int)
@click.option("--theme", default=None)
def docs_search_cmd(query: str, limit: int, theme: str | None) -> None:
    hits = docs.search_docs(query, limit=limit, theme=theme)
    payload = [{"path": h.path, "heading": h.heading, "score": h.score, "snippet": h.snippet}
               for h in hits]
    _print_json(payload)


@main.group()
def wiki_cmd():
    """Wiki retrieval commands."""


main.add_command(wiki_cmd, name="wiki")


@wiki_cmd.command("list")
def wiki_list_cmd() -> None:
    _print_json(wiki.list_wiki_pages())


@wiki_cmd.command("get")
@click.argument("name")
def wiki_get_cmd(name: str) -> None:
    click.echo(wiki.get_wiki_page(name))


@main.group()
def graph_cmd():
    """Graph query commands."""


main.add_command(graph_cmd, name="graph")


@graph_cmd.command("query")
@click.argument("text")
@click.option("--dfs", is_flag=True, default=False, help="DFS traversal (default: BFS)")
@click.option("--budget", default=2000, type=int, help="Token budget for output")
def graph_query_cmd(text: str, dfs: bool, budget: int) -> None:
    result = graph.query(text, mode=("dfs" if dfs else "bfs"), budget=budget)
    click.echo(result["rendered"])


@graph_cmd.command("explain")
@click.argument("label")
def graph_explain_cmd(label: str) -> None:
    _print_json(graph.explain(label))


@graph_cmd.command("path")
@click.argument("from_label")
@click.argument("to_label")
def graph_path_cmd(from_label: str, to_label: str) -> None:
    p = graph.shortest_path(from_label, to_label)
    _print_json({"path": p, "length": len(p) - 1})


@graph_cmd.command("find")
@click.argument("pattern")
def graph_find_cmd(pattern: str) -> None:
    payload = [{"label": n.label, "id": n.id, "community": n.community}
               for n in graph.find_nodes(pattern)]
    _print_json(payload)


@graph_cmd.command("community")
@click.argument("name")
def graph_community_cmd(name: str) -> None:
    payload = [{"label": n.label, "id": n.id} for n in graph.community_nodes(name)]
    _print_json(payload)


@main.group(invoke_without_command=True)
@click.option("--confirm", is_flag=True, help="Print the full playbook (~30K tokens).")
@click.pass_context
def guide_cmd(ctx: click.Context, confirm: bool):
    """Playbook retrieval commands."""
    if ctx.invoked_subcommand is None:
        out = guide.get_full(confirm=confirm)
        if "content" in out:
            click.echo(out["content"])
        else:
            _print_json(out)


main.add_command(guide_cmd, name="guide")


@guide_cmd.command("toc")
def guide_toc_cmd() -> None:
    payload = [{"level": s.level, "heading": s.heading, "anchor": s.anchor}
               for s in guide.toc()]
    _print_json(payload)


@guide_cmd.command("section")
@click.argument("heading")
def guide_section_cmd(heading: str) -> None:
    _print_json(guide.get_section(heading))


@guide_cmd.command("search")
@click.argument("query")
@click.option("--limit", default=10, type=int)
def guide_search_cmd(query: str, limit: int) -> None:
    hits = guide.search_guide(query, limit=limit)
    _print_json([{"path": h.path, "heading": h.heading, "score": h.score, "snippet": h.snippet}
                 for h in hits])


@main.command("init")
@click.option("--project", default=".", help="Project directory (default cwd).")
@click.option("--dry-run", is_flag=True, help="Print the change without writing.")
def init_cmd(project: str, dry_run: bool) -> None:
    out = init_module.inject(Path(project), version=__version__, dry_run=dry_run)
    click.echo(out)


@main.command("uninit")
@click.option("--project", default=".", help="Project directory (default cwd).")
def uninit_cmd(project: str) -> None:
    click.echo(init_module.uninject(Path(project)))


@main.command("build", hidden=True)
@click.option("--source", required=True, help="Path to ai-study-library/ checkout.")
@click.option("--out-dir", required=True, help="Output dir for the bundled data (typically src/harness_kb/data).")
@click.option("--version", default=__version__, help="Version string written into manifest.")
@click.option("--no-staleness-check", is_flag=True, help="Skip the graph-staleness check.")
def build_cmd(source: str, out_dir: str, version: str, no_staleness_check: bool) -> None:
    """Maintainer-only: rebuild bundled data from a parent ai-study-library/ checkout."""
    from harness_kb.build.build import build_data
    build_data(
        source=Path(source).resolve(),
        out_dir=Path(out_dir).resolve(),
        version=version,
        no_staleness_check=no_staleness_check,
    )
    click.echo(f"build complete: {out_dir}")
