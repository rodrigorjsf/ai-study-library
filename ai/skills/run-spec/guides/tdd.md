# Test-first guide

Read this before the first test of a ticket or a fix. It applies to every test you write in the run.

## 1. Pick the seams first

A seam is a place where you can observe or replace behaviour without editing the code there. For a test, the useful seam is a module's public interface: the functions, commands, endpoints, or events its callers use.

Before you write a test, list the seams you will test at:

- The spec's `Testing Decisions` section names them when it has one. Use those.
- Otherwise, choose the public interface the ticket changes, at the highest level that still runs fast and deterministically.

Every test drives the code through one of these seams. A private function, an internal class, or a module's own collaborators are never a test's entry point.

## 2. Work in vertical slices

One slice is one behaviour, end to end, through one seam:

1. **Red.** Write one test for the next behaviour. Run it and watch it fail for the reason you expect: a missing behaviour, not a typo or an import error.
2. **Green.** Write the least code that makes it pass. Run it and the tests near it.
3. **Clean.** With every test green, tidy the code you just wrote: names, duplication, shape. Run the tests again.

Then pick the next behaviour. Each slice teaches you something about the design, so the next test can use it. Order the slices so the first one crosses the whole path (input to output) and later ones add cases.

## 3. What a good test looks like

- **It states a behaviour.** Its name reads as a fact about the system a user or caller relies on: "rejects an expired token", not "calls validateToken".
- **It goes through the interface.** It sets up through the public interface, acts through it, and checks the result through it. It never reads a database table or a private field to check what the interface already returns.
- **It survives a refactor.** Rewrite the implementation without changing behaviour, and the test still passes. A test that fails then was testing structure.
- **Its expected value is independent of the code.** Hard-code the result you derived by hand, or the one the spec's example states. A value the test computes with the code's own formula proves nothing.
- **It is deterministic.** Time, randomness, and the network are fixed or replaced at a seam.

## 4. Anti-patterns

- **Coupled to the implementation.** The test mocks the module's own internals, calls private functions, or asserts on how many times an internal helper ran. It breaks on every refactor and proves nothing a caller sees.
- **Tautological assertion.** The assertion repeats the code's own computation, or compares a value with itself, so it can never fail. It adds a green tick and no evidence.
- **Horizontal slicing.** Writing every test first and the code after, or every layer before the next. The tests guess at a design nobody has built yet, and none of them fails for a reason you learn from.
- **A test for each line.** Coverage of trivial getters and wiring, instead of the behaviours the ticket asks for.

## 5. Test doubles only at system boundaries

Replace a dependency only where your system meets something it does not own:

- the network and third-party services;
- the clock, randomness, and the process environment;
- a store that is slow or unavailable in the test environment.

Prefer the real thing when it is fast and local: an in-memory or temporary database, a temporary directory, a local server. Inject the boundary dependency at the module's seam, so the test passes a fake and production passes the real one. Never replace a module that the code under test owns, and never mock a type you do not own when a thin adapter of your own can sit in front of it.

## Done when

- every behaviour the ticket or finding asks for has a test that failed first and passes now;
- every test enters through a seam listed in step 1;
- no test matches an anti-pattern in step 4.
