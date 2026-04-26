# Long Live MCP - a recap of MCP Dev Summit NY | Aqfer

**Source:** https://aqfer.com/long-live-mcp-a-recap-of-mcp-dev-summit-ny/
**Category:** Model Context Protocol (MCP)

## Summary

A detailed recap by Aqfer's Ross Williams (Director of Application Engineering) of the MCP Dev Summit NA 2026, held April 2-3 in New York. The article argues that MCP is not dead despite online skepticism, highlights the June 2026 roadmap (stateless transport, enterprise auth via XAA, hardened async tasks), and covers major technical announcements including MRTR (Multi Round-Trip Requests), MCP Apps, and the CIMD/XAA auth story.

## Content

By Ross Williams, Director of Application Engineering

If you've been paying attention to the dev conversation online the last couple of months, you've seen some version of the _"MCP is over"_ take. Claude Code is just CLI calls. Security folks carved up the auth spec at RSAC. Every few weeks some new protocol lands promising to eat MCP for breakfast.

Short answer: no, MCP is not dead. MCP Dev Summit NA 2026 pushed back on the death narrative, mostly quietly, through who showed up and what they were running. More importantly, the summit laid out a concrete 2026 roadmap that directly addresses the valid concerns the critics had: scaling MCP on serverless, and getting auth off bearer tokens without DCR pain.

The event drew roughly 1,200 attendees to the New York Marriott Marquis on April 2 and 3. It was also the first summit under the new **Agentic AI Foundation** at the Linux Foundation, after MCP was donated there in December 2025. Jim Zemlin drew the CNCF comparison directly from the opening stage: CNCF took about 13 months to become infrastructure currency for cloud-native. MCP did the same in about 13 weeks.

## "MCP is dead" met the people with it in production

**James Hood** at AWS made the point most directly in his _"MCP @ Amazon Scale"_ keynote. One of his slides had the Mark Twain line on it: _"the reports of my death have been greatly exaggerated."_ The self-described former AI skeptic put it in his own words: _"There's a flurry of social media posts or articles proclaiming the death of MCP. I can tell you at Amazon, that is not true."_ The enterprise keynote roster across both days read the same way: Uber, Duolingo, Datadog, Docker, Nordstrom, Bloomberg, PwC, WorkOS, Workato. OpenAI's **Nick Cooper** landed the cleanest framing on Day 2: **"MCP is an API for AI,"** specifically designed assuming the consumer is a model, not a human developer. On CLIs versus MCP, his answer was _"you clearly want both. The most powerful systems combine them."_

## DSP's 2026 roadmap

