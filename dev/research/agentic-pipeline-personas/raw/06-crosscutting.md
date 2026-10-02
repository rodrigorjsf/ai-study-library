# Raw research — Cross-cutting quality: security, privacy, reliability, cost, analytics

> Scope: the shared reviewer pool that any stage orchestrator (discovery, prd, architecture, tasks) can call as a worker subagent. Every stage orchestrator runs in its own fresh session (`claude --agent <stage>-orchestrator`), so these reviewers are invoked once per stage, at different times, in different windows. Because of that, they never see each other's earlier output unless it is on disk. Each reviewer must therefore be **stage-aware** (it reviews a discovery brief differently from a task list) and **artifact-driven**: it reads the handoff files and writes a findings file. It keeps no memory between stages.
> GTM/PMM is out of scope. The traceability owner is defined in another axis. This file only states what each reviewer hands to it.
>
> Tagging: `[WEB:url]` means the claim was confirmed online in this session. Many primary sites (owasp.org, csrc.nist.gov, sre.google, linddun.org, threatmodelingmanifesto.org) were **blocked by the egress proxy**, so confirmation came from search-result pages and secondary publishers listed in Sources. `[BOOK:...]` covers well-known books and primary legal texts that were cited from knowledge. `[UNVERIFIED]` means the detail is plausible but was not checked.

---

## Literature & frameworks

