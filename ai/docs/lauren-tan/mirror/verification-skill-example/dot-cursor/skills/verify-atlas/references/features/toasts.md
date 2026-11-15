# Toasts

Bottom-right toasts with severity and actions, warning-toast setting, and the quiet extension notification buffer.

## Sub-features

- toast-show-dismiss: show and dismiss a toast
- toast-actions: action buttons on a toast
- warning-toast-setting: user setting that filters warning toasts
- extension-notification-buffer: quiet buffer surfaced from file tabs

## How to get to it (user POV)

Toasts appear bottom-right in response to events (save failures, invite results, update ready). Preferences controls warning visibility.

## Driving it with control-atlas

Trigger a deterministic toast from a fixture action (for example copy invite link success). Assert aria role/status and dismiss.

Do not depend on update-ready toasts in normal suites.

## Gotchas

- Toasts auto-dismiss. Assert quickly or pause dismissal timers only if the driver supports it.
- Multiple toasts stack; target by name, not by index.
