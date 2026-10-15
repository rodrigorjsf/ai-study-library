# A2A Protocol - Hugging Face Community

> **Currency check (2026-10-11):** Partially outdated
>
> - **Fidelity warning — the body below is not a capture of the source page.** The Hugging Face organization page still resolves (opened 2026-10-11; page title "a2aprotocol (zhangcheng)") but carries only a short profile; of 25 sentences sampled from the body below, 1 appears on it. The body says of itself that it is "synthesized from the organization's public profile and related web" material. The account is a community one, not an official A2A project property: https://huggingface.co/a2aprotocol
> - "As of mid-2025" is two major steps behind. A2A v1.0.0 was released 2026-03-12 and v1.0.1 on 2026-05-26/28; v1.0 has many breaking changes from v0.3: https://github.com/a2aproject/A2A/blob/main/CHANGELOG.md and https://github.com/a2aproject/A2A/releases
> - Agent Card discovery is `/.well-known/agent-card.json`, not `/.well-known/agent.json` (already true in v0.3.0): https://github.com/a2aproject/A2A/blob/main/docs/whats-new-v1.md
> - A2A is a Linux Foundation project ("contributed by Google") governed by an eight-seat Technical Steering Committee — Google, Microsoft, Cisco, AWS, Salesforce, ServiceNow, SAP, IBM — not simply "Google, broad ecosystem": https://github.com/a2aproject/A2A/blob/main/GOVERNANCE.md
> - The MCP column is stale too: MCP is no longer "stateless(ish)" by accident but stateless by design since revision 2026-07-28 (no `initialize`, no sessions; `server/discover` replaces capability negotiation at connect time): https://modelcontextprotocol.io/specification/2026-07-28/changelog

**Source:** https://huggingface.co/a2aprotocol
**Category:** Model Context Protocol (MCP)

## Summary

The A2A Protocol Hugging Face organization hosts resources related to Google's Agent-to-Agent (A2A) protocol, a complementary standard to MCP designed for agent-to-agent coordination rather than agent-to-tool integration. The organization publishes LLM paper collections and maintains the A2A Practical Guide space. A2A and MCP form complementary layers: MCP for tool access, A2A for multi-agent orchestration.

## Content

### Overview

The `a2aprotocol` organization on Hugging Face (`huggingface.co/a2aprotocol`) is dedicated to the **Agent-to-Agent (A2A) Protocol** — a standard introduced by Google in early 2025 for enabling autonomous software agents to communicate, coordinate, and collaborate regardless of vendor or framework.

> **Note:** The Hugging Face Spaces within this organization require authentication to access. The following content is synthesized from the organization's public profile and related web resources.

---

### What is A2A?

**A2A (Agent-to-Agent Protocol)** was introduced by Google in early 2025 as an open standard for multi-agent systems. Where MCP standardizes how agents access tools and resources, A2A standardizes how agents communicate with each other.

**Key A2A concepts:**

- **Agent Cards:** JSON descriptors that advertise an agent's capabilities, authentication requirements, and supported modalities (text, audio, video, structured data)
- **Tasks:** The unit of work in A2A — agents delegate tasks to one another; tasks can be synchronous or long-running/asynchronous
- **Artifacts:** The outputs of completed tasks — agents can pass artifacts to downstream agents in a workflow
- **Push Notifications:** A2A supports real-time updates for long-running tasks via webhooks or SSE

---

### A2A Protocol Hugging Face Content

The organization's Hugging Face profile includes:

#### Model/Paper Collections

Collections of papers related to:
- Multi-agent systems and frameworks
- Agent communication protocols
- LLM orchestration architectures
- Cooperative and competitive agent behaviors

#### A2A Practical Guide Space

A Hugging Face Space (requires auth) providing:
- Hands-on examples of A2A in action
- Code samples for building A2A-compatible agents
- Integration patterns with popular agent frameworks (LangChain, AutoGen, CrewAI)

---

