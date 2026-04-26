# Handoff: Harness Engineering Research + Knowledge Graph Wiki

**Created:** 2026-04-25 12:06 BRT
**Branch:** main
**Session Duration:** ~1.5 hours
**Working Directory:** `/home/rodrigo/Workspace/ai-study-library/`

---

## Summary

Built a knowledge-graph (graphify deep mode) over `ai/docs/` (117 files, 272K words → 476 nodes / 665 edges / 21 communities), then ran a parallel-subagent research pass over `reference/prp-agentic-engineering` and the corpus to produce a single comprehensive harness-engineering reference document at `dev/research/2026-04-25-harness-engineering-research.md`. Generated the agent-crawlable wiki under `graphify-out/wiki/` and wrote a complete `graphify-out/README.md` cross-referencing the research doc. All artifacts are written to disk; nothing committed.

---

## Work Completed

### Changes Made

- [x] Ran `/graphify ./ai/docs --mode deep` — built graph (476 nodes, 665 edges, 21 communities)
- [x] Generated `graphify-out/{graph.html, graph.json, GRAPH_REPORT.md, manifest.json, cost.json}` + `cache/`
- [x] Dispatched 3 parallel research sub-agents (reference project / ai/docs themes / graphify-out inspection)
- [x] Wrote `dev/research/2026-04-25-harness-engineering-research.md` (70.8 KB) — research synthesis + LLM reference guide combined
- [x] Generated `graphify-out/wiki/` (31 articles + index.md) via direct call to `graphify.wiki.to_wiki`
- [x] Wrote `graphify-out/README.md` (12.6 KB) — full README with stats, files, god nodes, communities, surprising connections, wiki usage, reproduction commands, honesty notes, references to research doc

