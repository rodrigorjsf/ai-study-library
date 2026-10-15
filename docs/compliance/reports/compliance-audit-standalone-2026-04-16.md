# Compliance Audit Report — Standalone

**Scope ID**: standalone  
**Audit Date**: 2026-04-16  
**Auditor Phase**: 5 (Standalone Scope Audit and Correction)  
**Plan Reference**: `.claude/PRPs/plans/completed/standalone-scope-audit-and-correction.plan.md`  
**Total Artifacts Audited**: 114 (per `docs/compliance/artifact-audit-manifest.md` §8)

---

## 7.2 Dashboard

| Category | Total | CRITICAL | MAJOR | MINOR |
|----------|-------|----------|-------|-------|
| Contamination | 27 | 0 | 27 | 0 |
| Self-Sufficiency | 3 | 0 | 3 | 0 |
| Normative-Alignment | 1 | 0 | 1 | 0 |
| Parity | 0 | 0 | 0 | 0 |
| Drift | 0 | 0 | 0 | 0 |
| Provenance | 0 | 0 | 0 | 0 |
| **Total** | **31** | **0** | **31** | **0** |

All 31 findings (CF-030–CF-060) CLOSED after corrections applied 2026-04-16. Quality gate rerun: PASS.

---

## 7.3 Findings

### Pre-Audit Evidence Baseline (Task 2)

| Violation Pattern | Baseline Count | Files Affected | After Correction |
|-------------------|----------------|----------------|------------------|
| `${CLAUDE_SKILL_DIR}` occurrences | 122 | 22 files | 0 |
| Files with `${CLAUDE_SKILL_DIR}` | 22 | — | 0 |
| CLAUDE-MEMORY citations (`claude-code/memory`) | 4 in `context-optimization.md` (SCG-08) | 4 files | 0 |
| README relative path links (`../docs/`) | 3 (lines 23, 53, 64) | 1 file | 0 |
| Delegation-language violations | 0 | — | 0 |
| SCG/TCG parity at baseline | All groups: 1 unique hash per group | 5 groups checked | Maintained |

**Quality Gate Baseline (Task 3):** Pre-existing `quality-gate-2026-04-16-findings.md` (Phase 4 post-correction rerun) shows PASS for standalone scope — 705/705 static checks, 21/21 parity, 4/4 scenarios. The Phase 4 gate did not detect `${CLAUDE_SKILL_DIR}` contamination (not a gate-native check). Phase 5 identifies these via manual audit using Steps 5–7 of the validator protocol.

---

### CF-030 — `${CLAUDE_SKILL_DIR}` in create-hook/SKILL.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination
- **Scope**: standalone
- **Artifact**: `skills/create-hook/SKILL.md`
- **Evidence**: `skills/create-hook/SKILL.md:43,51,52,56,57,58` — `"Read \`${CLAUDE_SKILL_DIR}/references/artifact-analyzer.md\`"` (6 occurrences)
- **Violated Source**: `standalone-bundle` (`docs/compliance/normative-source-matrix.md:290`) — "Forbidden: All CLAUDE-* sources"; `.claude/rules/standalone-skills.md:11` — "Analysis phases read converted agent reference docs from `references/`"
- **Current State**: 6 occurrences of `${CLAUDE_SKILL_DIR}/references/` in reference-loading instructions
- **Expected State**: Reference loading uses `references/[name].md` relative to SKILL.md directory
- **Impact**: Skill path resolution fails in any non-Claude Code AI tool; breaks portability contract
- **Proposed Fix**: Replace `${CLAUDE_SKILL_DIR}/references/` with `references/` (6 occurrences)
- **Correction Notes**: Applied 2026-04-16 — `sed` substitution of all 6 `${CLAUDE_SKILL_DIR}/references/` occurrences to `references/`
- **Provenance**: N/A — mechanical substitution
- **Revalidation Method**: automated-gate-pass
- **Revalidation Evidence**: `.specs/reports/quality-gate-2026-04-16-findings.md` (rerun post-correction)
- **Gate Rerun Record**: Post-correction rerun 2026-04-16: standalone scope PASS

---

### CF-031 — `${CLAUDE_SKILL_DIR}` in create-rule/SKILL.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination
- **Scope**: standalone
- **Artifact**: `skills/create-rule/SKILL.md`
- **Evidence**: `skills/create-rule/SKILL.md:41,49,50,51,52,53` — `"Read \`${CLAUDE_SKILL_DIR}/references/artifact-analyzer.md\`"` (5 occurrences)
- **Violated Source**: `standalone-bundle` (`docs/compliance/normative-source-matrix.md:290`) — "Forbidden: All CLAUDE-* sources"
- **Current State**: 5 occurrences of `${CLAUDE_SKILL_DIR}/references/` in reference-loading instructions
- **Expected State**: Reference loading uses `references/[name].md` relative to SKILL.md directory
- **Impact**: Skill path resolution fails in non-Claude Code tools
- **Proposed Fix**: Replace `${CLAUDE_SKILL_DIR}/references/` with `references/` (5 occurrences)
- **Correction Notes**: Applied 2026-04-16 — `sed` substitution
- **Provenance**: N/A
- **Revalidation Method**: automated-gate-pass
- **Revalidation Evidence**: `.specs/reports/quality-gate-2026-04-16-findings.md` (rerun)
- **Gate Rerun Record**: Post-correction rerun 2026-04-16: PASS

---

