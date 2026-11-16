import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

TICKETS = Path(__file__).resolve().parent / "tickets.py"
ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}

ISSUES = {
    "01-parse-input.md": "# 01 — Parse input\n\n**Blocked by:** None (can start immediately)\n\n**Status:** ready-for-agent\n",
    "02-render-output.md": "# 02 — Render output, Blocked by: 05, Status: draft\n\nSee Status: ok below.\n\nBlocked by: 01\n\nStatus: ready-for-agent\n",
    "03-export-report.md": "# 03 — Export report\n\nBlocked by: 99\n\nStatus: ready-for-agent\n",
    "04-pick-a-format.md": "# 04 — Pick a format\n\nBlocked by: None\n\nStatus: needs-info\n",
    "05-ship-package.md": "# 05 — Ship package\n\nBlocked by: 02\n\nStatus: ready-for-agent\n",
    "06-seed-data.md": "# 06 — Seed data\n\nBlocked by: none\n\nStatus: resolved\n",
}


def git(repo, *args):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
                   cwd=repo, env=ENV, capture_output=True, text=True, check=True)


def oracle(repo, failures, spec=".scratch/demo", work="spec/demo"):
    r = subprocess.run([sys.executable, "-I", str(TICKETS), "--tracker", "local", "--spec", spec,
                        "--work-branch", work, "--failures-dir", str(failures)],
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
    assert all("criteria" not in ticket for ticket in out["tickets"]), out["tickets"]
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

with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as failures:
    repo = Path(tmp)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "commit", "-q", "--allow-empty", "-m", "root")
    git(repo, "switch", "-q", "-c", "feature/x")
    for slug in ("a", "b"):
        (repo / f".scratch/{slug}/issues").mkdir(parents=True)
        (repo / f".scratch/{slug}/spec.md").write_text(f"# {slug}\n")
        (repo / f".scratch/{slug}/issues/01-work.md").write_text("# 01 — Work\n\nBlocked by: none\n\nStatus: ready-for-agent\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "specs a and b")
    git(repo, "commit", "-q", "--allow-empty", "-m", "feat: a work", "--trailer", "Spec: a", "--trailer", "Ticket: 01")

    out, t = oracle(repo, failures, ".scratch/b", "feature/x")
    assert out["slug"] == "b" and t["01"]["done"] is False and out["ready"] == ["01"], out
    out, t = oracle(repo, failures, ".scratch/a", "feature/x")
    assert out["slug"] == "a" and t["01"]["done"] is True and out["remaining"] == [], out

    git(repo, "commit", "-q", "--allow-empty", "-m", "feat: b work", "--trailer", "spec: b", "--trailer", "ticket: 01")
    out, t = oracle(repo, failures, ".scratch/b", "feature/x")
    assert t["01"]["done"] is True and out["remaining"] == [], out


def criteria(repo, spec, tracker="local", env=ENV):
    r = subprocess.run([sys.executable, "-I", str(TICKETS), "--tracker", tracker, "--spec", spec, "--criteria"],
                       cwd=repo, env=env, capture_output=True, text=True)
    assert (r.returncode, r.stderr) == (0, ""), r
    return json.loads(r.stdout)


LOCAL_CRITERIA_TICKETS = {
    "01-template-shape.md": (
        "# 01 — Template shape\n\n**What to build:** the thing\n\n**Blocked by:** None (can start immediately)\n\n"
        "**Status:** ready-for-agent\n\n"
        "- [ ] Runs `tool --flag` and prints `ok`.\n- [x] A checked box with `span`.\n"
        "- [ ] **Bold** lead without any code\n- [X] Capital X and `code`\n* [ ] star bullet\n+ [ ] plus bullet with `x`\n"
    ),
    "02-wrapped.md": (
        "# 02 — Wrapped\n\n**Blocked by:** 01\n\n**Status:** ready-for-agent\n\n"
        "- [ ] First line\n  continues here with `span`\n\n- [ ] Lists:\n  - `a`\n  - plain\n- [ ] Last one\n\n"
        "**Notes:** a paragraph that is not part of the last criterion\n"
    ),
    "03-draft.md": "# 03 — Draft\n\n**Blocked by:** none\n\n**Status:** needs-info\n\n- [ ] Not run yet, with `span`\n",
    "04-no-criteria.md": "# 04 — No criteria\n\n**Blocked by:** none\n\n**Status:** ready-for-agent\n\nJust prose, and [ ] not a bullet.\n- [ ]\n- plain bullet\n",
    "05-resolved.md": "# 05 — Resolved\n\nBlocked by: none\n\nStatus: resolved\n\n- [x] Done long ago\n",
}

with tempfile.TemporaryDirectory() as tmp:
    repo = Path(tmp)
    git(repo, "init", "-q", "-b", "main")
    issues = repo / ".scratch/crit/issues"
    issues.mkdir(parents=True)
    (repo / ".scratch/crit/spec.md").write_text("# Crit\n")
    for name, text in LOCAL_CRITERIA_TICKETS.items():
        (issues / name).write_text(text)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "tickets")

    assert criteria(repo, ".scratch/crit") == {"slug": "crit", "spec": ".scratch/crit/spec.md", "tickets": [
        {"id": "01", "in_scope": True, "criteria": [
            "Runs `tool --flag` and prints `ok`.", "A checked box with `span`.", "**Bold** lead without any code",
            "Capital X and `code`", "star bullet", "plus bullet with `x`"]},
        {"id": "02", "in_scope": True, "criteria": ["First line continues here with `span`", "Lists: - `a` - plain", "Last one"]},
        {"id": "03", "in_scope": False, "criteria": ["Not run yet, with `span`"]},
        {"id": "04", "in_scope": True, "criteria": []},
        {"id": "05", "in_scope": True, "criteria": ["Done long ago"]},
    ]}, "local tickets"

    (issues / "02-wrapped.md").write_bytes(LOCAL_CRITERIA_TICKETS["02-wrapped.md"].replace("\n", "\r\n").encode())
    assert criteria(repo, ".scratch/crit/spec.md")["tickets"][1]["criteria"] == [
        "First line continues here with `span`", "Lists: - `a` - plain", "Last one"], "crlf file, spec.md path"

    without_oracle_flags = subprocess.run([sys.executable, "-I", str(TICKETS), "--tracker", "local", "--spec", ".scratch/crit"],
                                          cwd=repo, env=ENV, capture_output=True, text=True)
    assert without_oracle_flags.returncode == 2 and without_oracle_flags.stdout == "", without_oracle_flags

