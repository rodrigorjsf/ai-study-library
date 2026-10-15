# Compliance Audit Report — agents-initializer

**Scope ID**: agents-initializer  
**Audit Date**: 2026-04-16  
**Auditor Phase**: 4 (Claude Code Scope Audit and Correction)  
**Plan Reference**: `.claude/PRPs/plans/claude-code-scope-audit-and-correction.plan.md`  
**Total Artifacts Audited**: 51 (per `docs/compliance/artifact-audit-manifest.md` §5)

---

## 7.2 Dashboard

| Category | Total | CRITICAL | MAJOR | MINOR |
|----------|-------|----------|-------|-------|
| Contamination | 0 | 0 | 0 | 0 |
| Self-Sufficiency | 0 | 0 | 0 | 0 |
| Normative-Alignment | 0 | 0 | 0 | 0 |
| Parity | 0 | 0 | 0 | 0 |
| Drift | 0 | 0 | 0 | 0 |
| Provenance | 0 | 0 | 0 | 0 |
| **Total** | **0** | **0** | **0** | **0** |

All three findings (CF-001–CF-003) opened at initial gate run and CLOSED after corrections applied in Phase 4 compliance session (2026-04-16). Quality gate rerun: all 4 scenarios PASS.

---

## 7.3 Findings

### CF-001 — Init Skills: Non-Standard Configuration Values Not Captured [MAJOR] — ✅ CLOSED

- **Check Category**: Normative-Alignment
- **Scope**: agents-initializer
- **Artifact**: `plugins/agents-initializer/skills/init-agents/`, `plugins/agents-initializer/skills/init-claude/`, `skills/init-agents/`, `skills/init-claude/` — templates and references
- **Evidence**: `.specs/reports/quality-gate-2026-04-16-findings.md` — "F001: Init Skills: Non-Standard Configuration Values Not Captured [MAJOR]" — scenario S1 (init-simple-project) returned PARTIAL for both distributions
- **Violated Source**: `quality-gate` G1 — "S1: init simple project — both distributions pass; GREEN required"
- **Current State**: Root template `## Tooling` section contains only command slots (`Build:`, `Test:`). No slot exists for non-standard configuration values (e.g., `strict = true`, `addopts = "--cov=src"`, `line-length = 88`). `codebase-analyzer.md` step 3 lists `[tool.pytest]`, `[tool.ruff]`, `[scripts]` but omits `[tool.mypy]`. `validation-criteria.md` quality checks verify non-standard commands but contain no check for non-standard configuration values.
- **Expected State**: Both distributions return GREEN for S1 — init skills capture non-standard configuration values alongside non-standard commands, codebase-analyzer detects mypy settings, and validation-criteria.md confirms configuration value capture.
- **Impact**: Init skills produce AGENTS.md/CLAUDE.md files that document non-standard commands but omit project-specific configuration values (mypy strictness, pytest coverage paths, custom lint rules), causing agents to run with unexpected defaults.
- **Proposed Fix**: (1) Add config-value slot to root template `## Tooling` in all four distributions; (2) Add `[tool.mypy]` to codebase-analyzer detection list; (3) Add "Non-standard configuration values captured" to `validation-criteria.md`.
- **Correction Notes**: Applied 2026-04-16 in Phase 4 compliance session. (1) `Config:` CONDITIONAL slot added to root templates in all 4 distributions; (2) `[tool.mypy]` detection + config value extraction added to `codebase-analyzer.md` (4 copies) and plugin agent; (3) "Non-standard configuration values documented" check added to `validation-criteria.md` (8 copies).
- **Provenance**: N/A
- **Revalidation Method**: automated-gate-pass
- **Revalidation Evidence**: Re-run `quality-gate` after applying proposed fixes; confirm G1 returns GREEN for both distributions.
- **Gate Rerun Record**: `.specs/reports/quality-gate-2026-04-16-findings.md` — post-correction rerun 2026-04-16: G1 PASS (both distributions). F001 RESOLVED.

---

### CF-002 — Init Skills: Migration Commands and Cross-Scope Build Prerequisites Missing [MAJOR] — ✅ CLOSED

