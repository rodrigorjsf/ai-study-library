# Compliance Audit Report — Cursor Initializer

**Scope ID**: cursor-initializer  
**Audit Date**: 2026-04-17  
**Auditor Phase**: 6 (Cursor Scope Audit and Correction)  
**Plan Reference**: `.claude/PRPs/plans/cursor-scope-audit-and-correction.plan.md`  
**Total Artifacts Audited**: 31 (per `docs/compliance/artifact-audit-manifest.md` §7)

---

## 7.2 Dashboard

| Category | Total | CRITICAL | MAJOR | MINOR |
|----------|-------|----------|-------|-------|
| Contamination | 6 | 0 | 6 | 0 |
| Self-Sufficiency | 5 | 0 | 5 | 0 |
| Provenance | 1 | 0 | 0 | 1 |
| **Total** | **10** | **0** | **10** | **0** |

> All 10 findings (CF-060–CF-069) CLOSED after corrections applied 2026-04-17. CF-070 reviewed and confirmed not a violation (see §7.5). No automated quality gate for cursor-initializer (confirmed in `docs/compliance/artifact-audit-manifest.md §12`). Grep-based manual revalidation substitutes — all commands PASS.

---

## 7.3 Findings

### Pre-Audit Evidence Baseline (Tasks 2–8)

| Violation Pattern | Baseline Count | Files Affected | After Correction |
|-------------------|----------------|----------------|------------------|
| CLAUDE-MEMORY citations (`claude-code/memory`) | 2 | 2 files (SCG-01 pair) | 0 |
| "Auto memory" rows (Claude Code-only mechanism) | 2 | 1 file (2 tables) | 0 |
| `disable-model-invocation: true` in default frontmatter | 1 | 1 template file | 0 |
| README relative path links (`../../docs/`) | 5 (lines 23, 53, 57, 58, 68) | 1 file | 0 |
| `paths:` frontmatter in .mdc templates | 0 | — | 0 |
| `tools:` or `maxTurns:` in agent frontmatter | 0 | — | 0 |
| Agent delegation scope violations | 0 | — | 0 |

**Walk-Through Summary (Tasks 2–8):** All 31 artifacts inspected individually.

- 3 agents: CLEAN (codebase-analyzer, file-evaluator, scope-detector)
- 2 SKILL.md files: CLEAN (improve-cursor, init-cursor)
- 7 improve-cursor reference files: CF-060, CF-062 confirmed; 5 clean
- 5 init-cursor reference files: CF-061 confirmed; 4 clean
- 6 improve-cursor template files: CF-063 confirmed; 5 clean
- 4 init-cursor template files: CLEAN
- Plugin config files (plugin.json, AGENTS.md, CLAUDE.md): CLEAN
- README.md: CF-064–CF-068 confirmed

**CF-069 discovered during Task 14 revalidation**: second "Auto memory" row in `automation-migration-guide.md` Distribution-Aware Recommendations table (line 106) — missed by initial walk-through grep. Recorded and corrected.

**CF-070 reviewed — not a violation**: README line 63 external URL `https://docs.anthropic.com/en/docs/claude-code/memory` matched revalidation grep pattern; reviewed against `docs/compliance/normative-source-matrix.md` — CLAUDE-MEMORY is defined narrowly as internal source `docs/claude-code/memory/` (see §7.5 for full analysis).

---

