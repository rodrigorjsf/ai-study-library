import json
import os
import random
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


PROPERTY_SEED = int(os.environ.get("RUN_SPEC_PROPERTY_SEED", "20261115"))
PROPERTY_CASES = 300
LOCAL_SPEC_SIZE = 75
GITHUB_SPEC = 6
TITLE_WORDS = ("parser cache render export billing ledger socket widget gadget queue retry backoff avatar bundler session "
               "token invoice report import schema router handler worker metric cursor buffer filter mapper loader").split()
CRITERION_WORDS = ("prints", "rejects", "accepts", "exits", "lists", "writes", "reads", "keeps", "skips", "each", "every",
                   "ticket", "output", "line", "file", "result", "error", "count", "when", "with", "after")
CRITERION_SPANS = ("`tool --flag`", "`ok`", "**bold**", "`a/b.py`", "Status: draft", "Blocked by: 99")
LOCAL_STATUSES = {"ready-for-agent": (True, False), "resolved": (True, True), "done": (True, True),
                  "closed": (True, True), "needs-info": (False, False), "draft": (False, False)}
LOCAL_STATUS_CHOICES = ("ready-for-agent",) * 4 + tuple(LOCAL_STATUSES)
LOCAL_DECOYS = ("See Status: draft and Blocked by: 99 for context.", "- plain bullet, not a checkbox",
                "A [ ] mid-line box and `span`.", "Plain text.")
GITHUB_DECOYS = ("- [ ] A checkbox in the description, with `span`", "Status: resolved",
                 "Follows the decision in #{other}.", "Mentions Blocked by: #{other} mid-line, with `code`.", "Plain text.")
FAKE_GH_SH = (
    "#!/bin/sh\n"
    'case "$1 $2 $5" in\n'
    '"repo view "*) echo o/r;;\n'
    '"issue list "*) cat "$FAKE_GH_DIR/list.json";;\n'
    '"issue view title") cat "$FAKE_GH_DIR/title.txt";;\n'
    '"issue view state") echo OPEN;;\n'
    '"issue view "*) cat "$FAKE_GH_DIR/issue-$3.json";;\n'
    '"api "*) ;;\n'
    '*) echo "fake gh: unexpected $*" >&2; exit 1;;\n'
    "esac\n"
)


def chooser(rng):
    return (lambda options: options[0]) if rng is None else rng.choice


def phrase(rng):
    return " ".join(rng.choice(CRITERION_WORDS) for _ in range(rng.randint(2, 8)))


def criterion_text(rng):
    words = phrase(rng).split(" ")
    for _ in range(rng.randint(0, 2)):
        words.insert(rng.randint(0, len(words)), rng.choice(CRITERION_SPANS))
    return " ".join(words)


def prose_lines(rng, decoys):
    return [phrase(rng).capitalize() + "."] + [rng.choice(decoys).format(other=rng.randint(1, 999))
                                               for _ in range(rng.randint(0, 2))]


def unique_titles(rng, count):
    titles = set()
    while len(titles) < count:
        titles.add(" ".join(rng.sample(TITLE_WORDS, 2)))
    return sorted(titles, key=lambda title: rng.random())


def criteria_lines(texts, rng):
    pick = chooser(rng)
    lines = []
    for text in texts:
        indent = " " * pick((0, 0, 1, 2, 3))
        words = text.split(" ")
        pieces = [text]
        if rng is not None and len(words) > 1 and rng.random() < 0.4:
            cuts = sorted(rng.sample(range(1, len(words)), rng.randint(1, min(2, len(words) - 1))))
            pieces = [" ".join(words[start:end]) for start, end in zip([0, *cuts], [*cuts, len(words)])]
        lines.append(f"{indent}{pick(('-', '*', '+'))}{' ' * pick((1, 1, 2))}[{pick((' ', 'x', 'X'))}]"
                     f"{' ' * pick((1, 1, 2))}{pieces[0]}{pick(('', '', '  '))}")
        for piece in pieces[1:]:
            lines += [""] * pick((0, 0, 0, 1)) + [f"{indent}  {piece}"]
        lines += [""] * pick((0, 0, 0, 1, 2))
    return lines


