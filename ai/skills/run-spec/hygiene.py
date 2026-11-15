#!/usr/bin/env python3
"""Hygiene gate for run-spec: comment lines and Markdown files that a git range adds.

Usage, from inside the repository: hygiene.py <base> <head> [--allow <path>]...

Checks only what <base>...<head> adds. Prints `<path>:<line>: comment: <text>` or
`<path>: markdown: added Markdown file` per violation and exits 1; exits 0 and prints nothing when
clean; exits 2 with one stderr line on a usage or git error.
"""
import argparse
import ast
import io
import re
import subprocess
import sys
import tokenize
import warnings
from pathlib import PurePosixPath

C_LIKE = "js jsx ts tsx mjs cjs mts cts java kt kts scala groovy go rs c h cc cpp hpp cs swift dart php scss less astro"
MARKERS = {**{e: ("//", "/*", "{/*") for e in C_LIKE.split()}, "vue": ("//", "/*", "{/*", "<!--"),
           "svelte": ("//", "/*", "{/*", "<!--"), "css": ("/*",), "sql": ("--",), "lua": ("--",), "hs": ("--",),
           **{e: ("<!--",) for e in "html htm xml svg".split()},
           **{e: ("#",) for e in "sh bash zsh fish rb yml yaml toml pl r ex exs tf hcl ps1 conf ini cfg".split()}}
HASH_NAMES = set("Dockerfile Makefile makefile Containerfile Gemfile Rakefile".split())
SKIP_DIRS = {"node_modules", "vendor", "dist"}
LOCKFILE = re.compile(r"(?:\.lockb?|-lock\.(?:json|ya?ml)|^go\.sum|^npm-shrinkwrap\.json)$")
CODING = re.compile(r"[ \t\f]*#.*?coding[:=]")
PRAGMAS = r"@(?:\w+-environment(?:-options)?|flow|noflow|generated|format|prettier|jsx\w*)\b"
TAG = (r"(?:(?:pyright|pylint|mypy|ruff|flake8|fmt|isort|yapf|pytype|type|typed|rubocop|tslint|swiftlint|phpcs|jscs|"
       r"frozen_string_literal|shareable_constant_value|warn_indent|warn_past_scope|encoding):|"
       r"(?:eslint|stylelint|deno-lint|deno-fmt|ktlint|tflint|pyre)-|@ts-|syntax=|jshint\s+(?:ignore:|[\w-]+\s*:)|"
       r"(?:prettier-ignore|biome-ignore|(?:istanbul|c8|v8) ignore|clang-format (?:on|off)|@license|"
       r"shellcheck|hadolint|yamllint|nolint(?:nextline|begin|end)?|nosonar|nosec|noqa|pragma|"
       r"spdx-license-identifier)\b)")
DIRECTIVE = re.compile(rf"(?:#|//+|/\*+|\{{/\*|--|<!--)\s*{TAG}|/\*+\s*(?:eslint|globals?|exported)\s|//go:|/// <reference",
                       re.I)
PRAGMA_LINE = re.compile(rf"(?:\s*{PRAGMAS}(?:[ \t]+(?!@)(?:\{{.*\}}|\S+))?)+\s*", re.I)
BSD_HEAD = ("Redistribution and use in source and binary forms, with or without modification, are permitted provided "
            "that the following conditions are met:\n\n1. Redistributions of source code must retain the above "
            "copyright notice, this list of conditions and the following disclaimer.\n\n2. Redistributions in binary "
            "form must reproduce the above copyright notice, this list of conditions and the following disclaimer in "
            "the documentation and/or other materials provided with the distribution.\n\n")
BSD_TAIL = ('THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED '
            "WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A "
            "PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR "
            "ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT "
            "LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS "
            "INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR "
            "TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF "
            "ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.")
