import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

KIT = Path(__file__).resolve().parent
RUNLOG = KIT / "runlog.py"
sys.dont_write_bytecode = True
sys.path.insert(0, str(KIT))
from test_support import cursor_table_rows, review_report
ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}

FULL_RECORD = ["--slug", "demo", "--pr", "https://github.com/o/r/pull/7", "--rounds", "2",
               "--findings", "acceptance=1", "standards=3", "security=0", "uxaix=2", "design=1", "hygiene=4",
               "--dismissals", "5", "--unverified", "1", "--unproven", "3", "--done", "4", "--skipped", "1", "--stuck", "2"]


def git(repo, *args):
    r = subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
                       cwd=repo, env=ENV, capture_output=True, text=True, check=True)
    return r.stdout.strip()


def runlog(repo, *args):
    return subprocess.run([sys.executable, "-I", str(RUNLOG), *args], cwd=repo, env=ENV, capture_output=True, text=True)


def new_repo(tmp, branch="main"):
    repo = Path(tmp)
    git(repo, "init", "-q", "-b", branch)
    git(repo, "commit", "-q", "--allow-empty", "-m", "base")
    return repo


def lines(path):
    return path.read_text().splitlines()


with tempfile.TemporaryDirectory() as tmp:
    repo = new_repo(tmp)
    head = git(repo, "rev-parse", "HEAD")
    metrics = repo / ".git/run-spec/metrics.tsv"
    assert not metrics.exists()

    r = runlog(repo, "record", *FULL_RECORD, "--head", head)
    assert (r.returncode, r.stdout, r.stderr) == (0, "", ""), r
    assert len(lines(metrics)) == 1, metrics.read_text()
    fields = lines(metrics)[0].split("\t")
    assert re.fullmatch(r"at=\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", fields[0]), fields[0]
    assert fields[1:] == ["slug=demo", "pr=https://github.com/o/r/pull/7", f"head={head}", "rounds=2",
                          "findings.acceptance=1", "findings.standards=3", "findings.security=0",
                          "findings.uxaix=2", "findings.design=1", "findings.hygiene=4",
                          "dismissals=5", "unverified=1", "done=4", "skipped=1", "stuck=2", "unproven=3"], fields
    first = lines(metrics)[0]

    r = runlog(repo, "record", "--slug", "second", "--head", head)
    assert r.returncode == 0, r
    assert len(lines(metrics)) == 2 and lines(metrics)[0] == first, metrics.read_text()
    assert lines(metrics)[1].split("\t")[1:] == [
        "slug=second", "pr=none", f"head={head}", "rounds=0", "findings.acceptance=0", "findings.standards=0",
        "findings.security=0", "findings.uxaix=0", "findings.design=0", "findings.hygiene=0",
        "dismissals=0", "unverified=0", "done=0", "skipped=0", "stuck=0", "unproven=0"], lines(metrics)[1]

    for bad in (["--slug", "x", "--head", "zz"], ["--slug", "a\tb", "--head", head],
                ["--slug", "x", "--head", head, "--rounds", "-1"],
                ["--slug", "x", "--head", head, "--unproven", "-1"], ["--slug", "x", "--head", head, "--unproven", "x"],
                ["--slug", "x", "--head", head, "--findings", "bogus=1"],
                ["--slug", "x", "--head", head, "--findings", "design=x"], ["--head", head]):
        r = runlog(repo, "record", *bad)
        assert r.returncode == 2 and r.stdout == "", (bad, r)
    assert len(lines(metrics)) == 2, metrics.read_text()

    worktree = repo.parent / (repo.name + "-wt")
    git(repo, "worktree", "add", "-q", "-b", "other", str(worktree))
    r = runlog(worktree, "record", "--slug", "from-worktree", "--head", head)
    assert r.returncode == 0, r
    assert len(lines(metrics)) == 3 and "slug=from-worktree" in lines(metrics)[2], metrics.read_text()
    assert not (worktree / ".git/run-spec").exists()
    assert git(repo, "status", "--porcelain") == ""
    git(repo, "worktree", "remove", "--force", str(worktree))


LEGACY_RECORD = ("at=2026-11-15T10:00:00Z\tslug=legacy\tpr=none\thead={head}\trounds=1\tfindings.acceptance=0"
                 "\tfindings.standards=2\tfindings.security=0\tfindings.uxaix=0\tfindings.design=1\tfindings.hygiene=0"
                 "\tdismissals=1\tunverified=0\tdone=2\tskipped=0\tstuck=0\n")

