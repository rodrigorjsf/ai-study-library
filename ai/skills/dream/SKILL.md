---
name: dream
description: Memory consolidation: orient, gather session/transcript signal, merge+prune topic files, update MEMORY.md. Trigger: dream, consolidate, sync memory. Flags: --project (default), --user.
argument-hint: "[--project] [--user]"
model: opus
effort: xhigh
---

# Dream — Memory Consolidation

A dream is a reflective pass over your memory files. The goal is to turn recent ephemeral signal (session logs, transcripts, in-flight conversations) into durable, well-organized memories so future sessions can orient quickly.

This skill mirrors the core Claude Code dream prompt, adapted so the user can invoke it explicitly with a scope flag. It can also be invoked autonomously by Claude when consolidation will obviously help (e.g., end of a long session, after the user makes several corrections or strong preference statements).

## Arguments

| Flag         | Scope                                | Transcripts source                          |
|--------------|--------------------------------------|---------------------------------------------|
| `--project`  | Memory tied to the current project    | `~/.claude/projects/<project-slug>/*.jsonl` |
| `--user`     | Global, cross-project user memory     | `~/.claude/projects/*/*.jsonl`              |

**Default behavior with no flag:** treat as `--project`. Project scope is the safer default for both explicit and autonomous invocations — it can't unintentionally write to global memory the user didn't expect to be touched.

**Both flags:** run two consolidation passes, project first, then user. Report each separately.

**Unknown flags:** stop and ask. Don't guess.

### Resolving the memory directory

**Project scope (`--project`):**

`<project-slug>` is the current project's absolute path with `/` replaced by `-` and prefixed with `-`. Example: `/home/rodrigo/Workspace/ai-study-library` → `-home-rodrigo-Workspace-ai-study-library`. Resolve it from `pwd` at runtime — do not hardcode.

Memory dir → `~/.claude/projects/<project-slug>/memory/`.

If it doesn't exist, create it (`mkdir -p`) before writing — this is a known, project-local path that the auto-memory system already uses.

**User scope (`--user`):**

There is no single canonical path for cross-project user memory. Probe in this order and use the first one that exists:

1. The path set in the `CLAUDE_USER_MEMORY_DIR` environment variable, if defined.
2. `~/.claude/memory/`.
3. `~/.claude/user-memory/`.

If none exist, **stop and ask the user** which path to use (or whether to create `~/.claude/memory/` as a new convention). Don't silently create a directory at the user-global level — that's a side effect the user didn't authorize. Once the user confirms a path on first run, suggest they record it in `~/.claude/CLAUDE.md` so future invocations skip the prompt.

## When to use

- User invokes `/dream`, `/dream --project`, `/dream --user`, or `/dream --project --user`.
- User says phrases like: "dream", "consolidate memories", "do a memory pass", "review what you remember", "sync memory before I switch projects", "tidy `MEMORY.md`".
- Autonomously, when wrapping up a long session that produced multiple corrections, validated approaches, or new project facts that future sessions would benefit from. Announce the intent before writing — do not silently rewrite memory.

## When not to use

- Single-fact saves. If the user just said "remember that X", write that one memory directly per the auto-memory rules in the system prompt — no full dream pass required.
- During the middle of a task. A dream is a reflective pass, not a way to organize in-flight scratch work. Use a plan or task list for that.
- When the user asks to *forget* something. Find and remove the specific entry; don't sweep the whole memory.

---

## Executor procedure

**You** (the executor, running this skill inline) complete these steps synchronously, then stop. Do not enter the consolidation phases yourself.

### Step 1 — Parse flags

Identify which scopes are requested. Default to `--project` if no flag is given.

### Step 2 — Resolve absolute paths

The subagent cannot access `pwd` or expand `~`. Resolve everything now:

- **Project scope:** run `pwd` to get the working directory, derive the project slug, and expand the full path. Example: `pwd` → `/home/rodrigo/Workspace/ai-study-library` → memory dir → `/home/rodrigo/.claude/projects/-home-rodrigo-Workspace-ai-study-library/memory/`.
- **User scope:** probe the three candidate paths. If none exist, **stop here and ask the user** — the subagent cannot ask interactively. Once confirmed, use the absolute path.
- **Never pass `~` or relative paths** in the subagent prompt.