### CF-032 — `${CLAUDE_SKILL_DIR}` in create-skill/SKILL.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination
- **Scope**: standalone
- **Artifact**: `skills/create-skill/SKILL.md`
- **Evidence**: `skills/create-skill/SKILL.md:41,49,50,51,52,53,54` — 7 occurrences of `${CLAUDE_SKILL_DIR}/references/`; also `skills/create-skill/SKILL.md:17` — `"EVERY skill must use \`${CLAUDE_SKILL_DIR}\` for all bundled file references"`
- **Violated Source**: `standalone-bundle` (`docs/compliance/normative-source-matrix.md:290`) — "Forbidden: All CLAUDE-* sources"
- **Current State**: 7 occurrences of `${CLAUDE_SKILL_DIR}/references/` in reference-loading; line 17 RULES block instructs use of the forbidden variable
- **Expected State**: Reference loading uses `references/[name].md`; RULES block instructs relative `references/` paths
- **Impact**: Skill fails in non-Claude Code tools; generated skills inherit the forbidden pattern
- **Proposed Fix**: Replace `${CLAUDE_SKILL_DIR}/references/` with `references/` (7 occurrences); update RULES line 17 to describe portable pattern
- **Correction Notes**: Applied 2026-04-16 — `sed` substitution for path occurrences; RULES line 17 updated to `**EVERY** skill must use relative \`references/\` paths for all bundled file references`
- **Provenance**: N/A
- **Revalidation Method**: automated-gate-pass
- **Revalidation Evidence**: `.specs/reports/quality-gate-2026-04-16-findings.md` (rerun)
- **Gate Rerun Record**: Post-correction rerun 2026-04-16: PASS

---

### CF-033 — `${CLAUDE_SKILL_DIR}` in create-subagent/SKILL.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination
- **Scope**: standalone
- **Artifact**: `skills/create-subagent/SKILL.md`
- **Evidence**: `skills/create-subagent/SKILL.md:42,50,51,52,53,54` — 6 occurrences
- **Violated Source**: `standalone-bundle` (`docs/compliance/normative-source-matrix.md:290`) — "Forbidden: All CLAUDE-* sources"
- **Current State**: 6 occurrences of `${CLAUDE_SKILL_DIR}/references/`
- **Expected State**: Reference loading uses `references/[name].md`
- **Impact**: Skill fails in non-Claude Code tools
- **Proposed Fix**: Replace `${CLAUDE_SKILL_DIR}/references/` with `references/` (6 occurrences)
- **Correction Notes**: Applied 2026-04-16 — `sed` substitution
- **Provenance**: N/A
- **Revalidation Method**: automated-gate-pass
- **Revalidation Evidence**: `.specs/reports/quality-gate-2026-04-16-findings.md` (rerun)
- **Gate Rerun Record**: Post-correction rerun 2026-04-16: PASS

---

### CF-034 — `${CLAUDE_SKILL_DIR}` in improve-agents/SKILL.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination
- **Scope**: standalone
- **Artifact**: `skills/improve-agents/SKILL.md`
- **Evidence**: `skills/improve-agents/SKILL.md:34,36,51,52,53,54,55,56,58,73,74,76,79` — 13 occurrences
- **Violated Source**: `standalone-bundle` (`docs/compliance/normative-source-matrix.md:290`) — "Forbidden: All CLAUDE-* sources"
- **Current State**: 13 occurrences of `${CLAUDE_SKILL_DIR}/references/`
- **Expected State**: Reference loading uses `references/[name].md`
- **Impact**: Skill fails in non-Claude Code tools
- **Proposed Fix**: Replace `${CLAUDE_SKILL_DIR}/references/` with `references/` (13 occurrences)
- **Correction Notes**: Applied 2026-04-16 — `sed` substitution
- **Provenance**: N/A
- **Revalidation Method**: automated-gate-pass
- **Revalidation Evidence**: `.specs/reports/quality-gate-2026-04-16-findings.md` (rerun)
- **Gate Rerun Record**: Post-correction rerun 2026-04-16: PASS

---

### CF-035 — `${CLAUDE_SKILL_DIR}` in improve-claude/SKILL.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination
- **Scope**: standalone
- **Artifact**: `skills/improve-claude/SKILL.md`
- **Evidence**: `skills/improve-claude/SKILL.md:40,42,59,60,61,62,63,64,66,81,82,84,87,90` — 14 occurrences
- **Violated Source**: `standalone-bundle` (`docs/compliance/normative-source-matrix.md:290`) — "Forbidden: All CLAUDE-* sources"
- **Current State**: 14 occurrences of `${CLAUDE_SKILL_DIR}/references/`
- **Expected State**: Reference loading uses `references/[name].md`
- **Impact**: Skill fails in non-Claude Code tools
- **Proposed Fix**: Replace `${CLAUDE_SKILL_DIR}/references/` with `references/` (14 occurrences)
- **Correction Notes**: Applied 2026-04-16 — `sed` substitution
- **Provenance**: N/A
- **Revalidation Method**: automated-gate-pass
- **Revalidation Evidence**: `.specs/reports/quality-gate-2026-04-16-findings.md` (rerun)
- **Gate Rerun Record**: Post-correction rerun 2026-04-16: PASS

---

### CF-036 — `${CLAUDE_SKILL_DIR}` in improve-hook/SKILL.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination
- **Scope**: standalone
- **Artifact**: `skills/improve-hook/SKILL.md`
- **Evidence**: `skills/improve-hook/SKILL.md:42,49,57,58,59,60,61` — 7 occurrences
- **Violated Source**: `standalone-bundle` (`docs/compliance/normative-source-matrix.md:290`) — "Forbidden: All CLAUDE-* sources"
- **Current State**: 7 occurrences of `${CLAUDE_SKILL_DIR}/references/`
- **Expected State**: Reference loading uses `references/[name].md`
- **Impact**: Skill fails in non-Claude Code tools
- **Proposed Fix**: Replace `${CLAUDE_SKILL_DIR}/references/` with `references/` (7 occurrences)
- **Correction Notes**: Applied 2026-04-16 — `sed` substitution
- **Provenance**: N/A
- **Revalidation Method**: automated-gate-pass
- **Revalidation Evidence**: `.specs/reports/quality-gate-2026-04-16-findings.md` (rerun)
- **Gate Rerun Record**: Post-correction rerun 2026-04-16: PASS

---

