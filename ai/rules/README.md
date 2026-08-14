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

- **Do not quote the glob list.** `globs: "**/*.java,**/pom.xml"` is read as one literal
  pattern containing a comma and matches nothing. Comma-separated and unquoted is correct.
- That means the frontmatter is **not strict YAML** — a bare `*` is an alias indicator, so
  a standard YAML parser rejects `globs: **/*.java`. Cursor parses it with its own reader
  and its UI writes it exactly this way; do not "fix" it to a YAML list.
- Braces are not relied on: `**/build.gradle{,.kts}` is written out as two patterns.
- The extension must be `.mdc`. A plain `.md` in `.cursor/rules/` is still a valid rule but
  carries no activation metadata.
- Cursor's guidance is to keep a rule under 500 lines and split anything larger into
  composable rules; this one is ~110.
