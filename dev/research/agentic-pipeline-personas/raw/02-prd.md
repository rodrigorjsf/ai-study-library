# Raw research — PRD & requirements

Axis: PRD and requirements engineering. Pipeline stage covered: **(2) PRD**, with entry from Discovery and exit to Architecture/Tasks.
Each stage runs as its own orchestrator (`claude --agent prd-orchestrator`) in a fresh session, so the PRD stage receives *only* the Discovery handoff file and can only send work downstream through its own handoff file.

Tag legend: [WEB:url] read or confirmed online in this session; [BOOK:...] from a well-known book; [LOCAL:path] from the local corpus; [UNVERIFIED] uncertain detail.
Note on the web: many primary sites (svpg.com, basecamp.com, alistairmavin.com, atlassian.com, lennysnewsletter.com, iso25000.com, volere.org PDFs) were blocked by the egress proxy. Where a claim relies on a search-result summary rather than the primary page, it is still tagged WEB with the search-result URL, and the claim is kept to what the summary supports.

---

## Literature & frameworks

### 1. Marty Cagan — critique of the PRD (Inspired; SVPG essays)
- Cagan's main critique: a PRD written by a PM who *believes they already know the answer*, and handed to engineers as "requirements", is a root cause of failed products. Most ideas fail, so requirements have to come out of discovery evidence, not opinion [WEB:https://uservoice.com/blog/is-the-product-requirements-document-dead] [BOOK:Cagan, Inspired, 2nd ed., 2017, Part IV "The Right Process" — Product Discovery] (corrected part title; confirmed [WEB:https://www.oreilly.com/library/view/inspired-2nd-edition/9781119387503/p04a.xhtml]).
- In "Revisiting the Product Spec" (SVPG, October 2006 — corrected from 2007), Cagan argued that a high-fidelity prototype should be the primary form of the spec, replacing most of the traditional written PRD [WEB:https://www.svpg.com/revisiting-the-product-spec/ (search summary)] [WEB:https://uservoice.com/blog/is-the-product-requirements-document-dead].
- He describes four product risks to settle in discovery: value, usability, feasibility and business viability [BOOK:Cagan, Inspired, 2nd ed., Part IV "The Right Process", ch. 33 "Principles of Product Discovery"] [WEB:https://www.svpg.com/four-big-risks/]. **Persona implication:** the PRD must carry the *evidence status* of each risk from Discovery. If it does not, it is writing opinion as spec.
- Cagan separates discovery prototypes (built to answer questions) from delivery products [WEB:https://enterprisezone.cc/distinguishing-product-discovery-prototypes-from-delivery-products-according-to-marty-cagan/].
- Takeaway for the pipeline: the PRD is a *communication and commitment* artifact that encodes validated learning. It is not the place where the problem is invented. The ENTRY gate has to reject a Discovery handoff that has no evidence.

### 2. Modern lean PRD templates (Kevin Yien / Square; Lenny Rachitsky; Atlassian)
- Kevin Yien's template (Square) is staged: **Draft → Problem Review → Solution Review → Launch Review → Launched**. Each part ends with a stakeholder sign-off before the next part starts [WEB:https://www.prodmgmt.world/blog/prd-template-guide] [WEB:https://docs.google.com/document/d/1mEMDcHmtQ6twzNlpvF-9maNlAcezpWDtCnyIqWkODZs/edit (title confirmed via search)].
- Part 1, Problem Alignment: the problem, why it matters to users and the business, customer insights, sign-off. Part 2, Solution Alignment: solution overview, goals, **Non-goals**, key flows and logic, mockups, edge cases, sign-off. Part 3, Launch Readiness: launch plan, metrics and success criteria, rollout [WEB:https://www.prodmgmt.world/blog/prd-template-guide].
- The template's most important feature is *ordered alignment*: no solution content until the problem is signed off. This maps directly onto an internal sub-gate inside the PRD orchestrator.
- Lenny Rachitsky has popularised Yien's template and his own 1-pager style. The 1-pager style holds that a PRD should be short, that its "why" and success metrics should come first, and that it should be treated as a living document [WEB:https://www.lennysnewsletter.com/p/my-favorite-templates-issue-37 (blocked; listing seen via search)] [UNVERIFIED for exact section list].
- Atlassian's agile requirements page recommends a one-page, living, collaborative PRD. It contains: project specifics (participants, status, target release), team goals and business objectives, background and strategic fit, assumptions, user stories, user interaction and design, questions, and **"Not doing"** [UNVERIFIED — page blocked; from memory of atlassian.com/agile/product-management/requirements].
- Common bar across all three: explicit non-goals, success metrics defined *before* build, open questions tracked in the document, and links instead of copied content.

### 3. Amazon Working Backwards — PR/FAQ (Bryar & Carr, 2021)
- The press release is written *before* the initiative is approved or built, as if launch day had arrived. It forces customer-first framing [WEB:https://www.koji.so/docs/working-backwards-pr-faq-guide] [BOOK:Bryar & Carr, Working Backwards, 2021, ch. 5 "Working Backwards"].
- Structure: about a one-page press release plus a multi-page FAQ. The **External FAQ** holds customer questions. The **Internal FAQ** covers viability, cost, risks, dependencies, metrics and the competitive landscape [WEB:https://www.koji.so/docs/working-backwards-pr-faq-guide].
- It belongs to Amazon's narrative culture: in 2004 Amazon replaced PowerPoint with six-page narrative memos, because writing in prose forces clear thinking [WEB:https://summaries.com/blog/working-backwards].
- The press release has a recognisable shape: headline, subheading (who the customer is and what the benefit is), problem paragraph, solution paragraph, leader quote, how to get started, customer quote, call to action [BOOK:Bryar & Carr, Working Backwards, ch. 5] [UNVERIFIED exact paragraph order].
- Persona use: a PR/FAQ is an excellent *Discovery→PRD bridge*. The Internal FAQ is a ready-made checklist for risks and assumptions, and a PRD critic can check "would a customer care about this headline?".

### 4. Basecamp Shape Up (Ryan Singer, 2019)
- A pitch has five ingredients: **Problem, Appetite, Solution, Rabbit holes, No-gos** [BOOK:Singer, Shape Up, 2019, ch. 6 "Write the Pitch"] (primary page blocked; the five-ingredient list is well known).
- **Appetite** is a fixed time budget, for example a 2-week small batch or a 6-week big batch. Scope bends to fit the time, the opposite of an estimate. This is "fixed time, variable scope" [BOOK:Singer, Shape Up, ch. 3 "Set Boundaries"].
- Shaped work is "rough, solved, bounded": abstract enough to leave room for designers, but with the main elements worked out [BOOK:Singer, Shape Up, ch. 2 "Principles of Shaping"].
- **Rabbit holes** are known technical or design risks that are named and patched in the pitch so they cannot sink the bet. **No-gos** are explicitly excluded functionality [BOOK:Singer, Shape Up, ch. 5 "Risks and Rabbit Holes"].
- Breadboards and fat-marker sketches set the level of fidelity: enough to communicate flows without locking in UI [BOOK:Singer, Shape Up, ch. 4 "Find the Elements"].
- Persona use: the PRD should declare an *appetite* (a scope budget for the Tasks stage), a rabbit-hole list (sent to the Architecture stage), and no-gos (enforced downstream as out_of_scope).

### 5. Lean UX (Jeff Gothelf & Josh Seiden, 3rd ed. 2021)
- Requirements are restated as **assumptions → hypotheses**. The canonical hypothesis template is: "We believe [this business outcome] will be achieved if [these users] attain [this user outcome] with [this feature]" [BOOK:Gothelf & Seiden, Lean UX, 3rd ed., 2021, ch. "Hypotheses"].
- The Lean UX Canvas covers business problem, business outcomes, users, user outcomes and benefits, solutions, hypotheses, "what's the most important thing we need to learn first?", and "least amount of work to learn it?" [BOOK:Gothelf & Seiden, Lean UX, 3rd ed., Lean UX Canvas].
- Outcomes are changes in customer behaviour. They are not outputs (features) [BOOK:Seiden, Outcomes Over Output, 2019].
- Persona use: every Must-have in the PRD should trace back to a hypothesis with a measurable success signal. Requirements with no hypothesis are "output-only" and a critic should flag them.

### 6. Karl Wiegers & Joy Beatty — Software Requirements, 3rd ed. (2013)
- Three requirement levels: **business** (organisational goals and benefits), **user** (tasks users must perform), and **functional** (system behaviour under specific conditions). Their documents are the Vision & Scope document, the user requirements document, and the SRS [WEB:https://github.com/craigtp/BookDigests/blob/master/BookDigests/SoftwareRequirements.md].
- Characteristics of an excellent individual requirement: **complete, correct, feasible, necessary, prioritized, unambiguous, verifiable** [WEB:https://github.com/craigtp/BookDigests/blob/master/BookDigests/SoftwareRequirements.md].
- Characteristics of a requirements collection: **complete, consistent, modifiable, traceable** [WEB:https://github.com/craigtp/BookDigests/blob/master/BookDigests/SoftwareRequirements.md].
- Words that hide multiple or vague requirements include "and/or", "also" and "unless". Modal verbs (shall/must/should/will) must be used consistently [WEB:https://github.com/craigtp/BookDigests/blob/master/BookDigests/SoftwareRequirements.md]. Wiegers also lists ambiguous terms to avoid, such as "user-friendly", "fast", "robust", "etc.", "as appropriate" and "support" [BOOK:Wiegers & Beatty, Software Requirements 3rd ed., ch. 11 "Writing excellent requirements"].
- Quality attributes (the "-ilities") have to be elicited early because they are expensive to retrofit [WEB:https://github.com/craigtp/BookDigests/blob/master/BookDigests/SoftwareRequirements.md] [BOOK:Wiegers & Beatty, ch. 14 "Beyond functionality"].
- Prioritization techniques: MoSCoW, an importance/urgency three-level scale, pairwise comparison, and QFD-style weighted value/cost/risk [WEB:https://github.com/craigtp/BookDigests/blob/master/BookDigests/SoftwareRequirements.md].
- The digest defines the BA as someone who enables change in an organizational context by defining needs and recommending solutions that deliver value to stakeholders [WEB:same]. (Corrected: the digest does not cite IIBA; the wording does match the IIBA BABOK v3 definition [BOOK:IIBA, BABOK Guide v3, 2015].)
- Persona use: Wiegers' characteristics become a **per-requirement lint**. "Prioritized" and "Feasible" need other roles: the PM gives priority and the tech lead gives feasibility.

### 7. ISO/IEC/IEEE 29148:2018 (requirements engineering)
- Each individual requirement must have nine characteristics: **Necessary, Appropriate, Unambiguous, Complete, Singular, Feasible, Verifiable, Correct, Conforming** [WEB:https://www.researchgate.net/publication/385802396_Well-Formed_Quality_of_System_Requirements_for_Verifying_to_ISO_29148-2018_A_Natural_Language_Processing_NLP_Based_Framework_and_Quantitative_Metric (search summary)].
- A requirement *set* must also be complete, consistent, feasible, comprehensible and able to be validated (5 set characteristics) [WEB:same summary confirms "5 more judging the set"; names UNVERIFIED-from-memory].
- The standard describes the information items StRS (stakeholder requirements specification), SyRS and SRS, plus requirement attributes such as identification, priority, rationale, risk, source, verification method and status [BOOK:ISO/IEC/IEEE 29148:2018 §5.2.8, §9] [UNVERIFIED section numbers]. Templates exist [WEB:https://www.reqview.com/doc/iso-iec-ieee-29148-templates/].
- It lists unbounded or ambiguous terms to avoid, such as superlatives, subjective language, vague pronouns, "but not limited to", and open-ended words like "etc." and "and so on" [BOOK:ISO/IEC/IEEE 29148:2018 §5.2.7 "Requirements language criteria"] [UNVERIFIED exact list].
- "Singular" (one requirement per statement) and "Conforming" (follows the agreed template or pattern) are the two characteristics most directly checkable by a machine. They are good candidates for a deterministic hook or linter rather than an LLM judgment.

### 8. Volere (James & Suzanne Robertson, Mastering the Requirements Process)
- The template has about 27 sections, and teams use only the subset they need. Sections fall into project drivers, project constraints, functional requirements, non-functional requirements and project issues (open issues, off-the-shelf solutions, new problems, tasks, migration, risks, costs, user documentation, waiting room, ideas for solutions) [WEB:https://www.reqview.com/doc/volere-template/ (search summary)] [BOOK:Robertson & Robertson, Mastering the Requirements Process, 3rd ed., 2012].
- **Fit criterion**: every requirement carries a quantified benchmark that lets a tester decide objectively whether it is met. In the Volere philosophy, "testing starts when you write the requirement" [WEB:search summary of volere.org template].
- The **Snow Card** (requirement shell) holds id, type, event/use case, description, rationale, originator, fit criterion, customer satisfaction and dissatisfaction ratings (1-5), priority, conflicts, supporting material and history [WEB:https://bacoach.nl/2026/03/the-volere-snow-card/ (search summary)] [BOOK:Robertson & Robertson] [UNVERIFIED for full field list].
- The **Waiting Room** section parks requirements deferred to later releases. It is a useful mechanism for non-goals that are "not now" rather than "never".
- Persona use: the Snow Card is a ready-made JSON schema for an atomic requirement in a machine-readable PRD handoff.

### 9. EARS — Easy Approach to Requirements Syntax (Mavin et al., Rolls-Royce, RE'09)
- Generic form: `While <precondition(s)>, when <trigger>, the <system name> shall <system response>` [WEB:https://www.incose.org/docs/default-source/working-groups/requirements-wg/rwg_iw2022/mav_ears_incoserwg_jan22.pdf (search summary)].
- Five patterns [WEB:search summary; templates from BOOK/memory of Mavin et al. 2009]:
  - Ubiquitous: `The <system> shall <response>`.
  - State-driven: `While <state>, the <system> shall <response>`.
  - Event-driven: `When <trigger>, the <system> shall <response>`.
  - Optional feature: `Where <feature is included>, the <system> shall <response>`.
  - Unwanted behaviour: `If <trigger>, then the <system> shall <response>`.
  - Complex: a combination of the keywords above.
- EARS is the requirements syntax used by AWS Kiro: Kiro's docs say it expands an idea into user stories whose acceptance criteria are written in EARS notation ("WHEN <condition> THE SYSTEM SHALL <behaviour>") [WEB:https://kiro.dev/docs/specs/feature-specs/ (search summary)] [WEB:https://www.braingrid.ai/blog/ears-notation (search result title)]. (Correction: the local corpus [LOCAL:ai/docs/spec-driven-development/spec-driven-development-variant.md:57] describes Kiro's acceptance criteria as "GIVEN… WHEN… THEN…"; Kiro's own docs say EARS, so treat the GWT description as the article author's paraphrase.)
- Warning from the local corpus: Kiro turned a small bug fix into 4 user stories with 16 acceptance criteria. Over-specification makes reviewing the spec cost more than reviewing the code would [LOCAL:ai/docs/spec-driven-development/spec-driven-development-main.md:40,82].
- Persona use: EARS is the best default syntax for LLM-written functional requirements because it is pattern-checkable. Explicit "If/then" for unwanted behaviour makes error and edge-case coverage auditable.

### 10. ISO/IEC 25010 (product quality model) for NFRs
- The 2023 edition has nine characteristics: **Functional Suitability, Performance Efficiency, Compatibility, Interaction Capability, Reliability, Security, Maintainability, Flexibility, Safety** [WEB:https://www.tiespecialistas.com.br/en/iso-iec-25010-software-quality-characteristics-examples/ (search summary)].
- Compared with 2011, Usability became Interaction Capability, Portability became Flexibility, and Safety was added [WEB:same search summary].
- Persona use: an NFR checklist for the PRD. Each of the nine is either stated with a measurable target or explicitly marked N/A with a reason. The arc42 quality model is a reference for scenario-style NFRs [WEB:https://quality.arc42.org/standards/iso-25010 (search result)].
- NFRs in the PRD should be *user-observable targets* ("p95 search results ≤ 1 s for catalogs ≤ 100k items"). They should not prescribe a design ("use Redis"), which belongs to Architecture.

### 11. Success metrics — North Star, HEART, OKRs, guardrails
- **HEART** (Rodden, Hutchinson, Fu — Google, CHI 2010) has five dimensions: Happiness, Engagement, Adoption, Retention, Task success. It is paired with the **Goals → Signals → Metrics** process [WEB:https://ixdf.org/literature/topics/heart-framework (search summary)].
- **North Star Metric**: one metric that captures the core value customers get, backed by input metrics the team can move [BOOK:Amplitude, North Star Playbook] [UNVERIFIED edition].
- **OKRs**: a qualitative Objective plus 3-5 measurable Key Results. Key results are outcomes, not task lists [BOOK:Doerr, Measure What Matters, 2018].
- **Guardrail metrics**: metrics that must *not* degrade (latency, error rate, unsubscribe rate, revenue per user), with explicit thresholds [BOOK:Kohavi, Tang & Xu, Trustworthy Online Controlled Experiments, 2020, ch. 6 "Organizational Metrics" (goal / driver / guardrail taxonomy; organizational guardrails such as latency and revenue per user); ch. 21 is "Sample Ratio Mismatch and Other Trust-Related Guardrail Metrics"] (corrected chapter attribution) [WEB:https://www.cambridge.org/core/books/abs/trustworthy-online-controlled-experiments/organizational-metrics/76086E652574E0A1719741FF7B26A146].
- Persona use: every PRD has to say (a) one primary success metric with a baseline, a target and a time window, (b) 1-3 secondary or HEART metrics, (c) guardrails with thresholds, and (d) instrumentation events. A metric with no baseline is a blocker for the metrics owner.

### 12. Prioritization — MoSCoW, RICE, Kano, Cost of Delay / WSJF
- **MoSCoW** (Must/Should/Could/Won't-this-time), from DSDM [BOOK:DSDM Agile Project Framework]. DSDM recommends keeping Must Have effort to no more than about 60% of the total [WEB:https://www.agilebusiness.org/dsdm-project-framework/moscow-prioritisation.html (search summary)].
- **RICE** (Sean McBride, Intercom): score = Reach × Impact × Confidence ÷ Effort. Impact is on a fixed scale (3/2/1/0.5/0.25), Confidence is 100/80/50%, and Effort is in person-months [WEB:https://kayako.com/blog/rice-prioritization/ (search summary)].
- **Kano** (Noriaki Kano, 1984) sorts features into must-be (basic), one-dimensional (performance), attractive (delighters), indifferent and reverse, using paired functional and dysfunctional survey questions [BOOK:Kano et al., "Attractive quality and must-be quality", 1984].
- **Cost of Delay / WSJF**: SAFe defines WSJF = (User-Business Value + Time Criticality + Risk Reduction/Opportunity Enablement) ÷ Job Size (relative) [WEB:https://framework.scaledagile.com/wsjf/ (search summary)]. Reinertsen's original rule is WSJF as cost of delay divided by duration [BOOK:Reinertsen, The Principles of Product Development Flow, 2009]; the label "CD3" (Cost of Delay Divided by Duration) was coined later by Joshua Arnold (Black Swan Farming) (corrected attribution) [WEB:https://blackswanfarming.com/wsjf-weighted-shortest-job-first/].
- Persona use: the PRD should use **one** declared method and show its inputs. An LLM will invent RICE numbers, so Reach and Confidence must cite Discovery evidence, or Confidence is capped at 50%.

### 13. Scope, non-goals, risks/assumptions, release criteria
- Non-goals appear in Yien's template, Atlassian's "Not doing", Shape Up's no-gos and Volere's Waiting Room. All four converge on the idea that explicit exclusion is part of scope [WEB:https://www.prodmgmt.world/blog/prd-template-guide].
- Assumptions and risks: the Internal FAQ in a PR/FAQ, Shape Up rabbit holes, Volere's "Risks" section, and the Lean UX assumption list. Each assumption should carry a validation status and an owner.
- Release criteria: a common PRD section that sets measurable go/no-go thresholds (functional completeness, quality, performance, supportability) [BOOK:Wiegers & Beatty, Software Requirements 3rd ed., release-readiness discussion] [UNVERIFIED chapter]. In Yien's template this is the Launch Review stage.
- Local corpus: separating the functional spec from technical implementation is hard in practice, and Spec Kit users were often confused about which level they were writing at [LOCAL:ai/docs/spec-driven-development/spec-driven-development-variant.md:125]. A PRD persona needs an explicit "no implementation" rule.

---

## Real-world roles

### R1. Product Manager — PRD owner
- **Titles:** Product Manager, Senior/Group PM, Product Owner (Scrum), Technical PM. **Stages:** PRD (owner). Consumes Discovery output and is consulted by Architecture and Tasks.
- **Mission:** Turn validated opportunity evidence into a bounded, prioritized and measurable commitment, and own the "why" and "what". The "how" is not theirs.
- **Mindset & principles:**
  - Outcomes over output: requirements are bets tied to hypotheses [BOOK:Seiden, Outcomes Over Output] [BOOK:Gothelf & Seiden, Lean UX].
  - Work backwards from the customer, starting with the headline [WEB:https://www.koji.so/docs/working-backwards-pr-faq-guide].
  - Problem alignment before solution alignment [WEB:https://www.prodmgmt.world/blog/prd-template-guide].
  - Fixed appetite, variable scope [BOOK:Singer, Shape Up ch. 3].
  - Treat the four risks (value, usability, feasibility, viability) as named, with evidence [BOOK:Cagan, Inspired].
- **OWNS:** problem statement, target users/personas reference, goals, non-goals, prioritization decisions, success metric selection (jointly with the analyst), scope and appetite, open questions log, sign-off routing, final PRD.
- **DOES NOT OWN:** solution architecture or technology choice (Tech Lead/Architecture), UI visual design (Designer), metric instrumentation design (Analyst), test cases (QA), compliance rulings (shared Privacy/Compliance), task breakdown and estimates (Tasks stage).
- **Inputs:** Discovery handoff (problem/opportunity statement, evidence, personas/JTBD, opportunity solution tree, validated and unvalidated assumptions, competitive notes), business objective/OKR, constraints (deadline, budget, regulatory flags).
- **Outputs:** PRD in a lean staged template (Yien-style): Header/status; Problem (why it matters to users and the business, evidence links); Goals; Non-goals; Users and use cases; Requirements (prioritized, IDs); Key flows; Success metrics and guardrails; Assumptions and risks; Open questions; Release criteria; Sign-offs. Optional PR/FAQ front matter.
- **ACCEPTANCE criteria:**
  - [ ] The problem statement names a specific user segment, a specific pain, and links at least one evidence item from Discovery.
  - [ ] At least one goal, each tied to a metric that has a baseline, target and time window.
  - [ ] At least 3 explicit non-goals. Each states why ("not now", which goes to the waiting room, versus "never").
  - [ ] Every requirement has a unique ID, a priority under one declared scheme, and a trace link to a goal or hypothesis.
  - [ ] An appetite or scope budget is declared, and Musts fit within it per the tech lead feasibility note.
  - [ ] The open questions list is empty, or every item has an owner and is marked non-blocking.
  - [ ] Contains no implementation prescriptions (no named technologies, schemas or endpoints) unless they are a stated constraint with a source.
- **REFUSAL criteria:**
  - *blocked*: no Discovery handoff, or the handoff has no target user, no problem evidence, or no business objective. A PM will not write a PRD from a solution-only idea ("build X") with no problem.
  - *blocked*: no decision-maker or constraint information (deadline/appetite unknown and not inferable). The PM writes this as an explicit assumption and asks; it is not fatal if a default appetite is allowed.
  - *rejected*: the Discovery handoff states a value hypothesis as validated, but the evidence is only internal opinion. Another rejection case: Discovery evidence contradicts its own conclusion.
  - *out_of_scope*: requests to choose the tech stack, produce estimates or sprint plans, write marketing/GTM positioning (GTM/PMM is an extension point), or make legal determinations.
- **Anti-patterns:** a PRD as a feature list with no "why"; solution-first PRDs; "everything is a Must"; no non-goals; vanity metrics (page views) with no guardrails; spec bloat (the Kiro "16 acceptance criteria for a bug" failure [LOCAL:ai/docs/spec-driven-development/spec-driven-development-main.md:40]); a PRD that is never updated after decisions change; copying discovery text in place of synthesising it.
- **Handoffs:** receives from the Discovery orchestrator handoff (product discovery lead/UX researcher outputs). Delivers to the PRD critic (review), then to Architecture (Tech Lead/Architect) and Tasks (Eng Manager/Tech Lead) via the PRD handoff file.

### R2. Business Analyst / Requirements Engineer
- **Titles:** Business Analyst, Requirements Engineer, Systems Analyst, Product Analyst (in some orgs), IIBA CBAP/PMI-PBA holders. **Stages:** PRD (primary). Discovery (elicitation support), Tasks (refinement).
- **Mission:** Turn stakeholder needs into a set of atomic, unambiguous, verifiable, traceable requirements: business, then user, then functional/non-functional.
- **Mindset & principles:**
  - Three requirement levels; do not mix them [WEB:https://github.com/craigtp/BookDigests/blob/master/BookDigests/SoftwareRequirements.md].
  - Every requirement is Necessary, Appropriate, Unambiguous, Complete, Singular, Feasible, Verifiable, Correct, Conforming [WEB:ISO 29148 summary, researchgate].
  - "Start testing when you write the requirement": every requirement gets a fit criterion [WEB:volere search summary].
  - Constrained natural language (EARS) beats free prose [WEB:incose EARS summary].
  - Elicit NFRs early; they are costly to retrofit [WEB:BookDigests].
- **OWNS:** requirement statements (functional and NFR), glossary/data dictionary, business rules catalog, requirement attributes (ID, type, source, rationale, priority as given by the PM, fit criterion, status), use-case and edge-case enumeration, consistency and completeness analysis, requirements traceability (forward links into the PRD; shares the matrix with the traceability owner).
- **DOES NOT OWN:** priority decisions (the PM decides; the BA facilitates), solution design, test scripts (QA), metric definitions (Analyst), UI copy (Designer/UX writer).
- **Inputs:** the PM's problem, goals and non-goals; Discovery JTBD and journey; domain rules and regulations (via the shared compliance role); existing system behaviour, if brownfield.
- **Outputs:** Requirements section/SRS-lite, with each requirement as a Volere-style shell: `{id, type: FR|NFR|BR|constraint, statement (EARS), rationale, source, priority, fit_criterion, acceptance (Given/When/Then), dependencies, status}`. Glossary. Business-rule table. NFR matrix against ISO 25010 (9 rows, each target-or-N/A). Use-case list with main, alternate and exception flows.
- **ACCEPTANCE criteria:**
  - [ ] 100% of FRs match an EARS pattern (regex-checkable keywords: `shall`, optional `While/When/Where/If…then`).
  - [ ] Each statement is singular: no "and/or", no "also", only one `shall` [WEB:BookDigests ambiguous-words guidance].
  - [ ] No banned vague terms (fast, user-friendly, robust, flexible, as appropriate, etc., support, minimize, maximize, easy) unless quantified in the fit criterion.
  - [ ] Every requirement has a fit criterion that is measurable, with a number, a unit and a condition.
  - [ ] Every "If…then" unwanted-behaviour case exists for each external input and integration listed in the flows.
  - [ ] All 9 ISO 25010 characteristics are addressed (target or justified N/A).
  - [ ] Glossary defines every domain noun used in more than one requirement. No synonyms are used for the same concept.
  - [ ] No two requirements conflict. A conflicts field is filled where trade-offs exist.
- **REFUSAL criteria:**
  - *blocked*: no stated users or actors; no goals to trace to; domain rules referenced but not provided ("follow our refund policy" with no policy).
  - *rejected*: an upstream "requirement" that is really a solution ("use a dropdown") with no underlying need, or that contradicts a stated non-goal. The BA returns it to the PM for rationale.
  - *out_of_scope*: deciding priority, writing code-level design, producing test automation, ruling on legal compliance.
  - Refuses to produce: requirements without a fit criterion; compound requirements; "TBD" values without a tracked open-question ID.
- **Anti-patterns:** gold-plating (adding requirements nobody asked for); requirements written as implementation; 50-page SRS for a 2-week appetite; passive voice that hides the actor ("data shall be validated"); missing negative and exception paths; inconsistent modal verbs.
- **Handoffs:** receives from the PM (scope, goals) and Discovery (JTBD, journeys). Delivers to QA (verifiability review), the Tech Lead (feasibility), the traceability owner (IDs), and the Architecture stage (NFR matrix).

### R3. Product Designer / UX Writer — flows & interaction requirements
- **Titles:** Product Designer, UX Designer, Interaction Designer, UX/Content Designer, UX Writer. **Stages:** Discovery (prototypes and research), PRD (flows and key screens), Tasks (design specs).
- **Mission:** Make the requirements concrete as user flows and states, at the right fidelity, so the experience is specified without freezing the UI too early.
- **Mindset & principles:**
  - Breadboards and fat-marker sketches: right-sized fidelity ("rough, solved, bounded") [BOOK:Singer, Shape Up ch. 2, 4].
  - Prototype to describe requirements; the prototype is evidence [WEB:https://uservoice.com/blog/is-the-product-requirements-document-dead].
  - Design for every state: empty, loading, partial, error, success. Content (words) is part of the interface [BOOK:Yifrah, Microcopy: The Complete Guide, 2017] (author name corrected from "Yifrach"; 1st ed. 2017, 2nd ed. 2019).
  - Interaction Capability (ISO 25010:2023) and accessibility are requirements, not polish [WEB:tiespecialistas 25010 summary].
- **OWNS:** user flows (happy path, alternates, errors), key-screen inventory and states, interaction rules, content/microcopy requirements (error messages, empty states, terminology aligned to the glossary), usability acceptance criteria.
- **DOES NOT OWN:** what to build and why (PM), business rules (BA), accessibility conformance verdict (shared Accessibility role), visual design system tokens (out of PRD scope; implementation detail).
- **Inputs:** PRD problem/goals, personas/JTBD, requirement IDs, Discovery prototypes and usability findings.
- **Outputs:** flow diagrams (Mermaid or breadboard text form: places → affordances → connections), screen-state matrix (screen × state), copy deck for critical messages, links to prototypes. Each flow step references FR IDs.
- **ACCEPTANCE criteria:**
  - [ ] Every Must FR that a user can observe appears in at least one flow step, and every flow step maps to an FR (bidirectional).
  - [ ] Every screen in the inventory has defined empty, loading, error and success states, or N/A with a reason.
  - [ ] Every "If…then" unwanted-behaviour requirement has a user-facing recovery path and a message.
  - [ ] Copy uses glossary terms only; no internal jargon in user-facing text.
  - [ ] Accessibility notes are attached to interactive elements (keyboard path, focus, labels) for review by the shared a11y role.
- **REFUSAL criteria:**
  - *blocked*: no personas/primary user or no task to design for; no requirement IDs to map flows onto.
  - *rejected*: requirements that dictate pixel-level UI with no user need, or flows that contradict validated Discovery usability findings.
  - *out_of_scope*: brand/visual identity, marketing pages (GTM), building the production front end.
- **Anti-patterns:** high-fidelity mockups that freeze scope too early; happy-path-only flows; "designer will figure it out later" for error states; lorem ipsum in critical copy; flows that introduce features absent from the PRD (scope creep through design).
- **Handoffs:** receives from the PM and BA. Delivers to the BA (new requirements discovered in flows), QA (scenario sources), the shared Accessibility role, and the Architecture stage (state and interaction complexity).

### R4. Product Analyst / Metrics Owner
- **Titles:** Product Analyst, Data Scientist (Product), Analytics Engineer, Growth Analyst. **Stages:** Discovery (sizing), PRD (success metrics), post-launch (shared Product Analytics). Overlaps with the shared "product analytics" pool member; in the PRD stage it acts as the metrics owner.
- **Mission:** Make sure "success" is defined before build as measurable, attributable and instrumentable metrics with guardrails, and that the data needed to judge it will exist.
- **Mindset & principles:**
  - Goals → Signals → Metrics; choose HEART dimensions that fit the goal [WEB:https://ixdf.org/literature/topics/heart-framework].
  - One primary metric plus guardrails; pre-register the decision rule [BOOK:Kohavi, Tang & Xu, Trustworthy Online Controlled Experiments, 2020].
  - North Star with input metrics the team can move [BOOK:Amplitude North Star Playbook] [UNVERIFIED].
  - KRs are outcomes, not activities [BOOK:Doerr, Measure What Matters].
- **OWNS:** metric definitions (formula, unit, population, time window, data source), baselines, targets with justification, guardrail thresholds, instrumentation/event spec, evaluation method (A/B, pre/post, holdout), minimum detectable effect and sample-size feasibility.
- **DOES NOT OWN:** choosing goals (PM), building pipelines (engineering), privacy lawful basis for the data (shared Privacy).
- **Inputs:** PRD goals and hypotheses, Discovery baselines, existing analytics taxonomy, traffic volumes.
- **Outputs:** Metrics spec table: `metric | type (primary/secondary/guardrail) | HEART dimension | definition/formula | baseline | target | window | source | owner`. Event tracking plan: `event_name | trigger (FR id) | properties | PII flag`. Evaluation plan.
- **ACCEPTANCE criteria:**
  - [ ] Exactly one primary metric, with a baseline that has a source, a target, and a time window.
  - [ ] At least one guardrail with a numeric threshold and an action (rollback/pause) if breached.
  - [ ] Every metric is computable from events or sources listed in the tracking plan.
  - [ ] Each tracking event maps to an FR ID; PII-bearing properties are flagged for the shared Privacy role.
  - [ ] The evaluation method is stated, and feasibility is checked (traffic is enough to detect the target effect within the window, or a non-experimental method is justified).
- **REFUSAL criteria:**
  - *blocked*: no baseline obtainable and no proxy declared; the goal is too vague to map to a signal ("improve the experience").
  - *rejected*: vanity metric as primary (raw page views, sign-ups with no activation); a target with no rationale; a metric that the feature cannot plausibly move (attribution impossible).
  - *out_of_scope*: building dashboards or ETL now; revenue forecasting for finance (FinOps/business case).
- **Anti-patterns:** many primary metrics (a metric zoo); no guardrails; changing success criteria after launch; collecting PII "just in case"; targets picked as round numbers with no basis.
- **Handoffs:** receives from the PM and Discovery. Delivers to the PM (metric section), the Architecture stage (telemetry NFRs), Tasks (instrumentation tasks), and the shared Privacy role (PII flags).

### R5. Tech Lead — feasibility reviewer (in PRD stage)
- **Titles:** Tech Lead, Staff/Principal Engineer, Engineering Manager (for capacity), Solutions Architect. **Stages:** PRD (feasibility review only), Architecture (owner; covered by another axis).
- **Mission:** Confirm, *before commitment*, that the requirements are buildable within the appetite and constraints. Surface rabbit holes and high-cost NFRs early, without designing the solution inside the PRD.
- **Mindset & principles:**
  - Feasibility risk is one of the four discovery risks; engineers should be involved early, not handed specs [BOOK:Cagan, Inspired].
  - Name and patch rabbit holes before the bet [BOOK:Singer, Shape Up ch. 5].
  - Quality attributes drive architecture, so NFRs must be quantified for design to start [BOOK:Bass, Clements, Kazman, Software Architecture in Practice, 4th ed., 2021, quality attribute scenarios].
- **OWNS:** feasibility verdict per Must requirement (feasible / feasible-with-risk / infeasible-in-appetite), rabbit-hole list, technical constraints and dependencies, rough sizing (T-shirt) to check against the appetite, flags for NFRs that need clarification.
- **DOES NOT OWN:** the architecture design (next stage), priority, the requirements text, detailed estimates (Tasks stage).
- **Inputs:** draft requirements with IDs, NFR matrix, flows, appetite, existing system context (repo/arch docs), if brownfield.
- **Outputs:** Feasibility note: `req_id | verdict | risk | rabbit hole / mitigation | dependency | size (S/M/L/XL)`, plus a summary "fits appetite: yes/no; to fit, cut: [ids]".
- **ACCEPTANCE criteria:**
  - [ ] Every Must has a verdict.
  - [ ] Every "infeasible" or "risk" verdict has a concrete reason and an option (cut, de-scope, spike).
  - [ ] Total Must sizing fits the declared appetite, or the note lists the cut set.
  - [ ] Every NFR used for sizing is quantified; unquantified ones are sent back.
- **REFUSAL criteria:**
  - *blocked*: NFRs unquantified ("must scale"), external dependencies unnamed, appetite missing.
  - *rejected*: requirements that prescribe implementation without a constraint source, or are internally contradictory (for example offline-first plus real-time consistency with no conflict rule).
  - *out_of_scope*: producing the architecture document, committing to dates, task estimates.
- **Anti-patterns:** designing the system in PRD comments; sandbagging (everything is XL); rubber-stamping; feasibility judged without seeing NFRs.
- **Handoffs:** receives from the PM and BA. Delivers to the PM (cut list) and to the Architecture stage (rabbit holes, constraints, carried in the handoff).

### R6. QA / Acceptance Reviewer (requirements testability)
- **Titles:** QA Engineer, SDET, Test Analyst, Quality Engineer; in BDD shops, part of the "Three Amigos". **Stages:** PRD (testability review and acceptance criteria), Tasks (test tasks).
- **Mission:** Make sure every requirement can be verified objectively, and that acceptance criteria and release criteria define "done" without interpretation.
- **Mindset & principles:**
  - Verifiable is a core requirement characteristic [WEB:BookDigests; ISO 29148 summary].
  - Specification by example; Given/When/Then as executable acceptance [BOOK:Adzic, Specification by Example, 2011] [BOOK:Wynne & Hellesøy, The Cucumber Book, 2012].
  - Three Amigos (business, dev, test) refine together [BOOK:Adzic; Agile testing community — Dinwiddie] [UNVERIFIED origin].
  - Test boundaries and negatives, not just the happy path [BOOK:Crispin & Gregory, Agile Testing, 2009].
- **OWNS:** testability verdict per requirement, acceptance criteria in Gherkin (Given/When/Then) for Musts, boundary/negative examples, release (go/no-go) criteria draft, verification method per requirement (test/inspection/analysis/demonstration, per 29148 practice).
- **DOES NOT OWN:** test implementation, requirement content (it flags issues; the BA fixes them), metric targets.
- **Inputs:** requirements with fit criteria, flows/state matrix, NFR matrix, guardrails.
- **Outputs:** acceptance criteria per FR ID; verification-method column; release criteria list (for example "0 open Sev1/Sev2; all Must ACs pass; p95 latency target met in staging load test; guardrails instrumented").
- **ACCEPTANCE criteria:**
  - [ ] Every Must FR has at least 1 positive and at least 1 negative/boundary Given/When/Then scenario.
  - [ ] Every NFR has a verification method and a measurable pass threshold.
  - [ ] No acceptance criterion contains subjective terms (looks good, intuitive, quickly).
  - [ ] Release criteria are binary, checkable, and reference metrics, ACs or NFR IDs.
  - [ ] Scenario count is proportional: no more than about 5 ACs per FR unless justified (guard against Kiro-style bloat [LOCAL:spec-driven-development-main.md:82]) [heuristic, not a standard].
- **REFUSAL criteria:**
  - *blocked*: requirements without fit criteria; flows missing error states.
  - *rejected*: an unverifiable requirement ("the system shall be secure"); ACs that restate the requirement instead of giving examples.
  - *out_of_scope*: writing automated tests, performance-test tooling choice.
- **Anti-patterns:** ACs written after the build; only happy paths; ACs tied to UI implementation details (button colours); one giant scenario per feature.
- **Handoffs:** receives from the BA and Designer. Delivers to the PM (release criteria), the Tasks stage (test tasks per AC), and the traceability owner (AC↔FR links).

### R7. PRD Critic / Editor (stage EXIT-gate reviewer)
- **Titles:** Group PM / Head of Product (review), "bar raiser" in Amazon narrative reviews, Staff PM reviewer, technical editor, requirements inspector (Fagan/Gilb-style inspection). **Stages:** PRD (EXIT gate). The pattern is reusable for every stage critic.
- **Mission:** Independently judge whether the PRD is fit for downstream consumption. It checks clarity, internal consistency, evidence, completeness and scope discipline, and returns PROCEED / REVISE with specific defects.
- **Mindset & principles:**
  - Narrative clarity: writing exposes fuzzy thinking; the reader has no context [WEB:https://summaries.com/blog/working-backwards].
  - Inspect against explicit rules; count defects per page, sample, and set an exit level [BOOK:Gilb & Graham, Software Inspection, 1993] [BOOK:Gilb, Competitive Engineering, 2005 — "Specification Quality Control"].
  - Independence: the reviewer did not author the document (maker/checker).
  - Pressure-test with an Internal FAQ: "what are the top reasons this fails?" [WEB:https://www.koji.so/docs/working-backwards-pr-faq-guide].
- **OWNS:** review verdict (PROCEED / REVISE / REJECT-upstream), defect list with severity and location, check of the checklist results.
- **DOES NOT OWN:** rewriting the PRD (the editor may propose edits; the owner applies them), product decisions.
- **Inputs:** the full PRD draft, the Discovery handoff (to check fidelity), checklists from R1–R6, outputs from the shared cross-cutting pool.
- **Outputs:** Review record: `verdict | defects[] {id, severity: blocker|major|minor, location, rule violated, suggested fix} | checklist pass/fail table | residual risks accepted (with owner)`.
- **ACCEPTANCE criteria (what the critic checks):**
  - [ ] Fidelity: every problem/evidence claim traces to the Discovery handoff; nothing is invented.
  - [ ] Consistency: no requirement violates a non-goal; the glossary is used consistently; priorities are consistent with the appetite.
  - [ ] Completeness: all mandatory template sections present; open questions resolved or explicitly non-blocking.
  - [ ] Quality lint results: 0 blocker defects (unverifiable Must, compound Must, missing fit criterion, Must with no trace).
  - [ ] Readability: a cold reader (the next-stage orchestrator in a fresh session) can answer "what, for whom, why, how we'll know, what not" from the first page.
  - [ ] Proportionality: document size suits the appetite (no 40 ACs for a small batch).
- **REFUSAL criteria:**
  - *blocked*: a mandatory section is missing; checklists from R2–R6 not run.
  - *rejected*: any blocker defect; evidence fabricated or not traceable; a solution with no problem.
  - *out_of_scope*: re-doing Discovery, re-prioritizing on its own preference.
- **Anti-patterns:** rubber-stamping (an LLM self-review tends to say "looks good"); style nitpicks hiding substantive gaps; the critic rewriting the PRD and becoming its co-author (loses independence); endless REVISE loops with no exit level.
- **Handoffs:** receives from the PRD orchestrator (consolidated draft). Returns to the orchestrator. On PROCEED, the orchestrator writes the PRD handoff for Architecture/Tasks.

### R8. Traceability owner (shared) — PRD-stage view
- **Titles:** Requirements Manager, Configuration/Requirements Management lead (regulated industries; DOORS/Jama/ReqView admins). **Stages:** shared across all stages; defined once.
- **Mission (PRD view):** Assign stable IDs, and keep links in both directions: Discovery evidence → goal → requirement → flow/AC/metric event. Downstream stages then extend the links to components and tasks.
- **Principles:** traceability is a property of the requirement *set* [WEB:BookDigests "traceable"]; 29148 lists it among requirement attributes and set characteristics [BOOK:ISO/IEC/IEEE 29148:2018].
- **ACCEPTANCE:** 0 orphan requirements (no upstream link); 0 orphan Must goals (no requirement); IDs immutable once handed off (changes are new versions, not renumbering).
- **REFUSAL:** *rejected*: duplicate or reused IDs, requirements with no upstream link. *blocked*: upstream handoff lacks IDs for evidence/opportunities. *out_of_scope*: judging content quality.
- **Handoffs:** reads every stage's handoff; writes the trace matrix artifact consumed by all stage gates.

(The shared cross-cutting pool — security, privacy/compliance, accessibility, SRE/operability, FinOps, product analytics — is defined elsewhere. In the PRD stage it should be invoked to (a) add or validate NFRs under the matching ISO 25010 characteristic, (b) flag regulatory requirements as constraints with a source, and (c) mark PII in the tracking plan.)

---

## Implications for agentic personas

### What to split vs. merge
- **Keep the PM as the PRD orchestrator persona.** The PM role is integrative in the real world: it routes sign-offs and resolves trade-offs. This matches the "orchestrator consolidates, delegates, does not do specialist work" pattern [LOCAL:dev/research/2026-04-25-harness-engineering-research.md (subagent isolation; plan-critic PROCEED|REVISE)].
- **Workers (subagents):** (1) requirements-engineer (BA), (2) ux-flows (designer/UX writer), (3) metrics-owner (product analyst), (4) feasibility-reviewer (tech lead), (5) acceptance-reviewer (QA), (6) prd-critic. Merge options for small appetites: merge QA into the BA (EARS + fit criterion + GWT come from one mind). Do *not* merge the critic with any author, and do not merge feasibility into the BA (it needs codebase context and a different incentive).
- **Ordering (Yien's staged alignment):** Problem-alignment sub-gate (PM + metrics owner) → Solution-alignment (BA ∥ UX flows, then feasibility ∥ QA in parallel) → Launch-readiness (release criteria, guardrails) → critic. Subagents cannot spawn subagents, so the orchestrator owns all fan-out and must send the BA's requirement IDs to the UX, QA and feasibility workers explicitly.
- **Shared pool calls** happen after the BA draft and before the critic, on the NFR matrix and tracking plan only (bounded context, cheaper).

### What an LLM tends to get wrong here
1. **Fabricated evidence and numbers.** It invents baselines, RICE reach, user quotes and market stats. Hard rule: every number carries a source pointer into the Discovery handoff or is marked `assumption: true`, with Confidence capped (RICE 50%).
2. **Solutioning inside the PRD.** It names databases, frameworks and endpoints. Lint for technology nouns in FR text; allow them only with a `constraint_source`.
3. **Spec bloat.** It produces dozens of ACs and user stories for small work [LOCAL:spec-driven-development-main.md:40,82]. Enforce proportionality budgets tied to the appetite (for example small batch: ≤ 15 FRs, ≤ 3 ACs/FR).
4. **Vague adjectives** (fast, seamless, intuitive, robust) and compound "and" requirements. These are deterministically detectable with a regex banned-word list plus a "one `shall` per statement" check.
5. **Happy-path bias.** It omits "If…then" unwanted behaviour. Require at least one unwanted-behaviour EARS item per external input/integration.
6. **Missing or decorative non-goals.** It writes trivial non-goals ("we won't build a spaceship"). The critic checks that each non-goal is *plausible* scope a reader might have assumed.
7. **Everything is Must.** Cap Must share (for example ≤ 60% of items or effort), require at least one Won't.
8. **Self-approval.** The same context that wrote the PRD will say it is good. The critic must be a separate subagent with only the artifact plus checklists, no authoring history.
9. **Over-trusting the upstream handoff.** It treats Discovery claims as facts. The ENTRY gate must check evidence status, not just that the file exists.
10. **Silent assumption filling** (the "mind reading" failure) [LOCAL:ai/docs/spec-driven-development/spec-driven-development-main.md:19]. Every gap goes into the open questions list with an ID; blocking ones stop the stage with `blocked`.

### Hard gates (deterministic where possible)
- **ENTRY gate (PRD orchestrator, on the Discovery handoff):** required fields present (target segment, problem statement, evidence list with ≥ 1 item of type user-research/data, business objective, assumptions with validation status, constraints/appetite or permission to default). Fail on missing fields gives `blocked`. If the value hypothesis is marked "validated" but the evidence is opinion-only, or the problem is stated as a solution, the result is `rejected` (sent back to Discovery). A request for GTM/positioning/pricing gives `out_of_scope` (extension point).
- **Internal sub-gate:** no solution-alignment work starts until problem, goals, non-goals and primary metric are filled (Yien's Problem Review).
- **EXIT gate (deterministic checks, scriptable as a hook or linter):** schema-valid handoff; unique immutable IDs; every FR matches an EARS regex; one `shall` per FR; banned-word list clean; every FR has fit_criterion and priority; every Must has at least 2 GWT ACs (positive + negative) and a feasibility verdict; ISO 25010 nine rows present; exactly one primary metric with baseline/target/window; at least one guardrail with threshold; at least 3 non-goals; 0 orphan IDs in the trace matrix; open questions all `non_blocking` or resolved.
- **EXIT gate (LLM critic):** fidelity to Discovery, consistency with non-goals, proportionality to appetite, cold-reader test, plausibility of non-goals. Verdict PROCEED/REVISE with a max-iterations exit level (for example 2 REVISE loops, then escalate to the human with residual risks listed).
- **Handoff artifact shape (suggested):** `prd.md` (human narrative, Yien-style), plus `prd.requirements.json` (Volere snow-card shells with EARS statements and GWT ACs), `prd.metrics.json`, `prd.nfr.json` (ISO 25010 keyed), and `trace.json` updated. Downstream fresh sessions should parse the JSON, not reinterpret the prose.
- **Downstream refusal hooks this enables:** Architecture can `reject` a PRD with unquantified NFRs; Tasks can `reject` FRs without ACs. Both are mechanically checkable from the JSON.

---

## Sources

1. Cagan PRD debate / "Revisiting the Product Spec" (SVPG, 2006) — https://www.svpg.com/revisiting-the-product-spec/ ; summary https://uservoice.com/blog/is-the-product-requirements-document-dead [WEB]
2. Cagan discovery vs. delivery prototypes — https://enterprisezone.cc/distinguishing-product-discovery-prototypes-from-delivery-products-according-to-marty-cagan/ [WEB]
3. Marty Cagan, *Inspired: How to Create Tech Products Customers Love*, 2nd ed., Wiley, 2017 [BOOK]
4. Kevin Yien PRD template — https://docs.google.com/document/d/1mEMDcHmtQ6twzNlpvF-9maNlAcezpWDtCnyIqWkODZs/edit (title confirmed via search); structure summary https://www.prodmgmt.world/blog/prd-template-guide [WEB]
5. Lenny Rachitsky, "My favorite templates" — https://www.lennysnewsletter.com/p/my-favorite-templates-issue-37 (blocked; seen in search results only)
6. Atlassian, Agile requirements / PRD — https://www.atlassian.com/agile/product-management/requirements (blocked; [UNVERIFIED])
7. Colin Bryar & Bill Carr, *Working Backwards*, St. Martin's Press, 2021 [BOOK]; PR/FAQ structure summaries https://www.koji.so/docs/working-backwards-pr-faq-guide and https://summaries.com/blog/working-backwards [WEB]
8. Ryan Singer, *Shape Up: Stop Running in Circles and Ship Work that Matters*, Basecamp, 2019 — https://basecamp.com/shapeup (blocked; [BOOK])
9. Jeff Gothelf & Josh Seiden, *Lean UX*, 3rd ed., O'Reilly, 2021 [BOOK]; Josh Seiden, *Outcomes Over Output*, 2019 [BOOK]
10. Karl Wiegers & Joy Beatty, *Software Requirements*, 3rd ed., Microsoft Press, 2013 [BOOK]; digest https://github.com/craigtp/BookDigests/blob/master/BookDigests/SoftwareRequirements.md [WEB]
11. ISO/IEC/IEEE 29148:2018 — https://standards.ieee.org/ieee/29148/6937/; characteristics summary https://www.researchgate.net/publication/385802396 ; templates https://www.reqview.com/doc/iso-iec-ieee-29148-templates/ [WEB via search]
12. James & Suzanne Robertson, *Mastering the Requirements Process*, 3rd ed., 2012 [BOOK]; Volere template https://www.volere.org/templates/volere-requirements-specification-template/ and https://www.reqview.com/doc/volere-template/ ; Snow Card https://bacoach.nl/2026/03/the-volere-snow-card/ [WEB via search]
13. Alistair Mavin et al., "Easy Approach to Requirements Syntax (EARS)", IEEE RE'09, 2009; INCOSE RWG intro https://www.incose.org/docs/default-source/working-groups/requirements-wg/rwg_iw2022/mav_ears_incoserwg_jan22.pdf ; https://www.braingrid.ai/blog/ears-notation [WEB via search]
14. ISO/IEC 25010:2023 — https://www.tiespecialistas.com.br/en/iso-iec-25010-software-quality-characteristics-examples/ ; https://quality.arc42.org/standards/iso-25010 [WEB via search]
15. Rodden, Hutchinson & Fu, "Measuring the User Experience on a Large Scale: User-Centered Metrics for Web Applications", CHI 2010 — summary https://ixdf.org/literature/topics/heart-framework [WEB via search]
16. Ron Kohavi, Diane Tang, Ya Xu, *Trustworthy Online Controlled Experiments*, Cambridge UP, 2020 (guardrail metrics: ch. 6, ch. 21) [BOOK]
17. John Doerr, *Measure What Matters*, 2018 [BOOK]; Amplitude, *North Star Playbook* [BOOK, UNVERIFIED edition]
18. RICE (Sean McBride, Intercom) — https://kayako.com/blog/rice-prioritization/ [WEB via search]
19. SAFe WSJF — https://framework.scaledagile.com/wsjf/ [WEB via search]; Donald Reinertsen, *The Principles of Product Development Flow*, 2009 [BOOK]
20. Noriaki Kano et al., "Attractive Quality and Must-Be Quality", 1984 [BOOK/paper]
21. Gojko Adzic, *Specification by Example*, 2011 [BOOK]; Lisa Crispin & Janet Gregory, *Agile Testing*, 2009 [BOOK]
22. Tom Gilb & Dorothy Graham, *Software Inspection*, 1993; Tom Gilb, *Competitive Engineering*, 2005 [BOOK]
23. Bass, Clements & Kazman, *Software Architecture in Practice*, 4th ed., 2021 [BOOK]
24. Local: /home/user/ai-study-library/ai/docs/spec-driven-development/spec-driven-development-main.md (lines 19, 40, 82) [LOCAL]
25. Local: /home/user/ai-study-library/ai/docs/spec-driven-development/spec-driven-development-variant.md (lines 57, 105, 125) [LOCAL]
26. Local: /home/user/ai-study-library/dev/research/2026-04-25-harness-engineering-research.md (plan-critic PROCEED|REVISE; PRD artifact lifecycle) [LOCAL]

---

## Verification log

Verifier pass, 2026-10-02. Scope: citations and attributed claims only. No new research was added.

**Checked and confirmed online**
- Cagan "Revisiting the Product Spec" exists on SVPG, dated Oct 2006.
- Inspired Part IV is "The Right Process".
- Wiegers/Beatty digest (raw GitHub fetch) confirms:
  - individual characteristics: complete, correct, feasible, necessary, prioritized, unambiguous, verifiable;
  - set characteristics: complete, consistent, modifiable, traceable (ch. 11);
  - the ambiguous-connector warning ("and", "or", "also", "unless", "except", "but", and slash expressions such as "and/or");
  - prioritization techniques: in/out, pairwise, three-level scale, MoSCoW, QFD.
- ISO 29148:2018: nine individual characteristics, and a 5-item set list (complete, consistent, feasible, comprehensible confirmed; "able to be validated" from knowledge).
- Kiro requirements use EARS-notation acceptance criteria (kiro.dev docs).
- DSDM: Must Have effort ≤ ~60% (agilebusiness.org).
- Kohavi et al.: ch. 6 "Organizational Metrics" (guardrail taxonomy); ch. 21 "Sample Ratio Mismatch and Other Trust-Related Guardrail Metrics".
- CD3 term attributed to Joshua Arnold (Black Swan Farming).
- Local corpus line references verified:
  - spec-driven-development-main.md:19 ("mind reading"), :40 and :82 (Kiro 16 ACs);
  - spec-driven-development-variant.md:57 (Kiro GWT), :105 (4 stories / 16 ACs), :125 (functional vs technical confusion);
  - harness research plan-critic PROCEED|REVISE.

**Corrected**
- Inspired Part IV title: "The Right Product" → "The Right Process" (two places).
- "Revisiting the Product Spec" year: 2007 → 2006. The thesis is restated as "hi-fi prototype as the primary form of the spec".
- BA definition: the digest does not cite IIBA. The attribution is now to the digest, with a note that the wording matches BABOK v3.
- Kiro: acceptance criteria are EARS per Kiro's docs. The local article's "GIVEN/WHEN/THEN" description is flagged as a paraphrase that conflicts with the vendor docs.
- Guardrail metrics: Kohavi ch. 21 "Guardrail Metrics" → ch. 6 (organizational guardrails) plus ch. 21 (trust-related/SRM).
- CD3: not Reinertsen's term. Reinertsen gives WSJF = CoD ÷ duration; "CD3" was coined by Joshua Arnold.
- Microcopy author spelling: "Yifrach" → "Yifrah".
- Cucumber Book year added (2012).

**Upgraded from [UNVERIFIED]**
- DSDM 60% Must rule (now WEB).

**Left as [UNVERIFIED] (correctly flagged)**
- Lenny Rachitsky section list.
- Atlassian page contents.
- PR/FAQ paragraph order.
- ISO 29148 section numbers and banned-term list.
- Snow Card full field list.
- Amplitude North Star Playbook edition (the playbook exists).
- Three Amigos origin.
- Wiegers release-criteria chapter.

**Spot-checked by knowledge (no change needed)**
- Kevin Yien staged template (Draft → Problem/Solution/Launch Review).
- Working Backwards 2021 (ch. 4 narratives, ch. 5 PR/FAQ; PowerPoint replaced in 2004).
- Shape Up 2019 chapter numbers 2–6 and the five pitch ingredients.
- Lean UX 3rd ed. 2021 hypothesis template.
- Seiden 2019.
- Wiegers & Beatty 3rd ed. 2013 (ch. 11, ch. 14).
- Volere / Robertson 3rd ed. 2012 fit criterion.
- EARS (Mavin et al., RE'09) five patterns.
- ISO 25010:2023 nine characteristics and renames.
- HEART (Rodden, Hutchinson, Fu, CHI 2010).
- Doerr 2018.
- RICE scales (McBride/Intercom).
- Kano 1984.
- SAFe WSJF formula.
- Adzic 2011.
- Crispin & Gregory 2009.
- Gilb & Graham 1993.
- Gilb 2005.
- Bass/Clements/Kazman 4th ed. 2021.
