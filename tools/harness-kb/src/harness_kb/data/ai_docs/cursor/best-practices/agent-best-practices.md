# Agent Best Practices

**Source:** [cursor.com/blog/agent-best-practices](https://cursor.com/blog/agent-best-practices)

Summary of Cursor's guidance for working effectively with its agent. For full details and UI walkthroughs, read the source at the link above.

## Key Points

- **Agent harness = instructions + tools + model.** Cursor tunes instructions and tools per model based on internal evals.
- **Plan before coding.** Use Plan Mode (`Shift+Tab`) to let the agent research the codebase, ask clarifying questions, and draft a plan before making changes. Revert and replan when things go off track — often faster than patching a flawed implementation.
- **Keep context focused.** Let the agent find files on demand rather than tagging everything manually. Start a fresh conversation when switching tasks or when the agent loses focus.
- **Rules = static context.** Keep `.cursor/rules/*.mdc` files focused: build commands, project-specific patterns, pointers to canonical examples. Add rules only when the agent repeats the same mistake.
- **Skills = dynamic workflows.** Defined in `SKILL.md` files; loaded when the agent deems them relevant. Use for reusable multi-step workflows and domain knowledge that doesn't belong in always-loaded rules.
- **Write specific prompts.** Prefer "Write a test for auth.ts covering the logout edge case, following patterns in `__tests__/`" over "add tests." Specificity reduces correction cycles.
- **Parallel agents via worktrees.** Cursor creates isolated git worktrees for parallel agent tasks; each has its own file state.
- **Review AI output rigorously.** Treat generated code like a PR from a junior developer — it can look right while being subtly wrong.

## Notes

This file intentionally summarizes ideas in original wording rather than reproducing the full post. Refer to the source for exact UI details, step-by-step examples, and current product features.
