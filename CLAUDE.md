## Planning

- ALWAYS when planning or before write a plan, work back and forth with me, starting with your open questions and outline before writing the plan.
- ALWAYS delegate a plan review to the advisor before claiming it is ready for execution.

## Harness coverage

- Cover Cursor IDE beside Claude Code in every study, analysis, plan and diagram in this repository: install path, hook events, how context reaches the agent, MCP, and parity gaps.
- Check each integration against the harness's own hook, plugin and MCP docs (`ai/docs/claude-code/`, `ai/docs/cursor/`), not the tool's description of itself.
- In diagrams, give Cursor and Claude Code separate nodes when their mechanisms differ.

# RTK (Rust Token Killer) - Token-Optimized Commands

@RTK.md

## Applied Learning

When something fails repeatedly, when User has to re-explain, or when a workaround is found for a platform/tool limitation, add a one-line bullet here. Keep each bullet under 15 words. No explanations. Only add things that will save time in future sessions.

- YouTube transcripts may 429 everywhere; try `youtube_transcript_api`, then ask user to paste.
- Blocked transcript: `yt-dlp --write-info-json --ignore-no-formats-error`, `player_client=web_embedded`, still gives description/chapters.
- `uvx` is not on Bash PATH; call `/home/linuxbrew/.linuxbrew/bin/uvx`.
- Mirror vendor docs with `curl` on the `.md` suffix (code.claude.com, platform.claude.com, cursor.com/docs).
- `harness-kb build` bundles `ai/docs/` but needs `graphify-out/manifest.json`, removed from the repo.
- No Chrome in WSL: archify `visual-check` skips; set `ARCHIFY_CHROME` first.
- No osv-scanner installed: query `api.osv.dev/v1/querybatch` with lockfile versions.
- archify `deliver` with `meta.repository` needs `--repo-root <checkout>`.
