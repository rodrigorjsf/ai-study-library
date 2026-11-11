# Lessons

- Before claiming a detection/guarantee from an SDK field, test it on the real API: `RunResult.model` returns the resolved id (reading the bundle suggested it echoed the request).
- `parallel()`/`pipeline()` null-on-failure: required steps must check for null, never treat missing as "no findings".
- Agents loading project settings also load the project's own MCP servers: guard against self-recursion.
- Side effects in resumable workflows (commit, PR) must be idempotent.
- Never print SDK login results: they contain the minted API key.
- Agent SDK usage events can aggregate several model calls; check granularity before deriving per-call metrics.
- Dashboards on localhost: bind 127.0.0.1, validate Host, no CORS, read-only DB.
- The Cursor SDK starts `.cursor/mcp.json` servers without the parent env: env-based guards need an inline same-name server.
- Measure token semantics on the API: Cursor `inputTokens` already includes cache read and write.
- Never run project commands through a login shell (`bash -lc`): the profile can swap the PATH of the caller.
- Unsandboxed local agents can write outside the repo; check with a marker file and `find -newer`.
