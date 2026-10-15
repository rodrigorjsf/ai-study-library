# Agent Best Practices

**Source:** [cursor.com/blog/agent-best-practices](https://cursor.com/blog/agent-best-practices)

Summary of Cursor's guidance for working effectively with its agent. For full details and UI walkthroughs, read the source at the link above.

## Key Points

- **Agent harness = instructions + tools + model.** Cursor tunes instructions and tools per model based on internal evals.
- **Plan before coding.** Use Plan Mode (`Shift+Tab`) to let the agent research the codebase, ask clarifying questions, and draft a plan before making changes. Revert and replan when things go off track — often faster than patching a flawed implementation.
- **Keep context focused.** Let the agent find files on demand rather than tagging everything manually. Start a fresh conversation when switching tasks or when the agent loses focus.
- **Rules = static context.** Keep `.cursor/rules/` files (`.md` or `.mdc`) focused: build commands, project-specific patterns, pointers to canonical examples. Add rules only when the agent repeats the same mistake.
- **Skills = dynamic workflows.** Defined in `SKILL.md` files; loaded when the agent deems them relevant. Use for reusable multi-step workflows and domain knowledge that doesn't belong in always-loaded rules.
- **Write specific prompts.** Prefer "Write a test for auth.ts covering the logout edge case, following patterns in `__tests__/`" over "add tests." Specificity reduces correction cycles.
- **Parallel agents via worktrees.** Cursor creates isolated git worktrees for parallel agent tasks; each has its own file state.
- **Review AI output rigorously.** Treat generated code like a PR from a junior developer — it can look right while being subtly wrong.

## More agent workflows

- **Include images.** Paste screenshots or mockups for design-to-code and visual debugging.
- **Review code in-flight and after.** Watch the diff as it generates and click **Stop** to redirect; run a dedicated **Review → Find Issues** pass; use **Bugbot** for automated PR review.
- **Delegate to cloud agents.** Hand background tasks (bug fixes, refactors, docs) to cloud agents — they clone the repo, create a branch, and open a PR. Accessible via cursor.com/agents and the Slack `@Cursor` integration.
- **Debug Mode for tricky bugs.** The agent generates hypotheses, instruments code with logging, collects runtime data during reproduction, then makes a targeted fix.
- **Save plans for the team.** Plan Mode output can be stored under `.cursor/plans/`. Use `@Branch` and `@Past Chats` to orient the agent on existing work.

## Notes

This file intentionally summarizes ideas in original wording rather than reproducing the full post. Refer to the source for exact UI details, step-by-step examples, and current product features.
