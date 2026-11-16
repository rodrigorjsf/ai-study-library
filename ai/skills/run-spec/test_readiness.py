import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

KIT = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(KIT))
import test_support as support
READINESS = KIT / "readiness.py"
BASE_ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
RUN_SPEC_FILE = "docs/agents/run-spec.md"
SEARCHED = ".claude/skills/verify*/, .claude/skills/run-*/, .cursor/skills/verify-*/"
SUGGESTION = "suggestion: run Claude Code's `/run-skill-generator` to create one"


FAKE_GH_BIN = tempfile.TemporaryDirectory()
FIXTURE_DIR = tempfile.TemporaryDirectory()
ENV = support.with_fake_gh(BASE_ENV, FAKE_GH_BIN.name)


def env_with_issues(issues, title="Spec: demo"):
    return support.with_fake_gh_issues(ENV, tempfile.mkdtemp(dir=FIXTURE_DIR.name), issues, title)


def github_ticket(number, criteria, labels=("ready-for-agent",), state="OPEN"):
    body = "## Parent\n\n#6\n\n## Acceptance criteria\n\n" + "".join(f"- [ ] {c}\n" for c in criteria) + "\n## Blocked by\n\nNone\n"
    return {"number": number, "title": f"Ticket {number}", "state": state, "body": body,
            "labels": [{"name": name} for name in labels]}


def git(repo, *args):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
                   cwd=repo, env=ENV, capture_output=True, text=True, check=True)


def new_repo(tmp, files=None):
    repo = Path(tmp)
    git(repo, "init", "-q", "-b", "main")
    for name, content in (files or {}).items():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content if isinstance(content, bytes) else content.encode())
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "--allow-empty", "-m", "base")
    return repo


def readiness(*args, cwd=None, env=ENV):
    return subprocess.run([sys.executable, "-I", str(READINESS), *args], cwd=cwd, env=env, capture_output=True, text=True)


def sections_of(repo, spec, env):
    r = readiness("--repo", str(repo), "--spec", spec, env=env)
    assert (r.returncode, r.stderr) == (0, ""), r
    lines = r.stdout.split("\n")
    assert lines.pop() == "", r.stdout
    sections, current = {}, None
    for line in lines[1:]:
        heading = re.fullmatch(r"### (.+)", line)
        if heading:
            current = sections.setdefault(heading.group(1), [])
        else:
            assert current is not None and line.startswith("- "), (line, r.stdout)
            current.append(line[2:])
    assert list(sections) == ["Check commands", "App recipe", "Surface"], r.stdout
    return lines[0], sections


def report(repo, spec="#6"):
    summary, sections = sections_of(repo, spec, ENV)
    return summary, sections["Check commands"], sections["App recipe"]


def surface(repo, spec="#6", env=ENV):
    summary, sections = sections_of(repo, spec, env)
    return summary, sections["Surface"]


def app_recipe_line(repo):
    r = readiness("--repo", str(repo), "--app-recipe")
    assert (r.returncode, r.stderr) == (0, ""), r
    assert r.stdout.count("\n") == 1 and r.stdout.endswith("\n"), r.stdout
    return r.stdout[:-1]


def check_section(run_spec_text):
    with tempfile.TemporaryDirectory() as tmp:
        repo = new_repo(tmp, {} if run_spec_text is None else {RUN_SPEC_FILE: run_spec_text})
        return report(repo)[1]


def recipe_line_and_section(*skill_dirs, extra=()):
    files = {f"{d}/SKILL.md": "x" for d in skill_dirs} | {name: "x" for name in extra}
    with tempfile.TemporaryDirectory() as tmp:
        repo = new_repo(tmp, files)
        return app_recipe_line(repo), report(repo)[2]


with tempfile.TemporaryDirectory() as tmp:
    repo = new_repo(tmp, {RUN_SPEC_FILE: "max-parallel: 2\ntypecheck: npm run typecheck\nlint: npm run lint\ntest: npm test\n"})
    summary, check_lines, recipe_lines = report(repo)
    assert check_lines == ["typecheck: declared (npm run typecheck)", "lint: declared (npm run lint)",
                           "test: declared (npm test)"], check_lines
    assert summary == "readiness #6: check commands 3 of 3 declared; no app recipe; surface unchecked", summary
    assert recipe_lines == [f"none found in {SEARCHED}", SUGGESTION], recipe_lines

