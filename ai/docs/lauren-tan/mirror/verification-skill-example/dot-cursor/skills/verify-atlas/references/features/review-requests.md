# Review requests

Per-PR tab: changed files, CI checks, commits, reviews, merge action, and add-comment-to-chat.

## Sub-features

- pr-overview: title, status, branches, reviewers
- pr-files: changed files list with diffs
- ci-checks: check rollup and per-check details
- reviews-commits: review threads and commit list
- merge-action: merge / ready-for-merge button
- comment-to-chat: add a PR comment into the current thread

## How to get to it (user POV)

Open a PR from Changes handoff, a deep link, or the PRs section of a project overview.

## Driving it with control-atlas

Prefer a fixture PR in a disposable repo. Snapshot tabs before clicking Merge.

Comment-to-chat: select text in a diff, choose Add to Chat, assert a mention/chip in the prompt.

## Gotchas

- Merge is destructive. Cancel out during sweeps unless the suite owns the PR.
- CI checks are eventually consistent; wait-settle and then assert on visible rollup text.
