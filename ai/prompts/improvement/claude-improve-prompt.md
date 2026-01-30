# Claude Prompt Optimization Protocol v2.0

Optimize prompts for Claude 4.5/Opus 4.5 using evidence-based techniques from official documentation.

## INPUT
<original_prompt>
[PROMPT TO OPTIMIZE]
</original_prompt>

---

## STEP 1: DIAGNOSTIC

Answer these questions:

1. **Core intent**: What specific output/behavior is needed? (1 sentence)
2. **Complexity level**: Simple retrieval | Multi-step reasoning | Long-form generation | Tool use required
3. **Current weaknesses**: Ambiguity | Missing constraints | Wrong structure | Inefficient

---

## STEP 2: APPLY TECHNIQUES (Evidence-Based Priority)

### 🔴 CRITICAL - Apply if missing

**Clear Task & Success Criteria**
- First sentence = exact task
- Define output format with examples
- Bad: "Write about X" → Good: "Write 500-word analysis of X covering Y and Z"

**XML Structure for Complex Inputs**
```xml
<documents>...</documents>
<examples>...</examples>
<instructions>...</instructions>
```
Use when: Multiple input types, need to separate data from instructions

**Explicit Constraints**
- Length (word/token count, not "brief")
- Format (markdown, JSON, code blocks)
- What to AVOID (often more important than what to include)

### 🟡 CONDITIONAL - Apply when beneficial

**Prefilling** (start Claude's response)
When: Need specific format, prevent preambles, enforce structure
```
User: Generate JSON
Assistant: {
```

**Chain of Thought**
When: Multi-step reasoning, math, logic, analysis
How: Add "Think through this step-by-step" or "Before answering, analyze:"

**Examples (Few-shot)**
When: Pattern isn't obvious from description alone
Use: 2-3 examples max (Claude learns fast)
Structure:
```xml
<examples>
<example>
<input>...</input>
<output>...</output>
</example>
</examples>
```

**Role Prompting**
ONLY when domain expertise changes reasoning (lawyer, doctor, architect)
NOT for generic roles (assistant, expert, professional)

### 🟢 ADVANCED - Specific use cases

**Prompt Chaining** (break into subtasks)
When: Task has >3 distinct steps or requires intermediate validation
Pattern:
1. Extract data → 2. Analyze → 3. Synthesize → 4. Format

**Long Context (>100k tokens)**
- Put reference docs in <documents> tags
- Place instructions AFTER documents
- Use: "Focus only on X sections" to guide attention

**Extended Thinking**
When: System design, multi-constraint optimization, complex tradeoffs
How: Available automatically for complex tasks

**Tool Specification**
```xml
<instructions>
- Use web_search for: current events, recent data
- Create artifact for: standalone documents, code >50 lines
- Use code execution for: data analysis, calculations
</instructions>
```

---

## STEP 3: ANTI-PATTERNS TO REMOVE

❌ **Remove these - they hurt performance:**

1. Motivational fluff: "You are the world's best...", "Take a deep breath"
2. Redundant politeness: "Please", "if you don't mind", "I would appreciate"
3. Multiple personas: "As expert A and expert B..."
4. Obvious instructions: "Be accurate", "think carefully"
5. Hedge words in constraints: "Try to", "around", "approximately" (use exact numbers)

---

## OUTPUT FORMAT

### 📋 Optimized Prompt
```
[Clean, executable prompt - no placeholders or explanations]
```

### 🔧 Optimization Summary

**Applied Techniques:**
- [Technique 1]: [Why it improves performance]
- [Technique 2]: [Why it improves performance]

**Removed:**
- [What was cut and why]

**Expected Improvement:**
- Clarity: [Specific ambiguity resolved]
- Reliability: [How consistency improves]
- Efficiency: [Token reduction or speed gain]

### ⚙️ Usage Guidance

**When to iterate:**
- If output is [X], adjust [Y parameter]

**Tool recommendations:**
- Use extended thinking if: [scenario]
- Enable web_search if: [scenario]

**Edge cases to test:**
- [Scenario 1]: Expected behavior [X]
- [Scenario 2]: Expected behavior [Y]

---

## OPTIMIZATION PRINCIPLES

### What Claude excels at:
✅ Following complex nested instructions  
✅ Maintaining consistency across 200k+ token contexts  
✅ Self-correction when given clear criteria  
✅ Separating data from instructions (XML)  
✅ Using examples to infer patterns (2-3 examples sufficient)

### What Claude doesn't need:
❌ Roleplay overhead ("You are a brilliant...")  
❌ Motivation/encouragement  
❌ Hand-holding through obvious steps  
❌ Multiple redundant examples (>5)  
❌ Asking for Chain of Thought on simple tasks

### Decision Framework:
- Simple task (1-step) → Direct instruction
- Medium task (2-4 steps) → Numbered steps or XML structure  
- Complex task (5+ steps) → Prompt chaining or extended thinking
- Requires latest data → Specify web_search
- Output >100 lines → Artifact creation

---

## VALIDATION CHECKLIST

Before finalizing, verify:

- [ ] First sentence clearly states the task
- [ ] Success criteria are measurable (not "good" or "comprehensive")
- [ ] Examples provided only when pattern is non-obvious
- [ ] All constraints are specific numbers (not "brief" or "detailed")
- [ ] No motivational fluff or redundant politeness
- [ ] XML structure used if >2 input types
- [ ] Chain of thought invoked only for multi-step reasoning
- [ ] Tool usage specified if required (search, code, artifacts)

**Token budget check:** Is every sentence necessary? If removed, would quality degrade?

---

## ADVANCED: PROMPT CHAINING TEMPLATE

For multi-stage tasks:

**Stage 1: Extract**
```
<documents>[DATA]</documents>
Extract all instances of X that match criteria Y.
Output format: JSON array
```

**Stage 2: Analyze** (uses Stage 1 output)
```
<extracted_data>[STAGE 1 OUTPUT]</extracted_data>
For each item, calculate Z and rank by W.
Output: Markdown table
```

**Stage 3: Synthesize**
```
<analysis>[STAGE 2 OUTPUT]</analysis>
Write executive summary highlighting top 3 insights.
Length: 200 words. Tone: Technical.
```