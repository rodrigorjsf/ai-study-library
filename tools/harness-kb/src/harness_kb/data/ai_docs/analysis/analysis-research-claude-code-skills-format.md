# Analysis: Research Claude Code Skills & Plugin Marketplace Format

> **Status**: Current
> **Source document**: [`docs/skills/research-claude-code-skills-format.md`](../skills/research-claude-code-skills-format.md)
> **Analysis date**: 2026-03-27
> **Scope**: Analysis of the research document on Claude Code skills formats, plugins, and marketplaces

---

## 1. Executive Summary

The document "Research: Claude Code Skills & Plugin Marketplace Format" is a technical research piece that maps the complete Claude Code extensibility ecosystem across three layers: Standalone Skills (SKILL.md following the Agent Skills standard), Plugins (packages that bundle skills + agents + hooks + MCP/LSP servers), and Marketplaces (plugin catalogs distributed via GitHub repositories). The research was conducted in March 2026 using official Anthropic sources, the open Agent Skills standard, and community repositories.

The most significant contribution of this document is the clarification of the distribution ecosystem: there is no `npx skills add` — installation occurs via `/plugin install` within Claude Code or `claude plugin install` on the CLI. This corrects a common misconception and positions the plugin system as the canonical distribution mechanism. The document also maps SKILL.md cross-agent compatibility, demonstrating that the same file works in Claude Code (`.claude/skills/`), VS Code/GitHub Copilot (`.agents/skills/`), and OpenAI Codex.

The third contribution is the documentation of the distinction between the Agent Skills Open Standard (minimum fields: `name` and `description`) and Claude Code proprietary extensions (`disable-model-invocation`, `context`, `agent`, `hooks`, `model`, `effort`). This distinction is critical for authors who wish to create portable skills vs skills that leverage advanced Claude Code capabilities.

---

## 2. Key Concepts and Mechanisms

### 2.1 The Three Layers of Extensibility

The document reveals a three-layer architecture that scales from simple to complex:

```
Layer 1: Skill (SKILL.md)
  - Atomic unit of extension
  - Format: directory with SKILL.md + supporting files
  - Invocation: /skill-name

Layer 2: Plugin (directory with .claude-plugin/)
  - Distribution package bundling multiple components
  - Contains: skills/ + agents/ + hooks/ + .mcp.json + .lsp.json
  - Invocation: /plugin-name:skill-name
  - Manifest: .claude-plugin/plugin.json

Layer 3: Marketplace (repository with marketplace.json)
  - Plugin catalog for discovery and installation
  - Contains: .claude-plugin/marketplace.json + plugins/
  - Installation: /plugin install name@marketplace
```

### 2.2 Agent Skills Open Standard vs Claude Code Extensions

**Open standard fields (agentskills.io):**

| Field | Required | Limit |
|-------|----------|-------|
| `name` | Yes* | 64 chars, kebab-case |
| `description` | Yes* | 1024 chars |
| `license` | No | - |
| `compatibility` | No | 500 chars |
| `metadata` | No | Arbitrary key-value |
| `allowed-tools` | No (experimental) | Space-separated list |

*In Claude Code, both are technically optional with fallbacks: `name` uses the directory name, `description` uses the first paragraph of content.

**Claude Code proprietary extensions:**

| Field | Function |
|-------|----------|
| `argument-hint` | Autocomplete hint (e.g., `[issue-number]`) |
| `disable-model-invocation` | Prevents automatic invocation by Claude |
| `user-invocable` | Hides from `/` menu (background knowledge) |
| `model` | Model override when skill is active |
| `effort` | Effort level: low, medium, high, max |
| `context` | `fork` for execution in isolated subagent |
| `agent` | Subagent type (Explore, Plan, general-purpose) |
| `hooks` | Hooks scoped to the skill lifecycle |

**Portability implication**: Skills using only open standard fields work in Claude Code, VS Code/Copilot, and OpenAI Codex. Skills with Claude Code extensions are platform-specific.

### 2.3 Name Validation Rules

The document details strict validation rules:

- 1-64 characters
- Only lowercase `a-z`, numbers, and hyphens
- CANNOT start or end with `-`
- CANNOT contain consecutive `--`
- MUST match the parent directory name
- CANNOT contain reserved words: "anthropic", "claude"
- CANNOT contain XML tags

### 2.4 Substitution Variables

