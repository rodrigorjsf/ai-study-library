# Raw research — Delivery planning, tasks & test strategy

Axis: turning an accepted PRD + Architecture handoff into an ordered, implementable task set (for human or coding-agent execution) plus a test strategy. Pipeline stage owned: **tasks** (stage 4). Several roles also contribute to **prd** (acceptance criteria / examples) and **architecture** (testability, contract boundaries).

Source-tag legend: `[WEB:<url>]` read/confirmed online during this session; `[BOOK:...]` from a well-known book; `[LOCAL:<path>]` read from the local corpus; `[UNVERIFIED]` not confirmed. Note: the egress proxy blocked most primary sites this session (mountaingoatsoftware.com, humanizingwork.com, xp123.com, martinfowler.com, scrumguides.org, dora.dev, cucumber.io, docs.pact.io, dannorth.net, lisacrispin.com, wikipedia). Where those were the natural source, the claim is tagged BOOK or UNVERIFIED rather than WEB, unless a search result confirmed it.

---

## Literature & frameworks

### 1. Jeff Patton — *User Story Mapping* (2014)
- A story map arranges work as a **backbone** (left-to-right sequence of user activities / big steps of the narrative flow) with **user tasks** under each activity, and details/alternatives stacked vertically by priority. [BOOK:Patton, User Story Mapping, 2014, ch.1-3]
- The map is sliced **horizontally into releases**: the top slice across the whole backbone is the smallest end-to-end product that lets a user complete the journey (Patton's "minimum viable product release" / first slice); later slices add depth. [BOOK:Patton, 2014, ch.1-2]
- The first slice is functionally a **walking skeleton** at the product level — thin across every activity rather than complete in one. [BOOK:Patton, 2014]
- Mindset: "stories are for telling, not writing" — the card is a placeholder for a conversation; shared understanding is the goal, not documents. [BOOK:Patton, 2014, ch.2 — paraphrased]
- Persona implication: the tasks stage should start from a map (activity -> task -> slice) and refuse to produce a flat backlog without a release-slice boundary; each slice states the outcome/learning it targets.
- Quality bar: every story in slice 1 is traceable to a backbone activity; no backbone activity is empty in slice 1 (otherwise the journey cannot be completed end-to-end).

### 2. Mike Cohn — *User Stories Applied* (2004) and *Agile Estimating and Planning* (2005)
- Story template popularized: "As a <role>, I want <goal> so that <benefit>"; Ron Jeffries' 3Cs (Card, Conversation, Confirmation) — the Confirmation is the acceptance tests. [BOOK:Cohn, User Stories Applied, 2004, ch.1-2]
- Acceptance tests are written on the back of the card / attached to the story *before* development; they are how the customer confirms the story is done. [BOOK:Cohn, 2004, ch.6]
- Estimating: relative sizing in story points or ideal days; velocity as an empirical planning input; "planning poker" (from James Grenning) for consensus. [BOOK:Cohn, Agile Estimating and Planning, 2005, ch.4-6,11]
- Plans at multiple levels (release plan vs iteration plan); a release plan is a prioritized set of stories fitted to velocity with a buffer for uncertainty. [BOOK:Cohn, 2005, ch.13-17]
- Test automation pyramid (unit base, service middle, UI tip) introduced by Cohn in *Succeeding with Agile* (2009). [BOOK:Cohn, Succeeding with Agile, 2009, ch.16]
- Persona implication: estimation for agents is less about velocity and more about **size caps** (diff size, files touched, context budget); retain relative sizing only as a split trigger.

### 3. Bill Wake — INVEST (2003) and SMART tasks
- INVEST: **I**ndependent, **N**egotiable, **V**aluable, **E**stimable, **S**mall, **T**estable — a checklist for good stories. [BOOK: Wake, "INVEST in Good Stories, and SMART Tasks", xp123.com, 2003; WEB:https://agilealliance.org/glossary/invest/ (search result corroborates article title, year and acronym)]
- Wake pairs INVEST (stories) with SMART (tasks): **S**pecific, **M**easurable, **A**chievable, **R**elevant, **T**ime-boxed. [WEB:https://t2informatik.de/en/smartpedia/invest-principle/ (search result, secondary; xp123.com itself not read)]
- "Negotiable" means the story is not a contract; details emerge in conversation — tension with spec-driven development, where the task *is* a contract. For agents, negotiation must happen upstream (PRD/architecture), so tasks become non-negotiable but stories remain negotiable during splitting.
- "Testable" is the most directly gateable letter: if you cannot write an acceptance test, the story is not understood.
- Persona implication: INVEST is the story-level gate; SMART is the task-level gate. Treat "Independent" loosely (Wake himself acknowledges dependencies can't always be removed) but require explicit dependency declarations.

### 4. Richard Lawrence (Humanizing Work) — Story splitting patterns
- Nine patterns (2009 blog, later "Humanizing Work Guide to Splitting User Stories" and flowchart): workflow steps; business rule variations; major effort; simple/complex; variations in data; data entry methods; defer system qualities (performance etc.); operations (e.g., CRUD); break out a spike. [BOOK/UNVERIFIED: Lawrence & Green, humanizingwork.com — blocked this session; names recalled]
- Process: (1) check the story against INVEST (except Small) first; (2) apply patterns; (3) evaluate split candidates — prefer the split that lets you **deprioritize or throw away** a part, and the split that yields **roughly equal-sized** pieces. [UNVERIFIED — recalled from the guide]
- "Meta-pattern": find the core complexity, identify the variations, reduce to one variation (thin slice). [UNVERIFIED]
- Anti-pattern explicitly warned against: splitting by architectural layer (UI story, DB story) — produces stories that deliver no value independently. [BOOK:Cohn, 2004, ch.2 (cake-layer analogy); UNVERIFIED for Lawrence]
- Persona implication: the decomposition worker should name the pattern used for every split ("split_by: business_rule_variation") so a critic can check it isn't a horizontal split in disguise.

### 5. Mike Cohn — SPIDR
- Five splitting techniques: **S**pikes, **P**aths, **I**nterfaces, **D**ata, **R**ules. [WEB:https://ascendle.com/ideas/spidr-an-alternative-method-for-splitting-user-stories/ (search result summary); WEB:https://socadk.github.io/design-practice-repository/activities/DPR-StorySplitting.html]
- Spike = research to make the team smarter about implementing a story; use when other techniques can't split due to unknowns. Paths = each branch of a flowchart/activity diagram can become a story. Interfaces = split by UI element/channel/device. Data = split by data subsets, starting with high-risk/high-value data. Rules = defer or separate complex business rules. [WEB:search summary, sources above]
- Cohn recommends spikes as a *last* resort because they produce knowledge, not shippable value. [UNVERIFIED]
- Persona implication: SPIDR is compact enough to embed verbatim in a decomposer prompt; Lawrence's nine patterns as extended reference.

### 6. Vertical slicing / Alistair Cockburn walking skeleton / Pragmatic Programmer tracer bullets
- Walking skeleton (Cockburn, *Crystal Clear*, 2004): a tiny implementation of the system that performs a small end-to-end function, linking the main architectural components; architecture and functionality then evolve in parallel. [BOOK:Cockburn, Crystal Clear, 2004, "Walking Skeleton" strategy]
- Tracer bullets (Hunt & Thomas, *The Pragmatic Programmer*, 1999/2019): build a thin, production-quality path through all layers to get immediate feedback on whether you're hitting the target; unlike **prototypes**, tracer code is kept; prototypes are disposable and explore a single aspect. [BOOK:Hunt & Thomas, The Pragmatic Programmer, 20th anniv. ed. 2019, Topics 12-13 "Tracer Bullets", "Prototypes and Post-it Notes"]
- Freeman & Pryce (*GOOS*, 2009) operationalize: first test is an end-to-end test against the walking skeleton including build, deploy, and test infrastructure. [BOOK:Freeman & Pryce, Growing Object-Oriented Software, Guided by Tests, 2009, ch.4]
- Vertical slice = a change that cuts through all layers needed to deliver observable behavior; horizontal (layer) tasks are acceptable only inside a slice, never as the unit of value.
- Persona implication: task set **must** start with a walking-skeleton slice (build + deploy + one end-to-end test path through the architecture's main components) unless the codebase already has one. Spikes must be timeboxed and declare their output (a decision/ADR), and their code is disposable.

### 7. BDD / Gherkin (Dan North; Cucumber) and Gojko Adzic
- Dan North, "Introducing BDD" (2006): test names as sentences using "should"; shift from "test" to "behaviour"; story template "As a / I want / So that" and acceptance criteria as **Given / When / Then** scenarios. (Correction: the "In order to / As a / I want" variant is Chris Matts' Feature Injection reformulation, popularised c. 2008 by Liz Keogh and others, not part of North's 2006 article.) [BOOK: North, "Introducing BDD", Better Software, March 2006 — dannorth.net blocked; venue/date and Matts attribution corroborated via search results, e.g. WEB:https://lizkeogh.com/2008/05/14/rip-as-a-i-want-so-that/]
- Gherkin keywords: Feature, Rule, Background, Scenario (Example), Scenario Outline + Examples, Given/When/Then/And/But. [UNVERIFIED: cucumber.io reference blocked; recalled]
- Good-scenario heuristics: declarative (business intent) over imperative (click/type); one behavior per scenario; few steps (~3-5); avoid UI coupling; ubiquitous language. [BOOK:Adzic, Specification by Example, 2011; Smart, BDD in Action, 2014/2023 — paraphrased]
- Gojko Adzic, *Specification by Example* (2011): key process patterns — derive scope from goals; specify collaboratively; illustrate using **key examples**; refine the specification; automate validation without changing specifications; validate frequently; evolve a **living documentation** system. [BOOK:Adzic, Specification by Example, 2011, ch.3-11]
- Adzic, *Impact Mapping* (2012): Goal -> Actors -> Impacts -> Deliverables; deliverables are only justified by an impact on an actor toward a goal. [BOOK:Adzic, Impact Mapping, 2012]
- Related: "Example Mapping" (Matt Wynne, "Introducing Example Mapping", Cucumber blog, Dec 2015): story (yellow), rules (blue), examples (green), questions (red); red-card questions must be answered before the story is ready. [WEB:https://cucumber.io/blog/bdd/example-mapping-introduction/ (search result summary)]
- Persona implication: Given/When/Then is the native acceptance-criteria format for tasks consumed by agents (Kiro uses exactly "As a..." + GIVEN/WHEN/THEN) [LOCAL:ai/docs/spec-driven-development/spec-driven-development-variant.md:57]. Example Mapping's "red card" count is a natural Definition-of-Ready gate.

### 8. Definition of Ready / Definition of Done (Scrum Guide 2020)
- Scrum Guide 2020: "The Definition of Done is a formal description of the state of the Increment when it meets the quality measures required for the product." The moment a PBI meets the DoD, an Increment is born. [WEB:https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf (quote confirmed via search result)]
- DoD is a **commitment** of the Increment (2020 change); work that doesn't meet DoD cannot be released or even presented at Sprint Review; it returns to the Product Backlog. [BOOK:Schwaber & Sutherland, Scrum Guide 2020, "Increment"]
- The Scrum Guide does **not** define a Definition of Ready; it only says PBIs that can be Done within one Sprint are deemed ready for selection after refinement. DoR is community practice and criticized as a potential stage-gate / waterfall-ism. [BOOK:Scrum Guide 2020 "Product Backlog"; UNVERIFIED for criticism source]
- Persona implication: in a pipeline, DoR is exactly the **ENTRY gate** of the tasks stage (and of each task handed to a coding agent); DoD is the per-task completion contract plus the stage EXIT gate. Make DoR minimal and objective to avoid bureaucracy.

### 9. Work Breakdown Structure, dependency mapping, critical path
- WBS (PMBOK): hierarchical decomposition of total scope into deliverables; **100% rule** — children sum to exactly 100% of parent scope, no more no less; decompose deliverables (nouns), not activities; lowest level = work package. [BOOK:PMI, PMBOK Guide 6th ed., 2017, §5.4; Practice Standard for WBS]
- Critical Path Method: longest chain of dependent activities defines minimum duration; zero-float tasks are critical; dependency types FS/SS/FF/SF. [BOOK:PMBOK 6th ed., §6.5 Develop Schedule (CPM); dependency types / PDM are in §6.3 Sequence Activities]
- Dependency mapping in agile: SAFe program board / dependency "red strings"; minimize cross-team dependencies by slicing. [BOOK:Leffingwell, SAFe reference; UNVERIFIED detail]
- Persona implication: for agent execution, "critical path" = longest chain in a task DAG; parallelizable tasks must touch disjoint files. Spec Kit's `[P]` marker encodes exactly this: "Include ONLY if task is parallelizable (different files, no dependencies on incomplete tasks)" (exact wording corrected at verification; the earlier quote was not in the source). [WEB:https://raw.githubusercontent.com/github/spec-kit/main/templates/commands/tasks.md]
- 100% rule maps to a **traceability coverage** check: every PRD requirement and architecture component maps to >=1 task; no task maps to nothing (gold plating).

### 10. Donald Reinertsen — *The Principles of Product Development Flow* (2009)
- Reduce batch size: smaller batches reduce cycle time, variability, risk, and overhead per feedback; batch size is the cheapest lever. [BOOK:Reinertsen, 2009, ch.5]
- Control WIP / queues: queues are the root cause of most economic waste in product development and are invisible; use WIP constraints. [BOOK:Reinertsen, 2009, ch.3,6]
- Cost of Delay and WSJF (Weighted Shortest Job First = CoD / duration) for sequencing. [BOOK:Reinertsen, 2009, ch.2,7]
- Fast feedback: value of information is highest early; sequence to buy information cheaply. [BOOK:Reinertsen, 2009, ch.8]
- Persona implication: task sizing rule ("one PR-sized task") and a WIP limit for parallel agents (e.g., max N concurrent coding agents per merge target). Sequence by risk-reduction/information value, then CoD.

### 11. Accelerate / DORA
- Forsgren, Humble, Kim, *Accelerate* (2018): four key metrics — deployment frequency, lead time for changes, change failure rate, time to restore; working in small batches, trunk-based development (<=3 active branches, branches lived < a day), and continuous integration predict delivery performance. [BOOK:Forsgren, Humble & Kim, Accelerate, 2018, ch.2,4]
- DORA capability "Working in small batches": features decomposed so each can be completed in hours/a day; use feature flags / dark launching to merge incomplete features. [UNVERIFIED: dora.dev blocked]
- Feature flags (Hodgson's taxonomy: release, experiment, ops, permission toggles) decouple deploy from release; release toggles should be short-lived and removed (toggle debt). [BOOK/UNVERIFIED: Pete Hodgson, "Feature Toggles", martinfowler.com, 2017 — blocked]
- Persona implication: every task must leave trunk releasable; a task that exposes incomplete behavior must declare a release flag and a removal task.

### 12. Risk-first sequencing & spikes
- Boehm's spiral model: resolve highest risks first. [BOOK:Boehm, "A Spiral Model of Software Development and Enhancement", IEEE Computer, 1988]
- Cockburn: early "walking skeleton" + "early victory" + spikes to retire technical risk. [BOOK:Cockburn, Crystal Clear, 2004]
- Spike rules: timeboxed, has a question, outputs a decision (ADR) not production code; follow-on stories are re-estimated after the spike. [BOOK:Cohn, 2005; Hunt & Thomas 2019]
- Persona implication: sequence = walking skeleton -> riskiest unknowns (from architecture risk register) -> highest-value slices -> polish. Architecture "open risks" must each have a spike or explicit acceptance.

### 13. Test strategy literature
- **Agile Testing Quadrants** (Marick 2003; Crispin & Gregory, *Agile Testing*, 2009): axes business-facing vs technology-facing and supporting-the-team vs critiquing-the-product. Q1 unit/component (tech, support); Q2 functional/story tests, examples, ATDD/SbE (business, support); Q3 exploratory, usability, UAT (business, critique); Q4 performance, load, security, "-ilities" (tech, critique). [WEB:https://www.pmi.org/disciplined-agile/agile/testingquadrants (search result); WEB:search summary of https://lisacrispin.com/agile-testing-quadrants-version-3-from-agile-testing-condensed/]
- Crispin & Gregory stress the quadrants are **not sequential** and not a staffing model; they're a thinking tool for coverage; later versions moved to "holistic testing" across the whole loop (discover, plan, build, release, observe). [BOOK:Crispin & Gregory, Agile Testing Condensed, 2019; More Agile Testing, 2014 — paraphrase]
- **Test pyramid** (Cohn 2009; Vocke "Practical Test Pyramid" 2018): many fast unit tests, fewer integration/service tests, few UI/E2E; anti-pattern "ice-cream cone"; rule of thumb: write tests with different granularity; the higher-level you go the fewer tests; push tests down the pyramid when possible and avoid duplicating coverage. [BOOK:Cohn 2009; UNVERIFIED for Vocke page (blocked)]
- **Testing trophy** (Kent C. Dodds, 2018): static analysis base, unit, a thick **integration** layer, thin E2E — "write tests, not too many, mostly integration" (Guillermo Rauch). Rationale: confidence per cost. [UNVERIFIED: kentcdodds.com blocked; recalled]
- **Risk-based testing**: allocate test effort by likelihood x impact of failure (ISTQB; ISO/IEC/IEEE 29119-1/-3 test strategy/plan concepts). [BOOK:ISTQB Foundation Syllabus v4, 2023, §5.2; ISO/IEC/IEEE 29119-3]
- **Consumer-driven contracts** (Ian Robinson, 2006; Pact): consumers publish expectations of a provider; provider verifies against all consumers' contracts in its CI; Pact Broker + "can-i-deploy" gate deploys. Best for internal service-to-service APIs you control both sides of; not a substitute for functional testing of the provider. [BOOK/UNVERIFIED: Robinson, "Consumer-Driven Contracts: A Service Evolution Pattern", martinfowler.com 2006; docs.pact.io blocked]. Spec-anchored SDD pairs OpenAPI with contract tools Pact/Specmatic. [LOCAL:ai/docs/spec-driven-development/spec-driven-development-arxiv.md:57,140]
- **Test data**: synthetic vs masked production data; builders/fixtures (Test Data Builder, Object Mother); deterministic seeds; privacy — never copy raw PII into test fixtures. [BOOK:Freeman & Pryce 2009, ch.22 "Constructing Complex Test Data" (introduces Test Data Builders); Meszaros, xUnit Test Patterns, 2007]
- **Acceptance test design**: ATDD/SbE examples written before coding; property-based tests address LLM nondeterminism by verifying spec invariants. [LOCAL:ai/docs/spec-driven-development/spec-driven-development-arxiv.md:110]

### 14. Spec-driven development & agentic task practice (local corpus + Spec Kit)
- SDD workflow: Specify -> Plan -> Tasks -> Implement; "/tasks breaks the plan into small reviewable chunks"; each task has clear objective and acceptance criteria pulled from the spec. [LOCAL:ai/docs/spec-driven-development/spec-driven-development-main.md:35,56]
- Implement in "small, validated increments — each task delivers a testable piece of functionality, enabling frequent checkpoints". [LOCAL:ai/docs/spec-driven-development/spec-driven-development-arxiv.md:91]
- Specs enable parallel agent execution on non-overlapping tasks. [LOCAL:...arxiv.md:108]
- Spec Kit task line format: `- [ ] [TaskID] [P?] [Story?] Description with file path`; e.g. `- [ ] T012 [P] [US1] Create User model in src/models/user.py`; invalid if missing ID, checkbox, story label (in story phases), or file path. Phases: Setup -> Foundational (blocking) -> one phase per user story by priority -> Polish. Tests optional unless requested; when present, "write these tests FIRST, ensure they FAIL before implementation"; each story ends with an independent-test checkpoint. [WEB:https://raw.githubusercontent.com/github/spec-kit/main/templates/commands/tasks.md; WEB:https://raw.githubusercontent.com/github/spec-kit/main/templates/tasks-template.md]
- Spec Kit `/analyze`: read-only cross-artifact check — coverage gaps (requirements with no task), ambiguity (unmeasurable adjectives, placeholders), duplication, constitution alignment (MUST violations = CRITICAL), inconsistency (terminology drift, task ordering contradictions); severities CRITICAL/HIGH/MEDIUM/LOW. [WEB:https://raw.githubusercontent.com/github/spec-kit/main/templates/commands/analyze.md] — this is essentially a ready-made **task critic** spec.
- Spec Kit plan: unresolved Technical Context fields marked "NEEDS CLARIFICATION" (blocked signal); Constitution Check gate before and after design. [WEB:https://raw.githubusercontent.com/github/spec-kit/main/templates/plan-template.md]
- Failure mode: over-ceremony — Kiro produced 4 user stories / 16 acceptance criteria for a small bug fix; review overhead scales with spec verbosity. [LOCAL:ai/docs/spec-driven-development/spec-driven-development-variant.md:105; ...-main.md:82]
- Long-running agent harness: feature list in **JSON** (category, description, verification steps, `passes: false`), because the model is less likely to inappropriately overwrite JSON than Markdown; one feature at a time; "It is unacceptable to remove or edit tests"; E2E verification via browser automation reduced premature "done" claims (source: browser automation helped Claude "identify and fix bugs that weren't obvious from the code alone"; "drastically" is our wording). Article by Justin Young, Anthropic, Nov 2025. [WEB:https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents; LOCAL:dev/research/2026-04-25-harness-engineering-research.md:647-665]
- Iron Law: no completion claims without fresh verification evidence (command + output from this run). [LOCAL:dev/research/2026-04-25-harness-engineering-research.md:688-705]
- Autonomy scales with plan detail: phased plan -> autonomous per phase; plan with file paths & function signatures -> autonomous implementation with PR review; exact specs with test cases -> fully autonomous with automated verification. [LOCAL:ai/docs/agentic-engineering/research-plan-implement-review-tyler-burleigh.md:115-120]
- RPI leverage: bad plan -> hundreds of bad lines; plan specifies exact file modifications and integration points; implementation starts in a fresh context with only the plan. [LOCAL:ai/docs/agentic-engineering/research-plan-implement-rpi.md:31-50,122-129]

#### Synthesis: what a task must contain for a CODING AGENT to execute it reliably
A task is a self-contained prompt executed in a fresh context. Minimum contract (fields), derived from the sources above:
1. **ID + title** (imperative, one outcome) and **trace links**: PRD requirement IDs / story ID, architecture component/ADR IDs.
2. **Objective / why** (1-3 sentences, the user-observable behavior or enabling capability).
3. **Scope boundary**: in-scope and explicitly out-of-scope; files/modules expected to change (exact paths), files that must NOT change (e.g., tests owned by other tasks, public contracts).
4. **Context pointers** (not pasted content): relevant spec sections, ADRs, interface contracts (OpenAPI/schema snippets quoted verbatim when they are constraints — Spec Kit requires data model constraints quoted verbatim), existing patterns to follow (file:line exemplars).
5. **Acceptance criteria** in Given/When/Then, each mapped to a named test (new or existing) — the test is the oracle.
6. **Verification commands** with expected result (e.g., `pytest tests/x -q` -> 0 failures; typecheck; lint; E2E script); test-first instruction where applicable (write failing test first).
7. **Dependencies** (task IDs that must be done; blocking/non-blocking), **parallel-safe flag** (`[P]` only if disjoint files and no incomplete dependency).
8. **Size cap**: fits one PR / one context window (heuristic: a reviewer can review the diff in one sitting; typical guidance a few hundred LOC) [UNVERIFIED numeric threshold — tune per project].
9. **Non-functional constraints** relevant to this task (security, privacy, a11y, perf budget, observability hooks) pulled from the shared cross-cutting pool.
10. **Release safety**: feature flag name + default off if behavior is incomplete; migration/rollback note for schema changes.
11. **Definition of Done** reference (shared DoD + task-specific items) and **stop conditions**: when to halt and report `blocked` instead of improvising (ambiguity in spec, needed change to a frozen contract, failing unrelated test).
12. **State fields** machine-readable (JSON/YAML): `status`, `passes`, `evidence` (command output hash/link) — the agent may flip `passes` only with evidence and may not edit acceptance tests.

---

## Real-world roles

### R1. Technical Program Manager / Delivery Manager
- **Titles:** Technical Program Manager (TPM), Delivery Manager, Engineering Program Manager, Release Train Engineer (SAFe). **Stage:** tasks (lead/orchestrator persona); light presence in architecture (dependency/risk intake).
- **Mission:** Turn an approved scope into a sequenced, dependency-aware delivery plan with explicit milestones, risks, and critical path, and keep it honest as reality changes.
- **Mindset & principles:** small batches & WIP limits [BOOK:Reinertsen 2009]; sequence by risk/information value and Cost of Delay (WSJF) [BOOK:Reinertsen 2009 ch.2]; 100% rule of scope coverage [BOOK:PMBOK 6th §5.4]; plans are hypotheses, re-plan on evidence [BOOK:Cohn 2005]; make dependencies and critical path visible [BOOK:PMBOK §6.5].
- **OWNS:** release slices/milestones, dependency DAG, critical path, sequencing rationale, risk register for delivery, RAID log, handoff assembly. **DOES NOT OWN:** what to build (PM/PRD), how to build (tech lead/architecture), the quality bar (QA lead/DoD), people management.
- **Inputs:** accepted PRD handoff (requirements with IDs, priorities, success metrics), architecture handoff (components, ADRs, interfaces, risk register, NFRs), team/agent capacity constraints, org release calendar.
- **Outputs:** delivery plan (milestones -> slices -> stories -> tasks), dependency graph (DAG, e.g., Mermaid), critical path list, RAID log (Risks, Assumptions, Issues, Dependencies), release plan with flags. Industry formats: Gantt/roadmap, SAFe program board, RAID log table.
- **ACCEPTANCE criteria:**
  - [ ] Every PRD must-have requirement ID maps to >=1 task; every task maps to >=1 requirement or an enabling/architecture item (100% rule, no orphans).
  - [ ] Dependency graph is acyclic; each dependency names a task ID; critical path is listed.
  - [ ] Slice 1 is a walking skeleton spanning all backbone activities/main components.
  - [ ] Each architecture risk marked "open" has a spike or explicit risk-acceptance with owner.
  - [ ] Each milestone has an exit criterion that is demonstrable (demo/test), not "X% complete".
  - [ ] WIP/parallelism limit stated; parallel tasks have disjoint file sets.
- **REFUSAL criteria:**
  - *blocked:* PRD lacks priorities (MoSCoW or rank) or requirement IDs; architecture handoff missing component list/interfaces; unresolved "NEEDS CLARIFICATION" markers upstream.
  - *rejected:* upstream PRD has requirements with no acceptance criteria/success metric; architecture has cyclic component dependencies or unowned open risks; scope + fixed date with no negotiable dimension (iron triangle fully fixed).
  - *out_of_scope:* deciding feature priority trade-offs (return to PRD owner); choosing technology (architecture); GTM/launch messaging.
- **Anti-patterns:** Gantt theater (precise dates on unknown work); "% complete" status; serializing everything (no parallelism) or over-parallelizing (merge conflicts); hiding risk at the end of the plan; planning by component team (horizontal).
- **Handoffs:** receives from PRD and architecture orchestrators (via handoff files); delivers to engineering/coding agents, release manager, QA lead; consults traceability owner.

### R2. Engineering Manager
- **Titles:** Engineering Manager, Software Development Manager (Amazon), Team Lead (people). **Stage:** tasks (capacity/ownership), shared (DoD policy, ways of working).
- **Mission:** Ensure the team (here: the agent fleet + human reviewers) can sustainably deliver the plan at the agreed quality, by setting capacity, ownership and engineering standards.
- **Mindset & principles:** sustainable pace [BOOK:Beck, XP Explained 1st ed. 1999 ("40-hour week"); renamed "Energized Work" in 2nd ed. 2004; also an Agile Manifesto principle, 2001]; outcomes and DORA metrics over output [BOOK:Forsgren et al. 2018]; team cognitive load as a design constraint [BOOK:Skelton & Pais, Team Topologies, 2019]; quality is not negotiable to hit dates — scope is.
- **OWNS:** capacity and assignment (which tasks a human must review vs agent-autonomous), team-level DoD contents (with QA lead), review policy, escalation. **DOES NOT OWN:** detailed decomposition (tech lead), product priority (PM), test design (QA).
- **Inputs:** delivery plan, task list with sizes/risk, autonomy policy, review capacity.
- **Outputs:** ownership/RACI matrix per task class; review & autonomy policy (e.g., "tasks touching auth require human review"); DoD baseline.
- **ACCEPTANCE criteria:** [ ] each task has an owner type (agent/human) and reviewer type; [ ] high-risk task classes (security, data migration, payments) have human review flagged; [ ] planned load <= stated capacity with buffer; [ ] DoD baseline exists and is referenced by all tasks.
- **REFUSAL criteria:** *blocked:* no capacity/review-budget info; *rejected:* plan that requires overtime/over-allocation, or that removes testing/review to meet date; *out_of_scope:* product priority calls, architecture decisions, individual performance management (not applicable to agents).
- **Anti-patterns:** treating velocity as a performance target; approving plans without slack; hero-dependence (one reviewer bottleneck).
- **Handoffs:** receives plan from TPM; delivers policy to all workers; escalation point for refusals.

### R3. Tech Lead (decomposition)
- **Titles:** Tech Lead, Staff Engineer, Lead Developer, Principal Engineer (feature lead). **Stage:** tasks (primary decomposer); consults architecture.
- **Mission:** Decompose stories into technically coherent, vertically sliced, independently verifiable tasks that respect the architecture and can be executed by a developer/coding agent without re-deriving design.
- **Mindset & principles:** vertical slices, walking skeleton first [BOOK:Cockburn 2004; Freeman & Pryce 2009]; tracer bullets vs disposable prototypes [BOOK:Hunt & Thomas 2019]; INVEST for stories, SMART for tasks [BOOK:Wake 2003]; SPIDR/Lawrence patterns for splitting [WEB:ascendle.com SPIDR]; keep trunk releasable, use flags [BOOK:Forsgren et al. 2018]; exact file paths and constraints quoted verbatim [WEB:spec-kit tasks.md].
- **OWNS:** story->task decomposition, technical sequencing within a story, file-level scope, interface/contract placement per task, spike definitions, per-task acceptance + verification commands (with QA). **DOES NOT OWN:** architecture decisions (may raise ADR change requests), product scope, release dates.
- **Inputs:** stories with acceptance criteria (PRD), architecture (component diagram, ADRs, API contracts, data model), codebase conventions / existing patterns, test strategy.
- **Outputs:** `tasks.md`/`tasks.json` in the 12-field contract above; Spec Kit-style line format for human scanning; spike cards (question, timebox, output = ADR/decision).
- **ACCEPTANCE criteria:**
  - [ ] Each task produces observable, testable change (or is an explicitly labeled enabling/setup task in a Setup/Foundational phase).
  - [ ] No task is a pure horizontal layer of a user story unless inside a slice whose last task delivers the behavior with an end-to-end test.
  - [ ] Each task lists exact paths to change; each `[P]` task has file-set disjoint from other concurrently runnable tasks.
  - [ ] Each task has >=1 Given/When/Then AC and >=1 runnable verification command.
  - [ ] Each split names the splitting pattern used.
  - [ ] Task size within cap (single PR; one context window).
  - [ ] No task requires a design decision not present in architecture (else spike or ADR request).
- **REFUSAL criteria:** *blocked:* missing interface contracts/data model for components the task touches; ambiguous AC ("fast", "user-friendly") with no metric; no codebase/convention information. *rejected:* architecture that contradicts PRD constraints; stories failing INVEST "Testable"; PRD stories that are actually tasks ("create table X"). *out_of_scope:* rewriting the architecture; changing product scope; writing the implementation code itself.
- **Anti-patterns:** layer-cake tasks (DB task, API task, UI task, each untestable alone); "implement feature X" mega-tasks; tasks that say *what file* but not *what behavior*; hidden design decisions inside tasks; spikes with no timebox or deliverable; over-decomposition (16 ACs for a bug fix) [LOCAL:...variant.md:105].
- **Handoffs:** receives from architecture handoff + PRD stories via TPM orchestrator; delivers tasks to QA lead/SDET (test mapping) and task critic; finally to coding agents.

### R4. Scrum Master / Agile Coach
- **Titles:** Scrum Master, Agile Coach, Agile Delivery Lead, Flow Coach (Kanban). **Stage:** tasks (DoR/DoD stewardship, flow); shared (process).
- **Mission:** Protect the flow and the team's working agreements: ensure items entering work are ready, items leaving are Done, and impediments/WIP are visible.
- **Mindset & principles:** DoD as commitment of the Increment [WEB:Scrum Guide 2020 PDF, quote confirmed via search]; DoR as a lightweight team agreement, not a gate for bureaucracy [BOOK:Scrum Guide 2020 has no DoR]; WIP limits and flow metrics (cycle time, throughput) [BOOK:Reinertsen 2009; Anderson, Kanban, 2010]; empiricism — inspect and adapt.
- **OWNS:** DoR and DoD documents (facilitates; team owns content), refinement facilitation, impediment log, WIP policy. **DOES NOT OWN:** backlog order (PO), technical decomposition (tech lead), test design.
- **Inputs:** team agreements, task list, DoD baseline, flow data.
- **Outputs:** DoR checklist; DoD checklist; working agreements; impediment list. Typical DoR: story has AC, is estimated/sized, dependencies identified, fits in sprint, testable, no open questions (Example Mapping red cards = 0) [UNVERIFIED for typical list source]. Typical DoD: code reviewed, tests written and passing in CI, AC verified, docs updated, deployed to staging, no new critical defects, NFRs met.
- **ACCEPTANCE criteria:** [ ] DoR has <=8 objective, checkable items; [ ] DoD items are verifiable by evidence (command output, link), not opinion; [ ] each task references DoD; [ ] WIP limit numerically stated.
- **REFUSAL criteria:** *blocked:* no team/stakeholder agreement on DoD (no baseline); *rejected:* tasks entering execution with open questions, or "done" claims with no evidence; DoD weakened mid-flight to hit a date; *out_of_scope:* prioritization, technical solutioning.
- **Anti-patterns:** DoR as a contract wall ("throw it back over"); DoD so long nobody applies it; "done-done" vs "done" ambiguity; status-meeting master.
- **Handoffs:** with TPM and QA lead; output feeds the ENTRY/EXIT gate checklists of orchestrator.

### R5. QA Lead / Test Architect
- **Titles:** QA Lead, Test Architect, Quality Engineering Lead, Test Manager. **Stage:** tasks (test strategy & plan); contributes to prd (testable ACs, examples) and architecture (testability, contract boundaries, environments).
- **Mission:** Define a risk-based test strategy that gives justified confidence in the release at sustainable cost, and ensure every requirement has an oracle.
- **Mindset & principles:** whole-team quality; quadrants as coverage thinking tool, not sequence [WEB:pmi.org testing quadrants; BOOK:Crispin & Gregory 2009, 2014]; risk-based allocation of effort [BOOK:ISTQB FL v4 §5.2]; push tests down the pyramid / mostly integration per trophy, avoid ice-cream cone [BOOK:Cohn 2009; UNVERIFIED Dodds 2018]; examples before code [BOOK:Adzic 2011]; "passing spec tests only show code matches spec, not that spec is right" [LOCAL:...arxiv.md:207] -> keep Q3 exploratory/critique.
- **OWNS:** test strategy document, risk-based test matrix, test level allocation (unit/integration/contract/E2E/NFR), environments & test data strategy, quality gates (entry/exit criteria for test), defect severity taxonomy. **DOES NOT OWN:** writing all tests (whole team/SDET/devs), product acceptance decision (PO), performance architecture (SRE pool contributes).
- **Inputs:** PRD requirements + ACs + NFRs, architecture (components, interfaces, deployment topology, data flows), risk registers (product, security, privacy), compliance constraints from shared pool.
- **Outputs:** Test Strategy (ISO/IEC/IEEE 29119-3-like sections: scope, risk analysis, test levels & types, entry/exit criteria, environments, data, tooling, metrics, responsibilities) [BOOK:ISO/IEC/IEEE 29119-3]; requirements->tests traceability matrix; quadrant coverage map; NFR test plan (perf budgets, security scans, a11y checks).
- **ACCEPTANCE criteria:**
  - [ ] Each requirement has >=1 test at the lowest effective level, mapped by ID.
  - [ ] Risk matrix (likelihood x impact) exists and high-risk items have >=2 levels of tests or an explicit compensating control.
  - [ ] All four quadrants considered; omissions justified in writing.
  - [ ] Every service boundary in architecture has a contract-test decision (CDC/provider schema test/none + why).
  - [ ] E2E tests limited to critical user journeys (list them); count justified.
  - [ ] Test data strategy names sources (synthetic/builders/masked), no raw PII, deterministic seeds.
  - [ ] Exit criteria measurable (e.g., 0 open Sev1/Sev2; all P1 AC tests green; perf p95 under budget).
- **REFUSAL criteria:** *blocked:* requirements without acceptance criteria; NFRs without numbers; no environment/deploy topology info. *rejected:* PRD ACs that are untestable or contradictory; architecture with no seam for testing (no way to stub external dependency); test plan relying only on E2E/UI. *out_of_scope:* deciding whether to ship despite known defects (PO/release decision); security pen-test execution (security pool); product UX research.
- **Anti-patterns:** test count as quality metric; coverage % as target; ice-cream cone; QA as end-of-line gate; "automation will cover it" with no oracle; duplicated tests across levels; flaky tests tolerated.
- **Handoffs:** receives PRD/arch via orchestrator; delivers strategy to SDET, tech lead (tests embedded in tasks), release manager (quality gates).

### R6. SDET (Software Development Engineer in Test)
- **Titles:** SDET, Test Automation Engineer, Quality Engineer, Software Engineer in Test (Google SET/TE historical split). **Stage:** tasks (test task authoring), execution.
- **Mission:** Turn acceptance criteria and the test strategy into executable, reliable, fast automated tests and test infrastructure tasks.
- **Mindset & principles:** ATDD — failing acceptance test first [BOOK:Freeman & Pryce 2009]; declarative Gherkin, one behavior per scenario [BOOK:Adzic 2011]; test data builders [BOOK:Freeman & Pryce 2009 ch.22]; deterministic, isolated, fast tests; contract tests over shared E2E environments for service boundaries [BOOK/UNVERIFIED:Robinson 2006]; "unacceptable to remove or edit tests" to make them pass [WEB:anthropic.com effective-harnesses].
- **OWNS:** test task definitions (test-first tasks), Gherkin feature files / acceptance test skeletons, test harness/fixtures/builders tasks, CI test stage, flakiness policy. **DOES NOT OWN:** strategy (QA lead), feature code, product acceptance.
- **Inputs:** test strategy, stories with ACs, task list, interface contracts (OpenAPI/schemas), test data policy.
- **Outputs:** `.feature` files or test specs per story; test tasks in task list (`T0xx [P] [US1] Contract test for POST /orders in tests/contract/test_orders.py`); fixture/builder modules; CI job definitions.
- **ACCEPTANCE criteria:** [ ] every AC has a named automated test or justified manual check; [ ] tests are written to fail before implementation (red evidence recorded); [ ] scenarios declarative, <=~5 steps [UNVERIFIED heuristic]; [ ] no test depends on execution order or wall-clock; [ ] contract tests exist for each consumer/provider pair flagged by QA lead; [ ] runtime budget for suite stated.
- **REFUSAL criteria:** *blocked:* AC without expected outcome; contract/schema missing; no test environment description. *rejected:* tasks asking to "update tests to pass" without spec change; ACs written imperatively against UI selectors; *out_of_scope:* deciding acceptance thresholds, implementing feature code.
- **Anti-patterns:** record-and-playback UI suites; sleeping tests; asserting on implementation details; mocking what you don't own; giant shared fixtures.
- **Handoffs:** receives from QA lead + tech lead; delivers test tasks into task list; coding agents consume.

### R7. Release Manager
- **Titles:** Release Manager, Release Engineer, Change Manager (ITIL), Deployment Lead. **Stage:** tasks (release slicing, flags, rollout); interfaces with SRE pool.
- **Mission:** Ensure each slice can be integrated, deployed and released safely, reversibly and observably, decoupling deploy from release.
- **Mindset & principles:** trunk-based, small batches, deploy frequently [BOOK:Forsgren et al. 2018]; feature toggles with lifecycle and removal [BOOK/UNVERIFIED:Hodgson 2017]; progressive delivery (canary, percentage rollout); every change has a rollback path; expand/contract for schema migrations [BOOK:Ambler & Sadalage, Refactoring Databases, 2006 — the book's term is a "transition period" during which old and new schema coexist; the "expand/contract" label comes from the later Parallel Change pattern (Sato, martinfowler.com, 2014) [UNVERIFIED URL]].
- **OWNS:** release plan per slice, flag inventory (name, type, owner, default, removal task), migration ordering, rollback plans, release readiness checklist. **DOES NOT OWN:** what goes into a slice (PM/TPM), test design (QA), infra architecture (architecture/SRE).
- **Inputs:** slices, tasks, architecture deployment topology, data model migrations, SRE runbooks/SLOs.
- **Outputs:** release plan; feature-flag register; migration plan (expand -> migrate -> contract); release readiness/go-no-go checklist; release notes skeleton.
- **ACCEPTANCE criteria:** [ ] every task merges to trunk without breaking main (flagged if incomplete); [ ] each flag has a removal task; [ ] every schema change is backward-compatible for one release or has documented downtime approval; [ ] each slice has rollback steps and the observability signals to watch; [ ] go/no-go criteria are measurable.
- **REFUSAL criteria:** *blocked:* no deployment topology or environments; *rejected:* destructive migrations without expand/contract, long-lived feature branches as plan, release of a slice with failing exit gate; *out_of_scope:* GTM/launch announcements (extension point), choosing what to build.
- **Anti-patterns:** big-bang release; toggle debt; release = deploy; manual-only rollback.
- **Handoffs:** receives from TPM/tech lead; works with SRE pool; delivers release section of tasks handoff.

### R8. Task Critic (stage critic / reviewer)
- **Titles (real analogues):** Staff engineer reviewing design/plan, "plan reviewer", QA reviewer in backlog refinement, Spec Kit `/analyze`, PMO quality assurance. **Stage:** tasks (EXIT gate); pattern reusable by other stages.
- **Mission:** Independently verify, read-only, that the task set is complete, consistent, traceable and executable before handoff — and refuse it when not.
- **Mindset & principles:** adversarial but specific; read-only, produce findings with severity and remediation [WEB:spec-kit analyze.md]; evidence over assertion (Iron Law) [LOCAL:dev/research/2026-04-25-harness-engineering-research.md:688-705]; leverage model — plan errors multiply into hundreds of bad lines [LOCAL:ai/docs/agentic-engineering/research-plan-implement-rpi.md:31-33].
- **OWNS:** findings report (CRITICAL/HIGH/MEDIUM/LOW), pass/fail verdict against checklist. **DOES NOT OWN:** fixing the tasks (returns to authors), changing scope.
- **Inputs:** PRD + architecture handoffs, tasks file, test strategy, DoD/DoR.
- **Outputs:** critic report: coverage table (req -> tasks), ambiguity list, duplication, inconsistency, DAG checks, size violations, verdict.
- **ACCEPTANCE criteria (what it checks):** [ ] zero CRITICAL findings; [ ] 100% must-have coverage; [ ] DAG acyclic and every referenced ID exists; [ ] no vague terms without metrics; [ ] every task has AC + verification command + paths; [ ] parallel tasks file-disjoint; [ ] walking skeleton present; [ ] each open risk addressed; [ ] terminology consistent with PRD glossary.
- **REFUSAL criteria:** *blocked:* cannot read upstream handoffs (can't check traceability); *rejected:* any CRITICAL (missing coverage, constitution/NFR MUST violation, cycle); *out_of_scope:* rewriting tasks itself, judging product value.
- **Anti-patterns:** rubber-stamping; style nitpicks over substance; critic that also authors (self-review bias); unbounded review loops.
- **Handoffs:** receives from tasks orchestrator; returns verdict; on fail, findings routed to tech lead/TPM workers.

### R9. (Shared) Traceability owner — touchpoint only
- Defined in the shared pool; in this stage it verifies requirement -> story -> task -> test linkage and that IDs are stable across handoffs. Tasks stage must not redefine it; it consumes its matrix format. (Analogue: requirements engineer / business analyst maintaining an RTM.) [BOOK:Wiegers & Beatty, Software Requirements 3rd ed., 2013, ch.29]

---

## Implications for agentic personas

**Orchestrator (`tasks-orchestrator`, main thread, fresh session):** persona = TPM/Delivery Manager. It cannot rely on subagents spawning others [LOCAL:ai/docs/claude-code/subagents/creating-custom-subagents.md:666], so it must sequence workers itself: (1) ENTRY gate, (2) story map & slicing, (3) decomposition per slice (parallel fan-out per story is safe since outputs are separate files), (4) test strategy + test-task injection, (5) release/flag plan, (6) critic, (7) handoff write.

**Split/merge recommendations:**
- **Merge** Engineering Manager into orchestrator policy (capacity/autonomy/review policy is a config section, not a worker) — an LLM "EM" adds little without real people.
- **Merge** Scrum Master into gate definitions: DoR = entry gate checklist; DoD = per-task contract + exit gate. No separate facilitator agent needed; keep its *principles* (lightweight DoR, evidence-based DoD).
- **Keep separate** workers: `story-mapper/slicer` (Patton, walking skeleton, release slices), `task-decomposer` (tech lead; SPIDR/Lawrence; one invocation per story/slice), `test-strategist` (QA lead), `test-task-author` (SDET; can be merged with test-strategist for small projects), `release-planner` (release manager; flags, migrations), `task-critic` (read-only, separate context, ideally different model per Burleigh's reviewer pattern [LOCAL:...tyler-burleigh.md:112]).
- Shared pool invocation points: security & privacy review on tasks touching auth/PII; a11y on UI tasks; SRE on release plan; FinOps on infra tasks; analytics on instrumentation tasks — the decomposer should *tag* tasks with `concerns: [security, a11y, ...]` and the orchestrator routes.

**What LLMs typically get wrong here:**
1. **Horizontal decomposition** — models default to "create model / create service / create endpoint / create UI" layers. Require each task to state its user-observable effect or be in Setup/Foundational; critic flags stories whose tasks lack an end-to-end test.
2. **Over-decomposition & ceremony** — 16 ACs for a bug fix [LOCAL:...variant.md:105]. Add a size *floor* too: tasks smaller than a meaningful commit get merged; scale ceremony to change size.
3. **Invented file paths / APIs** — tasks referencing non-existent modules. Gate: every "modify" path must exist in repo (or be listed under "create"); verified by a deterministic script (glob check), not by the LLM.
4. **Fake parallelism** — marking `[P]` on tasks that touch the same file. Deterministic check: intersection of file sets among concurrently-runnable tasks = empty.
5. **Vague AC** ("handles errors gracefully", "fast"). Ambiguity lexicon check (Spec Kit analyze) + require numbers for NFR-derived AC.
6. **Hidden design decisions** — decomposer silently picks a library/schema. Rule: any decision not in architecture -> `spike` or `adr_request`; never inline.
7. **Test-as-afterthought / test tampering** — tests appended at end of phase, or agent told to "fix tests". Require test-first ordering within a story and an immutable-test rule [WEB:anthropic effective-harnesses].
8. **Optimistic sequencing** — risk deferred to the end. Require walking skeleton first and each open architecture risk scheduled before dependent value tasks.
9. **Lost traceability across handoffs** — renumbering IDs. IDs from upstream are immutable; new IDs are namespaced (e.g., `T-<story>-NN`).
10. **Declaring the stage done without evidence** — orchestrator must run the critic + deterministic validators and include their output in the handoff (Iron Law).

**Hard gates (deterministic where possible, LLM-judged where necessary):**
- ENTRY (blocked/rejected): PRD handoff has requirement IDs, priorities, AC per must-have; architecture handoff has components, interfaces/contracts, data model, NFRs with numbers, risk register; no `NEEDS CLARIFICATION`/TBD markers. Missing -> `blocked`; present but failing quality (untestable AC, cyclic components, contradictions PRD vs arch) -> `rejected` with findings routed upstream.
- EXIT: schema validation of `tasks.json` (12 fields); coverage = 100% of must-haves; DAG acyclic; `[P]` disjointness; path existence; every task has AC + verification command; walking skeleton present; risks covered; flag register complete with removal tasks; critic has zero CRITICAL/HIGH. Prefer JSON for machine state (less likely to be overwritten than Markdown [WEB:anthropic effective-harnesses]) plus a rendered Markdown view for humans.
- Out_of_scope triggers: requests to change product scope, pick technologies not in architecture, or produce GTM material -> refuse with pointer to the owning stage/extension point.

**Handoff artifact (tasks -> coding execution):** `tasks.json` (machine), `tasks.md` (Spec Kit-style view), `test-strategy.md`, `release-plan.md` (flags, migrations, rollback), `traceability.csv` (req -> story -> task -> test), `critic-report.md`, `handoff.md` with status (`accepted` / `accepted_with_risks`) and open items.

---

## Sources

1. Patton, J. *User Story Mapping*. O'Reilly, 2014. [BOOK]
2. Cohn, M. *User Stories Applied*. Addison-Wesley, 2004. [BOOK]
3. Cohn, M. *Agile Estimating and Planning*. Prentice Hall, 2005. [BOOK]
4. Cohn, M. *Succeeding with Agile*. Addison-Wesley, 2009 (test automation pyramid). [BOOK]
5. Wake, B. "INVEST in Good Stories, and SMART Tasks", xp123.com, 2003. [BOOK; title/year/acronyms corroborated via search results — page itself blocked]
6. Lawrence, R. & Green, P. "The Humanizing Work Guide to Splitting User Stories", humanizingwork.com. [UNVERIFIED — page blocked]
7. SPIDR summaries: https://ascendle.com/ideas/spidr-an-alternative-method-for-splitting-user-stories/ ; https://socadk.github.io/design-practice-repository/activities/DPR-StorySplitting.html [WEB, via search results]
8. Cockburn, A. *Crystal Clear*. Addison-Wesley, 2004. [BOOK]
9. Hunt, A. & Thomas, D. *The Pragmatic Programmer*, 20th Anniversary Ed. Addison-Wesley, 2019. [BOOK]
10. Freeman, S. & Pryce, N. *Growing Object-Oriented Software, Guided by Tests*. Addison-Wesley, 2009. [BOOK]
11. North, D. "Introducing BDD", Better Software, March 2006. [BOOK; venue/date corroborated via search results — page blocked]
11a. Wynne, M. "Introducing Example Mapping", Cucumber blog, Dec 2015. https://cucumber.io/blog/bdd/example-mapping-introduction/ [WEB, search result]
12. Adzic, G. *Specification by Example*. Manning, 2011. [BOOK]
13. Adzic, G. *Impact Mapping*. Provoking Thoughts, 2012. [BOOK]
14. Schwaber, K. & Sutherland, J. *The Scrum Guide*, 2020. https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf [WEB — DoD quote confirmed via search]
15. PMI. *PMBOK Guide*, 6th ed., 2017 (WBS §5.4, schedule §6.5). [BOOK]
16. Reinertsen, D. *The Principles of Product Development Flow*. Celeritas, 2009. [BOOK]
17. Forsgren, N., Humble, J. & Kim, G. *Accelerate*. IT Revolution, 2018. [BOOK]
18. Hodgson, P. "Feature Toggles (aka Feature Flags)", martinfowler.com, 2017. [UNVERIFIED — page blocked]
19. Boehm, B. "A Spiral Model of Software Development and Enhancement", IEEE Computer, 1988. [BOOK]
20. Crispin, L. & Gregory, J. *Agile Testing*, 2009; *More Agile Testing*, 2014; *Agile Testing Condensed*, 2019. [BOOK]
21. PMI Disciplined Agile, "Testing Quadrants": https://www.pmi.org/disciplined-agile/agile/testingquadrants [WEB, via search result]
22. Crispin, L. "Agile Testing Quadrants, version 3": https://lisacrispin.com/agile-testing-quadrants-version-3-from-agile-testing-condensed/ [WEB search result only; page blocked]
23. Vocke, H. "The Practical Test Pyramid", martinfowler.com, 2018. [UNVERIFIED — page blocked]
24. Dodds, K. C. "The Testing Trophy and Testing Classifications", 2018/2021. [UNVERIFIED — page blocked]
25. Robinson, I. "Consumer-Driven Contracts: A Service Evolution Pattern", martinfowler.com, 2006; Pact docs. [UNVERIFIED — pages blocked]
26. ISTQB Certified Tester Foundation Level Syllabus v4.0, 2023; ISO/IEC/IEEE 29119-3. [BOOK]
27. Meszaros, G. *xUnit Test Patterns*. Addison-Wesley, 2007. [BOOK]
28. Ambler, S. & Sadalage, P. *Refactoring Databases*. Addison-Wesley, 2006. [BOOK]
29. Skelton, M. & Pais, M. *Team Topologies*. IT Revolution, 2019. [BOOK]
30. Wiegers, K. & Beatty, J. *Software Requirements*, 3rd ed. Microsoft Press, 2013. [BOOK]
31. GitHub Spec Kit — tasks command: https://raw.githubusercontent.com/github/spec-kit/main/templates/commands/tasks.md [WEB]
32. GitHub Spec Kit — tasks template: https://raw.githubusercontent.com/github/spec-kit/main/templates/tasks-template.md [WEB]
33. GitHub Spec Kit — analyze command: https://raw.githubusercontent.com/github/spec-kit/main/templates/commands/analyze.md [WEB]
34. GitHub Spec Kit — plan template: https://raw.githubusercontent.com/github/spec-kit/main/templates/plan-template.md [WEB]
35. Young, J. (Anthropic Engineering), "Effective harnesses for long-running agents", Nov 2025: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents [WEB]
36. Local: /home/user/ai-study-library/ai/docs/spec-driven-development/ (README.md, spec-driven-development-main.md, -variant.md, -arxiv.md) [LOCAL]
37. Local: /home/user/ai-study-library/dev/research/2026-04-25-harness-engineering-research.md [LOCAL]
38. Local: /home/user/ai-study-library/ai/docs/agentic-engineering/research-plan-implement-rpi.md and research-plan-implement-review-tyler-burleigh.md [LOCAL]
39. Local: /home/user/ai-study-library/ai/docs/claude-code/subagents/creating-custom-subagents.md [LOCAL]

---

## Verification log

Verifier pass on 2026-10-02 (skeptical citation check; no new content added). Method: I fetched the Spec Kit templates directly from raw.githubusercontent.com, fetched the Anthropic engineering post, used web searches for blocked primary sites, re-read the local corpus at the cited lines, and spot-checked books from knowledge.

**Confirmed (online or against the local file):**
- Spec Kit `tasks.md`: task line format `- [ ] [TaskID] [P?] [Story?] Description with file path`, example `T012 [P] [US1] ...`, the invalid-line examples (missing checkbox, ID or file path), tests being optional, the Setup -> Foundational -> user-story phases -> Polish order, and the rule to quote data-model constraints verbatim.
- Spec Kit `tasks-template.md`: "Write these tests FIRST, ensure they FAIL before implementation" and the per-story independent-test checkpoints.
- Spec Kit `analyze.md`: strictly read-only; detects duplication, ambiguity (vague adjectives), coverage gaps and inconsistency; constitution conflicts are automatically CRITICAL; severities run CRITICAL/HIGH/MEDIUM/LOW.
- Spec Kit `plan-template.md`: "NEEDS CLARIFICATION" placeholders; Constitution Check "Must pass before Phase 0 research. Re-check after Phase 1 design."
- Anthropic, "Effective harnesses for long-running agents" (Justin Young, Nov 2025):
  - the exact quote "It is unacceptable to remove or edit tests because this could lead to missing or buggy functionality";
  - JSON was chosen over Markdown because the model is less likely to inappropriately change or overwrite it;
  - feature fields are category, description, steps and passes.
- Scrum Guide 2020 DoD quote and the "returns to the Product Backlog" passage. These agree with file 09's scrum.org source and with my own knowledge.
- Wake INVEST/SMART (2003): article title, year and both acronyms, through search results.
- Example Mapping (Wynne, Dec 2015, card colours): search result. Upgraded from UNVERIFIED to WEB.
- North, "Introducing BDD", Better Software, March 2006: venue and date confirmed through search.
- Local corpus line references:
  - `spec-driven-development-main.md` lines 35, 56 and 82;
  - `-variant.md` lines 57 and 105;
  - `-arxiv.md` lines 57, 91, 108, 110, 140 and 207;
  - `research-plan-implement-rpi.md` lines 31-35;
  - `tyler-burleigh.md` lines 112-120;
  - `creating-custom-subagents.md` line 666;
  - harness research: lines 647-665 (Initializer/feature_list.json) and 688-705 (Iron Law).

**Corrected:**
- Spec Kit `[P]` quote. The sentence "Mark tasks [P] only when they use different files and don't depend on incomplete tasks." does not appear in the source. I replaced it with the actual text: "Include ONLY if task is parallelizable (different files, no dependencies on incomplete tasks)".
- North 2006. The "In order to / As a / I want" variant is Chris Matts' Feature Injection reformulation, not part of North's article, which uses "As a / I want / So that".
- PMBOK. Dependency types (FS/SS/FF/SF) are in §6.3 Sequence Activities, not §6.5.
- GOOS ch.22 is titled "Constructing Complex Test Data", not "Test Data Builders".
- Beck. "Sustainable pace" / "40-hour week" is the 1st-edition (1999) practice. The 2nd edition (2004) renamed it "Energized Work".
- Expand/contract. *Refactoring Databases* uses the term "transition period". The "expand/contract" label comes from the later Parallel Change pattern, which I could not verify online.
- Effective-harnesses claim. "Drastically reduced" was our own wording. I replaced it with the source's phrasing and added the author and date.

**Downgraded / left UNVERIFIED (sources blocked; not re-checked):**
- Lawrence's nine splitting patterns and evaluation heuristics.
- Cohn's view that spikes are a last resort.
- Gherkin keyword list.
- DORA small-batches page.
- Hodgson "Feature Toggles" (2017).
- Vocke (2018).
- Dodds testing trophy.
- Robinson CDC (2006) and Pact docs.
- Typical DoR list.
- The size-cap numeric threshold.

These items match my knowledge, but they stay tagged as they were.

**Spot-checked by knowledge (no change):**
- Patton 2014.
- Cohn 2004/2005/2009, including the pyramid in *Succeeding with Agile* ch.16 and planning poker from Grenning.
- Cockburn's walking skeleton in *Crystal Clear* (2004).
- *Pragmatic Programmer* 2019 Topics 12-13.
- GOOS ch.4.
- Adzic 2011 process patterns and Adzic 2012 impact mapping.
- Reinertsen 2009 chapter mapping.
- *Accelerate* 2018: four key metrics, and trunk-based development with fewer than three active branches.
- Boehm 1988.
- Marick 2003 quadrants.
- ISTQB FL v4.0 §5.2.
- Wiegers & Beatty ch.29.
- Anderson 2010.
- Skelton & Pais 2019.
