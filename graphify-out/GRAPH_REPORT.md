# Graph Report - ./ai/docs  (2026-04-25)

## Corpus Check
- 117 files · ~272,422 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 476 nodes · 665 edges · 21 communities detected
- Extraction: 89% EXTRACTED · 10% INFERRED · 1% AMBIGUOUS · INFERRED: 69 edges (avg confidence: 0.78)
- Token cost: 18,500 input · 4,200 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Cursor Agent Tooling|Cursor Agent Tooling]]
- [[_COMMUNITY_Agent Orchestration & Plugins|Agent Orchestration & Plugins]]
- [[_COMMUNITY_Agent Skills Standard|Agent Skills Standard]]
- [[_COMMUNITY_Agent Communication Protocols|Agent Communication Protocols]]
- [[_COMMUNITY_Agentic Harness Patterns|Agentic Harness Patterns]]
- [[_COMMUNITY_Context Engineering Foundations|Context Engineering Foundations]]
- [[_COMMUNITY_Advanced Context Optimization|Advanced Context Optimization]]
- [[_COMMUNITY_MCP & Protocol Ecosystem|MCP & Protocol Ecosystem]]
- [[_COMMUNITY_Spec-Driven Development|Spec-Driven Development]]
- [[_COMMUNITY_Prompting Techniques|Prompting Techniques]]
- [[_COMMUNITY_SDD Tools & Levels|SDD Tools & Levels]]
- [[_COMMUNITY_Claude 4.x Best Practices|Claude 4.x Best Practices]]
- [[_COMMUNITY_MCP Enterprise & Governance|MCP Enterprise & Governance]]
- [[_COMMUNITY_Documentation Index|Documentation Index]]
- [[_COMMUNITY_HumanLayer Architecture|HumanLayer Architecture]]
- [[_COMMUNITY_Commercial Context Systems|Commercial Context Systems]]
- [[_COMMUNITY_AGENTS.md Efficacy Research|AGENTS.md Efficacy Research]]
- [[_COMMUNITY_Human-Agent Collaboration|Human-Agent Collaboration]]
- [[_COMMUNITY_JSON Schema Behavior|JSON Schema Behavior]]
- [[_COMMUNITY_Refusal Edge Case|Refusal Edge Case]]
- [[_COMMUNITY_MCP Runtime|MCP Runtime]]

## God Nodes (most connected - your core abstractions)
1. `Progressive Disclosure (Skills Context Management)` - 20 edges
2. `Spec-Driven Development` - 17 edges
3. `Cursor Hooks Guide` - 15 edges
4. `Model Context Protocol (MCP)` - 13 edges
5. `Cursor Subagents Guide` - 12 edges
6. `Research-Plan-Implement (RPI) Workflow` - 12 edges
7. `SKILL.md Format (Frontmatter + Markdown Body)` - 12 edges
8. `Cursor Rules Guide` - 11 edges
9. `Lost in the Middle (Liu et al., TACL 2024)` - 11 edges
10. `Cursor IDE Official Documentation README` - 10 edges

## Surprising Connections (you probably didn't know these)
- `Context-Free Grammar (CFG) Constrained Decoding` --semantically_similar_to--> `Spec-Driven Development`  [AMBIGUOUS] [semantically similar]
  ai/docs/structured-outputs/README.md → ai/docs/spec-driven-development/README.md
- `Spec-Driven Development` --semantically_similar_to--> `Cursor Plan Mode (Shift+Tab)`  [INFERRED] [semantically similar]
  ai/docs/spec-driven-development/README.md → ai/docs/cursor/best-practices/agent-best-practices.md
- `Progressive / On-Demand Skill Loading` --semantically_similar_to--> `Progressive Disclosure in AI Agents`  [INFERRED] [semantically similar]
  ai/docs/cursor/skills/agent-skills-guide.md → ai/docs/context-engineering/progressive-disclosure-ai-agents.md
- `Phase-Based Context Loading` --semantically_similar_to--> `Research-Plan-Implement (RPI) Workflow`  [INFERRED] [semantically similar]
  ai/docs/context-engineering/progressive-disclosure-ai-agents.md → ai/docs/agentic-engineering/research-plan-implement-rpi.md
