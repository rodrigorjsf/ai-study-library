# Prompt Optimizer

## Input

**ORIGINAL_PROMPT:**

{{USER_PROMPT}}

## Optimization Protocol

Apply these evidence-based techniques in order:

### 1. Structural Analysis

- Extract core task and success criteria
- Identify implicit assumptions
- Map input→output requirements
- **Analyze context dependency:** Determine if the task requires accessing large-context data (docs, codebases).

### 2. Optimization

Apply relevant techniques (skip if not applicable):

**A. Instruction Clarity & Delimitation (Always)**

- Use imperative verbs (Analyze, Generate, Architect)
- **Use XML Tags:** Enclose distinct sections in semantic tags (e.g., `<instructions>`, `<context>`, `<constraints>`) to prevent instruction drift in long contexts.
- Define quality thresholds numerically or binary (Pass/Fail).

**B. Context & Modality Injection (If task is ambiguous)**

- **Multimodal grounding:** Specify how to handle non-text inputs (images, diagrams, logs) if present.
- Define the "Persona Level": Use specific expert roles (e.g., "Staff Engineer") rather than generic ones, or define a specific mental model.
- Include edge case handling.

**C. Structured Reasoning (For complex tasks)**

- **Internal Monologue:** Request the model to use a `<thinking>` block before the final response to plan and self-correct.
- Use markdown headings to guide the final output structure.
- Add verification step: "Check if [criteria] is met".

**D. Few-Shot Anchoring (Only if pattern is non-obvious)**

- Provide 1 high-quality example (One-shot is often sufficient).
- Show input→thinking→output transformation.
- Highlight negative constraints (what *not* to do).

**E. Constraint Specification (For creative/open-ended tasks)**

```markdown
<constraints>
  <must_have>[Element 1]</must_have>
  <must_have>[Element 2]</must_have>
  <forbidden>[Pattern 1]</forbidden>
</constraints>
```

### 3. Performance Boosters

- **Use XML for Data/Context:** `<code_snippet>`, `<logs>`, `<reference_text>`.
- **Employ numbered lists** for sequential steps.
- **Request "Chain of Density":** Ask for iterative refinement if the answer needs to be concise yet information-dense.
- **Reasoning Directive:** Explicitly ask the model to "Plan step-by-step" inside `<thinking>` tags for logic-heavy tasks.

### 4. Output Specification

Format as:

```markdown
## OPTIMIZED PROMPT

[Optimized prompt]

## OPTIMIZATION RATIONALE

**Applied Techniques:**

1. [Technique] → [Specific improvement]
2. [Technique] → [Specific improvement]

**Expected Improvements:**

- Precision: [How/Why]
- Context Adherence: [How/Why]
- Reasoning Depth: [How/Why]

**Adaptations:**

- [Specific leveraging of large context or reasoning capabilities]

## USAGE NOTES

**Input Requirements:**

- [What user must provide, including potential files/images]

**Quality Checks:**

- [How to verify output quality]

**Iteration Strategy:**

- [How to refine if first attempt fails]

-----

## CRITICAL RULES

1. **XML Delimiters**: Prefer `<tag>` structures over loose text for defining boundaries.
2. **No auto-execution**: This is an optimizer, not an executor.
3. **Variable Syntax**: Use `{{variables}}` for placeholders.
4. **Density over Fluff**: Remove conversational filler; optimize for token density.
5. **Evidence-based**: Every technique must have clear performance rationale.

## ANTI-PATTERNS TO AVOID

❌ Generic Personas (“You are a helpful assistant…”) → Use **Specific Expert Roles**.
❌ Loose Formatting (Mixing instructions with data without separators).
❌ Redundant safety disclaimers (Trust native guardrails).
❌ Asking for "Reflections" on trivial tasks (Adds latency).
❌ Ignoring Modality (Treating visual inputs as text descriptions only).

## CURRENT BEST PRACTICES

Based on recent architecture standards:

- **Tag-Based Control**: Models parse `<tags>` with higher attention weighting than markdown headers in long contexts.
- **Thinking Tokens**: Allocating output tokens for "silent" or explicit reasoning (`<thinking>`) drastically reduces logic errors.
- **Context Pinning**: Placing critical instructions at the *end* of the prompt (Recency Bias) or wrapping them in XML is more effective than repetition.
- **Zero-Shot CoT**: "Let's think step by step" is standard; prefers specific reasoning frameworks (e.g., "Analyze utilizing First Principles").
```