with tempfile.TemporaryDirectory() as tmp:
    repo = new_repo(tmp)
    head = git(repo, "rev-parse", "HEAD")
    metrics = repo / ".git/run-spec/metrics.tsv"
    metrics.parent.mkdir(parents=True)
    metrics.write_text(LEGACY_RECORD.format(head=head))
    legacy = metrics.read_text()

    r = runlog(repo, "record", "--slug", "after-legacy", "--head", head, "--unproven", "2")
    assert (r.returncode, r.stdout, r.stderr) == (0, "", ""), r
    assert lines(metrics)[0] == legacy.rstrip("\n"), metrics.read_text()
    assert lines(metrics)[1].endswith("\tunproven=2"), lines(metrics)[1]
    assert not list(metrics.parent.glob("metrics.tsv.corrupt-*"))

    r = runlog(repo, "reverts")
    assert (r.returncode, r.stdout, r.stderr) == (0, "", ""), r
    assert not list(metrics.parent.glob("metrics.tsv.corrupt-*"))


def topic(repo, name, base="main"):
    git(repo, "switch", "-q", "-c", name, base)
    (repo / f"{name}.txt").write_text(name)
    git(repo, "add", f"{name}.txt")
    git(repo, "commit", "-q", "-m", f"feat: {name}")
    head = git(repo, "rev-parse", "HEAD")
    git(repo, "switch", "-q", base)
    return head


def merge_commit(repo, name):
    git(repo, "merge", "-q", "--no-ff", name, "-m", f"Merge {name}")
    return git(repo, "rev-parse", "HEAD")


def marks(metrics):
    return {next(f for f in line.split("\t") if f.startswith("slug="))[5:]:
            [f for f in line.split("\t") if f.startswith("reverted=")] for line in lines(metrics)}


with tempfile.TemporaryDirectory() as tmp:
    repo = new_repo(tmp)
    metrics = repo / ".git/run-spec/metrics.tsv"
    heads = {}
    for name in ("reverted-merge", "kept-merge", "abbreviated", "never-merged"):
        heads[name] = topic(repo, name)
    merge_commit(repo, "reverted-merge")
    git(repo, "revert", "--no-edit", "-m", "1", "HEAD")
    revert_of_merge = git(repo, "rev-parse", "--short=7", "HEAD")
    merge_commit(repo, "kept-merge")
    heads["reverted-head"] = topic(repo, "reverted-head")
    git(repo, "merge", "-q", "--ff-only", "reverted-head")
    git(repo, "revert", "--no-edit", "HEAD")
    revert_of_head = git(repo, "rev-parse", "--short=7", "HEAD")
    abbreviated_merge = merge_commit(repo, "abbreviated")
    git(repo, "commit", "-q", "--allow-empty", "-m", "Revert abbreviated", "-m",
        f"This reverts commit {abbreviated_merge[:7]}.")
    revert_abbreviated = git(repo, "rev-parse", "--short=7", "HEAD")
    for name, head in heads.items():
        assert runlog(repo, "record", "--slug", name, "--head", head).returncode == 0
    before = metrics.read_text()

    r = runlog(repo, "reverts")
    assert r.returncode == 0 and r.stderr == "", r
    assert len(r.stdout.splitlines()) == 1, r.stdout
    assert marks(metrics) == {"reverted-merge": [f"reverted={revert_of_merge}"], "kept-merge": [],
                              "reverted-head": [f"reverted={revert_of_head}"],
                              "abbreviated": [f"reverted={revert_abbreviated}"], "never-merged": []}, metrics.read_text()
    assert [line.split("\t")[:-1] if "reverted=" in line else line.split("\t") for line in lines(metrics)] == [
        line.split("\t") for line in before.splitlines()], metrics.read_text()

    marked = metrics.read_text()
    r = runlog(repo, "reverts")
    assert (r.returncode, r.stdout, r.stderr) == (0, "", ""), r
    assert metrics.read_text() == marked


def asides(metrics):
    return sorted(metrics.parent.glob("metrics.tsv.corrupt-*"))


with tempfile.TemporaryDirectory() as tmp:
    repo = new_repo(tmp)
    head = git(repo, "rev-parse", "HEAD")
    metrics = repo / ".git/run-spec/metrics.tsv"
    assert runlog(repo, "record", "--slug", "good", "--head", head).returncode == 0
    good = metrics.read_text()
    CORRUPT_FILES = {
        "not a record": b"not a record\n",
        "missing fields": b"at=2026-11-15T10:00:00Z\tslug=x\n",
        "non-numeric count": good.replace("rounds=0", "rounds=many").encode(),
        "non-numeric unproven": good.replace("unproven=0", "unproven=many").encode(),
        "binary": b"\xff\xfe\x00\x01\n",
        "no final newline": good.rstrip("\n").encode(),
    }

    for kind, content in CORRUPT_FILES.items():
        metrics.write_bytes(content)
        r = runlog(repo, "record", "--slug", "after-corruption", "--head", head)
        assert r.returncode == 0 and r.stderr == "", (kind, r)
        assert len(r.stdout.splitlines()) == 1 and "corrupt" in r.stdout, (kind, r.stdout)
        assert len(lines(metrics)) == 1 and "slug=after-corruption" in lines(metrics)[0], (kind, metrics.read_text())
        assert content in [a.read_bytes() for a in asides(metrics)], kind
    assert len(asides(metrics)) == len(CORRUPT_FILES), asides(metrics)

    for kind, content in CORRUPT_FILES.items():
        asides_before = len(asides(metrics))
        metrics.write_bytes(content)
        r = runlog(repo, "reverts")
        assert r.returncode == 0 and r.stderr == "", (kind, r)
        assert len(r.stdout.splitlines()) == 1 and "corrupt" in r.stdout, (kind, r.stdout)
        assert metrics.read_bytes() == b"", (kind, metrics.read_bytes())
        assert len(asides(metrics)) == asides_before + 1, kind

    metrics.unlink()
    r = runlog(repo, "reverts")
    assert (r.returncode, r.stdout, r.stderr) == (0, "", ""), r
    assert not metrics.exists()


