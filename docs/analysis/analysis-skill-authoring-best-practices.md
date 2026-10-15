# Complete Analysis: Skill Authoring Best Practices

> **Status**: Current
> **Source document**: [`docs/skills/skill-authoring-best-practices.md`](../skills/skill-authoring-best-practices.md)
> **Analysis date**: 2026-03-27
> **Scope**: Comprehensive analysis of the official Anthropic guide on writing effective Claude Code skills, covering design principles, content patterns, testing strategies, and anti-patterns

---

## 1. Executive Summary

The document **skill-authoring-best-practices.md** is Anthropic's official guide for authoring effective skills in Claude Code. While `extend-claude-with-skills.md` defines the architecture and `research-claude-code-skills-format.md` details the technical format, this document focuses on **how to write well** — the design principles, content patterns, testing strategies, and anti-patterns that determine whether a skill will be effective or waste tokens.

The document is deeply aligned with the context optimization principles identified in `research-context-engineering-comprehensive.md`: conciseness as a fundamental principle (the context window is a "public good"), progressive disclosure as the central architecture (SKILL.md as index, reference files loaded on demand), and degrees of freedom calibrated to task fragility. The central mantra is: **"Claude is already very smart — only add context it doesn't have."**

The most significant contribution of this document is the methodology of **iterative development with two Claudes** (Claude A as the expert refining the skill, Claude B as the agent using it), combined with the **evaluation-driven development** approach that prioritizes creating evaluations before writing extensive documentation. This observe-refine-test cycle is the practical implementation of the Reflexion principle applied to agent infrastructure design.

## 2. Key Concepts and Mechanisms

### 2.1 Fundamental Principles

#### Conciseness as a Central Principle

The document establishes a clear hierarchy of token cost:

| Moment | What is Loaded | Cost |
|--------|---------------|------|
| Startup | Only `name` + `description` from all skills | Minimal |
| Trigger | Complete `SKILL.md` of the relevant skill | Moderate |
| On demand | Referenced files (reference/, examples/) | Variable |

**Decisive test for each piece of information:**

- "Does Claude actually need this explanation?"
- "Can I assume Claude already knows this?"
- "Does this paragraph justify its token cost?"

**Concrete example from the document:**

- Good (~50 tokens): Direct code with `pdfplumber` without explanation
- Bad (~150 tokens): Explanation of what PDF is, why use pdfplumber, how to install

#### Calibrated Degrees of Freedom

The document introduces a powerful metaphor — Claude as a robot exploring a path:

| Degree | Metaphor | When to Use | Example |
|--------|----------|-------------|---------|
| **High** | Open field with no dangers | Multiple valid approaches, decisions depend on context | Code review |
| **Medium** | Path with markers | Preferred pattern exists but variation is acceptable | Templates with parameters |
| **Low** | Narrow bridge with cliffs | Fragile operations, critical consistency | Database migrations |

**Derived principle:** The specificity of instructions should be proportional to error risk. The more destructive or irreversible the operation, the more prescriptive the skill should be.

#### Multi-Model Testing

Skills should be tested with all intended models:

| Model | Testing Consideration |
|-------|-----------------------|
| **Haiku** | Does the skill provide sufficient guidance? (needs more detail) |
| **Sonnet** | Is the skill clear and efficient? (balance) |
| **Opus** | Does the skill avoid over-explaining? (may need less) |

### 2.2 Skill Structure

#### YAML Frontmatter

| Field | Requirements | Limit |
|-------|-------------|-------|
| `name` | Lowercase, numbers, hyphens only. No XML tags, no reserved words ("anthropic", "claude") | 64 characters |
| `description` | Non-empty, no XML tags. Must describe WHAT it does AND WHEN to use it | 1024 characters |

#### Naming Conventions

**Preferred form — gerund (verb + -ing):**

- `processing-pdfs`, `analyzing-spreadsheets`, `managing-databases`

**Acceptable — noun phrases or action-oriented:**

- `pdf-processing`, `process-pdfs`

**Avoid:**

- Vague names: `helper`, `utils`, `tools`
- Generic: `documents`, `data`, `files`

#### Effective Descriptions

**Critical rule:** Always in third person. The description is injected into the system prompt — inconsistent POV causes discovery problems.

