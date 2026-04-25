---
title: Research Doc — HumanLayer Reframe (Sub-project A)
date: 2026-04-25
status: design-approved
target_file: dev/research/2026-04-25-harness-engineering-research.md
related_subproject: B (local knowledge-stack tool — separate spec)
---

# Research Doc — HumanLayer Reframe (Sub-project A)

## Goal

Make `dev/research/2026-04-25-harness-engineering-research.md` portable. The doc must be usable as a reference in any project with no dependency on the locally-vendored `humanlayer/` directory. HumanLayer survives in the doc only as a named case-study evidencing concepts from `ai/docs/`. No file:line citations, no path references, repo URL allowed once.

This refactor is the first half of a two-step program. Sub-project B (separate spec) will package `ai/docs/` + `graphify-out/` + `graphify-out/wiki/` into a portable knowledge-stack tool. The reframed research doc becomes one of the canonical reference artifacts that tool serves.

## Scope

### In scope

- The single file `dev/research/2026-04-25-harness-engineering-research.md`.
- All HumanLayer-related content within it, in every form (paths, file:line cites, narrative references, frontmatter, related-research items, open-questions items, architecture-insights evidence).

### Out of scope

- The `humanlayer/` vendored directory itself — submodule/vendor decision unchanged this session.
- Markdown lint warnings (MD032/MD060) — pre-existing, not introduced.
- Sub-project B (local knowledge-stack tool).
- Any other research file.

## Change Inventory

| # | Location | Current | New |
|---|----------|---------|-----|
| 1 | Frontmatter `sources:` | lists `humanlayer/` path | `https://github.com/humanlayer/humanlayer` |
| 2 | Frontmatter `tags:` | includes `humanlayer` | unchanged (signals studied case) |
| 3 | "HumanLayer Codebase Findings" section (~200 lines) | architecture-of-humanlayer narrative with file:line citations | rewritten as `Case Study: HumanLayer (concept→pattern mapping)`; full-preserve depth (table + patterns confirmed + patterns absent + surprises); concept-first wording; zero paths |
| 4 | Code References → "HumanLayer Codebase — Concrete Instantiation" subsection (~30 file:line cites) | full subsection with paths | **deleted entirely**. Optionally replaced by a single pointer line "see Case Study section" |
| 5 | Architecture Insights → Insight #9 (heavy-stack vs lean-shell) | uses HumanLayer evidence | reframed as a pure concept tension on the ai/docs spine. Optional one cross-link "(see Case Study)" |
| 6 | Related Research humanlayer-comparison items | humanlayer-anchored items | converted to concept-level items |
| 7 | Open Questions Q5 (lean-shell vs heavy-stack viability) | concept question already, light humanlayer phrasing | rephrased to drop any HumanLayer-specific phrasing |
| 8 | Appendix block A20 "HumanLayer Architecture" (graphify queries) | uses HumanLayer Architecture community label | **kept as-is** — references graphify community structure, not file:line |
| 9 | Any remaining `humanlayer/` path strings outside the above | scattered occurrences | grep-strip; replace with concept names or "(see Case Study)" |

## New Section Spec — `Case Study: HumanLayer`

### Location

Same location in the doc as the current "HumanLayer Codebase Findings" section: immediately after the Knowledge Graph Structure block.

### Header

```
## Case Study: HumanLayer — Concepts from ai/docs Applied in Practice
```

### Lead paragraph (~5 lines)

- One sentence on what HumanLayer is.
- One sentence on why it was studied: a concrete instance of `ai/docs/` harness concepts in production code.
- Repo URL once: `https://github.com/humanlayer/humanlayer`.
- One-sentence disclaimer: case-study only, no path citations, snapshots a moment in time, may drift.

### Block 2.1 — Concept→Pattern Mapping Table

Spine of the section. 8–12 rows. Schema:

| ai/docs concept | What HumanLayer applies it to | Observed pattern |
|---|---|---|
| Always-loaded memory (CLAUDE.md) | Project-wide rules and protocol enforcement | Single root CLAUDE.md, no path-scoped variants |
| Subagents as context firewall | Dispatching parallel research tasks | Subagent results return as compressed summaries to main thread |
| Approval-loop / human-in-the-loop | Tool-call gating before destructive ops | MCP-mediated approval channel |
| Plugin-as-orchestrator | Bundling agents and commands as one unit | `.claude/` directory packages the workflow |
| Long-running maintenance | Recurring repo hygiene tasks | Slash-command driven, manual trigger |
| Verification gates | Pre-completion checks | Inline command checklists, no formal hook |
| Progressive disclosure | Skill content unloaded until needed | Commands list → command body → tools |
| Smart-zone / context-rot mitigation | Keeping working set lean | Heavy reliance on commands and subagents to scope context |

The exact rows may grow to 12 if the existing findings surface additional first-class concept mappings (e.g., agent-communication-protocols, structured-outputs).

### Block 2.2 — Patterns Confirmed (~40 lines)

