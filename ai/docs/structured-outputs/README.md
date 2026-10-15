# Structured Outputs (Anthropic) — Research Index

> **Index refreshed 2026-10-11** (previous capture ~2026-05-01). All four documents were re-fetched from `https://platform.claude.com/docs/en/...` (raw markdown, `.md` suffix) and replaced with verbatim mirrors. The earlier files were condensed summaries; the new ones are the full pages, including every language tab.

**Category:** Structured Outputs — Anthropic Claude API
**Sources:** platform.claude.com (the `docs.anthropic.com` URLs named by the earlier capture redirect there)

This directory contains research documents about Anthropic Claude's Structured Outputs feature — the mechanism that constrains Claude's responses to follow a specific JSON schema via grammar-based (constrained) decoding, enabling reliable, type-safe AI integration.

---

## Documents

| File | Mirrored page | Description |
|------|---------------|-------------|
| [anthropic-structured-outputs.md](./anthropic-structured-outputs.md) | [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) | **Primary reference.** JSON outputs (`output_config.format`), SDK helpers, raw JSON schema usage, common use cases, grammar caching, JSON Schema limitations, schema complexity limits, migrating from the beta, data retention, feature compatibility. The page frontmatter (kept at the top of the file) carries the supported-model and platform lists. |
| [anthropic-strict-tool-use.md](./anthropic-strict-tool-use.md) | [Strict tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use) | `strict: true` on tool definitions — grammar-constrained sampling that guarantees tool inputs match the JSON Schema. Why it matters for agents, quick start, how it works, common use cases, data retention. |
| [anthropic-implement-tool-use.md](./anthropic-implement-tool-use.md) | [Define tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools) | **Page renamed.** The former "Implement tool use" URL now redirects to "Define tools"; the file name is historical. Covers tool definition parameters, the tool use system prompt, best practices for tool definitions, `input_examples`, and controlling output with `tool_choice`. |
| [anthropic-increase-consistency.md](./anthropic-increase-consistency.md) | [Increase output consistency](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/increase-consistency) | Prompt-engineering techniques for consistency — format specification, prefill, examples, retrieval, prompt chaining, staying in character — and the pointer to Structured Outputs when schema conformance must be guaranteed. |

---

## What changed since the previous capture

| Topic | Previous capture (~2026-05-01) | Mirrored page (2026-10-11) |
|-------|-------------------------------|----------------------------|
| Supported models | Mythos Preview, Opus 4.7/4.6, Sonnet 4.6/4.5, Opus 4.5, Haiku 4.5 | Adds Fable 5.1, Mythos 5.1, Fable 5, Mythos 5, Opus 5.5, Opus 5, Opus 4.8, Sonnet 5.5, Sonnet 5, Haiku 5.5 (the older ones remain listed) |
| Microsoft Foundry | "In beta" | Generally available |
| Google Cloud | "Not supported on Vertex AI for Mythos Preview" | Listed as generally available, with no such exception in the frontmatter |
| Amazon Bedrock | GA for the 4.5/4.6 family; Opus 4.7 and Mythos Preview through the Messages-API Bedrock endpoint | GA only on the *legacy* Amazon Bedrock integration (Opus 4.6 and earlier models); **not** available on "Claude in Amazon Bedrock" |
| Old `output_format` request parameter | "Will continue working for a transition period" | Deprecated. It only works with the `structured-outputs-2025-11-13` beta header; without the header the API returns a 400 error |
| Python SDK | — | v1.0 and later raise `TypeError` for `output_format={...}` on `client.beta.messages.create()` / `count_tokens()`; use `output_config`. (`client.messages.parse(output_format=MyModel)` is still the recommended helper.) |
| Tool `name` limit ("Define tools") | `^[a-zA-Z0-9_-]{1,64}$` | `^[a-zA-Z0-9_-]{1,128}$` |
| "Choosing a model" section | Present in "Implement tool use" | Not present on the "Define tools" page |
| Computer use / browser use toolsets | Not mentioned | `computer_toolset_20260801` and `browser_toolset_20260801` do not accept `strict: true` or `input_examples` |
| Prefill ("Increase output consistency") | "Not supported on Claude Mythos Preview, Claude Opus 4.7, Claude Opus 4.6, and Claude Sonnet 4.6" | Generalized: "Prefilling is not supported on Claude 4.6 and later models and Claude Mythos Preview" — use structured outputs or system prompt instructions instead |

Unchanged: the three explicit complexity limits, the 180-second compilation timeout, the 24-hour grammar cache, and the compatibility list below.

---

## Key Concepts

### Two Complementary Features

| Feature | Parameter | What it controls |
|---------|-----------|-----------------|
| **JSON outputs** | `output_config.format` | Claude's **response format** (what Claude says) |
| **Strict tool use** | `strict: true` on tool definition | Claude's **tool inputs** (how Claude calls your functions) |

