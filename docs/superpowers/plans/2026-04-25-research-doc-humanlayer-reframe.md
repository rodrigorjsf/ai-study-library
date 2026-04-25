# Research Doc — HumanLayer Reframe Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reframe `dev/research/2026-04-25-harness-engineering-research.md` so it contains zero HumanLayer paths/file:line citations and presents HumanLayer only as a case-study evidencing concepts from `ai/docs/`. The doc must be portable to any project that has only `ai/docs/` and `graphify-out/` available.

**Architecture:** Single-file rewrite. Replace one section, delete one subsection, reword four spots, validate via five grep commands. Work occurs in a dedicated git worktree branched from `main`. Final commit bundles all research-file edits.

**Tech Stack:** Markdown only. Grep, jq, git for verification. No build, no test framework.

**Companion spec:** `docs/superpowers/specs/2026-04-25-research-doc-humanlayer-reframe-design.md`. Consult for full case-study section content rules. Plan tasks reference spec section IDs explicitly.

---

## Pre-flight

### Pre-flight Task A: Commit planning artifacts to main

**Files:**
- `docs/superpowers/specs/2026-04-25-research-doc-humanlayer-reframe-design.md` (already on disk, untracked)
- `docs/superpowers/plans/2026-04-25-research-doc-humanlayer-reframe.md` (this file, untracked)

- [ ] **Step 1: Stage the spec and plan files**

```bash
cd /home/rodrigo/Workspace/ai-study-library
rtk git add docs/superpowers/specs/2026-04-25-research-doc-humanlayer-reframe-design.md \
         docs/superpowers/plans/2026-04-25-research-doc-humanlayer-reframe.md
```

- [ ] **Step 2: Commit on main**

```bash
rtk git commit -m "$(cat <<'EOF'
docs: add spec and plan for research-doc HumanLayer reframe

Sub-project A of the harness-engineering knowledge stack effort.
Spec defines the rewrite of dev/research/2026-04-25-harness-engineering-research.md
to remove HumanLayer paths/file:line citations and reframe HumanLayer
as a case study of ai/docs concepts. Plan implements the rewrite
in a dedicated worktree.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Expected: one commit added on `main`.

- [ ] **Step 3: Verify commit**

```bash
rtk git log -1 --stat
```

Expected output contains both new files.

### Pre-flight Task B: Create worktree

- [ ] **Step 1: Invoke worktree skill**

Use the `superpowers:using-git-worktrees` skill with parameters:
- worktree path: `dev/wt-research-reframe`
- branch name: `research-doc-humanlayer-reframe`
- base branch: `main`

If the skill is unavailable in this session, run manually:

```bash
cd /home/rodrigo/Workspace/ai-study-library
git worktree add -b research-doc-humanlayer-reframe ./dev/wt-research-reframe main
```

- [ ] **Step 2: Switch working directory to worktree for the rest of the plan**

All subsequent task commands assume `cwd = /home/rodrigo/Workspace/ai-study-library/dev/wt-research-reframe/`.

```bash
cd /home/rodrigo/Workspace/ai-study-library/dev/wt-research-reframe
pwd
```

Expected: `/home/rodrigo/Workspace/ai-study-library/dev/wt-research-reframe`

- [ ] **Step 3: Verify research file exists in worktree**

```bash
ls dev/research/2026-04-25-harness-engineering-research.md
wc -l dev/research/2026-04-25-harness-engineering-research.md
```

Expected: file exists, ~1567 lines.

---

## Task 1: Frontmatter `sources:` Swap

**Goal:** Replace the local `humanlayer/` path in the frontmatter `sources:` line with the canonical GitHub URL. `tags:` stays unchanged.

**Files:**
- Modify: `dev/research/2026-04-25-harness-engineering-research.md` (frontmatter, lines 1-20)

- [ ] **Step 1: Read the frontmatter to capture the exact `sources:` line**

```bash
sed -n '1,30p' dev/research/2026-04-25-harness-engineering-research.md
```

Expected: YAML frontmatter listing `sources:` with one entry per source. The HumanLayer entry will look like `humanlayer/` or similar — record the exact string for the next step.

- [ ] **Step 2: Apply the edit**

Use the Edit tool with:
- `old_string`: the exact line containing the `humanlayer/` path entry from the `sources:` block
- `new_string`: the same line with `humanlayer/` replaced by `https://github.com/humanlayer/humanlayer`

