# Skills Over MCP Interest Group - Office Hours (Discussion #2460)

**Source:** https://github.com/modelcontextprotocol/modelcontextprotocol/discussions/2460
**Category:** Model Context Protocol (MCP)

## Summary

Notes from the March 24, 2025 Skills Over MCP Interest Group office hours session. Four agenda items were covered: skill URI schemes (index.json at `/.well-known/agent-skills/` adopted as primary approach), script execution and dependency management, lazy loading strategies, and the file system dependency problem for skills over remote MCP servers.

## Content

### Meeting Details

- **Date:** March 24, 2025
- **Format:** Online office hours (open to community)
- **Related discussion:** [#2248 – Inaugural meeting notes](https://github.com/modelcontextprotocol/modelcontextprotocol/discussions/2248)

### Agenda

1. URI Schemes for skill discovery
2. Script execution and dependency management for skills
3. Lazy loading of skills
4. File system dependency problem

---

### 1. URI Schemes for Skill Discovery

**Context:** The group needed to decide on a canonical way for agents to discover and reference skills provided by MCP servers.

**Options considered:**

| Approach | Description | Pros | Cons |
|----------|-------------|------|------|
| `skill://server/skill-id` | Custom URI scheme | Clean, explicit, purposeful | Requires custom resolution logic; spec change needed |
| `/.well-known/agent-skills/index.json` | HTTP convention | Standard HTTP pattern; works with any HTTP client | Only applies to HTTP-based servers, not STDIO |
| `prompts/list` extension | Extend existing MCP RPC | No spec change; backward compatible | Metadata-poor; no canonical URL |
| Embedded in server manifest | Skills listed in server's capability block | Discoverable at connection time | Server restart required to add skills; heavy payload |

**Decision: `/.well-known/agent-skills/index.json` adopted as primary approach**

Rationale:
- Follows established HTTP well-known conventions (RFC 8615)
- Does not require changes to MCP core spec
- Lightweight index: each entry has `id`, `name`, `description`, `version`, and optional `href` pointing to the full skill document
- Full skill documents can be fetched on demand (supports lazy loading)
- Works well with existing HTTP tooling (curl, browsers, CDNs)

The mandatory `skill://` custom scheme was rejected as the primary approach because it requires all clients to implement custom resolution logic, raising the barrier to adoption.

**Decision for STDIO servers:** STDIO-based MCP servers (local tool use) will expose skills via the `prompts/list` RPC method, with a convention that a skill entry may include `"uri"` metadata pointing to a local file path or relative resource path.

---

### 2. Script Execution and Dependency Management

**Context:** Some skills are not just instructional text—they define executable scripts or workflows that reference external libraries, tools, or commands. How should these dependencies be managed?

**Discussion:**

Several participants (from AWS and Databricks) shared experience with "skill scripts" in enterprise settings:
- Some skills must run specific shell commands or Python scripts as part of execution
- These scripts have version-pinned dependencies
- Current practice: bundle dependencies in skill definition as structured metadata; rely on agent to resolve

**Working group consensus:**

1. **Pure text skills:** Skills whose entire content is markdown/text instructions for the agent. No execution dependency. Most common case; should remain the default.
2. **Script-bearing skills:** Skills with embedded code (bash, Python, etc.) must declare a `"requires"` block in their metadata:
   - `language`: e.g., `"bash"`, `"python3"`, `"node"`
   - `packages`: list of required packages/libraries
   - `min_version`: minimum required runtime version
3. **Trust model:** Agents should NOT execute script-bearing skills from untrusted servers without explicit user confirmation.
4. **Sandboxing:** Skills with embedded scripts should run in sandboxed environments (containers, virtual envs); the agent is responsible for enforcing this.

**Open question:** Who manages the environment setup? Options: the MCP client, the agent framework, or the skill itself. No decision reached.

---

### 3. Lazy Loading of Skills

**Context:** Large MCP server deployments may surface 100+ skills. Loading all skills at connection time is expensive—latency, token usage, and context window pressure.

**Proposed lazy loading pattern:**

```
Client connects to MCP server
       |
       V
Fetch index.json from /.well-known/agent-skills/
  → Returns lightweight skill index (id + name + one-line description)
       |
       V
Agent reads task / user intent
       |
       V
Agent searches index to identify relevant skills
       |
       V
Agent fetches full skill documents for top candidates (on demand)
       |
       V
Agent follows skill instructions when executing task
```

**Key design decisions:**

- **Index format:** Array of objects: `[{id, name, description, version, href?}]`
  - `href`: Optional URL to full skill document; if absent, client must use `prompts/get` RPC with `id`
- **Index TTL:** Index should include a `"ttl"` field (seconds) for client-side caching; default suggested: 300 seconds (5 min)
- **Full skill caching:** Full skill documents should include ETag headers (HTTP) or version identifiers (MCP RPC) to enable safe caching
- **Search mechanism:** Initially, keyword/substring matching on skill name and description; vector-search-based skill discovery is out of scope for v1

**Current limitations acknowledged:**
- Simple keyword search may miss semantically relevant skills; embeddings/semantic search would help but are complex to standardize
- The agent still needs "instructions to look for skills" in the system prompt; lazy loading does not automatically solve the agent-ignores-skills problem

---

### 4. File System Dependency Problem

**Context:** Many skills reference files on a local file system (e.g., "load the context from this project's `CLAUDE.md`" or "read the schema from `./schemas/user.json`"). When skills are served from a remote MCP server, these file-system-relative paths break.

**Discussion:**

Jack Lindamood described three failure modes observed in production:
1. **Absolute paths:** Skills hardcode absolute paths like `/Users/jack/project/README.md`—these fail for every other user
2. **Relative paths:** Skills reference `./docs/conventions.md`—relative to what? The server? The client? The agent's working directory?
3. **No-file fallback:** Skills designed for local context assume files exist; when run remotely (e.g., via a cloud MCP server), they silently degrade

**Proposed solutions:**

1. **Skill scope declaration:** Each skill declares whether it is `"local-only"`, `"remote-safe"`, or `"conditional"` (works remotely if certain resources are available)
   - Clients can filter skills by scope; remote agents skip `"local-only"` skills
2. **Resource URIs instead of paths:** Skills should reference files using MCP Resource URIs (e.g., `mcp://server-name/resources/schema.json`) instead of file system paths
   - MCP servers can expose files as resources, making them accessible remotely
3. **Required resources block:** Skills that need external files declare a `"required_resources"` block listing all needed resource URIs; clients verify availability before presenting the skill to the agent

**Decision:** Adopt approach #2 (Resource URIs) as the long-term target; approach #1 (scope declaration) as a short-term pragmatic workaround.

A follow-up proposal: define a `"resources"` key in the skill index entry, listing the resource URIs that a skill depends on, so clients can pre-check availability at discovery time.

---

### Action Items

| Item | Owner | Due |
|------|-------|-----|
| Write RFC for `/.well-known/agent-skills/index.json` format | Justin Overholt | April 2025 |
| Draft trust model for script-bearing skills | Ben Schreiber | April 2025 |
| Prototype lazy loading in TypeScript reference client | Marcus Hill | April 2025 |
| Write up skill scope declaration proposal | Jack Lindamood | April 2025 |
| Add Resource URIs guidance to MCP Skills docs | Adam Bloom | May 2025 |

---

### Open Questions Carried Forward

- Should skill index search be standardized (query language, filters)?
- How to handle skill conflicts when two MCP servers provide skills with the same name?
- Are skills "owned" by a server, or can they be user-level (stored in client)?
- How does skill enforcement (required vs. advisory) interact with multi-agent setups?

---

### References

- [Discussion #2248 – Inaugural meeting notes](https://github.com/modelcontextprotocol/modelcontextprotocol/discussions/2248)
- [RFC 8615 – Well-Known URIs](https://www.rfc-editor.org/rfc/rfc8615)
- [MCP Resources Primitive](https://modelcontextprotocol.io/specification/2025-11-25/server/resources)
- [MCP Prompts Primitive](https://modelcontextprotocol.io/specification/2025-11-25/server/prompts)
