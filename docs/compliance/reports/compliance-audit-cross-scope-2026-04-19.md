# Compliance Audit Report — Cross-Scope

**Scope ID**: cross-scope  
**Audit Date**: 2026-04-19  
**Auditor Phase**: 7 (Shared references, self-sufficiency, parity, and docs drift remediation)  
**Plan Reference**: `.claude/PRPs/plans/shared-references-self-sufficiency-parity-and-docs-drift-remediation.plan.md`  
**Parent PRD**: `.claude/PRPs/prds/repository-compliance-validation-and-correction.prd.md`  
**Source Issue**: Issue #68 — [Phase 7: Shared references, self-sufficiency, parity, and docs drift remediation](https://github.com/rodrigorjsf/agent-engineering-toolkit/issues/68)  
**Total Artifacts Audited**: ~180 (per `docs/compliance/artifact-audit-manifest.md:660-668`)  
**CF Range**: CF-071 onward

---

## 7.2 Dashboard

| Category | Total | CRITICAL | MAJOR | MINOR |
|----------|-------|----------|-------|-------|
| Contamination | 0 | 0 | 0 | 0 |
| Self-Sufficiency | 0 | 0 | 0 | 0 |
| Normative-Alignment | 3 | 0 | 3 | 0 |
| Parity | 1 | 0 | 1 | 0 |
| Drift | 0 | 0 | 0 | 0 |
| Provenance | 0 | 0 | 0 | 0 |
| **Total** | **4** | **0** | **4** | **0** |

Baseline inventory established 2026-04-19. Counts above reflect Phase 7 findings CF-071 through CF-074; all four are closed in the correction log below.

---

## 7.3 Findings

### Phase 7 Target Inventory (Tasks 1-2)

Phase 7 scope comes from the Shared Copy Group Registry and Quality Gate Coverage Map (`docs/compliance/artifact-audit-manifest.md:558-609,646-668`). All shared-copy rows below are registry-backed `Ph.7?=yes` scope. Repository-global follow-up surfaces come from deferred observations in the standalone Phase 5 report (`docs/compliance/reports/compliance-audit-standalone-2026-04-16.md:606-611`).

#### Shared Copy Groups

| Group | Type | Target | Scope Layer | Validator / Revalidation Path | Origin | Scope Evidence |
|-------|------|--------|-------------|-------------------------------|--------|----------------|
| SCG-01 | Reference | `context-optimization.md` | agents-initializer + cursor-initializer + standalone | quality-gate parity-checker (X1) + manual lockstep review | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:566` |
| SCG-02 | Reference | `validation-criteria.md` | agents-initializer + cursor-initializer + standalone | quality-gate parity-checker (X2) + manual lockstep review | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:567` |
| SCG-03 | Reference | `what-not-to-include.md` | agents-initializer + cursor-initializer + standalone | quality-gate parity-checker (X1) + manual lockstep review | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:568` |
| SCG-04 | Reference | `progressive-disclosure-guide.md` | agents-initializer + cursor-initializer + standalone | quality-gate parity-checker (X1) + manual lockstep review | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:569` |
| SCG-05 | Reference | `automation-migration-guide.md` | improve scopes across agents-initializer + cursor-initializer + standalone | quality-gate parity-checker (X1) + manual lockstep review | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:570` |
| SCG-06 | Reference | `evaluation-criteria.md` | improve scopes across agents-initializer + cursor-initializer + standalone | quality-gate parity-checker (X1) + manual lockstep review | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:571` |
| SCG-07 | Reference | `claude-rules-system.md` | Claude-only plugin + standalone | quality-gate parity-checker (X1) | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:572` |
| SCG-08 | Reference | `codebase-analyzer.md` | standalone only | quality-gate parity-checker (X1) | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:573` |
| SCG-09 | Reference | `file-evaluator.md` | standalone improve only | quality-gate parity-checker (X1) | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:574` |
| SCG-10 | Reference | `scope-detector.md` | standalone init only | quality-gate parity-checker (X1) | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:575` |
| SCG-11 | Reference | `prompt-engineering-strategies.md` | agent-customizer create/improve pairs | agent-customizer-quality-gate parity-checker (X1) | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:581` |
| SCG-12 | Reference | `skill-validation-criteria.md` | agent-customizer create/improve-skill | agent-customizer-quality-gate parity-checker (X2) | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:582` |
| SCG-13 | Reference | `hook-validation-criteria.md` | agent-customizer create/improve-hook | agent-customizer-quality-gate parity-checker (X3) | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:583` |
| SCG-14 | Reference | `rule-validation-criteria.md` | agent-customizer create/improve-rule | agent-customizer-quality-gate parity-checker (X4) | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:584` |
| SCG-15 | Reference | `subagent-validation-criteria.md` | agent-customizer create/improve-subagent | agent-customizer-quality-gate parity-checker (X5) | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:585` |
| SCG-16 | Reference | `skill-authoring-guide.md` | agent-customizer create/improve-skill | agent-customizer-quality-gate parity-checker (X6) | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:586` |
| SCG-17 | Reference | `hook-authoring-guide.md` | agent-customizer create/improve-hook | agent-customizer-quality-gate parity-checker (X7) | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:587` |
| SCG-18 | Reference | `rule-authoring-guide.md` | agent-customizer create/improve-rule | agent-customizer-quality-gate parity-checker (X8) | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:588` |
| SCG-19 | Reference | `subagent-authoring-guide.md` | agent-customizer create/improve-subagent | agent-customizer-quality-gate parity-checker (X9) | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:589` |
| SCG-20 | Reference | `skill-format-reference.md` | agent-customizer create/improve-skill | agent-customizer-quality-gate parity-checker (X10) | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:590` |
| SCG-21 | Reference | `hook-events-reference.md` | agent-customizer create/improve-hook | agent-customizer-quality-gate parity-checker (X11) | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:591` |
| SCG-22 | Reference | `subagent-config-reference.md` | agent-customizer create/improve-subagent | agent-customizer-quality-gate parity-checker (X12) | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:592` |
| SCG-23 | Template | `skill-md.md` | agent-customizer create/improve-skill | agent-customizer-quality-gate parity-checker (X13) + quality-gate T2 overlap via TCG-09 | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:593,608` |
| SCG-24 | Template | `subagent-definition.md` | agent-customizer create/improve-subagent | agent-customizer-quality-gate parity-checker (X14) + quality-gate T2 overlap via TCG-10 | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:594,609` |

