# Raw research — Software architecture core

Axis: software architecture practice. Pipeline stage covered: **(3) Architecture**, which takes its input from the PRD handoff and sends its output to Tasks. The architecture-review critic and the platform architect also serve as **shared** advisors.
Execution model: each stage orchestrator runs as the main thread in a *fresh* session (`claude --agent architecture-orchestrator`). It sees only the upstream handoff files on disk and talks to later stages only through its own handoff files. In Claude Code, subagents cannot spawn subagents, so the orchestrator must do all fan-out to workers itself [LOCAL:ai/docs/claude-code/subagents/creating-custom-subagents.md:47,295,666].

Tag legend: [WEB:url] = read or confirmed online in this session (often through a search-result summary, because the egress proxy blocked martinfowler.com, c4model.com, docs.arc42.org, adr.github.io, cognitect.com, oreilly.com and thoughtworks.com). [BOOK:...] = from a well-known book. [LOCAL:path] = from the local corpus. [UNVERIFIED] = uncertain detail.
The ADR and MADR templates were fetched verbatim from GitHub raw files.

---

## Literature & frameworks

### 1. Richards & Ford — *Fundamentals of Software Architecture* (1st ed. 2020; 2nd ed. 2025)
- **Laws of software architecture.**
  - First law: *everything in software architecture is a trade-off*. Corollary: if you think you have found something that is not a trade-off, you have not yet found the trade-off.
  - Second law: *why is more important than how*. Diagrams show the how, but they cannot show the why.
  - The 2nd edition adds a third law: most architecture decisions are not binary. They sit on a spectrum between extremes.
  - [WEB:https://www.oreilly.com/library/view/fundamentals-of-software/9781098175504/ch27.html (search summary; ch. 27 "The Laws of Software Architecture, Revisited"; third-law wording "most architecture decisions aren't binary but rather exist on a spectrum between extremes" confirmed via search summary)] [WEB:https://kb.segersian.com/software-architecture/topics/laws-of-software-architecture/]
  - **Persona implication:** if an architecture output names an option and lists no rejected alternatives and no explicit "what we give up", it violates the first law and the critic should reject it. If a decision records the how but not the why, it violates the second law.
- **Architecture characteristics** (the "-ilities") are what the system must support beyond its domain function.
  - A characteristic qualifies only if it (a) specifies a non-domain design consideration, (b) influences some structural aspect of the design, and (c) is critical or important to success.
  - Architects are told to pick the **fewest** characteristics possible. A useful heuristic is the *top three* that drive the design, not a wish list. ("Generic architecture" means an architecture that tries to support every characteristic.)
  - Characteristics can be explicit (stated in requirements) or implicit (for example availability or security, which nobody writes down).
  - [BOOK:Richards & Ford, Fundamentals of Software Architecture, 2020, ch. 4–5 "Architecture Characteristics Defined/Identified"]
- **Architecture styles** are rated by characteristic using star ratings: layered, pipeline, microkernel, service-based, event-driven, space-based, orchestration-driven SOA, microservices. The 2nd edition also adds modular monolith.
  - The choice of style follows from the driving characteristics and from whether the system is a single quantum or several quanta.
  - [BOOK:Richards & Ford, FoSA, Part II "Architecture Styles"; ch. "Choosing the Appropriate Architecture Style"]
- **Architecture quantum** is the unit used to decide whether you need a distributed architecture. If different parts need *different* characteristics (for example one part needs elastic scale and another needs strong consistency), the system has more than one quantum. [BOOK:Richards & Ford, FoSA, ch. 7 "Scope of Architecture Characteristics"]
- **Expectations of an architect.** There are eight:
  1. make architecture decisions
  2. continually analyze the architecture
  3. keep current with trends
  4. ensure compliance with decisions
  5. have diverse exposure and experience
  6. have business domain knowledge
  7. possess interpersonal skills
  8. understand and navigate politics
  - Architects *guide* technology choices. They do not *specify* them, for example "use a reactive framework" rather than "use React" [BOOK:Richards & Ford, FoSA, ch. 1 "Expectations of an Architect"].
  - "Ensure compliance" connects straight to fitness functions.
- **Technical breadth over depth.** The architect's knowledge pyramid runs "stuff you know / stuff you know you don't know / stuff you don't know you don't know". A frozen-caveman anti-pattern is reverting to a past bad experience as an irrational blocker [BOOK:Richards & Ford, FoSA, ch. 2 "Architectural Thinking"].
- **Architecture vs. design is a spectrum** (strategic vs. tactical). The test: how many people does the decision affect, how long will it last, and how hard is it to reverse? [BOOK:Richards & Ford, FoSA, ch. 2].

### 2. Ford, Richards, Sadalage, Dehghani — *Software Architecture: The Hard Parts* (2021)
- "Hard parts" are problems that have *no best practice*. You can only pick the least-worst set of trade-offs [WEB:https://www.goodreads.com/en/book/show/58153482-software-architecture].
- **Architecture quantum, refined:** independently deployable, high functional cohesion, high static coupling, synchronous dynamic coupling [WEB:https://danlebrero.com/2022/03/30/software-architecture-the-hard-parts-book-summary/].
- **Two kinds of coupling.** Static coupling is wiring: dependencies and connection points, often visible at compile time. Dynamic coupling is how parts *call* each other at runtime. It has three dimensions: communication (sync/async), consistency (atomic/eventual) and coordination (orchestration/choreography). Combinations of the three give eight named saga patterns [WEB:https://danlebrero.com/2022/03/30/software-architecture-the-hard-parts-book-summary/] [BOOK:Ford et al., Hard Parts, ch. 2 & 12 "Transactional Sagas"].
- **Granularity disintegrators** (reasons to split): service scope and function, code volatility, scalability and throughput, fault tolerance, security, extensibility. **Integrators** (reasons to keep together) include database transactions, workflow and choreography, shared code and data relationships [WEB:https://newsletter.techworld-with-milan.com/p/what-i-learned-from-the-software] [BOOK:Ford et al., Hard Parts, ch. 7].
- **Trade-off analysis method** [BOOK:Ford et al., Hard Parts, ch. 15 "Build Your Own Trade-Off Analysis"]:
  1. find the entangled dimensions
  2. analyze how they are coupled
  3. assess trade-offs by modeling realistic scenarios, not generic pros/cons
  4. prefer *qualitative* comparison matrices when you cannot quantify
  5. avoid "evangelist" over-selling
  6. present the result as a bottom line to stakeholders
  - **Persona implication:** a trade-off worker should output a scenario-grounded matrix (options × driving characteristics), not a generic pros/cons list copied from blogs.
- Data is the hardest part: data ownership, distributed transactions and data decomposition drivers are treated as first-class architecture decisions [BOOK:Ford et al., Hard Parts, Part I ch. 6 "Pulling Apart Operational Data"].

### 3. Bass, Clements, Kazman — *Software Architecture in Practice* (4th ed. 2021) and SEI methods
- **Quality attribute scenario (QAS)** has six parts: *source of stimulus, stimulus, environment, artifact, response, response measure*. The response measure is what makes the scenario testable [WEB:https://wstomv.win.tue.nl/edu/2ii45/year-0910/Software_Architecture_in_Practice_2nd_Edition_Chapter4.pdf (search summary)].
  - Illustrative example (written for this note, not quoted from the book): "An unanticipated external user (source) sends 10k req/s (stimulus) during peak sale (environment) to the checkout API (artifact). The system processes all requests (response) with p99 < 300 ms and 0 dropped orders (response measure)." The six-part form itself is from [BOOK:Bass et al., SAiP 4th ed., ch. 3 "Understanding Quality Attributes"].
  - **Persona implication:** the PRD→Architecture ENTRY gate should ask for NFRs that can be *converted* into QASs. The architecture stage then owns the conversion and must not proceed with an NFR that has no response measure.
- **Tactics** are design primitives that each address one quality attribute. Availability tactics include heartbeat, redundancy, rollback and circuit breaker. Performance tactics include caching, concurrency and resource scheduling. Modifiability tactics include encapsulation, restricting dependencies and deferring binding. Patterns are bundles of tactics [BOOK:Bass et al., SAiP 4th ed., chs. 4–13].
- **Architecturally significant requirements (ASRs)**: requirements with a deep effect on architecture. They are captured in a **utility tree** (utility → QA → refinement → scenario). Each leaf is rated High/Medium/Low on business importance and on architectural risk/difficulty. (H,H) leaves get priority [BOOK:Bass et al., SAiP, ch. 19 "Architecturally Significant Requirements"] [WEB:https://en.wikipedia.org/wiki/Architecture_tradeoff_analysis_method].
- **ATAM** has nine steps: present ATAM; present business drivers; present architecture; identify architectural approaches; generate the QA utility tree; analyze approaches; brainstorm and prioritize scenarios; analyze again; present results. Outputs are **risks, non-risks, sensitivity points, trade-off points** and risk themes [WEB:https://en.wikipedia.org/wiki/Architecture_tradeoff_analysis_method].
  - This is the most directly reusable *critic protocol* for the Architecture EXIT gate.
  - Lighter variants exist: the Lightweight Architecture Evaluation method [BOOK:Bass et al., SAiP, ch. 21 "Evaluating an Architecture"] [UNVERIFIED exact chapter title in 4th ed.], and the "mini-QAW" (a short Quality Attribute Workshop), which comes from Ozkaya, Keeling and Chaparro rather than from SAiP [BOOK:Keeling, Design It!, Pragmatic Bookshelf, 2017] [UNVERIFIED exact attribution].
- **Documentation:** *Documenting Software Architectures: Views and Beyond* (Clements et al., 2nd ed. 2010) frames documentation as views of three kinds: module, component-and-connector, allocation. Its rule is "document from the reader's point of view" [BOOK:Clements et al., DSA: Views and Beyond, 2010].

### 4. Rozanski & Woods — *Software Systems Architecture: Working with Stakeholders Using Viewpoints and Perspectives* (2nd ed. 2011)
- Seven **viewpoints**: Context, Functional, Information, Concurrency, Development, Deployment, Operational. Each viewpoint comes with stakeholders, concerns, models and pitfalls [WEB:https://software-architecture-guild.com/guide/competencies/modeling/frameworks/viewpoints-and-perspectives/] [WEB:https://www.viewpoints-and-perspectives.info/vpandp/wp-content/themes/secondedition/doc/spa191-viewpoints-and-perspectives.pdf (search listing)].
- **Perspectives** are quality concerns that cut *across* views: Security, Performance & Scalability, Availability & Resilience, Evolution as the core set, plus Accessibility, Development Resource, Internationalization, Location, Regulation, Usability [WEB:https://www.researchgate.net/publication/4236448_Using_Architectural_Perspectives (search summary)].
- **Persona implication:** this maps almost one-to-one onto our design. *Viewpoints* are produced by the architecture-stage workers. *Perspectives* are applied by the **shared cross-cutting pool**: security, privacy/regulation, accessibility, SRE/availability, FinOps/development resource. Each perspective is a checklist applied to every view. It is not a separate document.
- Their stakeholder-centric stance: an architecture is "good" only relative to stakeholder concerns. An architect who cannot name the stakeholders and their concerns is not finished [BOOK:Rozanski & Woods, SSA 2nd ed., ch. 9 "Identifying and Engaging Stakeholders"].

### 5. Simon Brown — C4 model
- Four hierarchical levels [WEB:https://www.archyl.com/blog/what-is-the-c4-model-complete-guide] [WEB:https://c4model.info/]:
  - **System Context**: the system plus users plus external systems.
  - **Container**: a separately runnable or deployable unit such as a web app, API, database, broker or batch job. This is *not* a Docker container.
  - **Component**: a grouping of functionality behind an interface inside one container, not separately deployable.
  - **Code**: optional, and usually generated.
- Supplementary diagrams: system landscape, dynamic, deployment [BOOK:Brown, The C4 Model for Visualising Software Architecture (Leanpub)] [UNVERIFIED that the list is complete].
- Notation hygiene Brown insists on [BOOK:Brown, Software Architecture for Developers vol. 2] [UNVERIFIED exact checklist wording]:
  - every diagram has a title, a key/legend and a stated scope
  - every element has a type, a technology and a one-line responsibility
  - every relationship arrow is labeled with intent and protocol
  - acronyms are explained
- Brown argues for "just enough up-front design" so that the team shares a vision and identifies significant risks. He does not argue for big design up front. His "risk-storming" technique is a collaborative way to find risks on C4 diagrams [BOOK:Brown, Software Architecture for Developers vol. 1].
- Diagrams-as-code (Structurizr DSL, PlantUML C4, Mermaid C4) makes the views diffable and machine-checkable. That matters for agents.

### 6. arc42 (Hruschka & Starke)
- Twelve sections [WEB:https://arc42.org/overview/ (search summary)]:
  1. Introduction & Goals (requirements overview, top-3–5 quality goals, stakeholders)
  2. Constraints
  3. Context & Scope (business and technical context)
  4. Solution Strategy
  5. Building Block View
  6. Runtime View
  7. Deployment View
  8. Crosscutting Concepts
  9. Architecture Decisions
  10. Quality Requirements (quality tree plus scenarios)
  11. Risks & Technical Debt
  12. Glossary
- arc42 is tailorable. Any section may be left empty or say "n/a" with a reason. It is not filled in for completeness' sake [WEB:https://arc42.org/overview/].
- **Persona implication:** arc42 makes a good *skeleton for the Architecture handoff file*. C4 supplies the diagrams for sections 3, 5 and 7. ADRs fill section 9. QASs fill section 10. ATAM risks feed section 11.

### 7. Architecture Decision Records — Nygard (2011) and MADR
- **Nygard format** sections: Title, Status, Context, Decision, Consequences (this is the adr-tools/template ordering; Nygard's 2011 essay lists them as Title, Context, Decision, Status, Consequences [BOOK:Nygard 2011, from knowledge]) [WEB:https://github.com/joelparkerhenderson/architecture-decision-record/tree/main/locales/en/templates/decision-record-template-by-michael-nygard]. adr-tools adds a number and a date. Its template text defines Consequences as "what becomes easier or more difficult to do and any risks introduced by the change that will need to be mitigated" [WEB:https://github.com/npryce/adr-tools/blob/master/src/template.md].
- Nygard's essay says ADRs should be short, numbered sequentially and never reused. A reversed decision is kept and marked superseded [BOOK/essay: Nygard, "Documenting Architecture Decisions", Relevance blog, 2011] [UNVERIFIED exact wording — cognitect.com blocked].
- **MADR template** (fetched verbatim) [WEB:https://github.com/adr/madr/blob/main/template/adr-template.md]:
  - optional front matter: `status` (proposed | rejected | accepted | deprecated | superseded by ADR-NNNN), `date`, `decision-makers`, `consulted`, `informed`
  - sections: Context and Problem Statement; Decision Drivers (optional); Considered Options; Decision Outcome ("Chosen option: X, because ..."), with optional Consequences (Good/Bad because...) and **Confirmation**; Pros and Cons of the Options (Good/Neutral/Bad); More Information
  - The Confirmation section explicitly asks how compliance will be checked: "Is there any automated or manual fitness function?", for example ArchUnit.
  - Files are named `nnnn-title.md` under `docs/decisions` [WEB:https://github.com/adr/madr/blob/main/README.md].
- **Persona implication:** MADR's *Considered Options* together with *Confirmation* enforce both FoSA laws and the evolutionary-architecture link in one artifact. Prefer MADR over bare Nygard for LLM output because its structure makes "a single option with no alternatives" visibly empty.

### 8. Ford, Parsons, Kua (and Sadalage, 2nd ed. 2022) — *Building Evolutionary Architectures*
- A **fitness function** is "an objective integrity assessment of some architectural characteristic(s)" [WEB:https://www.oreilly.com/library/view/building-evolutionary-architectures/9781491986356/ch02.html (search summary)].
- Categories:
  - atomic vs holistic
  - triggered vs continual
  - static vs dynamic
  - automated vs manual
  - temporal
  - intentional vs emergent
  - domain-specific
  - [WEB:https://continuous-architecture.org/practices/fitness-functions/] [BOOK:Ford et al., BEA 2nd ed., ch. 2]
- Mechanisms include tests, metrics, monitoring and logging. Concrete examples: ArchUnit/NetArchTest dependency rules, cyclic-dependency checks, p99 latency SLO alarms, chaos experiments, license and CVE scans in CI [WEB:https://gist.github.com/scottwd9/ada88f963aac95893e1eba10d4ad8f6d] [BOOK:Ford et al., BEA 2nd ed., ch. 4 "Automating Architectural Governance"].
- The 2nd edition's subtitle is "Automated Software Governance". Governance moves from review boards to CI-executed checks [WEB:https://dokumen.pub/building-evolutionary-architectures-automated-software-governance-2nbsped-1492097543-9781492097549.html (title)].
- "Last responsible moment" and "guided, incremental change across multiple dimensions" are the core of the evolutionary stance [BOOK:Ford et al., BEA].
- **Persona implication:** each driving characteristic in the architecture handoff should have ≥1 fitness function spec that becomes a Tasks-stage ticket. This is where architecture becomes *executable* for downstream agents. It matches the harness-engineering principle of "deterministic back-pressure via linters and verification hooks" [LOCAL:ai/docs/harness-engineering/harness-engineering.md:14] and Spec Kit's "constitution" of enforced constraints [LOCAL:ai/docs/spec-driven-development/spec-driven-development-main.md:38].

### 9. Gregor Hohpe — *The Software Architect Elevator* (2020)
- The architect rides the elevator between the **engine room** (technical implementation) and the **penthouse** (business strategy), translating in both directions [WEB:https://chrisebert.net/software-architect-elevator-review/] [WEB:https://www.goodreads.com/book/show/49828197-the-software-architect-elevator].
- Architects **sell options**. Architecture's value is in deferring and enabling decisions under uncertainty; an option has value when uncertainty is high [BOOK:Hohpe, Architect Elevator, Part II, ch. 9 "Architecture Is Selling Options"] [WEB:https://dokumen.pub/the-software-architect-elevator-9781492077541.html (table of contents via search summary)].
- Architects should *reduce* decision-makers' blind spots rather than act as the smartest person in the room. They look for and show trade-offs, and help others make better decisions [BOOK:Hohpe, Architect Elevator, Part I, e.g. ch. 6 "Making Decisions"] [UNVERIFIED — the chapter titles previously cited here ("Architects Look for Trade-Offs", "Architects as Enablers") do not appear in the table of contents; the idea is Hohpe's but the exact location is unconfirmed].
- Diagrams should make a point, and a single picture should carry one message. An "architecture of nothing" (boxes with no decisions) is a failure [BOOK:Hohpe, Architect Elevator, Part III "Communication"].
- **Persona implication:** the architecture orchestrator must emit *two* summaries: an executive one-pager (penthouse: cost, risk, options, reversibility) and an engineering handoff (engine room). This is a translation duty, not decoration.

### 10. Martin Fowler — architecture as "the important stuff"; sacrificial architecture
- Fowler, following Ralph Johnson, defines architecture as *the important stuff, whatever that is*. In other words: the shared understanding among expert developers of the parts of a system that matter for its long-term health, and decisions that are hard to change [WEB:https://mariadelia.blog/2025/11/16/understanding-software-architecture-through-martin-fowlers-lens/] [BOOK:Fowler, "Who Needs an Architect?", IEEE Software, 2003].
- **Sacrificial architecture**: deliberately build something you expect to throw away when scale or learning demands it. eBay and Twitter rebuilt. Google designs for about 10× current capacity, expecting a rewrite beyond that. Modularity is what lets you sacrifice parts rather than the whole [WEB:https://www.freecodecamp.org/news/sacrificial-architecture-make-tough-decisions-to-abandon-and-rebuild-systems/] [WEB:https://medium.com/flowingis/sacrificial-architecture-in-web-development-3926c0593fc8].
- Related: the **Design Stamina Hypothesis** (design pays off only past a certain point) and the **Technical Debt Quadrant** (reckless/prudent × deliberate/inadvertent) [BOOK:Fowler bliki, 2007/2009] [UNVERIFIED — site blocked].
- **Persona implication:** the architecture stage must state the *expected lifespan / scale envelope*, for example "designed for 10× current load; beyond that, re-architect". It must also mark explicitly sacrificial components. That stops over-engineering an MVP that came out of Discovery.

### 11. Conway's law and Team Topologies (Skelton & Pais, 2019; 2nd ed. 2025)
- **Conway (1968):** organizations that design systems produce designs that copy their communication structures [BOOK:Conway, "How Do Committees Invent?", Datamation, 1968].
- **Team Topologies** names four team types (stream-aligned, platform, enabling, complicated-subsystem) and three interaction modes (collaboration, X-as-a-service, facilitating). It uses team **cognitive load** as a design constraint and the **inverse Conway maneuver** (shape teams to get the architecture you want) [WEB:https://itrevolution.com/articles/four-team-types/] [WEB:https://umbrex.com/resources/frameworks/organization-frameworks/team-topologies/].
- Misuse warning: platform teams that become ticket-driven gatekeepers rather than a self-service product [WEB:https://teamtopologies.com/news-blogs-newsletters/2024/11/24/revisiting-team-topologies-misuses-of-platform-teams].
- **Persona implication:** even in an agentic pipeline, the Tasks stage sorts work into ownership units, whether human teams or agent lanes. The architecture handoff should state the *intended ownership boundaries*. Component/container boundaries should match them, so that a task never needs two owners to change one quantum at the same time. For agents, "cognitive load" corresponds to context-window budget per work unit [LOCAL:dev/research/2026-04-25-harness-engineering-research.md:1047].

### 12. Build vs. buy and Technology Radar
- **Build vs buy**:
  - Build what differentiates; buy or rent commodity. This is Wardley-style evolution: genesis → custom → product → commodity [BOOK:Wardley, Wardley Maps, 2016–] [UNVERIFIED as a book citation; online-published].
  - Hohpe: "buy" moves the cost into integration, upgrade and lock-in. Lock-in should be judged by *switching cost × likelihood of switching*, not avoided blindly [BOOK:Hohpe, Cloud Strategy, 2020, ch. "Don't Get Locked Up Into Avoiding Lock-In"].
  - Evaluation dimensions used in practice: TCO over 3–5 years (license, run, integrate, staff), strategic differentiation, time-to-value, vendor viability, exit strategy and data portability, security/compliance posture, and skills [UNVERIFIED — synthesized industry practice].
- **Technology Radar**: four quadrants (Techniques, Tools, Platforms, Languages & Frameworks) × four rings (Adopt, Trial, Assess, Hold). Hold means "don't start anything new with this" [WEB:https://www.thoughtworks.com/insights/blog/build-your-own-technology-radar (search summary)] [WEB:https://github.com/red-gate/Tech-Radar/issues/5]. Companies build their own radar as a governance artifact.
- **Persona implication:** an org radar, or a `tech-constraints.md` file in the repo, is an *input* to the architecture stage. Choosing a "Hold" technology without an ADR that justifies the exception is a refusal-grade violation.

### 13. Staff+ engineering (Larson) and architect archetypes
- Larson's four staff archetypes: **Tech Lead** (one team's technical direction and execution), **Architect** (direction across teams/systems in a critical area), **Solver** (drops into the hardest problems), **Right Hand** (extends an executive's reach) [WEB:https://leaddev.com/career-development/how-master-four-staff-archetypes-and-elevate-your-impact] [BOOK:Larson, Staff Engineer, 2021, ch. 1].
- Larson's practices: "write engineering strategy" (5 design docs → 1 strategy), "writing design docs", "manage technical quality" [BOOK:Larson, Staff Engineer; also An Elegant Puzzle, 2019].
- Gergely Orosz describes twelve lighthearted, complementary architect archetypes (e.g., "The Ivory Tower Architect", "The Coding Machine", "The Detailed Documenter") rather than a single spectrum [WEB:https://newsletter.pragmaticengineer.com/p/software-architect-archetypes (search summary, July 2023)].

---

## Real-world roles

Each subsection lists:
- **Stage**
- **Mission**
- **Mindset & principles**
- **OWNS / DOES NOT OWN**
- **Inputs**
- **Outputs**
- **ACCEPTANCE criteria**
- **REFUSAL criteria**: `blocked` = missing or insufficient input; `rejected` = upstream work fails the quality bar; `out_of_scope`
- **Anti-patterns**
- **Handoffs**

### R1. Solution Architect (→ the Architecture-stage orchestrator persona)
- **Titles:** Solution Architect, Lead Solution Architect, Systems Architect (product-scoped). **Stage:** architecture (owner/orchestrator). It also consults on feasibility during PRD.
- **Mission:** Turn a validated PRD into a fit-for-purpose, justified solution design that a delivery team can build. Every significant decision is traceable to a requirement, and every trade-off is made explicit.
- **Mindset & principles:**
  - Trade-offs over best practices (FoSA first law).
  - Why over how (second law).
  - Fewest driving characteristics.
  - "Just enough" up-front design (Brown).
  - Reader-centric documentation (Views & Beyond).
  - Sell options and defer irreversible choices to the last responsible moment (Hohpe; BEA).
- **OWNS:**
  - the architecture characteristics selection (top 3–5, ranked)
  - QAS conversion of NFRs
  - style/topology choice and quantum analysis
  - C4 L1–L2 (L3 for risky containers)
  - the ADR set for significant decisions
  - the risk register
  - fitness-function specs
  - the architecture handoff (arc42 skeleton)
  - consolidating cross-cutting perspective findings
- **DOES NOT OWN:**
  - product scope or priority (PM/PRD)
  - enterprise-wide standards (EA)
  - detailed class/code design (tech lead/devs)
  - shared platform roadmap (platform architect)
  - final security sign-off (security pool)
  - estimates and sequencing of tasks (Tasks stage)
- **Inputs:**
  - PRD handoff: problem, goals and success metrics, functional requirements with IDs, NFRs, constraints, non-goals, appetite, rabbit holes
  - org constraints: radar, mandated platforms, compliance regime, budget
  - existing-system context (brownfield): repo, current C4 or deployment
  - team/ownership model
- **Outputs (standard formats):**
  - arc42-structured `architecture.md`
  - C4 diagrams as code (Structurizr DSL or Mermaid C4)
  - MADR ADRs at `docs/decisions/nnnn-*.md`
  - a QAS table (six-part)
  - a utility tree with (importance, difficulty) ratings
  - a risk & tech-debt register
  - a fitness-function catalog
  - an executive one-pager
  - a handoff manifest with traceability (FR/NFR-ID → component → ADR → fitness function)
- **ACCEPTANCE criteria (reviewer checklist):**
  - [ ] Driving characteristics: 3–7 named, ranked, each traced to PRD IDs or an explicit implicit-characteristic rationale.
  - [ ] Every NFR is restated as a six-part QAS with a numeric or boolean response measure. No adjectives like "fast", "scalable" or "secure" without a measure.
  - [ ] Number of quanta stated, with justification. If >1 quantum, the inter-quantum communication/consistency/coordination choice is recorded in an ADR.
  - [ ] C4 Context and Container diagrams exist. Every element has a type, technology and responsibility. Every arrow is labeled. A legend is present.
  - [ ] Every ADR has ≥2 considered options (the "do nothing / buy" option counts), a decision with "because", consequences with ≥1 Bad, a status, and a Confirmation (fitness function or review method).
  - [ ] Each driving characteristic has ≥1 fitness function spec: what is measured, threshold, trigger (CI/deploy/continual), and owner.
  - [ ] Every Must-have FR maps to ≥1 container/component. No orphan components (each component maps to ≥1 FR/NFR or ADR).
  - [ ] Risk register: each risk has likelihood/impact and a mitigation or explicit acceptance. ATAM-style sensitivity and trade-off points are listed.
  - [ ] Build-vs-buy recorded for every non-differentiating capability over a trivial size.
  - [ ] Scale/lifespan envelope stated (e.g., "valid to 10× launch load"). Sacrificial components flagged.
  - [ ] No technology in the org radar's "Hold" ring without an exception ADR.
  - [ ] Cross-cutting pool verdicts (security, privacy, a11y, SRE, FinOps) attached. Each is `pass`, or `pass-with-conditions` with the conditions turned into ADRs or tasks.
- **REFUSAL criteria:**
  - `blocked`: PRD handoff missing or unreadable. No NFRs at all and no stated way to derive them (no user volumes, no data sensitivity class, no availability expectation). Hard constraints unknown: deployment target, compliance regime, budget envelope. Brownfield work without access to the current system description.
  - `rejected`:
    - PRD requirements lack stable IDs, so they cannot be traced.
    - Requirements contradict each other, e.g., "offline-first" plus "real-time strong consistency across devices" with no priority.
    - NFRs are pure adjectives that cannot be resolved by a single clarifying assumption.
    - The PRD prescribes implementation ("use Kafka") with no rationale. The architect should push back and ask for the need behind it.
    - Non-goals are absent, so scope is unbounded.
  - `out_of_scope`: re-deciding product priority or scope; writing production code; estimating story points; GTM/pricing; enterprise-wide standard changes (escalate to EA).
- **Anti-patterns:**
  - Résumé-driven / hype-driven architecture (microservices for a 1-quantum MVP).
  - "Generic architecture" that supports every -ility.
  - Ivory-tower diagrams with no decisions ("architecture of nothing").
  - ADRs written after the fact with a single option.
  - Covering-your-assets decision paralysis (FoSA anti-pattern) [BOOK:Richards & Ford, FoSA, ch. 19 "Architecture Decisions"].
  - "Groundhog Day" re-debating because the why wasn't recorded [BOOK:same].
  - "Email-driven architecture": decisions not in a system of record [BOOK:same].
- **Handoffs:** receives from the PRD orchestrator (handoff file) and the cross-cutting pool. Delivers to the Architecture critic (EXIT gate), then to the Tasks orchestrator via the handoff file. Escalates to the EA when standards conflict.

### R2. Enterprise Architect
- **Titles:** Enterprise Architect, Domain/Segment Architect, Chief Architect. **Stage:** shared (constraint provider). In a single-product pipeline it is usually a **static input** (standards, radar, reference architectures), not a live worker.
- **Mission:** Make sure individual solutions fit the organization's capability map, standards, data strategy and target-state roadmap, so the portfolio does not fragment.
- **Mindset:**
  - Portfolio and long-horizon thinking.
  - Rides the "architect elevator" between strategy and IT [WEB:https://chrisebert.net/software-architect-elevator-review/].
  - Governance through guardrails rather than gates (BEA "automated governance").
  - Prefers reuse and convergence.
  - Frameworks: TOGAF ADM, capability maps, ArchiMate [BOOK:The Open Group, TOGAF Standard, 10th ed., 2022] [UNVERIFIED edition detail].
- **OWNS:** technology standards and the radar; reference architectures; the capability map; integration and data standards; exception policy.
- **DOES NOT OWN:** individual solution designs; delivery; product priorities.
- **Inputs:** business strategy, the current-state portfolio, solution architecture proposals.
- **Outputs:** tech radar (quadrants × Adopt/Trial/Assess/Hold), standards catalog, reference architectures, exception decisions (ADR-style), roadmap.
- **ACCEPTANCE:**
  - [ ] Solution uses only Adopt/Trial items, or has an approved exception.
  - [ ] Integration via sanctioned patterns (API gateway, event bus).
  - [ ] Data classification and master-data ownership respected.
  - [ ] No duplicate of an existing enterprise capability without a build-vs-reuse justification.
- **REFUSAL:**
  - `blocked`: proposal lacks a context diagram showing integrations with existing systems.
  - `rejected`: introduces a Hold technology or a new system-of-record for a mastered entity without justification.
  - `out_of_scope`: component-level design and task breakdown.
- **Anti-patterns:** ivory tower and standards-for-their-own-sake; review boards as bottlenecks; TOGAF-shaped paperwork with no decisions.
- **Handoffs:** publishes constraints *before* the pipeline runs (e.g., `org/tech-radar.json`, `org/standards.md`). Consulted by R1 and R6 on exceptions.

### R3. Software / Application Architect
- **Titles:** Software Architect, Application Architect, Principal Engineer (system-scoped). **Stage:** architecture (worker).
- **Mission:** Design the internal structure of one system or container — modules, components, interfaces, data model, runtime behavior — so that it meets its quality scenarios and stays changeable.
- **Mindset:**
  - Modularity and cohesion/coupling as primary metrics.
  - Tactics before patterns (Bass).
  - Static vs dynamic coupling (Hard Parts).
  - Domain-driven boundaries (bounded contexts) [BOOK:Evans, Domain-Driven Design, 2003].
  - Design for testability and replaceability (sacrificial modularity).
- **OWNS:** C4 L3 component diagrams; interface/API contracts (OpenAPI/AsyncAPI); the logical data model and data ownership; runtime/sequence views for key scenarios; component-level ADRs; architectural dependency rules (as fitness functions, e.g., ArchUnit rules).
- **DOES NOT OWN:** system-of-systems topology across quanta (R1), infrastructure provisioning (platform), code implementation.
- **Inputs:** R1's driving characteristics, QAS and container diagram; FR list with IDs; domain glossary from PRD/Discovery.
- **Outputs:** component diagrams, API specs, entity/data-ownership tables, runtime views (sequence diagrams for the top 3–5 scenarios), dependency rules.
- **ACCEPTANCE:**
  - [ ] Each component has a single stated responsibility and owns its data or explicitly reads someone else's through an interface.
  - [ ] No cyclic dependencies between components.
  - [ ] Every external interface has a contract (schema, errors, versioning policy, idempotency for writes).
  - [ ] Runtime views cover the happy path plus ≥1 failure path per top QAS.
  - [ ] Each data entity has exactly one owning component.
- **REFUSAL:**
  - `blocked`: no container boundary or no driving characteristics from R1.
  - `rejected`: container diagram puts two quanta with conflicting characteristics in one deployable without an ADR; FR set has ambiguous domain terms (no glossary).
  - `out_of_scope`: picking cloud vendor; writing code.
- **Anti-patterns:**
  - Big ball of mud; entity-trap services ("CustomerService" CRUD wrappers) [BOOK:Richards & Ford, FoSA, ch. 8 "Component-Based Thinking"].
  - Shared database used as integration.
  - Layer-skipping.
  - Over-abstracted frameworks for speculative needs.
- **Handoffs:** from R1 (container scope) → back to R1 for consolidation. API contracts flow to Tasks.

### R4. Staff / Principal Engineer (Architect archetype) and Tech Lead
- **Titles:** Staff/Senior Staff/Principal Engineer; Tech Lead (TL), Tech Lead Manager. **Stage:** architecture (feasibility/implementability reviewer) and tasks (TL owns breakdown). In Larson's terms, the Architect archetype sets cross-team direction and the Tech Lead archetype owns one team's execution [WEB:https://leaddev.com/career-development/how-master-four-staff-archetypes-and-elevate-your-impact].
- **Mission:** Make sure the architecture is *buildable by this team with these skills in this appetite*. Turn it into an executable technical plan. Raise the quality floor (testing, observability, migration paths).
- **Mindset:**
  - Pragmatism; "boring technology" by default (innovation tokens) [BOOK:McKinley, "Choose Boring Technology", essay/talk, mcfunley.com, 2015 — an essay, not a book].
  - Writes design docs and engineering strategy [BOOK:Larson, Staff Engineer, 2021].
  - Manages technical quality incrementally.
  - Skeptical of anything that cannot be incrementally delivered.
- **OWNS:** implementability review; walking-skeleton / thin-slice definition; migration & rollout strategy (feature flags, strangler fig, dual-write); developer-experience concerns; test strategy outline. (TL) the task decomposition and sequencing in the Tasks stage.
- **DOES NOT OWN:** product scope; enterprise standards; final architecture style choice (advises R1).
- **Inputs:** architecture handoff (ADRs, C4, fitness functions), team skills and capacity, PRD appetite.
- **Outputs:** design doc / RFC (Google-style: Context & scope, Goals & non-goals, The actual design, Alternatives considered, Cross-cutting concerns) [WEB:https://www.industrialempathy.com/posts/design-docs-at-google/ (Malte Ubl, "Design Docs at Google", 2020; search summary)]. Corrected: this section list comes from Ubl's post, not from *Software Engineering at Google*; walking-skeleton definition; milestone plan; risk spikes list.
- **ACCEPTANCE:**
  - [ ] A thin end-to-end slice (walking skeleton) touching every container is identified as the first milestone.
  - [ ] Every new technology is either known to the team or has a spike task with a timebox.
  - [ ] Brownfield: migration path has no "big bang" cutover without a rollback plan.
  - [ ] Each fitness function is implementable in the existing CI/observability stack, or has a task to add it.
- **REFUSAL:**
  - `blocked`: no appetite or capacity information, so feasibility cannot be judged.
  - `rejected`: architecture needs more novel technologies than the innovation budget (heuristic: >2–3 new) with no spikes; decisions that can't be delivered incrementally.
  - `out_of_scope`: re-litigating product goals.
- **Anti-patterns:** hero-coding instead of enabling; gold-plating; "we'll fix it later" with no debt record; architecture-astronaut abstraction.
- **Handoffs:** reviews R1 output before the EXIT gate. As TL persona, receives the architecture handoff at the Tasks ENTRY gate.

### R5. Platform Architect
- **Titles:** Platform Architect, Platform Engineering Lead, Cloud/Infrastructure Architect, Internal Developer Platform PM-architect. **Stage:** shared (invoked by architecture; informs tasks).
- **Mission:** Provide the paved road (self-service compute, CI/CD, observability, identity, data services) as an internal product, and make sure solutions use it rather than reinventing it.
- **Mindset:**
  - Platform as a product, X-as-a-service interaction, reducing stream-aligned teams' cognitive load [WEB:https://itrevolution.com/articles/four-team-types/].
  - Avoid becoming a ticket-gatekeeper [WEB:https://teamtopologies.com/news-blogs-newsletters/2024/11/24/revisiting-team-topologies-misuses-of-platform-teams].
  - Golden paths over mandates.
  - Lock-in judged by switching cost [BOOK:Hohpe, Cloud Strategy, 2020].
- **OWNS:** deployment view (arc42 §7 / C4 deployment); environment topology; paved-road capabilities catalog; infra-as-code standards; platform-level fitness functions (deploy pipeline checks, policy-as-code).
- **DOES NOT OWN:** application logic; product requirements; cost decisions beyond platform scope (FinOps pool).
- **Inputs:** container diagram, QAS for availability/scalability, data residency constraints, platform catalog.
- **Outputs:** deployment diagram, environment matrix (dev/stage/prod), capability-mapping table (need → platform service | gap), gap ADRs.
- **ACCEPTANCE:**
  - [ ] Every container maps to a paved-road runtime or has an ADR for deviation.
  - [ ] Availability QAS are backed by a deployment topology (zones/regions, redundancy).
  - [ ] Secrets, identity and observability come from platform services, not bespoke ones.
- **REFUSAL:**
  - `blocked`: no deployment target or data residency info.
  - `rejected`: bespoke infra duplicating a platform capability without a justification ADR; a multi-region requirement with a single-region design.
  - `out_of_scope`: application component design.
- **Anti-patterns:** platform-as-gatekeeper; the "everything must be on Kubernetes" mandate; lowest-common-denominator multi-cloud.
- **Handoffs:** consulted by R1. Outputs feed SRE (shared pool) and Tasks (infra tickets).

### R6. Architecture Review Board member / Architecture Critic (→ Architecture EXIT-gate critic persona)
- **Titles:** ARB member, Design Authority, Architecture Reviewer, Principal Engineer (reviewer rotation), ATAM evaluation-team lead. **Stage:** architecture (EXIT gate). The same persona type can run ENTRY review of the PRD for architectural significance.
- **Mission:** Independently evaluate whether the proposed architecture meets its driving quality scenarios and constraints. Surface risks, sensitivity points and trade-off points *before* commitment. Do not redesign it.
- **Mindset:**
  - ATAM evaluator stance: analyze approaches against prioritized scenarios and classify findings as risks / non-risks / sensitivity points / trade-off points [WEB:https://en.wikipedia.org/wiki/Architecture_tradeoff_analysis_method].
  - Evidence over opinion.
  - Independence (not the author).
  - Prefers automated governance (fitness functions) to manual sign-off [BOOK:Ford et al., BEA 2nd ed.].
  - Hohpe's warning: reviews should improve decisions, not just police them.
- **OWNS:** review verdict (approve / approve-with-conditions / reject); findings list; risk themes; check of ADR quality and traceability completeness.
- **DOES NOT OWN:** authoring the fix (sends back to R1); product scope; any decision rights beyond the gate.
- **Inputs:** full architecture handoff draft; PRD handoff (for traceability); org standards/radar; cross-cutting pool verdicts.
- **Outputs:** review report: utility-tree check, scenario walk-throughs for the top (H,H) scenarios, findings table (ID, type ∈ {risk, non-risk, sensitivity, trade-off}, scenario, affected ADR/component, severity, required action), risk themes, verdict.
- **ACCEPTANCE (criteria it applies; also its own output bar):**
  - [ ] Walked through ≥ every (H,H) utility-tree scenario against the design.
  - [ ] Every finding cites a specific element (ADR-ID, component, QAS-ID). No generic advice.
  - [ ] Verdict is binary per criterion with a reason. "Approve-with-conditions" lists conditions as testable items.
  - [ ] Checked traceability both ways (requirement→design and design→requirement).
- **REFUSAL:**
  - `blocked`: no ranked characteristics or QAS (there is nothing to evaluate against); no ADRs (no why).
  - `rejected`: any ADR with one option or no Bad consequence; diagrams without a legend or with unlabeled relationships; NFRs left as adjectives; driving characteristic without a fitness function; Hold-ring tech without an exception.
  - `out_of_scope`: redesigning the solution; rewriting ADRs itself (it must return them).
- **Anti-patterns:** rubber-stamping; bikeshedding on notation while missing the quantum/consistency risk; ARB as a bottleneck that meets monthly; reviewer re-architecting to personal taste (frozen caveman).
- **Handoffs:** receives from the R1 orchestrator. Returns to R1 (rejected → loop, max N iterations) or lets the handoff be written.

### R7. Traceability / Architecture-documentation owner (specialization relevant to this axis)
- **Titles:** Architecture Documentation Lead, Requirements/Architecture Traceability Engineer (common in regulated industries: avionics DO-178C, medical IEC 62304) [UNVERIFIED as job titles at specific firms]. **Stage:** shared (the pipeline's traceability owner).
- **Mission:** Keep a bidirectional trace from Discovery evidence → PRD requirement → QAS/ADR/component → task → test/fitness function.
- **OWNS:** trace matrix schema and IDs; orphan/gap detection.
- **DOES NOT OWN:** content of any decision.
- **ACCEPTANCE:** zero orphan Must-haves; zero orphan components; every ADR links ≥1 driver ID.
- **REFUSAL:**
  - `blocked`: artifacts without stable IDs.
  - `rejected`: duplicate or reused IDs; an ADR number reused after supersession (violates the Nygard convention).
  - `out_of_scope`: judging design quality.
- **Handoffs:** invoked at every EXIT gate.

---

## Implications for agentic personas

### What to split and what to merge
1. **Orchestrator = Solution Architect (R1).** It keeps decision consolidation and the handoff. It **delegates** the following workers (each a fresh-context subagent returning a compact artifact):
   - (a) *characteristics & QAS analyst*: PRD → ranked characteristics, six-part QASs, utility tree with (importance, difficulty)
   - (b) *style & decomposition analyst*: quanta, style candidates, coupling/consistency analysis, granularity disintegrators/integrators
   - (c) *component & contract designer* (R3): C4 L2/L3 as code, API contracts, data ownership
   - (d) *ADR writer*: MADR from the options matrix
   - (e) *fitness-function designer*: one or more per driving characteristic
   - (f) *implementability reviewer* (R4)
   - (g) *platform/deployment* (R5, from the shared pool)
   - (h) *architecture critic* (R6) as the EXIT gate
   - Subagents cannot spawn subagents [LOCAL:ai/docs/claude-code/subagents/creating-custom-subagents.md:666], so the orchestrator must sequence (a)→(b)→(c,d,e in parallel)→(f,g, cross-cutting pool in parallel)→(h). Workers should be split by **context budget and phase**, not by human job title for its own sake [LOCAL:dev/research/2026-04-25-harness-engineering-research.md:1047]. Merge (d) into (b) if ADR volume is small.
2. **Enterprise Architect (R2) is not a live agent.** Model it as **static files** read at ENTRY (`org/tech-radar.*`, `org/standards.md`, reference architectures). A live "EA agent" would invent standards the organization does not have. If those files are absent, the orchestrator records "no org constraints provided" as an explicit assumption rather than hallucinating them.
3. **Critic independence.** R6 must run in a fresh subagent that receives *only* the handoff draft, the PRD handoff and the rubric. It must not see the worker transcripts, so it cannot inherit the author's rationalizations. Prefer a different model or tier for the critic when possible (cross-model review) [LOCAL:ai/docs/harness-engineering/harness-engineering.md:81].
4. **Rozanski & Woods mapping.** Viewpoints come from workers (a)–(c),(g). Perspectives come from the shared cross-cutting pool (security, privacy/regulation, accessibility, SRE/availability, FinOps). Each pool member returns `pass | pass-with-conditions | fail` *per view*, and conditions become ADRs or tasks.

### What LLMs tend to get wrong here (and the countermeasure)
- **Hype default.** Without strong constraints, models drift toward microservices + Kubernetes + Kafka + event sourcing. Countermeasure: force quantum analysis first. If there is 1 quantum, the default style must be a modular monolith or service-based, and any distributed style needs an ADR citing a specific disintegrator.
- **Fake trade-offs.** Generic pros/cons ("microservices: scalable; cons: complex"). Countermeasure: the options matrix must be scored *against this system's ranked QASs*, and every Bad consequence must name a QAS-ID or constraint.
- **Single-option ADRs written backwards** from a decision already made. Countermeasure: the schema demands ≥2 considered options. "Do nothing / buy / extend existing" always counts as one, so this is mechanical to check.
- **Adjective NFRs passed through** ("highly available"). Countermeasure: hard lint for a numeric or boolean response measure in each QAS. A failing NFR is either converted with an explicit assumption flagged for PRD confirmation, or the run is `rejected` back upstream.
- **Diagram hallucination.** Boxes that don't map to requirements, unlabeled arrows, inconsistent names between diagram and ADR. Countermeasure: diagrams-as-code (Structurizr DSL / Mermaid C4) plus a script check that element IDs in diagrams equal the IDs in the trace matrix.
- **Over-documentation.** Filling all 12 arc42 sections with filler. Countermeasure: allow "n/a — reason". Cap size, e.g., an executive one-pager ≤1 page and ADRs ≤1–2 pages (Nygard: keep ADRs short [UNVERIFIED wording]).
- **Ignoring the org/team context** (Conway). Countermeasure: the handoff must state ownership boundaries per container/quantum. The Tasks stage checks that no task spans two owners.
- **Inventing org standards or a radar** that were never provided. Countermeasure: ENTRY gate lists provided constraint files. Anything else is an explicit `assumption` with an ID.
- **Premature irreversibility.** Choosing vendor/DB specifics when the PRD doesn't need them yet. Countermeasure: each ADR declares *reversibility* (one-way door / two-way door) [BOOK:Bezos, Amazon 2015 Letter to Shareholders (published April 2016), "Type 1 / Type 2 decisions"]. One-way doors need ≥3 options and critic attention.

### Hard gates (deterministic, scriptable where possible)
**ENTRY gate (PRD → Architecture):**
- `blocked` if the PRD handoff file is missing, or required sections are missing (FR list with IDs, NFRs, constraints, non-goals, success metrics).
- `rejected` if FR IDs are not unique, NFRs are unmeasurable *and* lack the data needed to derive a measure (volumes, data class, availability expectation), or Must-haves contradict each other without priority.
- Record org-constraint files found or absent.

**EXIT gate (Architecture → Tasks):**
- Schema checks (scriptable):
  - every ADR is MADR-valid with ≥2 options, a status, and a Confirmation
  - every QAS has six fields with a measurable response measure
  - every driving characteristic has ≥1 fitness function with threshold + trigger
  - trace matrix has no orphans in either direction
  - diagram element IDs match the trace
  - no Hold-ring technology without an exception ADR
- Critic checks (LLM, rubric-bound): ATAM-style walk-through of every (H,H) scenario; findings typed (risk / non-risk / sensitivity / trade-off); verdict per criterion.
- Cross-cutting pool verdicts present; any `fail` blocks the handoff.
- Bounded loop: critic `rejected` → orchestrator revises (max 2–3 rounds) → otherwise write a handoff with status `rejected` and an escalation note for the human. Never silently downgrade.

**Handoff file contents for Tasks:**
- arc42-skeleton `architecture.md`
- `docs/decisions/*.md` (MADR)
- `c4/*.dsl` or Mermaid
- `qas.yaml`
- `fitness-functions.yaml`, each item turnable into a ticket
- `risks.md`
- `trace.csv`
- ownership boundaries
- walking-skeleton definition
- explicit `assumptions[]` and `open_questions[]`
- Each fitness function and each risk mitigation becomes a candidate task, so architecture is executable downstream [LOCAL:ai/docs/spec-driven-development/spec-driven-development-main.md:38].

### Persona prompt seeds (one line each)
- R1 orchestrator: "Everything is a trade-off; record the why; choose the fewest characteristics that matter; prefer reversible options; refuse to decide what the PRD hasn't validated."
- R6 critic: "You evaluate, you do not redesign. Every finding cites an ID and is typed risk, non-risk, sensitivity point or trade-off point."
- R4 implementability: "Show me the walking skeleton and the spikes; anything that can't ship incrementally is a risk."
- R5 platform: "Paved road first; deviations need an ADR; cognitive load is a design constraint."

---

## Sources

1. [WEB:https://github.com/joelparkerhenderson/architecture-decision-record/tree/main/locales/en/templates/decision-record-template-by-michael-nygard] — Nygard ADR template sections (fetched).
2. [WEB:https://github.com/npryce/adr-tools/blob/master/src/template.md] — adr-tools template text (fetched).
3. [WEB:https://github.com/adr/madr/blob/main/template/adr-template.md] and [WEB:https://github.com/adr/madr/blob/main/README.md] — MADR full template and conventions (fetched).
4. [WEB:https://arc42.org/overview/] — arc42 twelve sections (search summary; site blocked).
5. [WEB:https://www.archyl.com/blog/what-is-the-c4-model-complete-guide], [WEB:https://c4model.info/] — C4 levels and container definition (search summary).
6. [WEB:https://www.oreilly.com/library/view/fundamentals-of-software/9781098175504/ch27.html], [WEB:https://kb.segersian.com/software-architecture/topics/laws-of-software-architecture/] — laws of software architecture, including the 2nd-edition third law (search summary).
7. [WEB:https://en.wikipedia.org/wiki/Architecture_tradeoff_analysis_method] — ATAM steps and outputs.
8. [WEB:https://wstomv.win.tue.nl/edu/2ii45/year-0910/Software_Architecture_in_Practice_2nd_Edition_Chapter4.pdf] — six-part quality attribute scenario (search summary).
9. [WEB:https://www.oreilly.com/library/view/building-evolutionary-architectures/9781491986356/ch02.html], [WEB:https://continuous-architecture.org/practices/fitness-functions/], [WEB:https://gist.github.com/scottwd9/ada88f963aac95893e1eba10d4ad8f6d] — fitness function definition and categories.
10. [WEB:https://danlebrero.com/2022/03/30/software-architecture-the-hard-parts-book-summary/], [WEB:https://newsletter.techworld-with-milan.com/p/what-i-learned-from-the-software] — Hard Parts quantum, coupling, granularity.
11. [WEB:https://software-architecture-guild.com/guide/competencies/modeling/frameworks/viewpoints-and-perspectives/], [WEB:https://www.researchgate.net/publication/4236448_Using_Architectural_Perspectives] — Rozanski & Woods viewpoints and perspectives.
12. [WEB:https://itrevolution.com/articles/four-team-types/], [WEB:https://umbrex.com/resources/frameworks/organization-frameworks/team-topologies/], [WEB:https://teamtopologies.com/news-blogs-newsletters/2024/11/24/revisiting-team-topologies-misuses-of-platform-teams] — Team Topologies.
13. [WEB:https://chrisebert.net/software-architect-elevator-review/], [WEB:https://www.goodreads.com/book/show/49828197-the-software-architect-elevator] — Hohpe, Architect Elevator.
14. [WEB:https://www.freecodecamp.org/news/sacrificial-architecture-make-tough-decisions-to-abandon-and-rebuild-systems/], [WEB:https://mariadelia.blog/2025/11/16/understanding-software-architecture-through-martin-fowlers-lens/] — Fowler: sacrificial architecture, "important stuff".
15. [WEB:https://www.thoughtworks.com/insights/blog/build-your-own-technology-radar], [WEB:https://github.com/red-gate/Tech-Radar/issues/5] — Tech Radar rings and quadrants (search summary).
16. [WEB:https://leaddev.com/career-development/how-master-four-staff-archetypes-and-elevate-your-impact], [WEB:https://newsletter.pragmaticengineer.com/p/software-architect-archetypes] — staff archetypes; architect archetypes (twelve, Orosz 2023).
16a. [WEB:https://www.industrialempathy.com/posts/design-docs-at-google/] — Malte Ubl, "Design Docs at Google" (design-doc section list).
17. [BOOK:Richards & Ford, Fundamentals of Software Architecture, O'Reilly, 2020; 2nd ed. 2025].
18. [BOOK:Ford, Richards, Sadalage, Dehghani, Software Architecture: The Hard Parts, O'Reilly, 2021].
19. [BOOK:Bass, Clements, Kazman, Software Architecture in Practice, 4th ed., Addison-Wesley, 2021].
20. [BOOK:Clements et al., Documenting Software Architectures: Views and Beyond, 2nd ed., 2010].
21. [BOOK:Rozanski & Woods, Software Systems Architecture, 2nd ed., Addison-Wesley, 2011].
22. [BOOK:Brown, Software Architecture for Developers vols. 1–2; The C4 Model, Leanpub].
23. [BOOK:Ford, Parsons, Kua, Sadalage, Building Evolutionary Architectures, 2nd ed., O'Reilly, 2022].
24. [BOOK:Hohpe, The Software Architect Elevator, O'Reilly, 2020; Cloud Strategy, 2020].
25. [BOOK:Fowler, "Who Needs an Architect?", IEEE Software, 2003].
26. [BOOK:Conway, "How Do Committees Invent?", Datamation, 1968].
27. [BOOK:Skelton & Pais, Team Topologies, IT Revolution, 2019; 2nd ed. Sept 2025 — confirmed WEB:https://itrevolution.com/product/team-topologies-second-edition/].
28. [BOOK:Larson, Staff Engineer: Leadership Beyond the Management Track, 2021].
29. [BOOK:Evans, Domain-Driven Design, 2003].
30. [LOCAL:ai/docs/claude-code/subagents/creating-custom-subagents.md] — subagents cannot spawn subagents; `--agent` main thread.
31. [LOCAL:ai/docs/harness-engineering/harness-engineering.md] — deterministic back-pressure; cross-model review.
32. [LOCAL:ai/docs/spec-driven-development/spec-driven-development-main.md] — Spec Kit constitution / enforced architectural constraints.
33. [LOCAL:dev/research/2026-04-25-harness-engineering-research.md] — subagents for context isolation, not human-role specialization.

---

## Verification log

Verifier pass on 2026-10-02 (citations and attributed claims only; no new research). Method: GitHub raw fetches, web search summaries (primary sites such as martinfowler.com, cognitect.com, c4model.com are blocked by the proxy), local-corpus line checks, and the verifier's own knowledge for well-known books.

**Confirmed (online or local):**
- FoSA laws, including the 2nd-edition third law and its wording; O'Reilly ch. 27 "The Laws of Software Architecture, Revisited" (web search).
- adr-tools template: section order (Number/Title, Date, Status, Context, Decision, Consequences) and the exact Consequences sentence (raw GitHub fetch).
- MADR template: Confirmation text "Is there any automated or manual fitness function?" with the ArchUnit example is verbatim (raw GitHub fetch).
- Hohpe, *Architect Elevator*: ch. 9 "Architecture Is Selling Options" in Part II (table of contents via search).
- Team Topologies 2nd ed. (IT Revolution, 23 Sept 2025).
- Orosz, "Software Architect Archetypes" (Pragmatic Engineer, July 2023) exists.
- Local references: creating-custom-subagents.md lines 47, 295 and 666 (subagents cannot spawn subagents); harness-engineering.md:14 (deterministic back-pressure) and :81 (cross-model review); spec-driven-development-main.md:38 (Spec Kit "constitutional foundation"); harness-engineering-research.md:1047 (subagents for context isolation, not specialization). All lines match the claims.

**Confirmed from the verifier's own knowledge (not re-fetched):** FoSA ch. 1 (eight expectations), ch. 2 (knowledge pyramid, frozen caveman), ch. 4–5, ch. 7, ch. 8 (entity trap), ch. 19 (Covering Your Assets / Groundhog Day / Email-Driven Architecture anti-patterns); Hard Parts quantum definition, ch. 7 disintegrators/integrators, ch. 12 eight sagas, ch. 15; SAiP six-part QAS, ATAM nine steps and outputs, utility tree; Views and Beyond (2nd ed. 2010); Rozanski & Woods viewpoints and perspectives; arc42 twelve sections; BEA fitness-function definition and categories, 2nd-ed. subtitle; Fowler/Ralph Johnson "important stuff" (IEEE Software 2003); Design Stamina Hypothesis (2007) and Technical Debt Quadrant (2009); Conway 1968 (Datamation); Team Topologies types and modes; Tech Radar quadrants and rings; Larson's four archetypes; TOGAF 10th ed. (2022).

**Corrected:**
- R4 design-doc section list was attributed to *Software Engineering at Google* (Winters et al.). It comes from Malte Ubl, "Design Docs at Google" (industrialempathy.com, 2020). Citation replaced (web search confirmed).
- Hohpe chapter titles "Architects Look for Trade-Offs" / "Architects as Enablers" do not appear in the table of contents. Retagged as UNVERIFIED location; "Architects Sell Options" corrected to ch. 9 "Architecture Is Selling Options".
- Orosz article: it describes twelve archetypes, not a spectrum from ivory tower to hands-on. Description corrected.
- QAS checkout example was presented as if from SAiP. It is now labeled as an illustrative example written for this note.
- "mini-QAW" was attributed to SAiP. It comes from Ozkaya/Keeling/Chaparro (see Keeling, *Design It!*, 2017); attribution kept UNVERIFIED.
- Nygard section order: added a note that the essay's order differs from the adr-tools order.

**Upgraded from UNVERIFIED:** Bezos one-way/two-way doors (2015 shareholder letter, "Type 1/Type 2 decisions"); McKinley "Choose Boring Technology" retagged as a 2015 essay, not a book.

**Left as UNVERIFIED (could not confirm; low impact on persona design):** Nygard essay exact wording (cognitect.com blocked); C4 supplementary-diagram list completeness and Brown's notation checklist wording; Fowler bliki pages (blocked); Wardley as a book citation; build-vs-buy evaluation dimensions (synthesized); TOGAF edition detail; regulated-industry job titles; SAiP 4th-ed. chapter title for evaluation.
