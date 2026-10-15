# Handoff: Cursor distribution overhaul (rules-first cursor-initializer + new cursor-customizer)

**Created:** 2026-05-01 ~23:30
**Branch:** `development` (main worktree)
**Session Duration:** ~3-4 hours

---

## Summary

Designed and started implementing a multi-PR effort to (a) refactor the existing `cursor-initializer` plugin to be rules-first and product-strict, and (b) create a new `cursor-customizer` plugin mirroring `agent-customizer` but Cursor-native. Foundation PR (CONTEXT.md + 3 ADRs) and the first two implementation slices (cursor-initializer refactor + cursor-customizer scaffold) are **merged into `development`**. Six remaining slices (#80-#85) are filed as issues in `needs-triage` state with refined bodies, ready to be triaged and executed.

---

## Work Completed

### Changes Made

- [x] Designed the Cursor distribution architecture via `/grill-with-docs` (8 questions, all resolved)
- [x] Materialised `CONTEXT.md` with toolkit-wide domain vocabulary (Initializer/Customizer roles, distributions, artifact types, rules-first, product-strict)
- [x] Recorded 3 ADRs: `0001-cursor-distribution-rules-first.md`, `0002-product-strict-research-foundation.md`, `0003-cursor-skills-default-path.md`
- [x] Published umbrella PRD as issue #77 with 20 user stories and 22 acceptance criteria
- [x] Sliced PRD into 8 vertical issues (#78–#85) via `/to-issues` with full dependency graph
- [x] Triaged #78 and #79 to `ready-for-agent` with full agent briefs (Key interfaces + Out of scope sections)
- [x] Caught and corrected cross-issue inconsistency on shared-references convention; refined bodies of #79–#83
- [x] Spawned 2 general-purpose agents in isolated worktrees, each implementing one slice in parallel
- [x] Extended agent A's scope to update `cursor-initializer-quality-gate` and cross-distribution `quality-gate` meta-skills broken by the refactor
- [x] Pushed both branches (after user-mediated SSH push); opened PR #86 (cursor-initializer) and PR #87 (cursor-customizer foundation)
- [x] Both PRs **merged** into `development`; issues #78 and #79 auto-closed

### Key Decisions

| Decision | Rationale | Alternatives Considered |
|---|---|---|
| Plugin name `cursor-customizer`, 1:1 paridade with `agent-customizer` | Same mental model across distributions; user only swaps namespace prefix | `cursor-artifact-customizer`, `cursor-craft`, polymorphic `create-artifact` skill |
| Rules-first for cursor-initializer; AGENTS.md as legacy input only | `.cursor/rules/*.mdc` supports 4 activation modes mapping cleanly to one-concern-per-rule; user explicit preference | Strip AGENTS.md entirely (loses legacy projects); rules-first with optional AGENTS.md (reintroduces monolith) |
| Decomposition heuristic: tooling-non-obvious → file-pattern → monorepo → on-demand | ETH study showed minimal developer-written files win; this captures highest-ROI signal first | File-pattern primary, monorepo primary, single-eixo |
| Product-strict on Claude branding; vendor-neutral research permitted as "Industry Research" | Goal is preventing Claude Code conventions leaking into Cursor outputs, not suppressing public research | Strict (ban any Anthropic-authored content); flexible (allow Anthropic engineering posts as guidance) |
| `.cursor/skills/` default for `cursor-customizer:create-skill` | Matches plugin namespace; simpler troubleshooting | `.agents/skills/` (open-standard portable); interactive prompt |
| 8 vertical slices instead of 5 PRs | Per-artifact-type slices (rules/hooks/skills/subagents) are independently demoable; enables 4-way parallelism after foundation lands | 5 coarse PRs matching original plan; 10 finest-grained slices |
| Shared references copied per-skill, not at plugin root | Matches existing `agent-customizer` convention encoded in root `CLAUDE.md` | Plugin-root canonical source with skills referencing |
| Expand `cursor-initializer-quality-gate` + `quality-gate` updates into slice A's scope | Meta-skills assert names of files slice A removed; otherwise AC #9 fails on false positives | Defer to follow-up issue; ignore until later slice |

---

## Files Affected

### Created (in PR #76, already merged)

- `CONTEXT.md` — toolkit domain vocabulary (root)
- `docs/adr/0001-cursor-distribution-rules-first.md`
- `docs/adr/0002-product-strict-research-foundation.md`
- `docs/adr/0003-cursor-skills-default-path.md`

### Created (in PR #87, already merged)

- `plugins/cursor-customizer/.cursor-plugin/plugin.json`
- `plugins/cursor-customizer/agents/artifact-analyzer.md`
- `plugins/cursor-customizer/README.md`
- `plugins/cursor-customizer/CLAUDE.md`
- `plugins/cursor-customizer/docs-drift-manifest.md`
- `plugins/cursor-customizer/skills/.gitkeep`

### Modified (in PR #86, already merged)

- `plugins/cursor-initializer/agents/scope-detector.md` → renamed to `rule-domain-detector.md`
- `plugins/cursor-initializer/agents/file-evaluator.md` — dual responsibility expansion
- `plugins/cursor-initializer/skills/init-cursor/SKILL.md` — drop AGENTS.md generation; use `rule-domain-detector`
- `plugins/cursor-initializer/skills/improve-cursor/SKILL.md` — add non-destructive AGENTS.md migration sub-flow
- `plugins/cursor-initializer/skills/{init,improve}-cursor/assets/templates/` — replace AGENTS.md and generic `.mdc` templates with three activation-mode variants (`cursor-rule-always.mdc`, `cursor-rule-globs.mdc`, `cursor-rule-description.mdc`)
- `plugins/cursor-initializer/skills/{init,improve}-cursor/references/validation-criteria.md` — refresh under rules-first
- `plugins/cursor-initializer/README.md` — product-strict rewrite
- `plugins/cursor-initializer/CLAUDE.md` — product-strict rewrite reflecting renames
- `plugins/cursor-initializer/.cursor-plugin/plugin.json` — description update
- `.claude/rules/cursor-plugin-skills.md` — descriptive bullet updated for rules-first
- `.claude/skills/cursor-initializer-quality-gate/{SKILL.md, agents/*.md, references/*.md}` — aligned with rules-first artifact names
- `.claude/skills/quality-gate/agents/parity-checker.md` — dropped cross-distribution checks for removed cursor-initializer files

### Deleted (in PR #86)

- `plugins/cursor-initializer/AGENTS.md` — incoherent with rules-first stance
- `plugins/cursor-initializer/skills/{init,improve}-cursor/assets/templates/{root-agents-md.md, scoped-agents-md.md}`
- `plugins/cursor-initializer/skills/{init,improve}-cursor/assets/templates/cursor-rule.mdc` (the generic single template)
- `plugins/cursor-initializer/agents/scope-detector.md` (renamed)

### Read (Reference)

- `plugins/agent-customizer/` — entire plugin used as topology model for `cursor-customizer`
- `docs/cursor/{rules/rules.md, skills/agent-skills-guide.md}` — Cursor official documentation
- `.claude/rules/{plugin-skills, agent-files, cursor-*, reference-files, readme-files}.md`

---

## Technical Context

### Architecture/Design Notes

The toolkit is now formally a multi-distribution marketplace:

- **Claude Code distribution**: `agents-initializer` + `agent-customizer` (unchanged in this work)
- **Cursor distribution**: `cursor-initializer` (refactored rules-first) + `cursor-customizer` (new, partial — only foundation landed)
- **Standalone distribution**: `skills/` at repo root (unchanged)

Each distribution follows the **Initializer/Customizer pattern**:
- *Initializer* = project-wide bootstrap (holistic, multi-artifact)
- *Customizer* = single-artifact CRUD (surgical, per-artifact-type)

Boundary makes `improve-cursor` (initializer, holistic) orthogonal to `cursor-customizer:improve-rule` (customizer, single-rule).

### Worktrees Still Locked

Two worktrees remain after the merges. Should be cleaned up:

```bash
git worktree remove /home/rodrigo/Workspace/agent-engineering-toolkit/.claude/worktrees/agent-a3b7298b537438c51 --force
git worktree remove /home/rodrigo/Workspace/agent-engineering-toolkit/.claude/worktrees/agent-ad3709b137fdac74c --force
```

The `--force` is needed because they're locked. Branches `feat/cursor-initializer-rules-first` and `feat/cursor-customizer-foundation` can also be deleted locally and on origin if desired.

### Configuration Changes

None.

---

## Things to Know

### Gotchas & Pitfalls

- **SSH push fails in this session environment** — no `ssh-askpass`. The user pushes manually via `!git push ...` in their prompt. Plan PR creation flows accordingly: do the work, ask user to push, then `gh pr create`.
- **`git ls-remote` also hangs** — same SSH issue. Use `gh api repos/.../branches/<name>` instead to verify branch state on origin.
- **Worktrees inherit dirty working tree from main repo** but do NOT push it — only commits. The pre-existing modified files on `development` (`.claude/settings.json`, `CLAUDE.md`, wiki pages, etc.) stay in the working tree and don't pollute branches.
- **`cd` persists in Bash tool between commands** — be careful when navigating into worktrees to `cd` back to the main repo before subsequent commands.
- **Banned tokens for product-strict** — full list: `CLAUDE.md`, `.claude/`, `tools:`, `maxTurns:`, `paths:`, `${CLAUDE_SKILL_DIR}`, `docs.anthropic.com/en/docs/claude-code/*`. Verify after every plugin file generation with: `grep -rE "(\$\{CLAUDE_SKILL_DIR\}|CLAUDE\.md|\.claude/|maxTurns:|tools:|paths:|docs\.anthropic\.com/en/docs/claude-code)" plugins/cursor-customizer/`. The literal "Claude" string is OK only in model names ("Claude Opus", "Claude Sonnet") inside the standard "Cost and Model Guidance" block.
- **Reference file convention**: shared references like `prompt-engineering-strategies.md` are copied **per-skill** into each skill's `references/` directory. There is NO plugin-root `references/`. This is encoded in the root `CLAUDE.md` and was the cross-issue refinement that fixed bodies of #79–#83.

### Assumptions Made

- Auto-merge of PRs by user is acceptable — both PR #86 and #87 merged within minutes of opening
- Atomic commits per concern are mandatory per project's git conventions in root `CLAUDE.md` (one logical change per commit; no `git add -A` across unrelated changes)
- The `cursor-initializer-quality-gate` skill is a project meta-skill (under `.claude/skills/`, not distributed). Updating it is in scope when the plugin it validates changes structurally.

### Known Issues

- The two worktrees at `.claude/worktrees/agent-{a3b7298b537438c51,ad3709b137fdac74c}/` are still locked. Cleanup needed (see Commands to Run).

---

## Current State

### What's Working

- ✅ PR #76 merged → CONTEXT.md + 3 ADRs on `development`
- ✅ PR #86 merged → cursor-initializer is fully rules-first, product-strict, with quality-gate meta-skill aligned
- ✅ PR #87 merged → cursor-customizer plugin scaffold landed; manifest, artifact-analyzer, README, CLAUDE.md, drift manifest skeleton all in place
- ✅ Issues #78, #79 auto-closed by PR merges
- ✅ All eight slice issues (#78-#85) have been published with full bodies; six remaining (#80-#85) have bodies refined for shared-references convention

### What's Not Working / Pending

- ⏳ Slice C (#80) — `cursor-customizer` rules support — `needs-triage`
- ⏳ Slice D (#81) — `cursor-customizer` hooks support — `needs-triage`
- ⏳ Slice E (#82) — `cursor-customizer` skills support — `needs-triage`
- ⏳ Slice F (#83) — `cursor-customizer` subagents support — `needs-triage`
- ⏳ Slice G (#84) — `cursor-customizer` quality gate — `needs-triage`, blocked by #80–#83
- ⏳ Slice H (#85) — Cursor distribution governance + repo-level integration — `needs-triage`, blocked by all upstream

### Tests

- [x] Banned-tokens grep on `plugins/cursor-initializer/` returns 0 hits
- [x] Banned-tokens grep on `plugins/cursor-customizer/` returns 0 hits
- [x] All 11 ACs of #78 satisfied (verified by agent A)
- [x] All 8 ACs of #79 satisfied (verified by agent B)
- [ ] No fixture-based smoke tests yet (out of scope per PRD)
- [ ] `cursor-initializer-quality-gate` and `cursor-customizer-quality-gate` skills not yet executed end-to-end (only inline-validated)

---

## Next Steps

### Immediate (Start Here)

1. **Clean up the two worktrees** — both branches landed, worktrees no longer needed:
   ```bash
   git worktree remove /home/rodrigo/Workspace/agent-engineering-toolkit/.claude/worktrees/agent-a3b7298b537438c51 --force
   git worktree remove /home/rodrigo/Workspace/agent-engineering-toolkit/.claude/worktrees/agent-ad3709b137fdac74c --force
   git branch -D feat/cursor-initializer-rules-first feat/cursor-customizer-foundation 2>/dev/null
   ```

2. **Triage and execute slices C–F in parallel** — these are the four per-artifact-type slices (#80, #81, #82, #83). All four depend only on #79, which is merged. They can all execute in parallel via 4 isolated worktrees with 4 general-purpose agents. Each slice has a refined body listing exactly which reference files (including type-specific evaluation/config/events files plus the shared `prompt-engineering-strategies.md` per-skill copies; #82 also needs `behavioral-guidelines.md`).

3. **After C–F merge, triage and execute slice G (#84)** — quality-gate skill for cursor-customizer + `docs-drift-checker` subagent. Mirror of `cursor-initializer-quality-gate` but for the new plugin.

4. **After G merges, triage and execute slice H (#85)** — final tracer: governance expansion (`.claude/rules/cursor-*`), `.cursor-plugin/marketplace.json` update to advertise both plugins, root `README.md`, root `CLAUDE.md`. PRs 4 and 5 from the original plan are combined into this single slice.

### Subsequent

- Close umbrella issue #77 once all 8 slices ship (it has no auto-close because each child PR closes only its own slice)
- Consider follow-up PRD for fixture-based smoke tests (currently out of scope)
- Consider scheduling a routine to run drift-checker periodically once it lands in slice G

### Blocked On

- Nothing immediate — all four next slices (#80–#83) are unblocked

---

## Related Resources

### Documentation

- **PRD (umbrella issue):** https://github.com/rodrigorjsf/agent-engineering-toolkit/issues/77
- **Open slices:**
  - #80 https://github.com/rodrigorjsf/agent-engineering-toolkit/issues/80 (rules)
  - #81 https://github.com/rodrigorjsf/agent-engineering-toolkit/issues/81 (hooks)
  - #82 https://github.com/rodrigorjsf/agent-engineering-toolkit/issues/82 (skills)
  - #83 https://github.com/rodrigorjsf/agent-engineering-toolkit/issues/83 (subagents)
  - #84 https://github.com/rodrigorjsf/agent-engineering-toolkit/issues/84 (quality gate)
  - #85 https://github.com/rodrigorjsf/agent-engineering-toolkit/issues/85 (governance + repo-level)
- **Merged PRs:**
  - #76 (foundation) https://github.com/rodrigorjsf/agent-engineering-toolkit/pull/76
  - #86 (cursor-initializer rules-first) https://github.com/rodrigorjsf/agent-engineering-toolkit/pull/86
  - #87 (cursor-customizer foundation) https://github.com/rodrigorjsf/agent-engineering-toolkit/pull/87
- **Local design docs:** `CONTEXT.md` (root), `docs/adr/0001-*.md`, `docs/adr/0002-*.md`, `docs/adr/0003-*.md`

### Commands to Run

```bash
# Cleanup worktrees
git worktree remove /home/rodrigo/Workspace/agent-engineering-toolkit/.claude/worktrees/agent-a3b7298b537438c51 --force
git worktree remove /home/rodrigo/Workspace/agent-engineering-toolkit/.claude/worktrees/agent-ad3709b137fdac74c --force

# Verify development is up-to-date
git fetch origin development && git log --oneline origin/development -5

# Triage next slice (e.g., #80)
gh issue view 80 --comments

# Validate banned tokens before any future cursor-distribution PR
grep -rE "(\$\{CLAUDE_SKILL_DIR\}|CLAUDE\.md|\.claude/|maxTurns:|tools:|paths:|docs\.anthropic\.com/en/docs/claude-code)" plugins/cursor-customizer/
grep -rE "(\$\{CLAUDE_SKILL_DIR\}|CLAUDE\.md|\.claude/|maxTurns:|tools:|paths:|docs\.anthropic\.com/en/docs/claude-code)" plugins/cursor-initializer/
```

### Search Queries

If you need to find more context:

- `grep -r "rules-first" CONTEXT.md docs/adr/` — find the rules-first stance encoded in domain docs
- `grep -r "product-strict" CONTEXT.md docs/adr/` — find the branding rule
- `find plugins/agent-customizer/skills -name "references" -type d` — topology model for cursor-customizer's per-skill references
- `gh issue list --label needs-triage --json number,title` — open slices waiting for triage

---

## Open Questions

- [ ] Should slices #80–#83 be executed sequentially (one at a time, observing each) or in parallel (4 worktrees, 4 agents at once)? User's earlier preference was parallel for #78/#79, which worked.
- [ ] Does the user want the umbrella issue #77 closed manually after all slices ship, or should it stay open for retrospective purposes?
- [ ] After slice H lands, does the user want a periodic drift-checker routine scheduled (the docs-drift-checker subagent could be invoked weekly)?

---

## Session Notes

- The grilling session resolved 8 design questions before any code was written; this paid off massively when the implementing agents needed only minor scope expansion (the meta-skill alignment) and zero rework.
- The `to-issues` quiz step caught one early but the cross-issue shared-references inconsistency was caught later during #79 triage; resulting refinement applied to bodies of #79–#83. This is a good reminder to inspect actual file structure (e.g., `find plugins/agent-customizer -name "behavioral-guidelines.md"`) when writing acceptance criteria, not just rely on conceptual knowledge of the convention.
- The two parallel agents handled the work well; agent A surfaced multiple decisions beyond the brief (init-cursor preflight, additional reference-file rewrites, `allowed-tools:` removal in a template) that all turned out correct on review. Agent B caught a literal "Claude-Code" leak via advisor that the validation grep missed.
- The user merged both PRs within minutes of opening, suggesting trust in the agent-implemented work plus thorough acceptance criteria upfront.

---

_This handoff was generated at context window capacity. Start a new session and use this document as your initial context._
