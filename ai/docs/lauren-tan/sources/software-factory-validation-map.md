# How `software-factory` validates agent work (as of 2026-11-15, plugin 0.1.8)

Repo: `/home/rodrigo/Workspace/software-factory` (HEAD `1dffd43`). Spec: issue #38 (open). Read-only survey for comparison with Lauren Tan's "poteto pyramid".

## Status labels and the one caveat that covers everything

- **BUILT**: code under `plugin/` plus seam tests under `tests/` (128 test files, 2107 `def test`).
- **BUILT-blocked**: code exists, but an open issue keeps it from working on a real image or repository.
- **DESIGNED**: an ADR, the spec or the glossary decides it, and no code computes it yet.

**Caveat.** Every test stubs Claude. A scripted stub sits at Claude Code's fixed path in the test image (spec #38, "Testing Decisions"). Seam 3, the agent texts, is "judged only through version one's acceptance runs, not by unit tests" (spec #38; `CODING_STANDARDS.md` Testing). Those runs are issue #79, still open and labelled `ready-for-human`. Issues #85 and #87 say the job image's pinned inputs and its `git` are not produced yet.

So no layer below has run end to end, with real agents, on a real target repository. "BUILT" means the deterministic skeleton is tested. It does not mean the loop is proven.

**Terminology trap.** In this repo, **"verification" means only the profile's exit-code commands**. GLOSSARY "Verification command" defines it as "a command in a repository profile whose exit code says whether the target repository is in a good state". GLOSSARY "Audit" even says _Avoid: Verification_. Lauren's "verification" (runtime driving of the app, formal methods, property tests) has no single counterpart here. Its nearest pieces are the browser lenses and the security lens's probes.

---

## 1. Pipeline stages and where verification happens

The frame is the study's 12 stages, 14 principles and 6 guardrail layers, as amended in ADR 0034:37-97. The front half (intake to tickets) runs on the host with the owner present. The back half runs headless in a job container, driven by a Python script on the host (ADR 0009, ADR 0033).

