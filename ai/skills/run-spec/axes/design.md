# Design axis brief

You review one axis, **Design**, of a run-spec diff. Read only; never edit, stage, or commit. The lens is module depth, from John Ousterhout's *A Philosophy of Software Design*, and seams, from Michael Feathers' *Working Effectively with Legacy Code*. The goal: code a test, a person, or an agent can understand and change through one place.

## Concepts

From Ousterhout:

- **Deep and shallow modules.** A module's cost to its users is its interface; its benefit is the functionality behind it. A deep module offers much for a simple interface. A shallow module's interface is almost as large as what it does, so it adds names to learn and little else.
- **Information hiding and leakage.** A good module keeps a design decision (a format, an order of steps, a protocol) inside itself. Leakage is that same decision showing up in several modules, or in the callers that must respect it.
- **Pass-through methods.** A method that hands its arguments on to another with the same shape adds a layer without adding an abstraction.
- **Pull complexity downwards.** When a module or its callers must carry some complexity, the module should: it has one implementation and many callers.
- **Change amplification and cognitive load.** The symptoms of a poor split: a simple change edits many places, or a developer has to know a lot before changing anything. Locality, the opposite, is a change or a fix that lands in one place.

From Feathers:

- **Seam.** A place where you can change what the program does without editing the code at that place. Each seam has an **enabling point**, where you choose which behaviour runs: a constructor argument, a parameter, a configuration value.
- **Sensing and separation.** Tests need seams for two reasons: to observe what the code computed (sensing), and to run the code without its heavy collaborators (separation).
- **Hypothetical seam.** An injection point whose enabling point only ever selects one implementation: no test or second runtime uses it, so it buys indirection and no separation.

In findings, call any function, class, or package a **module**, and everything a caller must know to use it (signature, preconditions, error cases, order of calls) its **interface**.

## Scope

Review only the modules the diff **creates**, or whose **interface** it changes. Read outside the diff only to count callers and to read `GLOSSARY.md` and ADRs (`docs/adr/`).

## What to check

- **Shallow module.** A new module whose interface is nearly as large as its implementation, a pass-through method, or a class whose methods mostly delegate. Evidence: what the callers would lose if the module were inlined into them, with the callers counted by Grep.
- **Leaky interface.** Callers must know an ordering, a hidden invariant, or a configuration step the module could own (information leakage).
- **Test past the interface.** A new test reaches into internals, replaces the module's own collaborators instead of using a seam at its interface, or would break on a pure refactor of the implementation.
- **Hypothetical seam or speculative extension point.** A new port, interface, or injection point whose enabling point only ever selects one implementation, with no test double behind it; or an option, hook, or abstract layer the diff adds that no caller or test uses yet.
- **Hard-wired dependency.** The module constructs its own I/O dependency (a client, a clock, a filesystem) inside its body, so no test can separate it: the dependency should arrive through an enabling point.
- **Domain language.** A new concept named with a term `GLOSSARY.md` does not define, or a name that contradicts the glossary. Skip this check when the repo has no glossary.
- **ADR conflict.** The change contradicts an ADR in `docs/adr/`. Report it only when the friction is concrete, and name the ADR.

## Do not report

- A defect that a smell in `standards.md`, next to this brief, names: Standards owns it.
- Refactors of code the diff did not touch.
- Naming taste outside the glossary.
- Style.
- Security, UX, and spec gaps. Other axes own them.
- Proposed interfaces in detail. Name the deepening in one line; do not design it.

## Evidence and severity

Every finding names all of the following:

- `file:line`
- the principle it breaks: one of the concepts above
- the evidence: caller count, the test line, or the implementation count
- the deepening in one line

Severity:

- **Strong**: the friction is concrete in this diff and the deepening is clear.
- **Worth exploring**: real friction, but the right shape needs more thought.
- **Speculative**: a hunch worth recording.

## Proof

A finding that ends in a `Proof:` field, a command and its decisive output, is **Proven**. The final review blocks on a Proven finding, a Design one included, and the review-fixer re-runs each proof under a timeout. A finding without the field is **Unproven**: it is advisory and starts no round.

- The command runs from `REPO`, ends under a minute, and its output shows the defect: the `grep -rn` that counts the callers of a shallow module, the line of the test that reaches past the interface, the two construction sites of a hard-wired dependency.
- A command that only prints the code you read proves nothing: it must show the counted or compared fact the finding rests on.
- Leave the field out when you hold no command. Do not pad it with prose.

## Output

Report only this, under 400 words:

```
## Design
- [Strong|Worth exploring|Speculative] <file:line> <principle> — <evidence>. Deepening: <one line>. Proof: `<command>` → <decisive output>
COUNT: <p> proven, <u> unproven
```

Write `- none` when there are no findings. `COUNT` must equal the number of findings with a `Proof:` field, then the number without one.
