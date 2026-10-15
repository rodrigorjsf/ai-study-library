# Writing the study chapters

## Layout

```text
<study>/
  README.md                       hub: scope, method, reading order, overview diagram, "when to use" table
  01-concepts.md                  state of the art from the verified-research findings
  02-<repo-a>.md                  concepts, architecture, benefits, limitations, claims checked
  03-<repo-a>-security.md         egress, exposure, secrets, at rest, poisoning, supply chain, findings, hardening
  04-<repo-b>.md / 05-...-security.md
  0N-comparison.md                when two or more repositories
  0N-integration-<harnesses>.md   when harnesses matter
  0N-plan-<name>.md               when an adoption plan was asked for
  diagrams/*.json                 diagram sources
  html/*.html                     rendered diagrams
  presentation/                   deck (see the html-presentation skill)
```

File names and headings follow the study's language. Number chapters in reading order.

## Every chapter

- **Header block**: what the chapter is, the repository and pinned SHA, the date, the method (static, nothing
  executed), and the label legend from `VERIFY.md`.
- **Footer and header nav**: `← previous | next →` with real links; the last chapter points back to the hub.
- **Tables first** for anything compared or enumerated; prose explains the table.
- **Mermaid** where a flow, an architecture or a state helps a beginner: `classDef` colours always, animated
  edges (`e1@--> ...` plus `e1@{ animate: true }`) where they show the main path.
- **Examples** for every concept a beginner would not know (show the input and the output).
- **Evidence** next to each claim: `path:line`, `[n]` into the bibliography, or the command you ran.

## Security chapter shape

1. What "guarantee no vulnerabilities" can and cannot mean: findings at the pinned SHA, residual risk,
   hardening; never a promise of zero risk.
2. Executive summary table (aspect → verdict).
3. Egress table (destination, trigger, content, default) and every gap between the data-handling doc and the
   code.
4. Exposure, secrets, data at rest, poisoning (with a sequence diagram of the attack), supply chain (OSV hits
   with reachability), the project's own advisories.
5. Findings table by severity, each with a concrete scenario.
6. Hardening checklist: each item names the setting or change and the finding it closes.
7. Residual risk after hardening.

## Comparison and plan chapters

`COMPARE.md` and `PLAN.md` hold their shapes.

## Before you call a chapter done

- `python3 -I scripts/check_links.py <study>` exits 0.
- Every number on the hub, the cover and the comparison matches the chapter it came from.
- The parent documentation index lists the study.
