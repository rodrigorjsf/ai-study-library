---
name: bottleneck-hunt
description: Find where the wall-clock of a slow loop goes (a test suite, a build, a gate, a request, an agent's work on a ticket), prove the cause with a profile, and try the fix as a measured spike.
disable-model-invocation: true
---

# Bottleneck hunt

A hunt answers one question with numbers: where does the wall-clock of this **loop** go, and what removes the largest part of it. The loop is one end-to-end run of the slow thing. Every claim in the hunt is a measurement taken in this run, with the command that produced it.

Three words carry the method:

- **Ledger**: the wall-clock of the loop written as lines that sum to it. Waiting is a line: time blocked on a background job, a queue, a rate limit or a person is where slow loops usually hide their cost.
- **Offender**: a ledger line, ranked by its share of the loop.
- **Spike**: the smallest change that removes an offender's work, measured before and after.

## Steps

### 1. Name the loop

Write the loop as one command or one kind of recorded run, and the duration it has today. "The suite is slow" becomes "`<test command>` takes 9 min, and it runs twice per ticket".

Done when a command or a set of recorded runs yields a duration for the loop.

### 2. Write the ledger from recorded runs

Take the evidence from runs that already happened, before reading any code:

- a build, a test suite or a gate: the tool's own timing report (per phase, per file, per test);
- a CI pipeline: the duration of each job and step from its logs;
- a service: traces or request logs, split by span;
- an agent's work (Claude Code sessions): `python3 <this skill's directory>/session_ledger.py <project transcripts> --last N`, which splits each agent's wall time into model, tools and waiting, and shell time by kind of command.

Count how many times the loop, and each line of it, runs: a 4-minute step run 350 times outweighs a 30-minute step run once.

Done when the lines account for at least 90% of the loop's wall-clock. Unassigned time above that is a line you have not found yet, most often waiting.

### 3. Rank the offenders

Sort the lines by share, with the cumulative share beside each. Take the top line.

Done when the top offender has a number and a share, and you have said which lines together make 80% of the loop.

### 4. Descend until one command reproduces the cost

Split the offender one level with the tool's own breakdown (phase, then package, then file, then test or function), and repeat on the largest part. At each level let the numbers rule a class of cause in or out: compile against execute, startup against steady state, CPU against I/O, one giant unit against many medium ones.

Done when a single command, running alone in about a minute or less, reproduces a named share of the offender.

### 5. Profile before you believe

Write the hypothesis and the profile result that would kill it. Then profile that single command ([PROFILING.md](PROFILING.md) has the command per ecosystem and how to read the output) and attribute the time twice: by library or module, and by the nearest frame of the project's own code.

Check the profile is of the work: its samples sum to about the command's wall time, and it is not mostly idle. A profile that is mostly idle measured a launcher, not the worker.

Done when one call path holds a named share of the command's time. When the hypothesis died, say so and carry the cause the profile showed.

### 6. Spike the fix

Change the least code that removes the work at its cause. A fix in the code that does the work comes before a shortcut in the tests or callers that trigger it: the shortcut hides the cost from one caller and leaves it for the rest, production included. When the fix changes behaviour, write the failing test of that behaviour first.

Measure the single command, then the whole loop, with the same commands as before. Before each measurement record the machine's load and free memory: another heavy process running beside the measurement is a **confound**, and it goes in the report next to the number.

Done when the loop has a before and an after from the same command, and the project's whole test suite passes.

### 7. Account for what changed

A faster path often behaves differently at the edges. For each test whose expectation had to change, decide with evidence whether the old expectation recorded the slowness (an artifact) or the new behaviour is a regression, and say which. Where the claim is "same results, faster", compare old and new over generated cases.

Done when every changed expectation has a verdict and its evidence.

### 8. Go round again, or stop

Rewrite the ledger with the new numbers and return to step 3. Stop when the top offender is under 10% of the loop, or when removing it needs a decision that is the user's.

### 9. Judge a replacement by the ledger

A proposal to replace something instead of fixing it (a faster toolchain, a rewrite in another language, more parallel workers, a bigger machine) has a ceiling: the share of the loop it can touch. Read that share off the ledger first. Then measure the candidate on this project, in a scratch copy, on the real inputs. For parallelism, run two at once and record the time of each, the peak load and the lowest free memory: the limit is whichever runs out first.

Done when each proposal has its ceiling from the ledger and, when the ceiling is worth it, a measurement on this project.

### 10. Have it attacked, then report

Hand the ledger, the profile and the conclusions to a fresh reviewer that has not seen your reasoning, with the instruction to break them: claims the numbers do not support, causes you did not rule out, fixes that would backfire. Answer each objection with a measurement or a correction.

Report, in this order: the ledger as a table; each offender with its cause and the profile line that proves it; before and after for each spike; what changed in behaviour; each rejected proposal with the number that rejected it; and what is not verified, with its confounds.
