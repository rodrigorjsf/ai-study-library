# tools/harness-kb/tests/test_cli.py
from click.testing import CliRunner
from harness_kb.cli import main


def test_version_flag():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "harness-kb" in result.output
    assert "0.1.0" in result.output


def test_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "themes" in result.output
    assert "docs" in result.output
    assert "graph" in result.output
    assert "wiki" in result.output
    assert "guide" in result.output
    assert "init" in result.output


def test_themes_subcommand_help():
    runner = CliRunner()
    result = runner.invoke(main, ["themes", "--help"])
    assert result.exit_code == 0


def test_docs_search_help():
    runner = CliRunner()
    result = runner.invoke(main, ["docs", "search", "--help"])
    assert result.exit_code == 0
    assert "--limit" in result.output
    assert "--theme" in result.output


def test_init_dry_run(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["init", "--project", str(tmp_path), "--dry-run"])
    assert result.exit_code == 0
    assert "harness-kb" in result.output
    assert not (tmp_path / "CLAUDE.md").exists()


def test_uninit_noop_on_empty(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["uninit", "--project", str(tmp_path)])
    assert result.exit_code == 0
    assert "noop" in result.output.lower()


def test_mcp_flag_recognized(monkeypatch):
    """--mcp dispatches to the MCP runner; we check it doesn't crash on parse."""
    runner = CliRunner()
    called = {"count": 0}

    def fake_run_mcp():
        called["count"] += 1

    import harness_kb.cli as cli_mod
    monkeypatch.setattr(cli_mod, "_run_mcp_server", fake_run_mcp)
    result = runner.invoke(main, ["--mcp"])
    assert called["count"] == 1
    assert result.exit_code == 0


def test_build_subcommand_hidden_from_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert "build" not in result.output  # hidden=True keeps it out of --help


def test_build_subcommand_help_directly():
    runner = CliRunner()
    result = runner.invoke(main, ["build", "--help"])
    assert result.exit_code == 0
    assert "--source" in result.output
    assert "--out-dir" in result.output