def join_blocks(head, blocks, rng):
    pick = chooser(rng)
    lines = list(head)
    for block in blocks:
        lines += ([""] * pick((1, 1, 2, 3, 4)) if lines else []) + block
    lines += [""] * pick((0, 0, 1, 2))
    text = "\n".join(lines) + "\n"
    return text.replace("\n", "\r\n") if rng is not None and rng.random() < 0.2 else text


def maybe_shuffled(rng, blocks):
    blocks = list(blocks)
    if rng is not None and rng.random() < 0.7:
        rng.shuffle(blocks)
    return blocks


def in_variant_order(rng, items):
    items = list(items)
    if rng is not None:
        rng.shuffle(items)
    return items


def local_models(rng, size):
    titles = unique_titles(rng, size)
    return [{"id": i + 1, "title": titles[i], "status": rng.choice(LOCAL_STATUS_CHOICES),
             "blockers": sorted(rng.sample(range(1, i + 1), min(i, rng.choice((0, 0, 1, 1, 2, 3))))),
             "criteria": [criterion_text(rng) for _ in range(rng.choice((0, 1, 2, 3, 4)))],
             "prose": prose_lines(rng, LOCAL_DECOYS)} for i in range(size)]


def local_expectation(model):
    in_scope, done = LOCAL_STATUSES[model["status"]]
    return {"in_scope": in_scope, "done": done, "blockers": [f"{b:02d}" for b in model["blockers"]],
            "criteria": model["criteria"]}


def local_blocked_by(model, by_id, rng):
    pick = chooser(rng)
    if not model["blockers"]:
        return pick(("None (can start immediately)", "None", "none", "None - nothing blocks it"))
    order = in_variant_order(rng, model["blockers"])
    numbers = [f"{b:02d}" for b in order]
    titles = [by_id[b]["title"] for b in order]
    return pick((", ".join(numbers), " and ".join(numbers), "Tickets " + ", ".join(numbers),
                 ", ".join(str(b) for b in order), ", ".join(titles), ", ".join(t.capitalize() for t in titles),
                 ", ".join(f"{n} ({t})" for n, t in zip(numbers, titles)), " and ".join(t.upper() for t in titles)))


def local_text(model, by_id, rng=None):
    pick = chooser(rng)
    title_line = f"# {model['id']:02d}{pick((' —', ':', ' -'))} {model['title'].capitalize()}"
    bold = pick(("**", ""))
    blocked = f"{bold}Blocked by:{bold}{' ' * pick((1, 1, 2, 3))}{local_blocked_by(model, by_id, rng)}"
    bold = pick(("**", ""))
    status = model["status"]
    status_line = f"{bold}Status:{bold}{' ' * pick((1, 1, 2, 3))}{pick((status, status, status.capitalize(), status.upper()))}"
    blocks = [[f"**What to build:** {model['prose'][0]}"], [blocked], [status_line]]
    if model["criteria"]:
        blocks.append(criteria_lines(model["criteria"], rng))
    blocks += [[line] for line in model["prose"][1:]]
    return join_blocks([title_line], maybe_shuffled(rng, blocks), rng)


def github_models(rng, count):
    models = []
    for i in range(count):
        earlier = rng.sample(range(i), min(i, rng.choice((0, 0, 1, 1, 2, 3))))
        outside = [3000 + rng.randint(0, 9)] if rng.random() < 0.15 else []
        models.append({"canonical": 1000 + i, "variant": 2000 + i, "closed": rng.random() < 0.1,
                       "labels": rng.choice((("ready-for-agent",), ("ready-for-agent",), ("needs-info",), ())),
                       "blockers": sorted(1000 + j for j in earlier) + outside,
                       "criteria": [criterion_text(rng) for _ in range(rng.choice((0, 1, 2, 3, 4)))],
                       "prose": prose_lines(rng, GITHUB_DECOYS)})
    return models


def github_expectation(model):
    return {"in_scope": model["closed"] or "ready-for-agent" in model["labels"], "done": model["closed"],
            "blockers": sorted(f"#{n}" for n in model["blockers"]), "criteria": model["criteria"]}