assert check_section("typecheck: tsc --noEmit\ntest: pytest -q\n") == [
    "typecheck: declared (tsc --noEmit)", "lint: missing", "test: declared (pytest -q)"], "partial"

with tempfile.TemporaryDirectory() as tmp:
    repo = new_repo(tmp, {RUN_SPEC_FILE: "typecheck: tsc\ntest: pytest\n"})
    summary, _, _ = report(repo, ".scratch/demo")
    assert summary == "readiness .scratch/demo: check commands 2 of 3 declared (missing: lint); no app recipe; surface unchecked", summary

everything_missing = ["typecheck: missing", "lint: missing", "test: missing"]
assert check_section(None) == everything_missing, "no file"
assert check_section("") == everything_missing, "empty file"
assert check_section("max-parallel: 3\n") == everything_missing, "other keys only"

assert check_section("typecheck:\nlint:   \ntest: npm test\n") == [
    "typecheck: missing", "lint: missing", "test: declared (npm test)"], "empty commands"
assert check_section("  typecheck: tsc\n\tlint: eslint .\n- test: pytest\nTest: pytest\n") == everything_missing, "indented or altered"
assert check_section("test: first\ntest: second\n")[2] == "test: declared (first)", "first line wins"
assert check_section("test:   pytest -q   \n")[2] == "test: declared (pytest -q)", "spaces trimmed"
assert check_section("typecheck:tsc\n")[0] == "typecheck: declared (tsc)", "no space after the colon"
assert check_section("typecheck: tsc\r\nlint: eslint .\r\ntest: npm test\r\n")[:3] == [
    "typecheck: declared (tsc)", "lint: declared (eslint .)", "test: declared (npm test)"], "crlf"
assert check_section("test: py\rtest\n")[2] == "test: declared (pytest)", "lone carriage return"
assert check_section("test: \x0c\x0bpytest\x0b\x0c \n")[2] == "test: declared (pytest)", "form feed and vertical tab"
assert check_section("test: pytest")[2] == "test: declared (pytest)", "no trailing newline"
assert check_section("typecheck: first\ntypecheck:\n")[0] == "typecheck: declared (first)", "later empty line ignored"
assert check_section("typecheck:\ntypecheck: second\n")[0] == "typecheck: missing", "first line wins even when empty"
assert check_section(b"test: pytest \xff\xfe\n")[2].startswith("test: declared (pytest "), "invalid utf-8"
assert check_section("test: make test && make e2e | tee out.log\n")[2] == "test: declared (make test && make e2e | tee out.log)"


def check_command_lines(repo):
    r = readiness("--repo", str(repo), "--check-commands")
    assert (r.returncode, r.stderr) == (0, ""), r
    return r.stdout.rstrip("\n").split("\n")


def report_as_prompt_lines(repo):
    lines = []
    for line in report(repo)[1]:
        key, command = re.fullmatch(r"(typecheck|lint|test): (?:declared \((.*)\)|missing)", line).groups()
        lines.append(f"{key.upper()}: {command or 'none'}")
    return lines


with tempfile.TemporaryDirectory() as tmp:
    repo = new_repo(tmp, {RUN_SPEC_FILE: "max-parallel: 2\ntest: pnpm -r test -- --run\n"})
    assert check_command_lines(repo) == ["TYPECHECK: none", "LINT: none", "TEST: pnpm -r test -- --run"]

with tempfile.TemporaryDirectory() as tmp:
    assert check_command_lines(new_repo(tmp)) == ["TYPECHECK: none", "LINT: none", "TEST: none"], "no file"

