# Cursor Agent — Programmatic / SDK / API Reference

> Grounding document for a Go reimplementation of a Cursor agent driver.
> Sources: **official Cursor properties only** — `cursor.com/docs` (incl. raw `.md` variants), `cursor.com/blog`, `cursor.com/changelog`, and Cursor's official npm package.
> **Access date for every citation: 2026-05-28.**
> Confidence tags: **[CONFIRMED]** = read verbatim from official primary text (raw `.md` or a code block reproduced identically across ≥2 fetches); **[VERIFY]** = strongly indicated but not pinned verbatim; **[UNVERIFIED]** = third-party only.
>
> Retrieval note: `docs.cursor.com/en/...` 308-redirects to `cursor.com/docs`. Every Cursor docs page is also served as clean Markdown at `<url>.md` (e.g. `https://cursor.com/docs/sdk/typescript.md`) — that is the authoritative, summarizer-free source and is what most **[CONFIRMED]** tags below rely on.

---

## 0. Headline verdict

As of 2026-05-28 there ARE official Cursor programmatic surfaces. A Go port has **four** entry points to choose from:

| # | Surface | What it is | Status | Best Go strategy |
|---|---|---|---|---|
| 1 | **Cursor SDK (TypeScript)** — `@cursor/sdk` (npm) | Official language SDK. Drives the *same* agent runtime (local **and** cloud) from code: codebase indexing, search/grep, MCP, skills, hooks, subagents, sandbox. | **Public beta, released 2026-04-29** | No Go SDK exists — reimplement its semantics. Richest spec to mirror. |
| 2 | **Cloud Agents API (`/v1`)** — `https://api.cursor.com/v1` | Current REST API. **Run-based**: durable *agents* own ephemeral *runs*; runs stream via SSE and emit artifacts. Self-hosted worker fleet endpoints too. | **Public beta** | Natural fit for a Go HTTP + SSE client. The SDK's cloud mode *appears* to ride this surface (shared `bc-` ids, shared status enums, shared run model) — **inference, not documented**; don't assume byte-for-byte isomorphism. |
| 3 | **Background Agents API (`/v0`)** — `https://api.cursor.com/v0` | Older REST surface (launch/poll/list/delete/followup on a GitHub repo, opens PRs). Coexists with `/v1`; **webhooks are documented on the `/v0`-style page**. No official "deprecated" notice was found. | Coexisting (older) | Simpler launch model; `/v1` is newer/richer. Use `/v1` for new work; reach for `/v0` shapes mainly for the webhook receiver. |
| 4 | **Cursor CLI (`cursor-agent`)** — local binary | Headless local agent. `--print` + `--output-format json\|stream-json` (NDJSON). | Beta | Easiest robust headless driver from Go: `os/exec` + NDJSON parse. |

**Languages (CORRECTED):** Cursor ships **TWO official SDKs** — **TypeScript** (`@cursor/sdk`) and **Python**. The "APIs Overview" page (`cursor.com/docs/api.md`) lists both as **"All users"**: *"TypeScript SDK — Run Cursor agents from TypeScript with one interface for local and cloud runtimes"* and *"Python SDK — Run Cursor agents from Python with sync and async clients for local and cloud runtimes"* (docs: `cursor.com/docs/sdk/python.md`). **No Go SDK** exists — the SDK-release blog only mentions investing "across more languages" (no Go date). Community PyPI/npm packages (`cursor-agent-sdk`, `cursor-cli`, `@nothumanwork/cursor-agents-sdk`, etc.) are **unofficial** — ignore them for modeling. **[CONFIRMED]** *(cursor.com/docs/api.md; cursor.com/blog/typescript-sdk)*
> The Python SDK page (`cursor.com/docs/sdk/python.md`) was **not transcribed** this session — its exact PyPI package name, sync/async client classes, and method names are **[VERIFY]**. Expect it to mirror the TS surface (Agent/Run/SDKMessage). For a Go port, the **TS SDK (Part 1) remains the most complete spec**; the Python SDK confirms the contract is cross-language and stable enough to mirror.

> Correction note: an earlier draft of this file said "no official SDK exists" (wrong — `@cursor/sdk` shipped 2026-04-29) and then "TypeScript only" (also wrong — an official Python SDK exists). This version supersedes both.

**Primary sources (all 2026-05-28):**
- SDK docs (raw md): `https://cursor.com/docs/sdk/typescript.md` (70 KB, read in full)
- SDK announce: `https://cursor.com/blog/typescript-sdk`, `https://cursor.com/changelog/sdk-release`
- npm: `https://www.npmjs.com/package/@cursor/sdk`
- Cloud Agents API (`/v1`) (raw md): `https://cursor.com/docs/cloud-agent/api/endpoints.md`
- Cursor APIs / auth (raw md): `https://cursor.com/docs/api.md`
- Webhooks (raw md): `https://cursor.com/docs/cloud-agent/api/webhooks.md` (and identical `.../background-agent/api/webhooks.md`)
- CLI params (raw md): `https://cursor.com/docs/cli/reference/parameters.md`
- CLI output format (raw md): `https://cursor.com/docs/cli/reference/output-format.md`
- CLI overview/using (raw md): `https://cursor.com/docs/cli/overview.md`, `https://cursor.com/docs/cli/using.md`

---

# PART 1 — Cursor SDK (`@cursor/sdk`, TypeScript)

The highest-fidelity spec to mirror in Go. Everything below is **[CONFIRMED]** from the raw SDK markdown unless tagged otherwise. The SDK exposes two namespaces: **`Agent`** (lifecycle + runs) and **`Cursor`** (account/catalog reads).

## 1.1 Install & auth
```bash
npm install @cursor/sdk        # NOTE: scoped name; bare "cursor/sdk" does not exist
export CURSOR_API_KEY="your-key"
```
- Auth: env `CURSOR_API_KEY`, or `apiKey` in options (option wins). Accepts **user API keys** (Dashboard → Integrations) and **service-account keys** (Team settings). **Team Admin keys not yet supported.** **[CONFIRMED]**
- All inference is **Cursor-hosted** in both local and cloud modes; "local" only means *where the agent loop runs*. **[CONFIRMED]**

## 1.2 Entry points (the `Agent` namespace, static methods)
```typescript
function Agent.create(options: AgentOptions): Promise<SDKAgent>;
function Agent.resume(agentId: string, options?: Partial<AgentOptions>): Promise<SDKAgent>;
function Agent.prompt(message: string, options?: AgentOptions): Promise<RunResult>;   // one-shot: create→send→wait→dispose

// inspection / lifecycle
function Agent.list(options?: ListAgentsOptions): Promise<ListResult<SDKAgentInfo>>;
function Agent.get(agentId: string, options?: GetAgentOptions): Promise<SDKAgentInfo>;
function Agent.listRuns(agentId: string, options?: ListRunsOptions): Promise<ListResult<Run>>;
function Agent.getRun(runId: string, options?: GetRunOptions): Promise<Run>;
function Agent.archive(agentId: string, options?: AgentOperationOptions): Promise<void>;
function Agent.unarchive(agentId: string, options?: AgentOperationOptions): Promise<void>;
function Agent.delete(agentId: string, options?: AgentOperationOptions): Promise<void>;
```
`Agent.resume()` auto-detects runtime from the **ID prefix**: `bc-<uuid>` = cloud, otherwise local (`agent-<uuid>`). **[CONFIRMED]**
> ⚠️ Agent-id separator is **not uniform** across surfaces: `/v1` + SDK use `bc-<uuid>` (hyphen); the `/v0` webhook payload shows `bc_abc123` (underscore). A Go id parser must accept **both** `bc-` and `bc_` (and the local `agent-` prefix). See PART 7 item 7. **[CONFIRMED on both pages]**

