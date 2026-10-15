# Cursor CLI (`cursor-agent`) — Canonical AFK / Headless Reference

> Scope: complete reference for the official Cursor command-line agent (`cursor-agent`), focused on **away-from-keyboard / non-interactive / fully automated** usage, intended to ground a Go reimplementation that shells out to the binary.
>
> **⚠️ Single most important rule for the implementer:** the CLI is in active beta and changes frequently. The authoritative ground truth is `cursor-agent --help` (and `cursor-agent help <command>`) run against the **exact binary version** your Go program will invoke. Snapshot that output into your repo at build/pin time and diff it on upgrades. Everything below is accurate to the docs as of 2026-05-28 but treat it as a starting map, not a frozen contract.
>
> Research date: **2026-05-28**. All claims are drawn from official Cursor sources (`cursor.com/docs/cli/*`, `cursor.com/cli`, `cursor.com/blog/cli`, `cursor.com/changelog/*`). Where a fact could not be confirmed from an official page (several official pages intermittently returned HTTP 404 to the fetcher during research, or were behind a challenge), it is marked **UNCONFIRMED** with the reason. Do not treat UNCONFIRMED items as verified API.
>
> Binary name note: As of the **Jan 8, 2026 CLI release**, the primary entrypoint is **`agent`**, with **`cursor-agent`** kept as a backward-compatible alias. Both name the same executable. This doc uses `cursor-agent` throughout for unambiguous grep-ability; substitute `agent` freely. (Source: `cursor.com/changelog/cli-jan-08-2026`, accessed 2026-05-28.)

---

## 0. Source map (official pages used)

| Topic | URL | Status when fetched 2026-05-28 |
|---|---|---|
| Overview | `https://cursor.com/docs/cli/overview` | OK |
| Installation | `https://cursor.com/docs/cli/installation` | OK |
| Headless usage | `https://cursor.com/docs/cli/headless` | OK |
| Parameters reference | `https://cursor.com/docs/cli/reference/parameters` | OK |
| Output format reference | `https://cursor.com/docs/cli/reference/output-format` | OK |
| Authentication reference | `https://cursor.com/docs/cli/reference/authentication` | OK |
| Permissions reference | `https://cursor.com/docs/cli/reference/permissions` | OK (verbatim JSON captured) |
| Configuration reference | `https://cursor.com/docs/cli/reference/configuration` | OK |
| Using agent in CLI | `https://cursor.com/docs/cli/using` | OK |
| Shell mode | `https://cursor.com/docs/cli/shell-mode` | OK |
| MCP (CLI) | `https://cursor.com/docs/cli/using/mcp` | Partial |
| GitHub Actions | `https://cursor.com/docs/cli/github-actions` | OK (verbatim YAML captured) |
| Launch blog | `https://cursor.com/blog/cli` | OK (published 2025-08-07) |
| CLI changelog (Jan 16 2026) | `https://cursor.com/changelog/cli-jan-16-2026` | OK |
| CLI changelog (Jan 08 2026) | `https://cursor.com/changelog/cli-jan-08-2026` | OK |
| CLI landing | `https://cursor.com/cli` | OK |
| Models | `https://cursor.com/docs/models` | OK |

Note: the `docs.cursor.com/en/...` mirror 308-redirects to `cursor.com/docs` (not deep-linkable); use `cursor.com/docs/...` directly. The `/reference/github-actions` path is wrong — the live page is `cursor.com/docs/cli/github-actions`.

The docs are also mirrored at `https://docs.cursor.com/en/cli/...` (same content).

---

## 1. Installation, version pinning, version check

### 1.1 Install script (macOS / Linux / WSL)

```bash
curl https://cursor.com/install -fsS | bash
```

Source: `cursor.com/docs/cli/installation`, `cursor.com/docs/cli/overview` (accessed 2026-05-28).

### 1.2 Install (Windows PowerShell, native)

```powershell
irm 'https://cursor.com/install?win32=true' | iex
```

Source: `cursor.com/docs/cli/installation` (accessed 2026-05-28).

### 1.3 Supported platforms

macOS, Linux, Windows (WSL), Windows (native PowerShell). Source: `cursor.com/docs/cli/overview` and `/installation` (accessed 2026-05-28).

### 1.4 Install location and PATH

- The installation page documents the install dir as `~/.local/bin`. **However**, official GitHub Actions examples add **`$HOME/.cursor/bin`** to `$GITHUB_PATH` instead. Both bin dirs appear in official material; the dir actually used is **version-dependent**.
- **Recommendation for a Go wrapper:** do not hardcode the binary path. After install, ensure **both** `~/.local/bin` and `~/.cursor/bin` are on `PATH`, then resolve the executable with `exec.LookPath("cursor-agent")` (fall back to `"agent"`). Snapshot the resolved absolute path.
- PATH setup shown by docs:
  ```bash
  # bash
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
  # zsh
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
  ```
- **Windows (native):** install is via PowerShell (`irm 'https://cursor.com/install?win32=true' | iex`). The executable name and on-disk location on native Windows are **UNCONFIRMED** — verify with `where.exe agent` / `where.exe cursor-agent` and inspect the install dir before relying on a path. The `agent`↔`cursor-agent` alias relationship is documented for macOS/Linux; assume but verify it on native Windows.

Source: `cursor.com/docs/cli/installation`, `cursor.com/docs/cli/github-actions` (accessed 2026-05-28).

### 1.5 npm install

**Not documented officially.** The official installation page documents only the `curl | bash` script and the PowerShell `irm | iex` script. It explicitly does not list an npm install method. There are third-party npm packages (e.g. `@nothumanwork/cursor-agents-sdk`, the unofficial PyPI `cursor-cli`) but these are **not** the official CLI. **For a Go reimplementation that shells out, depend on the `curl` installer, not npm.** (Status: npm path UNCONFIRMED / not official.)

### 1.6 Version check

```bash
cursor-agent --version        # or: agent --version
cursor-agent -v
cursor-agent about            # version, system, and account info
```

Source: parameters reference (`-v, --version`: "Output the version number"), commands table (`about`: "Display version, system, and account info"), installation page (`agent --version`). Accessed 2026-05-28.

### 1.7 Update

```bash
cursor-agent update           # update to latest
```

The CLI **auto-updates by default**; `update` forces a manual update. Source: installation page + parameters/commands table (accessed 2026-05-28).

### 1.8 Version pinning