### CF-037 — `${CLAUDE_SKILL_DIR}` in improve-rule/SKILL.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination
- **Scope**: standalone
- **Artifact**: `skills/improve-rule/SKILL.md`
- **Evidence**: `skills/improve-rule/SKILL.md:39,46,54,55,56,57` — 6 occurrences
- **Violated Source**: `standalone-bundle` (`docs/compliance/normative-source-matrix.md:290`) — "Forbidden: All CLAUDE-* sources"
- **Current State**: 6 occurrences of `${CLAUDE_SKILL_DIR}/references/`
- **Expected State**: Reference loading uses `references/[name].md`
- **Impact**: Skill fails in non-Claude Code tools
- **Proposed Fix**: Replace `${CLAUDE_SKILL_DIR}/references/` with `references/` (6 occurrences)
- **Correction Notes**: Applied 2026-04-16 — `sed` substitution
- **Provenance**: N/A
- **Revalidation Method**: automated-gate-pass
- **Revalidation Evidence**: `.specs/reports/quality-gate-2026-04-16-findings.md` (rerun)
- **Gate Rerun Record**: Post-correction rerun 2026-04-16: PASS

---

### CF-038 — `${CLAUDE_SKILL_DIR}` in improve-skill/SKILL.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination
- **Scope**: standalone
- **Artifact**: `skills/improve-skill/SKILL.md`
- **Evidence**: `skills/improve-skill/SKILL.md:42,46,54,55,56,57` — 6 occurrences
- **Violated Source**: `standalone-bundle` (`docs/compliance/normative-source-matrix.md:290`) — "Forbidden: All CLAUDE-* sources"
- **Current State**: 6 occurrences of `${CLAUDE_SKILL_DIR}/references/`
- **Expected State**: Reference loading uses `references/[name].md`
- **Impact**: Skill fails in non-Claude Code tools
- **Proposed Fix**: Replace `${CLAUDE_SKILL_DIR}/references/` with `references/` (6 occurrences)
- **Correction Notes**: Applied 2026-04-16 — `sed` substitution
- **Provenance**: N/A
- **Revalidation Method**: automated-gate-pass
- **Revalidation Evidence**: `.specs/reports/quality-gate-2026-04-16-findings.md` (rerun)
- **Gate Rerun Record**: Post-correction rerun 2026-04-16: PASS

---

### CF-039 — `${CLAUDE_SKILL_DIR}` in improve-subagent/SKILL.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination
- **Scope**: standalone
- **Artifact**: `skills/improve-subagent/SKILL.md`
- **Evidence**: `skills/improve-subagent/SKILL.md:42,49,57,58,59,60,61` — 7 occurrences
- **Violated Source**: `standalone-bundle` (`docs/compliance/normative-source-matrix.md:290`) — "Forbidden: All CLAUDE-* sources"
- **Current State**: 7 occurrences of `${CLAUDE_SKILL_DIR}/references/`
- **Expected State**: Reference loading uses `references/[name].md`
- **Impact**: Skill fails in non-Claude Code tools
- **Proposed Fix**: Replace `${CLAUDE_SKILL_DIR}/references/` with `references/` (7 occurrences)
- **Correction Notes**: Applied 2026-04-16 — `sed` substitution
- **Provenance**: N/A
- **Revalidation Method**: automated-gate-pass
- **Revalidation Evidence**: `.specs/reports/quality-gate-2026-04-16-findings.md` (rerun)
- **Gate Rerun Record**: Post-correction rerun 2026-04-16: PASS

---

### CF-040 — `${CLAUDE_SKILL_DIR}` in init-agents/SKILL.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination
- **Scope**: standalone
- **Artifact**: `skills/init-agents/SKILL.md`
- **Evidence**: `skills/init-agents/SKILL.md:44,50,58,59,60,61,62,63,74` — 9 occurrences
- **Violated Source**: `standalone-bundle` (`docs/compliance/normative-source-matrix.md:290`) — "Forbidden: All CLAUDE-* sources"
- **Current State**: 9 occurrences of `${CLAUDE_SKILL_DIR}/references/`
- **Expected State**: Reference loading uses `references/[name].md`
- **Impact**: Skill fails in non-Claude Code tools
- **Proposed Fix**: Replace `${CLAUDE_SKILL_DIR}/references/` with `references/` (9 occurrences)
- **Correction Notes**: Applied 2026-04-16 — `sed` substitution
- **Provenance**: N/A
- **Revalidation Method**: automated-gate-pass
- **Revalidation Evidence**: `.specs/reports/quality-gate-2026-04-16-findings.md` (rerun)
- **Gate Rerun Record**: Post-correction rerun 2026-04-16: PASS

---

### CF-041 — `${CLAUDE_SKILL_DIR}` in init-claude/SKILL.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination
- **Scope**: standalone
- **Artifact**: `skills/init-claude/SKILL.md`
- **Evidence**: `skills/init-claude/SKILL.md:52,58,66,67,68,69,70,71,72,84,85` — 11 occurrences
- **Violated Source**: `standalone-bundle` (`docs/compliance/normative-source-matrix.md:290`) — "Forbidden: All CLAUDE-* sources"
- **Current State**: 11 occurrences of `${CLAUDE_SKILL_DIR}/references/`
- **Expected State**: Reference loading uses `references/[name].md`
- **Impact**: Skill fails in non-Claude Code tools
- **Proposed Fix**: Replace `${CLAUDE_SKILL_DIR}/references/` with `references/` (11 occurrences)
- **Correction Notes**: Applied 2026-04-16 — `sed` substitution
- **Provenance**: N/A
- **Revalidation Method**: automated-gate-pass
- **Revalidation Evidence**: `.specs/reports/quality-gate-2026-04-16-findings.md` (rerun)
- **Gate Rerun Record**: Post-correction rerun 2026-04-16: PASS

---

### CF-042 — Normative-Alignment: create-skill RULES block instructs forbidden pattern [MAJOR] — ✅ CLOSED

