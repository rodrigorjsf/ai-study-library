# Skills Over MCP Interest Group - Meeting Notes (Discussion #2248)

**Source:** https://github.com/modelcontextprotocol/modelcontextprotocol/discussions/2248
**Category:** Model Context Protocol (MCP)

## Summary

Minutes from the inaugural Skills Over MCP Interest Group meeting on February 13, 2025, attended by 13 participants from Anthropic, AWS, Databricks, Stacklok, Astronomer, and others. The meeting established the group's mandate, discussed the fundamental challenge of agents ignoring skills in favor of direct tool use, and introduced the core "skills-as-instructors" vs. "skills-as-helpers" distinction.

## Content

### Meeting Details

- **Date:** February 13, 2025
- **Format:** Online (Zoom)
- **Duration:** 1 hour

### Attendees

| Name | Organization |
|------|-------------|
| Justin Overholt | Anthropic |
| Dotan Nahum | Stacklok |
| Adam Bloom | Databricks |
| Jack Lindamood | Astronomer |
| Ben Schreiber | AWS |
| Alice Heiman | (Independent) |
| Farrukh Atabekov | (Independent) |
| Hana Mohan | Magic |
| Marcus Aurelius | (Independent) |
| Priya Rajan | Kensington AI |
| Marcus Hill | Vercel |
| Yuanli Zhang | (Independent) |
| Rosa Chen | (Independent) |

### 1. Background and Mandate

Justin Overholt opened the meeting by introducing the context for the group:

Anthropic's MCP 1.0 specification defines "Prompts" as a primitive—but the name is misleading, and the feature has been underexplored. In practice, MCP prompts are best understood as **Skills**: reusable, named, structured instructions for how an agent should perform specific tasks using one or more tools. The group exists because:

1. Real-world MCP deployments show agents mostly ignore skills and jump straight to tools
2. The skills primitive is semantically richer than it appears from the spec
3. Cross-vendor interoperability for skills has not been addressed

The group's mandate: define conventions, URI schemes, discovery mechanisms, lifecycle policies, and agent interaction patterns for skills over MCP.

### 2. Core Problem: Agents Ignore Skills

The group discussed early evidence from production deployments: when given both skill definitions and tools, most agents (LLMs) skip the skills and attempt to accomplish tasks by chaining raw tool calls. This produces suboptimal outcomes in three ways:

- **Correctness:** Agents make tool-use mistakes that skills were designed to prevent
- **Efficiency:** Agents take more steps than necessary
- **Predictability:** Results vary across runs and models

**Root causes identified:**
1. No instruction to check skills before tool use in most system prompts
2. Skills often appear as long text blobs with no structured metadata, making them "invisible" to attention mechanisms
3. System prompts may include skills but no mechanism for agents to "discover" which skills apply to a given task

### 3. Skills-as-Instructors vs. Skills-as-Helpers

The meeting's most substantive discussion centered on two mental models for how skills fit in agentic systems:

#### Skills-as-Instructors Model
- A skill is a **standing instruction** from the system or MCP server that agents should follow
- Skills define policies, guardrails, workflows, and standard operating procedures
- Agents are expected to check for relevant skills before using tools, and to follow skill instructions when applicable
- The skill is "in charge"—it defines the expected behavior; the agent is an executor of the skill's intent

#### Skills-as-Helpers Model
- A skill is a **reference document** the agent can consult, but is not required to follow
- Skills provide context, tips, patterns, and best practices
- The agent retains autonomy to decide when and how to use skills
- The skill is "advisory"—like an internal wiki or knowledge base

**Key tension:** The instructors model requires more system-prompt infrastructure and reliable agent compliance; the helpers model is easier to deploy but produces weaker guarantees.

**Working group consensus (tentative):** Both models are valid in different contexts. Skills over MCP should support both modes, likely via metadata flags on skill definitions (e.g., `"enforcement": "required"` vs. `"enforcement": "advisory"`).

### 4. Discovery and URI Schemes

Brief discussion on how agents and clients discover available skills:

- Current MCP spec: Skills (Prompts) are listed by the `prompts/list` RPC method—no dedicated URI scheme
- Community proposals for URI schemes like `skill://server-name/skill-id` are emerging but not standardized
- Early preference in group: use `index.json` discovery files at `/.well-known/agent-skills/` rather than mandatory `skill://` scheme

Formal decision deferred to later working group meeting (see Discussion #2460 for updates).

### 5. Cross-Vendor Interoperability

Participants flagged the risk of skills becoming a "vendor moat":
- If each LLM vendor (Anthropic, AWS, Google) interprets skill definitions differently, cross-vendor compatibility breaks
- Need: a shared JSON schema for skills that is vendor-neutral and model-agnostic
- The group agreed to draft an interoperability requirements document before defining a formal schema

### 6. Skill Versioning

Several participants noted that as servers evolve, skills will change—but clients may cache old skill definitions:
- Skills need version identifiers (semver preferred)
- Clients should know when cached skill content is stale
- Some discussion of ETag-style invalidation; no decision reached

### 7. Lazy Loading

Large skill libraries (100+ skills) present a challenge: listing all skills upfront is expensive in tokens and latency:
- Proposal: support lazy loading where agents request individual skills by ID rather than fetching all at once
- Key question: how does an agent know which skills to request if it doesn't know what exists?
- Proposed partial solution: a skill index (lightweight list of skill IDs + one-line descriptions) that agents can use for initial discovery

### 8. Security Considerations

Quick survey of security concerns raised:
- Skills from untrusted MCP servers could contain harmful instructions (prompt injection vectors)
- Need for sandboxing or trust levels: "trusted" vs. "untrusted" skill sources
- At minimum, user consent before executing a skill from an external server

### 9. Relation to MCP Prompts Primitive

Question raised: should "Skills over MCP" extend the existing `prompts` primitive or define a new primitive?

Working group leaning: extend the existing primitive via convention (metadata, naming, discovery), not a new MCP primitive—to maintain spec compatibility without requiring server updates.

### 10. Open Questions

- Should skill enforcement be opt-in or opt-out?
- What is the canonical format for a skill definition? (Markdown vs. JSON vs. structured template)
- How do skills interact with multi-agent setups where different sub-agents may have different skill sets?
- Who is responsible for skill composition when multiple MCP servers each contribute their own skills?

### Action Items

| Item | Owner | Due |
|------|-------|-----|
| Draft interoperability requirements doc | Justin Overholt | March 2025 |
| Survey MCP server implementations for skills usage | Ben Schreiber | March 2025 |
| Write up skills-as-instructors vs. skills-as-helpers distinction for community post | Dotan Nahum | March 2025 |
| Prototype lazy skill loading in reference server | Adam Bloom | March 2025 |
| Propose initial skill URI scheme options | Jack Lindamood | March 2025 |

### Next Meeting

The group agreed to meet monthly. Next meeting: **March 24, 2025** — see Discussion #2460 for notes.

### References

- [MCP Specification: Prompts Primitive](https://modelcontextprotocol.io/specification/2025-11-25/server/prompts)
- [Discussion #2460: Skills Over MCP – March 2025 Office Hours](https://github.com/modelcontextprotocol/modelcontextprotocol/discussions/2460)
- [MCP SDK: TypeScript](https://github.com/modelcontextprotocol/typescript-sdk)