## 1.3 `AgentOptions` (constructor config) — [CONFIRMED]
```typescript
interface AgentOptions {
  model?: ModelSelection;                 // REQUIRED for local; cloud falls back to a server default
  apiKey?: string;                        // default: CURSOR_API_KEY env
  name?: string;                          // human-readable; auto-generated if omitted
  agentId?: string;                       // durable id; auto-generated if omitted
  mode?: "agent" | "plan";                // default: "agent"
  local?: {
    cwd?: string | string[];
    settingSources?: SettingSource[];     // which on-disk layers to load
    sandboxOptions?: { enabled: boolean };// default disabled
  };
  cloud?: CloudOptions;
  mcpServers?: Record<string, McpServerConfig>;
  agents?: Record<string, AgentDefinition>;   // subagents
}

type SettingSource = "project" | "user" | "team" | "mdm" | "plugins" | "all";

interface CloudOptions {
  env?: { type: "cloud" | "pool" | "machine"; name?: string };   // default { type: "cloud" }
  repos?: Array<{ url: string; startingRef?: string; prUrl?: string }>;   // up to 20
  workOnCurrentBranch?: boolean;          // default false
  autoCreatePR?: boolean;                 // default false
  skipReviewerRequest?: boolean;          // default false
  envVars?: Record<string, string>;       // encrypted, injected into shell, deleted with agent; names cannot start with CURSOR_
}
```
Runtime is selected by **which key you pass**: `local` → local loop; `cloud` → Cursor VM. **[CONFIRMED]**
- `cloud.env.type`: `cloud` = Cursor-hosted VM; `pool` = your **self-hosted pool**; `machine` = a specific **My Machines** worker. `env.name` selects a saved environment/pool. **Named Cursor-hosted environments and explicit `repos` are mutually exclusive**; omit `repos` + default `env` for a no-repo empty workspace. **[CONFIRMED]**
- SDK is **Node-first**: ships native deps (`sqlite3` for the local checkpoint store + a per-platform `@cursor/sdk-<os>-<arch>` binary for sandboxing/ripgrep). Local mode needs Node support for these. **[CONFIRMED]**
- SDK-created **cloud agents are hidden from the default agent list** (filter Source → SDK to see them). **[CONFIRMED]**

## 1.4 `SDKAgent` handle — [CONFIRMED]
```typescript
interface SDKAgent {
  readonly agentId: string;
  readonly model: ModelSelection | undefined;

  send(message: string | SDKUserMessage, options?: SendOptions): Promise<Run>;
  close(): void;                          // begin disposal, don't await
  reload(): Promise<void>;                // re-read hooks/MCP/subagents without disposing
  [Symbol.asyncDispose](): Promise<void>; // for `await using`

  listArtifacts(): Promise<SDKArtifact[]>;          // cloud only; local returns []
  downloadArtifact(path: string): Promise<Buffer>;  // cloud only; local throws
}

interface SDKUserMessage { text: string; images?: SDKImage[]; }
type SDKImage =
  | { url: string;  dimension?: { width: number; height: number } }
  | { data: string; mimeType: string; dimension?: { width: number; height: number } };

interface SendOptions {
  model?: ModelSelection;
  mode?: "agent" | "plan";
  mcpServers?: Record<string, McpServerConfig>;     // overrides create-time servers for this run
  onStep?:  (args: { step  }) => void | Promise<void>;
  onDelta?: (args: { update }) => void | Promise<void>;   // raw InteractionUpdate stream (see 1.7)
  local?: { force?: boolean };            // expire a stuck local run (local AgentBusy recovery)
}
```

## 1.5 `Run` — the unit of work — [CONFIRMED]
```typescript
type RunStatus = "running" | "finished" | "error" | "cancelled";   // SDK-level (lowercase)
type RunOperation = "stream" | "wait" | "cancel" | "conversation";

interface Run {
  readonly id: string;
  readonly agentId: string;
  readonly status: RunStatus;
  readonly result?: string;
  readonly model?: ModelSelection;
  readonly durationMs?: number;
  readonly git?: RunGitInfo;
  readonly createdAt?: number;

  stream(): AsyncGenerator<SDKMessage, void>;       // event stream (see 1.6)
  wait(): Promise<RunResult>;                        // resolves at terminal status
  cancel(): Promise<void>;                           // → status "cancelled", aborts stream, stops in-flight tools; partial output kept
  conversation(): Promise<ConversationTurn[]>;       // structured transcript (see 1.8)

  supports(operation: RunOperation): boolean;
  unsupportedReason(operation: RunOperation): string | undefined;
  onDidChangeStatus(listener: (status: RunStatus) => void): () => void;   // returns unsubscribe
}

interface RunResult {
  id: string;
  status: "finished" | "error" | "cancelled";
  result?: string;          // final assistant text
  model?: ModelSelection;
  durationMs?: number;
  git?: RunGitInfo;         // cloud only
}

interface RunGitInfo { branches: Array<{ repoUrl: string; branch?: string; prUrl?: string }>; }   // [CONFIRMED]
```
> ⚠️ Two distinct status vocabularies coexist. **SDK `Run.status`** is lowercase `running|finished|error|cancelled`. **REST/stream `status` events** use uppercase `CREATING|RUNNING|FINISHED|ERROR|CANCELLED|EXPIRED` (see `SDKStatusMessage` in 1.6 and `/v1` §2.5). A Go port must keep these two enums separate or normalize explicitly.

