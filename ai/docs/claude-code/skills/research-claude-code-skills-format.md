# Research: Claude Code Skills & Plugin Marketplace Format

> **Date**: 2026-03-22
> **Sources**: Anthropic official docs, Agent Skills open standard spec, GitHub repos

**Related documentation**: [Extend Claude with Skills](extend-claude-with-skills.md) (Claude Code tutorial) | [Skill Authoring Best Practices](../../shared/skill-authoring-best-practices.md) (universal guide) | [Agent Skills Standard](../../shared/skills-standard/README.md) (open standard spec)

---

## Summary

Claude Code has a **three-layer extensibility system**: standalone Skills, Plugins (bundling skills + agents + hooks + MCP/LSP servers), and Plugin Marketplaces (catalogs of plugins). Skills follow the **[Agent Skills](https://agentskills.io) open standard** (originally by Anthropic, now open), which is a cross-agent format also supported by VS Code/GitHub Copilot and OpenAI Codex. There is **no `npx skills add` command** — plugin installation is done via Claude Code's built-in `/plugin install` command or `claude plugin install` CLI. Plugins are distributed through **marketplace repositories** (GitHub repos with a `.claude-plugin/marketplace.json` catalog file).

---

## 1. The `/plugin install` Command (NOT `npx skills add`)

**Source**: [Anthropic Docs — Discover and install plugins](https://docs.anthropic.com/en/docs/claude-code/discover-plugins)

There is **no `npx skills add` command**. The actual installation mechanism is:

### Interactive (inside Claude Code TUI)
```bash
# Add a marketplace (one-time)
/plugin marketplace add owner/repo

# Install a plugin from a marketplace
/plugin install plugin-name@marketplace-name

# Example: Install from the official Anthropic marketplace
/plugin install github@claude-plugins-official
```

### CLI (non-interactive)
```bash
# Install to user scope (default)
claude plugin install formatter@my-marketplace

# Install to project scope (shared with team via .claude/settings.json)
claude plugin install formatter@my-marketplace --scope project

# Install to local scope (gitignored, only for you in this project)
claude plugin install formatter@my-marketplace --scope local
```

### Marketplace Sources
Marketplaces can be added from:
- **GitHub repos**: `/plugin marketplace add owner/repo`
- **Git URLs**: `/plugin marketplace add https://gitlab.com/company/plugins.git`
- **Local paths**: `/plugin marketplace add ./my-marketplace`
- **Remote URLs**: `/plugin marketplace add https://example.com/marketplace.json`
- **Branch/tag pinning**: `/plugin marketplace add https://gitlab.com/company/plugins.git#v1.0.0`

### Official Marketplace
The official Anthropic marketplace (`claude-plugins-official`) is **auto-available**. Browse at [claude.com/plugins](https://claude.com/plugins).

### Plugin Source Types (in marketplace.json)
| Source Type | Example |
|-------------|---------|
| Relative path | `"./plugins/my-plugin"` |
| GitHub repo | `{"source": "github", "repo": "owner/repo"}` |
| Git URL | `{"source": "url", "url": "https://gitlab.com/..."}` |
| Git subdirectory | `{"source": "git-subdir", "url": "...", "path": "tools/plugin"}` |
| npm package | `{"source": "npm", "package": "@acme/claude-plugin"}` |

---

## 2. Agent Skills Open Standard (SKILL.md Format)

**Source**: [Agent Skills Specification](https://agentskills.io) · [GitHub: agentskills/agentskills](https://github.com/agentskills/agentskills)

### Minimum Viable Skill
A skill is a **directory containing a `SKILL.md` file**:

```
my-skill/
└── SKILL.md
```

### SKILL.md Format
YAML frontmatter + Markdown body:

```markdown
---
name: my-skill
description: What this skill does and when to use it.
---

Step-by-step instructions for the agent...
```

### Frontmatter Fields (Agent Skills Open Standard)

| Field | Required | Constraints |
|-------|----------|-------------|
| `name` | Yes* | Max 64 chars. Lowercase letters, numbers, hyphens only. Must match parent directory name. |
| `description` | Yes* | Max 1024 chars. What it does + when to use it. |
| `license` | No | License name or path to LICENSE file |
| `compatibility` | No | Max 500 chars. Environment requirements. |
| `metadata` | No | Arbitrary key-value map (e.g., author, version) |
| `allowed-tools` | No | Space-delimited list of pre-approved tools (experimental) |

> *In Claude Code, `name` and `description` are technically optional but recommended. If `name` is omitted, the directory name is used. If `description` is omitted, the first paragraph of content is used.

### Name Validation Rules
- 1-64 characters
- Only lowercase `a-z`, numbers, and hyphens
- Must NOT start or end with `-`
- Must NOT contain consecutive `--`
- Must match the parent directory name

### Claude Code Extensions to the Standard

Claude Code adds several proprietary frontmatter fields beyond the open standard:

| Field | Description |
|-------|-------------|
| `argument-hint` | Hint shown in autocomplete (e.g., `[issue-number]`) |
| `disable-model-invocation` | `true` = only user can invoke (not auto-triggered by Claude) |
| `user-invocable` | `false` = hidden from `/` menu (background knowledge only) |
| `allowed-tools` | Tools Claude can use without permission when skill is active |
| `model` | Model override when skill is active |
| `effort` | Effort level: `low`, `medium`, `high`, `max` |
| `context` | Set to `fork` to run in an isolated subagent |
| `agent` | Subagent type when `context: fork` (e.g., `Explore`, `Plan`, `general-purpose`) |
| `hooks` | Hooks scoped to this skill's lifecycle |

### String Substitutions in Skill Content

| Variable | Description |
|----------|-------------|
| `$ARGUMENTS` | All arguments passed when invoking |
| `$ARGUMENTS[N]` / `$N` | Specific argument by 0-based index |
| `${CLAUDE_SESSION_ID}` | Current session ID |
| `${CLAUDE_SKILL_DIR}` | Directory containing the SKILL.md file |

### Dynamic Context Injection
The `` !`<command>` `` syntax runs shell commands **before** skill content is sent to Claude:

```markdown
---
name: pr-summary
description: Summarize the current PR
context: fork
agent: Explore
---

## PR Context
- Diff: !`gh pr diff`
- Comments: !`gh pr view --comments`
```

---

## 3. Full Skill Directory Structure

**Source**: [Anthropic Docs — Skills](https://docs.anthropic.com/en/docs/claude-code/skills) · [Agent Skills Spec](https://github.com/agentskills/agentskills/blob/main/docs/specification.mdx)

### Standard Layout
```
my-skill/
├── SKILL.md           # Required: metadata + instructions (entrypoint)
├── reference.md       # Optional: detailed API docs
├── examples.md        # Optional: usage examples
├── scripts/           # Optional: executable code (Python, Bash, JS)
│   ├── helper.py
│   └── validate.sh
├── references/        # Optional: additional documentation
│   └── REFERENCE.md
└── assets/            # Optional: templates, images, schemas
    └── template.md
```

### Progressive Disclosure Model
1. **Metadata** (~100 tokens): `name` + `description` — loaded at startup for ALL skills
2. **Instructions** (<5000 tokens recommended): Full SKILL.md body — loaded when skill activates
3. **Resources** (as needed): Scripts, references, assets — loaded only when required

### Guidelines
- Keep `SKILL.md` under **500 lines**
- Move detailed reference material to separate files
- Reference supporting files from SKILL.md:
  ```markdown
  ## Additional resources
  - For complete API details, see [reference.md](reference.md)
  - For usage examples, see [examples.md](examples.md)
  ```

---

## 4. Where Skills Live in Claude Code

**Source**: [Anthropic Docs — Skills](https://docs.anthropic.com/en/docs/claude-code/skills)

| Location | Path | Applies to |
|----------|------|------------|
| Enterprise | Managed settings | All users in org |
| Personal | `~/.claude/skills/<skill-name>/SKILL.md` | All your projects |
| Project | `.claude/skills/<skill-name>/SKILL.md` | This project only |
| Plugin | `<plugin>/skills/<skill-name>/SKILL.md` | Where plugin is enabled |
| VS Code / Copilot | `.agents/skills/<skill-name>/SKILL.md` | VS Code Agent mode |

**Priority**: Enterprise > Personal > Project. Plugin skills use `plugin-name:skill-name` namespace (no conflicts).

**Monorepo support**: Claude auto-discovers `.claude/skills/` in subdirectories when editing files there.

---

## 5. Plugin Structure (Wrapping Skills for Distribution)

**Source**: [Anthropic Docs — Plugins](https://docs.anthropic.com/en/docs/claude-code/plugins) · [Plugins Reference](https://docs.anthropic.com/en/docs/claude-code/plugins-reference)

### Standard Plugin Layout
```
my-plugin/
├── .claude-plugin/           # Metadata directory (optional)
│   └── plugin.json           # Plugin manifest
├── commands/                 # Markdown command files (legacy)
│   ├── deploy.md
│   └── status.md
├── skills/                   # Agent Skills (preferred for new skills)
│   ├── code-reviewer/
│   │   └── SKILL.md
│   └── pdf-processor/
│       ├── SKILL.md
│       └── scripts/
├── agents/                   # Subagent definitions
│   ├── security-reviewer.md
│   └── compliance-checker.md
├── hooks/                    # Hook configurations
│   └── hooks.json
├── scripts/                  # Hook and utility scripts
│   ├── format-code.py
│   └── deploy.js
├── settings.json             # Default settings (currently only `agent` key)
├── .mcp.json                 # MCP server definitions
├── .lsp.json                 # LSP server configurations
├── README.md                 # Documentation
├── LICENSE                   # License
└── CHANGELOG.md              # Version history
```

### plugin.json Schema

```json
{
  "name": "my-plugin",
  "version": "1.2.0",
  "description": "Brief plugin description",
  "author": {
    "name": "Author Name",
    "email": "dev@example.com",
    "url": "https://github.com/author"
  },
  "homepage": "https://docs.example.com/plugin",
  "repository": "https://github.com/author/plugin",
  "license": "MIT",
  "keywords": ["keyword1", "keyword2"],
  "commands": ["./custom/commands/special.md"],
  "agents": "./custom/agents/",
  "skills": "./custom/skills/",
  "hooks": "./config/hooks.json",
  "mcpServers": "./mcp-config.json",
  "outputStyles": "./styles/",
  "lspServers": "./.lsp.json"
}
```

**Only `name` is required** if you include a manifest. The manifest itself is optional — Claude Code auto-discovers components in default locations.

### Key Environment Variables
- `${CLAUDE_PLUGIN_ROOT}` — Absolute path to plugin's installation directory (changes on update)
- `${CLAUDE_PLUGIN_DATA}` — Persistent data directory surviving updates (`~/.claude/plugins/data/{id}/`)

---

## 6. Marketplace Repository Format

**Source**: [Anthropic Docs — Plugin Marketplaces](https://docs.anthropic.com/en/docs/claude-code/plugin-marketplaces)

### Marketplace Repository Structure
```
my-marketplace/
├── .claude-plugin/
│   └── marketplace.json      # The catalog file (required)
├── plugins/
│   ├── plugin-one/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── skills/
│   │   │   └── my-skill/
│   │   │       └── SKILL.md
│   │   └── commands/
│   │       └── hello.md
│   └── plugin-two/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       └── skills/
│           └── another-skill/
│               └── SKILL.md
├── README.md
└── LICENSE
```

### marketplace.json Schema

```json
{
  "name": "my-marketplace-name",
  "owner": {
    "name": "Your Org Name",
    "email": "team@org.com"
  },
  "metadata": {
    "description": "A collection of Claude Code plugins",
    "version": "1.0.0",
    "pluginRoot": "./plugins"
  },
  "plugins": [
    {
      "name": "plugin-one",
      "description": "What this plugin does",
      "version": "1.0.0",
      "author": { "name": "Author" },
      "source": "./plugins/plugin-one",
      "category": "developer-tools",
      "tags": ["tag1", "tag2"],
      "keywords": ["keyword1", "keyword2"]
    },
    {
      "name": "remote-plugin",
      "description": "A plugin hosted elsewhere",
      "source": {
        "source": "github",
        "repo": "owner/plugin-repo",
        "ref": "v2.0.0"
      }
    },
    {
      "name": "npm-plugin",
      "description": "An npm-distributed plugin",
      "source": {
        "source": "npm",
        "package": "@acme/claude-plugin",
        "version": "^2.0.0"
      }
    }
  ]
}
```

### Required Marketplace Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Marketplace identifier (kebab-case, no spaces) |
| `owner` | object | `{ name: string, email?: string }` |
| `plugins` | array | List of plugin entries |

### Required Plugin Entry Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Plugin identifier (kebab-case) |
| `source` | string or object | Where to fetch the plugin from |

### Optional Plugin Entry Fields
`description`, `version`, `author`, `homepage`, `repository`, `license`, `keywords`, `category`, `tags`, `strict`, `commands`, `agents`, `hooks`, `mcpServers`, `skills`

### Strict Mode
| Value | Behavior |
|-------|----------|
| `true` (default) | `plugin.json` is authority; marketplace entry supplements |
| `false` | Marketplace entry is the entire definition |

---

## 7. Real-World Example: Complete Minimal Plugin Marketplace

From [ivan-magda/claude-code-plugin-template](https://github.com/ivan-magda/claude-code-plugin-template):

### `.claude-plugin/marketplace.json`
```json
{
  "name": "my-team-plugin-marketplace",
  "owner": {
    "name": "Your Organization",
    "email": "team@your-org.com"
  },
  "metadata": {
    "description": "A curated collection of Claude Code plugins for our team",
    "version": "1.3.0"
  },
  "plugins": [
    {
      "name": "hello-world",
      "description": "A simple example plugin demonstrating basic Claude Code plugin functionality",
      "version": "1.0.0",
      "author": { "name": "Your Team" },
      "source": "./plugins/hello-world",
      "category": "examples",
      "tags": ["example", "tutorial", "getting-started"],
      "keywords": ["example", "tutorial", "getting-started"]
    }
  ]
}
```

### `plugins/hello-world/.claude-plugin/plugin.json`
```json
{
  "name": "hello-world",
  "version": "1.0.0",
  "description": "A simple example plugin that demonstrates basic Claude Code plugin functionality",
  "author": {
    "name": "Your Team",
    "email": "team@your-org.com",
    "url": "https://github.com/your-org"
  },
  "homepage": "https://github.com/your-org/your-marketplace-name",
  "repository": "https://github.com/your-org/your-marketplace-name",
  "license": "MIT",
  "keywords": ["example", "tutorial", "hello-world"]
}
```

### `plugins/hello-world/commands/hello.md`
```markdown
---
description: Greet the user with a friendly, personalized message
argument-hint: [name]
---

# Hello Command

Greet the user warmly and enthusiastically.

## Instructions

1. If the user provided a name in `$ARGUMENTS`, greet them personally
2. If no name was provided, use a friendly generic greeting
3. After the greeting, explain this is an example plugin
```

---

## 8. Skills vs Commands (Legacy) vs Plugins — Comparison

| Aspect | Standalone Skill | Command (Legacy) | Plugin |
|--------|-----------------|-------------------|--------|
| File format | `skills/<name>/SKILL.md` directory | `commands/<name>.md` file | Directory with `.claude-plugin/plugin.json` |
| Invocation | `/skill-name` | `/command-name` | `/plugin-name:skill-name` |
| Supports subfiles | ✅ (reference.md, scripts/, etc.) | ❌ (single file) | ✅ |
| Auto-invoked by Claude | ✅ (unless disabled) | ✅ | ✅ |
| Distributable | Manually copy | Manually copy | Via marketplace |
| Namespace | Global | Global | `plugin-name:` prefixed |

---

## 9. Key Community Marketplace Repos

| Repository | Stars | Description |
|------------|-------|-------------|
| [davepoon/buildwithclaude](https://github.com/davepoon/buildwithclaude) | 2624 | Hub for Claude Skills, Agents, Commands, Hooks, Plugins |
| [jeremylongshore/claude-code-plugins-plus-skills](https://github.com/jeremylongshore/claude-code-plugins-plus-skills) | 1686 | 340 plugins + 1367 agent skills with CCPI package manager |
| [numman-ali/n-skills](https://github.com/numman-ali/n-skills) | 940 | Curated marketplace for Claude Code, Codex, and openskills |
| [trailofbits/skills-curated](https://github.com/trailofbits/skills-curated) | 285 | Community-vetted plugin marketplace |
| [ivan-magda/claude-code-plugin-template](https://github.com/ivan-magda/claude-code-plugin-template) | 44 | GitHub template for creating plugin marketplaces |
| [anthropics/claude-code](https://github.com/anthropics/claude-code) (plugins dir) | — | Official demo plugins marketplace |

---

## 10. Official Plugin Submission

To submit to the official Anthropic marketplace:
- **Claude.ai**: [claude.ai/settings/plugins/submit](https://claude.ai/settings/plugins/submit)
- **Console**: [platform.claude.com/plugins/submit](https://platform.claude.com/plugins/submit)

---

## 11. Validation

### Agent Skills Spec Validation
```bash
# Using the reference implementation (Python)
pip install skills-ref  # from agentskills/agentskills repo
skills-ref validate ./my-skill
```

### Claude Code Plugin Validation
```bash
# Inside Claude Code
/plugin validate

# Or via CLI
claude --debug  # Shows plugin loading details
```

---

## Gaps & Notes

1. **No `npx skills add` exists**: This may refer to community tools like the CCPI package manager from `jeremylongshore/claude-code-plugins-plus-skills`, but is NOT an official Anthropic tool.
2. **No `skills.json` manifest**: Skills don't have their own manifest file. The manifest is `SKILL.md` (frontmatter) for individual skills and `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` for plugins/marketplaces.
3. **The Agent Skills open standard is minimal**: Only `SKILL.md` with `name` + `description` frontmatter is required. Claude Code extends it with many proprietary fields.
4. **Cross-agent compatibility**: The same `SKILL.md` format works in Claude Code, VS Code/GitHub Copilot (in `.agents/skills/`), and OpenAI Codex. Claude Code looks in `.claude/skills/`, VS Code looks in `.agents/skills/`.