for content in ("typecheck: npm run typecheck\nlint: npm run lint\ntest: npm test\n", "test: pytest\n", "",
                "typecheck:\nlint:  \ntest: x\n", "  test: indented\ntest: real\n", "test: a\ntest: b\n",
                "typecheck: tsc\r\nlint: eslint .\r\ntest: npm test\r\n", "lint:\teslint .\t\n", "test: a   b   \n",
                "max-parallel: 3\n# test: commented\ntest: ok\n", "test: a\rb\n", "test: \x0cpytest \x0b\n",
                "lint: eslint\x0b.\n"):
    with tempfile.TemporaryDirectory() as tmp:
        repo = new_repo(tmp, {RUN_SPEC_FILE: content})
        assert check_command_lines(repo) == report_as_prompt_lines(repo), (content, check_command_lines(repo))

for layout, extra, found in (
        ((".claude/skills/verify-app",), (), ".claude/skills/verify-app/"),
        ((".claude/skills/verify",), (), ".claude/skills/verify/"),
        ((".claude/skills/run-app",), (), ".claude/skills/run-app/"),
        ((".cursor/skills/verify-app",), (), ".cursor/skills/verify-app/"),
        ((".claude/skills/run-app", ".cursor/skills/verify-app"), (), ".claude/skills/run-app/"),
        ((".claude/skills/verify-app", ".claude/skills/run-app", ".cursor/skills/verify-app"), (), ".claude/skills/verify-app/"),
        ((".claude/skills/verify-b", ".claude/skills/verify-a"), (), ".claude/skills/verify-a/"),
        ((".claude/skills/verify-app",), (".claude/skills/other/SKILL.md",), ".claude/skills/verify-app/"),
        ((".claude/skills/runner",), (), None), ((".claude/skills/run",), (), None),
        ((".claude/skills/other",), (), None), ((".claude/skills/xverify",), (), None),
        ((".cursor/skills/verify",), (), None), ((".cursor/skills/run-app",), (), None),
        ((".cursor/skills/other",), (), None), ((".claude/commands/verify-app",), (), None),
        (("skills/verify-app",), (), None), ((".agents/skills/verify-app",), (), None),
        ((), (".claude/skills/verify-app/notes.txt",), None), ((), (".claude/skills/verify-app",), None)):
    line, section = recipe_line_and_section(*layout, extra=extra)
    if found:
        assert (line, section) == (f"APP_RECIPE: {found}", [f"found: {found}"]), (layout, extra, line, section)
    else:
        assert line == "APP_RECIPE: none" and section[0].startswith("none found"), (layout, extra, line, section)

with tempfile.TemporaryDirectory() as tmp:
    assert app_recipe_line(new_repo(tmp)) == "APP_RECIPE: none", "no recipe"

with tempfile.TemporaryDirectory() as tmp:
    repo = new_repo(tmp, {RUN_SPEC_FILE: "test: pytest\n", ".claude/skills/verify-app/SKILL.md": "x"})
    other = tempfile.mkdtemp()
    r = readiness("--repo", os.path.relpath(repo, other), "--app-recipe", cwd=other)
    assert (r.returncode, r.stdout, r.stderr) == (0, "APP_RECIPE: .claude/skills/verify-app/\n", ""), r
    os.rmdir(other)
    assert subprocess.run(["git", "status", "--porcelain"], cwd=repo, env=ENV, capture_output=True, text=True).stdout == ""

with tempfile.TemporaryDirectory() as tmp:
    plain = Path(tmp)
    (plain / ".cursor/skills/verify-app").mkdir(parents=True)
    (plain / ".cursor/skills/verify-app/SKILL.md").write_text("x")
    assert app_recipe_line(plain) == "APP_RECIPE: .cursor/skills/verify-app/", "a directory that is not a git repository"

with tempfile.TemporaryDirectory() as tmp:
    repo = new_repo(tmp)
    target = repo / "elsewhere"
    target.mkdir()
    (repo / ".claude/skills").mkdir(parents=True)
    (repo / ".claude/skills/verify-link").symlink_to(target)
    assert app_recipe_line(repo) == "APP_RECIPE: none", "a symlink to a directory without SKILL.md"
    (target / "SKILL.md").write_text("x")
    assert app_recipe_line(repo) == "APP_RECIPE: .claude/skills/verify-link/", "a symlinked recipe"
    (repo / ".claude/skills/verify-link").unlink()
    (repo / ".claude").rename(repo / ".claude-moved")
    (repo / ".claude").write_text("a file where a directory belongs")
    assert app_recipe_line(repo) == "APP_RECIPE: none", ".claude is a file"

