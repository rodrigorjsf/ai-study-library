import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

TICKETS = Path(__file__).resolve().parent / "tickets.py"
ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}

ISSUES = {
    "01-parse-input.md": "# 01 — Parse input\n\n**Blocked by:** None (can start immediately)\n\n**Status:** ready-for-agent\n",
    "02-render-output.md": "# 02 — Render output\n\nBlocked by: 01\n\nStatus: ready-for-agent\n",
    "03-export-report.md": "# 03 — Export report\n\nBlocked by: 99\n\nStatus: ready-for-agent\n",
    "04-pick-a-format.md": "# 04 — Pick a format\n\nBlocked by: None\n\nStatus: needs-info\n",
    "05-ship-package.md": "# 05 — Ship package\n\nBlocked by: 02\n\nStatus: ready-for-agent\n",
    "06-seed-data.md": "# 06 — Seed data\n\nBlocked by: none\n\nStatus: resolved\n",
}


def git(repo, *args):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
                   cwd=repo, env=ENV, capture_output=True, text=True, check=True)


def oracle(repo, failures):
    r = subprocess.run([sys.executable, "-I", str(TICKETS), "--tracker", "local", "--spec", ".scratch/demo",
                        "--work-branch", "spec/demo", "--failures-dir", str(failures)],
                       cwd=repo, env=ENV, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    return out, {t["id"]: t for t in out["tickets"]}


with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as failures:
    repo = Path(tmp)
    git(repo, "init", "-q", "-b", "main")
    earlier = repo / ".scratch/earlier/issues"
    earlier.mkdir(parents=True)
    (repo / ".scratch/earlier/spec.md").write_text("# Earlier\n")
    (earlier / "01-old-work.md").write_text("# 01 — Old work\n\nBlocked by: none\n\nStatus: resolved\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "earlier spec")
    git(repo, "switch", "-q", "-c", "spec/earlier")
    git(repo, "commit", "-q", "--allow-empty", "-m", "feat: old work", "--trailer", "Ticket: 01")
    git(repo, "switch", "-q", "main")
    git(repo, "merge", "-q", "--no-ff", "spec/earlier", "-m", "merge spec/earlier")

    issues = repo / ".scratch/demo/issues"
    issues.mkdir(parents=True)
    (repo / ".scratch/demo/spec.md").write_text("# Demo\n")
    for name, text in ISSUES.items():
        (issues / name).write_text(text)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "tickets")
    git(repo, "switch", "-q", "-c", "spec/demo")

    out, t = oracle(repo, failures)
    assert (out["slug"], out["spec"]) == ("demo", ".scratch/demo/spec.md"), out
    assert t["01"]["done"] is False, t["01"]
    assert out["ready"] == ["01"], out["ready"]
    assert t["06"]["done"] is True and t["06"]["ready"] is False, t["06"]

    git(repo, "branch", "-m", "main", "trunk")
    git(repo, "update-ref", "refs/remotes/origin/trunk", "trunk")
    git(repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/trunk")
    out, t = oracle(repo, failures)
    assert t["01"]["done"] is False and out["ready"] == ["01"], (t["01"], out["ready"])
    assert [t[i]["blockers"] for i in ("01", "02", "03", "05")] == [[], ["01"], ["99"], ["02"]], t
    assert t["03"]["ready"] is False
    assert t["04"]["in_scope"] is False and "ready" not in t["04"], t["04"]
    assert out["remaining"] == ["01", "02", "03", "05"], out["remaining"]

    git(repo, "commit", "-q", "--allow-empty", "-m", "feat: parse input", "--trailer", "Ticket: 01")
    out, t = oracle(repo, failures)
    assert t["01"]["done"] is True
    assert out["ready"] == ["02"], out["ready"]
    assert t["03"]["ready"] is False
    assert "04" not in out["remaining"] and out["remaining"] == ["02", "03", "05"], out["remaining"]

    for k in (1, 2):
        (Path(failures) / f"02-attempt{k}.md").write_text("failed\n")
    out, t = oracle(repo, failures)
    assert t["02"]["attempts"] == 2 and t["02"]["skipped"] is True, t["02"]
    assert t["05"]["skipped"] is True and t["05"]["attempts"] == 0, t["05"]
    assert "02" not in out["ready"] and "05" not in out["ready"], out["ready"]
    assert out["ready"] == [] and out["remaining"] == ["03"], out
    assert t["03"]["ready"] is False

print("ok")