If the existing entry is `  - humanlayer/`, the replacement is `  - https://github.com/humanlayer/humanlayer`.

- [ ] **Step 3: Verify**

```bash
sed -n '1,30p' dev/research/2026-04-25-harness-engineering-research.md | grep -E 'humanlayer'
```

Expected: exactly one line, containing `https://github.com/humanlayer/humanlayer`. No bare `humanlayer/` path string in the frontmatter.

---

## Task 2: Replace Findings Section with Case Study

**Goal:** Replace the existing "HumanLayer Codebase Findings" section (~200 lines, immediately after the Knowledge Graph Structure block) with a new `Case Study: HumanLayer — Concepts from ai/docs Applied in Practice` section. Full-preserve depth: lead + table + Block 2.2 (Patterns Confirmed) + Block 2.3 (Patterns Absent) + Block 2.4 (Notable Surprises) + Block 2.5 (Further Reading). Zero file:line citations. Repo URL appears exactly once (lead paragraph).

**Files:**
- Modify: `dev/research/2026-04-25-harness-engineering-research.md`

**Spec reference:** `docs/superpowers/specs/2026-04-25-research-doc-humanlayer-reframe-design.md` — section "New Section Spec — `Case Study: HumanLayer`". All hard rules in that section apply.

- [ ] **Step 1: Locate section boundaries**

```bash
grep -n '^## ' dev/research/2026-04-25-harness-engineering-research.md
```

Expected: list of all H2 headings. Identify the start line of "HumanLayer Codebase Findings" (or whatever the existing heading is, possibly "## HumanLayer Codebase Findings") and the start line of the next H2 after it. Those two line numbers bracket the section to replace.

- [ ] **Step 2: Read the section in full to confirm boundaries**

```bash
sed -n '<start>,<end-1>p' dev/research/2026-04-25-harness-engineering-research.md
```

Substitute `<start>` and `<end-1>` from Step 1. Confirm the full section (and only that section) is captured.

- [ ] **Step 3a: Read spec Blocks 2.2–2.5 (no edit)**

```bash
sed -n '/^### Block 2.2/,/^## /p' \
  /home/rodrigo/Workspace/ai-study-library/docs/superpowers/specs/2026-04-25-research-doc-humanlayer-reframe-design.md
```

Read carefully. The block specs define candidate themes, target line counts, paragraph structure, and hard rules. The executor is not required to re-read the spec during composition — Steps 3b–3e repeat all relevant constraints inline.

- [ ] **Step 3b: Compose Block 2.2 (Patterns Confirmed) prose**

Constraints:
- Target: ~40 lines.
- One short paragraph per affirmed theme. Pick from this candidate set: memory, subagents, approval-loop / human-in-the-loop, plugin packaging, long-running maintenance.
- Each paragraph structure: `ai/docs/` concept name → what HumanLayer does with it → why this pattern matters for an `ai/docs/` reader.
- Every paragraph must explicitly name at least one `ai/docs/` concept.
- Zero path strings. Zero file:line citations.
- A theme HumanLayer lacks belongs in Block 2.3, not here.

Deliverable: `block_2_2.md` (in-memory only — held for Step 3f assembly). Final markdown subsection begins with `### Patterns Confirmed`.

- [ ] **Step 3c: Compose Block 2.3 (Patterns Absent) prose**

Constraints:
- Target: ~30 lines.
- One short paragraph per absent artifact. Candidates: hooks, skills, AGENTS.md, path-scoped CLAUDE.md, Ralph sentinels.
- Each paragraph structure: `ai/docs/` concept name → why HumanLayer succeeds without the literal artifact → lesson for the reader.
- Every paragraph must explicitly name the `ai/docs/` concept that is absent.
- Zero path strings. Zero file:line citations.
- A theme already used in Block 2.2 must NOT also appear here.

Deliverable: `block_2_3.md` (in-memory). Final markdown subsection begins with `### Patterns Absent`.

- [ ] **Step 3d: Compose Block 2.4 (Notable Surprises) prose**

