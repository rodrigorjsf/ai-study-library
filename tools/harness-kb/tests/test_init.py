# tools/harness-kb/tests/test_init.py
from pathlib import Path
import pytest
from harness_kb.init import render_block, inject, uninject, _BEGIN_RE, _END_RE


def test_render_block_includes_version():
    block = render_block("0.1.0")
    assert "<!-- harness-kb v0.1.0 BEGIN -->" in block
    assert "<!-- harness-kb v0.1.0 END -->" in block
    assert "Harness Knowledge Base" in block
    assert "harness-kb themes" in block
    assert "harness-kb guide toc" in block


def test_inject_creates_file_when_absent(tmp_path: Path):
    project = tmp_path
    out = inject(project, version="0.1.0")
    md = (project / "CLAUDE.md").read_text()
    assert "<!-- harness-kb v0.1.0 BEGIN -->" in md
    assert "created" in out.lower()


def test_inject_appends_to_existing_no_marker(tmp_path: Path):
    project = tmp_path
    (project / "CLAUDE.md").write_text("# My Project\n\nExisting content.")
    inject(project, version="0.1.0")
    md = (project / "CLAUDE.md").read_text()
    assert md.startswith("# My Project")
    assert "Existing content." in md
    assert "<!-- harness-kb v0.1.0 BEGIN -->" in md


def test_inject_idempotent_replaces_existing_block(tmp_path: Path):
    project = tmp_path
    inject(project, version="0.1.0")
    first = (project / "CLAUDE.md").read_text()
    inject(project, version="0.1.0")
    second = (project / "CLAUDE.md").read_text()
    assert first == second


def test_inject_replaces_old_version_block(tmp_path: Path):
    project = tmp_path
    inject(project, version="0.1.0")
    inject(project, version="0.2.0")
    md = (project / "CLAUDE.md").read_text()
    assert "<!-- harness-kb v0.2.0 BEGIN -->" in md
    assert "<!-- harness-kb v0.1.0 BEGIN -->" not in md


def test_inject_dry_run_does_not_write(tmp_path: Path):
    project = tmp_path
    inject(project, version="0.1.0", dry_run=True)
    assert not (project / "CLAUDE.md").exists()


def test_inject_dry_run_returns_preview_text(tmp_path: Path):
    project = tmp_path
    out = inject(project, version="0.1.0", dry_run=True)
    assert "<!-- harness-kb v0.1.0 BEGIN -->" in out


def test_inject_unbalanced_markers_aborts(tmp_path: Path):
    project = tmp_path
    (project / "CLAUDE.md").write_text(
        "# Proj\n\n<!-- harness-kb v0.1.0 BEGIN -->\nstuff but no end marker"
    )
    with pytest.raises(RuntimeError):
        inject(project, version="0.2.0")


def test_uninject_removes_block(tmp_path: Path):
    project = tmp_path
    (project / "CLAUDE.md").write_text("# Proj\n\nKeep this.")
    inject(project, version="0.1.0")
    uninject(project)
    md = (project / "CLAUDE.md").read_text()
    assert "<!-- harness-kb" not in md
    assert "Keep this." in md


def test_uninject_no_marker_is_noop(tmp_path: Path):
    project = tmp_path
    (project / "CLAUDE.md").write_text("# Proj\n\nNo block here.")
    out = uninject(project)
    md = (project / "CLAUDE.md").read_text()
    assert "No block here." in md
    assert "no harness-kb block" in out.lower() or "noop" in out.lower()