One short paragraph per major theme. Each paragraph follows the structure: `ai/docs/` concept name → what HumanLayer does with it → why this pattern matters for an `ai/docs/` reader. Candidate themes for 2.2 (those HumanLayer affirms): memory, subagents, approval-loop / human-in-the-loop, plugin packaging, long-running maintenance. Themes where HumanLayer lacks the artifact (skills, hooks, AGENTS.md, path-scoped CLAUDE.md, Ralph sentinels) belong in Block 2.3, not here.

### Block 2.3 — Patterns Absent (~30 lines)

Honest divergence. HumanLayer has no hooks, no skills, no AGENTS.md, no Ralph sentinels, no path-scoped CLAUDE.md. Lesson for the reader: the `ai/docs/` concept catalog can manifest in spirit without literal artifacts. Not every harness needs every artifact. This block exists precisely to teach by negative example — high signal for portable doc.

### Block 2.4 — Notable Surprises (~15 lines)

Two or three observations that the `ai/docs/` spine alone would not predict. Examples (final pick made during edit): the way HumanLayer leans on slash commands as a substitute for hooks; the absence of progressive-disclosure skills despite heavy command usage; the implicit verification pattern via inline checklists.

### Block 2.5 — Further Reading (~10 lines)

Pointers back into `ai/docs/` themes most relevant to the case-study findings. One pointer to graphify community label `HumanLayer Architecture` for readers who want a graph view.

### Total target

~150–180 lines.

### Hard rules for the section

- Zero `humanlayer/...` path strings.
- Zero file:line citations.
- Repo URL appears exactly once (lead paragraph).
- All concept names match labels used elsewhere in the doc and graphify nodes (consistency).
- **Every entry in Blocks 2.2, 2.3, and 2.4 must explicitly name at least one `ai/docs/` concept** (as confirmation, absence, or extension). No standalone HumanLayer trivia. This rule enforces the user's "only ai/docs-related" requirement and prevents the section from drifting back into a HumanLayer architecture note that happens to lack paths.
- A theme appears in Block 2.2 (Patterns Confirmed) **or** Block 2.3 (Patterns Absent), never both. If HumanLayer lacks a given `ai/docs/` artifact, the theme belongs in 2.3 only.

## Execution Plan

Edit sequence, top-down through the doc:

1. Frontmatter: swap `sources:` line value (humanlayer path → github URL). Tags unchanged.
2. Replace existing "HumanLayer Codebase Findings" section with the new `Case Study: HumanLayer` per the spec above. Single Edit (large block) preferred; Write only if a clean Edit boundary cannot be established.
3. Code References: delete the entire "HumanLayer Codebase — Concrete Instantiation" subsection.
4. Architecture Insights #9: reword to a concept tension on the `ai/docs/` spine. Optional single cross-link "(see Case Study)" — decide during edit.
5. Related Research: replace humanlayer-comparison items with concept-only items.
6. Open Questions Q5: rephrase concept-level.
7. Final grep sweep for stragglers (`humanlayer/`, `humanlayer.*:[0-9]`).

## Verification

Mandatory before claiming done:

```bash
# 1. Zero humanlayer paths in doc (excluding the single allowed repo URL)
grep -n 'humanlayer/' dev/research/2026-04-25-harness-engineering-research.md \
  | grep -v 'github.com/humanlayer/humanlayer'
# Expect: zero output

# 2. Zero file:line citations against humanlayer
grep -nE 'humanlayer.*:[0-9]+' dev/research/2026-04-25-harness-engineering-research.md
# Expect: zero output

# 3. Repo URL appears exactly once
grep -cE 'github\.com/humanlayer/humanlayer' dev/research/2026-04-25-harness-engineering-research.md
# Expect: 1

# 4. Appendix queries still validate against graph.json
jq -r '.nodes[].label' graphify-out/graph.json | sort -u > /tmp/labels.txt
grep -E "^/graphify (path|explain)" dev/research/2026-04-25-harness-engineering-research.md \
  | grep -oE '"[^"]+"' | sort -u > /tmp/used.txt
comm -23 /tmp/used.txt <(sed 's/.*/"&"/' /tmp/labels.txt | sort -u)
# Expect: only "Node A" / "Node B" / "Node Name" placeholders remain

# 5. Line-count regression check
wc -l dev/research/2026-04-25-harness-engineering-research.md
# Expect: net reduction from 1567. Estimated ~1480-1530 (section reword: -20 to -50; subsection delete: ~-17; insight #9 reword: ~-5 to -10).
```

## Risk and Rollback

- All edits are confined to one git-tracked file. `git checkout dev/research/2026-04-25-harness-engineering-research.md` reverts cleanly.
- Risk: accidental deletion of non-HumanLayer content during a large block replace. Mitigation: read-before-write; prefer Edit over Write.
- Risk: appendix targets accidentally invalidated by section deletion. Mitigation: appendix block A20 unchanged; verification step 4 catches any drift.

## Success Criteria

- All five verification commands pass.
- The reworked section reads as a self-contained case study, intelligible to a reader who has never seen the `humanlayer/` codebase.
- A reader of the doc can locate the HumanLayer evidence in exactly one place.
- The doc remains usable as a reference in any project that has only `ai/docs/` and `graphify-out/` available locally — no `humanlayer/` checkout required.
