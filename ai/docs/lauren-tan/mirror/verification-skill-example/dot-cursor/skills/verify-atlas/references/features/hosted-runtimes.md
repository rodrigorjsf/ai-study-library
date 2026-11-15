# Hosted runtimes

Desktop surfaces that wrap cloud runtimes: remote desktop tab, open in web, environment setup, private workers, migrate local/cloud, provider connect.

## Sub-features

- cloud-desktop-tab: remote desktop / VNC-style tab
- open-in-web: open the same thread on the web app
- environment-setup: cloud environment bootstrap UI
- private-workers: self-hosted worker pools
- migrate-local-cloud: move a thread between local and cloud
- provider-connect: connect GitHub/GitLab/Azure DevOps for cloud

## How to get to it (user POV)

Select a cloud runtime in session creation, or open Hosted Desktop from an existing cloud thread's header.

## Driving it with control-atlas

Cloud paths need a cloud-entitled account. If missing, skip the whole file with that reason.

Open-in-web: click the control, assert a system browser open is attempted (may be manual to finish).

Provider connect: prefer the in-app GitHub flow when available; other providers may hand off to a dashboard.

## Gotchas

- Full VNC pointer/keyboard validation needs a live cloud desktop and OS clipboard permissions. Mark manual when entitlement is missing.
- Migration is sticky; restore the original runtime after tests that move it.
