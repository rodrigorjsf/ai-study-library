# Analysis: Creating Plugins for Claude Code

> **Status**: Current
> **Source document**: [Create Plugins](https://docs.anthropic.com/en/docs/claude-code/plugins)
> **Analysis date**: 2026-03
> **Scope**: Analysis of Claude Code plugin creation, structure, and distribution mechanisms

---

## 1. Executive Summary

The "Create Plugins" document is Anthropic's official guide for creating custom Claude Code extensions. Plugins are distributable packages that bundle skills, agents, hooks, MCP servers, LSP servers, and settings into a single unit with namespace, versioning, and metadata. The fundamental distinction from standalone configuration (`.claude/`) is distributability: plugins can be shared via marketplaces, installed with `/plugin install`, and versioned with semantic versioning.

The plugin architecture is based on a manifest (`plugin.json` inside `.claude-plugin/`), with components organized in directories at the plugin root: `commands/`, `agents/`, `skills/`, `hooks/`, `.mcp.json`, `.lsp.json`, and `settings.json`. Namespacing is mandatory -- plugin skills are accessed as `/plugin-name:skill-name`, preventing conflicts between plugins. The `settings.json` field at the plugin root can activate a custom agent as the main thread, fundamentally changing how Claude Code behaves when the plugin is enabled.

Anthropic recommends starting with standalone configuration in `.claude/` for rapid iteration and converting to a plugin when ready to share. Local testing via `--plugin-dir` allows development without installation, and `/reload-plugins` updates components without restarting. Converting existing configuration to a plugin is a structured process of migrating files from `.claude/` to the plugin structure.

---

## 2. Key Concepts and Mechanisms

### 2.1 Standalone vs Plugin

| Aspect | Standalone (`.claude/`) | Plugin |
|--------|------------------------|--------|
| Skill names | `/hello` | `/plugin-name:hello` |
| Best for | Personal, project-specific, experimentation | Sharing, distribution, reuse |
| Versioning | Manual | Semantic versioning in manifest |
| Installation | Copy files | `/plugin install` |
| Name conflicts | Possible with multiple projects | Prevented by namespacing |

### 2.2 Plugin Structure

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # Manifest (ONLY plugin.json goes here)
├── commands/                  # Skills as Markdown (user-invocable)
├── agents/                    # Custom agent definitions
├── skills/                    # Agent Skills with SKILL.md
│   └── code-review/
│       └── SKILL.md
├── hooks/
│   └── hooks.json             # Event handlers
├── .mcp.json                  # MCP server configurations
├── .lsp.json                  # LSP server configurations
└── settings.json              # Plugin default settings
```

**CRITICAL WARNING**: Do NOT place `commands/`, `agents/`, `skills/`, or `hooks/` inside `.claude-plugin/`. Only `plugin.json` goes inside `.claude-plugin/`. All other directories go at the plugin root.

### 2.3 Plugin Manifest

```json
{
  "name": "my-plugin",
  "description": "A greeting plugin to learn the basics",
  "version": "1.0.0",
  "author": {
    "name": "Your Name"
  }
}
```

| Field | Purpose |
|-------|---------|
| `name` | Unique identifier and skill namespace |
| `description` | Displayed in the plugin manager |
| `version` | Semantic versioning for releases |
| `author` | Attribution (optional) |

Additional fields: `homepage`, `repository`, `license`.

### 2.4 Skills in Plugins

```yaml
---
name: code-review
description: Reviews code for best practices and potential issues.
---

When reviewing code, check for:
1. Code organization and structure
2. Error handling
3. Security concerns
4. Test coverage
```

Skills in plugins have frontmatter with `name` and `description`, followed by instructions. Claude invokes them automatically based on the description, or the user invokes them via `/plugin-name:skill-name`.

### 2.5 LSP Servers in Plugins

```json
{
  "go": {
    "command": "gopls",
    "args": ["serve"],
    "extensionToLanguage": {
      ".go": "go"
    }
  }
}
```

Provides real-time code intelligence. Users must have the language server binary installed.

### 2.6 Plugin Default Settings

```json
{
  "agent": "security-reviewer"
}
```

The `agent` field activates one of the plugin's custom agents as the main thread, applying its system prompt, tool restrictions, and model. Currently only the `agent` field is supported in plugin `settings.json`.

### 2.7 Dynamic Arguments

The `$ARGUMENTS` placeholder captures text after the skill name:

```markdown
---
description: Greet the user with a personalized message
---
# Hello Skill
Greet the user named "$ARGUMENTS" warmly.
```

Invocation: `/my-plugin:hello Alex`

### 2.8 Development and Testing

- **`--plugin-dir ./my-plugin`**: Loads plugin locally without installation
- **`/reload-plugins`**: Updates components without restarting the session
- **Multiple plugins**: `claude --plugin-dir ./plugin-one --plugin-dir ./plugin-two`
- **Override**: Local plugin with the same name as a marketplace plugin takes precedence (except managed)
- **Validation**: Verify structure, test each component individually

### 2.9 Migration from Standalone to Plugin

```bash
# 1. Create structure
mkdir -p my-plugin/.claude-plugin

# 2. Create manifest
echo '{"name":"my-plugin","description":"Migrated","version":"1.0.0"}' > my-plugin/.claude-plugin/plugin.json

# 3. Copy components
cp -r .claude/commands my-plugin/
cp -r .claude/agents my-plugin/
cp -r .claude/skills my-plugin/

# 4. Migrate hooks (from settings.json to hooks/hooks.json)
mkdir my-plugin/hooks
# Copy the "hooks" object from settings.json to hooks/hooks.json

# 5. Test
claude --plugin-dir ./my-plugin
```

---

## 3. Points of Attention

### 3.1 Common Structure Error

The most documented error: placing component directories inside `.claude-plugin/`. The documentation emphasizes this with an explicit warning:

> "Don't put `commands/`, `agents/`, `skills/`, or `hooks/` inside the `.claude-plugin/` directory."

### 3.2 Security Restrictions in Plugin Agents

Agents defined in plugins do NOT support:

- `hooks` (no lifecycle hooks)
- `mcpServers` (no MCP server definitions)
- `permissionMode` (no permission override)

These fields are silently ignored. To use them, copy the agent to `.claude/agents/` or `~/.claude/agents/`.

### 3.3 Mandatory Namespacing

Plugin skills are ALWAYS prefixed: `/plugin-name:skill-name`. It is not possible to have plugin skills with short names like `/deploy`. For short names, use standalone configuration.

### 3.4 Skill Context Cost

Skill descriptions consume ~2% of the context window. Plugins with many skills can accumulate significant cost. Monitor via `/context`.

### 3.5 Limited Settings

Currently only `agent` is supported in the plugin's `settings.json`. Unknown keys are silently ignored.

### 3.6 Managed Plugins CANNOT Be Overridden

Marketplace plugins force-enabled by managed settings CANNOT be overridden by the local `--plugin-dir`.

### 3.7 Binary Dependency for LSP

Plugins with `.lsp.json` require the user to have the language server binary installed. There is no automatic installation mechanism.

---

## 4. Use Cases and Scope

### 4.1 When to Use Plugins

| Scenario | Recommendation |
|----------|---------------|
| Share skills/agents with the team | Plugin (versionable, installable) |
| Distribute to the community | Plugin (marketplace) |
| Same skills across multiple projects | Plugin (install once, use everywhere) |
| Personal rapid iteration | Standalone first, plugin later |
| Skills with short names | Standalone (no namespace) |
| Experimenting with hooks | Standalone (no security restrictions) |

### 4.2 Plugin Types by Functionality

| Type | Main Components | Example |
|------|----------------|---------|
| **Code quality** | agents (reviewer), hooks (PostToolUse linter), skills | Review plugin with code-reviewer agent |
| **Language support** | LSP server, agents (language-reviewer), rules | TypeScript plugin with gopls LSP |
| **Workflow automation** | skills, hooks, agents | Deploy plugin with skill + validation |
| **Domain knowledge** | skills (reference material), agents | API conventions plugin |
| **Testing** | agents (tester), hooks (PreToolUse validation) | TDD plugin with test-runner agent |

### 4.3 Recommended Development Flow

```
1. Prototype in .claude/ (standalone)
   -> Iterate rapidly, test, refine

2. Convert to plugin when stable
   -> Create manifest, copy components, migrate hooks

3. Test locally with --plugin-dir
   -> Verify each component, /reload-plugins

4. Version and document
   -> Semantic versioning, README.md

5. Distribute
   -> Marketplace or team git repository
```

---

## 5. Applicability to Agent Infrastructure

### 5.1 Skills

- **Skills as a central component**: Plugins allow packaging and distributing reusable skills with namespace
- **Agent Skills vs Commands**: `skills/` contains SKILL.md with frontmatter (model-invoked); `commands/` contains plain Markdown (user-invoked)
- **$ARGUMENTS for parameterization**: Placeholder captures dynamic user input
- **Progressive disclosure maintained**: Descriptions at startup, content loaded on demand, even in plugins
- **Skill frontmatter in plugins**: Supports `name`, `description`, `argument-hint`, `disable-model-invocation`, `context`, `agent`, `hooks`, `allowed-tools`, `model`, `effort`
- **Dynamic injection**: `` !`command` `` works normally in plugin skills

### 5.2 Hooks

- **`hooks/hooks.json` in the plugin**: Format identical to `settings.json`, with an array of hooks per event
- **All events supported**: `PreToolUse`, `PostToolUse`, `Stop`, etc.
- **JSON on stdin**: Hook commands receive input as JSON; `jq` for extraction
- **Restriction in plugin agents**: Agents defined in plugins CANNOT have hooks in their frontmatter
- **Hooks at plugin root**: `hooks/hooks.json` works normally (the restriction applies only to agent frontmatter)

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{ "type": "command", "command": "jq -r '.tool_input.file_path' | xargs npm run lint:fix" }]
      }
    ]
  }
}
```

### 5.3 Subagents

- **Agents in plugins**: Defined in `agents/` at the plugin root, appear as `<plugin-name>:<agent-name>`
- **Invocation**: `claude --agent <plugin-name>:<agent-name>` or @-mention
- **Security restrictions**: No `hooks`, `mcpServers`, `permissionMode` in plugin agents
- **Supported fields**: `name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, `isolation`
- **Plugin settings.json**: `agent` field activates an agent as main thread -- changes default Claude Code behavior
- **Precedence**: Plugin `settings.json` takes priority over `settings` in `plugin.json`

### 5.4 Rules

- **Rules in plugins**: There is no explicitly documented `rules/` directory in the plugin structure
- **Plugin CLAUDE.md**: Not directly documented, but plugins load project context normally
- **Path-scoped rules**: Should be maintained in the project (`.claude/rules/`), not in the plugin
- **Settings as rules**: Plugin `settings.json` can influence behavior via the `agent` field
- **Alternative**: Plugin skills serve as a means of injecting contextual instructions

### 5.5 Memory

- **Plugin agents with memory**: `memory` field supported (user, project, local)
- **Shared memory**: Plugin agents can use `memory: project` to build versionable knowledge
- **Auto memory**: Loaded normally in sessions with plugins enabled
- **Project CLAUDE.md**: Loaded alongside the plugin, providing persistent context
- **Cross-plugin**: There is no shared memory mechanism between plugins

---

## 6. Applicability of the Prompt Engineering Guide

### 6.1 CoT for Subagent Reasoning Chains

Plugin skills can include CoT instructions in SKILL.md. Plugin agents can have CoT in the system prompt (markdown body). CoT is particularly valuable in complex skills that require multi-step reasoning:

```yaml
---
name: architecture-review
description: Review architecture decisions for the project
context: fork
agent: general-purpose
---

## Process
Think step by step:
1. What is the current architecture?
2. What are the proposed changes?
3. What are the trade-offs?
4. What are the risks?
5. Recommendation with justification
```

### 6.2 ReAct for Subagents with Tool Access

Plugin agents with tool access operate in the ReAct loop. The system prompt should encourage the Thought -> Action -> Observation cycle. Skills with `context: fork` and `agent: general-purpose` inherit full tools for ReAct.

### 6.3 Tree of Thoughts for Exploration Subagents

Plugins can include skills that spawn multiple subagents in parallel (via `context: fork` with `agent: Explore`), each exploring a different aspect. A code review plugin could have separate skills for security, performance, and testing, invocable in parallel.

### 6.4 Self-Consistency for Validation Across Multiple Subagents

Review plugins can implement Self-Consistency by running the same review agent multiple times and comparing results. The `PostToolUse` hook can trigger cross-validation.

### 6.5 Reflexion for Iterative Subagent Improvement

Plugin agents with `memory: project` implement cross-session Reflexion:

- Agent learns patterns in each review
- Next invocation consults memory
- Feedback incorporated incrementally

The combination of agent + memory + hooks creates a continuous improvement loop.

### 6.6 Least-to-Most for Task Decomposition Across Subagents

Plugins can define multi-step workflows with chained skills:

1. Exploration skill (Explore agent)
2. Planning skill (Plan agent)
3. Implementation skill (general-purpose agent)
4. Validation skill (review agent)

Each skill can be invoked sequentially or automatically by Claude based on the description.

---

## 7. Correlations with Key Documents

### With "Creating Custom Subagents"

Plugins are the distribution mechanism for subagents. Agents in `.claude/agents/` can be packaged into plugins for sharing. The security restriction (no hooks/mcpServers/permissionMode in plugin agents) is documented in both. The plugin's `settings.json` with the `agent` field is a way to make a subagent the session default.

### With "Orchestrate Teams of Claude Code Sessions"

There is no directly documented integration between plugins and agent teams. Plugins are loaded normally by each teammate, and plugin skills can be invoked in a teams context. The main connection is that plugins can provide `TeammateIdle`/`TaskCompleted` hooks via `hooks/hooks.json`.

### With "How Claude Remembers a Project"

Plugins interact with the memory system in two ways:

1. Plugin agents can have the `memory` field (user/project/local)
2. Project CLAUDE.md is loaded alongside the plugin

The progressive disclosure philosophy is maintained: plugin skill descriptions at startup, full content on-demand.

### With "Research: Subagent Best Practices"

Section 16 of the research (Plugin-Shipped Agents) documents:

- Directory structure for agents in plugins
- Supported fields vs security restrictions
- Naming convention `<plugin-name>:<agent-name>`

The research complements the plugin docs with community examples and anti-patterns applicable to plugins.

### With "Research: LLM Context Optimization"

Plugins implement progressive disclosure (skill descriptions at startup, content on-demand). The ~2% context cost per skill description accumulates with multiple plugins. The "hybrid pre-loaded + on-demand" strategy is maintained in plugins. The "quality over quantity" principle applies to the number of skills/agents registered per plugin.

---

## 8. Strengths and Limitations

### Strengths

1. **Distributability**: Marketplaces, `/plugin install`, semantic versioning
2. **Namespacing**: Prevents conflicts between plugins
3. **Rich composition**: Skills + agents + hooks + MCP + LSP + settings in one package
4. **Local testing**: `--plugin-dir` + `/reload-plugins` for rapid development
5. **Easy migration**: Structured process from standalone to plugin
6. **Default settings**: `agent` field can transform Claude Code behavior
7. **Local override**: Local plugin takes precedence over marketplace (except managed)
8. **Multiple plugins**: `--plugin-dir` accepts multiple plugins simultaneously

### Limitations

1. **Security restrictions on agents**: No hooks, mcpServers, permissionMode
2. **Limited settings**: Only `agent` field supported in plugin settings.json
3. **Mandatory namespacing**: Skills always prefixed (cannot have `/deploy` via plugin)
4. **LSP binary dependency**: No automatic installation
5. **No native rules**: There is no `rules/` directory in the plugin structure
6. **Accumulated context cost**: Many plugins = many skill descriptions = budget consumed
7. **Immutable managed plugins**: Force-enabled by IT cannot be overridden locally
8. **No cross-plugin memory**: There is no memory sharing between plugins

---

## 9. Practical Recommendations

### 9.1 Minimal Plugin Template

```bash
mkdir -p my-plugin/.claude-plugin my-plugin/skills/main my-plugin/agents

# Manifest
cat > my-plugin/.claude-plugin/plugin.json << 'EOF'
{
  "name": "my-plugin",
  "description": "Description of what this plugin does",
  "version": "1.0.0",
  "author": { "name": "Your Name" }
}
EOF

# Main skill
cat > my-plugin/skills/main/SKILL.md << 'EOF'
---
name: main
description: Primary skill of the plugin. Use when [trigger].
---

Instructions for the skill...
EOF

# Main agent
cat > my-plugin/agents/reviewer.md << 'EOF'
---
name: reviewer
description: Review specialist. Use proactively after code changes.
tools: Read, Grep, Glob, Bash
model: sonnet
memory: project
---

You are a reviewer specializing in [domain]...
EOF
```

### 9.2 Code Quality Plugin Pattern

```
quality-plugin/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   ├── code-reviewer.md      # Review agent (read-only)
│   ├── security-reviewer.md   # Security specialist
│   └── performance-reviewer.md # Performance analyst
├── skills/
│   └── full-review/
│       └── SKILL.md           # Spawns all 3 reviewers in parallel
├── hooks/
│   └── hooks.json             # PostToolUse: lint after edits
└── settings.json              # Default agent: code-reviewer
```

### 9.3 Publishing Checklist

```
[ ] plugin.json with name, description, version, author
[ ] Correct structure (nothing inside .claude-plugin/ except plugin.json)
[ ] All skills tested via /reload-plugins
[ ] Agents tested via /agents
[ ] Hooks tested via real operations
[ ] README.md with installation and usage
[ ] Semantic versioning applied
[ ] Tested with --plugin-dir in a clean project
[ ] Verified via /context that skill cost is acceptable
```

### 9.4 Gradual Migration Strategy

1. **Week 1**: Prototype in `.claude/` -- individual skills, agents, hooks
2. **Week 2**: Test with the team via `.claude/` committed to VCS
3. **Week 3**: Convert to plugin, test with `--plugin-dir`
4. **Week 4**: Publish to marketplace or team git repo

### 9.5 Context Cost Optimization

For plugins with many skills:

1. Use `disable-model-invocation: true` on skills rarely used by the model
2. Consolidate similar skills into a single skill with `$ARGUMENTS`
3. Monitor budget via `/context`
4. Prefer fewer powerful skills over many specific skills
5. Use concise descriptions (each description consumes tokens at startup)
