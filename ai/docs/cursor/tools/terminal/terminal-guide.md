# Terminal

Agent runs shell commands directly in your terminal, with safe sandbox execution on macOS, Linux, and Windows.

## Sandbox

By default, Agent runs terminal commands in a restricted environment that blocks unauthorized file access and network activity. Commands execute automatically while staying confined to your workspace.

### Platform requirements

- **macOS:** Cursor v2.0 or later — Works out of the box with no additional setup
- **Windows:** The sandbox runs inside WSL2, applying the same restrictions as on Linux
- **Linux:** Kernel 6.2 or later, `CONFIG_SECURITY_LANDLOCK=y`, Unprivileged user namespaces

If your kernel doesn't meet these requirements, Agent falls back to asking for approval before running commands.

### AppArmor setup

Some distributions restrict user namespaces through AppArmor. The Cursor desktop package ships with the required profile, so no extra setup is needed for local installations.

**Debian / Ubuntu:**

```bash
curl -fsSL https://downloads.cursor.com/lab/enterprise/cursor-sandbox-apparmor_0.4.0_all.deb -o cursor-sandbox-apparmor.deb
sudo dpkg -i cursor-sandbox-apparmor.deb
```

**RHEL / Fedora:**

```bash
curl -fsSL https://downloads.cursor.com/lab/enterprise/cursor-sandbox-apparmor-0.4.0-1.noarch.rpm -o cursor-sandbox-apparmor.rpm
sudo rpm -i cursor-sandbox-apparmor.rpm
```

After installing, restart Cursor or your CLI session for the sandbox to work.

### How the sandbox works

The sandbox prevents unauthorized access while allowing workspace operations:

| Access Type | Description |
|---|---|
| File access | Workspace-scoped |
| Network access | Allowlist-controlled |
| `sandbox.json` | Policy configuration |
| Temporary files | Permitted |
| `.cursor` | Accessible |

Some commands need full system access and bypass the sandbox. Agent will indicate when a command runs outside the sandbox and ask for your approval.

### Allowlist

Commands on the allowlist skip sandbox restrictions and run immediately. You can add commands to the allowlist by choosing the appropriate option when prompted.

When a sandboxed command fails due to restrictions, you can:

| Option | Description |
|---|---|
| Cancel | Cancel the command and let Agent try something else |
| Execute without sandbox | Execute the command without sandbox restrictions |
| Add to allowlist | Run without restrictions and automatically approve it for future use |

### Default network allowlist

When network access is enabled, outbound connections are restricted to a curated set of domains. These cover common package registries, cloud providers, and language toolchains so most development workflows work without extra configuration.

## Sandbox configuration

Configuration files:

- `~/.cursor/sandbox.json` — Global user configuration
- `<workspace>/.cursor/sandbox.json` — Per-workspace configuration

## Environment variables

Cursor injects environment variables into every sandboxed child process. These are available to your scripts, build tools, and automation running inside the sandbox.

| Variable | Platforms | Description |
|---|---|---|
| `CURSOR_SANDBOX` | macOS, Linux, Windows | Indicates sandbox is active |
| `CURSOR_ORIG_UID` | macOS, Linux | The UID of the user who launched Cursor, captured before sandbox identity changes |
| `CURSOR_ORIG_GID` | macOS, Linux | The GID of the user who launched Cursor, captured before sandbox identity changes |
| `CURSOR_SANDBOX_LANDLOCK_STATUS` | Linux | `fully_enforced` or `bubblewrap` |

> **Note (Linux):** UID inside the sandbox may not match your real user.

### Docker and container automation

When using Docker inside the sandbox, use `CURSOR_ORIG_*` variables to pass through your real UID:

```bash
docker run --rm \
  --user ${CURSOR_ORIG_UID:-$(id -u)}
```

## Editor configuration

Navigate to **Settings > Cursor Settings > Agents > Auto-Run**.

### Auto-run mode

Choose how Agent runs tools like command execution, MCP, and file writes:

| Mode | Behavior |
|---|---|
| Run in Sandbox | Tools and commands auto-run in the sandbox where possible. Available on macOS, Linux, and Windows (via WSL2). |
| Ask Every Time | All tools and commands require user approval before running. |
| Run Everything | The agent runs all tools and commands automatically without asking for input. |

### Auto-run network access

Choose how sandboxed commands access the network:

| Option | Description |
|---|---|
| `sandbox.json` Only | Only domains listed in your sandbox.json |
| `sandbox.json` + Defaults | Your allowlist plus Cursor's built-in defaults (common package managers, etc.). **This is the default.** |
| Allow All | All network access permitted |

### Protection settings

| Setting | Description |
|---|---|
| Command Allowlist | Commands that can run automatically outside of the sandbox |
| MCP Allowlist | MCP tools that can run automatically outside of the sandbox |
| Browser Protection | Restricts browser automation |
| File-Deletion Protection | Prevent Agent from deleting files automatically |
| Dotfile Protection | Prevent Agent from modifying dot files like `.gitignore` automatically |
| External-File Protection | Prevent Agent from creating or modifying files outside of the workspace automatically |

## Enterprise controls

*Only available for Enterprise subscriptions.*

Navigate to **Settings > Auto-Run** in the web dashboard.

| Control | Description |
|---|---|
| Auto-Run Controls | Enable controls for auto-run and sandbox mode. When disabled, commands auto-run in the sandbox where available, otherwise they ask for permission. |
| Sandboxing Mode | Control whether sandbox is available for end users. When enabled, commands auto-run in the sandbox even if they are not on the allowlist. |
| Sandbox Networking | Choose whether sandboxed commands have network access. |
| Delete File Protection | Prevent file deletion |
| MCP Tool Protection | Prevent Agent from automatically running MCP tools. |
| Terminal Command Allowlist | Commands that can run automatically without sandboxing. When sandbox is enabled, commands not on this list auto-run in sandbox mode. |
| Enable Run Everything | Give end users the ability to enable the "Run Everything" mode. |

## Troubleshooting

Some shell themes (for example, Powerlevel9k/Powerlevel10k) can interfere with the inline terminal output. If your command output looks truncated or misformatted, disable the theme or switch to a simpler prompt when Agent runs.

### Disable heavy prompts for Agent sessions

Use the `CURSOR_AGENT` environment variable to detect when Agent is running and switch to a simpler prompt:

```zsh
# ~/.zshrc — disable Powerlevel10k when Cursor Agent runs
if [[ -n $CURSOR_AGENT ]]; then
  # switch to a simple prompt
fi
```

```bash
# ~/.bashrc — fall back to a simple prompt in Agent sessions
if [[ -n $CURSOR_AGENT ]]; then
  # switch to a simple prompt
fi
```
