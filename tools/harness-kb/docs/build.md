# Building the harness-kb Data Bundle

Maintainer-only documentation. End users do not run anything in this file.

## Prerequisites

- A local checkout of `ai-study-library/` (the source repo).
- Python 3.10+ with `pip` available.
- For graph refresh: Claude Code installed (the `/graphify` slash command).

## Editable install

From `tools/harness-kb/`:

```bash
pip install -e .
```

This puts `harness-kb` on PATH for use in subsequent steps.

## Refresh the graph (only if `ai/docs/` has changed)

From inside Claude Code, with `<source-root>` as your working directory:

```
/graphify update .
```

`harness-kb build` will check `graphify-out/manifest.json` mtime against `ai/docs/` mtimes and abort if any doc is newer than the manifest. If you have a reason to skip the check, pass `--no-staleness-check`.

## Build the bundle

```bash
harness-kb build \
  --source <source-root> \
  --out-dir <repo>/tools/harness-kb/src/harness_kb/data \
  --version 0.1.0
```

The build performs: validate source → check freshness → stage data (ai_docs, graph, wiki) → adapt research doc into `data/guide/harness-engineering-playbook.md` → build BM25 index → write `manifest.json` → post-validate.

## Verify

```bash
cd tools/harness-kb
pytest -v
```

All tests must pass against the new bundle.

## Release Checklist

- [ ] Bump `__version__` in `src/harness_kb/__init__.py`.
- [ ] Bump `version` in `pyproject.toml`.
- [ ] Update `CHANGELOG.md` with the new version's changes and the data SHA.
- [ ] Rebuild data with `harness-kb build --version <new>`.
- [ ] Run `pytest -v` and confirm 100% pass.
- [ ] Tag: `git tag harness-kb-v<new>` (do not push without explicit user approval).

## Out of scope (v0.1.0)

- PyPI publishing (`python -m build && twine upload`).
- CI/CD release workflow.
