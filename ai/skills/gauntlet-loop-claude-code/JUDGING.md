# Judging against an artifact, and picking between drafts

Open this when the bar is an artifact the critic puts beside the work, when two drafts exist and
one must be chosen, or when the work is read by a model or a tool rather than a person.

## Findings and the pick are two runs

The **findings** critic knows which side is the work: it gets the SINCE block, and the bar never
changes, so the change list gives the side away. It returns blocking and polish. The **pick** is a
separate, blind run with neither: "A and B, which is better?". Where the bar has no pick (a
clause-by-clause specification), there is only the findings critic.

- **Strip the labels.** Shown "your work and the reference", a critic leans toward the side it was
  told is its team's. Shown A and B, it answers the question you meant.
- **Ask for a binary pick, not a score.** A 1–10 score drifts upward across rounds because each
  round really did improve on the last, and the loop exits on a number that never had a fixed
  meaning.
- **Put each pair both ways round.** Two judges once each favoured whichever draft they saw first.
  Count a win only when the same *draft* wins from opposite slots: one judge answering `FIRST` and
  the other `SECOND` for the same draft is agreement; both answering `FIRST` is position bias. A
  split is no signal, not a tie. Map each positional answer to its draft before reading the result.

## When the pick runs

The pick is one more stage of the round script, beside the critics: per piece, two fresh agents see
the pair in opposite orders and each answers `FIRST` or `SECOND`. Each writes its answer to
`$HANDOFF/picks/<TAG>-<key>-<order>.json`, outside `state/`, so `trend.py` never reads it as a
verdict. Its prompt opens and closes like a critic's (main page, *The round script measures*): it
returns that file unchanged when it exists, and it reads only the pair and the paths it names. Done
when both answers of every pair are on disk and mapped to their drafts. What the result decides:

- **two drafts** (below): the draft that won both orders continues; a split continues neither and
  goes to the user;
- **an artifact bar**: whether the work has caught up with the bar, which the exit does not
  require; the findings critic's list of what the bar does that the work does not is what the fix
  wave closes.

## Two builders instead of a bar

When no reference exists, two builders produce the work independently, neither seeing the other's,
and the pick compares them. You learn which is better and, from what the critic says is
missing from both, what neither thought of.

## Judge what the consumer receives

When a model or a tool consumes the work (a tool schema, a prompt, a generated file), one critic
reads only what that consumer receives, with the source closed. A critic once verified sixteen
formulas by hand and missed that eleven reached the model with no operand order at all: the rich
per-constant documentation was source-only, and the generated schema was a bare list of names.
