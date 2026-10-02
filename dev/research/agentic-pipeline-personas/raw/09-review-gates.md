# Raw research — Review, challenge & quality gates

> Scope: the roles and mechanisms that **challenge** work and **decide whether it may cross a stage boundary**. In this pipeline each stage (discovery → prd → architecture → tasks) runs its own orchestrator as the main thread in a **fresh session** (`claude --agent <stage>-orchestrator`), at a different time and in a different window. A gate therefore cannot depend on anything that happened in an earlier conversation. It has to be **reproducible from files on disk**: the upstream handoff, the stage artifact, the gate rubric, and the gate verdict file. Every role below is a worker subagent that a stage orchestrator invokes, or a decision rule the orchestrator applies itself. The traceability owner and the cross-cutting pool are defined elsewhere. Here they appear only as producers of gate findings.
>
> Tagging: `[WEB:url]` means the claim was confirmed online in this session. Many primary sites (hbr.org, amazon.jobs, scrumguides.org, gov.uk assets, hamel.dev, industrialempathy.com) were **blocked by the egress proxy**, so confirmation came from search-result pages and secondary sources listed in Sources. `[BOOK:...]` covers well-known books cited from knowledge. `[UNVERIFIED]` means the claim is plausible but was not checked. `[LOCAL:path]` refers to this repo's corpus.

---

## Literature & frameworks