with tempfile.TemporaryDirectory() as tmp:
    repo = new_repo(tmp, {RUN_SPEC_FILE: "test: pytest\n", ".claude/skills/verify-app/SKILL.md": "x"})
    summary, _, _ = report(repo)
    assert summary == "readiness #6: check commands 1 of 3 declared (missing: typecheck, lint); app recipe .claude/skills/verify-app/; surface unchecked", summary
    before = subprocess.run(["git", "status", "--porcelain"], cwd=repo, env=ENV, capture_output=True, text=True).stdout
    assert before == "", before
    other = tempfile.mkdtemp()
    r = readiness("--repo", os.path.relpath(repo, other), "--spec", "#6", cwd=other)
    assert r.returncode == 0 and "found: .claude/skills/verify-app/" in r.stdout, r
    os.rmdir(other)

with tempfile.TemporaryDirectory() as tmp:
    plain = Path(tmp)
    (plain / ".cursor/skills/verify-app").mkdir(parents=True)
    (plain / ".cursor/skills/verify-app/SKILL.md").write_text("x")
    assert report(plain)[2] == ["found: .cursor/skills/verify-app/"], "a directory that is not a git repository"

with tempfile.TemporaryDirectory() as tmp:
    repo = new_repo(tmp)
    (repo / "docs/agents/run-spec.md").mkdir(parents=True)
    assert report(repo)[1] == everything_missing, "run-spec.md is a directory"
    (repo / ".claude").write_text("a file where a directory belongs")
    assert report(repo)[2][0].startswith("none found"), ".claude is a file"

with tempfile.TemporaryDirectory() as tmp:
    repo = new_repo(tmp)
    target = repo / "elsewhere"
    target.mkdir()
    (repo / ".claude/skills").mkdir(parents=True)
    (repo / ".claude/skills/verify-link").symlink_to(target)
    assert report(repo)[2][0].startswith("none found"), "a symlink to a directory without SKILL.md"
    (target / "SKILL.md").write_text("x")
    assert report(repo)[2] == ["found: .claude/skills/verify-link/"], "a symlinked recipe"

with tempfile.TemporaryDirectory() as tmp:
    repo = new_repo(tmp)
    usage_errors = (
        [], ["--repo", str(repo)], ["--spec", "#6"], ["--repo", str(repo), "--spec", ""],
        ["--repo", str(repo), "--spec", "  "], ["--repo", str(repo / "missing"), "--spec", "#6"],
        ["--repo", str(repo / ".git/HEAD"), "--spec", "#6"], ["--repo", str(repo), "--spec", "#6", "--strict"],
        ["--repo", str(repo), "--spec", "#6", "extra"], ["--bogus"], ["--check-commands"],
        ["--repo", str(repo), "--spec", "#6", "--check-commands"], ["--repo", str(repo / "missing"), "--check-commands"],
        ["--app-recipe"], ["--repo", str(repo), "--app-recipe", "--spec", "#6"],
        ["--repo", str(repo), "--app-recipe", "--check-commands"], ["--repo", str(repo / "missing"), "--app-recipe"],
        ["--repo", str(repo / ".git/HEAD"), "--app-recipe"], ["--repo", str(repo), "--app-recipe", "extra"])
    for args in usage_errors:
        r = readiness(*args)
        assert r.returncode == 2 and r.stdout == "" and r.stderr != "", (args, r)
    assert readiness("--help").returncode == 0

GITHUB_SUMMARY_PREFIX = "readiness #6: check commands 0 of 3 declared (missing: typecheck, lint, test); no app recipe"

