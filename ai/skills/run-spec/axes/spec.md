# Spec axis brief

You review one axis, **Spec**, of one ticket's diff, inside the implementer's per-ticket review. Read the code and run the evidence commands; never edit, stage, or commit.

## Sources

- `TICKET`: the ticket. `#N` → `gh issue view <N> --json title,body,comments`; a path → that file under `REPO`.
- `SPEC`: the parent spec, read the same way. Its user stories and out-of-scope list frame the ticket.
- `DIFF` and `COMMITS`: the change, run in `REPO`.
- `EVIDENCE`: one line per criterion, `<criterion> — <command> → <decisive output>`.

## What to check

Compare the diff with every acceptance criterion of the ticket, and with the spec lines the ticket cites.

- **Missing.** A criterion the diff does not implement at all.
- **Partial.** A criterion implemented for some of its cases: an edge case, an error path, or an input the criterion names that the code does not handle.
- **Wrong.** A criterion the code appears to implement, but whose logic gives a different result than the criterion states: a wrong condition, a wrong default, a wrong unit, an off-by-one.
- **Scope creep.** Observable behaviour the diff adds that neither the ticket nor the spec asks for: a new command, flag, endpoint, output, side effect, or default. Refactors, tests, and internal structure are not scope creep.
- **Evidence.** Re-run each `EVIDENCE` command from `REPO` under `timeout 600`, skipping lines marked UNVERIFIED (they carry no command), and stop whatever it started. Report every command whose decisive output differs from the line, or that fails or times out, quoting both outputs.

Every finding except Evidence quotes the ticket or spec line it measures against.

## Do not report

- Coding standards, comments, security, and design: other axes own them.
- Code the diff did not touch.

## Output

Report only this, under 400 words:

```
## Spec
- [missing|partial|wrong|scope-creep] <file:line or criterion> — "<quoted ticket or spec line>" — <why>
- [evidence] <command> — expected `<line's output>`, got `<your output>`
COUNT: <n>
```

Write `- none` when there are no findings.
