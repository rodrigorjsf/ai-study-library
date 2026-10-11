# Baseline

The literature baseline a reviewer applies when the repo documents nothing on the point. Every item is a labelled heuristic ("possible Feature Envy"), always a judgement call, and a domain rule in `CODING_STANDARDS.md` overrides it. Copy into the file's `## Baseline` section only the items no domain rule overrides and no tool enforces.

## Code smells

From Martin Fowler, _Refactoring_ (2nd ed., ch. 3). Each reads as what it is, then how to fix it.

- **Mysterious Name**: a name that does not reveal what the thing does or holds. Rename it; if no honest name comes, the design is murky.
- **Duplicated Code**: the same logic shape in more than one place. Extract the shared shape and call it from both.
- **Feature Envy**: a method that uses another object's data more than its own. Move the method to the data it envies.
- **Data Clumps**: the same few fields or parameters travelling together. Bundle them into one type.
- **Primitive Obsession**: a primitive or string standing in for a domain concept. Give the concept its own small type.
- **Repeated Switches**: the same branch on the same type in several places. Replace with polymorphism or one shared map.
- **Shotgun Surgery**: one logical change forcing edits across many files. Gather what changes together into one module.
- **Divergent Change**: one module edited for several unrelated reasons. Split it so each module changes for one reason.
- **Speculative Generality**: abstraction, parameters, or hooks added for needs nobody has. Delete it and inline until a real need shows.
- **Message Chains**: long `a.b().c().d()` navigation the caller depends on. Hide the walk behind one method on the first object.
- **Middle Man**: a class or function that mostly delegates onward. Remove it and call the real target.
- **Refused Bequest**: a subtype that ignores or overrides most of what it inherits. Replace inheritance with composition.

## Module design

From John Ousterhout, _A Philosophy of Software Design_ (deep modules), and Michael Feathers, _Working Effectively with Legacy Code_ (seams).

- **Prefer deep modules.** A new module puts a lot of behaviour behind a small interface. A module whose interface is nearly as complex as its implementation is shallow.
- **The deletion test.** Imagine deleting the module. If the complexity vanishes, it was a pass-through; if it reappears across its callers, it earns its place.
- **The interface is the test surface.** Callers and tests cross the same seam. Needing to test past the interface means the module has the wrong shape.
- **A seam needs two adapters.** Introduce an interface at a seam when something actually varies across it. One implementation is a hypothetical seam.
- **Accept dependencies, return results.** A module receives its collaborators and returns values, so it can be tested through its interface.

## Tests

- **Behaviour through the public interface.** A test reads as a specification of what the module does and survives a refactor that keeps behaviour.
- **Mock at system boundaries only**: external services, time, randomness, and sometimes the database or filesystem. The module's own collaborators stay real.
- **Independent expected values.** The expected value is a known literal or a worked example, never recomputed the way the code computes it.
- **Vertical slices.** One test, then the code that passes it. Tests written in bulk ahead of the code verify imagined behaviour.