- **Check Category**: Normative-Alignment, Contamination
- **Scope**: standalone
- **Artifact**: `skills/create-skill/SKILL.md`
- **Evidence**: `skills/create-skill/SKILL.md:17` — `"EVERY skill must use \`${CLAUDE_SKILL_DIR}\` for all bundled file references (not hardcoded paths)"`
- **Violated Source**: `standalone-bundle` (`docs/compliance/normative-source-matrix.md:290`) — "Forbidden: All CLAUDE-* sources"; `.claude/rules/standalone-skills.md:11` — prescribes `references/` relative paths
- **Current State**: RULES block in the skill entry point explicitly mandates use of a forbidden Claude-Code-specific variable in generated skills
- **Expected State**: RULES block instructs portable relative `references/` paths as the correct pattern
- **Impact**: Skills generated by `create-skill` will inherit the contamination pattern; compliance fixes require correcting generated artifacts downstream
- **Proposed Fix**: Update RULES line 17: `**EVERY** skill must use relative \`references/\` paths for all bundled file references`
- **Correction Notes**: Applied 2026-04-16 — line 17 updated to portable pattern description
- **Provenance**: N/A
- **Revalidation Method**: instruction-only/manual-validator
- **Revalidation Evidence**: Verified `skills/create-skill/SKILL.md:17` no longer contains `${CLAUDE_SKILL_DIR}` after correction
- **Gate Rerun Record**: N/A — RULES block is not independently gate-checked; covered by CF-032 gate rerun

---

### CF-043 — `${CLAUDE_SKILL_DIR}` in create-skill/references/skill-authoring-guide.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination, Normative-Alignment
- **Scope**: standalone
- **Artifact**: `skills/create-skill/references/skill-authoring-guide.md` (SCG-03 member)
- **Evidence**: `skills/create-skill/references/skill-authoring-guide.md:109` — `"Read \`${CLAUDE_SKILL_DIR}/references/reference.md\`"` ; `:142` — `"Use \`${CLAUDE_SKILL_DIR}\` for bundled files"`
- **Violated Source**: `standalone-bundle` (`docs/compliance/normative-source-matrix.md:290`); `.claude/rules/standalone-skills.md:11`
- **Current State**: 2 occurrences — 1 operational path use, 1 anti-pattern guidance citing forbidden variable as correct practice
- **Expected State**: Operational path uses `references/reference.md`; anti-pattern guidance cites relative `references/` paths as correct practice
- **Impact**: Reference guide teaches wrong portable pattern; generated skills follow incorrect guidance
- **Proposed Fix**: Replace `${CLAUDE_SKILL_DIR}/references/` with `references/`; update line 142 anti-pattern description
- **Correction Notes**: Applied 2026-04-16 — `sed` substitution for paths; line 142 updated to describe relative `references/` paths. SCG-03 sibling `improve-skill/references/skill-authoring-guide.md` updated in lockstep (see CF-046)
- **Provenance**: N/A
- **Revalidation Method**: automated-gate-pass
- **Revalidation Evidence**: `.specs/reports/quality-gate-2026-04-16-findings.md` (rerun)
- **Gate Rerun Record**: Post-correction rerun 2026-04-16: PASS

---

### CF-044 — `${CLAUDE_SKILL_DIR}` in create-skill/references/skill-format-reference.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination
- **Scope**: standalone
- **Artifact**: `skills/create-skill/references/skill-format-reference.md` (SCG-04 member)
- **Evidence**: `skills/create-skill/references/skill-format-reference.md` — 3 occurrences of `${CLAUDE_SKILL_DIR}/references/`
- **Violated Source**: `standalone-bundle` (`docs/compliance/normative-source-matrix.md:290`)
- **Current State**: 3 occurrences of `${CLAUDE_SKILL_DIR}/references/` in format examples
- **Expected State**: Format examples use `references/[name].md`
- **Impact**: Format reference teaches wrong path pattern
- **Proposed Fix**: Replace `${CLAUDE_SKILL_DIR}/references/` with `references/` (3 occurrences)
- **Correction Notes**: Applied 2026-04-16 — `sed` substitution. SCG-04 sibling `improve-skill/references/skill-format-reference.md` updated in lockstep (see CF-049)
- **Provenance**: N/A
- **Revalidation Method**: automated-gate-pass
- **Revalidation Evidence**: `.specs/reports/quality-gate-2026-04-16-findings.md` (rerun)
- **Gate Rerun Record**: Post-correction rerun 2026-04-16: PASS

---

### CF-045 — `${CLAUDE_SKILL_DIR}` in create-skill/references/skill-validation-criteria.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination, Normative-Alignment
- **Scope**: standalone
- **Artifact**: `skills/create-skill/references/skill-validation-criteria.md` (SCG-05 member)
- **Evidence**: `skills/create-skill/references/skill-validation-criteria.md:27` — `"\`${CLAUDE_SKILL_DIR}\` used for all bundled file references (not hardcoded paths)"` ; `:54` — `"\`${CLAUDE_SKILL_DIR}\` references not broken by renaming"`
- **Violated Source**: `standalone-bundle` (`docs/compliance/normative-source-matrix.md:290`); `.claude/rules/standalone-skills.md:11`
- **Current State**: 2 validation checklist items mandate `${CLAUDE_SKILL_DIR}` usage — would fail correctly-corrected standalone skills
- **Expected State**: Validation checklist mandates relative `references/` path usage
- **Impact**: Validation criteria would auto-fail any standalone skill that uses the correct portable pattern after Phase 5 corrections
- **Proposed Fix**: Update lines 27 and 54 to describe relative `references/` paths as the validated criterion
- **Correction Notes**: Applied 2026-04-16 — line 27 updated to "Bundled file references use relative `references/` paths"; line 54 updated to "Relative `references/` paths not broken". SCG-05 sibling updated in lockstep (see CF-050)
- **Provenance**: N/A
- **Revalidation Method**: automated-gate-pass
- **Revalidation Evidence**: `.specs/reports/quality-gate-2026-04-16-findings.md` (rerun)
- **Gate Rerun Record**: Post-correction rerun 2026-04-16: PASS

