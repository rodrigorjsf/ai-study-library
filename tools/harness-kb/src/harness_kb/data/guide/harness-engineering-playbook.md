---
date: 2026-04-25T00:00:00-03:00
topic: "Harness Engineering Reference: Artifacts, Long-Running Context Maintenance, Subagent Best Practices"
tags: [research, harness-engineering, context-engineering, subagents, skills, hooks, humanlayer, agent-protocols, claude-code, cursor]
status: complete
last_updated: 2026-04-25
sources:
  - ai/docs/ (corpus of 117 documents, ~272K words)
  - https://github.com/humanlayer/humanlayer (concrete reference implementation: TS MCP + Go daemon + Tauri UI)
  - `harness-kb graph + harness-kb wiki` (knowledge graph: 476 nodes, 665 edges, 21 communities)
intended_audience: LLM agents producing harness engineering structures (plugins, skills, agents, rules, hooks, references) for any project
---

# Harness Engineering Reference Guide

**Date:** 2026-04-25

## Research Question

How does the `ai/docs/` corpus synthesize a coherent harness engineering practice, and how does the HumanLayer codebase concretely instantiate (and selectively diverge from) those patterns? Produce a single reference an LLM agent can use to build any harness engineering structure efficiently — covering artifact development, automatic context window maintenance for long-running executions, subagent execution best practices, and artifact creation guidelines, all with verifiable citations.

## Summary

A coding agent is `AI model(s) + harness`. The harness is everything around the model — context injection, control flow, action surfaces, persistence, and observe-and-verify. **Harness engineering is the operationalization of context engineering**: every recurring agent failure becomes a structural fix in the harness so that mistake never repeats.

The corpus surveyed here converges on a **canonical harness pattern**: a stack of seven artifact classes — references, rules, skills, agents, hooks, commands-as-skills, and CI evals — governed by five operating priorities (Smart Zone <40%, Harness-First, Subagent Isolation, Artifact-First, Progressive Disclosure). HumanLayer is studied as a case-study instance (see Case Study) that confirms several of these patterns strongly (subagent isolation, structured-note state, session forking) and selectively diverges from others (zero hooks, zero skills, no explicit "smart zone" terminology — back-pressure shifted to a daemon-mediated approval loop instead of Stop hooks). Both equilibria are legitimate; this guide treats them as the two endpoints on a spectrum from "heavy artifact stack" to "lean shell + daemon."

The empirical foundation comes from four converging bodies of evidence:
1. **Lost-in-the-Middle** (Liu et al., TACL 2024) — U-shaped recall curve.
2. **Same-Task-More-Tokens** (Levy et al., ACL 2024) — accuracy 0.92 → 0.68 with 3K filler tokens.
3. **Chroma context-rot study** — all 18 models tested degrade with context length, at every increment.
4. **ETH AGENTBENCH** — LLM-generated `AGENTS.md` files HURT performance and cost 20%+ more reasoning tokens.

The structural responses are: (a) keep always-loaded files small (target <200 lines, ideally <60), (b) push everything else behind progressive disclosure (skills, path-scoped rules, references loaded JIT), (c) delegate noisy work to subagents that return compacted briefs, (d) convert behavioral instructions to deterministic hooks where possible, (e) gate completion on verification evidence, not assertions.

This document is structured so a downstream LLM agent can copy the artifact templates verbatim, follow the orchestration patterns, and cite the primary sources when justifying design choices.

---

## Part I — Detailed Findings

### Canonical Harness Components (Synthesized)

The corpus converges on a stack of seven artifact classes that, taken together, operationalize context engineering at the project level. Listed in load-order from "always present" to "loaded only on explicit demand":

| # | Class | Lives at | Loaded when | Target size |
|---|-------|----------|-------------|-------------|
| 1 | **Always-loaded memory** | `CLAUDE.md` / `AGENTS.md` (root + per-package) | Every session | <60 lines preferred, hard cap 200 |
| 2 | **Path-scoped rules** | `.claude/rules/<name>.md` (frontmatter `paths: [glob]`) | Files matching the glob enter context | 30-80 lines |
| 3 | **References (policy layer)** | `<plugin>/references/<name>.md` (mirrored to `.claude/references/`) | Linked from a skill's "Context Contract" section | ≤100 lines, mirror parity enforced |
| 4 | **Skills** | `<plugin>/skills/<name>/SKILL.md` + optional `references/`, `scripts/`, `assets/` | Slash command, MCP discovery, or context-match trigger | SKILL.md <500 lines (≤400 recommended) |
| 5 | **Subagents** | `<plugin>/agents/<name>.md` (YAML + system prompt) | Parent agent dispatches via `Agent` tool | Frontmatter declares model, tools, `maxTurns` |
| 6 | **Hooks** | `<plugin>/hooks/hooks.json` + handler scripts | Lifecycle event fires (22 events in Claude Code) | Each handler ≤100 lines, exit-code contract |
| 7 | **CI evals** | `scripts/<plugin>_prompt_eval.py` + `tests/<plugin>/prompt-cases.json` + GitHub workflow | Every PR | Deterministic — no LLM calls |

**Five recommended canonical references** (each ≤100 lines, mirror parity, deletion-test enforced — i.e., deleting the file should cause every consumer to fail an explicit error referencing it):

| File | Purpose |
|------|---------|
| `harness-taxonomy.md` | Three component classes: **artifact** (produces durable file), **advisory** (read-only recommendation), **utility** (operational helper). Allowed tools and constraints per class. |
| `context-budget-policy.md` | Smart-Zone thresholds (e.g., 40% normal / 70% requires compaction or handoff); per-phase brief size limits (discovery ≤50, execution ≤30, validation ≤20 lines). Cites Levy et al. ACL 2024. |
| `execution-policy.md` | Four delegation modes: **stay inline** (<5 file reads, deterministic), **isolated subagent** (noisy exploration, returns compact brief), **parallelize subagents** (independent scopes, no shared state), **repo-local eval harness** (deterministic batch verification). |
| `artifact-lifecycle.md` | `.claude/PRPs/` paths and naming (`<NN>-<slug>.prd.md`, `<NN>-<slug>.plan.md`, `archived/<NN>-<slug>.plan.md`). |
| `agent-prompt-style.md` | Required system-prompt structure: CRITICAL one-job declaration → DO NOT boundaries → Core Responsibilities → Strategy → Output Format → Approval Criteria. |

Skills load these references on demand via a **Context Contract** section instead of restating policy content. This is the deduplication mechanism that lets the always-loaded budget stay small while shared discipline remains enforceable.

**Rule layer** maps path globs to scoped rules. Recommended baseline:

| Rule (suggested name) | Path scope | Intent |
|------|-----------|--------|
| `harness-engineering.md` | `.claude/**/*.md`, `**/*.prd.md`, `**/*.plan.md` | Smart-zone thresholds, harness rails, subagent isolation, artifact discipline, progressive disclosure |
| `<plugin>-workflow.md` | `.claude/PRPs/prds/**`, `.claude/PRPs/plans/**` | Lifecycle gates: advisor-first, GitHub issue creation/update, verification before completion, commit per phase |
| `agent-conventions.md` | (root) | YAML frontmatter requirements, model selection heuristics, advisory-only constraint |
| `hook-conventions.md` | (root) | Hook stdin/stdout/sentinel contract |
| `reference-conventions.md` | (root) | References ≤100 lines, mirror parity, deletion test |
| `skill-conventions.md` | (root) | SKILL.md ≤400 lines, frontmatter, plugin-qualified agent names |

**Skill layer** is the user-invocable command surface. A typical complete harness exposes 12-18 skills, partitioned by class:

- **Artifact-class** (3-7): a PRD generator, plan generator, implementation runner, GitHub-issue-investigate, GitHub-issue-fix, multi-agent research team planner, autonomous-loop launcher.
- **Utility-class** (4-6): codebase-question (parallel-subagent research), 5-Whys debugger, atomic conventional commit, PR-with-template, verification-before-completion gate, autonomous-loop cancel.
- **Advisory-class** (3-4): senior PR review (single agent), multi-agent PR review (parallel critics), advisor (native-tool-detect + subagent fallback).

Names should be plugin-prefixed (`<plugin>-prd`, `<plugin>-plan`, `<plugin>-implement`, `<plugin>-advisor`, etc.) to namespace cleanly when multiple plugins coexist.

**Agent layer** default tool allowlist is `Read, Grep, Glob, Bash, Agent, Skill`. Advisory agents are read-only with `maxTurns: 10`. Recommended baseline subagents and model selection:

| Suggested agent | Role | Model |
|-------|------|-------|
| `code-reviewer` | Project-guideline compliance, bugs, quality (confidence ≥80) | sonnet |
| `code-simplifier` | Clarity opportunities, advisory-only (no edits) | sonnet |
| `codebase-analyst` | HOW code works, traces flow, file:line refs | sonnet |
| `codebase-explorer` | WHERE code lives + extracts patterns | haiku, maxTurns 15 |
| `comment-analyzer` | Comment accuracy/value audit | haiku |
| `docs-impact-agent` | Stale docs, missing entries, advisory-only | haiku |
| `plan-critic` | Validates consolidated findings before plan/PRD write — PROCEED \| REVISE | sonnet, maxTurns 10 |
| `pr-test-analyzer` | Behavioral coverage, criticality 1-10 | sonnet |
| `silent-failure-hunter` | Swallowed errors, inadequate handling | sonnet |
| `type-design-analyzer` | Encapsulation, invariants 1-10 | sonnet |
| `<plugin>-advisor` | Second-opinion before substantive work; ≤100 words enumerated | opus, effort high, maxTurns 10 |
| `web-researcher` | External docs research with citations | sonnet |

**Hook layer** at minimum registers two Stop hooks:

- **Loop-continuation Stop hook** — reads a state file (`.claude/<plugin>-ralph.state.md`) with YAML frontmatter (`iteration`, `max_iterations`, `plan_path`); injects the next-iteration prompt; terminates when sentinel `<promise>COMPLETE</promise>` is found in conversation.
- **Artifact-validation Stop hook** — verifies a generated artifact contains required sections (e.g., the six-section schema for a research-team plan: `## Research Question`, `## Research Question Decomposition`, `## Team Composition`, `## Research Tasks`, `## Team Orchestration Guide`, `## Acceptance Criteria`); blocks completion via exit code 2 if missing.

Hook contract: JSON in/out via stdin/stdout, stderr for messages, `set -euo pipefail`, sentinel-based loop termination, `stop_hook_active` field check to prevent infinite Stop loops.

**CI eval layer** runs 4-6 deterministic prompt-contract cases per release: contract-string presence checks (every SKILL.md must contain `## Context Contract`), mirror-parity for every `<plugin>/<x>` vs `.claude/<x>` pair, hook section-schema regex. No LLM calls — pure file reads and regex. Wired into a GitHub Actions workflow that blocks merge on failure.

This canonical pattern represents the **heavy-stack** equilibrium. The HumanLayer Case Study (below) is the **lean-shell** equilibrium — same operating priorities, very different artifact mass.

### `ai/docs/` Thematic Map

The 117-document corpus organizes around eight themes whose canonical primary sources are listed below. Citations are relative to `ai/docs/` unless absolute.

#### Harness Engineering
- `harness-engineering/skill-issue-harness-engineering-for-coding-agents.md:30-33` — `coding agent = AI model(s) + harness`; harness components are Context Injection, Control, Action, Persist, Observe-and-Verify.
- `harness-engineering/skill-issue-harness-engineering-for-coding-agents.md:80-104` — every agent mistake should become a structural harness fix (Mitchell Hashimoto).
- `harness-engineering/harness-engineering.md:24-35` — Five Pillars of Context Engineering: Selection, Structuring, Memory, Compression, Evaluation.
- `harness-engineering/harness-engineering.md:37-44` — Smart Zone vs Dumb Zone (~40-60% context utilization).
- `harness-engineering/skill-issue-harness-engineering-for-coding-agents.md:683-696` — Back-pressure: success likelihood correlates with self-verification surface (typecheck, lint, test).
- `harness-engineering/harness-engineering.md:95` and `skill-issue:692-696` — Golden Rule of Output: success silent, failures verbose.
- `claude/effective-harnesses-long-running-agents.md:23-110` — Initializer Agent + Coding Agent pattern with `init.sh`, `claude-progress.txt`, `feature_list.json`.
- `agentic-engineering/research-plan-implement-rpi.md:30-34` — RPI leverage hierarchy: bad research → 1000s bad lines; bad plan → 100s; bad code → 1.
- `agentic-engineering/research-plan-implement-rpi.md:23-29,150-160` — Frequent Intentional Compaction (FIC): each phase starts at 10-15% utilization with compacted artifact.

