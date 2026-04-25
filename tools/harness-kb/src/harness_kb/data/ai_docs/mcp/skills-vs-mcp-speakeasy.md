# Skills vs MCP: Not Competing, Just Different Layers - Speakeasy

**Source:** https://www.speakeasy.com/blog/skills-vs-mcp
**Category:** Model Context Protocol (MCP)

## Summary

This Speakeasy article by Sagar Batchu argues that Skills and MCP are not competing technologies — they are different layers of an agentic architecture. Skills encode *how* to do things (static markdown instructions, institutional knowledge), while MCP encodes the *ability* to do things (live authenticated service access). The article recommends a two-layer architecture using both together for robust enterprise AI systems.

## Content

### Introduction

In the growing world of AI agents, two concepts have been creating some confusion: **Skills** and **MCP (Model Context Protocol)**. On the surface, they seem to overlap — both help AI agents do things. But they're actually solving different problems at different layers of your stack.

Skills and MCP are not competing technologies. Skills define *how* an agent does things. MCP defines the agent's *ability* to do things. Let's explore why you want both.

---

### What Are Skills?

Skills are static, reusable instructions that tell an agent how to perform specific tasks. They're essentially sophisticated system prompt components that encode:

- **Step-by-step workflows:** "To deploy a service, first check the current status with `kubectl get pods`, then..."
- **Best practices and patterns:** "When writing SQL queries for our data warehouse, always..."  
- **Error handling procedures:** "If the API returns a 429, implement exponential backoff starting at..."
- **Domain knowledge:** "Our authentication flow uses OAuth 2.0 with these specific parameters..."
- **Team conventions:** "Code reviews must include performance implications and security considerations..."

**Skills are fundamentally knowledge artifacts.** They don't execute code, make API calls, or access systems — they tell the agent how to use the tools it already has. Think of skills as your team's institutional knowledge, distilled into machine-readable form.

**Example skill:**
```markdown
# Deploy Service to Staging

## When to use this skill
Use this skill when deploying any microservice to the staging environment.

## Prerequisites
- kubectl access configured for staging cluster
- Docker image built and pushed to registry
- Environment variables updated in secrets manager

## Steps
1. Verify current deployment status: `kubectl get deployment {service-name} -n staging`
2. Update the image: `kubectl set image deployment/{service-name} {service-name}={image-tag} -n staging`
3. Watch rollout: `kubectl rollout status deployment/{service-name} -n staging`
4. Verify health: `curl https://staging.internal/{service-name}/health`

## Common Issues
- If rollout fails, check logs: `kubectl logs -l app={service-name} -n staging --tail=50`
- If health check fails, verify environment variables are updated in secrets manager
```

---

### What Is MCP?

MCP (Model Context Protocol) is a standardized protocol that gives agents *capability* — the ability to interact with external systems, APIs, and data sources. MCP is what allows agents to actually make things happen.

Through MCP, agents can:

- **Read and write data:** Query databases, read files, update records
- **Call APIs:** Make authenticated requests to external services
- **Execute actions:** Run commands, trigger workflows, deploy changes

**MCP is fundamentally about capability access.** It provides the authenticated, governed connections that let agents move from thinking to doing. Think of MCP as the secure, auditable access layer that connects your agents to your systems.

**Example MCP interaction:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "kubernetes_get_deployment",
    "arguments": {
      "name": "payment-service",
      "namespace": "staging"
    }
  }
}
```

---

### Why Both? The Two-Layer Architecture

Here's where it gets interesting. Skills and MCP are complementary — they work best together.

