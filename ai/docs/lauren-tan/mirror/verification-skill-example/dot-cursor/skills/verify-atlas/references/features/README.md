# Atlas feature map

Behavior-level inventory of Atlas (Harbor Labs workspace desktop). Agents use this map to decide what to drive and what evidence counts. Humans use it as the regression checklist.

This sample is intentionally large (~30 feature files) so you can see how a real app map stays navigable: one file per area, shared conventions in this README, multi-surface journeys in a single file at the end.

## Baseline preconditions

- Signed-in desktop build unless the feature is the sign-in gate.
- Fresh bundle: run `doctor` and clear `STALE BUILD` / wrong-instance warnings before driving.
- From an isolated checkout, pass `--checkout` on every command.
- Keep developer overlays off. Leave unrelated feature-flag overrides untouched.
- Prefer ARIA labels, `data-component`, `data-action-id`, and `data-message-*`. Class selectors are fallbacks.
- Streaming is non-deterministic. Wait on observable end states with `wait-settle`.
- Prefer `press` with the registered chord over coordinate clicks.
- Do not invoke `atlas.*` through `eval`. Use `eval` to read DOM, clipboard, and attributes after the user path ran.
- Real OS file drops, native context menus, and system-browser auth are manual unless the driver has first-class support.

## Proof and skip reporting

For a fix or feature, the relevant feature file defines the coverage set. When a change spans sessions, shortcuts, or drag/drop, also read `multi-surface-journeys.md`.

- Exercise every reachable entry point, mode, enabled gated variant, and the success, cancel, error, empty, and persistence paths the change can affect.
- Record the action and the final observable state.
- Mocks count only behind the same production boundary an unavailable external dependency would use. They do not count when they skip the renderer, a workbench service, an RPC, persistence, or the tool path under test.
- When a path is unreachable, name it, say whether account, OS, entitlement, or native driver blocks it, and cover the closest real path that remains.

## Full sweep

Walk this map top to bottom for a broad regression. Finish with `multi-surface-journeys.md`. Keep new entries behavior-level, grounded in selectors or visible state, and short enough to run without reading source.

## Account & chrome

- [sign-in](sign-in.md): Sign in / out, sign-in gate, account footer menu, plan display.
- [workspace-chrome](workspace-chrome.md): Persistent authenticated frame, titlebar, first-launch splash, setup wizard.

## Left rail & sessions

- [left-rail](left-rail.md): Left rail: hide/show, resize, group, filter, reorder, bulk-manage.
- [session-rows](session-rows.md): A single session row: select, hover tooltip, pin/rename/archive/move, next/previous.
- [new-session](new-session.md): Empty-state prompt for a new session: project and runtime selectors, local vs hosted targets, first message.
- [shared-sessions](shared-sessions.md): Team shared sessions: visibility, create, start session.
- [workspace-groups](workspace-groups.md): Local workspace groups with parent/child sessions and tabs/panes.

## Prompt & replies

- [prompt-box](prompt-box.md): Prompt input: mode and model pills, mentions, attachments, history, submit chords.
- [live-replies](live-replies.md): How a reply streams: assistant text, thinking bubble, tool cards, abort.
- [follow-ups](follow-ups.md): Follow-up queue, reorder/edit, parallel spawn, child-session tray.
- [transcript](transcript.md): Transcript scroll, outline, in-chat find, draft persistence, hosted stream recovery.
- [session-menu](session-menu.md): Session overflow actions and per-turn thumbs feedback.
- [prompt-banners](prompt-banners.md): Status, questionnaire, runbook, error, billing, and branch-mismatch banners.

## Layout & navigation

- [split-view](split-view.md): App panes, tiling, icon rail, per-session tab memory.
- [command-palette](command-palette.md): Cmd/Ctrl+K palette family and go-to-session chords.

## Source control

- [working-tree](working-tree.md): Working-tree diff cards, stage, commit/push/review handoff.
- [review-requests](review-requests.md): Per-review tab: files, CI, reviews, merge, comment-to-chat.

## App panes

- [project-brief](project-brief.md): Gated project overview and brief files.
- [web-pane](web-pane.md): Embedded web pane: omnibar, tabs, find, console, agent-lock overlay.
- [shell-pane](shell-pane.md): Shell pane, multi-shell, buffer search, agent read-only panes.
- [file-browser](file-browser.md): File tree, preview, find, workspace search, viewers.
- [runbook](runbook.md): Editable runbook document, Build, add-to-chat.
- [log-pane](log-pane.md): Read-only log channels.
- [live-preview](live-preview.md): Live `*.preview.tsx` preview/source.

## Hosted & remote

- [hosted-runtimes](hosted-runtimes.md): Hosted desktop tab, open on web, env setup, private workers, migrate, provider connect.
- [remote-machines](remote-machines.md): SSH / WSL connect, remote folder, port forwarding, remote sessions.

## Preferences & extensibility

- [preferences](preferences.md): Full-screen preferences overlay and tab set.
- [extensions-catalog](extensions-catalog.md): Browse/install plugins, skills, MCPs, rules, commands, hooks.
- [scheduled-jobs](scheduled-jobs.md): Hosted jobs and gated local schedules, run history.

## System UX

- [toasts](toasts.md): Toasts, warning-toast setting, extension notification buffer.
- [overlays-and-links](overlays-and-links.md): Modal stack and `atlas://` deep links.
- [unattended-runs](unattended-runs.md): Unattended runs against a branch/review request.
- [odds-and-ends](odds-and-ends.md): Workspace tasks, perf toolbar, promos, running extensions.

## Multi-surface journeys

- [multi-surface-journeys](multi-surface-journeys.md): Multi-session isolation, optimistic hosted create + queue, shortcut sweep, drag/drop gaps.

## Entry contract

Every feature file uses the same four H2s:

1. `Sub-features`
2. `How to get to it (user POV)`
3. `Driving it with control-atlas`
4. `Gotchas`
