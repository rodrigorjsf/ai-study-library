# Handoff: harness-kb Brainstorm + Spec + Plan (Sub-project B) — Ready to Execute

**Created:** 2026-04-25 16:00 BRT
**Branch:** main
**Session Duration:** ~3 hours (continuation of prior session that handed off A in progress)
**Working Directory:** `/home/rodrigo/Workspace/ai-study-library/`

---

## Summary

This session shipped Sub-project A end-to-end (research-doc HumanLayer reframe — 3 commits on `main`) and then took Sub-project B (the `harness-kb` portable knowledge-stack tool) from concept → brainstorm → spec → implementation plan. B's spec and plan are written but **not yet committed**; B's implementation has **not started**. The session ended at the execution-handoff prompt for B (subagent-driven vs inline). Picking up = answer that prompt or commit B's spec/plan first.

---

## Work Completed

### Sub-project A — research-doc HumanLayer reframe (DONE, on main)

- [x] Brainstormed structure (consolidated case-study section, aggressive cleanup, full-preserve depth)
- [x] Wrote spec: `docs/superpowers/specs/2026-04-25-research-doc-humanlayer-reframe-design.md`
- [x] Wrote plan: `docs/superpowers/plans/2026-04-25-research-doc-humanlayer-reframe.md`
- [x] Executed plan via subagent-driven-development (8 tasks + final review):
  - Task 1: frontmatter `sources:` swap (humanlayer/ path → github URL)
  - Task 2: replaced `### HumanLayer Codebase Findings` (lines 218-322) with new `### Case Study: HumanLayer — Concepts from ai/docs Applied in Practice` (lines 218-273); 8-row concept→pattern table + Patterns Confirmed + Patterns Absent + Notable Surprises + Further Reading
  - Task 3: deleted `### HumanLayer Codebase — Concrete Instantiation` subsection (24 lines)
  - Task 4: reworded Architecture Insights #4, #5, #9 (dropped paths/file:line, added `(see Case Study)` cross-links)
  - Task 5: reworded Related Research items (dropped HumanLayer-specific anchors)
  - Task 6: reworded Open Questions Q5
  - Task 7: final path sweep (Summary line 26 + closing italic line 1495 reworded to `Case Study (below)` / `Case Study above`)
  - Task 8: full verification (5 grep checks) + commit
  - Final code review: APPROVED with 2 minor fixes applied (line 113 cross-reference rename, spec verification step 3 expected-count corrected from 1 to 2)
- [x] 3 commits on `main`:
  - `9d3b042` docs: add spec and plan for research-doc HumanLayer reframe
  - `df30297` docs(research): reframe HumanLayer as case study, remove paths
  - `8c8737c` docs(research): apply final review fixes

### Sub-project B — harness-kb (BRAINSTORM + SPEC + PLAN done; NOT committed; NOT executed)

- [x] Brainstormed via 8 single-question rounds (data delivery, form factor, runtime, retrieval depth, graph integration, CLAUDE.md injection depth, refresh story, naming/repo location) + extension question (research doc inclusion + naming)
- [x] Wrote spec: `docs/superpowers/specs/2026-04-25-harness-kb-design.md` (~370 lines)
  - Self-reviewed: fixed init trailing-newline ambiguity + frontmatter sources adaptation rules
  - Advisor-reviewed: fixed 4 issues (Examples block restored in CLAUDE.md injection, build pipeline `/graphify update` replaced with staleness check + clear error, 16-tool surface decision documented, "no persistent config" boundary added)
- [x] Wrote plan: `docs/superpowers/plans/2026-04-25-harness-kb-implementation.md` (~2400 lines, 18 tasks: 2 pre-flight + 16 main)
  - Self-reviewed: type contracts locked at top, spec coverage verified, no placeholders
  - Advisor-reviewed: fixed 4 issues (added `harness-kb build` hidden CLI subcommand to align spec/plan/Task14 invocations, replaced permissive MCP `inputSchema` with real per-tool `_TOOL_SCHEMAS`, expanded Task 13 doc steps with concrete templates, dropped tautological assertion in test_uninit_noop_on_empty)