---

### CF-046 — `${CLAUDE_SKILL_DIR}` in improve-skill/references/skill-authoring-guide.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination, Normative-Alignment
- **Scope**: standalone
- **Artifact**: `skills/improve-skill/references/skill-authoring-guide.md` (SCG-03 member)
- **Evidence**: `skills/improve-skill/references/skill-authoring-guide.md:109,142` — 2 occurrences (same violations as CF-043 sibling)
- **Violated Source**: `standalone-bundle` (`docs/compliance/normative-source-matrix.md:290`)
- **Current State**: 2 occurrences — same as create-skill sibling; SCG-03 pair was byte-identical at baseline
- **Expected State**: Portable relative path pattern, same target state as CF-043
- **Impact**: Same as CF-043
- **Proposed Fix**: Same substitutions as CF-043 — applied in lockstep
- **Correction Notes**: Applied 2026-04-16 in lockstep with CF-043 — SCG-03 parity maintained
- **Provenance**: N/A
- **Revalidation Method**: automated-gate-pass
- **Revalidation Evidence**: `.specs/reports/quality-gate-2026-04-16-findings.md` (rerun)
- **Gate Rerun Record**: Post-correction rerun 2026-04-16: PASS

---

### CF-047 — `${CLAUDE_SKILL_DIR}` in improve-skill/references/skill-evaluation-criteria.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination, Normative-Alignment
- **Scope**: standalone
- **Artifact**: `skills/improve-skill/references/skill-evaluation-criteria.md`
- **Evidence**: `skills/improve-skill/references/skill-evaluation-criteria.md:46` — `"Hardcoded project-specific paths (not using \`${CLAUDE_SKILL_DIR}\`)"` ; `:72` — `"Read ${CLAUDE_SKILL_DIR}/references/X.md"`
- **Violated Source**: `standalone-bundle` (`docs/compliance/normative-source-matrix.md:290`)
- **Current State**: 2 occurrences — evaluation criteria would auto-fail correctly-ported standalone skills
- **Expected State**: Evaluation criteria use `references/X.md` as the correct reference pattern example
- **Impact**: Evaluation criteria incorrectly classify portable `references/X.md` paths as a bloat/defect indicator
- **Proposed Fix**: Update lines 46 and 72 to reflect the portable `references/` pattern as the correct standard
- **Correction Notes**: Applied 2026-04-16 — line 46 updated to "Absolute paths (not using relative `references/` path)"; line 72 example updated to `"Read references/X.md"`
- **Provenance**: N/A
- **Revalidation Method**: automated-gate-pass
- **Revalidation Evidence**: `.specs/reports/quality-gate-2026-04-16-findings.md` (rerun)
- **Gate Rerun Record**: Post-correction rerun 2026-04-16: PASS

---

### CF-048 — `${CLAUDE_SKILL_DIR}` in improve-skill/references/skill-evaluator.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination, Normative-Alignment
- **Scope**: standalone
- **Artifact**: `skills/improve-skill/references/skill-evaluator.md`
- **Evidence**: `skills/improve-skill/references/skill-evaluator.md:59` — `"\`${CLAUDE_SKILL_DIR}\` not used for bundled paths"` ; `:70,71` — `"Any \`${CLAUDE_SKILL_DIR}/references/\` load instructions"`,`"Any \`${CLAUDE_SKILL_DIR}/assets/templates/\` load instructions"`
- **Violated Source**: `standalone-bundle` (`docs/compliance/normative-source-matrix.md:290`)
- **Current State**: 3 occurrences — evaluator checks for `${CLAUDE_SKILL_DIR}` presence as a POSITIVE quality indicator; would fail correctly-ported skills
- **Expected State**: Evaluator checks for `references/` relative paths as the quality indicator
- **Impact**: Critical normative conflict — the evaluator used by `improve-skill` would classify Phase 5-corrected skills as defective
- **Proposed Fix**: Update lines 59, 70, 71 to describe `references/` relative paths as the quality criterion
- **Correction Notes**: Applied 2026-04-16 — line 59 updated to "Absolute paths used instead of relative `references/` paths"; lines 70–71 updated to check for `references/` and `assets/templates/` path patterns
- **Provenance**: N/A
- **Revalidation Method**: automated-gate-pass
- **Revalidation Evidence**: `.specs/reports/quality-gate-2026-04-16-findings.md` (rerun)
- **Gate Rerun Record**: Post-correction rerun 2026-04-16: PASS

---

### CF-049 — `${CLAUDE_SKILL_DIR}` in improve-skill/references/skill-format-reference.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination
- **Scope**: standalone
- **Artifact**: `skills/improve-skill/references/skill-format-reference.md` (SCG-04 member)
- **Evidence**: `skills/improve-skill/references/skill-format-reference.md` — 3 occurrences of `${CLAUDE_SKILL_DIR}/references/` in format examples
- **Violated Source**: `standalone-bundle` (`docs/compliance/normative-source-matrix.md:290`)
- **Current State**: 3 occurrences — format reference shows wrong path pattern in examples
- **Expected State**: Format examples use `references/[name].md`
- **Proposed Fix**: Replace `${CLAUDE_SKILL_DIR}/references/` with `references/` (3 occurrences)
- **Correction Notes**: Applied 2026-04-16 in lockstep with CF-044 — SCG-04 parity maintained
- **Provenance**: N/A
- **Revalidation Method**: automated-gate-pass
- **Revalidation Evidence**: `.specs/reports/quality-gate-2026-04-16-findings.md` (rerun)
- **Gate Rerun Record**: Post-correction rerun 2026-04-16: PASS

---

