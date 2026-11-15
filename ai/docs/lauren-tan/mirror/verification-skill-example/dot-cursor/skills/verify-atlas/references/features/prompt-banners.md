# Prompt banners

Stack of trays and pills above the prompt: active goal, status, questionnaire, mode switch, plan, errors, billing, branch mismatch.

## Sub-features

- status-bar-tray: compact status above the prompt during a run
- questionnaire-tray: blocking multiple-choice prompts from the agent
- plan-tray: link to the active plan document
- error-tray: actionable error with retry/dismiss
- billing-usage-tray: usage and billing callouts
- branch-mismatch-tray: warn when the runtime branch drifted

## How to get to it (user POV)

Trays appear above the prompt when their condition is active. Most are transient; questionnaire and billing can block send.

## Driving it with control-atlas

Trigger each tray via its real condition when possible (feature-flag for treatments, intentional error for error-tray).

Assert tray roots by aria-label from snapshot. Dismiss or answer without leaving the suite blocked.

## Gotchas

- Multiple trays can stack. Assert order only when the feature file claims a priority.
- Do not `send` while a blocking questionnaire is open; submit will no-op or error.