- [x] Offered execution-handoff (subagent-driven vs inline) — user invoked `/session:handoff` instead

### Key Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|-------------------------|
| Sub-project A: aggressive strip, consolidated Case Study section, full-preserve depth | User said "only ai/docs-related from humanlayer findings, not direct reference" — implies max-strip + concept-anchored prose | targeted-strip, inline-distribution, table-only |
| Sub-project A: skip worktree | Research file was untracked on `main`; worktree-from-main wouldn't have the file. Single-file rewrite — isolation buys little | Add baseline commit; manual file-copy into worktree |
| Sub-project A: 2 commits only (planning + rewrite) plus 1 review-fixes commit (3 total) | User answered Q2=b (two commits) before knowing file was untracked; final-review delta was small enough to add a 3rd | Per-task commits; single bundled commit |
| Sub-project B: bundled package (option a) | Matches user's "wrapped fixed local stack" phrasing. Versioned, reproducible | Reference-paths; remote-pull-on-init |
| Sub-project B: hybrid CLI + MCP | Matches `/graphify --mcp` pattern. Single backend, two surfaces. No tradeoff lost | MCP-only; CLI-only |
| Sub-project B: Python (pipx) | Matches `/graphify` ecosystem; mature MCP Python SDK | Node.js (npm); Go single binary |
| Sub-project B: BM25 + section retrieval | Two complementary lenses (graph for concepts, BM25 for literal text). No ML deps | Minimal (no search); embedding semantic search |
| Sub-project B: native graph ops via networkx | Self-contained, no `/graphify` skill dependency, deterministic | Wrap `/graphify` CLI; depend on graphify Python pkg |
| Sub-project B: 30-line CLAUDE.md injection w/ explicit theme list | Strong enough to bind agent behavior, small enough not to dominate memory | Minimal mention; heavy guidance |
| Sub-project B: research doc bundled as `harness-engineering-playbook.md` with size warning + confirm gate on full retrieval | User asked for the doc to be "explicit about context impact" | Don't bundle; bundle without confirm gate |
| Sub-project B: location `tools/harness-kb/` (subdir of this repo) | Single git history, build pulls from `../../ai/docs/` | Separate repo |
| Sub-project B: 16 typed MCP tools (vs lean dispatch) | Agents reason better with discrete typed tools + per-tool schemas | Omnibus tools with verb param |
| Sub-project B: `harness-kb build` hidden CLI subcommand | Aligns spec/docs/Task 14 invocations; `hidden=True` keeps it out of user-facing `--help` | Module-only invocation; module + script entry-point |

---

## Files Affected

### Created (this session)

- `docs/superpowers/specs/2026-04-25-research-doc-humanlayer-reframe-design.md` (committed in 9d3b042)
- `docs/superpowers/plans/2026-04-25-research-doc-humanlayer-reframe.md` (committed in 9d3b042)
- `docs/superpowers/specs/2026-04-25-harness-kb-design.md` — **NOT committed**
- `docs/superpowers/plans/2026-04-25-harness-kb-implementation.md` — **NOT committed**
- `.claude/handoffs/HANDOFF_HARNESS_KB_BRAINSTORM_PLAN_04_25_16_00.md` — this file

### Modified (this session)

- `dev/research/2026-04-25-harness-engineering-research.md` — fully reworked (committed in df30297 + 8c8737c)

### Read (Reference)

- `.claude/handoffs/HANDOFF_HARNESS_RESEARCH_REWRITE_04_25_13_51.md` — prior session handoff
- `dev/research/2026-04-25-harness-engineering-research.md` — current state via grep + read
- `~/.claude/skills/graphify/SKILL.md` (listed only — `--mcp` pattern referenced)
- `graphify-out/manifest.json` — manifest schema reference for harness-kb's manifest.py
- `ai/docs/` listing (17 themes confirmed)
- `graphify-out/wiki/` listing (31 pages)