## 1.6 Streaming events — `run.stream()` yields `SDKMessage` — [CONFIRMED]
```typescript
type SDKMessage =
  | SDKSystemMessage
  | SDKUserMessageEvent
  | SDKAssistantMessage
  | SDKThinkingMessage
  | SDKToolUseMessage
  | SDKStatusMessage
  | SDKTaskMessage
  | SDKRequestMessage;

// every event carries agent_id + run_id (snake_case)
interface SDKSystemMessage   { type: "system"; subtype?: "init"; agent_id: string; run_id: string; model?: ModelSelection; tools?: string[]; }
interface SDKUserMessageEvent{ type: "user";   agent_id: string; run_id: string; message: { role: "user"; content: TextBlock[] }; }
interface SDKAssistantMessage{ type: "assistant"; agent_id: string; run_id: string;
                               message: { role: "assistant"; content: Array<TextBlock | ToolUseBlock> }; }
interface SDKThinkingMessage { type: "thinking"; agent_id: string; run_id: string; text: string; thinking_duration_ms?: number; }
interface SDKToolUseMessage  { type: "tool_call"; agent_id: string; run_id: string;
                               call_id: string; name: string;
                               status: "running" | "completed" | "error";
                               args?: unknown; result?: unknown;
                               truncated?: { args?: boolean; result?: boolean }; }
interface SDKStatusMessage   { type: "status"; agent_id: string; run_id: string;
                               status: "CREATING"|"RUNNING"|"FINISHED"|"ERROR"|"CANCELLED"|"EXPIRED"; message?: string; }
interface SDKTaskMessage     { type: "task"; agent_id: string; run_id: string; status?: string; text?: string; }
interface SDKRequestMessage  { type: "request"; agent_id: string; run_id: string; request_id: string; }  // awaiting user input

interface TextBlock    { type: "text"; text: string; }
interface ToolUseBlock { type: "tool_use"; id: string; name: string; input: unknown; }
```
Consumption pattern:
```typescript
for await (const event of run.stream()) {
  switch (event.type) {
    case "assistant": for (const b of event.message.content) if (b.type === "text") process.stdout.write(b.text); break;
    case "thinking":  process.stdout.write(event.text); break;
    case "tool_call": console.log(`[tool] ${event.name}: ${event.status}`); break;
    case "status":    console.log(`[status] ${event.status}`); break;
  }
}
```
Go: model `SDKMessage` as a tagged union discriminated on `type` (and `tool_call`.`status`). `args`/`result`/`input` are arbitrary → `json.RawMessage`.

## 1.7 Raw deltas — `onDelta` `InteractionUpdate` union — [CONFIRMED]
Lower-level than `stream()`; character-level deltas + token/step accounting.
```typescript
type InteractionUpdate =
  | { type: "text-delta"; text: string }
  | { type: "thinking-delta"; text: string }
  | { type: "thinking-completed"; thinkingDurationMs: number }
  | { type: "tool-call-started";   callId: string; toolCall: ToolCall; modelCallId: string }
  | { type: "partial-tool-call";   callId: string; toolCall: ToolCall; modelCallId: string }
  | { type: "tool-call-completed"; callId: string; toolCall: ToolCall; modelCallId: string }
  | { type: "token-delta"; tokens: number }
  | { type: "step-started";   stepId: number }
  | { type: "step-completed"; stepId: number; stepDurationMs: number }
  | { type: "turn-ended"; usage?: { inputTokens: number; outputTokens: number; cacheReadTokens: number; cacheWriteTokens: number } }
  // also documented in the union: user-message-appended, summary, summary-started, summary-completed, shell-output-delta
  ;
```
*(`ToolCall` is a **discriminated union over every built-in tool** — documented set: `shell, edit, read, write, glob, grep, ls, semSearch, mcp, task` (and others). Its per-tool shape is explicitly **internal-facing and NOT stable** — the docs say: treat `args`/`result`/`input` as `unknown` and parse defensively; only the envelope (`type`, `call_id`, `name`, `status`) is stable. **[CONFIRMED]** For Go, model `ToolCall`/`args`/`result` as `json.RawMessage` and branch on `name`.)*

## 1.8 Structured transcript — `run.conversation()` — [CONFIRMED]
```typescript
type ConversationTurn =
  | { type: "agentConversationTurn"; turn: AgentConversationTurn }
  | { type: "shellConversationTurn"; turn: ShellConversationTurn };

interface AgentConversationTurn { userMessage?: UserMessage; steps: ConversationStep[]; }
interface ShellConversationTurn { shellCommand?: ShellCommand; shellOutput?: ShellOutput; }   // [CONFIRMED]
type ConversationStep =
  | { type: "assistantMessage"; message: AssistantMessage }
  | { type: "toolCall";         message: ToolCall }
  | { type: "thinkingMessage";  message: ThinkingMessage };

interface AssistantMessage { text: string; }
interface ThinkingMessage  { text: string; thinkingDurationMs?: number; }
interface UserMessage      { text: string; }
interface ShellCommand     { command: string; workingDirectory?: string; }                    // [CONFIRMED]
interface ShellOutput      { stdout: string; stderr: string; exitCode: number; }              // [CONFIRMED]
```

## 1.9 Models — [CONFIRMED]
```typescript
interface ModelSelection      { id: string; params?: ModelParameterValue[]; }
interface ModelParameterValue { id: string; value: string; }   // e.g. { id: "thinking", value: "high" } / { id: "fast", value: "true" }

function Cursor.models.list(options?: CursorRequestOptions): Promise<SDKModel[]>;
interface SDKModel {
  id: string; displayName: string; description?: string;
  parameters?: ModelParameterDefinition[]; variants?: ModelVariant[];
}
interface ModelParameterDefinition { id: string; displayName?: string; values: Array<{ value: string; displayName?: string }>; }
interface ModelVariant { params: ModelParameterValue[]; displayName: string; description?: string; isDefault?: boolean; }
```
Discover models at runtime; **do not hardcode ids**. Real ids seen in docs: `composer-2`, `composer-2.5`, `gpt-5.5`, `claude-4.6-sonnet-thinking`, plus alias `auto`. **[CONFIRMED examples; query at runtime]**

## 1.10 Permissions & approvals — [CONFIRMED]
- **Default for local agents: tool calls (shell/edit/write) run WITHOUT approval — there is no human-in-the-loop prompt in headless mode.** (Same posture as CLI `--force`.) **[CONFIRMED]**
- Gate tool calls via **hooks** (`.cursor/hooks.json`, e.g. `beforeShellExecution`) — file-based only, no programmatic callback API. **[CONFIRMED]**
- **Sandbox** (local only): `local.sandboxOptions.enabled` (default `false`). When on: writes limited to cwd + allowlist; reads outside workspace blocked; shell in platform sandbox (`bubblewrap`/Linux, `seatbelt`/macOS); outbound network denied except `.cursor/sandbox.json` allowlist. Cloud always runs in an isolated VM. **[CONFIRMED]**

## 1.11 Sessions & resuming — [CONFIRMED]
- Local agents persist conversation in a SQLite checkpoint store under the home dir; `Agent.resume(agentId)` from a new process resumes it.
- Cloud agents persist server-side; reattach from anywhere.
- **Inline `mcpServers` are NOT persisted across `Agent.resume()`** — re-pass them or use file-based `.cursor/mcp.json`.

## 1.12 Cancellation & disposal — [CONFIRMED]
```typescript
await run.cancel();                 // → "cancelled"; stream aborts; in-flight tools stop; run.wait() resolves "cancelled"
await using agent = await Agent.create({...});   // auto-dispose on block exit
await agent[Symbol.asyncDispose]();              // explicit
agent.close();                                   // fire-and-forget
```