### CF-060 — CLAUDE-MEMORY citation in improve-cursor context-optimization.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination
- **Scope**: cursor-initializer
- **Artifact**: `plugins/cursor-initializer/skills/improve-cursor/references/context-optimization.md`
- **Evidence**: `plugins/cursor-initializer/skills/improve-cursor/references/context-optimization.md:127` — `"| ≤200 lines per file | Anthropic Docs: claude-code/memory |"`
- **Violated Source**: `cursor-plugin-bundle` (`docs/compliance/normative-source-matrix.md`) — "Forbidden: ALL CLAUDE-* sources" (CLAUDE-MEMORY); `.claude/rules/cursor-plugin-skills.md` — "Cursor artifacts must reference only cursor-plugin-bundle sources"
- **Current State**: Line 127 cites `Anthropic Docs: claude-code/memory` as source for the 200-line limit guideline
- **Expected State**: Citation replaced with neutral attribution matching Agent Skills Standard (same fix as CF-051 in Phase 5)
- **Impact**: Cursor-native reference contains a forbidden Claude Code-specific source citation; creates Claude scope dependency in distributed reference material
- **Proposed Fix**: Replace `Anthropic Docs: claude-code/memory` with `Agent Skills Standard` on line 127
- **Correction Notes**: Applied 2026-04-17 — line 127 source cell updated from `Anthropic Docs: claude-code/memory` to `Agent Skills Standard`. SCG-01 sibling `init-cursor/references/context-optimization.md` updated in lockstep (CF-061)
- **Provenance**: Guidance retained; citation updated to neutral source consistent with Agent Skills Standard
- **Revalidation Method**: instruction-only/manual-validator
- **Revalidation Evidence**: `grep 'claude-code/memory' plugins/cursor-initializer/skills/improve-cursor/references/context-optimization.md` → 0 results
- **Gate Rerun Record**: N/A — no automated quality gate for cursor-initializer (confirmed artifact-audit-manifest.md §12)

---

### CF-061 — CLAUDE-MEMORY citation in init-cursor context-optimization.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination
- **Scope**: cursor-initializer
- **Artifact**: `plugins/cursor-initializer/skills/init-cursor/references/context-optimization.md` (SCG-01 member)
- **Evidence**: `plugins/cursor-initializer/skills/init-cursor/references/context-optimization.md:127` — `"| ≤200 lines per file | Anthropic Docs: claude-code/memory |"` (identical violation to CF-060)
- **Violated Source**: `cursor-plugin-bundle` (`docs/compliance/normative-source-matrix.md`) — "Forbidden: ALL CLAUDE-* sources"
- **Current State**: Same as CF-060 sibling; SCG-01 pair was byte-identical at baseline for the Citations table
- **Expected State**: Same correction as CF-060 — applied in lockstep
- **Impact**: Same as CF-060
- **Proposed Fix**: Same as CF-060 — SCG-01 lockstep requirement
- **Correction Notes**: Applied 2026-04-17 in lockstep with CF-060 — SCG-01 parity maintained; Citations table verified identical in both copies after correction
- **Provenance**: Same as CF-060
- **Revalidation Method**: instruction-only/manual-validator
- **Revalidation Evidence**: `grep 'claude-code/memory' plugins/cursor-initializer/skills/init-cursor/references/context-optimization.md` → 0 results; SCG-01 parity confirmed
- **Gate Rerun Record**: N/A — no automated quality gate for cursor-initializer

---

### CF-062 — "Auto memory" row in automation-migration-guide.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination
- **Scope**: cursor-initializer
- **Artifact**: `plugins/cursor-initializer/skills/improve-cursor/references/automation-migration-guide.md`
- **Evidence**: `plugins/cursor-initializer/skills/improve-cursor/references/automation-migration-guide.md:87` — `"| Auto memory | First 200 lines at startup | Advisory — system-managed | Cross-session learnings, preferences |"`
- **Violated Source**: `cursor-plugin-bundle` (`docs/compliance/normative-source-matrix.md`) — "Forbidden: ALL CLAUDE-* sources" (CLAUDE-MEMORY); `.claude/rules/cursor-plugin-skills.md` — "Cursor artifacts must reference only cursor-plugin-bundle sources"
- **Current State**: Mechanism Comparison table includes "Auto memory" row — a Claude Code-specific mechanism not available in Cursor
- **Expected State**: Table lists only Cursor-native mechanisms
- **Impact**: Cursor developer guidance presents a Claude Code-only mechanism as if it were a Cursor option; generates incorrect migration recommendations
- **Proposed Fix**: Remove the "Auto memory" row from the Mechanism Comparison table
- **Correction Notes**: Applied 2026-04-17 — "Auto memory" row removed from Mechanism Comparison table. Note below table (referencing hook events) retained — it is valid Cursor-native content
- **Provenance**: N/A — removal only
- **Revalidation Method**: instruction-only/manual-validator
- **Revalidation Evidence**: `grep 'Auto memory' plugins/cursor-initializer/skills/improve-cursor/references/automation-migration-guide.md` → 0 results
- **Gate Rerun Record**: N/A — no automated quality gate for cursor-initializer

---

