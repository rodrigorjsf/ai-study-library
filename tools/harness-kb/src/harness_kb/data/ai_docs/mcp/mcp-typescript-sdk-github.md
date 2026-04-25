# MCP TypeScript SDK - Official GitHub Repository

**Source:** https://github.com/modelcontextprotocol/typescript-sdk
**Category:** Model Context Protocol (MCP)

## Summary

The official TypeScript SDK for Model Context Protocol (MCP), maintained by Anthropic. The main branch now tracks a V2 pre-alpha with breaking changes; v1.x is still recommended for production use. The SDK provides `@modelcontextprotocol/sdk` package with built-in support for server and client implementations, multiple transports (STDIO, HTTP), and middleware for Node.js, Express, and Hono.

## Content

### Overview

The TypeScript SDK implements the full [Model Context Protocol specification](https://spec.modelcontextprotocol.io), providing:

- Client and server implementations
- Protocol types and validation (with Zod)
- Transport implementations: STDIO and Streamable HTTP
- Middleware integrations for popular Node.js frameworks
- Full TypeScript type safety

---

### Version Status

> ⚠️ **The `main` branch of this repository now tracks the pre-alpha V2 SDK which has breaking changes from V1.** For the stable V1 SDK, see the [`v1` branch](https://github.com/modelcontextprotocol/typescript-sdk/tree/v1). The npm package currently still ships v1. V2 pre-alpha is available as `@modelcontextprotocol/sdk@next`.

---

### Packages

| Package | Description | npm |
|---------|-------------|-----|
| `@modelcontextprotocol/sdk` | Core MCP SDK (client + server) | `npm install @modelcontextprotocol/sdk` |

---

### Installation

```bash
npm install @modelcontextprotocol/sdk
```

---

### Quick Start: Server

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({
  name: "Demo",
  version: "1.0.0",
});

// Add a tool
server.tool("add", { a: z.number(), b: z.number() }, async ({ a, b }) => ({
  content: [{ type: "text", text: String(a + b) }],
}));

// Start with stdio transport
const transport = new StdioServerTransport();
await server.connect(transport);
```

---

### Quick Start: Client

```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const client = new Client({ name: "example-client", version: "1.0.0" });

const transport = new StdioClientTransport({
  command: "node",
  args: ["server.js"],
});

await client.connect(transport);

// List available tools
const tools = await client.listTools();
console.log(tools);

// Call a tool
const result = await client.callTool({ name: "add", arguments: { a: 1, b: 2 } });
console.log(result);

await client.close();
```

---

### Server Features

#### Tools

```typescript
// Simple tool
server.tool("get-weather", { city: z.string() }, async ({ city }) => {
  const weather = await fetchWeather(city);
  return { content: [{ type: "text", text: `Weather in ${city}: ${weather}` }] };
});
```

#### Resources

```typescript
// Static resource
server.resource("config", "config://app", async (uri) => ({
  contents: [{ uri: uri.href, text: "App configuration here" }],
}));

// Dynamic resource with template
server.resource(
  "user-profile",
  new ResourceTemplate("users://{userId}/profile", { list: undefined }),
  async (uri, { userId }) => ({
    contents: [{ uri: uri.href, text: `Profile for user ${userId}` }],
  })
);
```

#### Prompts (Skills)

```typescript
server.prompt("review-code", { code: z.string() }, ({ code }) => ({
  messages: [
    {
      role: "user",
      content: { type: "text", text: `Please review this code:\n\n${code}` },
    },
  ],
}));
```

---

### Transport Options

#### STDIO Transport (local)

```typescript
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
const transport = new StdioServerTransport();
await server.connect(transport);
```

#### Streamable HTTP Transport (remote)

```typescript
import express from "express";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";

const app = express();
app.use(express.json());

app.post("/mcp", async (req, res) => {
  const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });
  await server.connect(transport);
  await transport.handleRequest(req, res, req.body);
  res.on("finish", () => server.close());
});

app.listen(3000);
```

---

### Middleware Integrations

The SDK provides ready-made middleware for popular frameworks:

#### Express Middleware

```typescript
import { createExpressMcpMiddleware } from "@modelcontextprotocol/sdk/middleware/express.js";

const app = express();
app.use(express.json());
app.use("/mcp", createExpressMcpMiddleware(server));
app.listen(3000);
```

#### Hono Middleware

```typescript
import { Hono } from "hono";
import { createHonoMcpMiddleware } from "@modelcontextprotocol/sdk/middleware/hono.js";

const app = new Hono();
app.use("/mcp/*", createHonoMcpMiddleware(server));
export default app;
```

---

### Authentication Support

The SDK includes OAuth 2.1-compliant authentication helpers:

```typescript
import { OAuthServerProvider } from "@modelcontextprotocol/sdk/server/auth.js";

// Implement OAuth provider for your auth system
class MyAuthProvider implements OAuthServerProvider {
  async authorize(req: OAuthRequest): Promise<OAuthResponse> {
    // Your auth logic
  }
}
```

---

### Error Handling

```typescript
import { McpError, ErrorCode } from "@modelcontextprotocol/sdk/types.js";

server.tool("my-tool", { id: z.string() }, async ({ id }) => {
  const result = await fetchById(id);
  if (!result) {
    throw new McpError(ErrorCode.InvalidRequest, `Item not found: ${id}`);
  }
  return { content: [{ type: "text", text: JSON.stringify(result) }] };
});
```

---

### Sampling / Elicitation

```typescript
// Client-side: request LLM completion from the host
const result = await server.requestSampling({
  messages: [{ role: "user", content: { type: "text", text: "What is 2+2?" } }],
  maxTokens: 100,
});
```

---

### Testing

The SDK includes utilities for testing MCP servers and clients without needing actual transport:

```typescript
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";

const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
await server.connect(serverTransport);
await client.connect(clientTransport);
// Now test client↔server interaction in memory
```

---

### V2 Changes (Pre-Alpha)

The V2 pre-alpha introduces:
- Simplified API surface for the most common patterns
- Improved TypeScript types
- Streamlined transport registration
- Built-in middleware for Express/Hono/Node.js (see above)
- Breaking changes from V1 — migration guide in progress

To install V2 pre-alpha:
```bash
npm install @modelcontextprotocol/sdk@next
```

---

### Resources

- [MCP Specification](https://spec.modelcontextprotocol.io)
- [MCP Documentation](https://modelcontextprotocol.io)
- [Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Inspector (debugging tool)](https://github.com/modelcontextprotocol/inspector)
- [Reference Servers](https://github.com/modelcontextprotocol/servers)