### Deleted

None on disk. Within research file (sub-project A): `### HumanLayer Codebase Findings` (replaced) + `### HumanLayer Codebase — Concrete Instantiation` (deleted ~22 cite lines).

---

## Technical Context

### Architecture Notes (Sub-project B — `harness-kb`)

- Hybrid Python package: CLI (Click) + stdio MCP server, sharing one backend.
- 4 retrieval modules (`docs`, `graph`, `wiki`, `guide`) + `init` (CLAUDE.md injection) + `build` (maintainer-only pipeline + `adapt_guide.py`).
- Bundled data (~5-8 MB): `data/ai_docs/` + `data/graph/graph.json` + `data/wiki/` + `data/guide/harness-engineering-playbook.md` + `data/index/` (BM25 corpus + index + chunks).
- Type contracts locked at the top of the plan: `Manifest`, `Chunk`, `SearchHit`, `DocInfo`, `GraphNode`, `GraphNeighbor`, `GuideSection`. Every task references these.
- 16 MCP tools with real `_TOOL_SCHEMAS` (additionalProperties: false). The dispatcher (`_tool_handlers`) and schema registry (`_TOOL_SCHEMAS`) must stay in sync — `test_each_tool_has_real_input_schema` enforces it.
- Build pipeline: validate source → check graph freshness (abort if `ai/docs/` newer than `graphify-out/manifest.json` unless `--no-staleness-check`) → stage data → adapt research doc (replace `/graphify` references → `harness-kb` references via `_RULES` regex list) → build BM25 index over chunked sections → write manifest → post-validate (zero `/graphify` residual; index loadable).
- No persistent config file — all behavior via CLI flags / MCP tool args.
- No network calls at runtime.

### Dependencies (Sub-project B)

- click >=8.1,<9
- networkx >=3.2,<4
- rank-bm25 >=0.2.2,<0.3
- mcp (Python SDK) >=1.0,<2
- pytest >=8.0,<9 (dev)
- pytest-cov >=4.1,<5 (dev)

### Configuration Changes

None this session.

---

## Things to Know

### Gotchas & Pitfalls

- **Research file (`dev/research/2026-04-25-harness-engineering-research.md`) is currently committed but `dev/` itself was untracked at session start.** It is now tracked because Sub-project A's `df30297` commit added it. Worktree-from-main now would include it.
- **`/graphify` is a Claude Code slash command, not subprocess-callable.** harness-kb's build pipeline therefore does NOT auto-refresh the graph — it staleness-checks and aborts with a clear instruction telling the maintainer to run `/graphify update` from inside Claude Code first.
- **The 16-tool MCP surface choice was justified in the spec by per-tool typed schemas.** Initially the plan had `inputSchema={"additionalProperties": True}` placeholder; advisor flagged the contradiction; plan now has full `_TOOL_SCHEMAS` dict with real schemas + a consistency test (`test_each_tool_has_real_input_schema`).
- **`harness-kb build` is a hidden CLI subcommand** (Click `hidden=True`). It does NOT appear in `--help` output. Maintainers find it via `harness-kb build --help` directly. The plan's tests assert both behaviors.
- **`rtk grep` is recursive by default** and produces non-standard output; use plain `/usr/bin/grep` for verification when filtering with `grep -v` is needed (sub-project A bug discovered during Task 7 verification).
- **Sub-project A's verification spec command 3 originally said `Expected: 1` for the URL count globally** — that's wrong (URL appears in frontmatter + Case Study lead = 2). Spec patched in commit `8c8737c`; plan never had the bug.
- **Plan file is ~2400 lines** — implementer subagents need it scoped per-task; they do not read the whole plan.

### Assumptions Made

- Date `2026-04-25`, time `16:00 BRT` per `date` command.
- User wants Python 3.10+ (stated in spec, accepted in plan Q5).
- `pipx` is available on the consumer machine.
- The `ai-study-library` repo is the source of truth for harness-kb's bundled data; the build pipeline runs from a parent checkout.
- Sub-project B's plan was treated as singular (option a) per Q1 — not split into v0.1.0 + v0.2.0.
- Sub-project B's plan does not use a worktree (consistent with sub-project A's deviation from the original Q1=a worktree choice).