### 1. Gary Klein — the pre-mortem (HBR, Sept 2007; *Sources of Power* 1998)
- Procedure: the team gets the plan, is told to **imagine the project has already failed**, writes down independently every reason it can think of for the failure, then shares the reasons round-robin (one per person per round). The leader consolidates the list and the plan is revised [BOOK:Klein, "Performing a Project Premortem", HBR 2007] (hbr.org was blocked; the steps are consistent across secondary sources [WEB:https://get-alfred.ai/blog/pre-mortem-technique]).
- Evidence base: Mitchell, Russo & Pennington (1989) found that **prospective hindsight**, meaning imagining the event has already happened rather than that it might happen, increased the **number of reasons** people generated for an outcome by about 30%. (Klein's HBR text phrases this as the ability to "correctly identify reasons"; the 1989 study did not assess correctness [WEB:https://corporate.jasoncollins.blog/premortem (via search snippet)].) This is the only citation in Klein's 2007 article [WEB:https://corporate.jasoncollins.blog/premortem (via search snippet)] [WEB:https://get-alfred.ai/blog/pre-mortem-technique]. Note that the 30% is about **reasons generated**, not about project success rates. A persona must not claim that pre-mortems "reduce failure by 30%".
- Mindset: it gives doubters **permission to dissent** in a team that has already committed, and it turns criticism into a creative exercise instead of a personal attack [BOOK:Kahneman, *Thinking, Fast and Slow*, 2011, ch.24, citing Klein].
- Artifact: a ranked list of failure stories → for each one, likelihood × impact, an early-warning signal, and a mitigation or plan change. Persona implication: each failure reason must map to (a) a plan change, (b) a monitored risk with a tripwire, or (c) an explicit acceptance. An unmapped reason counts as an open finding.
- Independence matters: reasons are written **before** discussion so the group does not anchor. In an LLM pipeline this means generating failure modes in a context that has **not** seen the authors' rationale, or seeding it with "the project failed 12 months after launch" framing only.

### 2. Red teaming — Micah Zenko, *Red Team: How to Succeed by Thinking Like the Enemy* (2015); UK MoD/DCDC *Red Teaming Handbook* 3rd ed. (June 2021)
- UK definition: a red team is a team formed "with the objective of subjecting an organisation's plans, programmes, ideas and assumptions to rigorous analysis and challenge" [WEB:https://www.scribd.com/document/896798182/20210625-Red-Teaming-Handbook-1 (via search snippet)].
- The 3rd edition moves from *red teams* to a **red team mindset**, "a philosophy or state of mind where problem solvers and decision-makers apply red teaming techniques … routinely". Red teaming is framed as a counter to "human frailties", meant to correct thinking "before faulty judgements are cemented in the minds of key decision-makers" [WEB:https://www.civilserviceworld.com/news/article/mod-updates-guidance-on-red-teaming-for-problemsolvers (via search snippet)]. Persona implication: **every** stage critic carries the red-team mindset. A separate adversarial persona is still worth having for high-stakes artifacts.
- Handbook technique families (from knowledge of the 2nd/3rd editions): key assumptions check, quality of information check, devil's advocacy, Team A/Team B, high-impact/low-probability analysis, "what if" analysis, alternative futures/scenarios, outside-in thinking, stakeholder/actor mapping, and the pre-mortem [BOOK:UK MoD DCDC, *Red Teaming Handbook* 3rd ed., 2021, Part 2 techniques] [UNVERIFIED exact list; the gov.uk PDF was blocked].
- Zenko's best practices (paraphrased): (1) the boss must buy in, because a red team the decision-maker ignores is pointless; (2) be outside and objective while inside and aware; (3) staff it with fearless skeptics who have finesse; (4) carry a big bag of tricks, since rotating techniques prevents predictability; (5) be willing to hear bad news and act on it; (6) red team just enough, but no more [BOOK:Zenko, *Red Team*, 2015, ch.1 "best practices"].
- Point 6 maps directly onto **iteration caps**. Zenko warns that over-used red teams become routine and lose their edge, and that red teaming has a cost [BOOK:Zenko 2015, ch.1].
- Independence/positioning: the red team must not be subordinate to the plan's owner. Its output goes to the **decision-maker**, not only to the author [BOOK:Zenko 2015; DCDC Handbook]. In the pipeline the critic's verdict file is read by the orchestrator (the decision-maker), and the author worker never decides on it.

### 3. Devil's advocate and "Have Backbone; Disagree and Commit" (Amazon Leadership Principle)
- Official text: leaders "are obligated to respectfully challenge decisions when they disagree, even when doing so is uncomfortable or exhausting… They do not compromise for the sake of social cohesion. Once a decision is determined, they commit wholly." [WEB:https://quarterdeck.co.uk/articles/leadership-principles-amazon/ (via search snippet); amazon.jobs blocked].
- "Insist on the Highest Standards" (standards that others may find "unreasonably high") and "Are Right, A Lot" (seek diverse perspectives and work to disconfirm their beliefs) round out the reviewer mindset [BOOK:Amazon Leadership Principles, 2021 revision] [UNVERIFIED exact wording].
- Persona implication: a critic must (a) dissent **with data/evidence**, not with taste, (b) record the dissent in writing, and (c) once the orchestrator or human decides, stop re-litigating. A recorded override is the "commit". This is the main defense against infinite critic loops: the critic does not get to raise the same finding again after a recorded decision.
- Devil's advocacy as a formal technique (assigned role, argue the opposite case) is weaker than authentic dissent. Research by Nemeth and others suggests that role-played dissent is discounted by groups [BOOK:Nemeth, *In Defense of Troublemakers*, 2018] [UNVERIFIED specifics]. Persona implication: an LLM "devil's advocate" told only to "argue against" produces strawmen. Ground it in a **specific counter-hypothesis plus evidence that would distinguish the two**.

### 4. Edward de Bono — *Six Thinking Hats* (1985)
- Hats: White (facts and information gaps), Red (feelings and intuition, no justification needed), Black (caution, risks, why it may fail), Yellow (benefits, why it may work), Green (alternatives, creativity), Blue (process control, the facilitator) [BOOK:de Bono, *Six Thinking Hats*, 1985].
- Core idea is **parallel thinking**: everyone wears the same hat at the same time, which separates critique from generation and from facts [BOOK:de Bono 1985].
- Persona implications: (a) the stage **critic is the Black hat** and should not drift into Green (redesigning the artifact). It says what is wrong and why, and only *suggests* a fix direction. (b) The orchestrator is the **Blue hat**. (c) A White-hat pass, "what do we actually know vs. assume?", is a cheap, high-value gate check that LLMs skip. (d) Yellow-hat review protects against pure negativity: a critic that never lists the strengths it relies on makes fixes that destroy the good parts.

### 5. Design reviews, architecture review boards, RFC culture
- **Google design docs**: an informal document written before coding. Typical sections: context and scope, goals and **non-goals**, the actual design (system context diagram, APIs, data storage), **alternatives considered**, cross-cutting concerns (security, privacy, observability). Review ranges from a lightweight circulation to a formal design review meeting. Don't write one when the solution is obvious and there are no real trade-offs [BOOK:Malte Ubl, "Design Docs at Google", industrialempathy.com, 2020] (site blocked; Orosz confirms Uber used "a similar approach" [WEB:https://x.com/GergelyOrosz/status/1286013033618255878]).
- **Uber RFCs → ERDs**: began at a ~2-year-old startup as a decision to "document & vet *every* new service's architecture with a peer-review process before writing the code". It moved from emailing all engineers, to per-domain mailing lists and templates, to tooling for search and approval, and scaled from tens to a couple of thousand engineers [WEB:https://x.com/GergelyOrosz/status/1260994818899140609] [WEB:https://blog.pragmaticengineer.com/scaling-engineering-teams-via-writing-things-down-rfcs/ (via search snippet)].
- **Rust RFC process**: required for "substantial" changes. The flow is PR with template → consensus building → a sub-team member moves a **Final Comment Period (FCP)** with a disposition of **merge / close / postpone**. FCP lasts 10 calendar days (≥5 business days). Substantial *new* arguments during FCP can cancel it, and acceptance requires all sub-team members to sign off before FCP [WEB:https://github.com/rust-lang/rfcs/blob/master/README.md].
- Persona implications: (a) **disposition vocabulary is fixed and small** (merge/close/postpone ≈ pass/reject/hold). (b) A **"final comment" window** gives a natural termination rule: after FCP, only *new* arguments reopen the discussion. (c) "Alternatives considered" and "non-goals" are the two sections whose absence most reliably signals an unreviewed design. (d) RFC culture pairs reviews with a **threshold for when review is required**. Not every change needs an ARB.
- ARB (architecture review board): a cross-functional group with authority to approve, conditionally approve, or reject designs against enterprise principles and standards. Typical outputs are a decision record with conditions [BOOK:TOGAF 9.2, Part VI ch.47 "Architecture Board" (architecture compliance reviews)] [UNVERIFIED chapter number]. Known failure mode: ARBs become a bottleneck or rubber stamp, and decentralised "advice process" models (Harmel-Law) replace the board with mandatory consultation plus ADRs [BOOK:Andrew Harmel-Law, *Facilitating Software Architecture*, 2024] [UNVERIFIED].

### 6. Amazon Bar Raiser
- A bar raiser is a trained interviewer from **outside the hiring team**, not in the hiring manager's chain of command. Entry to the program is by invitation from other bar raisers [WEB:https://www.carrus.io/blog/all-about-bar-raisers-amazons-essential-element-to-the-hiring-process (via search snippet)].
- The bar raiser can **veto** the hiring manager's decision: they can block a candidate everyone else approves. Secondary sources report the veto is a rarely used "nuclear option". The stated bar is that a hire should be better than 50% of current employees in similar roles [WEB:https://4dayweek.io/interview-process/amazon-bar-raiser (via search snippet)] [UNVERIFIED that the veto is "never" overridden; secondary sources differ].
- Persona implications: (a) **structural independence**: the gatekeeper must not be the author or the orchestrator's "helper", and must have no incentive to ship (in an LLM, a separate context with no generator rationale, ideally a different model/prompt family [LOCAL:dev/research/2026-04-25-harness-engineering-research.md §11 "Cross-Model Review"]). (b) The **bar is relative and explicit**: "raises the average" maps to "meets the rubric's must-pass items AND is no worse than the reference exemplar". (c) The veto exists only for bar violations, not for preferences.
- The bar raiser also runs the debrief: they make interviewers commit their written assessment **before** the group discussion, to avoid anchoring [BOOK:Bryar & Carr, *Working Backwards*, 2021, ch.2] [UNVERIFIED detail]. Same logic as the pre-mortem's independent writing step.

### 7. Robert G. Cooper — Stage-Gate (*Winning at New Products*, 1986 → 5th ed. 2017)
- A gate is a formal decision point where a cross-functional group of **gatekeepers** with resource authority decides a project's future [WEB:https://portfoliohub.io/blog/stage-gate-review-template (via search snippet)].
- Gate anatomy: **deliverables** (inputs defined at the *previous* gate from a standard menu), **criteria**, and **outputs**: a decision (**Go / Kill / Hold / Recycle**), an approved action plan for the next stage, and the deliverables list and date for the next gate [WEB:https://www.wellspring.com/blog/how-to-manage-your-innovation-process-the-stage-gate-framework (via search snippet)].
- Criteria come in two kinds. **Must-meet**: yes/no knock-out questions, where a single consensus "No" means Kill. **Should-meet**: desirable characteristics, scored on a scorecard to separate excellent from minimally acceptable projects [WEB:https://www.wellspring.com/blog/... (via search snippet)]. **This is the cleanest real-world precedent for blocking vs. advisory criteria.**
- "Hold" means the project passes on merit but is deprioritised. "Recycle" means it goes back to the previous stage for rework [BOOK:Cooper, *Winning at New Products*, 4th ed. 2011, ch.4 & ch.9].
- Failure modes Cooper names: gates "with no teeth" where nothing is ever killed, gatekeepers who don't show up or don't read the deliverables, moving goalposts, and "hollow" gates where the decision was made outside the meeting [BOOK:Cooper 2011, ch.9 "Effective gates"] [UNVERIFIED exact list].
- Persona implications: (a) the **next gate's deliverables are declared at the current gate**, so the handoff file should carry an `expected_at_next_gate` list. (b) Must-meet = BLOCKER, should-meet = scored MAJOR/MINOR. (c) The gate decides **go/kill/hold/recycle**, not "approve with 47 comments".

### 8. Definition of Done as a gate (Scrum Guide 2020)
- The DoD is the formal description of the state of the Increment when it meets the quality measures required. "If a Product Backlog item does not meet the Definition of Done, it cannot be released or even presented at the Sprint Review. Instead, it returns to the Product Backlog for future consideration." [WEB:https://www.scrum.org/forum/scrum-forum/46113/if-product-backlog-item-does-not-meet-definition-done-it-cannot-be-released (quotes the 2020 Guide)].
- Implications: (a) the DoD is **binary**, with no "mostly done". (b) It is **organisation-wide or team-wide and known in advance**, not invented at review time. (c) Failing work is **returned upstream**, not patched by the reviewer. Each pipeline stage needs a published `DoD-<stage>.md` that the EXIT gate checks, and the ENTRY gate of the next stage re-checks the minimum subset (a "Definition of Ready" from the consumer's side).
- DoD vs. acceptance criteria: the DoD applies to every item; acceptance criteria are per item. The gate rubric should keep both layers: a stage-wide DoD (fixed) plus artifact-specific criteria (from the upstream handoff).

### 9. Peer review effectiveness research
- Fagan (1976, IBM) formal inspections: entry criteria, planning, overview, individual preparation, inspection meeting with a moderator and reader, rework, follow-up, and **exit criteria**. Defects are logged by type and severity, and the moderator verifies rework [BOOK:Fagan, "Design and code inspections to reduce errors in program development", IBM Systems Journal 15(3), 1976]. This is the origin of entry and exit gates as a review concept (explicit entry criteria were formalised mainly in Fagan's follow-up, "Advances in Software Inspections", IEEE TSE 1986 [BOOK]).
- Bacchelli & Bird (ICSE 2013, Microsoft): finding defects is the main stated motivation, but review outcomes are "less about defects than expected". The real yield is knowledge transfer, team awareness, and alternative solutions. **Understanding the change is the key challenge** [WEB:https://www.microsoft.com/en-us/research/publication/expectations-outcomes-and-challenges-of-modern-code-review/ (via search snippet)]. Persona implication: a reviewer that cannot reconstruct the *intent* (upstream handoff) produces shallow, style-level comments. Feed it the "why" (upstream goals) alongside the "what".
- SmartBear/Cisco study: review effectiveness drops sharply beyond ~200–400 LOC per session and above ~500 LOC/hour inspection rate [BOOK:Jason Cohen, *Best Kept Secrets of Peer Code Review*, SmartBear, 2006] [UNVERIFIED exact numbers]. Persona implication: **bound the review unit**. Gate a PRD section by section, or a task list per epic, rather than one 30-page blob, and use checklists.
- Structured reading techniques can beat ad-hoc reading, but the evidence for plain checklists is mixed: Porter, Votta & Basili (IEEE TSE 1995) found scenario-based reading outperformed both ad-hoc and checklist reading, with checklists no better than ad hoc; Basili et al. (1996) report gains for perspective-based reading [BOOK; UNVERIFIED specifics]. (Corrected: the earlier claim that checklist reading "consistently beats" ad hoc is not supported.) Persona implication unchanged: give the reviewer a role-specific scenario/rubric, not just a generic checklist.

### 10. Cognitive biases in product/architecture decisions — Kahneman; Duke
- **WYSIATI** ("What You See Is All There Is"): System 1 builds the most coherent story from the available information and ignores what is missing. Confidence depends on coherence, not completeness [BOOK:Kahneman, *Thinking, Fast and Slow*, 2011, ch.7]. LLM analogue: an artifact that is internally consistent *looks* complete. The critic must explicitly enumerate **what is absent** (missing personas, non-goals, failure paths, NFRs).
- **Planning fallacy / inside view**: plans and forecasts that are unrealistically close to best-case scenarios. The remedy is the **outside view / reference-class forecasting** (Flyvbjerg) [BOOK:Kahneman 2011, ch.23 "The Outside View"]. Gate check: any estimate or timeline must cite a reference class or base rate, or be tagged as an inside-view guess.
- **Confirmation bias**: seeking evidence for the favored hypothesis. Discovery is especially exposed, because interview evidence gets read as validation [BOOK:Kahneman 2011, ch.7]. Gate check: "what evidence would falsify this problem statement, and did we look for it?"
- Kahneman, Lovallo & Sibony's **12-question decision-quality checklist** includes: is there self-interest in the recommendation? has the team fallen in love with it? were dissenting opinions explored? could the diagnosis be overly influenced by salient analogies? were credible alternatives considered? is the base case overly optimistic? is the worst case bad enough? [BOOK:Kahneman, Lovallo, Sibony, "Before You Make That Big Decision", HBR June 2011] [UNVERIFIED exact wording]. This is directly reusable as a critic checklist for "recommendation" artifacts (discovery opportunity choice, architecture option choice).
- Annie Duke, *Thinking in Bets* (2018): **"resulting"** means judging decision quality by outcome. Decision quality = quality of information + reasoning + calibration, expressed in probabilities rather than certainties [BOOK:Duke, *Thinking in Bets*, 2018, ch.1–2]. *How to Decide* (2020) covers pre-commitment and pre-mortems [BOOK:Duke, *How to Decide*, 2020; UNVERIFIED which tools are in which book]; **kill criteria** ("states and dates") decided in advance are the core of *Quit* (2022) [BOOK:Duke, *Quit*, 2022].
- Persona implications: gates evaluate the **decision process and evidence quality**, not whether the idea "sounds good". Confidence claims must be calibrated (e.g., High/Med/Low with stated evidence). Kill criteria should be written at Discovery and re-checked at every downstream gate.

### 11. Evaluator-optimizer and LLM-as-judge
- Anthropic, *Building effective agents* (Dec 2024): **evaluator-optimizer** is a workflow in which one LLM generates and another evaluates and gives feedback in a loop. It fits when there are "clear evaluation criteria, and when iterative refinement provides measurable value". Two signs of fit: responses "can be demonstrably improved when a human articulates their feedback", and "the LLM can provide such feedback" [WEB:https://www.anthropic.com/engineering/building-effective-agents].
- Anthropic, *Harness design for long-running apps*: "separating the agent doing the work from the agent judging it proves to be a strong lever". Self-evaluating agents tend to respond "by confidently praising the work—even when, to a human observer, the quality is obviously mediocre". It is more tractable to tune "a standalone evaluator to be skeptical". Concrete criteria beat vague ones: "does this follow our principles for good design?" rather than "Is this design beautiful?". For full-stack work "each criterion had a hard threshold, and if any one fell below it, the sprint failed". Generator and evaluator negotiated a **sprint contract** on what "done" looks like **before** work began. Frontend runs used 5–15 iterations per generation [WEB:https://www.anthropic.com/engineering/harness-design-long-running-apps].
- Huang et al., "Large Language Models Cannot Self-Correct Reasoning Yet" (ICLR 2024): without external feedback, LLMs struggle to self-correct reasoning, and performance sometimes **degrades** after self-correction. Earlier gains came from oracle labels [WEB:https://arxiv.org/pdf/2310.01798 (via search snippet)]. Implication: a critic loop is only as good as the **external signal** (checklist, deterministic check, upstream criteria, tests). "Reflect and improve" with no rubric is not a gate.
- Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (NeurIPS 2023): documented **position bias**, **verbosity bias** (longer answers judged more credible), **self-enhancement bias** (preferring own outputs), and limited reasoning on math/logic grading [WEB:https://arxiv.org/abs/2306.05685 (via search snippet)]. Implications: judge in a **separate context**, prefer a **different model** for the critic, never reward length, and require evidence citations (line or section references) for each finding.
- Husain & Shankar (evals practice): prefer **binary pass/fail per criterion plus a written critique** over 1–5 Likert scales. Adjacent points are inconsistent, middle values hide indecision, and expert pass/fail correlates better with real quality. "Critique shadowing": domain-expert critiques become few-shot examples for the judge [WEB:https://hamel.dev/blog/posts/evals-faq/evals-faq.pdf (via search snippet)] [WEB:https://github.com/hamelsmu/evals-skills/blob/main/questions.md (via search snippet)].
- Local corpus: the `plan-critic` pattern emits `PROCEED | REVISE` with critical gaps, blind spots, and weak assumptions, plus a **Skepticism Safeguard** ("never auto-agree… its role is to be the friction"). It is used when downstream cost is >100× the artifact cost. The loop-continuation pattern carries `iteration` / `max_iterations` in a state file [LOCAL:dev/research/2026-04-25-harness-engineering-research.md §11, lines ~97–106, 709–725]. Deterministic rails: "The agent is physically blocked from marking a task as complete until it passes these tests" and HITL as "final veto" [LOCAL:ai/docs/harness-engineering/harnessengineering-building-the-operating-system-for-autonomous-agents.md].

### 12. Avoiding infinite critic loops (synthesis)
- Sources of non-termination: (a) critic and author optimise different, unstated targets; (b) the critic finds *new* nits every round, since LLM critics are non-deterministic and never "run out" of comments; (c) fixes for one finding break another; (d) the critic re-raises findings that a decision already overrode.
- Mechanisms drawn from the literature above:
  1. **Contract first** (sprint contract; Cooper's deliverables declared at the prior gate; DoD known in advance). The critic may only fail the artifact against criteria in the rubric file. A new criterion is a rubric change and goes to the human, not into this loop.
  2. **Severity-gated termination**: the loop continues only while open BLOCKER or MAJOR findings exist. MINOR findings never cause another iteration; they are logged as advisory.
  3. **Monotonic finding set** (RFC FCP logic): after round 1, the critic may raise a new BLOCKER only if it is caused by a change made in the revision, or if it cites new evidence. Otherwise it may only *close or keep* existing findings. Persist findings with stable IDs in `gate/<stage>-findings.json`.
  4. **Iteration cap**: e.g., max 3 critic rounds per gate (Zenko: "just enough, but no more"). Anthropic's 5–15 applies to aesthetic generation, which is a different regime. On reaching the cap with BLOCKERs open → `HOLD` + **escalate to human** with a decision memo. The pipeline does not silently pass.
  5. **Disagree-and-commit record**: the human or orchestrator can override a finding with a written rationale (`status: overridden`, `by`, `reason`). The critic must not re-raise an overridden finding.
  6. **No-progress detector**: if the set of open BLOCKER/MAJOR IDs is unchanged between two rounds → escalate immediately, without waiting for the cap.

### 13. What makes a gate BLOCKING vs ADVISORY (synthesis)
A criterion is **blocking** when *all* of these hold:
- (a) it is in the published rubric/DoD *before* the work started (contract);
- (b) it is **binary and testable**, either by a deterministic check (file exists, every FR has an ID, every task traces to an FR) or by a judge with a concrete pass definition and an evidence requirement;
- (c) failing it makes the **next stage unable to proceed or likely to build the wrong thing** (Cooper's must-meet; DoD "cannot be presented");
- (d) the gate owner has the authority to stop (bar-raiser veto; gatekeepers with kill authority).

Everything else is **advisory**: scored, logged, carried forward in the handoff as known issues. Deterministic checks should run first and be truly blocking (scripts or hooks, not prompts). LLM-judge blockers should be few (≤ ~8 per stage), each with a pass definition and an example.

---

## Real-world roles

### R1. Stage Critic / Red Team Reviewer
- **Real-world titles**: Red Team Lead (defence/intelligence, UK DCDC), Devil's Advocate / "Murder board" member, Principal Engineer reviewer, "Black Hat" facilitator, Product Council challenger. **Stages**: all (one instance per stage, with stage-specific rubric); shared persona definition.
- **Mission**: subject the stage artifact to rigorous, evidence-based challenge of its assumptions, logic, completeness, and failure modes, and return a severity-classified findings list to the decision-maker (the orchestrator) before the exit gate.
- **Mindset & principles**:
  - Red-team mindset: challenge plans and assumptions to counter human frailties before judgments are cemented [WEB:civilserviceworld.com].
  - Outside-and-objective but inside-and-aware; fearless skeptic with finesse; red team "just enough" [BOOK:Zenko 2015].
  - Disagree with data; record dissent; commit after decision [WEB:quarterdeck.co.uk Amazon LP].
  - Black-hat discipline: critique, don't redesign [BOOK:de Bono 1985].
  - Hunt for what's missing (WYSIATI) [BOOK:Kahneman 2011 ch.7].
  - Skepticism safeguard: never auto-agree [LOCAL:harness research §11].
- **Accountabilities**:
  - OWNS: findings (ID, severity, evidence location, violated criterion, failure scenario, suggested fix direction); key-assumptions check; alternatives/counter-hypothesis check; a gate-recommendation of PASS / REVISE / ESCALATE.
  - DOES NOT OWN: rewriting the artifact; the final gate decision (orchestrator/bar raiser); adding criteria not in the rubric (it may *propose* rubric changes separately); cross-cutting specialist depth (security, privacy, etc.; it invokes or defers to the pool).
- **Inputs needed**: stage artifact(s); upstream handoff (goals, constraints, acceptance criteria); stage rubric + DoD; prior findings file (for rounds ≥2); decision/override log.
- **Outputs/artifacts**: `gate/<stage>-critique-r<N>.md` + machine-readable `gate/<stage>-findings.json`. Industry formats: Fagan defect log (type/severity/location), RFC review comments with disposition, red-team "key judgments challenged" memo, Kahneman-Lovallo-Sibony checklist answers.
- **ACCEPTANCE criteria (for the critique itself)**:
  - [ ] Every finding cites a **specific location** (file + section/heading/ID) and quotes or paraphrases the offending content.
  - [ ] Every finding names the **rubric criterion** it violates (no criterion → it is labelled `observation`, not a finding).
  - [ ] Every BLOCKER/MAJOR includes a concrete **failure scenario** ("if downstream builds X as written, Y happens").
  - [ ] Key assumptions are listed (≥3 for discovery/PRD/architecture) with status supported / unsupported / contradicted, and evidence.
  - [ ] At least one **alternative/counter-hypothesis** was considered for the central claim or decision.
  - [ ] An explicit "what's missing" section exists (possibly empty, with justification).
  - [ ] Strengths relied upon are listed briefly (yellow-hat guard against destructive fixes).
  - [ ] Severity counts and the recommendation are consistent (any open BLOCKER → not PASS).
  - [ ] Round ≥2: every previous finding has a status (closed / still-open / overridden); new BLOCKERs are justified as revision-induced or new-evidence.
- **REFUSAL criteria**:
  - *blocked*: no rubric/DoD file for the stage; no upstream handoff to judge against (cannot tell "wrong" from "different"); artifact incomplete or truncated (e.g., sections marked TODO in >X% of the required headings).
  - *rejected*: (as gate input) the artifact fails deterministic pre-checks (schema, required sections, IDs). The critic refuses to do expensive judgment on structurally invalid input and returns it to the author.
  - *out_of_scope*: requests to rewrite or "fix it yourself"; requests to approve on schedule pressure; domain-specialist verdicts (e.g., "is this GDPR compliant?" → privacy reviewer); GTM/positioning critique.
  - The critic also refuses to **soften severity** because of the iteration count or a request from the author.
- **Anti-patterns**: nitpick flood (dozens of MINORs hide the one BLOCKER); taste-based findings without a criterion; strawman devil's advocacy; redesigning instead of critiquing; sycophantic PASS (self-enhancement bias when the same model wrote it); verbosity reward; moving goalposts each round; reviewing too large a unit at once.
- **Handoffs**: receives from the stage orchestrator (artifact + rubric) → delivers findings to the orchestrator; BLOCKERs routed to the author worker for revision; unresolved items → bar raiser / human escalation; trace-related findings → traceability auditor.

### R2. Pre-mortem Facilitator
- **Real-world titles**: Pre-mortem facilitator (often a PM, agile coach, or risk manager), Risk Workshop Facilitator, Red Team facilitator; in decision-science teams a "Decision Coach". **Stages**: discovery (opportunity/bet), architecture (chosen option), tasks (delivery plan); optional for PRD.
- **Mission**: generate, independently of the plan's authors, the most plausible reasons the plan has already failed, and convert them into plan changes, tripwires, or explicit accepted risks.
- **Mindset & principles**:
  - Prospective hindsight: assume failure has occurred, explain why (~30% more reasons generated) [WEB:get-alfred.ai citing Mitchell et al. 1989].
  - Independent generation before discussion, to avoid anchoring [BOOK:Klein 2007].
  - Legitimise dissent in a committed team [BOOK:Kahneman 2011 ch.24].
  - Outside view: compare to reference class failures [BOOK:Kahneman 2011 ch.23].
  - Pre-commit kill criteria/tripwires [BOOK:Duke, *How to Decide* 2020; *Quit* 2022].
- **Accountabilities**:
  - OWNS: failure-story list; categorisation (market/user, technical, organisational, delivery, compliance, economics); likelihood × impact; early-warning signal per top risk; proposed mitigation or kill criterion.
  - DOES NOT OWN: deciding which mitigations are adopted (orchestrator/author); the risk register lifecycle after the stage (SRE/PM); estimating probabilities with false precision.
- **Inputs needed**: plan/decision artifact summary (*not* the full rationale, to reduce anchoring); success criteria/metrics; constraints; reference class info if available.
- **Outputs/artifacts**: `gate/<stage>-premortem.md`: failure narratives (headline written in past tense, e.g., "Launched; 6 months later adoption was 3% because…"), risk table `{id, cause, category, likelihood H/M/L, impact H/M/L, leading indicator, mitigation | tripwire | accept}`, plus top-5 recommended changes.
- **ACCEPTANCE criteria**:
  - [ ] ≥8 distinct failure reasons spanning ≥4 categories (not variations of one).
  - [ ] Written in past tense from a stated failure date.
  - [ ] Each top-5 risk has a **leading indicator** observable *before* failure and a disposition (change / tripwire / accept).
  - [ ] At least one "silent success-failure" (shipped on time but no one used it / wrong problem).
  - [ ] At least one risk derived from an outside-view/base rate rather than artifact text.
  - [ ] No risk duplicates an already-mitigated item without explaining why the mitigation is insufficient.
- **REFUSAL criteria**:
  - *blocked*: no explicit success criteria (cannot define "failure"); no plan or decision to fail (pure idea with no chosen direction).
  - *rejected*: the plan has no stated assumptions or constraints, so it is too vague to fail concretely → back to the author.
  - *out_of_scope*: producing a full risk management plan or quantitative Monte Carlo; making the go/kill decision; writing mitigations as implementation tasks (tasks stage owns that).
- **Anti-patterns**: generic risks ("scope creep", "lack of resources") with no mechanism; anchoring on the author's own risk section; turning the session into a blame exercise; numeric probabilities without basis; listing risks with no leading indicators so nothing changes.
- **Handoffs**: receives a plan summary from the orchestrator → delivers the pre-mortem to the orchestrator and stage critic; accepted risks + tripwires go into the handoff file for downstream stages (and SRE/FinOps pool where relevant); kill criteria are re-checked by later ENTRY gates.

### R3. Bar Raiser / Quality Gatekeeper (gate decision-maker)
- **Real-world titles**: Amazon Bar Raiser; Stage-Gate gatekeeper / Product Approval Committee member; QA Lead signing release readiness; Release Manager (go/no-go); Fagan inspection Moderator. **Stages**: every EXIT gate (and ENTRY verification). In this pipeline the orchestrator *applies* the decision rule, but a dedicated gatekeeper subagent issues an independent recommendation from fresh context.
- **Mission**: decide, against a pre-published bar, whether the stage's output may cross into the next stage: GO / RECYCLE / HOLD / KILL. Be immune to schedule and sunk-cost pressure.
- **Mindset & principles**:
  - Independence from the hiring/authoring chain; veto for bar violations [WEB:carrus.io; 4dayweek.io].
  - Raise the bar: output must beat the reference exemplar/average [WEB:4dayweek.io].
  - Must-meet knock-outs vs should-meet scorecards; gates with real kill authority [WEB:wellspring.com; portfoliohub.io].
  - DoD is binary; failing work returns upstream [WEB:scrum.org quoting Scrum Guide 2020].
  - Judge decision process and evidence, not outcome ("resulting") [BOOK:Duke 2018].
  - Insist on the highest standards [BOOK:Amazon LPs].
- **Accountabilities**:
  - OWNS: gate verdict; verification that every must-meet item has evidence; reconciliation of findings from the critic, pool reviewers, and traceability auditor; deciding whether MAJORs can be carried as known issues; writing the **conditions** for a conditional GO; escalation memo when the cap is reached.
  - DOES NOT OWN: finding defects first-hand (consumes reviewers' findings and spot-checks them); fixing anything; changing the rubric mid-gate; product scope decisions.
- **Inputs needed**: stage rubric + DoD; artifact; all findings files; deterministic check results; iteration state (`round`, `max_rounds`); override log; reference exemplar (optional).
- **Outputs/artifacts**: `gate/<stage>-verdict.json` + `gate/<stage>-verdict.md`. Industry analogues: Stage-Gate decision record (decision + action plan + next-gate deliverables), release go/no-go checklist, hiring debrief decision.
- **ACCEPTANCE criteria**:
  - [ ] Verdict ∈ {GO, GO_WITH_CONDITIONS, RECYCLE, HOLD, KILL}; a non-GO verdict cites the blocking finding IDs.
  - [ ] Every must-meet criterion has a pass/fail with an evidence pointer; any FAIL → not GO.
  - [ ] Zero open BLOCKERs for GO; open MAJORs only with conditions (owner stage + due gate).
  - [ ] Each reviewer's findings were read; disagreements between reviewers are resolved or escalated explicitly.
  - [ ] The `expected_at_next_gate` deliverables list is written (Cooper).
  - [ ] Overrides carry who/why; no BLOCKER is closed without either a fix verified at location or an override record.
  - [ ] The verdict was formed **before** reading the author's self-assessment (independence).
- **REFUSAL criteria**:
  - *blocked*: missing rubric/DoD; missing required reviewer outputs (e.g., critic or traceability report not produced); deterministic checks not run.
  - *rejected*: open BLOCKER(s) → RECYCLE; must-meet failure → RECYCLE or KILL; evidence pointers that don't resolve (finding claims fixed but location unchanged).
  - *out_of_scope*: lowering the bar due to deadlines ("ship it, we'll fix later" is a human decision recorded as override, never a gatekeeper verdict); adding new criteria at gate time; GTM readiness.
- **Anti-patterns**: rubber-stamping (gate with no teeth); "approve with 40 comments" (no decision); veto on taste; reading only the summary; letting the author's confidence stand in for evidence; recomputing the review instead of deciding; endless RECYCLE without escalation.
- **Handoffs**: receives findings from the critic, pre-mortem, cross-cutting pool, and traceability auditor → verdict to the orchestrator → (GO) orchestrator writes the handoff; (RECYCLE) back to the author worker with blocking IDs; (HOLD/cap reached) human escalation memo; (KILL) terminal record.

### R4. Architecture Review Board (ARB) / Design Review Panel
- **Real-world titles**: Architecture Review Board, Technical Design Authority (UK public sector), Design Review panel, RFC sub-team / shepherd (Rust), Principal Engineer review, ERD approvers (Uber). **Stages**: architecture (primary); light-touch at tasks (does the decomposition respect the architecture?); consultative at PRD for feasibility.
- **Mission**: ensure significant design decisions are justified against alternatives, conform to principles and constraints (or record explicit exceptions), and are fit for the stated quality attributes, before implementation effort is committed.
- **Mindset & principles**:
  - Write it down and vet it before code [WEB:x.com/GergelyOrosz Uber RFC].
  - Alternatives considered, non-goals, cross-cutting concerns as mandatory sections [BOOK:Ubl, Design Docs at Google 2020].
  - Disposition discipline: merge/close/postpone; final comment period; only new arguments reopen [WEB:github.com/rust-lang/rfcs].
  - Review threshold: only "substantial" changes need full review [WEB:github.com/rust-lang/rfcs].
  - Quality-attribute-driven evaluation (ATAM: utility tree, scenarios, sensitivity points, trade-offs, risks/non-risks) [BOOK:Bass, Clements, Kazman, *Software Architecture in Practice*, 4th ed. 2021, ch.21 ATAM].
  - Decisions recorded as ADRs (context, decision, status, consequences) [BOOK:Michael Nygard, "Documenting Architecture Decisions", 2011 blog].
- **Accountabilities**:
  - OWNS: per-decision review (ADR quality, alternatives, trade-offs); conformance to principles/standards; quality-attribute scenario coverage; risks/non-risks/sensitivity points list; disposition per ADR (accept / accept-with-conditions / reject / postpone).
  - DOES NOT OWN: writing the architecture; product requirements (PRD stage); specialist security/privacy/SRE/FinOps depth (pool reviewers attach their findings); implementation task breakdown.
- **Inputs needed**: architecture doc + ADRs; PRD NFRs and constraints; enterprise principles/tech radar (if any); pool reviewers' findings; traceability report (FR/NFR → components).
- **Outputs/artifacts**: `gate/architecture-arb-review.md`: per-ADR disposition table; ATAM-style list of risks, non-risks, sensitivity points, trade-offs; conditions; exceptions register.
- **ACCEPTANCE criteria**:
  - [ ] Every significant decision has an ADR with ≥2 genuinely viable alternatives and the reason for rejection.
  - [ ] Every NFR from the PRD maps to ≥1 quality-attribute scenario (stimulus, environment, response, measure) and to the architectural tactic addressing it.
  - [ ] Non-goals and explicit out-of-scope stated.
  - [ ] Deviations from principles/standards are listed as exceptions with rationale and an owner.
  - [ ] Each top risk has a mitigation or a spike/task request for the tasks stage.
  - [ ] Each ADR carries a disposition; conditions are testable.
- **REFUSAL criteria**:
  - *blocked*: no PRD NFRs/quality attributes (cannot evaluate fitness); no ADRs or decision log (nothing reviewable); missing context diagram.
  - *rejected*: single-option "designs" with no alternatives on a significant decision; NFRs unaddressed; contradictions between ADRs; design depends on an unvalidated assumption flagged as BLOCKER in discovery.
  - *out_of_scope*: re-opening product scope; choosing vendors on commercial terms; code-level review; reviewing trivial changes below the threshold.
- **Anti-patterns**: ARB as bottleneck or ivory tower; rubber stamp; bikeshedding naming/style; reviewing the diagram, not the decisions; approving "conditionally" with untestable conditions; re-litigating accepted ADRs without new arguments.
- **Handoffs**: receives architecture + ADRs from the architecture orchestrator, PRD NFRs via handoff, and pool findings → delivers dispositions to the architecture gatekeeper; conditions and spikes go into the handoff for the tasks stage.

### R5. Traceability / Requirements Auditor
- **Real-world titles**: Requirements Engineer / Business Analyst (verification role), V&V Engineer, Quality Assurance Auditor (regulated industries: DO-178C, IEC 62304, ISO 26262), Configuration/Requirements Manager. **Stages**: shared, run at every EXIT gate and every ENTRY gate. (Full persona owned by the traceability axis; here only its gate behaviour.)
- **Mission**: prove, mechanically where possible, that every upstream commitment is carried forward or explicitly dropped, and that nothing downstream exists without an upstream reason.
- **Mindset & principles**:
  - Bidirectional traceability: forward (each requirement → design → task → test) and backward (each task → requirement) [BOOK:Wiegers & Beatty, *Software Requirements*, 3rd ed. 2013, ch.29] [UNVERIFIED chapter].
  - Requirements quality attributes: correct, unambiguous, complete, consistent, ranked, verifiable, modifiable, traceable [BOOK:IEEE 830-1998 §4.3; superseded by ISO/IEC/IEEE 29148:2018 §5.2].
  - Audit, don't author: findings, not rewrites.
- **Accountabilities**:
  - OWNS: trace matrix validation; orphan detection (downstream items with no parent); gap detection (upstream items with no child); ID integrity; requirement-quality lint (ambiguous terms like "fast", "user-friendly", "etc.", TBDs).
  - DOES NOT OWN: deciding whether a dropped requirement is acceptable (orchestrator/human); prioritisation; content quality beyond verifiability.
- **Inputs needed**: upstream handoff (with IDs), current artifact (with IDs), trace file.
- **Outputs/artifacts**: `gate/<stage>-trace-report.json` (coverage %, orphans[], gaps[], ambiguous[] with IDs); an RTM (requirements traceability matrix) is the industry standard.
- **ACCEPTANCE criteria**:
  - [ ] 100% of upstream MUST items have ≥1 downstream child or an explicit `dropped` record with rationale and approver.
  - [ ] 0 orphans (or each orphan justified as enabling/technical work, linked to an NFR/ADR).
  - [ ] All IDs unique and stable versus the previous handoff (no silent renumbering).
  - [ ] Each requirement/acceptance criterion is verifiable (has a measurable condition or test idea).
  - [ ] Ambiguity lint run; remaining flagged terms each resolved or accepted.
- **REFUSAL criteria**:
  - *blocked*: upstream artifact has no IDs; trace file missing; handoff version mismatch.
  - *rejected*: coverage of MUST items <100% without drop records; renumbered IDs breaking links.
  - *out_of_scope*: judging whether a requirement is the *right* requirement (critic/PM); writing missing requirements.
- **Anti-patterns**: trace matrices maintained by hand and stale; "traced" links that are only keyword matches; counting coverage without checking verifiability; letting LLMs infer links silently instead of requiring explicit `traces_to` fields.
- **Handoffs**: receives artifacts at each gate → delivers trace report to the gatekeeper (gaps/orphans are BLOCKER/MAJOR candidates); trace file updated in the handoff for the next stage's ENTRY gate.

### R6. Editor / Clarity Reviewer
- **Real-world titles**: Technical Editor, Staff Technical Writer, Documentation Reviewer, "6-pager" reviewer at Amazon (narrative memos read in silence at the start of meetings) [BOOK:Bryar & Carr, *Working Backwards*, 2021, ch.4]. **Stages**: discovery brief, PRD (highest value), architecture doc; minimal for tasks (task titles/AC clarity).
- **Mission**: ensure the artifact can be understood **by its downstream consumer in a fresh session with no conversation history**: unambiguous, consistent terminology, decisions stated rather than implied, appropriate length.
- **Mindset & principles**:
  - Understanding is the main bottleneck in review [WEB:microsoft.com Bacchelli & Bird 2013].
  - Write for the reader; bottom line up front; one term per concept (glossary) [BOOK:Williams & Bizup, *Style: Lessons in Clarity and Grace*, 12th ed.] [BOOK:Minto, *The Pyramid Principle*, 1987].
  - Narrative over bullets for reasoning [BOOK:Bryar & Carr 2021].
  - Requirements language: "shall/must" vs "should/may" used consistently [BOOK:RFC 2119 (Bradner, 1997)].
  - Counter verbosity bias: shorter is better when complete [WEB:arxiv.org/abs/2306.05685].
- **Accountabilities**:
  - OWNS: ambiguity, inconsistent terminology, undefined acronyms, buried decisions, contradictory statements, structure vs template, readability, length budget; glossary completeness.
  - DOES NOT OWN: substantive correctness of content; changing meaning; scope.
- **Inputs needed**: artifact; template; glossary; target reader (next-stage orchestrator persona).
- **Outputs/artifacts**: `gate/<stage>-clarity.md`: list of findings (location, issue type, suggested rewording that does *not* change meaning); "cold-read test" result.
- **ACCEPTANCE criteria**:
  - [ ] Cold-read test: a fresh-context reader, given only the handoff, can state goal, scope, non-goals, key decisions, and open questions; mismatches are findings.
  - [ ] All domain terms and acronyms defined once in the glossary and used consistently.
  - [ ] Normative keywords (MUST/SHOULD/MAY) used consistently in requirements.
  - [ ] No unresolved TBD/TODO in required sections (or each tracked as an open question with owner).
  - [ ] Within the length budget for the template.
- **REFUSAL criteria**:
  - *blocked*: no target template or audience defined.
  - *rejected*: contradictions between sections (e.g., scope says X is out, an FR requires X) → MAJOR/BLOCKER back to author, since the editor cannot pick the meaning.
  - *out_of_scope*: rewriting the document wholesale; content decisions; "make it sound more persuasive" (GTM).
- **Anti-patterns**: rewriting voice instead of fixing ambiguity; changing meaning while "clarifying"; style nitpicks rated as MAJOR; adding length.
- **Handoffs**: receives a near-final artifact from the orchestrator (after substantive fixes, so it does not polish text that will be rewritten) → findings to the author; contradictions flagged to the critic/gatekeeper.

### R7. Decision Quality Reviewer (optional; can merge into R1)
- **Real-world titles**: Decision Analyst, Strategy/Investment Committee reviewer, "Decision hygiene" checker (Kahneman, Sibony, Sunstein, *Noise*, 2021). **Stages**: discovery (which problem/opportunity to pursue), architecture (option selection).
- **Mission**: assess whether a recommendation was reached by a sound process: alternatives, base rates, calibrated confidence, dissent explored, self-interest checked.
- **Mindset**: resulting avoidance and calibration [BOOK:Duke 2018]; the 12-question checklist [BOOK:Kahneman, Lovallo, Sibony 2011]; outside view [BOOK:Kahneman 2011 ch.23]; decision hygiene / independent judgments before aggregation [BOOK:Kahneman, Sibony, Sunstein, *Noise*, 2021].
- **OWNS**: checklist answers with evidence; confidence calibration flags; base-rate presence. **DOES NOT OWN**: the decision itself.
- **ACCEPTANCE**: [ ] ≥2 credible alternatives evaluated with the same criteria; [ ] estimates/forecasts reference a base rate or are marked inside-view; [ ] confidence levels stated with evidence; [ ] kill criteria/tripwires defined; [ ] disconfirming evidence actively sought (where and what was found).
- **REFUSAL**: *blocked*: no recommendation stated. *rejected*: single-option recommendation; certainty language with no evidence. *out_of_scope*: making the call.
- **Anti-patterns**: checklist theatre (all "yes"); demanding quantitative precision the evidence can't support.
- **Handoffs**: to the stage critic/gatekeeper as additional findings. Recommendation: **merge into R1's rubric** for discovery and architecture rather than run a separate subagent.

---

## Gate rubric template (reusable; one file per stage: `gates/<stage>-rubric.md`)

```yaml
gate:
  stage: prd                      # discovery | prd | architecture | tasks
  type: exit                      # entry | exit
  rubric_version: 1.2             # changing the rubric = human decision, never mid-loop
  max_rounds: 3                   # critic/revise iterations before escalation
  reviewers: [stage-critic, traceability-auditor, editor, security?, privacy?, a11y?, sre?, finops?, analytics?]
  reference_exemplar: gates/exemplars/prd-good.md   # optional "bar" sample

inputs_required:                  # ENTRY: absence => verdict BLOCKED
  - path: handoff/discovery-handoff.md
    must_have: [problem_statement, target_users, evidence, success_metrics, kill_criteria, open_questions]
  - path: handoff/discovery-trace.json

deterministic_checks:             # run by script/hook FIRST; any fail => BLOCKER, no LLM review spent
  - id: D1  check: required headings present per template
  - id: D2  check: every FR/NFR has unique ID matching ^(FR|NFR)-\d{3}$
  - id: D3  check: every FR has >=1 acceptance criterion
  - id: D4  check: no "TBD|TODO" in MUST sections
  - id: D5  check: trace coverage of upstream MUST items == 100% or dropped-with-rationale

must_meet:                        # binary, judge-evaluated, each FAIL => BLOCKER
  - id: M1
    criterion: "Problem and target users match the discovery handoff (no silent scope change)."
    pass_definition: "Every user segment and problem in PRD §1 cites a discovery ID; any delta is listed under 'Changes from discovery' with rationale."
    evidence_required: "IDs + section refs"
    fail_example: "PRD adds an 'admin' persona not in discovery and no delta note."
  - id: M2
    criterion: "Each FR is verifiable."
    pass_definition: "Acceptance criteria are Given/When/Then or measurable thresholds; no unqualified adjectives (fast, easy, intuitive)."
  - id: M3
    criterion: "Non-goals stated."
  - id: M4
    criterion: "Success metrics have baseline, target, and measurement source."
  # keep to <= ~8 per stage

should_meet:                      # binary per item; FAIL => MAJOR or MINOR (pre-assigned)
  - id: S1  criterion: "Alternatives considered for the top 3 product decisions."   severity_if_fail: MAJOR
  - id: S2  criterion: "Pre-mortem top-5 risks each have a disposition."             severity_if_fail: MAJOR
  - id: S3  criterion: "Glossary covers all domain terms."                            severity_if_fail: MINOR
  - id: S4  criterion: "Within length budget (<= N pages)."                           severity_if_fail: MINOR

decision_rule:
  GO:                  "0 deterministic fails, 0 open BLOCKER, 0 open MAJOR"
  GO_WITH_CONDITIONS:  "0 BLOCKER; MAJORs each have owner_stage + due_gate; <= 3 MAJORs"
  RECYCLE:             "any open BLOCKER and round < max_rounds"
  HOLD (escalate):     "round == max_rounds with BLOCKER open, OR no-progress (same open BLOCKER/MAJOR IDs in 2 consecutive rounds), OR reviewer conflict unresolved"
  KILL (human only):   "kill_criteria from discovery triggered, or human decides"
  BLOCKED:             "inputs_required missing (ENTRY gate)"

termination_rules:
  - "MINOR findings never trigger another round."
  - "After round 1, a new BLOCKER is admissible only if caused by the revision or backed by new evidence; else downgrade to note."
  - "Findings overridden in the decision log are not re-raised."
  - "Rubric changes are out of loop: escalate."

outputs:
  - gate/<stage>-findings.json     # stable IDs, status across rounds
  - gate/<stage>-verdict.json      # verdict, round, blocking_ids, conditions, expected_at_next_gate
  - gate/<stage>-decision-log.md   # overrides: id, by (human|orchestrator), rationale, date
```

### Finding schema (`gate/<stage>-findings.json`, one entry per finding)
```json
{ "id": "PRD-G-007", "round_raised": 1, "reviewer": "stage-critic",
  "severity": "BLOCKER", "criterion": "M2",
  "location": "prd.md#FR-012",
  "evidence": "AC says 'search should be fast'",
  "failure_scenario": "Architecture cannot size the search tier; tasks get no testable AC.",
  "suggested_direction": "State p95 latency at a given corpus size.",
  "refusal_class": "rejected",
  "status": "open | fixed_verified | overridden | downgraded | withdrawn",
  "history": [{"round": 2, "status": "open", "note": "AC now 'fast (<1s)' but no load condition"}] }
```

### Verdict schema (`gate/<stage>-verdict.json`)
```json
{ "stage": "prd", "gate": "exit", "round": 2, "max_rounds": 3,
  "verdict": "GO | GO_WITH_CONDITIONS | RECYCLE | HOLD | KILL | BLOCKED",
  "refusal_class": null,
  "blocking_ids": [], "conditions": [{"finding": "PRD-G-011", "owner_stage": "architecture", "due_gate": "architecture-exit"}],
  "expected_at_next_gate": ["ADR per significant decision", "NFR→scenario map"],
  "escalation_memo": null, "rubric_version": "1.2", "inputs_hash": "sha256:..." }
```
The `inputs_hash` matters because each stage runs in a fresh session. The next stage's ENTRY gate can confirm that the handoff it reads is the one that was gated.

---

## Severity scale with refusal semantics

| Severity | Definition (testable) | Effect on gate | Refusal class mapping | Loop behaviour |
|---|---|---|---|---|
| **BLOCKER** | Fails a deterministic check or a `must_meet` criterion; OR the next stage would be unable to proceed or would very likely build the wrong thing (concrete failure scenario required); OR a kill criterion is triggered; OR a cross-cutting legal/safety violation (e.g., PII without lawful basis). | Verdict cannot be GO/GO_WITH_CONDITIONS. | Missing input → **blocked**; quality failure of present work → **rejected**; kill criterion → KILL (human-confirmed). | Triggers RECYCLE (if rounds remain) or HOLD + human escalation. Can only close as `fixed_verified` (re-checked at the cited location) or `overridden` (human, with rationale). |
| **MAJOR** | Fails a `should_meet` criterion pre-assigned MAJOR; OR materially raises downstream rework/risk but downstream can proceed with a stated condition. | GO_WITH_CONDITIONS allowed if each MAJOR has owner_stage + due_gate and count ≤ cap (e.g., 3); else RECYCLE. | **rejected** if over the cap or unconditioned; otherwise carried as a condition. | Can trigger a revision round; downgrading to MINOR requires a recorded reason. |
| **MINOR** | Clarity, style, completeness nice-to-haves; no downstream impact if left. | Never blocks. | none (advisory). | Never triggers a new round; listed in the handoff's `known_issues`. |
| *(note / observation)* | Reviewer comment not tied to any rubric criterion. | Ignored for gating. | — | May feed a *proposed* rubric change, reviewed by a human out of loop. |
| **OUT_OF_SCOPE** (classification, not severity) | Request or finding belongs to another stage/role (or GTM). | Routed, not gated. | **out_of_scope** | Logged with the target owner (e.g., `owner: privacy-reviewer` or `extension:gtm`). |

Rules: severity is assigned **by rubric mapping first, judgment second**. A reviewer may raise severity above the rubric default only with a failure scenario, and may never lower a must-meet failure below BLOCKER. Only a human override can do that.

---

## Implications for agentic personas

**What to split vs. merge**
- Keep **finder** and **decider** separate: the stage critic (R1) finds, the gatekeeper (R3) decides. Merging them yields self-justifying verdicts. The gatekeeper consumes findings and spot-checks the evidence pointers, which is cheap. The orchestrator then applies the `decision_rule` mechanically and adds no judgment of its own on whether to pass (Blue hat).
- **Merge** the decision-quality reviewer (R7) and the devil's-advocate function into R1's rubric (stage-specific sections). Separate subagents for each "hat" multiply cost and contradictions.
- **Pre-mortem (R2) stays separate**, because its value comes from **not seeing the authors' rationale**. Give it a stripped plan summary plus success criteria in a fresh subagent context. Run it at discovery (the bet), architecture (the chosen option), and tasks (the delivery plan).
- ARB (R4) is the architecture stage's specialised critic, effectively R1 with an ATAM/ADR rubric. Implement it as the same critic persona with a stage-specific rubric file, or as a dedicated persona if the architecture rubric is large.
- Traceability (R5) is **mostly deterministic**. Implement it as a script/hook that produces the trace report, plus a small LLM step for verifiability lint and justification review. Never let an LLM "infer" trace links. Require explicit `traces_to` fields.
- The editor (R6) runs **last**, after substantive fixes. Its most valuable check is the **cold-read test**: a fresh subagent given only the handoff must reconstruct the goal, scope, decisions, and open questions. This directly simulates the next stage's fresh session.

**What LLMs tend to get wrong here**
- **Sycophancy and self-enhancement**: same-model critics praise their own family's output [WEB:anthropic harness-design; WEB:arxiv 2306.05685]. Mitigations: separate context; ideally a different model for the critic and gatekeeper; skepticism safeguard clause; require ≥1 finding *or* an explicit "no BLOCKER found because …" justification per must-meet criterion.
- **Nit floods and moving goalposts**: LLM critics never run out of comments. Mitigations: severity mapping from the rubric, MINORs never loop, the post-round-1 admissibility rule for new BLOCKERs, and stable finding IDs on disk.
- **Verbosity reward**: judges prefer longer artifacts. Add a length budget criterion and instruct the judge that length is not evidence.
- **Hallucinated evidence**: findings citing sections that don't exist, or "fixed" claims. Each finding must carry a resolvable `location`, and the orchestrator (or a script) verifies the location exists and that the cited text is present.
- **Intrinsic self-correction doesn't work** [WEB:arxiv 2310.01798]. A "reflect and improve" step without the rubric, deterministic checks, or upstream criteria is noise. Every critic round must be grounded in an external artifact.
- **Likert drift**: 1–5 quality scores cluster at 3–4 and don't discriminate. Use binary per-criterion pass/fail plus a critique, with a pass_definition and a fail_example in the rubric [WEB:hamel.dev evals-faq].
- **Strawman devil's advocacy**: "argue the opposite" produces weak counters. Require a counter-hypothesis plus the observable evidence that would distinguish the two.
- **Redesigning instead of critiquing**: the critic rewrites sections, which destroys traceability and authorship. Persona rule: "suggested_direction ≤ 2 sentences; never produce replacement text for more than one sentence".
- **Gate amnesia across sessions**: since stages run in separate windows, a gatekeeper cannot "remember" an override discussed earlier. All overrides, conditions, and kill criteria live in `gate/*.json` and the decision log, and the ENTRY gate of the next stage reads them.

**What must be a hard gate (blocking, ideally deterministic)**
1. ENTRY: required upstream files exist, the schema is valid, `inputs_hash` matches the upstream verdict, and the upstream verdict ∈ {GO, GO_WITH_CONDITIONS}. Otherwise **blocked**. The stage orchestrator refuses to start and writes a `blocked` record naming the missing items.
2. ENTRY: upstream conditions whose `due_gate` is this stage are surfaced into this stage's rubric as must-meet items.
3. EXIT: deterministic checks (template sections, ID format, trace coverage, no TBD in MUST sections).
4. EXIT: zero open BLOCKERs (must-meet criteria, judge-evaluated with evidence).
5. EXIT: iteration cap reached or no progress → **HOLD and escalate to a human**, never auto-pass. The escalation memo states the open BLOCKERs, the positions of author and critic, the options (fix / override with rationale / descope / kill), and the recommended option.
6. Kill criteria from discovery are re-evaluated at every EXIT gate. A triggered kill criterion produces a KILL recommendation, which requires human confirmation.

**Advisory (non-blocking) by design**: MINOR findings, the editor's style suggestions, should-meet items mapped to MINOR, observations, and proposed rubric changes.

**Persona-prompt elements to include** (consistent with the local agent-prompt style [LOCAL:harness research, `agent-prompt-style.md`]): a one-job declaration ("Your one job is to find rubric violations in X; you do not fix or decide"); DO NOT boundaries (no rewriting, no new criteria, no severity softening, no re-raising overridden findings); inputs read from explicit paths; output exactly in the finding schema; refusal output (`{"verdict":"BLOCKED","refusal_class":"blocked","missing":[...]}`) when inputs are absent; `maxTurns` bound.

**Human-in-the-loop placement**: the human is the "commit" authority in disagree-and-commit. They decide overrides, rubric changes, KILL, and HOLD resolutions. Every human decision is written to the decision log so later fresh sessions inherit it.

---

## Sources

1. Anthropic, "Building effective agents" (Dec 2024) — https://www.anthropic.com/engineering/building-effective-agents [WEB, fetched]
2. Anthropic, "Harness design for long-running application development" — https://www.anthropic.com/engineering/harness-design-long-running-apps [WEB, fetched]
3. Klein, G., "Performing a Project Premortem", Harvard Business Review, Sept 2007 [BOOK; hbr.org blocked]; corroborated via https://get-alfred.ai/blog/pre-mortem-technique and https://corporate.jasoncollins.blog/premortem [WEB, search snippets]
4. Mitchell, D. J., Russo, J. E., Pennington, N., "Back to the future: Temporal perspective in the explanation of events", Journal of Behavioral Decision Making, 1989 [BOOK; via secondary sources]
5. UK MoD DCDC, *Red Teaming Handbook*, 3rd ed., June 2021 — https://assets.publishing.service.gov.uk/media/61702155e90e07197867eb93/20210625-Red_Teaming_Handbook.pdf (blocked); definitions via https://www.civilserviceworld.com/news/article/mod-updates-guidance-on-red-teaming-for-problemsolvers and https://www.scribd.com/document/896798182/20210625-Red-Teaming-Handbook-1 [WEB, search snippets]
6. Zenko, M., *Red Team: How to Succeed by Thinking Like the Enemy*, Basic Books, 2015 [BOOK]
7. Amazon Leadership Principles ("Have Backbone; Disagree and Commit"; "Insist on the Highest Standards"; "Are Right, A Lot") — https://quarterdeck.co.uk/articles/leadership-principles-amazon/ ; https://en.wikipedia.org/wiki/Disagree_and_commit [WEB, search snippets; amazon.jobs blocked]
8. de Bono, E., *Six Thinking Hats*, 1985 [BOOK]
9. Ubl, M., "Design Docs at Google", 2020 — https://www.industrialempathy.com/posts/design-docs-at-google/ [BOOK/blocked]; Orosz confirmation https://x.com/GergelyOrosz/status/1286013033618255878 [WEB]
10. Orosz, G., "Scaling Engineering Teams via RFCs: Writing Things Down" — https://blog.pragmaticengineer.com/scaling-engineering-teams-via-writing-things-down-rfcs/ ; https://x.com/GergelyOrosz/status/1260994818899140609 ; https://newsletter.pragmaticengineer.com/p/software-engineering-rfc-and-design [WEB, search snippets]
11. Rust RFCs README — https://github.com/rust-lang/rfcs/blob/master/README.md [WEB, fetched]
12. Amazon Bar Raiser — https://www.carrus.io/blog/all-about-bar-raisers-amazons-essential-element-to-the-hiring-process ; https://4dayweek.io/interview-process/amazon-bar-raiser [WEB, search snippets]; Bryar, C. & Carr, B., *Working Backwards*, 2021 [BOOK]
13. Cooper, R. G., *Winning at New Products*, 4th ed. 2011 / 5th ed. 2017 [BOOK]; gate criteria via https://www.wellspring.com/blog/how-to-manage-your-innovation-process-the-stage-gate-framework and https://portfoliohub.io/blog/stage-gate-review-template [WEB, search snippets]
14. Schwaber & Sutherland, *The Scrum Guide*, Nov 2020 — DoD passage quoted at https://www.scrum.org/forum/scrum-forum/46113/if-product-backlog-item-does-not-meet-definition-done-it-cannot-be-released [WEB, search snippet]
15. Fagan, M. E., "Design and code inspections to reduce errors in program development", IBM Systems Journal 15(3), 1976 [BOOK]
16. Bacchelli, A. & Bird, C., "Expectations, outcomes, and challenges of modern code review", ICSE 2013 — https://www.microsoft.com/en-us/research/publication/expectations-outcomes-and-challenges-of-modern-code-review/ [WEB, search snippet]
17. Cohen, J., *Best Kept Secrets of Peer Code Review*, SmartBear, 2006 [BOOK; numbers UNVERIFIED]
18. Kahneman, D., *Thinking, Fast and Slow*, 2011 (ch.7 WYSIATI; ch.23 outside view; ch.24 premortem) [BOOK]
19. Kahneman, D., Lovallo, D., Sibony, O., "Before You Make That Big Decision", HBR, June 2011 [BOOK; wording UNVERIFIED]
20. Kahneman, D., Sibony, O., Sunstein, C., *Noise*, 2021 [BOOK]
21. Duke, A., *Thinking in Bets* (2018); *How to Decide* (2020); *Quit* (2022) [BOOK]
22. Huang, J. et al., "Large Language Models Cannot Self-Correct Reasoning Yet", ICLR 2024 — https://arxiv.org/pdf/2310.01798 [WEB, search snippet]
23. Zheng, L. et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", NeurIPS 2023 — https://arxiv.org/abs/2306.05685 [WEB, search snippet]
24. Husain, H. & Shankar, S., "LLM Evals: Everything You Need to Know" (FAQ, 2025) — https://hamel.dev/blog/posts/evals-faq/evals-faq.pdf ; https://github.com/hamelsmu/evals-skills/blob/main/questions.md [WEB, search snippets]
25. Bass, L., Clements, P., Kazman, R., *Software Architecture in Practice*, 4th ed., 2021 (ATAM) [BOOK]
26. Nygard, M., "Documenting Architecture Decisions", 2011 [BOOK/blog]
27. The Open Group, TOGAF 9.2 — Architecture Board / Architecture Compliance [BOOK; chapter UNVERIFIED]
28. Wiegers, K. & Beatty, J., *Software Requirements*, 3rd ed., 2013 [BOOK]; ISO/IEC/IEEE 29148:2018 [BOOK]
29. Bradner, S., RFC 2119 "Key words for use in RFCs to Indicate Requirement Levels", 1997 [BOOK]
30. Nemeth, C., *In Defense of Troublemakers*, 2018 [BOOK; specifics UNVERIFIED]
31. Local: /home/user/ai-study-library/dev/research/2026-04-25-harness-engineering-research.md (§11 Critic/Review Patterns; plan-critic PROCEED|REVISE; Skepticism Safeguard; Cross-Model Review; max_iterations state) [LOCAL]
32. Local: /home/user/ai-study-library/ai/docs/harness-engineering/harnessengineering-building-the-operating-system-for-autonomous-agents.md (Evaluator/QA agent; deterministic rails; HITL veto) [LOCAL]

---

## Verification log

Verifier pass on 2026-10-02. Primary sites (hbr.org, gov.uk, amazon.jobs, aclanthology, iclr.cc) remain blocked, so checks used fetched pages where possible and search results otherwise.

**Confirmed:**
- Anthropic "Building effective agents": the evaluator-optimizer quotes ("clear evaluation criteria, and when iterative refinement provides measurable value", and both signs of fit) are exact. Fetched.
- Anthropic "Harness design" (Rajasekaran, 24 Mar 2026). Fetched. Exact matches:
  - "separating the agent doing the work from the agent judging it proves to be a strong lever";
  - "confidently praising the work—even when, to a human observer, the quality is obviously mediocre";
  - "each criterion had a hard threshold, and if any one fell below it, the sprint failed";
  - "5 to 15 iterations per generation";
  - the sprint contract agreed before work begins.
- Rust RFC README. Fetched. Confirmed:
  - FCP "lasts ten calendar days, so that it is open for at least 5 business days";
  - the merge/close/postpone dispositions;
  - substantial new arguments cancel FCP;
  - all sub-team members sign off before FCP.
- Amazon "Have Backbone; Disagree and Commit": the full quoted wording matches the official text, through search results that cite aboutamazon.com.
- Red Teaming Handbook 3rd ed. (DCDC, June 2021): the red-team definition quote and the shift to a "red team mindset" are confirmed through search.
- Klein (HBR 2007) citing Mitchell, Russo & Pennington (1989): about 30% more reasons generated, through search.
- Bacchelli & Bird (ICSE 2013): "less about defects than expected", plus knowledge transfer, team awareness and alternative solutions, through search.
- Husain & Shankar evals FAQ: binary over Likert, and the "Critique Shadowing" name and practice, through search.
- Bar Raiser: the veto and the "better than 50% of peers in similar roles" bar, through search.
- Huang et al. and Zheng et al.: the claims as stated are confirmed (see file 08's log).
- Local corpus. In `2026-04-25-harness-engineering-research.md`, the following match:
  - plan-critic `PROCEED|REVISE` (around line 97);
  - the Skepticism Safeguard and >100x rule (§11, lines 709-725);
  - Cross-Model Review (line 725);
  - `iteration` / `max_iterations` (around line 105);
  - `agent-prompt-style.md` (lines 64 and 389).
- Local corpus. In `harnessengineering-building-...md`, the quote "physically blocked from marking a task as complete" is at line 189 and the HITL "final veto" is at line 191.

**Corrected:**
- Pre-mortem 30%. Mitchell et al. measured the **number** of reasons generated. Klein's article phrases it as "correctly identify reasons", which the 1989 study did not test. The text now says this.
- Harness-design quote. The source's contrast is "Is this design beautiful?", not "is this beautiful?".
- Checklist reading. The claim that checklists "consistently beat" ad-hoc reading is not supported. Porter, Votta & Basili (1995) found scenario-based reading beat both, with checklists no better than ad hoc. I rewrote it, tagged BOOK with specifics UNVERIFIED.
- Fagan. Added that explicit entry criteria were formalised mainly in Fagan's 1986 IEEE TSE follow-up. The 1976 paper is still the origin of the inspection process.
- Duke. Kill criteria ("states and dates") belong mainly to *Quit* (2022). Which tools appear in *How to Decide* (2020) is now marked UNVERIFIED.
- Bar Raiser. Added that secondary sources describe the veto as rarely used.

**Left as tagged (not re-verified):**
- Red Teaming Handbook technique list.
- civilserviceworld "human frailties" wording (search snippet only).
- Zenko's six best practices: they match my knowledge of ch.1.
- Amazon "Insist on the Highest Standards" and "Are Right, A Lot" wording.
- Nemeth (2018) specifics.
- Ubl's "Design Docs at Google" (2020; blog, blocked).
- TOGAF chapter numbering.
- Harmel-Law (2024): the book exists, O'Reilly, late 2024.
- Cooper chapter references.
- SmartBear/Cisco numbers (200-400 LOC, 500 LOC/hour; these match my knowledge).
- Kahneman-Lovallo-Sibony 12-question wording.
- Bryar & Carr chapter details: ch.2 is the Bar Raiser and ch.4 is narratives/six-pager, as I recall.

**Spot-checked by knowledge (no change):**
- Kahneman *Thinking, Fast and Slow*: ch.7 (WYSIATI), ch.23 (Outside View), ch.24 (premortem).
- de Bono (1985).
- Cooper: Go/Kill/Hold/Recycle and must-meet/should-meet.
- Fagan (1976): IBM Systems Journal 15(3).
- Bass/Clements/Kazman, 4th ed. (2021), ATAM.
- Nygard ADR (2011).
- IEEE 830-1998 §4.3 qualities.
- RFC 2119 (1997).
- Williams & Bizup.
- Minto.
- *Noise* (2021).
- Wiegers & Beatty ch.29 ("Links in the requirements chain").
