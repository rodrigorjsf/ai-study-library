# run-spec in this repository

test: for f in ai/skills/run-spec/test_*.py; do python3 -I "$f" || exit 1; done

This repository has no typecheck and no lint. The test line above is the full suite for the run-spec kit: standard-library Python tests, run one file at a time. The vendored `statechart` tests under `ai/skills/run-spec-dev/formal/statechart/scripts/` run separately with `node --test test/*.test.ts` after `npm install --no-package-lock`. They are not part of a run-spec ticket's suite.
