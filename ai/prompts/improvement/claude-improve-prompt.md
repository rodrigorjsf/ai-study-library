# Claude Prompt Optimization Protocol

Optimize prompts for Claude 4.5/Opus 4.5 across **single-shot tasks** and **long-running agentic workflows**.

---

## QUICK DECISION TREE

**Is this a single-shot task?** (answer in one context window)  
→ Use **SECTION A: Single-Shot Optimization**

**Is this a long-running agent?** (multiple context windows, hours/days of work)  
→ Use **SECTION B: Long-Running Agent Harness**

**Unsure?**  
→ If task is >2 hours or requires >100k tokens, use Section B

---

# SECTION A: SINGLE-SHOT OPTIMIZATION

## INPUT

<original_prompt>
[PROMPT TO OPTIMIZE]
</original_prompt>

## STEP 1: DIAGNOSTIC

1. **Core intent**: What specific output is needed? (1 sentence)
2. **Complexity**: Simple retrieval | Multi-step reasoning | Long-form generation | Tool use
3. **Current weakness**: Ambiguity | Missing constraints | Wrong structure | Inefficient

## STEP 2: APPLY TECHNIQUES (Evidence-Based Priority)

### 🔴 CRITICAL - Apply if missing

**Be Explicit & Specific**

- Claude 4.x is LITERAL - vague requests get minimal responses
- Bad: "Create a dashboard"
- Good: "Create an analytics dashboard with 5+ charts, user filtering, and export functionality"

**Provide Context (The "Why")**

- Explain WHY a constraint matters - Claude generalizes from reasoning
- Bad: "Never use ellipses"
- Good: "This will be read by TTS, so avoid ellipses which can't be pronounced"

**Clear Success Criteria**

- First sentence = exact task
- Define output format with examples
- Specify what to AVOID (often more important than what to include)

**XML Structure for Complex Inputs**

```xml
<documents>...</documents>
<examples>...</examples>
<instructions>...</instructions>
```

Use when: Multiple input types, need to separate data from instructions

### 🟡 CONDITIONAL - Apply when beneficial