- `MCP vs A2A Protocol` --possibly_related_to--> `Agent Teams (Claude Code)`  [AMBIGUOUS]
  ai/docs/harness-engineering/harness-engineering.md → ai/docs/claude-code/subagents/claude-orchestrate-of-claude-code-sessions.md

## Hyperedges (group relationships)
- **Cursor Agent Control Plane: Rules, Hooks, and MCP together define the agent's behavior envelope** — cursor_rules_doc, cursor_hooks_guide, cursor_mcp_guide, cursor_subagents_guide [INFERRED 0.85]
- **Structured Outputs Reliability Triad: CFG decoding, schema complexity limits, and grammar caching together guarantee schema-valid AI output** — structured_outputs_cfg_decoding, structured_outputs_schema_complexity_limits, structured_outputs_grammar_caching [EXTRACTED 0.95]
- **SDD Tooling Triad: GitHub Spec Kit, AWS Kiro, and Tessl each implement SDD at different rigor levels and complexity** — sdd_readme_github_spec_kit, sdd_readme_aws_kiro, sdd_readme_tessl [EXTRACTED 0.95]
- **Context Degradation Triad: Lost-in-Middle, Dumb Zone, Context Rot all describe the same underlying LLM performance collapse from context overload** — u_shaped_performance_curve, dumb_zone_concept, context_rot [INFERRED 0.95]
- **RPI Workflow Independent Convergence: RPI (HumanLayer), RPIR (Tyler Burleigh), Atelier harness and Agentic Modernization all independently converged on Research→Plan→Implement as the optimal agentic coding workflow** — rpi_workflow, tyler_burleigh_rpir_workflow, atelier_harness, agentic_software_modernization [EXTRACTED 1.00]
- **Context Engineering Solution Space: Intentional Compaction, Progressive Disclosure, and Phase-Based Context Loading are all strategies addressing the same problem of context overload in agentic workflows** — intentional_compaction, progressive_disclosure_agents, phase_based_context_loading [INFERRED 0.88]
- **Skill Quality Improvement Loop: Progressive Disclosure + Eval-Driven Dev + Description Optimization** — concept_progressive_disclosure, concept_eval_driven_development, concept_skill_triggering, agentskills_optimizing_descriptions [INFERRED 0.82]
- **MCP Enterprise Stack: Stateless Transport + XAA Auth + AAIF Governance** — concept_mcp_transport_stateless, concept_mcp_xaa_auth, concept_agentic_ai_foundation, long_live_mcp_aqfer [EXTRACTED 0.90]
- **Skills-over-MCP Discovery System: Lazy Loading + Well-Known Index + URI Resolution** — concept_skill_lazy_loading, concept_skill_uri_well_known, concept_mcp_skills_over_mcp, skills_over_mcp_office_hours_2460 [EXTRACTED 0.88]
- **Context Management Triad: Rot Prevention via Subagents, Skills, Hooks** — subagent_context_firewall, skill_progressive_disclosure, rationale_hooks_determinism, context_rot [INFERRED 0.85]
- **Claude Code Extensibility Stack: Skills + Plugins + Hooks + Subagents** — extend_claude_skills, claude_plugin_doc, hook_reference_doc, creating_custom_subagents [EXTRACTED 1.00]
- **Harness Engineering Core Pattern: Memory + Deterministic Rails + Orchestration** — harness_persistent_memory, harness_deterministic_rails, harness_specialized_roles, back_pressure_mechanisms [INFERRED 0.90]
- **Context Optimization Triad: Hooks + Path-Scoped Rules + Skills as Progressive Disclosure** — concept_hooks_deterministic, concept_path_scoped_rules, concept_skill_md_format, concept_progressive_disclosure [EXTRACTED 0.95]
- **Agent Protocol Convergence: MCP (tool-to-agent) + A2A (agent-to-agent) form complementary 2026 stack** — concept_mcp_protocol, concept_a2a_protocol, concept_full_connectivity_2026 [EXTRACTED 0.90]
- **Context Engineering Foundations: Context Rot + Attention Budget + Instruction Budget share the same finite-resource constraint model** — concept_context_rot, concept_attention_budget, concept_instruction_budget [INFERRED 0.88]
- **PTC + Tool Search + Sandboxed Execution together constitute the modern token-optimization architecture for agentic tool calling** — ptc_concept, tool_search_concept, vercel_sandbox, opensandbox_platform [EXTRACTED 0.95]
- **MCP, A2A, ANP, and ACP form an emerging protocol ecosystem for agent interoperability and communication** — mcp_protocol, a2a_protocol, anp_protocol, acp_protocol [EXTRACTED 0.92]
- **Positional bias, U-shaped curve, and in-between effect jointly constrain optimal RAG document placement strategies** — positional_bias_phenomenon, u_shaped_performance_curve, in_between_effect [INFERRED 0.88]