## 1.13 Listing / inspection types — [CONFIRMED]
```typescript
interface ListResult<T> { items: T[]; nextCursor?: string; }

type ListAgentsOptions = { limit?: number; cursor?: string } & (
  | { runtime?: undefined }
  | { runtime: "local"; cwd?: string }
  | { runtime: "cloud"; prUrl?: string; includeArchived?: boolean; apiKey?: string }
);
type ListRunsOptions = { limit?: number; cursor?: string } & (
  | { runtime?: "local"; cwd?: string }
  | { runtime: "cloud"; apiKey?: string }
);
type GetRunOptions =
  | { runtime?: "local"; cwd?: string }
  | { runtime: "cloud"; agentId: string; apiKey?: string };
interface GetAgentOptions { cwd?: string; apiKey?: string; }
interface AgentOperationOptions { cwd?: string; apiKey?: string; }

type SDKAgentInfo = {
  agentId: string; name: string; summary: string; lastModified: number;
  status?: "running" | "finished" | "error"; createdAt?: number; archived?: boolean;
} & (
  | { runtime?: undefined }
  | { runtime: "local"; cwd?: string }
  | { runtime: "cloud"; env?: { type: "cloud"|"pool"|"machine"; name?: string }; repos?: string[] }
);
```

## 1.14 MCP / subagents / artifacts / account — [CONFIRMED]
```typescript
type McpServerConfig =
  | { type?: "stdio"; command: string; args?: string[]; env?: Record<string,string>; cwd?: string }
  | { type?: "http" | "sse"; url: string; headers?: Record<string,string>;
      auth?: { CLIENT_ID: string; CLIENT_SECRET?: string; scopes?: string[] } };

interface AgentDefinition {            // subagents (also loadable from .cursor/agents/*.md)
  description: string; prompt: string;
  model?: ModelSelection | "inherit";
  mcpServers?: Array<string | Record<string, McpServerConfig>>;
}

interface SDKArtifact { path: string; sizeBytes: number; updatedAt: string; }   // cloud only

function Cursor.me(options?: CursorRequestOptions): Promise<SDKUser>;
interface SDKUser { apiKeyName: string; userEmail?: string; createdAt: string; }
function Cursor.repositories.list(options?: CursorRequestOptions): Promise<SDKRepository[]>;
interface SDKRepository { url: string; }
interface CursorRequestOptions { apiKey?: string; }
```
MCP precedence (local): send-opts → create-opts → plugins → project `.cursor/mcp.json` → user `~/.cursor/mcp.json`. Cloud: send-opts → create-opts → team servers at cursor.com/agents. **[CONFIRMED]**

## 1.15 Error types — [CONFIRMED]
```typescript
class CursorSdkError extends Error {        // re-exported as CursorAgentError for backwards compat
  readonly code?: string;        // stable SDK/backend code
  readonly status?: number;      // HTTP status if available
  readonly cause?: unknown;      // wrapped underlying error
  readonly endpoint?: string;
  readonly requestId?: string;
  readonly operation?: string;
  readonly isRetryable?: boolean;          // drive retry logic off this  [CONFIRMED]
}
class AuthenticationError          extends CursorSdkError {}     // invalid/expired/disabled key
class RateLimitError               extends CursorSdkError {}     // burst OR monthly usage cap; isRetryable:true for transient
class ConfigurationError           extends CursorSdkError {}     // bad model/params, unsupported file, admin policy, AND 409 agent_archived
class AgentBusyError               extends CursorSdkError { readonly code: "agent_busy"; readonly status: 409; readonly isRetryable: false; }  // cloud only
class IntegrationNotConnectedError extends ConfigurationError { readonly provider: string; readonly helpUrl: string; }  // provider e.g. "github"/"gitlab"/"azuredevops"
class NetworkError                 extends CursorSdkError {}     // transient/timeout (check requestId)
class UnsupportedRunOperationError extends ConfigurationError { readonly operation: RunOperation; }  // guard via run.supports()
class UnknownAgentError            extends CursorSdkError {}     // unclassified; inspect code/cause
```
> Distinguish 409s: **`agent_busy` → `AgentBusyError`** (not retryable; wait/cancel first), but **`agent_archived` → `ConfigurationError`**. Log `error.helpUrl` when present (most common on `IntegrationNotConnectedError`). **[CONFIRMED]**
**AgentBusy recovery** (the canonical SDK pattern): catch `AgentBusyError` → `Agent.listRuns(agentId, { runtime: "cloud" })` → cancel `items[0]` if `status === "running"` → retry `send`. For local: `send(msg, { local: { force: true } })`. **[CONFIRMED]**

## 1.16 SDK end-to-end examples — [CONFIRMED]
Local, streaming:
```typescript
import { Agent } from "@cursor/sdk";
const agent = await Agent.create({ apiKey: process.env.CURSOR_API_KEY!, model: { id: "composer-2.5" }, local: { cwd: process.cwd() } });
const run = await agent.send("Summarize this repository");
for await (const e of run.stream()) if (e.type === "assistant") for (const b of e.message.content) if (b.type === "text") process.stdout.write(b.text);
await agent[Symbol.asyncDispose]();
```
Cloud, fire-and-reattach:
```typescript
const agent = await Agent.create({ apiKey: process.env.CURSOR_API_KEY!, model: { id: "gpt-5.5" },
  cloud: { repos: [{ url: "https://github.com/cursor/cookbook", startingRef: "main" }], autoCreatePR: true } });
const run = await agent.send("Fix the auth token expiry bug");
const result = await (await Agent.getRun(run.id, { runtime: "cloud", agentId: run.agentId })).wait();
console.log(result.git?.branches[0]?.prUrl);
```
Multi-turn plan→build (AFK on one cloud session):
```typescript
const agent = await Agent.create({ apiKey, model: { id: "composer-2.5" }, mode: "plan", cloud: { repos: [{ url }] } });
await (await agent.send("Design the auth refactor")).wait();
await (await agent.send("Looks good, start building", { mode: "agent" })).wait();
```
Pricing: token-based consumption; spend tagged "SDK" in the usage dashboard. User keys bill the user; service-account keys bill the team. **[CONFIRMED]**

> Cookbook (official examples): `https://github.com/cursor/cookbook` → `sdk/quickstart`, `sdk/app-builder`, plus a cloud-agents kanban demo. **[CONFIRMED]**

---

# PART 2 — Cloud Agents API (`/v1`) — current REST surface

Base URL **`https://api.cursor.com`**, endpoints under **`/v1`** (worker-fleet ones under `/v0`). Run-based: durable **agent** + ephemeral **runs**; **only one active run per agent** (concurrent → HTTP `409 agent_busy`). Public beta. **[CONFIRMED]** *(cloud-agent/api/endpoints.md)*

## 2.1 Authentication — [CONFIRMED]
> **RULE (verbatim from `api.md`): Basic auth works on ALL Cursor APIs; `Authorization: Bearer` is accepted ONLY by the Cloud Agents API.** *"All Cursor APIs accept Basic Authentication. The Cloud Agents API additionally accepts Bearer tokens."* So for a Go client that may also touch Admin/Analytics/AI-Code-Tracking endpoints, **default to Basic everywhere** and use Bearer only as an optional convenience on `/v0`+`/v1` agent endpoints.

Both schemes accepted on the Cloud Agents API (curl forms from `api.md`):
```bash
curl https://api.cursor.com/v1/me -u YOUR_API_KEY:                       # Basic: key as username, EMPTY password (trailing colon) — works on every Cursor API
curl https://api.cursor.com/v1/me -H "Authorization: Bearer YOUR_API_KEY"   # Bearer — Cloud Agents API only
```
Go: `req.SetBasicAuth(apiKey, "")` (preferred, universal) **or** `req.Header.Set("Authorization", "Bearer "+apiKey)` (Cloud Agents only). Basic header form is `Authorization: Basic base64("YOUR_API_KEY:")`. Keys: user (Dashboard → Integrations) or service account (Team settings; required for worker/fleet + `/v1/sub-tokens`).