**No official mechanism documented.** The installer and `update` always target latest; there is no documented `--version=X.Y.Z` install flag or pin file. For reproducible CI, the practical approach is to cache the installed binary artifact yourself after a known-good install. (Status: pinning UNCONFIRMED / appears unsupported.)

---

## 2. Authentication (headless / CI)

Two mechanisms: **API key** (preferred for headless/CI) and **interactive login** (stores credentials on disk).

### 2.1 API key — `CURSOR_API_KEY`

- Create a key in the Cursor dashboard (Dashboard → Integrations / API Keys). Keys are prefixed `cursor_...`. The "Cursor User API Key" grants access to the **headless Cursor Agent CLI** and the **Background Agent API**.
- Headless / CI usage:
  ```bash
  export CURSOR_API_KEY=cursor_your_key_here
  cursor-agent -p "Analyze this code"
  ```
- The key may also be passed as a flag (`--api-key <key>`), but the env var is recommended so the key never appears in process args / shell history.
- CI guidance from Cursor: store the key in the platform secret store (GitHub repo/environment secrets), scope it to the job that needs it, rotate on a schedule, and revoke-then-rotate on leak.

Sources: `cursor.com/docs/cli/reference/authentication` (linked), `cursor.com/docs/cli/headless`, `cursor.com/docs/api` (User API Key powers headless CLI + Background Agent API). Accessed 2026-05-28.

> **Scopes:** Official docs describe the User API Key as a single key granting access to the headless CLI and Background Agent API. A granular per-scope/per-tool token model for the CLI is **not documented** — treat it as a single broad-scope user key. (Status: fine-grained scopes UNCONFIRMED.)

### 2.2 Interactive login (stores credentials)

```bash
cursor-agent login      # authenticate with Cursor (opens browser / device flow)
cursor-agent logout     # sign out and clear stored authentication
cursor-agent status     # check authentication status   (alias: whoami)
```

- `login` authenticates with Cursor; after success, subsequent runs don't need `CURSOR_API_KEY`.
- `logout` clears stored auth.
- `status` / `whoami` reports current auth status.
- In `stream-json` output, the `system/init` event reports the auth source via `apiKeySource`: `"env"` | `"flag"` | `"login"` (see §5).

Other documented auth/troubleshooting flags (from the authentication page): `--api-key <key>`, `--insecure` (skip SSL verification), `--endpoint <url>` (custom API endpoint).

Credentials storage path: docs reference a `~/.cursor` config area (shell integration installs to `~/.zshrc`; worktrees under `~/.cursor/worktrees`; MCP config in `.cursor/mcp.json`; CLI config in `~/.cursor/cli-config.json`). The exact **credential** file path after `login` is **not explicitly documented** (it is not `cli-config.json`, which holds permissions/editor prefs). (Status: exact credential file path UNCONFIRMED.) For containers/CI, prefer `CURSOR_API_KEY` so no on-disk credential is needed.

Sources: parameters/commands table; authentication reference (linked). Accessed 2026-05-28.

### 2.3 Auth precedence

There are three credential sources, reported by the `apiKeySource` field as one of `"flag"` | `"env"` | `"login"` (= the `--api-key` flag, the `CURSOR_API_KEY` env var, or stored `login` credentials). **The relative precedence when more than one is present is NOT documented** — flag > env > login is the conventional ordering and a reasonable assumption, but treat it as **inferred/UNCONFIRMED**. To avoid the question entirely in a wrapper, supply exactly one source. For unattended runs, **prefer `CURSOR_API_KEY`** (no interactive prompt, no browser, no on-disk credential).

---

## 3. Subcommands (complete list)

From the official parameters reference (`cursor.com/docs/cli/reference/parameters`, accessed 2026-05-28). Invoke as `cursor-agent <command>`.

| Command | Aliases | Description |
|---|---|---|
| `agent` | (default) | Start in agent mode (the default when no command is given). |
| `login` | | Authenticate with Cursor. |
| `logout` | | Sign out and clear stored authentication. |
| `status` | `whoami` | Check authentication status. |
| `about` | | Display version, system, and account info. |
| `models` | | List all available models. |
| `mcp` | | Manage MCP servers (has subcommands, see §7). |
| `acp` | | Start ACP (Agent Client Protocol) server mode. *Advanced, hidden command.* |
| `update` | | Update Cursor Agent to the latest version. |
| `ls` | | List previous chat sessions. |
| `resume` | | Resume the latest chat session. |
| `create-chat` | | Create a new empty chat and return its ID. |
| `generate-rule` | `rule` | Generate a new Cursor rule interactively. |
| `install-shell-integration` | | Install shell integration to `~/.zshrc`. |
| `uninstall-shell-integration` | | Remove shell integration from `~/.zshrc`. |
| `help [command]` | | Display help for a command. |

Positional argument for the default `agent` command:
- **`prompt`** — initial prompt for the agent (optional).

**Most relevant to AFK / automation:** the default `agent` run with `-p`, plus `create-chat` (mint a session id), `ls` (enumerate sessions), `resume` (resume latest), and `--resume <id>` (resume a specific one). `acp` is for editor/IDE integration over the Agent Client Protocol, not typical scripting.

---

## 4. Flags / options (complete reference)

Global options usable with the default `agent` run (from `cursor.com/docs/cli/reference/parameters`, accessed 2026-05-28). Verbatim descriptions are quoted.

| Short | Long | Argument | Default | Description |
|---|---|---|---|---|
| `-v` | `--version` | — | — | "Output the version number" |
| | `--api-key` | `<key>` | — | "API key for authentication (can also use `CURSOR_API_KEY` env var)" |
| `-H` | `--header` | `<header>` | — | "Add custom header to agent requests (format: `Name: Value`, can be used multiple times)" |
| `-p` | `--print` | — | — | "Print responses to console (for scripts or non-interactive use). Has access to all tools, including write and shell." |
| | `--output-format` | `<format>` | `text` | "Output format (only works with `--print`): `text`, `json`, or `stream-json`" |
| | `--stream-partial-output` | — | — | "Stream partial output as individual text deltas" (only with `--print` + `stream-json`) |
| | `--resume` | `[chatId]` | — | "Resume a chat session" (optional chat id; see §6) |
| | `--continue` | — | — | "Continue the previous session (alias for `--resume=-1`)" |
| | `--model` | `<model>` | (account default) | "Model to use" |
| | `--mode` | `<mode>` | `agent` | "Set agent mode: `plan` or `ask` (agent is the default when no mode is specified)" |
| | `--plan` | — | — | "Start in plan mode (shorthand for `--mode=plan`)" |
| | `--list-models` | — | — | "List all available models" |
| `-f` | `--force` | — | — | "Force allow commands unless explicitly denied" |
| | `--yolo` | — | — | "Alias for `--force`" |
| | `--sandbox` | `<mode>` | — | "Set sandbox mode: `enabled` or `disabled`" |
| | `--approve-mcps` | — | — | "Automatically approve all MCP servers" |
| | `--trust` | — | — | "Trust the workspace without prompting (headless mode only)" |
| | `--workspace` | `<path>` | (cwd) | "Workspace directory to use" |
| | `--plugin-dir` | `<path>` | — | "Load a local plugin directory (can be specified multiple times)" |
| | `--worktree` | — | — | "Run in a new Git worktree under `~/.cursor/worktrees`" |
| | `--insecure` | — | — | Skip SSL certificate verification (dev/troubleshooting; from authentication docs). |
| | `--endpoint` | `<url>` | — | Use a custom API endpoint (dev/troubleshooting; from authentication docs). |
| `-h` | `--help` | — | — | "Display help for command" |

