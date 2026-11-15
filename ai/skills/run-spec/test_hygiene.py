import importlib.util
import os
import random
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


def notice(name, style, width, holder="Acme Corp", year=2026):
    body = [f"Copyright (c) {year} {holder}", ""]
    for para in MODULE.LICENSES[name].split("\n\n"):
        body += textwrap.wrap(para, width, break_long_words=False) + [""]
    body = body[:-1]
    if style == "block":
        return "/*\n" + "".join(f" * {line}".rstrip() + "\n" for line in body) + " */\n"
    if style == "html":
        return "<!--\n" + "".join(f"  {line}".rstrip() + "\n" for line in body) + "-->\n"
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
    "Dockerfile": "FROM alpine\nRUN <<EOF\n# pin curl because the latest release breaks TLS\napk add curl\nEOF\n",
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
    "Dockerfile:3: comment: # pin curl because the latest release breaks TLS",
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


def gate(script, repo, *args):
    r = subprocess.run([sys.executable, "-I", str(script), *args], cwd=repo, env=ENV, capture_output=True, text=True)
    return r.returncode, r.stdout.splitlines(), r.stderr.splitlines()


def hygiene(repo, *args):
    return gate(HYGIENE, repo, *args)


with tempfile.TemporaryDirectory() as tmp:
    repo = Path(tmp)
    git(repo, "init", "-q", "-b", "main")
    base = commit(repo, BASE, "base")
    head = commit(repo, HEAD, "head", remove=["src/gone.ts", "notes.txt", "docs/old.md"])
    clean = commit(repo, {"src/clean.ts": "export const c = 3;\n", "clean.py": 's = "#x"\n'}, "clean")

    code, out, err = hygiene(repo, base, head)
    assert (code, out, err) == (1, EXPECTED, []), (code, out, err)

    allowed = ("allowed.ts", "docs/notes.md", "Dockerfile")
    code, out, err = hygiene(repo, base, head, *(x for path in allowed for x in ("--allow", path)))
    kept = [line for line in EXPECTED if not line.startswith(("allowed.ts", "docs/", "Dockerfile"))]
    assert (code, out) == (1, kept), (code, out)

    assert hygiene(repo, head, clean) == (0, [], []), hygiene(repo, head, clean)

    for args in ((), (base,), (base, "no-such-rev")):
        code, out, err = hygiene(repo, *args)
        assert code == 2 and out == [] and len(err) == 1, (args, code, out, err)

BODY = "".join(f"export const v{i} = {i};\n" for i in range(8))
MOVE_BASE = {
    "f.ts": "export function f() {\n  // retries because the API drops calls\n  g();\n}\n",
    "a.py": "timeout = 30  # seconds\n",
    "k.py": 'def f():\n    """Doc."""\n    # why\n    return 1\n\n\ndef g():\n    """\n    Old text.\n    """\n',
    "m.ts": "// first\nexport const a = 1;\nexport const b = 2;\nexport const c = 3;\n",
    "e.ts": "// old wording\nexport const e = 1;\n",
    "e.py": "x = 1  # old wording\n",
    "dup.ts": "  // shared note\nexport const x = 1;\n",
    "dup.py": "x = 1  # shared note\n",
    "old.ts": "  // kept through the rename\n" + BODY,
    "b.ts": "/**\n * Legacy adder.\n */\nexport function add(a: number, b: number) {\n  return a + b;\n}\n" + BODY,
}
MOVE_HEAD = {
    "f.ts": "export function f() {\n  if (x) {\n    // retries because the API drops calls\n    g();\n  }\n}\n",
    "a.py": "timeout = 60  # seconds\n",
    "k.py": 'class K:\n    def f(self):\n        """Doc."""\n        # why\n        return 1\n\n'
            '    def g(self):\n        """\n        New text.\n        """\n',
    "m.ts": "export const a = 1;\nexport const b = 2;\n// first\nexport const c = 3;\n",
    "e.ts": "// new wording\nexport const e = 1;\n",
    "e.py": "x = 1  # new wording\n",
    "dup.ts": "// shared note\nexport const x = 1;\n// shared note\n",
    "dup.py": "x = 2  # shared note\ny = 3  # shared note\n",
    "new.ts": "// kept through the rename\n" + BODY,
    "b.ts": BODY + "/**\n * Multiplies because the billing API rounds sums.\n */\n"
                   "export function mul(a: number, b: number) {\n  return a * b;\n}\n",
}
MOVE_EXPECTED = [
    "a.py:1: comment: timeout = 60  # seconds",
    "b.ts:9: comment: /**",
    "dup.py:1: comment: x = 2  # shared note",
    "dup.py:2: comment: y = 3  # shared note",
    "dup.ts:1: comment: // shared note",
    "dup.ts:3: comment: // shared note",
    "e.py:1: comment: x = 1  # new wording",
    "e.ts:1: comment: // new wording",
    "f.ts:3: comment: // retries because the API drops calls",
    'k.py:3: comment: """Doc."""',
    "k.py:4: comment: # why",
    'k.py:8: comment: """',
    "m.ts:3: comment: // first",
    "new.ts:1: comment: // kept through the rename",
]