def reverted_merge_scenario(repo, base):
    head = topic(repo, "work", base=base)
    merged = merge_commit(repo, "work")
    assert runlog(repo, "record", "--slug", "work", "--head", head).returncode == 0
    git(repo, "revert", "--no-edit", "-m", "1", "HEAD")
    return merged, git(repo, "rev-parse", "HEAD")


with tempfile.TemporaryDirectory() as tmp:
    repo = new_repo(tmp, branch="master")
    metrics = repo / ".git/run-spec/metrics.tsv"
    _, reverted_tip = reverted_merge_scenario(repo, "master")
    r = runlog(repo, "reverts")
    assert r.returncode == 0 and len(r.stdout.splitlines()) == 1, r
    assert marks(metrics) == {"work": [f"reverted={reverted_tip[:7]}"]}, metrics.read_text()

with tempfile.TemporaryDirectory() as tmp:
    repo = new_repo(tmp, branch="trunk")
    metrics = repo / ".git/run-spec/metrics.tsv"
    merged, reverted_tip = reverted_merge_scenario(repo, "trunk")
    git(repo, "update-ref", "refs/remotes/origin/trunk", reverted_tip)
    git(repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/trunk")
    git(repo, "reset", "-q", "--hard", merged)
    r = runlog(repo, "reverts")
    assert r.returncode == 0 and len(r.stdout.splitlines()) == 1, r
    assert marks(metrics) == {"work": [f"reverted={reverted_tip[:7]}"]}, metrics.read_text()

with tempfile.TemporaryDirectory() as tmp:
    repo = new_repo(tmp, branch="develop")
    assert runlog(repo, "record", "--slug", "no-default-branch", "--head", git(repo, "rev-parse", "HEAD")).returncode == 0
    r = runlog(repo, "reverts")
    assert (r.returncode, r.stdout, r.stderr) == (0, "", ""), r

with tempfile.TemporaryDirectory() as tmp:
    for command in (["record", "--slug", "x", "--head", "a" * 40], ["reverts"]):
        r = runlog(tmp, *command)
        assert r.returncode != 0 and r.stdout == "" and "git" in r.stderr, (command, r)

def review_fields(metrics_line):
    keys = ("rounds", *(f"findings.{axis}" for axis in ("acceptance", "standards", "security", "uxaix", "design",
                                                        "hygiene")), "unverified")
    fields = dict(field.split("=", 1) for field in metrics_line.split("\t"))
    return tuple(int(fields[key]) for key in keys)


with tempfile.TemporaryDirectory() as tmp:
    (Path(tmp) / "repo").mkdir()
    repo = new_repo(Path(tmp) / "repo")
    head = git(repo, "rev-parse", "HEAD")
    metrics = repo / ".git/run-spec/metrics.tsv"
    state = Path(tmp) / "state"
    state.mkdir()

    r = runlog(repo, "record", "--slug", "no-reviews", "--head", head, "--state", str(state))
    assert (r.returncode, r.stdout, r.stderr) == (0, "", ""), r
    assert review_fields(lines(metrics)[-1]) == (0, 0, 0, 0, 0, 0, 0, 0), lines(metrics)[-1]

    (state / "review-1.md").write_text(review_report(Acceptance="COUNT: 2 blocking, 1 unverified",
                                                     Standards="COUNT: 1 proven, 3 unproven",
                                                     Security="COUNT: 1 blocking, 2 needs-human",
                                                     Design="COUNT: 2 proven, 1 unproven", Hygiene="COUNT: 1",
                                                     UX_AIX="COUNT: 4"))
    (state / "review-2.md").write_text(review_report(Acceptance="COUNT: 1 blocking, 4 unverified",
                                                     Standards="COUNT: 0 proven, 2 unproven"))
    (state / "review-10.md").write_text(review_report(Acceptance="COUNT: 0 blocking, 5 unverified"))
    (state / "review-1-fix.md").write_text("- S1 unproven\nCOUNT: 9\n")
    (state / "user-1-fix.md").write_text("COUNT: 9\n")
    (state / "review-3.partial").write_text("COUNT: 9\n")
    r = runlog(repo, "record", "--slug", "three-reviews", "--head", head, "--state", str(state), "--unproven", "2")
    assert (r.returncode, r.stdout, r.stderr) == (0, "", ""), r
    assert review_fields(lines(metrics)[-1]) == (3, 3, 1, 1, 4, 2, 1, 5), lines(metrics)[-1]
    assert lines(metrics)[-1].endswith("\tunproven=2"), lines(metrics)[-1]

    for overlapping in (["--rounds", "1"], ["--findings", "design=1"], ["--unverified", "1"]):
        r = runlog(repo, "record", "--slug", "both", "--head", head, "--state", str(state), *overlapping)
        assert r.returncode == 2 and r.stdout == "", (overlapping, r)

    recorded = metrics.read_text()
    (state / "review-11.md").write_text(review_report(Design="COUNT: 2"))
    r = runlog(repo, "record", "--slug", "malformed", "--head", head, "--state", str(state))
    assert r.returncode == 2 and r.stdout == "" and "review-11.md" in r.stderr, r
    assert metrics.read_text() == recorded


ROUND_ONE_FINDINGS = {
    "Acceptance": ['- [PASS] "list shows tasks" — `python3 todo.py list` → 1 task (A)',
                   '- [FAIL] "clear resets ids" — `python3 todo.py clear` → ids reused (A)',
                   '- [UNVERIFIED] "runs on Windows" — needs: a Windows host',
                   "scope-creep:",
                   "- todo.py:41 added a --force flag nobody asked for"],
    "Standards": ['- [hard] todo.py:12 no inline imports (CLAUDE.md) — import in a function. Fix: move it. '
                  'Proof: "no inline imports" (CLAUDE.md)',
                  "- [judgement] todo.py:30 possible Long Function — three stages. Fix: Extract Function"],
    "Security": ["- [HIGH] todo.py:50 path traversal (confidence 9/10) — `..` in the file name → read any file. "
                 "Fix: reject it",
                 "needs-human:",
                 "- todo.py:60 weak hash (confidence 4/10) — md5 for ids. Fix: sha256"],
    "UX/AIX": ["- [warning] todo.py:70 clear message — now: silent; expected: says how many. Fix: print the count",
               "deferred-to-build: none"],
    "Design": ["- [Strong] todo.py:5 shallow module — one caller. Deepening: merge it. "
               "Proof: `grep -c load todo.py` → 1"],
    "Hygiene": ["- todo.py:7: comment: # keeps\tthe id",
                "- docs/notes.md: markdown: added Markdown file"],
}
ROUND_ONE_COUNTS = {"Acceptance": "COUNT: 2 blocking, 1 unverified", "Standards": "COUNT: 1 proven, 1 unproven",
                    "Security": "COUNT: 1 blocking, 1 needs-human", "UX_AIX": "COUNT: 1",
                    "Design": "COUNT: 1 proven, 0 unproven", "Hygiene": "COUNT: 2"}
ROUND_ONE_FIX = """STATUS: GREEN
ROUND: 1
FINDINGS:
- A1 fixed — 1a2b3c4 ids are never reused after clear
- A2 dismissed — "added a --force flag nobody asked for" — "spec: --force clears without asking"
- S1 fixed — 2b3c4d5 moved the import to the top
- S2 unproven — no proof field — todo.py:30
- SEC1 fixed — 3c4d5e6 rejects `..` in the file name
- SEC2 needs-human — a person decides the hash
- UX1 follow-up — .scratch/follow-ups/issues/demo-1-wording.md
- D1 dismissed — the module has two callers now
- H1 fixed — 4d5e6f7 deleted the comment
- H2 dismissed — allow: docs/notes.md — "spec: the notes file"
TESTS: for f in test_*.py; do python3 -I "$f" || exit 1; done
ALLOWED: docs/notes.md
"""
ROUND_TWO_STANDARDS = ['- [hard] todo.py:3 no inline imports (CLAUDE.md) — import in a function. Fix: move it. '
                       'Proof: "no inline imports" (CLAUDE.md)']
ROUND_TEN_HYGIENE = ["- todo.py:90: comment: # again"]


def fixture_state(directory):
    state = Path(directory) / "demo-spec"
    state.mkdir()
    (state / "review-1.md").write_text(review_report(ROUND_ONE_FINDINGS, **ROUND_ONE_COUNTS))
    (state / "review-1-fix.md").write_text(ROUND_ONE_FIX)
    (state / "review-2.md").write_text(review_report({"Standards": ROUND_TWO_STANDARDS},
                                                     Standards="COUNT: 1 proven, 0 unproven"))
    (state / "review-2-fix.md").write_text("STATUS: GREEN\nROUND: 2\nFINDINGS:\n- S1 fixed — 5e6f708 moved it\n"
                                           "TESTS: green\nALLOWED: none\n")
    (state / "review-10.md").write_text(review_report({"Hygiene": ROUND_TEN_HYGIENE}, Hygiene="COUNT: 1"))
    (state / "review-10-fix.md").write_text("STATUS: GREEN\nROUND: 10\nFINDINGS:\n- H1 fixed — 6f70819 deleted it\n"
                                            "TESTS: green\nALLOWED: none\n")
    (state / "review-11.md").write_text(review_report())
    (state / "review-12.partial").write_text("COUNT: 9\n")
    return state


def finding_line(head, round_, axis, location, finding, outcome):
    return "\t".join(["slug=demo-spec", f"head={head}", f"round={round_}", f"axis={axis}", f"location={location}",
                      f"finding={finding}", f"outcome={outcome}"])


def expected_fixture_lines(head):
    def line(*fields):
        return finding_line(head, *fields)
    return [
        line(1, "acceptance", "-", '[FAIL] "clear resets ids" — `python3 todo.py clear` → ids reused (A)', "fixed"),
        line(1, "acceptance", "todo.py:41", "todo.py:41 added a --force flag nobody asked for", "dismissed"),
        line(1, "standards", "todo.py:12", '[hard] todo.py:12 no inline imports (CLAUDE.md) — import in a function. '
             'Fix: move it. Proof: "no inline imports" (CLAUDE.md)', "fixed"),
        line(1, "standards", "todo.py:30", "[judgement] todo.py:30 possible Long Function — three stages. "
             "Fix: Extract Function", "unproven"),
        line(1, "security", "todo.py:50", "[HIGH] todo.py:50 path traversal (confidence 9/10) — `..` in the file "
             "name → read any file. Fix: reject it", "fixed"),
        line(1, "security", "todo.py:60", "todo.py:60 weak hash (confidence 4/10) — md5 for ids. Fix: sha256",
             "needs-human"),
        line(1, "uxaix", "todo.py:70", "[warning] todo.py:70 clear message — now: silent; expected: says how many. "
             "Fix: print the count", "follow-up"),
        line(1, "design", "todo.py:5", "[Strong] todo.py:5 shallow module — one caller. Deepening: merge it. "
             "Proof: `grep -c load todo.py` → 1", "dismissed"),
        line(1, "hygiene", "todo.py:7", "todo.py:7: comment: # keeps the id", "fixed"),
        line(1, "hygiene", "-", "docs/notes.md: markdown: added Markdown file", "dismissed"),
        line(2, "standards", "todo.py:3", '[hard] todo.py:3 no inline imports (CLAUDE.md) — import in a function. '
             'Fix: move it. Proof: "no inline imports" (CLAUDE.md)', "fixed"),
        line(10, "hygiene", "todo.py:90", "todo.py:90: comment: # again", "fixed"),
    ]


with tempfile.TemporaryDirectory() as tmp:
    (Path(tmp) / "repo").mkdir()
    repo = new_repo(Path(tmp) / "repo")
    head = git(repo, "rev-parse", "HEAD")
    state = fixture_state(Path(tmp))
    findings = repo / ".git/run-spec/findings.tsv"
    assert not findings.exists()

    r = runlog(repo, "findings", "--state", str(state))
    assert (r.returncode, r.stdout, r.stderr) == (0, "", ""), r
    first_run = expected_fixture_lines(head)
    assert lines(findings) == first_run, findings.read_text()
    assert git(repo, "status", "--porcelain") == ""

    r = runlog(repo, "findings", "--state", str(state))
    assert (r.returncode, r.stdout, r.stderr) == (0, "", ""), r
    assert lines(findings) == first_run, findings.read_text()

    (state / "user-1-fix.md").write_text("STATUS: GREEN\nROUND: user-1\nFINDINGS:\n"
                                         "- U1 fixed — 5e6f708 renamed the flag\n"
                                         "- U2 dismissed — a new Markdown file breaks the no-Markdown rule\n"
                                         "TESTS: green\nALLOWED: none\n")
    git(repo, "commit", "-q", "--allow-empty", "-m", "after the user fix")
    later_head = git(repo, "rev-parse", "HEAD")
    r = runlog(repo, "findings", "--state", str(state))
    assert (r.returncode, r.stdout, r.stderr) == (0, "", ""), r
    assert lines(findings) == first_run + [
        finding_line(later_head, "user-1", "user", "-", "5e6f708 renamed the flag", "fixed"),
        finding_line(later_head, "user-1", "user", "-", "a new Markdown file breaks the no-Markdown rule",
                     "dismissed")], findings.read_text()

    (state / "user-2-fix.md").write_text("STATUS: GREEN\nROUND: user-2\nFINDINGS:\n- U1 fixed — 7081920 kept ids\n"
                                         "TESTS: green\nALLOWED: none\n")
    r = runlog(repo, "findings", "--state", str(state), "--head", "abcdef1")
    assert (r.returncode, r.stdout, r.stderr) == (0, "", ""), r
    assert lines(findings)[-1] == finding_line("abcdef1", "user-2", "user", "-", "7081920 kept ids", "fixed")
    assert len(lines(findings)) == len(first_run) + 3

    worktree = repo.parent / (repo.name + "-wt")
    git(repo, "worktree", "add", "-q", "-b", "other", str(worktree))
    (state / "user-3-fix.md").write_text("STATUS: GREEN\nROUND: user-3\nFINDINGS:\n- U1 fixed — 8192031 again\n"
                                         "TESTS: green\nALLOWED: none\n")
    r = runlog(worktree, "findings", "--state", str(state))
    assert (r.returncode, r.stdout, r.stderr) == (0, "", ""), r
    assert len(lines(findings)) == len(first_run) + 4, findings.read_text()
    assert not (worktree / ".git/run-spec").exists()
    assert git(repo, "status", "--porcelain") == ""
    git(repo, "worktree", "remove", "--force", str(worktree))


with tempfile.TemporaryDirectory() as tmp:
    (Path(tmp) / "repo").mkdir()
    repo = new_repo(Path(tmp) / "repo")
    findings = repo / ".git/run-spec/findings.tsv"
    state = Path(tmp) / "demo-spec"
    state.mkdir()

    r = runlog(repo, "findings", "--state", str(state))
    assert (r.returncode, r.stdout, r.stderr) == (0, "", ""), r
    (state / "review-1.md").write_text(review_report())
    r = runlog(repo, "findings", "--state", str(state))
    assert (r.returncode, r.stdout, r.stderr) == (0, "", ""), r
    assert not findings.exists()

    for bad in (["--state", str(state / "missing")], ["--state", str(state), "--head", "zz"], []):
        r = runlog(repo, "findings", *bad)
        assert r.returncode == 2 and r.stdout == "", (bad, r)
    assert not findings.exists()
    assert "runlog.py" in runlog(repo, "findings", "--state", str(state / "missing")).stderr

with tempfile.TemporaryDirectory() as tmp:
    r = runlog(tmp, "findings", "--state", tmp)
    assert r.returncode != 0 and r.stdout == "" and "git" in r.stderr, r


STANDARDS_FINDING = "- [hard] todo.py:12 no inline imports (CLAUDE.md) — import in a function. Fix: move it"
FIX_OF_ONE_STANDARDS = "STATUS: GREEN\nROUND: {n}\nFINDINGS:\n- S1 fixed — 1a2b3c4 moved it\nTESTS: green\nALLOWED: none\n"

with tempfile.TemporaryDirectory() as tmp:
    (Path(tmp) / "repo").mkdir()
    repo = new_repo(Path(tmp) / "repo")
    head = git(repo, "rev-parse", "HEAD")
    findings = repo / ".git/run-spec/findings.tsv"
    state = Path(tmp) / "demo-spec"
    state.mkdir()
    one_standards = review_report({"Standards": [STANDARDS_FINDING]}, Standards="COUNT: 1 proven, 0 unproven")

    (state / "review-1.md").write_text(one_standards)
    (state / "review-1-fix.md").write_text(FIX_OF_ONE_STANDARDS.format(n=1))
    (state / "review-2.md").write_text(one_standards.replace("COUNT: 1 proven, 0 unproven\n", ""))
    (state / "review-2-fix.md").write_text(FIX_OF_ONE_STANDARDS.format(n=2))
    (state / "review-3.md").write_text(one_standards)
    (state / "review-3-fix.md").write_text("STATUS: GREEN\nROUND: 3\nTESTS: green\n")
    (state / "review-4.md").write_text(review_report(
        {"Standards": [STANDARDS_FINDING, STANDARDS_FINDING.replace("12", "13")]},
        Standards="COUNT: 2 proven, 0 unproven"))
    (state / "review-4-fix.md").write_text(FIX_OF_ONE_STANDARDS.format(n=4))
    (state / "review-5-fix.md").write_text(FIX_OF_ONE_STANDARDS.format(n=5))
    (state / "review-6.md").write_bytes(b"\xff\xfe\x00\x01\n")
    (state / "review-7.md").write_text(one_standards)
    (state / "review-8.md").write_text(one_standards)
    (state / "review-8-fix.md").write_text("STATUS: GREEN\nROUND: 8\nFINDINGS:\n- S1 fixed — a\n- S1 dismissed — b\n")
    (state / "user-1-fix.md").write_text("STATUS: GREEN\nROUND: user-1\nFINDINGS:\n- U1 mended — it\n")

    r = runlog(repo, "findings", "--state", str(state))
    assert (r.returncode, r.stderr) == (0, ""), r
    reported = r.stdout.splitlines()
    assert len(reported) == 8, r.stdout
    for name in ("review-2.md", "review-3-fix.md", "review-4.md", "review-5.md", "review-6.md", "review-7.md",
                 "review-8-fix.md", "user-1-fix.md"):
        assert sum(name in line for line in reported) == 1, (name, r.stdout)
    assert lines(findings) == [
        finding_line(head, 1, "standards", "todo.py:12", STANDARDS_FINDING[2:], "fixed")], findings.read_text()

with tempfile.TemporaryDirectory() as tmp:
    (Path(tmp) / "repo").mkdir()
    repo = new_repo(Path(tmp) / "repo")
    findings = repo / ".git/run-spec/findings.tsv"
    state = Path(tmp) / "demo-spec"
    state.mkdir()
    clean_with_notes = review_report().replace(
        "COUNT: 0 proven, 0 unproven\n\n",
        "COUNT: 0 proven, 0 unproven\n\nNotes:\n- S1 is fixed by 1a2b3c4.\n- D2 stays a known dismissal.\n\n")
    (state / "review-1.md").write_text(clean_with_notes)

    r = runlog(repo, "findings", "--state", str(state))
    assert (r.returncode, r.stdout, r.stderr) == (0, "", ""), r
    assert not findings.exists() or lines(findings) == [], findings.read_text()


NOISY_ACCEPTANCE = [
    "recipe: none — feature map entries: none",
    "Shared evidence:",
    "- DASH = `out/dash.log`",
    "- GATE = `make check`. Result: green",
    '- [PASS] "list shows tasks" — `python3 todo.py list` → 1 task (A)',
    '- [FAIL] "story 15: the confirm step is documented" — `grep -n confirm todo.py` → no doc (A)',
    '- [FAIL] "clear resets ids" — `python3 todo.py clear` → ids reused (A)',
    "scope-creep:",
    "- todo.py:41 added a --force flag nobody asked for",
    "- todo.py:55 prints a banner nobody asked for",
    "Environment notes, not counted:",
    "- the build cache holds stale files",
    "Round-1 scope-creep lines rechecked on HEAD; both are gone:",
    "- todo.py:41 is gone",
    "HEAD: abcdef1",
]
NOISY_ACCEPTANCE_FIX = """STATUS: GREEN
ROUND: 1
FINDINGS:
- A1 dismissed — "story 15: the confirm step is documented" — `grep -n confirm todo.py` → no doc — Code explains itself
- A2 fixed — 1a2b3c4 ids are never reused after clear
- A3 follow-up — .scratch/follow-ups/issues/demo-1-force.md
- A4 needs-human — the owner decides the banner
- S1 fixed — 2b3c4d5 moved the import
TESTS: green
ALLOWED: none
"""
STANDARDS_WITH_NOTES = ["- none", "Verification (round 3):", "- S1 fixed, confirmed at todo.py:12",
                        "- I found no new comments in the range"]

with tempfile.TemporaryDirectory() as tmp:
    (Path(tmp) / "repo").mkdir()
    repo = new_repo(Path(tmp) / "repo")
    head = git(repo, "rev-parse", "HEAD")
    findings = repo / ".git/run-spec/findings.tsv"
    state = Path(tmp) / "demo-spec"
    state.mkdir()
    (state / "review-1.md").write_text(review_report(
        {"Acceptance": NOISY_ACCEPTANCE, "Standards": [STANDARDS_FINDING]},
        Acceptance="COUNT: 4 blocking, 0 unverified", Standards="COUNT: 1 proven, 0 unproven"))
    (state / "review-1-fix.md").write_text(NOISY_ACCEPTANCE_FIX)
    (state / "review-2.md").write_text(review_report({"Standards": STANDARDS_WITH_NOTES}))
    (state / "review-2-fix.md").write_text("STATUS: GREEN\nROUND: 2\nFINDINGS:\n- none\nTESTS: green\nALLOWED: none\n")
    (state / "review-3.md").write_text(review_report(
        {"Standards": [STANDARDS_FINDING], "Design": ["- [Strong] todo.py:5 shallow module. Proof: `grep -c x`",
                                                      "- a note the reviewer left"]},
        Standards="COUNT: 1 proven, 0 unproven", Design="COUNT: 1 proven, 0 unproven"))
    (state / "review-3-fix.md").write_text("STATUS: GREEN\nROUND: 3\nFINDINGS:\n- S1 fixed — 3c4d5e6 moved it\n"
                                           "- D1 dismissed — two callers\nTESTS: green\nALLOWED: none\n")
    (state / "review-4.md").write_text(review_report(
        {"Standards": [STANDARDS_FINDING], "Security": ["- [HIGH] todo.py:50 path traversal. Fix: reject it"]},
        Standards="COUNT: 1 proven, 0 unproven", Security="COUNT: 1 blocking, 0 needs-human"))
    (state / "review-4-fix.md").write_text("STATUS: GREEN\nROUND: 4\nFINDINGS:\n- SEC1 fixed — 4d5e6f7 rejects it\n"
                                           "TESTS: green\nALLOWED: none\n")
    (state / "review-5.md").write_text(review_report({"Acceptance": NOISY_ACCEPTANCE[4:7]}))

    r = runlog(repo, "findings", "--state", str(state))
    assert (r.returncode, r.stderr) == (0, ""), r
    reported = r.stdout.splitlines()
    assert len(reported) == 3, r.stdout
    assert "review-5.md" in reported[2] and "Acceptance" in reported[2] and "COUNT" in reported[2], reported
    assert "review-3.md" in reported[0] and "Design" in reported[0] and "COUNT" in reported[0], reported
    assert "review-4.md" in reported[1] and "Standards" in reported[1] and "S1" in reported[1], reported
    assert lines(findings) == [
        finding_line(head, 1, "acceptance", "-", '[FAIL] "story 15: the confirm step is documented" — '
                     "`grep -n confirm todo.py` → no doc (A)", "dismissed"),
        finding_line(head, 1, "acceptance", "-", '[FAIL] "clear resets ids" — `python3 todo.py clear` → ids reused (A)',
                     "fixed"),
        finding_line(head, 1, "acceptance", "todo.py:41", "todo.py:41 added a --force flag nobody asked for",
                     "follow-up"),
        finding_line(head, 1, "acceptance", "todo.py:55", "todo.py:55 prints a banner nobody asked for",
                     "needs-human"),
        finding_line(head, 1, "standards", "todo.py:12", STANDARDS_FINDING[2:], "fixed"),
        finding_line(head, 3, "standards", "todo.py:12", STANDARDS_FINDING[2:], "fixed"),
        finding_line(head, 4, "security", "todo.py:50", "[HIGH] todo.py:50 path traversal. Fix: reject it", "fixed"),
    ], findings.read_text()


CORRUPT_BUFFERS = {
    "not a record": b"not a record\n",
    "missing fields": b"slug=demo-spec\thead=abcdef1\n",
    "unknown outcome": finding_line("abcdef1", 1, "standards", "-", "text", "mended").encode() + b"\n",
    "unknown axis": finding_line("abcdef1", 1, "style", "-", "text", "fixed").encode() + b"\n",
    "bad round": finding_line("abcdef1", "first", "standards", "-", "text", "fixed").encode() + b"\n",
    "bad head": finding_line("zz", 1, "standards", "-", "text", "fixed").encode() + b"\n",
    "binary": b"\xff\xfe\x00\x01\n",
    "no final newline": finding_line("abcdef1", 1, "standards", "-", "text", "fixed").encode(),
}

with tempfile.TemporaryDirectory() as tmp:
    (Path(tmp) / "repo").mkdir()
    repo = new_repo(Path(tmp) / "repo")
    head = git(repo, "rev-parse", "HEAD")
    findings = repo / ".git/run-spec/findings.tsv"
    state = fixture_state(Path(tmp))

    def findings_asides():
        return sorted(findings.parent.glob("findings.tsv.corrupt-*"))

    for kind, content in CORRUPT_BUFFERS.items():
        findings.parent.mkdir(exist_ok=True)
        findings.write_bytes(content)
        r = runlog(repo, "findings", "--state", str(state))
        assert (r.returncode, r.stderr) == (0, ""), (kind, r)
        assert len(r.stdout.splitlines()) == 1 and "corrupt" in r.stdout, (kind, r.stdout)
        assert lines(findings) == expected_fixture_lines(head), (kind, findings.read_text())
        assert content in [aside.read_bytes() for aside in findings_asides()], kind
    assert len(findings_asides()) == len(CORRUPT_BUFFERS), findings_asides()
    assert not list(findings.parent.glob("metrics.tsv*"))


skill_text = (KIT / "SKILL.md").read_text()
step_seven = skill_text.split("\n## 7. ")[1]
assert "RUNLOG record" in step_seven and "RUNLOG findings --state $STATE" in step_seven
assert step_seven.index("RUNLOG findings --state $STATE") > step_seven.index("RUNLOG record")
assert "A failure of `RUNLOG` never fails the run: print its error line and go on" in step_seven
assert "RUNLOG findings" in skill_text.split("\n## 1. ")[0]

readme_text = (KIT / "README.md").read_text()
assert any(row.startswith("| Findings buffer |") for row in cursor_table_rows(readme_text))
assert any(row.startswith("| `<git-common-dir>/run-spec/findings.tsv` |") for row in readme_text.splitlines())
