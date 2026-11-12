# The bar

Open this when you are naming the bar at the start of a loop, or when a critic keeps returning the
same grade round after round: read it before touching the work.

## A bar is a thing, not an adjective

"Make it excellent" gives the critic nothing, so it invents a comparison, a different one each
round, drifting upward as the work improves. That is why a loop against a vague bar never ends.

```
BAD   "production quality"     "make it beautiful"     "as good as a senior would write"
GOOD  "the opening two pages of <a named book in this genre>: same rate of concrete detail,
       same distance between the reader and the events"
      "the checkout flow at stripe.com/checkout, screenshotted at 360px and 1440px"
      "the onboarding guide we shipped last quarter: same voice, same evidence density"
      "the accessibility criteria, clause by clause, with the clause number beside each verdict"
```

Three properties; dropping any one breaks the loop:

- **Named**: a specific artifact, not a category. "A good CLI" is a category; `ripgrep --help` is
  an artifact.
- **Fetchable**: the critic can open it *this round*. A bar that lives in someone's head is
  reconstructed differently every time.
- **Comparable**: the work and the bar sit side by side in the same form: two screenshots, two
  documents, two outputs of the same command. Otherwise the critic compares a thing to a
  description of a thing, and the description always wins.

**Prefer a real reference to a rubric you wrote.** A rubric is your opinion of what matters, and
the loop optimises it exactly, including the parts that never mattered.

**A famous bar is recognised, and recognition is not judgement.** Strip the labels off a household
reference and the critic still knows which is which; in the run this technique comes from, every
critic in every round picked the real reference. Normalise the presentation until recognition is
hard (same format, length, framing, incidental signatures removed), or accept that the bar wins and
read the critic's findings rather than its pick.

**A bar that is not reached is not a failed run.** The origin run (`github.com/mshumer/Claude-of-Duty`)
set Call of Duty as the bar and did not get there; it got a game far past what one pass produces.
The bar's job is to pull, not to certify; the exit (*Blocking, polish and the grade*, on the main
page) is what certifies.

## When nothing obvious exists

Four sources, in the order worth trying:

1. **The best instance of the same kind of thing**, not the same subject. A runbook for another
   service is still a runbook: it shows the density, the ordering, what it assumes the reader knows.
2. **Your own best previous work.** "As good as the chapter we already shipped" is fetchable,
   comparable, and in a voice you can match: the strongest bar for anything internal.
3. **A specification, read clause by clause**, with the clause number beside each verdict. Weaker
   than an artifact (a spec says what must not be wrong, rarely what would be good), but it never
   drifts.
4. **The rejected alternative.** Build two versions independently and compare those
   ([JUDGING.md](JUDGING.md)). You lose the absolute standard and keep the blinding.

A bar in someone's head becomes usable once written as something checkable:

```
BAD    "it should feel fast"
GOOD   "first paint under 1s on a throttled 3G profile, screenshotted with the timing overlay"
BAD    "the API should be intuitive"
GOOD   "a developer who has not seen it writes the three most common calls from the reference
        page alone, without opening the source"
```

**Constraints stay beside the bar, not inside it.** A domain rule, a decision made elsewhere, a
thing that must hold regardless: list them under RULES in the brief (main page, *Starting a loop*
step 6). Folded into the bar, a constraint failure reads as a quality failure and nobody can tell
which.

## When the grade stops moving

A critic told to pass the work "only when you cannot name a concrete improvement" never passes
anything: in any artifact of real size something is always nameable. The grade stops carrying
information, the work improves, the number does not move, and the loop runs until something else
stops it.

**Measured.** Eight documents ran four rounds under that instruction; every round returned the same
grade with six to ten blocking defects. The instruction was replaced by the exit on the main page
and the polish bucket. The next round returned 0–3 blocking per document, polish absorbed six to
fifteen items each, and two documents passed for the first time. The relabelling is what made the
grade carry information; the passes came from the build round that followed. No work was
relabelled into passing.

So when the same grade returns round after round, look at the exit before the work: is it an
observable property, does the critic have a polish bucket, did the user say which paths count, and
is a guideline's number being graded as blocking? Told nothing, critics flag every piece against a
figure (a length ceiling, a count) that the shipped work itself exceeds.