## Communities

### Community 0 - "Cursor Agent Tooling"
Cohesion: 0.04
Nodes (64): Cursor Agent Best Practices, Cursor Agent Harness (instructions + tools + model), Cursor Plan Mode (Shift+Tab), Rules as Static Context, Skills as Dynamic Workflows, Cursor Browser Design Sidebar, Cursor Browser Tool Guide, Browser MCP Server Integration (+56 more)

### Community 1 - "Agent Orchestration & Plugins"
Cohesion: 0.05
Nodes (57): Agent Skills Open Standard (agentskills.io), Agent Team Lead, Agent Team Mailbox (Inter-agent Messaging), Agent Team Shared Task List, Agent Teams (Claude Code), Analysis: Orchestrating Agent Teams in Claude Code, Analysis: Creating Plugins for Claude Code, Analysis: Creating Custom Subagents (+49 more)

### Community 2 - "Agent Skills Standard"
Cohesion: 0.08
Nodes (55): Best Practices for Skill Creators, Evaluating Skill Output Quality, Optimizing Skill Descriptions, Agent Skills Standard README, Agent Skills Specification, Using Scripts in Skills, What Are Skills?, Analysis: Automate Workflows with Hooks (+47 more)

### Community 3 - "Agent Communication Protocols"
Cohesion: 0.06
Nodes (47): Agent-to-Agent Protocol (A2A) by Google, Agentic Context Engineering (ACE) Framework (Zhang et al. 2025), Agent Communication Protocol (ACP) by IBM Research, Advancing Agentic AI through Communication Protocols (IJSRST 2025), Agent Cards (capability-rich discovery in A2A), Agentic Loop Pattern (tool_use / tool_result cycle), Agent Network Protocol (ANP), Architectural Paradigms of Advanced Agentic Systems (synthesis) (+39 more)

### Community 4 - "Agentic Harness Patterns"
Cohesion: 0.06
Nodes (38): Agent Skills Open Standard, Atelier Agent Harness, Browser Automation Testing for Agents, Chain of Thought (CoT) Prompting, Claude Progress File (claude-progress.txt), Claude Interaction & Prompting Guide, Coding Agent Incremental Progress Pattern, Cursor Agent Skills (+30 more)

### Community 5 - "Context Engineering Foundations"
Cohesion: 0.07
Nodes (35): Analysis: A Guide to CLAUDE.md, Analysis: LLM Context Optimization for AI Coding Agents, Auto Memory (Claude Code), Back-Pressure Mechanisms, CLAUDE.md Files, .claude/rules/ Directory, Context Engineering (as a Skill), Context Rot (+27 more)

### Community 6 - "Advanced Context Optimization"
Cohesion: 0.07
Nodes (34): Advanced Context Engineering for Coding Agents (Dex Horthy), Agentic Software Modernization, Your AGENTS.md is a Liability (Paddo), Attention Sinks (Xiao et al., ICLR 2024), Bad Trajectory Reinforcement (Context Poison), Codebase Hygiene (Pre-AI Cleanup), Context Window as RAM Analogy, Critic Agent Pattern (Engineer + Critic Loop) (+26 more)

### Community 7 - "MCP & Protocol Ecosystem"
Cohesion: 0.11
Nodes (29): A2A Protocol - Hugging Face Community, Agent-to-Agent Protocol (A2A), Agent Communication Protocol (ACP), Agent Card (A2A Discovery), Full Connectivity Vision 2026 (AI Agents), MCP Primitives (Resources, Prompts, Tools, Sampling), Model Context Protocol (MCP), Skills over MCP (MCP Prompts as Skill Libraries) (+21 more)