> `--insecure` and `--endpoint` are documented on the authentication page as troubleshooting flags, not in the main parameters table. They are not needed for normal headless use; `--endpoint` is for self-hosted/proxy gateways and `--insecure` for cert issues. (Source: `cursor.com/docs/cli/reference/authentication`, accessed 2026-05-28.)

### 4.1 Notes per flag for AFK use

- **`-p, --print`** — the master switch for non-interactive mode. In print mode the agent has full tool access (write + shell). Print mode is also **inferred** when stdout is not a TTY or stdin is piped (per output-format docs). Always pass it explicitly in scripts to be safe.
- **`--output-format`** — only honored together with `--print`. Values: `text`, `json`, `stream-json`. **Default is `text`** when you pass `-p`/`--print` explicitly (which your wrapper always will) — this is the authoritative parameters-reference default. (A separate claim that the default is `stream-json` applies only to the SDK / *inferred* print-mode path, a different code path; it does not contradict the `text` default for explicit `-p`.) Regardless, **always pass `--output-format` explicitly** so behavior is version-independent. See §5 for exact schemas.
- **`--stream-partial-output`** — emits incremental text deltas as separate `assistant` events; only with `--print --output-format stream-json`. Without it, `assistant` events arrive as larger chunks/whole messages.
- **`--model <model>`** — see §10 for model identifiers. If omitted, uses the account/workspace default (or "Auto").
- **`-f, --force` / `--yolo`** — **the key unattended-autonomy flag.** Without it, in print mode file writes and commands are *proposed but not applied*. With it, the agent may run commands and apply edits unless explicitly denied by the permission config (§6). For batch/AFK runs you almost always want `--force`.
- **`--sandbox enabled|disabled`** — controls whether tool/command execution runs inside Cursor's sandbox. `enabled` = run inside the controlled sandbox (network egress etc. gated); `disabled` = run unsandboxed. See §6.
- **`--approve-mcps`** — auto-approves all configured MCP servers so they don't block on interactive trust prompts (essential for headless MCP use; see §7).
- **`--trust`** — *(headless only)* trust the workspace without the interactive "do you trust this folder" prompt. Needed for first-run-in-a-fresh-checkout CI.
- **`--workspace <path>`** — sets the working/workspace directory. This is the documented analog of a `--cwd`. **There is no `--cwd` flag in the official reference** — use `--workspace`. Note the agent's effective working directory is the **process cwd** unless `--workspace` overrides it; the `stream-json` `system/init` event echoes the resolved `cwd`. From Go, either set `exec.Cmd.Dir` (process cwd) or pass `--workspace`; both work, and `--workspace` wins if both are set.
- **`--resume [chatId]` / `--continue`** — session continuation; see §6.
- **`--worktree`** — runs the agent in a fresh git worktree under `~/.cursor/worktrees` (isolation for parallel agents).
- **`--plugin-dir <path>`** — load local plugin dir(s), repeatable.
- **`-H, --header`** — inject custom HTTP headers on agent requests, repeatable (proxy/gateway scenarios).

### 4.2 Flags that DO NOT exist in the official reference (do not invent)

The following appeared in our search hypotheses but are **NOT** in the official parameters reference and should be treated as **non-existent** unless a future doc confirms them: `--cwd`, `--output`, `--rules`, `--mcp-config`, `--fullscreen`, `--with-diffs`, `--background`, `-b`, `-a`, `--editor`, `--max-mode` (the `--max-mode` flag was mentioned by one overview fetch but is **not** in the parameters reference — treat as **UNCONFIRMED**). Rules and MCP config are supplied via files in `.cursor/`, not flags (see §7, §8).

---

## 5. Output formats — exact schemas

Source: `cursor.com/docs/cli/reference/output-format` (accessed 2026-05-28). All JSON below is reproduced verbatim from the official page.

### 5.1 `text` (default)

Plain text: only the final assistant message, no intermediate progress or tool summaries.

Example:
```
The command to move this branch onto main is `git rebase --onto main HEAD~3`.
```

### 5.2 `json`

A single JSON object printed (followed by a newline) when the run completes. Deltas and tool events are not emitted; text is aggregated into `result`.

```json
{
  "type": "result",
  "subtype": "success",
  "is_error": false,
  "duration_ms": 1234,
  "duration_api_ms": 1234,
  "result": "<full assistant text>",
  "session_id": "<uuid>",
  "request_id": "<optional request id>"
}
```

Field notes:
- `type`: always `"result"` for this format.
- `subtype`: `"success"` on success (error subtypes exist for failures — see §9).
- `is_error`: boolean.
- `duration_ms` / `duration_api_ms`: integers (ms).
- `result`: full aggregated assistant text.
- `session_id`: UUID — capture this to resume (§6).
- `request_id`: optional request id (may be absent).

Parsing example:
```bash
cursor-agent -p --output-format json "Summarize the repo" | jq -r '.result'
```

### 5.3 `stream-json` (NDJSON)

Newline-delimited JSON; one JSON object per line, one per real-time event. Event order in a typical run: `system/init` → `user` → (`assistant` / `tool_call` ...) → `result`.

**Field-additions caveat (official):** new fields may be added in a backward-compatible way; **consumers must ignore unknown fields.** In the public beta the SDK additionally emits these `type` values: `system`, `user`, `assistant`, `tool_call`, `thinking`, `status`, `request`, and `task`.

