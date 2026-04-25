# CLAUDE.md Injection

`harness-kb init` writes a marked block into the consumer project's `CLAUDE.md` so agents always reach for the tool when working on the listed themes. The block is idempotent: running `init` again replaces the existing block with the current version's content.

## What gets written

The exact content (with `{version}` substituted at runtime by the package's `__version__`):

```markdown
<!-- harness-kb v{version} BEGIN -->
## Harness Knowledge Base (`harness-kb`)

This project has access to `harness-kb` — a portable, version-pinned knowledge base of agent / harness / context-engineering reference material drawn from the `ai-study-library` corpus. **Always consult `harness-kb` before implementing, designing, or reasoning about any of the following themes:**

- agent-protocols (MCP, A2A, ACP, ANP)
- agentic-engineering (RPI, harness patterns, plan-implement workflows)
- analysis (study notes on LLM agent papers and posts)
- claude (Claude-specific guides: prompting, harnesses, long-running agents)
- claude-code (Claude Code: hooks, skills, plugins, settings, IDE)
- context-engineering (smart zone, progressive disclosure, attention sinks, context rot)
- cursor (Cursor IDE: rules, hooks, subagents, plugins, agent tools)
- general-llm (LLM behavior, evaluation, structured outputs)
- harness-engineering (canonical patterns, references, skills, agents, hooks, evals)
- human-layer-project (HumanLayer codebase as case study)
- long-context-research (Lost-in-the-Middle, recall curves, chunking)
- mcp (Model Context Protocol: primitives, runtime, governance)
- shared (cross-cutting reference material)
- spec-driven-development (Spec Kit, Constitutional Foundation, SDD tools)
- structured-outputs (tool use, JSON schema, strict mode, prefilling)
- tool-calling (tool design, programmatic tool calling, search)

### How to use it

**Discovery:**

    harness-kb themes                          # what topics are available
    harness-kb docs list --theme <name>        # docs in a theme
    harness-kb wiki list                       # graph-derived wiki pages

**Retrieval (prefer section over full doc to save context):**

    harness-kb docs section <path> "<heading>" # one section
    harness-kb docs search "<query>"           # ranked BM25 hits
    harness-kb wiki get <page-name>            # wiki page

**Graph queries (concept-level reasoning):**

    harness-kb graph query "<text>"            # fuzzy substring over node labels
    harness-kb graph explain "<node-label>"    # node + 1-hop neighbors
    harness-kb graph path "<from>" "<to>"      # path between concepts
    harness-kb graph community "<name>"        # all nodes in a community

**Native MCP server (preferred for agents — typed tools, persistent context):**

    harness-kb --mcp

Configure in `.claude/settings.json` under `mcpServers` if Claude Code is the harness, or via the equivalent block for other agent runtimes.

### Comprehensive playbook (heavy — ~1500 lines, ~30K tokens)

When you want **complete coverage** of harness-engineering concepts, examples, primary-source references, and 281 pre-built graph queries before writing any artifact or memory, consult the playbook:

    harness-kb guide toc                       # outline first (cheap)
    harness-kb guide section "<H2>"            # one section at a time (preferred)
    harness-kb guide search "<query>"          # find relevant sections
    harness-kb guide --confirm                 # full file — only when you genuinely need it all

Loading the full playbook costs ~30K tokens. Default to `toc` + targeted `section` retrieval.

### When to consult

- Before writing skills, hooks, agents, plugins, rules, or any harness artifact.
- Before designing context-management strategies (always-loaded memory, progressive disclosure, subagent dispatch).
- Before implementing tool-use schemas, structured-output contracts, or MCP servers.
- When debugging recurring agent failures — check whether a known pattern (smart-zone violation, lost-in-the-middle, context rot) explains the symptom.
- When choosing between architectural options (heavy-stack vs lean-shell, MCP vs A2A, hooks vs slash commands).

### Examples

    # Find docs about back-pressure
    harness-kb docs search "back-pressure"

    # What's in the smart-zone concept space?
    harness-kb graph explain "Dumb Zone / Smart Zone (Context Threshold)"

    # How are skills and progressive disclosure connected?
    harness-kb graph path "Agent Skills Standard" "Progressive Disclosure (Skills Context Management)"

`harness-kb --version` shows the bundled data snapshot. To upgrade the snapshot: upgrade the package.
<!-- harness-kb v{version} END -->
```

## Idempotency rules

- Default project = current working directory. `--project <path>` overrides.
- If `<project>/CLAUDE.md` does not exist: create it with this block as the sole content.
- If exists and contains `<!-- harness-kb v` markers: replace the block (idempotent upgrade). Both BEGIN and END markers must be present for replacement; if only one is found, abort with an error rather than corrupt the file.
- If exists without markers: ensure the file ends with exactly one trailing newline, then append a blank line, then append the block. The block itself ends with one trailing newline.
- `--dry-run`: print what would change, do not write.
- `uninit`: remove the marked block; leave the rest of CLAUDE.md untouched.

## Removing the block

`harness-kb uninit --project <path>` removes the marked block and leaves the rest of `CLAUDE.md` untouched. Run this before `pipx uninstall harness-kb`.