### CF-063 — Inverted default in skill.md template frontmatter [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination, Normative-Alignment
- **Scope**: cursor-initializer
- **Artifact**: `plugins/cursor-initializer/skills/improve-cursor/assets/templates/skill.md`
- **Evidence**: `plugins/cursor-initializer/skills/improve-cursor/assets/templates/skill.md:4` — `"disable-model-invocation: true"` in default frontmatter; `:11-12` — `"Rule: disable-model-invocation: true is the default for migrated skills"` and `"Rule: Remove disable-model-invocation: true ONLY when the skill should be auto-invoked"`; `:18-21` — CONDITIONAL block restating manual-only as default
- **Violated Source**: `docs/cursor/skills/agent-skills-guide.md:92-95` — "field absent = auto-invocable (default); disable-model-invocation: true is opt-in override for manual-only skills"
- **Current State**: Three locations all frame manual-only (field present) as the default, requiring users to remove the field to get auto-invocable behavior
- **Expected State**: Frontmatter omits `disable-model-invocation` (auto-invocable by default); CONDITIONAL block describes when to ADD the field (manual-only is opt-in)
- **Impact**: Generated skills are manual-only by default; users must know to delete a field to get the correct default behavior; counter to Cursor documentation
- **Proposed Fix**: (1) Remove `disable-model-invocation: true` from frontmatter; (2) Rewrite rule comments to remove "default for migrated skills" framing; (3) Rewrite CONDITIONAL block to describe when to ADD the field
- **Correction Notes**: Applied 2026-04-17 — (1) `disable-model-invocation: true` removed from frontmatter (lines 1-5); (2) rule comments rewritten to remove inverted-default framing; (3) CONDITIONAL block rewritten to describe ADD pattern with correct framing: "Default (field absent) = auto-invocable"
- **Provenance**: N/A — correction to match normative source
- **Revalidation Method**: instruction-only/manual-validator
- **Revalidation Evidence**: `head -6 plugins/cursor-initializer/skills/improve-cursor/assets/templates/skill.md` shows no `disable-model-invocation` in frontmatter; `grep 'disable-model-invocation' ...skill.md` finds field only in conditional comment
- **Gate Rerun Record**: N/A — no automated quality gate for cursor-initializer

---

### CF-064 — Relative doc link in README line 23 [MAJOR] — ✅ CLOSED

- **Check Category**: Self-Sufficiency
- **Scope**: cursor-initializer
- **Artifact**: `plugins/cursor-initializer/README.md`
- **Evidence**: `plugins/cursor-initializer/README.md:23` — `"[Evaluating AGENTS.md](../../docs/general-llm/Evaluating-AGENTS-paper.pdf)"`
- **Violated Source**: PRD #56 Phase 6 self-sufficiency contract; `.claude/rules/readme-files.md` — README must be self-contained for distribution; Phase 5 pattern CF-057–CF-059
- **Current State**: Relative path `../../docs/general-llm/Evaluating-AGENTS-paper.pdf` — breaks when plugin installed outside repo tree
- **Expected State**: Full GitHub URL: `https://github.com/rodrigorjsf/agent-engineering-toolkit/blob/development/docs/general-llm/Evaluating-AGENTS-paper.pdf`
- **Impact**: Link 404s in any tarball/installed context; breaks documentation portability
- **Proposed Fix**: Replace relative path with full GitHub URL using `blob/development/` prefix
- **Correction Notes**: Applied 2026-04-17 — replaced with full GitHub URL
- **Provenance**: N/A — URL correction only
- **Revalidation Method**: instruction-only/manual-validator
- **Revalidation Evidence**: `grep -n '\.\./\.\./docs/' plugins/cursor-initializer/README.md` → 0 results after all CF-064–CF-068 corrections applied
- **Gate Rerun Record**: N/A — no automated quality gate for cursor-initializer

---

### CF-065 — Relative doc link in README line 53 [MAJOR] — ✅ CLOSED