Every session from the summit is now on the [Agentic AI Foundation YouTube channel](https://www.youtube.com/@AgenticAI-Foundation). If you only have time to watch one, make it David Soria Parra's _"MCP: The Integration Protocol"_ keynote. DSP is the MCP co-creator, and his twenty minutes on stage laid out where MCP is going in 2026.

Three things are landing in the **June 2026 spec release**:
- **Stateless transport by default** (designed for serverless runtimes like AWS Lambda and Cloudflare Workers)
- **Hardened long-running tasks** (SEP-1686, for async jobs that take minutes or hours)
- **Enterprise auth via Cross-App Access** (XAA)

Beyond June, DSP flagged:
- **Triggers** — basically webhooks for MCP, so servers can wake up clients when new data arrives
- **Native streaming** — will replace all-or-nothing tool results with incremental output
- **Skills over MCP** — gives you a way to ship skill libraries alongside MCP servers
- **Interceptors** — give the protocol standard hook points for observability, policy, and telemetry
- **Composability through code** — lets the model write a small program that chains several tool calls in sequence on the server side

DSP addressed context bloat head-on: the complaint that connecting an MCP server with a thousand tools blows out the context window. DSP was empathetic but direct: **that's a client problem, not a protocol problem.** Claude Code already solved it with progressive tool discovery, loading tool definitions only when the model actually needs them, with about an 85% reduction in token usage on real workloads.

## The scaling unlock: phone calls become email threads

The most important change in the June release for anyone running remote MCP servers on serverless is **MRTR**, Multi Round-Trip Requests (SEP-2322). The simplest way to explain it:

> **Today, a tool call is like a phone call.** The client and server stay on the line the whole time. If the server needs to ask the user something mid-call, say to confirm deletion of 1.2 million records from an audience, it holds the line open until the user answers. If the connection drops, the call is lost. This is fine on a long-lived server. It is structurally incompatible with any runtime that spins up per-request, like AWS Lambda or Cloudflare Workers.
>
> **MRTR turns the phone call into an email thread.** Each message carries the full context of prior messages. When the server needs to ask a question, it sends a reply with the question and closes the thread. The client comes back later, maybe five seconds later, maybe five minutes later, with a new message that includes the prior exchange. Any server can pick up the new message and respond. No held connections. No sticky routing. No shared memory.

For any team that has tried to make elicitation, sampling, or long-running tasks work on a horizontally-scaled backend, MRTR moves those features from _"impossible on our architecture"_ to _"just a normal email thread."_

## SDK Roadmap

The official SDKs are moving in parallel with the spec. **Max Isbey** at Anthropic laid out the shape in _"Path to V2 for MCP SDKs"_:
- **TypeScript V2 alpha is out now**
- Python V2 beta is Q2
- Both stable releases ship alongside the June spec

The architectural headline is a clean **dispatcher pattern** that finally separates MCP semantics from wire format and transport, which makes pluggable transports practical for the first time. TypeScript V2 also runs natively on Cloudflare Workers. **Go** joined TypeScript, Python, and C# in the tier-1 SDK list.

## The auth story: CIMD for clients, XAA for enterprise

Two things landed in the auth track:

**CIMD** (Client ID Metadata Documents) is the fix for Dynamic Client Registration. CIMD replaces DCR with DNS-rooted trust. A client hosts a JSON metadata document at a well-known URL, and that URL _is_ the client ID. No registration table, no silent expiry, no impersonation risk. Claude Code shipped CIMD support two weeks before the summit.

**Cross-App Access (XAA)** is the enterprise security story. Demoed live across Claude Code and Cursor into a real Figma MCP server with zero consent screens visible to the user, XAA lets the workforce IdP handle authorization centrally so end users stop drowning in per-app OAuth prompts.

**Aaron Parecki**, co-author of the OAuth 2.1 draft, tied the whole auth story together in one line: _"Most of OAuth works fine for MCP. It's three specific gaps."_ Client identification (CIMD). Bootstrap discovery from one URL (Protected Resource Metadata, now RFC 9728). Enterprise consent fatigue (XAA).

## MCP Apps: the future of the internet

MCP Apps is the first official MCP extension, shipped on January 26. Servers return tool results that point at HTML/JS/CSS bundles, the host renders them in a sandboxed iframe, and UI and host communicate bidirectionally over postMessage. Within four months every major host adopted it: Claude, ChatGPT, VS Code with Copilot, Cursor, Goose, Postman.

The Day 2 keynote by **Ido Salomon** (creator of MCP-UI) and **Liad Yosef** (co-creator of MCP Apps) made the case plainly: **this is the future of the internet.** The chat-box era is opening back up into rich, interactive, agent-driven surfaces, and the standard for how that works is being set right now.

## Tasks in practice

In _"Durable, Asynchronous, and Tricky: Implementing MCP Tasks in Practice,"_ **Cornelia Davis** at Temporal walked through implementing the SEP-1686 tasks primitive. She noted: _"There are no off-the-shelf agents today that support the task protocol. None. Claude doesn't. Claude Desktop doesn't. Goose doesn't."_

Davis closed her session with a line that ties the tasks work back to the transport story:

> _"Doing async over a stateful transport protocol is really tricky. I was over the moon excited this morning when I heard at least one, if not two, people in the keynote say we want to work on a transport protocol that is stateless."_

## The short version

A year of workarounds, half-built fixes, and skeptical social media threads got answered on stage by people with working code. The **June 2026 spec release** is the inflection point. If you've been waiting for MCP to grow up before betting on it, the wait is basically over.

The next North American AAIF event is **AGNTCon + MCPCon North America** in San Jose on October 22 and 23.