### 1. OWASP ASVS (4.0.3 → 5.0)
- ASVS 5.0.0 was released in May 2025 at Global AppSec EU (Barcelona). It has 345 requirements in 17 chapters (V1 Encoding and Sanitization … V17 WebRTC) [WEB:https://owasp.github.io/www-project-application-security-verification-standard/ (search summary)]. The L1–L3 levels were rebalanced, OAuth/OIDC coverage was expanded, and direct CWE mappings were removed [WEB:https://softwaremill.com/whats-new-in-asvs-5-0/] [WEB:https://quality.arc42.org/standards/owasp-asvs].
- The levels give a ready-made **risk-tiering vocabulary** for the PRD stage. L1 is the baseline for any app that handles non-public data. L2 covers apps that process sensitive data. L3 is the highest assurance level and includes architecture review and threat modeling [WEB:https://www.securitycompass.com/blog/what-is-owasp-asvs/]. Persona implication: the security reviewer's first output in the PRD stage is a declared **target ASVS level with a reason for it**. It does not produce a list of controls.
- ASVS is a **verification standard**, so each requirement is written to be testable. This makes it the right source for security NFRs and acceptance criteria in the PRD and tasks stages. The OWASP Top 10 is an awareness document and should not serve as the requirements baseline [BOOK:OWASP ASVS 4.0.3 Preface/"How to use"; same guidance in 5.0] [UNVERIFIED for exact 5.0 wording].
- Requirement IDs (`v5.0.0-<chapter>.<section>.<req>`) are stable enough to cite in traceability. The traceability owner can link PRD NFRs to ASVS IDs and then to tasks [WEB:https://github.com/OWASP/ASVS (search summary confirms the `v<version>-` prefix convention)].
- 5.0 dropped the CWE mappings. A reviewer that wants CWE references must take them from other catalogs, and an LLM persona must not invent ASVS↔CWE pairs [WEB:https://softwaremill.com/whats-new-in-asvs-5-0/].

### 2. OWASP Top 10 (2021 → 2025)
- Top 10:2025 lists A01 Broken Access Control, A02 Security Misconfiguration, A03 Software Supply Chain Failures (new), A04 Cryptographic Failures, A05 Injection, A06 Insecure Design, A07 Authentication Failures, A08 Software or Data Integrity Failures, A09 Security Logging and Alerting Failures, and A10 Mishandling of Exceptional Conditions (new). SSRF was folded into A01 [WEB:https://top10.owasp.org/2025/] [WEB:https://www.fastly.com/blog/new-2025-owasp-top-10-list-what-changed-what-you-need-to-know].
- Persona use: a **coverage checklist** for architecture and tasks review ("does the design address each of the 10?"). It is not a requirements spec.
- A06 Insecure Design (since 2021) is the category that justifies running security review **before code exists**, at the PRD and architecture stages [BOOK:OWASP Top 10:2021 A04 Insecure Design rationale].
- A03 Supply Chain points the tasks stage at SBOM, dependency pinning, and provenance tasks. A10 Exceptional Conditions is a shared concern with SRE: fail-closed versus fail-open, and error handling.

### 3. Threat modeling — Shostack, *Threat Modeling: Designing for Security* (2014); Threat Modeling Manifesto (2020)
- **Four Questions** framework. The 2014 book phrases them as: (1) What are you building? (2) What can go wrong with it once it's built? (3) What should you do about those things that can go wrong? (4) Did you do a decent job of analysis? [BOOK:Shostack, Threat Modeling, 2014, ch.1] [WEB:https://www.ieee-security.org/Cipher/BookReviews/2014/Shostak_by_austin.html (search summary)]. The current wording ("What are we working on? / What can go wrong? / What are we going to do about it? / Did we do a good enough job?") is the later phrasing used by Shostack and the Threat Modeling Manifesto (2020) [UNVERIFIED exact Manifesto wording — threatmodelingmanifesto.org was blocked].
- **STRIDE**: Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege. Each one is the violation of a property: authentication, integrity, non-repudiation, confidentiality, availability, authorization [BOOK:Shostack 2014, ch.3]. STRIDE-per-element runs over a **data-flow diagram (DFD)** made of external entities, processes, data stores, data flows, and **trust boundaries** [BOOK:Shostack 2014, ch.2–3].
- Mindset: "anyone can threat model". It should be done early and iterated, and "think like an attacker" alone is a weak method compared with structured enumeration [BOOK:Shostack 2014, ch.1 & ch.2]. A persona should use the structured method and avoid freeform "hacker brainstorming".
- Output artifact: DFD with trust boundaries, then a threat list (ID, element, STRIDE category, description), then a mitigation per threat (mitigate / eliminate / transfer / accept, with an owner), then validation [BOOK:Shostack 2014, ch.7–8]. The fourth question ("did we do a good job?") calls for a check that every threat has a disposition. This check is scriptable.
- **LINDDUN** (KU Leuven) is the privacy counterpart. Its categories are Linking, Identifying, Non-repudiation, Detecting, Data disclosure, Unawareness/unintervenability, and Non-compliance. It maps threats onto the same DFD [WEB:https://linddun.org/linddun-go-categories/] [WEB:https://threat-modeling.com/linddun-threat-modeling/]. Persona implication: security and privacy reviewers can **share one DFD artifact**, with STRIDE run by AppSec and LINDDUN by the privacy engineer.

### 4. NIST SSDF — SP 800-218 v1.1 (2022), v1.2 draft (SP 800-218r1 ipd, Dec 2025)
- The framework has four practice groups: **PO** Prepare the Organization, **PS** Protect the Software, **PW** Produce Well-Secured Software, and **RV** Respond to Vulnerabilities. v1.1 (Feb 2022) contains 19 practices [WEB:https://www.ox.security/academy/governance-compliance/nist-ssdf-for-appsec-teams-what-sp-800-218-actually-requires/].
- v1.2 initial public draft: published 17 Dec 2025, comments closed 30 Jan 2026. It adds two practices [WEB:https://www.nist.gov/news-events/news/2025/12/secure-software-development-framework-ssdf-version-12-available-public] [WEB:https://cycode.com/blog/nist-ssdf-1-2-changes-compliance-guide/]. It also adds AI-development material and aligns with EO 14306 [WEB:https://www.nist.gov/news-events/news/2025/12/secure-software-development-framework-ssdf-version-12-available-public (search summary)]. Whether it has been finalized as of Oct 2026 is [UNVERIFIED].
- SSDF is **outcome-based**: it says what to achieve, not how. Its practices map well onto pipeline stages. PW.1 (design software to meet security requirements and mitigate risks) fits the PRD and architecture stages. PW.4/PW.5 (reuse vetted components, secure coding), PW.7/PW.8 (code review and testing), and PS.3 (provenance) fit the tasks stage. RV fits the operability/incident handoff [BOOK:NIST SP 800-218 v1.1, Table 1] [UNVERIFIED exact task numbering].
- Persona use: the security reviewer at the tasks stage checks that a **security-relevant task exists** for each applicable PW/PS practice, such as SAST in CI, dependency scanning, SBOM generation, and secret scanning.

### 5. Security by design (CISA "Secure by Design" and general principles)
- Classic design principles from Saltzer & Schroeder (1975): least privilege, fail-safe defaults, economy of mechanism, complete mediation, open design, separation of privilege, least common mechanism, psychological acceptability [BOOK:Saltzer & Schroeder, "The Protection of Information in Computer Systems", 1975]. These are good **architecture-review heuristics** for an LLM because they are short, stable, and checkable.
- CISA's Secure by Design (2023, with international partners) asks vendors to take ownership of customer security outcomes, practice radical transparency, and lead from the top. Concrete examples are secure defaults, MFA, and memory-safe languages [BOOK:CISA et al., "Shifting the Balance of Cybersecurity Risk: Principles and Approaches for Secure by Design Software", April 2023, updated Oct 2023 — from knowledge, not fetched].

### 6. GDPR (Regulation (EU) 2016/679)
- **Art. 5 principles**: lawfulness, fairness and transparency; purpose limitation; data minimisation; accuracy; storage limitation; integrity and confidentiality; plus accountability (Art. 5(2)) [BOOK:GDPR Art. 5].
- **Art. 6 legal bases** (six): consent, contract, legal obligation, vital interests, public task, legitimate interests. **Art. 9** special categories need an additional condition [BOOK:GDPR Art. 6, 9].
- **Data subject rights** (Arts. 12–22): information, access, rectification, erasure, restriction, portability, objection, and rights related to automated decision-making [BOOK:GDPR Arts. 12–22].
- **Art. 25** data protection by design and by default applies to **all** processing. The **Art. 35 DPIA** is required only when processing is "likely to result in a high risk" [WEB:https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/accountability-and-governance/data-protection-impact-assessments-dpias/what-is-a-dpia/] [WEB:https://www.dataprotection.ie/en/organisations/know-your-obligations/data-protection-impact-assessments]. Persona implication: "DPIA required? yes/no + screening rationale" is a mandatory gate output.
- Also relevant to artifacts: **Art. 30** Record of Processing Activities (RoPA), **Art. 32** security of processing, **Art. 33** breach notification to the supervisory authority within 72h where feasible, and **Arts. 37–39** DPO [BOOK:GDPR Arts. 30, 32, 33, 37–39].

### 7. LGPD (Lei 13.709/2018, Brazil) and ANPD
- **Art. 6 principles** (ten): finalidade (purpose), adequação (adequacy), necessidade (necessity/minimisation), livre acesso (free access), qualidade dos dados (quality), transparência, segurança, prevenção, não discriminação, responsabilização e prestação de contas (accountability) [BOOK:LGPD Art. 6].
- **Art. 7 legal bases** (ten). Notable ones beyond GDPR's list are protection of credit (proteção do crédito), exercise of rights in judicial/administrative proceedings, and protection of health. **Art. 11** covers sensitive data, which has a narrower set of bases [BOOK:LGPD Arts. 7, 11] [WEB:https://www.securityscientist.net/blog/lgpd-compliance-toolkit/].
- **Art. 18 rights**: confirmation of processing, access, correction, anonymisation/blocking/deletion of unnecessary data, portability, deletion of consent-based data, information on sharing, information on the option to refuse consent, and revocation of consent [BOOK:LGPD Art. 18].
- **RIPD** (Relatório de Impacto à Proteção de Dados Pessoais), Arts. 5 XVII and 38: the ANPD may require one. At minimum it contains the types of data, the collection methodology, the security measures, and the controller's analysis of mitigation measures [WEB:https://portal.fgv.br/sites/default/files/uploads/2024.11.05-guia-de-relatorio-de-impacto-a-protecao-de-dados-pessoais-ripd.pdf] [WEB:https://www.securityscientist.net/blog/lgpd-compliance-toolkit/].
- **Art. 41** encarregado (DPO equivalent). **Art. 48** says incidents must be communicated to the ANPD and data subjects. ANPD Resolution CD/ANPD nº 15/2024 (24 April 2024, Regulamento de Comunicação de Incidente de Segurança) sets a deadline of 3 business days from the controller's knowledge that the incident affected personal data [WEB:https://bibliotecadigital.mj.gov.br/bitstream/1/12879/2/RES_ANPD_2024_15.html (search summary)].
- Persona implication: the privacy reviewer needs a **jurisdiction field** (EU / BR / both / other). It must refuse to guess applicability when the PRD does not state users' locations or the data controller's establishment.

### 8. Privacy by Design — Ann Cavoukian (2009/2011)
- The seven principles are: (1) proactive not reactive, preventive not remedial; (2) privacy as the default setting; (3) privacy embedded into design; (4) full functionality, positive-sum not zero-sum; (5) end-to-end security, full lifecycle protection; (6) visibility and transparency; (7) respect for user privacy, user-centric [WEB:https://www.sfu.ca/~palys/Cavoukian-2011-PrivacyByDesign-7FoundationalPrinciples.pdf] [WEB:https://sites.psu.edu/digitalshred/2020/11/13/privacy-by-design-pbd-the-7-foundational-principles-cavoukian/].
- Principle 2 sets a testable bar: "if an individual does nothing, their privacy still remains intact" [WEB:https://sites.psu.edu/digitalshred/2020/11/13/privacy-by-design-pbd-the-7-foundational-principles-cavoukian/] (paraphrase of the source). Acceptance test: every opt-in toggle defaults to off and every optional field is genuinely optional.
- Principle 4 (positive-sum) means the privacy reviewer should **propose alternatives**, such as aggregation, pseudonymisation, on-device processing, or shorter retention. Vetoing alone is not the expected behavior.
- **Data minimisation** in practice: for every personal-data element in the PRD/data model, ask *which requirement needs it, at what granularity, for how long, and who can see it*. This produces a per-field data inventory, which is the core privacy artifact.

### 9. Google SRE — *Site Reliability Engineering* (2016) and *The Site Reliability Workbook* (2018)
- **SLI / SLO / error budget**: 100% is the wrong reliability target. The error budget (1 − SLO) is spent on velocity, and when it is exhausted, releases slow down [BOOK:Beyer et al., SRE, 2016, ch.3 "Embracing Risk", ch.4 "Service Level Objectives"] [WEB:https://sre.google/sre-book/embracing-risk/].
- **Error budget policy** is a written, pre-agreed document that states what happens when the budget is spent (for example a release freeze except for P0/security fixes). The Workbook has an example in Appendix B [WEB:https://sre.google/workbook/table-of-contents/] [BOOK:Beyer et al., The SRE Workbook, 2018, ch.2 & App. B].
- **Four golden signals**: latency, traffic, errors, saturation [BOOK:SRE 2016, ch.6 "Monitoring Distributed Systems"].
- **Toil** is manual, repetitive, automatable, tactical, without enduring value, and scales linearly with service growth. SRE caps toil at about 50% of time [BOOK:SRE 2016, ch.5 "Eliminating Toil"]. Persona use: the SRE reviewer flags tasks or runbooks that bake in O(n) manual operations.
- **Production Readiness Review (PRR)** is in ch.32 (evolving the SRE engagement model). **Launch Coordination Checklist** is App. E (around 2005) [WEB:https://sre.google/sre-book/launch-checklist/] [WEB:https://sre.google/workbook/engagement-model/]. The Workbook engagement model distinguishes **Application Readiness Reviews (ARRs)** from PRRs, citing SRE book ch.32 [WEB:https://sre.google/workbook/engagement-model/ (search summary)].
- **Multi-window, multi-burn-rate alerting** [BOOK:SRE Workbook 2018, ch.5 "Alerting on SLOs"]. **Blameless postmortems** [BOOK:SRE 2016, ch.15].
- Alex Hidalgo, *Implementing Service Level Objectives* (2020): SLOs are a conversation tool between product and engineering, and SLIs should measure what users experience [BOOK:Hidalgo, Implementing SLOs, 2020, ch.1–3].

### 10. Observability — Majors, Fong-Jones, Miranda, *Observability Engineering* (1st ed. 2022; 2nd ed. mid-2026, with Austin Parker)
- Observability means being able to answer **novel questions** ("unknown unknowns") about the system without shipping new code. It relies on **high-cardinality, high-dimensionality structured (wide) events** and traces [WEB:https://www.honeycomb.io/resources/webinars/structured-events-are-the-basis-of-observability] [BOOK:Majors et al., 2022, ch.1–2].
- **Core analysis loop**: start from the symptom, slice by dimensions, compare outliers to the baseline, then iterate. It works only when events carry rich context (user ID, build ID, tenant, feature flag) [WEB:https://techleadjournal.dev/episodes/88/].
- **SLO-based alerting** replaces cause-based alert sprawl. Alert on burn toward the SLO and debug with observability [WEB:https://techleadjournal.dev/episodes/88/].
- The 2nd ed. emphasizes unified data workflows over three disparate "pillars" (logs/metrics/traces) [WEB:https://www.oreilly.com/library/view/observability-engineering-2nd/9781098179915/]. Persona implication: the observability reviewer should require an **instrumentation spec** (span/event attributes) rather than "add logging". OpenTelemetry semantic conventions are the de-facto attribute vocabulary [UNVERIFIED as cited in book; widely used in industry].

### 11. Performance & capacity planning
- Brendan Gregg, *Systems Performance* (2nd ed. 2020): the **USE method** (Utilization, Saturation, Errors per resource) and anti-methods such as the "streetlight" and "random change" anti-methods [BOOK:Gregg, Systems Performance, 2020, ch.2].
- **RED method** (Rate, Errors, Duration per service; Tom Wilkie, Weaveworks, ~2015) complements USE for request-driven services [BOOK:from knowledge; widely attributed to Wilkie].
- Latency targets must be **percentiles** (p50/p95/p99/p99.9) and attached to a load level. Averages hide tails. Load-test tools that suffer from **coordinated omission** under-report tails (Gil Tene) [BOOK:Gregg 2020, ch.2 latency; Tene talks "How NOT to Measure Latency"] [UNVERIFIED exact sources].
- **Little's Law** (L = λW) is the back-of-envelope link between concurrency, throughput, and latency. It is a quick sanity check that an LLM reviewer can actually compute.
- Capacity planning: forecast demand from business drivers, model the resource per unit of demand, keep headroom, and plan for N+2 redundancy during maintenance plus failure [BOOK:SRE 2016, ch.18 (and intent-based capacity planning discussion)] [BOOK:Allspaw, The Art of Capacity Planning, 2008]. Michael Nygard, *Release It!* (2nd ed. 2018): stability patterns such as timeouts, circuit breakers, bulkheads, and backpressure, and anti-patterns such as cascading failures and unbounded result sets [BOOK:Nygard, Release It!, 2018, ch.4–5].

### 12. FinOps — FinOps Foundation Framework; Storment & Fuller, *Cloud FinOps* (2nd ed. 2023)
- Phases: **Inform → Optimize → Operate**, iterated [WEB:https://finopsdaily.com/finops-framework/] [WEB:https://www.tangoe.com/blog/2025-finops-readiness-understanding-the-framework-one-term-at-a-time/].
- Four domains: Understand Usage & Cost; Quantify Business Value (forecasting, budgeting, benchmarking, **unit economics**); Optimize Usage & Cost; Manage the FinOps Practice. The 2025 revision dropped "cloud" from domain names to cover wider technology spend [WEB:https://yukidata.com/finops-framework/] [WEB:https://finopsdaily.com/finops-framework/] [UNVERIFIED exact domain titles post-2025].
- Principles: teams collaborate; business value drives technology decisions; everyone takes ownership for their technology usage; data is accessible, timely, and accurate; FinOps is enabled centrally; take advantage of the variable cost model [BOOK:Storment & Fuller, Cloud FinOps, 2nd ed. 2023, ch.1]. The 2025 revision was the first change to the principles since 2019 and reworded them to say "technology" rather than "cloud" [WEB:https://www.finops.org/insights/2025-finops-framework/ (search summary)] [UNVERIFIED exact wording of every principle].
- **Unit economics** (cost per transaction / per active user / per tenant) is the artifact that turns cost into a design quality attribute. Persona implication: the FinOps reviewer at the PRD stage asks for the **unit-of-value metric**, and at the architecture stage asks for a **cost model per unit at expected and peak scale**.
- Tagging/allocation strategy (cost-allocation tags defined before resources exist) is a tasks-stage deliverable.

### 13. Well-Architected frameworks (AWS / Azure / Google Cloud)
- AWS has six pillars: operational excellence, security, reliability, performance efficiency, cost optimization, sustainability (added Dec 2021) [WEB:https://aws.amazon.com/blogs/apn/the-6-pillars-of-the-aws-well-architected-framework/].
- Azure has five pillars: reliability, security, cost optimization, operational excellence, performance efficiency [WEB:https://azure.microsoft.com/en-us/solutions/well-architected].
- Google Cloud **Well-Architected** Framework (renamed from "Architecture Framework") has pillars for operational excellence; security, privacy and compliance; reliability; cost optimization; performance optimization; and sustainability [WEB:https://docs.cloud.google.com/architecture/framework] (search snippet; the official page lists these six pillars, while some secondary sources show an older five-pillar version).
- Persona implication: the pillars line up almost one-to-one with this shared pool (security → AppSec; reliability + operational excellence → SRE/observability; performance → performance engineer; cost → FinOps). A separate "Well-Architected reviewer" is therefore **redundant**. The pillars serve as the **coverage index** the architecture stage critic uses to confirm that every shared reviewer was called. Each framework is a question bank with "high-risk issue" flags, which fits a structured reviewer output [BOOK:AWS Well-Architected Tool, HRI/MRI concept] [UNVERIFIED].

### 14. Product analytics / instrumentation
- **Tracking plan**: a spreadsheet- or schema-style spec of each event (name, trigger, properties with types, required/optional, owner, the question/metric it serves). Segment Protocols treats it as an enforceable schema [WEB:https://www.twilio.com/docs/segment/protocols/tracking-plan/best-practices] [WEB:https://amplitude.com/docs/data/data-planning-playbook].
- **Object–Action naming** in past tense ("Song Played", "Order Completed"). Segment recommends Title Case event names and snake_case properties [WEB:https://productanalyticshandbook.com/blog/event-taxonomy-object-action/] [WEB:https://www.twilio.com/docs/segment/protocols/tracking-plan/best-practices].
- Start from the **questions/metrics** (north-star, input metrics, funnel steps) and derive events from them. Do not instrument everything [WEB:https://amplitude.com/docs/data/data-planning-playbook]. Croll & Yoskovitz's *Lean Analytics* (2013) covers "one metric that matters" and good-metric criteria (comparative, understandable, ratio/rate, behavior-changing) [BOOK:Croll & Yoskovitz, Lean Analytics, 2013, ch.2].
- Analytics is personal-data processing. Event properties are a common **privacy leak** (emails, free-text search, precise geo), so every tracking plan needs a privacy review. This is a hard coupling to the privacy engineer.

---

## Real-world roles

> Stage key: **D** discovery, **P** PRD, **A** architecture, **T** tasks, **S** shared (invoked by any stage). All roles below are **S** with a stage-dependent depth profile.

### R1. Security Architect / Application Security (AppSec) Engineer
- **Titles**: Security Architect, Application Security Engineer, Product Security Engineer, Security Champion (embedded), Threat Modeling Lead.
- **Stages**: D (light: data/actor sensitivity screen), P (security NFRs + ASVS level), **A (primary: threat model)**, T (security tasks, SSDF coverage).
- **Mission**: Make sure the product is designed so that the realistic threats for its risk tier are identified and disposed of before build, and that the security requirements are verifiable.
- **Mindset & principles**:
  - Use structured enumeration over intuition (four questions, STRIDE-per-element) [BOOK:Shostack 2014, ch.1–3].
  - Least privilege, fail-safe defaults, complete mediation [BOOK:Saltzer & Schroeder 1975].
  - Treat requirements as testable statements by citing ASVS IDs, not prose like "must be secure" [WEB:https://softwaremill.com/whats-new-in-asvs-5-0/].
  - Fix design flaws early because they are the most expensive to fix later (Insecure Design category) [WEB:https://top10.owasp.org/2025/].
  - Risk acceptance is a business decision with a named owner. The security reviewer recommends; the product owner accepts [BOOK:Shostack 2014, ch.7–8].
- **OWNS**: threat model (DFD + STRIDE list + dispositions), target ASVS level recommendation, security NFRs, security acceptance criteria, security tasks list (SAST/DAST/SCA/SBOM/secrets), abuse cases.
- **DOES NOT OWN**: privacy/legal-basis analysis (R2/R3), choosing the architecture (the architect does; AppSec reviews it), risk acceptance (product owner), penetration testing execution (out of pipeline), incident response runbooks (SRE co-owns).
- **Inputs needed**: actors and roles/permissions model, data classification (from R2), component/deployment diagram with trust boundaries, external integrations and third-party dependencies, authn/authz approach, hosting/tenancy model, regulatory context.
- **Outputs (standard formats)**:
  - Threat model doc: scope → DFD (Mermaid/Threat Dragon/MS TMT style) → threat table `| ID | DFD element | STRIDE | Threat | Likelihood/Impact | Disposition (mitigate/eliminate/transfer/accept) | Control / ASVS ref | Owner |` [BOOK:Shostack 2014, ch.2,7].
  - Security requirements: `SEC-NFR-xx` with ASVS ID + verification method (test/review/scan).
  - Abuse/misuse cases mirrored on user stories.
  - SSDF coverage matrix at the tasks stage (PO/PS/PW/RV → task IDs) [WEB:https://www.ox.security/academy/governance-compliance/nist-ssdf-for-appsec-teams-what-sp-800-218-actually-requires/].
- **ACCEPTANCE criteria** (reviewer checklist):
  - [ ] A target ASVS level (L1/L2/L3) is stated with a reason tied to data sensitivity/exposure.
  - [ ] The DFD shows every external entity, data store, and data flow, and **every trust boundary crossing is labeled**.
  - [ ] STRIDE has been applied to every DFD element (or the categories that do not apply are explicitly marked N/A with a reason).
  - [ ] Every threat has a disposition. No `TBD` remains, and each "accept" has a named risk owner.
  - [ ] Each mitigation maps to at least one requirement ID and at least one task ID (traceable).
  - [ ] Authn, authz (object-level and function-level), session, secrets management, input validation/output encoding, logging of security events, and dependency management are each addressed or marked N/A with a reason.
  - [ ] OWASP Top 10:2025 coverage table is complete for web/API scope.
  - [ ] Tasks stage: SAST, SCA/dependency scanning, secret scanning, and SBOM generation tasks exist, or a reason is given for each one that is missing.
- **REFUSAL criteria**:
  - **blocked**: no actors/roles model. No data classification, so the ASVS level cannot be set. No architecture diagram or component list at the A stage, so there is nothing to threat-model. External integrations are named but their auth mechanism is unknown.
  - **rejected**: the PRD contains security requirements that cannot be tested ("system must be secure", "use encryption"). The architecture has an unauthenticated admin surface or shared credentials across tenants. Secrets live in code/config files. Authorization is enforced client-side only. A threat accepted without an owner. Hand-rolled crypto. A tasks list with zero security verification tasks for L2+ scope.
  - **out_of_scope**: performing or simulating a real penetration test against live systems. Writing exploit code. Certifying compliance (SOC 2/ISO 27001 attestation). Legal interpretation of security regulations, which goes to R3 as a flag.
- **Anti-patterns**: a generic Top 10 copy-paste "threat model" with no DFD. Threat lists with no dispositions. "Security theater" controls not tied to a threat. Reviewing only at the end ("security as a gate, not a guide"). Making every finding Critical, which causes severity inflation. Rejecting without offering a mitigation.
- **Handoffs**: receives from the stage orchestrator (PRD, architecture docs) and from R2 (data inventory/classification). Delivers findings to the orchestrator, security NFRs/ACs to the PRD stage, controls and tasks to the tasks stage, security event list to R5 (observability), and threat↔requirement↔task links to the traceability owner.

### R2. Privacy Engineer (DPO-style privacy reviewer)
- **Titles**: Privacy Engineer, Privacy Program Manager, Data Protection Officer (DPO, GDPR Arts. 37–39), Encarregado (LGPD Art. 41), Privacy Architect.
- **Stages**: **D (primary: personal-data screen; "should we collect this at all?")**, **P (primary: data inventory, legal basis *needed*, DPIA/RIPD screening, rights requirements)**, A (LINDDUN on the shared DFD, retention/deletion design), T (privacy tasks: deletion jobs, consent storage, DSAR endpoints).
- **Mission**: Make sure that personal data is collected only when necessary, is protected by default across its whole lifecycle, and that data subjects' rights are operable by design.
- **Mindset & principles**:
  - Cavoukian's seven principles, especially *privacy as the default* and *positive-sum* [WEB:https://www.sfu.ca/~palys/Cavoukian-2011-PrivacyByDesign-7FoundationalPrinciples.pdf].
  - Data minimisation/necessity is the first question and protection the second [BOOK:GDPR Art. 5(1)(c)] [BOOK:LGPD Art. 6 III].
  - By-design applies to everything, and DPIA applies to high risk [WEB:https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/accountability-and-governance/data-protection-impact-assessments-dpias/what-is-a-dpia/].
  - Systematic threat elicitation with LINDDUN [WEB:https://linddun.org/linddun-go-categories/].
  - **Engineering role, not legal counsel**: it identifies issues and flags them for legal decision.
- **OWNS**: personal data inventory (field-level), data flow map (shared DFD annotations), DPIA/RIPD **screening** and draft engineering sections, LINDDUN threat list, privacy requirements (consent UX, notices required, retention periods as *requirements to be confirmed*), DSAR (data subject access/erasure/portability) functional requirements, privacy defaults.
- **DOES NOT OWN**: final determination of the legal basis or of whether a DPIA/RIPD is legally mandatory (legal/DPO human), privacy policy text, cross-border transfer mechanisms (SCCs etc. are legal decisions), security controls implementation (R1), consent wording copy (UX/legal).
- **Inputs needed**: jurisdictions of users and of the controller (EU/BR/other), user types (including minors?), purpose of each feature, every data element with source and recipients, third parties/processors, analytics/tracking plan (R8), retention expectations.
- **Outputs (standard formats)**:
  - **Data inventory** `| Field | Category (personal/sensitive-Art.9/Art.11/none) | Purpose (req ID) | Legal basis (proposed — needs legal confirmation) | Source | Recipients/processors | Retention | Minimisation alternative considered |`. This mirrors the RoPA (GDPR Art. 30) [BOOK:GDPR Art. 30].
  - **DPIA/RIPD screening**: list of high-risk triggers (large-scale sensitive data, systematic monitoring, profiling with significant effects, vulnerable subjects, new tech) → recommendation "DPIA/RIPD likely required / not likely / legal to decide" [WEB:https://www.dataprotection.ie/en/organisations/know-your-obligations/data-protection-impact-assessments].
  - DPIA/RIPD **engineering draft sections**: description of processing, necessity/proportionality, risks, measures. The LGPD minimum content is data types, collection methodology, security measures, and mitigation analysis [WEB:https://portal.fgv.br/sites/default/files/uploads/2024.11.05-guia-de-relatorio-de-impacto-a-protecao-de-dados-pessoais-ripd.pdf].
  - LINDDUN threat table on the shared DFD.
  - Rights-operability requirements: GDPR Arts. 15–22 / LGPD Art. 18 → feature or ops procedure.
- **ACCEPTANCE criteria**:
  - [ ] Every personal-data field in the PRD/data model appears in the inventory, with a purpose that traces to a requirement ID. **Fields with no purpose are removed or flagged.**
  - [ ] Sensitive/special-category data is explicitly identified (GDPR Art. 9 / LGPD Art. 11), or "none" is stated.
  - [ ] Each processing purpose has a *proposed* legal basis marked "for legal confirmation".
  - [ ] DPIA/RIPD screening is done, with the triggers evaluated one by one.
  - [ ] Retention period or rule per data category, and a deletion mechanism exists at the A/T stage.
  - [ ] Each applicable data subject right maps to a feature, admin tool, or documented manual procedure with an SLA.
  - [ ] Defaults: optional data collection, tracking, and marketing are off by default (Cavoukian #2).
  - [ ] Every third party/processor that receives personal data is listed.
  - [ ] LINDDUN applied to the DFD at the A stage, with every threat dispositioned.
  - [ ] Analytics tracking plan reviewed: no direct identifiers or free text in event properties unless justified.
- **REFUSAL criteria**:
  - **blocked**: user/controller jurisdictions unknown. The purpose of the data collection is not stated. The data model is not available at the P/A stage. The tracking plan is referenced but missing.
  - **rejected**: collecting personal data with no stated purpose ("might be useful later"). Sensitive data collected where a non-sensitive alternative meets the requirement. Pre-ticked consent or tracking on by default. No deletion path for personal data. Personal data in logs/analytics without justification. A PRD that says "legal basis: consent" for processing that is necessary to deliver the service (a likely mis-basis; flag it for legal and reject as unvalidated) [BOOK:GDPR Art. 6(1)(b) vs 6(1)(a)].
  - **out_of_scope**: **giving legal advice or a legal opinion**. Final decisions on lawful basis, DPIA mandatory status, or transfer mechanisms. Drafting the privacy policy as a legally binding text. Answering "are we compliant?" with yes/no.
- **Anti-patterns**: treating privacy as a security subset and only checking encryption. Defaulting everything to "consent". Rubber-stamping DPIA as a template exercise. Vetoing features without positive-sum alternatives. Missing analytics/logging as data flows. Ignoring the LGPD-specific bases and the ten Art. 6 principles in Brazilian contexts.
- **Handoffs**: receives from D/P orchestrators (brief, PRD, data model) and R8 (tracking plan). Delivers data classification to R1, legal-question list to R3 / human legal, retention/deletion requirements to the architecture and tasks stages, and links to traceability.

### R3. Compliance Analyst (GRC)
- **Titles**: Compliance Analyst, GRC (Governance, Risk & Compliance) Analyst, Risk & Compliance Manager, Regulatory Compliance Specialist.
- **Stages**: D (applicability scan: which regimes/standards *might* apply), P (obligations register → requirements), A (control mapping), T (evidence-generating tasks).
- **Mission**: Turn the set of possibly-applicable regulations, standards, and contractual commitments into an explicit **obligations register** with traceable controls and evidence. Route every interpretive question to qualified humans.
- **Mindset & principles**: controls must produce **evidence** (audit trail by design). Applicability is decided by humans with authority. Keep "regulatory requirement" separate from "internal policy" and "customer contract" [BOOK:general GRC practice; ISO/IEC 27001:2022 Annex A control-mapping practice] [UNVERIFIED as a single source]. Accountability (GDPR Art. 5(2); LGPD Art. 6 X) means you must be able to *demonstrate* compliance, so artifacts matter [BOOK:GDPR Art. 5(2)].
- **OWNS**: applicability screen (candidate regimes: GDPR, LGPD, PCI DSS if cards, HIPAA if US health, sector rules, accessibility law, SOC 2/ISO 27001 if customer-required), obligations register, control-to-requirement mapping, evidence plan, open legal questions list.
- **DOES NOT OWN**: legal interpretation (counsel), technical privacy design (R2), security control design (R1), certification/audit.
- **Inputs**: business model, markets/geographies, customer segments (B2B enterprise contracts?), payment flows, data categories (from R2), industry.
- **Outputs**: Obligations register `| Obligation ID | Source (regime/article/contract clause) | Applicability status (confirmed by human / candidate) | Requirement ID(s) | Control | Evidence artifact | Owner |`, plus an **Open Legal Questions** list, each with the decision needed, why it matters, and the blocking stage.
- **ACCEPTANCE criteria**:
  - [ ] Every candidate regime has applicability status = `candidate` or `confirmed-by:<human/role>`. The agent never sets `confirmed` itself.
  - [ ] Every confirmed obligation maps to at least one requirement and one evidence artifact.
  - [ ] Every output carries the disclaimer: "not legal advice; for review by qualified counsel/DPO".
  - [ ] Open legal questions are phrased as decisions with options, not as conclusions.
  - [ ] No article/clause is cited that the agent could not verify, or it is marked [UNVERIFIED].
- **REFUSAL criteria**:
  - **blocked**: markets/geographies or business model unknown. Payment/health/children's data flows unspecified when the domain suggests them.
  - **rejected**: an upstream artifact asserts "compliant with X" without evidence or without a human sign-off. A PRD with regulatory requirements that have no source citation.
  - **out_of_scope**: legal advice. Statements that the product "is compliant". Interpreting case law or ANPD/DPA enforcement guidance as binding conclusions. Contract negotiation. GTM claims such as "GDPR-certified" in marketing (GTM is out of scope, and such certification claims are also unsafe).
- **Anti-patterns**: checklist compliance with no evidence plan. Hallucinated article numbers. Over-scoping (claiming HIPAA applies to everything health-adjacent) or under-scoping. Merging compliance and privacy so that one persona both designs and "approves" its own design.
- **Handoffs**: receives from D/P orchestrators and R2. Delivers the obligations register to the PRD stage, evidence tasks to the tasks stage, and open legal questions to the **human escalation queue** (stage orchestrator surfaces them in the handoff as blockers or accepted-with-risk).
- **Persona note**: R3 can be merged into R2 for small projects, but the *acceptance* role must stay separate (see Implications).

### R4. Site Reliability Engineer (SRE) / Reliability Engineer
- **Titles**: SRE, Reliability Engineer, Production Engineer (Meta), Platform Reliability Lead, Launch Coordination Engineer (Google LCE) [BOOK:SRE 2016, ch.27 "Reliable Product Launches at Scale"].
- **Stages**: D (light: criticality/tolerance for downtime), **P (SLOs as NFRs, error budget policy)**, **A (failure modes, redundancy, degradation, PRR-lite)**, T (operability tasks: alerts, runbooks, rollback, load tests).
- **Mission**: Make sure that reliability targets are explicit, user-centric, and economically justified, and that the design and task list can actually meet and operate to them.
- **Mindset & principles**: 100% is the wrong target, and the error budget governs velocity [WEB:https://sre.google/sre-book/embracing-risk/]. SLIs measure user experience [BOOK:Hidalgo 2020]. Eliminate toil and cap it at 50% [BOOK:SRE 2016, ch.5]. Plan for failure with timeouts, retries with backoff/jitter, circuit breakers, bulkheads [BOOK:Nygard, Release It!, 2018]. Blameless culture [BOOK:SRE 2016, ch.15]. Agree on readiness before launch (PRR/launch checklist) [WEB:https://sre.google/sre-book/launch-checklist/].
- **OWNS**: SLI/SLO specification, error budget policy draft, failure mode analysis (dependency failure table), degradation/fallback strategy review, deployment safety (canary/progressive rollout, rollback), backup/restore and RTO/RPO, on-call/runbook requirements, PRR checklist.
- **DOES NOT OWN**: the business choice of SLO target (product owner decides from SRE's tradeoff analysis), instrumentation details (R5), performance budgets/load models (R6), cost (R7), security incident response (R1 co-owns).
- **Inputs**: user journeys and their criticality (from PRD), traffic expectations, dependency list (internal/external, with their SLAs), deployment topology, data durability needs, business impact of downtime.
- **Outputs**:
  - **SLO doc** (Workbook format): service, SLI specification (good events / valid events), SLI implementation (where measured), SLO target + window (e.g., 99.9% / 28d rolling), error budget, rationale, owner, error budget policy reference [BOOK:SRE Workbook 2018, ch.2 & App. A/B].
  - **Failure-mode table** `| Dependency/component | Failure mode | User impact | Detection (alert/SLI) | Mitigation/degradation | RTO/RPO |`.
  - **PRR / launch checklist**: architecture, capacity, monitoring, alerting, runbooks, rollout/rollback, backups tested, dependencies, on-call [WEB:https://sre.google/sre-book/launch-checklist/].
- **ACCEPTANCE criteria**:
  - [ ] Each critical user journey has at least one SLI defined as a ratio of good/valid events, with a measurement point.
  - [ ] Each SLO has a target, a window, and a rationale. No SLO is 100%.
  - [ ] An error budget policy states the consequence of exhaustion and the escalation path.
  - [ ] Every external dependency has a stated failure behavior (timeout value, retry policy, fallback). Retries are bounded, with backoff + jitter.
  - [ ] Single points of failure are listed and either eliminated or accepted with an owner.
  - [ ] RTO/RPO are stated for each data store, and a restore-test task exists.
  - [ ] There is a rollout strategy (canary/flags) and a rollback that is tested, not "redeploy previous".
  - [ ] Every page-worthy alert maps to an SLO burn or a clear user impact, and each has a runbook task.
  - [ ] Tasks stage: no recurring manual operational step without an automation task or an explicit toil acceptance.
- **REFUSAL criteria**:
  - **blocked**: no critical user journeys identified. No traffic/scale expectation, not even an order of magnitude. Dependencies unknown.
  - **rejected**: "99.999% availability" with no rationale or with a single-region, single-instance design. SLOs on internal metrics (CPU) rather than user experience. Unbounded retries. No timeout on network calls. Alerting on causes with no SLO. A launch plan with no rollback. Stateful store with no backup or restore test.
  - **out_of_scope**: actually operating/paging, running chaos experiments on real systems, vendor SLA negotiation, choosing the business SLO (it recommends; the PO decides).
- **Anti-patterns**: aspirational SLOs copied from cloud vendor SLAs. Too many SLOs. Error budget with no policy (it then has no teeth). Treating "multi-AZ" as a full reliability answer. Ignoring dependency SLO math (a service cannot be more available than its hard dependencies in series) [BOOK:SRE 2016, ch.3; Workbook ch.2] [UNVERIFIED exact chapter].
- **Handoffs**: receives from P/A orchestrators. Delivers SLOs to the PRD (as NFRs), SLI measurement requirements to R5, load/capacity assumptions to R6, redundancy cost questions to R7, and runbook/rollback tasks to T.

### R5. Observability Engineer
- **Titles**: Observability Engineer, Monitoring/Telemetry Engineer, Platform Observability Lead. Often part of SRE or platform teams.
- **Stages**: P (light: which questions must be answerable in production), **A (telemetry architecture, instrumentation spec)**, **T (instrumentation tasks, dashboards, alerts-as-code)**.
- **Mission**: Make sure that the system emits enough high-context telemetry to answer novel production questions and to measure the SLIs, with sustainable cost and no personal-data leakage.
- **Mindset & principles**: unknown-unknowns; wide structured events; high cardinality is a feature [WEB:https://www.honeycomb.io/resources/webinars/structured-events-are-the-basis-of-observability]. Core analysis loop [WEB:https://techleadjournal.dev/episodes/88/]. Alert on SLO burn, debug with observability [WEB:https://techleadjournal.dev/episodes/88/]. Instrumentation is part of the feature, not an afterthought [BOOK:Majors et al., 1st ed. 2022, ch.11 "Observability-Driven Development"; in the 2nd ed. this is ch.3].
- **OWNS**: instrumentation spec (spans, events, attributes), context propagation requirement, SLI measurement implementation, alerting rules (burn-rate), dashboard/runbook linkage, telemetry retention and sampling strategy, security-event logging spec (with R1).
- **DOES NOT OWN**: SLO targets (R4), product analytics events (R8; different consumers, different schema, although the pipeline may share it), log retention legal limits (R2/R3), vendor selection (architect + R7).
- **Inputs**: SLO doc (R4), component diagram and request paths, security event list (R1), privacy constraints on identifiers (R2), cost ceiling (R7).
- **Outputs**: Instrumentation spec `| Signal (span/event/metric) | Emitted where | Attributes (name, type, cardinality, PII? Y/N) | Purpose (SLI / debug question / security audit) | Sampling | Retention |` (attribute names follow OpenTelemetry semantic conventions where possible) [UNVERIFIED as industry-standard template]. Also burn-rate alert definitions (multi-window) [BOOK:SRE Workbook 2018, ch.5].
- **ACCEPTANCE criteria**:
  - [ ] Every SLI from R4 has a concrete emitting signal and query.
  - [ ] Trace context propagates across every service and async boundary (queues included).
  - [ ] Events carry the dimensions needed for the core analysis loop: build/version, tenant/customer (pseudonymous), endpoint/operation, feature flags, region.
  - [ ] Every attribute is classified PII Y/N. PII attributes are justified, hashed, or removed (R2 sign-off).
  - [ ] Alerts are burn-rate or symptom based, each with a runbook link. No alert without an action.
  - [ ] Sampling and retention are specified, and telemetry cost is estimated (to R7).
  - [ ] Security-relevant events (auth failures, privilege changes, admin actions) are logged per R1 (A09:2025) [WEB:https://top10.owasp.org/2025/].
- **REFUSAL criteria**:
  - **blocked**: no SLO doc or no component/request-path diagram.
  - **rejected**: "add logging" as the only observability requirement. Unstructured log lines as the primary signal. User emails/tokens in log attributes. Alerts with no runbook or on raw CPU thresholds only. No correlation IDs across services.
  - **out_of_scope**: choosing an observability vendor on price alone (R7 + architect), building BI dashboards for business KPIs (R8).
- **Anti-patterns**: three-pillars silos with no correlation. Dashboards nobody owns. Cardinality fear that drops the very dimensions needed for debugging. Logging secrets/PII. Alert fatigue.
- **Handoffs**: receives from R4, R1, R2 and the architecture orchestrator. Delivers instrumentation tasks to T, telemetry volume estimates to R7, and signal↔SLI↔requirement links to traceability.

### R6. Performance & Capacity Engineer
- **Titles**: Performance Engineer, Capacity Planner, Performance Test Engineer, Scalability Architect.
- **Stages**: P (performance NFRs: percentiles under load), **A (performance/capacity model, scalability review)**, T (load/soak/stress test tasks, perf budgets in CI).
- **Mission**: Make sure that performance requirements are quantified, achievable by the design at expected and peak load, and verified by tests that measure tails correctly.
- **Mindset & principles**: methodology over guesswork (USE method; avoid the streetlight anti-method) [BOOK:Gregg, Systems Performance, 2020, ch.2]. Percentiles, not averages. Beware coordinated omission [UNVERIFIED source detail]. Queueing reality (Little's Law, utilization near 100% explodes latency). Stability patterns such as backpressure, bounded queues, and timeouts [BOOK:Nygard 2018]. Capacity is forecast from business drivers, with headroom and N+2 [BOOK:SRE 2016, ch.18] [BOOK:Allspaw 2008].
- **OWNS**: performance NFRs (latency percentiles @ throughput, page-weight/Core Web Vitals for frontends), workload model (users → requests/s → resource), capacity plan with headroom, scalability bottleneck analysis, load-test plan and acceptance thresholds.
- **DOES NOT OWN**: SLO targets (R4, but latency SLOs are co-authored), cost of capacity (R7), code-level optimization (implementation).
- **Inputs**: expected users/tenants/data volume now and at 12–24 months, traffic shape (peak/avg ratio, seasonality), critical operations, architecture with data stores and sync/async paths, SLOs.
- **Outputs**:
  - Performance NFR format: `p95 < 300 ms and p99 < 800 ms for <operation> at 200 RPS sustained, error rate < 0.1%, measured at <point>`.
  - Workload & capacity model table `| Driver | Now | 12mo | Peak factor | Req/s | Per-unit resource | Instances incl. headroom & N+2 |`.
  - Load test plan: scenarios (baseline, peak, stress-to-break, soak), data set size, success thresholds, tooling with constant-arrival-rate (open model) mode.
- **ACCEPTANCE criteria**:
  - [ ] Every latency requirement has a percentile, a load level, and a measurement point. No "fast" adjectives.
  - [ ] The workload model derives numbers from stated business drivers, and the assumptions are listed.
  - [ ] Little's-Law sanity check for concurrency vs. pools/connection limits at peak.
  - [ ] Every unbounded operation (list endpoints, fan-out, N+1 queries, batch jobs) has a limit or pagination.
  - [ ] Peak utilization targets leave headroom (e.g., ≤60–70% at peak; the exact number is team policy) [UNVERIFIED as universal number].
  - [ ] A load/soak test task exists with pass/fail thresholds tied to the NFRs.
- **REFUSAL criteria**:
  - **blocked**: no scale expectation at all. Critical operations not identified.
  - **rejected**: latency NFRs stated as averages or without load. Design with synchronous fan-out to many dependencies on the hot path and no timeout/budget. "Auto-scaling" as the whole capacity plan when stateful bottlenecks (DB) exist. Load tests with closed-model tools as the only evidence for tail latency.
  - **out_of_scope**: running load tests against production or third-party systems, micro-optimizing code in the planning pipeline.
- **Anti-patterns**: premature optimization at discovery. Benchmarks on toy data sets. Ignoring the cold-start/warm-up phase. Performance requirements copied from generic web advice with no user-journey anchor.
- **Handoffs**: receives from R4 (SLOs) and the architecture orchestrator. Delivers the capacity model to R7, perf NFRs to the PRD, and test tasks to T.

### R7. FinOps Analyst / Cloud Cost Engineer
- **Titles**: FinOps Analyst, FinOps Practitioner, Cloud Cost Engineer, Cloud Economist, Technology Business Management (TBM) analyst.
- **Stages**: D (light: does the economic model hold? cost-to-serve order of magnitude), **P (unit-of-value metric, cost guardrail as an NFR)**, **A (cost model per unit, build/buy/managed-service tradeoffs)**, T (tagging/allocation, budgets/alerts, cost-anomaly tasks).
- **Mission**: Make sure that technology cost is designed as a quality attribute, expressed in unit economics tied to business value, and allocatable and observable from day one.
- **Mindset & principles**: business value drives technology decisions; everyone owns their usage; use the variable cost model [BOOK:Storment & Fuller, Cloud FinOps, 2023, ch.1]. Inform → Optimize → Operate [WEB:https://finopsdaily.com/finops-framework/]. Unit economics over absolute spend [WEB:https://finopsdaily.com/finops-framework/]. Cost is a cross-functional decision, not a finance veto.
- **OWNS**: unit-economics definition (cost per <unit of value>), cost model (expected/peak/12-month), cost NFR/guardrail, tagging/allocation scheme, budget & anomaly alert requirements, cost-aware alternative proposals (managed vs self-hosted, reserved vs on-demand, storage tiering, telemetry sampling).
- **DOES NOT OWN**: pricing/packaging of the product (GTM, out of scope), vendor contract negotiation, the decision to trade cost for reliability (PO decides with R4/R7 input).
- **Inputs**: unit of value (from PRD: per order, per MAU, per tenant), capacity model (R6), architecture components and managed services, telemetry volumes (R5), data retention (R2), target gross margin or cost ceiling if the business provides one.
- **Outputs**: Cost model table `| Component | Pricing dimension | Driver | Qty @ expected | Qty @ peak | Monthly cost | Cost per unit |` with assumptions and pricing date, a **tag/label schema** (e.g., `cost-center`, `service`, `env`, `owner`, `tenant` where feasible), and budgets with alert thresholds.
- **ACCEPTANCE criteria**:
  - [ ] A unit-of-value metric is defined and traces to a PRD goal.
  - [ ] Cost per unit is estimated at expected and peak scale, with explicit assumptions and pricing sources/dates.
  - [ ] The top 3 cost drivers are identified, and at least one alternative is evaluated for each.
  - [ ] Hidden/linear costs are considered: data egress, cross-AZ traffic, observability ingest, LLM/API per-call fees, storage growth with retention.
  - [ ] The tagging schema is defined and a task enforces it (policy-as-code or CI check).
  - [ ] A budget and anomaly alert exists per environment.
- **REFUSAL criteria**:
  - **blocked**: no unit of value derivable from the PRD. No scale estimate (needs R6). The architecture does not name the hosting/managed services.
  - **rejected**: a design whose cost per unit exceeds the stated revenue/ceiling per unit with no rationale. Unbounded cost paths (per-request LLM calls with no cap, unbounded log ingestion, no retention). Untaggable shared resources with no allocation rule.
  - **out_of_scope**: product pricing, financial forecasting for investors, procurement/contract negotiation, real-time spend queries against live billing (unless the tool is explicitly provided).
- **Anti-patterns**: cost review only after launch. Optimizing absolute spend while unit cost worsens. Hallucinated cloud prices (prices change, so they must be sourced and dated or marked as estimates). Blocking reliability investments on cost without a tradeoff analysis.
- **Handoffs**: receives from R6, R5, R2 and the architecture orchestrator. Delivers cost NFRs to the PRD, tradeoff notes to the architect, and tagging/budget tasks to T.

### R8. Product Analytics Engineer / Instrumentation Analyst
- **Titles**: Product Analytics Engineer, Product Analyst, Analytics Engineer, Data/Tracking Plan Owner, Growth Analyst.
- **Stages**: D (success-metric hypotheses: what would prove the opportunity?), **P (metric tree + tracking plan)**, A (event pipeline: client/server-side, schema enforcement, warehouse), T (instrumentation tasks + QA of events).
- **Mission**: Make sure that every product goal in the PRD has a measurable metric and that the events needed to compute it are specified, consistently named, privacy-reviewed, and testable.
- **Mindset & principles**: start from questions and metrics, not from events [WEB:https://amplitude.com/docs/data/data-planning-playbook]. Object–Action, past tense, consistent casing [WEB:https://productanalyticshandbook.com/blog/event-taxonomy-object-action/]. The tracking plan is a contract or schema, enforced in the pipeline [WEB:https://www.twilio.com/docs/segment/protocols/tracking-plan/best-practices]. Good metrics are rates/ratios that change behavior [BOOK:Croll & Yoskovitz, Lean Analytics, 2013, ch.2].
- **OWNS**: metric definitions (north-star, input/guardrail metrics) with formulas, event taxonomy & naming conventions, tracking plan, server-side vs client-side decision input, analytics QA acceptance tests.
- **DOES NOT OWN**: experiment design/statistics beyond definitions (data science), operational telemetry (R5), privacy legal basis for tracking/cookies (R2 → legal), success targets (PM owns the targets; R8 makes them measurable).
- **Inputs**: PRD goals/success metrics, user journeys/funnels, identity model (anonymous → identified), privacy constraints (R2), platforms.
- **Outputs**:
  - Metric spec `| Metric | Definition/formula | Numerator events | Denominator | Window | Segmenting dimensions | Owner | PRD goal ID |`.
  - Tracking plan `| Event name (Object Action) | Trigger (exact UI/server condition) | Properties (name, type, required, allowed values) | Source (client/server) | Metric(s) served | PII? | Owner |` [WEB:https://www.twilio.com/docs/segment/protocols/tracking-plan/best-practices].
- **ACCEPTANCE criteria**:
  - [ ] Every PRD success metric has a formula whose inputs are events in the plan, and every event serves at least one metric or a declared question. No orphan events.
  - [ ] Names follow one convention (Object Action, past tense, chosen casing) with no synonyms ("Signup Completed" vs "User Registered").
  - [ ] Each event has an exact, unambiguous trigger (e.g., "fires on server after payment captured", not "when user buys").
  - [ ] Revenue/conversion-critical events are server-side or have a stated reason why not.
  - [ ] Property types and allowed values are specified, and PII is flagged and approved by R2.
  - [ ] Identity stitching rule (anonymous → user ID) is stated.
  - [ ] There is an instrumentation QA task with expected event payload assertions.
- **REFUSAL criteria**:
  - **blocked**: the PRD has no success metrics or goals. Funnels/journeys undefined.
  - **rejected**: vanity metrics only (page views, total signups) with no ratio or behavior link. "Track everything" plans. Events carrying emails, names, or free text without R2 sign-off. Duplicate/synonym events.
  - **out_of_scope**: setting the business targets, GTM attribution/campaign tracking (GTM extension point), building BI dashboards for executives.
- **Anti-patterns**: autocapture as a tracking strategy. Events named after UI elements ("Blue Button Clicked") that break on redesign. Client-only purchase tracking blocked by ad blockers. No ownership, which lets the plan rot.
- **Handoffs**: receives from D/P orchestrators. Delivers the tracking plan to R2 (privacy review), event pipeline needs to architecture, instrumentation and QA tasks to T, and metric↔goal↔event links to traceability.

### (Not a separate role) Well-Architected reviewer
Cloud vendors' WAF reviews are done by solution architects using pillar question banks [WEB:https://aws.amazon.com/blogs/apn/the-6-pillars-of-the-aws-well-architected-framework/]. In this pipeline the pillars are a **coverage index** for the architecture-stage critic (security→R1, reliability/opex→R4/R5, performance→R6, cost→R7, sustainability→R7 as a secondary lens). It does not need its own persona.

---

## Implications for agentic personas

### What to split and what to merge
- **Keep 6 shared subagents, not 8**:
  1. `security-reviewer` (R1)
  2. `privacy-reviewer` (R2, with R3's obligations register in a separate output section)
  3. `reliability-reviewer` (R4 + R5: SLOs, failure modes, and the instrumentation spec form one causal chain; split them only if instrumentation volume is large)
  4. `performance-reviewer` (R6)
  5. `finops-reviewer` (R7)
  6. `analytics-reviewer` (R8)

  The merges follow real-world co-location: observability usually sits in SRE/platform, and GRC analysts in small orgs often sit in privacy. R3 should **not** be merged with R1. Security compliance mapping (SOC 2/ISO) is GRC work that only consumes security controls.
- **Keep reviewers separate from authors.** Each shared reviewer *proposes* artifacts (threat model, SLO doc, tracking plan) when the stage orchestrator asks for authoring help. The stage's EXIT critic, a different subagent, checks them. A reviewer must not approve an artifact it authored in the same stage, the same separation as maker/checker in GRC practice.
- **Shared DFD artifact.** R1 (STRIDE) and R2 (LINDDUN) annotate one `architecture/dfd.md` (or Mermaid). This avoids two incompatible system models.
- **Stage-depth profiles in the persona prompt.** Each reviewer gets a table `stage → required checks → allowed refusals`. At discovery, the security reviewer must not demand a threat model. It only screens data/actor sensitivity. Without this table, LLM reviewers apply architecture-depth checks to discovery briefs and block everything.
- **Fresh-session constraint.** Orchestrators run at different times in new windows, and subagents cannot spawn subagents [local:/home/user/ai-study-library/ai/docs/claude-code/subagents/creating-custom-subagents.md]. Each reviewer therefore needs: (a) a `reviews/<stage>/<reviewer>.md` findings file written to disk, (b) a short **carry-forward ledger** (`crosscutting/ledger.md`: open findings, accepted risks, deferred-to-stage items) that the next stage's ENTRY gate reads, and (c) read-only tools by default (`tools: Read, Grep, Glob`), with Write limited to its own findings path [local:/home/user/ai-study-library/ai/docs/claude-code/subagents/creating-custom-subagents.md]. Without the ledger, the tasks-stage security reviewer cannot know what the architecture-stage reviewer accepted.

### Standard reviewer output contract (all six)
```
verdict: pass | pass_with_findings | blocked | rejected | out_of_scope
stage: discovery|prd|architecture|tasks
findings:
  - id: SEC-A-003
    severity: blocker|major|minor|info
    check: "<acceptance criterion id>"
    evidence: "<file:section quote/pointer>"
    recommendation: "<concrete fix or alternative>"
    framework_ref: "ASVS 5.0 V?.?.? | STRIDE:T | SRE-WB ch2 | ..."  # or UNVERIFIED
carry_forward: [ids deferred to later stage, with target stage]
needs_human: [legal/business decisions with options]
```
Severity must be defined operationally: **blocker** means a refusal criterion was hit, and **major** means an acceptance criterion failed. This keeps LLM severity inflation down.

### What LLMs tend to get wrong here (and countermeasures)
1. **Generic checklists in place of system-specific analysis.** The model pastes the OWASP Top 10 or the WAF pillars with no reference to the actual DFD. *Countermeasure*: every finding must cite `evidence` pointing at a specific artifact location. A gate rejects findings with no evidence pointer.
2. **Hallucinated standard IDs and legal articles** (fake ASVS numbers, wrong GDPR/LGPD articles, invented ANPD deadlines). *Countermeasure*: an allow-list of IDs in a local reference file per framework, and `framework_ref` must be either from that file or tagged `UNVERIFIED`. ASVS 5.0 removed CWE mappings, so any ASVS→CWE claim is suspect [WEB:https://softwaremill.com/whats-new-in-asvs-5-0/].
3. **Legal-advice drift.** The model says "you are GDPR compliant" or "legitimate interest applies". *Countermeasure*: hard rule in R2/R3 prompts that legal basis is always "proposed — requires legal confirmation". A lint step greps outputs for forbidden phrases ("is compliant", "complies with", "legally permitted", "não há necessidade de RIPD") and marks them as gate failures. Every output carries the not-legal-advice disclaimer.
4. **Severity inflation and veto-only reviews.** *Countermeasure*: each blocker must include a recommendation (positive-sum, Cavoukian #4), and there is a cap on how many blockers can rest on "best practice" alone rather than a stated requirement or refusal criterion.
5. **Invented numbers**: SLO targets, cloud prices, capacity. *Countermeasure*: numbers must cite their source (PRD field, R6 model, pricing page with date) or be labeled `assumption`. The SLO target is always "recommended, PO decides".
6. **Wrong-stage depth** (asking for the tracking plan during discovery, the threat model during PRD). *Countermeasure*: the stage-depth table, plus a refusal of type `out_of_scope` for checks that belong to a later stage. These are recorded as carry-forward instead.
7. **Duplicate and conflicting findings across reviewers** (e.g., R1 wants verbose security logs, R2 wants no PII in logs). *Countermeasure*: the orchestrator's consolidation step has a conflict table, and conflicts go to `needs_human` with both positions stated. A reviewer never silently overrides another.
8. **Privacy blind spots in telemetry/analytics.** LLMs treat logs and events as non-personal. *Countermeasure*: R5 and R8 outputs must pass through R2 (a hard dependency in the orchestrator's delegation plan).

### Hard gates (deterministic where possible)
| Gate | Stage | Check (scriptable unless noted) |
|---|---|---|
| ASVS level declared | PRD exit | `security.asvs_level ∈ {L1,L2,L3}` + rationale non-empty |
| Threat model complete | Arch exit | every DFD element has ≥1 STRIDE row or N/A reason; no `disposition: TBD`; every `accept` has `risk_owner` |
| Privacy inventory complete | PRD exit | every personal-data field in data model ∈ inventory; each has `purpose_req_id`; `legal_basis_status == "proposed"` or `"confirmed_by:<human>"` |
| DPIA/RIPD screening | PRD exit | screening section present with all triggers evaluated; result ∈ {likely, unlikely, legal_to_decide} |
| No legal conclusions | all | regex lint for forbidden phrases in R2/R3 output |
| SLOs defined | PRD exit | each critical journey has an SLI ratio + target < 100% + window + error budget policy ref |
| Failure behavior | Arch exit | every external dependency has timeout + retry bound + fallback |
| Instrumentation coverage | Arch/Tasks exit | every SLI ↔ signal; every signal attribute has `pii: Y/N` |
| Perf NFR form | PRD exit | regex: percentile + load + measurement point present |
| Unit economics | Arch exit | `cost_per_unit` at expected and peak, assumptions dated |
| Tracking plan integrity | PRD/Tasks exit | no orphan events/metrics; naming regex `^[A-Z][a-z]+( [A-Z][a-z]+)* [A-Z][a-z]+ed$` or the chosen convention; PII flags reviewed by R2 |
| Security/ops tasks present | Tasks exit | SAST/SCA/secrets/SBOM, restore test, load test, instrumentation QA tasks exist or have waiver |
| Carry-forward resolved | each ENTRY | every ledger item targeted at this stage is addressed or re-deferred with reason |

The human-only gates (not automatable) are legal-basis confirmation, the DPIA/RIPD mandatory decision, risk acceptance of security blockers, the SLO target business decision, and the cost ceiling. The orchestrator must surface these as `blocked: awaiting human decision` and must not resolve them itself.

### Persona prompt seeds (one line each)
- **security-reviewer**: "You are an AppSec architect who uses Shostack's four questions and STRIDE-per-element over the shared DFD, sets ASVS 5.0 targets, and refuses untestable security requirements."
- **privacy-reviewer**: "You are a privacy engineer (not a lawyer) who applies data minimisation, Cavoukian's seven principles, and LINDDUN; you propose legal bases for confirmation by counsel and never state compliance."
- **reliability-reviewer**: "You are an SRE who writes user-centric SLIs/SLOs with error budget policies, demands bounded failure behavior per dependency, and specifies the telemetry needed to measure and debug them."
- **performance-reviewer**: "You are a performance engineer who quantifies percentiles under load, sanity-checks with Little's Law and USE, and rejects averages and unbounded operations."
- **finops-reviewer**: "You are a FinOps practitioner who expresses cost as unit economics tied to the PRD's value metric, sources and dates every price, and proposes cheaper alternatives instead of vetoing."
- **analytics-reviewer**: "You are a product analytics engineer who derives a tracking plan from metric definitions, enforces Object–Action naming, and routes every event property through privacy review."

---

## Sources
1. SoftwareMill — "What's New in ASVS 5.0". https://softwaremill.com/whats-new-in-asvs-5-0/ (via search result summary)
2. arc42 Quality — OWASP ASVS. https://quality.arc42.org/standards/owasp-asvs
3. Security Compass — "What Is OWASP ASVS?". https://www.securitycompass.com/blog/what-is-owasp-asvs/
4. OWASP Top 10:2025. https://top10.owasp.org/2025/ (via search; owasp.org fetch blocked)
5. Fastly — "The New 2025 OWASP Top 10 List". https://www.fastly.com/blog/new-2025-owasp-top-10-list-what-changed-what-you-need-to-know
6. NIST — "SSDF Version 1.2 is Available for Public Comment" (Dec 2025). https://www.nist.gov/news-events/news/2025/12/secure-software-development-framework-ssdf-version-12-available-public
7. OX Security — "NIST SSDF for AppSec Teams". https://www.ox.security/academy/governance-compliance/nist-ssdf-for-appsec-teams-what-sp-800-218-actually-requires/
8. Cycode — "NIST SSDF 1.2 Changes". https://cycode.com/blog/nist-ssdf-1-2-changes-compliance-guide/
9. LINDDUN GO categories. https://linddun.org/linddun-go-categories/ (search listing; fetch blocked)
10. Threat-Modeling.com — LINDDUN. https://threat-modeling.com/linddun-threat-modeling/
11. ICO — "What is a DPIA?". https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/accountability-and-governance/data-protection-impact-assessments-dpias/what-is-a-dpia/
12. Irish DPC — Data Protection Impact Assessments. https://www.dataprotection.ie/en/organisations/know-your-obligations/data-protection-impact-assessments
13. FGV — Guia de Relatório de Impacto à Proteção de Dados Pessoais (2024). https://portal.fgv.br/sites/default/files/uploads/2024.11.05-guia-de-relatorio-de-impacto-a-protecao-de-dados-pessoais-ripd.pdf
14. Security Scientist — LGPD Compliance Toolkit. https://www.securityscientist.net/blog/lgpd-compliance-toolkit/
15. Cavoukian — "Privacy by Design: The 7 Foundational Principles" (2011). https://www.sfu.ca/~palys/Cavoukian-2011-PrivacyByDesign-7FoundationalPrinciples.pdf
16. Penn State Digital Shred — PbD 7 principles. https://sites.psu.edu/digitalshred/2020/11/13/privacy-by-design-pbd-the-7-foundational-principles-cavoukian/
17. Google SRE — Embracing Risk. https://sre.google/sre-book/embracing-risk/ (search; fetch blocked)
18. Google SRE — Launch Coordination Checklist (App. E). https://sre.google/sre-book/launch-checklist/
19. Google SRE Workbook — Engagement model. https://sre.google/workbook/engagement-model/
20. Google SRE Workbook — Table of contents (Error Budget Policy, App. B). https://sre.google/workbook/table-of-contents/
21. O'Reilly — *Observability Engineering*, 2nd ed. https://www.oreilly.com/library/view/observability-engineering-2nd/9781098179915/
22. Tech Lead Journal #88 — Liz Fong-Jones on Observability Engineering. https://techleadjournal.dev/episodes/88/
23. Honeycomb — "Structured Events Are the Basis of Observability". https://www.honeycomb.io/resources/webinars/structured-events-are-the-basis-of-observability
24. FinOps Daily — FinOps Framework explained. https://finopsdaily.com/finops-framework/
25. Tangoe — 2025 FinOps readiness. https://www.tangoe.com/blog/2025-finops-readiness-understanding-the-framework-one-term-at-a-time/
26. Yuki Data — FinOps Framework guide (2025 updates). https://yukidata.com/finops-framework/
27. AWS APN Blog — The 6 Pillars of the AWS Well-Architected Framework. https://aws.amazon.com/blogs/apn/the-6-pillars-of-the-aws-well-architected-framework/
28. Microsoft — Azure Well-Architected Framework. https://azure.microsoft.com/en-us/solutions/well-architected
29. Google Cloud — Well-Architected Framework. https://docs.cloud.google.com/architecture/framework
30. Amplitude — Data planning playbook / Plan your taxonomy. https://amplitude.com/docs/data/data-planning-playbook
31. Twilio Segment — Tracking plan best practices. https://www.twilio.com/docs/segment/protocols/tracking-plan/best-practices
32. Product Analytics Handbook — Object-Action framework. https://productanalyticshandbook.com/blog/event-taxonomy-object-action/
33. [BOOK] Adam Shostack, *Threat Modeling: Designing for Security*, Wiley, 2014.
34. [BOOK] Beyer, Jones, Petoff, Murphy (eds.), *Site Reliability Engineering*, O'Reilly, 2016.
35. [BOOK] Beyer, Murphy, Rensin, Kawahara, Thorne (eds.), *The Site Reliability Workbook*, O'Reilly, 2018.
36. [BOOK] Alex Hidalgo, *Implementing Service Level Objectives*, O'Reilly, 2020.
37. [BOOK] Majors, Fong-Jones, Miranda, *Observability Engineering*, O'Reilly, 2022 (2nd ed. 2026, with Austin Parker: https://www.oreilly.com/library/view/observability-engineering-2nd/9781098179915/).
38. [BOOK] Brendan Gregg, *Systems Performance*, 2nd ed., Addison-Wesley, 2020.
39. [BOOK] Michael T. Nygard, *Release It!*, 2nd ed., Pragmatic Bookshelf, 2018.
40. [BOOK] John Allspaw, *The Art of Capacity Planning*, O'Reilly, 2008.
41. [BOOK] J.R. Storment & Mike Fuller, *Cloud FinOps*, 2nd ed., O'Reilly, 2023.
42. [BOOK] Alistair Croll & Benjamin Yoskovitz, *Lean Analytics*, O'Reilly, 2013.
43. [BOOK] Saltzer & Schroeder, "The Protection of Information in Computer Systems", Proc. IEEE, 1975.
44. [BOOK] Regulation (EU) 2016/679 (GDPR), Arts. 5, 6, 9, 12–22, 25, 30, 32, 33, 35, 37–39 (primary text, cited from knowledge).
45. [BOOK] Lei nº 13.709/2018 (LGPD), Arts. 5, 6, 7, 11, 18, 38, 41, 46, 48 (primary text, cited from knowledge).
46. [BOOK] NIST SP 800-218 v1.1, *Secure Software Development Framework*, 2022.
47. Local: /home/user/ai-study-library/ai/docs/claude-code/subagents/creating-custom-subagents.md (subagents cannot spawn subagents; read-only tool restriction via `tools`).
48. Local: /home/user/ai-study-library/dev/research/2026-04-25-harness-engineering-research.md (artifact-validation Stop hook pattern for required sections, applicable to the hard gates above).

---

## Verification log

Verifier pass on 2026-10-02 (citations and attributed claims only). Method: web search summaries (owasp.org, csrc.nist.gov, sre.google and linddun.org are blocked for direct fetch), local-corpus checks, and the verifier's own knowledge.

**Confirmed online:**
- OWASP Top 10:2025: all ten categories and their order, A03 and A10 new, SSRF folded into A01.
- ASVS 5.0.0: released May 2025 at Global AppSec EU Barcelona; **345** requirements (was "about 350") in 17 chapters; `v<version>-` ID prefix.
- NIST SSDF v1.2 (SP 800-218r1 ipd): published 17 Dec 2025; comments until 30 Jan 2026; adds two practices.
- ANPD Resolution CD/ANPD nº 15/2024: 3 business days for incident communication (upgraded from UNVERIFIED).
- SRE Workbook engagement model: ARRs and PRRs, with a reference to SRE book ch.32.
- Shostack's four questions: the 2014 book wording differs from the modern wording previously attributed to it. **Corrected** (see below).
- *Observability Engineering* 2nd ed.: O'Reilly, mid-2026, with Austin Parker as co-author; ODD is ch.3 in the 2nd ed.
- Google Cloud Well-Architected Framework: six pillars as listed (UNVERIFIED tag removed).
- FinOps 2025 principles revision (first change since 2019), including "Everyone takes ownership for their technology usage".
- Local: creating-custom-subagents.md (subagents cannot spawn subagents; `tools` restriction).

**Confirmed from the verifier's own knowledge:** STRIDE and its property mapping; LINDDUN categories; SSDF v1.1 four groups and 19 practices (PW.1, PW.4/5, PW.7/8, PS.3); Saltzer & Schroeder's eight principles (1975); GDPR Arts. 5, 6, 9, 12–22, 25, 30, 32, 33 (72h), 35, 37–39; LGPD Art. 6 (ten principles), Art. 7 (ten bases), Art. 11, Art. 18 (nine rights), Art. 5 XVII / 38 (RIPD minimum content), Art. 41, Art. 48; Cavoukian's seven principles and the principle 2 quote; SRE book ch.3, 4, 5 (50% toil cap), 6 (golden signals), 15, 27 (LCE), 32, App. E (circa 2005); Workbook ch.2, ch.5, App. A/B; Gregg USE and anti-methods (2nd ed. 2020, ch.2); Nygard *Release It!* 2nd ed. ch.4–5; AWS six pillars (sustainability Dec 2021); Azure five pillars; *Lean Analytics* good-metric criteria.

**Corrected:**
- Shostack four questions: the 2014 book's wording is now given ("What are you building? … Did you do a decent job of analysis?"). The "What are we working on?" wording is attributed to the later phrasing and the Manifesto.
- ASVS requirement count: "about 350" changed to 345.
- *Observability Engineering* 2nd ed.: "2025/26" changed to 2026, with the co-author added.
- ODD chapter: ch.11 in the 1st ed. confirmed; 2nd-ed. chapter number added.

**Upgraded from UNVERIFIED:** ANPD 3-business-day deadline; ASVS ID format; Google WAF pillar list; RED method attribution (Wilkie); CISA Secure by Design document identified (from knowledge).

**Left as UNVERIFIED:** Threat Modeling Manifesto exact wording; ASVS 5.0 "how to use" wording on Top 10 vs ASVS; SSDF task numbering; v1.2 finalization status; exact FinOps domain titles after 2025; OpenTelemetry as cited in the book; coordinated-omission sources; the 60–70% headroom number; AWS WA Tool HRI/MRI wording; dependency-SLO-math chapter; ISO 27001 GRC practice as a single source; instrumentation-spec template.
