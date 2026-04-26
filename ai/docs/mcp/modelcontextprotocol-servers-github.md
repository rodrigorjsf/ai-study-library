# MCP Servers - Official Reference Implementations (GitHub)

**Source:** https://github.com/modelcontextprotocol/servers
**Category:** Model Context Protocol (MCP)

## Summary

The official `modelcontextprotocol/servers` GitHub repository houses the reference MCP server implementations maintained by Anthropic. It includes the canonical "reference servers" (Fetch, Filesystem, Git, Memory, Sequential Thinking, Time, Everything) plus a curated list of frameworks, utilities, clients, and community resources for building MCP-compatible tools.

## Content

### Overview

This repository is a collection of reference implementations for the [Model Context Protocol](https://modelcontextprotocol.io/) (MCP), as well as references to community built servers and additional resources.

The servers in this repository showcase the versatility and extensibility of MCP, demonstrating how it can be used to give Large Language Models (LLMs) secure, controlled access to tools and data sources. Each MCP server is carefully implemented with security in mind, following MCP's core principle that servers should request only the permissions they need.

---

### Reference Servers

These servers are maintained by Anthropic and demonstrate canonical patterns for MCP implementation:

#### Everything
- **Package:** `@modelcontextprotocol/server-everything`
- **Description:** This MCP server attempts to exercise all the features of the MCP protocol. It is not intended to be a useful server, but rather a test server for MCP clients. It implements prompts, tools, resources, sampling, and roots.

#### Fetch
- **Package:** `@modelcontextprotocol/server-fetch`
- **Description:** A server that provides web content fetching capabilities. MCP server for fetching web content using headless Chrome. Enables LLMs to retrieve and process content from the web.

#### Filesystem
- **Package:** `@modelcontextprotocol/server-filesystem`
- **Description:** Node.js server implementing Model Context Protocol (MCP) for filesystem operations. Allows secure file operations with configurable access controls. Features: Read/write files, create/list/delete directories, move files/directories, search files, get file metadata.

#### Git
- **Package:** `@modelcontextprotocol/server-git`
- **Description:** A Model Context Protocol server for Git repository interaction and automation. This server provides tools to LLMs to interact with Git repositories, including reading file contents, listing branches, committing changes, and other Git operations.

#### Memory
- **Package:** `@modelcontextprotocol/server-memory`
- **Description:** An MCP server backed by a local knowledge graph for storing memories as entities and relations between them. Memories are stored in a local JSON file and are preserved between server restarts.

#### Sequential Thinking
- **Package:** `@modelcontextprotocol/server-sequential-thinking`
- **Description:** An MCP server implementation that provides a tool for dynamic and reflective problem-solving through a structured thinking process. This tool helps Claude think through complex problems by breaking them down into steps, allowing for revisions and refinements along the way.

#### Time
- **Package:** `@modelcontextprotocol/server-time`
- **Description:** A Model Context Protocol server providing tools for time and timezone conversions. Enables Claude to work with time-related queries and timezone conversions.

---

### Frameworks for Servers

| Name | Language | Description |
|------|----------|-------------|
| FastMCP | Python | Fast, Pythonic building of MCP servers with a simple API |
| FastMCP | TypeScript | High-level TypeScript framework for building MCP servers |
| Foxy Contexts | Golang | Golang library to write MCP servers declaratively |
| Genkit MCP | TypeScript | Provides integration between Genkit and MCP |
| LiteMCP | TypeScript | Lightweight MCP server framework |
| mark3labs/mcp-go | Golang | Golang implementation of MCP |
| mcp-framework | TypeScript | MCP framework for building servers |
| mcp-proxy | TypeScript | MCP proxy for wrapping stdio servers with an SSE server |
| mcp-rs-template | Rust | MCP CLI server template for Rust |
| Quarkus MCP Server | Java | Quarkus framework integration for MCP |
| Spring AI MCP | Java | Java+Spring AI MCP client and server |
| Template MCP Server | TypeScript | Template for creating MCP-servers |

---

### Frameworks for Clients

| Name | Language | Description |
|------|----------|-------------|
| coday | TypeScript | An opinionated multi-agent framework with MCP support |
| Continue | TypeScript | Open-source AI code assistant |
| Genkit | TypeScript | Firebase Genkit with MCP support |
| LangChain MCP | Python | LangChain MCP adapters for Python |
| LangChain.js MCP | TypeScript | LangChain MCP adapters for JavaScript |
| mcp-agent | Python | Powerful and simple framework to build AI agents |
| mastra | TypeScript | TypeScript agent framework with MCP support |
| omagent | Python | OmAgent: A multi-modal framework for agents |
| Semantic Kernel MCP | C# | Semantic Kernel with MCP integration |
| smolagents | Python | HuggingFace smolagents with MCP tooling |
| strands | Python | AWS Strands agent framework |
| vercel-ai-sdk | TypeScript | Vercel AI SDK with MCP toolset support |

---

### Utilities

| Name | Description |
|------|-------------|
| mcptools | CLI for MCP server management |
| mcp-get | CLI for installing and managing MCP servers |
| mcp-manager | CLI for managing MCP server configurations |
| MCP Inspector | Interactive debugging tool for MCP servers |

---

### Clients

Applications that support MCP as a client:

- **Claude Desktop** — Anthropic's desktop client for Claude
- **Claude.ai** — Web interface with remote MCP server support
- **Cline** — Open source AI coding assistant (VS Code extension)
- **Continue** — Open-source AI code assistant
- **Cursor** — AI-powered code editor
- **Windsurf** — AI coding environment by Codeium
- **Zed** — Code editor with built-in MCP support
- **GitHub Copilot** — Microsoft's AI code assistant (with MCP extension points)

---

### Additional Resources

**Official Sources:**
- [MCP Specification](https://spec.modelcontextprotocol.io)
- [MCP Documentation](https://modelcontextprotocol.io)
- [Model Context Protocol Blog](https://blog.modelcontextprotocol.io)
- [MCP Community Discord](https://discord.gg/TFE8FmjCdS)

**SDKs:**
- [TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Java SDK](https://github.com/modelcontextprotocol/java-sdk)
- [Kotlin SDK](https://github.com/modelcontextprotocol/kotlin-sdk)
- [C# SDK](https://github.com/modelcontextprotocol/csharp-sdk)
- [Go SDK](https://github.com/modelcontextprotocol/go-sdk)
- [Rust SDK](https://github.com/modelcontextprotocol/rust-sdk)
- [Swift SDK](https://github.com/modelcontextprotocol/swift-sdk)

---

### Contributing

MCP server contributions are welcome. The repository includes:
- Reference server implementations in TypeScript
- A `CONTRIBUTING.md` guide for adding new servers
- Issue templates for bug reports and feature requests

Contributions should follow the MCP protocol specification and include appropriate tests and documentation.