#### Context Engineering & Long-Running Maintenance
- `general-llm/research-context-engineering-comprehensive.md:36` — Anthropic's unifying definition: "find the smallest possible set of high-signal tokens that maximize the likelihood of some desired outcome."
- `general-llm/research-context-rot-and-management.md:21-27` — Three architectural causes of rot: n² self-attention, training-distribution mismatch, position interpolation degradation.
- `general-llm/research-context-rot-and-management.md:104-117` — Lost-in-the-Middle U-shaped curve: 10-20% drop when info is buried mid-context (Liu et al., TACL 2023). Place critical instructions at start AND end.
- `general-llm/research-context-rot-and-management.md:130-146` — Same-Task-More-Tokens: accuracy 0.92 → 0.68 at 3K filler tokens (Levy et al., ACL 2024).
- `context-engineering/agents-md-is-a-liability-paddo.md:21-31,53-62` — IFScale 500-instruction ceiling; attention sinks (Xiao et al., ICLR 2024) — instructions at the top of `AGENTS.md` ride the sink.
- `general-llm/research-context-rot-and-management.md:236-273` — Anthropic's three strategies: Compaction, Structured Note-Taking, Sub-Agent Architectures; just-in-time loading; progressive-disclosure mechanism table.
- `context-engineering/progressive-disclosure-ai-agents.md:64-108` — Four progressive-disclosure patterns: index-first, scout, phase-based, separated skill files.
- `general-llm/Evaluating-AGENTS-paper.md` (ETH Zurich) — LLM-generated agentfiles HURT performance and cost 20%+ more reasoning tokens.
- `context-engineering/advanced-context-engineering-coding-agents-dev.md:67-82` — Bad-correction loops reinforce failure. Anthropic's "after two failed corrections, /clear".
- `context-engineering/shedding-dead-context-ryan-spletzer.md:1-50,62-78` — Dead context (plugins/skills/CLAUDE.md occupying space without contributing). Bigger window = more RAM with a memory leak.

#### Subagent Best Practices
- `harness-engineering/skill-issue-harness-engineering-for-coding-agents.md:388-394` — Sub-agents are for context control, not roles. "Frontend agent / backend agent / QA agent" doesn't work.
- `analysis/analysis-research-subagent-best-practices.md:23-31` — Description is the routing signal: include "Use proactively when [trigger]".
- `analysis/analysis-research-subagent-best-practices.md:84-95` — Effective system-prompt structure: Role → Process → Checklist → Output Format → Approval Criteria.
- `analysis/analysis-research-subagent-best-practices.md:99-149` — Read-only agents dominate community examples; Opus reserved for `architect`, Sonnet default, Haiku only for mechanical/exploration.
- `analysis/analysis-research-subagent-best-practices.md:138-149` — Confidence-Based Filtering: report only if >80% confident.
- `analysis/analysis-research-subagent-best-practices.md:155-170` — 10 documented anti-patterns: aggressive "CRITICAL" prompts, too many skills/agents (~2% per description), god agents, no `maxTurns`, vague descriptions, no output format.
- `analysis/analysis-research-subagent-best-practices.md:236` — Anti-nesting: subagents cannot spawn subagents.
- `analysis/analysis-claude-orchestrate-of-claude-code-sessions.md:1-87,254-274` — Agent Teams (peer-to-peer mailbox, shared task list, `TeammateIdle`/`TaskCompleted` hooks); start with 3-5 teammates, 5-6 tasks each.
- `analysis/analysis-claude-orchestrate-of-claude-code-sessions.md:138-150` — Decision tree: need inter-worker communication or debate? Teams. Otherwise subagents.
- `harness-engineering/skill-issue-harness-engineering-for-coding-agents.md:494-528` — Subagents return citation-rich summaries (`filepath:line`) so parent re-fetches detail.

#### Skills (Open Standard + Claude Code)
- `shared/skills-standard/agentskills-specification.md:23-249` — SKILL.md format: YAML frontmatter (`name` ≤64 chars, `description` ≤1024 chars, optional `license`, `compatibility`, `metadata`, `allowed-tools`); three-tier progressive disclosure (metadata ~100 tokens always; instructions <5000 tokens on activation; resources `scripts/`/`references/`/`assets/` only when referenced); SKILL.md target <500 lines.
- `shared/skills-standard/agentskills-optimizing-descriptions.md:22-167` — Description carries the entire trigger burden. Use imperative phrasing. Eval-driven loop: ~20 queries (8-10 should-trigger, 8-10 near-miss should-not-trigger), train/validation 60/40, 5 iterations usually enough.
- `shared/skills-standard/agentskills-best-practices.md:48-262` — Add what the agent lacks; match specificity to fragility; provide defaults not menus; procedures over declarations; gotchas section is highest-value.
- `mcp/skills-over-mcp-meeting-notes-2248.md:60-79,118-124` — Skills can be instructors (enforced) or helpers (advisory). Working-group consensus: support both via `enforcement` metadata.

#### Hooks
- `analysis/analysis-automate-workflow-with-hooks.md:22-30` — Four hook types: command (shell), http (POST), prompt (single-turn LLM), agent (subagent verifier).
- `analysis/analysis-automate-workflow-with-hooks.md:32-74` — 22 lifecycle events: Session, Agentic loop, Subagent, Compaction, Control, Configuration, Worktree, MCP.
- `analysis/analysis-automate-workflow-with-hooks.md:75-93` — Communication: stdin JSON → hook → stdout/stderr + exit code. Exit 0 = allow; 2 = block (stderr feedback to Claude); other = allow with stderr verbose.
- `analysis/analysis-automate-workflow-with-hooks.md:95-130` — Matchers are case-sensitive regex; configuration scope hierarchy.
- `analysis/analysis-automate-workflow-with-hooks.md:138-194` — Pitfalls: infinite Stop-hook loops (must check `stop_hook_active`), shell-profile `echo` poisoning stdout, case-sensitive matchers, `PermissionRequest` doesn't fire in headless `-p` mode, `PostToolUse` cannot undo, `"allow"` from PreToolUse doesn't override permission deny rules.
- `harness-engineering/skill-issue-harness-engineering-for-coding-agents.md:639-681` — HumanLayer's Stop hook runs biome + typecheck in parallel; success silent, failures exit 2 to re-engage agent.

#### Agent Protocols (MCP, A2A, ACP, ANP)
- `mcp/mcp-specification.md` — Authoritative MCP spec.
- `harness-engineering/skill-issue-harness-engineering-for-coding-agents.md:299-336` — MCP primitives are tools/resources/prompts/elicitations; in practice "MCP servers are primarily for plugging tools." Resources/prompts/elicitations are not well-supported by clients. Too many tools push you into the dumb zone.
- `agent-protocols/architectural-paradigms-advanced-agentic-systems.md:90-98` — MCP collapses N×M integration to M+N.
- `tool-calling/programmatic-tool-calling-claude-api.md:23-90` — Anthropic's experimental `tool_search` server tool: progressive disclosure for tools (JIT load definitions). Programmatic Tool Calling: LLM writes orchestration code → sandbox runs → only final result returns; ~80% token savings.
- `harness-engineering/harness-engineering.md:55-58` — MCP June 2026 roadmap: SEP-1442/SEP-2243 (stateless transport via HTTP headers), SEP-2322 MRTR (Multi-Round-Trip Requests), SEP-1686 (Tasks for durable async jobs).
- `harness-engineering/skill-issue-harness-engineering-for-coding-agents.md:333-356` — MCP vs CLI tradeoff: when an MCP server duplicates a CLI well-represented in training data, prompting the agent to use the CLI works better.

#### Spec-Driven Development
- `spec-driven-development/spec-driven-development-main.md:21-44` — Three adoption levels: spec-first / spec-anchored / spec-as-source. Spec Kit (`/specify` → `/plan` → `/tasks`), AWS Kiro (3-document workflow), Tessl (1:1 spec↔code mapping).
- `spec-driven-development/spec-driven-development-main.md:88-94` — Move ambiguity from code review to spec review where it's cheaper to fix.

#### Prompting / Structured Outputs
- `claude/prompting-best-practices.md:11-117` — Be explicit and add context; long-horizon reasoning + state tracking; multi-context-window prompting (initializer setup, structured tests JSON, `init.sh` quality-of-life scripts, starting fresh > compacting, verification tools); state management (JSON for state data, unstructured for progress notes, git for checkpoints).
- `structured-outputs/anthropic-strict-tool-use.md:7-145` — `strict: true` enables grammar-constrained sampling; 20 strict tools per request, 24 optional params, 16 union-typed params; combine `tool_choice: any` with strict for guaranteed tool call + schema conformance.

### Knowledge Graph Structure (`harness-kb graph + harness-kb wiki`)

The graphify run on 2026-04-25 produced:
- 117 files, ~272,422 words analyzed
- 476 nodes, 665 edges, 21 communities
- Edge quality: 89% EXTRACTED, 10% INFERRED, 1% AMBIGUOUS

**God nodes** (most-connected core abstractions):
1. Progressive Disclosure (Skills Context Management) — 20 edges
2. Spec-Driven Development — 17 edges
3. Cursor Hooks Guide — 15 edges
4. Model Context Protocol (MCP) — 13 edges
5. Cursor Subagents Guide — 12 edges
6. Research-Plan-Implement (RPI) Workflow — 12 edges
7. SKILL.md Format (Frontmatter + Markdown Body) — 12 edges
8. Cursor Rules Guide — 11 edges
9. Lost in the Middle (Liu et al., TACL 2024) — 11 edges
10. Cursor IDE Official Documentation README — 10 edges

**Communities** (top by size, all 21 in `graphify-out/GRAPH_REPORT.md`):
- 0: Cursor Agent Tooling (64 nodes)
- 1: Agent Orchestration & Plugins (57 nodes)
- 2: Agent Skills Standard (55 nodes)
- 3: Agent Communication Protocols (47 nodes)
- 4: Agentic Harness Patterns (38 nodes)
- 5: Context Engineering Foundations (35 nodes)
- 6: Advanced Context Optimization (34 nodes)
- 7: MCP & Protocol Ecosystem (29 nodes)
- 8: Spec-Driven Development (24 nodes)
- 9: Prompting Techniques (23 nodes)
- 10-17: smaller specialized clusters (HumanLayer, AGENTS.md research, Human-Agent Collaboration, MCP Enterprise, etc.)

**Surprising connections**: SDD ↔ CFG Constrained Decoding; Phase-Based Context Loading ↔ RPI Workflow; Progressive Skill Loading ↔ Progressive Disclosure in AI Agents; Cursor Agent Skills bridges Agentic Harness Patterns ↔ Agent Orchestration & Plugins (betweenness 0.387 — highest cross-community broker).

### Case Study: HumanLayer — Concepts from ai/docs Applied in Practice

HumanLayer is an open-source agent-tooling project. Studied here as a concrete instance of `ai/docs/` harness concepts running in production code. Repository: <https://github.com/humanlayer/humanlayer>. Treat this section as a snapshot — case-study only, zero path citations, may drift as upstream evolves.

#### Concept→Pattern Mapping

| ai/docs concept | What HumanLayer applies it to | Observed pattern |
|---|---|---|
| Always-loaded memory (CLAUDE.md) | Project-wide rules and protocol enforcement | Single root CLAUDE.md, no path-scoped variants |
| Subagent as context firewall | Dispatching parallel research tasks | Subagent results return as compressed summaries to the main thread |
| Approval-loop / human-in-the-loop | Tool-call gating before destructive ops | MCP-mediated approval channel |
| Plugin-as-orchestrator | Bundling agents and commands as one unit | `.claude/` directory packages the workflow |
| Long-running maintenance | Recurring repo hygiene tasks | Slash-command driven, manual trigger |
| Verification gates | Pre-completion checks | Inline command checklists, no formal hook |
| Progressive disclosure | Skill content unloaded until needed | capability loaded on invocation, not upfront |
| Smart-zone / context-rot mitigation | Keeping working set lean | Heavy reliance on commands and subagents to scope context |

#### Patterns Confirmed

*Always-loaded memory.* The ai/docs concept of CLAUDE.md as a curated, lean context spine shows up here as a single short root memory file that encodes repo structure, dev commands, and a graded-priority TODO convention. The takeaway for an ai/docs reader is that always-loaded memory pays off when it is the smallest possible authoritative description of the project — anything longer competes with the user prompt for attention and erodes the smart-zone the ai/docs concept describes; the same lean-memory discipline this case study confirms is the practical realization of smart-zone / context-rot mitigation in always-loaded context.

*Subagent as context firewall.* The ai/docs treatment of subagent isolation — sub-threads that gather information and return compressed summaries — is realized by a fleet of read-only agents, each scoped to a single retrieval task (locating files, finding patterns, searching the web), that return compressed summaries to the parent. Every agent is a pure retrieval surface; judgement stays in the parent context. For an ai/docs reader this is the canonical context-firewall pattern made concrete: the parent thread never sees the raw search hits, only the agent's distilled answer, which is exactly the bandwidth saving the concept promises.

*Approval-loop / human-in-the-loop.* The ai/docs concept of an approval gate before destructive tool calls is implemented as an out-of-band approval channel: every tool call is intercepted by an MCP-mediated permission tool that blocks until a human decides. The pattern matters because it moves back-pressure off the agent's hot path — the agent does not need to self-police, the harness does. An ai/docs reader should read this as a worked example of the human-in-the-loop concept extended beyond simple confirmation prompts into a durable, multi-surface (terminal, web, chat) approval queue.