### Known Issues

- **Markdown linter warnings** (MD025, MD060, MD040, MD032, cSpell) — pre-existing across the research file and the spec/plan files. Not introduced this session. Can be auto-fixed later with `markdownlint --fix` if desired.
- **Plan task 13 doc step 5 (`docs/claude-md-injection.md`) instructs the implementer to copy `_BODY_TEMPLATE` from `init.py` verbatim.** That template lives in Task 8's code block. Implementer must reach back to Task 8 — explicit cross-reference is in the step.
- **No automated rebuild trigger when `ai-study-library/` evolves.** The build is manual. Documented in the plan as out of scope.

---

## Current State

### What's Working

- Sub-project A: shipped to `main` (3 commits). Research doc is portable per spec.
- Sub-project B: spec + plan written, advisor-approved, on disk, ready to commit + execute.
- Tasks completed (TaskList): 1-5 (sub-A spec/plan/review/user/writing-plans), 6-16 (sub-A execution + review), 17 (sub-B brainstorm+spec+plan). All marked completed in TaskList.

### What's Not Working

Nothing broken. Sub-project B not yet executed by design.

### Tests

- Sub-project A: all 5 verification grep commands pass against the committed research doc.
- Sub-project B: no implementation = no tests run yet. Plan tasks each include their own pytest commands.

---

## Next Steps

### Immediate (Start Here)

1. **Decide commit + execution path for Sub-project B.** Two open commitments before implementation:
   - (a) Commit B's spec + plan to `main` as the first commit of B's work (Pre-flight Task A in the plan). User has not yet authorized this commit.
   - (b) Pick execution mode: **subagent-driven** (`superpowers:subagent-driven-development`, ~48-60 dispatches, highest quality) or **inline** (`superpowers:executing-plans`, batched checkpoints, lower cost, fills main context).
2. **Confirm or adjust the plan's deviations from typical TDD strictness.** Plan Q3 chose pragmatic-TDD (test-batch + impl-batch per task, not per-function). User accepted; flag if reconsidered.
3. **Run Pre-flight Task A** (commit spec + plan) once authorized:

```bash
cd /home/rodrigo/Workspace/ai-study-library
rtk git add docs/superpowers/specs/2026-04-25-harness-kb-design.md \
         docs/superpowers/plans/2026-04-25-harness-kb-implementation.md
rtk git commit -m "docs: add spec and plan for harness-kb (Sub-project B)"
```

### Subsequent

- **Pre-flight Task B:** scaffold `tools/harness-kb/` skeleton (pyproject.toml, dir tree, version constant, README placeholder, CHANGELOG, LICENSE, .gitignore, conftest.py).
- **Tasks 1-12:** implement modules in dependency order (manifest → chunking → search → docs → graph → wiki → guide → init → cli → mcp → build/adapt_guide → build/build).
- **Task 13:** documentation (README + 5 docs files + changelog).
- **Task 14:** run `harness-kb build` against the live `ai-study-library/` checkout, populate `src/harness_kb/data/`, commit the bundled snapshot.
- **Task 15:** integration smoke test via `pipx install` from path.
- **Task 16:** final verification + tag `harness-kb-v0.1.0`.

### Blocked On

- User decision on commit + execution mode.
- (Soft) `/graphify update .` may need to be run inside Claude Code from the project root before Task 14 if `ai/docs/` has been touched since the last graphify update. Build aborts with a clear error if stale.

---

## Related Resources

### Documentation