- Good: "Processes Excel files and generates reports"
- Bad: "I can help you process Excel files"
- Bad: "You can use this to process Excel files"

**Elements of a good description:**

1. What the skill does (capabilities)
2. When to use it (triggers/contexts)
3. Specific key terms (for matching)

### 2.3 Progressive Disclosure — Patterns

#### Pattern 1: High-Level Guide with References

```
SKILL.md (overview + quick start)
  ├── FORMS.md (loaded if form filling needed)
  ├── REFERENCE.md (loaded if API details needed)
  └── EXAMPLES.md (loaded if examples needed)
```

Claude loads files on demand. Zero context cost for unaccessed files.

#### Pattern 2: Domain-Based Organization

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md (revenue metrics)
    ├── sales.md (pipeline, opportunities)
    ├── product.md (API usage)
    └── marketing.md (campaigns)
```

When the user asks about sales, Claude loads only `sales.md`.

#### Pattern 3: Conditional Details

```markdown
## Creating documents
Use docx-js for new documents. See [DOCX-JS.md](DOCX-JS.md).

## Editing documents
For simple edits, modify XML directly.
**For tracked changes**: See [REDLINING.md](REDLINING.md)
```

#### Depth Rule: Maximum 1 Level

**Critical:** References must be at most 1 level deep from SKILL.md. Claude may use `head -100` to preview files referenced by other referenced files, resulting in incomplete information.

- Bad: `SKILL.md → advanced.md → details.md` (2 levels)
- Good: `SKILL.md → advanced.md`, `SKILL.md → reference.md` (1 level each)

#### Long Reference Files: Table of Contents

For files with more than 100 lines, include a TOC at the top so Claude can see the complete scope even in partial reads.

### 2.4 Workflows and Feedback Loops

#### Checklists for Complex Tasks

The document recommends providing copyable checklists that Claude can mark during execution:

```markdown
Task Progress:
- [ ] Step 1: Analyze the form
- [ ] Step 2: Create field mapping
- [ ] Step 3: Validate mapping
- [ ] Step 4: Fill the form
- [ ] Step 5: Verify output
```

#### Feedback Loops (Validate → Fix → Repeat)

Pattern that significantly improves quality:

1. Run validator/script
2. Fix errors found
3. Re-validate
4. Only proceed when validation passes

Applies to both skills with code (validation scripts) and without code (verification against style guides).

### 2.5 Content Guidelines

**Avoid time-sensitive information:**

- Bad: "If before August 2025, use the old API"
- Good: "Current method" section + collapsible "Old patterns" section

**Consistent terminology:**

- Choose ONE term and use it throughout the skill
- "API endpoint" always, don't mix with "URL", "route", "path"

### 2.6 Skills with Executable Code

#### Principle: Solve, Don't Punt

Scripts should handle errors instead of leaving Claude to resolve them:

- Good: `except FileNotFoundError: create default`
- Bad: `return open(path).read()` (silent failure)

#### Documented Constants (Ousterhout's Law)

```python
# Good: self-documenting
REQUEST_TIMEOUT = 30  # HTTP requests typically complete within 30s
MAX_RETRIES = 3       # Most intermittent failures resolve by 2nd retry