## 2.2 Endpoint map — [CONFIRMED]
| Method | Path | Purpose |
|---|---|---|
| POST | `/v1/agents` | Create agent + enqueue initial run |
| GET | `/v1/agents` | List agents (`limit`≤100 def 20, `cursor`, `prUrl`, `includeArchived` def true) |
| GET | `/v1/agents/{id}` | Get agent |
| POST | `/v1/agents/{id}/archive` | Archive (reversible) |
| POST | `/v1/agents/{id}/unarchive` | Unarchive |
| DELETE | `/v1/agents/{id}` | Delete permanently |
| POST | `/v1/agents/{id}/runs` | Create follow-up run |
| GET | `/v1/agents/{id}/runs` | List runs (`limit`≤100, `cursor`) |
| GET | `/v1/agents/{id}/runs/{runId}` | Get run |
| GET | `/v1/agents/{id}/runs/{runId}/stream` | **SSE stream** |
| POST | `/v1/agents/{id}/runs/{runId}/cancel` | Cancel run |
| GET | `/v1/agents/{id}/artifacts` | List artifacts |
| GET | `/v1/agents/{id}/artifacts/download?path=…` | Presigned S3 URL (~15-min) |
| POST | `/v1/sub-tokens` | User-scoped worker token (1-hr, non-refreshing; needs service-account key) |
| GET | `/v0/private-workers` | List self-hosted workers (`status` all/in_use/idle, `limit` 1–100 def 50, `nextPageToken`) |
| GET | `/v0/private-workers/summary` | Fleet summary (`teamSummary.totalConnected`, `.inUse`) |
| GET | `/v0/private-workers/{id}` | Worker detail (id like `pw_123`) |
| GET | `/v0/private-workers/pending-requests` | Unassigned pool requests (`limit`,`pageToken`,`repository`) |
| GET | `/v1/me` | API key info |
| GET | `/v1/models` | List models |
| GET | `/v1/repositories` | List repos (rate-limited 1/min, 30/hr per user) |

## 2.3 Create Agent — `POST /v1/agents` — [CONFIRMED]
Request body:
| Field | Type | Req | Limits / notes |
|---|---|---|---|
| `prompt.text` | string | ✓ | |
| `prompt.images[]` | array | | ≤5, 15 MB each; `image/png\|jpeg\|gif\|webp`; each `{ data, mimeType }` or `{ url }` |
| `model.id` | string | (req if `model` given) | from `GET /v1/models` |
| `model.params[]` | `[{id,value}]` | | |
| `name` | string | | ≤100 chars |
| `env.type` | `cloud`\|`pool`\|`machine` | | |
| `env.name` | string | | named env/pool |
| `repos[]` | array | | ≤20; each `{ url(req), startingRef?, prUrl? }` |
| `workOnCurrentBranch` | boolean | | default false |
| `autoCreatePR` | boolean | | |
| `skipReviewerRequest` | boolean | | |
| `envVars` | object | | ≤50; name ≤255 B, value ≤4096 B |
| `mcpServers[]` | array | | ≤50 |
| `customSubagents[]` | array | | ≤20 |
| `mode` | `plan`\|`agent` | | default `agent` |
| `agentId` | string | | client-supplied `bc-<uuid>` for idempotency |

Response — `{ agent, run }`:
```json
{
  "agent": {
    "id": "bc-00000000-0000-0000-0000-000000000001",
    "name": "Add README with setup instructions",
    "status": "ACTIVE",
    "env": { "type": "cloud" },
    "repos": [{ "url": "https://github.com/your-org/your-repo", "startingRef": "main" }],
    "workOnCurrentBranch": false,
    "autoCreatePR": true,
    "url": "https://cursor.com/agents/bc-00000000-0000-0000-0000-000000000001",
    "createdAt": "2026-04-13T18:30:00.000Z",
    "updatedAt": "2026-04-13T18:30:00.000Z",
    "latestRunId": "run-00000000-0000-0000-0000-000000000001"
  },
  "run": {
    "id": "run-00000000-0000-0000-0000-000000000001",
    "agentId": "bc-00000000-0000-0000-0000-000000000001",
    "status": "CREATING",
    "createdAt": "2026-04-13T18:30:00.000Z",
    "updatedAt": "2026-04-13T18:30:00.000Z"
  }
}
```
> Note the two id spaces: **agents** `bc-<uuid>`, **runs** `run-<uuid>`. **Agent `status` enum = `ACTIVE` | `ARCHIVED`** (≠ run status). [CONFIRMED]

## 2.4 Runs — [CONFIRMED]
- `POST /v1/agents/{id}/runs` body: `prompt.{text(req),images?}`, `mcpServers?` (replaces create-time for this run), `mode?`. Response `{ run: { id, agentId, status:"CREATING", createdAt, updatedAt } }`.
- `GET /v1/agents/{id}/runs/{runId}` (terminal example):
```json
{
  "id": "run-00000000-0000-0000-0000-000000000001",
  "agentId": "bc-00000000-0000-0000-0000-000000000001",
  "status": "FINISHED",
  "createdAt": "2026-04-13T18:30:00.000Z",
  "updatedAt": "2026-04-13T18:45:00.000Z",
  "durationMs": 12357,
  "result": "Added README.md with installation instructions and usage examples.",
  "git": { "branches": [
    { "repoUrl": "github.com/your-org/your-repo", "branch": "cursor/add-readme-a1b2", "prUrl": "https://github.com/your-org/your-repo/pull/123" }
  ]}
}
```
> `git.branches[]` = `{ repoUrl, branch?, prUrl? }`; it is **per-agent state, not per-run** — all runs on the same agent return the same snapshot. `durationMs`, `result`, `git` appear only once a run progresses → model as optional/nullable in Go. **[CONFIRMED]**

## 2.5 Run `status` enum — [CONFIRMED]
`CREATING`, `RUNNING`, `FINISHED`, `ERROR`, `CANCELLED`, `EXPIRED`. (Use a string type + named constants; tolerate unknowns — beta.)

## 2.6 Stream a Run (SSE) — `GET /v1/agents/{id}/runs/{runId}/stream` — [CONFIRMED]
Header `Accept: text/event-stream`. **Resume with `Last-Event-ID`** (each event has `id:`). Retention advertised via response header `X-Cursor-Stream-Retention-Seconds`; after expiry the endpoint may return **`410 stream_expired`** (fall back to `GET .../runs/{runId}`).

Event names + `data` shape:
| `event:` | `data` JSON |
|---|---|
| `status` | `{ "runId", "status" }` |
| `assistant` | `{ "text" }` |
| `thinking` | `{ "text" }` |
| `tool_call` | `{ "callId", "name", "status", "args"?, "result"?, "truncated"? }` (`status` `running`\|`completed`) |
| `interaction_update` | SDK-shaped (mirrors §1.7) |
| `heartbeat` | `{}` |
| `result` | `{ "runId", "status", "text"?, "durationMs"?, "git"? }` |
| `error` | `{ "code", "message" }` |
| `done` | `{}` |