```
┌─────────────────────────────────────────────────────────────────┐
│                          AI AGENT                               │
│                                                                 │
│  ┌─────────────────────┐    ┌────────────────────────────────┐  │
│  │       SKILLS        │    │             MCP                │  │
│  │  (How to do things) │    │   (Ability to do things)       │  │
│  │                     │    │                                │  │
│  │ • Workflows         │    │ • Database connections         │  │
│  │ • Best practices    │    │ • API access                  │  │
│  │ • Domain knowledge  │    │ • File system access          │  │
│  │ • Team conventions  │    │ • External service calls      │  │
│  │ • Error handling    │    │ • Authenticated operations    │  │
│  └─────────────────────┘    └────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

**Skills tell the agent what steps to follow. MCP gives the agent the tools to execute those steps.**

Without skills, an agent with MCP access is like a brilliant intern with system access but no onboarding — they can do things, but they don't know your organization's way of doing them, your standards, or your procedures.

Without MCP, an agent with skills is like a highly knowledgeable consultant who can't access any of your systems — they have all the knowledge but none of the capabilities.

---

### Real-World Example: Customer Support Agent

Consider a customer support agent that needs to handle refund requests:

**The MCP Layer provides:**
- Access to the orders database
- Connection to the payment processing API
- Ability to update customer records
- Integration with the ticketing system

**The Skills Layer provides:**
- "Refund Request Handling" skill: check order age, verify payment method, calculate refund amount, apply retention offer for high-value customers, process refund, send confirmation email, update ticket

The agent uses the skill to know *how to handle* refund requests, and uses MCP to actually *execute* each step: query the database, check order details, call the payment API, update records.

---

### Decision Framework: Skills vs MCP

| Question | If Yes, Use... |
|----------|----------------|
| Does the agent need institutional knowledge? | Skills |
| Does the agent need access to live data? | MCP |
| Are you encoding team workflows? | Skills |
| Are you connecting to external APIs? | MCP |
| Do you need auditable access trails? | MCP |
| Are you encoding domain expertise? | Skills |
| Do you need authentication/authorization? | MCP |
| Are you building reusable procedures? | Skills |

**For most enterprise agents: use both.**

---

### Implementing the Two-Layer Architecture

**Step 1: Define your MCP servers** — what systems does your agent need access to?

```typescript
// MCP Server example (TypeScript SDK)
const server = new McpServer({ name: "company-tools", version: "1.0.0" });
server.tool("get_order", { orderId: z.string() }, async ({ orderId }) => {
  const order = await db.orders.findById(orderId);
  return { content: [{ type: "text", text: JSON.stringify(order) }] };
});
```

**Step 2: Write skills for your domain** — what does your agent need to know?

```markdown
# Refund Request Handling
When processing refund requests:
1. Use `get_order` to retrieve order details
2. If order is less than 30 days old, approve immediately
3. If customer has spent >$1000 lifetime, offer 10% store credit bonus
4. Use `process_refund` with the calculated amount
5. Use `send_email` to confirm with customer
```

**Step 3: Wire them together** — serve skills from your MCP server

```typescript
server.prompt("refund_handling", () => ({
  messages: [{
    role: "user",
    content: { type: "text", text: fs.readFileSync("./skills/refund-handling.md", "utf-8") }
  }]
}));
```

---

### Common Misconceptions

**"Skills are just system prompts"** — Skills are more structured and reusable. They can be versioned, shared across agents, and loaded conditionally based on context.

**"MCP replaces the need for skills"** — MCP gives capabilities; skills provide judgment about when and how to use those capabilities.

**"I should choose one or the other"** — They solve different problems. You almost always want both.

---

### Conclusion

Skills and MCP are distinct layers of modern agentic architecture:

- **Skills = Institutional knowledge, encoded** — the *how*
- **MCP = Authenticated capability access** — the *ability*

The most sophisticated enterprise agents leverage both: MCP for governed, auditable access to your systems and data; skills for the domain knowledge, workflows, and conventions that make the agent effective in your specific context.

Don't pick one. Build both layers, and build them well.

---

### Related Resources

- [MCP Official Documentation](https://modelcontextprotocol.io)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [Skills Over MCP Interest Group](https://github.com/modelcontextprotocol/modelcontextprotocol/discussions/2248)
- [Speakeasy MCP Guide](https://www.speakeasy.com/openapi/mcp)