Both use grammar-constrained decoding and can be combined in the same request.

### How It Works

Structured outputs compile your JSON schemas into a grammar that constrains which tokens Claude can generate. This means schema violations are prevented at the token generation level — not just discouraged by prompting. (Refusals and `max_tokens` cut-offs can still produce output that does not match the schema; see "Invalid outputs" in the primary reference.)

### Supported Models and Platforms

Taken from the page frontmatter on 2026-10-11. Status: **generally available**; zero data retention eligible.

| Family | Model IDs |
|--------|-----------|
| Fable / Mythos | `claude-fable-5-1`, `claude-mythos-5-1`, `claude-fable-5`, `claude-mythos-5`, `claude-mythos-preview` |
| Opus | `claude-opus-5-5`, `claude-opus-5`, `claude-opus-4-8`, `claude-opus-4-7`, `claude-opus-4-6`, `claude-opus-4-5-20251101` |
| Sonnet | `claude-sonnet-5-5`, `claude-sonnet-5`, `claude-sonnet-4-6`, `claude-sonnet-4-5-20250929` |
| Haiku | `claude-haiku-5-5`, `claude-haiku-4-5-20251001` |

| Platform | Availability |
|----------|--------------|
| Claude API | GA |
| Claude Platform on AWS | GA |
| Amazon Bedrock | GA on the legacy integration only (Opus 4.6, Sonnet 4.6, Sonnet 4.5, Opus 4.5, Haiku 4.5) |
| Google Cloud | GA |
| Microsoft Foundry | GA |

### Schema Complexity Limits (per request)

| Limit | Value |
|-------|-------|
| Strict tools per request | 20 |
| Total optional parameters | 24 |
| Parameters with union types (`anyOf` or type arrays) | 16 |

Beyond these, internal grammar-size limits can return a 400 "Schema is too complex for compilation", and compilation times out at 180 seconds.

### Performance Characteristics

- **First request**: Additional latency for grammar compilation
- **Subsequent requests**: Compiled grammars cached for **24 hours** from last use
- Cache is invalidated by schema structure changes, or by changing the set of tools in the request (not by `name`/`description`-only changes)

---

## Quick Reference

The snippets below are shortened from the mirrored pages; the full, runnable versions (cURL, CLI, Python, TypeScript, and other SDKs) are in [anthropic-structured-outputs.md](./anthropic-structured-outputs.md) and [anthropic-strict-tool-use.md](./anthropic-strict-tool-use.md).

### JSON Outputs (Python / Pydantic)

```python
from anthropic import Anthropic
from pydantic import BaseModel

class ContactInfo(BaseModel):
    name: str
    email: str

client = Anthropic()
response = client.messages.parse(
    model="claude-opus-5-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Extract: Alice Smith, alice@example.com"}],
    output_format=ContactInfo,  # the SDK sends this as output_config.format
)
print(response.parsed_output)  # typed as ContactInfo
```

### JSON Outputs (TypeScript / Zod)

```typescript
import Anthropic from "@anthropic-ai/sdk";
import { z } from "zod";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";

const ContactInfoSchema = z.object({
  name: z.string(),
  email: z.string(),
});

const client = new Anthropic();
const response = await client.messages.parse({
  model: "claude-opus-5-5",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Extract: Alice Smith, alice@example.com" }],
  output_config: { format: zodOutputFormat(ContactInfoSchema) },
});
```

### Raw JSON Schema via output_config

The schema sits directly under `format.schema`. (The earlier version of this index nested it under a `json_schema` object with a `name`; that shape is not what the mirrored page documents.)

```python
response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "..."}],
    output_config={
        "format": {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                },
                "required": ["name", "email"],
                "additionalProperties": False,
            },
        }
    },
)
result_json = response.content[0].text  # valid JSON string
```

### Strict Tool Use

```python
tools = [{
    "name": "save_contact",
    "description": "Save a contact record.",
    "strict": True,                    # enables grammar-constrained sampling
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "email": {"type": "string"},
        },
        "required": ["name", "email"],
        "additionalProperties": False,
    },
}]
```

---

## Feature Compatibility

| Feature | Compatible |
|---------|-----------|
| Batch processing | ✅ (50% discount) |
| Token counting | ✅ |
| Streaming | ✅ |
| Strict tool use + JSON outputs together | ✅ |
| Citations | ❌ (returns 400 with `output_config.format`) |
| Message prefilling | ❌ (incompatible with JSON outputs) |
| Thinking (grammar scope) | ⚠️ Grammars apply to Claude's direct output only, not to tool use calls, tool results, or thinking |
| Programmatic tool calling | ❌ for `strict: true` tools (see [`../tool-calling/programmatic-tool-calling-claude-api.md`](../tool-calling/programmatic-tool-calling-claude-api.md)) |
