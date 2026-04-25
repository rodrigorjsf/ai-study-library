# tools/harness-kb/src/harness_kb/build/build.py
from __future__ import annotations
import datetime as _dt
import json
import shutil
import subprocess
from pathlib import Path

from harness_kb.build.adapt_guide import adapt
from harness_kb.chunking import chunk_markdown
from harness_kb.search import BM25SearchIndex
from harness_kb.manifest import Manifest, save_manifest


REQUIRED_THEMES = [
    "agent-protocols", "agentic-engineering", "analysis", "claude", "claude-code",
    "context-engineering", "cursor", "general-llm", "harness-engineering",
    "human-layer-project", "long-context-research", "mcp", "shared",
    "spec-driven-development", "structured-outputs", "tool-calling",
]
_RESEARCH_DOC_REL = "dev/research/2026-04-25-harness-engineering-research.md"
_PLAYBOOK_FILENAME = "harness-engineering-playbook.md"


class BuildError(Exception):
    pass


def _git_sha(source: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(source), "rev-parse", "HEAD"], text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _validate_source(source: Path) -> None:
    docs_root = source / "ai" / "docs"
    if not docs_root.exists():
        raise BuildError(f"source missing ai/docs/: {source}")
    missing = [t for t in REQUIRED_THEMES if not (docs_root / t).is_dir()]
    if missing:
        raise BuildError(f"missing themes: {missing}")
    if not (source / "graphify-out" / "graph.json").exists():
        raise BuildError("source missing graphify-out/graph.json")
    if not (source / _RESEARCH_DOC_REL).exists():
        raise BuildError(f"source missing research doc at {_RESEARCH_DOC_REL}")


def _check_graph_freshness(source: Path) -> None:
    graphify_manifest = source / "graphify-out" / "manifest.json"
    if not graphify_manifest.exists():
        raise BuildError("graph stale: graphify-out/manifest.json missing — run /graphify update first")
    manifest_mtime = graphify_manifest.stat().st_mtime
    docs_root = source / "ai" / "docs"
    for p in docs_root.rglob("*.md"):
        if p.stat().st_mtime > manifest_mtime:
            raise BuildError(
                f"graph stale: {p.relative_to(source)} is newer than graphify-out/manifest.json. "
                "Run '/graphify update' inside Claude Code from "
                f"{source}, then re-run 'harness-kb build'."
            )


def _stage_data(source: Path, out_dir: Path) -> None:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    # ai_docs
    shutil.copytree(source / "ai" / "docs", out_dir / "ai_docs")
    # graph
    (out_dir / "graph").mkdir()
    shutil.copy(source / "graphify-out" / "graph.json", out_dir / "graph" / "graph.json")
    rep = source / "graphify-out" / "GRAPH_REPORT.md"
    if rep.exists():
        shutil.copy(rep, out_dir / "graph" / "GRAPH_REPORT.md")
    # wiki
    wiki_src = source / "graphify-out" / "wiki"
    if wiki_src.exists():
        shutil.copytree(wiki_src, out_dir / "wiki")
    else:
        (out_dir / "wiki").mkdir()


def _adapt_and_copy_playbook(source: Path, out_dir: Path) -> None:
    src_doc = source / _RESEARCH_DOC_REL
    raw = src_doc.read_text()
    adapted = adapt(raw)
    if "/graphify" in adapted:
        raise BuildError("adaptation failed: residual /graphify references remain in playbook")
    if "harness-kb" not in adapted:
        raise BuildError("adaptation produced playbook with no harness-kb references — check rules")
    guide_dir = out_dir / "guide"
    guide_dir.mkdir(exist_ok=True)
    (guide_dir / _PLAYBOOK_FILENAME).write_text(adapted)


def _build_index(out_dir: Path) -> int:
    chunks = []
    for p in (out_dir / "ai_docs").rglob("*.md"):
        rel = p.relative_to(out_dir).as_posix()  # e.g. "ai_docs/.../foo.md"
        chunks.extend(chunk_markdown(p.read_text(), rel))
    pb = out_dir / "guide" / _PLAYBOOK_FILENAME
    if pb.exists():
        rel = pb.relative_to(out_dir).as_posix()
        chunks.extend(chunk_markdown(pb.read_text(), rel))
    idx = BM25SearchIndex.build(chunks)
    index_dir = out_dir / "index"
    index_dir.mkdir()
    idx.save(index_dir / "bm25_index.pkl", index_dir / "chunks.json")
    return len(chunks)


def _post_validate(out_dir: Path) -> None:
    pb = out_dir / "guide" / _PLAYBOOK_FILENAME
    if "/graphify" in pb.read_text():
        raise BuildError("post-build validation: /graphify residual in playbook")
    BM25SearchIndex.load(
        out_dir / "index" / "bm25_index.pkl",
        out_dir / "index" / "chunks.json",
    )


def build_data(
    source: Path,
    out_dir: Path,
    version: str,
    no_staleness_check: bool = False,
    no_graph_refresh: bool = True,  # always true; graph refresh is manual
) -> None:
    _validate_source(source)
    if not no_staleness_check:
        _check_graph_freshness(source)
    _stage_data(source, out_dir)
    _adapt_and_copy_playbook(source, out_dir)
    _build_index(out_dir)
    # write manifest
    docs_root = out_dir / "ai_docs"
    themes = sorted(p.name for p in docs_root.iterdir() if p.is_dir())
    doc_count = sum(1 for _ in docs_root.rglob("*.md"))
    graph_payload = json.loads((out_dir / "graph" / "graph.json").read_text())
    manifest = Manifest(
        version=version,
        source_commit_sha=_git_sha(source),
        build_date=_dt.date.today().isoformat(),
        doc_count=doc_count,
        graph_node_count=len(graph_payload.get("nodes", [])),
        themes=themes,
    )
    save_manifest(manifest, out_dir)
    _post_validate(out_dir)