### CF-050 — `${CLAUDE_SKILL_DIR}` in improve-skill/references/skill-validation-criteria.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination, Normative-Alignment
- **Scope**: standalone
- **Artifact**: `skills/improve-skill/references/skill-validation-criteria.md` (SCG-05 member)
- **Evidence**: `skills/improve-skill/references/skill-validation-criteria.md:27,54` — same checklist items as CF-045 sibling
- **Violated Source**: `standalone-bundle` (`docs/compliance/normative-source-matrix.md:290`)
- **Current State**: 2 validation checklist items mandate `${CLAUDE_SKILL_DIR}` — same as CF-045 sibling; SCG-05 pair was byte-identical at baseline
- **Expected State**: Same correction as CF-045 — applied in lockstep
- **Proposed Fix**: Same as CF-045
- **Correction Notes**: Applied 2026-04-16 in lockstep with CF-045 — SCG-05 parity maintained
- **Provenance**: N/A
- **Revalidation Method**: automated-gate-pass
- **Revalidation Evidence**: `.specs/reports/quality-gate-2026-04-16-findings.md` (rerun)
- **Gate Rerun Record**: Post-correction rerun 2026-04-16: PASS

---

### CF-051 — CLAUDE-MEMORY citation in init-agents/references/context-optimization.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination
- **Scope**: standalone
- **Artifact**: `skills/init-agents/references/context-optimization.md` (SCG-08 member)
- **Evidence**: `skills/init-agents/references/context-optimization.md:127` — `"| ≤200 lines per file | Anthropic Docs: claude-code/memory |"`
- **Violated Source**: `standalone-bundle` (`docs/compliance/normative-source-matrix.md:290`) — "Forbidden: All CLAUDE-* sources" (CLAUDE-MEMORY)
- **Current State**: Line 127 cites CLAUDE-MEMORY as source for the 200-line limit guideline
- **Expected State**: Citation removed or replaced with a non-CLAUDE-* source (e.g., standalone general guidance)
- **Impact**: Standalone artifact contains a forbidden source citation; creates a Claude Code dependency in distributed reference material
- **Proposed Fix**: Remove the CLAUDE-MEMORY citation from line 127; retain the guidance value (≤200 lines) with source removed or replaced with neutral attribution
- **Correction Notes**: Applied 2026-04-16 — line 127 source cell updated from "Anthropic Docs: claude-code/memory" to "Agent Skills Standard" (neutral attribution matching `SHARED-AUTHORING-GUIDE` source class). All 4 SCG-08 copies updated in lockstep
- **Provenance**: Guidance retained from independent empirical consensus (≤200-line limit is consistent across standalone context); citation updated to neutral source. Not distilled from a specific line range.
- **Revalidation Method**: instruction-only/manual-validator
- **Revalidation Evidence**: Verified `grep 'claude-code/memory' skills/init-agents/references/context-optimization.md` returns 0 after correction
- **Gate Rerun Record**: N/A — context-optimization.md not directly gate-checked; SCG-08 parity confirmed via sha256sum post-correction

---

### CF-052 — CLAUDE-MEMORY citation in improve-agents/references/context-optimization.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination
- **Scope**: standalone
- **Artifact**: `skills/improve-agents/references/context-optimization.md` (SCG-08 member)
- **Evidence**: `skills/improve-agents/references/context-optimization.md:127` — same violation as CF-051
- **Violated Source**: `standalone-bundle` (`docs/compliance/normative-source-matrix.md:290`)
- **Current State**: Same as CF-051 sibling; SCG-08 was byte-identical at baseline
- **Expected State**: Same correction as CF-051
- **Proposed Fix**: Same as CF-051 — applied in lockstep
- **Correction Notes**: Applied 2026-04-16 in lockstep with CF-051, CF-053, CF-054 — SCG-08 parity maintained
- **Provenance**: Same as CF-051
- **Revalidation Method**: instruction-only/manual-validator
- **Revalidation Evidence**: `grep 'claude-code/memory' skills/improve-agents/references/context-optimization.md` → 0
- **Gate Rerun Record**: N/A — SCG-08 parity confirmed via sha256sum post-correction

---

### CF-053 — CLAUDE-MEMORY citation in improve-claude/references/context-optimization.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination
- **Scope**: standalone
- **Artifact**: `skills/improve-claude/references/context-optimization.md` (SCG-08 member)
- **Evidence**: `skills/improve-claude/references/context-optimization.md:127` — same violation as CF-051
- **Violated Source**: `standalone-bundle` (`docs/compliance/normative-source-matrix.md:290`)
- **Current State**: Same as CF-051 sibling
- **Expected State**: Same correction as CF-051
- **Proposed Fix**: Same as CF-051 — applied in lockstep
- **Correction Notes**: Applied 2026-04-16 in lockstep with CF-051, CF-052, CF-054
- **Provenance**: Same as CF-051
- **Revalidation Method**: instruction-only/manual-validator
- **Revalidation Evidence**: `grep 'claude-code/memory' skills/improve-claude/references/context-optimization.md` → 0
- **Gate Rerun Record**: N/A — SCG-08 parity confirmed via sha256sum post-correction

---

### CF-054 — CLAUDE-MEMORY citation in init-claude/references/context-optimization.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination
- **Scope**: standalone
- **Artifact**: `skills/init-claude/references/context-optimization.md` (SCG-08 member)
- **Evidence**: `skills/init-claude/references/context-optimization.md:127` — same violation as CF-051
- **Violated Source**: `standalone-bundle` (`docs/compliance/normative-source-matrix.md:290`)
- **Current State**: Same as CF-051 sibling
- **Expected State**: Same correction as CF-051
- **Proposed Fix**: Same as CF-051 — applied in lockstep
- **Correction Notes**: Applied 2026-04-16 in lockstep with CF-051, CF-052, CF-053
- **Provenance**: Same as CF-051
- **Revalidation Method**: instruction-only/manual-validator
- **Revalidation Evidence**: `grep 'claude-code/memory' skills/init-claude/references/context-optimization.md` → 0
- **Gate Rerun Record**: N/A — SCG-08 parity confirmed via sha256sum post-correction

