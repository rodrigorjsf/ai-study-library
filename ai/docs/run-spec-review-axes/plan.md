# Plan: Security, UX/AIX and Design axes in `/run-spec`, then import run-spec into this repo

> **Superseded 2026-11-15:** this is the executed plan of PR #3. The kit has changed since then: no code-review skill spawns, no `readonly`, and no mattpocock prerequisite. See [README.md](README.md) revision (2) and [`ai/skills/run-spec/README.md`](../../skills/run-spec/README.md).

Decisions and sources: [README.md](README.md) (pt-BR study). This plan is the execution order.

## Part A — add the three axes (edited in the repo copy, after a verbatim import commit; see B3)

### A1. Axis briefs — `~/.claude/skills/run-spec/axes/`

| File | Content |
|---|---|
| `security.md` | Brief from study §3.5: diff-only scope, OWASP Top 10:2025 + ASI01–ASI10 tags, exploit path required, HIGH/MEDIUM at confidence ≥ 8/10, hard-exclusion list, crypto/config/policy below the bar reported as `needs-human`, never dropped. |
| `ux-aix.md` | Brief from study §4.3: state coverage, actionable error text, code-checkable WCAG 2.2 AA SCs, HAX "when wrong" paths, agent-facing errors and bounded output, CLI `stderr`/`--json`. Never claims conformance; contrast/layout are `deferred-to-build`. Severity critical/warning/info. |
| `ux-aix.triggers` | One extended regex per line, matched against `git diff --name-only`: front-end files, templates, styles, i18n, design tokens, tool/MCP, CLI, prompt files. |
| `design.md` | Brief from study §5.3: `codebase-design` vocabulary verbatim, only modules the diff creates or whose interface it changes, deletion test with caller count, test past the interface, one-adapter seam, locality, `GLOSSARY.md`/ADR. Leaves Speculative Generality, Middle Man, Shotgun Surgery to Standards. Severity Strong / Worth exploring / Speculative. |

Every brief ends its report with a heading `## <Axis>` and a last line `COUNT: <n>` (Security: `COUNT: <n> blocking, <m> needs-human`), so the dispatcher counts without reading findings.

### A2. `run-spec/SKILL.md` step 6

- Item 1 gains a sub-item: in the same message as the code-review skill's two spawns, spawn one `ticket-reviewer` per new axis. Each prompt: the axis brief pasted in full, the diff command and commit list for the round's fixed point, SPEC, the known dismissals, and in round 3 the same "check only `fixed`" restriction.
- UX/AIX gate, before spawning: `git diff --name-only <fixed point>...WORK | grep -E -q -f ${CLAUDE_SKILL_DIR}/axes/ux-aix.triggers`. No match → no spawn; the report carries `## UX/AIX` with `skipped: no UI or agent-surface files`. The dispatcher contract forbids it reading the spec, so the gate is the file list only.
- Item 2: the report is the skill's aggregate plus the three sections, in the order Standards, Spec, Security, UX/AIX, Design. Chat line: `review <r>: Standards <x>, Spec <y>, Security <z>, UX/AIX <w|skipped>, Design <v>`.
- Item 3: the loop exits when Standards, Spec and Security's blocking count are all zero. If UX/AIX, Design or Security `needs-human` findings remain, run item 4 once for them and go to step 7 without a new round.
- Contract toolbox line names the axis files.

### A3. `review-fixer.md`

- Description and inputs: five sections, not two.
- IDs: `S`, `SP`, `SEC`, `UX`, `D`.
- Security finding = bug: fix test-first when testable. A `needs-human` finding is fixed only at >80% confidence, else output `needs-human` (never `dismissed`).
- UX/AIX and Design = judgement calls, same rule as Standards.
- Output status set gains `needs-human`; validation count unchanged.

### A4. `ticket-reviewer.md`

- Description and body: "one axis (Standards, Spec, Security, UX/AIX or Design)".
- Add `readonly: true` for Cursor, which ignores `tools:`.

### A5. Not changed

`ticket-implementer` per-ticket review stays two-axis. `wave-integrator`, `followup-triager`, `tickets.py`, `watchdog.sh`, `QUEUE.md` untouched.

### A6. Check

- `grep` that no file still says the final review is two-axis where it now is five.
- `bash -n` on scripts; the trigger regex file runs through `grep -E -f` against a sample file list (a `.tsx` matches, a `.py` service file does not).
- No live `/run-spec` run in this task: the flow stays untested end to end (as the 2026-11-12 changes already are). Say so in the report.

## Part B — import run-spec into this repo as one flow

### B1. Layout

```
ai/skills/run-spec/
  SKILL.md, QUEUE.md, tickets.py, watchdog.sh, axes/   (copied from ~/.claude/skills/run-spec, no __pycache__)
  agents/ ticket-implementer.md ticket-reviewer.md wave-integrator.md followup-triager.md review-fixer.md
  README.md   the single-flow document
  install.sh  copies skill → ~/.claude/skills/run-spec, agents → ~/.claude/agents (as copies, like gauntlet)
```

### B2. `README.md` (English; repo convention for skills)

- One flow diagram (Mermaid): resolve → branch → recover → frontier → wave (worktree, implement, collect, integrate, triage) → final review (5 axes, gate) → clean → publish → queue.
- Artifact inventory: every file above with role; external prerequisites — `mattpocock-skills` plugin pinned 1.3.1 (`code-review`, `tdd`, `to-spec`, `to-tickets`, `setup-matt-pocock-skills`), `follow-up-issue` skill, `docs/agents/issue-tracker.md` and optional `docs/agents/run-spec.md` in the target repo, `git`, `gh`, `python3`, optional `codegraph` and `pnpm`.
- Run records in `$STATE` (from SKILL.md variables).
- Claude Code vs Cursor section (repo CLAUDE.md rule): install paths, how context reaches each agent, MCP/hooks not used, parity gaps (no `ListAgents`/`SendMessage` equivalents verified, `readonly` vs `tools`, Bugbot via `.cursor/BUGBOT.md` links).
- Update `ai/skills/README.md` table and `ai/docs/README.md` index rows (study + Bugbot mirror).

### B3. Ship

Branch `feat/run-spec-in-repo`, commits (study + Bugbot mirror; run-spec import; axes), push, PR, merge to `main` (user asked), then `post-merge` cleanup.
