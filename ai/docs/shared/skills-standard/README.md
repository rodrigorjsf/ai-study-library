# Agent Skills Standard — Official Documentation

> **Mirror refreshed 2026-10-11** (previous capture ~2026-05-01). Every file below was re-fetched from the site's raw-markdown endpoints (`https://agentskills.io/<page>.md`) and replaced verbatim; each carries its own `> Source:` line under the H1.

This directory contains official documentation mirrored from **[agentskills.io](https://agentskills.io)**, the open standard for extending AI agents with skills.

The Agent Skills standard is widely adopted across GenAI agents (Cursor, Claude Code, Codex, and others). It defines the portable, version-controlled format that allows skills to work across any compliant agent implementation.

**Related documentation**: [Skill Authoring Best Practices](../skill-authoring-best-practices.md) (universal guide) | [Extend Claude with Skills](../../claude-code/skills/extend-claude-with-skills.md) (Claude Code tutorial) | [Research: Skills Format Comparison](../../claude-code/skills/research-claude-code-skills-format.md)

## Documents

| File | Title on the site | Mirrored from | Description |
|------|-------------------|---------------|-------------|
| [agentskills-what-are-skills.md](./agentskills-what-are-skills.md) | Agent Skills Overview | `https://agentskills.io/home.md` | Core concepts: what a skill is, why the format exists, the three progressive-disclosure stages, and the client logo list. The former "What are skills?" page (`/what-are-skills`) now redirects here, so the file name is historical. |
| [agentskills-specification.md](./agentskills-specification.md) | Specification | `https://agentskills.io/specification.md` | Full technical specification — directory structure, `SKILL.md` frontmatter fields and constraints, optional directories, progressive disclosure, file references, validation |
| [agentskills-best-practices.md](./agentskills-best-practices.md) | Best practices for skill creators | `https://agentskills.io/skill-creation/best-practices.md` | Authoring guidelines: start from real expertise, scope, calibrating control, instruction patterns, bundling reusable scripts |
| [agentskills-using-scripts.md](./agentskills-using-scripts.md) | Using scripts in skills | `https://agentskills.io/skill-creation/using-scripts.md` | How to run one-off commands and bundle self-contained scripts inside a skill, and how to design script interfaces for agents |
| [agentskills-optimizing-descriptions.md](./agentskills-optimizing-descriptions.md) | Optimizing skill descriptions | `https://agentskills.io/skill-creation/optimizing-descriptions.md` | Techniques for testing and improving `description` fields so a skill triggers reliably |
| [agentskills-evaluating-skills.md](./agentskills-evaluating-skills.md) | Evaluating skill output quality | `https://agentskills.io/skill-creation/evaluating-skills.md` | Eval-driven iteration: test cases, assertions, grading, comparing with and without the skill |

## What changed between the two captures

A line-by-line diff of the May and October captures shows the standard is stable. The real changes are few:

| Page | Change |
|------|--------|
| Specification | `name` charset now explicitly lists digits: "(`a-z`, `0-9`) and hyphens" (the summary table already allowed numbers; the detailed rule previously showed only `a-z`). |
| Specification | `metadata` is now specified as "a map from string keys to string values". |
| Specification | `allowed-tools` is described as a "space-separated string" (was "space-delimited list"); still marked Experimental. |
| Best practices | New closing sections: "Bundling reusable scripts" and "Next steps". |
| Best practices, Optimizing descriptions | The progressive-disclosure link moved from `/what-are-skills#how-skills-work` to `/specification#progressive-disclosure`. |
| What are skills? | Page removed as a standalone URL; content folded into the site's home page ("Agent Skills Overview"). |
| Evaluating skills, Using scripts | No content change (whitespace only). |

## Pages on the site that are not mirrored here

The site index (<https://agentskills.io/llms.txt>, opened 2026-10-11) lists three more pages. They are listed for completeness; no local copy exists.

| Page | URL |
|------|-----|
| Client Showcase | <https://agentskills.io/clients.md> |
| Quickstart | <https://agentskills.io/skill-creation/quickstart.md> |
| How to add skills support to your agent | <https://agentskills.io/client-implementation/adding-skills-support.md> |

## Related: skills served over MCP

Since 2026-09-13 there is an official MCP extension for discovering and reading Agent Skills from MCP servers (`io.modelcontextprotocol/skills`, SEP-2640, status Final). It builds on this standard's `SKILL.md` format and is documented at <https://modelcontextprotocol.io/extensions/skills/overview>.

## Source

All documents originate from the official Agent Skills documentation site:

- **Website**: <https://agentskills.io>
- **Full doc index**: <https://agentskills.io/llms.txt>

> These files are kept as a local reference for AI agents working in this repository. When in doubt, consult the live site for the most up-to-date version of the standard.
