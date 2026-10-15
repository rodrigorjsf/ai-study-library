# Verifying subagent findings in the main thread

A subagent's `path:line` is a lead. A claim reaches a chapter at the strength of the check that **you** ran.

## What to re-check yourself

Run `sed -n '<start>,<end>p' <file>` or `grep -n` on the pinned checkout and read the lines for:

- every Critical, High and Medium security finding;
- every default that decides a verdict: bind address and port, auth on or off, telemetry consent, LLM
  provider and fallback, auto-update, redaction on or off, retention;
- every claim that a project document is false (quote the document line **and** the code line);
- every number that appears on a cover, a scorecard or a comparison (harness counts, tool counts, versions).

Search **wide** before you confirm an absence. "There is no mTLS client" needs a grep for every way the
language spells it (`Identity::from`, `with_client_auth`, `client_cert`, `cert`, `key`), not a grep filtered
down to the word you expected.

## When findings disagree

Two subagents, or a subagent and the docs, often disagree on a default (for example a documented port that
the code computes differently). The code at the pinned SHA wins; say in the chapter which source was stale.

## Labels

| Label | Meaning | Who may apply it |
|---|---|---|
| `[verificado]` | You ran the command and read the output this session | main thread only |
| `[código]` | Read in code by a subagent, with `path:line` | anyone |
| `[doc]` | From the project's documentation, partly checked in code | anyone |
| `[inferido]` | Conclusion from code plus documentation that needs a runtime test | anyone |

Translate the label words into the study's language; keep the four levels.

## Severity sanity

Rate by scenario, not by keyword. A finding's severity depends on the deployment the user named: an
unauthenticated loopback API is High on a shared host and Low on a single-user laptop. Write both when the
user's deployment is mixed. A critical CVE in a dependency is a finding only when the vulnerable function is
reachable from the code; otherwise it is an upgrade item.

## Removing what fails

A claim you cannot trace to code, a fetched source or command output is deleted from the chapter. Do not
keep it with a warning.
