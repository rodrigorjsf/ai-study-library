---
name: follow-up-issue
description: File a follow-up issue from a fixed template, only for a suspicion that needs investigation before anyone knows it is real, or a defect in an external resource the same owner controls (e.g. the user's own Claude Code plugin). Every finding the running task can act on is absorbed into it instead. Also use when the user says "abre uma issue", "registra isso numa issue", "cria uma issue pra isso".
---

# Follow-up issue

A **follow-up issue** hands one open problem from this session to the backlog, so its fate stops depending on anyone reading a chat summary or a PR body. The reader is a future agent or maintainer with none of this session's context. They must be able to act on the issue cold, without re-deriving anything.

Synthesize from what you already know and what you capture below. Filing is internal: no interview, no confirmation round with the user.

## Steps

1. **Qualify: absorb whatever the context can close.** An issue is the rare exception. A finding is **absorbed** into the running task whenever the context already holds the evidence to act on it, or understanding and fixing it is small work from where you stand. That holds when it grows the diff, needs a design choice, or falls outside the ticket's acceptance criteria: the finding came from this task, so this task delivers it.
   - **In code:** fix it test-first, add it as a Definition-of-Done item, verify it with fresh command output.
   - **In a task with no code** (triage, grilling, spec, review of a plan): add it to the running issue's scope, as an acceptance criterion or a slice, in the same comment or brief that records the task's outcome.
   - **A decision only the user can make:** ask it now (`AskUserQuestion`), then absorb the answer. An agent running AFK decides, records the decision in its handoff, and absorbs.

   File an issue **only** when one of these holds:
   - **(a) Suspicion.** You saw a sign of a problem but hold no evidence that it is real, and settling it needs an investigation of its own: a reproduction you cannot run here (production data, a live service, a rare timing), or a question whose answer could be "not a problem". A finding you already traced to a `file:line` is evidence, not a suspicion.
   - **(b) Owned external resource.** A tool, plugin, skill, MCP server, or repo used in the current flow misbehaves, and its repo owner is the same account (`gh api user -q .login`) or an org that account owns. The current task does not own the resource, so there is nothing to fix in place.

   Neither holds:
   - **Third-party resource the user does not own:** file no issue. Work around it, and record the workaround as an Applied Learning bullet in the project's root `CLAUDE.md`.
   - **Anything else:** absorb it. When the user explicitly asks for an issue ("abre uma issue"), the user's request is the qualification; skip the gate.

   Every absorbed item gets one line in the final summary, PR body, handoff, or triage comment (`absorbed: <what>, verified by <command or where it was added>`), so the extra scope stays reviewable.
   *Done when:* every finding is absorbed and verified, or you can state in one line why it is a suspicion (what evidence is missing and what would produce it) or an owned external defect.

2. **Resolve the tracker.** Case (b): the issue goes in the **resource's own repo**, not the current project's; for `agent-engineering-toolkit` plugins, hand off to the `orchestrate-upstream-issues` skill instead. Case (a): read the project `CLAUDE.md` for an issue-tracker section, then `docs/agents/issue-tracker.md` if it exists. Otherwise use `gh repo view --json nameWithOwner`. Read the label vocabulary from `docs/agents/triage-labels.md` or `gh label list`.
   *Done when:* you hold an `owner/repo` and the list of labels that actually exist there. `gh issue create --label <missing>` fails the whole create, so apply only existing labels.

3. **Dedupe.** Search open and closed issues for the same defect: `gh search issues --repo owner/repo "<key terms>"` with two or three phrasings (the symptom, the file or symbol, the mechanism).
   *Done when:* either no match exists, or you found one. On a match, add a comment with your new evidence (`gh issue comment N --body-file …`), report its URL, and stop.

4. **Capture fresh evidence.** Run the reproducing command this turn and keep its output verbatim; quote the shortest decisive lines. Record `git rev-parse --short HEAD`, so every `file:line` stays interpretable after the lines drift. Prefer permalinks (`https://github.com/owner/repo/blob/<sha>/path#L10-L20`) for a GitHub remote.
   *Done when:* every claim in the Finding section maps to output captured this turn or to a pinned `file:line`. A claim you could not reproduce is labelled *hypothesis* in the body. For a suspicion, the body also states what evidence is missing, and its **Options** are the investigations that would confirm or refute it.

5. **Write the body.** Fill the template below into a file in the scratchpad directory. Every section is present; a section with nothing to say reads `None known.` instead of being deleted, so the reader knows it was considered. Write in the language the project's rule files set for durable content (its `CLAUDE.md` or `AGENTS.md`); English where they set none.
   *Done when:* every section is filled, the title is a defect claim, and no sentence needs this session's context to make sense ("as discussed", "the earlier bug" are session leaks).

6. **Create.** `gh issue create --repo owner/repo --title "…" --body-file <path> [--label …]`. Use `--body-file`, never an inline heredoc: backticks in the body break shell quoting.
   *Done when:* you hold the new issue URL.

7. **Link back.** Add the issue reference at every place that carries the limitation: a code comment next to the workaround, a line in the doc that states the limitation, the PR body. Name the issue as `#N` or `see #N`. Keep `fix #N`, `fixes #N`, `closes #N` out of commit subjects and PR bodies until the fix is verified; GitHub auto-closes the issue on push or merge.
   *Done when:* every site that carries the limitation names the issue, and you have reported the URL to the user in one line.

## Template

The title states the defect as a claim, in present tense. Example: "No gate compares spend against the money ceiling; a reached ceiling surfaces only in parar-ou-continuar". Avoid "Investigate X" or "Problem with Y".

<issue-template>

## Context

What you were doing when you found this, in one or two sentences. The parent or tracking issue, if any ("Tracked under #10"). The commit SHA the evidence was captured at.

## Finding

What was observed, stated as fact. Every location as `file:line` pinned to the SHA above, or as a permalink.

### Reproduction

The exact command or input, then the shortest decisive lines of its output, verbatim in a code block.

### Expected vs. actual

- **Expected:** what the task definition, spec, or docs say should happen. Cite where it says so.
- **Actual:** what happens instead.

## Reason

The mechanism, not the symptom: why the code behaves this way. Tag each claim **[verified]** (you traced or ran it) or **[hypothesis]** (inferred, not confirmed).

## Impact

- **Severity:** one of:
  - `blocker`: wrong results or data loss on the normal path, with no workaround.
  - `major`: wrong results on a reachable path, or a workaround exists but is not obvious.
  - `minor`: an edge case, a cosmetic defect, or a documented workaround.
  - `polish`: nothing is wrong; an improvement or a debt item.
- **Who or what it affects:** the users, modules, docs, or runs that hit it.
- **What still works:** the paths confirmed unaffected, so nobody over-scopes the fix.

## Gotchas

The false leads you already ruled out. The constraint that makes the obvious fix wrong. The test or gate that passes and must not reassure anyone.

## Options

A numbered list. For each option: what it is, what it settles, its rough cost (small / medium / large, or hours), and its risk. End with one line: **Run first:** the option you would start with, and why.

## Acceptance criteria

Checkable conditions that tell the implementer the issue is done. Each is a command with its expected result, or an observable behavior. Include the check that goes red on the defect today and must go green after the fix.

- [ ] …

## Out of scope

What this issue deliberately does not cover, with a pointer to where it belongs if known.

## Links

The sites that carry the limitation (step 7), related issues, PRs, ADRs, and docs.

</issue-template>
