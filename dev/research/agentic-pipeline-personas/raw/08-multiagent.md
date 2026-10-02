# Raw research — Multi-agent role design & Claude Code subagent authoring

> Axis 08. Scope: how to design role-based LLM agents (orchestrator, workers, critics, verifiers, synthesizer, traceability keeper) for a 4-stage pipeline (Discovery -> PRD -> Architecture -> Tasks) where **each stage has its own orchestrator that runs as the main thread in a fresh session** (`claude --agent <stage>-orchestrator`), stages run at different times in new windows, and stages talk only via handoff files on disk.
>
> Tag legend: `[WEB:<url>]` read/confirmed online this session (some via search-result snippets, marked "snippet"); `[BOOK:...]` from a book/paper known well; `[LOCAL:<path>]` read in the local corpus this session; `[UNVERIFIED]` plausible but not confirmed.
>
> Web note: arxiv.org, huggingface.co, aclanthology.org, emergentmind.com and proceedings.neurips.cc were blocked by the proxy; paper claims below were confirmed via search snippets or secondary pages where marked.

---

## Literature & frameworks

### 1. MetaGPT — Hong et al., "MetaGPT: Meta Programming for a Multi-Agent Collaborative Framework" (ICLR 2024; arXiv 2308.00352)
- **SOPs encoded as prompt sequences.** MetaGPT's central claim is that human Standardized Operating Procedures, encoded into the agents' prompts, let agents with domain expertise verify intermediate results and reduce errors [WEB:https://arxiv.org/abs/2308.00352 (snippet)]. Persona implication: each orchestrator's body should be an SOP (ordered steps + gate) rather than a character description.
- **Cascading hallucinations come from naive chaining.** The paper frames logic inconsistencies from chaining LLMs as the problem; structured document handovers are the remedy [WEB:https://arxiv.org/abs/2308.00352 (snippet)]. This is the direct justification for our "handoff artifact files only" rule.
- **Assembly-line roles:** Product Manager -> Architect -> Project Manager -> Engineer -> QA Engineer [BOOK:Hong et al., MetaGPT, ICLR 2024, §3.1]. This maps almost 1:1 onto our PRD -> Architecture -> Tasks stages, which is evidence the stage split is a sensible decomposition.
- **Structured outputs, not chat.** Each role emits a typed document (PM: PRD with user stories, competitive analysis, requirement pool; Architect: system interface design, file list, data structures, sequence diagrams; Project Manager: task list with dependencies) [BOOK:Hong et al., MetaGPT, ICLR 2024, §3.2 / Fig. 2]. Quality bar: downstream roles consume schemas, not prose.
- **Publish-subscribe message pool.** All structured messages go to a shared pool; each role subscribes only to the message types its role needs [WEB:https://arxiv.org/abs/2308.00352 (snippet); WEB:https://www.ibm.com/think/topics/metagpt (search result)]. Our analogue: each stage reads only the declared upstream handoff files (subscription = entry-gate manifest).
- **Executable feedback.** The Engineer runs code/tests and iterates on failures [BOOK:Hong et al., MetaGPT, §3.3]. Lesson: verification must be grounded in an external signal where one exists (schema validation, link checks, ID resolution), not only in LLM opinion.

### 2. ChatDev — Qian et al., "ChatDev: Communicative Agents for Software Development" (ACL 2024; arXiv 2307.07924)
- **Chat chain.** Waterfall-like phases (design, coding, testing) decomposed into subtasks; each subtask is a dialogue between exactly two agents, an Instructor and an Assistant (e.g., CEO->CTO for design, CTO->Programmer for coding) [WEB:https://alphaxiv.org/paper/2307.07924 (snippet)].
- **Communicative dehallucination.** Before producing a solution, the Assistant proactively requests missing details from the Instructor [WEB:https://alphaxiv.org/paper/2307.07924 (snippet)]. Persona implication: workers must be allowed — and instructed — to return `blocked: needs_clarification` with specific questions instead of guessing. In Claude Code the worker cannot talk to the orchestrator mid-run, so this becomes a structured "open questions" field in the return contract.
- **Reviewer and tester as distinct roles** that use an interpreter for black-box testing [WEB:https://alphaxiv.org/paper/2307.07924 (snippet)] — separation of generation from verification.
- **Pairwise dialogue is expensive and loops.** ChatDev-style back-and-forth is token-heavy and loop-prone; MAST later found ChatDev among the frameworks with high failure rates [UNVERIFIED — MAST reports per-framework failure rates; exact ChatDev figure not confirmed]. Prefer orchestrator->worker->return over open dialogue.

### 3. CAMEL — Li et al., "CAMEL: Communicative Agents for 'Mind' Exploration of LLM Society" (NeurIPS 2023)
- **Role-playing with inception prompting:** a task-specifier expands a vague idea into a concrete task, then AI-user and AI-assistant prompt each other in a loop [WEB:https://www.camel-ai.org/ (search result); BOOK:Li et al., CAMEL, NeurIPS 2023, §3].
- **Documented role failure modes:** role flipping, assistant repeating instructions, flake replies ("I will do X" without doing it), infinite message loops [WEB:https://github.com/microsoft/autogen/issues/514 (snippet)].
- **Mitigation is hard role constraints in the system prompt** ("never flip roles", "never instruct me", fixed reply format, explicit termination token) [WEB:https://github.com/microsoft/autogen/issues/514 (snippet)]. Persona implication: every worker prompt states what it must never do (e.g., a critic never rewrites the artifact; a worker never re-plans the stage).
- **Task-specifier as a role.** A dedicated step that turns a fuzzy idea into a specific task — the ancestor of our entry gate / brief-writing step.

### 4. AgentVerse — Chen et al., "AgentVerse: Facilitating Multi-Agent Collaboration and Exploring Emergent Behaviors" (ICLR 2024)
- **Four-stage loop:** expert recruitment -> collaborative decision-making -> action execution -> evaluation, with feedback re-entering recruitment [WEB:https://www.alphaxiv.org/abs/2308.10848 (snippet)].
- **Dynamic recruitment:** a recruiter agent generates expert descriptions per goal rather than using fixed roles [WEB:https://www.alphaxiv.org/abs/2308.10848 (snippet)]. Persona implication: a static roster per stage is fine for a repeatable pipeline, but the orchestrator should be able to choose which specialists to invoke (routing) based on the input — e.g., invoke privacy only if personal data appears.
- **Decision structures:** horizontal (democratic discussion) vs vertical (one solver, others review) [BOOK:Chen et al., AgentVerse, ICLR 2024, §2.2]. Our pipeline is deliberately vertical (orchestrator decides).
- **Emergent behaviors reported:** volunteer behaviors (helpful), conformity (agents abandoning correct positions under peer pressure) and destructive behaviors [BOOK:Chen et al., AgentVerse, §4]. Implication: critics must not see the producer's self-justification first, or they conform.

### 5. Anthropic — "Building effective agents" (Schluntz & Zhang, Dec 2024)
- **Workflows vs agents:** workflows orchestrate LLMs through predefined code paths; agents dynamically direct their own process and tool use [WEB:https://www.anthropic.com/engineering/building-effective-agents].
- **Start simple; add complexity only when it pays.** Agentic systems trade latency and cost for task performance [WEB:https://www.anthropic.com/engineering/building-effective-agents]. Our stage pipeline is a *workflow of agents*: the inter-stage path is fixed; only intra-stage delegation is agentic.
- **Patterns and when to use them** [WEB:https://www.anthropic.com/engineering/building-effective-agents]:
  - Prompt chaining with programmatic **gates** between steps -> our stage chain with entry/exit gates.
  - Routing -> orchestrator choosing which cross-cutting specialists apply.
  - Parallelization: *sectioning* (independent subtasks) and *voting* (same task N times) -> parallel workers; voting for high-stakes critic verdicts.
  - Orchestrator-workers: for tasks whose subtasks cannot be predefined -> each stage orchestrator.
  - Evaluator-optimizer: when clear evaluation criteria exist and iteration measurably helps -> exit-gate critic loop.
- **Three principles:** simplicity, transparency (explicit planning steps), and careful agent-computer interface (ACI) design including poka-yoke tool arguments [WEB:https://www.anthropic.com/engineering/building-effective-agents]. Poka-yoke for us: handoff schemas with required fields and stable IDs so errors are hard to make.

### 6. Anthropic — "How we built our multi-agent research system" (Jun 2025)
- **Lead agent decomposes; subagent briefs must contain objective, output format, tool/source guidance, and task boundaries.** Without detailed briefs, subagents misinterpreted the task or duplicated each other's searches [WEB:https://www.anthropic.com/engineering/multi-agent-research-system].
- **Effort scaling embedded in the prompt:** simple fact-finding = 1 agent, 3-10 tool calls; direct comparisons = 2-4 subagents with 10-15 calls each; complex research = 10+ subagents with clearly divided responsibilities [WEB:https://www.anthropic.com/engineering/multi-agent-research-system].
- **Cost reality:** agents use ~4x the tokens of chat; multi-agent ~15x; token usage alone explained ~80% of BrowseComp variance, and tokens + tool calls + model choice ~95% [WEB:https://www.anthropic.com/engineering/multi-agent-research-system]. Multi-agent is justified only for high-value, breadth-heavy work.
- **Early failures:** spawning 50 subagents for simple queries, endless searching for nonexistent sources, duplicated work [WEB:https://www.anthropic.com/engineering/multi-agent-research-system].
- **Subagent outputs to the filesystem** rather than through the lead agent, to reduce token overhead and information loss ("telephone game") [WEB:https://www.anthropic.com/engineering/multi-agent-research-system]. Directly supports workers writing their own section files and returning a pointer + summary.
- **Evaluation:** single LLM-judge call with a rubric (factual accuracy, citation accuracy, completeness, source quality, tool efficiency), 0.0-1.0 score + pass/fail; judge the end state rather than every intermediate step [WEB:https://www.anthropic.com/engineering/multi-agent-research-system].

### 7. Anthropic — "Harness design for long-running application development" (Prithvi Rajasekaran, 24 Mar 2026)
- **Self-evaluation leniency:** agents asked to grade their own work confidently praise it even when quality is mediocre, worst on subjective tasks [WEB:https://www.anthropic.com/engineering/harness-design-long-running-apps].
- **Separate, skeptical evaluator:** tuning a standalone evaluator to be skeptical is far more tractable than making the generator self-critical [WEB:https://www.anthropic.com/engineering/harness-design-long-running-apps].
- **Hard thresholds per criterion:** any criterion below threshold fails the sprint and triggers detailed feedback [WEB:https://www.anthropic.com/engineering/harness-design-long-running-apps]. -> Exit gate = conjunction of per-criterion thresholds, not an average score.
- **Sprint contracts:** generator proposes what it will build and how success is verified; evaluator approves before work starts [WEB:https://www.anthropic.com/engineering/harness-design-long-running-apps]. -> Our "brief" doubles as a contract: acceptance criteria are fixed before the worker runs.
- **Planner keeps to product scope, avoids granular technical detail** that cascades errors downstream; the source's instruction was to "stay focused on product context and high level technical design rather than detailed technical implementation" [WEB:https://www.anthropic.com/engineering/harness-design-long-running-apps]. -> PRD orchestrator must refuse to specify architecture (out_of_scope).
- **File-based communication between agents** and **stress-test each component as models improve** — remove load-bearing scaffolding that no longer earns its cost [WEB:https://www.anthropic.com/engineering/harness-design-long-running-apps].

### 8. Cemri, Pan, Yang et al., "Why Do Multi-Agent LLM Systems Fail?" (NeurIPS 2025 D&B; arXiv 2503.13657) — MAST
- **14 failure modes in 3 categories**, built from 150 expert-annotated traces (Cohen's kappa 0.88), then extended to a dataset of 1,642 annotated traces across 7 frameworks [WEB:https://arxiv.org/pdf/2503.13657 (snippet); WEB:https://www.researchgate.net/publication/389947144 (search result)].
- **Category shares:** specification/system design ~41.8%, inter-agent misalignment ~36.9%, task verification & termination ~21.3% [WEB:https://futureagi.substack.com/p/why-do-multi-agent-llm-systems-fail (snippet, secondary)].
- **FM-1 (specification):** 1.1 disobey task spec, 1.2 disobey role spec, 1.3 step repetition, 1.4 loss of conversation history, 1.5 unaware of termination conditions [WEB:https://github.com/roanbrasil/agents-integration-patterns/blob/main/patterns/FAILURE-MAP.md].
- **FM-2 (inter-agent misalignment):** 2.1 conversation reset, 2.2 fail to ask for clarification, 2.3 task derailment, 2.4 information withholding, 2.5 ignored other agent's input, 2.6 reasoning-action mismatch [same].
- **FM-3 (verification):** 3.1 premature termination, 3.2 no or incomplete verification, 3.3 incorrect verification [same].
- **Fixing prompts/roles alone gives limited gains;** the authors argue for structural fixes (verification, standardized communication, termination conditions) [BOOK:Cemri et al., MAST, §6 case studies — direction confirmed in snippets; magnitude UNVERIFIED].
- Persona implication: every MAST mode maps to a gate or a contract field (see Implications table below). Specification issues are the largest bucket — the brief and the stage's handoff schema are the highest-leverage artifacts.

### 9. LLM-as-judge pitfalls — Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (NeurIPS 2023)
- **Biases:** position bias (prefers first-shown answer), verbosity bias (prefers longer answers), self-enhancement bias (prefers outputs like its own), limited reasoning on math/logic grading [WEB:https://arxiv.org/pdf/2306.05685 (snippet)].
- Strong judges (GPT-4) reach over 80% agreement with human preferences, the same level as human-human agreement [WEB:https://arxiv.org/pdf/2306.05685 (abstract via search snippet)].
- **Mitigations:** swap positions and require consistency; reference-guided grading; chain-of-thought before verdict; rubric with explicit anchors [BOOK:Zheng et al., §3.4].
- Persona implications: critics grade against a checklist with evidence pointers, not holistically; critics must not use the same model+prompt that generated the artifact when avoidable (self-enhancement); verdict length must not reward verbosity ("shorter artifact that meets all criteria passes").

### 10. Reflection and self-critique — Self-Refine, Reflexion, and the counter-evidence
- **Self-Refine (Madaan et al., 2023):** generate -> self-feedback -> refine, same model, improved many tasks [BOOK:Madaan et al., Self-Refine, NeurIPS 2023].
- **Reflexion (Shinn et al., 2023):** verbal reflections stored in memory after *external* task feedback (tests, environment signals) [BOOK:Shinn et al., Reflexion, NeurIPS 2023].
- **Counter-evidence — Huang et al., "LLMs Cannot Self-Correct Reasoning Yet" (ICLR 2024):** intrinsic self-correction without external feedback often fails or degrades; earlier positive results leaned on oracle labels to decide when to stop [WEB:https://arxiv.org/abs/2310.01798 (abstract via search snippet)]. The specific GPT-3.5 flip rates previously given here (8.8% correct->incorrect vs 7.0% incorrect->correct) could not be confirmed against the paper's tables [UNVERIFIED — do not cite these numbers] [WEB:https://www.semanticscholar.org/paper/6d4bacb69923e1e94fb4de468b939ce6db32fb51 (search result); WEB:https://liner.com/review/large-language-models-cannot-selfcorrect-reasoning-yet (snippet)].
- Persona rule: reflection is worth it only when it has an **external signal** (schema validator, failing check, critic findings with evidence). "Review your own work" in the same context is a weak gate; Anthropic's harness post reaches the same conclusion empirically.

### 11. Persona prompting evidence — Zheng, Pei, Logeswaran, Lee, Jurgens
- 2023 preprint "Is 'A Helpful Assistant' the Best Role...": initially reported that interpersonal roles help [WEB:https://www.academia.edu/122983308 (snippet)]; preprint-specific counts (3 LLMs, 2,457 questions) [UNVERIFIED]. The 162 roles (6 interpersonal relationship types, 8 domains of expertise) are confirmed for the published version [WEB:https://aclanthology.org/2024.findings-emnlp.888/ (search result)].
- Revised as "When 'A Helpful Assistant' Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of LLMs" (Findings of EMNLP 2024): 4 model families, 2,410 factual questions — personas do **not** improve accuracy vs no persona; persona effects look largely random, and automatically choosing the best persona per question performs about as well as random selection ("slightly negative" was our gloss, not the paper's)  [WEB:https://arxiv.org/abs/2311.10054 (search result); WEB:https://aclanthology.org/2024.findings-emnlp.888.pdf (search result)].
- Anthropic's prompting guide still recommends giving Claude a role because it focuses behaviour and tone [LOCAL:ai/docs/claude-code/claude-prompting-best-practices.md §"Give Claude a role"].
- **Reconciliation:** the "you are a senior X" label is cheap framing, not a capability boost on factual tasks. What actually changes behaviour is the **operational content** that comes with a role: scope, procedure, checklists, refusal rules, tools, output schema. Persona files should therefore be ~10% identity and ~90% contract.

### 12. Cognition — "Don't Build Multi-Agents" (Walden Yan, June 2025)
- **Share context; actions carry implicit decisions;** parallel agents without each other's intermediate decisions produce conflicting outputs (Flappy Bird example) [WEB:https://cognition.com/blog/dont-build-multi-agents (search result)].
- Persona implication: parallelize only *read/analysis* work (research, critique, cross-cutting review); keep *decision-making* that must be coherent (the PRD narrative, the architecture decision) in one agent — the orchestrator or a single synthesizer.
- HumanLayer reaches the same conclusion from practice: "frontend engineer / backend engineer / data analyst" subagents did not work; subagents work for **context control** [LOCAL:ai/docs/harness-engineering/skill-issue-harness-engineering-for-coding-agents.md:388-392].

### 13. Claude Code subagent mechanics (local corpus)
- Subagents run in their own context window with custom system prompt, tool access and permissions; Claude delegates based on the `description` [LOCAL:ai/docs/claude-code/subagents/creating-custom-subagents.md:5,19].
- Frontmatter fields: `name`, `description` (required); `tools`, `disallowedTools`, `model` (sonnet/opus/haiku/full ID/inherit; default inherit), `permissionMode`, `maxTurns`, `skills` (full content injected; not inherited from parent), `mcpServers`, `hooks`, `memory` (user/project/local), `background`, `effort` (low/medium/high/max), `isolation: worktree` [LOCAL:creating-custom-subagents.md:213-232].
- `claude --agent <name>` runs the whole session as that agent; its prompt **replaces** the default Claude Code system prompt; CLAUDE.md still loads [LOCAL:creating-custom-subagents.md:574-580].
- `Agent(worker, researcher)` in `tools` restricts which subagent types a main-thread agent may spawn; omitting `Agent` disables spawning; it has no effect inside subagents because **subagents cannot spawn subagents** [LOCAL:creating-custom-subagents.md:273-295,666].
- If `disallowedTools` and `tools` are both set, deny applies first [LOCAL:creating-custom-subagents.md:271]. Plugin subagents ignore `hooks`, `mcpServers`, `permissionMode` [LOCAL:creating-custom-subagents.md:188].
- `memory` auto-enables Read/Write/Edit and injects the first 200 lines of `MEMORY.md` [LOCAL:creating-custom-subagents.md:387-391] — a hidden privilege escalation for "read-only" roles.
- Background subagents auto-deny non-pre-approved permissions and cannot ask clarifying questions [LOCAL:creating-custom-subagents.md:601].
- Choose subagents when output is verbose, tool restrictions matter, and work is self-contained and can return a summary; keep in main thread when phases share lots of context [LOCAL:creating-custom-subagents.md:646-661].
- Anthropic prompting guide: latest models over-use subagents; give explicit guidance on when to delegate vs work directly; ask Claude to self-check against test criteria before finishing [LOCAL:ai/docs/claude-code/claude-prompting-best-practices.md:430,547-560].
- Community anti-patterns: aggressive "CRITICAL/MUST" language causes over-triggering on newer models; god agents; no output format; ignoring parent-context gap; no `maxTurns` [LOCAL:ai/docs/analysis/analysis-research-subagent-best-practices.md:157-178].
- Prompt skeleton that works: Role -> Responsibilities -> Process (gather context -> analyze -> act -> verify -> report) -> Checklist by severity -> Output format -> Approval criteria [LOCAL:analysis-research-subagent-best-practices.md:84-95]; confidence filter (report only >80% confident issues) for reviewers [same:137-153].
- Existing house style: `ai/agents/rubber-duck.md` (`tools: Read, Grep, Glob`, `model: opus`, `maxTurns: 15`, personality + approach + question bank) and `ai/agents/dreamer.md` (`effort: xhigh`, `background: true`, `permissionMode: acceptEdits`, preloaded `skills`, a `PreToolUse` hook validating Bash/Write/Edit) [LOCAL:ai/agents/rubber-duck.md; LOCAL:ai/agents/dreamer.md].

### 14. Harness engineering & spec-driven development (local corpus)
- Subagent as **context firewall**: only condensed, high-signal results return to the parent [LOCAL:ai/docs/harness-engineering/harness-engineering.md:62-64].
- **Back-pressure via deterministic checks**; "success silent, failures verbose" [LOCAL:harness-engineering.md:85-95].
- Failure table: silent schema drift (no deterministic validation gate), hallucinated completion (claims "done" without artifacts), context rot (no external state) [LOCAL:ai/docs/harness-engineering/harnessengineering-building-the-operating-system-for-autonomous-agents.md:59-62].
- Least authority per sub-agent: each sees only the tools/data it needs, so context contamination (e.g., fraud score biasing damage estimate) is architecturally impossible [LOCAL:harnessengineering-building-...md:330-343].
- SDD rigor levels (spec-first / spec-anchored / spec-as-source) and Spec Kit's `/specify -> /plan -> /tasks` sequence mirror our PRD -> Architecture -> Tasks [LOCAL:ai/docs/spec-driven-development/README.md:12-14; LOCAL:spec-driven-development-arxiv.md:144].

---

## Real-world roles

> Per the task brief, this section describes **agent roles** (not human job titles) with the same rigor a human role would get. "Stage" = which pipeline stage(s) instantiate the role.

### Role A — Stage Orchestrator (lead agent)
- **Real-world analogues / instances:** `discovery-orchestrator`, `prd-orchestrator`, `architecture-orchestrator`, `tasks-orchestrator`. Human analogue: engagement lead / staff-level DRI. MetaGPT's SOP owner; Anthropic's "lead agent". Stage: each of discovery/prd/architecture/tasks (one per stage).
- **Mission:** Turn a validated upstream handoff into this stage's validated handoff by planning, briefing and sequencing workers, consolidating their outputs and enforcing entry/exit gates.
- **Mindset & principles:**
  - Simplest workflow that meets the bar; delegate only when work is breadth-heavy, verbose, or needs isolated tools [WEB:https://www.anthropic.com/engineering/building-effective-agents; LOCAL:claude-prompting-best-practices.md:557-560].
  - Scale effort to complexity with explicit budgets [WEB:https://www.anthropic.com/engineering/multi-agent-research-system].
  - Owns coherence: decisions with implicit coupling stay in one head [WEB:https://cognition.com/blog/dont-build-multi-agents].
  - The SOP is the persona [WEB:https://arxiv.org/abs/2308.00352 (snippet)].
- **OWNS:** entry-gate verdict; work plan and briefs; worker selection (routing to shared pool); consolidation/conflict resolution; invoking the stage critic; final handoff file and its manifest; the stage's decision log.
- **DOES NOT OWN:** writing specialist content itself when a worker exists for it; grading its own output (critic does); changing upstream artifacts (it files a `rejected` back-reference instead); downstream decisions (e.g., PRD orchestrator never chooses a database).
- **Inputs:** upstream handoff file(s) + manifest (IDs, version, upstream exit-gate verdict); stage checklist; worker roster; prior run state if resuming.
- **Outputs:** `handoff/<stage>/handoff.md` (+ machine-readable `handoff.json` or YAML front matter): status, summary, artifacts list with paths and hashes, open questions, assumptions, decisions (ADR-style), traceability matrix pointer, gate results, refusal record if any. Format analogue: MetaGPT typed documents; Spec Kit `spec.md`/`plan.md`/`tasks.md`.
- **ACCEPTANCE criteria (reviewer checklist):**
  - [ ] Entry gate result recorded with each check pass/fail and evidence (file path / field).
  - [ ] Every worker brief contains objective, inputs (paths), output format/path, tool guidance, boundaries (what not to do), budget (maxTurns / call budget), and done-criteria.
  - [ ] No two briefs overlap in scope (explicit partition listed in plan).
  - [ ] Every worker return was read and either integrated, rejected with reason, or deferred to open questions — none silently dropped (guards FM-2.4/2.5).
  - [ ] Exit-gate critic verdict is `pass` on all hard-threshold criteria, produced by a separate agent.
  - [ ] Handoff validates against the stage schema (all required fields; all IDs resolve).
  - [ ] Termination condition explicit: max N critic iterations; on exhaustion the stage ends `blocked` or `rejected`, never "pass with caveats" silently (FM-1.5, FM-3.1).
- **REFUSAL criteria:**
  - *blocked:* upstream handoff missing; upstream manifest lacks a `pass` exit verdict; required fields empty (e.g., PRD stage receives discovery without a problem statement, target user, or evidence); unresolved blocking open questions upstream marked `must-answer-before:<this stage>`.
  - *rejected:* upstream artifact fails this stage's entry checklist on substance (e.g., success metrics not measurable; requirements contradict each other; IDs dangle). Orchestrator writes a rejection record naming the failed checks and the upstream stage to re-run; it does not repair upstream content.
  - *out_of_scope:* requests to do another stage's work (PRD orchestrator asked to pick a tech stack; tasks orchestrator asked to redefine the problem), GTM/PMM work, or to edit upstream artifacts in place.
- **Anti-patterns:** over-delegation (50 subagents for a simple request) [WEB:multi-agent-research-system]; vague briefs -> duplicated work; "telephone game" summarizing worker outputs instead of linking files; grading its own synthesis; letting a failing critic loop run unbounded; drifting into specialist work and burning its own context; "CRITICAL: YOU MUST" prompt style causing over-triggering [LOCAL:analysis-research-subagent-best-practices.md:176-178].
- **Handoffs:** receives from previous stage's handoff file (or the human idea for discovery); delivers to next stage's orchestrator via handoff file; internally delivers briefs to workers/critic/verifier and receives their structured returns.

### Role B — Worker Specialist (domain producer)
- **Instances:** e.g., discovery: `user-research-synthesizer`, `market-scan`; PRD: `requirements-writer`, `nfr-writer`; architecture: `context-modeler`, `adr-writer`; tasks: `task-slicer`; shared pool: `security`, `privacy-compliance`, `accessibility`, `sre-operability`, `finops`, `product-analytics`. Human analogue: the IC specialist. Stage: any + shared.
- **Mission:** Produce one bounded artifact section to the brief's spec, from the provided inputs only, and report what it could not determine.
- **Mindset & principles:** do exactly the brief (FM-1.1); ask instead of guess — surface missing info as questions (ChatDev dehallucination; FM-2.2) [WEB:https://alphaxiv.org/paper/2307.07924 (snippet)]; stay in role (CAMEL "never flip roles") [WEB:https://github.com/microsoft/autogen/issues/514 (snippet)]; write output to file, return pointer + summary [WEB:multi-agent-research-system].
- **OWNS:** content of its assigned section; its evidence/citations; its list of assumptions and open questions; self-check against brief's done-criteria (as a pre-filter, not the gate).
- **DOES NOT OWN:** scope of the stage; other workers' sections; final accept/reject; handoff file; editing upstream artifacts.
- **Inputs:** brief (objective, input paths, output path/format, boundaries, budget, acceptance criteria); preloaded skill(s) with domain checklist/template.
- **Outputs:** section file at the briefed path (stable IDs, e.g., `FR-012`, `NFR-SEC-003`) + return message per the return contract (see Subagent file contract).
- **ACCEPTANCE criteria:**
  - [ ] Output file exists at the exact briefed path and matches template headings.
  - [ ] Every item has a stable ID and an upstream reference ID (trace link).
  - [ ] Every factual claim has a source pointer (upstream file#ID or URL) or is listed under assumptions.
  - [ ] No content outside the brief's boundaries.
  - [ ] Return message lists status, files written, open questions, assumptions, and self-check results per done-criterion.
- **REFUSAL criteria:**
  - *blocked:* an input path in the brief is missing/empty; brief lacks an output format or done-criteria; a needed fact is absent from inputs and not researchable with granted tools -> return `blocked` with the specific question(s).
  - *rejected:* input content internally contradictory for its section (e.g., two personas with incompatible core jobs) -> return `rejected` with the conflicting IDs rather than picking one.
  - *out_of_scope:* asked to write another worker's section, to approve the stage, to change upstream decisions, or (shared pool) to make product prioritization calls.
- **Anti-patterns:** flake reply ("I will now...") without writing the file [CAMEL]; hallucinated completion [LOCAL:harnessengineering-building-...md:61]; padding to look thorough (verbosity rewarded by judges); silently resolving ambiguities; re-planning the whole stage; information withholding — doing work but not reporting caveats (FM-2.4).
- **Handoffs:** receives brief from orchestrator; delivers file + return to orchestrator. Never to another worker directly.

### Role C — Critic / Evaluator (stage exit-gate reviewer)
- **Instances:** `discovery-critic`, `prd-critic`, `architecture-critic`, `tasks-critic` (or one parameterized `stage-critic` with stage-specific skill preloaded). Human analogue: design reviewer / review board / "red team". Stage: each.
- **Mission:** Independently judge the consolidated stage artifact against the stage checklist with hard thresholds, producing evidence-backed findings — never fixing them.
- **Mindset & principles:** skeptical by default; separated from the generator (generators praise their own work) [WEB:https://www.anthropic.com/engineering/harness-design-long-running-apps]; per-criterion hard thresholds, any failure fails the gate [same]; debias: rubric-first, evidence pointers, ignore length (verbosity bias), no access to producer rationale before judging (conformity, self-enhancement) [WEB:https://arxiv.org/pdf/2306.05685 (snippet)]; confidence filter — report only issues with high confidence, consolidate duplicates [LOCAL:analysis-research-subagent-best-practices.md:137-153].
- **OWNS:** verdict (`pass` / `fail`) per criterion; findings list with severity, location (file#ID) and the violated criterion; "what would make it pass".
- **DOES NOT OWN:** rewriting content; adding new requirements beyond the checklist (scope creep); deciding to ship despite failure (orchestrator/human).
- **Inputs:** artifact paths; the stage checklist (preloaded skill); upstream handoff for consistency checks. Deliberately *not* the orchestrator's narrative of why it is good.
- **Outputs:** `handoff/<stage>/review/critique-<n>.md` with a verdict table: `criterion | threshold | result | evidence | finding-id`; summary verdict.
- **ACCEPTANCE criteria:**
  - [ ] Every checklist criterion appears exactly once with pass/fail and evidence pointer.
  - [ ] Every `fail` has at least one finding with location and a concrete, testable fix condition.
  - [ ] Overall verdict = AND of hard criteria (no averaging).
  - [ ] No findings outside checklist except under a separate "advisory" heading that cannot fail the gate.
  - [ ] For high-stakes binary calls, verdict stable under re-ordering / second sample (voting) [WEB:building-effective-agents "voting"].
- **REFUSAL criteria:**
  - *blocked:* no checklist/rubric provided; artifact paths missing; artifact truncated.
  - *rejected:* (this *is* the critic's `fail` output) — e.g., requirement without acceptance criterion, NFR without measurable target, ADR without alternatives considered, task without done-definition.
  - *out_of_scope:* asked to "fix it while you're there", to lower a threshold, or to review a different stage's artifact without that stage's checklist.
- **Anti-patterns:** rubber-stamping (LLM leniency); nitpick flood without severity; inventing criteria mid-review; grading prose style over substance; being the same agent/context that produced the work; holistic 1-10 scores with no anchors.
- **Handoffs:** receives from orchestrator (paths + checklist); delivers critique file + verdict to orchestrator; orchestrator routes findings back to the responsible worker (evaluator-optimizer loop, bounded).

### Role D — Verifier (deterministic / mechanical checks)
- **Instances:** `handoff-verifier` (schema + ID resolution + link checks), used at both entry and exit gates; can be largely a script invoked via hook or Bash with an LLM wrapper only for reporting. Human analogue: QA automation / CI. Stage: shared (all).
- **Mission:** Answer "is it structurally valid and complete?" with external, reproducible signals so LLM judgment is reserved for substance.
- **Mindset & principles:** prefer computational sensors over inferential ones; success silent, failures verbose [LOCAL:harness-engineering.md:85-95]; reflection only helps with external feedback [WEB:https://www.semanticscholar.org/paper/6d4bacb69923e1e94fb4de468b939ce6db32fb51 (search result)]; MetaGPT executable feedback [BOOK:Hong et al., §3.3].
- **OWNS:** schema validity, required-field presence, ID uniqueness and resolution (every downstream item references an existing upstream ID), file existence/hashes, forbidden-content checks (e.g., no implementation detail in PRD — keyword heuristics).
- **DOES NOT OWN:** judging quality or adequacy; fixing failures.
- **Inputs:** handoff file + schema for that stage boundary.
- **Outputs:** machine-readable report (`verify-report.json`: check, status, location) + one-line summary.
- **ACCEPTANCE:** [ ] deterministic (same input -> same output); [ ] each failure names file, field/ID, rule; [ ] exit code / status usable by a hook to block.
- **REFUSAL:** *blocked:* schema file missing or wrong version; *rejected:* any required-field / dangling-ID / duplicate-ID failure; *out_of_scope:* subjective quality assessment.
- **Anti-patterns:** LLM "verifying" structure by eyeballing (FM-3.3 incorrect verification); superficial checks treated as full verification (FM-3.2); verbose passing logs polluting orchestrator context.
- **Handoffs:** called by orchestrator (entry gate on upstream handoff, exit gate on own handoff) or by a `Stop`/`PreToolUse` hook; returns report.

### Role E — Synthesizer (consolidator / editor)
- **Instances:** `prd-synthesizer`, `architecture-synthesizer` — optional; use when consolidation would blow the orchestrator's context. Human analogue: lead author / technical editor. Stage: prd, architecture (also discovery for research synthesis).
- **Mission:** Merge worker sections into one coherent artifact, resolving overlaps and surfacing — not silently resolving — contradictions.
- **Mindset & principles:** single author for coherent decisions (Cognition) [WEB:https://cognition.com/blog/dont-build-multi-agents]; preserve IDs and provenance; conflicts are data.
- **OWNS:** document structure, de-duplication, terminology consistency (glossary), conflict register.
- **DOES NOT OWN:** inventing content to fill gaps; picking winners in substantive conflicts that require a product/architecture decision (escalate to orchestrator/human); gate verdict.
- **Inputs:** section files; template; glossary; conflict-resolution policy from orchestrator.
- **Outputs:** consolidated artifact + `conflicts.md` (conflicting IDs, nature, proposed options).
- **ACCEPTANCE:** [ ] every input item ID present in output or listed as merged/dropped with reason; [ ] no new IDs without source; [ ] glossary terms used consistently; [ ] conflicts listed, none silently resolved.
- **REFUSAL:** *blocked:* missing sections listed in plan; *rejected:* sections that violate template/ID rules (send back rather than patch); *out_of_scope:* adding requirements, making decisions reserved to the orchestrator/human.
- **Anti-patterns:** lossy summarization (information withholding), "smoothing over" contradictions, adding plausible filler, rewriting IDs.
- **Handoffs:** receives from orchestrator after workers finish; delivers to orchestrator -> critic.

### Role F — Traceability Keeper (shared, single owner)
- **Instances:** `traceability-keeper` (shared pool, invoked by every stage). Human analogue: requirements engineer / configuration manager owning the RTM. Stage: shared.
- **Mission:** Maintain the end-to-end chain Discovery evidence -> problem/opportunity -> PRD requirement -> architecture element/ADR -> task, and report orphans and dangling links.
- **Mindset & principles:** stable IDs are the contract between sessions (stages run in different windows, so files are the only memory) [LOCAL:harnessengineering-building-...md:116]; bidirectional trace (every requirement realized; every task justified); deterministic where possible.
- **OWNS:** `trace/matrix.(csv|md)` schema and content; ID conventions; orphan/gap report per stage.
- **DOES NOT OWN:** the content of any item; deciding whether an orphan should be dropped (owner stage decides).
- **Inputs:** all handoff files to date; ID convention.
- **Outputs:** updated matrix; `trace/report-<stage>.md` (forward gaps: upstream items with no downstream realization; backward gaps: downstream items with no upstream justification; changed-upstream impact list).
- **ACCEPTANCE:** [ ] 100% of current-stage items have >=1 upstream link or an explicit `justification: new-<reason>`; [ ] every upstream `must` item has a downstream link or a recorded deferral; [ ] report is regenerable from files alone.
- **REFUSAL:** *blocked:* items lacking IDs; *rejected:* duplicate/reused IDs, IDs renamed across versions without mapping; *out_of_scope:* editing items to "make the trace pass".
- **Anti-patterns:** trace by fuzzy text similarity (LLM guesses links); matrix maintained in chat memory; trace done only at the end (gaps discovered too late).
- **Handoffs:** invoked by each orchestrator before its exit gate; its report is a required input to the critic.

### Role G — Shared-pool Cross-cutting Reviewer (security, privacy, a11y, SRE, FinOps, analytics)
- Covered in depth in axis 06; here only the *agent-design* aspects. Stage: shared, invoked by routing.
- **Mission:** Apply one lens to one stage's artifact and return findings/requirements in that lens only.
- **Design rules:** one lens per agent (no "god reviewer"); each preloads its own lens skill + a **stage-specific** checklist section (security at PRD = abuse cases & data classification; at architecture = threat model/STRIDE; at tasks = security tasks & DoD); invoked only when the routing condition holds (e.g., personal data present -> privacy) [WEB:building-effective-agents "routing"]; read-only + write to its own findings file.
- **REFUSAL:** *out_of_scope:* making product trade-offs or architecture choices outside its lens; *blocked:* stage artifact lacks the facts its lens needs (e.g., no data inventory) -> returns the specific missing facts as questions.

---

## Implications for agentic personas

### What to split / merge
- **Split by context need and tool privilege, not by job title.** HumanLayer's "frontend/backend engineer subagents don't work; subagents are for context control" [LOCAL:skill-issue-...md:388-392] plus Cognition's coherence argument -> split read-heavy research and independent lenses into workers; keep coherent decision-making (PRD narrative, architectural decisions) in the orchestrator or a single synthesizer.
- **Always split generator from evaluator** (harness design post; Huang et al. on intrinsic self-correction). The critic is a separate subagent with its own context and ideally its own preloaded rubric skill.
- **Merge verifier logic into scripts/hooks** wherever deterministic; an LLM verifier only for summarizing results.
- **One parameterized critic vs four stage critics:** prefer one `stage-critic` agent file + four stage rubric skills if the critique procedure is identical; separate files only if tools/model differ. Fewer agent descriptions also reduces delegation confusion and context cost [LOCAL:analysis-research-subagent-best-practices.md:172-174].
- **Synthesizer is optional;** add it only if consolidation would push the orchestrator past ~40% context utilization ("smart zone") [LOCAL:dev/research/2026-04-25-harness-engineering-research.md:627].
- **Stage orchestrators are main-thread agents** (`claude --agent`), so they are the only layer that can spawn; workers cannot nest. Anything needing nested delegation (e.g., security reviewer wanting its own researchers) must be flattened: the orchestrator spawns both and passes results along, or the specialist uses preloaded skills instead [LOCAL:creating-custom-subagents.md:666].

### What LLMs get wrong here (and the countermeasure)
| MAST mode / known failure | Where it bites in this pipeline | Countermeasure (gate or contract) |
|---|---|---|
| FM-1.1 disobey task spec | Worker writes beyond its section | Brief "boundaries" + critic criterion "no out-of-brief content" |
| FM-1.2 disobey role spec / CAMEL role flip | Critic rewrites the artifact; PRD orchestrator designs architecture | Tool scoping (critic has no Write except its critique path; enforce with PreToolUse hook); explicit out_of_scope list |
| FM-1.3 step repetition | Re-running the same research worker | Orchestrator plan file with status per brief; resume reads it |
| FM-1.4 loss of history | New-window stages forget prior decisions | Decision log + handoff manifest are the only memory; entry gate reads them |
| FM-1.5 unaware of termination | Endless critic loop | Max iterations (e.g., 2-3); `maxTurns` on every agent; on exhaustion end `blocked`/`rejected` with record |
| FM-2.2 fail to ask for clarification | Worker invents personas/metrics | Return contract has mandatory `open_questions`; "no guessing" rule; ChatDev dehallucination |
| FM-2.4 information withholding | Worker drops caveats in summary | Return contract fields `assumptions`, `limitations`; files are source of truth, not summaries |
| FM-2.5 ignored other agent's input | Orchestrator ignores critic finding | Acceptance item "every finding dispositioned (fixed/deferred/disputed with reason)" |
| FM-2.6 reasoning-action mismatch | Says "validated IDs" but didn't run check | Verifier output file required as evidence |
| FM-3.1 premature termination | Handoff written before critic pass | `Stop` hook / exit gate checks critic verdict file exists and = pass |
| FM-3.2/3.3 no or incorrect verification | LLM "looks fine" | Deterministic verifier + rubric critic with evidence pointers |
| Judge biases (position/verbosity/self-enhancement) | Critic prefers longer PRD | Rubric with anchors; "length is not a criterion"; separate model or at least separate context; swap/second sample for binary gates |
| Persona placebo | "You are a world-class PM" adds nothing | Spend tokens on procedure, checklists, refusal rules, schema |
| Over-delegation | Orchestrator spawns many workers for a tiny idea | Effort-scaling table in orchestrator prompt; `Agent(...)` allowlist |

### What must be a hard gate (not a prompt suggestion)
1. **Entry gate:** upstream handoff exists, schema-valid, upstream exit verdict = pass, no `must-answer-before:<stage>` open questions. Deterministic first; LLM substance check second. Outcome is one of `accept | blocked | rejected | out_of_scope` written to `handoff/<stage>/entry-gate.md`.
2. **Exit gate:** verifier pass AND traceability report with zero blocking gaps AND critic verdict pass on all hard criteria. Enforce with a `Stop` hook or a final Bash check in the orchestrator's SOP; prompts alone are not enough (FM-3.1).
3. **Write scope:** each agent writes only under its own path (hook-enforced `PreToolUse` matcher on Write/Edit, like `dreamer.md`'s validate script) [LOCAL:ai/agents/dreamer.md].
4. **Termination:** `maxTurns` on every agent + max critic iterations in the SOP.
5. **Upstream immutability:** no stage edits another stage's handoff; changes go through a `rejected` record that a human routes back.

### Persona prompt shape (recommended)
- 2-4 lines identity (role, stage, who it serves) — framing only.
- Mission + OWNS / DOES NOT OWN.
- SOP: numbered steps with explicit gate points (MetaGPT).
- Acceptance checklist (what "done" means) and refusal taxonomy with concrete triggers.
- Output schema + exact paths.
- Calm language; avoid "CRITICAL/MUST" shouting [LOCAL:analysis-research-subagent-best-practices.md:176-178]; explain *why* a rule exists (Claude generalizes from reasons) [LOCAL:claude-prompting-best-practices.md (general guidance) — UNVERIFIED line ref].

---

## Subagent file contract

### Recommended frontmatter per role type

| Role | `tools` (least privilege) | `model` | `effort` | `maxTurns` | Other |
|---|---|---|---|---|---|
| Stage orchestrator (main thread via `claude --agent`) | `Agent(<stage workers>, stage-critic, handoff-verifier, traceability-keeper, <shared-pool names>), Read, Write, Edit, Glob, Grep, Bash` | `opus` (planning, consolidation, judgment) | `high` | 60-120 (it runs the whole stage) | `hooks:` Stop/PreToolUse to enforce exit gate and write scope; `skills:` stage SOP + handoff schema; no `memory` (handoffs are the memory) |
| Worker specialist (research/analysis) | `Read, Grep, Glob, Write` (+ `WebSearch, WebFetch` only for research workers) | `sonnet` default; `opus` for architecture-decision workers | `medium` (`high` for architecture/ADR) | 20-40 | `skills:` domain template + checklist; write path constrained by hook |
| Critic / evaluator | `Read, Grep, Glob, Write` (Write only for critique file; hook-restricted) | `opus` or a different model family/tier from the generator where possible (self-enhancement bias) | `high` | 15-30 | `skills:` stage rubric; never `memory` (avoid drift in the bar across runs unless curated) |
| Verifier | `Read, Glob, Grep, Bash` | `haiku` (mechanical) | `low` | 5-10 | Prefer the check as a script; agent only runs and reports it |
| Synthesizer | `Read, Glob, Grep, Write, Edit` | `opus` (coherence) | `high` | 20-40 | `skills:` template + glossary |
| Traceability keeper | `Read, Glob, Grep, Write, Bash` | `sonnet` (or `haiku` if fully scripted) | `medium` | 15-25 | Owns only `trace/`; hook-restricted |
| Shared-pool lens reviewer | `Read, Grep, Glob, Write` | `sonnet` (security/privacy may justify `opus`) | `medium`-`high` | 15-30 | `skills:` lens checklist with per-stage sections |

Notes:
- `Agent(type)` allowlists only matter for main-thread agents; omit `Agent` entirely in workers (they cannot spawn anyway) [LOCAL:creating-custom-subagents.md:295].
- Do not enable `memory` on "read-only" roles without noting it auto-grants Read/Write/Edit [LOCAL:creating-custom-subagents.md:391].
- `skills:` must be listed explicitly; subagents do not inherit the parent's skills [LOCAL:creating-custom-subagents.md:226,358]. Put templates/checklists in skills so the agent body stays short and the same rubric is reused across stages.
- Avoid `background: true` for any worker that may need to return `blocked` with questions to a human-facing flow — background agents auto-deny unapproved tools and cannot ask questions [LOCAL:creating-custom-subagents.md:601]. Background is fine for parallel read-only research.
- `isolation: worktree` is unnecessary for document-producing stages; consider it only in the Tasks stage if workers touch code.
- `permissionMode: plan` should not be used for unattended workers (they block waiting for approval) [UNVERIFIED for local subagents; documented for remote child sessions].
- Plugin-distributed agents lose `hooks`, `mcpServers`, `permissionMode` — if hook-enforced gates matter, ship agents in `.claude/agents/` [LOCAL:creating-custom-subagents.md:188].

### Description-writing rules (reliable delegation)
1. Lead with **what it does + artifact it produces**, then **when to use** ("Use when the <stage> orchestrator needs <X> from <inputs>"), then **when not to** ("Not for <adjacent role>").
2. Name the **trigger nouns** the orchestrator will use in briefs (e.g., "non-functional requirements", "NFR", "SLO") so routing by description matches.
3. One responsibility per description; if you need "and" twice, split the agent.
4. Avoid shouting ("MUST USE PROACTIVELY"); newer models over-trigger on it [LOCAL:analysis-research-subagent-best-practices.md:176-178]. Use "Use proactively after..." only where proactive use is genuinely wanted (e.g., verifier after any handoff write).
5. Mention the stage(s) explicitly ("PRD stage only") so the wrong orchestrator does not route to it — and back it with the `Agent(...)` allowlist, which is the real control.
6. Keep descriptions short; all descriptions consume context in every session where they load [LOCAL:analysis-research-subagent-best-practices.md:172-174].

Example: `description: Writes measurable non-functional requirements (NFR-* IDs) for the PRD from discovery handoff and PRD draft. Use when the prd-orchestrator needs performance, availability, scalability or compliance targets. Not for architecture tactics or security threat modeling.`

### Brief contract (orchestrator -> worker)
Required fields (from Anthropic research system + harness design "sprint contract"):
```
objective:        one sentence, outcome not activity
stage / role:     e.g. prd / nfr-writer
inputs:           [paths]  (only these; nothing from orchestrator chat is visible)
output:           path + template/skill name + ID prefix
boundaries:       in-scope / explicitly out-of-scope
tools_guidance:   which sources/tools to prefer; what not to search
budget:           max tool calls or turns; effort hint
done_criteria:    checklist the critic will apply (fixed before work starts)
known_context:    decisions already made upstream that must not be revisited
return_format:    the return contract below
```

### Return contract (worker -> orchestrator)
Keep the return small (context firewall); the file is the source of truth.
```
status:            done | blocked | rejected | out_of_scope
files_written:     [path#ID-range]
summary:           <= 10 lines, decisions and why
self_check:        [{criterion, pass|fail, evidence}]
open_questions:    [{id, question, blocking: yes|no, needed_by_stage}]
assumptions:       [{id, assumption, risk_if_wrong}]
refusal_reason:    required if status != done (which check failed, what input is needed)
confidence:        low | medium | high  (with one-line why)
```

### Context-isolation rules
1. **Workers see only what the brief names.** The parent conversation is invisible; anything not in the brief or files does not exist for the worker [LOCAL:analysis-research-subagent-best-practices.md:166 (anti-pattern 8)].
2. **Files over messages.** Workers write artifacts to disk and return pointers; orchestrator reads files selectively instead of accumulating full outputs in context [WEB:multi-agent-research-system; LOCAL:harness-engineering.md:62-64].
3. **Critic isolation:** critic receives artifact + rubric + upstream handoff, never the producer's rationale or the orchestrator's opinion (anti-conformity, anti-self-enhancement).
4. **Lens isolation:** shared-pool reviewers do not see each other's findings in the same pass (avoids anchoring; harness-engineering least-authority example) [LOCAL:harnessengineering-building-...md:330-343]; orchestrator reconciles.
5. **Stage isolation:** each stage starts in a fresh session; its only inputs are the upstream handoff directory and shared `trace/`. No reliance on CLAUDE.md for stage state (CLAUDE.md loads in every `--agent` session [LOCAL:creating-custom-subagents.md:580], so keep pipeline-wide conventions there, not run state).
6. **Parallelize reads, serialize decisions.** Parallel workers only on independent sections; anything with implicit coupling goes through one agent [WEB:https://cognition.com/blog/dont-build-multi-agents].
7. **Silent success, verbose failure** in verifier/hook output returned to the orchestrator [LOCAL:harness-engineering.md:95].

---

## Sources

1. Hong, S. et al. "MetaGPT: Meta Programming for a Multi-Agent Collaborative Framework." ICLR 2024. https://arxiv.org/abs/2308.00352 (abstract via search snippet; arXiv blocked).
2. IBM. "What is MetaGPT?" https://www.ibm.com/think/topics/metagpt (search result).
3. Qian, C. et al. "ChatDev: Communicative Agents for Software Development." ACL 2024. https://alphaxiv.org/paper/2307.07924 (snippet).
4. Li, G. et al. "CAMEL: Communicative Agents for 'Mind' Exploration of Large Language Model Society." NeurIPS 2023. https://www.camel-ai.org/ ; inception prompting discussion: https://github.com/microsoft/autogen/issues/514 (snippet).
5. Chen, W. et al. "AgentVerse: Facilitating Multi-Agent Collaboration and Exploring Emergent Behaviors." ICLR 2024. https://www.alphaxiv.org/abs/2308.10848 (snippet).
6. Schluntz, E. & Zhang, B. "Building effective agents." Anthropic, 2024. https://www.anthropic.com/engineering/building-effective-agents (read).
7. Anthropic. "How we built our multi-agent research system." 2025. https://www.anthropic.com/engineering/multi-agent-research-system (read).
8. Rajasekaran, P. "Harness design for long-running application development." Anthropic, 24 Mar 2026. https://www.anthropic.com/engineering/harness-design-long-running-apps (read).
9. Cemri, M., Pan, M. Z., Yang, S. et al. "Why Do Multi-Agent LLM Systems Fail?" NeurIPS 2025 D&B. https://arxiv.org/pdf/2503.13657 (snippet); failure-mode list: https://github.com/roanbrasil/agents-integration-patterns/blob/main/patterns/FAILURE-MAP.md (read); category shares: https://futureagi.substack.com/p/why-do-multi-agent-llm-systems-fail (snippet, secondary).
10. Zheng, L. et al. "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena." NeurIPS 2023. https://arxiv.org/pdf/2306.05685 (snippet).
11. Huang, J. et al. "Large Language Models Cannot Self-Correct Reasoning Yet." ICLR 2024. https://www.semanticscholar.org/paper/6d4bacb69923e1e94fb4de468b939ce6db32fb51 ; https://liner.com/review/large-language-models-cannot-selfcorrect-reasoning-yet (snippets).
12. Madaan, A. et al. "Self-Refine: Iterative Refinement with Self-Feedback." NeurIPS 2023 [BOOK].
13. Shinn, N. et al. "Reflexion: Language Agents with Verbal Reinforcement Learning." NeurIPS 2023 [BOOK].
14. Zheng, M., Pei, J., Logeswaran, L., Lee, M., Jurgens, D. "When 'A Helpful Assistant' Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of LLMs." Findings of EMNLP 2024 (originally "Is 'A Helpful Assistant' the Best Role...", 2023). https://arxiv.org/abs/2311.10054 ; https://www.academia.edu/122983308 (snippets).
15. Yan, W. "Don't Build Multi-Agents." Cognition, June 2025. https://cognition.com/blog/dont-build-multi-agents (search result).
16. Local: /home/user/ai-study-library/ai/docs/claude-code/subagents/creating-custom-subagents.md.
17. Local: /home/user/ai-study-library/ai/docs/analysis/analysis-research-subagent-best-practices.md.
18. Local: /home/user/ai-study-library/ai/docs/general-llm/subagents/research-subagent-best-practices.md.
19. Local: /home/user/ai-study-library/ai/docs/claude-code/claude-prompting-best-practices.md.
20. Local: /home/user/ai-study-library/ai/docs/harness-engineering/harness-engineering.md; harnessengineering-building-the-operating-system-for-autonomous-agents.md; skill-issue-harness-engineering-for-coding-agents.md.
21. Local: /home/user/ai-study-library/ai/docs/spec-driven-development/README.md; spec-driven-development-arxiv.md.
22. Local: /home/user/ai-study-library/dev/research/2026-04-25-harness-engineering-research.md.
23. Local: /home/user/ai-study-library/ai/agents/rubber-duck.md; /home/user/ai-study-library/ai/agents/dreamer.md.
24. Local: /home/user/ai-study-library/ai/docs/claude-code/subagents/claude-orchestrate-of-claude-code-sessions.md (agent teams vs subagents; consulted for headings only).

---

## Verification log

Verifier pass on 2026-10-02. arxiv.org, Semantic Scholar API, aclanthology.org and iclr.cc were blocked, so paper checks relied on search-result abstracts.

**Confirmed online:**
- Anthropic, "Building effective agents" (Erik Schluntz & Barry Zhang, 19 Dec 2024). Confirmed:
  - the workflow vs agent definitions;
  - parallelization's two variants, sectioning and voting;
  - evaluator-optimizer "clear evaluation criteria ... measurable value" and its two signs of fit;
  - the three principles: simplicity, transparency, and an ACI built through documentation and testing.
- Anthropic, "How we built our multi-agent research system" (13 Jun 2025). Confirmed:
  - about 4x tokens for agents and about 15x for multi-agent;
  - token usage explains 80% of BrowseComp variance, and three factors explain 95%;
  - effort-scaling tiers: 1 agent with 3-10 calls, 2-4 subagents with 10-15 calls each, more than 10 subagents;
  - the 50-subagent failure;
  - writing outputs to the filesystem to avoid the "game of telephone";
  - the judge rubric criteria and 0.0-1.0 score;
  - the brief contents: objective, output format, tool/source guidance, and boundaries.
- Anthropic, "Harness design for long-running application development" (Prithvi Rajasekaran, 24 Mar 2026). Confirmed:
  - self-evaluation leniency;
  - "tuning a standalone evaluator to be skeptical turns out to be far more tractable";
  - per-criterion hard thresholds;
  - sprint contracts;
  - file-based communication;
  - the planner kept to product context.
- MAST (Cemri et al.):
  - 14 modes in 3 categories, 150 traces, kappa 0.88, 1,642 traces;
  - category shares of 41.8% and 36.9% from search results; 21.3% is the remainder.
- Zheng et al. MT-Bench: position, verbosity and self-enhancement biases, plus over 80% agreement, equal to human-human agreement. Upgraded from UNVERIFIED.
- Huang et al. (ICLR 2024): self-correction without external feedback struggles or degrades, and earlier gains came from oracle labels.
- Persona paper (Zheng, Pei, Logeswaran, Lee, Jurgens; Findings of EMNLP 2024): 162 roles across 6 relationship types and 8 domains; the persona effect is largely random.
- Cognition (Walden Yan, June 2025):
  - the principles "Share context" and "Actions carry implicit decisions";
  - the Flappy Bird example.
- Local corpus. `creating-custom-subagents.md` lines 5, 19, 188, 213-232, 271-295, 358, 387-391, 574-580, 601, 646-661 and 666 all match. Specifically:
  - the frontmatter fields;
  - the `Agent(...)` allowlist applies only to the main thread, and subagents cannot spawn subagents;
  - `--agent` replaces the system prompt while CLAUDE.md still loads;
  - memory auto-enables Read/Write/Edit and injects the first 200 lines;
  - background subagents auto-deny unapproved tools, and their clarifying-question calls fail.
- Also matched:
  - `claude-prompting-best-practices.md`: "Give Claude a role" at line 85, self-check at line 430, subagent overuse at lines 547-560;
  - `analysis-research-subagent-best-practices.md`: prompt skeleton, >80% confidence filter, and anti-patterns table, including "CRITICAL/MUST" over-triggering;
  - `harness-engineering.md` lines 62-64 and 85-95;
  - `harnessengineering-building-...md` lines 59-62 and 330-343;
  - `skill-issue-...md`, HumanLayer section around lines 388-392;
  - harness research: <40% smart zone around line 626;
  - `ai/agents/rubber-duck.md` and `dreamer.md` frontmatter. Note that dreamer uses `effort: xhigh`, a value the local subagent doc does not list.

**Corrected:**
- MAST "1,600+ traces" is now the exact figure, 1,642.
- Huang et al. The 8.8% / 7.0% flip rates could not be confirmed. I removed them from the claim and marked them UNVERIFIED with a do-not-cite note.
- Persona paper, 2023 preprint. Its counts (3 LLMs, 2,457 questions) are downgraded to UNVERIFIED. The source says "8 domains of expertise", not "8 occupation types". "Slightly negative" was our gloss, and I replaced it with the paper's finding that persona effects are largely random.
- Harness design. Added the author's full name and date. The planner claim now quotes the source's instruction.
- Cognition. Added the publication month.

**Left as tagged (not re-verified online):**
- MetaGPT, ChatDev, CAMEL and AgentVerse section numbers and details. Venues are correct by my knowledge: ICLR 2024, ACL 2024, NeurIPS 2023 and ICLR 2024.
- MAST FM-x.y list (the secondary GitHub source matches my knowledge of the paper).
- MAST §6 magnitude.
- Self-Refine and Reflexion (NeurIPS 2023).
- MT-Bench §3.4 mitigations.
- `permissionMode: plan` for local subagents.
