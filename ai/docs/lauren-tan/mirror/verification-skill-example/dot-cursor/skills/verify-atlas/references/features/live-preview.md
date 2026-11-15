# Live preview

Live React `*.canvas.tsx` artifact rendered in a webview tab, with preview/source modes and a canvas list.

## Sub-features

- canvas-preview: rendered preview of a canvas artifact
- canvas-source: source mode for the canvas file
- canvas-list: list of canvases in the project

## How to get to it (user POV)

Open a `*.canvas.tsx` from Files or from an agent artifact card. Toggle preview/source in the tab header.

## Driving it with control-atlas

Use a fixture canvas in the sample project. Screenshot preview mode. Toggle source and assert the editor/webview swap.

## Gotchas

- Canvas is gated in some builds. If the tab cannot open, record the gate and skip.