- **Check Category**: Self-Sufficiency
- **Scope**: cursor-initializer
- **Artifact**: `plugins/cursor-initializer/README.md`
- **Evidence**: `plugins/cursor-initializer/README.md:53` — `"[Evaluating AGENTS study](../../docs/general-llm/Evaluating-AGENTS-paper.pdf)"`
- **Violated Source**: PRD #56 Phase 6 self-sufficiency contract; Phase 5 pattern CF-057–CF-059
- **Current State**: Same relative path as CF-064 — second occurrence of the same PDF link
- **Expected State**: Full GitHub URL (same target as CF-064)
- **Impact**: Same as CF-064
- **Proposed Fix**: Replace with same full GitHub URL as CF-064
- **Correction Notes**: Applied 2026-04-17 in same edit as CF-064 — both PDF occurrences replaced atomically
- **Provenance**: N/A
- **Revalidation Method**: instruction-only/manual-validator
- **Revalidation Evidence**: Covered by CF-064 revalidation command
- **Gate Rerun Record**: N/A — no automated quality gate for cursor-initializer

---

### CF-066 — Relative doc link in README line 57 [MAJOR] — ✅ CLOSED

- **Check Category**: Self-Sufficiency
- **Scope**: cursor-initializer
- **Artifact**: `plugins/cursor-initializer/README.md`
- **Evidence**: `plugins/cursor-initializer/README.md:57` — `"[Cursor Rules](../../docs/cursor/rules/)"`
- **Violated Source**: PRD #56 Phase 6 self-sufficiency contract; Phase 5 pattern CF-057–CF-059
- **Current State**: Relative directory path `../../docs/cursor/rules/` — breaks in distributed context
- **Expected State**: Full GitHub URL: `https://github.com/rodrigorjsf/agent-engineering-toolkit/tree/development/docs/cursor/rules/`
- **Impact**: Link 404s when plugin installed outside repo; directory link requires `tree/development/` prefix
- **Proposed Fix**: Replace with full GitHub URL using `tree/development/` for directory
- **Correction Notes**: Applied 2026-04-17 — replaced with full GitHub tree URL
- **Provenance**: N/A
- **Revalidation Method**: instruction-only/manual-validator
- **Revalidation Evidence**: Covered by CF-064 revalidation command
- **Gate Rerun Record**: N/A — no automated quality gate for cursor-initializer

---

### CF-067 — Relative doc link in README line 58 [MAJOR] — ✅ CLOSED

- **Check Category**: Self-Sufficiency
- **Scope**: cursor-initializer
- **Artifact**: `plugins/cursor-initializer/README.md`
- **Evidence**: `plugins/cursor-initializer/README.md:58` — `"[Cursor Subagents](../../docs/cursor/subagents/)"`
- **Violated Source**: PRD #56 Phase 6 self-sufficiency contract; Phase 5 pattern CF-057–CF-059
- **Current State**: Relative directory path `../../docs/cursor/subagents/` — breaks in distributed context
- **Expected State**: Full GitHub URL: `https://github.com/rodrigorjsf/agent-engineering-toolkit/tree/development/docs/cursor/subagents/`
- **Impact**: Same as CF-066
- **Proposed Fix**: Replace with full GitHub URL using `tree/development/` for directory
- **Correction Notes**: Applied 2026-04-17 — replaced with full GitHub tree URL
- **Provenance**: N/A
- **Revalidation Method**: instruction-only/manual-validator
- **Revalidation Evidence**: Covered by CF-064 revalidation command
- **Gate Rerun Record**: N/A — no automated quality gate for cursor-initializer

---

### CF-068 — Relative doc link in README line 68 [MAJOR] — ✅ CLOSED

- **Check Category**: Self-Sufficiency
- **Scope**: cursor-initializer
- **Artifact**: `plugins/cursor-initializer/README.md`
- **Evidence**: `plugins/cursor-initializer/README.md:68` — `"[A Complete Guide to AGENTS.md](../../docs/general-llm/a-guide-to-agents.md)"`
- **Violated Source**: PRD #56 Phase 6 self-sufficiency contract; Phase 5 pattern CF-057–CF-059
- **Current State**: Relative path `../../docs/general-llm/a-guide-to-agents.md` — breaks in distributed context
- **Expected State**: Full GitHub URL: `https://github.com/rodrigorjsf/agent-engineering-toolkit/blob/development/docs/general-llm/a-guide-to-agents.md`
- **Impact**: Link 404s when plugin installed outside repo
- **Proposed Fix**: Replace with full GitHub URL using `blob/development/`
- **Correction Notes**: Applied 2026-04-17 — replaced with full GitHub URL
- **Provenance**: N/A
- **Revalidation Method**: instruction-only/manual-validator
- **Revalidation Evidence**: Covered by CF-064 revalidation command
- **Gate Rerun Record**: N/A — no automated quality gate for cursor-initializer