- `docs/superpowers/specs/2026-04-25-research-doc-humanlayer-reframe-design.md` — sub-project A spec
- `docs/superpowers/plans/2026-04-25-research-doc-humanlayer-reframe.md` — sub-project A plan
- `docs/superpowers/specs/2026-04-25-harness-kb-design.md` — sub-project B spec
- `docs/superpowers/plans/2026-04-25-harness-kb-implementation.md` — sub-project B plan
- `dev/research/2026-04-25-harness-engineering-research.md` — the rewritten research doc
- `~/.claude/skills/graphify/SKILL.md` — graphify CLI reference
- `graphify-out/GRAPH_REPORT.md` — graph entry point

### Commands to Run

```bash
# Confirm sub-project A on main
rtk git log --oneline main -5
# Should include 9d3b042, df30297, 8c8737c

# Verify research doc passes all 5 spec checks
grep -n 'humanlayer/' dev/research/2026-04-25-harness-engineering-research.md | grep -v 'github.com/humanlayer/humanlayer'  # zero
grep -nE 'humanlayer.*:[0-9]+' dev/research/2026-04-25-harness-engineering-research.md  # zero
grep -cE 'github\.com/humanlayer/humanlayer' dev/research/2026-04-25-harness-engineering-research.md  # 2 (frontmatter + Case Study lead)
wc -l dev/research/2026-04-25-harness-engineering-research.md  # ~1495 lines

# Inspect sub-project B artifacts
wc -l docs/superpowers/specs/2026-04-25-harness-kb-design.md         # ~370
wc -l docs/superpowers/plans/2026-04-25-harness-kb-implementation.md # ~2400

# Sub-project B Pre-flight Task A (commit spec + plan)
rtk git status --short docs/superpowers/

# Inspect existing TaskList state on resume
# (TaskList persists across sessions in the harness; just call TaskList)
```

### Search Queries

- `grep -rn "harness_kb_" docs/superpowers/plans/2026-04-25-harness-kb-implementation.md` — finds every MCP tool reference
- `grep -nE "^### Task [0-9]" docs/superpowers/plans/2026-04-25-harness-kb-implementation.md` — lists all 16 main tasks
- `grep -nE "^- \[ \]" docs/superpowers/plans/2026-04-25-harness-kb-implementation.md | wc -l` — total checkbox count (estimate of step granularity)
- `git log --oneline --all -10` — recent commits across all branches

---

## Open Questions

- [ ] Subagent-driven vs inline execution for Sub-project B?
- [ ] User wants Pre-flight A committed standalone, or bundled with Pre-flight B (scaffold) as a single setup commit?
- [ ] Should Plan Q3's pragmatic-TDD interpretation be revisited if early tasks turn up coupling issues that real-TDD would have caught earlier?
- [ ] Does the user want the v0.1.0 tag pushed to a remote (none configured today), or kept local?
- [ ] Tokenizer choice in BM25: whitespace-only is the default (Open Question 2 in spec). If recall is poor, revisit. No action required pre-execution.

---

## Session Notes

- Workflow: brainstorming skill → spec self-review → advisor → user-review-gate → writing-plans skill → spec self-review → advisor → execution-handoff offer (deferred by `/session:handoff`).
- Caveman mode active throughout chat; spec/plan/research-doc bodies written in normal prose per the boundary rule.
- TaskList tracked 17 tasks across both sub-projects; all marked completed at handoff time.
- Two advisor passes per spec/plan boundary: each caught real issues (sub-A: too-narrow grep + missing concept-rule; sub-B: 4 issues incl. `harness-kb build` invocation mismatch + permissive MCP schemas).
- The 16-tool MCP surface decision is the most architecturally consequential choice in B — committed in spec + reinforced with real schemas in plan. Reversing later means breaking the registry contract.
- Sub-project A demonstrated the value of pre-commit advisor passes: one quick post-write fix (line 113 cross-reference; spec verification step 3 expected count) caught only by the final reviewer, not by either prior advisor pass — suggests advisor's depth is tied to having concrete diff to point at.

---

*This handoff was generated mid-session via `/session:handoff` command. Start a new session and use this document as your initial context. Begin at "Immediate (Start Here)" → item 1 (decide commit + execution mode for Sub-project B).*