| Variable | Description | Usage Example |
|----------|-------------|---------------|
| `$ARGUMENTS` | All arguments | `Analyze $ARGUMENTS` |
| `$ARGUMENTS[N]` / `$N` | Argument by index | `Migrate $0 from $1 to $2` |
| `${CLAUDE_SESSION_ID}` | Session ID | Logging, correlation |
| `${CLAUDE_SKILL_DIR}` | Skill directory | Bundled scripts |

### 2.5 Dynamic Context Injection

The `` !`<command>` `` syntax executes shell commands BEFORE sending to Claude:

```markdown
- Diff: !`gh pr diff`
- Comments: !`gh pr view --comments`
```

**Mechanism**: Pure pre-processing. The command executes, the output replaces the placeholder, Claude receives only the final result. It is not execution by Claude.

### 2.6 Complete Plugin Structure

```
my-plugin/
  .claude-plugin/
    plugin.json          # Manifest (optional — auto-discovery works)
  skills/                # Skills (Agent Skills format)
  agents/                # Subagent definitions
  commands/              # Legacy commands (markdown)
  hooks/
    hooks.json           # Hook configurations
  scripts/               # Scripts for hooks and utilities
  settings.json          # Default settings
  .mcp.json              # MCP servers
  .lsp.json              # LSP servers
```

**Minimum plugin.json field**: Only `name` is required if the manifest exists. The manifest itself is optional — Claude Code auto-discovers components in default locations.

**Environment variables for plugins:**

- `${CLAUDE_PLUGIN_ROOT}` — Absolute path to the installation directory (changes on updates)
- `${CLAUDE_PLUGIN_DATA}` — Persistent data directory that survives updates

### 2.7 marketplace.json Format

```json
{
  "name": "marketplace-name",
  "owner": { "name": "Org", "email": "team@org.com" },
  "metadata": { "description": "...", "version": "1.0.0" },
  "plugins": [
    {
      "name": "plugin-name",
      "source": "./plugins/plugin-name",
      "description": "...",
      "version": "1.0.0"
    }
  ]
}
```

**Supported source types:**

- Relative path: `"./plugins/my-plugin"`
- GitHub repo: `{ "source": "github", "repo": "owner/repo" }`
- Git URL: `{ "source": "url", "url": "https://..." }`
- Git subdirectory: `{ "source": "git-subdir", "url": "...", "path": "tools/plugin" }`
- npm package: `{ "source": "npm", "package": "@acme/plugin" }`

**Strict mode:**

- `true` (default): `plugin.json` is authoritative; marketplace entry only supplements
- `false`: Marketplace entry is the complete definition

### 2.8 Installation Mechanism

```bash
# Add marketplace
/plugin marketplace add owner/repo

# Install plugin
/plugin install plugin-name@marketplace-name

# Non-interactive CLI
claude plugin install formatter@my-marketplace --scope project

# Installation scopes
# user (default) - personal, all projects
# project - shared via .claude/settings.json
# local - gitignored, only for you on this project
```

### 2.9 Progressive Disclosure Model

The document formalizes the 3-level model:

1. **Metadata** (~100 tokens): `name` + `description` — loaded at startup for ALL skills
2. **Instructions** (<5000 tokens recommended): SKILL.md body — loaded when skill is activated
3. **Resources** (as needed): Scripts, references, assets — loaded on demand

---

## 3. Points of Attention

### 3.1 Common Errors and Misconceptions

1. **`npx skills add` misconception**: DOES NOT EXIST. Installation is via `/plugin install` or `claude plugin install`. Community tools like CCPI may offer alternatives, but they are not official.

2. **`skills.json` misconception**: There is NO skills manifest. The "manifest" is the SKILL.md itself (frontmatter). For plugins, the manifest is `plugin.json`. For marketplaces, `marketplace.json`.

3. **Assumed portability**: Skills with Claude Code fields (`context`, `hooks`, `agent`) DO NOT work in VS Code/Copilot or OpenAI Codex. Only open standard fields are portable.

4. **Name vs directory**: The `name` field MUST match the parent directory name. A skill in `my-skill/SKILL.md` must have `name: my-skill`.

5. **Plugin namespace**: Plugin skills use `plugin-name:skill-name`. Project/personal skills DO NOT have a namespace — conflicts are resolved by priority (enterprise > personal > project).

### 3.2 Context Pitfalls

