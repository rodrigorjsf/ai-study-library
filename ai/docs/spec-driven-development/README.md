# Spec-Driven Development — Research Overview

> **Currency check (2026-10-11):** Partially outdated
>
> - **Still holds:** the three rigor levels and the critique themes (review overhead, spec rot, false confidence).
> - **Tool landscape changed:** Tessl now presents itself as an "agent enablement platform" built on a skills registry, not as an SDD framework (https://www.tessl.io/); Kiro is a Code OSS-based IDE plus CLI and web app, not a VS Code extension (https://kiro.dev/); Spec Kit (about 141k stars) now describes itself as a toolkit for "SDD or any other process" (https://github.com/github/spec-kit).
> - **Missing tools:** BMAD-METHOD (about 54k stars, active, https://github.com/bmad-code-org/BMAD-METHOD) and GSD (about 64k stars; archived 26 Jun 2026 and continued as GSD Core at https://github.com/open-gsd/gsd-core, https://github.com/gsd-build/get-shit-done).
> - **Later critique to read alongside:** HumanLayer's "Why 'spec is the new code' is not enough" and "Why Software Factories Fail" (https://www.humanlayer.com/blog/humanlayer-resources, https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/wsff.md).
> - **Could not verify:** the "up to 50% error reduction" figure repeated below; it comes from the arXiv paper's own citation and was not independently checked.

This directory contains research on **Spec-Driven Development (SDD)** — the practice of treating specifications, not code, as the primary artifact of software development, particularly in the context of AI coding assistants.

## What is Spec-Driven Development?

SDD inverts the traditional workflow: instead of writing code and documenting later, teams write structured specifications first, which then serve as the source of truth for both human developers and AI coding agents. AI models are excellent at pattern completion but poor at mind reading — a precise spec eliminates the guesswork that leads to "vibe coding" failures.

**Three levels of rigor:**
| Level | Description | When to Use |
|-------|-------------|-------------|
| **Spec-First** | Write spec before coding; spec may not be maintained after | AI-assisted initial development, prototypes |
| **Spec-Anchored** | Spec maintained alongside code; tests enforce alignment | Production systems, long-lived features |
| **Spec-as-Source** | Spec is the only human-edited artifact; code is generated | Domains with mature code generation (API stubs, embedded automotive) |

**The SDD Workflow:**
1. **Specify** — Define behavior, requirements, acceptance criteria (not implementation details)
2. **Plan** — Define architecture, data models, technology choices
3. **Implement** — Generate/write code in small validated increments
4. **Validate** — Run automated tests + stakeholder review; spec remains authority

## Saved Files

### 1. [spec-driven-development-arxiv.md](./spec-driven-development-arxiv.md)
**Source:** https://arxiv.org/abs/2602.00180  
**Type:** Academic paper (arXiv:2602.00180, submitted to AIWare 2026)  
**Author:** Deepak Babu Piskala  
**Content:** Comprehensive practitioner guide covering SDD principles, all three rigor levels, four-phase workflow, how SDD boosts AI coding agents (up to 50% error reduction), survey of tools (BDD frameworks, OpenAPI, Spec Kit, Kiro, Tessl), three case studies (financial services API: 75% cycle time reduction; enterprise BDD; automotive embedded with ISO 26262), common pitfalls, and comparison to traditional design documents.

### 2. [spec-driven-development-main.md](./spec-driven-development-main.md)
**Source:** https://dev.to/bobbyblaine/spec-driven-development-write-the-spec-not-the-code-2p5o  
**Type:** Practitioner blog post (DEV Community)  
**Content:** Practical, opinionated guide contrasting "vibe coding" with SDD. Step-by-step getting started with GitHub Spec Kit. Honest assessment of where SDD breaks down: review overhead, poor fit for exploratory work, persistent AI non-determinism. Real-world examples from Anthropic, Vercel, and Pydantic. Key insight: *"Move the ambiguity from code review to spec review, where it is cheaper to fix."*

### 3. [spec-driven-development-variant.md](./spec-driven-development-variant.md)
**Source:** https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html  
**Type:** Critical analysis (martinfowler.com "Exploring Gen AI" series)  
**Content:** Hands-on critical evaluation of Kiro, GitHub Spec Kit, and Tessl by a practitioner. Raises important open questions about SDD's real-world applicability: one-workflow-fits-all-sizes limitations, markdown review fatigue, false sense of control despite AI non-determinism, difficulty separating functional from technical spec. Provides a balanced counterpoint to SDD hype with concrete failure modes observed during actual tool usage.

## Key Insights

- **AI catalyst**: Specs act as "super-prompts" giving AI agents unambiguous, executable contracts — empirical studies show up to 50% error reduction with human-refined specs
- **Not new**: SDD builds on decades of TDD and BDD wisdom; what's new is tooling, CI/CD maturity, and AI as a spec consumer
- **Tool landscape as captured (late 2025 – early 2026)**: GitHub Spec Kit (CLI, most customizable), AWS Kiro (simplest; a Code OSS-based IDE, described in the saved articles as a VS Code extension), Tessl (most ambitious, spec-as-source). See the currency check at the top for what changed by October 2026 (Tessl repositioned, BMAD-METHOD and GSD not covered).
- **Sweet spot**: Greenfield features with well-understood requirements; less useful for exploratory/prototype work
- **Common pitfalls**: Over-specification, spec rot, spec-as-bureaucracy, tooling complexity, false confidence from passing tests

## Further Reading

- GitHub Spec Kit: https://github.com/github/spec-kit
- AWS Kiro: https://kiro.dev/
- Tessl (now an "agent enablement platform"; Framework status could not be verified on 2026-10-11): https://tessl.io/
- BMAD-METHOD: https://github.com/bmad-code-org/BMAD-METHOD
- GSD (archived 2026-06-26; continued as GSD Core): https://github.com/open-gsd/gsd-core
- Thoughtworks Technology Radar (SDD entry): https://www.thoughtworks.com/radar/techniques/spec-driven-development
- Specmatic (contract testing): https://specmatic.io/