---

### CF-069 — Second "Auto memory" row in automation-migration-guide.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination
- **Scope**: cursor-initializer
- **Artifact**: `plugins/cursor-initializer/skills/improve-cursor/references/automation-migration-guide.md`
- **Evidence**: `plugins/cursor-initializer/skills/improve-cursor/references/automation-migration-guide.md:106` — `"| Auto memory | Mention only | Mention only | System-managed; not a direct migration target |"`
- **Violated Source**: `cursor-plugin-bundle` (`docs/compliance/normative-source-matrix.md`) — "Forbidden: ALL CLAUDE-* sources" (CLAUDE-MEMORY); same rule as CF-062
- **Current State**: Distribution-Aware Recommendations table includes "Auto memory" row — a Claude Code-specific mechanism not available in Cursor; missed during initial walk-through (CF-062 only removed the Mechanism Comparison table row at line 87)
- **Expected State**: Distribution-Aware Recommendations table lists only Cursor-native mechanisms
- **Impact**: Same as CF-062 — Cursor developer guidance presents a Claude Code-only mechanism; Distribution table would mislead users into treating auto memory as a Cursor distribution option
- **Proposed Fix**: Remove the "Auto memory" row from the Distribution-Aware Recommendations table
- **Correction Notes**: Discovered during Task 14 revalidation (`grep -n "Auto memory"` returned line 106 as remaining hit after CF-062 correction). Applied 2026-04-17 — row removed from Distribution-Aware Recommendations table
- **Provenance**: N/A — removal only
- **Revalidation Method**: instruction-only/manual-validator
- **Revalidation Evidence**: `grep 'Auto memory' plugins/cursor-initializer/skills/improve-cursor/references/automation-migration-guide.md` → 0 results
- **Gate Rerun Record**: N/A — no automated quality gate for cursor-initializer

---

## 7.4 Summary

| Metric | Value |
|--------|-------|
| Total artifacts audited | 31 |
| Findings recorded | 10 (CF-060–CF-069) |
| Reviewed not-violation | 1 (CF-070 — see §7.5) |
| CRITICAL | 0 |
| MAJOR | 10 |
| MINOR | 0 |
| OPEN | 0 |
| IN-PROGRESS | 0 |
| CORRECTED | 0 |
| REVALIDATED | 0 |
| CLOSED | 10 |

**Gate Rerun**: N/A — no automated quality gate for cursor-initializer (confirmed `docs/compliance/artifact-audit-manifest.md §12`). Manual grep-based revalidation substitutes — all commands PASS.

**SCG-01 Parity**: Both `context-optimization.md` copies corrected in lockstep; Citations table verified identical after correction.

**Compliance Status**: COMPLETE — all 10 findings CLOSED, 0 OPEN.

---

## 7.5 Reviewed-Not-Violation: CF-070

**Candidate**: `plugins/cursor-initializer/README.md:63` — `https://docs.anthropic.com/en/docs/claude-code/memory`

**Trigger**: Global contamination revalidation grep pattern `claude-code/memory` matched this external URL.

**Normative Matrix Analysis** (`docs/compliance/normative-source-matrix.md`):

- CLAUDE-MEMORY source identifier is defined as the internal repository source: `docs/claude-code/memory/` — i.e., relative paths or source attributions pointing to the internal `docs/claude-code/memory/` directory tree
- The candidate is an external absolute URL (`https://docs.anthropic.com/...`) that happens to contain the substring `claude-code/memory` in its path component
- These are distinct: an external Anthropic documentation URL is a reference *to* a resource; CLAUDE-MEMORY contamination means *drawing authority from* the internal Claude Code memory docs as a normative source
- `cursor-plugin-bundle` normative matrix forbids CLAUDE-* **sources** — a public URL to Anthropic's documentation for cross-tool context is not a source attribution; it is a reader resource link

**Verdict**: NOT A VIOLATION under the narrow normative-matrix definition of CLAUDE-MEMORY. The URL is a reader reference to external documentation consistent with the README's "Documentation Base" section purpose. No correction required.

**Disposition**: Reviewed and dismissed 2026-04-17. Grep pattern false-positive documented to prevent re-raising in future audits.
