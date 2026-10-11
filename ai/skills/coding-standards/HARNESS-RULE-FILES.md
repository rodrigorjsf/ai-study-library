# Harness rule files

Where each agent harness reads repository rules. Fetched from the official docs on 2026-10-11. These paths churn, so this list is a starting point: after checking it, also glob the repo for `**/*rules*`, `**/*.mdc`, `**/*instructions*.md`, and any dot-directory named after an agent tool, and treat what you find as rule files too.

| Harness | Repository locations | Scoping mechanism | Source |
|---|---|---|---|
| Cross-harness | `AGENTS.md` at the root or any subdirectory; nested files apply to their directory | nearest file wins | read by Codex, Cursor, Copilot, Windsurf, Claude Code, and Gemini CLI when configured |
| Claude Code | `CLAUDE.md`, `.claude/CLAUDE.md`, `CLAUDE.local.md`, nested `CLAUDE.md` in subdirectories, `.claude/rules/**/*.md` | `paths:` frontmatter on a rules file; `@path` imports | https://code.claude.com/docs/en/memory |
| Codex | `AGENTS.override.md` then `AGENTS.md`, one per directory from the repo root down to the working directory; extra names via `project_doc_fallback_filenames` | later (deeper) files override; combined size capped by `project_doc_max_bytes` (default 32 KiB) | https://learn.chatgpt.com/docs/agent-configuration/agents-md |
| Cursor | `.cursor/rules/**/*.mdc`; `AGENTS.md` | frontmatter `description`, `globs`, `alwaysApply` | https://cursor.com/docs/context/rules |
| GitHub Copilot | `.github/copilot-instructions.md`; `.github/instructions/**/*.instructions.md`; `AGENTS.md` anywhere; a single root `CLAUDE.md` or `GEMINI.md` | `applyTo:` globs and `excludeAgent:` frontmatter | https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions |
| Gemini CLI | `GEMINI.md` in the workspace and its parents; other names via `context.fileName` in `settings.json` | nested files load when their directory is touched | https://geminicli.com/docs/cli/gemini-md/ |
| Windsurf / Devin Desktop | `.devin/rules/*.md`, fallback `.windsurf/rules/*.md`, legacy `.windsurfrules`; `AGENTS.md` | `trigger:` frontmatter (`always_on`, `model_decision`, `glob`, `manual`); 12,000 characters per file | https://docs.devin.ai/desktop/cascade/memories |

## User-level locations

Rules here apply to every project on the machine and are not in the repository. Read them, point at them, and leave them untouched.

| Harness | User-level locations |
|---|---|
| Claude Code | `~/.claude/CLAUDE.md`, `~/.claude/rules/**/*.md` |
| Codex | `~/.codex/AGENTS.override.md` then `~/.codex/AGENTS.md` (or under `CODEX_HOME`) |
| Cursor | User Rules, held in the app settings with no file path: ask the user what theirs govern, and point at them as `Cursor Settings > Rules (user-level)` with that one line |
| Gemini CLI | `~/.gemini/GEMINI.md` |
| Windsurf / Devin Desktop | `~/.codeium/windsurf/memories/global_rules.md` |

Unverified against official docs, check if present: legacy `.cursorrules` (Cursor), `.clinerules` (Cline), `.roo/rules/` (Roo Code), `CONVENTIONS.md` (Aider), `.junie/guidelines.md` (JetBrains Junie).

## On-demand activation

How a kept, detailed rule file is made to load only when a model needs its guidance. Use the harness's documented mechanism; where it has none, the fallback applies.

| Harness | Mechanism |
|---|---|
| Cursor | frontmatter `alwaysApply: false` with a `description` and no `globs` ("Apply Intelligently": the agent reads the description and decides whether to pull the rule in) |
| Windsurf / Devin Desktop | frontmatter `trigger: model_decision` with a description (only the description sits in the system prompt) |
| Claude Code | no description-triggered mode is documented for `.claude/rules/`. Use `paths:` frontmatter when the detail belongs to specific files; otherwise use the fallback |
| GitHub Copilot | `applyTo:` globs only. Use them when the detail belongs to specific files; otherwise use the fallback |
| Codex, Gemini CLI | no scoped rule files. Use the fallback |

**Fallback:** move the detail to `docs/standards/<name>.md`. A plain doc is never auto-loaded, so it is read only when a model follows the `_Detail:_` pointer in `CODING_STANDARDS.md`.

Write the rule file's `description` as the condition for reading it, matching the condition on its `_Detail:_` pointer.

## What this means for the pointer

- Always-loaded files (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `copilot-instructions.md`, an `alwaysApply` or `always_on` rule) cost context on every turn. In the repository, they keep their non-standards content and get the one-line pointer to `CODING_STANDARDS.md`.
- Several harnesses cap rule-file size (Codex 32 KiB combined, Windsurf 12,000 characters per file). Standards text placed in those files can be silently truncated, which is one more reason it lives in `CODING_STANDARDS.md`.
- Project scoped rule files (`.cursor/rules/*.mdc`, `.claude/rules/*.md`, `.github/instructions/*.instructions.md`, `.devin/rules/*.md`) that declare coding standards are exported into `CODING_STANDARDS.md`, then deleted when short or kept on demand when detailed.
- User-level rule files are the only ones pointed at without export: they sit outside the repository, so they cannot be moved into it.
