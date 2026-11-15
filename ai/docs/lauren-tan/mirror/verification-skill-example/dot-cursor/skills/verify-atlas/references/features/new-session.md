# New session and targets

The empty-state prompt is the blank "new thread" surface: a prompt box with a project badge above it. From here a user starts a fresh local or cloud thread, picks where it runs, and sends the first message.

## Sub-features

- empty-state-composer: blank prompt for a new thread, with the project selector badge.
- new-session-shortcuts: Cmd/Ctrl+N opens a plain new thread; Cmd/Ctrl+Alt+N keeps the app panes open.
- new-session-in-project: fresh empty state scoped to an existing row's project, from the left rail row menu and the thread top bar.
- project-selector: pick a target. Recents, workspaces, cloud repos, No Project, plus clone, SSH, and provider-connect actions.
- runtime-selector: switch among local checkout, worktrees, cloud, and self-hosted runtimes for the selected project.
- cloud-thread-creation: optimistic UI that flips to the new conversation before the cloud thread is created server-side.
- send-to-cloud: treatment-only secondary submit that sends an eligible local draft to a runnable cloud sibling.
- open-folder: native OS folder picker that adds and targets a workspace.
- empty-state-quickstarts: optional cards that prefill the prompt and matching mode.
- rotating-product-tips: tips beneath the empty-state prompt, with a "Hide tips" control.

## How to get to it (user POV)

Reach the empty state:
- Left-rail header: click New Thread. The session panel switches to the empty-state prompt and the prompt focuses. Analytics source is `sidebar`.
- Keyboard: press Cmd/Ctrl+N from anywhere in Atlas.
- Hidden-sidebar top bar: the New Thread control there does the same.

When eligible, the empty state usually shows quickstart cards such as "Start with a plan", "Debug an issue", and "Draft a summary". Clicking one prefills the prompt and selects the matching mode; it does not submit until you send.

Pick a target (project selector):
- Click the project badge above the prompt, or press Cmd/Ctrl+.
- Type to filter, or pick from Recents / workspaces / cloud repos.
- Choose Clone Repository to paste a Git URL, review the preview, then Clone or Escape.

Switch runtime:
- The runtime selector appears when the target has multiple runtimes. Click it or press Cmd/Ctrl+Shift+. ; Cmd/Ctrl+; cycles without opening the menu.

Send:
- Type a prompt and use the configured submit chord (Enter, or Cmd+Enter when Submit with Cmd+Enter is enabled). Local targets open immediately. Cloud targets switch optimistically while the server creates the thread.
- In the `send_to_hosted_prompt` treatment, an eligible local draft also shows **Send to Hosted** beside Send.

## Driving it with control-atlas

Preconditions: signed-in build (`clone-userdata` for the happy path), at least one workspace folder, and a model the account can use. Cloud paths need a cloud-entitled account. From a checkout, pass `--checkout` on every command.

```bash
node .cursor/skills/verify-atlas/control-atlas.mjs new-session
node .cursor/skills/verify-atlas/control-atlas.mjs send "list files in this folder"
node .cursor/skills/verify-atlas/control-atlas.mjs wait-settle
node .cursor/skills/verify-atlas/control-atlas.mjs screenshot /tmp/atlas-new-session.png
```

- Open the empty state: `new-session` (clicks New Thread, auto-dismisses settings), or `press "Meta+KeyN"`. For the keep-pane variant use `press "Meta+Alt+KeyN"`. To assert the `sidebar` analytics source, click `data-action-id="new-session"` inside `[data-component="left-rail"]`.
- Send the first message: `send "..."` presses Enter. Pass `--meta` for Cmd+Enter. The conversation renders under `[data-component="session-panel"]`; wait on human and AI bubbles, not a fixed sleep.
- Project selector: `press "Meta+Period"` or `click` the badge. The menu is `[aria-label="Select a project"]`. Driver shortcuts `select-project <local|cloud|self-hosted>` and `select-runtime [name]` wrap common picks.
- Clone Repository: open the picker, choose Clone Repository, type a disposable URL, assert the preview and enabled Clone button, then Escape during a read-only sweep.
- Runtime selector: `press "Meta+Shift+Period"` to open, `press "Meta+Semicolon"` to cycle.
- Quickstarts: `snapshot` the empty state, click a live card name, assert prompt text and mode chip before sending. Tip dismiss is `aria-label="Hide tips"`.
- Send to Hosted: set `send_to_hosted_prompt` on via feature-flag / experiment overrides, open an eligible local empty state with a cloud sibling, type prompt text, assert `aria-label="Send to Hosted"`.

## Gotchas

- Command titles and ids are easy to swap. `atlas.openFolder` is titled "Open Folder" (Cmd/Ctrl+O); `atlas.openTargetPicker` is titled "Open Project" (Cmd/Ctrl+.).
- Quickstart cards have no dedicated feature gate. They render only on eligible empty states (no existing user messages, not a cloud target, not while provider access is being checked). Snapshot before relying on exact labels.
- Send to Hosted needs a paid/team account, a local runtime with a runnable cloud sibling, non-empty prompt text, and no hard usage-limit block. Changing to a cloud target hides it immediately.
- The runtime selector and Cmd/Ctrl+; cycle are no-ops unless runtime choice is relevant.
