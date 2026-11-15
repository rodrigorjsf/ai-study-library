import importlib.util
import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

HYGIENE = Path(__file__).resolve().parent / "hygiene.py"
ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
SPEC = importlib.util.spec_from_file_location("hygiene", HYGIENE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def notice(name, style, width):
    body = ["Copyright (c) 2026 Acme Corp", ""]
    for para in MODULE.LICENSES[name].split("\n\n"):
        body += textwrap.wrap(para, width) + [""]
    body = body[:-1]
    if style == "block":
        return "/*\n" + "".join(f" * {line}".rstrip() + "\n" for line in body) + " */\n"
    return "".join(f"{style} {line}".rstrip() + "\n" for line in body)


MIT_LINES = notice("MIT", "//", 70).split("\n")
META = ("/**\n * Copyright (c) Acme, Inc. and its affiliates.\n *\n * This source code is licensed under the MIT license found"
        " in the\n * LICENSE file in the root directory of this source tree.\n")
MIT_PROSE = "\n".join(MIT_LINES[:4] + ["// retries because the API drops calls"] + MIT_LINES[4:])

BASE = {
    "src/old.ts": "// Copyright 2026 Acme\nexport const a = 1;\n",
    "src/gone.ts": "// deleted with its file\nexport const g = 1;\n",
    "notes.txt": "line one of notes\nline two\nline three\nline four\n",
    "docs/old.md": "# Old\n\nline one\nline two\nline three\n",
}
HEAD = {
    "src/old.ts": "// Copyright 2026 Acme\n// Inserted explanation of a\nexport const a = 2;\n",
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
    "src/lic.ts": "// Copyright (c) 2026 Acme Corp. All rights reserved.\n// Use of this source code is governed by a"
                  " BSD-style license that can be found in the LICENSE file.\n\n// explains the retry loop below\nexport const r = 1;\n// Copyright moved here\n",
    "src/apache.java": "/*\n * Licensed under the Apache License, Version 2.0.\n */\npackage p;\n",
    "DECISIONS.md": "line one of notes\nline two\nline three\nline four\nextra\n",
    "docs/moved.md": "# Old\n\nline one\nline two\nline three\n",
    "prag.py": "x = 1  # Pragmatic shortcut until v2\ny = 2  # noqa\n",
    "hdr.py": "#!/usr/bin/env python3\n# Copyright 2026 Acme\n# All rights reserved.\nv = 1\n",
    "src/key.ts": "// Validates the license key before activation\nexport const v = 1;\n",
    "src/retry.ts": "// Copyright 2026 Acme\n// This module retries because the upstream API drops requests\n"
                    "export const r = 1;\n",
    "src/blk.ts": "/*\n * Copyright 2026 Acme\n * This module retries because the upstream API drops requests\n */\n"
                  "export const b = 1;\n",
    "src/mit.ts": notice("MIT", "//", 76) + "export const m = 1;\n",
    "src/mit.css": notice("MIT", "block", 60) + "a {}\n",
    "src/bsd.c": notice("BSD-3-Clause", "block", 78) + "int x;\n",
    "src/bsd2.go": notice("BSD-2-Clause", "//", 64) + "package b\n",
    "src/apache.go": notice("Apache-2.0", "//", 72) + "package a\n",
    "src/Apache.kt": notice("Apache-2.0", "block", 80).replace("http://", "https://") + "val a = 1\n",
    "deploy.sh": "#!/bin/sh\n" + notice("Apache-2.0", "#", 66) + "echo ok\n",
    "src/prose.ts": MIT_PROSE + "export const p = 1;\n",
    "tools/build/NOTES.md": "# Build notes\n",
    "tools/build/step.ts": "// explains the bundler step\nexport const s = 1;\n",
    "node_modules/dep/README.md": "# Dep\n",
    "vendor/lib/x.go": "// vendored\npackage lib\n",
    "dist/index.js": "/******/ (() => {})();\n",
    "src/meta.js": META + " *\n * @format\n * @flow strict\n */\nexport const m = 1;\n",
    "src/card.js": META + " *\n * Renders the profile card and caches the avatar because it is slow.\n *\n * @format\n"
                   " * @flow strict\n */\nexport const c = 1;\n",
    "src/p.test.ts": "/**\n * @jest-environment jsdom\n * Uses jsdom because the component reads window.location on mount.\n"
                     " */\ntest(\"p\", () => {});\n",
    "src/one.test.ts": "/** @jest-environment jsdom — renders the login form */\ntest(\"o\", () => {});\n"
                       "// @flow strict because the store is typed\n/* @jsx h */\n// @generated SignedSource<<abc>>\n",
    "src/open.js": "/** @flow\n * explains the store\n */\nexport const o = 1;\n",
    "src/dir.ts": "// @ts-expect-error the library types are wrong here\n"
                  "// eslint-disable-next-line no-console -- we log here because the API drops calls\n"
                  "// biome-ignore lint/style/useConst: this value is reassigned by the retry loop later\n"
                  "// eslint-disable-next-line no-console\n// eslint-disable-next-line curly, eqeqeq\n"
                  "/* eslint-env node */\n/* istanbul ignore next */\n// c8 ignore next 3\n"
                  "//nolint:errcheck // the error is logged upstream\nexport const z = 1;\n",
    "src/dir.py": "import os  # noqa: F401 kept because plugins import it lazily\nimport sys  # noqa: F401\n"
                  "x = 1  # pylint: disable=invalid-name because legacy naming\ny = os  # type: ignore  # noqa: E501\n"
                  "z = sys  # pragma: no cover\nw = 2  # noqa: F401 intentional\n"
                  "v = 3  # pragma: no cover because tests skip it\nu = 4  # noqa:F401 intentional\n",
    "dir.sh": "#!/bin/sh\n# shellcheck disable=SC2086 because word splitting is intended here\n"
              "# shellcheck disable=SC2086\necho $1\n",
    "src/top.ts": "// Copyright 2026 Acme. Retries three times because the upstream API drops requests.\n"
                  "export const t = 1;\n",
    "src/ms.ts": "// Copyright (c) Microsoft Corporation. Licensed under the MIT License.\nexport const ms = 1;\n",
    "src/init.ts": "// Copyright 2026 John Q. Public. All rights reserved.\nexport const i = 1;\n",
    "gen.sh": '#!/bin/sh\ncat > "$1/.env.example" <<EOF\n# Database\nDB_URL=postgres://localhost/app\nEOF\n'
              "# real comment after\ncat <<-'X'\n\t# indented body\n\tX\n",
    "open.sh": "#!/bin/sh\necho $((1 << 2))\nn=$((x <<y))\ncat <<< \"$n\"\n# still a comment\n",
    "r.rb": "class Foo\n  class << self\n  end\nend\ns = <<~EOS\n  # not a comment\nEOS\n# explains r\n",
    "s.ts": "export const banner = `\n// generated by app, do not edit\n`;\n",
    "src/tick.ts": 'const q = "`";\n// stray ` in a comment\nconst t = `a ${q} b\n// inside the template\n'
                   "${f(`x`)}`;\n// after the template\nconst e = `${(() => {\n  // code inside the expression\n"
                   "  return 1;\n})()}`;\n",
    "src/raw.go": "package raw\n\nconst s = `\n// not a comment\n`\n",
    "src/unterm.ts": "const u = `abc\n// later comment\n",
}
EXPECTED = sorted([
    "DECISIONS.md: markdown: added Markdown file",
    "a.rb:6: comment: # explains",
    "allowed.ts:1: comment: // allowed",
    "app.py:4: comment: x = 1  # why",
    "app.py:5: comment: # comment",
    'app.py:9: comment: """Docstring."""',
    "docs/notes.md: markdown: added Markdown file",
    "node_modules/dep/README.md: markdown: added Markdown file",
    "page.html:2: comment: <!-- c -->",
    "prag.py:1: comment: x = 1  # Pragmatic shortcut until v2",
    "q.sql:1: comment: -- comment",
    "run.sh:3: comment: # comment",
    "src/A.java:1: comment: /** Javadoc */",
    "src/a.ts:2: comment: // note",
    "src/a.ts:3: comment: /**",
    "src/blk.ts:1: comment: /*",
    "src/card.js:1: comment: /**",
    "src/one.test.ts:1: comment: /** @jest-environment jsdom — renders the login form */",
    "src/one.test.ts:3: comment: // @flow strict because the store is typed",
    "src/open.js:1: comment: /** @flow",
    "src/p.test.ts:1: comment: /**",
    "src/d.test.ts:10: comment: // global state is shared",
    "src/d.test.ts:11: comment: // re-enable the cache",
    "src/j.test.js:4: comment: /**",
    "src/key.ts:1: comment: // Validates the license key before activation",
    "src/lic.ts:4: comment: // explains the retry loop below",
    "src/lic.ts:6: comment: // Copyright moved here",
    "src/old.ts:2: comment: // Inserted explanation of a",
    "src/prose.ts:5: comment: // retries because the API drops calls",
    "src/retry.ts:2: comment: // This module retries because the upstream API drops requests",
    "tools/build/NOTES.md: markdown: added Markdown file",
    "tools/build/step.ts:1: comment: // explains the bundler step",
    "src/dir.ts:1: comment: // @ts-expect-error the library types are wrong here",
    "src/dir.ts:2: comment: // eslint-disable-next-line no-console -- we log here because the API drops calls",
    "src/dir.ts:9: comment: //nolint:errcheck // the error is logged upstream",
    "src/dir.py:1: comment: import os  # noqa: F401 kept because plugins import it lazily",
    "src/dir.py:3: comment: x = 1  # pylint: disable=invalid-name because legacy naming",
    "src/dir.py:6: comment: w = 2  # noqa: F401 intentional",
    "src/dir.py:7: comment: v = 3  # pragma: no cover because tests skip it",
    "src/dir.py:8: comment: u = 4  # noqa:F401 intentional",
    "dir.sh:2: comment: # shellcheck disable=SC2086 because word splitting is intended here",
    "src/top.ts:1: comment: // Copyright 2026 Acme. Retries three times because the upstream API drops requests.",
    "gen.sh:6: comment: # real comment after",
    "open.sh:5: comment: # still a comment",
    "r.rb:8: comment: # explains r",
    "src/tick.ts:2: comment: // stray ` in a comment",
    "src/tick.ts:6: comment: // after the template",
    "src/tick.ts:8: comment: // code inside the expression",
    "src/unterm.ts:2: comment: // later comment",
])


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