#### system / init
```json
{
  "type": "system",
  "subtype": "init",
  "apiKeySource": "env|flag|login",
  "cwd": "/absolute/path",
  "session_id": "<uuid>",
  "model": "<model display name>",
  "permissionMode": "default"
}
```

#### user
```json
{
  "type": "user",
  "message": {
    "role": "user",
    "content": [{ "type": "text", "text": "<prompt>" }]
  },
  "session_id": "<uuid>"
}
```

#### assistant
```json
{
  "type": "assistant",
  "message": {
    "role": "assistant",
    "content": [{ "type": "text", "text": "<complete message text>" }]
  },
  "session_id": "<uuid>"
}
```
With `--stream-partial-output`, multiple `assistant` events carry incremental `text` deltas that must be concatenated. Without it, `assistant` events carry larger/whole chunks.

#### tool_call — started
```json
{
  "type": "tool_call",
  "subtype": "started",
  "call_id": "<string id>",
  "tool_call": {
    "readToolCall": {
      "args": { "path": "file.txt" }
    }
  },
  "session_id": "<uuid>"
}
```

#### tool_call — completed (read)
```json
{
  "type": "tool_call",
  "subtype": "completed",
  "call_id": "<string id>",
  "tool_call": {
    "readToolCall": {
      "args": { "path": "file.txt" },
      "result": {
        "success": {
          "content": "file contents...",
          "isEmpty": false,
          "exceededLimit": false,
          "totalLines": 54,
          "totalChars": 1254
        }
      }
    }
  },
  "session_id": "<uuid>"
}
```

#### tool_call — completed (write)
```json
{
  "type": "tool_call",
  "subtype": "completed",
  "call_id": "<string id>",
  "tool_call": {
    "writeToolCall": {
      "args": {
        "path": "summary.txt",
        "fileText": "# README Summary\n\nThis project contains...",
        "toolCallId": "<string id>"
      },
      "result": {
        "success": {
          "path": "/Users/user/project/summary.txt",
          "linesCreated": 19,
          "fileSize": 942
        }
      }
    }
  },
  "session_id": "<uuid>"
}
```

#### result (terminal)
```json
{
  "type": "result",
  "subtype": "success",
  "duration_ms": 1234,
  "duration_api_ms": 1234,
  "is_error": false,
  "result": "<full assistant text>",
  "session_id": "<uuid>",
  "request_id": "<optional request id>"
}
```

#### Full verbatim stream-json transcript example (from official docs)
```json
{"type":"system","subtype":"init","apiKeySource":"login","cwd":"/Users/user/project","session_id":"c6b62c6f-7ead-4fd6-9922-e952131177ff","model":"Claude 4 Sonnet","permissionMode":"default"}
{"type":"user","message":{"role":"user","content":[{"type":"text","text":"Read README.md and create a summary"}]},"session_id":"c6b62c6f-7ead-4fd6-9922-e952131177ff"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"I'll read the README.md file"}]},"session_id":"c6b62c6f-7ead-4fd6-9922-e952131177ff"}
{"type":"tool_call","subtype":"started","call_id":"toolu_vrtx_01NnjaR886UcE8whekg2MGJd","tool_call":{"readToolCall":{"args":{"path":"README.md"}}},"session_id":"c6b62c6f-7ead-4fd6-9922-e952131177ff"}
{"type":"tool_call","subtype":"completed","call_id":"toolu_vrtx_01NnjaR886UcE8whekg2MGJd","tool_call":{"readToolCall":{"args":{"path":"README.md"},"result":{"success":{"content":"# Project\n\nThis is a sample project...","isEmpty":false,"exceededLimit":false,"totalLines":54,"totalChars":1254}}}},"session_id":"c6b62c6f-7ead-4fd6-9922-e952131177ff"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Based on the README, I'll create a summary"}]},"session_id":"c6b62c6f-7ead-4fd6-9922-e952131177ff"}
{"type":"tool_call","subtype":"started","call_id":"toolu_vrtx_01Q3VHVnWFSKygaRPT7WDxrv","tool_call":{"writeToolCall":{"args":{"path":"summary.txt","fileText":"# README Summary\n\nThis project contains...","toolCallId":"toolu_vrtx_01Q3VHVnWFSKygaRPT7WDxrv"}}},"session_id":"c6b62c6f-7ead-4fd6-9922-e952131177ff"}
{"type":"tool_call","subtype":"completed","call_id":"toolu_vrtx_01Q3VHVnWFSKygaRPT7WDxrv","tool_call":{"writeToolCall":{"args":{"path":"summary.txt","fileText":"# README Summary\n\nThis project contains...","toolCallId":"toolu_vrtx_01Q3VHVnWFSKygaRPT7WDxrv"},"result":{"success":{"path":"/Users/user/project/summary.txt","linesCreated":19,"fileSize":942}}}},"session_id":"c6b62c6f-7ead-4fd6-9922-e952131177ff"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Done! I've created the summary in summary.txt"}]},"session_id":"c6b62c6f-7ead-4fd6-9922-e952131177ff"}
{"type":"result","subtype":"success","duration_ms":5234,"duration_api_ms":5234,"is_error":false,"result":"I'll read the README.md fileBased on the README, I'll create a summaryDone! I've created the summary in summary.txt","session_id":"c6b62c6f-7ead-4fd6-9922-e952131177ff","request_id":"10e11780-df2f-45dc-a1ff-4540af32e9c0"}
```

#### Parsing notes for a Go consumer
- Read NDJSON line-by-line; `json.Unmarshal` each line into a struct with `Type string` and decode the rest by `type`/`subtype`.
- `tool_call.tool_call` is a **map keyed by tool name** (`readToolCall`, `writeToolCall`, and presumably `shellToolCall`, `listToolCall`, etc.). Model it as `map[string]json.RawMessage` and switch on the single present key — do not hardcode an exhaustive enum (forward-compat).
- **The final answer is the `result` field** — use it directly. It aggregates assistant text **with NO separator** between segments (the official example literally shows `"...README.md fileBased on the README..."` — no space). **Do NOT reconstruct the answer by concatenating `assistant` events, and do NOT expect whitespace between concatenated segments.** Read `result` from the terminal `result` event (stream-json) or from the single `json` object. This is the single most likely parsing bug — get it right once here.
- `session_id` is on every event; capture it from `system/init` for resume.
- The `--stream-partial-output` event shapes have multiple undocumented forms (acknowledged in the Cursor forum); be defensive when parsing partial assistant events.