Constraints:
- Target: ~15 lines.
- Two or three observations that the `ai/docs/` spine alone would not predict.
- Each surprise must explicitly name the `ai/docs/` concept it extends or refines.
- Zero path strings. Zero file:line citations.

Deliverable: `block_2_4.md` (in-memory). Final markdown subsection begins with `### Notable Surprises`.

- [ ] **Step 3e: Compose Block 2.5 (Further Reading) prose**

Constraints:
- Target: ~10 lines.
- Pointers back into `ai/docs/` themes most relevant to the case-study findings.
- Include one pointer to the graphify community label `HumanLayer Architecture`.
- Zero path strings into `humanlayer/`. Zero file:line citations.

Deliverable: `block_2_5.md` (in-memory). Final markdown subsection begins with `### Further Reading`.

- [ ] **Step 3f: Assemble final new_string**

Concatenate, in this exact order:

1. The literal lead block:

```markdown
## Case Study: HumanLayer — Concepts from ai/docs Applied in Practice

HumanLayer is an open-source agent-tooling project. Studied here as a concrete instance of `ai/docs/` harness concepts running in production code. Repository: <https://github.com/humanlayer/humanlayer>. Treat this section as a snapshot — case-study only, zero path citations, may drift as upstream evolves.

### Concept→Pattern Mapping

| ai/docs concept | What HumanLayer applies it to | Observed pattern |
|---|---|---|
| Always-loaded memory (CLAUDE.md) | Project-wide rules and protocol enforcement | Single root CLAUDE.md, no path-scoped variants |
| Subagents as context firewall | Dispatching parallel research tasks | Subagent results return as compressed summaries to the main thread |
| Approval-loop / human-in-the-loop | Tool-call gating before destructive ops | MCP-mediated approval channel |
| Plugin-as-orchestrator | Bundling agents and commands as one unit | `.claude/` directory packages the workflow |
| Long-running maintenance | Recurring repo hygiene tasks | Slash-command driven, manual trigger |
| Verification gates | Pre-completion checks | Inline command checklists, no formal hook |
| Progressive disclosure | Skill content unloaded until needed | Commands list → command body → tools |
| Smart-zone / context-rot mitigation | Keeping working set lean | Heavy reliance on commands and subagents to scope context |
```

2. `block_2_2.md` from Step 3b
3. `block_2_3.md` from Step 3c
4. `block_2_4.md` from Step 3d
5. `block_2_5.md` from Step 3e

The result is the final `new_string`. No `[Compose ...]` bracket placeholder must survive in the assembled output.

Sanity check before Step 4:

```bash
# Save the assembled new_string to a temp file and run:
echo "$NEW_STRING" | grep -cE '^\[Compose'
# Expected: 0
echo "$NEW_STRING" | grep -cE 'humanlayer/[A-Za-z0-9._/-]'
# Expected: 0
echo "$NEW_STRING" | grep -cE 'github\.com/humanlayer/humanlayer'
# Expected: 1
```

If any expected count fails, return to the relevant compose step and fix before applying the Edit.

- [ ] **Step 4: Apply the edit**

Use the Edit tool with:
- `old_string`: the entire existing "HumanLayer Codebase Findings" section captured in Step 2 (from the `## ` heading line through the line before the next `## ` heading)
- `new_string`: the assembled output from Step 3f

- [ ] **Step 5: Verify section header swap**

Two separate checks (both must hold):

```bash
grep -c '^## HumanLayer Codebase Findings' dev/research/2026-04-25-harness-engineering-research.md
# Expected: 0  (old heading must be gone)

grep -c '^## Case Study: HumanLayer' dev/research/2026-04-25-harness-engineering-research.md
# Expected: 1  (new heading must be present)
```

- [ ] **Step 6: Verify no path leaks in new section**

```bash
awk '/^## Case Study: HumanLayer/{f=1; next} /^## /{f=0} f' \
  dev/research/2026-04-25-harness-engineering-research.md \
  | grep -nE 'humanlayer/[A-Za-z0-9._/-]'
```

Expected: zero output.

- [ ] **Step 7: Verify repo URL appears in section exactly once**

