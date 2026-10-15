# Analysis: How Claude Remembers a Project

> **Status**: Current
> **Source document**: [Anthropic — How Claude Code Remembers Your Project](https://docs.anthropic.com/en/docs/claude-code/memory)
> **Analysis date**: 2026-03-27
> **Scope**: Claude Code memory persistence mechanisms — CLAUDE.md and auto memory

---

## 1. Executive Summary

The document "How Claude Remembers Your Project" describes two complementary cross-session knowledge persistence mechanisms in Claude Code: **CLAUDE.md files** (instructions written by the user) and **Auto Memory** (notes written by Claude automatically). Both are loaded at the beginning of each session as context — not as enforced configuration — and their effectiveness depends directly on the specificity, conciseness, and structure of the instructions.

The memory system implements a hybrid two-tier architecture: **always-loaded** (CLAUDE.md, first 200 lines of MEMORY.md) and **on-demand** (subdirectory CLAUDE.md, memory topic files, path-scoped rules). This architecture is a direct implementation of the Just-In-Time documentation principle described by Anthropic: maintain lightweight identifiers and load data on demand at runtime. The scope hierarchy (managed policy > project > user > subdirectory) enables granular configuration from organizational level down to specific codebase areas.

Auto memory introduces an elegant emergent documentation mechanism: Claude decides what is worth remembering based on cross-session value, stores it in MEMORY.md (index) + topic files (details), and automatically curates to keep the index under 200 lines. Each git project shares a single auto memory directory (all worktrees and subdirectories). The system is machine-local, plain markdown, and editable by humans at any time.

---

## 2. Key Concepts and Mechanisms

### 2.1 Two Complementary Systems

| | CLAUDE.md | Auto Memory |
|---|-----------|-------------|
| **Who writes** | User | Claude |
| **Content** | Instructions and rules | Learnings and patterns |
| **Scope** | Project, user, or organization | Per working tree |
| **Loaded at** | Every session (complete) | Every session (first 200 lines) |
| **Use for** | Code patterns, workflows, architecture | Build commands, debug insights, preferences |

### 2.2 CLAUDE.md Hierarchy

| Scope | Location | Purpose | Shared with |
|-------|----------|---------|-------------|
| **Managed policy** | `/etc/claude-code/CLAUDE.md` (Linux/WSL) | Organizational instructions (IT/DevOps) | All users |
| **Project** | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Shared project instructions | Team via VCS |
| **User** | `~/.claude/CLAUDE.md` | Personal preferences | Only you |
| **Subdirectory** | `./subdir/CLAUDE.md` | Area-specific, on-demand | Team via VCS |

- CLAUDE.md in the directory hierarchy above the working directory: loaded in full at launch
- CLAUDE.md in subdirectories: loaded on-demand when Claude reads files in those folders
- Managed policy: CANNOT be excluded via `claudeMdExcludes`

### 2.3 Rules System

```
.claude/
├── CLAUDE.md           # Main project instructions
└── rules/
    ├── code-style.md   # Style guidelines
    ├── testing.md       # Testing conventions
    ├── security.md      # Security requirements
    └── frontend/
        └── react.md     # Frontend-specific rules
```

**Rules without `paths` frontmatter**: loaded unconditionally at launch
**Rules with `paths` frontmatter**: loaded when Claude reads matching files

```yaml
---
paths:
  - "src/api/**/*.ts"
---
# API Development Rules
- All API endpoints must include input validation
```

Supported patterns:

| Pattern | Match |
|---------|-------|
| `**/*.ts` | All TypeScript in any directory |
| `src/**/*` | All files under `src/` |
| `*.md` | Markdown in the project root |
| `src/components/*.tsx` | React components in a specific directory |

### 2.4 Import System

CLAUDE.md supports `@path/to/import`:

- Relative paths (relative to the file containing the import)
- Absolute paths
- Recursive imports (max 5 hops)
- Personal imports: `@~/.claude/my-project-instructions.md`

```markdown
See @README for project overview and @package.json for available npm commands.

# Additional Instructions
- git workflow @docs/git-instructions.md
```

### 2.5 Auto Memory

**Location**: `~/.claude/projects/<project>/memory/`
**Structure**:

```
~/.claude/projects/<project>/memory/
├── MEMORY.md          # Concise index, loaded every session
├── debugging.md       # Detailed debugging notes
├── api-conventions.md # API design decisions
└── ...                # Other topic files
```

- `MEMORY.md` (first 200 lines): loaded at startup
- Topic files: loaded on demand by Claude
- Shared across worktrees and subdirectories of the same git repo
- Machine-local (not shared across machines)
- Plain markdown editable at any time

### 2.6 Compaction and CLAUDE.md

CLAUDE.md **fully survives compaction**. After `/compact`, Claude re-reads CLAUDE.md from disk and re-injects it fresh into the session. Instructions given only in conversation (not written in CLAUDE.md) are lost after compaction.

### 2.7 Exclusions for Monorepos

```json
{
  "claudeMdExcludes": [
    "**/monorepo/CLAUDE.md",
    "/home/user/monorepo/other-team/.claude/rules/**"
  ]
}
```

Configurable in any settings layer. Arrays merge across layers. Managed policy CLAUDE.md CANNOT be excluded.

### 2.8 Effective Writing Guidelines

- **Size**: maximum 200 lines per CLAUDE.md file
- **Structure**: Markdown headers and bullets
- **Specificity**: "Use 2-space indentation" instead of "Format code properly"
- **Consistency**: eliminate contradictory instructions across files
- **Verifiability**: each instruction must be concrete enough to verify

---

## 3. Points of Attention

### 3.1 CLAUDE.md is NOT Enforced Configuration

The most critical point: CLAUDE.md is delivered as a user message after the system prompt, not as part of the system prompt. Claude reads and attempts to follow it, but there is NO guarantee of strict compliance, especially for vague or conflicting instructions.

> "CLAUDE.md instructions shape Claude's behavior but are not a hard enforcement layer."

For deterministic enforcement, use **hooks** (which execute outside the model) or **permissions** (in settings.json).

### 3.2 The 200-Line Limit

CLAUDE.md is loaded in full regardless of size. However, files longer than 200 lines:

- Consume more context
- Reduce adherence to instructions
- Important instructions get lost in the noise

The 200-line limit applies ONLY to auto memory's MEMORY.md (content beyond line 200 is not loaded at startup).

### 3.3 Contradictions Across Files

If two CLAUDE.md files, rules, or combinations thereof give contradictory instructions, Claude may choose arbitrarily. Periodic review is mandatory.

### 3.4 Auto Memory is Not Shared

Auto memory is machine-local. Worktrees of the same repo share it, but different machines do not. For shared knowledge, use CLAUDE.md committed to VCS.

### 3.5 Loading Order Matters

CLAUDE.md in the hierarchy above the working directory: loaded at launch (complete).
Subdirectory CLAUDE.md: loaded on-demand (when Claude reads files in that folder).
Rules without paths: loaded at launch.
Rules with paths: loaded when Claude works with matching files.

The "lost in the middle" effect implies that instructions in the middle of long files have a lower probability of being followed.

### 3.6 Compaction Preserves CLAUDE.md but Loses Conversation

CLAUDE.md survives `/compact`. Instructions given only in conversation do NOT survive. If an instruction is important enough to persist, it should be written in CLAUDE.md.

### 3.7 `/init` and Interactive Mode

The `/init` command generates an initial CLAUDE.md by analyzing the codebase. With `CLAUDE_CODE_NEW_INIT=true`, it activates a multi-phase interactive flow that also configures skills and hooks. If CLAUDE.md already exists, `/init` suggests improvements instead of overwriting.

---

## 4. Use Cases and Scope

### 4.1 When to Use CLAUDE.md vs Auto Memory vs Rules

| Scenario | Mechanism | Justification |
|----------|-----------|---------------|
| Project code patterns | CLAUDE.md (project) | Shareable via VCS, applies to everyone |
| Specific build command | Auto Memory | Claude discovers and remembers automatically |
| Per-directory API rules | `.claude/rules/` with `paths` | Loaded only when relevant |
| Personal style preferences | `~/.claude/CLAUDE.md` | Personal, cross-project |
| Organizational security policy | Managed policy | Cannot be excluded, applies to everyone |
| Recurring debugging insights | Auto Memory topic file | Claude loads when relevant |

### 4.2 When to Convert Instructions to Hooks

Criterion: if deterministic enforcement is needed and the instruction can be verified programmatically, convert to a hook.

| Instruction in CLAUDE.md | Equivalent Hook |
|--------------------------|-----------------|
| "Run linter after editing" | `PostToolUse` with matcher `Edit\|Write` |
| "Never commit .env files" | `PreToolUse` with matcher `Bash` + validation |
| "Run tests before pushing" | `PreToolUse` with matcher `Bash` + push detection |

Hooks remove the instruction from the context budget and guarantee enforcement independent of the model.

### 4.3 Organization for Large Teams

1. **Managed policy**: organizational standards (security, compliance)
2. **Project CLAUDE.md**: architecture, conventions, project workflows
3. **`.claude/rules/`**: modular rules by topic and path-scoped
4. **User CLAUDE.md**: personal preferences
5. **`claudeMdExcludes`**: filter out other teams' rules in monorepos

---

## 5. Applicability to Agent Infrastructure

### 5.1 Skills

- **Skills as progressive disclosure**: Skill descriptions are visible at startup; full content only loads when invoked. This is consistent with the JIT philosophy of the memory system.
- **Skills with `disable-model-invocation: true`**: Descriptions stay completely out of context until manual invocation — complements the strategy of keeping CLAUDE.md concise.
- **Skills vs rules**: Rules load every session or when a path matches; skills load when invoked or when Claude determines relevance. For instructions that don't need to always be in context, skills are preferable to rules.
- **Dynamic injection in skills**: `` !`command` `` loads data in real time, implementing pure JIT.

### 5.2 Hooks

- **Hooks as an alternative to CLAUDE.md**: Instructions that can be verified programmatically should be converted from CLAUDE.md to hooks. This removes the instruction from the context budget and guarantees enforcement.
- **`InstructionsLoaded` hook**: Allows logging which instruction files were loaded, when, and why. Useful for debugging path-scoped or lazy-loaded rules.
- **Hooks for memory hygiene**: `PostToolUse` can be used to update auto memory after significant operations.
- **Plugin lifecycle hooks**: Plugin hooks are loaded into the session normally and interact with the memory system in the same way.

### 5.3 Sub-agents

- **Sub-agent memory**: Three scopes (user, project, local) with the same MEMORY.md + topic files mechanism
- **Sub-agents and CLAUDE.md**: Sub-agents load CLAUDE.md and project memory via the normal message flow (they do NOT inherit conversation history)
- **Sub-agent auto memory**: Enabled via the `memory` field in frontmatter. Each sub-agent can have its own memory directory.
- **Sub-agents and rules**: Path-scoped rules are activated when the sub-agent reads matching files

### 5.4 Rules

- **Rules as CLAUDE.md modularity**: When CLAUDE.md grows large, rules allow extracting topical instructions
- **Path-scoped rules**: Implement native progressive disclosure — only loaded when relevant
- **Symlinks for sharing**: Rules support symlinks, enabling shared rules across projects
- **User-level rules**: `~/.claude/rules/` for personal cross-project preferences
- **Priority**: user rules < project rules (project takes higher priority)
- **Recursive discovery**: Rules in subdirectories of `.claude/rules/` are discovered automatically

### 5.5 Memory

- **Two-tier architecture**: MEMORY.md (index, always-loaded, 200 lines) + topic files (on-demand)
- **JIT documentation**: Direct implementation of the pattern described by Anthropic in "Effective Context Engineering"
- **Auto-curation**: Claude moves details to topic files and keeps MEMORY.md concise
- **Hierarchical scope**: Auto memory is machine-local; CLAUDE.md is shareable via VCS
- **Compaction**: CLAUDE.md fully survives; auto memory is unaffected (stored separately)
- **Hygiene**: `/memory` to inspect and edit; periodic review recommended
- **Worktrees**: All worktrees of the same git repo share auto memory

---

## 6. Applicability of the Prompt Engineering Guide

### 6.1 CoT for Sub-agent Reasoning Chains

CLAUDE.md can include CoT instructions that will be loaded in every session: "Before making changes, think step by step about the impact." Auto memory can store reasoning chains that worked well in previous sessions, serving as emergent few-shot CoT.

### 6.2 ReAct for Sub-agents with Tool Access

The memory system supports the ReAct loop indirectly: CLAUDE.md can define the expected workflow (Thought → Action → Observation) and auto memory can remember which tools were effective for which tasks. Path-scoped rules can inject ReAct-specific instructions when Claude works in areas that require tool interaction.

### 6.3 Tree of Thoughts for Exploration Sub-agents

CLAUDE.md can instruct Claude to consider multiple approaches before choosing. Auto memory can store hypotheses explored in previous sessions, preventing re-exploration of already-discarded paths.

### 6.4 Self-Consistency for Validation Across Multiple Sub-agents

Auto memory serves as a historical record that can be used for consistency validation: if a decision in one session contradicts a previous decision stored in memory, Claude can identify and resolve the inconsistency.

### 6.5 Reflexion for Iterative Sub-agent Improvement

Auto memory is the native cross-session Reflexion mechanism:

1. Claude makes a mistake → user corrects → Claude stores the learning in auto memory
2. Next session → Claude consults auto memory → avoids the same mistake

`/memory` allows the user to audit and refine this reflexion process.

### 6.6 Least-to-Most for Task Decomposition Across Sub-agents

CLAUDE.md can define the default task decomposition for the project. Path-scoped rules can provide specific decomposition instructions per codebase area. Auto memory can remember decompositions that worked well previously.

---

## 7. Correlations with Core Documents

### With "Creating Custom Subagents"

Sub-agent memory (the `memory` field in frontmatter) is a special case of the auto memory system. Identical mechanism (MEMORY.md + topic files, 200 lines), but with different scopes (user/project/local in the sub-agent vs per-working-tree in the main auto memory). CLAUDE.md and rules are loaded normally by sub-agents via the message flow.

### With "Orchestrate Teams of Claude Code Sessions"

Each teammate in agent teams loads CLAUDE.md and auto memory independently. The team lead's spawn prompt is NOT stored in memory — only in CLAUDE.md that teammates load. Multiple teammates writing auto memory simultaneously can create redundancy.

### With "Research: Subagent Best Practices"

The research emphasizes that the sub-agent's system prompt is EVERYTHING it has (it does NOT receive history). CLAUDE.md partially mitigates this gap by providing persistent project context. The recommendation of "Consult memory before starting" in the sub-agent's prompt complements the sub-agent auto memory mechanism.

### With "Create Plugins"

Plugins have `settings.json` that can configure `autoMemoryEnabled` and `autoMemoryDirectory`. Plugin skills are progressive disclosure (description at startup, content on-demand), aligning with the JIT philosophy of auto memory.

### With "Research: LLM Context Optimization"

Most direct correlations:

- **200 lines of CLAUDE.md**: aligns with the "instruction budget" of ~2,000–4,000 tokens
- **Path-scoped rules**: implement formal "progressive disclosure"
- **Auto memory MEMORY.md + topic files**: implement "just-in-time documentation"
- **Compaction**: implements "context recycling"
- **`claudeMdExcludes`**: prevents "context poisoning" from irrelevant instructions
- **Lost in the middle**: justifies headers and bullets (structure facilitates attention)
- **Quality over quantity**: "for each line, ask whether removing it would cause errors"

---

## 8. Strengths and Limitations

### Strengths

1. **Elegant simplicity**: Editable markdown files, no database or proprietary format
2. **Scope hierarchy**: Managed > project > user > subdirectory covers all scenarios
3. **Native progressive disclosure**: Path-scoped rules + subdirectory CLAUDE.md
4. **Auto-curation**: Claude manages MEMORY.md autonomously
5. **Survives compaction**: CLAUDE.md is re-read from disk after compact
6. **Import system**: `@path` enables flexible composition
7. **Symlinks for sharing**: Rules can be shared across projects
8. **`/memory` command**: Integrated interface for inspection and editing

### Limitations

1. **Not enforcement**: CLAUDE.md is advisory, not deterministic — the model may ignore instructions
2. **Machine-local**: Auto memory does not sync across machines
3. **200-line limit**: MEMORY.md beyond 200 lines is not loaded automatically
4. **No merge conflict handling**: Multiple agents/worktrees writing auto memory simultaneously may conflict
5. **No versioning**: Auto memory has no change history (unless committed via project scope)
6. **Silent contradictions**: Conflicting instructions are resolved arbitrarily without warning
7. **Context cost**: Long CLAUDE.md consumes tokens from the attention budget

---

## 9. Practical Recommendations

### 9.1 Recommended CLAUDE.md Structure

```markdown
# Project Name

## Build & Test
- `npm install` for dependencies
- `npm test` to run tests
- `npm run lint` for linting

## Architecture
- API handlers: `src/api/handlers/`
- Components: `src/components/`
- Tests: `tests/`

## Code Style
- 2-space indentation
- Named exports (not default exports)
- Async/await (not .then chains)

## Conventions
- Atomic commits with conventional commit format
- PRs must have tests for new features
- Reviews required before merge
```

Keep under 200 lines. For details, use `@path` imports or `.claude/rules/`.

### 9.2 Path-Scoped Rules Pattern

```markdown
<!-- .claude/rules/api-validation.md -->
---
paths:
  - "src/api/**/*.ts"
---

# API Validation Rules
- All endpoints must validate input with zod schemas
- Error responses follow the standard format in src/api/errors.ts
- Include rate limiting metadata in response headers
```

```markdown
<!-- .claude/rules/react-components.md -->
---
paths:
  - "src/components/**/*.tsx"
---

# React Component Rules
- Use functional components with hooks
- Props types defined with TypeScript interfaces (not type aliases)
- Extract custom hooks to src/hooks/
```

### 9.3 CLAUDE.md → Hooks Conversion Strategy

Periodic audit:

1. List all instructions in CLAUDE.md
2. For each instruction, ask: "Can this be verified programmatically?"
3. If YES: convert to `PreToolUse` or `PostToolUse` hook
4. If NO: keep in CLAUDE.md
5. Result: smaller CLAUDE.md, deterministic hooks, optimized context budget

### 9.4 Auto Memory Hygiene

1. Run `/memory` periodically to review what Claude has stored
2. Remove outdated or incorrect entries
3. Consolidate redundant entries
4. Verify that MEMORY.md is under 200 lines
5. Consider moving valuable knowledge to CLAUDE.md (where it will be loaded in full)

### 9.5 Monorepo: Context Isolation

```json
// .claude/settings.local.json (not committed)
{
  "claudeMdExcludes": [
    "**/other-team/CLAUDE.md",
    "**/legacy-service/.claude/rules/**",
    "**/infrastructure/CLAUDE.md"
  ]
}
```

Combine with path-scoped rules to ensure only instructions relevant to your work area are loaded.
