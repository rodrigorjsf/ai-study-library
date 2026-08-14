# Rules

Rules that steer coding agents, organized by the tool that loads them. The same rule is
kept in one variant per tool, because the activation metadata — not the guidance — is what
differs between hosts.

```
ai/rules/
  claude/java-concurrency-static.md    # Claude Code / agent rule, activated by path globs
  cursor/java-concurrency-static.mdc   # Cursor project rule, "Apply Intelligently"
```

## Java concurrency & `static`

Decision rule for `static` in high-RPM Java 25 services: shared state, virtual threads,
DynamoDB/Redis client lifecycle, and OpenTelemetry. The body is identical across both
variants; keep them in sync when editing one.

Executable enforcement lives in
[`ai/examples/java/static-concurrency-enforcement/`](../examples/java/static-concurrency-enforcement/) —
two ArchUnit suites and an Error Prone `BugChecker`.

### Installing the Claude variant

Copy to `.claude/rules/java-concurrency-static.md` in the target repo. Activation comes
from the `paths` frontmatter, so the rule loads whenever a matching Java or build file is
in context:

```yaml
---
paths:
  - "**/*.java"
  - "**/pom.xml"
  - "**/build.gradle{,.kts}"
---
```

### Installing the Cursor variant

Copy to `.cursor/rules/java-concurrency-static.mdc` in the target repo. Cursor derives the
rule type from which frontmatter fields are present:

| Rule type | Frontmatter |
| --- | --- |
| Always Apply | `alwaysApply: true` |
| Apply Intelligently | `description` set, `alwaysApply: false`, **no** `globs` |
| **Apply to Specific Files** | **`globs` set** — what this rule uses |
| Apply Manually | none of the three — invoked with `@java-concurrency-static` |

This rule is scoped to Java sources and build files, so it attaches only when one of them
is in context:

```yaml
---
description: <what the rule covers and when it is relevant>
globs: **/*.java,**/pom.xml,**/build.gradle,**/build.gradle.kts
alwaysApply: false
---
```

Setting `globs` makes the file match the trigger, not the agent's judgement. The
`description` is kept anyway — it is what the settings UI shows and what `@`-mention
discovery reads — but it no longer drives activation. If you would rather have the agent
decide by relevance (it pulls the rule in on shared state, monitors, virtual threads or
client lifecycle, and skips it on a getter rename, at the cost of sometimes not pulling it
in at all), delete the `globs` line and the rule reverts to Apply Intelligently.

### Frontmatter gotchas

