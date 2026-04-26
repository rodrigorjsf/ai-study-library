# Handoff: harness-kb Sub-project B — Resume at Task 12

**Created:** 2026-04-25 17:50 -03
**Branch:** main
**Session Duration:** ~1h45m (continuation of 04_25_16_00 handoff)
**Working Directory:** `/home/rodrigo/Workspace/ai-study-library/`
**Skill Active:** `superpowers:subagent-driven-development`
**Mode:** caveman (full)

---

## Summary

Subagent-driven execution of harness-kb v0.1.0 plan. **11 of 16 main tasks committed to `main`**, plus pre-flight bundled commit, plan-bugs log, and cache-fixture infrastructure. Hit usage limit mid-dispatch of Task 12 (`build/build.py`). The Task 12 implementer prompt was fully crafted and pasted into an Agent call that returned with "You're out of extra usage". No code written for Task 12 yet. Resume by re-dispatching the same prompt — it's preserved in this handoff body.

---

## Work Completed

### User decisions locked at session start
- **Pre-flight commit:** option (b) — bundled spec + plan + scaffold into single setup commit (commit `c95b8c7`).
- **Worktree:** option (b) — no worktree.
- **Model tier:** option (a) — haiku for mechanical tasks, sonnet for spec+quality reviews, advisor at architectural checkpoints.

### Tasks done (commits on main)

- [x] Pre-flight (bundled): spec + plan + scaffold → `c95b8c7`
- [x] Task 1: manifest.py → `7b065a4`
- [x] Task 2: chunking.py → `1428ba6` (plan-bug fix: added `_split_long_paragraph`)
- [x] gitignore: ignore .venv + uv.lock → `b61bb3f`
- [x] Task 3: search.py BM25 → `1dc6971`
- [x] Task 4: docs.py → `089d6b8` (plan-bug fix: chunk fixture text "MCP Model Context Protocol overview")
- [x] Plan-bugs log + autouse cache-reset fixture in test_docs.py → `61c3563`
- [x] Task 5: graph.py → `1f20670` (added autouse `_reset_graph_cache` fixture)
- [x] Task 6: wiki.py → `ce04b50`
- [x] Task 7: guide.py → `80234b5` (added autouse `_reset_index_cache` fixture)
- [x] Task 8: init.py CLAUDE.md injection → `760121e`
- [x] Task 9: cli.py Click → `d66b279`
- [x] Task 10: mcp.py 16-tool stdio MCP server → `3789057` (architectural commit-line crossed)
- [x] Task 11: build/adapt_guide.py → `beb4d58`
- [x] Task 11 fix: untrack .pyc files; anchor `build/` gitignore → `6c58362`

### Tasks pending

