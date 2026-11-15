# Copy pstack's formal-verification and correction logic instead of depending on the plugin

run-spec adopts four practices from Lauren Tan's pstack: the TLA+ formal-verification procedure, the `statechart` renderer, the procedure that keeps both in sync with the code, and the `/correct` hierarchy. We copy the logic we use into this kit under its MIT licence, with a notice naming `cursor/plugins@bf0c7cd8`, and do not require the pstack plugin. A plugin dependency would tie run-spec to a third-party release cadence and to Cursor-first tool names that Claude Code maps only partly. The copy must be kept in step with upstream by hand.

## Considered Options

- **Install pstack and call its skills.** Rejected for the reasons above. In Claude Code the `Skill` tool refuses most pstack skills, so they have to be read by path.
- **Write the TLA+ by hand, without `statechart`.** Rejected. It loses the owner-readable chart and the shortest-path report of each broken rule.

## Consequences

- The `statechart` skill is copied verbatim, test corpus included, into `ai/skills/run-spec-dev/formal/statechart/`. That folder sits outside the installed run-spec folder, so `install.sh` never copies it. The copy is committed by hand, outside any `/run-spec` run. Otherwise the hygiene gate would strip its upstream comments, and every review would read about 4 MB of third-party code.
- The procedures adapted from pstack (formal checks, `/correct`) are written by the run that needs them, and are not verbatim.
- The scripts need a Node that runs TypeScript directly, 22.18 or later. The machine default is now Node 26.13.1, the current LTS.
- An upstream fix reaches this kit only when someone copies it again. The notice records the source commit so that drift can be measured.