```bash
awk '/^## Case Study: HumanLayer/{f=1; next} /^## /{f=0} f' \
  dev/research/2026-04-25-harness-engineering-research.md \
  | grep -cE 'github\.com/humanlayer/humanlayer'
```

Expected: `1`.

- [ ] **Step 8: Verify hard rule — every patterns/surprises paragraph names an ai/docs concept**

Manual review. Read each paragraph of Patterns Confirmed, Patterns Absent, and Notable Surprises in the new section. Each must explicitly name at least one `ai/docs/` concept. If any paragraph fails, edit it to name the relevant concept before proceeding.

---

## Task 3: Delete Code References "HumanLayer Codebase — Concrete Instantiation" Subsection

**Goal:** Remove the entire H3/H4 subsection in the Code References block that currently lists ~30 file:line citations into the local `humanlayer/` checkout.

**Files:**
- Modify: `dev/research/2026-04-25-harness-engineering-research.md`

- [ ] **Step 1: Locate subsection boundaries**

```bash
grep -nE '^### .*HumanLayer Codebase|^### .*Concrete Instantiation' \
  dev/research/2026-04-25-harness-engineering-research.md
```

Expected: exactly one line, capturing the subsection heading. Record its line number. Then identify the next `### ` or `## ` heading after it — those bracket the block.

```bash
awk -v start=<heading-line> 'NR>=start && /^(##|###) / && NR>start{print NR; exit}' \
  dev/research/2026-04-25-harness-engineering-research.md
```

Substitute `<heading-line>` with the line number from the first command.

- [ ] **Step 2: Read the subsection to confirm**

```bash
sed -n '<start>,<end-1>p' dev/research/2026-04-25-harness-engineering-research.md
```

Confirm the full subsection (heading + ~30 file:line cite lines) is captured.

- [ ] **Step 3: Apply the edit**

Use the Edit tool with:
- `old_string`: the entire subsection from the `### ` heading line through the line before the next heading
- `new_string`: empty string

- [ ] **Step 4: Verify subsection gone**

```bash
grep -nE '^### .*(HumanLayer Codebase|Concrete Instantiation)' \
  dev/research/2026-04-25-harness-engineering-research.md
```

Expected: zero output.

- [ ] **Step 5: Verify Code References block still intact**

```bash
grep -nE '^## Code References' dev/research/2026-04-25-harness-engineering-research.md
```

Expected: exactly one line. The parent H2 must still exist.

---

## Task 4: Reword Architecture Insight #9

**Goal:** Insight #9 (heavy-stack vs lean-shell) currently uses HumanLayer as evidence. Reword to a pure concept tension on the `ai/docs/` spine. HumanLayer reference allowed once via `(see Case Study)` — optional.

**Files:**
- Modify: `dev/research/2026-04-25-harness-engineering-research.md`

- [ ] **Step 1: Locate Insight #9**

```bash
grep -nE '^### .*Insight 9|^### 9\.|^### .*heavy.stack' \
  dev/research/2026-04-25-harness-engineering-research.md
```

Expected: exactly one line. Record line number. Capture the full insight block (until next `### ` or `## ` heading).

- [ ] **Step 2: Read the insight in full**

```bash
sed -n '<start>,<end-1>p' dev/research/2026-04-25-harness-engineering-research.md
```

Identify the sentence(s) that lean on HumanLayer as evidence (paths, file:line, or "HumanLayer demonstrates X" wording).

- [ ] **Step 3: Compose the reworded insight**

Reword the insight so the heavy-stack vs lean-shell tension stands on the `ai/docs/` concept spine alone. The reasoning should reference `ai/docs/` concepts (memory, skills, hooks, subagents, etc.) — not a specific codebase. If a HumanLayer pointer adds value, include exactly one parenthetical `(see Case Study)` cross-link.

- [ ] **Step 4: Apply the edit**

Use the Edit tool with:
- `old_string`: the exact original insight text from Step 2
- `new_string`: the reworded insight from Step 3

- [ ] **Step 5: Verify no path leaks in insight**

```bash
sed -n '<start>,<end-1>p' dev/research/2026-04-25-harness-engineering-research.md \
  | grep -nE 'humanlayer/[A-Za-z0-9._/-]|humanlayer.*:[0-9]+'
```

Expected: zero output. (Use the new line range — block size may have changed.)

