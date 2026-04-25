# tools/harness-kb/src/harness_kb/wiki.py
from __future__ import annotations
from pathlib import Path
from harness_kb.manifest import get_data_dir


def _wiki_dir() -> Path:
    return get_data_dir() / "wiki"


def list_wiki_pages() -> list[str]:
    return sorted(p.stem for p in _wiki_dir().glob("*.md"))


def get_wiki_page(name: str) -> str:
    p = _wiki_dir() / f"{name}.md"
    if not p.exists():
        raise FileNotFoundError(f"wiki page not found: {name}")
    return p.read_text()
