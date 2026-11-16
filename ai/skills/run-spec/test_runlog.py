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
from test_support import review_report
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
