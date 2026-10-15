# Writing an adoption plan (fork, hardening, integration)

## Before writing

1. Reconnoitre anything new the plan touches (another tool, the organisation's infrastructure) enough to ask
   informed questions. Read the code points that decide the design (identifier stability, extension points
   such as webhooks or plugins, existing config keys) before proposing changes to them.
2. Present to the user, explanation-first: what the plan must solve, what you verified, an outline, the
   options for each open decision with their consequences, and your recommendation. Ask only what changes the
   plan: deployment topology, LLM policy, depth of integration, the role of existing systems (read-only source
   or write target), network reachability, certificate authorities, deliverable formats.
3. Treat each answer as a decision. When research later suggests otherwise, keep the decision and record the
   alternative as a future option.

## Shape

| Section | Content |
|---|---|
| Decisions | The user's answers as premises, each with its consequence on the plan |
| Target architecture | One row per scope (code, work, organisation) with the question it answers and who writes what; a diagram |
| Epics | A table per epic: ID, change, finding it closes, where in the code, acceptance criterion |
| Integration bridge | The problem, the phases (federation first), where each part runs **in each deployment profile**, the contract with each tool (its CLI or MCP, never its private storage), how state is written without churning history, failure modes (enrichers fail open, gates fail closed) |
| Existing systems | Read-only access path, least-privilege role, audit, partitioning, untrusted-content handling, the open schema contract |
| Roadmap | Waves with dependencies and a verifiable exit for each |
| Risks and open decisions | Each with its mitigation or owner |
| Verification | Tests per acceptance criterion, contract tests per harness, red team, network capture, pentest |
| Bibliography | Every external fact with URL and the checked quote |

Every epic item cites the finding it closes. Cover **every** High and Medium finding of the security
chapters; the review in the next section checks that.

## Cross-cutting requirements that come up

- **Corporate certificate authorities**: check how each component builds TLS (OS trust store, bundled roots,
  `SSL_CERT_FILE`, `NODE_EXTRA_CA_CERTS`, `AWS_CA_BUNDLE`), whether client certificates (mTLS) are
  supported, and how hooks reach the server.
- **Telemetry and update checks** off by policy, with the exact variables.
- **Egress allowlist** and an explicit LLM policy (none, internal, vendor under zero retention).

## Before calling it ready

Run an advisor or critic review of the plan. Typical objections worth expecting: a component placed where
its data does not exist (a server cannot read a laptop's local index), state written in a way that floods
history, a High finding with no epic, a confirmed absence that was only grepped narrowly, a trade-off in a
new protocol left unstated. Apply each that holds.