- **Skill descriptions consume 2% of the context window**: With many skills, the description budget can silently overflow
- **plugins.json strict mode**: In strict mode (default), inconsistencies between plugin.json and marketplace.json can cause unexpected behavior
- **Auto-discovery in monorepo**: Claude auto-discovers `.claude/skills/` in subdirectories when editing files there. This can load unexpected skills.

### 3.3 Gaps Identified by the Document

The document itself identifies important gaps:

1. **No `npx skills add`**: The standalone skill distribution mechanism (without plugin wrapper) is limited to manual copying
2. **No `skills.json`**: There is no skill collection manifest. Each skill is self-contained
3. **Minimal open standard**: The Agent Skills Open Standard defines only SKILL.md with name + description. Claude Code adds most of the functionality
4. **Limited cross-agent compatibility**: Although the format is the same, advanced features are platform-specific

---

## 4. Use Cases and Scope

### 4.1 Distribution Decision

| Scenario | Recommended Mechanism |
|----------|----------------------|
| Personal skill for my workflow | `~/.claude/skills/skill-name/SKILL.md` |
| Skill shared with team | `.claude/skills/skill-name/SKILL.md` (commit) |
| Collection of skills + hooks + MCP | Plugin with `.claude-plugin/plugin.json` |
| Public distribution of multiple plugins | Marketplace with `marketplace.json` |
| Cross-platform skill (Claude + Copilot) | Use only open standard fields |
| Skill with advanced Claude Code features | Use proprietary extensions (accept lock-in) |

### 4.2 When to Create Plugin vs Standalone Skill

**Standalone skill when:**

- Single, self-contained functionality
- No need for hooks, MCP, or LSP
- Distribution via copy/git is sufficient
- Cross-agent portability is desired

**Plugin when:**

- Multiple related skills
- Need for integrated hooks
- Need for MCP/LSP servers
- Distribution via marketplace desired
- Default settings needed (settings.json)
- Utility scripts shared across skills

### 4.3 When to Use Marketplace vs Direct Distribution

**Marketplace when:**

- Multiple plugins for discovery
- Team/organization with internal catalog
- Automatic versioning and updates desired
- Need for categories and tags for discovery

**Direct distribution (GitHub repo) when:**

- Single plugin
- Manual updates are acceptable
- Simplicity is the priority

---

## 5. Applicability to Agent Infrastructure

### 5.1 Skills (Design Patterns for Portability)

**Pattern 1: Portable skill (pure open standard)**

```yaml
---
name: code-review-checklist
description: Code review checklist. Use when reviewing PRs, performing code review, or analyzing code quality.
---

# Code Review Checklist

## Correctness
- Is the logic correct for all edge cases?
- Are inputs properly validated?

## Performance
- Are there N+1 queries?
- Unnecessary loops?

## Security
- Are inputs sanitized?
- Is authorization verified?
```

This skill works identically in Claude Code, VS Code/Copilot, and OpenAI Codex.

**Pattern 2: Advanced skill (Claude Code extensions)**

```yaml
---
name: security-scan
description: Automated security scan of the codebase
context: fork
agent: Explore
disable-model-invocation: true
allowed-tools: Read, Grep, Glob
effort: high
hooks:
  PostSkillExecution:
    - command: "echo 'Scan completed on $(date)' >> security-scan.log"
---

# Security Scan

1. Identify all entry points (HTTP endpoints, handlers)
2. For each point, verify:
   - Input validation
   - Authorization
   - Rate limiting
3. Generate report prioritized by severity
```

This skill leverages the full potential of Claude Code but does not work on other platforms.

**Cross-platform composition strategy:**

```
my-skill/
  SKILL.md              # Instructions using only the open standard
  .claude-extensions.md  # Claude Code extensions (referenced only in SKILL.md
                         # with conditional instructions)
```

### 5.2 Hooks (Integration with Plugins)

The plugin format allows bundling hooks alongside skills:

```json
// hooks/hooks.json
{
  "PreToolExecution": [
    {
      "matcher": "Bash",
      "hooks": [
        { "command": "python ${CLAUDE_PLUGIN_ROOT}/scripts/validate.py" }
      ]
    }
  ]
}
```

**Hook-skill integration patterns:**

1. **Pre-skill hook**: Pre-condition validation before skill execution
2. **Post-skill hook**: Logging, notification, or cleanup after execution
3. **Hook that triggers skill**: Hook detects event and instructs skill invocation
4. **Skill that configures hooks**: Setup skill that installs hooks in the project

### 5.3 Subagents (Composition via Plugins)

Plugins allow bundling custom agents:

