import os
import subprocess
import tempfile
from pathlib import Path

KIT = Path(__file__).resolve().parent
INSTALL = KIT / "install.sh"

RUNTIME_FILES = ["SKILL.md", "QUEUE.md", "tickets.py", "hygiene.py", "runlog.py", "watchdog.sh",
                 "guides/tdd.md", "axes/standards.md", "axes/spec.md", "axes/security.md",
                 "axes/ux-aix.md", "axes/design.md", "axes/ux-aix.triggers"]
AGENTS = ["acceptance-verifier.md", "followup-triager.md", "review-fixer.md", "ticket-implementer.md",
          "ticket-reviewer.md", "wave-integrator.md"]
NOT_INSTALLED = ["GLOSSARY.md", "docs", "README.md", "install.sh", "agents", "test_install.py", "test_tickets.py"]


def install(home):
    env = {**os.environ, "HOME": str(home)}
    env.pop("CLAUDE_HOME", None)
    return subprocess.run(["bash", str(INSTALL)], env=env, capture_output=True, text=True)


def installed_files(skill_dir):
    return sorted(p.relative_to(skill_dir).as_posix() for p in skill_dir.rglob("*") if p.is_file())


def committed_runtime_files():
    relative = subprocess.run(["git", "-C", str(KIT), "ls-tree", "-r", "--name-only", "HEAD", "."],
                              capture_output=True, text=True, check=True).stdout.split()
    skipped = ("agents/", "docs/")
    return sorted(name for name in relative
                  if not name.startswith(skipped)
                  and name not in ("GLOSSARY.md", "README.md", "install.sh")
                  and not (name.startswith("test_") and name.endswith(".py")))


with tempfile.TemporaryDirectory() as tmp:
    home = Path(tmp)
    r = install(home)
    assert r.returncode == 0, r
    skill = home / ".claude/skills/run-spec"

    assert not (skill / "GLOSSARY.md").exists(), installed_files(skill)
    assert not (skill / "docs").exists(), installed_files(skill)
    for name in NOT_INSTALLED:
        assert not (skill / name).exists(), (name, installed_files(skill))

    for name in RUNTIME_FILES:
        assert (skill / name).is_file(), (name, installed_files(skill))
    for name in AGENTS:
        assert (home / ".claude/agents" / name).is_file(), (name, sorted(p.name for p in (home / ".claude/agents").iterdir()))
    assert (home / ".claude/skills/follow-up-issue/SKILL.md").is_file()

    assert installed_files(skill) == committed_runtime_files(), (installed_files(skill), committed_runtime_files())


with tempfile.TemporaryDirectory() as tmp:
    home = Path(tmp)
    skill = home / ".claude/skills/run-spec"
    (skill / "docs/adr").mkdir(parents=True)
    (skill / "docs/adr/0001-old.md").write_text("old\n")
    (skill / "GLOSSARY.md").write_text("old\n")
    (skill / "__pycache__").mkdir()
    (skill / "__pycache__/hygiene.cpython-312.pyc").write_bytes(b"old")
    (skill / "SKILL.md").write_text("stale\n")

    r = install(home)
    assert r.returncode == 0, r
    assert not (skill / "GLOSSARY.md").exists(), installed_files(skill)
    assert not (skill / "docs").exists(), installed_files(skill)
    assert not (skill / "__pycache__").exists(), installed_files(skill)
    assert (skill / "SKILL.md").read_text() != "stale\n"
    assert installed_files(skill) == committed_runtime_files(), (installed_files(skill), committed_runtime_files())

    first = installed_files(skill)
    r = install(home)
    assert r.returncode == 0, r
    assert installed_files(skill) == first

print("ok")
