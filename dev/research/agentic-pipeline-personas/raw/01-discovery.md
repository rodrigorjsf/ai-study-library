# Raw research — Discovery & product strategy

Axis: what happens BEFORE a PRD. Scope: turning a raw idea into a validated problem/opportunity statement with explicit, tested-or-flagged assumptions, so the PRD orchestrator (fresh session) can enter with a handoff it can trust.

Tagging convention: [WEB:<url>] = read/confirmed online during this research (often via search-result summaries, since svpg.com, producttalk.org, momtestbook.com and nngroup.com were blocked by the egress proxy; tagged with the URL that surfaced the claim); [BOOK:...] = from the book, known well; [UNVERIFIED] = plausible but not confirmed. Quotes appear only where the wording was confirmed in a search result.

---

## Literature & frameworks

### 1. Marty Cagan — *Inspired* (2nd ed. 2017), *Empowered* (2020), *Transformed* (2024)
- **Four big risks** frame all discovery: value (will customers buy it or choose to use it), usability (can users figure out how to use it), feasibility (can engineering build it with the time, skills and tech available), business viability (does it work for the business: sales channel, legal/contracts, cost to acquire, monetization, brand). [WEB:https://www.svpg.com/four-big-risks/] (via search summary)
- Risks are to be attacked **during discovery, cheaply, with prototypes, before production code**; the PM owns value and viability risk, the designer usability, the tech lead feasibility. [WEB:https://www.svpg.com/four-big-risks/] [BOOK:Cagan, Inspired, 2017, Part IV "The Right Process" — Product Discovery, ch. 33 "Principles of Product Discovery"] [WEB:https://www.oreilly.com/library/view/inspired-2nd-edition/9781119387503/p04a.xhtml] (corrected: discovery is Part IV "The Right Process", not Part III "The Right Product")
- **Product trio** (PM + product designer + tech lead) does discovery together; engineers must be in discovery, not only delivery, or feasibility risk is discovered late. [BOOK:Cagan, Inspired, 2017, ch. "The Product Manager" / "Product Discovery Principles"]
- Discovery vs delivery are distinct workstreams; discovery output is *validated product backlog items*, not specs. Most ideas will not work and those that do take several iterations. [BOOK:Cagan, Inspired, 2017, ch. 33 "Principles of Product Discovery"]
- **Empowered teams are given problems to solve, not features to build**; "feature team" vs "empowered product team"; outcomes over output; OKRs at team level. [BOOK:Cagan & Jones, Empowered, 2020, Part I and "Team Objectives"]
- *Transformed* adds the **product operating model** and explicitly names the product manager's knowledge requirements: deep knowledge of users/customers, data, the business (stakeholders, finance, legal, sales) and the industry/market. [BOOK:Cagan, Transformed, 2024, "Product Model Competencies"] (also in *Inspired* ch. "The Product Manager") 
- Persona-design implication: the discovery orchestrator must produce a **risk register keyed by the four risks**, each with status (untested / tested-supported / tested-refuted / assumed) — not a narrative.

### 2. Teresa Torres — *Continuous Discovery Habits* (2021)
- Definition: continuous discovery = at minimum weekly touchpoints with customers by the team building the product, conducting small research activities in pursuit of a desired product outcome. [WEB:https://maze.co/blog/making-better-product-decisions-with-teresa-torres/] (search summary, quoting Torres)
- **Opportunity Solution Tree (OST)**: root = one desired *outcome* (a metric the team can influence), then opportunities (customer needs, pain points, desires — expressed from the customer's perspective, never as solutions), then solutions, then assumption tests. [WEB:https://www.chameleon.io/blog/opportunity-solution-tree] [BOOK:Torres, Continuous Discovery Habits, 2021, ch. 3-6]
- Rule: **an opportunity that can only be addressed by one solution is a solution in disguise** [BOOK:Torres, CDH, 2021, ch. 6 "Mapping the Opportunity Space"]; target opportunities should be sized so they can be addressed in a reasonable time — go down the tree to smaller sub-opportunities.
- **Compare-and-contrast**: for a target opportunity generate at least three candidate solutions and compare, rather than evaluate one idea for "whether". [BOOK:Torres, CDH, 2021, ch. 7-8]
- **Five assumption types**: desirability, viability, feasibility, usability, ethical. [WEB:https://www.producttalk.org/2021/04/no-single-right-way-3/] (search summary). Assumptions are surfaced via story mapping, pre-mortems and walking the lines of the OST, then **mapped on importance × evidence**; test the "leap of faith" ones (important, little evidence) first. [BOOK:Torres, CDH, 2021, ch. 9 "Identifying Hidden Assumptions"]
- **Story-based interviewing**: ask for a specific recent instance ("tell me about the last time…"), excavate the story with temporal prompts; synthesize each interview into a one-page **interview snapshot** (segment/quick facts, opportunities, insights, memorable quote). [WEB:https://www.shortform.com/blog/teresa-torres-customer-interviews/] [WEB:https://andrewclark.co.uk/product-book-summaries/continuous-discovery-habits]
- Assumption tests should be small, fast, and define **success criteria before running** (Torres's own illustration is of the form "at least 4 out of 10 participants choose X"; the exact numbers are illustrative). [BOOK:Torres, CDH, 2021, ch. 10 "Testing Assumptions, Not Ideas"] [WEB:https://www.shortform.com/blog/continuous-discovery-habits-by-teresa-torres/]

### 3. Rob Fitzpatrick — *The Mom Test* (2013)
- Three rules: talk about their life instead of your idea; ask about specifics in the past instead of generics or opinions about the future; talk less and listen more. [WEB:https://www.lesswrong.com/posts/fuktKYSvzFMTfPpeT/the-mom-test-summary-and-thoughts] [WEB:https://hatrabbits.com/en/the-mom-test/]
- **Bad data** comes in three forms: compliments, fluff (generics, hypotheticals, future promises — "I would", "I usually", "I might"), and ideas/feature requests. Deflect compliments, anchor fluff back to specifics, dig beneath feature requests to the motivation. [BOOK:Fitzpatrick, The Mom Test, 2013, ch. 2 "Avoiding bad data"]
- **Commitment and advancement**: a meeting/test "succeeded" only if it ended with a currency the customer gives up — time, reputation, or money (e.g., intro to boss, pilot, pre-order). Compliments are not signal. [BOOK:Fitzpatrick, The Mom Test, 2013, ch. 5]
- Ask the "scary questions" (would they pay, is this a top-3 problem); know the 3 most important things you want to learn before each conversation. [BOOK:Fitzpatrick, The Mom Test, 2013, ch. 3 "Asking Important Questions"] (corrected from ch. 4, which is "Keeping It Casual"; chapter list confirmed [WEB:https://www.bookey.app/book/the-mom-test])
- Persona-design implication: a **"Mom Test linter"** — any evidence statement phrased as future intent/opinion/compliment is downgraded to "weak signal" automatically.

### 4. Jobs-to-be-Done (three schools — keep them distinct)
- **Christensen** (*Competing Against Luck*, 2016): customers "hire" products to make progress in a particular circumstance; jobs have functional, social and emotional dimensions; the circumstance is the unit of analysis, not the customer demographic. [BOOK:Christensen, Hall, Dillon & Duncan, Competing Against Luck, 2016, ch. 2-3]
- **Ulwick / ODI** (*What Customers Want*, 2005; *Jobs to be Done: Theory to Practice*, 2016): the job is mapped (job map: define, locate, prepare, confirm, execute, monitor, modify, conclude [BOOK:Ulwick, JTBD Theory to Practice, 2016]); needs are written as **desired outcome statements** in strict grammar: direction + metric + object of control + contextual clarifier, e.g. "Minimize the time it takes to identify the correct drill bit size for the material being drilled". [WEB:https://en.wikipedia.org/wiki/Outcome-Driven_Innovation] [WEB:https://strategyn.com/jobs-to-be-done-template/]
- ODI **opportunity score** = Importance + max(Importance − Satisfaction, 0), from survey data (typically 50-150 outcome statements rated by many respondents). [WEB:https://bradenbuchanan.substack.com/p/outcome-driven-innovation-a-critique] (search summary). Implication: an agent *cannot* compute a real opportunity score without survey data; any score it emits is an estimate and must be labelled so.
- **Moesta** (*Demand-Side Sales 101*, 2020): **four forces of progress** — push of the current situation and pull of the new solution versus anxiety of the new and habit of the present; switching happens only when push+pull > anxiety+habit. **Switch interview timeline**: first thought → passive looking → active looking → deciding → consuming/first use. [WEB:https://jobstobedone.org/radio/unpacking-the-progress-making-forces-diagram/] [WEB:https://elementalconcept.com/insights/moesta-four-forces-of-progress-jtbd/]
- Persona-design implication: job statements should be **solution-agnostic** (a test: the statement would still be true 10 years ago and 10 years from now) [BOOK:Ulwick, JTBD Theory to Practice, 2016]; the four-forces diagram is the natural place to surface adoption risk (anxiety/habit) that PRDs usually ignore.

### 5. Ash Maurya — *Running Lean* (2nd ed. 2012; 3rd ed. 2022), Lean Canvas
- **Lean Canvas** (adapted from the Business Model Canvas) 9 boxes: Problem (top 3) + Existing alternatives, Customer segments + Early adopters, Unique value proposition + High-level concept, Solution, Channels, Revenue streams, Cost structure, Key metrics, Unfair advantage. [BOOK:Maurya, Running Lean, 2012, ch. 3]
- Fill the canvas fast (≈20 minutes), treat every box as a hypothesis, and **rank risk**: problem/customer risk first, then product, then market. [BOOK:Maurya, Running Lean, 2012, ch. 4 "Identify the Riskiest Parts of Your Plan"]
- Stages: problem/solution fit → product/market fit → scale. Do not optimize solution before the problem is validated. [BOOK:Maurya, Running Lean, 2012, ch. 1]
- 3rd ed. adds **"customer factory"** and the "innovator's bias" (love the problem, not your solution) and back-of-envelope **"Fermi estimate"** of whether the model can reach a minimum success criterion in a time box. [BOOK:Maurya, Running Lean 3rd ed., 2022] [WEB:https://www.oreilly.com/library/view/running-lean-3rd/9781098108762/part03.html] (concepts confirmed in the 3rd ed.; note the Customer Factory model was first introduced in Maurya's *Scaling Lean*, 2016; exact chapter [UNVERIFIED])
- "Unfair advantage" box is the one most often filled with non-advantages ("passion", "first mover"); a reviewer should reject those. [BOOK:Maurya, Running Lean, 2012, ch. 3]

### 6. Alexander Osterwalder et al. — *Value Proposition Design* (2014)
- Value Proposition Canvas: **customer profile** (jobs, pains, gains) vs **value map** (products & services, pain relievers, gain creators). **Fit** = the value map addresses the most important jobs/pains/gains. [BOOK:Osterwalder, Pigneur, Bernarda, Smith, Value Proposition Design, 2014, "Canvas"]
- Pains and gains should be ranked (extreme vs moderate; essential vs nice-to-have) and made concrete/measurable ("waiting more than 10 minutes" rather than "waiting too long"). [BOOK:Osterwalder et al., Value Proposition Design, 2014]
- Three levels of fit: problem-solution fit (on paper), product-market fit (in market evidence), business model fit. [BOOK:Osterwalder et al., Value Proposition Design, 2014]
- *Testing Business Ideas* (Bland & Osterwalder, 2019): **test cards** (We believe… / To verify, we will… / And measure… / We are right if…) and **learning cards**; evidence strength ranked (what people say < what people do; lab < real context). [BOOK:Bland & Osterwalder, Testing Business Ideas, 2019, "Test" section]

### 7. Steve Blank — *The Four Steps to the Epiphany* (2005); Blank & Dorf, *The Startup Owner's Manual* (2012)
- Customer Development: customer discovery → customer validation → customer creation → company building. The first two are a search loop with explicit **pivot or proceed** decisions. [BOOK:Blank, Four Steps to the Epiphany, 2005, ch. 2]
- "There are no facts inside the building, so get outside" — hypotheses are only converted to facts by contact with customers. [BOOK:Blank & Dorf, Startup Owner's Manual, 2012, "Customer Development Manifesto"]
- A startup is a temporary organization **searching** for a repeatable and scalable business model (vs. executing a known one). [BOOK:Blank & Dorf, 2012]
- Customer discovery starts with writing down the business model hypotheses, then a problem test, then a solution test; earlyvangelists have the problem, know they have it, are actively looking, have cobbled a workaround, and have/can get budget. [BOOK:Blank, Four Steps, 2005, ch. 3]

### 8. Eric Ries — *The Lean Startup* (2011)
- **Value hypothesis** (does it deliver value) and **growth hypothesis** (how new customers discover it) are the two leap-of-faith assumptions. [BOOK:Ries, The Lean Startup, 2011, ch. 5]
- Build-Measure-Learn; plan in reverse (decide what to learn → what to measure → what to build). [BOOK:Ries, 2011, ch. 7]
- **MVP** = the version that enables a full turn of the loop with minimum effort; validated learning over vanity metrics; actionable/accessible/auditable metrics. [BOOK:Ries, 2011, ch. 6-7]
- **Pivot or persevere** decision is scheduled, not ad hoc. [BOOK:Ries, 2011, ch. 8]

### 9. Alberto Savoia — *The Right It* (2019)
- Most new ideas fail in the market even when executed well ("Law of Market Failure") → validate "the right it" before "building it right". [BOOK:Savoia, The Right It, 2019, Part I]
- **Market Engagement Hypothesis → XYZ hypothesis** ("At least X% of Y will Z") → zoomed-in **xyz** hypotheses testable locally and quickly. [WEB:https://www.shortform.com/summary/the-right-it-summary-alberto-savoia] [WEB:https://www.linkedin.com/posts/albertosavoia_10-the-xyz-hypothesisten-minutes-that-activity-7008129136330207233-0cDA]
- **Data beats opinions; "Your Own DAta" (YODA)** — others' data (reports, analogs) is weaker than data you collected. **Skin in the game** (time, money, contact info, commitment) is the credible signal. [WEB:https://www.buildtherightit.com/] [BOOK:Savoia, The Right It, 2019, Part II]
- Pretotype types: Mechanical Turk, Pinocchio, Fake Door, Facade, YouTube, One-Night Stand, Infiltrator, Relabel. [BOOK:Savoia, The Right It, 2019, ch. "Pretotyping Techniques"]
- Implication: XYZ is the ideal **machine-checkable hypothesis format** — every key belief in the handoff can be forced into "at least X% of Y will Z" with X, Y, Z non-empty.

### 10. Market sizing (TAM / SAM / SOM) & competitive analysis
- TAM = total demand for the category; SAM = portion reachable with your business model/channels/geography; SOM = share realistically capturable in the planning horizon. [BOOK:Blank & Dorf, Startup Owner's Manual, 2012, "Market Size" hypothesis] 
- **Bottom-up (number of target customers × reachable × price × frequency) is preferred over top-down (% of an analyst-report market)**; top-down figures are routinely inflated and unfalsifiable. [UNVERIFIED — common VC guidance; consistent with Savoia's YODA principle]
- Competitive analysis must include **non-consumption and workarounds** (spreadsheets, email, "do nothing"), not only named competitors; JTBD redefines competition as anything hired for the same job. [BOOK:Christensen et al., Competing Against Luck, 2016] [BOOK:Maurya, Running Lean, 2012 — "Existing alternatives" box]
- Porter's Five Forces for industry structure (rivalry, threat of entrants, substitutes, buyer power, supplier power). [BOOK:Porter, Competitive Strategy, 1980, ch. 1]
- Positioning (April Dunford, *Obviously Awesome*, 2019): competitive alternatives → unique attributes → value → best-fit customers → market category. [BOOK:Dunford, Obviously Awesome, 2019] (bridges to GTM, which is out of scope — record as extension point.)

### 11. Problem framing — Kees Dorst, "How Might We"
- **Frame creation** (Dorst, *Frame Innovation*, 2015): instead of solving the stated problem, create new frames — viewpoints on the problem situation — through design abduction, where both the WHAT (thing) and the HOW (working principle) are unknown and only the desired VALUE is known; a frame proposes a HOW, which then guides the creation of a WHAT (corrected: earlier wording implied HOW was given). [WEB:https://oxd.com/insights/how-frame-creation-can-inspire-innovation/] [WEB:https://www.penguinrandomhouse.com/books/657088/frame-innovation-by-kees-dorst/] [BOOK:Dorst, Frame Innovation, 2015, ch. 3-4 (nine-step frame creation model: archaeology, paradox, context, field, themes, frames, futures, transformation, integration)]
- Implication: the discovery stage should **generate multiple alternative frames** before converging; a single frame copied from the user's idea is the main failure mode.
- **"How might we…"** questions open a problem for ideation: not too broad, not too narrow, no embedded solution. Origin: invitation stems in Sid Parnes's creative-problem-solving work (1960s), carried into industry by Min Basadur at Procter & Gamble in the early 1970s, later adopted by IDEO and the d.school [WEB:https://www.basadur.com/the-origin-of-how-might-we/] [WEB:https://hbr.org/2012/09/the-secret-phrase-top-innovato]; used in the Monday "Map" step of a design sprint [BOOK:Knapp, Zeratsky & Kowitz, Sprint, 2016].
- Wedell-Wedellsborg (*What's Your Problem?*, 2020): reframing loop — frame, look outside the frame, rethink the goal, examine bright spots, look in the mirror, take their perspective, move forward. [BOOK:Wedell-Wedellsborg, What's Your Problem?, 2020]

### 12. Pre-mortem / devil's advocate
- Klein's **pre-mortem**: assume the project has already failed and ask what *did* go wrong (prospective hindsight); research cited by Klein suggests prospective hindsight raised the ability to correctly identify reasons for future outcomes by ~30%. [WEB:https://nesslabs.com/pre-mortem-anticipate-failure-with-prospective-hindsight] [BOOK:Klein, "Performing a Project Premortem", HBR, Sept 2007]
- Torres uses pre-mortems as one of the assumption-surfacing techniques. [BOOK:Torres, CDH, 2021, ch. 9]
- Kahneman: pre-mortem counters overconfidence and groupthink once a team has converged. [BOOK:Kahneman, Thinking, Fast and Slow, 2011, ch. 24]

### 13. Synthetic evidence (LLM-simulated users)
- NN/g (Rosala & Moran, 2024) compared a synthetic-users platform against three real studies: synthetic responses were shallow, sycophantic, consistently favorable, and predicted idealized behaviour (e.g., claimed to complete courses real users abandoned); recommendation: user research needs real users; synthetic output may help with desk-research-like tasks, hypothesis generation, or interview-guide piloting. [WEB:https://www.nngroup.com/articles/synthetic-users/] (via search summary; direct fetch blocked; authors Maria Rosala & Kate Moran, published June 2024; the three-study comparison and the course-completion example were confirmed in search summaries) [UNVERIFIED: the second URL nngroup.com/articles/ai-simulations-studies/ did not surface in verification searches]
- Implication: in our pipeline, synthetic "interviews" violate Mom Test rule 2 by construction (they are hypothetical by nature) — they may *generate* assumptions and interview guides, never *validate* them.

---

## Real-world roles

Stage legend: D = discovery, P = prd, A = architecture, T = tasks, S = shared pool.

### R1. Product Manager / Discovery Lead (→ discovery-orchestrator)
- **Titles**: Product Manager, Senior/Group PM, Product Lead, Head of Product Discovery, Product Owner (in SAFe/Scrum contexts, narrower). Stage: **D (orchestrator)**, consulted in P.
- **Mission**: Decide whether a problem is worth solving for a defined customer and the business, and reduce value and viability risk to an explicit, documented level before a PRD is commissioned.
- **Mindset & principles**: owns outcomes not output [BOOK:Cagan & Jones, Empowered, 2020]; problem before solution, "fall in love with the problem" [BOOK:Maurya, Running Lean 3rd ed., 2022]; most ideas fail [BOOK:Cagan, Inspired, 2017]; data beats opinions [BOOK:Savoia, 2019]; decide pivot/persevere/kill on pre-agreed criteria [BOOK:Ries, 2011].
- **OWNS**: target outcome definition; problem statement; segment choice; four-risk register (value + viability primary); go/no-go recommendation; consolidation of worker outputs; the discovery handoff.
- **DOES NOT OWN**: requirements detail (PRD stage), UX solution detail, technical design, pricing execution, GTM/messaging (out of scope), final business sign-off (human sponsor).
- **Inputs**: idea brief (problem hypothesis, target user, business context, constraints, any existing evidence: interviews, tickets, analytics, sales notes); strategic objective/OKR; budget/time box; known non-goals.
- **Outputs**: *Discovery brief / Opportunity assessment* — Cagan's 10 questions variant: what problem, for whom, how big, competitive landscape, why us, why now, go-to-market (extension point), success metrics, critical factors, recommendation [BOOK:Cagan, Inspired 1st ed. 2008, "Assessing Product Opportunities"] (note: the 10-question list is from the 1st edition; the 2nd edition's ch. 35 "Opportunity Assessment Technique" reduces it to four questions — objective, key results, customer problem, target market); OST; Lean Canvas; risk/assumption register; decision log.
- **ACCEPTANCE**:
  - [ ] Exactly one primary outcome metric with baseline (or "unknown — to measure") and target direction.
  - [ ] Problem statement names segment + circumstance + current workaround + cost of the problem; contains no solution words.
  - [ ] Every one of the four risks (plus Torres's ethical) has ≥1 assumption listed with status and evidence grade.
  - [ ] ≥3 alternative solution directions considered for the target opportunity, with reason the chosen one leads.
  - [ ] Recommendation is one of {proceed, proceed-with-conditions, pivot, kill} with explicit kill/pivot criteria.
  - [ ] Non-goals listed; open questions listed with owner.
- **REFUSAL**:
  - *blocked*: no identifiable target user/segment; no business objective or success notion; idea brief is a feature list without a stated problem and the user refuses/cannot answer clarifying questions; no human decision-maker named for go/no-go.
  - *rejected* (returns to worker or upstream): worker output asserting validation from synthetic or opinion-only evidence; market size given only as top-down analyst number; OST where opportunities are solutions in disguise.
  - *out_of_scope*: writing requirements/user stories, choosing tech stack, pricing page copy, launch/messaging plan (GTM extension point), committing delivery dates.
- **Anti-patterns**: "feature factory" — validating the solution the stakeholder already decided [BOOK:Cagan & Jones, Empowered, 2020]; confirmation bias; treating stakeholder requests as validated needs; endless discovery with no decision; skipping viability (legal/cost).
- **Handoffs**: receives from human sponsor (idea brief) and from all discovery workers; delivers discovery handoff to PRD orchestrator; invokes shared pool (privacy/compliance for viability, analytics for metric definition) and traceability owner (assigns IDs to problems/opportunities/assumptions).

### R2. UX Researcher (user research)
- **Titles**: UX Researcher, User Researcher, Design Researcher, Research Ops (supporting). Stage: **D**, consulted in P (usability acceptance) and later evaluation.
- **Mission**: Produce trustworthy, behaviour-based understanding of users' needs, contexts and current practices, with explicit evidence quality, so decisions rest on what people do rather than what they say.
- **Mindset & principles**: past behaviour over future intent (Mom Test rules 1-2) [WEB:https://hatrabbits.com/en/the-mom-test/]; story-based interviewing [WEB:https://www.shortform.com/blog/teresa-torres-customer-interviews/]; separate observation from interpretation; triangulate (qual + quant + secondary); sample for the decision, saturation not statistical significance in qual [BOOK:Portigal, Interviewing Users, 2nd ed. 2023]; research ethics/consent.
- **OWNS**: research plan (questions, method, participants/screeners), interview guides, synthesis (affinity map, interview snapshots), opportunity candidates, evidence grading, persona/JTBD-based segments.
- **DOES NOT OWN**: the product decision; solution design; market sizing; statistical analytics (shares with insights analyst).
- **Inputs**: research questions tied to decisions; target segment hypotheses; any raw data (transcripts, support tickets, reviews, session recordings); constraints (time, access).
- **Outputs**: research plan (objective, decisions it informs, method, sample, screener, guide); interview snapshots [WEB:https://andrewclark.co.uk/product-book-summaries/continuous-discovery-habits]; synthesis report: insights each stated as "observation → interpretation → implication" with source count; experience map / journey map; assumption-to-test list; in an agentic pipeline, a **research-ready interview guide** for humans to run.
- **ACCEPTANCE**:
  - [ ] Each insight cites ≥1 traceable source (transcript ID, ticket ID, URL) and states n (how many sources support it).
  - [ ] Insights are behaviours/needs, not feature requests; feature requests are reported separately with underlying motivation.
  - [ ] Every evidence item labelled {real-primary, real-secondary, synthetic, assumption}.
  - [ ] Interview guide contains no leading or future-hypothetical questions ("would you…") as primary probes.
  - [ ] Contradicting evidence is reported, not dropped.
- **REFUSAL**:
  - *blocked*: no research question linked to a decision; no access to any real data and the orchestrator asks for "validation".
  - *rejected*: requests to "confirm users want X" (leading); synthetic personas presented as research findings; insights without sources.
  - *out_of_scope*: designing the solution UI; statistical claims of prevalence from n<~10 qualitative data; recruiting real participants (a human action — the agent can only draft the plan).
- **Anti-patterns**: persona fiction (demographic personas without behaviour) [BOOK:Christensen et al., Competing Against Luck, 2016]; asking users for solutions; synthesis by cherry-picked quotes; NN/g-documented sycophancy of synthetic users [WEB:https://www.nngroup.com/articles/synthetic-users/].
- **Handoffs**: receives research questions from PM/orchestrator; delivers snapshots/opportunities to PM (OST) and designer; receives quant signals from insights analyst for triangulation.

### R3. Market & Competitive Analyst (market/competitive intelligence)
- **Titles**: Market Research Analyst, Competitive Intelligence Analyst, Strategy Analyst, Product Marketing (CI function — note PMM is out of scope, only the CI analysis piece is kept). Stage: **D**.
- **Mission**: Quantify the size and accessibility of the opportunity and map the alternatives customers currently hire, so the team knows whether the prize is worth it and where it can differentiate.
- **Mindset & principles**: bottom-up over top-down sizing [UNVERIFIED as a universal rule; widely used]; competition = any alternative for the job incl. non-consumption [BOOK:Christensen et al., 2016]; YODA — own data beats others' data [WEB:https://www.buildtherightit.com/]; cite sources with dates; distinguish fact, estimate, and assumption.
- **OWNS**: TAM/SAM/SOM model with formula and inputs; competitor/alternative landscape; feature/positioning comparison; Five Forces snapshot; "why now" market trends.
- **DOES NOT OWN**: pricing decision; positioning/messaging (PMM, extension point); solution direction.
- **Inputs**: segment definition, geography, business model hypothesis (who pays, how), time horizon; access to web/desk sources.
- **Outputs**: market sizing sheet (each input with source/date/confidence; formula shown; sensitivity range low/base/high); competitive matrix (alternatives × jobs/outcomes served × pricing × strengths/weaknesses × switching cost); Five Forces summary; trend memo.
- **ACCEPTANCE**:
  - [ ] Bottom-up calculation present: #customers × adoption/reach × price × frequency, each term sourced or flagged as assumption.
  - [ ] TAM ⊇ SAM ⊇ SOM numerically consistent; SOM has a time horizon and a rationale (channel capacity, comparable ramp).
  - [ ] Ranges, not point estimates, with the single most sensitive input identified.
  - [ ] Landscape includes ≥1 non-consumption/workaround alternative and direct + indirect competitors.
  - [ ] Every external figure has a source URL/publication and year; figures older than ~3 years flagged.
- **REFUSAL**:
  - *blocked*: no segment or geography or business model → cannot size; no web/desk access and no supplied data.
  - *rejected*: "1% of a $50B market" style SOM; sources not citable; competitor claims taken from the competitor's marketing without verification label.
  - *out_of_scope*: pricing strategy decisions, launch plans, sales forecasts for budgeting.
- **Anti-patterns**: hallucinated statistics (critical for LLMs); "no competitors"; feature-checklist matrices that ignore jobs; stale reports.
- **Handoffs**: receives segment/model hypotheses from PM and strategist; delivers sizing + landscape to PM, strategist (viability), and PRD (context section).

### R4. Business Analyst / Business Strategist (viability)
- **Titles**: Business Analyst, Strategy & Operations, Product Strategist, Business Architect, Corporate Development (in incumbents), Venture Architect. Stage: **D** (viability, business model), **P** (BA also elicits requirements — the PRD-stage BA is a separate persona).
- **Mission**: Test whether the opportunity works for the business — model, unit economics, constraints, stakeholder and strategic fit — and make the viability assumptions explicit and falsifiable.
- **Mindset & principles**: viability is a first-class risk (sales channel, legal, cost to acquire, monetization, brand) [WEB:https://www.svpg.com/four-big-risks/]; canvas as hypothesis map, riskiest box first [BOOK:Maurya, 2012]; strategy = diagnosis + guiding policy + coherent actions [BOOK:Rumelt, Good Strategy Bad Strategy, 2011, ch. 5]; BABOK's needs/stakeholder/change thinking [BOOK:IIBA, BABOK Guide v3, 2015, "Strategy Analysis"].
- **OWNS**: Lean Canvas / Business Model Canvas; unit-economics sketch (CAC, LTV, gross margin — as assumptions); stakeholder map (power/interest); strategic-fit statement; constraint inventory (contractual, regulatory pointers handed to shared compliance).
- **DOES NOT OWN**: legal/compliance verdicts (shared pool); financial forecasts for the board; requirements elicitation (PRD stage).
- **Inputs**: company strategy/OKRs, business model, cost constraints, sizing from R3, stakeholder list.
- **Outputs**: Lean Canvas with risk ranking; viability assumptions in XYZ/test-card format; stakeholder map; "strategy kernel" (Rumelt) one-pager.
- **ACCEPTANCE**:
  - [ ] All 9 Lean Canvas boxes filled; each marked {evidence, assumption}; top-3 riskiest boxes ranked.
  - [ ] "Unfair advantage" is something not easily copied or bought, or explicitly "none yet".
  - [ ] Unit economics expressed as formula + assumption values + break-even condition.
  - [ ] Strategic fit links to a named company objective.
  - [ ] Regulatory/contractual flags routed to shared privacy/compliance with IDs.
- **REFUSAL**:
  - *blocked*: no business model intent at all (who pays?) and no stated non-commercial objective (internal tool → then measure via cost/time saved).
  - *rejected*: revenue projections without driver assumptions; "fluff" goals ("become the leader").
  - *out_of_scope*: legal opinion, investment approval, GTM plan, pricing experiments execution.
- **Anti-patterns**: Rumelt's "bad strategy" — fluff, goals mistaken for strategy, not facing the challenge; spreadsheet precision on fiction.
- **Handoffs**: receives from PM, R3; sends to PM; calls shared compliance and FinOps (for run-cost assumptions of the solution later) and analytics.

### R5. Product Designer (discovery)
- **Titles**: Product Designer, UX Designer, Service Designer, Design Lead. Stage: **D** (framing, concepts, usability risk), **P** (flows), consulted in A.
- **Mission**: Reframe the problem, generate divergent solution concepts and prototypes cheap enough to test value and usability risk before anything is specified.
- **Mindset & principles**: frame creation — multiple frames before solutions [WEB:https://oxd.com/insights/how-frame-creation-can-inspire-innovation/]; diverge then converge (Double Diamond) [WEB:https://www.designcouncil.org.uk/resources/the-double-diamond/history-of-the-double-diamond/] (Design Council, developed 2004 and popularised from 2005; sources differ between 2004 and 2005); compare-and-contrast ≥3 solutions [BOOK:Torres, CDH, 2021]; prototype fidelity matched to the question [BOOK:Cagan, Inspired, 2017, "Prototype Techniques"]; owns usability risk [WEB:https://www.svpg.com/four-big-risks/].
- **OWNS**: HMW questions; alternative frames; concept sketches/storyboards; story map of the core flow; prototype/pretotype specs; usability-risk assumptions.
- **DOES NOT OWN**: final requirements; visual design system; accessibility conformance verdict (shared pool), feasibility verdict.
- **Inputs**: opportunity (from OST), research insights, constraints, brand/design principles.
- **Outputs**: HMW set; frame alternatives (Dorst: WHAT + HOW → VALUE); 3+ concept briefs; user story map; prototype/pretotype test plan with success criteria; journey / service blueprint (current and future state).
- **ACCEPTANCE**:
  - [ ] ≥3 HMW statements, none containing a solution, each traceable to an opportunity ID.
  - [ ] ≥3 materially different concepts (not variations of one UI) with the assumption each one relies on.
  - [ ] Each prototype/pretotype has a question it answers, a fidelity justification and a pass/fail threshold.
  - [ ] Accessibility considerations flagged early (handed to shared a11y).
- **REFUSAL**:
  - *blocked*: no opportunity/problem defined (asked to "make screens for the idea").
  - *rejected*: a single concept handed down as "the solution" without alternatives; HMW that is a disguised feature.
  - *out_of_scope*: pixel-perfect UI, design system, front-end build, production copy.
- **Anti-patterns**: solutionizing early; fidelity too high too early; designing for the stakeholder; "Dribbble" concepts with no testable assumption.
- **Handoffs**: receives opportunities from PM/UXR; delivers concepts and test plans to PM; usability findings to PRD (UX requirements).

### R6. Data / Insights Analyst (product analytics in discovery)
- **Titles**: Product Analyst, Data Analyst, Insights Analyst, Decision Scientist. Stage: **D** (baseline, sizing of the problem in existing data), **S** (product analytics shared pool owns instrumentation later).
- **Mission**: Quantify how often and how badly the problem occurs using existing behavioural data, set baselines for the outcome metric, and design measurable success/kill criteria.
- **Mindset & principles**: actionable vs vanity metrics [BOOK:Ries, 2011, ch. 7]; one metric that matters per stage [BOOK:Croll & Yoskovitz, Lean Analytics, 2013, ch. 6 "The Discipline of One Metric That Matters"] (corrected from ch. 2) [WEB:https://www.blinkist.com/magazine/posts/the-lean-analytics-discipline-of-one-metric-that-matters]; North Star / input metrics tree [UNVERIFIED — Amplitude North Star playbook]; pre-register thresholds; beware Simpson's paradox and survivorship bias.
- **OWNS**: metric definitions (formula, unit, population, window), baselines, problem prevalence from data, success/kill thresholds, experiment sizing (sample/MDE) when tests are run.
- **DOES NOT OWN**: instrumentation implementation (shared analytics/tasks stage), research synthesis, product decision.
- **Inputs**: data access or exports; outcome hypothesis; segments.
- **Outputs**: metric spec (name, definition, formula, source, owner, baseline, target, guardrails); prevalence analysis; metric tree; experiment design (hypothesis, primary metric, MDE, duration).
- **ACCEPTANCE**:
  - [ ] Every metric has formula, population, time window and data source; baseline value or explicit "no data — instrumentation needed".
  - [ ] At least one guardrail metric for the outcome.
  - [ ] Thresholds stated before any test result is seen.
  - [ ] Numbers reproducible (query or calculation included).
- **REFUSAL**:
  - *blocked*: no data source and asked for baselines → returns "unknown" with instrumentation requirement, does not fabricate.
  - *rejected*: vanity metrics (page views, sign-ups) as the success criterion; post-hoc thresholds.
  - *out_of_scope*: building dashboards/pipelines; causal claims from correlational data.
- **Anti-patterns**: invented numbers; precision theater; metric with no decision attached.
- **Handoffs**: from PM (outcome), UXR (hypotheses to quantify); to PM, PRD (success metrics section), shared product-analytics (instrumentation needs).

### R7. Domain Subject-Matter Expert (SME)
- **Titles**: Domain Expert, Clinical/Legal/Financial SME, Industry Advisor, Solutions Consultant, Customer Success lead (as proxy). Stage: **D** primarily; consulted in **P** and **A** (domain rules).
- **Mission**: Supply domain truth — regulations, workflows, terminology, edge cases, incumbent practices — and challenge naive assumptions about how the domain works.
- **Mindset & principles**: ubiquitous language [BOOK:Evans, Domain-Driven Design, 2003, ch. 2]; distinguish "how it is done" from "how it should be"; cite authoritative sources (standards, regulations).
- **OWNS**: domain glossary; current-state workflow description; domain constraints and edge-case catalogue; reality check on assumptions.
- **DOES NOT OWN**: product decisions; compliance sign-off (shared pool); user preference claims (research).
- **Inputs**: the problem statement, segment, jurisdiction, assumptions list.
- **Outputs**: glossary (term, definition, synonyms, source); domain constraint list; "assumption challenges" (assumption ID → domain counter-evidence).
- **ACCEPTANCE**:
  - [ ] Each constraint cites a source (regulation article, standard, documented practice) or is labelled expert judgement/[assumption].
  - [ ] Glossary covers every domain noun used in problem statement and OST.
  - [ ] Jurisdiction/version of rules stated.
- **REFUSAL**:
  - *blocked*: domain or jurisdiction unspecified when rules depend on it.
  - *rejected*: domain claims from the brief contradicted by authoritative source.
  - *out_of_scope*: legal advice/certification, medical decisions; anything requiring licensed professional sign-off → escalate to human.
- **Anti-patterns**: "curse of knowledge" (jargon, assuming current practice is the only way); LLM failure: confident plausible-but-wrong regulation citations.
- **Handoffs**: from PM; to PM, UXR (workflow context), shared compliance, PRD (glossary/business rules).

### R8. Devil's Advocate / Pre-mortem facilitator / Red team (→ discovery stage critic)
- **Titles**: no single title — performed by an Investment/Stage-gate committee, Product Council, "red team", Principal PM or Bar-raiser, or an independent reviewer. Stage: **D exit gate** (and analogous critics in other stages).
- **Mission**: Try to kill the opportunity on paper before money is spent; expose untested leaps of faith, bias, and weak evidence.
- **Mindset & principles**: prospective hindsight — "it has failed; why?" [WEB:https://nesslabs.com/pre-mortem-anticipate-failure-with-prospective-hindsight]; never auto-agree, look for what's missing/assumed/over-asserted (local plan-critic "skepticism safeguard") [local: dev/research/2026-04-25-harness-engineering-research.md §11]; use a different model family for critique to avoid shared blind spots [local: ai/docs/harness-engineering/harness-engineering.md, cited at research doc §11]; evidence hierarchy say < do < pay [BOOK:Bland & Osterwalder, Testing Business Ideas, 2019].
- **OWNS**: pre-mortem failure list; challenge register; verdict PROCEED / REVISE / KILL-RECOMMEND with reasons; evidence-grade audit.
- **DOES NOT OWN**: fixing the artifacts; the final decision (human sponsor + PM).
- **Inputs**: the full consolidated discovery package.
- **Outputs**: pre-mortem (failure stories → causes → mapped to assumption IDs → mitigation/test); critique with severity.
- **ACCEPTANCE** (of its own output):
  - [ ] ≥1 failure scenario per risk category (value, usability, feasibility, viability, ethical).
  - [ ] Each challenge references a specific artifact ID/line, not general skepticism.
  - [ ] Verdict follows declared rules (e.g., any untested leap-of-faith with "assumed" status on value → REVISE or proceed-with-conditions).
- **REFUSAL**:
  - *blocked*: package incomplete (missing risk register/OST) — cannot review.
  - *rejected*: package claiming "validated" on synthetic/opinion evidence.
  - *out_of_scope*: proposing alternative product strategy as replacement (it may note it; the PM owns it).
- **Anti-patterns**: performative negativity; nitpicking format over substance; LLM rubber-stamping (same model, same context = same blind spots).
- **Handoffs**: from discovery orchestrator (exit gate); verdict back to orchestrator; summary goes into handoff.

### (Mentioned, merged) Tech lead in discovery — feasibility risk
- Cagan puts the tech lead in the trio for feasibility [WEB:https://www.svpg.com/four-big-risks/]. In this pipeline, deep feasibility belongs to Architecture, but discovery needs a **quick feasibility spike/sanity check** ("is this known-hard? AI/ML uncertainty? dependency on third-party APIs?"). Recommend: a light worker or a task given to the PM with a mandatory "feasibility flags" list handed to the architecture stage, not a full persona.

---

## Implications for agentic personas

### A. Evidence is the core problem — make it a typed field, not prose
1. There are no real users in the loop. Every evidence item in the discovery handoff must carry `evidence_type ∈ {real_primary, real_secondary, desk_research, synthetic, assumption}` and `strength ∈ {say, do, pay/commit}` (Bland & Osterwalder hierarchy; Mom Test commitment; Savoia skin-in-the-game).
2. **Hard rule**: `synthetic` evidence may *generate* hypotheses, interview guides, objection lists and pretotype ideas; it may **never** move an assumption to `validated`. Status vocabulary: `assumed | supported_by_desk | supported_by_real | refuted | untested`. "Validated" requires `real_*` with `do` or `pay` strength. Grounding: NN/g found synthetic users sycophantic and idealized [WEB:https://www.nngroup.com/articles/synthetic-users/]; Mom Test rule 2 forbids hypothetical-future data.
3. Desk research (web) is legitimate secondary evidence but is subject to hallucination: every desk claim needs URL + access date; the orchestrator should spot-check a sample (e.g., re-fetch 20%) at the exit gate.
4. When the human supplies real artifacts (transcripts, tickets, analytics exports), workers should prefer them and cite file+line. The entry gate should explicitly ask: "Do you have any real customer evidence? (interviews, tickets, reviews, data)".
5. Output a **"Validation plan for humans"**: the discovery stage cannot run interviews, so its honest deliverable for untested leaps of faith is an executable test plan (Torres test card / Savoia xyz hypothesis / Mom Test interview guide) that humans can run, plus a re-entry path into the pipeline with results.

### B. What an LLM tends to get wrong here
- **Solution anchoring**: the idea arrives as a solution; the LLM rationalizes it. Gate: problem statement must pass a "no solution words" check; OST must contain ≥3 solutions per target opportunity; designer must produce ≥2 alternative frames.
- **Sycophancy toward the user's idea** — same failure as synthetic users. Counter: a separate pre-mortem critic with a skepticism clause, ideally different model or at least fresh context.
- **Fabricated numbers** (market sizes, percentages, competitor facts). Counter: no number without source or explicit `[assumption]` tag; bottom-up formula shown; ranges.
- **Fluff outputs** — generic personas, "users want an easy-to-use solution". Counter: Mom Test linter on all evidence statements (reject "would/might/usually", compliments, generic adjectives); pains must be concrete (Osterwalder).
- **Opportunities that are solutions in disguise** (Torres) and **HMW with embedded solutions** — linter: if only one solution can address it, flag.
- **Mixing JTBD schools** (Christensen narrative jobs vs Ulwick outcome statements vs Moesta forces) — specify one canonical format per artifact: job statement (verb + object + context), outcome statements in ODI grammar, four-forces table for switching.
- **Fake quantitative rigor** (ODI opportunity scores without survey data). Label as "estimated importance/satisfaction (no survey)" or omit.
- **Never concluding** (endless exploration) or **always concluding "proceed"**. Recommendation enum + pre-declared kill criteria.

### C. Split / merge recommendations (subagents cannot spawn subagents; orchestrator = PM)
- **discovery-orchestrator** = PM/Discovery Lead (R1). Owns framing, consolidation, the risk register, and the handoff. Should *not* do the research itself (context protection).
- Workers (each a single-job subagent with read-only + web tools where needed):
  1. `problem-framer` = product designer (framing half of R5) + Dorst/HMW + JTBD job statement. Runs early.
  2. `user-research-synthesizer` = UXR (R2): synthesizes *supplied real evidence* + desk evidence (reviews, forums) into snapshots/opportunities; drafts the human interview guide. Must be the only worker allowed to write `opportunity` nodes from evidence.
  3. `market-competitive-analyst` = R3 (web-heavy; give it the source-citation contract).
  4. `business-viability-analyst` = R4 (Lean Canvas, unit economics, stakeholder map); calls on shared compliance via orchestrator rather than directly.
  5. `metrics-analyst` = R6 (outcome metric spec, baselines or "unknown", kill thresholds). Could merge into R4 for small runs; keep separate when data exists.
  6. `domain-sme` = R7, instantiated per domain (parametrized), optional — invoke only when domain is regulated/specialized.
  7. `solution-concepts-designer` = concept half of R5 (≥3 concepts + pretotype plans). Merge with problem-framer if budget is tight, but run as a **second pass after research**, never before.
  8. `discovery-critic` = R8, runs at EXIT gate in a clean context with only the package; outputs PROCEED/REVISE/KILL-RECOMMEND. Do not give it the orchestrator's reasoning — only artifacts.
- Feasibility: no separate persona; a "feasibility flags" checklist inside the orchestrator or problem-framer, forwarded to Architecture.
- Shared pool calls from discovery: privacy/compliance (viability: data/regulatory red flags), product analytics (metric definitions), accessibility (only to flag excluded users early), FinOps (only if solution run-cost is a viability driver, e.g., LLM inference cost). Traceability owner assigns IDs: `OUT-`, `OPP-`, `SOL-`, `ASM-`, `EVD-`, `RSK-`.

### D. Hard gates
**ENTRY gate (blocked if any fail):**
- Idea brief states a problem (not only a feature) OR the user answers the clarifying round; a target segment hypothesis; a business objective or reason to exist; a named human decision owner; time box.
- If the user provides no real evidence, proceed but set the run mode `evidence_mode: desk+synthetic-only`, which caps every value assumption at `supported_by_desk` and forces recommendation ≤ `proceed-with-conditions`.

**EXIT gate (stage critic + checklist; rejected if any fail):**
- One outcome metric with definition; problem statement free of solution words; ≥3 opportunities, ≥3 solution directions for the target opportunity.
- Assumption register covers 5 categories (value/desirability, usability, feasibility, viability, ethical), each with `evidence_type`, `strength`, `status`, and a test card or xyz hypothesis for each leap of faith.
- No assumption with `status=validated` whose evidence is synthetic/opinion-only.
- Every number has source or `[assumption]`; TAM⊇SAM⊇SOM and bottom-up present (or explicitly N/A for internal tools, replaced by cost-of-problem estimate).
- Competitive landscape includes non-consumption/workarounds.
- Pre-mortem done by separate critic; all "high" challenges resolved or carried as open risks.
- Recommendation enum + kill criteria + open questions with owners + non-goals.
- Traceability IDs present for all items the PRD will reference.

### E. Handoff shape (discovery → PRD)
A machine-readable `discovery-handoff.md` (frontmatter: stage, version, verdict, evidence_mode, open_blockers) with sections: Outcome; Problem statement & frame; Segment & JTBD (job statement + four forces); OST (outcome → opportunities → solutions → assumptions); Assumption & risk register (table); Market & alternatives summary; Viability (Lean Canvas); Metrics (spec + kill criteria); Domain glossary & constraints; Pre-mortem & critic verdict; Non-goals; Open questions; Human validation plan. The PRD entry gate should `reject` if verdict ≠ PROCEED/proceed-with-conditions, or if the register is missing.

### F. Refusal semantics specific to this stage
- `blocked`: idea with no problem/segment/objective after one clarifying round; regulated domain with no jurisdiction.
- `rejected`: upstream (human brief) claiming "users love it / validated" with no evidence → accept as hypothesis, never as fact (more precisely: not a rejection of the run, but a reclassification; record it).
- `out_of_scope`: requests for GTM/positioning/messaging/pricing pages (extension point), requirements, architecture, estimates.

---

## Sources

1. [WEB:https://www.svpg.com/four-big-risks/] — Cagan, "The Four Big Risks" (content via search summary; direct fetch blocked).
2. [WEB:https://roadmap.one/blog/posts/blog6-6-svpg-product-risks/] — secondary summary of the four risks.
3. [BOOK:Cagan, Inspired: How to Create Tech Products Customers Love, 2nd ed., 2017]
4. [BOOK:Cagan & Jones, Empowered, 2020]
5. [BOOK:Cagan, Transformed, 2024]
6. [BOOK:Torres, Continuous Discovery Habits, 2021]
7. [WEB:https://www.producttalk.org/2021/04/no-single-right-way-3/] — five assumption types (via search summary).
8. [WEB:https://www.chameleon.io/blog/opportunity-solution-tree] — OST structure.
9. [WEB:https://maze.co/blog/making-better-product-decisions-with-teresa-torres/] — continuous discovery definition.
10. [WEB:https://www.shortform.com/blog/teresa-torres-customer-interviews/] — story-based interviewing.
11. [WEB:https://andrewclark.co.uk/product-book-summaries/continuous-discovery-habits] — interview snapshot.
12. [BOOK:Fitzpatrick, The Mom Test, 2013]
13. [WEB:https://www.lesswrong.com/posts/fuktKYSvzFMTfPpeT/the-mom-test-summary-and-thoughts] — Mom Test rules.
14. [WEB:https://hatrabbits.com/en/the-mom-test/] — Mom Test rules.
15. [BOOK:Christensen, Hall, Dillon & Duncan, Competing Against Luck, 2016]
16. [BOOK:Ulwick, Jobs to be Done: Theory to Practice, 2016; What Customers Want, 2005]
17. [WEB:https://en.wikipedia.org/wiki/Outcome-Driven_Innovation] — ODI outcome statement grammar.
18. [WEB:https://strategyn.com/jobs-to-be-done-template/] — Strategyn JTBD template.
19. [WEB:https://bradenbuchanan.substack.com/p/outcome-driven-innovation-a-critique] — opportunity score formula and critique.
20. [BOOK:Moesta & Engle, Demand-Side Sales 101, 2020]
21. [WEB:https://jobstobedone.org/radio/unpacking-the-progress-making-forces-diagram/] — four forces.
22. [WEB:https://elementalconcept.com/insights/moesta-four-forces-of-progress-jtbd/] — four forces / switch timeline.
23. [BOOK:Maurya, Running Lean, 2nd ed. 2012; 3rd ed. 2022]
24. [BOOK:Osterwalder, Pigneur, Bernarda & Smith, Value Proposition Design, 2014]
25. [BOOK:Bland & Osterwalder, Testing Business Ideas, 2019]
26. [BOOK:Blank, The Four Steps to the Epiphany, 2005; Blank & Dorf, The Startup Owner's Manual, 2012]
27. [BOOK:Ries, The Lean Startup, 2011]
28. [BOOK:Savoia, The Right It, 2019]
29. [WEB:https://www.shortform.com/summary/the-right-it-summary-alberto-savoia] — MEH / XYZ hypothesis.
30. [WEB:https://www.linkedin.com/posts/albertosavoia_10-the-xyz-hypothesisten-minutes-that-activity-7008129136330207233-0cDA] — Savoia on XYZ hypothesis.
31. [WEB:https://www.buildtherightit.com/] — Savoia site (YODA, skin in the game).
32. [BOOK:Porter, Competitive Strategy, 1980]
33. [BOOK:Dunford, Obviously Awesome, 2019]
34. [BOOK:Dorst, Frame Innovation: Create New Thinking by Design, MIT Press, 2015]
35. [WEB:https://oxd.com/insights/how-frame-creation-can-inspire-innovation/] — frame creation.
36. [WEB:https://www.penguinrandomhouse.com/books/657088/frame-innovation-by-kees-dorst/] — publisher page.
37. [BOOK:Wedell-Wedellsborg, What's Your Problem?, 2020]
38. [BOOK:Knapp, Zeratsky & Kowitz, Sprint, 2016]
39. [BOOK:Klein, "Performing a Project Premortem", Harvard Business Review, Sept 2007]
40. [WEB:https://nesslabs.com/pre-mortem-anticipate-failure-with-prospective-hindsight] — pre-mortem, prospective hindsight.
41. [BOOK:Kahneman, Thinking, Fast and Slow, 2011]
42. [WEB:https://www.nngroup.com/articles/synthetic-users/] — NN/g synthetic users (via search summary; direct fetch blocked).
43. [WEB:https://www.nngroup.com/articles/ai-simulations-studies/] — NN/g AI simulation studies.
44. [BOOK:Rumelt, Good Strategy Bad Strategy, 2011]
45. [BOOK:IIBA, A Guide to the Business Analysis Body of Knowledge (BABOK Guide) v3, 2015]
46. [BOOK:Croll & Yoskovitz, Lean Analytics, 2013]
47. [BOOK:Portigal, Interviewing Users, 2nd ed., 2023]
48. [BOOK:Evans, Domain-Driven Design, 2003]
49. Local: /home/user/ai-study-library/dev/research/2026-04-25-harness-engineering-research.md (§11 Critic/Review patterns: plan-critic skepticism safeguard; cross-model review).
50. Local: /home/user/ai-study-library/ai/docs/spec-driven-development/spec-driven-development-variant.md (Spec Kit checklists as per-step "definition of done").

---

## Verification log

Verifier pass, 2026-10-02. Scope: citations and attributed claims only. No new research was added. Web checks were done through search summaries, because svpg.com, nngroup.com and several publisher sites block direct fetches.

**Checked and confirmed online**
- Inspired 2nd ed. structure: Product Discovery is in Part IV "The Right Process" (ch. 33 "Principles of Product Discovery", ch. 35 "Opportunity Assessment Technique") (oreilly.com TOC).
- Mom Test chapter list: ch. 2 Avoiding Bad Data, ch. 3 Asking Important Questions, ch. 4 Keeping It Casual, ch. 5 Commitment and Advancement.
- Running Lean 3rd ed. (2022) contains Customer Factory, Innovator's Bias and Fermi estimate.
- Lean Analytics: OMTM is ch. 6.
- NN/g "Synthetic Users" article by Rosala and Moran (June 2024): it compares synthetic users against three real studies, the synthetic users over-claim course completion, and it recommends using them for hypotheses and desk research only.
- HMW origin: Parnes, then Basadur at P&G, then IDEO (basadur.com, HBR 2012).
- Double Diamond: Design Council, 2004–2005.
- Torres success-criteria example ("at least 4 out of 10").
- Local corpus: harness research §11 (plan-critic Skepticism Safeguard, PROCEED|REVISE, cross-model review citing harness-engineering.md:79-81) confirmed. Note: the example in harness-engineering.md:81 uses two models from the same family, which weakens its own "different family" point.

**Corrected**
- Inspired part attribution for discovery: Part III "The Right Product" → Part IV "The Right Process".
- Mom Test "scary questions / 3 things to learn": ch. 4 → ch. 3.
- Lean Analytics OMTM: ch. 2 → ch. 6.
- Torres success-criteria example: "7 of 10" (presented as a quote) → Torres's own illustration of the form "4 out of 10", explicitly labelled illustrative.
- Dorst design abduction: both WHAT and HOW are unknown, and only VALUE is known (the earlier wording implied HOW was given).
- HMW origin story: replaced "[UNVERIFIED] P&G/IDEO" with the sourced Parnes → Basadur/P&G → IDEO lineage.
- Cagan's 10-question opportunity assessment: noted as a 1st-edition (2008) item; the 2nd edition reduces it to 4 questions.
- Running Lean 3rd ed.: noted that the Customer Factory first appeared in *Scaling Lean* (2016).

**Downgraded / flagged**
- `nngroup.com/articles/ai-simulations-studies/`: the URL did not surface in verification searches, so it is now marked [UNVERIFIED]. The claims it supported are covered by the confirmed synthetic-users article.
- Bottom-up vs top-down sizing remains [UNVERIFIED] (correctly tagged).

**Spot-checked by knowledge (no change needed)**
- Years and authors confirmed for: Cagan four risks and owner split; Empowered 2020 (Cagan & Jones); Transformed 2024; CDH 2021 ch. 6/9/10 topics; Torres five assumption types; Mom Test 2013 and its three rules.
- JTBD sources confirmed: Competing Against Luck 2016 (four authors); Ulwick 2005/2016, job map steps and opportunity-score formula; Moesta & Engle 2020 (four forces).
- Strategy and lean sources confirmed: Value Proposition Design 2014 (four authors, three fits); Testing Business Ideas 2019 test-card wording; Blank 2005/2012 (earlyvangelist traits, "get outside the building"); Lean Startup 2011 ch. 5–8 topics; Savoia 2019 (Law of Market Failure, XYZ, YODA, pretotype names).
- Strategy, framing and decision sources confirmed: Porter 1980; Dunford 2019; Dorst 2015 nine-step model; Wedell-Wedellsborg 2020; Klein HBR Sept 2007 (~30% prospective hindsight); Kahneman 2011 ch. 24; Rumelt 2011 ch. 5 kernel; BABOK v3 2015.
- Research and domain sources confirmed: Portigal 2nd ed. 2023; Evans 2003 ch. 2.