### A2A vs. MCP: The Key Distinction

| Dimension | A2A | MCP |
|-----------|-----|-----|
| Full Name | Agent-to-Agent Protocol | Model Context Protocol |
| Origin | Google (early 2025) | Anthropic (November 2024) |
| Primary Purpose | Agent-to-agent coordination | Agent-to-tool/resource integration |
| Communication Model | Peer-to-peer between agents | Client (agent) to server (tool) |
| State | Stateful tasks with lifecycle | Stateless(ish) tool invocations |
| Discovery | Agent Cards at `/.well-known/agent.json` | MCP Registry / capability negotiation |
| Authentication | Per-agent auth, supports enterprise SSO | OAuth 2.1, CIMD, XAA |
| Modalities | Text, audio, video, structured data | Text, binary resources |
| Industry Support | Google, broad ecosystem | Anthropic, 170+ AAIF members |

---

### Combined Architecture: A2A + MCP

The two protocols are designed to be complementary, not competitive:

```
┌─────────────────────────────────────────────────────────────────────┐
│                      ENTERPRISE AI PLATFORM                         │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    A2A ORCHESTRATION LAYER                  │    │
│  │                                                             │    │
│  │   Orchestrator Agent                                        │    │
│  │        │ (A2A delegation)                                   │    │
│  │   ┌────┴────────────────────────┐                          │    │
│  │   │                             │                          │    │
│  │   V                             V                          │    │
│  │ Research Agent              Writer Agent                   │    │
│  │ (A2A peer)                  (A2A peer)                     │    │
│  └───────┬─────────────────────────┬───────────────────────── ┘    │
│          │ MCP tool access         │ MCP tool access                │
│  ┌───────▼─────────────────────────▼───────────────────────────┐    │
│  │                    MCP TOOL ACCESS LAYER                    │    │
│  │                                                             │    │
│  │  Web Search   │  Database  │  File System  │  APIs          │    │
│  │  MCP Server   │  MCP Server│  MCP Server   │  MCP Server   │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

- **A2A handles:** Which agent does what, task delegation, parallel execution, state handoff between agents
- **MCP handles:** How each agent accesses the tools and data sources it needs

---

### A2A in Practice

**Use cases where A2A shines:**

1. **Research pipelines:** A coordinator agent (A2A) delegates to a web research specialist (A2A), a code execution specialist (A2A), and a summarizer (A2A) — each using MCP for their specific tool access

2. **Customer service orchestration:** A triage agent (A2A) routes tickets to billing specialist, technical specialist, or escalation agent based on intent — each running independently with their own tool access

3. **Data pipeline automation:** Planning agent spawns data extraction agents in parallel (A2A), collects artifacts, then delegates to transformation and reporting agents

**Companies exploring A2A:**
- Google (creator and primary advocate)
- Salesforce (AgentForce integration)
- SAP (Business AI)
- ServiceNow (Now Assist)
- Workday

---

### Relation to the MCP Ecosystem

As of mid-2025:
- A2A and MCP are on parallel tracks — separate governance bodies, separate specs
- Anthropic's MCP focuses on single-agent-to-tools; not positioned to address multi-agent coordination
- Google's A2A fills that gap
- No official bridge protocol exists yet, but community implementations use both

**Industry consensus:** For sophisticated enterprise AI systems, the answer is A2A + MCP, not A2A vs. MCP.

---

### Resources

- [A2A Protocol GitHub](https://github.com/google-a2a/a2a-protocol)
- [A2A Protocol Specification](https://google-a2a.github.io/a2a-spec/)
- [Google Blog: Introducing A2A](https://developers.google.com/workspace/blog/a2a-protocol)
- [Hugging Face: a2aprotocol organization](https://huggingface.co/a2aprotocol)
- [MCP Official Site](https://modelcontextprotocol.io)
- [DZone: MCP vs A2A comparison](https://dzone.com/articles/a2a-mcp-agent-ai-communication-evolution)