- [ ] **Task 12: build/build.py** (full pipeline) — IN PROGRESS, prompt ready
- [ ] Task 13: docs/* + README + CHANGELOG
- [ ] Task 14: Bundle data via build (live `ai-study-library/` checkout) — advisor checkpoint pre-dispatch
- [ ] Task 15: pipx integration smoke test
- [ ] Task 16: Final verification + tag harness-kb-v0.1.0
- [ ] Final code review of entire branch + `finishing-a-development-branch`

### Key Decisions

| Decision | Rationale | Alternatives Considered |
|---|---|---|
| Pre-flight A+B bundled into one commit | User chose option (b) at session start; reduces commit noise | Standalone commit per task |
| No worktree for B | User chose option (b); single git history; simpler refresh | Worktree + branch |
| Haiku for implementer; sonnet for reviewer; advisor at Task 10/12/14 | Cost/value tier; verbatim plan = mechanical work | All sonnet; all opus |
| Inline pre-flight (vs subagent dispatch) | Pre-flight is bookkeeping/scaffolding, not implementation | Subagent dispatch |
| Pragmatic-TDD per task (tests-batch then impl-batch) | Plan Q3 chose this; user accepted | Per-function TDD |
| Combined spec+quality review for verbatim-clean tasks; separate for plan-bug-fix tasks | Reduce review-dispatch cost on uncontested impls | Always two-stage |
| Mirror autouse `_reset_*_cache` fixture per module | Advisor recommendation; defense-in-depth against test isolation flakes | Trust manual reset |
| Plan-bugs logged in separate file (NOT plan-patched mid-flight) | Advisor recommendation; avoid two-direction rewrites | Patch plan inline |
| Skip non-blocking Important issues (KeyError-vs-ValueError, str.find offsets) | Plan-bound; defer to final review | Fix mid-flight |

### Plan-bug fixes applied (logged)

See `docs/superpowers/plans/2026-04-25-harness-kb-plan-bugs.md` (committed `61c3563`):
1. **Bug 1 — chunking.py:** plan's `_split_long_section` cannot split a single oversized paragraph (no `\n\s*\n` separators); test fixture `"para. " * 1000` would fail. Implementer added `_split_long_paragraph` helper.
2. **Bug 2 — docs.py test fixture:** plan's chunk text "Model Context Protocol overview" doesn't tokenize to include "mcp"; test query "MCP" returns 0 hits → assertion fails. Fixed fixture to "MCP Model Context Protocol overview".
3. **Latent issue 1 — `_index_cache` leak:** module-globals never reset between tests; mitigated by autouse fixtures in test_docs.py / test_graph.py / test_guide.py.

---

## Files Affected

### Created this session

- `tools/harness-kb/` entire package tree (pyproject.toml, src/harness_kb/{manifest,chunking,search,docs,graph,wiki,guide,init,cli,mcp,build/{__init__,adapt_guide}}.py + __init__.py + __main__.py + data/.gitkeep)
- `tools/harness-kb/tests/test_*.py` for each module (8 test files: manifest, chunking, search, docs, graph, wiki, guide, init, cli, mcp, adapt_guide — total 9 files)
- `tools/harness-kb/conftest.py`, `LICENSE`, `README.md` (skeleton), `CHANGELOG.md`, `.gitignore`
- `docs/superpowers/plans/2026-04-25-harness-kb-plan-bugs.md`

### Modified
- `tools/harness-kb/.gitignore` (twice: add `.venv/uv.lock`; anchor `/build/`)
- `tools/harness-kb/tests/test_docs.py` (added autouse cache reset fixture in `61c3563`)

### Untracked / not in any commit
- `.venv/` and `uv.lock` in `tools/harness-kb/` — local dev only, gitignored
- All untracked status from session start (`.claude/`, `CLAUDE.md`, `ai/`, `graphify-out/`, `humanlayer/` etc) is unchanged from prior handoffs

---

## Technical Context

### Architecture & key invariants

- **16 themes** in `ai/docs/` (verified by `ls ai/docs/` — actual count is 16, NOT 17 as prior handoff claimed). `REQUIRED_THEMES` in build.py is correctly 16. `len(m["themes"]) == 16` test will pass against real corpus. Advisor's "Task 14 drift risk" concern was based on outdated handoff; no drift expected.
- **MCP 16-tool registry** locked at Task 10: `_tool_handlers` dict and `_TOOL_SCHEMAS` dict must keep identical key sets. `test_each_tool_has_real_input_schema` enforces. Reversing means breaking the contract.
- **Cache pattern in retrieval modules** (docs/graph/guide): module-global `_index_cache` / `_graph_cache`. Tests use autouse `_reset_*_cache` fixture to reset before/after each test.
- **uv venv** at `tools/harness-kb/.venv/` is the dev environment. All test runs must use `uv run pytest` from `tools/harness-kb/`. System `python3` lacks pytest. Pre-installed deps: click 8.3.3, rank-bm25 0.2.2, networkx 3.6.1, mcp SDK, pytest 8.4.2.
- **Lazy imports in cli.py:** `from harness_kb.mcp import run_stdio_server` inside `_run_mcp_server()`; `from harness_kb.build.build import build_data` inside `build_cmd`. These were intentional to keep test_cli.py from triggering Task 10/12 module load before they exist. After Task 12 lands, both lazy imports resolve normally.

### Dependencies (no changes)
- click >=8.1,<9 (8.3.3 installed)
- networkx >=3.2,<4 (3.6.1 installed)
- rank-bm25 >=0.2.2,<0.3 (0.2.2 installed)
- mcp >=1.0,<2 (installed)
- pytest >=8.0,<9 (8.4.2 installed)

### Configuration changes
- `tools/harness-kb/.gitignore` final state: ignores `__pycache__/`, `*.pyc`, `.pytest_cache/`, `*.egg-info/`, `/build/` (anchored), `dist/`, `.coverage`, `htmlcov/`, `.venv/`, `uv.lock`.

---

## Things to Know

### Gotchas
- **Implementer subagent has occasionally deviated silently from "verbatim".** Caught by spec reviewer in Tasks 2 and 4 (both genuine plan bugs); caught controller-side in Task 11 (force-added .pyc files). Implementer prompt now includes: "Any deviation — even a plan-bug fix — REQUIRES status DONE_WITH_CONCERNS with the exact diff and reason." Apply this in every dispatch.
- **`rank-bm25` zero-score chunks are filtered out** in `BM25SearchIndex.search`; query tokens must literally appear in chunk text for any hit. Real ai/docs corpus has the actual vocabulary; only fixtures need synthetic tokens.
- **`subprocess.check_output(["git", ...])`** in `build.py::_git_sha` returns "unknown" if source dir is not a git repo. Test fixture `mini_source` is not a repo → returns "unknown" → manifest's `source_commit_sha` is "unknown" in tests. Real Task 14 run from `ai-study-library/` returns the actual SHA.
- **`shutil.rmtree(out_dir)`** in `_stage_data` wipes `out_dir` if it exists. For Task 14, `--out-dir` is `tools/harness-kb/src/harness_kb/data/`, which currently has only `.gitkeep`. After Task 14, `.gitkeep` is gone but bundled data files exist; pyproject's `package-data = ["data/**/*"]` glob picks them up.
- **Plan says "Expected: 6 passed" for Task 10** but the test block has 7 functions. Plan typo. Used 7 in dispatch. Same kind of typo may exist elsewhere — count the actual `def test_` functions before dispatching.
- **`_safe()` exception coverage** in mcp.py catches only `FileNotFoundError`/`KeyError`/`ValueError`. `RuntimeError` (from init.py unbalanced markers) and `re.error` (from graph_find bad pattern) propagate uncaught. Plan-bound; not fixed.
- **`graph.shortest_path` raises `KeyError` on invalid label** before reaching networkx. Plan's test only exercises the connected-components path. Plan-bound; not fixed.
- **`str.find()`-based offset reconstruction** in chunking.py is fragile on inputs with irregular whitespace. Real corpus is well-formed markdown; not exercised in pathological cases.