# Bad: magic numbers
TIMEOUT = 47  # Why 47?
```

#### Utility Scripts vs Generated Code

| Aspect | Pre-made Script | Code Generated by Claude |
|--------|----------------|-------------------------|
| Reliability | Higher (tested) | Variable |
| Token cost | Low (output only) | High (code in context) |
| Time | Fast (executes directly) | Slow (generates + executes) |
| Consistency | High | Variable |

**Critical distinction in instructions:**

- "Run `analyze_form.py` to extract fields" → **execute**
- "See `analyze_form.py` for the extraction algorithm" → **read as reference**

#### Plan-Validate-Execute Pattern

For complex and destructive operations:

1. Analyze → Create plan file (`changes.json`)
2. **Validate plan** with script
3. Execute changes
4. Verify output

When to use: batch operations, destructive changes, complex validation, high-stakes.

### 2.7 Evaluation and Iteration

#### Evaluation-Driven Development

**Recommended sequence:**

1. Identify gaps (run Claude without skill and document failures)
2. Create evaluations (3 minimum scenarios)
3. Establish baseline (performance without the skill)
4. Write minimal instructions
5. Iterate (run evaluations, compare, refine)

#### Iterative Development with Two Claudes

| Role | Function |
|------|----------|
| **Claude A** | Expert that helps refine the skill (design, structure, content) |
| **Claude B** | Agent that tests the skill on real tasks |
| **You** | Observer who identifies gaps and provides domain expertise |

**Cycle:** Observe Claude B → Identify problems → Refine with Claude A → Test with Claude B → Repeat

#### Observing Skill Navigation

Patterns to monitor:

- **Unexpected paths**: Claude reads files in unanticipated order → non-intuitive structure
- **Missed connections**: Claude doesn't follow references → links need to be more explicit
- **Excessive dependency**: Claude re-reads the same file repeatedly → content should be in the main SKILL.md
- **Ignored content**: Claude never accesses a bundled file → possibly unnecessary

## 3. Points of Attention

### 3.1 Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| **Over-explaining for Opus** | Wastes tokens with information Opus already knows | Test with each model; use "escape hatches" for details |
| **Under-explaining for Haiku** | Haiku needs more guidance than Opus | Aim for instructions that work for all models |
| **2+ level references** | Claude may do `head -100` instead of reading completely | Keep references at 1 level from SKILL.md |
| **First-person description** | Causes discovery problems when injected into system prompt | Always third person |
| **SKILL.md over 500 lines** | Degraded performance, excessive token competition | Split into reference files |
| **Time-sensitive information** | Becomes incorrect without warning | Use collapsible "Old patterns" section |
| **Multiple options without default** | Claude becomes indecisive | Provide clear default + escape hatch |
| **Windows-style paths** | Errors on Unix systems | Always forward slashes |
| **Assuming packages installed** | Silent failure in clean environments | List dependencies explicitly |
| **Voodoo constants** | Claude doesn't know how to adjust | Document justification for each constant |

### 3.2 The Completeness Paradox

The document reveals a fundamental tension: skills must be **sufficiently complete** to guide Claude, but **sufficiently concise** to not waste the context budget. The resolution lies in progressive disclosure — SKILL.md is a concise index, and details live in separate files loaded on demand.

### 3.3 Discovery vs Execution

The `description` serves for **discovery** (Claude deciding which skill to use among 100+), while the SKILL.md body serves for **execution** (how to perform the task). Optimizing for one without considering the other leads to problems:

- Vague description → skill is never selected
- Good description + bad body → skill is selected but fails in execution

## 4. Use Cases and Scope

### 4.1 When to Create a Skill

| Situation | Create Skill? | Alternative |
|-----------|--------------|-------------|
| Repetitive workflow with multiple steps | **Yes** | — |
| Domain knowledge that Claude doesn't have | **Yes** | — |
| Validation/formatting with specific scripts | **Yes** | — |
| Simple rule that should always be followed | No | Rule (`.claude/rules/`) |
| Deterministic enforcement of a constraint | No | Hook |
| General information about the project | No | CLAUDE.md |
| Dynamic session context | No | Hook `SessionStart` |

### 4.2 Decision: Degree of Freedom

```
Is the operation destructive or irreversible?
├── YES → Low freedom (exact scripts, no variation)
│   Examples: migrations, deploys, file deletions
└── NO → Are multiple approaches valid?
    ├── YES → High freedom (textual instructions, heuristics)
    │   Examples: code review, research, documentation
    └── NO → Medium freedom (pseudocode/templates with parameters)
        Examples: report generation, API calls, data processing
```

### 4.3 Application Scope by Task Type

| Task Type | Recommended Pattern | Required References |
|-----------|--------------------|--------------------|
| Data analysis | Domain-specific organization | Schemas per domain |
| Document processing | High-level guide + references | Format guides, scripts |
| Code generation | Template pattern + examples | API docs, examples |
| DevOps/CI | Workflow with checklist | Scripts, configs |
| Research/synthesis | Code-free workflow | Style guide, sources |

## 5. Applicability to Agent Infrastructure

### 5.1 Skills (Design Patterns)

**Skill Evolution Pattern:**

```
v1: Monolithic SKILL.md (< 200 lines)
  ↓ Natural growth
v2: SKILL.md + 1-2 reference files (< 500 lines total in SKILL.md)
  ↓ More domains/cases
