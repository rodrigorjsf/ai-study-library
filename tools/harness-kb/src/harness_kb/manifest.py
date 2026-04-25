# tools/harness-kb/src/harness_kb/manifest.py
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Manifest:
    version: str
    source_commit_sha: str
    build_date: str
    doc_count: int
    graph_node_count: int
    themes: list[str]


def get_data_dir() -> Path:
    return Path(__file__).parent / "data"


def load_manifest(data_dir: Path | None = None) -> Manifest:
    if data_dir is None:
        data_dir = get_data_dir()
    manifest_path = data_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"manifest.json not found at {manifest_path}")
    payload = json.loads(manifest_path.read_text())
    return Manifest(**payload)


def save_manifest(manifest: Manifest, data_dir: Path) -> None:
    payload = {
        "version": manifest.version,
        "source_commit_sha": manifest.source_commit_sha,
        "build_date": manifest.build_date,
        "doc_count": manifest.doc_count,
        "graph_node_count": manifest.graph_node_count,
        "themes": manifest.themes,
    }
    (data_dir / "manifest.json").write_text(json.dumps(payload, indent=2))