- **Check Category**: Normative-Alignment
- **Scope**: agents-initializer
- **Artifact**: `plugins/agents-initializer/skills/init-agents/assets/templates/scoped-agents-md.md`, `plugins/agents-initializer/skills/init-claude/assets/templates/scoped-claude-md.md`, `skills/init-agents/assets/templates/scoped-agents-md.md`, `skills/init-claude/assets/templates/scoped-claude-md.md` — and `codebase-analyzer.md` and `validation-criteria.md` in both distributions
- **Evidence**: `.specs/reports/quality-gate-2026-04-16-findings.md` — "F002: Init Skills: Migration Commands and Cross-Scope Build Prerequisites Missing [MAJOR]" — scenario S2 (init-complex-monorepo) returned PARTIAL for both distributions (plugin slightly better due to agent isolation)
- **Violated Source**: `quality-gate` G2 — "S2: init complex monorepo — both distributions pass; GREEN required"
- **Current State**: Scoped template `## Tooling` has only `Build:` and `Test:` command slots; no migration/setup command slot. `codebase-analyzer.md` step 4 detects SQLAlchemy ORM but does not list migration tools (Alembic, Flyway, Prisma Migrate) with instruction to always report run command. Root template `## Tooling` has no cross-scope build prerequisites section. `validation-criteria.md` checks build/test commands but has no check for migration or setup commands.
- **Expected State**: Both distributions return GREEN for S2 — scoped templates accommodate migration commands, codebase-analyzer surfaces migration tool run commands, root template provides guidance for cross-scope build ordering constraints, and validation-criteria.md validates migration command coverage.
- **Impact**: Monorepo init produces AGENTS.md files missing critical setup commands (database migrations cause first-run failures) and missing cross-scope build ordering constraints (WASM-before-web type prerequisite chains silently absent from root).
- **Proposed Fix**: (1) Add `Migrate:` slot to scoped template `## Tooling` in all four distributions; (2) Add migration tools to codebase-analyzer detection (Alembic via `alembic.ini`, Flyway, Prisma Migrate); (3) Add cross-scope prerequisites slot to root template; (4) Add "migration/setup commands documented" to `validation-criteria.md`.
- **Correction Notes**: Applied 2026-04-16 in Phase 4 compliance session. (1) `Migrate:` CONDITIONAL slot added to scoped templates in all 4 distributions; (2) `Prerequisite:` slot added to root templates in all 4 distributions; (3) Migration tool detection (Alembic `alembic.ini`, Flyway, Prisma Migrate) added to `codebase-analyzer.md` (4 copies) and plugin agent; (4) "Non-standard migration/setup commands documented" check added to `validation-criteria.md` (8 copies).
- **Provenance**: N/A
- **Revalidation Method**: automated-gate-pass
- **Revalidation Evidence**: Re-run `quality-gate` after applying proposed fixes; confirm G2 returns GREEN for both distributions.
- **Gate Rerun Record**: `.specs/reports/quality-gate-2026-04-16-findings.md` — post-correction rerun 2026-04-16: G2 PASS (both distributions). F002 RESOLVED.

---

### CF-003 — Improve Skills: Missing Precision Calibration for High-Quality Files [MAJOR] — ✅ CLOSED

- **Check Category**: Normative-Alignment
- **Scope**: agents-initializer
- **Artifact**: `plugins/agents-initializer/skills/improve-agents/references/validation-criteria.md`, `plugins/agents-initializer/skills/improve-claude/references/validation-criteria.md`, `skills/improve-agents/references/validation-criteria.md`, `skills/improve-claude/references/validation-criteria.md` — and `evaluation-criteria.md`, `what-not-to-include.md`, `file-evaluator.md` across all improve skill directories
- **Evidence**: `.specs/reports/quality-gate-2026-04-16-findings.md` — "F003: Improve Skills: Missing Precision Calibration for High-Quality Files [MAJOR]" — scenario S4 (improve-reasonable-file) returned PARTIAL for all distributions (equal quality)
- **Violated Source**: `quality-gate` G4 — "S4: improve reasonable file — surgical changes only; GREEN required"
- **Current State**: No restrained-improve calibration exists for files scoring ≥ 7/10. `file-evaluator.md` has no DELETE_CANDIDATE row for standard default commands already in the file being evaluated. `validation-criteria.md` lists "15–40 lines (recommended)" under the "Hard Limits / Auto-fail" header — contradictory qualifier risks unnecessary validation loop iterations on reasonable files. `what-not-to-include.md` provides no guidance distinguishing "architectural constraint referencing paths" from "directory listing." No over-specification boundary example distinguishing tsconfig-enforced rules from project-specific decisions.
- **Expected State**: All distributions return GREEN for S4 — improve skills apply surgical changes to high-quality files, preserving architectural constraints and project-specific conventions, with hard-limit ambiguity resolved and DELETE_CANDIDATE guidance for standard defaults.
- **Impact**: Improve skills risk over-modifying reasonable files: removing architectural path constraints, triggering unnecessary restructuring loops, and deleting project-specific TypeScript conventions that agents genuinely need. A 7/10 file could exit the improve workflow at lower quality than it entered.
- **Proposed Fix**: (1) Add calibrated-improvement mode to `evaluation-criteria.md` for quality ≥ 7/10 files; (2) Add DELETE_CANDIDATE row for standard default commands to `file-evaluator.md` bloat indicators; (3) Split `validation-criteria.md` Hard Limits into auto-fail and advisory sub-tables; (4) Add architectural-path vs directory-listing distinction to `what-not-to-include.md`; (5) Add tsconfig-enforced vs project-convention differentiation example to `evaluation-criteria.md`.
- **Correction Notes**: Applied 2026-04-16 in Phase 4 compliance session. (1) Calibrated Improvement Mode section added to `evaluation-criteria.md` (4 copies) with calibrated-mode tiebreaker for progressive disclosure threshold; (2) DELETE_CANDIDATE row for standard default commands added to `file-evaluator.md` (2 standalone copies) and plugin agent; (3) Hard Limits split into auto-fail and advisory sub-tables in `validation-criteria.md` (8 copies); (4) "Architectural path trap" guidance added to `what-not-to-include.md` (8 copies) and plugin `file-evaluator` agent; (5) tsconfig-enforced vs project-convention differentiation example added to `evaluation-criteria.md`. Supplementary fix: "Contradictions (within or between files)" wording applied to `validation-criteria.md` (8 copies).
- **Provenance**: N/A
- **Revalidation Method**: automated-gate-pass
- **Revalidation Evidence**: Re-run `quality-gate` after applying proposed fixes; confirm G4 returns GREEN for all distributions.
- **Gate Rerun Record**: `.specs/reports/quality-gate-2026-04-16-findings.md` — post-correction rerun 2026-04-16: G3 PASS, G4 PASS (all distributions). F003 RESOLVED.

