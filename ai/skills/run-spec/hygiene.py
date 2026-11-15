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
SKIP_DIRS = {"node_modules", "vendor", "dist", "build", ".git"}
LOCKFILE = re.compile(r"(?:\.lockb?|-lock\.(?:json|ya?ml)|^go\.sum|^npm-shrinkwrap\.json)$")
CODING = re.compile(r"[ \t\f]*#.*?coding[:=]")
DIRECTIVE = re.compile(
    r"(?:#|//+|/\*+|\{/\*|--|<!--)\s*(?:eslint-|@ts-|prettier-ignore|biome-ignore|(?:istanbul|c8|v8) ignore|"
    r"shellcheck|rubocop:|nolint|nosonar|spdx-license-identifier|@license|syntax=|yamllint|"
    r"noqa|type:|pragma|pylint:|mypy:|fmt:|isort:)|//go:|/// <reference", re.I)
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


def exempt(n, text):
    return (n == 1 and text.startswith("#!")) or (n <= 2 and bool(CODING.match(text))) or bool(DIRECTIVE.match(text))


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
    new_files = set(filter(None, git("diff", "--name-only", "-z", "-M", "--diff-filter=A", rng, "--").split("\0")))
    files = added_lines(git("diff", "-U0", "-M", "--no-color", "--no-ext-diff", "--src-prefix=a/", "--dst-prefix=b/",
                            "--diff-filter=d", rng, "--"))
    out = []
    for path in sorted(new_files | set(files)):
        parts = path.split("/")
        if path in a.allow or SKIP_DIRS.intersection(parts[:-1]) or LOCKFILE.search(parts[-1]):
            continue
        if path.lower().endswith((".md", ".mdx")):
            if path in new_files and not (parts[0] == ".scratch" and "issues" in parts[1:-1]):
                out.append(f"{path}: markdown: added Markdown file")
            continue
        lines = files.get(path)
        if not lines:
            continue
        if path.lower().endswith((".py", ".pyi")):
            hits = python_hits(a.head, path, lines)
        else:
            p = PurePosixPath(path)
            m = ("#",) if p.name in HASH_NAMES else MARKERS.get(p.suffix.lower()[1:])
            hits = marker_hits(m, lines) if m else {}
        out += [f"{path}:{n}: comment: {text.strip()[:120]}" for n, text in sorted(hits.items())]
    if out:
        print("\n".join(out))
    sys.exit(1 if out else 0)


if __name__ == "__main__":
    main()