### Community 8 - "Spec-Driven Development"
Cohesion: 0.11
Nodes (24): AI Non-Determinism Limitation, Constitutional Foundation (Spec Kit), /plan Command (Spec Kit), Rationale: Move Ambiguity from Code Review to Spec Review, SDD Practitioner Guide (DEV.to), /specify Command (Spec Kit), /tasks Command (Spec Kit), AWS Kiro (+16 more)

### Community 9 - "Prompting Techniques"
Cohesion: 0.11
Nodes (23): Few-Shot Examples for Consistency, Prompt Chaining for Complex Tasks, Retrieval-Augmented Generation for Consistency, Response Prefilling Technique, Anthropic Tool Use Implementation Guide, Anthropic Increase Consistency Guide, Anthropic Strict Tool Use Guide, Rationale: Strict Mode for Reliable Agentic Systems (+15 more)

### Community 10 - "SDD Tools & Levels"
Cohesion: 0.2
Nodes (12): Amazon Kiro (VS Code SDD extension), GitHub Spec Kit (AI-assisted SDD CLI tool), Rationale: AI coding assistants made SDD newly relevant because LLMs are excellent at pattern completion but poor at mind reading without specs, Spec-Driven Development: From Code to Contract in the Age of AI Coding Assistants, Spec-Driven Development (SDD), Spec-Anchored (living documentation level), Spec-as-Source (humans edit specs, machines generate code), Spec-First (guided initial development level) (+4 more)

### Community 11 - "Claude 4.x Best Practices"
Cohesion: 0.2
Nodes (11): Adaptive Thinking (Claude 4.6), Anthropic Claude Cookbook, Claude 4.x Prompting Best Practices, Claude Context Awareness (Token Budget Tracking), Claude Prompting Best Practices, Context Window Management, Multi-Context Window Workflow, Parallel Tool Calling (+3 more)

### Community 12 - "MCP Enterprise & Governance"
Cohesion: 0.29
Nodes (10): Agentic AI Foundation (AAIF) at Linux Foundation, MCP Apps Extension (HTML/JS sandboxed UI results), MCP CIMD (Client ID Metadata Documents), MCP Server Cards (/.well-known/mcp.json), MCP Stateless Transport (MRTR / June 2026 Roadmap), MCP Cross-App Access (XAA) Enterprise Auth, Long Live MCP - MCP Dev Summit NA 2026 Recap (Aqfer), Long Live MCP - Dev Summit Recap (AWS Builder Center) (+2 more)

### Community 13 - "Documentation Index"
Cohesion: 0.22
Nodes (9): Third-Party Hooks Compatibility (Claude Code), Agent Skills Open Standard, AI Documentation Hub, Analysis Documentation, Claude Code Documentation, Context Engineering Research, Cursor IDE Documentation, General LLM Documentation (+1 more)

### Community 14 - "HumanLayer Architecture"
Cohesion: 0.36
Nodes (8): Approval Loop via MCP (HumanLayer), claudecode-go (Go SDK for Claude Code), CodeLayer (AI Agent IDE), hld Daemon (HumanLayer Local Runtime), hlyr CLI (HumanLayer Runtime CLI), HumanLayer Repository Analysis, humanlayer-wui (Tauri/React Desktop UI), SQLite Persistence (hld Session Store)

### Community 15 - "Commercial Context Systems"
Cohesion: 0.33
Nodes (6): Canonical Truth vs Acceleration Layers, Context Engineering for Commercial Agent Systems (Jeremy Daly), Context Engine Loop (10-Step), Rationale: Context is Infrastructure (not Implementation Detail), Tenant Isolation in Context (Multi-Tenant Safety), Typed and Scoped Memory System

### Community 16 - "AGENTS.md Efficacy Research"
Cohesion: 0.4
Nodes (6): AGENTBENCH (benchmark for context file impact on coding agents), AGENTS.md / CLAUDE.md Context Files, Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?, Rationale: LLM-generated context files reduce performance and increase cost by 20%+, Rationale: Human-written context files preferred over LLM-generated because LLM-generated files add redundant documentation and unnecessary requirements, SWE-bench Lite (300 GitHub issue tasks benchmark)

