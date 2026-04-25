# HTTP/2 and HTTP/3 Support in the Future - MCP Transport Evolution

**Source:** https://www.reddit.com/r/mcp/comments/1jqbkhd/http2http3_support_in_the_future/ (Reddit - requires verification)
**Additional Source:** https://blog.modelcontextprotocol.io/posts/2025-12-19-mcp-transport-future/ (Official MCP Blog)
**Category:** Model Context Protocol (MCP)

## Summary

This covers community discussion and the official MCP Transport Working Group's roadmap regarding HTTP/2 and HTTP/3 support for the Model Context Protocol. The official MCP blog post from December 2025 outlines a detailed roadmap for evolving MCP transports toward a stateless architecture, with significant implications for serverless deployments on AWS Lambda, Cloudflare Workers, and similar platforms.

## Content

### Background: MCP Transport History

When MCP first launched in November 2024, quite a few of its users relied on local environments, connecting clients to servers over [STDIO](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports#stdio). As MCP became the go-to standard for LLM integrations, community needs evolved, leading to the build-out of infrastructure around remote servers.

The [Streamable HTTP](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports#streamable-http) transport was a significant step forward, enabling remote MCP deployments and unlocking new use cases. However, as enterprise deployments scale to millions of daily requests, early adopters have encountered practical challenges.

### Current Challenges with MCP Transports

- **Infrastructure Complexity:** Load balancers and API gateways must parse full JSON-RPC payloads to route traffic, rather than using standard HTTP patterns.
- **Scaling Friction:** Stateful connections force "sticky" routing that pins traffic to specific servers, preventing effective auto-scaling.
- **High Barrier for Simple Tools:** Developers building simple, ephemeral tools are often required to manage complex backend storage to support basic multi-turn interactions.
- **Ambiguous Session Scope:** There is no predictable mechanism for defining where a conversation context starts and ends across distributed systems.

### HTTP/2 and HTTP/3 Status

**Current State (2025):**
- MCP's Streamable HTTP transport operates over standard HTTP/1.1 and HTTP/2
- Full MCP streaming (Streamable HTTP) effectively requires HTTP/2 or higher for correct, robust full-duplex operation
- HTTP/1.1 works, but you only get synchronous (simple) request/response—no "true streaming" or mid-request notifications
- HTTP/3 support is being actively explored but not yet part of the official specification
- No mainstream MCP servers or clients in 2025 rely on HTTP/3 yet, but several vendors are experimenting with it

**Community Feedback:**
- Many developers hit problems trying to use MCP streaming on platforms that only support HTTP/1.1
- Developers call for docs/specs to make "HTTP/2+ required" explicit
- Community best practices: If you want full MCP capability (streaming, notifications, interactive/incremental workflows), deploy your server with HTTP/2 enabled
- For prototyping or local tools, `stdio` works well and sidesteps HTTP requirements

### Official Roadmap for Transport Evolution

From the MCP Transport Working Group's December 2025 blog post:

#### A Stateless Protocol

MCP was originally designed as a stateful protocol. The vision is a future where agentic applications are stateful, but the protocol itself doesn't need to be. A stateless protocol enables scale, while still providing features to support stateful application sessions when needed.

Planned changes:
- Replacing the `initialize` handshake and sending the shared information with each request and response instead
- Providing a `discovery` mechanism for clients to query server capabilities if needed early

#### Elevating Sessions

Currently, sessions are a side effect of the transport connection. The plan is to move sessions to the _data model layer_, making them explicit rather than implicit. This direction mirrors standard HTTP, where the protocol itself is stateless while applications build stateful semantics using cookies, tokens, and similar mechanisms.

#### Elicitations and Sampling at Scale

Supporting these features at scale requires rethinking the bidirectional communication pattern they rely on. The plan is to design server requests and responses to work similarly to chat APIs—the server returns the elicitation request as usual, and the client returns both the request and response together. This allows the server to reconstruct the necessary state purely from the returned message.

#### Update Notifications and Subscriptions

Exploring replacing the general-purpose `GET` stream with explicit subscription streams. Clients would open dedicated streams for specific items they want to monitor, with support for multiple concurrent subscriptions.

Adding Time-To-Live (TTL) values and version identifiers (such as ETags) to data would let clients make intelligent caching decisions independently of the notification stream, significantly improving reliability.

#### JSON-RPC Envelopes

Exploring ways to expose routing-critical information (such as the RPC method or tool name) via standard HTTP paths or headers. This would allow load balancers and API gateways to route traffic without parsing JSON bodies.

#### Server Cards

Introducing [MCP Server Cards](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1649): structured metadata documents that servers expose through a standardized `/.well-known/mcp.json` endpoint. Server Cards enable clients to discover server capabilities, authentication requirements, and available primitives _before_ establishing a connection.

#### Official and Custom Transports

MCP will continue to support only two official transports:
- **STDIO** for local deployments
- **Streamable HTTP** for remote deployments

Custom Transports are supported for teams with specialized requirements, including potential HTTP/3 implementations.

### Timeline

The goal is to finalize the required Spec Enhancement Proposals (SEPs) in Q1 2026 for inclusion in the June 2026 specification release. These changes reorient MCP around stateless, independent requests without sacrificing the rich features that make it powerful.

### What This Means for Developers

- **For simple deployments:** Continue using STDIO or basic Streamable HTTP
- **For production scale:** Target Streamable HTTP with HTTP/2 enabled; monitor MCP's working group for HTTP/3 advancements
- **For serverless:** The June 2026 spec release (with MRTR/stateless transport) will be the key milestone enabling AWS Lambda, Cloudflare Workers, etc.
- **For custom transports:** The SDK improvements will make custom transport implementations (including HTTP/3) more practical

### References

- [Official MCP Transport Roadmap Blog Post](https://blog.modelcontextprotocol.io/posts/2025-12-19-mcp-transport-future/)
- [MCP Contributors Discord server](https://modelcontextprotocol.io/community/communication#discord)
- [MCP Spec Enhancement Proposals](https://modelcontextprotocol.io/community/sep-guidelines)
- [Reddit r/mcp thread on HTTP2/HTTP3 support](https://www.reddit.com/r/mcp/comments/1jqbkhd/http2http3_support_in_the_future/)