Verbatim wire sample:
```text
event: status
data: {"runId":"run-00000000-0000-0000-0000-000000000001","status":"RUNNING"}

id: 1713033000000-0
event: assistant
data: {"text":"I'll update the README now."}

id: 1713033005000-0
event: tool_call
data: {"callId":"call-1","name":"read_file","status":"running","args":{"path":"README.md"}}

id: 1713033006000-0
event: tool_call
data: {"callId":"call-1","name":"read_file","status":"completed","args":{"path":"README.md"},"result":{"success":{"content":"# Project","totalLines":1,"fileSize":9,"path":"README.md"}}}

id: 1713033010000-0
event: result
data: {"runId":"run-...001","status":"FINISHED","text":"Added README.md ...","durationMs":12357,"git":{"branches":[{"repoUrl":"github.com/your-org/your-repo","branch":"cursor/add-readme-a1b2"}]}}

id: 1713033010000-0
event: done
data: {}
```
Go: standard SSE parser (split on blank line; collect `event:`/`id:`/`data:`); persist last `id` for reconnect via `Last-Event-ID`; dispatch on `event`; terminate on `done`/`error`.

## 2.7 Cancel / lifecycle / artifacts / metadata — [CONFIRMED]
- `POST /v1/agents/{id}/runs/{runId}/cancel` → `{ "id": "run-...001" }`
- `POST /v1/agents/{id}/archive` | `/unarchive`, `DELETE /v1/agents/{id}` → `{ "id": "bc-...001" }`
- `GET /v1/agents/{id}/artifacts` → `{ "items": [{ "path", "sizeBytes", "updatedAt" }] }`
- `GET /v1/agents/{id}/artifacts/download?path=…` → `{ "url": "https://cloud-agent-artifacts.s3...", "expiresAt": "...Z" }`
- `POST /v1/sub-tokens` body one-of `{ forUserEmail }` | `{ forUserId }` → `{ "accessToken", "expiresAt", "userId", "teamId" }` (1-hr)
- `GET /v1/me` → user-scoped `{ apiKeyName, userId, createdAt, userEmail, userFirstName, userLastName }`; service-account `{ apiKeyName, createdAt }`
- `GET /v1/models` → `{ "items": [{ id, displayName, aliases?, description?, parameters?[], variants?[] }] }`
- `GET /v1/repositories` → `{ "items": [{ "url" }] }`

## 2.8 Pagination convention — [CONFIRMED]
`/v1` lists return `{ items, nextCursor? }` (pass `nextCursor` back as `cursor`). Worker `/v0` lists use `{ ..., nextPageToken? }` (pass back as `pageToken`/`nextPageToken`). Absence of the cursor field = end.

---

# PART 3 — Background Agents API (`/v0`) — older REST surface + webhooks

Same base URL/auth as `/v1`, **coexisting** with it (no official deprecation notice was found — do not assume `/v0` is removed). Launch/poll/list/delete/followup against a GitHub repo; agent ids are `bc-...`. The **webhook system is documented on the `/v0`-style page** and is the simplest push-notification path. **[CONFIRMED for auth + webhooks; per-endpoint `/v0` field tables are partly VERIFY — prefer `/v1` for new work.]**

## 3.1 Endpoints (`/v0`)
| Method | Path | Purpose |
|---|---|---|
| POST | `/v0/agents` | Launch (body `prompt.text`, `source.{repository(req),ref}`, `model?`, `target.{autoCreatePr?,branchName?}`, `webhook.{url,secret?}`) |
| GET | `/v0/agents` | List (`limit`,`cursor`) → `{ agents:[...], nextCursor? }` |
| GET | `/v0/agents/{id}` | Status |
| GET | `/v0/agents/{id}/conversation` | Conversation/messages **[VERIFY shape]** |
| POST | `/v0/agents/{id}/followup` | `{ prompt:{ text } }` → `{ id }` |
| DELETE | `/v0/agents/{id}` | Delete (permanent) → `{ id }` |
| GET | `/v0/models` | `{ models:[...] }` |
| GET | `/v0/repositories` | repo list |
| GET | `/v0/me` | key info |

> The `/v0` agent/launch JSON uses `source`/`target` (e.g. `source.repository`, `target.autoCreatePr`, `target.branchName`, `target.prUrl`) — **different field names from `/v1`'s `repos[]`/`autoCreatePR`**. The webhook payload (below) is `/v0`-shaped, so a Go webhook receiver must use the `source`/`target` schema even if you launch via `/v1`. **[CONFIRMED for webhook; VERIFY for launch body field-by-field]**

## 3.2 Webhooks — [CONFIRMED] *(cloud-agent/api/webhooks.md, identical at background-agent/api/webhooks.md)*
Configure at launch with a `webhook` object (`url`, optional `secret`). Cursor POSTs on status change.

Payload (verbatim from docs — note `id` uses `bc_` underscore form here, vs `bc-` hyphen in `/v1`; do not assume one canonical separator):
```json
{
  "event": "statusChange",
  "timestamp": "2024-01-15T10:30:00Z",
  "id": "bc_abc123",
  "status": "FINISHED",
  "source": { "repository": "https://github.com/your-org/your-repo", "ref": "main" },
  "target": {
    "url": "https://cursor.com/agents?id=bc_abc123",
    "branchName": "cursor/add-readme-1234",
    "prUrl": "https://github.com/your-org/your-repo/pull/1234"
  },
  "summary": "Added README.md with installation instructions"
}
```
Headers (verbatim table):
| Header | Meaning |
|---|---|
| `X-Webhook-Signature` | **`sha256=<hex_digest>`** — HMAC-SHA256 of the **raw** request body, keyed by your webhook `secret`. The `sha256=` prefix IS part of the header value. |
| `X-Webhook-ID` | Unique delivery id (use for logging/idempotency) |
| `X-Webhook-Event` | Event type (currently only `statusChange`) |
| `User-Agent` | Always `Cursor-Agent-Webhook/1.0` |

Verification (verbatim from docs — compute and compare the **prefixed** value):
```go
// Go translation of the documented JS/Python verifier
mac := hmac.New(sha256.New, []byte(secret))
mac.Write(rawBody)                              // RAW body, before JSON parsing
expected := "sha256=" + hex.EncodeToString(mac.Sum(nil))
ok := hmac.Equal([]byte(expected), []byte(headerSignature))
```
**Trigger:** webhooks fire **only on `statusChange`, specifically when the agent reaches `ERROR` or `FINISHED`** (not on every transition). Some payload fields are optional (present only when available). Webhooks may be **retried** on non-2xx; return `2xx` quickly and store the raw payload. **[CONFIRMED verbatim from cloud-agent/api/webhooks.md]**

---

# PART 4 — Cursor CLI (`cursor-agent`) — headless local driver

Easiest to drive from Go (`os/exec` + NDJSON). All flags/JSON below are **[CONFIRMED]** verbatim from raw markdown.