| # | Stage / gate | Who judges | What it checks | Status |
|---|---|---|---|---|
| 1 | **Implementer** per ticket, in its own worktree | agent | Works test first. Writes a handoff whose first line is `Status: DONE` or `FAILED`, and lists each acceptance criterion with the test or command that shows it (`plugin/prompts/implementer.md:14,38`) | BUILT |
| 2 | **Ticket done-gate** | script | Requires a commit with the `Ticket: #n` trailer (`attempt.py:62`) and a handoff starting `Status: DONE` (`attempt.py:80-81`). Both are claims the script reads, not proof | BUILT |
| 3 | **Per-ticket review**: Standards + Spec lenses, then one fixer, one round | separate agents | Reviews the diff from the accepted tip. The script runs this review because a leaf agent cannot spawn one (`review_ticket.py` docstring; ADR 0034:111). The fixed result is "not trusted either": the integration re-verifies it | BUILT |
| 4 | **Integration**: one ticket at a time, `merge --no-ff` | script | Runs the profile `verify` commands itself (`integrate.py:88`; `verification.py` docstring: "an agent's word that its tests pass is not evidence, the script's own run is"). On a conflict or a red result, the integrator agent fixes it. The script then re-verifies: "the integrator's own test line is not evidence" (ADR 0027 step 5) | BUILT |
| 5 | **Merge-integrity checks** in the push mirror, which no agent writes | script | ADR 0027 names **three** checks: the old tip is kept, every ticket head is kept, and the merge tree differs from git's auto-merge only on conflicted paths. `merge_checks.py` (docstring) runs **four**: it adds a first-parent check from spec "Other details". A base merge adds an ancestry check (ADR 0024). A failure rejects the merge as `MERGE_FAILED`, keeps the attempt as `refs/factory/attempts/<ticket>/<k>` (`work_branch.py:102`) and resets to the accepted tip. Attempt cap: `oracle_impl.py:12` `MAX_ATTEMPTS = 2` | BUILT (docs say 3, code does 4) |
| 6 | **Final review** of the integrated branch against the base commit, at most 2 rounds | agents | Standards and Spec always. Security, UI and UX when a trigger fires. All findings go to one review-fixer, and its commits pass verification and the checks again (`review.py` docstring; `review.py:43` `MAX_ROUNDS = 2`; ADR 0017:28-42) | BUILT. UI/UX are BUILT-blocked (#102, #103) |
| 7 | **Pre-push gate**: protected list, secret scan, prototype check | script | Two tiers. **Held**: `.github/**`, a secret, or prototype/task code; the push stops until the owner runs `sf clear`. **Escalated**: everything else; the verdict is forced to escalate (`push_check.py`, `protected_list.py`, `secret_scan.py` docstrings; ADR 0010:39-78) | BUILT |
| 8 | **Push** | script | Pushes only when verify passed on the exact tip to be pushed. Never force-pushes (`deliver.py:47-61`, docstring) | BUILT |
| 9 | **CI wait** on the profile's required checks, plus a **CI fixer** | script + agent | Waits up to a ceiling. At most 2 fixer rounds (`ci.py:31`). A check the job caused that still fails forces an escalation. The fixer prompt: "do not weaken a test, a check or a configuration file" (`plugin/prompts/fixer.md:12`) | BUILT (#90: commit statuses are misread) |
| 10 | **Approver**, advisory | agent, reads only | Returns the door, the blast radius, its own call and a per-criterion evidence table. The script renders the verdict and adds the forced escalations (ADR 0029; `plugin/prompts/approver.md`; `verdict.py` docstring) | BUILT |
| 11 | **Audit**: PR comments and reviews vs the ledger | script | Flags forged or changed verdict comments and any approving review. Blocks nothing (`verdict_audit.py` docstring; ADR 0029:65-72) | BUILT |
| 12 | **Owner merges** on GitHub, under autonomy stage C | human | `sf rework` and `sf discard` are typed terminal acts bound to a hash (`rework.py` docstring; ADR 0018) | BUILT |
| 13 | **Ledger**: hash-chained, append-only, outlives jobs | script | Records verdicts, owner acts, guard events, cost, diff size and the fixer's dismissal ratio (ADR 0016:55-62). The chain cannot detect a rewritten last line (#82) | BUILT |
| 14 | **Regression mark and revert scan** | owner + script | `sf regression <job> --note` (`tests/test_regression_mark.py`). `reverts.py` scans the base branch for `This reverts commit <sha>`. Both count against the approver for stage D (`stage_d.py` docstring) | BUILT |
| 15 | **Retro**, per repository | agent proposes, owner accepts | Section 4 below | BUILT |

**Approver's forced escalations** (ADR 0029:42-51). The approver cannot lower any of the six.

1. A protected-list hit.
2. An open blocking security finding.
3. A required check not concluded at the ceiling.
4. A partial job. **DESIGNED only**: it is never computed, because a job with a skipped ticket stops before the verdict (`verdict.py` docstring; #99).
5. A job-caused check still red after 2 fixer rounds.
6. A lens result discarded because the branch changed under the lens.

The approver must also choose to escalate on five cases (`plugin/prompts/merge-policy.md:19-27`). Case 4: "has an acceptance criterion without convincing evidence". It may approve only a two-way door with a small blast radius (`merge-policy.md:15`).

## 2. Evidence of "done"

- **Implementation ticket done test.** "A commit carrying its `Ticket:` trailer on the work branch's accepted tip, read in the push mirror, or its issue closed" (ADR 0019:58; ADR 0027 "Handoffs, and what counts as done"). A ticket with nothing to change makes an empty commit with the trailer. This is a **structural** done test. It is not a behavioural one.
- **Acceptance criteria.**
  - The implementer lists each criterion with the test or command that shows it, in its handoff (`implementer.md:38`).
  - The Spec lens reports missing, partial or wrong requirements, "quote the line of the spec or the criterion", as blocking (`plugin/agents/reviewer.md`, "Spec").
  - The approver fills `criteria: [{criterion, evidence, convinced}]` (`approver.md:19-29`).
  - The approver's evidence is "only what the script produced: the output of the verification commands, the checks and CI conclusions in facts.md, and the diff". Lens reports and handoffs are "agents' words … never evidence themselves" (`merge-policy.md:33-37`).
  - **No component executes the acceptance criteria themselves.** There is no counterpart of run-spec's `acceptance-verifier`. A criterion holds only if the profile's tests, CI or a lens happen to show it.
- **Evidence in the PR.** Principle 8, "Evidence, not claims", is accepted (ADR 0034:62). The PR body is adapted from upstream `pr`. The script appends the verification output and each browser-lens report, folded (`deliver.py` docstring, `deliver.py:118-128`, story 72). **Screenshots and Lighthouse reports stay in the job record. The PR body names them, without images** (ADR 0023:94). There is no video.
- **Runtime verification of the built app.**
  - The UI and UX **browser lenses** drive Chrome DevTools MCP against the app. The script starts the app from the profile's `[app] start` and `ready_urls` (`app_run.py`, `browser.py` docstrings; ADR 0017, ADR 0023).
  - UI covers layout and responsiveness at viewports 375×812, 768×1024 and 1440×900, with at most 12 screenshots. UX covers the flow, the loading, error and empty states, and accessibility, via `lighthouse_audit` (spec #38 "Other details"; ADR 0017:32).
  - Screens behind a login are listed as "not reviewed" and force nothing. `evaluate_script` and `upload_file` are denied.
  - **BUILT-blocked:** #102 says the image carries no Node, chrome-devtools-mcp or Chrome. #103 says a profile with an app and no screen glob starts no lens.
  - **Spike S5** (`spikes/s5-chrome-devtools-mcp/README.md:23-34`) proved headless screenshots and Lighthouse in the container (F2). It also found two problems: the browser sandbox must be switched off (F3), and the browser tool can write into the clone via MCP roots (F5). That is why the script checks the tip and tree after each browser lens.
- **Feature-map-like artifact: none.** Nothing lists features or flows to re-drive. The nearest pieces are the profile's `[app]` table, its `[lenses] screens` globs, and the spec's `## Review lenses` section (`review_trigger.py` docstring). The wayfinder "map" is a planning artifact, not a feature map.
- **Spike S9 limits what "verify passed" proves.**
  - The pilots' verification commands "need no service and pass with nothing listening" (F1).
  - In `med-trilha`, 15 of 96 Go test files need Postgres behind `-tags integration`, and CI does not run them (F3).
  - So "green verify" means unit-level tests on those pilots.
- **Absent:** formal methods (TLA+/Lean), property-based testing, and recorded walkthroughs. A grep of `plugin/`, `docs/` and the research finds none.

## 3. Static and deterministic gates

- **Target repository, profile commands.**
  - `setup = [...]` and `verify = [...]` live in `.software-factory/profile.toml` (spec #38 "Profile schema"; ADR 0020).
  - The profile is always read **from the base commit**, never from the work branch, so an agent cannot weaken its own check. ADR 0010:118 rejected the alternative: "an agent could pass its own verification by editing the command".
  - The profile runs only when the owner has approved its exact content hash (ADR 0020). A **profile check** runs every declared command in a container before that approval (ADR 0026). In effect, the gate is itself tested before it is trusted.
- **Protected list as anti-weakening** (ADR 0010:59-78; `protected_list.py` docstring).
  - Default escalations: the profile, the image definition, instruction files, `.mcp.json`, `.claude/` and git-hook manager config.
  - Profile-declared lists, all escalated: `manifests`, `migrations`, `sensitive`, `lint`, `guards` and `verify_defs`.
  - A test that existed on the base and is deleted or renamed is **escalated**. A modified one is only listed. A new one is nothing. ADR 0010:119 rejected counting assertions as language-specific.
- **Secret scan.** `gitleaks` is pinned and uses the factory's own config. `--ignore-gitleaks-allow` is on. It scans every commit in `<base>..<tip>` (`secret_scan.py` docstring). #92: a merge commit's own diff is not scanned.
- **CI.** Lint and type checks happen only if the target's CI or `verify` runs them; the factory adds no linters of its own. ADR 0034:93 replaced CI checks for protected files, deleted tests, secrets and dependencies with the script's own diff. **ADR 0034:114 dropped the study's `PostToolUse` fast-check hook** because it "cannot stop anything". The script verifies at each integration and before push instead.
- **`CODING_STANDARDS.md`: two different things.**
  1. **In target repositories, nothing is installed** (ADR 0034:94,116). The Standards lens reads whatever `CODING_STANDARDS.md`, `CLAUDE.md`, `AGENTS.md`, glossary or ADRs the repository already has, plus a Fowler smell baseline. It is told to "skip anything a tool already enforces" (`reviewer.md`, "Standards"). So target standards are enforced by **reviewer prose**.
     - A Standards or Spec blocking finding that the fixer dismisses **forces nothing**. Only an open security finding and a discarded lens result force (`review.py:243-248`).
     - The run-spec history shows the fixer dismissed about half of 228 findings (ADR 0016:98-105).
     - #88: steps read the work branch's instruction files, not the base commit's.
  2. **The factory's own `CODING_STANDARDS.md`** says: "Rules a tool enforces live in that tool's config and are not repeated here" (`:3`). It also says: "A `[check candidate]` rule is one a tool could check; it leaves this file when the check exists" (`:9`).
     - Each section opens with "Enforced by tooling:" and names the test that enforces it, e.g. `tests/test_plugin_static.py` (no third-party imports, no shell, no GitHub review submission) and `tests/test_repo_rules.py` (`path:line` citations resolve; ADR shape).
     - Four `[check candidate]` rules are still prose: the ADR-shape rule, Conventional Commits and the ticket trailers (`:113,125,126`).
     - This is the closest analog to "every correction becomes a deterministic check". It applies to the factory repo only.
- **The factory repository itself has no CI** (no `.github/`). The suite runs locally and "can take 2.5 hours" (CLAUDE.md Applied Learning).
- **Hooks.** One `PreToolUse` hook (guard, `onFailure: block`) and one `UserPromptSubmit` hook (size) (`plugin/hooks/hooks.json`). They act only in a host factory session, and they guard state and owner acts, not code quality.

## 4. Learning loop

- **Retro, stage 12** (ADR 0034:10, 118-122; mermaid at :19-29). Owner-initiated and per repository. The script **suggests** one after `retro_after_jobs` ended jobs (default 10); "nothing runs a retro on its own" (`retro_inputs.py` docstring).
- **Inputs.**
  - Ledger entries witnessed by the script, the terminal, the session tool or a hook, never agent-reported ones: verdicts, owner acts, guard events and rework notes.
  - The "Learnings" sections of the handoffs and the failure records, copied at job end (`retro_inputs.py`, `retro_evidence.py` docstrings).
  - Session transcripts are not kept.
- **Output.** A JSON report. Each proposal must cite `ledger:<seq>` or `input:<job>/…` pointers (`retro_report.py` docstring).
  - `change ∈ {checks, standards, glossary, instructions}` becomes a **follow-up request**, and only after the owner accepts it via `sf retro accept`: a terminal act with a typed hash.
  - `profile` becomes a profile discovery, which then needs its own approval (`retro_accept.py` docstring).
  - Findings about the factory are "only listed": "the factory never changes its own plugin" (ADR 0034:121).
- **So a correction becomes a check only through a human-accepted job.** It goes from retro proposal, to follow-up request, to a full job with spec, review, verdict and PR. Nothing is automated, by design: the study warns an automated retro "drifts on false positives" (ADR 0034:129).
- **The learning loop for the approver itself** (ADR 0016; `stage_d.py`, `classify.py`, `pairing.py` docstrings).
  - Each verdict is paired with the owner's next act.
  - The owner classifies the pairs **once**, at the stage-D review: a rework is a `defect` or a `scope` change, and a chosen escalation was `right` or `wrong`.
  - Stage D entry values, written before any data exists so the bar cannot move:
    - at least 30 approvals paired with an owner act;
    - no defect, discard or regression among the last 30 approvals;
    - more than half of chosen escalations right;
    - no regression among approved jobs merged at least 14 days before the review.
  - This is "don't automate a bad loop" made literal. Version one stays at stage C, and stage D is gated on ledger data (ADR 0002; ADR 0034:65).

## 5. Independence, model diversity, adversarial review

- **Principle 3, "The worker never judges its own work"**, is accepted (ADR 0034:57).
  - The implementer no longer runs its own review. The seed's implementer did, but the script now runs it (`review_ticket.py` docstring).
  - Each lens is a separate `claude -p` step with its own agent file and tool list. The reviewer's `Bash` is limited to `git diff` and `git log` (`review_steps.py` docstring).
- **The approver is the most isolated judge.** It runs nothing and reads only its inbox. It "read[s] no comment or review on the pull request" (`merge-policy.md:37`). It treats handoffs and lens reports as claims. It cannot drop a fact, because the script renders the facts (ADR 0029:59). It gives its own call even on forced runs, which the ledger keeps as evidence (ADR 0029:60).
- **Script, not agent, as verifier of record.** These all re-run or re-read in the script, outside the agent's reach: verify after the implementer, the integrator and every fixer; the merge checks in the push mirror; the protected list read from the base; the check that the tip and tree are unchanged after the security and browser lenses (ADR 0017:40).
- **Independence gap.** The **fixer (an agent) adjudicates the reviewers' findings** and may answer `dismissed`. Only for security (and discarded lenses) does dismissal force an escalation. For Standards and Spec, the backstops are the approver's case 4 and the owner. The ledger records the dismissal ratio, but "never call[s] [it] the precision of the review" (ADR 0016:61).
- **Model diversity: none enforced; one vendor.**
  - Agent files pin: `reviewer` Opus/medium, `review-fixer` Opus/medium, `lens-security` Opus/high, `lens-ui` and `lens-ux` Sonnet/high, `explorer` Sonnet/medium (`plugin/agents/*.md` frontmatter).
  - The **implementer, approver, integrator and CI fixer have no agent file**. They pass no `--agent`, and `STEP_COMMAND` sets no `--model` (`agent_step.py:34-40`; calls at `attempt.py:73`, `deliver.py:305`, `ci.py:172`, `ticket_integration.py:133`). The image code sets no model either, so these run on Claude Code's default model.
  - The spec's model/effort table is "the study's table, not accepted by any record" (spec #38).
  - So the author and the judge may be the same model. Independence is by session, prompt and tool restriction, not by model.
- **Adversarial review.** There is no "argue against" pass in the build loop. The Security lens is the adversarial one: it reports only exploitable issues held with more than 80% confidence, each with `file:line`, an exploit and a fix, and it may run non-mutating probes (ADR 0017:38-41). The approver's forced-call design is the other check on judgement.

## 6. Open questions and gaps relevant to verification

**`docs/open-questions.md` has no open verification question.** Every row (Q1-Q18, W1-W5) links an ADR. The real gaps live in spec #38's "Known limits" table and in the open issues.

**Known limits** (spec #38):

- A forged verdict is "found, not prevented".
- "A semantic conflict with the base starts no refresh", left to CI and the owner.
- A starter profile's verify "passes until its trigger file exists". The backstop is acceptance criteria, the Spec lens and the owner.
- The prototype check catches identical files only.
- There is no Rule of Two: the agent that reads untrusted text also writes code (ADR 0034:109).

**Open issues that weaken verification:**

| Issue | Gap |
|---|---|
| #79 | Acceptance runs never done, so seam 3 (the agent texts) is unvalidated |
| #102, #103 | No browser lens can run |
| #99 | The partial-job escalation is never computed |
| #96 | The 2-round review cap restarts per run |
| #95 | `dontAsk` may deny Edit, Write and Bash to real steps |
| #90 | CI commit statuses are misread, so every job escalates |
| #89 | The CI fixer sees only the check's title and summary, never its log |
| #92 | The secret scan misses a merge commit's own diff |
| #88 | Instruction files are read from the work branch, not the base |
| #81 | The discovery-note gate tests existence only |
| #82 | The ledger tail can be rewritten undetected |
| #107 | The integrator's inbox hands over text outside an untrusted block |

**Undecided** (ADR 0029:34): a size threshold for escalation is deferred until there is stage-D data.

## 7. Glossary terms relevant to verification (`GLOSSARY.md`, condensed)

- **Verification command**: profile command whose exit code says the repo is in a good state.
- **Repository profile** / **Profile check** / **Profile approval**: the approved per-repo recipe (setup, verify, app start, protected and lens globs). Every command is run before the owner approves its exact content hash.
- **Lens**: an independent reviewer with a narrow brief. **Lens trigger**: script-computed, never by an agent; the spec can switch a lens on, never off. **Browser lens**: UX or UI, which drives the app; the branch is checked unchanged afterwards.
- **Approver**: judges against the **Merge policy**, which is written "as if the approver merged". Advisory in version one.
- **Verdict**: `APPROVE`/`ESCALATE`; the local copy is authoritative, the PR comment a mirror. **Door**: two-way or one-way. **Blast radius**: what a wrong change could affect.
- **Forced escalation**: computed by the script, cannot be lowered. **Chosen escalation**: the approver's.
- **Protected list**: checked before anything leaves the machine. A **hit** is **Held** (needs a **Clearance**) or **Escalated**.
- **Audit** / **Audit flag**: PR compared with the ledger; blocks nothing.
- **Ledger**: append-only, hash-chained, outlives jobs; pairs each verdict with the owner's next act.
- **Integration**: one ticket merged, "accepted only once the script's checks on it pass". **Integrator**: an agent, called only on a conflict or red verify.
- **Owner act**: counts only through a channel the agent cannot answer. **Rework**: owner change request with a note, later classified.
- **Retro** / **Retro inputs**: per-repo proposals from the ledger and handoff Learnings; each counts only when the owner accepts it.
- **Autonomy stage**: A to E; version one is C. **Seam**: (1) CLI, (2) hook/MCP JSON, (3) agent texts, judged only by acceptance runs. **Spike**: a throwaway probe under `spikes/`.