with tempfile.TemporaryDirectory() as tmp:
    repo = Path(tmp)
    git(repo, "init", "-q", "-b", "main")
    base = commit(repo, MOVE_BASE, "base")
    head = commit(repo, MOVE_HEAD, "head", remove=["old.ts"])
    assert "R" in git(repo, "diff", "--name-status", "-M", base, head, "--", "old.ts", "new.ts")
    assert hygiene(repo, base, head) == (1, MOVE_EXPECTED, []), hygiene(repo, base, head)


PROPERTY_SEED = int(os.environ.get("RUN_SPEC_PROPERTY_SEED", "20261115"))
PROPERTY_CASES = 300
WORDS = ("retries cache because upstream drops calls timeout queue parser backoff flaky renders avatar slow billing "
         "rounds sums bundler widget gadget ledger socket").split()
HOLDERS = ("Acme Corp", "Widget Works Ltd", "Gadget Labs", "Ledger Socket Inc", "Parser Guild")


class Lang:
    def __init__(self, ext, statements, comments, notices, strings=(), markers=()):
        self.ext, self.statements, self.comments = ext, statements, comments
        self.notices, self.strings, self.markers = notices, strings, markers


LANGS = (
    Lang("ts", ("const {a} = {n};", 'let {a}: string = "{t}";',
                "export function {a}({b}: number) {{\n  return {b} / {n};\n}}", "if ({a} > {n}) {{\n  {b}();\n}}",
                "const {a} = `{t} ${{{b}}}`;", "{a}.push({b}, {n});", "import {{ {a} }} from './{b}';"),
         ("// {t}", "/* {t} */", "/** {t} */"), ("//", "block"),
         ('const {a} = "{p}{m}{s}";', "const {a} = '{p}{m}{s}';", "const {a} = `{p}{m}{s} ${{{b}}} {p}{m}`;",
          'const {a} = "{p}\\"{m}{s}";', "export default {{ {a}: '{p}{m}{s}', {b}: {n} }};",
          'console.log("{p}{m}{s}", {n});'), ("//", "/*")),
    Lang("java", ("int {a} = {n};", 'String {a} = "{t}";', "public void {a}() {{\n  {b}({n});\n}}",
                  "if ({a} > {n}) {{\n  {b}();\n}}"),
         ("// {t}", "/* {t} */", "/** {t} */"), ("//", "block")),
    Lang("go", ("package {a}", "func {a}({b} int) int {{\n\treturn {b} / {n}\n}}", "var {a} = {n}",
                'fmt.Println("{t}")', "if {a} > {n} {{\n\t{b}()\n}}"), ("// {t}", "/* {t} */"), ("//",)),
    Lang("css", (".{a} {{\n  margin: {n}px;\n}}", "#{b} .{a} {{ color: red; }}",
                 "@media (min-width: {n}px) {{\n  .{a} {{ display: none; }}\n}}"), ("/* {t} */",), ("block",)),
    Lang("html", ("<p>{t}</p>", '<div class="{a}">', "</div>", '<a href="/{a}">{t}</a>',
                  "<ul>\n  <li>{t}</li>\n</ul>"), ("<!-- {t} -->",), ("html",)),
    Lang("sh", ("{a}={n}", 'echo "{t}"', 'if [ "$1" = "{a}" ]; then\n  {b} {n}\nfi', "{a}() {{\n  echo {n}\n}}",
                "export {a}={b}"), ("# {t}",), ("#",),
         ('echo "{p}{m}{s}"', "echo '{p}{m}{s}'", '{a}="{p}{m}{s}"', "printf '%s\\n' \"{p}{m}{s}\"",
          'if [ "$1" = "{p}{m}{s}" ]; then'), ("#", "//")),
    Lang("sql", ("SELECT {a}, {b} FROM {a} WHERE {a} > {n};", "INSERT INTO {a} VALUES ({n}, '{t}');",
                 "UPDATE {a} SET {b} = {n} WHERE id = {n};", "SELECT\n  {a},\n  {b}\nFROM {a};"),
         ("-- {t}",), ("--",),
         ("SELECT '{p}{m}{s}' AS {a};", "INSERT INTO {a} VALUES ('{p}{m}{s}', {n});",
          "UPDATE {a} SET {b} = '{p}''{m}{s}' WHERE id = {n};", "SELECT {a} FROM {b} WHERE {a} LIKE '%{m}%';"),
         ("--",)),
    Lang("py", ("{a} = {n}", '{a} = "{t}"', "def {a}({b}):\n    return {b} + {n}", "if {a} > {n}:\n    {b} = {a}",
                "print({a}, {b})", "class {a}:\n    {b} = {n}"), ("# {t}",), ("#",),
         ('{a} = "{p}{m}{s}"', "{a} = '{p}{m}{s}'", '{a} = f"{p}{m}{s} {{{b}}}"', '{a} = r"{p}{m}{s}"',
          '{a} = b"{p}{m}{s}"', '{a} = """{p}{m}{s}"""', 'print("{p}{m}{s}", {n})', '{a} = "{p}\\"{m}{s}"',
          '{a} = {{"{b}": "{p}{m}{s}"}}'), ("#", "--", "/*")),
    Lang("rb", ("{a} = {n}", 'puts "{t}"', "def {a}({b})\n  {b} + {n}\nend", "if {a} > {n}\n  {b}\nend"),
         ("# {t}",), ("#",)),
    Lang("yaml", ("{a}: {n}", '{a}: "{t}"', "{a}:\n  {b}: {n}\n  items:\n    - {t}"), ("# {t}",), ("#",),
         ('{a}: "{p}{m}{s}"', "{a}: '{p}{m}{s}'", '- "{p}{m}{s}"', '  {a}: "{p}{m}{s}"', '{a}: ["{p}{m}{s}", {n}]'),
         ("#",)),
)
STRING_LANGS = tuple(lang for lang in LANGS if lang.strings)


