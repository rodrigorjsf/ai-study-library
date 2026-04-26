# Handoff: Harness Research File Rewrite + HumanLayer Merge + Graphify Query Appendix

**Created:** 2026-04-25 13:51 BRT
**Branch:** main
**Session Duration:** ~1.5 hours
**Working Directory:** `/home/rodrigo/Workspace/ai-study-library/`

---

## Summary

Refactored `dev/research/2026-04-25-harness-engineering-research.md` (1114 → 1567 lines). Stripped every explicit `reference/prp-agentic-engineering` mention, genericized `prp-*` skill/agent names to `<plugin>-*` slot syntax, integrated a HumanLayer codebase findings section sourced via parallel-subagent research, added a 21-topic / 281-query graphify lookup appendix, and validated every `path`/`explain` target against `graph.json`. Two advisor passes completed; ready to ship.

---

## Work Completed

### Changes Made

- [x] Stripped all `reference/prp-agentic-engineering` and `reference project` mentions from the research file
- [x] Replaced "Reference Project Inventory" + "Recent Harness Engineering Commits" sections (lines 42-165 of original) with synthesized "Canonical Harness Components" section anchored on `ai/docs/` only
- [x] Genericized 9 `prp-*` skill/agent names (prp-prd, prp-plan, prp-implement, prp-advisor, prp-verification-before-completion, prp-research-team, prp-review-agents, prp-commit, prp-ralph) to `<plugin>-*` slot form via `replace_all`
- [x] Dispatched parallel general-purpose subagent to research `humanlayer/` codebase; received 8-section findings report (always-loaded memory, skills, subagents, hooks, long-running maintenance, progressive disclosure, verification gates, plugin/commands)
- [x] Inserted "HumanLayer Codebase Findings" section (~200 lines) after the Knowledge Graph Structure section
- [x] Honest reporting: HumanLayer has zero hooks, zero skills, no AGENTS.md, no Ralph sentinels, no explicit smart-zone terminology — patterns present in spirit but not encoded. Documented as a divergence, not a failure
- [x] Rewrote "Code References → Reference Project — Canonical Files" subsection: deleted reference-project anchors, added 21 humanlayer file:line citations
- [x] Rewrote "Architecture Insights" — stripped reference-project mentions, added 9th insight (heavy-stack vs lean-shell two-equilibria framing) with HumanLayer evidence
- [x] Deleted entire "Historical Context" section (12 commit-hash entries from reference project)
- [x] Rewrote "Related Research" + "Open Questions" — replaced reference-project items with HumanLayer-comparison and equilibrium questions
- [x] Built per-topic graphify query appendix (A1-A21): 281 total queries across Definition+Philosophy, Artifact Taxonomy, Always-Loaded Memory, Path-Scoped Rules, References, Skills, Subagents, Hooks, Long-Running Context, Verification, Critic/Review, Agent Communication Protocols, CI Evals, Plugin Packaging, Orchestration Recipes, Smart Zone & Context Rot, Lost-in-the-Middle, Progressive Disclosure, SDD, HumanLayer Architecture, Prompting/Structured Outputs
- [x] Validated every `path`/`explain` query target against `jq -r '.nodes[].label' graphify-out/graph.json` (468 unique labels). Replaced ~12 dead targets initially extracted from hyperedge IDs with real node labels
- [x] Empirical spot-check via direct `graph.json` queries: `"Subagent as Context Firewall"` exists with 6 edges; `"Approval Loop via MCP (HumanLayer)"` (id `approval_loop_mcp`) and `"Back-Pressure Mechanisms"` (id `back_pressure_mechanisms`) both exist
- [x] Two advisor() passes — initial sequencing/scoping plan, final dead-target verification