v3: SKILL.md (index) + reference/ directory (domain-specific)
  ↓ Operational complexity
v4: SKILL.md + reference/ + scripts/ + hooks in frontmatter
```

**Skill Composition:**

- Skills can reference other skills indirectly (via instructions in SKILL.md)
- Skills with `context: fork` execute in an isolated subagent — zero impact on the main context
- Skills with `disable-model-invocation: true` keep descriptions out of context until trigger

**Refactoring Checklist:**

1. SKILL.md over 500 lines? → Split into references
2. References with more than 1 level? → Flatten to 1 level
3. Claude ignores a file? → Remove or improve signaling
4. Claude re-reads repeatedly? → Move to main SKILL.md
5. Description sufficiently specific? → Add key terms and triggers

### 5.2 Hooks

**How hooks complement skills:**

| Hook Event | Complement to Skill |
|-----------|---------------------|
| `PreToolUse` | Security validation before skill scripts execute |
| `PostToolUse` | Post-execution verification (lint, format, test) |
| `Stop` (agent) | Verification that the skill workflow completed correctly |
| `SessionStart` | Loading state that the skill needs |

**Hooks in skill frontmatter:**

```yaml
---
name: safe-deploy
description: Deploy with safety checks
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-deploy-cmd.sh"
  Stop:
    - hooks:
        - type: agent
          prompt: "Verify deployment completed. Check health endpoints."
---
```

**`once: true` flag:** For setup hooks that should run only once on skill activation (e.g., check installed dependencies).

### 5.3 Subagents

**Skills that delegate to subagents:**

- Main skill defines workflow and delegates investigation to subagents
- `context: fork` ensures the skill executes in an isolated subagent
- Subagents inherit hooks defined in the skill frontmatter

**Decomposition Pattern:**

```
Skill "research-and-implement"
  ├── Phase 1: Delegate research to Explore subagent
  ├── Phase 2: Analyze results in main context
  ├── Phase 3: Delegate implementation to subagent with worktree
  └── Phase 4: Verify result via Stop hook (agent type)