### Key Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|-------------------------|
| Single combined research+guide document | User said "crie um documento completo" (singular). Research synthesis is the audit trail; reference guide is the deliverable; combining preserves citation context | Two separate files (research.md + guide.md) — rejected, more navigation overhead |
| Parallel sub-agents instead of sequential reads | research-codebase skill mandates parallel agents for context isolation. 3 independent scopes (reference project / ai-docs themes / graphify-out) | Single agent reading everything — would blow out main context |
| Generate wiki via direct Python API, not full pipeline rerun | Graph already built and cached; wiki step (Step 6b) only needs G + communities + labels. Avoids re-running extraction | Full `/graphify --wiki` rerun — wasteful since cache hit on all 117 files |
| Use general-purpose subagent type (not Explore) | Skill instructions mandate general-purpose for chunk extraction (Explore is read-only, can't write chunk files) | Explore — would silently drop extraction results |
| Skip TDD/two-stage-review pattern from subagent-driven-development skill | Task is research + doc creation, not code implementation. Two-stage review (spec + quality) doesn't fit research deliverables | Force the pattern — would add overhead without quality gain |

---

## Files Affected

### Created

- `dev/research/2026-04-25-harness-engineering-research.md` — canonical harness engineering reference (70.8 KB, frontmatter + 17-section guide + citations)
- `graphify-out/README.md` — graphify-out directory entry point (12.6 KB)
- `graphify-out/GRAPH_REPORT.md` — auto-generated audit report
- `graphify-out/graph.html` — interactive D3 viz (385 KB)
- `graphify-out/graph.json` — raw graph data (502 KB)
- `graphify-out/manifest.json` — corpus snapshot for `--update`
- `graphify-out/cost.json` — token cost log (18.5K input / 4.2K output)
- `graphify-out/cache/` — per-file semantic-extraction cache (115 files)
- `graphify-out/wiki/index.md` + 30 article `.md` files (one per community + per god node)
- `graphify-out/.graphify_python` — pinned Python interpreter
- `.claude/handoffs/HANDOFF_HARNESS_ENGINEERING_RESEARCH_04_25_12_06.md` — this file

### Read (Reference)

- `reference/prp-agentic-engineering/CLAUDE.md`, `plugins/prp-core/CLAUDE.md`, `plugins/prp-core/references/*.md`, `rules/*.md`, `skills/*/SKILL.md`, `agents/*.md`, `hooks/hooks.json`, `scripts/prp_core_prompt_eval.py`, `tests/prp-core/prompt-cases.json` — sub-agent A used these for project inventory
- `ai/docs/harness-engineering/*.md`, `ai/docs/context-engineering/*.md`, `ai/docs/general-llm/research-context-rot-and-management.md`, `ai/docs/analysis/*.md`, `ai/docs/shared/skills-standard/*.md`, `ai/docs/claude-code/hooks/*.md`, `ai/docs/spec-driven-development/*.md` — sub-agent B mapped corpus by theme
- `graphify-out/GRAPH_REPORT.md`, `graph.json`, `cost.json`, `manifest.json` — sub-agent C inspected outputs

### Modified

None — only new files written.

### Deleted

- Cleaned up internal graphify temp files (`.graphify_detect.json`, `.graphify_extract.json`, `.graphify_ast.json`, `.graphify_semantic.json`, `.graphify_analysis.json`, `.graphify_labels.json`, `.graphify_chunk_*.json`) per skill cleanup step

---

## Technical Context

### Architecture/Design Notes

The research document's reference guide is structured so an LLM agent can copy artifact templates verbatim:

- **17 sections** mapping definition → artifact taxonomy → CLAUDE.md/AGENTS.md → rules → references → skills → subagents → hooks → long-running context maintenance → verification gate → critic patterns → agent protocols → CI evals → plugin packaging → 4 orchestration recipes (RPI / Ralph loop / multi-agent research team / parallel code review) → step-by-step new-project sequence → quality heuristics

- **Five canonical references** (copyable from `reference/prp-agentic-engineering/plugins/prp-core/references/`): `harness-taxonomy.md`, `context-budget-policy.md`, `execution-policy.md`, `artifact-lifecycle.md`, `agent-prompt-style.md`

- **Reference project's recent harness arc** (5 commits identified): `0364b91` (context optimization + critic) → `09b325c` (verification before completion) → `890a792` (advisor + Phase 4.6 gate) → `7c49f49` (advisor wired into agents) → `fdb1d20` (references layer + CI evals + wiki)

### Dependencies

- `graphifyy` Python package (already installed; pinned interpreter at `graphify-out/.graphify_python`)
- No new dependencies added

### Configuration Changes

None.

---

## Things to Know

### Gotchas & Pitfalls

- Graphify wiki step needs `G + communities + labels + cohesion + gods`. Skill's standard Step 6b reads from `.graphify_analysis.json` and `.graphify_labels.json` which were cleaned up — direct API call to `to_wiki()` from `graph.json` is the workaround if rerunning wiki only.
- Sub-agent dispatch must use `subagent_type="general-purpose"` for chunk-extraction work. Explore type is read-only and silently fails to write chunk files.
- Reference project commit `fdb1d20` (Apr 22, 2026) is the consolidation commit — adds 21,813 lines including all five `references/` policy files, `harness-engineering` rule, prompt-eval CI, and the 70+ wiki/knowledge pages. Read this commit for the full harness shape.

### Assumptions Made

- Date assumed as 2026-04-25 (per system context).
- `dev/research/` chosen as research doc location per `/research-codebase` skill convention.
- Community labels (21) hand-assigned during graphify run; labels persist in `graph.json` as node `community` attribute. Wiki regeneration re-applied the same label dict.

### Known Issues

- **180 nodes are isolated** (≤1 connection) in the graph — long tail not surfaced by wiki. Documented honestly in `graphify-out/README.md`.
- **3 singleton communities** (IDs 18-20: JSON Schema Behavior, Refusal Edge Case, MCP Runtime) are noise candidates flagged automatically.
- **1 sensitive file skipped** during detection (`ai/docs/context-engineering/million-token-context-window-syntackle.md`) — not in graph.

---

## Current State

### What's Working

- All 7 task list items completed (TaskList shows 7/7 done)
- Knowledge graph built and cached (incremental updates will be cheap)
- Research document written with full `path:line` citations to `ai/docs/` and `reference/prp-agentic-engineering/`
- Wiki generated and crawlable via Obsidian-style `[[wiki-link]]` references
- README in `graphify-out/` cross-references research doc

### What's Not Working

Nothing broken. All deliverables on disk.

### Tests

- [x] Manual verification: `ls /home/rodrigo/Workspace/ai-study-library/dev/research/` → research doc present
- [x] Manual verification: `ls /home/rodrigo/Workspace/ai-study-library/graphify-out/` → README, GRAPH_REPORT, graph.html, graph.json, wiki/, cache/, manifest, cost — all present
- [x] Wiki article count: 31 files (`graphify-out/wiki/` + index.md) confirmed
- [ ] No automated tests run (no test suite in this study-library project)

---

## Next Steps

### Immediate (Start Here)

1. **Decide on git commits.** Repo currently shows 14 untracked top-level paths (`ai/docs/*`, `dev/`, `graphify-out/`, `reference/`, `.claude/`, `.gitignore`). User has not requested commits — ask before committing. If yes, suggest separate commits per concern: (a) ai/docs corpus addition, (b) reference project addition (or git submodule?), (c) graphify-out artifacts (consider gitignoring `cache/` and `cost.json`), (d) dev/research synthesis, (e) .claude/handoffs.
2. **Decide whether to gitignore `graphify-out/cache/` and `manifest.json`.** They're regenerable. Reference project gitignores graphify-out entirely; check whether to follow that convention.
3. **Open `graphify-out/graph.html` in a browser** for visual sanity check of communities and god nodes.

### Subsequent

- Apply the harness engineering reference guide to a real project: pick a target repo, run the 11-step new-project sequence (Section 16 of research doc), and iterate.
- Run `/graphify ./ai/docs --update` periodically to keep graph current as `ai/docs/` evolves.
- Consider running graphify on `reference/prp-agentic-engineering` itself (not just docs) to map the harness implementation as a graph.
- Investigate the 4 open questions in the research doc (esp. Q1: SDD ↔ CFG Constrained Decoding — may be productive to write).

### Blocked On

Nothing.

---

## Related Resources

### Documentation

- `dev/research/2026-04-25-harness-engineering-research.md` — primary deliverable
- `graphify-out/README.md` — graph-base entry point
- `graphify-out/GRAPH_REPORT.md` — auto audit
- `reference/prp-agentic-engineering/README.md` — reference project intro
- `~/.claude/skills/graphify/SKILL.md` — graphify pipeline reference

### Commands to Run

```bash
# Verify deliverables
ls -la dev/research/ graphify-out/

# Re-open the interactive graph
xdg-open graphify-out/graph.html  # or wslview

# Incremental graph rebuild after editing ai/docs/
/graphify ./ai/docs --update

# Query the graph
/graphify query "How does progressive disclosure relate to subagents?"
/graphify path "Progressive Disclosure" "Lost in the Middle"
/graphify explain "RPI Workflow"

# Inspect git state before deciding commits
git status --short
git log --oneline -10

# Check the reference project's recent harness arc
cd reference/prp-agentic-engineering && git log --oneline -20
```

### Search Queries

- `grep -rn "Smart Zone" ai/docs/` — finds the 40%/70% threshold sources
- `grep -rn "Lost in the Middle" ai/docs/` — finds primary + analysis docs
- `grep -rn "back-pressure\|back pressure" ai/docs/harness-engineering/` — finds verification patterns
- `grep -rn "progressive disclosure" ai/docs/` — finds the cross-cutting principle (top god node, 20 edges)
- `find reference/prp-agentic-engineering/plugins/prp-core -name "SKILL.md" | xargs head -10` — quick scan of all plugin skills

---

## Open Questions

- [ ] Do graphify-out `cache/`, `manifest.json`, `cost.json` belong in git, or gitignore?
- [ ] Should `reference/prp-agentic-engineering/` be a git submodule (it's its own repo with own remote `https://github.com/rodrigorjsf/prp-agentic-engineering.git`) or vendored?
- [ ] Does the user want commits created from this work, or stage only?
- [ ] Should the harness engineering reference guide be copied / symlinked into a more discoverable location (e.g. project root `HARNESS_ENGINEERING.md`) or kept under `dev/research/`?

---

## Session Notes

- Workflow used: parallel research sub-agents → synthesis → write artifact → graphify wiki API → README. Execution time mostly absorbed by 3 parallel research agents (longest ~6.8 min, sub-agent A on reference project).
- Caveman mode active in chat per session-start hook; docs themselves written in normal prose.
- TaskList tracked 7 tasks; all marked completed.
- Total token cost for graphify deep extraction this run: 18.5K input / 4.2K output (cached for incremental updates).
- One subagent (chunk 1/6) returned a result too large (77 KB) and was persisted to a tool-results file, but the chunk JSON (`graphify-out/.graphify_chunk_01.json`) was successfully written to disk and merged correctly (123 nodes, 152 edges).

---

*This handoff was generated mid-session via `/session:handoff` command. Start a new session and use this document as your initial context. Begin at "Immediate (Start Here)" → item 1.*