Each item is tagged with how well it is established — see [References](#references) for
where each one comes from.

- **Do not quote the glob list.** `globs: "**/*.java,**/pom.xml"` is read as a single
  literal pattern containing a comma, so it matches nothing; comma-separated and unquoted
  is correct. *(Secondhand — see [the note on this finding](#the-globs-quoting-finding)
  before trusting it. What is directly verified: quoting does collapse the list into one
  string, and Cursor's own examples are unquoted.)*
- **The frontmatter is not strict YAML.** A bare `*` is a YAML alias indicator, so a
  standard parser rejects `globs: **/*.java` outright — verified locally with PyYAML
  (`ScannerError`). Cursor reads it with its own parser and its UI writes it unquoted, so
  do not "fix" it into a YAML list. *(Verified.)*
- **Brace expansion is not relied on.** `**/build.gradle{,.kts}` is written out as two
  explicit patterns. The Claude variant keeps the brace form because its `paths` field is
  parsed as real YAML by a different engine. *(Deliberate choice, not a documented
  limitation — braces may well work.)*
- **The extension must be `.mdc`** for frontmatter to be read. A plain `.md` in
  `.cursor/rules/` is still a valid rule, but carries no activation metadata. *(Official.)*
- **Keep a rule under 500 lines** and split anything larger into composable rules; this one
  is ~110. *(Official.)*

## References

`cursor.com` is blocked by this container's network egress proxy, so the official docs page
was read through two mirrors rather than at the source. Everything below was opened and
read; nothing is cited from a search-engine summary alone, except where explicitly marked.

### Official — Cursor, *Rules*

<https://cursor.com/docs/rules> (not reachable here). Consulted via:

1. **This repo's vendored copy**, [`ai/docs/cursor/rules/rules.md`](../docs/cursor/rules/rules.md) —
   the text matches the current published page. Precise anchors:
   - line 31 — `.md` vs `.mdc`: "Cursor supports `.md` and `.mdc` extensions. Use `.mdc`
     files with frontmatter to specify `description` and `globs`."
   - lines 41–50, *Rule anatomy* — the four rule types and the note that the dropdown
     "changes properties `description`, `globs`, `alwaysApply`". This is the basis for the
     rule-type table above.
   - line 74, *Best practices* — "Keep rules under 500 lines".
   - lines 92–105, *Rule file format* — the `description` + `alwaysApply: false` example,
     and the sentence that decides Apply Intelligently: "If alwaysApply is true, the rule
     will be applied to every chat session. Otherwise, the description of the rule will be
     presented to the Cursor Agent to decide if it should be applied."
   - line 301, *FAQ — "Why isn't my rule being applied?"* — "For `Apply Intelligently`,
     ensure a description is defined. For `Apply to Specific Files`, ensure the file
     pattern matches referenced files." This is what establishes that `globs` and
     description-based selection are different modes rather than additive.
2. **GitHub mirror** — [sanjeed5/awesome-cursor-rules-mdc → `cursor-rules-reference.md`](https://github.com/sanjeed5/awesome-cursor-rules-mdc/blob/main/cursor-rules-reference.md),
   same doc text, used to confirm the vendored copy is not stale.

Note what the official page does **not** contain: no example combining `globs` with
`description`, and no statement about quoting the glob list. The two examples it gives are
`globs:` empty and `description` + `alwaysApply` only.

### The globs-quoting finding

**Provenance is weaker than the rest of this file, and worth stating plainly.** The claim
that quoting the list breaks matching — "Use only comma-separated values with no
surrounding quotes. Quoting turns it into a single string with a literal comma, and it may
be interpreted as one malformed pattern instead of two valid ones" — was returned by a web
search as a synthesized answer over a result set that included
[shiplight.ai](https://www.shiplight.ai/blog/cursor-rules),
[morphllm.com](https://www.morphllm.com/cursor-rules-best-practices) and
[techsy.io](https://techsy.io/en/blog/cursor-rules-guide). **All three are blocked by the
egress proxy**, so the sentence could not be traced to a section of a page that was
actually opened, and it is quoted here from the search summary. The same summary also
reported that "the undocumented `globs:` format works reliably" — i.e. this is community
knowledge, not vendor documentation.

What *is* verified locally: quoting collapses the list into the single string
`'**/*.java,**/pom.xml'` (PyYAML), and Cursor's own examples are unquoted. Whether Cursor
then splits that string on commas anyway is exactly the untested part. The unquoted form is
chosen because it is what the vendor's examples and UI produce, so it is the form least
likely to be mishandled — not because the failure mode has been reproduced.

Counter-evidence worth knowing: [stevekinney.net's course notes](https://github.com/stevekinney/stevekinney.net/blob/main/courses/ai-development/cursor-rules.md),
under *A Small Useful Rule*, use a quoted YAML array instead:

```yaml
globs:
  - 'src/**/*.ts'
```

So the community does not agree on one form. If a rule silently stops attaching, the glob
syntax is the first thing to suspect.

### Rule type when `globs` and `description` are both set

That `globs` + `description` + `alwaysApply: false` yields file-triggered attachment
(rather than agent-decided selection) also comes from a search summary over blocked
domains, and is *consistent with* — but not stated by — the official FAQ line at
`rules.md:301`. Treat the rule-type table above as reliable for each field in isolation and
as inference for the combination.