def github_blocked_blocks(model, rng):
    pick = chooser(rng)
    refs = [f"#{n}" for n in in_variant_order(rng, model["blockers"])]
    heading = pick(("## Blocked by", "## Blocked By", "## BLOCKED BY", "## Blocked by  "))
    if not refs:
        return pick(([[heading, "", "None (can start immediately)"]], [[heading, "", "None"]],
                     [["Blocked by: None"]], [["**Blocked by:** None"]], []))
    joined = ", ".join(refs)
    return pick(([[heading, "", *[f"- {ref}" for ref in refs]]], [[heading, "", joined]],
                 [[heading, "", *[f"- {ref} (must land first)" for ref in refs]]],
                 [[f"Blocked by: {joined}"]], [[f"**Blocked by:** {joined}"]],
                 [[heading, "", *[f"- {ref}" for ref in refs]], [f"Blocked by: {joined}"]]))


def github_body(model, rng=None):
    pick = chooser(rng)
    parent_as_line = pick((False, True))
    what = [pick(("## What to build", "## WHAT TO BUILD")), ""]
    for index, line in enumerate(model["prose"]):
        what += ([""] if index else []) + [line]
    criteria_heading = pick(("## Acceptance criteria", "## Acceptance Criteria", "## ACCEPTANCE CRITERIA", "## Acceptance criteria  "))
    headed = [] if parent_as_line else [[pick(("## Parent", "## PARENT")), "", f"#{GITHUB_SPEC}"]]
    headed += [what, [criteria_heading, "", *criteria_lines(model["criteria"], rng)]]
    blocked = github_blocked_blocks(model, rng)
    headed += [block for block in blocked if block[0].startswith("## ")]
    blocks = maybe_shuffled(rng, headed)
    for block in (block for block in blocked if not block[0].startswith("## ")):
        blocks.insert(rng.randint(0, len(blocks)) if rng is not None else len(blocks), block)
    return join_blocks([f"Part of #{GITHUB_SPEC}"] if parent_as_line else [], blocks, rng)


def write_fake_gh(bin_dir, fixture_dir, issues):
    gh = Path(bin_dir) / "gh"
    gh.write_text(FAKE_GH_SH)
    gh.chmod(gh.stat().st_mode | stat.S_IXUSR)
    fixture = Path(fixture_dir)
    (fixture / "title.txt").write_text("Spec: property\n")
    (fixture / "list.json").write_text(json.dumps([{"number": n, "body": issue["body"]} for n, issue in issues.items()]))
    for number, issue in issues.items():
        (fixture / f"issue-{number}.json").write_text(json.dumps(issue))
    return {**ENV, "PATH": f"{bin_dir}{os.pathsep}{ENV['PATH']}", "FAKE_GH_DIR": str(fixture)}


def init_property_repo(repo):
    git(repo, "init", "-q", "-b", "main")
    git(repo, "commit", "-q", "--allow-empty", "-m", "root")


def ticket_facets(script, repo, tracker, spec, env, failures_dir):
    runs = {}
    for mode, flags in (("criteria", ["--criteria"]), ("oracle", ["--work-branch", "main", "--failures-dir", failures_dir])):
        r = subprocess.run([sys.executable, "-I", str(script), "--tracker", tracker, "--spec", spec, *flags],
                           cwd=repo, env=env, capture_output=True, text=True)
        try:
            runs[mode] = {t["id"]: t for t in json.loads(r.stdout)["tickets"]}
        except (ValueError, KeyError, TypeError):
            return {}, [f"{tracker} {mode} run: exit {r.returncode}, stderr {r.stderr.strip()[-300:]}"]
    return {ident: {"in_scope": t.get("in_scope"), "criteria": t.get("criteria"),
                    "done": runs["oracle"].get(ident, {}).get("done"), "blockers": runs["oracle"].get(ident, {}).get("blockers")}
            for ident, t in runs["criteria"].items()}, []


def differences(subject, got, want, texts):
    found = []
    for ident, expected in want.items():
        actual = got.get(ident)
        for facet, value in expected.items():
            if actual is None or actual[facet] != value:
                found.append(f"{subject} {ident} {facet}: {None if actual is None else actual[facet]!r}, expected {value!r}\n"
                             f"{texts.get((subject, ident), '')}")
    return found


def summarised(found, limit=3):
    return [] if not found else [f"{len(found)} differences", *found[:limit]]


