# Sign-in and account menu

How a user signs in to Atlas, sees who they are, manages the account from the left rail footer, and signs out.

## Sub-features

- sign-in-gate: full-window gate with Log In and Sign Up.
- oauth-login: Log In / Sign Up open the OS browser to auth.harborlabs.example.
- dev-auto-login: one-click plan presets in desktop dev builds.
- logout: signs out from the account menu and returns to the logged-out screen.
- account-menu: avatar, name, plan or team on the trigger; Docs / Shortcuts / Contact / Log Out inside.
- plan-visibility: footer subtitle shows selected team name when active, otherwise the plan.

## How to get to it (user POV)

Signed out: launch with no stored auth. The window is the logged-out screen (wordmark, headline, Log In, Sign Up). Click either to start auth in the system browser. Dev builds also show a "Developer quick login" row.

Signed in: account lives in the left rail footer, bottom-left. Click the avatar to open the account menu. Log out from that menu, then confirm. Preferences gear (or Cmd/Ctrl+,) opens Plan & Usage for plan detail.

## Driving it with control-atlas

Preferred auth for automation: `clone-userdata --force --overwrite` then `restart` (boots pre-logged-in).

```bash
node .cursor/skills/verify-atlas/control-atlas.mjs clone-userdata --force --overwrite
node .cursor/skills/verify-atlas/control-atlas.mjs restart
node .cursor/skills/verify-atlas/control-atlas.mjs snapshot   # expect sidebar + footer, no logged-out gate
```

- Logged-out screen: clean user-data-dir. Assert `[data-component="sign-in-gate"]` and absence of `[data-component="left-rail"]`. Do not gate on absence of `[data-component="root"]` (root wraps both states).
- OAuth login: manual. The driver refuses to complete the external browser flow.
- Dev auto-login: click a named button ("Pro Login") or run the matching palette command.
- Account menu: click `aria-label="Account menu"` inside `[data-component="account-footer"]`.
- Logout: open menu → Log Out → cancel once (shell unchanged) → reopen and confirm. `[data-component="sign-in-gate"]` returns. Restore with `clone-userdata` + `restart`.

## Gotchas

- `[data-component="root"]` is present when signed out. Assert on the logged-out screen component and missing authenticated chrome.
- Appearance is a preferences tab, not an account-menu item.
- Plan & Usage and team invite need matching account state; skip with an explicit reason when the account cannot reach them.