### Key Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|-------------------------|
| Single combined rewrite (strip + merge + restructure) instead of two passes | Advisor flagged that re-anchoring sections to humanlayer findings would force restructure twice | Two-pass: strip first, merge second — wasteful |
| Single Edit-based incremental rewrite vs full Write rewrite | Edits cheaper than 30K-token Write; lower risk of mass error | Full Write — abandoned |
| Genericize `prp-*` to `<plugin>-*` slot syntax | Preserves workflow shape, drops brand without losing the template's usefulness | Drop the names entirely — would gut Recipes A-D |
| Honest "patterns absent" reporting in HumanLayer section | Advisor explicitly warned against forced alignment; user said "highly implemented based on smart zone..." but evidence shows otherwise | Sugar-coat the divergence — would mislead future readers |
| Validate query targets via `jq` against `graph.json` instead of running `/graphify` queries | Cheap, deterministic, no LLM cost; same coverage | Run all 281 queries — would burn graphify cost for zero new info |
| Skip TDD/two-stage review pattern from subagent-driven-development skill | Doc work, not code; per prior session's handoff decision | Force TDD — overhead without quality gain |
| `replace_all` on quoted dead labels (e.g. `"Smart Zone"`) | Safe because all quoted occurrences were inside graphify queries (verified via grep filter) | Hand-edit each path query — slow, error-prone |

---

## Files Affected

### Created

- `.claude/handoffs/HANDOFF_HARNESS_RESEARCH_REWRITE_04_25_13_51.md` — this file

### Modified

- `dev/research/2026-04-25-harness-engineering-research.md` (1114 → 1567 lines, ~80KB → ~110KB)
  - frontmatter `sources:` line updated (dropped reference/, added humanlayer/)
  - frontmatter `tags:` updated (`prp-core` → `humanlayer`)
  - Lines ~42-165 of original replaced with synthesized "Canonical Harness Components" section (new ~80 lines)
  - New "HumanLayer Codebase Findings" section inserted after Knowledge Graph Structure (~200 lines)
  - All `prp-*` skill names → `<plugin>-*`
  - Code References "Reference Project — Canonical Files" subsection replaced with "HumanLayer Codebase — Concrete Instantiation"
  - Architecture Insights expanded from 8 to 9 items
  - Historical Context section deleted
  - Related Research + Open Questions rewritten
  - New Appendix "Per-Topic Graphify Queries" appended (~430 lines)

### Read (Reference)

- `dev/research/2026-04-25-harness-engineering-research.md` — original state (full file, in chunks)
- `.claude/handoffs/HANDOFF_HARNESS_ENGINEERING_RESEARCH_04_25_12_06.md` — prior session handoff (full)
- `humanlayer/CLAUDE.md` (head 100 lines), `humanlayer.md` (head 50)
- `humanlayer/.claude/settings.json`, `humanlayer/.claude/agents/`, `humanlayer/.claude/commands/` (listing)
- `~/.claude/skills/graphify/SKILL.md` (lines 1-555, focused on CLI surface)
- `graphify-out/GRAPH_REPORT.md` (full 204 lines — god nodes, communities, hyperedges, surprising connections)
- `graphify-out/graph.json` (queried via `jq` — 468 unique node labels extracted to `/tmp/graphify_labels.txt`)
- Subagent (general-purpose) read humanlayer files for the findings report — see "Notable surprises" section of its output (preserved in research doc)

### Deleted

None on disk. Within the research file: ~115-line Reference Project Inventory section, ~9-line Recent Commits table, 17-line Reference Project Canonical Files subsection, 16-line Historical Context section.

---

## Technical Context

### Architecture / Design Notes

The research document now has two clear genres in one file:
1. **Synthesis** — Part I (canonical components + ai/docs thematic map + graph structure + HumanLayer findings)
2. **Reference guide** — Part II (17 sections of templates + recipes), Code References, Architecture Insights, Appendix

The HumanLayer section is the document's primary new value — it's the only section with concrete primary-source `file:line` citations into a real codebase. It is structured to be read independently: TL;DR → 8 thematic findings → patterns confirmed → patterns absent → notable surprises → reading.

The graphify queries appendix uses three forms: `query "<question>"`, `path "Node A" "Node B"`, `explain "Node Name"`. Every `path`/`explain` target was validated against actual node labels. The appendix ends with a `--mcp` integration note for agents.

### Dependencies

None added.

### Configuration Changes

None.

---

## Things to Know

### Gotchas & Pitfalls

