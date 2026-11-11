# Lessons

- Before claiming a detection/guarantee from an SDK field, read how the bundle fills it (e.g. `RunResult.model` echoes the request).
- `parallel()`/`pipeline()` null-on-failure: required steps must check for null, never treat missing as "no findings".
- Agents loading project settings also load the project's own MCP servers: guard against self-recursion.
- Side effects in resumable workflows (commit, PR) must be idempotent.
- Never print SDK login results: they contain the minted API key.
- Agent SDK usage events can aggregate several model calls; check granularity before deriving per-call metrics.
- Dashboards on localhost: bind 127.0.0.1, validate Host, no CORS, read-only DB.