*Plugin-as-orchestrator.* The ai/docs concept of bundling commands and agents into a single coherent unit is present as a flat `.claude/` directory that ships agents, slash commands, and settings together as the project's working harness. The unit is not formally distributed as a marketplace plugin, but the structural intent — one directory carries the orchestration vocabulary — is exactly what the ai/docs concept describes. Lesson for the reader: the orchestrator role is a structural property, not a packaging format; you can adopt it without ever publishing a plugin.

*Long-running maintenance.* The ai/docs concept of recurring repo hygiene is realized through slash-command-driven research, planning, implementation, and handoff phases. There is no autonomous cron loop; instead each maintenance arc is a human-triggered command that ends with a written artifact. The pattern matters because it shows long-running maintenance does not require a daemon-driven loop — a disciplined slash-command vocabulary plus a state-as-files convention is enough to keep the repo's narrative continuous across sessions.

#### Patterns Absent

*Hooks.* The ai/docs concept of a hooks layer — settings.json-declared lifecycle handlers that the harness fires deterministically — is not used here. The project succeeds without it because its enforcement surface is the approval gate plus inline command checklists; both run when the agent acts, so the deterministic-trigger guarantee that hooks provide is delegated to the approval channel instead. The lesson for an ai/docs reader is that the hooks concept solves a specific problem (guaranteed pre/post-action enforcement that memory cannot guarantee), and if you already have an out-of-band gate doing that job, the literal hooks artifact may be redundant.

*Skills.* The ai/docs concept of a skill — a self-contained, progressively-disclosed capability bundle keyed by a SKILL.md descriptor — is absent. All workflow capability lives in slash commands and subagent prompts instead. The project still gets the practical benefit the skills concept targets (capability is loaded only when invoked) because slash commands are themselves lazy-loaded by name. The reader's lesson is that the skill concept and the slash-command concept overlap in the progressive-disclosure dimension; choosing skills specifically buys richer metadata, scripts, and resource bundling, and you should adopt them when those affordances are needed, not as a default.

*AGENTS.md.* The ai/docs concept of AGENTS.md as a cross-tool agent-guidance manifest is not present. The harness leans on CLAUDE.md and per-agent prompt files instead. This is a useful demonstration that AGENTS.md becomes valuable mainly when multiple agent runtimes need to share guidance; a single-runtime project can route the same content through CLAUDE.md and agent definitions without losing fidelity.

*Path-scoped CLAUDE.md.* The ai/docs concept of nested CLAUDE.md files that activate when the agent enters a subtree is not exploited as a design tool here. Where multiple memory files exist, they function as auto-generated scaffolding rather than curated subtree guidance — a cautionary signal that path-scoped memory only pays off when each file is hand-tuned to the directory it governs; otherwise it dilutes the always-loaded context budget the smart-zone concept warns about.

*Ralph sentinels.* The ai/docs concept of Ralph-loop sentinel files — promise tags, progress files, completion flags that drive autonomous iteration — is absent. The "Ralph" name is reused here for a ticket-state-machine workflow that is human-stepped through slash commands. The lesson is that the sentinel mechanism is distinct from any naming convention — a reader should confirm that promise tags, progress files, and completion flags are present before treating a workflow as Ralph-driven, and should not feel obligated to adopt that vocabulary when human-driven phase commands cover the same iteration ground.

#### Notable Surprises

*The approval channel exposes exactly one MCP tool.* The ai/docs concept of MCP-as-progressive-disclosure usually imagines a server fanning out many tools. Here the entire MCP surface is a single permission-request tool; everything else is a Claude Code native that the gate wraps. This refines the progressive-disclosure concept: the smallest possible MCP surface is itself a form of disclosure discipline, achieved by making the gate, not the toolset, the unit of indirection.

*"Trust mode" still carries a back-pressure deadline.* The ai/docs concept of an approval-loop typically treats bypass flags as escape hatches. Here the bypass is itself time-bounded by a periodic expiry sweep, so even the escape hatch closes on a clock. This extends the human-in-the-loop concept by showing that back-pressure is not a binary on/off — it can be a deadline, which is a softer but still durable form of the same guarantee.

*Subagents are explicitly forbidden from critique.* The ai/docs concept of subagent roles typically includes a critic or advisor variant. The deliberate exclusion of critique from every read-only agent here pushes that concept in a different direction: the parent thread owns all judgement, the subagents own all retrieval. This is a non-obvious refinement of the context-firewall concept — it preserves bandwidth savings while keeping evaluation centralized, at the cost of giving up the parallel-critique pattern the ai/docs subagent-roles material describes.

#### Further Reading

For the always-loaded-memory and smart-zone concepts that the case study confirms, return to the ai/docs treatment of CLAUDE.md sizing and dead-context drag. For the subagent-as-context-firewall pattern, the ai/docs material on parallel research dispatch and agent-protocols expands the compressed-summary discipline observed here. For the approval-loop concept, see the ai/docs human-in-the-loop and tool-calling sections — they cover the same back-pressure shape from the agent side, where this case study covers it from the harness side. For the plugin-as-orchestrator concept, the ai/docs harness-engineering material describes the bundling expectations that a flat `.claude/` directory satisfies in spirit. For the absent hooks and skills patterns, the ai/docs sections on those artifacts explain when adopting them buys more than slash commands and approval gates already provide.

The graphify community label `HumanLayer Architecture` collects the structural nodes referenced throughout this case study and is the right entry point for readers who want to traverse the project's modules without a local checkout.

---

## Part II — Harness Engineering Reference Guide for LLM Agents

This part is a how-to for an LLM agent producing harness engineering structures in any project. Follow it top-down. Each section ends with primary-source citations.

### 1. Definition and Philosophy

A **harness** is everything around the model — the tools, files, prompts, hooks, subagents, memory, and observation surface that turn raw model capability into a reliable autonomous worker. **Harness engineering** is the iterative practice of fixing recurring agent failures structurally so the same mistake never recurs without engineering effort.

The harness has five components (`harness-engineering/skill-issue-harness-engineering-for-coding-agents.md:30-78`):

1. **Context Injection** — what reaches the model (CLAUDE.md, MCP tool descriptions, skill metadata, file contents, prior conversation).
2. **Control** — how the agent loop is driven (slash commands, state files, sentinel-driven loops like Ralph).
3. **Action** — what the agent can do (tool allowlist, MCP servers, shell capability scope).
4. **Persist** — what state survives the session (progress files, JSON state, git, structured note-taking).
5. **Observe-and-Verify** — what the harness checks autonomously (back-pressure hooks, typecheck, test runs, eval harnesses).

The unifying objective (`general-llm/research-context-engineering-comprehensive.md:36`): "find the smallest possible set of high-signal tokens that maximize the likelihood of some desired outcome."

### 2. Artifact Taxonomy

A canonical `harness-taxonomy.md` reference distinguishes three component classes. Use this taxonomy when designing artifacts in any project:

| Class | Purpose | Examples |
|-------|---------|----------|
| **Artifact** | Produces a durable file (PRD, plan, implementation, archived plan) | `<plugin>-prd`, `<plugin>-plan`, `<plugin>-implement` |
| **Advisory** | Read-only recommendation; no edits | `<plugin>-advisor`, `<plugin>-review`, `code-simplifier`, `docs-impact-agent` |
| **Utility** | Operational helper inside a workflow | `<plugin>-commit`, `<plugin>-pr`, `<plugin>-debug`, `<plugin>-verification-before-completion` |

Seven kinds of files implement these classes:

1. **Always-loaded memory** — `CLAUDE.md` / `AGENTS.md` (root + subdir hierarchies). Target <200 lines, ideally <60. Reserve for absolute project priorities.
2. **Path-scoped rules** — `.claude/rules/<name>.md` with frontmatter `paths: [...]`. Loaded when files matching those globs enter context.
3. **References** — `<plugin>/references/<name>.md`, ≤100 lines, mirror parity rule. Loaded JIT by skills via "Context Contract" sections.
4. **Skills** — `<plugin>/skills/<name>/SKILL.md` plus optional `references/`, `scripts/`, `assets/`. Three-tier progressive disclosure.
5. **Subagents** — `<plugin>/agents/<name>.md`. YAML frontmatter declares model, tools, maxTurns; body is the system prompt.
6. **Hooks** — `<plugin>/hooks/hooks.json` registers events; handler scripts live alongside. Four types: command, http, prompt, agent.
7. **CI evals** — deterministic prompt-contract checks (`scripts/<plugin>_prompt_eval.py` + `tests/<plugin>/prompt-cases.json` + GitHub workflow). Catch silent regressions in artifact contracts.

### 3. Always-Loaded Memory: `CLAUDE.md` / `AGENTS.md`

**Empirical baseline** (`general-llm/Evaluating-AGENTS-paper.md`): LLM-generated `AGENTS.md` files HURT performance and cost 20%+ more reasoning tokens. Human-written context files helped only ~4%.

**Constraints**:
- Aim for <200 lines, prefer <60. HumanLayer's CLAUDE.md is under 60 lines (`harness-engineering/skill-issue-harness-engineering-for-coding-agents.md:297`).
- Document **capabilities, not structure** (file paths rot; capabilities are durable). Source: `general-llm/a-guide-to-agents.md:62-72`.
- Place critical priorities at the very top — instructions ride the attention sink (`context-engineering/agents-md-is-a-liability-paddo.md:58-62`).
- Never include codebase overviews, file-tree dumps, or auto-generated content.

**Template** (recommended root `CLAUDE.md` shape):

```markdown
# <Project Name>

<one-sentence project description>

## Operating Priorities (in order)

1. **<Priority 1 name>** — <imperative one-liner with threshold or trigger>.
2. **<Priority 2 name>** — <imperative one-liner>.
3. **<Priority 3 name>** — <imperative one-liner>.
4. **<Priority 4 name>** — <imperative one-liner>.
5. **<Priority 5 name>** — <imperative one-liner>.

## Key Locations

- `<path>` — <one-line purpose>
- `<path>` — <one-line purpose>

## Workflow Entry Points

- `/<command>` — <one-line trigger>
```

For multi-package monorepos, place per-package `CLAUDE.md` files with package-specific guidance and rely on hierarchical lookup.

### 4. Path-Scoped Rules

Rules are conditional context. They load only when the agent reads a file matching the rule's path glob, removing them from the always-loaded budget.

**Frontmatter** (mandatory):

```yaml
---
paths: ["<glob1>", "<glob2>"]
description: "<one-line trigger description>"
---
```

**Use cases**:
- Conventions for a specific artifact class (`.claude/PRPs/plans/**` → planning conventions).
- Conventions for a specific code area (`packages/api/**/*.ts` → API conventions).
- Hook conventions (`.claude/hooks/**` → JSON-in/JSON-out contract).

**Body**: prescriptive, terse, citation-anchored. Typical length 30-80 lines. Reference the policy file in `references/` rather than restating it.

### 5. References (Policy Layer)

References are the deduplicated source of truth for cross-cutting policies. Skills and agents link to them via Context Contract sections instead of restating the policy. This gives a single edit point for shared rules.

**Conventions** (canonical `reference-conventions.md` rule):
- ≤100 lines per file.
- Mirror parity: `<plugin>/references/<x>` and `.claude/references/<x>` must be byte-identical.
- Deletion test: if you delete the file, every consumer should fail an explicit error referencing it (no silent skip).

**Five canonical references** (copy structure verbatim into new projects):

1. **`harness-taxonomy.md`** — three artifact classes (artifact/advisory/utility) with allowed tools and behaviors.
2. **`context-budget-policy.md`** — Smart-Zone thresholds (e.g., 40% normal, 70% requires compaction or handoff); brief size limits per phase (discovery ≤50, execution ≤30, validation ≤20 lines). Cite Levy et al. ACL 2024.
3. **`execution-policy.md`** — four delegation modes:
   - **Stay inline** — short deterministic work, <5 file reads, no parallelism gain.
   - **Isolated subagent** — noisy exploration; return compact brief, drop transcript.
   - **Parallelize subagents** — only when scopes share no files / state / ordering.
   - **Repo-local eval harness** — deterministic batch verification scripted in repo.
4. **`artifact-lifecycle.md`** — `.claude/PRPs/` paths and naming (`<NN>-<slug>.prd.md`, `<NN>-<slug>.plan.md`, `archived/<NN>-<slug>.plan.md`).
5. **`agent-prompt-style.md`** — required structure for advisory/analyst agent prompts: CRITICAL one-job declaration → DO NOT boundaries → Core Responsibilities → Strategy → Output Format.

### 6. Skills: User-Invocable Workflows

A **skill** is a Markdown file with YAML frontmatter that the agent invokes via slash command (Claude Code) or context match (other harnesses). Skills implement workflows that are reusable across sessions and projects.

**Frontmatter contract** (`shared/skills-standard/agentskills-specification.md:23-200`):

```yaml
---
name: <kebab-case-name>           # ≤64 chars, lowercase + hyphens only
description: |                    # ≤1024 chars
  <imperative trigger description that carries the entire routing burden>
license: <SPDX-id>                # optional
allowed-tools: [Read, Grep, ...]  # optional restriction
metadata:                         # optional
  enforcement: instructor|helper  # for skills-over-MCP semantics
  context: fork                   # run in isolated subagent context
---
```