LICENSES = {
    "MIT": "Permission is hereby granted, free of charge, to any person obtaining a copy of this software and "
           'associated documentation files (the "Software"), to deal in the Software without restriction, including '
           "without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell "
           "copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the "
           "following conditions:\n\nThe above copyright notice and this permission notice shall be included in all "
           'copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF '
           "ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR "
           "A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR "
           "ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, "
           "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.",
    "BSD-2-Clause": BSD_HEAD + BSD_TAIL,
    "BSD-3-Clause": BSD_HEAD + "3. Neither the name of the copyright holder nor the names of its contributors may be "
                    "used to endorse or promote products derived from this software without specific prior written "
                    "permission.\n\n" + BSD_TAIL,
    "Apache-2.0": 'Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in '
                  "compliance with the License. You may obtain a copy of the License at\n\n"
                  "http://www.apache.org/licenses/LICENSE-2.0\n\nUnless required by applicable law or agreed to in "
                  'writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT '
                  "WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific "
                  "language governing permissions and limitations under the License.",
    "Meta": "This source code is licensed under the MIT license found in the LICENSE file in the root directory of "
            "this source tree.",
    "Go": "Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.",
    "reserved": "All rights reserved.",
}
OWNER = re.compile(r"(?:copyright\s*(?:\(c\)|©|\d{4}|the\s)|@copyright\b|(?:\(c\)|©)\s*\d{4}|@license\b|"
                   r"spdx-license-identifier\s*:)", re.I)