### Step 3 — Summarize current-session signal

The subagent has no access to this conversation's history. Extract any durable signal now and prepare a `## Current session notes` block to inject into the prompt. Include:

- Corrections or validated preferences the user expressed in this session.
- New project facts, references to external systems, or decisions made.
- Anything else that a future session should know.

If the current conversation has no notable durable signal, write: `No notable session signal — standard consolidation pass only.`

### Step 4 — Build the subagent prompt

Assemble the prompt as follows:

```
You are running a Dream — Memory Consolidation pass.

## Scope
<project | user | project + user>

## Memory directory
<fully resolved absolute path(s)>

## Transcripts source
<fully resolved absolute path(s)>

## Current session notes
<content from Step 3>

---

<embed the full "Subagent template" section below verbatim, starting from "Source of truth for memory format">
```

For `--project --user`: include both paths and instruct the subagent to run two sequential passes (project first, then user). The final report must cover each scope separately.

### Step 5 — Spawn the subagent

```
Agent(
  model="opus",
  run_in_background=true,
  description="Dream — memory consolidation (<scope> — <resolved-path>)",
  prompt=<assembled prompt from Step 4>
)
```

Include in the prompt: "Run all five phases completely. Do not skip or short-circuit any phase. Read every file the phases specify."

### Step 6 — Announce and stop

Tell the user in one message:
- Which scope is running
- The resolved memory path(s)
- That they'll receive a notification when consolidation is complete

Then stop. Do not read any memory files, do not execute any consolidation phase yourself.

---

## Subagent template

> Embed the content below verbatim in the Agent prompt (Step 4 above).

### Source of truth for memory format

Your system prompt's **auto-memory** section is authoritative for:

- Memory file format (frontmatter with `name`, `description`, `type`)
- Allowed types (`user`, `feedback`, `project`, `reference`)
- Body structure for `feedback` and `project` types (rule/fact, then `**Why:**`, then `**How to apply:**`)
- What NOT to save (code patterns, file paths, git history, ephemeral state, anything already in `CLAUDE.md`)
- The role of `MEMORY.md` as a one-line index, not a content dump

Re-read those rules before writing. This skill orchestrates the *pass*; the system prompt defines the *artifact*.

---

### Phase 1 — Orient

For the chosen scope:

1. `ls <memory-dir>` to see what already exists.
2. Read `<memory-dir>/MEMORY.md` if it exists. This is the index.
3. Skim existing topic files (`*.md` other than `MEMORY.md`) so you improve them rather than creating near-duplicates. Don't read everything — sample by topic.
4. `ls -R <memory-dir>/logs/` if a logs directory exists. Each session is a single file under `logs/YYYY/MM/DD/<id>-<title>.md`. If no logs directory exists, skip — you'll fall back to JSONL transcripts.
5. If a `<memory-dir>/sessions/` subdirectory exists, scan recent entries there too.

If `MEMORY.md` doesn't exist, plan to create it during Phase 4. If the memory directory itself doesn't exist, `mkdir -p` it.

### Phase 2 — Gather recent signal

Look for new information worth persisting. The executor has already injected a `## Current session notes` block at the top of this prompt — treat it as a primary source alongside the sources below.

Sources, in priority order:

1. **Current session notes.** Read the `## Current session notes` block injected by the executor. These are pre-extracted durable signals from the triggering session that you cannot access directly.

2. **Session logs.** If `logs/YYYY/MM/DD/<id>-<title>.md` files exist, read the most recent 1–3 days. Each line is prefix-coded — `>` user, `<` assistant, `.` tool call. The filename title tells you what the session was about, so you can skip irrelevant ones cheaply.

3. **Drifted memories.** Look at existing topic files and ask: does anything here contradict what I see in the project right now? Renamed files, removed flags, superseded decisions — note them for Phase 3 fixes.

4. **Transcript search (narrow).** Transcripts are large JSONL files. Never read them whole. Grep for narrow terms only when you already suspect something matters:

   ```bash
   grep -rn "<narrow term>" <transcripts-source> --include="*.jsonl" | tail -50
   ```

   Examples of "narrow terms": a specific error message, a flag name, a person's name, a Linear/Jira ticket ID. Don't grep generic words like "bug" or "fix".

