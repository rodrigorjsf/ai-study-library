# Diagrams with archify

When the `archify` skill is installed, render the study's diagrams with it: it validates layout, and its
`sources` field checks every component's `path:line` against the pinned checkout. Without archify, keep the
Mermaid diagrams in the chapters and skip this file.

## Which diagrams

| Diagram | Type | Content |
|---|---|---|
| `<repo>.architecture.json` | architecture | Real components from the ARCHIFY INPUT section; **each harness that matters is its own node** with its real mechanism (hooks, MCP only, rules file); egress destinations as external nodes, with defaults in the sublabel |
| `<repo>-<harness>.sequence.json` | sequence | One session in that harness, drawn from code, including what is **not** injected |
| `plan-target.architecture.json` | architecture | The plan's target architecture (one node per scope) |
| `plan-<state>.lifecycle.json` | lifecycle | Any state machine the plan introduces |

At most 12 primary nodes per diagram. Labels in the study's language; identifiers verbatim.

## Commands

From the archify skill directory:

```bash
node bin/archify.mjs validate <type> <spec.json> --quality showcase --repo-root <pinned checkout> --json
node bin/archify.mjs deliver  <type> <spec.json> <study>/html/<name>.html --quality showcase --repo-root <pinned checkout> --json
```

## Gotchas met in practice

- A spec with `meta.repository` refuses to render without `--repo-root <checkout>`.
- A note in `meta.views` is limited to 140 characters.
- Sequences: no self-messages (the span must be ≥ 60 px); keep 28 px or more between messages that share
  columns; keep every message inside the readable band. A tall `viewBox` shrinks the text: prefer
  `[960, 820]` with `column_fit: "spread"` and short participant sublabels.
- Lifecycle: the gaps on the main rail are too narrow for labels; drop labels that the target state already
  says, and put the meaning in the state's sublabel.
- Architecture: fix one diagnosed control per round (`labelAt`, then `fromSide`/`toSide`, then `via`). When
  two edges must cross, move the edge to the component that really emits the call (check the code) before
  adding detours.
- `visual-check` needs Chrome or Chromium (`ARCHIFY_CHROME`). Without it the check is skipped: report that, and
  delete the `*.visual-check.json` sidecars it writes.
- The viewer's fixed interface is English or Chinese only; say so when the study is in another language.
