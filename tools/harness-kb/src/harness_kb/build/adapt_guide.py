# tools/harness-kb/src/harness_kb/build/adapt_guide.py
from __future__ import annotations
import re

# Each rule: (regex, replacement). Order matters — most specific first.
_RULES: list[tuple[re.Pattern, str]] = [
    (re.compile(r"/graphify\s+query\s+"), r"harness-kb graph query "),
    (re.compile(r"/graphify\s+path\s+"), r"harness-kb graph path "),
    (re.compile(r"/graphify\s+explain\s+"), r"harness-kb graph explain "),
    (re.compile(r"/graphify\s+--mcp"), r"harness-kb --mcp"),
    # graphify-out/wiki/<Name>.md → harness-kb wiki get <Name>
    (re.compile(r"`?graphify-out/wiki/([A-Za-z0-9_\-+]+?)\.md`?"), r"`harness-kb wiki get \1`"),
    # graphify-out/graph.json (or graphify-out/) → harness-kb graph
    (re.compile(r"`?graphify-out/graph\.json`?"), r"`harness-kb graph` (bundled graph)"),
    # graphify-out/GRAPH_REPORT.md → bundled location description (used in three contexts)
    (re.compile(r"`?graphify-out/GRAPH_REPORT\.md`?"), r"`[bundled at data/graph/GRAPH_REPORT.md]`"),
    # graphify-out/graph.html — NOT bundled; delete the entire bullet line
    (re.compile(r"^- `?graphify-out/graph\.html`?[^\n]*\n", re.MULTILINE), r""),
    # graphify-out/manifest.json — NOT bundled; delete the entire bullet line
    (re.compile(r"^- `?graphify-out/manifest\.json`?[^\n]*\n", re.MULTILINE), r""),
    (re.compile(r"`?graphify-out/`?(?=[\s.,)])"), r"`harness-kb graph + harness-kb wiki`"),
    # graphify-out/<anything> catch-all (must come after specific rules above)
    (re.compile(r"`?graphify-out/[^\s`'\")\]]+`?"), r"`harness-kb graph + harness-kb wiki`"),
    # generic /graphify mention not caught above (fail-safe)
    (re.compile(r"/graphify\b"), r"harness-kb"),
]


def adapt(text: str) -> str:
    out = text
    for rx, repl in _RULES:
        out = rx.sub(repl, out)
    return out