def local_formatting_invariance(rng, script, cases):
    details = []
    with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as failures_dir:
        repo = Path(tmp)
        init_property_repo(repo)
        for group in range(max(1, cases // LOCAL_SPEC_SIZE)):
            models = local_models(rng, LOCAL_SPEC_SIZE)
            by_id = {model["id"]: model for model in models}
            texts, facets = {}, {}
            for form, style in (("canonical", None), ("variant", rng)):
                root = repo / ".scratch" / f"{form}{group}"
                (root / "issues").mkdir(parents=True)
                (root / "spec.md").write_text("# Spec\n")
                for model in models:
                    ident = f"{model['id']:02d}"
                    texts[form, ident] = local_text(model, by_id, style)
                    (root / "issues" / f"{ident}-{model['title'].replace(' ', '-')}.md").write_bytes(texts[form, ident].encode())
                facets[form], problems = ticket_facets(script, repo, "local", f".scratch/{form}{group}", ENV, failures_dir)
                details += problems
            want = {f"{model['id']:02d}": local_expectation(model) for model in models}
            details += summarised(differences("canonical", facets["canonical"], want, texts))
            details += summarised(differences("variant", facets["variant"], facets["canonical"] or want, texts))
    return details


def github_formatting_invariance(rng, script, cases):
    models = github_models(rng, cases)
    issues, texts = {}, {}
    for model in models:
        for form, number, style in (("canonical", model["canonical"], None), ("variant", model["variant"], rng)):
            body = github_body(model, style)
            texts[form, f"#{model['canonical']}"] = body
            issues[number] = github_issue(number, body, "CLOSED" if model["closed"] else "OPEN", model["labels"])
    with tempfile.TemporaryDirectory() as tmp:
        repo, failures_dir, bin_dir, fixture_dir = (Path(tmp) / name for name in ("repo", "failures", "bin", "fixtures"))
        for directory in (repo, failures_dir, bin_dir, fixture_dir):
            directory.mkdir()
        init_property_repo(repo)
        env = write_fake_gh(bin_dir, fixture_dir, issues)
        facets, details = ticket_facets(script, repo, "github", str(GITHUB_SPEC), env, str(failures_dir))
    if details:
        return details
    want = {f"#{model['canonical']}": github_expectation(model) for model in models}
    canonical = {ident: facets.get(ident) for ident in want}
    variant = {f"#{model['canonical']}": facets.get(f"#{model['variant']}") for model in models}
    details += summarised(differences("canonical", canonical, want, texts))
    details += summarised(differences("variant", variant, canonical if all(canonical.values()) else want, texts))
    return details


PROPERTIES = {"local-ticket-formatting": local_formatting_invariance,
              "github-ticket-formatting": github_formatting_invariance}


def run_properties(script, seed, cases=PROPERTY_CASES):
    return {name: prop(random.Random(f"{seed}/{name}"), script, cases) for name, prop in PROPERTIES.items()}


def failure_report(results, seed):
    return [f"property {name} failed with seed {seed}; rerun with RUN_SPEC_PROPERTY_SEED={seed}\n" + "\n".join(details)
            for name, details in results.items() if details]


SILENT_ORACLE = "import json\nprint(json.dumps({'slug': 's', 'spec': 's', 'tickets': []}))\n"

with tempfile.TemporaryDirectory() as tmp:
    broken_oracle = Path(tmp) / "tickets.py"
    broken_oracle.write_text(SILENT_ORACLE)
    failed = run_properties(broken_oracle, 7, LOCAL_SPEC_SIZE)
    assert all(failed.values()), failed
    assert all("with seed 7;" in text for text in failure_report(failed, 7)), failure_report(failed, 7)
    assert failed == run_properties(broken_oracle, 7, LOCAL_SPEC_SIZE)
    assert failed != run_properties(broken_oracle, 8, LOCAL_SPEC_SIZE)

results = run_properties(TICKETS, PROPERTY_SEED)
for name, details in results.items():
    print(f"property {name}: {PROPERTY_CASES} cases, seed {PROPERTY_SEED}, {'FAILED' if details else 'passed'}")
if any(results.values()):
    sys.exit("\n\n".join(failure_report(results, PROPERTY_SEED)))

print("ok")