#### Template Copy Groups

| Group | Type | Target | Scope Layer | Validator / Revalidation Path | Origin | Scope Evidence |
|-------|------|--------|-------------|-------------------------------|--------|----------------|
| TCG-01 | Template | `domain-doc.md` | agents-initializer + cursor-initializer + standalone | quality-gate parity-checker (T2) + manual member check | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:600` |
| TCG-02 | Template | `root-agents-md.md` | agents-initializer + cursor-initializer + standalone | quality-gate parity-checker (T2) + manual member check | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:601` |
| TCG-03 | Template | `scoped-agents-md.md` | agents-initializer + cursor-initializer + standalone | quality-gate parity-checker (T2) + manual member check | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:602` |
| TCG-04 | Template | `root-claude-md.md` | agents-initializer + standalone | quality-gate parity-checker (T2) | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:603` |
| TCG-05 | Template | `scoped-claude-md.md` | agents-initializer + standalone | quality-gate parity-checker (T2) | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:604` |
| TCG-06 | Template | `claude-rule.md` | agents-initializer + standalone | quality-gate parity-checker (T2) + manual registry/member reconciliation | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:605` |
| TCG-07 | Template | `hook-config.md` | agents-initializer + agent-customizer + cursor-initializer + standalone | quality-gate parity-checker (T2) + manual registry/member reconciliation | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:606` |
| TCG-08 | Template | `skill.md` | agents-initializer + cursor-initializer + standalone | quality-gate parity-checker (T2) + manual registry/member reconciliation | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:607` |
| TCG-09 | Template | `skill-md.md` | agent-customizer + standalone | quality-gate (T2) + agent-customizer-quality-gate (X13) | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:608` |
| TCG-10 | Template | `subagent-definition.md` | agent-customizer + standalone | quality-gate (T2) + agent-customizer-quality-gate (X14) | routine shared-copy reconciliation | `docs/compliance/artifact-audit-manifest.md:609` |

#### Repository-Global / Manual Follow-Up Targets

| Artifact | Why In Scope | Revalidation Path | Origin | Scope Evidence |
|----------|--------------|-------------------|--------|----------------|
| `.claude/skills/quality-gate/references/quality-gate-criteria.md` | Repository-global quality-gate guidance still listed as a Phase 5 follow-up and remains outside automated repository-global coverage | instruction-only/manual-validator | deferred from Phase 5 follow-up | `docs/compliance/reports/compliance-audit-standalone-2026-04-16.md:608`, `docs/compliance/artifact-audit-manifest.md:652-656` |
| `.claude/rules/standalone-skills.md` | Phase 5 deferred explicit standalone wording update for `${CLAUDE_SKILL_DIR}` / cross-directory references | instruction-only/manual-validator | deferred from Phase 5 follow-up | `docs/compliance/reports/compliance-audit-standalone-2026-04-16.md:609` |
| `.claude/PRPs/tests/scenarios/create-simple-artifact.md` | Shared scenario deferred after standalone path corrections because it still rewards stale path expectations | quality-gate red-green rerun + manual validator | deferred from Phase 5 follow-up | `docs/compliance/reports/compliance-audit-standalone-2026-04-16.md:611` |
| `.claude/PRPs/tests/scenarios/improve-bloated-artifact.md` | Shared scenario deferred after standalone path corrections because it still rewards stale path expectations | quality-gate red-green rerun + manual validator | deferred from Phase 5 follow-up | `docs/compliance/reports/compliance-audit-standalone-2026-04-16.md:611` |
| repository-global + cursor-initializer manual surfaces | Coverage map still marks both scopes manual-only outside automated gate coverage | manual-auditor-rerun | routine manual-only coverage gap handling | `docs/compliance/artifact-audit-manifest.md:652-656` |

### CF-071 — SCG-01 through SCG-06 registry groups collapse platform-specific reference variants [MAJOR]

- **Check Category**: Normative-Alignment
- **Scope**: cross-scope
- **Artifact**: `docs/compliance/artifact-audit-manifest.md`
- **Evidence**: `docs/compliance/artifact-audit-manifest.md:560-571` — "identify which files must be byte-identical"; `plugins/agents-initializer/skills/init-agents/references/context-optimization.md:24,28` — `"CLAUDE.md file"` / `"Bloated CLAUDE.md files"`; `plugins/cursor-initializer/skills/init-cursor/references/context-optimization.md:24,28` — `"configuration files in this toolkit"` / `"Anthropic's warning generalizes here"`; `plugins/agents-initializer/skills/init-agents/references/validation-criteria.md:3-4,14-26` — `"AGENTS.md / CLAUDE.md files"`; `plugins/cursor-initializer/skills/init-cursor/references/validation-criteria.md:3-4,14-30` — `"AGENTS.md / \`.cursor/rules/\` files"`
- **Violated Source**: `docs/compliance/normative-source-matrix.md:223-238` — platform boundaries require `${CLAUDE_SKILL_DIR}/references/...` for Claude-targeted plugin skills, relative `references/...` for Cursor/standalone, and different rule/artifact targets per platform
- **Current State**: Fresh 2026-04-19 md5 sweeps show SCG-01 has three stable hash families (plugin `f17fdcdb`, cursor `2c1783f7`, standalone `0a3f7030`); SCG-02..SCG-06 also split by cursor vs non-cursor content even though the registry records each as one byte-identical group.
- **Expected State**: Phase 7 registry rows should describe parity families that respect platform-specific content boundaries instead of treating all plugin/cursor/standalone copies as one byte-identical unit.
- **Impact**: Auditors cannot distinguish intended platform adaptation from true drift, and quality-gate evidence cannot be mapped cleanly back to the registry.
- **Proposed Fix**: Rewrite SCG-01..SCG-06 registry expectations to reflect platform-specific parity families and align the listed enforcers with those families.
- **Correction Notes**: `docs/compliance/artifact-audit-manifest.md:566-571` now splits SCG-01..SCG-06 into intended family A/B groupings and records singleton manual validation where Cursor intentionally stands alone.
- **Revalidation Method**: manual-auditor-rerun against the corrected registry + shared parity coverage reread
- **Revalidation Evidence**: `docs/compliance/artifact-audit-manifest.md:566-571`; `.claude/skills/quality-gate/references/quality-gate-criteria.md:75-82`

---

### CF-072 — TCG-02, TCG-03, TCG-06, TCG-07, TCG-08, and TCG-09 registry groups collapse platform or lifecycle variants [MAJOR]

- **Check Category**: Normative-Alignment
- **Scope**: cross-scope
- **Artifact**: `docs/compliance/artifact-audit-manifest.md`
- **Evidence**: `docs/compliance/artifact-audit-manifest.md:601-608` — TCG rows listed as single parity groups; `plugins/agents-initializer/skills/init-agents/assets/templates/root-agents-md.md:20-25` adds `Config` and `Prerequisite` blocks that are absent from `plugins/cursor-initializer/skills/init-cursor/assets/templates/root-agents-md.md:20-25`; `plugins/agents-initializer/skills/init-claude/assets/templates/claude-rule.md:16-20` omits migration instructions present in `plugins/agents-initializer/skills/improve-claude/assets/templates/claude-rule.md:16-25`; `plugins/agent-customizer/skills/create-skill/assets/templates/skill-md.md:10-11,38` uses `${CLAUDE_SKILL_DIR}` while `skills/create-skill/assets/templates/skill-md.md:10-11,38` uses relative bundled-file paths
- **Violated Source**: `docs/compliance/normative-source-matrix.md:223-238,244-249` — platform and init/improve lifecycle boundaries intentionally change bundled-file references, rule formats, and migration-template behavior
- **Current State**: Fresh 2026-04-19 md5 sweeps show TCG-02 has two hash families, TCG-03 two, TCG-06 two, TCG-07 three, TCG-08 two, and TCG-09 two, while the registry currently models each as a single template parity group.
- **Expected State**: Template parity groups should only bundle files that are actually intended to remain byte-identical within the same platform/lifecycle family.
- **Impact**: Phase 7 template parity findings are ambiguous: the registry currently treats valid Cursor or improve-template differences as if they were shared-copy drift.
- **Proposed Fix**: Split or relabel TCG-02/03/06/07/08/09 so platform-specific and lifecycle-specific template families are tracked separately from truly byte-identical copies.
- **Correction Notes**: `docs/compliance/artifact-audit-manifest.md:600-609` now models TCG-02..TCG-10 as family-specific groups instead of single cross-platform buckets.
- **Revalidation Method**: manual-auditor-rerun + targeted md5 reruns on corrected template families
- **Revalidation Evidence**: `docs/compliance/artifact-audit-manifest.md:600-609`; fresh 2026-04-19 md5 reruns recorded one hash across all four `hook-config.md` copies (`e76f7ba9f7b0be9c989261d38c840d78`), one hash across all four `subagent-definition.md` copies (`4f2b662ce05b50d369fd5011dc5d1461`), and the intended two-family split for `skill-md.md` (plugin pair `a8ac9464edfb6a1928c3a2b0e7fad84c`, standalone pair `6a77fe2fd7e6a9e1f58513f410d10c9a`)

---

### CF-073 — quality-gate parity-checker omits manifest-declared TCG-05 through TCG-10 coverage [MAJOR]

- **Check Category**: Parity
- **Scope**: cross-scope
- **Artifact**: `.claude/skills/quality-gate/agents/parity-checker.md`
- **Evidence**: `.claude/skills/quality-gate/agents/parity-checker.md:102-136` lists template md5 checks only for `root-agents-md.md`, `scoped-agents-md.md`, `root-claude-md.md`, `domain-doc.md`, and `cursor-rule.mdc`; `docs/compliance/artifact-audit-manifest.md:604-609` declares TCG-05 through TCG-10 as quality-gate-covered template groups; fresh 2026-04-19 `rg` against the parity-checker returned no `scoped-claude-md.md`, `claude-rule.md`, `hook-config.md`, `skill.md`, or `subagent-definition.md` entries
- **Violated Source**: `docs/compliance/artifact-audit-manifest.md:604-609` — each listed TCG row names `quality-gate parity-checker (T2)` or `quality-gate (T2)` as an enforcer
- **Current State**: The quality-gate parity-checker has no explicit md5 commands for manifest-declared groups TCG-05..TCG-10. Fresh md5 runs show TCG-05 and TCG-10 currently hash clean, while TCG-06..TCG-09 have multi-family hashes that the checker does not model at all.
- **Expected State**: After registry correction, the quality-gate parity-checker should include explicit commands for every quality-gate-managed template parity family.
- **Impact**: A PASS from the shared quality gate cannot prove template parity for half of the manifest-declared Phase 7 template scope, and drift in those families can go undetected.
- **Proposed Fix**: Update the parity-checker command matrix after registry reconciliation so every quality-gate-managed template family is checked explicitly.
- **Correction Notes**: `.claude/skills/quality-gate/agents/parity-checker.md:124-171` now includes explicit md5 coverage for `scoped-claude-md.md`, both `claude-rule.md` families, both `hook-config.md` families, the non-Cursor `skill.md` family, and the standalone `skill-md.md` / `subagent-definition.md` families.
- **Revalidation Method**: shared `quality-gate` rerun
- **Revalidation Evidence**: `.claude/skills/quality-gate/agents/parity-checker.md:124-171`; shared `quality-gate` rerun on 2026-04-19 recorded `411/411` static compliance, `30/30` parity groups MATCH, `4/4` scenario passes, overall `445/445 PASS`

---

### CF-074 — quality-gate criteria still describe template identity too broadly for current platform/lifecycle families [MAJOR]

- **Check Category**: Normative-Alignment
- **Scope**: repository-global
- **Artifact**: `.claude/skills/quality-gate/references/quality-gate-criteria.md`
- **Evidence**: `.claude/skills/quality-gate/references/quality-gate-criteria.md:74-82` — `"Templates identical across plugin and standalone"` and `"Shared template files byte-identical across distributions"`; representative template variants differ at `plugins/agents-initializer/skills/init-agents/assets/templates/root-agents-md.md:20-25` vs `plugins/cursor-initializer/skills/init-cursor/assets/templates/root-agents-md.md:20-25`, `plugins/agents-initializer/skills/init-claude/assets/templates/claude-rule.md:16-20` vs `plugins/agents-initializer/skills/improve-claude/assets/templates/claude-rule.md:16-25`, and `plugins/agent-customizer/skills/create-skill/assets/templates/skill-md.md:10-11,38` vs `skills/create-skill/assets/templates/skill-md.md:10-11,38`
- **Violated Source**: `docs/compliance/normative-source-matrix.md:223-249` — platform targets and init/improve lifecycle rules intentionally permit different template content families
- **Current State**: The shared quality-gate criteria still describe template identity at a broader level than the current platform/lifecycle template families support.
- **Expected State**: Gate criteria should describe parity within intended copy families, not across Cursor/plugin/standalone or init/improve variants that the normative matrix deliberately differentiates.
- **Impact**: Future audits, parity-checker updates, and scenario expectations can be driven by an overstated parity rule and reintroduce false positives.
- **Proposed Fix**: Reword the quality-gate criteria to target intended copy families and update examples to match the corrected Phase 7 registry model.
- **Correction Notes**: `.claude/skills/quality-gate/references/quality-gate-criteria.md:74-82` now scopes T2/X1/X2 to "intended multi-copy family" wording instead of cross-distribution identity language, and `.claude/rules/standalone-skills.md:10-19` keeps standalone bundled-file path boundaries explicit.
- **Revalidation Method**: instruction-only/manual-validator reread + shared gate criteria reread
- **Revalidation Evidence**: `.claude/skills/quality-gate/references/quality-gate-criteria.md:74-82`; `.claude/rules/standalone-skills.md:10-19`

---

## 7.4 Correction Log

| CF-NNN ID | State | Correction Date | Revalidation Method | Revalidation Date |
|-----------|-------|-----------------|---------------------|-------------------|
| CF-071 | CLOSED | 2026-04-19 | manual-auditor-rerun + parity criteria reread | 2026-04-19 |
| CF-072 | CLOSED | 2026-04-19 | manual-auditor-rerun + targeted md5 reruns | 2026-04-19 |
| CF-073 | CLOSED | 2026-04-19 | shared `quality-gate` rerun | 2026-04-19 |
| CF-074 | CLOSED | 2026-04-19 | instruction-only/manual-validator reread | 2026-04-19 |

---

## 7.5 Gate Rerun Summary

| Gate | Scope | Run Date | Report Path | Result | Relevant CF-NNN IDs |
|------|-------|----------|-------------|--------|---------------------|
| `quality-gate` | Shared references, templates, and shared scenario surfaces | 2026-04-19 | — | PASS — `411/411` static, `30/30` parity, `4/4` scenarios, overall `445/445` | CF-071, CF-072, CF-073, CF-074 |
| `agent-customizer-quality-gate` | agent-customizer parity + docs drift + scenario-sensitive follow-up | 2026-04-19 | automated rerun blocked by provider `429` rate limits | Manual revalidation PASS — `14/14` parity groups MATCH; drift manifest `34` rows / `74` cited source paths / `0` missing paths; no nested reference imports; corrected create-hook/create-skill/create-subagent surfaces recorded in plugin SKILL/template files | CF-072 |

Automated `agent-customizer-quality-gate` sub-agent reruns were attempted repeatedly on 2026-04-19 but returned provider `429` rate limits. Phase 7 closeout therefore records the manual validator evidence that remained available in-repo: fresh parity hashes, manifest path existence, zero nested reference-import matches, unchanged source-doc set for the touched drift-managed references, and the scenario-sensitive SKILL/template corrections at `plugins/agent-customizer/skills/create-hook/SKILL.md:57-65`, `plugins/agent-customizer/skills/create-hook/assets/templates/hook-config.md:24-40`, `plugins/agent-customizer/skills/create-skill/SKILL.md:55-75`, `plugins/agent-customizer/skills/create-skill/assets/templates/skill-md.md:5-39`, `plugins/agent-customizer/skills/create-subagent/SKILL.md:62-86`, and `plugins/agent-customizer/skills/create-subagent/assets/templates/subagent-definition.md:8-20`.
