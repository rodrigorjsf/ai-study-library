# Test smells

The catalogue every unit test is read against. A test matching no smell here is sound.

## What a test is worth

Four properties, from Vladimir Khorikov, _Unit Testing: Principles, Practices, and Patterns_. Judge a test on all four; volume is not one of them.

- **Protection against regressions**: it fails when domain behaviour breaks.
- **Resistance to refactoring**: it stays green when the implementation changes and behaviour does not.
- **Fast feedback**: it runs quickly.
- **Maintainability**: it is short, reads as a specification, and needs little setup.

Vocabulary:

- A **seam** (Michael Feathers) is where a module's interface lives. Tests belong at seams, and **the interface is the test surface**: callers and tests cross the same one.
- A **deep module** (John Ousterhout) puts a lot of behaviour behind a small interface, so a few tests at its seam protect a lot of code.
- An **equivalence class** is a set of inputs the code treats the same way. One test per class plus one per boundary is the whole job.

## Smells

Each reads as what it is, the proof that confirms it, then the action.

### Padding

Tests written to raise a count or a coverage number.

- **Assertion-free**: executes code and asserts nothing, or asserts only that no exception was thrown where none could be. _Proof:_ kills no mutant; removing it changes only line coverage. _Action:_ delete; if the lines matter, a carrier with a real assertion must cover them.
- **Trivial target**: tests a getter, setter, constructor, generated `equals`/`toString`, a constant, or a framework or library feature (the mapper maps, the annotation validates). _Proof:_ the code under test has no branch and no domain rule. _Action:_ delete.
- **Tautological**: the expected value is recomputed the way the code computes it, or a snapshot derived the same way, so it passes by construction. _Proof:_ a mutant in the computation survives. _Action:_ rewrite with an independent literal if the behaviour matters and has no carrier; otherwise delete.
- **Mock echo**: stubs a mock to return X, then asserts the result is X, with no logic between. _Proof:_ replacing the code under test with a pass-through keeps it green. _Action:_ delete.

### Coupled to implementation

Tests that break on refactor and pass on regression.

- **Interaction-only**: asserts only that internal collaborators were called, how often, or in what order. _Proof:_ the collaborator is inside the system, not at a system boundary. _Action:_ rewrite as one assertion on the outcome at the module's seam, or delete when a carrier already asserts that outcome.
- **Over-mocked**: mocks classes the team owns, so the test exercises the mocks. _Proof:_ the real collaborators are cheap and deterministic. _Action:_ use the real collaborators; keep mocks for system boundaries (external services, time, randomness, sometimes the database or filesystem).
- **Private reach**: tests a private method, a package-private helper, or internal state through reflection or a side channel. _Proof:_ the behaviour is reachable through the public interface. _Action:_ move the assertion to the public interface, or delete when a carrier covers it.

### Redundant

- **Duplicate behaviour**: two tests at the same seam assert the same behaviour for inputs in the same equivalence class. _Proof:_ the carrier kills every mutant this one kills. _Action:_ delete the weaker one.
- **Same shape, different data**: several tests share arrange, act, and assert and differ only in values. _Proof:_ a line diff shows only literals changing. _Action:_ **parameterize** into one test with a data table, one row per equivalence class and boundary, each row named. Drop rows that repeat a class.
- **Subsumed**: a test at an inner helper repeats what a test at the module's seam already asserts. _Proof:_ the seam-level test kills the same mutants. _Action:_ delete the inner one.
- **Wrong seam**: many small tests on shallow internals where a few at the module's interface would protect the same behaviour. _Proof:_ the internals have one caller and no independent meaning. _Action:_ write the seam-level tests first, prove them, then delete the internal ones.

### Obsolete

- **Disabled**: skipped, ignored, or commented out, with no linked issue and no recent change. _Proof:_ `git log` shows the skip is old. _Action:_ delete.
- **Dead target**: tests code that nothing in production calls, a removed feature, or a deprecated path scheduled for deletion. _Proof:_ no production reference to the symbol. _Action:_ delete, and report the dead code as a finding.
- **Stale expectation**: the name or comment describes behaviour the code no longer has, and the assertion was loosened to keep it green. _Proof:_ `git log` on the assertion. _Action:_ rewrite to the current behaviour, or delete when a carrier covers it.

### Slow for no reason

These are speed findings; the test usually stays.

- **Heavy fixture**: starts a framework context, container, or database to test pure logic. _Action:_ run it as a plain unit test with the logic constructed directly.
- **Repeated setup**: rebuilds an expensive immutable fixture per test. _Action:_ share it per class or per suite.
- **Real waiting**: sleeps, real timers, or real network. _Action:_ inject a clock or a fake at the boundary.

## Keep-list

A test matching any of these stays, whatever else it matches:

- the only test that kills some mutant
- a boundary value of a domain rule (limit, threshold, rounding, empty, maximum)
- a regression test tied to a bug (an issue id in its name, comment, or commit)
- a worked example of a domain rule that the glossary, a spec, or an ADR states
- a test of error or failure behaviour the interface promises
