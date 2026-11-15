# Runbook

Plan tab: the agent's latest plan as an editable document, with Build, find, edit/export, and add-to-chat.

## Sub-features

- plan-document: rendered plan markdown/document
- build-from-plan: hand the plan to an agent run
- plan-find-edit-export: find, edit, export the plan
- add-plan-to-chat: insert plan context into the prompt

## How to get to it (user POV)

After an agent produces a plan, open the Plan app tab. Or open an existing plan from the plan tray above the prompt.

## Driving it with control-atlas

Seed by sending a prompt that asks for a plan. Wait-settle, open Plan, screenshot the document.

Add-to-chat: assert a chip/mention appears in the prompt editor.

## Gotchas

- Empty Plan tab is valid before any plan exists.
- Build-from-plan starts real work; cancel if the suite should stay read-only.