STRIP = re.compile(r"^\s*(?:<!--|\{/\*|/\*+!?|//+!?|#+|--+|\*+(?!/))?|(?:\*+/\}?|-->)\s*$")
CLOSERS = {"/*": "*/", "{/*": "*/", "<!--": "-->"}
HUNK = re.compile(r"@@ -\d+(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def die(msg):
    print(f"hygiene: {msg}", file=sys.stderr)
    sys.exit(2)


class Args(argparse.ArgumentParser):
    def error(self, message):
        die(f"{message} (usage: hygiene.py <base> <head> [--allow <path>]...)")


def git(*args):
    try:
        r = subprocess.run(["git", "-c", "core.quotePath=false", *args], capture_output=True)
    except OSError as e:
        die(f"git: {e}")
    if r.returncode:
        die((r.stderr.decode("utf-8", "replace").strip().splitlines() or [f"git {args[0]} failed"])[0])
    return r.stdout.decode("utf-8", "replace")


def added_lines(patch):
    files, path, n, old_left, new_left = {}, None, 0, 0, 0
    for line in patch.split("\n"):
        if old_left > 0 or new_left > 0:
            tag = line[:1]
            if tag == "+":
                files[path].append((n, line[1:].rstrip("\r")))
                n, new_left = n + 1, new_left - 1
            elif tag == "-":
                old_left -= 1
            elif tag == " ":
                n, old_left, new_left = n + 1, old_left - 1, new_left - 1
        elif line.startswith("diff --git "):
            path = None
        elif line.startswith("+++ "):
            name = line[4:].rstrip("\t")
            path = (ast.literal_eval(name) if name.startswith('"') else name)[2:]
            files.setdefault(path, [])
        elif path is not None and (m := HUNK.match(line)):
            old_left, n, new_left = int(m[1] or 1), int(m[2]), int(m[3] or 1)
    return files


def created(fields):
    paths, i = set(), 0
    while i + 1 < len(fields):
        if fields[i].startswith("R"):
            if not fields[i + 1].lower().endswith((".md", ".mdx")):
                paths.add(fields[i + 2])
            i += 3
        else:
            paths.add(fields[i + 1])
            i += 2
    return paths


def pragma(text):
    return bool(PRAGMA_LINE.fullmatch(STRIP.sub("", text).strip()))


def exempt(n, text):
    opener = next((o for o in CLOSERS if text.startswith(o)), None)
    closed = opener is None or CLOSERS[opener] in text[len(opener):]
    return ((n == 1 and text.startswith("#!")) or (n <= 2 and bool(CODING.match(text))) or bool(DIRECTIVE.match(text))
            or (closed and pragma(text)))


def words(text):
    return ["http" if w == "https" else w for w in re.findall(r"[a-z0-9]+", text.lower())]


CORPUS = " " + " | ".join(" ".join(words(t)) for t in LICENSES.values()) + " "


def notice_lines(entries):
    found, span = set(), []

    def close():
        if sum(len(w) for _, w in span) >= 3:
            found.update(n for n, _ in span)

    for n, line in entries:
        text = STRIP.sub("", line).strip()
        w = words(text)
        if not w:
            continue
        if OWNER.match(text):
            close()
            found.add(n)
            span = []
        elif f" {' '.join([x for _, ws in span for x in ws] + w)} " in CORPUS:
            span.append((n, w))
        else:
            close()
            span = [(n, w)] if f" {' '.join(w)} " in CORPUS else []
    close()
    return found


def header(text, markers):
    lines = text.split("\n")
    i = 1 if lines[0].startswith(("#!", "<?")) else 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    blocks = []
    while i < len(lines) and (opener := next((m for m in markers if lines[i].strip().startswith(m)), None)):
        j, close = i, CLOSERS.get(opener)
        if close and close not in lines[i].strip()[len(opener):]:
            j += 1
            while j < len(lines) and close not in lines[j]:
                j += 1
        blocks.append(range(i + 1, min(j, len(lines) - 1) + 2))
        i = j + 1
    notice = notice_lines([(n, lines[n - 1]) for block in blocks for n in block])
    top = set()
    for block in blocks:
        content = [n for n in block if words(STRIP.sub("", lines[n - 1]))]
        if (content or notice) and all(n in notice or pragma(lines[n - 1]) for n in content):
            top.update(block)
    return top


def marker_hits(markers, lines):
    return {n: s for n, text in lines if (s := text.strip()).startswith(markers) and not exempt(n, s)}


def python_hits(head, path, lines):
    text = git("show", f"{head}:{path}")
    src = [s.rstrip("\r") for s in text.split("\n")]
    added = {n for n, _ in lines}
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tree = ast.parse(text)
            tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except (SyntaxError, ValueError, tokenize.TokenError, RecursionError):
        return marker_hits(("#",), lines)
    hits = {t.start[0]: src[t.start[0] - 1] for t in tokens
            if t.type == tokenize.COMMENT and t.start[0] in added and not exempt(t.start[0], t.string)}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.body:
            doc = node.body[0]
            if (isinstance(doc, ast.Expr) and isinstance(doc.value, ast.Constant) and isinstance(doc.value.value, str)
                    and added.intersection(range(doc.lineno, doc.end_lineno + 1))):
                hits[doc.lineno] = src[doc.lineno - 1]
    return hits


def main():
    ap = Args(prog="hygiene.py")
    ap.add_argument("base")
    ap.add_argument("head")
    ap.add_argument("--allow", action="append", default=[])
    a = ap.parse_args()
    rng = f"{a.base}...{a.head}"
    new_files = created(git("diff", "--name-status", "-z", "-M", "--diff-filter=AR", rng, "--").split("\0"))
    files = added_lines(git("diff", "-U0", "-M", "--no-color", "--no-ext-diff", "--src-prefix=a/", "--dst-prefix=b/",
                            "--diff-filter=d", rng, "--"))
    out = []
    for path in sorted(new_files | set(files)):
        parts = path.split("/")
        if path in a.allow:
            continue
        if path.lower().endswith((".md", ".mdx")):
            if path in new_files and not (parts[0] == ".scratch" and "issues" in parts[1:-1]):
                out.append(f"{path}: markdown: added Markdown file")
            continue
        if SKIP_DIRS.intersection(parts[:-1]) or LOCKFILE.search(parts[-1]):
            continue
        lines = files.get(path)
        if not lines:
            continue
        if path.lower().endswith((".py", ".pyi")):
            m = ("#",)
            hits = python_hits(a.head, path, lines)
        else:
            p = PurePosixPath(path)
            m = ("#",) if p.name in HASH_NAMES else MARKERS.get(p.suffix.lower()[1:])
            hits = marker_hits(m, lines) if m else {}
        if hits:
            top = header(git("show", f"{a.head}:{path}"), m)
            hits = {n: text for n, text in hits.items() if n not in top}
        out += [f"{path}:{n}: comment: {text.strip()[:120]}" for n, text in sorted(hits.items())]
    if out:
        print("\n".join(out))
    sys.exit(1 if out else 0)


if __name__ == "__main__":
    main()