---

## 6. Permissions / approval / autonomy (unattended)

Source: `cursor.com/docs/cli/reference/permissions` (JSON captured verbatim), `cursor.com/docs/cli/reference/configuration`, `cursor.com/docs/cli/shell-mode`, `cursor.com/blog/agent-sandboxing`, and the parameters reference. Accessed 2026-05-28.

### 6.1 The core autonomy levers

For a fully unattended run you typically combine:

```bash
export CURSOR_API_KEY=cursor_...
cursor-agent -p --force "<task>"
# add for fresh checkouts / first run:
cursor-agent -p --force --trust "<task>"
# add if MCP servers are configured and must be used:
cursor-agent -p --force --approve-mcps "<task>"
```

- **`-p` / `--print`** grants full tool access (write + shell) in non-interactive mode.
- **`-f` / `--force` (alias `--yolo`)**: "Force allow commands unless explicitly denied." This is the auto-approve switch. Without it, edits/commands are proposed, not executed.
- **`--trust`**: bypasses the interactive workspace-trust prompt (headless only).
- **`--approve-mcps`**: auto-approves MCP servers (otherwise they block on an interactive trust step).
- **`--sandbox enabled|disabled`**: choose whether tools run inside the Cursor sandbox.

### 6.2 Permission config — CONFIRMED schema

Source: `cursor.com/docs/cli/reference/permissions` and `cursor.com/docs/cli/reference/configuration` (accessed 2026-05-28, JSON captured verbatim from multiple fetches).

**Config files (both optional):**
- Global: `~/.cursor/cli-config.json`
- Project: `<project>/.cursor/cli.json`

**Structure** — top-level `permissions` object with `allow` and `deny` string arrays:

```json
{
  "permissions": {
    "allow": [
      "Shell(ls)",
      "Shell(git)",
      "Read(src/**/*.ts)",
      "Write(package.json)",
      "WebFetch(docs.github.com)",
      "WebFetch(*.github.com)",
      "Mcp(datadog:*)"
    ],
    "deny": [
      "Shell(rm)",
      "Read(.env*)",
      "Write(**/*.key)",
      "WebFetch(malicious-site.com)"
    ]
  }
}
```

**Permission entry types (the five documented forms):**

| Form | Meaning |
|---|---|
| `Shell(commandBase)` | Shell command execution. Matches by the command's base name (first token); e.g. `Shell(git)` allows any `git` subcommand. The `command:args` form (e.g. `npm:test`, `curl:*`) matches command **and** arguments. |
| `Read(pathOrGlob)` | File/dir read access. |
| `Write(pathOrGlob)` | File/dir write access. **In print mode, `--force` is required for writes to actually apply** even if `Write(...)` is allowed. |
| `WebFetch(domainOrPattern)` | Web fetch by domain. Patterns: exact (`docs.github.com`), subdomain wildcard (`*.github.com`), universal (`*`). Without an allow entry, each fetch prompts for approval. |
| `Mcp(server:tool)` | MCP tool access via `server:tool` notation (e.g. `Mcp(datadog:*)`). |

**Rules:**
- **Deny rules take precedence over allow rules** (verbatim from docs). This is why `--force`/`--yolo` ("force allow commands unless explicitly denied") still respects the denylist — put hard guardrails (e.g. `Shell(rm)`, `Read(.env*)`, `Write(**/*.key)`) in `deny` and they hold even under `--force`.
- Glob wildcards supported in path/glob entries: `**`, `*`, `?`.
- Relative paths scope to the workspace; absolute paths target files outside the project.
- Known behavior (forum, 2026): the interactive "add to allowlist" action has at times written to the **global** `cli-config.json` rather than the project `cli.json` — when scripting, write the config file explicitly to the path you want rather than relying on the agent persisting it.

### 6.3 Sandbox & approval modes

- `stream-json` `system/init` reports `permissionMode` (observed value `"default"`). Full enum of `permissionMode` values is not documented (only `"default"` appears in official examples). (Status: full enum UNCONFIRMED.)
- Cursor's **agent sandboxing** (GA in Cursor 2.0; macOS/Linux/Windows): sandboxed tool calls run freely inside a controlled environment and only request approval when stepping outside it (most commonly network egress). With `--force`/`--yolo` that approval is auto-granted, subject to the denylist.
- Cursor UI Auto-Run modes ("Ask Every Time", "Auto-Run in Sandbox", "Run Everything (Unsandboxed)") map roughly to CLI flags: no `--force` ≈ propose/ask; `--force --sandbox enabled` ≈ auto-run in sandbox; `--force --sandbox disabled` ≈ run everything unsandboxed. (Status: mapping inferred; exact correspondence UNCONFIRMED.)

### 6.4 Recommended unattended invocation (safe default)

```bash
cursor-agent -p \
  --force \
  --trust \
  --sandbox enabled \
  --output-format stream-json \
  --model "<model>" \
  --workspace "$PWD" \
  "<task prompt>"
```

`--sandbox enabled` keeps execution contained while `--force` auto-approves in-sandbox actions. Drop to `--sandbox disabled` only when the task legitimately needs unrestricted host access.

---

## 7. MCP integration via the CLI

Source: parameters reference (mcp subcommands), `cursor.com/docs/cli/using/mcp`, Sep 2025 changelog. Accessed 2026-05-28.

### 7.1 `cursor-agent mcp` subcommands

| Subcommand | Argument | Description |
|---|---|---|
| `mcp login` | `<identifier>` | "Authenticate with an MCP server configured in `.cursor/mcp.json`" |
| `mcp list` | — | "List configured MCP servers and their status" |
| `mcp list-tools` | `<identifier>` | "List available tools and their argument names for a specific MCP" |
| `mcp enable` | `<identifier>` | "Enable an MCP server" |
| `mcp disable` | `<identifier>` | "Disable an MCP server" |

### 7.2 Config file