def ident(rng):
    return rng.choice(WORDS) + str(rng.randint(0, 99))


def phrase(rng):
    return " ".join(rng.choice(WORDS) for _ in range(rng.randint(1, 5)))


def fill(rng, template, markers=()):
    return template.format(a=ident(rng), b=ident(rng), n=rng.randint(0, 999), t=phrase(rng),
                           m=rng.choice(markers or ("",)), p=rng.choice(("", phrase(rng) + " ", ident(rng) + ":")),
                           s=rng.choice(("", " " + phrase(rng), ident(rng))))


def source_lines(rng, lang, templates):
    lines = []
    for _ in range(rng.randint(1, 12)):
        lines += fill(rng, rng.choice(templates), lang.markers).split("\n")
        if rng.random() < 0.2:
            lines.append("")
    return lines


def source(rng, lang, templates=None):
    return "\n".join(source_lines(rng, lang, templates or lang.statements)) + "\n"


def reported_in_repo(script, files, base_files=None):
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        git(repo, "init", "-q", "-b", "main")
        base = commit(repo, {"keep.txt": "x\n", **(base_files or {})}, "base")
        head = commit(repo, files, "head")
        return gate(script, repo, base, head)


def unexpected_output(script, files):
    code, out, err = reported_in_repo(script, files)
    shown = [f"{line}\n{files.get(line.split(':')[0], '')}" for line in out[:3]]
    return [] if (code, out, err) == (0, [], []) else [f"exit {code}, stderr {err}", *shown]