**Prefilling** (start Claude's response)

```
User: Generate JSON for user profile
Assistant: {
  "user_id":
```

When: Need specific format, prevent preambles, enforce structure

**Chain of Thought**
When: Multi-step reasoning, math, logic, analysis  
How: "Think through this step-by-step" or "Before answering, analyze:"

**Few-Shot Examples**
When: Pattern isn't obvious from description  
Use: 2-3 examples max (Claude 4.x learns FAST)

```xml
<examples>
<example>
<input>...</input>
<ideal_output>...</ideal_output>
</example>
</examples>
```

**Role Prompting**
ONLY when: Domain expertise changes reasoning (lawyer, doctor, security researcher)  
NOT for: Generic roles (assistant, expert, professional)

### 🟢 ADVANCED

**Prompt Chaining** (break into subtasks)
When: >3 distinct steps or requires intermediate validation  
Pattern:

1. Extract → 2. Analyze → 3. Synthesize → 4. Format

**Long Context (>100k tokens)**

- Put reference docs in `<documents>` tags
- Place instructions AFTER documents (Claude reads last messages more carefully)
- Use: "Focus only on sections X and Y" to guide attention

**Tool Specification**

```xml
<tool_guidelines>
- Use web_search for: current events, post-Jan-2025 data
- Create artifact for: documents >200 words, code >50 lines
- Use code execution for: data analysis, calculations
</tool_guidelines>
```

## STEP 3: ANTI-PATTERNS TO REMOVE

❌ **Remove - they hurt performance:**

1. Motivational fluff: "You are the world's best..."
2. Redundant politeness: "Please", "if you don't mind"
3. Multiple personas: "As expert A and expert B..."
4. Obvious instructions: "Be accurate", "think carefully"
5. Hedge words: "Try to", "around", "approximately" (use exact numbers)

## STEP 4: MODEL-SPECIFIC TUNING

### Opus 4.5 Specific

**Problem**: Overeagerness, over-engineering, unnecessary abstractions

**Solution**: Add explicit constraints

```text
Avoid over-engineering. Only make changes directly requested. Keep solutions minimal.
Don't add features, refactor code, or make "improvements" beyond what was asked.
Don't create helpers or abstractions for one-time operations.
```

### Haiku 4.5 Specific

**Problem**: May need more explicit step-by-step guidance

**Solution**: Break down complex tasks into numbered steps

### All Claude 4.x Models

**Problem**: Can be overly literal with examples

**Solution**: Ensure examples align EXACTLY with desired behavior

---

# SECTION B: LONG-RUNNING AGENT HARNESS

## When to use this section

- Task spans multiple context windows (>200k tokens)
- Work expected to take hours or days
- Requires state persistence across sessions
- Building complex software projects

## CORE PROBLEM

Agents working across multiple context windows face:

1. **No memory** between sessions
2. **Tendency to one-shot** complex tasks (leading to half-finished work)
3. **Premature completion** (declaring victory too early)
4. **Context fragmentation** (losing track of what was done)

## SOLUTION: TWO-AGENT PATTERN

### Agent 1: INITIALIZER (First context window only)

**Purpose**: Set up environment for all future coding sessions

**Required setup:**

1. **Feature list** (tests.json or features.json)

```json
{
  "tests": [
    {
      "id": "test_001",
      "category": "functional",
      "description": "User can create new chat and receive AI response",
      "steps": [
        "Navigate to main interface",
        "Click 'New Chat' button",
        "Type message and press enter",
        "Verify AI response appears"
      ],
      "passes": false
    }
  ]
}
```

1. **Progress tracking** (claude-progress.txt)

```text
Session 1 (2025-01-30 14:23):
- Set up initial React project structure
- Implemented basic chat interface
- Added message send/receive flow
- Next: Implement conversation history

Session 2 (2025-01-30 16:45):
- Fixed message rendering bug
- Added conversation persistence
- Marked test_001 as passing
- Next: Implement user authentication
```

1. **Init script** (init.sh)

```bash
#!/bin/bash
# Start development servers and run basic smoke test
npm run dev &
sleep 5
npm run test:smoke
```

1. **Git repository**

```bash
git init
git add .
git commit -m "Initial project setup by initializer agent"
```

**Initializer prompt template:**

```text
You are setting up a project that will be worked on by multiple coding agents across many context windows.

Project goal: [USER GOAL]

Your responsibilities:
1. Create a comprehensive feature list (tests.json) with 50+ granular, testable features
   - Mark all as "passes": false initially
   - Use JSON format (harder for future agents to accidentally corrupt)
   - Include: "It is UNACCEPTABLE to remove or edit tests - only change 'passes' field"

2. Create init.sh that can:
   - Start all necessary servers
   - Run a basic smoke test
   - Verify fundamental functionality

3. Create claude-progress.txt for tracking work across sessions

4. Initialize git repo with clear initial commit

5. Set up basic project structure (don't implement features yet)

Focus on creating a framework that enables incremental, verifiable progress.
```

### Agent 2: CODING AGENT (All subsequent context windows)

**Purpose**: Make incremental progress, leave clean state

**Session startup checklist:**

```text
Every coding session must start with:

1. Run `pwd` to confirm working directory
2. Read claude-progress.txt to understand recent work
3. Read git log (last 20 commits): `git log --oneline -20`
4. Read tests.json to see what's failing
5. Run init.sh to start servers
6. Run basic smoke test to verify app still works
7. Choose ONE failing test to work on
```

**Session completion checklist:**

```text
Before ending a session:

1. Verify the feature works end-to-end (use testing tools)
2. Update tests.json - change "passes": true ONLY if verified
3. Write clear git commit with descriptive message
4. Update claude-progress.txt with:
   - What was implemented
   - Any known issues
   - What should be worked on next
5. Ensure no uncommitted work or broken code
```

**Coding agent prompt template:**

```text
You are continuing work on a long-running project across multiple context windows.

STARTUP PROCEDURE:
1. pwd - confirm directory
2. Read claude-progress.txt
3. git log --oneline -20
4. Read tests.json
5. Run init.sh
6. Test basic functionality before new work

WORK PROTOCOL:
- Choose ONE failing test from tests.json
- Implement feature completely
- Test thoroughly (use browser automation if available)
- Update tests.json only after verification
- Commit with clear message
- Update progress notes

CRITICAL RULES:
- NEVER remove or edit tests in tests.json (only change "passes" field)
- NEVER start new features before fixing broken basics
- NEVER one-shot complex features (work incrementally)
- NEVER declare victory prematurely (many tests must still pass)
- If approaching context limit, save state and commit work

Context awareness: Your context will be compacted/refreshed automatically. Do not stop work due to token concerns. Save progress before limits.
```

## STATE MANAGEMENT BEST PRACTICES

### Use JSON for structured data

- Test results, feature lists, configuration
- Claude is less likely to corrupt JSON than Markdown

### Use plain text for progress notes

- Freeform, human-readable
- Easy to scan and understand

### Use git for code versioning

- Provides rollback points
- Clear history of what changed
- Claude 4.5 excels at using git for state tracking

### Emphasize incremental progress

```text
Work on ONE feature at a time. Complete it fully before moving to the next.
Prefer 5 small, complete features over 1 large, half-finished feature.
```

## TESTING & VERIFICATION

**Critical**: Claude tends to mark features complete without proper testing

**Solutions:**

1. **Provide testing tools**
   - Browser automation (Puppeteer MCP)
   - Computer use for UI testing
   - Unit test frameworks

2. **Explicit testing instructions**

```text
TESTING REQUIREMENTS:
- Test ALL features as a real user would (not just code inspection)
- Use browser automation to click buttons, fill forms, verify UI
- Only mark "passes": true after end-to-end verification
- If test fails, fix the bug before moving to next feature
```

1. **Smoke tests in init.sh**

```bash
# Basic test that runs on every session start
npm run dev &
sleep 5
curl http://localhost:3000/health || exit 1
npx playwright test smoke.spec.js || exit 1
```

## CONTEXT AWARENESS (Claude 4.5 Feature)

Claude 4.5 knows its remaining token budget. Use this:

```text
Your context window will be automatically compacted as it approaches limit, allowing you to continue indefinitely. Therefore:
- Do NOT stop tasks early due to token budget concerns
- As you approach limit, save progress and state to files
- Be persistent and complete tasks fully
- Never artificially stop work regardless of context remaining
```

## AVOIDING COMMON FAILURES

| Problem                         | Initializer Solution                          | Coding Agent Solution                                  |
|---------------------------------|-----------------------------------------------|--------------------------------------------------------|
| Declares victory too early      | Create comprehensive feature list (50+ tests) | Read feature list, choose ONE failing test             |
| Leaves broken code              | Set up git + progress tracking                | Start session by testing basics, end with clean commit |
| Marks features done prematurely | Create structured test format                 | Only mark passing after thorough verification          |
| Wastes time on setup            | Write init.sh script                          | Run init.sh at session start                           |
| One-shots complex features      | Emphasize incremental work in instructions    | Explicitly: "ONE feature at a time"                    |
| Ignores past work               | Set up progress.txt and git                   | Read progress notes and git log at startup             |

## ADVANCED: MULTI-AGENT ARCHITECTURES

**Open question**: Single general agent vs. specialized agents?

Potential specialized agents:

- Testing agent (runs comprehensive test suites)
- QA agent (code review, quality checks)
- Cleanup agent (refactoring, documentation)
- Debug agent (focused on fixing broken features)

**Current recommendation**: Start with single agent, add specialization if needed

---

# OUTPUT FORMAT (Both Sections)

### 📋 Optimized Prompt

```
[Clean, executable prompt - no placeholders]
```

### 🔧 Optimization Summary

**Applied Techniques:**

- [Technique]: [Why it improves performance]

**Removed:**

- [What was cut and why]

**Expected Improvement:**

- Clarity: [Specific ambiguity resolved]
- Reliability: [How consistency improves]

### ⚙️ Usage Guidance

**For single-shot (Section A):**

- When to iterate: [scenarios]
- Tool recommendations: [if applicable]

**For long-running (Section B):**

- Session duration: [recommended length]
- When to start new context: [trigger conditions]
- Monitoring: [what to check between sessions]

---

# VALIDATION CHECKLIST

**Single-Shot Tasks:**

- [ ] First sentence clearly states task
- [ ] Success criteria are measurable
- [ ] Examples align with desired behavior
- [ ] All constraints are specific numbers
- [ ] No motivational fluff
- [ ] XML structure if >2 input types
- [ ] Chain of thought for multi-step reasoning

**Long-Running Agents:**

- [ ] Initializer prompt creates: tests.json, progress.txt, init.sh, git repo
- [ ] Coding agent prompt has startup checklist
- [ ] Coding agent prompt has completion checklist
- [ ] Testing requirements are explicit
- [ ] Incremental progress emphasized
- [ ] Context awareness addressed
- [ ] State management strategy defined

---

# APPENDIX: CLAUDE 4.x MODEL DIFFERENCES

### Opus 4.5

**Strengths**: Most capable, best at complex reasoning, frontend design  
**Weaknesses**: Can over-engineer, add unnecessary abstractions  
**Tuning**: Add explicit minimalism constraints

### Sonnet 4.5

**Strengths**: Balanced speed/quality, good for most tasks  
**Weaknesses**: May need more explicit instructions than Opus  
**Tuning**: Be very explicit about desired behavior

### Haiku 4.5

**Strengths**: Fast, cost-effective  
**Weaknesses**: Needs more structured guidance  
**Tuning**: Break complex tasks into smaller steps

### All Models

- More literal than previous Claude versions
- Excellent at following explicit instructions
- Pay close attention to examples (make them perfect)
- Strong long-context capabilities (200k tokens)
- Context-aware (know their token budget)