**Description-writing rules** (`shared/skills-standard/agentskills-optimizing-descriptions.md:22-29`):
- Imperative phrasing: "Use this skill when …".
- Focus on user intent and triggers, not internal mechanics.
- "Err on the side of pushy" — list contexts including ones not naming the domain (e.g., "code review" should also trigger on "look at this PR", "what's wrong here").
- Keep description self-contained — the SKILL.md body is loaded only on activation.

**Three-tier progressive disclosure** (`shared/skills-standard/agentskills-specification.md:241-249`):
- **Metadata** (~100 tokens, always loaded) — `name` + `description` only.
- **Instructions** (<5000 tokens, loaded on activation) — the SKILL.md body. Target <500 lines (≤400 recommended).
- **Resources** (loaded only when explicitly referenced from the body) — `references/`, `scripts/`, `assets/`.

**Body structure** (synthesized from `shared/skills-standard/agentskills-best-practices.md:163-262`):

```markdown
# <Skill Name>

<one-sentence purpose>

## Context Contract

This skill operates under the following shared policies:
- `references/context-budget-policy.md` — brief size limits per phase
- `references/execution-policy.md` — delegation modes
- `references/<other>.md` — <reason>

## When to Use

- <trigger 1>
- <trigger 2>

## When NOT to Use

- <anti-pattern 1>
- <anti-pattern 2>

## Workflow

### Phase 1: <name>
1. <step>
2. <step>

### Phase 2: <name>
…

## Output Format

<exact artifact path/template>

## Gotchas

- <surprising failure mode 1 — what to do instead>
- <surprising failure mode 2>

## Validation

<how to verify the artifact is correct before closing>
```

**Critical practices**:
- "Procedures over declarations" — teach how to approach a class of problems, not what to produce for one instance (`shared/skills-standard/agentskills-best-practices.md:144-161`).
- "Provide defaults, not menus" — pick one default tool/library; mention alternatives briefly (`agentskills-best-practices.md:127-143`).
- "Match specificity to fragility" — prescriptive for fragile/destructive ops; flexible (with stated rationale) for tasks that tolerate variation.
- **Eval-driven optimization** — for any skill with discoverability concerns, write 8-10 should-trigger queries and 8-10 near-miss should-not-trigger queries, run them, iterate the description until trigger rate is ≥90% on positive set and ≤20% on negative set.

### 7. Subagents: Context Firewalls

Subagents fork a clean context window for one bounded job and return a compacted brief. Their power is **context isolation, not specialization** (`harness-engineering/skill-issue-harness-engineering-for-coding-agents.md:388-394`). "Frontend agent / backend agent / QA agent" is an anti-pattern.

**Subagent definition** (`<plugin>/agents/<name>.md`):

```markdown
---
name: <kebab-case>
description: |
  <one-line role description with "Use proactively when X" trigger>
model: <opus|sonnet|haiku>
tools: [Read, Grep, Glob, Bash, Agent, Skill]
maxTurns: <integer>           # critical — bounds runaway loops
effort: <low|medium|high|max> # optional
---

# <Agent Name>

CRITICAL: Your one job is to <single sentence>.

DO NOT:
- <boundary 1>
- <boundary 2>

## Core Responsibilities

1. <responsibility>
2. <responsibility>

## Strategy

<how to approach the job — phase steps, decision rules>

## Output Format

<exact format the parent will consume — citation-rich, ≤<N> lines>

## Approval Criteria

The work is complete when:
- <criterion>
- <criterion>
```

**Model selection** (`analysis/analysis-research-subagent-best-practices.md:99-149`):
- **Haiku** — exploration, mechanical work (file location, simple greps).
- **Sonnet** — default for analysis, review, planning.
- **Opus** — architecture, advisor roles, judgment-heavy work; reserve carefully due to cost.

**Anti-patterns** (`analysis/analysis-research-subagent-best-practices.md:155-170`):
- Aggressive "CRITICAL" prompts in many fields — over-triggers on Opus 4.6+.
- Vague descriptions — agents won't be selected.
- No `maxTurns` — runaway loops.
- God agents that try to do everything.
- Too many subagents loaded — each description costs ~2% of attention budget.
- No output format — parent can't reliably consume the result.

**Output format rules**:
- Always cite `path:line` so the parent can re-fetch detail.
- Stay under a token budget (research subagents typically target 30-50 lines for execution briefs, ≤80 for discovery).
- Surface uncertainty explicitly (confidence ≥80% rule from `analysis/analysis-research-subagent-best-practices.md:138-149`).

**Dispatch patterns**:

| Mode | When | Effect |
|------|------|--------|
| Inline | <5 file reads, deterministic | Stays in main context |
| Single isolated subagent | Noisy exploration | Compacted brief returns; transcript discarded |
| Parallel subagents | Multiple independent scopes | Send all dispatches in one message; conflict-free |
| Agent Teams (peer-to-peer) | Need debate, mutual challenge, dependency tracking | Mailbox + shared task list; cost scales linearly |
| MCP-launched subagent (escape hatch) | Subagent needs to spawn its own subagents | Risks "telephone game" of context drift; use sparingly |

**Anti-nesting rule**: subagents cannot spawn subagents directly. The MCP-launch escape hatch exists but introduces telephone-game drift — keep nesting depth ≤2.

### 8. Hooks: Deterministic Rails

Hooks convert behavioral instructions into deterministic enforcement, removing them from the LLM's attention budget while ensuring absolute compliance.

**Hook types** (`analysis/analysis-automate-workflow-with-hooks.md:22-30`):
- **command** — shell script
- **http** — POST to a URL
- **prompt** — single-turn LLM call
- **agent** — full subagent verifier

**Lifecycle events** (Claude Code, 22 in total — `analysis/analysis-automate-workflow-with-hooks.md:32-74`):

| Category | Events |
|----------|--------|
| Session | `SessionStart` (matchers: startup/resume/clear/compact), `SessionEnd` |
| Agentic loop | `UserPromptSubmit`, `PreToolUse` (can block), `PermissionRequest`, `PostToolUse`, `PostToolUseFailure` |
| Subagent | `SubagentStart`, `SubagentStop` |
| Compaction | `PreCompact`, `PostCompact` |
| Control | `Stop`/`StopFailure`, `TaskCompleted`, `TeammateIdle` |
| Configuration | `ConfigChange`, `InstructionsLoaded` |
| Worktree | `WorktreeCreate`, `WorktreeRemove` |
| MCP | `Elicitation`, `ElicitationResult` |

**Communication contract** (`analysis/analysis-automate-workflow-with-hooks.md:75-93`):
- stdin = JSON describing the event.
- stdout = JSON only (parsed by the harness).
- stderr = human-readable messages.
- Exit code: `0` allow; `2` block (stderr is fed back to the agent); other = allow with stderr in verbose.

**`hooks.json` template**:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "<regex>",
        "hooks": [
          {"type": "command", "command": ".claude/hooks/<script>.sh"}
        ]
      }
    ]
  }
}
```

**Canonical use cases**:
- **Back-pressure on Stop**: run typecheck + tests in parallel; success silent, failures exit 2 → agent re-engages to fix (`harness-engineering/skill-issue-harness-engineering-for-coding-agents.md:639-681`).
- **Loop continuation**: state file + sentinel pattern (Ralph). Hook reads `.claude/<name>.state.md`, injects next prompt, terminates when sentinel `<promise>COMPLETE</promise>` appears.
- **Artifact validation**: Stop hook verifies generated file has required sections (six-section schema in `<plugin>-research-team-stop.sh:32-40`).
- **Approval injection**: PermissionRequest hook posts to Slack/HumanLayer; blocks until human responds.

**Pitfalls** (`analysis/analysis-automate-workflow-with-hooks.md:138-194`):
- Infinite Stop-hook loop — must check `stop_hook_active` field in stdin.
- Shell profile `echo` poisoning stdout — always source shells with `--no-rcs` or write JSON via `printf` only.
- Case-sensitive matchers — `pretooluse` won't match `PreToolUse`.
- `PermissionRequest` doesn't fire in headless `-p` mode.
- `PostToolUse` cannot undo a tool call — for prevention, use `PreToolUse`.
- `"allow"` decision from `PreToolUse` does NOT override permission deny rules.

**Hook script skeleton**:

```bash
#!/usr/bin/env bash
set -euo pipefail
input="$(cat)"
# Parse JSON via jq, never inline regex
flag=$(printf '%s' "$input" | jq -r '.tool_name // empty')
if [[ "$flag" == "DangerousTool" ]]; then
  printf '{"decision":"block","reason":"<why>"}\n'
  echo "Blocked dangerous tool" >&2
  exit 2
fi
printf '{"decision":"allow"}\n'
```

### 9. Long-Running Context Maintenance

Long-running agents (Ralph loops, multi-day plans, large refactors) require explicit context-maintenance machinery. The single goal is: **keep utilization in the smart zone (<40%) at every turn**, even after thousands of tool calls.

**Empirical foundations**:
- All 18 models tested by Chroma degrade with context length, at every increment, not just near the limit (`general-llm/research-context-rot-and-management.md:30-41`).
- Levy et al. ACL 2024: 3K filler tokens drop reasoning accuracy from 0.92 → 0.68 even when filler is duplicate of useful content (`research-context-rot-and-management.md:130-146`).
- Lost-in-the-Middle (Liu et al. TACL 2023): 10-20% recall drop for mid-context information; place critical instructions at start AND end, queries last (up to 30% improvement per Anthropic) (`research-context-rot-and-management.md:104-117`).
- IFScale 500-instruction ceiling: best frontier model scored 68% at 500 instructions (`context-engineering/agents-md-is-a-liability-paddo.md:21-31`).

**Anthropic's three strategies** (`general-llm/research-context-rot-and-management.md:236-251`):

| Strategy | Mechanism | When |
|----------|-----------|------|
| **Compaction** | Summarize at limit, reinit fresh context with summary + recent files | When utilization >70% and work must continue in current session |
| **Structured Note-Taking** | Persist progress/state to files outside context | Always, for any multi-phase or multi-day work |
| **Sub-Agent Architectures** | Spawn subagent for noisy work; receives compacted brief | Whenever a phase will read >5 large files or run >5 tool calls |

**Frequent Intentional Compaction (FIC)** (`agentic-engineering/research-plan-implement-rpi.md:23-29,150-160`): each phase starts at 10-15% utilization with a compacted artifact carried over. Don't wait for forced compaction — design phase boundaries so compaction is the natural transition.

**Initializer + Coding Agent pattern** (`claude/effective-harnesses-long-running-agents.md:23-110`):

A long-running task uses two roles:

1. **Initializer Agent** (run once, fresh context): produces
   - `init.sh` — a script that brings the dev environment to a runnable state.
   - `claude-progress.txt` — natural-language progress journal (append-only).
   - `feature_list.json` — structured backlog. Each entry has `id`, `description`, `acceptance_criteria`, `passes: false`.
   - Initial `tests.json` (or equivalent test manifest).

2. **Coding Agent** (run repeatedly, fresh context per iteration):
   - Reads `claude-progress.txt` (last N entries) + `feature_list.json` for next item.
   - Picks one feature with `passes: false`.
   - Implements + tests end-to-end.
   - Sets `passes: true` only when tests run green.
   - Commits work; appends one paragraph to `claude-progress.txt`.

This pattern eliminates the four documented failure modes:
- Declaring victory too early (gated by `passes: true` + test evidence).
- Leaving environment dirty (`init.sh` resets every iteration).
- Marking features done without testing (acceptance criteria checked).
- Wasting time figuring out how to run the app (`init.sh` handles it).

**Phase-based loading** (`context-engineering/progressive-disclosure-ai-agents.md:64-96`):
- Each phase loads only what it needs and explicitly compacts before the next phase begins.
- Phase artifacts (research_doc.md, implementation_plan.md, progress.md) become the next phase's input — raw transcripts are discarded.

**Trajectory rule**: after two failed corrections on the same problem, `/clear` and start fresh — don't keep correcting (`general-llm/research-context-rot-and-management.md:148-153`). Bad-correction-bad-correction loops reinforce failure.

**RPI Workflow** (`agentic-engineering/research-plan-implement-rpi.md:30-34`): leverage hierarchy — bad research yields 1000s of bad lines; bad plan yields 100s; bad code yields 1. Spend disproportionate effort upstream.

```
Phase 1: Research (subagents) → research_brief.md (50 lines)
       ↓ (fresh context)
Phase 2: Plan (subagent + critic) → plan.md (with phases, validation gates)
       ↓ (fresh context)
Phase 3: Implement (per-phase subagents) → code + tests
       ↓
Phase 4: Verification gate (Iron Law)
       ↓
