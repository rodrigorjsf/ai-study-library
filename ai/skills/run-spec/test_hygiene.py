import os
import subprocess
import sys
import tempfile
from pathlib import Path

HYGIENE = Path(__file__).resolve().parent / "hygiene.py"
ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}

BASE = {
    "src/old.ts": "// kept from base\nexport const a = 1;\n",
    "src/gone.ts": "// deleted with its file\nexport const g = 1;\n",
}
HEAD = {
    "src/old.ts": "// kept from base\nexport const a = 2;\n",
    "src/a.ts": 'const u = "http://x";\n// note\n/**\n * jsdoc\n */\n'
                "// eslint-disable-next-line no-console\nconsole.log(u);\n",
    "src/A.java": "/** Javadoc */\npublic class A {}\n",
    "src/b.go": "//go:build linux\n\npackage b\n",
    "app.py": '#!/usr/bin/env python3\nimport x  # noqa: F401\ns = "#not"\nx = 1  # why\n# comment\n\n\n'
              'def f():\n    """Docstring."""\n    return s\n',
    "run.sh": '#!/bin/sh\necho "#x"\n# comment\n',
    "q.sql": "-- comment\nSELECT 1;\n",
    "page.html": "<p>hi</p>\n<!-- c -->\n",
    "docs/notes.md": "# Notes\n",
    ".scratch/demo/issues/01-a.md": "# 01 — a\n",
    "allowed.ts": "// allowed\n",
    "pnpm-lock.yaml": "# generated\nlockfileVersion: 9\n",
    "node_modules/dep/index.js": "// vendored\n",
}
EXPECTED = [
    "allowed.ts:1: comment: // allowed",
    "app.py:4: comment: x = 1  # why",
    "app.py:5: comment: # comment",
    'app.py:9: comment: """Docstring."""',
    "docs/notes.md: markdown: added Markdown file",
    "page.html:2: comment: <!-- c -->",
    "q.sql:1: comment: -- comment",
    "run.sh:3: comment: # comment",
    "src/A.java:1: comment: /** Javadoc */",
    "src/a.ts:2: comment: // note",
    "src/a.ts:3: comment: /**",
]


def git(repo, *args):
    r = subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
                       cwd=repo, env=ENV, capture_output=True, text=True, check=True)
    return r.stdout.strip()


def commit(repo, files, msg, remove=()):
    for name, text in files.items():
        p = repo / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    for name in remove:
        (repo / name).unlink()
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", msg)
    return git(repo, "rev-parse", "HEAD")


def hygiene(repo, *args):
    r = subprocess.run([sys.executable, "-I", str(HYGIENE), *args], cwd=repo, env=ENV, capture_output=True, text=True)
    return r.returncode, r.stdout.splitlines(), r.stderr.splitlines()


with tempfile.TemporaryDirectory() as tmp:
    repo = Path(tmp)
    git(repo, "init", "-q", "-b", "main")
    base = commit(repo, BASE, "base")
    head = commit(repo, HEAD, "head", remove=["src/gone.ts"])
    clean = commit(repo, {"src/clean.ts": "export const c = 3;\n", "clean.py": 's = "#x"\n'}, "clean")

    code, out, err = hygiene(repo, base, head)
    assert (code, out, err) == (1, EXPECTED, []), (code, out, err)

    code, out, err = hygiene(repo, base, head, "--allow", "allowed.ts", "--allow", "docs/notes.md")
    assert (code, out) == (1, [line for line in EXPECTED if not line.startswith(("allowed.ts", "docs/"))]), (code, out)

    assert hygiene(repo, head, clean) == (0, [], []), hygiene(repo, head, clean)

    for args in ((), (base,), (base, "no-such-rev")):
        code, out, err = hygiene(repo, *args)
        assert code == 2 and out == [] and len(err) == 1, (args, code, out, err)

print("ok")