```markdown
# agents/data-analyst.md
---
skills:
  - plugin-name:bigquery-skill
  - plugin-name:visualization-skill
allowed-tools: Read, Grep, Glob, Bash(bq *)
model: claude-sonnet-4-5-20250514
---

You are a specialized data analyst.
Use the loaded skills to answer data queries.
```

**Subagent-plugin composition patterns:**

| Pattern | Description | Use Case |
|---------|-------------|----------|
| Subagent with preloaded skills | Agent .md with `skills` field | Domain knowledge specialist |
| Skill with fork to subagent | SKILL.md with `context: fork` | Isolated task with focused output |
| Plugin as deployment unit | Plugin bundles agent + skills + hooks | Complete package for a domain |

### 5.4 Rules (Complement in Plugin)

Plugins can include rules via `CLAUDE.md` in the plugin directory (loaded when the plugin is active). This enables:

- Domain-specific rules for the plugin
- Conventions that complement plugin skills
- Integration instructions with the host project

### 5.5 Memory (Plugins with Persistent Data)

The `${CLAUDE_PLUGIN_DATA}` variable points to a persistent directory that survives plugin updates:

```
~/.claude/plugins/data/{plugin-id}/
```

This enables:

- Cross-session result caching
- Persistent user settings
- Execution history
- Shared state between skills of the same plugin

**Template for skill using persistent data:**

```yaml
---
name: project-stats
description: Project statistics with history
---

## Statistics Collection

1. Collect current project metrics
2. Compare with history in ${CLAUDE_PLUGIN_DATA}/stats-history.json
3. Generate trends report
4. Save current metrics to history
```

---

## 6. Prompt Engineering Guide Applicability

### 6.1 CoT for Multi-Step Workflows in Plugins

Plugins that bundle multiple skills benefit from explicit CoT for orchestration. The guide documents that CoT improves multi-step reasoning from 17.9% to 58.1%:

```yaml
---
name: full-audit
description: Complete project audit (security + performance + quality)
context: fork
---

Conduct the audit using chain of thought reasoning:

1. **Reasoning**: Which aspect should I analyze first and why?
2. **Security**: Run security analysis (OWASP patterns)
3. **Reasoning**: Given the security findings, what performance impact do I expect?
4. **Performance**: Analyze performance points
5. **Reasoning**: Which quality issues might cause the problems already found?
6. **Quality**: Code quality analysis
7. **Synthesis**: Consolidate findings with cross-category dependencies
```

### 6.2 ReAct for Tool-Using Skills in Plugins

The ReAct pattern is natural for plugin skills that integrate with external tools (MCP, Bash, etc.). The guide documents a +34% success rate:

```yaml
---
name: data-pipeline-debug
description: Data pipeline debugging
allowed-tools: Bash(bq *), Read, Grep
---

Follow the ReAct loop to debug the pipeline:

For each iteration:
1. **Thought**: Which part of the pipeline do I suspect? What BQ query would give me evidence?
2. **Action**: Execute the query or read the relevant file
3. **Observation**: What do the data tell me about the root cause?

Continue until identifying the failure point with concrete evidence.
```

### 6.3 Tree of Thoughts for Plugin Architecture Decisions

When a plugin needs to make complex decisions about which approach to follow:

```yaml
---
name: migration-planner
description: Plan complex database migrations
context: fork
effort: high
---

To plan the migration of $ARGUMENTS:

1. **Generate 3 strategies** for migration:
   - Incremental migration (zero downtime)
   - Big-bang migration (planned downtime)
   - Dual-write migration (temporary parallel)

2. **Evaluate each strategy**:
   - Data loss risk (1-5)
   - Implementation complexity (1-5)
   - Estimated downtime
   - Rollback capability

3. **Discard** strategies with risk > 3
4. **Deep dive** into remaining ones with detailed plan
5. **Recommend** with justification based on trade-offs
```

### 6.4 Least-to-Most for Decomposition Skills in Plugins

For plugins that decompose large tasks into progressively more complex subtasks:

```yaml
---
name: codebase-modernization
description: Incremental modernization of legacy codebase
---

Modernize $ARGUMENTS using progressive decomposition:

1. **Identify the simplest change**: What is the smallest improvement that adds value?
   (E.g.: update a dependency, remove a deprecation warning)
2. **Implement and validate**
3. **Identify the next change**: Based on what was done, what comes next?
4. **Repeat** until the modernization scope is complete
5. **Document** each change with motivation and impact
```