Phase 5: Commit + PR
```

### 10. Verification Before Completion (Iron Law)

The Iron Law: **NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE.**

Source: a `<plugin>-verification-before-completion` skill, validated against `harness-engineering/skill-issue-harness-engineering-for-coding-agents.md:683-696` (back-pressure principle).

**Mechanism**: every "this is done" claim must map to a verification command whose fresh output is included in the response. The skill maintains a `claim → requires → not_sufficient` table:

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| "All tests pass" | `npm test` output with `0 failures` from this run | Memory of an earlier run |
| "TypeScript compiles" | `tsc --noEmit` output with no errors from this run | "I didn't change types" |
| "Linter is clean" | `eslint .` output with `0 problems` | "The change looks fine" |
| "Migration applied" | `db:migrate:status` output | Migration file exists |

**Red-flag phrases that trigger the gate**: "should work", "probably fine", "I didn't change that", "tests should pass", "no obvious issues".

**Rationalization-prevention** rules: if the agent finds itself thinking "this is too small to verify" or "I'd be testing things I didn't change", it must verify anyway. The cost of one extra check is bounded; the cost of declaring done falsely is unbounded.

This skill is invoked as a Phase 4.6 gate in `<plugin>-implement` before plan archival. Make any equivalent workflow gate completion the same way.

### 11. Critic / Review Patterns

**Plan-Critic** (`agents/plan-critic.md`): a dedicated subagent that validates consolidated findings before the artifact-writer subagent runs. Its output is a verdict `PROCEED|REVISE` with critical gaps / blind spots / weak assumptions.

The plan-critic includes a **Skepticism Safeguard** clause: never auto-agree with the consolidated findings. Always look for what's missing, what's assumed without evidence, what's been over-confidently asserted. Its role is to be the friction.

When to use:
- Before writing any artifact whose downstream work cost is >100x the artifact write cost (PRDs, plans, large refactor designs).
- The recommended pattern gates this at Phase 5.5 / 6.5 of `<plugin>-plan` and `<plugin>-prd` for MEDIUM/HIGH-complexity features.

**Advisor pattern** (`<plugin>-advisor`): a dual-mode advisory that detects whether a native `advisor` tool is present in the harness. If yes, forward the full conversation; if no, fall back to a `<plugin>-advisor` subagent with a composed context summary.

The advisor speaks **before substantive work** (writing, deciding, committing). It does not implement. Output target: ≤100 words, enumerated steps. This forces the orchestrator to externalize its plan and receive a second opinion before context fills up.

**Review-Agents** (`<plugin>-review-agents`): aspect-specialists run in parallel on a PR — `code-reviewer` (always) plus `docs-impact-agent`, `pr-test-analyzer`, `silent-failure-hunter`, `type-design-analyzer`, `code-simplifier`, `comment-analyzer` selected by `--aspects`.

**Cross-Model Review** (`harness-engineering/harness-engineering.md:79-81`): use a different model family for critic roles. Shared blind spots between two instances of the same model are systemic; cross-family critique catches more.

### 12. Agent Communication Protocols

**MCP** (`mcp/mcp-specification.md`): the universal interface for connecting agents to tools, resources, prompts, elicitations.

Practical guidance:
- In real-world harnesses, MCP servers are primarily for tools (`harness-engineering/skill-issue-harness-engineering-for-coding-agents.md:299-307`). Resources/prompts/elicitations are not consistently supported by clients yet.
- Tool descriptions go into the system prompt and consume attention budget — keep tool count tight.
- Never connect untrusted MCP servers — they are a prompt-injection vector.
- When an MCP server duplicates a CLI well-represented in training data, prompt the agent to use the CLI directly (composability with `grep`/`jq`/`awk` is a major advantage).
- Use `tool_search` (Anthropic experimental) for progressive disclosure of tools — JIT load definitions instead of loading all at once.

**A2A** (Google): peer-to-peer task delegation between agents from different organizations. Includes Secure Passport Extension and Traceability Extension.

**ACP** (IBM Research): Agent Communication Protocol; merged conceptually into A2A.

**ANP**: decentralized identity for agents; mostly speculative as of 2026.

**Programmatic Tool Calling** (`tool-calling/programmatic-tool-calling-claude-api.md:82-90`): the LLM generates orchestration code; sandbox runs; only the final result returns. N round-trips → 2 fixed; ~80% token savings.

### 13. CI Eval Harness for Artifacts

Artifacts (skills, agents, hooks, references) carry implicit contracts. Without automated checks, contract drift goes silent. Implement a deterministic prompt-eval:

`scripts/<plugin>_prompt_eval.py` runs cases from `tests/<plugin>/prompt-cases.json`:

```json
[
  {
    "name": "skill-mentions-context-contract",
    "files": ["plugins/<plugin>/skills/*/SKILL.md"],
    "must_contain": ["## Context Contract"]
  },
  {
    "name": "mirror-parity-skills",
    "type": "mirror_parity",
    "pairs": [
      ["plugins/<plugin>/skills/<x>", ".claude/skills/<x>"]
    ]
  },
  {
    "name": "hook-six-section-schema",
    "files": [".claude/hooks/<x>.sh"],
    "type": "regex",
    "pattern": "^## (Research Question|Research Question Decomposition|Team Composition|Research Tasks|Team Orchestration Guide|Acceptance Criteria)"
  }
]
```

Wire into CI:

```yaml
# .github/workflows/<plugin>-prompt-evals.yml
on: [pull_request, push]
jobs:
  evals:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python scripts/<plugin>_prompt_eval.py
```

Failures block merge. This is the structural fix for "skills drift out of compliance with the reference layer over time."

### 14. Plugin Packaging (Claude Code Plugin Standard)

Wrap your harness in a plugin so it ships as a single installable unit.

**Manifest** (`<plugin>/.claude-plugin/plugin.json`):

```json
{
  "name": "<plugin-name>",
  "version": "<semver>",
  "description": "<one-line description>"
}
```

**Marketplace** (`.claude-plugin/marketplace.json` at repo root):

```json
{
  "name": "<marketplace-name>",
  "owner": "<owner>",
  "plugins": [
    {
      "name": "<plugin-name>",
      "path": "plugins/<plugin-name>"
    }
  ]
}
```

**Mirror parity rule**: keep `.claude/<artifact>/<x>` byte-identical to `plugins/<plugin>/<artifact>/<x>` for local development. Enforce via CI eval (mirror-parity case above).

### 15. Orchestration Recipes

#### Recipe A: Research → Plan → Implement (RPI)

```
User: /<plugin>-prd <topic>
  ↓
<plugin>-prd skill (artifact)
  Phase 0: <plugin>-advisor gate
  Phase 1: parallel exploration (codebase-explorer × N, web-researcher)
  Phase 2: phase-brief compression (each subagent returns ≤50 lines)
  Phase 3: synthesis (in main context)
  Phase 4: plan-critic gate (PROCEED|REVISE)
  Phase 5: writer subagent (fresh context) writes prd.md
  Phase 6: archive at .claude/PRPs/prds/<NN>-<slug>.prd.md
  ↓
User: /<plugin>-plan <prd>
  ↓
<plugin>-plan skill (artifact, same shape)
  Output: .claude/PRPs/plans/<NN>-<slug>.plan.md
  ↓
User: /<plugin>-implement <plan>
  ↓
<plugin>-implement skill (artifact)
  For each phase in plan:
    - Subagent implements phase
    - Run tests + typecheck (back-pressure hook)
    - <plugin>-commit
  Phase 4.6: <plugin>-verification-before-completion (Iron Law gate)
  Archive plan
  ↓
User: /<plugin>-pr
```

#### Recipe B: Autonomous Loop (Ralph)

```
User: /<plugin>-ralph <plan>
  ↓
Initialize state file .claude/<plugin>-ralph.state.md with frontmatter:
  iteration: 0
  max_iterations: 50
  plan_path: <path>
  ↓
Hook (Stop event) detects state file:
  Reads next-iteration prompt
  Increments iteration counter
  Injects prompt into next turn (via JSON exit code 2 + reason)
  ↓
Agent runs iteration; on completion checks plan acceptance criteria
  ↓
If acceptance met → write <promise>COMPLETE</promise> sentinel
  Hook detects sentinel → terminates loop, archives state
  ↓
If iteration count exhausted → terminate, mark FAILED
```

#### Recipe C: Multi-Agent Research Team

```
User: /<plugin>-research-team <question>
  ↓
<plugin>-research-team skill (artifact)
  Phase 1: decompose question into sub-questions (≤7)
  Phase 2: assign teammates per sub-question (skill-matched, model-matched)
  Phase 3: write team plan with the six required sections:
    ## Research Question
    ## Research Question Decomposition
    ## Team Composition
    ## Research Tasks
    ## Team Orchestration Guide
    ## Acceptance Criteria
  ↓
Hook (Stop event, <plugin>-research-team-stop.sh) validates the six sections
  Missing section → exit 2 with feedback → agent fixes
  All present → allow exit
```

#### Recipe D: Code Review (parallel critics)

```
User: /<plugin>-review-agents <pr-url> --aspects <list>
  ↓
<plugin>-review-agents skill (advisory)
  Always: code-reviewer subagent
  If --aspects includes "tests": pr-test-analyzer
  If --aspects includes "docs": docs-impact-agent
  If --aspects includes "errors": silent-failure-hunter
  If --aspects includes "types": type-design-analyzer
  If --aspects includes "clarity": code-simplifier
  If --aspects includes "comments": comment-analyzer
  ↓
Run all selected subagents in parallel (one message, N tool calls)
  ↓
Synthesize findings into a single PR comment
  Confidence ≥80% only; consolidate similar issues
  ↓
