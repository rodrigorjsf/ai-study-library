#!/usr/bin/env python3
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FIXTURE = Path(__file__).resolve().parent / "fixture"
GIT_SETTINGS = ["-c", "user.name=run-spec fixture", "-c", "user.email=fixture@example.invalid",
                "-c", "core.autocrlf=false", "-c", "core.excludesFile=/dev/null",
                "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false"]
SKIPPED = shutil.ignore_patterns("__pycache__", ".todo.json")


def git(repo, *args):
    result = subprocess.run(["git", *GIT_SETTINGS, *args], cwd=repo, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"materialize_fixture: git {args[0]} failed: {result.stderr.strip()}")


def main():
    repo = Path(tempfile.mkdtemp(prefix="run-spec-fixture-"))
    shutil.copytree(FIXTURE, repo, ignore=SKIPPED, dirs_exist_ok=True)
    (repo / "dot-claude").rename(repo / ".claude")
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "chore: initial commit of the todo fixture")
    print(repo)


if __name__ == "__main__":
    main()
