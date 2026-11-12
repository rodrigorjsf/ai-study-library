# Fix waves

Open this when step 9 of *Starting a loop* chose a fix wave for a round's blocking findings. A round
measures; a **fix wave** closes what it found. Every fix is new text the next critic will read, so
the wave is where a loop either converges or starts to oscillate.

## 1. Red or filed

Every blocking finding gets exactly one of, before anything is edited:

- **red**: a mechanical check (a failing test, a checker rule, an entry in the project's check
  table) committed failing at the defective sites. The wave closes it green.
- **filed**: a tracker issue with the reproducing state, when no check can fail for the right
  reason (say why in the issue), when the finding predates the wave, or when it hit the cycle bound.

Filing replaces the check, not the fix: a filed finding from this round is still fixed in the wave
unless the user defers it, and a deferral goes into the brief.

A red check aims at the *class*, not the reported line: a predicate or a glob finds the twins the
finding did not name. When the same kind of defect returns twice, ask how many there are, and
whether the class is defined by a name, a pattern or a predicate: each search is blind to what the
other two find. Prefer a check that the rule's **home** exists plus checks that sites point at it; a
check keyed on today's wording goes silent when a reviser rewords the site, so mark such checks as
wording-keyed. A check that passes on a phrase already present for another reason is vacuous:
tighten it until it fails for the right reason.

Drafting checks can go to one agent writing candidates to a file. You review and add them; the
wave's adversarial review (§3) covers them.

## 2. Revisers own disjoint file groups

Split the findings into file groups that do not overlap. Before any reviser starts, write the wave
record into the handoff: the wave base (`git rev-parse HEAD`), each group with its files and
findings, and the stage reached (revisers); a resumed session finishes the wave from it. Update the
stage as the wave moves: each group finished, review cycle 1 or 2, closed.
Then launch one fresh `Agent` reviser per group, together, in the background. Each reviser prompt:

- lists the exact paths it edits: "these paths and no others";
- points at the brief (`$HANDOFF/brief.md`), which holds the bar, the exit, the scope and the
  user's decisions;
- says to fix the *finding*: the critic's proposed patch is a suggestion, and the reviser may
  decline it with a reason (one declined to widen a catch to `Throwable`, because catching an
  out-of-memory error allocates while allocation fails, and closed the defect where it began);
- ends on its checks: the gate commands and the red checks of its group (only the red checks when
  the brief says `gates: none`), done when every one exits clean on the reviser's paths; a group
  whose findings were all filed without a check is done when the reviser reports each one fixed,
  and §3 verifies it.

**Cross-cutting rules get one home and exact wording.** When a fix spans groups, the brief names the
rule's home file and heading, the sentence other files use to point at it, and the one group that
writes the home. Groups that improvise the same rule disagree.

Answer a reviser's open question with `SendMessage` to the same agent; it keeps its context. While
the revisers run, the files are theirs (main page, *Durable state and who owns it*). Record each
reviser's and reviewer's tokens with `trend.py usage` against the round the wave follows, so the
budget counts the wave too.

**Boundary check before committing:** map `git diff --name-only <wave-base>` to the groups. A path
outside every group (the check table, a generated copy) is reverted and handed to its owner; the
main thread owns generators and the check table. Then run the generators once, yourself.

## 3. Adversarial review, two cycles at most

With every check of the wave green and the wave committed, run a fresh `Agent` reviewer per area
whose whole task is to **break** it: the diff range, the issues, the bar, the scope, and the doubts
the revisers reported about their own work. It returns `grade`, `blocking` (each with the
reproducing state), `polish`.

- A blocking finding goes red, then back to the reviser that owns the file.
- **Until a cycle finds nothing blocking, or two cycles.** Blockers open after cycle 2 are filed; a
  third cycle is never launched. The reviewer sees the work and the diff, never the reviser's
  reasoning.
- Blockers that come from the wave's own design (new surface, not missed sites) are a signal to
  re-check the design against the project's frozen contract and to put a simpler, product-level
  alternative to the user.

## 4. When a check fails on an improvement

A genuine improvement that turns a check red means one of the two is wrong, and it is not always
the work: the check may encode the very defect just removed (a test asserting the broken output, a
style rule forbidding the clearer phrasing). Change the check when it was wrong, and record the
change where it is reviewed: in the commit body and the handoff. A check quietly edited until it
passes still looks like a gate and certifies nothing.

## 5. Prefer the fix that deletes

A rule added to close one path is a new path to attack. When two fixes close the same finding, take
the one that removes or shortens text; the shorter artifact has fewer places for the next defect to
hide. This is the first lever to pull when the trend shows the loop oscillating.

## 6. Close

Run every gate and red check in this turn, commit, push, close each issue with the check output
quoted, and mark the wave closed in its record with its end SHA (`git rev-parse HEAD`). The next
round measures.