- [ ] **Step 6: Verify insight still present**

```bash
grep -cE '^### .*(Insight 9|9\.|heavy.stack)' \
  dev/research/2026-04-25-harness-engineering-research.md
```

Expected: `1`. The insight must still exist with its rewording.

---

## Task 5: Reword Related Research Items

**Goal:** Replace HumanLayer-comparison items in the "Related Research" block with concept-only items.

**Files:**
- Modify: `dev/research/2026-04-25-harness-engineering-research.md`

- [ ] **Step 1: Locate Related Research block**

```bash
grep -nE '^## Related Research' dev/research/2026-04-25-harness-engineering-research.md
```

Expected: exactly one line.

- [ ] **Step 2: Identify HumanLayer items in the block**

```bash
awk '/^## Related Research/{f=1; next} /^## /{f=0} f' \
  dev/research/2026-04-25-harness-engineering-research.md \
  | grep -niE 'humanlayer'
```

Expected: list of lines mentioning HumanLayer. Record the exact text of each.

- [ ] **Step 3: For each HumanLayer-mentioning item, compose a concept-level replacement**

A HumanLayer-comparison item like "compare HumanLayer's lack of hooks against ai/docs concept of automation gates" becomes "investigate when ai/docs hooks are necessary versus when slash-command-driven workflows suffice." Drop the codebase anchor; keep the concept question.

- [ ] **Step 4: Apply the edits**

Use the Edit tool one item at a time. For each:
- `old_string`: the exact HumanLayer-mentioning item line(s)
- `new_string`: the concept-level rewrite

- [ ] **Step 5: Verify**

```bash
awk '/^## Related Research/{f=1; next} /^## /{f=0} f' \
  dev/research/2026-04-25-harness-engineering-research.md \
  | grep -niE 'humanlayer'
```

Expected: zero output.

---

## Task 6: Reword Open Questions Q5

**Goal:** Q5 (lean-shell vs heavy-stack viability) currently has light HumanLayer phrasing. Strip it.

**Files:**
- Modify: `dev/research/2026-04-25-harness-engineering-research.md`

- [ ] **Step 1: Locate Open Questions block**

```bash
grep -nE '^## Open Questions' dev/research/2026-04-25-harness-engineering-research.md
```

Expected: exactly one line.

- [ ] **Step 2: Read Q5**

```bash
awk '/^## Open Questions/{f=1; next} /^## /{f=0} f' \
  dev/research/2026-04-25-harness-engineering-research.md \
  | grep -nE '^.*Q5|^- .*Q5|^[0-9]+\. .*Q5|lean.shell|heavy.stack'
```

Identify the Q5 line(s).

- [ ] **Step 3: Compose the reworded Q5**

Q5 must remain a concept question about lean-shell vs heavy-stack viability for small teams. Strip any HumanLayer-specific phrasing or anchor.

- [ ] **Step 4: Apply the edit**

Use the Edit tool:
- `old_string`: original Q5 line(s)
- `new_string`: reworded Q5

- [ ] **Step 5: Verify**

```bash
awk '/^## Open Questions/{f=1; next} /^## /{f=0} f' \
  dev/research/2026-04-25-harness-engineering-research.md \
  | grep -niE 'humanlayer'
```

Expected: zero output.

---

## Task 7: Final Path Sweep

