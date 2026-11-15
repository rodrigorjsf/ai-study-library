# Overlays and deep links

Layered modal stack behind overlays, plus `atlas://` deep links that open a thread, automation, settings, and more.

## Sub-features

- modal-stack: layered dialogs with focus trap and Escape
- confirm-dialogs: destructive confirmations
- deeplink-thread: open a thread from an atlas:// link
- deeplink-settings: open a preferences tab from a link
- deeplink-automation: open an automation detail from a link

## How to get to it (user POV)

Modals open from many features (logout confirm, invite, clone). Deep links are hit from OS handlers or `open` in automation.

## Driving it with control-atlas

For modals: open, assert focus trap via snapshot, Escape to dismiss, assert underlying UI restored.

For deep links: invoke a fixture `atlas://` URL the suite owns, assert the landing surface.

## Gotchas

- Deep link registration is OS-level and may be unavailable in bare CDP harnesses. Skip with reason when the handler is not registered.
- Stacked modals need one Escape per layer.
