# harness-kb Plan-Bugs Log

Running list of plan-bug fixes applied during execution of `2026-04-25-harness-kb-implementation.md`. Each entry is a deviation from plan-verbatim that was justified by a real correctness or test-failure issue. The plan file itself is NOT patched mid-flight; this log feeds the final review and any future re-runs.

## Bug 1 — Task 2 chunking.py: single-paragraph subsplit

- **Plan refs:** lines 446-495 (test), 540-577 (`_split_long_section`)
- **Test that triggered it:** `test_chunk_markdown_long_section_subsplit`
- **Root cause:** Test fixture is `body = "para. " * 1000` — a single 1000-token "paragraph" with no `\n\s*\n` separators. Plan's `_split_long_section` splits ONLY at paragraph boundaries, so it cannot split a single oversized paragraph. Test asserts `len(chunks) > 1` and `c.token_count <= 320`; verbatim impl emits 1 chunk with 1000 tokens → fails.
- **Fix applied:** Added `_split_long_paragraph` helper (word-boundary splitter with overlap) and modified `_split_long_section` to delegate to it when a single paragraph exceeds `max_tokens`.
- **Commit:** `1428ba6`
- **Risk:** `_split_long_paragraph` uses the same `str.find()`-based offset reconstruction as `_split_long_section`. Latent fragility on inputs with irregular whitespace. Currently masked because corpus has well-formed markdown.

## Bug 2 — Task 4 docs.py: BM25 fixture token mismatch

- **Plan refs:** lines 901-911 (chunk fixtures), 969-972 (`test_search_docs_returns_hits`)
- **Test that triggered it:** `test_search_docs_returns_hits`
- **Root cause:** Test queries `"MCP"` (tokenizes via `\w+`, lowercased → `["mcp"]`). Plan's chunk fixtures contain `"Model Context Protocol overview"` and `"Resources Prompts Tools Sampling"` — neither contains the literal token `mcp`. BM25 scores all chunks zero; `search` filters out zero-score hits → returns `[]`. Assertion `len(hits) >= 1` fails.
- **Fix applied:** Test fixture changed: `text="MCP Model Context Protocol overview"` (added literal `MCP`).
- **Commit:** `089d6b8`
- **Risk:** Fixture is now slightly artificial. Real `ai_docs/` corpus does contain literal `MCP` tokens, so production behavior is unaffected.

## Latent Issue 1 — Module-level `_index_cache` leak (Task 4)

- **Plan refs:** lines 1016, 1027-1034 (`_index_cache` global + `_load_index`)
- **Status:** Acknowledged but NOT fixed in plan-verbatim impl. Mitigated by autouse pytest fixture below.
- **Root cause:** `_index_cache` is module-global. Plan's tests use `monkeypatch.setattr(docs_module, "get_data_dir", ...)` per-test (auto-undoes), but the cache itself never resets. First test that calls `search_docs` caches THAT test's `tmp_path` index. Subsequent tests with different `tmp_path` would still get the stale cache. Tests pass only because all current fixtures build identical chunks.
- **Mitigation applied:** Added `_reset_index_cache` autouse fixture in `test_docs.py` (resets `docs_module._index_cache = None` before/after each test).
- **Pattern for downstream tasks:** Tasks 5 (graph), 6 (wiki), 7 (guide) likely use the same module-cache pattern. Each implementer prompt MUST include the autouse-reset fixture.
- **Commit:** TBD (added with this log).