### Assumptions
- Date 2026-04-25 used in commit messages and test comments.
- Python 3.10+ enforced via pyproject; venv is 3.13.12.
- Plan tasks are sized small enough (<300 lines each) for haiku to execute correctly with verbatim instructions.

### Known issues
- Markdown linter warnings (MD060, cSpell) on plan/spec/handoff files — pre-existing, not introduced.
- The prior handoff (`HANDOFF_HARNESS_KB_BRAINSTORM_PLAN_04_25_16_00.md`) claimed 17 themes; actual count is 16. Advisor's Task 14 concern based on the inflated count is moot.

---

## Current State

### Working
- 11 of 16 main tasks fully implemented + tested + committed.
- Total tests now in suite: ~70+ (manifest 4, chunking 6, search 7, docs 10, graph 9, wiki 3, guide 6, init 10, cli 9, mcp 7, adapt_guide 8).
- Per-task `uv run pytest tests/test_<module>.py -v` passes for all done tasks.
- Plan-bugs log keeps provenance of every deviation.
- Cache-isolation infrastructure mirrored across all module-cached test files.

### Not working / pending
- Task 12 build pipeline never written. Implementer call hit usage limit. Re-dispatch needed.
- No full-suite cross-module test run yet (`uv run pytest`). Should pass post-Task 12.
- No bundled data in `src/harness_kb/data/` — only `.gitkeep`. Task 14 populates.

### Tests
- Per-module: 11/11 done modules green.
- Full suite: not yet run.
- Integration: pending Task 15.

---

## Next Steps

### Immediate (Start Here)

1. **Re-dispatch Task 12 implementer.** The Agent call dispatched mid-session was cut off by usage cap. The full prompt body is preserved verbatim further down in this handoff (see "Task 12 Dispatch Prompt — Ready to Re-Send" section). Important pinning notes that MUST stay in the prompt:
   - REQUIRED_THEMES is plan-pinned at 16 entries — do NOT modify based on actual `ai/docs/` (which is 16 anyway, but advisor wanted defensive pinning).
   - Tests fixture has 16 theme stubs — `len(m["themes"]) == 16` assertion.
   - Use `uv run pytest`, not `python3 -m pytest`.
   - DONE_WITH_CONCERNS required on any deviation.
   - Commit ONLY 2 files: `src/harness_kb/build/build.py` + `tests/test_build.py`.
