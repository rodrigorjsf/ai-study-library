---
name: verify-atlas
description: "Drive the Atlas workspace UI in a running Harbor Labs desktop build via CDP. Use for screenshots, clicks, sending messages, accessibility-tree inspection, JS evaluation, or visual-state checks."
disable-model-invocation: true
---

# Verify Atlas

Drive a running Atlas desktop build over CDP: inspect the DOM, take screenshots, click, type, read the accessibility tree, evaluate JS, and manage checkout-isolated parallel instances.

`node .cursor/skills/verify-atlas/control-atlas.mjs --help` lists commands, flags, and examples. This sample documents usage only; the driver scripts are not included.

## Pick a flow

`test -f .git && echo checkout` distinguishes an isolated checkout (`.git` is a file) from the main workspace (`.git` is a directory).

- **Main workspace:** the desktop build runs on CDP port 9222 with the shared user-data-dir. Drive it directly without `--checkout`.
- **Isolated checkout:** every command takes `--checkout` so the port and user-data-dir are derived for this tree. That keeps the run from fighting the user's main session or polluting auth.

From a checkout, a connect/launch command without `--checkout` (and without an explicit `--cdp`) is refused. Pass `--checkout`, or `--cdp <endpoint>` if you mean another instance on purpose.

Run `doctor` first when anything looks off. It reports checkout context, who owns the CDP port, watcher liveness, and build freshness.

## Checkout quick start

```bash
# provision an isolated checkout, optionally seed auth, restart, then health-check
node .cursor/skills/verify-atlas/control-atlas.mjs checkout-setup --watch
node .cursor/skills/verify-atlas/control-atlas.mjs clone-userdata --force --overwrite   # optional
node .cursor/skills/verify-atlas/control-atlas.mjs --checkout restart
node .cursor/skills/verify-atlas/control-atlas.mjs --checkout info
node .cursor/skills/verify-atlas/control-atlas.mjs doctor
node .cursor/skills/verify-atlas/control-atlas.mjs cleanup --remove-checkout
```

## Main-workspace quick start

```bash
node .cursor/skills/verify-atlas/control-atlas.mjs info
node .cursor/skills/verify-atlas/control-atlas.mjs doctor
```

The desktop build must already be running with remote debugging enabled (default port 9222 in the Harbor Labs desktop launcher).

## Command surface

`--help` is canonical. Categories:

- **Inspection:** `info`, `snapshot`, `screenshot`, `components`
- **Navigation:** `home`, `new-session`, `select-project`, `select-runtime`, `scroll`
- **Interaction:** `send`, `click`, `click-xy`, `aria-click`, `type`, `press`, `eval`, `upload-image`, `add-context`, `feature-flag`
- **Performance:** `trace`, `profile`, `record`, `perf-metrics`, `wait-settle`
- **Streaming:** `console`, `network-log`, `network-summary`
- **Health & cleanup:** `doctor`, `cleanup`, `watch --restart`

Examples:

```bash
# health
node .cursor/skills/verify-atlas/control-atlas.mjs doctor

# open a blank thread and send
node .cursor/skills/verify-atlas/control-atlas.mjs new-session
node .cursor/skills/verify-atlas/control-atlas.mjs send "list open tasks in this project"

# keyboard path
node .cursor/skills/verify-atlas/control-atlas.mjs press "Meta+KeyN"

# accessibility snapshot of the live UI
node .cursor/skills/verify-atlas/control-atlas.mjs snapshot

# screenshot for evidence
node .cursor/skills/verify-atlas/control-atlas.mjs screenshot /tmp/atlas-proof.png

# wait for streaming / layout to settle
node .cursor/skills/verify-atlas/control-atlas.mjs wait-settle

# flip a gated path for the session
node .cursor/skills/verify-atlas/control-atlas.mjs feature-flag rooms_v2 on
```

## Proof bar

Do not submit "look, it opens" captures. A proof must exercise the production user path and show the observable result a skeptical reviewer would accept.

- Drive the running build through user-visible UI, registered keybindings, menus, and normal backend plumbing. Use `eval` to inspect state after the user path ran, not to invoke internal handlers as the primary proof.
- Run `doctor` first. A video against a stale bundle is not evidence.
- Read the relevant file under `references/features/`. Exercise every reachable entry point, mode, enabled gated variant, and the success / cancel / error / empty / persistence paths the change can affect.
- For broad regression sweeps, walk `references/features/README.md` top to bottom, then `multi-surface-journeys.md`.
- Show the trigger and the stable end state in the same recording.
- Verify side effects, not just pixels: DOM attributes, clipboard, network/RPC log, file contents, or a reload / switch-away round trip.

## Driving conventions

- Prefer ARIA labels, `data-component`, `data-action-id`, and `data-message-*` selectors. Class selectors are fallbacks.
- Streaming is non-deterministic. Wait on observable end states with `wait-settle`, not fixed sleeps.
- Prefer `press` with the registered chord over coordinate clicks.
- The command service is not on `window`. Do not invoke `atlas.*` through `eval`.
- Use `feature-flag` for gated paths. Reload when the feature file says the mounted tree needs it.
- Treat real OS file drops, native context menus, and system-browser auth as manual unless the driver has first-class support.

## Feature map

The behavior inventory lives in [`references/features/`](references/features/). Each file uses the same four H2s: `Sub-features`, `How to get to it (user POV)`, `Driving it with control-atlas`, `Gotchas`.