FAKE_GH = (
    "import json, os, sys\n"
    "fixture = os.environ.get('FAKE_GH')\n"
    "if not fixture:\n"
    "    sys.exit('fake gh: no fixture')\n"
    "data = json.load(open(fixture))\n"
    "issues = data['issues']\n"
    "args = sys.argv[1:]\n"
    "if args[:2] == ['repo', 'view']:\n"
    "    print('o/r')\n"
    "elif args[:2] == ['issue', 'list']:\n"
    "    print(json.dumps([{'number': i['number'], 'body': i['body']} for i in issues.values()]))\n"
    "elif args[:2] == ['issue', 'view'] and args[2] == data['spec']:\n"
    "    print(data['title'])\n"
    "elif args[:2] == ['issue', 'view'] and args[4] == 'state':\n"
    "    print(issues.get(args[2], {'state': 'OPEN'})['state'])\n"
    "elif args[:2] == ['issue', 'view']:\n"
    "    print(json.dumps(issues[args[2]]))\n"
    "elif args[0] == 'api':\n"
    "    print('')\n"
    "else:\n"
    "    sys.exit('fake gh: unexpected ' + ' '.join(args))\n"
)


def fake_gh_env(bin_dir, fixture_dir, data):
    gh = Path(bin_dir) / "gh"
    gh.write_text(f"#!{sys.executable}\n{FAKE_GH}")
    gh.chmod(gh.stat().st_mode | stat.S_IXUSR)
    fixture = Path(fixture_dir) / "gh.json"
    fixture.write_text(json.dumps(data))
    return {**ENV, "PATH": f"{bin_dir}{os.pathsep}{ENV['PATH']}", "FAKE_GH": str(fixture)}


def github_issue(number, body, state="OPEN", labels=("ready-for-agent",)):
    return {"number": number, "title": f"Ticket {number}", "state": state, "body": body,
            "labels": [{"name": name} for name in labels]}


GITHUB_BODY = (
    "## Parent\n\n#6\n\n## What to build\n\n- [ ] A checkbox outside the criteria section, with `span`\n\n"
    "## Acceptance criteria\n\n- [ ] Runs `a`.\n- [x] **Bold** checked criterion\n- [ ] Wrapped\n  `b` on the next line\n\n"
    "### Sub heading\n\n- [ ] Under a sub heading `c`\n\n## Blocked by\n\n- #12\n\n- [ ] A checkbox after the section\n"
)

with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bin_dir, tempfile.TemporaryDirectory() as fixture_dir:
    repo = Path(tmp)
    git(repo, "init", "-q", "-b", "main")
    env = fake_gh_env(bin_dir, fixture_dir, {"spec": "6", "title": "Spec: demo", "issues": {
        "13": github_issue(13, GITHUB_BODY),
        "14": github_issue(14, "## Parent\r\n\r\n#6\r\n\r\n## Acceptance criteria\r\n\r\n- [ ] Windows line ends with `span`\r\n"
                               "- [ ] and none here\r\n\r\n## Blocked by\r\n\r\nNone\r\n", labels=("needs-info",)),
        "15": github_issue(15, "## Parent\n\n#6\n\n## What to build\n\nNo criteria section.\n", state="CLOSED", labels=()),
        "16": github_issue(16, "Part of #6\n\n## acceptance CRITERIA\n\n* [ ] Lowercase heading `x`\n"),
    }})
    out = criteria(repo, "#6", "github", env)
    assert (out["slug"], out["spec"]) == ("6-spec-demo", "#6"), out
    assert out["tickets"] == [
        {"id": "#13", "in_scope": True, "criteria": ["Runs `a`.", "**Bold** checked criterion", "Wrapped `b` on the next line",
                                                      "Under a sub heading `c`"]},
        {"id": "#14", "in_scope": False, "criteria": ["Windows line ends with `span`", "and none here"]},
        {"id": "#15", "in_scope": True, "criteria": []},
        {"id": "#16", "in_scope": True, "criteria": ["Lowercase heading `x`"]},
        {"id": "#12", "in_scope": False, "criteria": []},
    ], out["tickets"]

print("ok")