### 6.5 Self-Consistency for Cross-Plugin Validation

To ensure consistency across skills within the same plugin:

```yaml
---
name: validate-plugin-consistency
description: Validates consistency across all plugin skills
context: fork
agent: Explore
---

For each skill in the plugin:
1. **Read** the complete SKILL.md
2. **Extract** declared conventions and patterns

Then:
3. **Compare** patterns across skills (terminology, format, style)
4. **Identify** inconsistencies
5. **Classify**:
   - Present in 2+ skills: ESTABLISHED PATTERN
   - Present in only 1: POSSIBLE INCONSISTENCY
6. **Recommend** alignment for identified inconsistencies
```

### 6.6 Reflexion for Iterative Plugin Improvement

For plugin skills that improve through iteration:

```yaml
---
name: plugin-quality-check
description: Plugin quality check with improvement cycle
context: fork
---

For each plugin component:
1. **Evaluate**: Quality, completeness, consistency
2. **Critique**: What is missing? What is redundant?
3. **Reflect**: How can I improve with minimum effort, maximum impact?
4. **Improve**: Apply the identified improvements
5. **Re-evaluate**: Has the score improved? If < 8/10, repeat.
```

---

## 7. Correlations with Main Documents

### 7.1 With extend-claude-with-skills.md

The research document complements the official documentation with:

| Aspect | extend-claude-with-skills | research-skills-format |
|--------|---------------------------|----------------------|
| SKILL.md format | Usage documentation | Detailed technical specification |
| Frontmatter | Fields and examples | Strict validation rules |
| Distribution | Mention of plugins and managed | Complete detailing of plugins and marketplaces |
| Cross-platform | Mention of Agent Skills standard | Detailed comparison Claude Code vs VS Code vs Codex |
| Installation | Not detailed | `/plugin install`, `claude plugin install`, scopes |

### 7.2 With skill-authoring-best-practices.md

The research provides the "what" (formats and structures) while best practices provide the "how" (quality and effectiveness):

- **Research**: Directory structure, frontmatter fields, validation rules
- **Best practices**: How to write effective descriptions, progressive disclosure, workflows
- **Complementarity**: Research for correct technical implementation, best practices for content effectiveness

### 7.3 With research-context-engineering-comprehensive.md

| Optimization Concept | Implementation in Skills Ecosystem |
|----------------------|----------------------------------------|
| Context rot | 3-level progressive disclosure prevents overload |
| Attention budget | Description budget (2% context window) manages budget |
| Just-in-time docs | Skills load on demand; plugins use `${CLAUDE_PLUGIN_DATA}` for persistence |
| Context isolation | `context: fork` + `agent` type = subagent with isolated context |
| Configuration hierarchy | Enterprise > Personal > Project > Plugin |
| Hooks as enforcement | Plugin bundling of hooks + skills ensures deterministic enforcement |

### 7.4 With prompt-engineering-guide.md

