# Domain catalog

One row per domain. A domain is **present** when its signal exists in the repo. The questions are what a survey answers with evidence; a question with no consistent answer in the code yields no rule.

| Domain | Present when | Questions the survey answers |
|---|---|---|
| **Language** (one heading per language) | source files of that language | Which idioms are preferred where the language offers several (records vs classes, streams vs loops, null handling, immutability, visibility defaults)? How are names formed beyond what the linter checks? |
| **Framework** (one heading per framework) | a framework dependency in the build file | How is wiring done (constructor vs field injection, config classes vs annotations)? Which framework features are standard and which are avoided? Where does framework code stop and domain code start? |
| **Architecture** | more than one module, package layer, or service | Which way do dependencies point between layers? Where are the seams, and what sits behind each? What belongs in a module's interface versus its implementation? Where do new files of each kind go? |
| **Domain language** | a glossary, or recurring domain nouns in type names | Which term names each concept, and which synonyms are retired? How do domain terms map to type, table, and endpoint names? |
| **Testing** | a test directory or test files | At which seam are tests written? What is mocked and what is real? How are tests named and structured? How are fixtures and test data built? Which test kinds exist and where does each live? |
| **Error handling** | any throw, error return, or result type | Exceptions or result values? Where are errors caught, translated, and logged? Which error types are domain errors? |
| **Persistence** | a database driver, ORM, or migration directory | Where do queries live? How are transactions bounded? How are migrations named and ordered? What is the entity-to-domain mapping rule? |
| **API and contracts** | HTTP handlers, RPC definitions, message schemas, or a public package interface | How are endpoints, payloads, and versions shaped? How are errors represented on the wire? How are breaking changes introduced? |
| **Concurrency** | threads, async, queues, or schedulers | Which concurrency primitive is standard? Where may blocking happen? How is shared state guarded? |
| **Security** | authentication, authorisation, secrets, or input from outside the process | Where is input validated? Where are authorisation checks placed? How are secrets read? |
| **Observability** | logging, metrics, or tracing calls | What is logged at each level? Which fields are structured? What must never be logged? |
| **Configuration** | config files, env var reads, or feature flags | Where is configuration read and typed? How are defaults and environments handled? |
| **Code documentation** | doc comments or a docs directory | Which elements get a doc comment, and what does it say? When does a comment explain why? Where do longer explanations live? |
| **Dependencies** | a build or package manifest | How is a new dependency justified and pinned? Which internal library is preferred over which external one? |
| **Frontend** | UI components, styles, or templates | How are components composed and state held? How is styling done? What are the accessibility requirements? |
| **Infrastructure as code** | Terraform, Helm, Kubernetes manifests, Dockerfiles, CI workflows | How are resources named and modules structured? How do environments differ? |

## Reading the Architecture and Testing domains

Use this vocabulary when stating rules in those two domains, so every reviewer reads them the same way:

- **Module**: anything with an interface and an implementation, at any scale.
- **Interface**: everything a caller must know to use the module: signature, invariants, ordering, error modes.
- **Deep module**: a lot of behaviour behind a small interface. **Shallow**: the interface is nearly as complex as the implementation.
- **Seam**: a place where behaviour can be altered without editing in that place; where a module's interface lives. Tests are written at seams.
- **Adapter**: a concrete thing that satisfies an interface at a seam. One adapter is a hypothetical seam; two make it real.
