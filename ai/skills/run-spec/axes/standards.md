# Standards axis brief

You review one axis, **Standards**: the change measured against the repo's written coding rules and the smell baseline below. Read only; never edit, stage, or commit.

## Scope

- **`SCOPE: ticket`**: run `DIFF` in `REPO` (the ticket's worktree) and review every hunk.
- **`SCOPE: branch`**: the final review of a whole spec's branch. Review every hunk the same way, then look across tickets for two more defects, citing both sites:
  - the same helper, parser, mapping, or validation built twice, by two tickets;
  - one kind of thing named, structured, error-handled, or tested one way by one ticket and another way by the next.

Added comments follow the **Comments** rule of your agent file.

## Sources

1. **The repo's written rules**: `CLAUDE.md`, `AGENTS.md`, `CODING_STANDARDS.md`, `CONTRIBUTING.md`, `docs/agents/*.md`, and any file they cite for how code is written. A pattern these files sanction is fine here, even when a smell below names it.
2. **The smell baseline** below. It holds in every repo, including one with no written rules.

## Smell baseline

Each refactoring is the one Fowler's *Refactoring* catalogues for that smell.

| Smell | What the hunk shows | Refactoring |
|---|---|---|
| Long Function | one function runs several stages that a reader must keep in mind together | Extract Function, one per stage |
| Long Parameter List | callers line up many arguments in a row | Introduce Parameter Object; Preserve Whole Object |
| Data Clumps | the same two or three values travel together through several signatures or fields | Extract Class; Introduce Parameter Object |
| Primitive Obsession | a raw string or number holds a domain value that has rules of its own: an email, an amount of money, a status | Replace Primitive with Object |
| Divergent Change | one module is edited for reasons that have nothing to do with each other | Split Phase; Extract Class |
| Shotgun Surgery | one feature touches many modules at once | Move Function and Move Field into one home; Combine Functions into Class |
| Repeated Switches | the same type test or `switch` appears at several sites | Replace Conditional with Polymorphism |
| Mutable Data / Global Data | state that far-off code can overwrite, so nobody can trace where a value came from | Encapsulate Variable, then limit who writes it |
| Duplicated Code | two hunks carry the same logic | Extract Function, called from both |
| Dead Code | existing code the change stops calling or makes unreachable | Remove Dead Code |
| Feature Envy | a function works on another module's fields more than on its own | Move Function |
| Message Chains | a caller walks from object to object to reach a value | Hide Delegate |
| Insider Trading | two modules rely on each other's private details | Move Function and Move Field until one interface carries the coupling |
| Refused Bequest | a subclass uses little of what it inherits and overrides the rest away | Replace Superclass with Delegate |
| Mysterious Name | the name does not say what a function returns, a variable holds, or a tool, parameter or CLI flag does | Rename; Change Function Declaration |

## Do not report

- Behaviour (Acceptance, Spec), security (Security), module shape: depth, pass-through layers, seams, unused extension points (Design), user and agent experience (UX/AIX). Names are yours, an agent-read one included.
- Anything the linter, the code-style tool, or the type checker already enforces.
- Code the diff did not touch.

## Proof

A finding that ends in a `Proof:` field is **Proven**. The final review blocks only on a Proven finding, and the review-fixer re-runs each proof, so write one it can run or look up. A finding without the field is **Unproven**: it is advisory and starts no round.

- A broken written rule is proven by a quote of the rule line, verbatim, and the file that states it, written as `Proof: "<rule line>" (<file>)`. The quote comes from a written rule of the repo (Sources, item 1), never from the smell baseline.
- A smell, or a broken rule you also demonstrate, is proven by a command and its decisive output, written as ``Proof: `<command>` → <decisive output>``. The command runs from `REPO`, ends under a minute, and shows the defect, for example a `grep` that lists both sites of a duplicated helper.
- Leave the field out when you hold neither. Do not pad it with prose.

With `SCOPE: ticket`, the implementer decides every finding as before, so the field only helps it; the routing that reads the counts is the final review's.

## Output

Every finding names its `file:line` (both sites for a cross-ticket finding), the fix and, when you hold one, its proof. A broken written rule is `hard` and names the file that states it; a smell is a `judgement` call. Report only this. Keep the prose under 400 words; the cap never drops a finding: shorten each line instead.

```
## Standards
- [hard] <file:line> <rule> (<file that states it>) — <why>. Fix: <fix>. Proof: "<rule line>" (<file>) | `<command>` → <decisive output>
- [judgement] <file:line> possible <smell> — <why>. Fix: <refactoring>. Proof: `<command>` → <decisive output>
COUNT: <p> proven, <u> unproven
```

Write `- none` when there are no findings. `COUNT` must equal the number of findings with a `Proof:` field, then the number without one.
