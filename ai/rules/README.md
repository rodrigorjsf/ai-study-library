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
rule type from the frontmatter fields, and this one is deliberately **Apply Intelligently**:

```yaml
---
description: <what the rule covers and when it is relevant>
alwaysApply: false
---
```

| Rule type | Frontmatter |
| --- | --- |
| Always Apply | `alwaysApply: true` |
| **Apply Intelligently** | **`description` set, `alwaysApply: false`, no `globs`** |
| Apply to Specific Files | `globs` set |
| Apply Manually | none of the three — invoked with `@java-concurrency-static` |

Intelligent activation was chosen over globs on purpose: the rule is about a *decision*
(should this be `static` at all?), not about a file type. Under `globs: **/*.java` it would
be injected into every trivial Java edit and burn context on a getter rename; under a
description the agent pulls it in when the work actually touches shared state, monitors,
virtual threads, or client lifecycle. The cost is that the description carries the whole
activation burden — it names the concrete triggers (`static`, `synchronized`,
`ThreadLocal`, virtual threads, DynamoDB/Redis/Kafka/HTTP clients, OTEL) rather than
describing the document, so keep it specific if you edit it.

The `.mdc` extension is what enables frontmatter — a plain `.md` file in `.cursor/rules/`
is a valid rule but has no activation metadata. Cursor's own guidance is to keep rules
under 500 lines and split anything larger into composable rules; this one is ~110.