---

## 7.4 Correction Log

| CF-NNN ID | State | Correction Date | Revalidation Method | Revalidation Date |
|-----------|-------|-----------------|--------------------|--------------------|
| CF-001 | CLOSED | 2026-04-16 | automated-gate-pass | 2026-04-16 |
| CF-002 | CLOSED | 2026-04-16 | automated-gate-pass | 2026-04-16 |
| CF-003 | CLOSED | 2026-04-16 | automated-gate-pass | 2026-04-16 |

All three findings closed. Quality gate post-correction rerun (2026-04-16): PASS. Phase 4 agents-initializer scope complete — 0 open findings.

---

## 7.5 Gate Rerun Summary

| Gate | Scope | Run Date | Report Path | Result | Relevant CF-NNN IDs |
|------|-------|----------|-------------|--------|---------------------|
| quality-gate (initial) | agents-initializer + standalone | 2026-04-16 | `.specs/reports/quality-gate-2026-04-16-findings.md` | FAIL (3 MAJOR) | CF-001, CF-002, CF-003 |
| quality-gate (post-correction) | agents-initializer + standalone | 2026-04-16 | `.specs/reports/quality-gate-2026-04-16-findings.md` | ✅ PASS | CF-001, CF-002, CF-003 |

**Gate result: PASS.** All 4 scenarios (G1–G4) GREEN for all distributions after corrections. Phase 4 agents-initializer scope complete. CF-NNN sequence continues at CF-004 for agent-customizer scope.

---

## Audit Notes

**Direct Validation Summary (Tasks 2–5)**

All 48 gated artifacts (4 SKILL.md + 3 agent files + 22 reference files + 19 template files) passed the 7-step validator protocol with zero CF-NNN findings:

- **SKILL.md files (4)**: Frontmatter valid; correct delegation patterns (codebase-analyzer, scope-detector, file-evaluator); self-validation phase present; no inline bash; ≤ 500 lines; no contamination. ✅
- **Agent files (3)**: Correct model (sonnet); correct maxTurns (15/15/20); read-only tools; structured output with confidence filtering; no agent spawning. ✅
- **Reference files (22)**: All ≤ 200 lines (max 171); all have source attribution; all TOC-compliant for files > 100 lines; no nested references; no contamination; SCG-01–SCG-07 parity verified within scope. ✅
- **Template files (19)**: All ≤ 200 lines; all have exactly one `<!-- TEMPLATE:` metadata block; TCG-01–TCG-07 parity verified within scope; init/improve boundary respected (no migration templates in init skills). ✅
- **Non-gated artifacts (3)**: plugin.json (valid JSON, all 6 required fields), CLAUDE.md (12 lines within 10–30 target), README.md (272 lines, all 10 sections in correct order, verbatim cost block). Revalidation Method: `instruction-only/manual-validator`. Gate Rerun Record: N/A. ✅