### Community 17 - "Human-Agent Collaboration"
Cohesion: 0.6
Nodes (5): Cooperative Cuisine (CoCu) research environment, Dynamic Mentalizing Model (resource-rational, action-driven ToM), Fluid Collaboration (FC) concept, Towards Fluid Human-Agent Collaboration (Frontiers in Robotics and AI 2025), Theory of Mind (ToM) / Action-Oriented Mentalizing

### Community 18 - "JSON Schema Behavior"
Cohesion: 1.0
Nodes (1): Property Ordering Behavior (required first)

### Community 19 - "Refusal Edge Case"
Cohesion: 1.0
Nodes (1): Refusal Edge Case (stop_reason: refusal)

### Community 20 - "MCP Runtime"
Cohesion: 1.0
Nodes (1): MCP Runtime Framework (mcpruntime)

## Ambiguous Edges - Review These
- `Spec-Driven Development` → `Context-Free Grammar (CFG) Constrained Decoding`  [AMBIGUOUS]
  ai/docs/structured-outputs/README.md · relation: semantically_similar_to
- `Agent Teams (Claude Code)` → `MCP vs A2A Protocol`  [AMBIGUOUS]
  ai/docs/harness-engineering/harness-engineering.md · relation: possibly_related_to
- `Plugin Marketplace` → `marketplace.json Schema`  [AMBIGUOUS]
  ai/docs/claude-code/plugins/claude-create-plugin-doc.md · relation: uses
- `Persuasion Principles for Agent Skill Engineering` → `Chain-of-Thought Prompting`  [AMBIGUOUS]
  ai/docs/general-llm/persuasion-principles.md · relation: partially_overlaps
- `ReAct Pattern (Thought-Action-Observation)` → `Parahuman Effect`  [AMBIGUOUS]
  ai/docs/general-llm/persuasion-principles.md · relation: semantically_similar_to
- `Positional Bias in Long-Context LLMs (primacy and recency bias)` → `Agentic Context Engineering (ACE) Framework (Zhang et al. 2025)`  [AMBIGUOUS]
  ai/docs/agent-protocols/architectural-paradigms-advanced-agentic-systems.md · relation: is_affected_by

## Knowledge Gaps
- **180 isolated node(s):** `Cursor IDE Documentation`, `Analysis Documentation`, `Agent Skills Open Standard`, `Context Engineering Research`, `Spec-First Level` (+175 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `JSON Schema Behavior`** (1 nodes): `Property Ordering Behavior (required first)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Refusal Edge Case`** (1 nodes): `Refusal Edge Case (stop_reason: refusal)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `MCP Runtime`** (1 nodes): `MCP Runtime Framework (mcpruntime)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Spec-Driven Development` and `Context-Free Grammar (CFG) Constrained Decoding`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._
- **What is the exact relationship between `Agent Teams (Claude Code)` and `MCP vs A2A Protocol`?**
  _Edge tagged AMBIGUOUS (relation: possibly_related_to) - confidence is low._
- **What is the exact relationship between `Plugin Marketplace` and `marketplace.json Schema`?**
  _Edge tagged AMBIGUOUS (relation: uses) - confidence is low._
- **What is the exact relationship between `Persuasion Principles for Agent Skill Engineering` and `Chain-of-Thought Prompting`?**
  _Edge tagged AMBIGUOUS (relation: partially_overlaps) - confidence is low._
- **What is the exact relationship between `ReAct Pattern (Thought-Action-Observation)` and `Parahuman Effect`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._
- **What is the exact relationship between `Positional Bias in Long-Context LLMs (primacy and recency bias)` and `Agentic Context Engineering (ACE) Framework (Zhang et al. 2025)`?**
  _Edge tagged AMBIGUOUS (relation: is_affected_by) - confidence is low._
- **Why does `Cursor Agent Skills` connect `Agentic Harness Patterns` to `Agent Orchestration & Plugins`?**
  _High betweenness centrality (0.387) - this node is a cross-community bridge._