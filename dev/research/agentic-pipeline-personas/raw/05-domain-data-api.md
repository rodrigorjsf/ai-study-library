# Raw research — Domain, data, API & integration

Axis: domain modeling, data, interfaces and integration. Pipeline stages touched: mostly **(3) Architecture**, with a thin and important presence in **(1) Discovery** (domain language, Big Picture event flow), **(2) PRD** (data requirements, API-as-product requirements, retention obligations) and **(4) Tasks** (migrations, contract tests, slicing tasks by aggregate and context).
Each stage runs as its own orchestrator in a fresh session (`claude --agent <stage>-orchestrator`). Workers are subagents, and subagents cannot spawn other subagents [LOCAL:ai/docs/claude-code/subagents/creating-custom-subagents.md:47,295]. A stage therefore learns about domain, data and contracts *only* from files on disk, which makes the artifact formats in this note the actual inter-stage protocol.

Tag legend: [WEB:url] = read or confirmed online in this session (some via search-result summaries, kept to what the summary supports). [GIT:repo/path] = read from a cloned public GitHub repo in this session. [BOOK:...] = from a well-known book. [LOCAL:path] = local corpus. [UNVERIFIED] = uncertain detail.
Web note: the egress proxy blocked martinfowler.com, microservices.io, google.aip.dev, rfc-editor.org and the GitHub API. Google AIPs and the DDD-Crew canvases were read by `git clone` of their public source repos instead.

---

## Literature & frameworks

### 1. Eric Evans — Domain-Driven Design (2003) and DDD Reference (2015)
- **Ubiquitous Language (UL):** the team and the domain experts use one rigorous language in speech, documents, diagrams *and code*. When the language changes, the model changes, and the reverse is also true [BOOK:Evans, Domain-Driven Design, 2003, ch. 2 "Communication and the Use of Language"]. Persona implication: the glossary is a *model artifact* that downstream code identifiers must match. It is not decoration.
- **Bounded Context (BC):** a model and its language are valid only inside an explicit boundary. The same word (e.g., "Account", "Customer") can mean different things in different BCs, and that is legitimate. Forcing a single enterprise-wide model is the anti-pattern [BOOK:Evans, DDD, ch. 14 "Maintaining Model Integrity"].
- **Context Map:** shows the relationships between BCs and teams. DDD-Crew lists nine patterns: Open-host Service, Conformist, Anticorruption Layer, Shared Kernel, Partnership, Customer/Supplier, Published Language, Separate Ways and Big Ball of Mud. It also lists three team relationships: mutually dependent, upstream/downstream and free [GIT:ddd-crew/context-mapping/README.md]. Their guidance is to prefer *small context maps that answer explicit questions* over one giant map, and to explain each pattern used [GIT:ddd-crew/context-mapping/README.md].
- **Tactical building blocks:** Entities have identity and lifecycle. Value Objects are immutable and defined by their attributes. Aggregates are consistency boundaries with a single root. Repositories are per aggregate. Domain Services hold stateless domain operations. Factories handle creation. Domain Events were added in the 2015 Reference [BOOK:Evans, DDD, ch. 5–6] [BOOK:Evans, DDD Reference, 2015].
- **Distillation / Core Domain:** spend the best talent and modeling effort on the core domain, and use off-the-shelf solutions or simpler designs everywhere else [BOOK:Evans, DDD, ch. 15 "Distillation"]. A **Domain Vision Statement** is a one-page artifact [BOOK:Evans, DDD, ch. 15].
- Quality bar: the model is "knowledge-crunched" with domain experts and refined continuously. A model that is not reflected in code (an "analysis model" disconnected from the implementation) counts as failure [BOOK:Evans, DDD, ch. 3 "Binding Model and Implementation"].

