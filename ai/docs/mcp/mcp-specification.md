> ## Documentation Index
> Fetch the complete documentation index at: https://modelcontextprotocol.io/llms.txt
> Use this file to discover all available pages before exploring further.

# Specification

> Source: https://modelcontextprotocol.io/specification/2026-07-28.md — mirrored 2026-10-11 (previous capture ~2026-05-01). Mirrored revision: **2026-07-28**, the latest dated revision on 2026-10-11 (`https://modelcontextprotocol.io/specification.md` redirects to it; the previous capture summarized revision 2025-11-25). This file mirrors the specification's index page and, appended below under its own H1, the revision's "Key Changes" page (`https://modelcontextprotocol.io/specification/2026-07-28/changelog.md`). The other pages of the revision (architecture, transports, authorization, server and client features, schema) are not mirrored here; site-relative links such as `/specification/2026-07-28/...` resolve against `https://modelcontextprotocol.io`.

**Category:** Model Context Protocol (MCP)

<div id="enable-section-numbers" />

[Model Context Protocol](https://modelcontextprotocol.io) (MCP) is an open protocol that
enables seamless integration between LLM applications and external data sources and
tools. Whether you're building an AI-powered IDE, enhancing a chat interface, or creating
custom AI workflows, MCP provides a standardized way to connect LLMs with the context
they need.

This specification defines the authoritative protocol requirements, based on the
TypeScript schema in
[schema.ts](https://github.com/modelcontextprotocol/specification/blob/main/schema/2026-07-28/schema.ts).

For implementation guides and examples, visit
[modelcontextprotocol.io](https://modelcontextprotocol.io).

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD
NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in [BCP 14](https://datatracker.ietf.org/doc/html/bcp14)
\[[RFC2119](https://datatracker.ietf.org/doc/html/rfc2119)]
\[[RFC8174](https://datatracker.ietf.org/doc/html/rfc8174)] when, and only when, they
appear in all capitals, as shown here.

## Overview

MCP provides a standardized way for applications to:

* Share contextual information with language models
* Expose tools and capabilities to AI systems
* Build composable integrations and workflows

The protocol uses [JSON-RPC](https://www.jsonrpc.org/) 2.0 messages to establish
communication between:

* **Hosts**: LLM applications that initiate connections
* **Clients**: Connectors within the host application
* **Servers**: Services that provide context and capabilities

MCP takes some inspiration from the
[Language Server Protocol](https://microsoft.github.io/language-server-protocol/), which
standardizes how to add support for programming languages across a whole ecosystem of
development tools. In a similar way, MCP standardizes how to integrate additional context
and tools into the ecosystem of AI applications.

## Key Details

### Base Protocol

* [JSON-RPC](https://www.jsonrpc.org/) message format
* Stateless, self-contained requests
* Per-request capability negotiation

### Features

Servers offer any of the following features to clients:

* **Resources**: Context and data, for the user or the AI model to use
* **Prompts**: Templated messages and workflows for users
* **Tools**: Functions for the AI model to execute

Clients may offer the following features to servers:

* **Elicitation**: Server-initiated requests for additional information from users

### Additional Utilities

* Configuration
* Progress tracking
* Cancellation
* Error reporting

### Extensions

Beyond the core protocol, MCP defines optional [extensions](/extensions/overview)
that add modular, specialized, or experimental functionality. Extensions
are always opt-in and require explicit support from both client and server, negotiated
during initialization. Notable extensions include:

* **[Tasks](/extensions/tasks/overview)**: Asynchronous execution of long-running
  operations, with polling, mid-flight input, and durable handles
* **[Skills over MCP](/community/working-groups/skills-over-mcp)**: Rich, structured
  instructions for agent workflows, discovered and consumed through MCP
* **[MCP Apps](/extensions/apps/overview)**: Interactive UI elements (charts, forms,
  video players) rendered inline within conversations

## Security and Trust & Safety

The Model Context Protocol enables powerful capabilities through arbitrary data access
and code execution paths. With this power comes important security and trust
considerations that all implementors must carefully address.

### Key Principles

1. **User Consent and Control**
   * Users must explicitly consent to and understand all data access and operations
   * Users must retain control over what data is shared and what actions are taken
   * Implementors should provide clear UIs for reviewing and authorizing activities

2. **Data Privacy**
   * Hosts must obtain explicit user consent before exposing user data to servers
   * Hosts must not transmit resource data elsewhere without user consent
   * User data should be protected with appropriate access controls

3. **Tool Safety**
   * Tools represent arbitrary code execution and must be treated with appropriate
     caution.
     * In particular, descriptions of tool behavior such as annotations should be
       considered untrusted, unless obtained from a trusted server.
   * Hosts must obtain explicit user consent before invoking any tool
   * Users should understand what each tool does before authorizing its use

### Implementation Guidelines

While MCP itself cannot enforce these security principles at the protocol level,
implementors **SHOULD**:

1. Build robust consent and authorization flows into their applications
2. Provide clear documentation of security implications
3. Implement appropriate access controls and data protections
4. Follow security best practices in their integrations
5. Consider privacy implications in their feature designs

## Learn More

Explore the detailed specification for each protocol component:

<CardGroup cols={5}>
  <Card title="Architecture" icon="sitemap" href="/specification/2026-07-28/architecture" />

  <Card title="Base Protocol" icon="code" href="/specification/2026-07-28/basic" />

  <Card title="Server Features" icon="server" href="/specification/2026-07-28/server" />

  <Card title="Client Features" icon="user" href="/specification/2026-07-28/client" />

  <Card title="Contributing" icon="pencil" href="/community/contributing" />
</CardGroup>

---

<!-- Appended verbatim mirror: Key Changes (changelog) for revision 2026-07-28 -->

> ## Documentation Index
> Fetch the complete documentation index at: https://modelcontextprotocol.io/llms.txt
> Use this file to discover all available pages before exploring further.

# Key Changes

> Source: https://modelcontextprotocol.io/specification/2026-07-28/changelog.md — mirrored 2026-10-11 (previous capture ~2026-05-01). Appended verbatim mirror of the 2026-07-28 revision's changelog page.

<div id="enable-section-numbers" />

This document lists changes made to the Model Context Protocol (MCP) specification since
the previous revision, [2025-11-25](/specification/2025-11-25).

## Major changes

1. Remove protocol-level sessions and the `Mcp-Session-Id` header from the Streamable HTTP transport. List endpoints (`tools/list`, `resources/list`, `prompts/list`) no longer vary per-connection. Servers that need cross-call state use explicit, server-minted handles passed as ordinary tool arguments ([SEP-2567](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2567)).

2. Make MCP stateless: remove the `initialize`/`notifications/initialized` handshake. Every request now carries its protocol version and client capabilities in `_meta` (`io.modelcontextprotocol/protocolVersion`, `io.modelcontextprotocol/clientCapabilities`). Clients SHOULD identify themselves on each request (`io.modelcontextprotocol/clientInfo`), and servers SHOULD identify themselves in each result's `_meta` (`io.modelcontextprotocol/serverInfo`). Version mismatches return `UnsupportedProtocolVersionError` ([SEP-2575](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2575)).

3. Add `server/discover`: servers MUST implement this RPC to advertise their supported protocol versions, capabilities, and identity. Clients MAY call it before any other request for up-front version selection, or use it as a backward-compatibility probe on STDIO ([SEP-2575](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2575)).

4. Replace the HTTP GET endpoint and `resources/subscribe`/`resources/unsubscribe` with `subscriptions/listen`: a single long-lived POST-response stream for opted-in server-to-client change notifications. Clients opt in to specific types (`toolsListChanged`, `promptsListChanged`, `resourcesListChanged`, `resourceSubscriptions`); the server acknowledges and tags notifications with `io.modelcontextprotocol/subscriptionId`. Request-scoped notifications such as `notifications/progress` and `notifications/message` continue to flow on the response stream of the request they relate to, not the `subscriptions/listen` stream ([SEP-2575](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2575)).

5. Remove `ping`, `logging/setLevel`, and `notifications/roots/list_changed`. Log level is now set per-request via `io.modelcontextprotocol/logLevel` in `_meta`; servers MUST NOT emit `notifications/message` for requests that did not include this field ([SEP-2575](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2575)).

6. Move experimental tasks out of the core protocol and into an official extension (`io.modelcontextprotocol/tasks`). The redesigned extension replaces the blocking `tasks/result` method with polling via `tasks/get` and a new `tasks/update` for client-to-server input, removes `tasks/list`, and allows servers to return task handles unsolicited without per-request opt-in ([SEP-2663](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2663)).

7. Multi Round-Trip Requests (MRTR) pattern introduced which replaces the previous approach of sending server-initiated requests, such as `roots/list`, `sampling/createMessage`, or `elicitation/create`. Servers return an `InputRequiredResult` (`resultType: "input_required"`) whose `inputRequests` field carries the requests for the additional information needed to process the request. Clients respond with `inputResponses` on a retry of the original request providing the requested information. ([SEP-2322](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2322)).

8. All results now carry a required `resultType` field: `"complete"` for ordinary results and `"input_required"` for [multi round-trip request](/specification/2026-07-28/basic/patterns/mrtr) interim results. Clients **MUST** treat results from earlier-protocol servers that omit the field as `"complete"` ([SEP-2322](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2322)).

9. Remove SSE stream resumability and message redelivery (the `Last-Event-ID` header and SSE event IDs) from the Streamable HTTP transport. A broken response stream loses the in-flight request; clients **MUST** re-issue it as a new request with a new request ID ([SEP-2575](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2575)).

## Minor changes

1. Add `extensions` field to `ClientCapabilities` and `ServerCapabilities` to support optional [extensions](/docs/extensions/overview) beyond the core protocol.
2. Document OpenTelemetry trace context propagation conventions for `_meta` keys (`traceparent`, `tracestate`, `baggage`) ([SEP-414](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/414)).
3. Servers **SHOULD** return tools from `tools/list` in a deterministic order to enable client-side caching and improve LLM prompt cache hit rates.
4. Require standard MCP request headers (`Mcp-Method`, `Mcp-Name`) on Streamable HTTP POST requests, and add support for custom headers from tool parameters via `x-mcp-header` ([SEP-2243](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2243)).
5. Require `ttlMs` and `cacheScope` fields on results returned by `tools/list`, `prompts/list`, `resources/list`, `resources/read`, and `resources/templates/list` via a new `CacheableResult` interface. `ttlMs` is a freshness hint (in milliseconds) allowing clients to cache responses and reduce polling; `cacheScope` (`"public"` or `"private"`) controls whether shared intermediaries may cache the response. Both fields complement existing `listChanged` notifications ([SEP-2549](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2549)).
6. Change resource not found error code from `-32002` to `-32602` (Invalid Params) to align with JSON-RPC specification.
7. Authorization servers **SHOULD** include the `iss` parameter in authorization responses per
   [RFC 9207](https://datatracker.ietf.org/doc/html/rfc9207), and MCP clients **MUST** validate a
   present `iss` against the recorded issuer before redeeming the authorization code
   ([SEP-2468](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2468)).
8. Require MCP clients to specify an appropriate `application_type` during Dynamic Client
   Registration to avoid OpenID Connect redirect URI conflicts
   ([SEP-837](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/837)).
9. Clarify that client credentials are bound to the authorization server that issued them:
   clients **MUST** key persisted credentials by the issuer identifier, **MUST NOT** reuse them
   with a different authorization server, and **MUST** re-register when the authorization server
   changes ([SEP-2352](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2352)).
10. Loosen `inputSchema` and `outputSchema` to allow any JSON Schema 2020-12 keywords, and
    `structuredContent` to allow any JSON value. Add `$ref` resolution requirements and
    composition-keyword resource bounds
    ([SEP-2106](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2106)).
11. Remove the `notifications/elicitation/complete` notification and the
    `elicitationId` field of URL mode elicitation requests, both introduced in
    `2025-11-25`. Under the
    [Multi Round-Trip Requests](/specification/2026-07-28/basic/patterns/mrtr) pattern, the
    client learns the outcome of an out-of-band interaction by retrying the original
    request, so a server-initiated completion signal — and the identifier used to
    correlate it — no longer fit the protocol. Servers needing to correlate an
    elicitation across retries encode their own identifier in `requestState`.
12. Define an [error code allocation policy](/specification/2026-07-28/basic/index#error-codes)
    partitioning the JSON-RPC server-error range: `-32000` to `-32019` remains
    implementation-defined (existing SDK usage is grandfathered), `-32020` to `-32099` is
    reserved for the MCP specification. Renumber the error codes introduced in this draft
    accordingly — `HeaderMismatch` `-32001` → `-32020`, `MissingRequiredClientCapability`
    `-32003` → `-32021`, `UnsupportedProtocolVersion` `-32004` → `-32022` — and add
    `HeaderMismatchError` to the schema, which previously existed only in transport prose.

## Deprecated

Features listed here remain part of the specification but are scheduled for removal under the [feature lifecycle and deprecation policy](/community/feature-lifecycle). New implementations should not adopt them. The [deprecated features registry](/specification/2026-07-28/deprecated) tracks every feature currently in the Deprecated state.

1. Deprecate the Roots, Sampling, and Logging features
   ([SEP-2577](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2577)).
   These features remain fully functional during the deprecation window but new
   implementations should not add support for them. Suggested migrations: pass
   directories or files via tool parameters, resource URIs, or server
   configuration instead of Roots; integrate directly with LLM provider APIs
   instead of Sampling; log to `stderr` (stdio) or use OpenTelemetry instead of
   Logging.

2. Reclassify the HTTP+SSE transport (deprecated since protocol version
   `2025-03-26`) as Deprecated under the feature lifecycle policy
   ([SEP-2596](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2596)).
   Migrate to [Streamable HTTP](/specification/2026-07-28/basic/transports/streamable-http).

3. Reclassify the `includeContext` values `"thisServer"` and `"allServers"`
   (soft-deprecated since protocol version `2025-11-25`) as Deprecated
   ([SEP-2596](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2596)).
   Omit the field or use `"none"`; these values will be removed no later than
   the Sampling feature itself.

4. Deprecate the OAuth 2.0 Dynamic Client Registration Protocol
   ([RFC7591](https://datatracker.ietf.org/doc/html/rfc7591)) as a client registration
   mechanism in favor of
   [Client ID Metadata Documents](/specification/2026-07-28/basic/authorization/client-registration#client-id-metadata-documents)
   ([PR #2858](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2858)).
   It remains available for backwards compatibility with authorization servers that do
   not support Client ID Metadata Documents.

## Other schema changes

1. `schema.json` now correctly reflects that the Typescript definition of minimum/maximum/default are `number`'s and not just `integers`. This was caused by running the generator using `--defaultNumberType integer` ([PR#2710](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2710)).

## Governance and process updates

1. Adopt a specification
   [feature lifecycle and deprecation policy](/community/feature-lifecycle)
   defining the Active, Deprecated, and Removed feature states, a minimum
   twelve-month deprecation window, and a
   [registry of deprecated features](/specification/2026-07-28/deprecated)
   ([SEP-2596](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2596)).

## Process changes

1. Formalize PR-based SEP workflow with markdown files in `seps/` directory, PR-derived numbering, sponsor responsibilities, and status management via PR labels ([SEP-1850](https://github.com/modelcontextprotocol/specification/pull/1850)).

## Full changelog

For a complete list of all changes that have been made since the last protocol revision,
[see GitHub](https://github.com/modelcontextprotocol/specification/compare/2025-11-25...2026-07-28).