**Goal:** Catch any remaining `humanlayer/` path string outside the allowed contexts (the single repo URL in Task 2's lead paragraph; the `https://github.com/humanlayer/humanlayer` URL on the frontmatter).

**Files:**
- Modify: `dev/research/2026-04-25-harness-engineering-research.md` (only if leaks found)

- [ ] **Step 1: Run the sweep**

```bash
grep -n 'humanlayer/' dev/research/2026-04-25-harness-engineering-research.md \
  | grep -v 'github.com/humanlayer/humanlayer'
```

Expected: zero output.

- [ ] **Step 2: If non-zero output, edit each leak**

For each line returned in Step 1:
- Read the surrounding context (`sed -n '<line-3>,<line+3>p' file`)
- Decide: replace path with concept name, replace with `(see Case Study)` cross-link, or delete the leaking sentence outright
- Apply the Edit
- Re-run Step 1

Iterate until Step 1 returns zero output.

- [ ] **Step 3: Sweep for residual file:line patterns**

```bash
grep -nE 'humanlayer.*:[0-9]+' dev/research/2026-04-25-harness-engineering-research.md
```

Expected: zero output. If non-zero, repeat the edit cycle from Step 2.

---

## Task 8: Full Verification Suite + Commit

**Goal:** Run all five verification commands from the spec. Confirm all expected outputs. Stage and commit the research-file changes as the second commit.

**Files:**
- Modify: none in this task — purely verify and commit
- Stage: `dev/research/2026-04-25-harness-engineering-research.md`

- [ ] **Step 1: Verification 1 — zero HumanLayer paths**

```bash
grep -n 'humanlayer/' dev/research/2026-04-25-harness-engineering-research.md \
  | grep -v 'github.com/humanlayer/humanlayer'
```

Expected: zero output.

- [ ] **Step 2: Verification 2 — zero file:line citations**

```bash
grep -nE 'humanlayer.*:[0-9]+' dev/research/2026-04-25-harness-engineering-research.md
```

Expected: zero output.

- [ ] **Step 3: Verification 3 — repo URL appears exactly once**

```bash
grep -cE 'github\.com/humanlayer/humanlayer' dev/research/2026-04-25-harness-engineering-research.md
```

Expected: `1`.

- [ ] **Step 4: Verification 4 — appendix queries still validate against graph.json**

```bash
jq -r '.nodes[].label' /home/rodrigo/Workspace/ai-study-library/graphify-out/graph.json | sort -u > /tmp/labels.txt
grep -E "^/graphify (path|explain)" dev/research/2026-04-25-harness-engineering-research.md \
  | grep -oE '"[^"]+"' | sort -u > /tmp/used.txt
comm -23 /tmp/used.txt <(sed 's/.*/"&"/' /tmp/labels.txt | sort -u)
```

Expected: only `"Node A"`, `"Node B"`, `"Node Name"` placeholders remain (these are intentional placeholders for query templates).

- [ ] **Step 5: Verification 5 — line-count regression**

```bash
wc -l dev/research/2026-04-25-harness-engineering-research.md
```

Expected: net reduction from 1567. Estimated range ~1480-1530 (per spec). If outside this range by more than ±50 lines, audit the rewrite for unintended deletion or expansion before committing.

- [ ] **Step 6: Stage the research file**

```bash
rtk git add dev/research/2026-04-25-harness-engineering-research.md
```

- [ ] **Step 7: Commit**

```bash
rtk git commit -m "$(cat <<'EOF'
docs(research): reframe HumanLayer as case study, remove paths

Strip all HumanLayer file:line citations and local-path references
from the harness-engineering research doc. Replace the previous
findings section with a Case Study: HumanLayer section that maps
ai/docs concepts to observed patterns. Delete the Code References
HumanLayer subsection. Reword Architecture Insight #9, Related
Research items, and Open Questions Q5 to drop HumanLayer anchoring.

Doc is now portable: usable as a reference in any project that has
only ai/docs/ and graphify-out/ available locally — no humanlayer/
checkout required.

Spec: docs/superpowers/specs/2026-04-25-research-doc-humanlayer-reframe-design.md
Plan: docs/superpowers/plans/2026-04-25-research-doc-humanlayer-reframe.md

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 8: Verify commit landed**

```bash
rtk git log -1 --stat
rtk git status
```

Expected: commit shows the research file. `git status` shows clean working tree.

---

## Post-flight

After Task 8 commits cleanly, the worktree branch `research-doc-humanlayer-reframe` contains the full rewrite. Hand back to the user — they decide whether to merge the worktree branch back to `main`, open a PR, or iterate further.

Recommend the user:
- Diff-review the worktree branch against main before merging.
- Run `git worktree remove ./dev/wt-research-reframe` after merge to clean up.

## Open Questions for Executor

None. All branches of execution are specified.

## Out of Scope (do not address in this plan)

- The `humanlayer/` vendored directory itself.
- Markdown lint warnings (MD032/MD060/MD025/MD040/cSpell).
- Sub-project B (local knowledge-stack tool) — separate spec/plan.
- Any other research file.
