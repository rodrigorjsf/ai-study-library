# Research

Step 5 compares this repo with current practice for its own stack. The step 3 inventory decides the topics; nothing here assumes a language.

## Rules for every research agent

- **Primary sources first:** the language and tool documentation, specifications, vendor security pages, OWASP and other standards bodies; well-regarded books and maintainers' guides after them. List only the URLs actually read, with the date. Prefer the current year's guidance and say when a practice changed.
- **Compare with the repo, read-only.** For every practice, open the files that decide it and set `repoState` to `already-followed`, `partially-followed`, `not-followed` or `not-applicable`, with `path:line` evidence. A practice not checked against the repo is not reported as followed or not.
- **Specific to this repo.** Skip advice that does not apply to what step 3 found; aim for the 10 to 20 practices that matter most per topic.
- **Mechanical or not:** when a tool could enforce the practice, name the exact check (a compiler flag, a linter rule by name, a package-manager setting, a repo-level test).
- **Severity** is the impact here if the practice is ignored: `critical`, `high`, `medium`, `low`.
- Write in English; the step 8 draft translates what becomes a rule.

Proposal schema, one object per practice:

```json
{ "practice": "", "why": "", "sources": [""], "repoState": "", "repoEvidence": ["path:line"], "severity": "", "mechanical": true, "proposedCheck": "" }
```

## Topics

Make one topic per line that applies; merge small ones.

1. **The language and its tooling.** Strictness and compiler or interpreter flags, the linter's strict and type-aware rule sets, formatting, error modelling, nullability, immutability, async or concurrency correctness, module and package boundaries in this repo's layout, testing practice for this language.
2. **Each framework or runtime that shapes the code** (a web framework, an ORM, a UI framework, a bot or agent SDK): its documented best practices and pitfalls.
3. **Security of the outside systems**, one topic per group from the step 3 inventory, each covering how this repo authenticates to the system, what it trusts from it, how it validates what comes back, and what a leak of its credential would expose.
4. **Security of the platform.** Dependency supply chain (lockfiles, pinning, install scripts, release-age delays, audits), build and runtime images (non-root, minimal and pinned base, capabilities, read-only filesystem), network exposure, data at rest (database file permissions, encryption of backups and their immutability), logging of secrets and personal data.

## Aspects the coverage critic checks

After the topics return, a critic reads the list of practices found and marks each aspect below as covered (a concrete practice compared with the repo) or missing. Skip an aspect only when step 3 shows the repo has nothing it applies to.

- **Identity and authorisation** at every entry point (who may call, and whether each action checks the caller owns what it touches).
- **Untrusted input**: every place outside data enters (HTTP, messages, files, uploads, third-party API answers) and where it is validated.
- **Secrets**: where each one is read, kept, rotated and revoked; never in images, logs, fixtures, issues or commits.
- **Outbound calls**: timeouts, which host a credential may be sent to, redirect and pagination handling.
- **AI model or agent runtime**, when present: prompt injection from every untrusted text the model reads, the tools and permissions each run gets, exfiltration channels (links, web access, previews), whether any model-called tool can write without a human confirmation.
- **Data at rest and in transit**: databases, caches, backups (encrypted, off-site, immutable to the host they protect).
- **Logs and telemetry**: no secret, no personal or financial value, redaction that covers every secret the config holds.
- **Network exposure** of every service and admin surface.
- **Supply chain and build.**
- **Personal data in the repository's own history and tracker** (tests, fixtures, issues, commit messages).
- **Third-party processors** that receive user data (retention settings, training opt-outs).
- **Root-of-trust accounts and the host itself** (the accounts that can change the code, the secrets or the machine).

For each missing aspect the critic writes a one-paragraph brief, and one gap researcher runs per brief. Cap the gap round if needed, and name every aspect the cap left out: an unresearched aspect is reported, never silently dropped.
