# File browser

Files app: tree, preview editors, find, symbol navigation, workspace search, and simple viewers.

## Sub-features

- file-tree: browse and open files from the project root.
- preview-editor: read-only or editable preview tab.
- find-in-file: in-tab find.
- workspace-search: project-wide text search.
- symbol-nav: go to definition / references when the language service is available.
- viewers: image, Markdown, and CSV/TSV viewers.

## How to get to it (user POV)

Open the Files app from the app panes or its shortcut. Click a file in the tree. Use find or workspace search from the panel header. Open an image or Markdown file to hit the viewers.

## Driving it with control-atlas

```bash
node .cursor/skills/verify-atlas/control-atlas.mjs press "Meta+Shift+KeyE"   # example Files shortcut; confirm in live build
node .cursor/skills/verify-atlas/control-atlas.mjs snapshot
```

- Prefer snapshot + aria labels over pixel clicks in the tree.
- Workspace search: focus the search box, `type` a rare string from a fixture file, assert a result row, open it, assert the preview lands on the match.
- Image / Markdown viewers: open a known fixture path via the tree or `add-context`, then screenshot.

## Gotchas

- Language-service symbol nav needs a ready language server. If it is cold, wait or skip with reason.
- Large repos paginate the tree; do not assert a deep path is visible without expanding parents.