## 4.1 Install & auth
```bash
curl https://cursor.com/install -fsS | bash          # → `cursor-agent`
# Windows: irm 'https://cursor.com/install?win32=true' | iex
cursor-agent login                                   # interactive
export CURSOR_API_KEY=your_api_key                   # headless/CI
cursor-agent --api-key "$CURSOR_API_KEY" -p "your prompt"
```
Precedence: `--api-key` > `CURSOR_API_KEY` > stored login. **[CONFIRMED]**

## 4.2 Global flags (complete, verbatim) — [CONFIRMED]
| Option | Description | Default |
|---|---|---|
| `-v, --version` | Output the version number | — |
| `--api-key <key>` | API key (also `CURSOR_API_KEY` env) | — |
| `-H, --header <header>` | Add custom header `Name: Value` (repeatable) | — |
| `-p, --print` | Print responses (scripts/non-interactive). Has access to **all** tools incl. write & shell. | off |
| `--output-format <format>` | `text`\|`json`\|`stream-json` (only with `--print`) | `text` |
| `--stream-partial-output` | Stream text deltas (only with `--print` + `stream-json`) | off |
| `--resume [chatId]` | Resume a chat session | — |
| `--continue` | Continue previous session (alias `--resume=-1`) | — |
| `--model <model>` | Model to use | account default |
| `--mode <mode>` | `plan`\|`ask` (agent is default) | agent |
| `--plan` | Shorthand for `--mode=plan` | — |
| `--list-models` | List all available models | — |
| `-f, --force` | Force allow commands unless explicitly denied | off |
| `--yolo` | Alias for `--force` | off |
| `--sandbox <mode>` | `enabled`\|`disabled` | — |
| `--approve-mcps` | Auto-approve all MCP servers | off |
| `--trust` | Trust workspace without prompting (**headless only**) | off |
| `--workspace <path>` | Workspace directory | cwd |
| `--plugin-dir <path>` | Load local plugin dir (repeatable) | — |
| `--worktree` | Run in new Git worktree under `~/.cursor/worktrees` | off |
| `-h, --help` | Help | — |

Commands: `agent`(default), `login`, `logout`, `status`/`whoami`, `about`, `models`, `mcp`(+`login`/`list`/`list-tools`/`enable`/`disable`), `acp`(hidden, ACP server mode), `update`, `ls`, `resume`, `create-chat`, `generate-rule`/`rule`, `install-shell-integration`, `uninstall-shell-integration`, `help`. **[CONFIRMED]**

**Headless autonomy combo:** `-p -f --trust --output-format stream-json` (or `--yolo`). Note `--mode` values for the CLI are `plan`/`ask` (the SDK/REST use `plan`/`agent`).

## 4.3 Output formats — [CONFIRMED]
All require `--print`. Default `text`.
- **`text`** → only the final assistant message (after the last tool call). No tool/progress lines.
- **`json`** → single object at completion (text aggregated; no deltas/tool events). **On failure: non-zero exit, error to stderr, NO JSON emitted.** Shape:
```json
{ "type":"result","subtype":"success","is_error":false,"duration_ms":1234,"duration_api_ms":1234,
  "result":"<full assistant text>","session_id":"<uuid>","request_id":"<optional>" }
```
  (`duration_api_ms` currently == `duration_ms`; `request_id` may be omitted.)
- **`stream-json`** → NDJSON, one object per line, one line per *complete* assistant message between tool calls. Ends with a terminal `result` on success; on failure exits non-zero and the stream **may end without a terminal event**.

## 4.4 `stream-json` event schema (verbatim) — [CONFIRMED]
Discriminator `type` ∈ `system`(`subtype:"init"`), `user`, `assistant`, `tool_call`(`subtype:"started"|"completed"`), `result`(`subtype:"success"`). **`thinking` events are suppressed in print mode.** Unknown fields must be ignored (forward-compat). Every event carries `session_id`.

```json
{"type":"system","subtype":"init","apiKeySource":"env|flag|login","cwd":"/absolute/path","session_id":"<uuid>","model":"<model display name>","permissionMode":"default"}
{"type":"user","message":{"role":"user","content":[{"type":"text","text":"<prompt>"}]},"session_id":"<uuid>"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"<complete message text>"}]},"session_id":"<uuid>"}
{"type":"tool_call","subtype":"started","call_id":"<id>","tool_call":{"readToolCall":{"args":{"path":"file.txt"}}},"session_id":"<uuid>"}
{"type":"tool_call","subtype":"completed","call_id":"<id>","tool_call":{"readToolCall":{"args":{"path":"file.txt"},"result":{"success":{"content":"...","isEmpty":false,"exceededLimit":false,"totalLines":54,"totalChars":1254}}}},"session_id":"<uuid>"}
{"type":"result","subtype":"success","duration_ms":1234,"duration_api_ms":1234,"is_error":false,"result":"<full assistant text>","session_id":"<uuid>","request_id":"<optional>"}
```
**Tool-call inner shape is open-ended**, keyed by tool kind (verbatim):
- `readToolCall` — started `args:{path}`; completed `result.success:{content,isEmpty,exceededLimit,totalLines,totalChars}`.
- `writeToolCall` — started `args:{path,fileText,toolCallId}`; completed `result.success:{path,linesCreated,fileSize}`.
- **Other tools** may instead use `tool_call.function:{name,arguments}` (arguments is a JSON string).
Go: decode `tool_call` as `map[string]json.RawMessage`, dispatch on the single key (or detect `function`).

**`--stream-partial-output`** emits 3 kinds of `assistant` events; **only the first carries new text** (verbatim rule):
| `timestamp_ms` | `model_call_id` | meaning | action |
|---|---|---|---|
| present | absent | streaming delta w/ new text | **USE** (append `message.content[].text`) |
| present | present | buffered flush before a tool call (dup) | **SKIP** |
| absent | absent | final flush at end of turn (dup) | **SKIP** |

## 4.5 Sessions / stdin / cloud handoff — [CONFIRMED]
```bash
cursor-agent create-chat            # → e.g. "chat_abc123"
cursor-agent --resume="chat_abc123" -p "Continue the task" --output-format json
cursor-agent --continue -p "next"   # = --resume=-1
cursor-agent ls
cat file.py | cursor-agent -p "Review this code"     # stdin (infers print mode)
# Cloud handoff: prefix a prompt with `&` to push to a Cloud Agent (async).  [from overview]
```
`session_id` in stream-json == the resumable chat id.

## 4.6 Cancellation (CLI)
No in-band abort flag; cancel = kill the subprocess (SIGINT/SIGTERM via `exec.Cmd`). On failure modes, rely on the non-zero exit code (json/stream-json emit nothing well-formed on failure). **[CONFIRMED behavior; no graceful-cancel API documented]**

## 4.7 AFK loop (composed from confirmed primitives)
```bash
CHAT_ID=$(cursor-agent create-chat)
while read -r task; do
  cursor-agent --resume="$CHAT_ID" -p "$task" -f --trust --output-format stream-json \
    | jq -c 'select(.type=="result")'
done < tasks.txt
```
*(Each primitive is documented; the loop itself is assembled here.)*

---