Stay in budget. You're harvesting durable signal, not transcribing recent activity. If nothing new is worth saving, that's a valid outcome — say so in the summary.

### Phase 3 — Consolidate

For each thing worth remembering, write or update a memory file at the top level of the memory directory.

- **Format and type conventions** → see the auto-memory section of your system prompt. Don't re-derive them here.
- **Merge, don't duplicate.** If a topic file already exists for this subject, update it. Create a new file only when no existing topic fits.
- **Convert relative dates to absolute dates.** "Yesterday" / "last week" / "next Thursday" become `YYYY-MM-DD` so the memory remains interpretable later. Today's date is available in your environment context.
- **Delete contradicted facts at the source.** If an old memory says X and the project now does Y, fix the file — don't append a footnote.
- **Don't save what doesn't belong.** Code patterns, file paths, project structure, recent diffs, debugging recipes, anything already in `CLAUDE.md` — these are derivable from the codebase or git, not memory material. The auto-memory exclusion list applies here in full.

### Phase 4 — Prune and index

Update `<memory-dir>/MEMORY.md`:

- **Format:** one line per pointer, under ~150 chars: `- [Title](file.md) — one-line hook`. No frontmatter. No memory content inside the index.
- **Size limits:** keep it under **200 lines** AND under ~25KB. Lines past 200 get truncated by the harness, so anything beyond that is dead weight.
- **Prune** pointers to memories that are now stale, wrong, or superseded. If you deleted a memory file in Phase 3, remove its index line too.
- **Demote verbose entries.** Any index line over ~200 chars is carrying content that belongs in the topic file. Shorten the line, move the detail.
- **Add pointers** for any newly important memories created in Phase 3.
- **Resolve contradictions.** If two index lines (or two files) disagree, fix the wrong one — don't leave both.

If `MEMORY.md` did not exist before this pass, create it now from the topic files present.

### Phase 5 — Reconcile with `CLAUDE.md` (optional, scope-aware)

If the project has a `CLAUDE.md` (project scope) or the user has a global `~/.claude/CLAUDE.md` (user scope), do a quick reconciliation pass:

- If a memory restates something already in `CLAUDE.md`, prefer the `CLAUDE.md` version and remove the redundant memory.
- If a memory contradicts `CLAUDE.md`, surface the conflict in your summary — don't silently overwrite either side.

This phase is best-effort. Skip it cleanly if no `CLAUDE.md` is present.

---

### Final report

Return a brief summary covering:

- **Scope(s) consolidated** (`project` and/or `user`) and the resolved memory directory paths.
- **Created** — new memory files (with one-line hook each).
- **Updated** — existing memory files changed, with a one-line note on what changed.
- **Pruned** — removed files or removed index lines, with the reason.
- **Conflicts surfaced** — anything you couldn't resolve unilaterally (e.g., a `CLAUDE.md` vs memory disagreement) that the user should look at.

If nothing changed because memories were already tight, say exactly that. A clean dream that finds nothing to do is a valid result, not a failure.

### Examples

**Example 1 — explicit project pass**

> User: `/dream --project`

→ Executor resolves project slug from `pwd`, expands memory path to absolute form, extracts session notes, spawns opus background agent with full template embedded. Announces: "Dream started — project scope at `/home/rodrigo/.claude/projects/-home-…/memory/`. You'll be notified when done."

**Example 2 — both scopes**

> User: `/dream --project --user`

→ Executor resolves both paths (probing user-memory candidates inline), spawns one background agent instructed to run two sequential passes. Final report covers each scope separately.

**Example 3 — autonomous invocation at end of session**

> User (after a 90-minute session with several corrections): "ok I'm done for today, anything else before I close?"

→ Offer: "Want me to dream a project pass to consolidate today's corrections into memory? I'd update X and Y." Wait for confirmation before spawning.

**Example 4 — single fact, skill should NOT trigger**

> User: "remember I prefer rebase over merge"

→ Don't run a dream. Save the single feedback memory directly per auto-memory rules.