```

### 5.4 Rules

**When rules replace skill content:**

- Rules that apply to ALL skills (e.g., "always use TypeScript") → Global rule
- Path-specific rules that affect skill execution → Rule with `paths:` frontmatter
- Rules that need stronger enforcement → Hook in skill frontmatter

**Rules that reference skills:**

```markdown
# .claude/rules/api-development.md
---
paths: ["src/api/**"]
---
When working with API endpoints, use the /api-development skill for patterns and conventions.
```

### 5.5 Memory

**Skills and the memory system:**

| Interaction | Example |
|-------------|---------|
| Skill that queries memory | Commit skill checks `feedback_commit-style.md` for user preferences |
| Skill that generates memory | Onboarding skill saves project discoveries in memory files |
| Memory that informs trigger | MEMORY.md records that "user prefers skill X for tasks Y" |

**Pattern: Memory-Aware Skill**

```markdown
# SKILL.md
## Before starting
Check if there are relevant memory files in the project's memory directory
that might inform this task (previous decisions, preferences, constraints).
```

## 6. Prompt Engineering Guide Applicability

### 6.1 Technique → Skill Aspect Mapping

| Technique | Application in Skill Authoring | Where in the Skill |
|-----------|-------------------------------|-------------------|
| **Chain-of-Thought** | Multi-step workflows with checklists | Workflow sections in SKILL.md |
| **Prompt Chaining** | Sequential skill phases (analyze → plan → execute → verify) | SKILL.md phase structure |
| **ReAct** | Skills that use tools (Read → Analyze → Execute → Verify) | Utility scripts + instructions |
| **Least-to-Most** | Decomposition of complex problems into sub-tasks | Conditional workflow pattern |
| **Self-Consistency** | Validation loops (execute → validate → fix → re-validate) | Feedback loops |
| **Tree of Thoughts** | Decision skills with multiple paths | Conditional workflow pattern |
| **Reflexion** | Iterative development with two Claudes (observe-refine-test) | Evaluation process |
| **Few-shot (Examples)** | Input/output example patterns in the skill | Examples pattern |
| **Structured Output** | Template pattern for output formats | Template pattern |
| **Zero-shot CoT** | "Analyze the code structure and organization" (high freedom) | Textual instructions |

### 6.2 Techniques by Skill Phase

**Discovery phase (description):**

- Implicit Role Prompting: the description defines the skill's "role"
- Zero-shot: description must be sufficient without examples

**Execution phase (SKILL.md body):**

- Prompt Chaining: sequential phases with validation gates
- ReAct: skills that alternate between reasoning and tool use
- Least-to-Most: decomposition of complex tasks

**Validation phase (feedback loops):**

- Self-Consistency: multiple validator runs
- Reflexion: iterative improvement loop

### 6.3 When NOT to Use Advanced Techniques

| Technique | Why to Avoid in Skills |
|-----------|----------------------|
| Extensive Few-shot CoT | High token cost; use external references |
| Tree of Thoughts | Excessive complexity for most skills |
| PAL | Skills can already execute code directly |
| Auto-CoT | Skills are manually written, not auto-generated |

**Document principle:** "Claude is already very smart." Advanced prompting techniques are often unnecessary in skills — clear and concise instructions usually suffice.

## 7. Correlations with Main Documents

### 7.1 research-context-engineering-comprehensive.md

| Context Principle | Implementation in Skill Authoring |
|-------------------|----------------------------------|
| Context as a finite resource | "The context window is a public good" — every token competes |
| Instruction budget ~150-200 | SKILL.md body < 500 lines; split when exceeded |
| Progressive disclosure | SKILL.md as index → references loaded on demand |
| Lost-in-the-middle | TOC at top of long files ensures Claude sees complete scope |
| Context poisoning | Consistent terminology prevents contradictions; avoid time-sensitive info |
| JIT documentation | Reference files loaded only when relevant |
| Hybrid strategy | Metadata always loaded (description) + content on-demand (SKILL.md + refs) |

### 7.2 Evaluating-AGENTS-paper.md

| Paper Finding | Alignment with Best Practices |
|---------------|-------------------------------|
| LLM-generated configs reduce performance | Evaluation-driven development prevents over-documentation |
| More context ≠ better performance | Conciseness as a central principle; "Claude is already smart" |
| Generic overviews are ineffective | Descriptions must be specific with key terms |
| Instructions are followed literally | Degrees of freedom calibrated to task fragility |
| Niche repositories benefit more | Skills most valuable for domains Claude doesn't know |

### 7.3 claude-prompting-best-practices.md

| Best Practice | Implementation in Skill Authoring |
|---------------|----------------------------------|
| Be direct and specific | Specific descriptions, no obvious explanations |
| Use examples | Examples pattern with input/output pairs |
| Structured output | Template pattern for output formats |
| Think step by step | Workflows with sequential checklists |
| Give Claude a role | Description implicitly defines the role |

### 7.4 a-guide-to-agents.md (merged guide)

| Guide Principle | Skill Authoring Equivalent |
|-----------------|----------------------------|
| Keep config minimal | SKILL.md < 500 lines, split into refs |
| Progressive disclosure | 3 progressive disclosure patterns |
| Don't auto-generate | Evaluation-driven development; human iteration |
| Stale docs poison context | Avoid time-sensitive info; keep skills updated |
| Point elsewhere | SKILL.md as index pointing to refs |

## 8. Strengths and Limitations

### 8.1 Strengths

| Strength | Detail |
|----------|--------|
| **Practical and actionable** | Each principle accompanied by concrete good/bad examples |
| **Effective metaphors** | "Narrow bridge" vs "open field" for degrees of freedom |
| **Testing methodology** | Iterative development with two Claudes is innovative and practical |
| **Final checklist** | Verifiable quality list before sharing |
| **Multi-model** | Recognizes that skills should work on Haiku, Sonnet, and Opus |
| **Native progressive disclosure** | 3 clear patterns with visual diagrams |

### 8.2 Limitations

| Limitation | Impact |
|------------|--------|
| **No quantitative metrics** | "< 500 lines" is an empirical rule without quantitative evidence |
| **Focus on individual skills** | Little guidance on composition and orchestration of multiple skills |
| **Manual evaluation** | "There is no built-in way to run evaluations" — entirely manual process |
| **No versioning guidance** | How to evolve skills without breaking existing users |
| **Coding-centric** | Examples mostly about PDF/data processing; little coverage of analysis, research, or creation skills |
| **No hook integration** | Mentions hooks in frontmatter but doesn't explore advanced patterns |
| **No discovery metrics** | How to know if the description is working (correct trigger rate) |

## 9. Practical Recommendations

### 9.1 Extended Checklist for Skill Creation

**Pre-creation:**

- [ ] Run the task without a skill; document where Claude fails
- [ ] Create 3+ evaluation scenarios
- [ ] Measure baseline (performance without skill)
- [ ] Identify if the domain requires knowledge Claude doesn't have

**Structure:**

- [ ] `name` in gerund, lowercase with hyphens, < 64 chars
- [ ] `description` in third person, specific, with triggers, < 1024 chars
- [ ] SKILL.md body < 500 lines
- [ ] References at 1 level of depth only
- [ ] TOC in reference files > 100 lines
- [ ] Domain-based organization for multi-domain skills

**Content:**

- [ ] No explanations that Claude already knows
- [ ] Degree of freedom calibrated to fragility
- [ ] Consistent terminology throughout the skill
- [ ] No time-sensitive information (or in "Old patterns" section)
- [ ] Concrete examples (not abstract)
- [ ] Workflows with copyable checklists
- [ ] Feedback loops for critical quality

**Code (if applicable):**

- [ ] Scripts that handle errors (don't "punt to Claude")
- [ ] Documented constants (no magic numbers)
- [ ] Dependencies listed explicitly
- [ ] Clear distinction between execute vs read as reference
- [ ] Plan-validate-execute for destructive operations
- [ ] Forward slashes in all paths
- [ ] Scripts with verbose and specific error messages

**Testing and Iteration:**

- [ ] Tested with Haiku, Sonnet AND Opus
- [ ] Tested with real scenarios (not just test cases)
- [ ] Observed how Claude navigates the skill
- [ ] Iterated based on observation (not assumptions)
- [ ] Team feedback incorporated (if applicable)

### 9.2 Reusable Templates

**Template: Simple Skill (no code)**

```markdown
---
name: reviewing-pull-requests
description: Reviews pull requests for code quality, security, and conventions. Use when the user asks to review a PR, check code changes, or evaluate merge readiness.
---