# PART 5 — Cross-cutting

## 5.1 Auth model (all surfaces) — [CONFIRMED]
- One key concept: **user API key** (Dashboard → Integrations) or **service-account key** (Team settings; required for REST worker/fleet + `/v1/sub-tokens`; bills the team). Team-Admin keys not yet usable with the SDK.
- Env var `CURSOR_API_KEY` for SDK + CLI. REST = HTTP Basic (`-u KEY:`) or Bearer.

## 5.2 Status-enum cheat sheet (don't conflate)
| Context | Values |
|---|---|
| `/v1` agent object | `ACTIVE`, `ARCHIVED` |
| `/v1` run + stream `status`/`SDKStatusMessage` | `CREATING`,`RUNNING`,`FINISHED`,`ERROR`,`CANCELLED`,`EXPIRED` |
| SDK `Run.status` / `RunResult.status` | `running`,`finished`,`error`,`cancelled` (lowercase) |
| SDK `SDKAgentInfo.status` | `running`,`finished`,`error` |
| `/v0` agent/webhook `status` | e.g. `FINISHED` (uppercase, run-style) |

## 5.3 Error handling — [partial]
- **SDK:** exported `CursorSdkError` hierarchy (§1.15) — model these as Go error types. `AgentBusyError` ⇔ HTTP `409`.
- **REST:** standard HTTP codes with body **`{ "error": "<Reason>", "message": "<detail>" }`** (verbatim from `api.md`): `400` Bad Request, `401` "Invalid API key", `403` Forbidden, `404` Not Found, `429` "Rate limit exceeded. Please try again later.", `500` Internal Server Error. Cloud-Agents-specific: `409 agent_busy` / `409 agent_archived`, `410 stream_expired`. The SSE `error` event payload = `{ code, message }`. Implement exponential backoff on `429`. **[CONFIRMED]**
- **CLI:** `result.is_error` (json/stream-json) + non-zero exit; on hard failure no JSON is emitted. Error `subtype` strings beyond `success` not documented → **[VERIFY]**.

## 5.4 AFK / multi-turn recipes by surface
- **SDK (richest):** `Agent.create({cloud|local})` → loop `agent.send()` per turn, consume `run.stream()` or `run.wait()`; persist `agentId`, `Agent.resume()` across processes; recover from `AgentBusyError`. Plan→build via `mode`.
- **`/v1`:** `POST /v1/agents` → SSE `GET .../runs/{runId}/stream` (resume `Last-Event-ID`; fall back to `GET .../runs/{runId}` after `410`) → `POST .../runs` per follow-up → `cancel`/`archive`/`delete`. One active run per agent.
- **`/v0`:** `POST /v0/agents` (with `webhook`) → receive `statusChange` POST (verify HMAC) **or** poll `GET /v0/agents/{id}` → `POST .../followup` → `DELETE`.
- **CLI:** §4.7.

---

# PART 6 — Source index (all 2026-05-28)
| URL | Used for | Capture |
|---|---|---|
| cursor.com/docs/sdk/typescript.md | entire SDK API surface | **raw md, in full (CONFIRMED)** + 6 verbatim WebFetch passes (mutually consistent) |
| cursor.com/blog/typescript-sdk ; cursor.com/changelog/sdk-release | release 2026-04-29, beta, pricing, cookbook, "more languages" plan | verbatim snippets |
| cursor.com/docs/api.md (APIs Overview table) | confirms official **Python SDK** + TS SDK (both "All users"); rate limits; error bodies | **raw md (CONFIRMED)** |
| npmjs.com/package/@cursor/sdk | package name/install | search snippet |
| cursor.com/docs/cloud-agent/api/endpoints.md | `/v1` endpoints, bodies, responses, SSE, enums | **raw md head + 5 verbatim WebFetch passes (CONFIRMED)** |
| cursor.com/docs/api.md | base URL + Basic/Bearer auth (verbatim curl) | **raw md (CONFIRMED)** |
| cursor.com/docs/cloud-agent/api/webhooks.md (= background-agent/api/webhooks.md) | webhook payload + headers + HMAC | **raw md (CONFIRMED)** |
| cursor.com/docs/cli/reference/parameters.md | CLI flags + commands | **raw md (CONFIRMED)** |
| cursor.com/docs/cli/reference/output-format.md | CLI text/json/stream-json + partial-output rules | **raw md (CONFIRMED)** |
| cursor.com/docs/cli/overview.md ; cli/using.md | install/auth/sessions/cloud-handoff | **raw md (CONFIRMED)** |

---

# PART 7 — Remaining uncertainties (re-check before freezing Go code)
1. **SDK `ToolCall` per-tool field shapes** — explicitly **not stable / internal-facing** per the docs; do NOT model field-by-field. Treat `args`/`result`/`input` as `json.RawMessage`, branch on `name`. (RESOLVED as "intentionally opaque".)
2. **Python SDK specifics** — package name, sync/async client class names, method names at `cursor.com/docs/sdk/python.md` (not transcribed). It exists and is GA-for-all-users; mirror the TS surface until confirmed. **[VERIFY]**
3. **`/v0` launch-body field names** (`source`/`target`) vs `/v1` (`repos[]`/`autoCreatePR`) — webhook payload confirms `/v0` `source`/`target`; the `/v0` `POST` body field table itself was not transcribed. **Prefer `/v1` (fully confirmed).** **[VERIFY for `/v0` only]**
4. **`GET /v0/agents/{id}/conversation`** response shape — not transcribed. **[VERIFY]**
5. **CLI `result.subtype` error strings** beyond `success` — not documented (CLI emits no well-formed JSON on hard failure; rely on exit code). **[VERIFY]**
6. **Model id strings** (SDK + `/v0` + `/v1`) — query `…/models` / `Cursor.models.list()` at runtime; never hardcode. (Docs warn ids/params change.)
7. **Agent id separator** — `/v1` + SDK use `bc-<uuid>` (hyphen); `/v0` webhook payload shows `bc_abc123` (underscore). Accept both in a Go parser. **[both CONFIRMED from their respective pages]**
8. **No Go SDK** as of 2026-05-28 — **TypeScript and Python SDKs both ship; Go does not.** Re-check `cursor.com/changelog` before assuming a Go SDK appears.

## RESOLVED since first draft (now CONFIRMED verbatim)
- REST auth: HTTP **Basic (`-u KEY:`) primary**, Bearer also accepted (`api.md`).
- Webhook signature: `X-Webhook-Signature: sha256=<hexHMAC-SHA256(secret, rawBody)>` — **prefix included** (`webhooks.md`).
- Webhook trigger: `statusChange` only, on `ERROR`/`FINISHED`.
- REST error bodies: `{ "error": "<Reason>", "message": "<detail>" }` for 400/401/403/404/429/500; 429 also documented for Cloud Agents API (`api.md`).
- Python SDK exists (official, all users).
- SDK `RunGitInfo`, `ShellConversationTurn`, `ShellCommand`, `ShellOutput`, `AgentBusyError{code,status,isRetryable}`, `CursorSdkError.isRetryable`, `cloud.env` pool/machine semantics — all confirmed (`sdk/typescript.md`).
