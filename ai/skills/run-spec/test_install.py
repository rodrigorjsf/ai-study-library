import os
import subprocess
import tempfile
from pathlib import Path

KIT = Path(__file__).resolve().parent
INSTALL = KIT / "install.sh"
CORRECT_KIT = KIT.parent / "run-spec-correct"

RUNTIME_FILES = ["SKILL.md", "QUEUE.md", "tickets.py", "hygiene.py", "runlog.py", "gitcmd.py", "watchdog.sh",
                 "guides/tdd.md", "axes/standards.md", "axes/spec.md", "axes/security.md",
                 "axes/ux-aix.md", "axes/design.md", "axes/ux-aix.triggers"]
AGENTS = ["acceptance-verifier.md", "followup-triager.md", "review-fixer.md", "ticket-implementer.md",
          "ticket-reviewer.md", "wave-integrator.md"]
NOT_INSTALLED = ["GLOSSARY.md", "docs", "README.md", "install.sh", "agents", "test_install.py", "test_tickets.py"]
DEVELOPMENT_ONLY = ["run-spec-dev", "statechart", "NOTICE", "formal-check"]


def install(home):
    env = {**os.environ, "HOME": str(home)}
    env.pop("CLAUDE_HOME", None)
    return subprocess.run(["bash", str(INSTALL)], env=env, capture_output=True, text=True)


def installed_files(skill_dir):
    return sorted(p.relative_to(skill_dir).as_posix() for p in skill_dir.rglob("*") if p.is_file())


def committed_files(directory):
    return subprocess.run(["git", "-C", str(directory), "ls-tree", "-r", "--name-only", "HEAD", "."],
                          capture_output=True, text=True, check=True).stdout.split()


def committed_runtime_files():
    committed_paths = committed_files(KIT)
    skipped = ("agents/", "docs/")
    return sorted(name for name in committed_paths
                  if not name.startswith(skipped)
                  and name not in ("GLOSSARY.md", "README.md", "install.sh")
                  and not (name.startswith("test_") and name.endswith(".py")))


with tempfile.TemporaryDirectory() as tmp:
    home = Path(tmp)
    r = install(home)
    assert r.returncode == 0, r
    skill = home / ".claude/skills/run-spec"

    for name in NOT_INSTALLED:
        assert not (skill / name).exists(), (name, installed_files(skill))

    for name in RUNTIME_FILES:
        assert (skill / name).is_file(), (name, installed_files(skill))
    for name in AGENTS:
        assert (home / ".claude/agents" / name).is_file(), (name, sorted(p.name for p in (home / ".claude/agents").iterdir()))
    assert (home / ".claude/skills/follow-up-issue/SKILL.md").is_file()

    assert installed_files(skill) == committed_runtime_files(), (installed_files(skill), committed_runtime_files())

    correct = home / ".claude/skills/run-spec-correct"
    assert installed_files(correct) == ["SKILL.md"], installed_files(correct)
    assert committed_files(CORRECT_KIT) == ["SKILL.md"], committed_files(CORRECT_KIT)

    leaked = [path for path in installed_files(home) if any(name in path for name in DEVELOPMENT_ONLY)]
    assert not leaked, leaked


with tempfile.TemporaryDirectory() as tmp:
    home = Path(tmp)
    skill = home / ".claude/skills/run-spec"
    (skill / "docs/adr").mkdir(parents=True)
    (skill / "docs/adr/0001-old.md").write_text("old\n")
    (skill / "GLOSSARY.md").write_text("old\n")
    (skill / "__pycache__").mkdir()
    (skill / "__pycache__/hygiene.cpython-312.pyc").write_bytes(b"old")
    (skill / "SKILL.md").write_text("stale\n")
    correct = home / ".claude/skills/run-spec-correct"
    correct.mkdir(parents=True)
    (correct / "SKILL.md").write_text("stale\n")
    (correct / "old.md").write_text("old\n")

    r = install(home)
    assert r.returncode == 0, r
    assert not (skill / "GLOSSARY.md").exists(), installed_files(skill)
    assert not (skill / "docs").exists(), installed_files(skill)
    assert not (skill / "__pycache__").exists(), installed_files(skill)
    assert (skill / "SKILL.md").read_text() != "stale\n"
    assert installed_files(skill) == committed_runtime_files(), (installed_files(skill), committed_runtime_files())
    assert installed_files(correct) == ["SKILL.md"], installed_files(correct)
    assert (correct / "SKILL.md").read_text() != "stale\n"

    first = installed_files(skill), installed_files(correct)
    r = install(home)
    assert r.returncode == 0, r
    assert (installed_files(skill), installed_files(correct)) == first

print("ok")