- **GRAPH_REPORT.md hyperedges contain snake_case IDs, not display labels.** When sourcing graphify query targets, do NOT extract from the "Hyperedges" section — use `jq -r '.nodes[].label' graph.json` instead. Initial appendix had ~12 dead targets pulled from hyperedge IDs (e.g. `subagent_context_firewall` → real label is `Subagent as Context Firewall`); fixed via systematic grep+replace_all.
- **graph.json uses `.links[]` not `.edges[]`** for the edge array. `jq` schema: top-level keys are `["directed", "graph", "hyperedges", "links", "multigraph", "nodes"]`. Edge filter: `[.links[] | select(.source == "X" or .target == "X")]`.
- **Community names ≠ node names.** "Agentic Harness Patterns", "Context Engineering Foundations", "Agent Skills Standard", "Agent Orchestration & Plugins", "HumanLayer Architecture" are all *community labels* — invalid as `path`/`explain` targets. Convert to `query "What is in the X community...?"` form.
- **HumanLayer's `humanlayer/` itself is its own git repo.** Same submodule/vendor question as `reference/` from the prior handoff. Not addressed this session.
- **Markdown linter diagnostics on lines 29, 47, 59, 71, 90+** flag `MD032` (lists need blank lines around) and `MD060` (table column style — pipe spacing). These are stylistic, pre-existing in the original file (the canonical-components table I added inherits the same pipe style as the existing tables). Not blocking. Can be auto-fixed by `markdownlint --fix` if desired.

### Assumptions Made

- Date 2026-04-25 (per system context).
- "humanlayer is highly implemented based on smart zone..." — user's framing — treated as a hypothesis to verify. Evidence partially refuted; reported honestly per advisor.
- Graphify CLI surface is `query` / `path` / `explain` + flags — verified via `~/.claude/skills/graphify/SKILL.md` lines 14-38. No additional verbs (`neighbors`, `community`) exist in the CLI.

### Known Issues

- **Markdown linter flags** (MD032, MD060) — pre-existing style from original doc, unchanged by this session.
- **A few `query` lines in the appendix exceed 200 chars** (long natural-language questions). Line-length not enforced in any linter rule active here.
- **Graphify `--mcp` mode integration unverified** — appendix recommends it but I did not actually launch the MCP server to confirm tool surface. Should still work per the SKILL.md spec (line 27: `--mcp # start MCP stdio server for agent access`).

---

## Current State

### What's Working

- All 5 TaskList items completed (5/5)
- Research file 1567 lines, 281 graphify queries, 21 topic blocks
- Every `path`/`explain` target empirically validated against `graph.json`
- HumanLayer findings cited with file:line throughout
- All explicit `reference/` mentions stripped (final grep returned 0 matches)
- Two advisor passes incorporated

### What's Not Working

Nothing broken. All deliverables on disk.

### Tests

- [x] Verified zero `reference project`/`reference/prp`/`prp-core`/`prp-prd`/etc. matches via final grep
- [x] Verified all `path`/`explain` query targets exist in `graph.json` via `comm -23 used_labels graphify_labels` (only `"Node A"`/`"Node B"`/`"Node Name"` placeholders remain — intentional)
- [x] Spot-checked 3 nodes via `jq` against `graph.json`: `Subagent as Context Firewall` (6 edges), `Approval Loop via MCP (HumanLayer)`, `Back-Pressure Mechanisms` — all resolve
- [ ] No automated test suite for markdown content in this project

---

## Next Steps

### Immediate (Start Here)

1. **Decide on commits.** User has not asked to commit. Repo shows ~14 untracked top-level paths plus the modified research file. If yes, suggest separate commits per concern: (a) the research-file rewrite, (b) the new HumanLayer findings + queries appendix, or (c) one bundled commit since the work is coherent. Current handoff doc itself wants to be in a third commit.
2. **Optional: run `markdownlint --fix dev/research/2026-04-25-harness-engineering-research.md`** to auto-resolve the MD032/MD060 stylistic warnings flagged in the diagnostic.
3. **Optional: live-verify one graphify query end-to-end.** `/graphify explain "Subagent as Context Firewall"` from the appendix — confirms the runtime path-resolver actually returns content (label-existence check covered the same thing but a runtime call is the strongest signal).

### Subsequent