def no_comment_tokens(rng, script):
    files = {}
    for i in range(PROPERTY_CASES):
        lang = rng.choice(LANGS)
        files[f"case{i:03d}.{lang.ext}"] = source(rng, lang)
    return unexpected_output(script, files)


def marker_inside_string(rng, script):
    files = {}
    for i in range(PROPERTY_CASES):
        lang = rng.choice(STRING_LANGS)
        files[f"case{i:03d}.{lang.ext}"] = source(rng, lang, lang.statements + lang.strings * 3)
    return unexpected_output(script, files)


def licence_notice_any_width(rng, script):
    files = {}
    for i in range(PROPERTY_CASES):
        lang = rng.choice([x for x in LANGS if x.notices])
        text = notice(rng.choice(sorted(MODULE.LICENSES)), rng.choice(lang.notices), rng.randint(1, 200),
                      rng.choice(HOLDERS), rng.randint(1990, 2026))
        if rng.random() < 0.5:
            text = text.replace("http://", "https://")
        files[f"case{i:03d}.{lang.ext}"] = text + source(rng, lang)
    return unexpected_output(script, files)


def added_comment_reported(rng, script):
    base_files, head_files, expected = {}, {}, []
    for i in range(PROPERTY_CASES):
        lang = rng.choice(LANGS)
        path, lines = f"case{i:03d}.{lang.ext}", source_lines(rng, lang, lang.statements)
        at = rng.randint(0, len(lines))
        comment = " " * rng.choice((0, 0, 2, 4)) + fill(rng, rng.choice(lang.comments))
        base_files[path] = "\n".join(lines) + "\n"
        head_files[path] = "\n".join(lines[:at] + [comment] + lines[at:]) + "\n"
        expected.append(f"{path}:{at + 1}: comment: {comment.strip()}")
    code, out, err = reported_in_repo(script, head_files, base_files)
    missing = sorted(set(expected) - set(out))
    return [] if (code, out, err) == (1, sorted(expected), []) else [
        f"exit {code}, stderr {err}, {len(out)} of {len(expected)} lines reported", *missing[:3]]


PROPERTIES = {"no-comment-tokens": no_comment_tokens, "marker-inside-string": marker_inside_string,
              "licence-notice-any-width": licence_notice_any_width, "added-comment-reported": added_comment_reported}


def run_properties(script, seed):
    return {name: prop(random.Random(f"{seed}/{name}"), script) for name, prop in PROPERTIES.items()}


def failure_report(results, seed):
    return [f"property {name} failed with seed {seed}; rerun with RUN_SPEC_PROPERTY_SEED={seed}\n" + "\n".join(details)
            for name, details in results.items() if details]


REPORTS_EVERY_FILE = (
    "import subprocess, sys\n"
    "diff = subprocess.run(['git', 'diff', '--name-only', f'{sys.argv[1]}...{sys.argv[2]}'], capture_output=True, text=True)\n"
    "print('\\n'.join(f'{path}:1: comment: x' for path in diff.stdout.split()))\n"
    "sys.exit(1)\n"
)

with tempfile.TemporaryDirectory() as tmp:
    broken_gate = Path(tmp) / "hygiene.py"
    broken_gate.write_text(REPORTS_EVERY_FILE)
    failed = run_properties(broken_gate, 7)
    assert all(failed.values()), failed
    assert all("with seed 7;" in text for text in failure_report(failed, 7)), failure_report(failed, 7)
    assert failed == run_properties(broken_gate, 7)
    assert failed != run_properties(broken_gate, 8)

results = run_properties(HYGIENE, PROPERTY_SEED)
for name, details in results.items():
    print(f"property {name}: {PROPERTY_CASES} cases, seed {PROPERTY_SEED}, {'FAILED' if details else 'passed'}")
if any(results.values()):
    sys.exit("\n\n".join(failure_report(results, PROPERTY_SEED)))

print("ok")
