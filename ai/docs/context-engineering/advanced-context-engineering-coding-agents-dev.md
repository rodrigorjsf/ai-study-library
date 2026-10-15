# Advanced Context Engineering for Coding Agents

**Source:** https://dev.to/ametel01/advanced-context-engineering-for-coding-agents-11p7
**Category:** Context Engineering

> **Currency check (2026-10-11):** Partially outdated
>
> - **Still holds:** curate context instead of filling it, restart a session rather than argue with a bad trajectory, and use sub-agents to fork a clean window and return a short summary. Anthropic's current docs say the same ("more context isn't automatically better … context rot", https://platform.claude.com/docs/en/build-with-claude/context-windows; sub-agents "preserve context", https://code.claude.com/docs/en/sub-agents).
> - **No longer holds — "dumb zone at ~40% of the window":** the percentage was calibrated on 200K windows. Every current Claude model (Opus/Sonnet/Haiku 5.5, Fable 5.1) has a 1M window (https://platform.claude.com/docs/en/about-claude/models/overview), where 40% would be 400K tokens. HumanLayer itself replaced the 40% rule with a fixed ~100K-token warning for long-context models in March 2026 (https://www.hlyr.dev/blog/long-context-isnt-the-answer).
> - **Revised by its own author — "review plans instead of code":** HumanLayer's April 2026 talk is titled "Everything We Got Wrong About Research-Plan-Implement" ("RPI became a way to outsource thought"), and their 2026 advice is to "read the code" in small slices (https://www.humanlayer.com/blog/humanlayer-resources, https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/wsff.md).
> - **Weakened — "intentional compaction is mandatory":** Claude Code now auto-compacts native-1M models at about 967K tokens (https://code.claude.com/docs/en/model-config), and Anthropic reports dropping context resets from its long-running harness once Opus 4.5 removed "context anxiety" (https://www.anthropic.com/engineering/harness-design-long-running-apps). Hand-written handoff artifacts remain useful; they are no longer a survival requirement.
> - **Changed mechanics:** sub-agents can now spawn their own sub-agents (three layers by default) and can be forked with the parent's full history (https://code.claude.com/docs/en/sub-agents). The source URL is still live.

## Summary

A technical distillation of Dex Horthy's talk on advanced context engineering for coding agents. The article identifies why AI productivity doesn't always equal progress in real-world codebases, introduces the "dumb zone" concept, and provides a systematic framework (Research–Plan–Implement) for managing context effectively across the software development lifecycle.

## Content

### Introduction

AI coding agents have dramatically increased developer throughput. However, in real-world usage — especially in large, long-lived ("brownfield") codebases — many teams observe a mismatch between _output_ and _progress_.

This post is a faithful technical distillation of Dex Horthy's talk on **advanced context engineering**: practical techniques for making today's LLMs effective, reliable, and scalable for serious software engineering.

---

### The Problem: Productivity ≠ Progress

Large-scale surveys of developers show a consistent pattern:

- AI increases code shipped
- Code churn increases even more
- Teams repeatedly rework AI-generated output
- Brownfield codebases suffer the worst outcomes

AI performs well for greenfield projects, prototypes, and dashboards. But in complex systems with legacy constraints, naive agent usage becomes a **tech-debt factory**.

---

### Why This Happens: Context Is the Only Control Surface

Large language models are:

- **Stateless** (no memory between sessions)
- **Non-deterministic**
- Entirely governed by the **current context window**

Every decision — tool usage, file edits, hallucinations — is determined by the tokens currently in context.

> Better tokens in → better tokens out.

More tokens does _not_ mean better outcomes.

---

### The Dumb Zone

As context usage grows, model quality degrades. Empirically, this often begins around **~40% of the context window**, depending on task complexity.

This region is referred to as the **dumb zone**.

**Common causes:**

- Large tool outputs (JSON, UUIDs, logs)
- Unfiltered file dumps
- Repeated correction loops
- MCPs dumping irrelevant data
- Long chat histories full of noise

Once in the dumb zone, agents become unreliable regardless of model quality.

---

### Trajectory Matters

LLMs learn patterns _within a conversation_.

If the conversation looks like:
1. Model makes a mistake
2. Human scolds the model
3. Model makes another mistake
4. Human scolds again

The most likely continuation is… another mistake.

**Bad trajectories reinforce failure modes.**

This is why restarting sessions or compressing context is often more effective than continued correction.

---

### Intentional Compaction

**Intentional compaction** is the deliberate compression of context into a minimal, high-signal representation.

Instead of dragging an ever-growing conversation forward, you:
1. Summarize the current state into a markdown artifact
2. Review and validate it as a human
3. Start a fresh context seeded with that artifact

**What to compact:**
- Relevant files and line ranges
- Verified architectural behavior
- Decisions already made
- Explicit constraints and non-goals

**What not to compact:**
- Raw logs
- Tool traces
- Full file contents
- Repetitive error explanations

Compaction converts exploration into a one-time cost instead of a recurring tax.

---

### Sub-Agents Are About Context, Not Roles

Sub-agents are frequently misunderstood.

They are **not** about mirroring human roles like "frontend agent" or "QA agent".

They exist to:
- Fork a clean context window
- Perform large exploratory reads
- Return a **succinct factual summary** to a parent agent

**Example:**
- Sub-agent scans a large repo
- Returns: _"Relevant logic is in `foo/bar.ts:120–340`, entrypoint is `BazHandler`"_

The parent agent then reads only what matters.

This is how you scale context without entering the dumb zone.

---

### The Research–Plan–Implement Workflow

This workflow is about **systematic compaction** at every stage.

#### Research: Compressing Truth

Goal:
- Understand how the system _actually_ works
- Identify authoritative files and flows
- Eliminate assumptions

Characteristics:
- Read code, not docs
- Produce a short research artifact
- Validate findings manually

If agents are not onboarded with accurate context, they will fabricate. This mirrors _Memento_: without memory, agents invent narratives.

#### Plan: Compressing Intent

Planning is the **highest-leverage activity**.

A good plan:
- Lists exact steps
- References concrete files and snippets
- Specifies validation after each change
- Makes failure modes obvious

A solid plan dramatically constrains agent behavior.

Bad plans produce dozens of bad lines of code.
Bad research produces hundreds.

#### Implement: Mechanical Execution

Once the plan is correct:
- Execution becomes mechanical
- Context remains small
- Reliability increases

---

### Mental Alignment and Code Review

Code review is primarily about **shared understanding**, not syntax.

As AI output scales, reviewing thousands of lines becomes unsustainable.

High-performing teams:
- Review research and plans
- Attach agent transcripts or AMP threads to PRs
- Show exact steps and test results

Reviewing plans preserves architectural coherence as throughput increases.

---

### Choosing the Right Level of Context Engineering

| Task Type | Recommended Approach |
|-----------|---------------------|
| UI tweak | Direct instruction |
| Small feature | Light plan |
| Cross-repo change | Research + plan |
| Deep refactor | Full RPI + human design |

The ceiling of problem difficulty rises with context discipline.

---

### Key Takeaways

- Context is the only lever that matters
- More tokens often reduce correctness
- Intentional compaction is mandatory
- Research and planning are the highest ROI activities
- AI amplifies thinking — it does not replace it

---

### Source & Attribution

This article is a faithful technical adaptation of Dex Horthy's talk "No Vibes Allowed: Solving Hard Problems in Complex Codebases."

All ideas, terminology, and frameworks originate from the referenced talk.