with tempfile.TemporaryDirectory() as tmp:
    repo = new_repo(tmp)
    env = env_with_issues({
        "13": github_ticket(13, ["Runs `a` and prints `ok`.", "No span here", "A **bold** lead", "Empty `` span", "Blank ` ` span"]),
        "14": github_ticket(14, ["Out of scope and without a span"], labels=("needs-info",)),
        "15": github_ticket(15, []),
        "16": github_ticket(16, ["Only `one` fine criterion"], labels=(), state="CLOSED"),
    })
    summary, lines = surface(repo, env=env)
    assert summary == f"{GITHUB_SUMMARY_PREFIX}; surface warnings: 5", summary
    assert lines == ["#13: No span here", "#13: A **bold** lead", "#13: Empty `` span", "#13: Blank ` ` span",
                     "#15: no acceptance criteria found"], lines

with tempfile.TemporaryDirectory() as tmp:
    repo = new_repo(tmp)
    env = env_with_issues({"13": github_ticket(13, ["Runs `a`.", "Prints `ok`."]), "14": github_ticket(14, ["Exits with `0`"])})
    summary, lines = surface(repo, env=env)
    assert summary == f"{GITHUB_SUMMARY_PREFIX}; surface ok", summary
    assert lines == ["every criterion names a surface (tickets: 2, criteria: 3)"], lines
    assert surface(repo, "6", env)[1] == lines, "a bare issue number"

with tempfile.TemporaryDirectory() as tmp:
    repo = new_repo(tmp)
    assert surface(repo, env=env_with_issues({"13": github_ticket(13, ["No span"], labels=("needs-info",))})) == (
        f"{GITHUB_SUMMARY_PREFIX}; surface unchecked", ["no ticket in scope to check"])
    summary, lines = surface(repo)
    assert summary == f"{GITHUB_SUMMARY_PREFIX}; surface unchecked", summary
    assert lines == ["could not read ticket criteria: fake gh: no fixture"], lines
    assert surface(repo, ".scratch/missing") == (
        "readiness .scratch/missing: check commands 0 of 3 declared (missing: typecheck, lint, test); no app recipe; surface unchecked",
        ["could not read ticket criteria: no tickets under .scratch/missing/issues"])

LOCAL_TICKETS = {
    ".scratch/demo/spec.md": "# Demo\n",
    ".scratch/demo/issues/01-first.md": "# 01 — First\n\n**Blocked by:** None\n\n**Status:** ready-for-agent\n\n"
                                        "- [ ] Prints `ok`\n- [x] A **checked** criterion without code\n",
    ".scratch/demo/issues/02-second.md": "# 02 — Second\n\n**Blocked by:** 01\n\n**Status:** ready-for-agent\n\n"
                                         "- [ ] Wrapped across\n  two lines, with `span`\n- [ ] Needs a surface\n",
    ".scratch/demo/issues/03-parked.md": "# 03 — Parked\n\n**Blocked by:** none\n\n**Status:** needs-info\n\n- [ ] Not in scope\n",
}
LOCAL_SUMMARY_PREFIX = "readiness {spec}: check commands 0 of 3 declared (missing: typecheck, lint, test); no app recipe"

with tempfile.TemporaryDirectory() as tmp:
    repo = new_repo(tmp, LOCAL_TICKETS)
    for spec in (".scratch/demo", ".scratch/demo/spec.md"):
        assert surface(repo, spec) == (f"{LOCAL_SUMMARY_PREFIX.format(spec=spec)}; surface warnings: 2",
                                       ["01: A **checked** criterion without code", "02: Needs a surface"]), spec
    before = subprocess.run(["git", "status", "--porcelain"], cwd=repo, env=ENV, capture_output=True, text=True).stdout
    assert before == "", before

with tempfile.TemporaryDirectory() as tmp:
    repo = new_repo(tmp, {name: text for name, text in LOCAL_TICKETS.items() if "02-" not in name})
    (repo / ".scratch/demo/issues/01-first.md").write_text(
        "# 01 — First\n\n**Blocked by:** None\n\n**Status:** ready-for-agent\n\n- [ ] Prints `ok`\n- [x] Exits `0`\n")
    assert surface(repo, ".scratch/demo")[1] == ["every criterion names a surface (tickets: 1, criteria: 2)"]

print("ok")
