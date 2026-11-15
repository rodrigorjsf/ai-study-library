# Remote machines

Connect Atlas to a remote machine over SSH or a WSL distro, pick a folder, manage forwarded ports, run threads against a remote workspace.

## Sub-features

- ssh-connect: add and connect an SSH target
- wsl-connect: pick a WSL distro (Windows)
- remote-folder-pick: open a folder on the remote
- port-forwarding: forward and list ports
- remote-thread: run a thread against the remote workspace

## How to get to it (user POV)

From the project selector, choose Connect SSH or Connect WSL. Complete the connection flow, then open a folder.

## Driving it with control-atlas

Prefer a disposable SSH fixture the suite owns. Do not use production bastions.

If no remote is configured, skip with reason and cover the connect dialog open/cancel path only.

## Gotchas

- WSL paths are Windows-only. Skip on macOS/Linux hosts.
- Auth prompts for SSH keys/passphrases can be modal and OS-native; mark manual when the driver cannot type them.