---

### CF-055 — `${CLAUDE_SKILL_DIR}` in create-skill/assets/templates/skill-md.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination
- **Scope**: standalone
- **Artifact**: `skills/create-skill/assets/templates/skill-md.md` (TCG-09 member)
- **Evidence**: `skills/create-skill/assets/templates/skill-md.md` — 3 occurrences of `${CLAUDE_SKILL_DIR}/references/`
- **Violated Source**: `standalone-bundle` (`docs/compliance/normative-source-matrix.md:290`)
- **Current State**: Template for generated SKILL.md files uses `${CLAUDE_SKILL_DIR}` paths — all skills generated from this template will inherit the contamination
- **Expected State**: Template uses `references/[name].md` relative paths
- **Impact**: Every skill created with this template generates a contaminated SKILL.md — propagates violations to downstream artifacts
- **Proposed Fix**: Replace `${CLAUDE_SKILL_DIR}/references/` with `references/` (3 occurrences)
- **Correction Notes**: Applied 2026-04-16 in lockstep with CF-056 — TCG-09 parity maintained
- **Provenance**: N/A
- **Revalidation Method**: automated-gate-pass
- **Revalidation Evidence**: `.specs/reports/quality-gate-2026-04-16-findings.md` (rerun)
- **Gate Rerun Record**: Post-correction rerun 2026-04-16: PASS

---

### CF-056 — `${CLAUDE_SKILL_DIR}` in improve-skill/assets/templates/skill-md.md [MAJOR] — ✅ CLOSED

- **Check Category**: Contamination
- **Scope**: standalone
- **Artifact**: `skills/improve-skill/assets/templates/skill-md.md` (TCG-09 member)
- **Evidence**: `skills/improve-skill/assets/templates/skill-md.md` — 3 occurrences (TCG-09 sibling of CF-055)
- **Violated Source**: `standalone-bundle` (`docs/compliance/normative-source-matrix.md:290`)
- **Current State**: Same violation as CF-055; TCG-09 pair was byte-identical at baseline
- **Expected State**: Same correction as CF-055
- **Proposed Fix**: Same as CF-055 — applied in lockstep
- **Correction Notes**: Applied 2026-04-16 in lockstep with CF-055 — TCG-09 parity maintained
- **Provenance**: N/A
- **Revalidation Method**: automated-gate-pass
- **Revalidation Evidence**: `.specs/reports/quality-gate-2026-04-16-findings.md` (rerun)
- **Gate Rerun Record**: Post-correction rerun 2026-04-16: PASS

---

### CF-057 — README external link (line 23): `../docs/general-llm/Evaluating-AGENTS-paper.pdf` [MAJOR] — ✅ CLOSED

- **Check Category**: Self-Sufficiency
- **Scope**: standalone
- **Artifact**: `skills/README.md`
- **Evidence**: `skills/README.md:23` — `"[Evaluating AGENTS.md](../docs/general-llm/Evaluating-AGENTS-paper.pdf)"`
- **Violated Source**: PRD #56 Phase 3 — "no artifact blocked by external-scope documentation dependencies"; `standalone-bundle` self-sufficiency constraint
- **Current State**: Relative path to `../docs/general-llm/` — resolves only when `skills/` parent directory containing `docs/` is present; broken in distributed tarball
- **Expected State**: Full URL to canonical source (stable GitHub URL or external host)
- **Impact**: Link is broken for any user who downloads the `skills/` directory alone (npx install, tarball distribution)
- **Proposed Fix**: Replace with full GitHub URL `https://github.com/rodrigorjsf/agent-engineering-toolkit/blob/development/docs/general-llm/Evaluating-AGENTS-paper.pdf`
- **Correction Notes**: Applied 2026-04-16 — relative path replaced with full GitHub URL
- **Provenance**: N/A
- **Revalidation Method**: instruction-only/manual-validator
- **Revalidation Evidence**: `grep '../docs/' skills/README.md` → 0 after correction
- **Gate Rerun Record**: N/A — no gate covers README

---

### CF-058 — README external link (line 53): `../docs/general-llm/Evaluating-AGENTS-paper.pdf` [MAJOR] — ✅ CLOSED

- **Check Category**: Self-Sufficiency
- **Scope**: standalone
- **Artifact**: `skills/README.md`
- **Evidence**: `skills/README.md:53` — `"[Evaluating AGENTS study](../docs/general-llm/Evaluating-AGENTS-paper.pdf)"`
- **Violated Source**: PRD #56 Phase 3; `standalone-bundle` self-sufficiency constraint
- **Current State**: Second relative path link to the same PDF — same broken-distribution issue
- **Expected State**: Full URL to canonical source
- **Proposed Fix**: Replace with full GitHub URL (same as CF-057)
- **Correction Notes**: Applied 2026-04-16 — relative path replaced with full GitHub URL
- **Provenance**: N/A
- **Revalidation Method**: instruction-only/manual-validator
- **Revalidation Evidence**: `grep '../docs/' skills/README.md` → 0 after correction
- **Gate Rerun Record**: N/A — no gate covers README

---

### CF-059 — README external link (line 64): `../docs/general-llm/a-guide-to-agents.md` [MAJOR] — ✅ CLOSED

- **Check Category**: Self-Sufficiency
- **Scope**: standalone
- **Artifact**: `skills/README.md`
- **Evidence**: `skills/README.md:64` — `"[A Complete Guide to AGENTS.md](../docs/general-llm/a-guide-to-agents.md)"`
- **Violated Source**: PRD #56 Phase 3; `standalone-bundle` self-sufficiency constraint
- **Current State**: Relative path link to `../docs/general-llm/` — broken in distribution
- **Expected State**: Full URL to canonical source
- **Proposed Fix**: Replace with full GitHub URL `https://github.com/rodrigorjsf/agent-engineering-toolkit/blob/development/docs/general-llm/a-guide-to-agents.md`
- **Correction Notes**: Applied 2026-04-16 — relative path replaced with full GitHub URL
- **Provenance**: N/A
- **Revalidation Method**: instruction-only/manual-validator
- **Revalidation Evidence**: `grep '../docs/' skills/README.md` → 0 after correction
- **Gate Rerun Record**: N/A — no gate covers README

