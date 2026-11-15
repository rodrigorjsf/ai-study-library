# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

This repo uses a **multi-context** layout. `GLOSSARY-MAP.md` at the repo root lists each context and the `GLOSSARY.md` that holds its language. A context keeps its ADRs in a `docs/adr/` beside its glossary.

## Before exploring, read these

- **`GLOSSARY-MAP.md`** at the repo root, then the `GLOSSARY.md` of the context you work in. For example, `ai/skills/run-spec/GLOSSARY.md` holds the language of the run-spec flow.
- **That context's `docs/adr/`**: read the ADRs that touch the area you are about to work in.

If any of these files don't exist, **proceed silently**. Don't flag their absence; don't suggest creating them upfront. The producer skill (`/grill-with-docs`) creates them lazily when terms or decisions actually get resolved.

## File structure

```
/
├── GLOSSARY-MAP.md
└── ai/skills/run-spec/
    ├── GLOSSARY.md
    └── docs/adr/
```

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in that context's `GLOSSARY.md`. Don't drift to synonyms the glossary explicitly avoids.

If the concept you need isn't in the glossary yet, that's a signal — either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/grill-with-docs`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0007 (event-sourced orders) — but worth reopening because…_