# Pull Request Review

## Process
1. Read the diff completely before commenting
2. Check for security issues (OWASP Top 10)
3. Verify adherence to project conventions
4. Assess test coverage for changed code
5. Provide actionable feedback with specific suggestions

## Conventions
See [conventions.md](conventions.md) for project-specific rules.

## Common Issues
See [common-issues.md](common-issues.md) for frequently caught problems.
```

**Template: Skill with Scripts**

```markdown
---
name: processing-data-exports
description: Processes and validates data exports from the analytics pipeline. Use when working with CSV/JSON export files or when the user mentions data validation, export processing, or pipeline output.
---

# Data Export Processing

## Quick start
Run the validation script on any export file:
```

```bash
python scripts/validate_export.py input.csv
```

```markdown
## Workflow

- [ ] Step 1: Validate format (`validate_export.py`)
- [ ] Step 2: Check data quality (`check_quality.py`)
- [ ] Step 3: Transform if needed (`transform.py`)
- [ ] Step 4: Generate report (`report.py`)

## Schemas

See [reference/schemas.md](reference/schemas.md) for expected data formats.

## Error handling

See [reference/errors.md](reference/errors.md) for common validation errors and fixes.
```

**Template: Skill with Hooks**

```yaml
---
name: deploying-services
description: Deploys services with safety checks and rollback capability. Use when deploying, releasing, or pushing to production environments.
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-deploy-command.sh"
  Stop:
    - hooks:
        - type: agent
          prompt: "Verify deployment completed. Check health endpoints. $ARGUMENTS"
          timeout: 120
---
```

### 9.3 Recommended Evolution Pattern

```
Week 1: Create minimal skill + 3 evaluations
  ↓ Test with Claude B, observe
Week 2: Refine with Claude A based on observations
  ↓ Add references where Claude failed
Week 3: Add scripts for repetitive operations
  ↓ Add feedback loops for quality
Week 4: Add hooks in frontmatter for enforcement
  ↓ Share with team, collect feedback
Week 5+: Continuous iteration based on real usage
```