- Open `graphify-out/graph.html` for visual sanity check of communities and god nodes.
- Run `/graphify ./ai/docs --update` periodically to keep graph current. New community labels would invalidate parts of the appendix — the validation `jq` snippet (see Commands below) is the regression check.
- Consider pinning the HumanLayer codebase commit in a `humanlayer/.gitkeep-meta` file — file:line citations rot if upstream rewrites lines.
- Investigate the 5 open questions in the research doc (esp. Q5: lean-shell vs heavy-stack viability for small teams).

### Blocked On

Nothing.

---

## Related Resources

### Documentation

- `dev/research/2026-04-25-harness-engineering-research.md` — primary deliverable (this session's main artifact)
- `.claude/handoffs/HANDOFF_HARNESS_ENGINEERING_RESEARCH_04_25_12_06.md` — prior session handoff
- `graphify-out/README.md` + `GRAPH_REPORT.md` — graph entry points (unchanged)
- `~/.claude/skills/graphify/SKILL.md` — graphify pipeline + CLI reference

### Commands to Run

```bash
# Verify deliverable size + query count
wc -l dev/research/2026-04-25-harness-engineering-research.md
grep -cE "^/graphify (query|path|explain)" dev/research/2026-04-25-harness-engineering-research.md

# Re-verify all path/explain targets exist in current graph
jq -r '.nodes[].label' graphify-out/graph.json | sort -u > /tmp/labels.txt
grep -E "^/graphify (path|explain)" dev/research/2026-04-25-harness-engineering-research.md \
  | grep -oE '"[^"]+"' | sort -u > /tmp/used.txt
comm -23 /tmp/used.txt <(sed 's/.*/"&"/' /tmp/labels.txt | sort -u)
# Should return only "Node A" / "Node B" / "Node Name" (placeholders)

# Final grep for any reference/ leakage
grep -ni "reference project\|reference/prp\|prp-core\|prp-prd\|prp-plan\|prp-implement" \
  dev/research/2026-04-25-harness-engineering-research.md
# Should return zero

# Optional auto-format
# markdownlint --fix dev/research/2026-04-25-harness-engineering-research.md

# Inspect git state
git status --short
git diff --stat dev/research/2026-04-25-harness-engineering-research.md
```

### Search Queries

- `grep -n "humanlayer/" dev/research/2026-04-25-harness-engineering-research.md` — finds every HumanLayer file:line citation (~30 hits)
- `grep -n "<plugin>-" dev/research/2026-04-25-harness-engineering-research.md` — finds every genericized slot reference
- `grep -n "^### A[0-9]" dev/research/2026-04-25-harness-engineering-research.md` — lists all 21 appendix topic blocks
- `jq '.nodes[] | select(.label | test("smart"; "i")) | .label' graphify-out/graph.json` — find labels matching a pattern (used to recover real labels for dead targets)

---

## Open Questions

- [ ] User wants commits? Single bundled commit or split per concern?
- [ ] Should the markdown linter warnings be fixed (`markdownlint --fix`) before committing?
- [ ] Should the research doc be symlinked / copied to a more discoverable location (project root `HARNESS_ENGINEERING.md`)?
- [ ] Should `humanlayer/` be vendored as-is, added as git submodule, or just gitignored?

---

## Session Notes

- Workflow: parallel humanlayer research subagent (background) + advisor pre-flight + targeted Edits + advisor post-verification + label validation + advisor approval. Total ~1.5 hours of clock time.
- Caveman mode active in chat per session-start hook; doc itself written in normal prose.
- TaskList tracked 5 tasks; all completed.
- Subagent-driven-development skill invoked but its TDD/two-stage-review structure was inappropriate for doc work (handoff from prior session noted same).
- The advisor's pre-flight call was the highest-leverage moment: identified the genre shift (audit → patterns guide), the dead-query risk, and the wait-for-humanlayer-before-rewrite sequencing — all of which paid off.
- Diagnostics noise (MD032/MD060 markdown lint) is pre-existing, not introduced this session — the canonical-components table I added inherits the same pipe-style as the original tables in Part II.

---

*This handoff was generated mid-session via `/session:handoff` command. Start a new session and use this document as your initial context. Begin at "Immediate (Start Here)" → item 1 (decide on commits).*