| Prompting Technique | Ecosystem Application |
|---------------------|--------------------------|
| Role prompting | Agent definitions in plugins (agents/*.md) |
| Few-shot | Examples in skill supporting files |
| CoT | Multi-step workflows in SKILL.md |
| ReAct | Skills with `allowed-tools` and iterative loop |
| Structured outputs | Communication between skills and subagents via JSON |
| Prompt chaining | Plugins that orchestrate multiple skills in sequence |
| RAG patterns | Skills with dynamic injection (`` !`command` ``) as real-time RAG |

---

## 8. Strengths and Limitations

### 8.1 Strengths

1. **Complete ecosystem documented**: The document maps all extensibility layers (skills -> plugins -> marketplaces) with structures and schemas
2. **Cross-platform awareness**: Documents compatibility and differences between Claude Code, VS Code/Copilot, and OpenAI Codex
3. **Explicit validation rules**: Detailed name validation rules not obvious in official documentation
4. **Real examples**: References to real community repositories (davepoon/buildwithclaude, jeremylongshore/claude-code-plugins-plus-skills, etc.)
5. **Misconception correction**: Clarifies that `npx skills add` does not exist, that there is no `skills.json`, and that the open standard is minimal
6. **Multiple source types**: Documents all ways to reference plugins (relative, GitHub, Git URL, Git subdir, npm)
7. **Strict mode explained**: Clarifies marketplace strict mode behavior and its implications

### 8.2 Limitations

1. **Point in time**: March 2026 research — the plugin ecosystem is evolving rapidly and parts may become outdated
2. **No performance benchmarks**: No data on performance impact of plugins vs standalone skills
3. **No migration guide**: No instructions for migrating from commands/ to skills/ or from standalone skills to plugins
4. **Private marketplace gap**: Marketplace documentation focuses on public repositories; internal corporate marketplaces have less coverage
5. **No security analysis**: Does not discuss security implications of installing third-party plugins (script execution, tool access)
6. **Community vs official**: Some listed repositories are community-maintained and may not follow best practices
7. **Limited validation**: The `/plugin validate` command is mentioned but not detailed in terms of what exactly it validates

---

## 9. Practical Recommendations

### 9.1 For Skill Authors

1. **Decide portability first**: If the skill should work in VS Code/Copilot, use ONLY open standard fields. If it is exclusive to Claude Code, use extensions.

2. **Follow name validation rules rigorously**:
   - Only lowercase, numbers, and hyphens
   - No consecutive `--`
   - Cannot start/end with `-`
   - No "anthropic" or "claude"
   - Name must = directory name

3. **Use `${CLAUDE_SKILL_DIR}` instead of hardcoded paths**: Ensures portability across installations and platforms.

4. **Keep descriptions under 200 characters when possible**: Every character consumes context budget. 1024-char descriptions are the maximum, not the ideal.

### 9.2 For Plugin Authors

1. **Create plugin.json even though it's optional**: Auto-discovery works, but an explicit manifest avoids ambiguity and allows additional metadata.

2. **Use `${CLAUDE_PLUGIN_ROOT}` for script paths**: Ensures scripts work regardless of installation directory.

3. **Use `${CLAUDE_PLUGIN_DATA}` for persistent data**: Do not store data in the plugin directory — it changes on updates.

4. **Define clear installation scopes in documentation**: Indicate whether the plugin should be installed at user, project, or local scope.

5. **Minimal plugin template:**

```
my-plugin/
  .claude-plugin/
    plugin.json
  skills/
    main-skill/
      SKILL.md
  README.md
  LICENSE
```

```json
// .claude-plugin/plugin.json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "Concise plugin description",
  "author": { "name": "Author" },
  "license": "MIT"
}
```

### 9.3 For Marketplace Authors

1. **Use consistent categories and tags**: Facilitates discovery as the marketplace grows.

2. **Prefer strict mode (default)**: Let each plugin define its own manifest. Use `strict: false` only for plugins without a manifest.

3. **Minimal marketplace template:**

```json
{
  "name": "my-marketplace",
  "owner": { "name": "Organization" },
  "plugins": [
    {
      "name": "plugin-1",
      "description": "What it does",
      "source": "./plugins/plugin-1"
    }
  ]
}
```

### 9.4 For Distribution Strategy

1. **Personal skill -> Project skill -> Plugin -> Marketplace**: Evolve distribution as the audience grows.

2. **Start with standalone skills**: Create and test individual skills before packaging into a plugin.

3. **Use plugin namespacing to avoid conflicts**: The `plugin-name:skill-name` namespace prevents conflicts with project/personal skills.

4. **Monitor community repositories**: The repos listed in the document (davepoon/buildwithclaude, numman-ali/n-skills, etc.) are sources of inspiration and emerging patterns.

### 9.5 Cross-Platform Portable SKILL.md Template

```yaml
---
name: universal-skill
description: >
  Portable skill that works in Claude Code, VS Code/Copilot, and OpenAI Codex.
  Uses only Agent Skills open standard fields.
---

# Universal Skill

## Instructions
[Instructions that do not depend on platform-specific features]

## Resources
- For details: [reference.md](reference.md)
- For examples: [examples.md](examples.md)
```

### 9.6 Advanced SKILL.md Template (Claude Code)

```yaml
---
name: advanced-skill
description: >
  Advanced skill using Claude Code exclusive features.
  Runs in an isolated subagent with restricted tools.
context: fork
agent: Explore
disable-model-invocation: true
allowed-tools: Read, Grep, Glob
effort: high
argument-hint: "[target-path] [options]"
---

# Advanced Skill

## Dynamic Context
- Current status: !`git status --short`
- Branch: !`git branch --show-current`

## Instructions
Analyze $ARGUMENTS[0] with options $ARGUMENTS[1]:

1. [Step 1 with tool]
2. [Step 2 with validation]
3. [Step 3 with structured output]
```