2. After Task 12 implementer returns: spec+quality review (one combined sonnet dispatch), mark TaskList #13 done.
3. Move to Task 13 (docs/* + README + CHANGELOG) — pure documentation, plan provides templates.

### Subsequent

- Task 14 (data bundle): **advisor checkpoint before dispatch** per advisor's plan. Verify `ai/docs/` has 16 themes (it does), check that `dev/research/2026-04-25-harness-engineering-research.md` exists and is well-formed. Run `harness-kb build --source ../../ --out-dir src/harness_kb/data --no-staleness-check` (or with staleness check after `/graphify update .`).
- Task 15: pipx install smoke test.
- Task 16: tag `harness-kb-v0.1.0`.
- Final review: `superpowers:code-reviewer` over entire branch; then `superpowers:finishing-a-development-branch` for merge / PR / cleanup.

### Blocked on
- Usage reset (5:50pm America/Fortaleza per error message). Resume after.

---

## Task 12 Dispatch Prompt — Ready to Re-Send

When the next session starts, re-dispatch with this exact prompt to the general-purpose haiku agent:

```
Implementing Task 12: build/build.py (full pipeline) for harness-kb.

**Files:**
- Create: tools/harness-kb/src/harness_kb/build/build.py
- Create: tools/harness-kb/tests/test_build.py

(... full test code from plan lines 2804-2900 verbatim ...)
(... full impl code from plan lines 2913-3066 verbatim ...)

Steps 1-5 as in plan section "Task 12: build/build.py (full pipeline)".

CRITICAL pinning rules:
- REQUIRED_THEMES is plan-pinned at 16 entries (the list in the impl). Do NOT modify based on actual ai/docs/ layout. Test asserts len(m["themes"]) == 16.
- Implementation is verbatim. NO additions/changes/comment edits.
- Any deviation — even a plan-bug fix — REQUIRES status DONE_WITH_CONCERNS with exact diff and reason. Reporting DONE on a deviation is a defect.

Important:
- ALWAYS use `uv run pytest` from tools/harness-kb/. NEVER python3 -m pytest.
- Pre-installed deps: chunking/search/manifest/adapt_guide already done. Build wires them.
- Fixture's mini_source is not a git repo; _git_sha returns "unknown" — expected.
- Do NOT run `graphify update` or other tooling.
- Commit ONLY the 2 listed files.
- Expected: 5 passed.

Report Format: Status / pytest output / Files changed (must be 2) / Commit SHA / Self-review / Deviations.
```

The plan source is at `docs/superpowers/plans/2026-04-25-harness-kb-implementation.md` lines 2791-3084. Re-read those lines to get the verbatim test and impl code blocks, then construct the prompt.

---

## Related Resources

### Documentation
- `docs/superpowers/specs/2026-04-25-harness-kb-design.md` — spec
- `docs/superpowers/plans/2026-04-25-harness-kb-implementation.md` — plan (3756 lines)
- `docs/superpowers/plans/2026-04-25-harness-kb-plan-bugs.md` — running deviation log

### Commands to Run

```bash
# Verify state at resume
cd /home/rodrigo/Workspace/ai-study-library
rtk git log --oneline -16              # Should show c95b8c7 → 6c58362 (15 commits)
rtk git status --short                  # No unexpected staged/unstaged

# Run full test suite (sanity)
cd tools/harness-kb && uv run pytest -v
# Expected: ~70 tests, all green (manifest 4, chunking 6, search 7, docs 10, graph 9, wiki 3, guide 6, init 10, cli 9, mcp 7, adapt_guide 8 = 79)

# Inspect plan for Task 12
sed -n '2791,3084p' docs/superpowers/plans/2026-04-25-harness-kb-implementation.md

# Verify theme count in real corpus (should be 16)
ls -d ai/docs/*/ | wc -l

# Check for mcp/build module presence
ls tools/harness-kb/src/harness_kb/build/

# After Task 12 lands, run cross-module integration check
cd tools/harness-kb && uv run pytest -q
```

### Search Queries

- `grep -nE "^def test_" tools/harness-kb/tests/test_*.py | wc -l` — total test count
- `grep -nE "^### Task [0-9]+:" docs/superpowers/plans/2026-04-25-harness-kb-implementation.md | head -20` — task index
- `grep -n "REQUIRED_THEMES" tools/harness-kb/src/harness_kb/build/` — pinning point (after Task 12)

---

## Open Questions

- Should Task 12 dispatch flag the line `no_graph_refresh: bool = True,  # always true; graph refresh is manual` as plan-comment cruft worth keeping? (yes — it's verbatim plan)
- For Task 14, does the user want to run `/graphify update .` first (to satisfy staleness check), or pass `--no-staleness-check`? Plan default is staleness-checked. Faster path = `--no-staleness-check` since corpus is current.
- Final-review scope: just harness-kb commits, or also include the 3 sub-A commits already on main? (just harness-kb — sub-A is already shipped and reviewed.)

---

## Session Notes

- Caveman mode active throughout — this handoff body itself is normal prose per the "code/commits/PRs/handoffs: write normal" rule.
- Advisor called twice: once at Task 4 (after pattern of plan bugs surfaced — locked the strategy + introduced cache-fixture pattern + plan-bugs log) and once at Task 12 dispatch (pinned REQUIRED_THEMES + flagged Task 14 risks). Next advisor checkpoint: pre-Task 14.
- Reviewer dispatches were combined spec+quality (single sonnet) for clean verbatim tasks; separate spec then quality (sonnet then code-reviewer) for plan-bug-fix tasks. Lower cost, same coverage.
- The plan-bugs log file is the single source of truth for "what did we change vs verbatim and why". Final review will use it as a checklist against `git diff main`.

---

*This handoff was generated mid-Task-12 due to usage cap. Resume by re-reading plan lines 2791-3084, then dispatching the implementer prompt above. Architectural decisions are committed (Task 10 16-tool registry); remaining work is mechanical implementation + bundle + tag.*
