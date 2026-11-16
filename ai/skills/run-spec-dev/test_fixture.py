import contextlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DEV = Path(__file__).resolve().parent
KIT = DEV.parent / "run-spec"
MATERIALIZE = DEV / "materialize_fixture.py"
FIXTURE = DEV / "fixture"
RECIPE = ".claude/skills/verify-todo"
SPEC = ".scratch/todo-housekeeping"
ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}


def git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, env=ENV, capture_output=True, text=True, check=True).stdout


def run(*command, cwd=None, env=ENV):
    return subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True)


@contextlib.contextmanager
def materialized():
    result = run(sys.executable, "-I", str(MATERIALIZE))
    assert (result.returncode, result.stderr) == (0, ""), result
    lines = result.stdout.splitlines()
    assert len(lines) == 1 and result.stdout.endswith("\n"), result.stdout
    repo = Path(lines[0])
    try:
        yield repo
    finally:
        shutil.rmtree(repo, ignore_errors=True)


template_files = git(DEV, "ls-files", "--", "fixture").splitlines()
assert any(Path(name).parts[1:2] == ("dot-claude",) for name in template_files), template_files
assert not any(".claude" in Path(name).parts for name in template_files), template_files
assert not (FIXTURE / ".claude").exists()

with materialized() as repo:
    assert repo.is_absolute() and repo.is_dir(), repo
    assert len(git(repo, "log", "--oneline").splitlines()) == 1
    assert git(repo, "status", "--porcelain") == ""

    assert (repo / RECIPE / "SKILL.md").is_file()
    assert not (repo / "dot-claude").exists()

    tracker_heading = (repo / "docs/agents/issue-tracker.md").read_text().splitlines()[0]
    assert tracker_heading == "# Issue tracker: Local Markdown", tracker_heading
    git(repo, "ls-files", "--error-unmatch", f"{SPEC}/spec.md", f"{SPEC}/issues")

    readiness = run(sys.executable, "-I", str(KIT / "readiness.py"), "--repo", str(repo), "--spec", SPEC)
    assert (readiness.returncode, readiness.stderr) == (0, ""), readiness
    assert "- found: .claude/skills/verify-todo/" in readiness.stdout.splitlines(), readiness.stdout

    oracle = run(sys.executable, "-I", str(KIT / "tickets.py"), "--tracker", "local", "--spec", SPEC,
                 "--work-branch", "HEAD", "--failures-dir", os.devnull, cwd=repo)
    assert (oracle.returncode, oracle.stderr) == (0, ""), oracle
    listed = json.loads(oracle.stdout)
    assert [ticket["id"] for ticket in listed["tickets"]] == ["01", "02", "03"], listed
    assert listed["ready"] == ["01", "02"], listed

    suite = run(sys.executable, "-I", "test_todo.py", cwd=repo)
    assert (suite.returncode, suite.stdout, suite.stderr) == (0, "ok\n", ""), suite

    feature_map = (repo / RECIPE / "feature-map.md").read_text()
    proofs = re.findall(r"^- Proves: `([^`]+)`$", feature_map, re.M)
    assert 2 <= len(proofs) <= 3, proofs
    assert len(re.findall(r"^## ", feature_map, re.M)) == len(proofs), feature_map
    for proof in proofs:
        assert "python3 -I -S todo.py" in proof, proof
        proved = run("bash", "-c", proof, cwd=repo)
        assert proved.returncode == 0, (proof, proved)
    assert git(repo, "status", "--porcelain") == ""

with materialized() as broken_repo:
    (broken_repo / "todo.py").write_text("import sys\nsys.exit(1)\n")
    for proof in proofs:
        assert run("bash", "-c", proof, cwd=broken_repo).returncode != 0, proof

with tempfile.TemporaryDirectory() as home:
    install_env = {**os.environ, "HOME": home}
    install_env.pop("CLAUDE_HOME", None)
    installed = run("bash", str(KIT / "install.sh"), env=install_env)
    assert installed.returncode == 0, installed
    installed_files = sorted(path.relative_to(home).as_posix() for path in Path(home).rglob("*") if path.is_file())
    development_files = git(DEV, "ls-files").splitlines()
    assert development_files, development_files
    leaked = [name for name in installed_files for source in development_files if name.endswith(f"/{source}")]
    assert leaked == [], leaked
    assert sorted(path.name for path in (Path(home) / ".claude/skills").iterdir()) == ["follow-up-issue", "run-spec"]

print("ok")