- MCP servers are defined in **`.cursor/mcp.json`** (project-level) — JSON files living under `.cursor`. As of the Sep 2025 changelog, MCP definitions/tools live as JSON files in `.cursor`, and agents discover/load them only when needed.
- Typical MCP config shape (Cursor's standard, same as the editor's `mcp.json`):
  ```json
  {
    "mcpServers": {
      "my-server": {
        "command": "npx",
        "args": ["-y", "@scope/mcp-server"],
        "env": { "API_TOKEN": "..." }
      }
    }
  }
  ```
  (The `mcpServers` object with `command`/`args`/`env` is Cursor's documented MCP format; the exact verbatim CLI example block could not be re-fetched from the using/mcp page during this run — treat the shape as standard-Cursor-MCP, **schema confirmed for editor, CLI example UNCONFIRMED verbatim**.)
- September 2025 changelog additions: **MCP Resources** support and **interpolated variables** in MCP config.

### 7.3 Headless MCP

- Use **`--approve-mcps`** to auto-approve all MCP servers in non-interactive runs (otherwise the agent blocks on an interactive trust prompt). This addresses the known "bypass interactive trust in headless" pain point.
- `cursor-agent mcp login <id>` may be required once to authenticate OAuth-style MCP servers before headless runs.

### 7.4 No `--mcp-config` flag

There is **no** `--mcp-config <path>` flag in the official reference; MCP is configured via `.cursor/mcp.json`, not a CLI flag. (Contrast with some other agent CLIs.)

---

## 8. Rules / project instructions

- Cursor rules apply to CLI runs the same way they apply in the editor: files under **`.cursor/rules/`** (`.mdc` files) and an **`AGENTS.md`** at the repo root are picked up automatically.
- Generate a rule interactively: `cursor-agent generate-rule` (alias `rule`).
- **No `--rules` flag** exists in the official parameters reference; rules are file-based and auto-discovered from the workspace. As of the Jan 8 2026 release there is a `/rules` interactive slash command (create/edit rules) and a `/commands` slash command, but no rules flag.

---

## 8b. CLI configuration file (`cli.json` / `cli-config.json`)

Source: `cursor.com/docs/cli/reference/configuration` (accessed 2026-05-28, keys captured verbatim).

- **Global config:** `~/.cursor/cli-config.json` (Windows: `$env:USERPROFILE\.cursor\cli-config.json`)
- **Project config:** `<project>/.cursor/cli.json` (**permissions only**)
- **Path overrides (env):** `CURSOR_CONFIG_DIR`, `XDG_CONFIG_HOME`

Documented keys:

| Key | Type | Default | Purpose |
|---|---|---|---|
| `version` | number | `1` (required) | Config schema version. |
| `editor.vimMode` | boolean | `false` | Vim keybindings toggle. |
| `permissions.allow` | string[] | — (required) | Permitted operations (see §6.2). |
| `permissions.deny` | string[] | — (required) | Forbidden operations (see §6.2). |
| `model` | object | — (optional) | Selected model configuration (CLI-managed; set via `/model`). |
| `hasChangedDefaultModel` | boolean | — (optional) | CLI-managed flag: user changed their default model. |
| `network.useHttp1ForAgent` | boolean | `false` | Use HTTP/1.1 instead of HTTP/2 for agent connections (proxy/gateway compatibility). |
| `attribution.attributeCommitsToAgent` | boolean | `true` | Add "Made with Cursor" trailer to commits the agent makes. |
| `attribution.attributePRsToAgent` | boolean | `true` | Add "Made with Cursor" footer to PRs the agent opens. |

Full example config (verbatim from docs):
```json
{
  "version": 1,
  "editor": { "vimMode": false },
  "permissions": { "allow": ["Shell(ls)"], "deny": [] },
  "network": { "useHttp1ForAgent": false },
  "attribution": {
    "attributeCommitsToAgent": true,
    "attributePRsToAgent": true
  }
}
```

The configuration page does **not** list `sandbox` or `approvalMode` as keys (community references mention them but they are absent from the official reference — treat as UNCONFIRMED). For a Go wrapper: set `permissions` (autonomy guardrails) and, if needed, `attribution`/`network` in the config file; set model/sandbox/force/mode via **CLI flags**. Note `attribution.*` defaults to `true` — if you do NOT want "Made with Cursor" trailers on automated commits/PRs, set both to `false` in CI.

---

## 9. Non-interactive invocation patterns

All examples from `cursor.com/docs/cli/headless` (accessed 2026-05-28) unless noted.

### 9.1 Single-shot prompt
```bash
cursor-agent -p "What does this codebase do?"
cursor-agent -p --force "Refactor this code to use modern ES6+ syntax"
```

### 9.2 Prompt via stdin (piping)
Print mode is inferred when stdin is piped:
```bash
echo "Add JSDoc comments to src/index.js" | cursor-agent -p
cat task.txt | cursor-agent -p --force
```

### 9.3 Capturing structured output
```bash
# single JSON object
cursor-agent -p --output-format json "Analyze this code" | jq -r '.result'

# NDJSON stream + jq per-event
cursor-agent -p --force --output-format stream-json --stream-partial-output \
  "Analyze this project structure" | while IFS= read -r line; do
    type=$(echo "$line" | jq -r '.type // empty')
    # ... handle system/user/assistant/tool_call/result
  done
```

### 9.4 Model + format combined
```bash
cursor-agent -p -m gpt-5 "find and fix performance issues"
cursor-agent -p --force --output-format text "Review the recent code changes"
cursor-agent -p --force --output-format json "Analyze this project structure"
```

### 9.5 Batch processing
```bash
find src/ -name "*.js" | while read file; do
  cursor-agent -p --force "Add comprehensive JSDoc comments to $file"
done
```

### 9.6 File / image references in the prompt
```bash
cursor-agent -p "Analyze this image and describe what you see: ./screenshot.png"
cursor-agent -p "Compare these two images and identify differences: ./before.png ./after.png"
cursor-agent -p --output-format json "Describe this image: $IMAGE_PATH" | jq -r '.result'
for image in images/*.png; do
  cursor-agent -p --output-format text "Describe this image: $image" > "${image%.png}.description.txt"
done
```

### 9.7 Session lifecycle (resume by ID)

```bash
# 1. mint a fresh session id up front (useful for orchestration)
SID=$(cursor-agent create-chat)

# 2. run against it, capturing session id from json output
SID=$(cursor-agent -p --output-format json "Start the task" | jq -r '.session_id')

# 3. resume that exact session later
cursor-agent -p --force --resume="$SID" "Continue: now add tests"

# convenience: resume the most recent session
cursor-agent resume
cursor-agent -p --continue "keep going"     # --continue == --resume=-1

# enumerate prior sessions
cursor-agent ls
```

- `--resume [chatId]` takes a UUID chat id (e.g. `67e321cf-8e58-2233-96ad-7a2abc1fd53c`). When you interrupt an interactive run with Ctrl-C, the CLI prints the chat id you can resume with.
- `--continue` is exactly `--resume=-1` (most recent).
- `create-chat` returns a new empty chat id you can drive non-interactively.
- `ls` lists previous sessions; community notes mention a `--cwd`-style narrowing to one project for `ls`, but this is **not** a documented global flag — verify on the target version.

Sources: parameters reference, `cursor.com/docs/cli/using`, community/forum (UUID format examples). Accessed 2026-05-28.

### 9.8 CI / GitHub Actions (verbatim official example)
Source: `cursor.com/docs/cli/github-actions` (accessed 2026-05-28). Reproduced verbatim:

```yaml
name: Cursor Agent
on:
  workflow_dispatch:
    inputs:
      prompt:
        description: 'Prompt for Cursor Agent'
        required: true
        default: 'Review the codebase'

jobs:
  cursor-agent:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Install Cursor CLI
        run: |
          curl https://cursor.com/install -fsS | bash
          echo "$HOME/.local/bin" >> $GITHUB_PATH

      - name: Run Cursor Agent
        env:
          CURSOR_API_KEY: ${{ secrets.CURSOR_API_KEY }}
        run: |
          cursor-agent -p "${{ github.event.inputs.prompt }}" --force --output-format=text
```

Key points from the official guide: install adds `$HOME/.local/bin` to `$GITHUB_PATH`; `CURSOR_API_KEY` comes from a GitHub secret; `-p` for non-interactive; `--force` to apply changes automatically; `--model "$MODEL"` is optional; `--output-format=text` for human-readable CI logs (note the `=` form is accepted). For machine parsing in a Go-driven pipeline, swap to `--output-format json` and pipe through `jq -r '.result'`:

```yaml
      - name: Run agent (machine-readable)
        env:
          CURSOR_API_KEY: ${{ secrets.CURSOR_API_KEY }}
        run: |
          cursor-agent -p --force \
            --output-format json \
            --model "gpt-5" \
            "Review the changes in this PR and fix any obvious bugs" \
            | jq -r '.result'
```
Cursor also publishes CLI **cookbook** pages with full headless workflows: `cursor.com/docs/cli/cookbook/code-review` (automated PR review) and `cursor.com/docs/cli/cookbook/fix-ci` (agent auto-fixing failing CI). The GitHub Actions page documents a "restricted autonomy" pattern; Windows runners use the PowerShell install (`irm 'https://cursor.com/install?win32=true' | iex`). Note: some official examples add **`$HOME/.cursor/bin`** to `$GITHUB_PATH` while others add `$HOME/.local/bin` — the install dir is version-dependent, so in CI add **both** to PATH to be safe.

---

## 10. Models

- List available models at runtime (do this rather than hardcoding):
  ```bash
  cursor-agent models          # or:
  cursor-agent --list-models
  ```
- Select with `--model <model>` / `-m <model>`. If omitted, the account/workspace default (often **Auto**) is used.
- The `stream-json` `system/init` event reports the resolved model display name (e.g. `"Claude 4 Sonnet"`).
- Model identifiers seen in official examples / the CLI landing page (`cursor.com/cli`, accessed 2026-05-28): `Auto`, `Composer 2.5`, `Opus 4.8`, `GPT-5.5 High Fast`, `Gemini 3.1 Pro`, `Grok 4.3`; older examples use `gpt-5`, `gpt-5.2`, `Claude 4 Sonnet`, `sonnet-4.5`. The exact accepted **CLI token** (display name vs slug) varies by model and version — **always resolve via `cursor-agent models` / `--list-models` rather than assuming a string.** Cursor draws models from OpenAI, Anthropic, Google (Gemini), xAI (Grok), and Cursor's own (Composer). Source: `cursor.com/docs/models`, `cursor.com/cli`.

---

## 11. Modes

`--mode <mode>` (or shorthands):
- `agent` — default; full tool access for coding tasks.
- `plan` — design/clarify before coding (`--plan` is shorthand for `--mode=plan`).
- `ask` — read-only exploration, no changes.

For AFK execution you want the default `agent` mode + `--force`. `plan`/`ask` are useful for read-only or review-only automated passes (e.g. a CI "review" job that must not modify files → `--mode=ask`). Source: overview + parameters reference + Jan 16 2026 changelog ("CLI Agent Modes and Cloud Handoff"). Accessed 2026-05-28.

---

## 12. Exit codes, errors, interrupts

- **Exit codes are not documented in an official table, and have been observed to be unreliable.** Convention is `0` on success / non-zero on failure, BUT multiple forum reports (2026) document **exit 1 on a successful run** and **exit 0 on a failed one** in some versions/CI environments. Therefore **do not rely on the exit code alone** — always parse the `result`/`json` object (`is_error`, `subtype`).
- The `result`/terminal event carries `is_error` (boolean) and `subtype`. On failure, `subtype` is an error variant (exact enum of error subtypes **UNCONFIRMED** — official examples only show `"success"`).
- Interrupting an interactive run with Ctrl-C (SIGINT) prints a resumable chat id (exit ~130 on SIGINT, OS convention).
- There is an official **CI cookbook** page (`cursor.com/docs/cli/cookbook/fix-ci`) — consult it for the recommended CI failure/fix loop and any version-specific exit-code guidance.
- Known issue (forum): headless mode may not cleanly release the terminal in some setups — when shelling out from Go, run with stdin from a pipe/`/dev/null` and capture stdout/stderr to avoid TTY entanglement.
- Shell tool calls have a **fixed 30-second, non-configurable timeout** (Shell Mode docs); long-running/interactive commands are unsupported as agent tool calls. Plan AFK timeouts around the *agent run* total, not individual shell calls; budget your own outer `context.WithTimeout` in Go.

Recommended Go failure detection:
1. Run with `--output-format json` (or capture the terminal `result` line from `stream-json`).
2. Parse it; treat `is_error == true` OR `subtype != "success"` OR process exit code `!= 0` as failure.
3. Fall back to non-zero exit code if no parseable result line was produced.

(Status: exit-code semantics UNCONFIRMED from official docs; the above is the defensive convention.)

---

## 13. Environment variables

| Var | Purpose | Source |
|---|---|---|
| `CURSOR_API_KEY` | API key for headless/CI auth (`cursor_...`). Alternative to `--api-key`. | authentication ref / headless / API docs |
| `PATH` | Must include `~/.local/bin` to find `cursor-agent`. | installation |

No other official env vars for the CLI were found. (A proxy/gateway setup uses `-H/--header` rather than env vars.) Community references to `~/.cursor/cli-config.json` describe a config *file*, not an env var.

---

## 14. Rate limits / cost notes

- Usage is billed against the Cursor account that owns the `CURSOR_API_KEY` / login, on the same plan/usage model as the editor (per Cursor's models & pricing). Model choice drives cost: cheaper/faster models for quick edits, frontier models (Opus/GPT-5-class) for heavy refactors.
- **No CLI-specific rate-limit numbers are published.** Rate limits follow the account plan and the underlying model provider limits. The `duration_api_ms` field in output reflects per-request API time but not cost.
- Cost-control levers in automation: pick a cheaper `--model`, use `--mode=ask`/`plan` for non-mutating passes, and bound batch loops. Source: `cursor.com/docs/models`, headless docs. (Status: specific limits UNCONFIRMED — none published.)

---

## 15. Changelog anchors (CLI-relevant)

| Date / version | What changed (CLI-relevant) | URL |
|---|---|---|
| **2026-01-16** | "CLI Agent Modes and Cloud Handoff" — Plan mode (`/plan`, `--mode=plan`) and Ask mode (`/ask`, `--mode=ask`) brought to the CLI; cloud-agent handoff (prepend `&` to a message, resume at cursor.com/agents); word-level inline diffs; one-click MCP auth + `/mcp list`; WebFetch/WebSearch tools with approval controls; session hooks; `/usage`, `/about`. **Removed `/list` (use `/resume`) and `/models` (use `/model`).** Terminal support for iTerm2, Ghostty, Kitty, Warp, Zed (`Shift+Enter`). | `cursor.com/changelog/cli-jan-16-2026` |
| **2026-01-08** | "New CLI Features and Improved CLI Performance." **`agent` becomes the primary entrypoint; `cursor-agent` is now the backward-compatible alias.** Added `agent models`, `--list-models`, `/models`; `/mcp enable` / `/mcp disable`; `/rules`; `/commands`; MCP server names with spaces; automatic tab naming. Hooks now run in parallel (10x lower latency); `afterFileEdit` hook provides `old_string`. | `cursor.com/changelog/cli-jan-08-2026` |
| 2025-09-11 (v1.6) | MCP Resources support; interpolated variables for MCP; MCP defs/tools as JSON in `.cursor`. | `cursor.com/changelog/1-6` |
| (late 2025) | `--continue` added (shorthand for `--resume=-1`); `/resume` to view prior conversations; `/mcp enable` / `/mcp disable` autocomplete filtering. | `cursor.com/changelog` |
| **2025-08-07** | Cursor Agent CLI launched (beta). Install `curl https://cursor.com/install -fsSL | bash`; example `agent chat "find one bug and fix it"`. Headless `-p`, `--output-format`, `CURSOR_API_KEY`, GitHub Actions documented in the CLI docs. | `cursor.com/blog/cli` |

(Exact verbatim per-entry text for the dated CLI changelogs could not all be re-fetched on 2026-05-28; entries above are summarized from the changelog index + search. Verify the specific entry before quoting.)

---

## 16. Quick-reference cheat sheet (for the Go wrapper)

```bash
# install
curl https://cursor.com/install -fsS | bash
export PATH="$HOME/.local/bin:$PATH"

# auth (headless)
export CURSOR_API_KEY=cursor_xxx

# one-shot, autonomous, machine-readable
cursor-agent -p --force --trust \
  --output-format json \
  --model "<model-from-`cursor-agent models`>" \
  --workspace "$PWD" \
  "<task>"

# streaming (NDJSON) with deltas
cursor-agent -p --force --output-format stream-json --stream-partial-output "<task>"

# resume
SID=$(cursor-agent -p --output-format json "<task>" | jq -r .session_id)
cursor-agent -p --force --resume="$SID" "<follow-up>"
cursor-agent -p --continue "<follow-up to latest>"

# discovery
cursor-agent models          # available models
cursor-agent ls              # prior sessions
cursor-agent status          # auth check
cursor-agent --version       # version
cursor-agent mcp list        # MCP servers
```

**Autonomy flag summary:** `-p` (non-interactive, full tools) + `--force`/`--yolo` (auto-approve unless denied) + `--trust` (skip workspace trust, headless) + `--approve-mcps` (auto-approve MCP) + `--sandbox enabled|disabled` (containment).

---

## 17. Confidence / open items for the Go implementer

Confirmed from official docs (high confidence): install commands; the full subcommand list; all flags in §4 incl. `-p/--print`, `--output-format` values + the exact JSON/stream-json schemas, `--model`, `--resume`/`--continue`, `-f/--force`/`--yolo`, `--sandbox`, `--approve-mcps`, `--trust`, `--workspace`, `--worktree`, `--plugin-dir`, `-H/--header`, `--api-key`, `--insecure`, `--endpoint`; `CURSOR_API_KEY` and the `login`/`logout`/`status` flow; the **permissions JSON schema** (`~/.cursor/cli-config.json` + `.cursor/cli.json`, `permissions.allow`/`deny`, the five `Shell/Read/Write/WebFetch/Mcp` entry types, `command:args` syntax, deny-precedence); the **configuration** keys; the **verbatim GitHub Actions** workflow; MCP subcommands; modes; the Aug 7 2025 launch and Jan 8/16 2026 changelogs.

Still verify directly against the binary on the target version before relying on them:
- Exact **credential storage path** after `login` (not documented; not `cli-config.json`).
- Exact **error `subtype` enum** and **exit-code semantics** (observed unreliable in CI — always parse `is_error`/`subtype`).
- Whether `sandbox` / `approvalMode` are valid **config-file** keys (documented config keys are `version`, `editor`, `permissions`, `model`, `hasChangedDefaultModel`, `network`, `attribution` — see §8b; `sandbox`/`approvalMode` are NOT among them). Set sandbox/force/mode via flags.
- Exact accepted **model token strings** for `--model` (resolve via `cursor-agent models`).
- The exact `.cursor/mcp.json` CLI example (standard-Cursor MCP shape is well known; CLI-page verbatim block was partial).
- `--max-mode`, `--cwd`, `--output`, `--rules`, `--mcp-config`, `--with-diffs`, `--background`, `-b` — **not in the official parameters reference; treat as non-existent** unless `cursor-agent --help` on the target version says otherwise.

> The single most reliable ground truth is `cursor-agent --help` and `cursor-agent help <command>` run against the exact pinned binary the Go program will shell out to. Snapshot that output into the repo at build time.
