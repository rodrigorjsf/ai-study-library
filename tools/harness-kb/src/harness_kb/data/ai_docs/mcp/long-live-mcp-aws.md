# Long Live MCP - the Dev Summit recap - AWS Builder Center

**Source:** https://builder.aws.com / https://community.aws (specific article not found - content compiled from web search)
**Category:** Model Context Protocol (MCP)

## Summary

A recap of the MCP Dev Summit NA 2026 from the AWS community perspective. AWS was a major participant and contributor at the summit, with James Hood delivering a keynote on "MCP @ Amazon Scale." The summit confirmed MCP's deep integration within AWS production workflows and announced major 2026 protocol improvements including stateless transport, enterprise auth, and hardened async support.

## Content

### Overview

The "Long Live MCP" theme was front and center at the MCP Dev Summit North America 2026, held April 2-3 at the New York Marriott Marquis, drawing about 1,200 attendees. As the newly donated MCP project found a home with the Linux Foundation's Agentic AI Foundation (AAIF), this summit marked MCP's transition from a fast-paced upstart to core industry infrastructure.

### Busting the "MCP is Dead" Myth

Despite widespread speculation about the decline of MCP, the summit was unequivocal: MCP is not only alive but rapidly maturing into a production-grade industry standard.

AWS's James Hood delivered a well-received keynote ("MCP @ Amazon Scale") debunking the "end of MCP" narrative. He cited Amazon's own heavy internal adoption of MCP: "There's a flurry of social media posts or articles proclaiming the death of MCP. I can tell you at Amazon, that is not true." MCP is a key integration protocol, not just a trendy wrapper around APIs—it is critical to the glue holding together agentic and AI-powered applications at scale.

### Enterprise Adoption & Ecosystem Growth

- **Attendance & Momentum:** The event doubled last year's numbers, making clear that MCP community momentum is surging. MCP is now hitting over 97 million SDK downloads per month and has support from 170+ AAIF member organizations (outpacing CNCF at the same point in its lifecycle).
- **Enterprise Use Cases:** Uber, Datadog, Docker, Duolingo, Bloomberg, and others demonstrated MCP in real-world deployment at both global and internal company scale. Patterns emerging included the use of centralized MCP Gateways, Registries, and observability integrations.

### Technical Roadmap: 2026 & Beyond

**June 2026 Major Features:**
- **Stateless Transport:** Designed for serverless/cloud-native platforms such as AWS Lambda or Cloudflare Workers, moving past stateful sessions and enabling easier horizontal scale.
- **Hardened Long-Running Tasks:** Improved async support for jobs that take minutes/hours, crucial for enterprise workflows (SEP-1686).
- **Enterprise Auth (Cross-App Access/XAA):** A move away from bearer tokens, introducing standardized, auditable authentication that integrates with SSO and workload identity federation.

**Beyond June:**
- **Registration & Discovery:** Enhanced support for MCP registry patterns—a must-have in complex enterprise environments.
- **Triggers:** Webhooks-for-MCP, supporting reactive workflows and automation.
- **Evolving Security**: Tightening conformance and audit trails, with over 30 CVEs filed and addressed so far in 2026.

### AWS & Community Highlights

- **AWS Leadership:** David Nalley, AWS's Director of Developer Experience, updated the summit on AAIF governance milestones and the opening of the project lifecycle process to nurture new contributions beyond MCP core.
- **OSS Ethos:** MCP's open source philosophy remains strong post-LF transition. The summit offered an open call-to-action for developers to engage, contribute, and co-create the protocol's next stages.
- **Developer Enablement:** Tooling around MCP—including discovery infrastructure, agent SOPS, and shared configuration frameworks—was showcased by AWS and other cloud vendors.

### AWS Builder Center & Developer Engagement

- AWS Builder Center is a key hub for MCP builders, offering community forums, showcases of agentic applications using MCP on AWS, tutorials (e.g., "From First Prompt to AI Agent"), and an official GitHub home for MCP AWS integrations.
- Live demos, blog posts, and "AIdeas" contest winners who are shipping MCP-based agents on AWS Builder Center show real-world use cases and rapid iteration with new AWS capabilities.

### Key Themes from the Summit

1. **Interoperability:** Repeated calls for MCP as the "API for AI." Not just another interface, but the backbone of cross-vendor, cross-cloud agentic architectures.
2. **Gateway Pattern:** Nearly all enterprise deployments now rely on agent gateways and registries to govern access, security, and scalability.
3. **Open Standards Stack:** AAIF leadership made clear MCP's scope will remain focused (agent-to-resource integration), with other functions like identity/governance addressed by companion standards or adjacent projects.

### Conclusion: "Long Live MCP"

Far from fading, MCP is scaling up—both in technical capability and in enterprise adoption, with AWS and community builders at the heart of this next phase. The summit's clear directive: participate, help define the open standards stack, and shape the rapidly emerging future of agentic AI.

All sessions (keynotes, technical deep dives, panels) from the summit are available for review on the Agentic AI Foundation YouTube channel.

### Resources

- [Agentic AI Foundation YouTube channel](https://www.youtube.com/@AgenticAI-Foundation)
- [AWS Builder Center](https://builder.aws.com/)
- [awslabs/mcp GitHub](https://github.com/awslabs/mcp) — Official MCP Servers for AWS
- [MCP Dev Summit official recap and slides](https://events.linuxfoundation.org/mcp-dev-summit-north-america/)
- [AAIF Blog: MCP Is Now Enterprise Infrastructure](https://aaif.io/blog/mcp-is-now-enterprise-infrastructure-everything-that-happened-at-mcp-dev-summit-north-america-2026/)
