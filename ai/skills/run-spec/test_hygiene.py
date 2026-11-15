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
    "notes.txt": "line one of notes\nline two\nline three\nline four\n",
    "docs/old.md": "# Old\n\nline one\nline two\nline three\n",
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
    "a.rb": "# frozen_string_literal: true\n# encoding: utf-8\n# rubocop:disable Style/Foo\n\nputs 1\n# explains\n",
    "tools.py": "# ruff: noqa: E501\nimport x\nv = x.y()  # pyright: ignore[reportUnknownMemberType]\n"
                "w = 1  # pylint: disable=invalid-name\n",
    "src/d.test.ts": "// @vitest-environment jsdom\n/* eslint no-console: off */\n/* global foo, bar */\n"
                     "/* jshint undef: true */\n// tslint:disable\n// @flow\n// @generated\n\nexport const d = 1;\n"
                     "// global state is shared\n// re-enable the cache\n",
    "src/j.test.js": "/**\n * @jest-environment jsdom\n */\n/**\n * explains the setup\n */\ntest(\"x\", () => {});\n",
    "src/lic.ts": "// Copyright (c) 2026 Acme Corp. All rights reserved.\n// Use of this code is governed by a"
                  " license.\n\n// explains the retry loop below\nexport const r = 1;\n// Copyright moved here\n",
    "src/apache.java": "/*\n * Licensed under the Apache License, Version 2.0.\n */\npackage p;\n",
    "DECISIONS.md": "line one of notes\nline two\nline three\nline four\nextra\n",
    "docs/moved.md": "# Old\n\nline one\nline two\nline three\n",
    "prag.py": "x = 1  # Pragmatic shortcut until v2\ny = 2  # noqa\n",
    "hdr.py": "#!/usr/bin/env python3\n# Copyright 2026 Acme\n# All rights reserved.\nv = 1\n",
}
EXPECTED = [
    "DECISIONS.md: markdown: added Markdown file",
    "a.rb:6: comment: # explains",
    "allowed.ts:1: comment: // allowed",
    "app.py:4: comment: x = 1  # why",
    "app.py:5: comment: # comment",
    'app.py:9: comment: """Docstring."""',
    "docs/notes.md: markdown: added Markdown file",
    "page.html:2: comment: <!-- c -->",
    "prag.py:1: comment: x = 1  # Pragmatic shortcut until v2",
    "q.sql:1: comment: -- comment",
    "run.sh:3: comment: # comment",
    "src/A.java:1: comment: /** Javadoc */",
    "src/a.ts:2: comment: // note",
    "src/a.ts:3: comment: /**",
    "src/d.test.ts:10: comment: // global state is shared",
    "src/d.test.ts:11: comment: // re-enable the cache",
    "src/j.test.js:4: comment: /**",
    "src/lic.ts:4: comment: // explains the retry loop below",
    "src/lic.ts:6: comment: // Copyright moved here",
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
    head = commit(repo, HEAD, "head", remove=["src/gone.ts", "notes.txt", "docs/old.md"])
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