Post via gh CLI
```

### 16. Bringing It Together: Step-by-Step for a New Project

When asked to produce a harness engineering structure for a new project, follow this exact sequence:

1. **Read the project's existing `CLAUDE.md` / `AGENTS.md`** if any. Note size, contradictions, dead instructions.
2. **Create the priorities.** Five top-level rules in the new `CLAUDE.md`. Order by frequency of relevance and severity of failure mode. Target 30-60 lines.
3. **Build the references layer.** Copy the five canonical references (`harness-taxonomy`, `context-budget-policy`, `execution-policy`, `artifact-lifecycle`, `agent-prompt-style`) and customize thresholds/paths to the project. Mirror to `.claude/references/`.
4. **Define path-scoped rules** for each artifact class and code area. Each rule ≤80 lines, references the relevant policy in `references/`.
5. **Design the workflow skills.** Identify the 3-7 user-invocable workflows that map to the project's recurring tasks (e.g. PRD, plan, implement, review, debug). For each:
   - Write the YAML frontmatter (description carries trigger burden).
   - Decompose into phases with explicit subagent dispatches and brief size budgets.
   - Add Context Contract section linking the references.
   - Cap SKILL.md at 400 lines.
6. **Design the subagents.** One per role; isolated context; tools-minimal; output format strict; `maxTurns` set. Cover at minimum: explorer (haiku), analyst (sonnet), reviewer (sonnet), advisor (opus).
7. **Add hooks** for the deterministic rails:
   - Stop hook: typecheck + tests (back-pressure).
   - Stop hook: artifact validation (e.g. six-section schema for research plans).
   - Optional: Ralph-style loop hook if any autonomous workflow is in scope.
   - Optional: PermissionRequest hook for human-in-the-loop approvals.
8. **Add the verification gate.** Either reuse `<plugin>-verification-before-completion` or implement an equivalent with the claim→requires→not-sufficient table customized for the project's verification commands.
9. **Add CI eval harness.** `scripts/<plugin>_prompt_eval.py` + `tests/<plugin>/prompt-cases.json` + `.github/workflows/<plugin>-prompt-evals.yml`. Cover: contract strings, mirror parity, hook schemas.
10. **Package as plugin.** `plugin.json` + `marketplace.json`. Verify mirror parity locally before tagging a release.
11. **Run a graphify pass** on the project's docs after each major harness revision (`harness-kb <docs-dir> --update`). Use the resulting god-nodes and surprising-connections lists as a quality signal: if the graph shows fragmented communities or low betweenness, the docs need cross-linking.

### 17. Quality Heuristics (use as a self-check)

A harness is well-engineered when:

- The always-loaded memory is <60 lines and the agent never needs to re-read it.
- Path-scoped rules load only when relevant files enter context.
- Skills have <500-line SKILL.md bodies; references handle policy.
- Subagents return <80-line briefs with `path:line` citations.
- Stop hooks run typecheck + tests on every completion claim.
- A verification skill blocks completion until commands have run fresh.
- A plan-critic agent gates artifact writes for medium/high-complexity work.
- Mirror parity is enforced by CI eval.
- A graphify pass on the project's docs places the harness's core abstractions among the god nodes (proof the docs reflect the harness shape).

A harness is failing when:

- The agent reads files repeatedly because path scoping is wrong.
- Skills duplicate policy from `references/`.
- Subagents return 5K-token transcripts instead of compacted briefs.
- Stop hooks are missing or async — failures pollute the next iteration.
- Plans are written without a critic gate.
- The graphify report shows >180 isolated nodes (≤1 connection) — the docs are fragmented.

---

## Code References

### `ai/docs/` — Primary Sources

**Harness engineering:**
- `ai/docs/harness-engineering/skill-issue-harness-engineering-for-coding-agents.md:30-78` (components), `:80-104` (engineering principle), `:204-240` (subagents), `:268-298` (AGENTS.md research), `:297` (HumanLayer CLAUDE.md size), `:299-336` (MCP), `:333-356` (CLI vs MCP), `:358-388` (skills as instructors/helpers), `:382-388` (distribution), `:388-394` (subagent context-not-roles), `:494-528` (citation-rich briefs), `:540-617` (anti-nesting escape), `:639-681` (Stop hook), `:683-696` (back-pressure), `:704-718` (don't pre-design)
- `ai/docs/harness-engineering/harness-engineering.md:24-35` (Five Pillars), `:37-44` (Smart Zone), `:55-58` (MCP roadmap), `:62-64` (subagent firewall), `:74-77` (review left), `:79-81` (cross-model review), `:95` (Golden Rule), `:113-117` (MCP principles), `:119-122` (MCP vs A2A)
- `ai/docs/harness-engineering/harnessengineering-building-the-operating-system-for-autonomous-agents.md` (long-form synthesis)
- `ai/docs/claude/effective-harnesses-long-running-agents.md:23-110` (Initializer + Coding Agent)
- `ai/docs/agentic-engineering/research-plan-implement-rpi.md:23-34,150-160` (RPI + FIC)
- `ai/docs/agentic-engineering/agentic-software-modernization-markus-harrer.md:46-55,99-102` (critic loop, leverage)
- `ai/docs/human-layer-project/humanlayer-repository-analysis.md` (concrete instance)

**Context engineering:**
- `ai/docs/general-llm/research-context-engineering-comprehensive.md:36` (definition), `:32,82-90` (English dominance), `:64-75` (whitespace)
- `ai/docs/general-llm/research-context-rot-and-management.md:21-27` (causes), `:30-41` (Chroma), `:74-80` (CLAUDE.md size), `:104-117` (Lost-in-Middle), `:130-146` (more tokens), `:148-153` (/clear after 2 corrections), `:160-167` (stale docs), `:236-273` (Anthropic strategies + table), `:323-332` (multi-turn refinement)
- `ai/docs/context-engineering/agents-md-is-a-liability-paddo.md:21-31,44-51,53-62` (IFScale, Smart Zone, attention sinks)
- `ai/docs/context-engineering/progressive-disclosure-ai-agents.md:64-108` (four patterns + trigger system)
- `ai/docs/context-engineering/shedding-dead-context-ryan-spletzer.md:1-78` (RAM analogy)
- `ai/docs/context-engineering/advanced-context-engineering-coding-agents-dev.md:67-128` (trajectory, dumb zone, subagent-as-context-control)
- `ai/docs/general-llm/Evaluating-AGENTS-paper.md` (ETH study)
- `ai/docs/long-context-research/lost-in-the-middle-acl.md` (primary)
- `ai/docs/general-llm/a-guide-to-agents.md:62-72` (capabilities not structure)

**Subagents:**
- `ai/docs/analysis/analysis-research-subagent-best-practices.md:23-329` (full distillation)
- `ai/docs/analysis/analysis-creating-custom-subagents.md`
- `ai/docs/analysis/analysis-claude-orchestrate-of-claude-code-sessions.md:1-274` (Agent Teams)
- `ai/docs/claude-code/subagents/creating-custom-subagents.md`
- `ai/docs/claude-code/subagents/claude-orchestrate-of-claude-code-sessions.md`
- `ai/docs/general-llm/subagents/research-subagent-best-practices.md`

**Skills:**
- `ai/docs/shared/skills-standard/agentskills-specification.md:23-249` (full spec)
- `ai/docs/shared/skills-standard/agentskills-best-practices.md:48-262`
- `ai/docs/shared/skills-standard/agentskills-optimizing-descriptions.md:22-167`
- `ai/docs/shared/skills-standard/agentskills-evaluating-skills.md`
- `ai/docs/shared/skills-standard/agentskills-using-scripts.md`
- `ai/docs/claude-code/skills/extend-claude-with-skills.md`
- `ai/docs/claude-code/skills/research-claude-code-skills-format.md`

**Hooks:**
- `ai/docs/analysis/analysis-automate-workflow-with-hooks.md:14-194` (full distillation)
- `ai/docs/claude-code/hooks/claude-hook-reference-doc.md` (authoritative reference)
- `ai/docs/claude-code/hooks/automate-workflow-with-hooks.md` (practical guide)
- `ai/docs/cursor/hooks/hooks-guide.md`

**Agent protocols:**
- `ai/docs/mcp/mcp-specification.md` (authoritative)
- `ai/docs/mcp/skills-over-mcp-meeting-notes-2248.md:38-124`
- `ai/docs/agent-protocols/architectural-paradigms-advanced-agentic-systems.md:85-98`
- `ai/docs/tool-calling/programmatic-tool-calling-claude-api.md:23-90`

**Spec-Driven Development:**
- `ai/docs/spec-driven-development/spec-driven-development-main.md:14-94`

**Prompting / Structured Outputs:**
- `ai/docs/claude/prompting-best-practices.md:11-117`
- `ai/docs/structured-outputs/anthropic-strict-tool-use.md:7-145`

### Knowledge Graph

- `graphify-out/GRAPH_REPORT.md` — full report, communities, god nodes
- `graphify-out/graph.html` — interactive visualization
- `harness-kb graph` (bundled graph) — raw graph data for programmatic queries
- `graphify-out/manifest.json` — corpus snapshot for incremental `--update`

---

## Architecture Insights

1. **Harness engineering = operationalized context engineering.** Every artifact (CLAUDE.md, rules, skills, subagents, hooks, references, evals) is a structural lever for keeping context in the smart zone. The five operating priorities (Smart Zone <40%, Harness-First, Subagent Isolation, Artifact-First, Progressive Disclosure) are coherent because they all converge on this thesis.

2. **The three-strategy frame is universal.** Anthropic's Compaction + Structured Note-Taking + Sub-Agent Architectures appears in every primary source — `effective-harnesses-long-running-agents.md`, `research-plan-implement-rpi.md`, `harness-engineering.md`, `research-context-rot-and-management.md`. Long-running execution = applying these three at every phase boundary.

3. **Progressive disclosure is the cross-cutting principle.** It appears as the top god node in graphify (20 edges) because it's the answer to four different problems: AGENTS.md size limits, skill discoverability, MCP tool overload, multi-phase context budgeting. The same mechanism solves all four.

4. **Subagent is for context isolation, not specialization.** Most-cited correction across the corpus (Dex Horthy, anti-pattern lists). When a project's harness has "frontend-engineer" / "backend-engineer" / "qa-engineer" subagents, it's mis-architected — those are roles for humans, not context budgets for agents. The lean-shell case study illustrates the alternative: a small set of read-only, same-shape information-retrieval agents, none scoped by domain (see Case Study).

5. **Verification + critic gates compound.** A `plan-critic` gates artifact writes (PROCEED|REVISE) and a `<plugin>-verification-before-completion` gates completion claims. Both make the agent prove rather than assert. Without these gates, every other harness improvement leaks because the agent will over-state completion. An out-of-band variant of the same idea — a daemon-mediated approval channel that blocks every tool call until a human decides — collapses both gates into one (see Case Study).

6. **Mirror parity + CI evals make harness drift detectable.** A deterministic prompt-eval script (contract strings, mirror parity for every plugin/local pair, hook section schemas) is the structural fix for "we updated the plugin but forgot the local mirror" — it surfaces drift on every PR. Any harness project at non-trivial scale needs equivalent CI.

7. **Graph-as-quality-signal.** Running graphify on the docs is a cheap audit of harness coherence. God nodes should reflect the project's core abstractions; high betweenness should sit on the cross-cutting principles; surprising connections should map to the harness's intended bridges (e.g. RPI ↔ Phase-Based Loading). Fragmented communities or stranded nodes mean the docs aren't reflecting the harness shape.

8. **The recommended harness build-out arc is generalizable.** In sequence: (a) extract policy to references; (b) gate writes with critic; (c) gate completion with verification; (d) consult advisor before substantive work; (e) lock contracts with CI evals. Apply this five-step arc to any harness that has skills/agents but lacks discipline.

9. **Two equilibria exist: heavy-stack vs lean-shell.** The canonical pattern (Section "Canonical Harness Components") expects skills + hooks + references + critic + verification + CI evals. A lean-shell instantiation skips skills, hooks, AGENTS.md, and critic agents — instead pushing back-pressure into a daemon, externalizing state to a git-submodule, and forking fresh sessions per workflow hop. Both implement the same operating priorities. Choose based on whether the harness is a single-team developer aid (heavy stack pays for itself) or a productized human-in-the-loop platform (lean shell + daemon scales the gating). See Case Study for a worked example of the lean-shell branch.

---

## Related Research

Future related work could include:

- A controlled comparison of "with `plan-critic`" vs "without `plan-critic`" outcomes on the same plan-writing task.
- A study of context-budget effectiveness when the always-loaded memory is diluted by uncurated boilerplate. At what curation ratio does the dilution start to measurably degrade response quality?
- A telemetry-driven evaluation of which subagents in a 12-18 skill harness are over- or under-used.
- A topology comparison: out-of-band back-pressure (daemon-mediated approval channel) vs in-band back-pressure (Stop hook running typecheck + tests). What classes of failure does each catch that the other misses?

---

## Open Questions

1. **What is the exact relationship between `Spec-Driven Development` and `Context-Free Grammar (CFG) Constrained Decoding`?** The graphify edge is AMBIGUOUS. Both enforce intent-before-execution, but the formal-language analogy may or may not generalize.
2. **What does the `MCP vs A2A` choice imply for `Agent Teams` topology?** Currently AMBIGUOUS in the graph. Worth tracing which protocol primitives are actually used by Claude Code Agent Teams in practice.
3. **How would the IFScale 500-instruction ceiling apply to skill descriptions in aggregate?** A typical heavy-stack harness ships ~12-18 skills; each description is part of the routing surface. At what skill count does routing accuracy start to degrade?
4. **Does the plan-critic skepticism safeguard hold up under repeated invocation?** Anecdotal evidence from instantiations suggests it does, but a controlled comparison vs no-critic would be valuable.
5. **Is the lean-shell equilibrium viable for a single-team internal developer aid, or does it only pay for itself when the harness is the product?** The skills + hooks discipline of the heavy stack may be over-engineered for small teams. (See Case Study for a worked lean-shell example.)

---

## Appendix — Per-Topic Graphify Queries (LLM Agent Lookup Index)

This appendix lists, for each major topic in the document, the most useful graphify queries an LLM agent can run against `harness-kb graph + harness-kb wiki` to retrieve authoritative context. The graph was built from `ai/docs/` (476 nodes, 665 edges, 21 communities); node names below are real names from `graphify-out/GRAPH_REPORT.md`. Three query forms:

```
harness-kb graph query "<question>"            # BFS traversal — broad context (default)
harness-kb graph query "<question>" --dfs      # DFS traversal — trace one path deeply
harness-kb graph query "<question>" --budget N # cap answer at N tokens
harness-kb graph path "Node A" "Node B"        # shortest path between two named nodes
harness-kb graph explain "Node Name"           # plain-language explanation of a single node
harness-kb --mcp                         # start MCP stdio server (let an agent call query/path/explain as tools)
```

For agent integration, `--mcp` is preferred — the agent calls `query`, `path`, `explain` as tools rather than shelling out. For interactive humans, the bare slash commands are easier.

### A1. Harness Engineering — Definition & Philosophy

```bash
harness-kb graph query "What is harness engineering and why does it matter for coding agents?"
harness-kb graph query "What are the five components of an agent harness (context injection, control, action, persist, observe-and-verify)?"
harness-kb graph query "How does Mitchell Hashimoto frame harness engineering — every mistake becomes a structural fix?"
harness-kb graph query "What are the Five Pillars of Context Engineering: Selection, Structuring, Memory, Compression, Evaluation?"
harness-kb graph query "What is in the Agentic Harness Patterns community of the graph and which nodes have the highest betweenness?"
harness-kb graph explain "Atelier Agent Harness"
harness-kb graph explain "Cursor Agent Harness (instructions + tools + model)"
harness-kb graph explain "Five Pillars of Context Engineering"
harness-kb graph path "Coding Agent Incremental Progress Pattern" "Back-Pressure Mechanisms"
harness-kb graph path "Atelier Agent Harness" "Cursor Agent Harness (instructions + tools + model)"
harness-kb graph query "What is the unifying definition of context engineering — find the smallest possible set of high-signal tokens?"
harness-kb graph query "How does harness engineering operationalize context engineering as a discipline?"
```

### A2. Artifact Taxonomy & Canonical Components

```bash
harness-kb graph query "What are the artifact / advisory / utility component classes for harness skills and agents?"
harness-kb graph query "What seven kinds of files implement an agent harness — memory, rules, references, skills, subagents, hooks, CI evals?"
harness-kb graph query "What is mirror parity for plugin and local artifact mirrors?"
harness-kb graph query "What size limits apply to references, rules, skills, subagents, and hooks?"
harness-kb graph explain "SKILL.md Format (Frontmatter + Markdown Body)"
harness-kb graph explain "Path-Scoped Rules"
harness-kb graph explain "Cursor Rules Guide"
harness-kb graph path "Cursor Rules Guide" "Path-Scoped Rules"
harness-kb graph path "Agent Skills Standard README" "Agent Skills Specification"
harness-kb graph query "What is the deletion test for canonical references?"
harness-kb graph query "How do path-scoped rules differ from always-loaded memory in attention budget impact?"
```

### A3. Always-Loaded Memory (CLAUDE.md / AGENTS.md)

```bash
harness-kb graph query "What does the AGENTBENCH study say about LLM-generated AGENTS.md performance?"
harness-kb graph query "What is the recommended size for a CLAUDE.md / AGENTS.md file and why?"
harness-kb graph query "Why should always-loaded memory document capabilities not structure?"
harness-kb graph query "How do attention sinks affect instructions placed at the top of AGENTS.md?"
harness-kb graph explain "AGENTS.md / CLAUDE.md Context Files"
harness-kb graph explain "CLAUDE.md Files"
harness-kb graph explain "Auto Memory (Claude Code)"
harness-kb graph explain "Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?"
harness-kb graph path "Attention Sinks (Xiao et al., ICLR 2024)" "AGENTS.md / CLAUDE.md Context Files"
harness-kb graph path "Analysis: A Guide to CLAUDE.md" "Context Rot"
harness-kb graph query "What is the IFScale 500-instruction ceiling and how does it apply to AGENTS.md?"
harness-kb graph query "Why do human-written context files outperform LLM-generated ones — what is the redundancy cost?"
```

### A4. Path-Scoped Rules

```bash
harness-kb graph query "What is a path-scoped rule and how does its frontmatter glob trigger loading?"
harness-kb graph explain "Cursor Rules Guide"
harness-kb graph explain ".claude/rules/ Directory"
harness-kb graph explain "Rules as Static Context"
harness-kb graph explain "Skills as Dynamic Workflows"
harness-kb graph path "Rules as Static Context" "Skills as Dynamic Workflows"
harness-kb graph path "Path-Scoped Rules" "Progressive Disclosure (Skills Context Management)"
harness-kb graph query "What conventions belong in path-scoped rules versus always-loaded memory?"
harness-kb graph query "How do Cursor's rule conventions compare to Claude Code's .claude/rules/ directory?"
harness-kb graph query "What is the recommended length for a path-scoped rule file?"
harness-kb graph query "When should a rule reference a policy file in references/ instead of restating policy?"
```

### A5. References (Policy Layer)

```bash
harness-kb graph query "What are the canonical references in a harness — harness-taxonomy, context-budget-policy, execution-policy, artifact-lifecycle, agent-prompt-style?"
harness-kb graph query "Why deduplicate policy from skills into a shared references layer?"
harness-kb graph query "What is a Context Contract section in a SKILL.md and what does it link to?"
harness-kb graph query "What is the deletion test enforcement for references?"
harness-kb graph query "What are the four delegation modes in an execution-policy: stay inline, isolated subagent, parallelize, repo-local eval?"
harness-kb graph query "What Smart-Zone thresholds (40%, 70%) belong in a context-budget-policy?"
harness-kb graph path "Dumb Zone / Smart Zone (Context Threshold)" "Context Rot"
harness-kb graph path "Back-Pressure Mechanisms" "Five Pillars of Context Engineering"
harness-kb graph explain "Back-Pressure Mechanisms"
harness-kb graph query "How does the references layer enable a single edit point for shared discipline?"
harness-kb graph query "What is mirror parity and why is byte-identical enforcement important for the policy layer?"
```

### A6. Skills (Open Standard + Claude Code)

```bash
harness-kb graph query "What is the Agent Skills Open Standard and what fields are required in SKILL.md frontmatter?"
harness-kb graph query "What is the three-tier progressive disclosure model for skills (metadata / instructions / resources)?"
harness-kb graph query "How should skill descriptions be written — imperative phrasing, trigger burden, eval-driven loop?"
harness-kb graph query "What are the skill anti-patterns: god skills, vague descriptions, too many overlapping skills?"
harness-kb graph explain "SKILL.md Format (Frontmatter + Markdown Body)"
harness-kb graph explain "Optimizing Skill Descriptions"
harness-kb graph explain "Best Practices for Skill Creators"
harness-kb graph explain "Evaluating Skill Output Quality"
harness-kb graph explain "Using Scripts in Skills"
harness-kb graph path "SKILL.md Format (Frontmatter + Markdown Body)" "Progressive Disclosure (Skills Context Management)"
harness-kb graph path "Agent Skills Open Standard" "Cursor Agent Skills"
harness-kb graph query "What are skills as instructors versus skills as helpers — enforced vs advisory semantics?"
harness-kb graph query "What is the recommended length cap for SKILL.md and what happens past it?"
```

### A7. Subagents (Context Isolation)

```bash
harness-kb graph query "Why are subagents for context isolation, not specialization?"
harness-kb graph query "What is the recommended system prompt structure for a subagent: Role, Process, Checklist, Output Format, Approval Criteria?"
harness-kb graph query "What are the subagent anti-patterns — aggressive CRITICAL prompts, no maxTurns, god agents, vague descriptions?"
harness-kb graph query "How should subagent output be formatted — citation-rich path:line summaries with confidence ≥80%?"
harness-kb graph query "When should I use Agent Teams (peer-to-peer) versus single-shot subagents?"
harness-kb graph explain "Cursor Subagents Guide"
harness-kb graph explain "Analysis: Creating Custom Subagents"
harness-kb graph explain "Subagent as Context Firewall"
harness-kb graph explain "Agent Teams (Claude Code)"
harness-kb graph explain "Agent Team Mailbox (Inter-agent Messaging)"
harness-kb graph explain "Agent Team Shared Task List"
harness-kb graph path "Cursor Subagents Guide" "Subagent as Context Firewall"
harness-kb graph path "Agent Teams (Claude Code)" "MCP vs A2A Protocol"
harness-kb graph query "What model selection heuristic applies to subagents — when Haiku vs Sonnet vs Opus?"
harness-kb graph query "What is the anti-nesting rule for subagents and what is the MCP escape hatch?"
```

### A8. Hooks (Deterministic Rails)

```bash
harness-kb graph query "What are the four hook types — command, http, prompt, agent — and when does each apply?"
harness-kb graph query "What are the 22 lifecycle events in Claude Code hooks (Session, Agentic loop, Subagent, Compaction, Control, Configuration, Worktree, MCP)?"
harness-kb graph query "What is the hook stdin/stdout/exit-code communication contract?"
harness-kb graph query "What hook pitfalls exist — infinite Stop loops, shell-profile stdout poisoning, case-sensitive matchers, PostToolUse cannot undo?"
harness-kb graph explain "Cursor Hooks Guide"
harness-kb graph explain "Analysis: Automate Workflows with Hooks"
harness-kb graph explain "Back-Pressure Mechanisms"
harness-kb graph explain "Third-Party Hooks Compatibility (Claude Code)"
harness-kb graph explain "Stop Hook Event"
harness-kb graph path "Cursor Hooks Guide" "Back-Pressure Mechanisms"
harness-kb graph path "Stop Hook Event" "Back-Pressure Mechanisms"
harness-kb graph query "What is the stop_hook_active field and why must Stop hooks check it?"
harness-kb graph query "How does HumanLayer implement back-pressure without Claude Code hooks — via the daemon-side approval loop?"
```

### A9. Long-Running Context Maintenance

```bash
harness-kb graph query "What are Anthropic's three context-management strategies: Compaction, Structured Note-Taking, Sub-Agent Architectures?"
harness-kb graph query "What is Frequent Intentional Compaction (FIC) and how does it keep phase utilization at 10-15%?"
harness-kb graph query "What is the Initializer Agent + Coding Agent pattern with init.sh, claude-progress.txt, feature_list.json?"
harness-kb graph query "What is the Smart Zone vs Dumb Zone threshold for context utilization?"
harness-kb graph query "Why does Chroma's research show all 18 models degrade with context length at every increment, not just near the limit?"
harness-kb graph explain "Context Rot"
harness-kb graph explain "Frequent Intentional Compaction (FIC) Methodology"
harness-kb graph explain "Phase-Based Context Loading"
harness-kb graph explain "Initializer Agent Pattern"
harness-kb graph explain "Claude Progress File (claude-progress.txt)"
harness-kb graph explain "Coding Agent Incremental Progress Pattern"
harness-kb graph path "Phase-Based Context Loading" "Research-Plan-Implement (RPI) Workflow"
harness-kb graph path "Frequent Intentional Compaction (FIC) Methodology" "Dumb Zone / Smart Zone (Context Threshold)"
harness-kb graph query "What is the /clear-after-two-failed-corrections rule and why does bad-correction-bad-correction reinforce failure?"
harness-kb graph query "How does the RPI leverage hierarchy work — 1000s bad lines from bad research vs 100s from bad plan vs 1 from bad code?"
```

### A10. Verification Before Completion (Iron Law)

```bash
harness-kb graph query "What is the Iron Law: NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE?"
harness-kb graph query "What is the claim → requires → not-sufficient table and how does it map to verification commands?"
harness-kb graph query "What red-flag phrases should trigger the verification gate (should work, probably fine, I didn't change that)?"
harness-kb graph query "How does back-pressure work — typecheck and tests on every Stop event, success silent, failures verbose?"
harness-kb graph explain "Back-Pressure Mechanisms"
harness-kb graph explain "Critic Agent Pattern (Engineer + Critic Loop)"
harness-kb graph explain "Bad Trajectory Reinforcement (Context Poison)"
harness-kb graph path "Back-Pressure Mechanisms" "Coding Agent Incremental Progress Pattern"
harness-kb graph path "Critic Agent Pattern (Engineer + Critic Loop)" "Bad Trajectory Reinforcement (Context Poison)"
harness-kb graph query "Why is rationalization-prevention a key part of verification — why must the agent verify even when the change feels small?"
harness-kb graph query "What is the Golden Rule of Output for back-pressure hooks — success silent, failures verbose?"
```

### A11. Critic & Review Patterns

```bash
harness-kb graph query "What is the plan-critic agent and what verdict does it return — PROCEED versus REVISE?"
harness-kb graph query "What is the Skepticism Safeguard clause for a plan-critic and why is it required?"
harness-kb graph query "What is the advisor pattern — speaks before substantive work, ≤100 words enumerated, second-opinion before context fills?"
harness-kb graph query "Why is cross-model review valuable — shared blind spots between two instances of the same model are systemic?"
harness-kb graph query "What aspect specialists run in a multi-agent code review — code-reviewer, docs-impact, test-analyzer, silent-failure-hunter, type-design, simplifier, comment-analyzer?"
harness-kb graph explain "Critic Agent Pattern (Engineer + Critic Loop)"
harness-kb graph explain "Agentic Software Modernization"
harness-kb graph path "Critic Agent Pattern (Engineer + Critic Loop)" "Research-Plan-Implement (RPI) Workflow"
harness-kb graph path "Critic Agent Pattern (Engineer + Critic Loop)" "Frequent Intentional Compaction (FIC) Methodology"
harness-kb graph query "When should a plan-critic gate fire — what is the >100x downstream-cost-to-write-cost rule?"
harness-kb graph query "What is the difference between an advisory agent (advisor, simplifier, docs-impact) and a utility agent (commit, debug, verification)?"
```

### A12. Agent Communication Protocols (MCP, A2A, ACP, ANP)

```bash
harness-kb graph query "What are the four MCP primitives — tools, resources, prompts, elicitations — and which are well-supported by clients?"
harness-kb graph query "How does MCP collapse N×M integrations to M+N?"
harness-kb graph query "What is the difference between MCP (tool-to-agent) and A2A (agent-to-agent)?"
harness-kb graph query "What is Programmatic Tool Calling and how does it achieve ~80% token savings?"
harness-kb graph query "What is the tool_search experimental server tool for progressive disclosure of tool definitions?"
harness-kb graph explain "Model Context Protocol (MCP)"
harness-kb graph explain "Agent-to-Agent Protocol (A2A) by Google"
harness-kb graph explain "Agent Communication Protocol (ACP) by IBM Research"
harness-kb graph explain "Agent Network Protocol (ANP)"
harness-kb graph explain "MCP Primitives (Resources, Prompts, Tools, Sampling)"
harness-kb graph explain "MCP Stateless Transport (MRTR / June 2026 Roadmap)"
harness-kb graph explain "MCP Cross-App Access (XAA) Enterprise Auth"
harness-kb graph path "Model Context Protocol (MCP)" "Agent-to-Agent Protocol (A2A) by Google"
harness-kb graph path "Programmatic Tool Calling (PTC)" "Tool Search (just-in-time tool discovery)"
harness-kb graph query "When should I use a CLI tool directly instead of an MCP server wrapping the same CLI?"
harness-kb graph query "What MCP June 2026 roadmap items matter — SEP-1442/2243 stateless transport, SEP-2322 MRTR, SEP-1686 Tasks?"
```

### A13. CI Eval Harness for Artifacts

```bash
harness-kb graph query "What is a deterministic prompt-eval harness and what does it check?"
harness-kb graph query "What contract-string checks should a SKILL.md prompt-eval enforce?"
harness-kb graph query "How does mirror-parity testing work for plugin payload versus local mirror pairs?"
harness-kb graph query "What hook section-schema regex enforces the six-section research-team plan structure?"
harness-kb graph query "Why does CI prompt-eval prevent silent contract drift across releases?"
harness-kb graph explain "Evaluating Skill Output Quality"
harness-kb graph path "Evaluating Skill Output Quality" "Optimizing Skill Descriptions"
harness-kb graph path "Evaluating Skill Output Quality" "SKILL.md Format (Frontmatter + Markdown Body)"
harness-kb graph query "What eval-driven loop refines skill descriptions — 8-10 should-trigger / 8-10 near-miss queries, 60/40 train/validation?"
harness-kb graph query "How many iterations are typically needed to converge a skill description?"
harness-kb graph query "Why are deterministic checks (no LLM calls) preferred for the CI eval layer?"
```

### A14. Plugin Packaging (Claude Code Plugin Standard)

```bash
harness-kb graph query "What is the Claude Code plugin manifest (.claude-plugin/plugin.json) and what fields does it require?"
harness-kb graph query "What is the marketplace.json schema and how does it list plugin paths?"
harness-kb graph query "How does mirror parity work between plugins/<plugin>/<x> and .claude/<x>?"
harness-kb graph query "What is the difference between a single-plugin marketplace and a multi-plugin marketplace?"
harness-kb graph explain "Plugin Marketplace"
harness-kb graph explain "marketplace.json Schema"
harness-kb graph explain "Analysis: Creating Plugins for Claude Code"
harness-kb graph query "What is the Claude Code extensibility stack — Skills, Plugins, Hooks, and Subagents — and how do they compose?"
harness-kb graph path "Plugin Marketplace" "Agent Skills Open Standard"
harness-kb graph path "marketplace.json Schema" "SKILL.md Format (Frontmatter + Markdown Body)"
harness-kb graph query "When should an artifact suite be packaged as a plugin versus shipped as a flat .claude/ directory?"
harness-kb graph query "What are the common pitfalls in publishing a Claude Code plugin to a marketplace?"
```

### A15. Orchestration Recipes (RPI, Ralph, Multi-Agent Research, Parallel Code Review)

```bash
harness-kb graph query "What is the RPI workflow — Research, Plan, Implement — and why is each phase a fresh-context boundary?"
harness-kb graph query "What is a Ralph loop — state file + sentinel + Stop hook injection?"
harness-kb graph query "How does a multi-agent research team decompose a question into sub-questions and assign teammates?"
harness-kb graph query "What are the six required sections of a research-team plan and how does the Stop hook validate them?"
harness-kb graph query "How does parallel code review dispatch aspect-specialists in one message and synthesize a single PR comment?"
harness-kb graph explain "Research-Plan-Implement (RPI) Workflow"
harness-kb graph explain "Two-Agent Architecture for Long-Running Tasks"
harness-kb graph explain "Atelier Agent Harness"
harness-kb graph explain "Research-Plan-Implement-Review Workflow (Tyler Burleigh)"
harness-kb graph explain "Phase-Based Context Loading"
harness-kb graph path "Research-Plan-Implement (RPI) Workflow" "Frequent Intentional Compaction (FIC) Methodology"
harness-kb graph path "Research-Plan-Implement (RPI) Workflow" "Critic Agent Pattern (Engineer + Critic Loop)"
harness-kb graph path "Phase-Based Context Loading" "Research-Plan-Implement (RPI) Workflow"
harness-kb graph query "What is the RPI Workflow Independent Convergence — RPI/RPIR/Atelier/Modernization arriving at the same shape?"
harness-kb graph query "When should I parallelize subagents in one message versus dispatch sequentially?"
```

### A16. Smart Zone & Context Rot (Empirical Foundations)

```bash
harness-kb graph query "What is the Smart Zone (≤40%) versus Dumb Zone (>60%) of context utilization?"
harness-kb graph query "What does the Chroma context-rot study show across all 18 tested models?"
harness-kb graph query "What are the three architectural causes of context rot — n² self-attention, training-distribution mismatch, position interpolation?"
harness-kb graph query "What is the Same-Task-More-Tokens result — accuracy 0.92 → 0.68 with 3K filler tokens (Levy et al. ACL 2024)?"
harness-kb graph explain "Context Rot"
harness-kb graph explain "Dumb Zone / Smart Zone (Context Threshold)"
harness-kb graph explain "Dumb Zone (Context Degradation Threshold ~40%)"
harness-kb graph explain "Context Window as RAM Analogy"
harness-kb graph query "How do Lost-in-the-Middle, the Dumb Zone, and Context Rot all describe the same underlying LLM performance collapse?"
harness-kb graph path "Context Rot" "Lost in the Middle (Liu et al., TACL 2024)"
harness-kb graph path "Dumb Zone / Smart Zone (Context Threshold)" "Frequent Intentional Compaction (FIC) Methodology"
harness-kb graph query "Why is filler token count more predictive of accuracy degradation than relevance of the filler?"
harness-kb graph query "What is Codebase Hygiene (Pre-AI Cleanup) and how does it shrink the always-loaded context surface?"
```

### A17. Lost-in-the-Middle & Positional Bias

```bash
harness-kb graph query "What is the U-shaped recall curve and where in context is information most likely to be ignored?"
harness-kb graph query "Why should critical instructions be placed at the start AND end of context?"
harness-kb graph query "What is the in-between effect and how does it interact with primacy and recency bias?"
harness-kb graph query "How does query-last placement improve recall by up to 30% per Anthropic's measurement?"
harness-kb graph explain "Lost in the Middle (Liu et al., TACL 2024)"
harness-kb graph explain "U-Shaped Performance Curve (Positional Bias)"
harness-kb graph explain "Positional Bias in Long-Context LLMs (primacy and recency bias)"
harness-kb graph explain "Attention Sinks (Xiao et al., ICLR 2024)"
harness-kb graph explain "In-Between Effect (relative distance between evidence documents)"
harness-kb graph path "Lost in the Middle (Liu et al., TACL 2024)" "Attention Sinks (Xiao et al., ICLR 2024)"
harness-kb graph path "U-Shaped Performance Curve (Positional Bias)" "Positional Bias in Long-Context LLMs (primacy and recency bias)"
harness-kb graph query "How does positional bias constrain optimal RAG document placement strategies?"
harness-kb graph query "What does AGENTBENCH show about coding-agent context-file performance under positional pressure?"
```

### A18. Progressive Disclosure (Cross-Cutting Principle)

```bash
harness-kb graph query "What is progressive disclosure as a context-management principle — metadata always, body on activation, resources only when referenced?"
harness-kb graph query "What are the four progressive-disclosure patterns — index-first, scout, phase-based, separated skill files?"
harness-kb graph query "How does progressive disclosure solve the AGENTS.md size problem, the skill discoverability problem, and the MCP tool overload problem with one mechanism?"
harness-kb graph query "What is the role of progressive disclosure in skill loading versus tool loading?"
harness-kb graph explain "Progressive Disclosure (Skills Context Management)"
harness-kb graph explain "Progressive Disclosure in AI Agents"
harness-kb graph explain "Progressive / On-Demand Skill Loading"
harness-kb graph explain "Phase-Based Context Loading"
harness-kb graph path "Progressive Disclosure (Skills Context Management)" "SKILL.md Format (Frontmatter + Markdown Body)"
harness-kb graph path "Progressive Disclosure (Skills Context Management)" "Tool Search (just-in-time tool discovery)"
harness-kb graph path "Progressive / On-Demand Skill Loading" "Progressive Disclosure in AI Agents"
harness-kb graph query "What is the Skill Quality Improvement Loop — Progressive Disclosure + Eval-Driven Dev + Description Optimization?"
harness-kb graph query "Which graphify community has the highest betweenness through Cursor Agent Skills, and why does that broker matter?"
```

### A19. Spec-Driven Development

```bash
harness-kb graph query "What are the three SDD adoption levels — spec-first, spec-anchored, spec-as-source?"
harness-kb graph query "How do GitHub Spec Kit, AWS Kiro, and Tessl differ in rigor and complexity?"
harness-kb graph query "What is the rationale for moving ambiguity from code review to spec review?"
harness-kb graph query "What are the /specify, /plan, /tasks commands in Spec Kit and how do they sequence?"
harness-kb graph explain "Spec-Driven Development"
harness-kb graph explain "Spec-Driven Development (SDD)"
harness-kb graph explain "GitHub Spec Kit (AI-assisted SDD CLI tool)"
harness-kb graph explain "Amazon Kiro (VS Code SDD extension)"
harness-kb graph explain "Constitutional Foundation (Spec Kit)"
harness-kb graph path "Spec-Driven Development" "Context-Free Grammar (CFG) Constrained Decoding"
harness-kb graph path "Spec-Driven Development" "Cursor Plan Mode (Shift+Tab)"
harness-kb graph query "Why are AI coding assistants newly relevant to SDD — what is the pattern-completion vs mind-reading gap?"
harness-kb graph query "What is the SDD Tooling Triad and how do the three tools target different complexity levels?"
```

### A20. HumanLayer Architecture (Lean-Shell Instantiation)

```bash
harness-kb graph query "What is HumanLayer's approval loop via MCP and how does it gate every Claude tool call?"
harness-kb graph query "What roles do hld, hlyr, humanlayer-wui, claudecode-go, and CodeLayer play in the HumanLayer stack?"
harness-kb graph query "How does HumanLayer use SQLite for daemon-side session persistence?"
harness-kb graph query "Why does HumanLayer expose only one MCP tool (request_permission) instead of many tools?"
harness-kb graph query "What nodes are in the HumanLayer Architecture community and how do hld, hlyr, and the WUI compose?"
harness-kb graph explain "Approval Loop via MCP (HumanLayer)"
harness-kb graph explain "hld Daemon (HumanLayer Local Runtime)"
harness-kb graph explain "hlyr CLI (HumanLayer Runtime CLI)"
harness-kb graph explain "humanlayer-wui (Tauri/React Desktop UI)"
harness-kb graph explain "claudecode-go (Go SDK for Claude Code)"
harness-kb graph explain "CodeLayer (AI Agent IDE)"
harness-kb graph explain "SQLite Persistence (hld Session Store)"
harness-kb graph path "Approval Loop via MCP (HumanLayer)" "Back-Pressure Mechanisms"
harness-kb graph path "hld Daemon (HumanLayer Local Runtime)" "Subagent as Context Firewall"
harness-kb graph query "How does HumanLayer's daemon-mediated back-pressure differ from Stop-hook back-pressure in Claude Code?"
harness-kb graph query "What is the parent-child session model in hld and how does getSessionLeaves implement UI-side compaction?"
```

### A21. Prompting & Structured Outputs

```bash
harness-kb graph query "What are Claude 4.x prompting best practices — explicit instructions, long-horizon reasoning, state tracking, multi-context-window prompting?"
harness-kb graph query "What is strict tool use (strict: true) and how does it use grammar-constrained sampling?"
harness-kb graph query "What are the limits on strict tools per request — 20 strict, 24 optional params, 16 union-typed params?"
harness-kb graph query "How does response prefilling steer model output and reduce ambiguity?"
harness-kb graph query "What is chain-of-thought prompting and when should it be used versus instructed reasoning?"
harness-kb graph query "What is prompt chaining for complex multi-step tasks?"
harness-kb graph explain "Anthropic Strict Tool Use Guide"
harness-kb graph explain "Strict Tool Use (strict: true schema enforcement)"
harness-kb graph explain "Claude 4.x Prompting Best Practices"
harness-kb graph explain "Few-Shot Examples for Consistency"
harness-kb graph explain "Response Prefilling Technique"
harness-kb graph explain "Prompt Chaining"
harness-kb graph explain "Adaptive Thinking (Claude 4.6)"
harness-kb graph explain "Chain-of-Thought Prompting"
harness-kb graph explain "Grammar Caching (24h TTL)"
harness-kb graph path "Strict Tool Use (strict: true schema enforcement)" "Context-Free Grammar (CFG) Constrained Decoding"
harness-kb graph path "Anthropic Strict Tool Use Guide" "Anthropic Tool Use Implementation Guide"
harness-kb graph query "When should I use chain-of-thought versus strict tool use for reliable structured output?"
harness-kb graph query "What are the trade-offs between prefilled responses and free-form generation in agentic systems?"
```

### Use With `--mcp` (recommended for agents)

```bash
# One-time setup: launch graphify as an MCP server in stdio mode
harness-kb ./ai/docs --mcp

# Then in your agent's MCP config, register it as the "graphify" server.
# Tools available to the agent at runtime:
#   query(question, dfs?, budget?)  — BFS or DFS traversal
#   path(from, to)                   — shortest path between two named nodes
#   explain(node)                    — plain-language explanation of a single node
#
# The agent can chain: explain a god node → path between two communities → query for synthesis.
```

---

*This document is the canonical reference for harness engineering work in this study library and any project that wants to inherit the same approach. When implementing a harness, copy the artifact templates from Part II, follow the orchestration recipes (Recipes A-D), cite the primary sources from `ai/docs/`, and consult the HumanLayer Case Study above for a worked lean-shell example. For graph-driven retrieval, point an agent at `harness-kb graph + harness-kb wiki` via `harness-kb --mcp` and use the per-topic query bank in the appendix.*