### 2. Vaughn Vernon — Implementing Domain-Driven Design (2013) and "Effective Aggregate Design" essays (2011)
- He gives four aggregate rules. (1) Model true invariants in consistency boundaries. (2) Design small aggregates. (3) Reference other aggregates by identity only. (4) Use eventual consistency outside the boundary, through domain events [WEB:https://www.dddcommunity.org/wp-content/uploads/files/pdf_articles/Vernon_2011_2.pdf] [BOOK:Vernon, IDDD, 2013, ch. 10 "Aggregates"]. Note: the essay comes in three parts; rules 1–2 are in Part I and rules 3–4 in Part II (the linked PDF), so the PDF alone does not cover all four [BOOK:Vernon, "Effective Aggregate Design" Parts I–III, 2011, from knowledge].
- One transaction should modify one aggregate instance. Breaking this rule is a smell that the boundary is wrong, unless an invariant truly spans the instances [BOOK:Vernon, IDDD, ch. 10].
- Large-cluster aggregates are an anti-pattern because they cause contention and performance problems [WEB:https://www.dddcommunity.org/wp-content/uploads/files/pdf_articles/Vernon_2011_2.pdf].
- Vernon gives practical patterns for context integration: REST and messaging between BCs, and domain events published reliably through an event store or outbox-like mechanism [BOOK:Vernon, IDDD, ch. 13 "Integrating Bounded Contexts", ch. 8 "Domain Events"].
- He treats strategic design as primary: subdomains, BCs and context maps come *before* tactical patterns. His shorter *Domain-Driven Design Distilled* (2016) makes this ordering explicit [BOOK:Vernon, DDD Distilled, 2016].
- **Aggregate Design Canvas** (DDD-Crew, inspired by the BC canvas): name, description, state transitions, enforced invariants, corrective policies, handled commands, created events, throughput (command rate, concurrent clients, which give the conflict chance) and size (event growth, instance lifetime) [GIT:ddd-crew/aggregate-design-canvas/README.md]. It makes explicit the trade-off between an invariant (enforced inside the boundary) and a corrective policy (eventual repair). That is exactly the decision an LLM tends to hand-wave.

### 3. Vlad Khononov — Learning Domain-Driven Design (O'Reilly, 2021/22)
- **Subdomain types.** *Core* is what the business does differently from competitors and gives it its competitive advantage. *Supporting* is necessary but not differentiating. *Generic* is solved the same way everywhere and can be bought [WEB:https://www.oreilly.com/library/view/learning-domain-driven-design/9781098100124/copyright-page01.html (search summary)]. Subdomain classifications change as the business changes [same].
- The type drives the design. Core gets rich domain models, event sourcing where it pays off, and in-house development. Supporting gets transaction script or active record and possibly outsourcing. Generic is bought or adopted as OSS [BOOK:Khononov, Learning DDD, ch. 1, ch. 10 "Design Heuristics"].
- Business-logic patterns are a spectrum: transaction script → active record → domain model → event-sourced domain model. Architecture patterns are layered → ports & adapters → CQRS. Both are chosen *per BC* from heuristics, not by fashion [BOOK:Khononov, Learning DDD, ch. 5–8, ch. 10].
- Communication patterns: model translation (stateless/stateful), outbox, saga, process manager [BOOK:Khononov, Learning DDD, ch. 9 "Communication Patterns"].
- **Bounded Context Canvas** (DDD-Crew, Nick Tune et al.) operationalises this. Its fields are: Name, Purpose, Strategic Classification (core/supporting/generic; revenue generator / engagement creator / compliance enforcer; Wardley evolution), Domain Roles, Inbound and Outbound Communication (messages typed as command/query/event, collaborators, relationship type), Ubiquitous Language, Business Decisions, Assumptions, Verification Metrics and Open Questions [GIT:ddd-crew/bounded-context-canvas/README.md]. This is the best ready-made template for a "BC card" handoff artifact.

### 4. Alberto Brandolini — EventStorming
- A workshop format built around domain events (orange stickies, past tense) on a timeline. It is meant to be lightweight and to need no computer support [WEB:https://en.wikipedia.org/wiki/Event_storming].
- It comes in three formats. **Big Picture** explores a whole business line with roughly 15–30 people. **Process Modelling** represents one business process. **Software Design** produces models for event-driven systems in DDD terms [WEB:https://www.avanscoperta.it/en/eventstorming/] [WEB:https://en.wikipedia.org/wiki/Event_storming].
- Grammar (Process/Design level): Actor → Command → Aggregate/System → Domain Event → Policy ("whenever X, then Y") → Command. It also uses Read Models, External Systems and **Hotspots** (pink: conflicts, questions, risks) [BOOK:Brandolini, Introducing EventStorming, Leanpub, ch. on notation] [UNVERIFIED exact colour conventions vary].
- Hotspots are a first-class output. Unresolved conflicts are surfaced, not smoothed over. Pivotal events and swimlanes suggest candidate BC boundaries [BOOK:Brandolini, Introducing EventStorming].
- Persona implication: an LLM can simulate the *grammar* (events → commands → policies → aggregates) as a structured textual artifact. It cannot simulate the domain experts in the room. Every event flow it produces must be marked **hypothesis** until it is validated against Discovery evidence, and a list of hotspots is mandatory.

### 5. Martin Kleppmann — Designing Data-Intensive Applications (2017; 2nd ed. with Chris Riccomini, O'Reilly, 2026)
- The 1st edition's three concerns are **Reliability** (keep working correctly despite hardware, software and human faults), **Scalability** (describe load with load parameters and performance with percentiles, p95/p99, not averages) and **Maintainability** (operability, simplicity, evolvability) [BOOK:Kleppmann, DDIA, 2017, ch. 1]. The 2nd edition reframes and extends these and adds cloud trade-offs [WEB:https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/] [UNVERIFIED exact 2nd-ed chapter structure].
- Data models and encoding: relational vs document vs graph is a fit question. Schema evolution needs backward *and* forward compatibility (Avro, Protobuf, Thrift field tags) because old and new code coexist during rolling deploys [BOOK:Kleppmann, DDIA, ch. 2, ch. 4].
- Replication (leader/follower, multi-leader, leaderless) and its anomalies: read-your-writes, monotonic reads, consistent prefix [BOOK:Kleppmann, DDIA, ch. 5].
- Partitioning by key range vs hash, the hot-spot problem, secondary-index partitioning (local vs global) and rebalancing [BOOK:Kleppmann, DDIA, ch. 6].
- Transactions and isolation levels (read committed, snapshot isolation, serializable). Watch for write skew and phantoms. "ACID" and "eventual consistency" are vague terms, and you must name the guarantee [BOOK:Kleppmann, DDIA, ch. 7, ch. 9].
- Derived data: systems of record vs derived data (caches, indexes, materialized views), CDC and event logs, and "unbundling the database" [BOOK:Kleppmann, DDIA, ch. 11–12]. Persona implication: every dataset in the data design must be labelled system-of-record or derived, with the derivation path stated.

### 6. Data modeling (conceptual / logical / physical) and data governance
- The three classic levels. **Conceptual** covers business entities and relationships with no attributes or technology. **Logical** adds attributes, keys and normalization, still DBMS-independent. **Physical** adds tables, types, indexes, partitioning and storage for a specific engine [BOOK:Simsion & Witt, Data Modeling Essentials, 3rd ed., 2005] [BOOK:DAMA, DMBOK2, 2017, ch. 5 "Data Modeling and Design"].
- Normalization (3NF/BCNF) applies to OLTP. Dimensional modeling applies to analytics: facts, conformed dimensions, a declared grain, and SCD types [BOOK:Kimball & Ross, The Data Warehouse Toolkit, 3rd ed., 2013]. "Declare the grain" is a hard quality bar for any analytics model.
- DAMA-DMBOK2 lists the knowledge areas: governance, architecture, modeling, storage and operations, security, integration and interoperability, document/content, reference and master data, warehousing/BI, metadata and data quality [BOOK:DAMA International, DMBOK2, 2017, ch. 1 "Data Management" wheel]. It defines Data Owner and Data Steward as accountable and responsible roles [BOOK:DMBOK2, ch. 3 "Data Governance"].
- Retention: every personal or regulated data class needs a purpose, a legal basis, a retention period and a deletion mechanism. GDPR Art. 5(1)(e) storage limitation and Art. 17 erasure apply [BOOK:GDPR text, Regulation (EU) 2016/679, Art. 5(1)(e), 17]. Erasure in event-sourced or append-only logs needs a design answer such as crypto-shredding [UNVERIFIED as an industry-standard term; widely used]. (Verifier: Art. 5(1)(e) = storage limitation and Art. 17 = right to erasure are correct.)
- **Data contracts:** the Open Data Contract Standard (ODCS, Bitol / Linux Foundation AI & Data, v3.1.0) is machine-readable YAML/JSON. It covers schema, data-quality rules, SLAs, stakeholders and roles, and since 3.1.0 also relationships and foreign keys [WEB:https://github.com/bitol-io/open-data-contract-standard/blob/main/README.md] [WEB:https://bitol.io/bitol-announces-odcs-v3-1-0-stronger-smarter-and-stricter/]. Persona implication: producer→consumer datasets get a contract file, the same way APIs get OpenAPI.
- Data Mesh ideas: domain-owned data products, data as a product, self-serve platform, federated computational governance. These align data ownership with BCs [BOOK:Dehghani, Data Mesh, O'Reilly, 2022].

### 7. API design — API-first, OpenAPI/AsyncAPI, Lauret, Google AIPs
- **API-first / design-first:** the contract (OpenAPI for HTTP, AsyncAPI for events) is written and reviewed *before* implementation. It then becomes the source for mocks, SDKs, docs and contract tests. The local SDD corpus calls this "spec-anchored": OpenAPI plus contract tests such as Pact or Specmatic keep spec and code aligned [LOCAL:ai/docs/spec-driven-development/spec-driven-development-arxiv.md:57,136-140].
- **AsyncAPI 3.0** separates *channels* (the messages that can flow on an address) from *operations* (`action: send|receive`, which references a channel and a subset of its messages). This makes channels and messages reusable across documents [WEB:https://www.asyncapi.com/docs/reference/specification/v3.0.0] [WEB:https://www.asyncapi.com/blog/release-notes-3.0.0].
- **Arnaud Lauret, The Design of Web APIs (Manning, 2019; 2nd ed. June 2025 [WEB:https://www.manning.com/books/the-design-of-web-apis-second-edition])** argues for designing from the consumer's goals, not the provider's internals. His "API goals canvas" asks Who / What / How / Inputs / Outputs / Goals. He also argues against exposing the data model or code ("provider's perspective" anti-pattern), and for designing for usability, evolvability and security together [BOOK:Lauret, The Design of Web APIs, 2019, ch. 2–3] [UNVERIFIED chapter numbers; the 2nd ed. was rewritten and may number them differently]. Persona implication: an API design must trace each operation to a consumer goal or use case from the PRD.
- **Google AIPs** (resource-oriented design) [GIT:aip-dev/google.aip.dev]:
  - AIP-158 Pagination: list RPCs **must** paginate *from the outset*, because adding it later is a breaking change. They use `page_size` / `page_token` / `next_page_token`, and page tokens **must** be opaque, URL-safe and not user-parseable [GIT:aip-dev/google.aip.dev/aip/general/0158.md].
  - AIP-155 Request identification: an optional `request_id` (UUID recommended) **must** guarantee idempotency [GIT:.../0155.md].
  - AIP-180 Backwards compatibility: existing clients **must not** break. Field types, defaults, resource names and value formats must not change within a major version [GIT:.../0180.md].
  - AIP-185 Versioning: major version only (`v1`), with alpha/beta channels such as `v1beta`. Beta must be a superset of stable. A newer interface-based option uses date versions `YYYY-MM-DD` [GIT:.../0185.md].
  - AIP-193 Errors: canonical codes, messages that are brief, actionable and do not assume expertise, a mandatory `ErrorInfo` with a machine-readable `reason` (≤63 chars) and `metadata` [GIT:.../0193.md].
- **RFC 9457 Problem Details for HTTP APIs** (July 2023, obsoletes RFC 7807). Members are `type` (URI), `title`, `status`, `detail` and `instance`, plus extension members, using media type `application/problem+json` [WEB:https://datatracker.ietf.org/doc/html/rfc9457]. The default error model for any HTTP API in the pipeline should be RFC 9457 unless an ecosystem standard (gRPC `google.rpc.Status`) applies.
- **Idempotency-Key header** (IETF httpapi draft, -07, Oct 2025, Standards Track intended). It makes POST and PATCH retry-safe. The key is client-generated (a UUID is recommended) and **must not** be reused with a different payload [WEB:https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-idempotency-key-header-07]. It is still a draft, so cite it as such. (Verifier: -07 was uploaded 2025-10-15 and is listed as expired since 2026-04-18; check the datatracker for a newer revision or RFC before citing.)
- **Richardson Maturity Model:** L0 is a single endpoint (RPC-over-HTTP). L1 adds resources. L2 adds HTTP verbs and status codes. L3 adds hypermedia controls (HATEOAS). Fowler notes it is a teaching model, not a definition of REST [BOOK:Fowler, "Richardson Maturity Model", martinfowler.com, 2010 (page blocked; well known)] [BOOK:Fielding, dissertation, 2000, ch. 5]. A practical bar is L2. L3 is optional and should be justified.
- Versioning strategies are URI major version, header/media-type, or date-based. Whichever is used, compatibility rules and a deprecation/sunset policy must be written down [GIT:.../0185.md]. The `Sunset` HTTP header is RFC 8594 (2019) [BOOK:RFC 8594, Wilde, 2019, from knowledge].

### 8. Enterprise Integration Patterns (Hohpe & Woolf, 2003) and event-driven architecture
- Four integration styles: file transfer, shared database, remote procedure invocation, messaging. Messaging is preferred for loose coupling, and a shared database is a coupling trap [BOOK:Hohpe & Woolf, Enterprise Integration Patterns, 2003, ch. 2].
- Pattern vocabulary: Message Channel (point-to-point vs publish-subscribe), Message (command / document / event message), Router (content-based, splitter, aggregator), Translator / Canonical Data Model, Endpoint (polling vs event-driven consumer, **Idempotent Receiver**), Dead Letter Channel, Guaranteed Delivery, Correlation Identifier, Process Manager [BOOK:Hohpe & Woolf, EIP, ch. 3–10].
- Fowler's four meanings of "event-driven" are event notification, event-carried state transfer, event sourcing and CQRS. A design must say which one it means [BOOK:Fowler, "What do you mean by Event-Driven?", 2017, martinfowler.com (blocked)] [UNVERIFIED wording].
- Delivery semantics: the realistic baseline is **at-least-once plus idempotent consumers**. "Exactly-once" holds only inside a specific system boundary, for example Kafka transactions [BOOK:Kleppmann, DDIA, ch. 11] [UNVERIFIED Kafka specifics].
- Ordering is per partition or key, not global. The design must name the ordering key, or state that order does not matter [BOOK:Kleppmann, DDIA, ch. 11].

### 9. Sagas and Transactional Outbox
- **Saga** (Garcia-Molina & Salem, 1987): a long-lived transaction split into local transactions, each with a compensating transaction [BOOK:Garcia-Molina & Salem, "Sagas", SIGMOD 1987]. Microservices variants are choreography (events) and orchestration (a central coordinator) [BOOK:Richardson, Microservices Patterns, Manning, 2018, ch. 4].
- A saga gives ACD without I, so it needs countermeasures: semantic lock, commutative updates, pessimistic view, reread value, version file, by value. Each step is compensatable, pivot or retriable [BOOK:Richardson, Microservices Patterns, ch. 4].
- **Transactional Outbox:** write the state change and the outgoing message in the *same* local DB transaction (outbox table). A relay then publishes it, either by polling publisher or by transaction-log tailing/CDC, for example Debezium. This avoids dual writes. The consequence is possible duplicate publication, so consumers must be idempotent [BOOK:Richardson, Microservices Patterns, ch. 3] (microservices.io page blocked).
- Persona implication: any design where a command handler "saves to DB and then publishes to the broker" without an outbox, CDC or event-sourced store is a **rejectable** defect.

---

## Real-world roles

Stage mapping summary: the Domain Architect is the anchor for this axis. Data Architect, API Designer and Integration Architect are Architecture-stage workers. The DBA and Data Engineer mainly review and slice work in Architecture and Tasks. The Data Steward / governance role belongs to the **shared pool** (it overlaps privacy/compliance).

### R1. Domain Architect / DDD Modeler
- **Real-world titles:** Domain Architect, Principal Engineer (DDD), Solution Architect (domain), "Domain Modeling Lead", EventStorming facilitator; DDD consultants. Often a staff or principal engineer and not a separate title [UNVERIFIED as a frequency claim].
- **Stages:** Discovery (light: glossary seed, Big Picture event timeline, hotspots), PRD (UL consistency review), **Architecture (primary)**, Tasks (slicing by BC and aggregate).
- **Mission:** Turn the validated problem into an explicit domain model: a classification of subdomains, bounded contexts with their own language, a context map, and aggregate designs that protect true invariants. Engineering effort should go where the business differentiates.
- **Mindset & principles:**
  - Language before structure: the UL glossary is the first artifact, and code identifiers must match it [BOOK:Evans, DDD, ch. 2].
  - Strategic before tactical: subdomains → BCs → context map → aggregates [BOOK:Vernon, DDD Distilled, 2016].
  - Invest by subdomain type: core gets rich models, generic gets buy [BOOK:Khononov, Learning DDD, ch. 1, 10].
  - Small aggregates, reference by ID, eventual consistency between aggregates [WEB:https://www.dddcommunity.org/wp-content/uploads/files/pdf_articles/Vernon_2011_2.pdf].
  - Keep context maps small and question-specific [GIT:ddd-crew/context-mapping/README.md].
  - Surface hotspots; never paper over ambiguity [BOOK:Brandolini, Introducing EventStorming].
- **OWNS:** UL glossary (per BC), subdomain classification, BC boundaries and BC canvases, context map with relationship patterns, aggregate design canvases (invariants vs corrective policies), domain event catalogue (names and meaning, not wire schema), domain hotspot list.
- **DOES NOT OWN:** physical schema (DBA / Data Architect), wire contracts (API Designer / Integration Architect), the infrastructure topology (Solution / Cloud Architect), product scope (PRD owner), team structure (Engineering management, though BC↔team alignment is advised).
- **Inputs needed:** Discovery handoff (problem, actors, jobs, current process, evidence), PRD (capabilities, user flows, business rules, NFRs, non-goals), existing system landscape and integrations, regulatory constraints (shared compliance).
- **Outputs/artifacts (industry formats):**
  - `glossary.md`: term | BC | definition | synonyms to avoid | example | source (PRD/Discovery ID).
  - `subdomains.md`: per subdomain, type (core/supporting/generic), rationale, build/buy/OSS, and optionally the Core Domain Chart axes (complexity × differentiation) [GIT:ddd-crew/bounded-context-canvas/README.md (references core-domain-charts)].
  - `bc-<name>.md` following the **Bounded Context Canvas** v5 fields [GIT:ddd-crew/bounded-context-canvas/README.md].
  - `context-map.md` (+ Mermaid, or Context Mapper CML [GIT:ddd-crew/context-mapping/README.md]): each edge carries upstream/downstream, pattern (OHS/PL/ACL/CF/CS/P/SK/SW) and the reason.
  - `aggregate-<name>.md` following the **Aggregate Design Canvas** (state transitions, invariants, corrective policies, commands→events, throughput, size) [GIT:ddd-crew/aggregate-design-canvas/README.md].
  - `event-storming.md`: a textual timeline (Actor → Command → Aggregate → Event → Policy → ...), with hotspots and with each item tagged *hypothesis* or *validated (evidence ID)*.
- **ACCEPTANCE criteria:**
  - [ ] Every PRD capability/requirement ID maps to at least one BC, and every BC maps back to at least one requirement (no orphan contexts).
  - [ ] Every core/supporting/generic classification has a written rationale. Generic subdomains have a build/buy decision.
  - [ ] Every glossary term is defined within exactly one BC. Homonyms across BCs are listed explicitly with their per-BC meanings.
  - [ ] Every context-map edge names a direction and a pattern. Any edge to a legacy or external system uses ACL or Conformist explicitly.
  - [ ] Each aggregate lists at least one invariant it enforces. No aggregate holds a direct object reference to another aggregate (IDs only).
  - [ ] A use case that changes more than one aggregate in one transaction is either justified by a named invariant or redesigned with events + corrective policy.
  - [ ] Domain events are past tense, named in UL, and owned by exactly one BC.
  - [ ] The hotspot list is non-empty or explicitly "none, validated by <evidence>". Each hotspot has an owner or a "question for PRD/Discovery" route.
- **REFUSAL criteria:**
  - *blocked:* no PRD requirement IDs or business rules to model against. No actors or processes in the Discovery handoff. Glossary terms are needed but domain sources are absent (it will not invent domain rules).
  - *rejected:* upstream PRD uses one term with conflicting meanings and does not flag it. The PRD contains contradictory business rules, for example "orders cannot be modified after payment" alongside a flow that edits paid orders. The PRD prescribes a data or DB structure as a requirement without a reason.
  - *out_of_scope:* choosing a DB engine or cloud service; org-chart and team design; pricing or GTM questions; writing production code.
- **Anti-patterns:** anemic domain model everywhere (or the opposite: rich models for a generic CRUD subdomain); one enterprise canonical model; BCs drawn as microservices by default (BC ≠ deployment unit, which is a separate decision); entity-centric aggregates mirroring tables; mega-aggregates; event names that are CRUD ("OrderUpdated"); context map with unlabeled arrows; "DDD theatre" (patterns without invariants).
- **Handoffs:** receives from the PRD handoff (and the Discovery glossary seed). Delivers to Data Architect (BCs and aggregates → logical model), API Designer (BC public interface, commands/queries/events), Integration Architect (context map edges → integration styles), Tasks stage (BC/aggregate as slicing unit), and Traceability owner (requirement → BC → aggregate links).

### R2. Data Architect
- **Real-world titles:** Data Architect, Enterprise Data Architect, Data Modeler, Information Architect (data sense), Analytics Architect.
- **Stages:** PRD (data requirements review: data classes, retention, reporting needs), **Architecture (primary)**, shared-pool consumer (privacy).
- **Mission:** Define how data is structured, owned, stored, moved, governed and retained across the system so that it is correct, consistent at the agreed level, evolvable and compliant.
- **Mindset & principles:**
  - Conceptual → logical → physical, with each level traceable to the one above [BOOK:DMBOK2, ch. 5].
  - One system of record per data element. Everything else is derived, and the derivation path is documented [BOOK:Kleppmann, DDIA, ch. 11–12].
  - Name the consistency guarantee and the isolation level, not "ACID / eventual" [BOOK:Kleppmann, DDIA, ch. 7, 9].
  - Schema evolution is a first-class constraint, so the design needs backward and forward compatibility [BOOK:Kleppmann, DDIA, ch. 4].
  - Data ownership aligns with BCs and domains (no shared database across BCs) [BOOK:Hohpe & Woolf, EIP, ch. 2] [BOOK:Dehghani, Data Mesh, 2022].
  - Every data class gets a classification, retention period and deletion path [BOOK:DMBOK2, ch. 3, 7].
- **OWNS:** conceptual and logical data models; data inventory/catalogue with classification (public/internal/confidential/restricted; PII/PHI/PCI flags); system-of-record map; consistency and replication strategy per store; partitioning-key rationale at the logical level; retention and deletion design; analytical model approach (dimensional grain); data contracts for shared datasets.
- **DOES NOT OWN:** domain boundaries (Domain Architect, but must agree with them); physical tuning, index choices, backup ops (DBA); pipeline implementation (Data Engineer); legal basis decisions (Privacy/Compliance in the shared pool, which it consults); API wire shapes (API Designer).
- **Inputs needed:** BC canvases + aggregates + glossary; PRD data requirements (entities mentioned, reports/metrics, volumes, retention, jurisdictions); NFRs (latency, throughput, RPO/RTO, growth); compliance constraints from the shared privacy role; analytics event requirements from the shared product-analytics role.
- **Outputs/artifacts:**
  - `data-model-conceptual.md`: an ER diagram (Mermaid `erDiagram`) of business entities per BC.
  - `data-model-logical.md`: entities, attributes, types (logical), keys, relationships, cardinality, normalization notes, owning BC.
  - `data-inventory.md`: table with element | BC owner | system of record | classification | PII? | retention | deletion mechanism | lawful-basis ref (from compliance).
  - `consistency-and-storage.md`: per store, data-model type (relational/document/KV/graph/log), consistency/isolation level, replication mode, partition key + hot-spot analysis, expected volume and growth.
  - `data-contracts/*.yaml` in **ODCS v3** form for every dataset consumed outside its owning BC [WEB:https://github.com/bitol-io/open-data-contract-standard/blob/main/README.md].
  - ADRs for each storage/consistency decision.
- **ACCEPTANCE criteria:**
  - [ ] Every logical entity traces to a glossary term and an owning BC. No entity is owned by two BCs.
  - [ ] Every data element has exactly one system of record. Each derived store (cache, search index, read model, warehouse) names its source and its staleness bound.
  - [ ] Every store states its consistency guarantee in precise terms (e.g., "snapshot isolation; read-your-writes via leader reads for the user's own profile").
  - [ ] Every PII or regulated class has retention + deletion mechanism, including in logs, backups, event streams and analytics copies.
  - [ ] Partition or shard keys are justified against access patterns and hot-key risk, or partitioning is explicitly N/A with volume numbers.
  - [ ] Schema-evolution policy is stated (additive-only within a version; how field removal happens).
  - [ ] Analytical models declare grain.
  - [ ] Volume and growth estimates come from the PRD/NFR numbers, or they are marked as assumptions with an owner.
- **REFUSAL criteria:**
  - *blocked:* no volume/latency/RPO-RTO NFRs, so the architect cannot size or choose consistency (it should ask, not guess); no data classification input for personal data; no BC/ownership model.
  - *rejected:* the domain model has entities shared by multiple BCs without a Shared Kernel decision; PRD requires "real-time everywhere" and "strong consistency globally" with no numbers; a design proposes a shared database between BCs as the integration mechanism; personal data is collected with no purpose stated.
  - *out_of_scope:* lawful-basis/legal interpretation (shared compliance); BI dashboard design (product analytics); vendor procurement.
- **Anti-patterns:** physical model presented as the domain model; "one big shared DB"; "we'll use NoSQL for scale" without access patterns; dual writes to DB and cache/broker; retention set as "forever" by default; PII copied into logs and analytics without inventory; using averages instead of percentiles for sizing.
- **Handoffs:** receives from the Domain Architect and the PRD handoff, and consults Privacy/Compliance and Product Analytics (shared). Delivers to DBA (logical → physical), Data Engineer (contracts, lineage, pipelines), API Designer (resource shapes must not leak the physical model), and the Tasks stage (migration and backfill tasks).

### R3. Data Engineer
- **Real-world titles:** Data Engineer, Analytics Engineer, Data Platform Engineer, Streaming Engineer.
- **Stages:** Architecture (feasibility and pipeline design review), **Tasks (primary)**: pipeline, CDC, backfill and data-quality tasks.
- **Mission:** Build and run reliable data movement and transformation (ingestion, CDC, streaming, batch, warehouse models) that honors the data contracts and quality rules.
- **Mindset & principles:** the data engineering lifecycle is generation → storage → ingestion → transformation → serving, with six undercurrents: security, data management, DataOps, data architecture, orchestration and software engineering [BOOK:Reis & Housley, Fundamentals of Data Engineering, O'Reilly, 2022, ch. 2]. Pipelines must be idempotent and re-runnable, backfill is designed up front, and data quality is tested as code [BOOK:Reis & Housley, ch. 8] [UNVERIFIED chapter]. Contracts are owned by the producer [WEB:https://github.com/bitol-io/open-data-contract-standard/blob/main/README.md].
- **OWNS:** pipeline design (batch vs stream, CDC source, schedule), data-quality checks implementing contract rules, lineage documentation, backfill/replay plan, transformation models.
- **DOES NOT OWN:** what the data means (Domain/Data Architect), which metrics matter (product analytics), source system schema (owning BC team / DBA), retention policy (Data Architect + compliance, though it must implement deletion propagation).
- **Inputs needed:** data contracts (ODCS), logical model, system-of-record map, freshness SLAs, volume estimates, retention/deletion rules.
- **Outputs/artifacts:** pipeline spec (source → transforms → sink, trigger, SLA, idempotency key, late-data handling); data-quality test list mapped to contract rules; lineage graph; backfill runbook; task breakdown.
- **ACCEPTANCE criteria:**
  - [ ] Each pipeline names its idempotency/dedup key and how a re-run of the same window behaves.
  - [ ] Freshness SLA is numeric and has an alert.
  - [ ] Every contract quality rule has an automated check.
  - [ ] Deletion/erasure requests propagate to every derived dataset (listed).
  - [ ] Schema-change handling is defined (fail, quarantine or evolve).
  - [ ] Late, out-of-order and duplicate events are handled explicitly.
- **REFUSAL criteria:**
  - *blocked:* no contract or schema for the source; no freshness requirement; no system-of-record designation.
  - *rejected:* the source is read directly from another BC's OLTP tables with no contract or CDC agreement; a "dual write" is proposed as the ingestion mechanism; retention conflicts between source and warehouse.
  - *out_of_scope:* choosing KPIs; building dashboards; redefining domain entities.
- **Anti-patterns:** non-idempotent appends; pipelines with no backfill story; silent schema drift; copying PII wholesale into lakes; the "data swamp" with no lineage.
- **Handoffs:** receives from the Data Architect and Integration Architect. Delivers to the Tasks stage, SRE/operability (shared: alerts, runbooks) and product analytics (shared).

### R4. API Designer / API Product Owner
- **Real-world titles:** API Designer, API Architect, API Product Manager / API Product Owner, Developer Experience (DX) Lead, API Governance lead / API Review Board member.
- **Stages:** PRD (API-as-product requirements when the API is a product or partner-facing: consumers, goals, SLAs, monetization out of scope), **Architecture (primary: contract design)**, Tasks (contract tests, mocks, SDK tasks).
- **Mission:** Design consumer-centric, consistent, evolvable and secure interface contracts (OpenAPI/AsyncAPI/gRPC) *before* implementation, and govern their lifecycle (versioning, deprecation).
- **Mindset & principles:**
  - Consumer goals before provider internals; do not expose the data model [BOOK:Lauret, The Design of Web APIs, ch. 2–3].
  - Design-first, spec-anchored, contract-tested [LOCAL:ai/docs/spec-driven-development/spec-driven-development-arxiv.md:57,136-140].
  - Consistency through a style guide (Google AIP-style resource-oriented design) [GIT:aip-dev/google.aip.dev].
  - Breaking changes are a contract violation. Compatibility rules are explicit [GIT:.../0180.md].
  - Paginate lists from day one; use opaque page tokens [GIT:.../0158.md].
  - Make unsafe operations retry-safe (request_id / Idempotency-Key) [GIT:.../0155.md] [WEB:https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-idempotency-key-header-07].
  - One error model: RFC 9457 problem details, machine-readable reason codes, actionable messages [WEB:https://datatracker.ietf.org/doc/html/rfc9457] [GIT:.../0193.md].
- **OWNS:** API goals canvas / consumer list; OpenAPI 3.1 and/or AsyncAPI 3.0 documents; API style guide (or adoption of an existing one); error catalogue; versioning and deprecation policy; examples; mock server config; contract-test expectations.
- **DOES NOT OWN:** domain semantics (Domain Architect); authN/authZ model details (shared security, which it must incorporate: scopes per operation); infrastructure (gateway selection belongs to the Solution Architect); internal storage.
- **Inputs needed:** PRD user flows and use cases with IDs; actors/consumers (internal UI, partners, other BCs); BC canvas inbound/outbound messages; aggregate commands and events; NFRs (latency, rate limits, payload sizes); security requirements (shared).
- **Outputs/artifacts:**
  - `api/goals-canvas.md`: Who | What | How | Inputs | Outputs | Goals → operation [BOOK:Lauret, ch. 2].
  - `api/openapi.yaml` (OpenAPI 3.1) that passes a linter (e.g., Spectral ruleset) [UNVERIFIED as a universal standard; common practice].
  - `api/asyncapi.yaml` (AsyncAPI 3.0) for events: channels, operations (send/receive), messages, with schemas [WEB:https://www.asyncapi.com/docs/reference/specification/v3.0.0].
  - `api/errors.md`: problem `type` URIs, HTTP status, `reason`, when emitted, client remediation.
  - `api/versioning-policy.md`: version scheme, compatibility rules, deprecation window, sunset signalling.
  - ADRs: REST vs gRPC vs GraphQL vs events per interface.
- **ACCEPTANCE criteria:**
  - [ ] Every operation traces to a PRD use case/requirement ID and a named consumer. Every PRD flow needing system interaction has operation(s).
  - [ ] Resource and field names use the UL of the owning BC. No table or column names leak, and no internal IDs other than resource IDs leak.
  - [ ] Every collection endpoint is paginated (`page_size`/`page_token` or cursor). Tokens are opaque. Max page size is documented.
  - [ ] Every non-idempotent mutation (POST/PATCH, or create/act RPCs) supports an idempotency key, or justifies why not. Behaviour on key reuse with a different payload is specified (error).
  - [ ] All errors use one model (RFC 9457 for HTTP) with a documented `type` per error. 4xx vs 5xx are used correctly. No stack traces or internal hostnames appear in `detail`.
  - [ ] HTTP semantics (RMM L2): correct methods, status codes (201 + Location on create, 404 vs 403 policy stated, 409 for conflicts, 412 for failed preconditions with ETags where concurrency matters).
  - [ ] Security scheme declared per operation (from shared security).
  - [ ] A versioning policy exists, and the spec version and breaking-change rules are stated.
  - [ ] Every spec lints clean and every schema has examples. Async messages carry id, type, source, time and correlation id (a CloudEvents-like envelope [UNVERIFIED as mandated]).
- **REFUSAL criteria:**
  - *blocked:* no consumers identified; no use cases/flows with IDs; no auth requirements for externally exposed APIs.
  - *rejected:* PRD or architecture asks to "expose the database tables as REST" / auto-generate the API from the ORM for external consumers; a change to an existing published contract is breaking within the same major version; the domain model has unresolved homonyms on public resource names.
  - *out_of_scope:* API monetization/pricing and developer marketing (GTM extension point); gateway vendor selection; SDK publishing logistics.
- **Anti-patterns:** CRUD-over-tables APIs; chatty APIs that need N calls per screen; verbs in URIs at L0/L1 with every error returned as 200 plus an error body; inconsistent naming and casing; pagination added later; offset pagination on large, mutable sets; leaking internal enums; version-per-endpoint chaos; spec written after the code (documentation, not contract).
- **Handoffs:** receives from the Domain Architect, the PRD handoff and shared security. Delivers to the Integration Architect (async contracts), the Tasks stage (contract-test tasks, mock-first frontend tasks) and the Traceability owner (requirement → operation).

### R5. Integration Architect
- **Real-world titles:** Integration Architect, Enterprise Integration Architect, Middleware/Messaging Architect, Event-Driven Architect, iPaaS architect.
- **Stages:** **Architecture (primary)**, Tasks (integration slices, consumer idempotency, DLQ handling).
- **Mission:** Choose and specify how BCs and external systems communicate (sync vs async, styles, patterns, delivery guarantees, failure handling) so cross-boundary workflows are correct under partial failure.
- **Mindset & principles:**
  - Prefer messaging over a shared database. Choose the integration style deliberately [BOOK:Hohpe & Woolf, EIP, ch. 2].
  - Assume at-least-once delivery, and make every consumer an Idempotent Receiver [BOOK:Hohpe & Woolf, EIP, "Idempotent Receiver"].
  - No dual writes: use a Transactional Outbox or CDC [BOOK:Richardson, Microservices Patterns, ch. 3].
  - Distributed workflows use sagas with explicit compensations and isolation countermeasures [BOOK:Richardson, ch. 4] [BOOK:Garcia-Molina & Salem, 1987].
  - ACLs protect the domain from upstream/legacy models [GIT:ddd-crew/context-mapping/README.md].
  - Name which "event-driven" is meant (notification vs state transfer vs sourcing) [UNVERIFIED Fowler 2017 wording].
- **OWNS:** integration view (which edges are sync/async, which EIP patterns); event catalogue at the wire level (with API Designer: AsyncAPI); saga/process designs (state machine, compensations, timeouts); delivery guarantees, ordering keys, DLQ and retry policies; ACL/translator specs for external systems.
- **DOES NOT OWN:** the domain meaning of events (Domain Architect); broker operations and capacity (SRE/platform); synchronous API style (API Designer); data warehouse pipelines (Data Engineer).
- **Inputs needed:** context map; BC canvases (inbound/outbound messages); aggregate commands and events; external system catalogue (protocols, SLAs, rate limits); NFRs (latency, availability, ordering needs); consistency requirements from the Data Architect.
- **Outputs/artifacts:**
  - `integration-view.md`: table per context-map edge with style (sync REST/gRPC, async event, command message, file, CDC), pattern (OHS/PL/ACL), guarantee, ordering key, timeout/retry, DLQ.
  - `sagas/<name>.md`: steps (local txn, compensating txn, step type compensatable/pivot/retriable), orchestration vs choreography, timeouts, isolation countermeasures, Mermaid state or sequence diagram.
  - `outbox-and-delivery.md`: outbox/CDC mechanism, dedup keys, consumer idempotency storage, retention of dedup records.
  - AsyncAPI documents (co-owned with the API Designer).
- **ACCEPTANCE criteria:**
  - [ ] Every context-map edge has an integration style and a failure behavior (timeout, retry with backoff, circuit breaker or fallback, DLQ).
  - [ ] No producer performs a DB write + broker publish without outbox, CDC or event store.
  - [ ] Every consumer names its dedup/idempotency key and where processed IDs are stored, and for how long.
  - [ ] Every saga lists each step's compensation (or why it is pivot or retriable) and the user-visible intermediate states. Lack of isolation is addressed.
  - [ ] Ordering requirements are named per stream, with a partition key.
  - [ ] Schema evolution rules for events are stated (additive; versioned type names for breaking changes).
  - [ ] Synchronous call chains across BCs have a stated depth limit and latency budget, or are replaced by async.
- **REFUSAL criteria:**
  - *blocked:* no context map or external-system list; no consistency requirement for a cross-BC workflow ("must the payment and the order be atomic for the user?").
  - *rejected:* the design requires distributed 2PC across services/brokers with no justification; a shared database is used as the integration channel between BCs; "exactly-once" is claimed end-to-end with no mechanism; a saga has no compensations.
  - *out_of_scope:* broker cluster sizing and ops (SRE/platform); vendor contract negotiation; business process re-engineering.
- **Anti-patterns:** distributed monolith (sync chains across all services); event soup without ownership; events carrying entire entities "just in case"; using events as remote commands without saying so; ignoring poison messages; global ordering assumptions; ESB holding business logic ("smart pipes"), the opposite of "smart endpoints and dumb pipes" [BOOK:Lewis & Fowler, "Microservices", martinfowler.com, 2014].
- **Handoffs:** receives from the Domain Architect, Data Architect and API Designer. Delivers to SRE/operability (shared: DLQ alerts, runbooks), security (shared: message auth/encryption) and the Tasks stage.

### R6. Database Administrator (DBA) / Database Reliability Engineer
- **Real-world titles:** DBA, Database Engineer, Database Reliability Engineer (DBRE), Database Performance Engineer.
- **Stages:** Architecture (physical design review), **Tasks (migrations, indexes, backup/restore tasks)**.
- **Mission:** Turn the logical model into a physical design that is performant, recoverable, secure and safely changeable, and guard production data during change.
- **Mindset & principles:** the DBRE view is that databases are managed like the rest of the stack, with automation, migrations as code, recoverability tested and not assumed, and SLO-driven work [BOOK:Campbell & Majors, Database Reliability Engineering, O'Reilly, 2017]. Use expand/contract (parallel change) for zero-downtime schema changes [BOOK:Ambler & Sadalage, Refactoring Databases, 2006 (transition-period refactorings)]. The "expand/contract" / "ParallelChange" name is usually credited to Danilo Sato's 2014 bliki entry on martinfowler.com rather than to the book [UNVERIFIED — site blocked]. Least privilege applies, and a backup that has not been restored is not a backup [UNVERIFIED as quoted maxim; paraphrase of common practice].
- **OWNS:** physical schema (DDL), data types, constraints, indexes, partitioning implementation, migration scripts and their ordering, backup/restore and PITR configuration to meet RPO/RTO, DB access roles, query performance review.
- **DOES NOT OWN:** logical semantics (Data Architect), domain invariants (Domain Architect, though DB constraints may enforce some), application ORM code, the engine choice alone (shared ADR with the architects).
- **Inputs needed:** logical model, access patterns and query list, volumes/growth, RPO/RTO, consistency/isolation needs, retention/deletion rules, security classification.
- **Outputs/artifacts:** physical model (DDL or migration files); index plan mapped to queries; migration plan (expand → migrate/backfill → contract, with rollback per step); backup/restore and PITR plan with a restore drill; access-role matrix.
- **ACCEPTANCE criteria:**
  - [ ] Every listed critical query has a supporting index or a justification. No unbounded full scans on large tables in hot paths.
  - [ ] Constraints (PK, FK where appropriate, NOT NULL, unique, check) enforce stated invariants that the DB can enforce.
  - [ ] Every migration is backward-compatible with the previous app version (expand/contract), is reversible or has a documented forward fix, and has an estimated lock and duration.
  - [ ] RPO/RTO are met by the configured backup/PITR, and a restore test is scheduled.
  - [ ] Isolation level is set explicitly where the Data Architect required it.
  - [ ] Deletion and retention jobs exist for every retained class.
  - [ ] PII columns have encryption/masking decisions recorded.
- **REFUSAL criteria:**
  - *blocked:* no access patterns or queries; no RPO/RTO; no volume estimate.
  - *rejected:* a destructive migration (drop/rename column) is shipped in the same release as code that stops using it; an app connects as DB superuser; a schema design relies on application-only enforcement for a critical uniqueness invariant without justification; the logical model has no keys.
  - *out_of_scope:* domain modeling, API design, BI reporting.
- **Anti-patterns:** EAV/"generic attributes" tables for everything; missing FK/unique constraints "for flexibility"; index-everything; untested backups; migrations run by hand; ORM-generated schemas accepted unreviewed.
- **Handoffs:** receives from the Data Architect. Delivers to the Tasks stage (migration tasks with ordering), SRE/operability (backup monitoring) and security (access roles).

### R7. Data Steward / Data Governance Lead (shared-pool adjacent)
- **Real-world titles:** Data Steward, Data Governance Manager, Data Owner (business), Records Manager, Data Protection Officer (DPO: legal side, separate).
- **Stages:** **Shared** (invoked by PRD for retention requirements and by Architecture for the data inventory). Best merged into the shared privacy/compliance worker, with a "data governance" checklist, rather than kept as a separate persona.
- **Mission:** Make sure data is defined, classified, quality-controlled, retained and disposed of per policy and regulation, with clear accountable owners.
- **Mindset & principles:** governance is about decision rights and accountability, with an owner (accountable) and a steward (responsible) [BOOK:DMBOK2, ch. 3]; collect data minimally and for a stated purpose; retention is purpose-bound [UNVERIFIED GDPR Art. 5 citation precision]; "federated computational governance" means policies as code where possible [BOOK:Dehghani, Data Mesh, 2022].
- **OWNS:** classification scheme, retention schedule, data-owner assignment per domain, data-quality dimensions and thresholds (accuracy, completeness, timeliness, uniqueness, validity, consistency [BOOK:DMBOK2, ch. 13] [UNVERIFIED exact list]).
- **DOES NOT OWN:** legal interpretation (DPO/counsel); schema design; pipelines.
- **ACCEPTANCE:** every data class has owner, classification, retention, disposal method and quality thresholds; a retention schedule exists for logs and backups as well as primary stores.
- **REFUSAL:** *blocked*: jurisdictions/regulatory regime unknown for personal data. *rejected*: personal data with no purpose or owner. *out_of_scope*: legal advice.
- **Anti-patterns:** governance as after-the-fact documentation; "retain everything, decide later"; ownership assigned to IT rather than the business domain.
- **Handoffs:** consulted by the Data Architect, Data Engineer and PRD owner. Feeds the Traceability owner (requirement → data class → retention control).

---

## Implications for agentic personas

### What to split vs. merge
- **Architecture-stage workers (recommended 4):**
  1. `domain-modeler`: subdomains, glossary, BC canvases, context map, aggregates, textual EventStorming.
  2. `data-architect`: absorbs the DBA *design review* checklist (physical design, migrations strategy, RPO/RTO) for small or medium projects, and splits off a separate `dba-reviewer` only when there is heavy existing-DB or brownfield migration work.
  3. `api-designer`: OpenAPI + AsyncAPI authoring, style, errors, versioning.
  4. `integration-architect`: integration view, sagas, outbox, delivery guarantees.
  The Data Engineer is better as a **Tasks-stage** specialist (pipeline/backfill slicing), or a conditional Architecture worker that runs only when the PRD has analytics/ETL scope.
- **Shared pool:** merge the Data Steward into `privacy-compliance` (data classification, retention schedule, erasure). The Data Architect *invokes* it, and the orchestrator (not a worker) does the invoking, because workers cannot spawn subagents [LOCAL:ai/docs/claude-code/subagents/creating-custom-subagents.md:295]. The orchestrator must therefore sequence: domain-modeler → data-architect → (privacy-compliance) → api-designer ∥ integration-architect → critic.
- **Discovery stage:** do not run a full domain modeler. Run a lightweight "domain glossary + Big Picture timeline + hotspots" pass (often the Discovery researcher can do it with a checklist) so Architecture inherits the language seed.
- **PRD stage:** a `data-and-interface-requirements` checklist (data classes, retention, volumes, consumers of any API, integration with external systems) reviewed by the PRD critic. This avoids the "blocked" refusals later.
- **Tasks stage:** slicing heuristics come from this axis. Use one task per aggregate behaviour (command → event) or per contract operation. Migrations follow expand/contract ordering. Contract tests come before implementation. Consumer idempotency is its own task.

### What an LLM tends to get wrong here
- **Mirroring tables as aggregates and resources.** LLMs default to entity-per-table CRUD: Order, OrderItem and Customer as aggregates, with REST CRUD on each. Countermeasure: require ≥1 invariant per aggregate and a consumer goal per operation. Reject otherwise.
- **Over-applying DDD and microservices.** Every subdomain gets event sourcing and CQRS. Countermeasure: the subdomain type must justify the pattern (Khononov heuristics), and generic → buy/CRUD is the default.
- **BC = microservice by assumption.** Force a separate deployment ADR.
- **Inventing domain rules.** The model fills gaps with plausible business rules. Countermeasure: every invariant and policy cites a PRD/Discovery ID or is tagged `assumption` and routed as an open question. A hotspot list is required.
- **Vague consistency words.** "Eventually consistent", "ACID", "real-time" with no numbers. Countermeasure: a lint-like rule rejects these terms unless qualified by a guarantee/isolation level or a numeric staleness bound.
- **Dual writes and missing idempotency.** LLM-generated designs routinely "save then publish" and assume exactly-once. Countermeasure: a hard checklist item and a grep-able rule in the critic.
- **Error and pagination afterthoughts.** Error responses invented per endpoint; list endpoints without pagination; offset pagination. Countermeasure: OpenAPI lint rules.
- **Spec drift across artifacts.** The glossary says "Booking", the OpenAPI says "Reservation", the DDL says `orders`. Countermeasure: a deterministic cross-artifact term check (glossary terms vs schema names vs DDL identifiers, with an allowed-alias table).
- **Retention omission.** Retention is mentioned for the primary DB but not for logs, events, backups and analytics copies.
- **Invalid specs.** Hallucinated OpenAPI/AsyncAPI keywords, or mixing AsyncAPI 2.x `publish/subscribe` with the 3.0 `operations.action`. Countermeasure: schema validation is a tool step, not an LLM judgement.

### What must be a hard gate (deterministic where possible)
- **Architecture ENTRY gate (on PRD handoff):** blocked if missing any of: requirement IDs, actors/consumers, business rules list, volume/latency/RPO-RTO NFRs (or explicit "assumption" values with an owner), data classes containing personal data flagged, external systems list. Rejected if: conflicting term definitions not flagged, contradictory rules, or prescriptive DB/table structure presented as requirements.
- **Architecture EXIT gate (domain/data/API portion):**
  - `openapi.yaml` / `asyncapi.yaml` validate against their official JSON Schemas and pass the lint ruleset (pagination present, error model = problem+json, idempotency on unsafe ops, security on every op). Deterministic: tool/hook.
  - ODCS contracts validate against the ODCS schema [WEB:https://github.com/bitol-io/open-data-contract-standard/blob/main/README.md].
  - Traceability: 100% of PRD functional requirement IDs map to ≥1 BC and to ≥1 operation, event or explicit "no interface" note. No orphan operations. Deterministic: script over the ID tables.
  - Glossary consistency check: every public schema name is either a glossary term or a declared alias.
  - Data inventory completeness: every PII-flagged element has retention + deletion mechanism + owner (table completeness check).
  - Critic (LLM) checklist for judgement items: aggregate invariants are real, the subdomain classification rationale is plausible, saga compensations make business sense, no dual writes, consistency claims are precise.
- **Tasks-stage ENTRY gate (on Architecture handoff):** rejected if the contracts are unvalidated, if a migration plan has destructive steps without expand/contract, or if a cross-BC workflow lacks a saga/consistency decision.
- **Refusal output format:** each worker should emit a machine-readable refusal block, `{status: blocked|rejected|out_of_scope, rule_id, evidence (file:line or requirement ID), needed_from (stage/role), suggested_question}`. This lets the orchestrator route a "blocked" back to PRD through the handoff file, and lets the Traceability owner record it.

### Persona prompt hints
- Give each worker its canonical template (BC Canvas, Aggregate Design Canvas, ODCS, OpenAPI/AsyncAPI skeleton, saga template) as a file the worker must fill. LLMs follow templates more reliably than prose instructions, and this matches the harness pattern of artifact-validation hooks that check required sections [LOCAL:dev/research/2026-04-25-harness-engineering-research.md:107].
- Make "assumption" a typed value in every artifact (e.g., `assumption: true, owner: prd, question: ...`). The exit critic then counts the assumptions and fails above a threshold for core-domain items.
- Order matters. Generating API specs before aggregates and the context map exist produces CRUD-over-tables. The orchestrator should enforce the dependency order and pass only file paths, not summaries, between workers, so that the names stay exact.

---

## Sources
1. DDD-Crew, *Context Mapping* (README, cheat sheet), GitHub: https://github.com/ddd-crew/context-mapping [GIT, cloned 2026-10-02]
2. DDD-Crew, *The Bounded Context Canvas* v5, GitHub: https://github.com/ddd-crew/bounded-context-canvas [GIT]
3. DDD-Crew, *The Aggregate Design Canvas* v1.1, GitHub: https://github.com/ddd-crew/aggregate-design-canvas [GIT]
4. Google AIP-158 Pagination, source: https://github.com/aip-dev/google.aip.dev/blob/master/aip/general/0158.md [GIT]
5. Google AIP-155 Request identification: https://github.com/aip-dev/google.aip.dev/blob/master/aip/general/0155.md [GIT]
6. Google AIP-180 Backwards compatibility: https://github.com/aip-dev/google.aip.dev/blob/master/aip/general/0180.md [GIT]
7. Google AIP-185 API Versioning: https://github.com/aip-dev/google.aip.dev/blob/master/aip/general/0185.md [GIT]
8. Google AIP-193 Errors: https://github.com/aip-dev/google.aip.dev/blob/master/aip/general/0193.md [GIT]
9. RFC 9457, *Problem Details for HTTP APIs* (Nottingham, Wilde, Dalal, July 2023): https://datatracker.ietf.org/doc/html/rfc9457 [WEB via search summary]
10. IETF draft-ietf-httpapi-idempotency-key-header-07 (Oct 2025): https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-idempotency-key-header-07 [WEB via search summary]
11. Khononov, V., *Learning Domain-Driven Design*, O'Reilly, 2021/22: https://www.oreilly.com/library/view/learning-domain-driven-design/9781098100124/ [WEB + BOOK]
12. Kleppmann, M. & Riccomini, C., *Designing Data-Intensive Applications*, 2nd ed., O'Reilly, 2026 (confirmed early 2026: https://martin.kleppmann.com/2026/03/24/designing-data-intensive-applications-2e.html): https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ [WEB]; 1st ed. 2017 [BOOK]
13. Brandolini, A., EventStorming formats: https://www.avanscoperta.it/en/eventstorming/ ; https://en.wikipedia.org/wiki/Event_storming ; *Introducing EventStorming*, Leanpub: https://www.eventstorming.com/book/ [WEB + BOOK]
14. Vernon, V., "Effective Aggregate Design Part II", 2011: https://www.dddcommunity.org/wp-content/uploads/files/pdf_articles/Vernon_2011_2.pdf [WEB via search summary]; *Implementing Domain-Driven Design*, Addison-Wesley, 2013; *Domain-Driven Design Distilled*, 2016 [BOOK]
15. AsyncAPI 3.0.0 specification and release notes: https://www.asyncapi.com/docs/reference/specification/v3.0.0 ; https://www.asyncapi.com/blog/release-notes-3.0.0 [WEB via search summary]
16. Bitol, Open Data Contract Standard (ODCS) v3.x: https://github.com/bitol-io/open-data-contract-standard/blob/main/README.md ; https://bitol.io/bitol-announces-odcs-v3-1-0-stronger-smarter-and-stricter/ [WEB via search summary]
17. Local: /home/user/ai-study-library/ai/docs/spec-driven-development/spec-driven-development-arxiv.md (spec-anchored OpenAPI + contract testing) [LOCAL]
18. Local: /home/user/ai-study-library/ai/docs/claude-code/subagents/creating-custom-subagents.md (subagents cannot spawn subagents) [LOCAL]
19. Local: /home/user/ai-study-library/dev/research/2026-04-25-harness-engineering-research.md (artifact-validation hooks) [LOCAL]
20. Evans, E., *Domain-Driven Design: Tackling Complexity in the Heart of Software*, Addison-Wesley, 2003; *DDD Reference*, 2015 (https://www.domainlanguage.com/ddd/reference/) [BOOK]
21. Lauret, A., *The Design of Web APIs*, Manning, 2019; 2nd ed. June 2025 (confirmed: https://www.manning.com/books/the-design-of-web-apis-second-edition) [BOOK + WEB]
22. Hohpe, G. & Woolf, B., *Enterprise Integration Patterns*, Addison-Wesley, 2003 [BOOK]
23. Richardson, C., *Microservices Patterns*, Manning, 2018 (ch. 3 outbox/messaging, ch. 4 sagas) [BOOK]
24. Garcia-Molina, H. & Salem, K., "Sagas", ACM SIGMOD 1987 [BOOK/paper]
25. DAMA International, *DAMA-DMBOK: Data Management Body of Knowledge*, 2nd ed., 2017 [BOOK]
26. Simsion, G. & Witt, G., *Data Modeling Essentials*, 3rd ed., 2005 [BOOK]
27. Kimball, R. & Ross, M., *The Data Warehouse Toolkit*, 3rd ed., 2013 [BOOK]
28. Reis, J. & Housley, M., *Fundamentals of Data Engineering*, O'Reilly, 2022 [BOOK]
29. Dehghani, Z., *Data Mesh*, O'Reilly, 2022 [BOOK]
30. Campbell, L. & Majors, C., *Database Reliability Engineering*, O'Reilly, 2017 [BOOK]
31. Ambler, S. & Sadalage, P., *Refactoring Databases*, Addison-Wesley, 2006 [BOOK]
32. Fowler, M., "Richardson Maturity Model", 2010, and "What do you mean by Event-Driven?", 2017, martinfowler.com (blocked by proxy; from memory) [BOOK/UNVERIFIED]
33. Fielding, R., *Architectural Styles and the Design of Network-based Software Architectures*, PhD dissertation, UC Irvine, 2000, ch. 5 [BOOK]

---

## Verification log

Verifier pass on 2026-10-02 (citations and attributed claims only). Method: raw GitHub fetches, web search summaries, local-corpus line checks, and the verifier's own knowledge.

**Confirmed (online or local):**
- DDD-Crew Context Mapping: the nine patterns and three team relationships (Mutually Dependent, Upstream/Downstream, Free). Raw README fetched.
- DDD-Crew Aggregate Design Canvas fields: name, description, state transitions, enforced invariants and corrective policies, handled commands and created events, throughput (with the concurrency-conflict chart), size. Raw README fetched.
- Google AIPs (raw fetch): AIP-158 (adding pagination later is backwards-incompatible; opaque, URL-safe tokens), AIP-155 ("Providing a request ID must guarantee idempotency"), AIP-185 (beta must be a superset of stable; interface-based versioning with `YYYY-MM-DD` dates), AIP-193 (reason at most 63 characters).
- Idempotency-Key draft -07: October 2025; key MUST NOT be reused with a different payload; UUID recommended. Also noted that -07 has expired since April 2026.
- ODCS v3.1.0: relationships and foreign keys added (web search).
- Lauret, *The Design of Web APIs*, 2nd ed.: Manning, June 2025 (web search).
- DDIA 2nd ed. (Kleppmann & Riccomini): published Feb–Mar 2026 (web search).
- Local: creating-custom-subagents.md:47 and :295; spec-driven-development-arxiv.md:57 and :136–140 (spec-anchored OpenAPI plus Pact/Specmatic); harness-engineering-research.md:107 (artifact-validation Stop hook).

**Confirmed from the verifier's own knowledge:** Evans DDD chapters 2, 3, 5–6, 14, 15; Vernon IDDD ch. 8, 10, 13 and *DDD Distilled* (2016); Khononov ch. 1, 5–10; DDIA 1st ed. chapter mapping (1, 2, 4, 5, 6, 7, 9, 11, 12); DMBOK2 (2017) knowledge areas and ch. 3, 5, 7, 13; Kimball & Ross 3rd ed. (2013); Simsion & Witt 3rd ed. (2005); RFC 9457 (July 2023, obsoletes 7807; members type/title/status/detail/instance); AsyncAPI 3.0 channels/operations split; EIP four integration styles (ch. 2) and the Idempotent Receiver; Garcia-Molina & Salem (SIGMOD 1987); Richardson *Microservices Patterns* ch. 3 (outbox) and ch. 4 (sagas, countermeasures, compensatable/pivot/retriable); Fowler's four meanings of "event-driven" (2017); Campbell & Majors DBRE (2017); Dehghani *Data Mesh* (2022).

**Corrected:**
- Reis & Housley undercurrents: added the missing "data architecture" (there are six undercurrents).
- Vernon rules: noted that the cited PDF (Part II) covers only rules 3–4; rules 1–2 are in Part I.
- Expand/contract naming: attribution clarified (Sato/Fowler "ParallelChange", 2014) and kept UNVERIFIED.

**Upgraded from UNVERIFIED:** GDPR Art. 5(1)(e) and Art. 17 numbering; Sunset header = RFC 8594; Lauret 2nd ed. (2025); "smart endpoints and dumb pipes" = Lewis & Fowler 2014.

**Left as UNVERIFIED:** Lauret chapter numbers (the 2nd ed. was rewritten); EventStorming colour conventions; DDIA 2nd-ed. chapter structure; Reis & Housley ch. 8; DMBOK2 data-quality dimension list; Spectral as a universal standard; CloudEvents as mandated; Kafka exactly-once specifics; the frequency of "Domain Architect" as a job title.