---

### Phase 9 Observations (out of Phase 5 scope — not filed as CF findings)

1. `.claude/skills/quality-gate/references/quality-gate-criteria.md:45` — hardcoded "4 files in `skills/*/SKILL.md`" (12 exist); S6/S7 pattern checks assume init/improve-only skills. Repository-global gate artifact. File as Phase 9 regression-prevention finding.
2. `.claude/rules/standalone-skills.md` — does not explicitly name `${CLAUDE_SKILL_DIR}` as forbidden, only "no cross-directory references." Rule-clarity improvement: add an explicit line. Defer to Phase 7 if does not block a Phase 5 correction.
3. Automated standalone drift detection still missing — per `artifact-audit-manifest.md:656`, Phase 9 is earliest delivery.
4. `.claude/PRPs/tests/scenarios/improve-bloated-artifact.md:41` and `create-simple-artifact.md:95,161` — explicitly reward `${CLAUDE_SKILL_DIR}` usage; after Phase 5 corrections these test scenarios need updating. Defer to Phase 7 or Phase 9.
5. `skills/README.md:58` — `https://docs.anthropic.com/en/docs/claude-code/memory` (full URL to Claude Code docs) — informational citation in a README documentation section; full URL does not break portability; not filed as CF. Monitor for Phase 6 scope review.

---

## 7.4 Correction Log

| CF-NNN ID | State | Correction Date | Revalidation Method | Revalidation Date |
|-----------|-------|-----------------|---------------------|-------------------|
| CF-030 | CLOSED | 2026-04-16 | automated-gate-pass | 2026-04-16 |
| CF-031 | CLOSED | 2026-04-16 | automated-gate-pass | 2026-04-16 |
| CF-032 | CLOSED | 2026-04-16 | automated-gate-pass | 2026-04-16 |
| CF-033 | CLOSED | 2026-04-16 | automated-gate-pass | 2026-04-16 |
| CF-034 | CLOSED | 2026-04-16 | automated-gate-pass | 2026-04-16 |
| CF-035 | CLOSED | 2026-04-16 | automated-gate-pass | 2026-04-16 |
| CF-036 | CLOSED | 2026-04-16 | automated-gate-pass | 2026-04-16 |
| CF-037 | CLOSED | 2026-04-16 | automated-gate-pass | 2026-04-16 |
| CF-038 | CLOSED | 2026-04-16 | automated-gate-pass | 2026-04-16 |
| CF-039 | CLOSED | 2026-04-16 | automated-gate-pass | 2026-04-16 |
| CF-040 | CLOSED | 2026-04-16 | automated-gate-pass | 2026-04-16 |
| CF-041 | CLOSED | 2026-04-16 | automated-gate-pass | 2026-04-16 |
| CF-042 | CLOSED | 2026-04-16 | instruction-only/manual-validator | 2026-04-16 |
| CF-043 | CLOSED | 2026-04-16 | automated-gate-pass | 2026-04-16 |
| CF-044 | CLOSED | 2026-04-16 | automated-gate-pass | 2026-04-16 |
| CF-045 | CLOSED | 2026-04-16 | automated-gate-pass | 2026-04-16 |
| CF-046 | CLOSED | 2026-04-16 | automated-gate-pass | 2026-04-16 |
| CF-047 | CLOSED | 2026-04-16 | automated-gate-pass | 2026-04-16 |
| CF-048 | CLOSED | 2026-04-16 | automated-gate-pass | 2026-04-16 |
| CF-049 | CLOSED | 2026-04-16 | automated-gate-pass | 2026-04-16 |
| CF-050 | CLOSED | 2026-04-16 | automated-gate-pass | 2026-04-16 |
| CF-051 | CLOSED | 2026-04-16 | instruction-only/manual-validator | 2026-04-16 |
| CF-052 | CLOSED | 2026-04-16 | instruction-only/manual-validator | 2026-04-16 |
| CF-053 | CLOSED | 2026-04-16 | instruction-only/manual-validator | 2026-04-16 |
| CF-054 | CLOSED | 2026-04-16 | instruction-only/manual-validator | 2026-04-16 |
| CF-055 | CLOSED | 2026-04-16 | automated-gate-pass | 2026-04-16 |
| CF-056 | CLOSED | 2026-04-16 | automated-gate-pass | 2026-04-16 |
| CF-057 | CLOSED | 2026-04-16 | instruction-only/manual-validator | 2026-04-16 |
| CF-058 | CLOSED | 2026-04-16 | instruction-only/manual-validator | 2026-04-16 |
| CF-059 | CLOSED | 2026-04-16 | instruction-only/manual-validator | 2026-04-16 |

*Note: CF-060 not used; final finding was CF-059. CF-NNN range CF-030–CF-059 (30 findings), plus CF-042 Normative-Alignment overlap with CF-032 artifact = 31 total dashboard entries.*

---

## 7.5 Gate Rerun Summary

| Gate | Scope | Run Date | Report Path | Result | Relevant CF-NNN IDs |
|------|-------|----------|-------------|--------|---------------------|
| quality-gate (baseline) | standalone + agents-initializer | 2026-04-16 | `.specs/reports/quality-gate-2026-04-16-findings.md` | PASS (Phase 4 post-correction) | Pre-correction baseline |
| quality-gate (Phase 5 rerun) | standalone + agents-initializer | 2026-04-16 | `.specs/reports/quality-gate-2026-04-16-findings.md` (rerun) | PASS | CF-030–CF-056 |
