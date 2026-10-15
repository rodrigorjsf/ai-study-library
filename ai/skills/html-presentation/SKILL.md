---
name: html-presentation
description: Build a standalone HTML slide deck from a study or report, following the repository's DESIGN.md when it has one. Use when findings must be presented, when a claude.ai Design canvas must be persisted as HTML in the repository, or when chapters need a visual summary.
---

# HTML Presentation

Produces a **deck**: one self-contained `index.html` of fixed-size slides (1600 × 1000 px, scaled to the
viewport), kept in the repository next to the chapters it summarises, with its sources versioned beside it.

## Steps

### 1. Find the design

Look for `DESIGN.md` at the repository root, then in `docs/`, then next to the chapters. When it exists it
is the **design source**: read it whole, and take colours, typefaces, spacing, radii, component shapes and
tone from it, quoting exact values. When it does not exist, commit to one small system and write it in a
comment at the top of the deck: one or two typefaces from Google Fonts, a ground, an ink, and at most two
accents that differ in lightness as well as hue (one per subject being compared).

Done when the deck's colour and type tokens are written down, each traced to `DESIGN.md` or to your stated
system.

### 2. Plan the slides

One slide per idea a decision-maker needs, in this order when the deck summarises a study: cover with the
verdict, concepts, one architecture slide per subject, security, integration, comparison, plan. Every number
on a slide comes from a chapter; note the chapter next to it in the slide's source.

Done when every slide has a title, its source chapter, and the figures it shows.

### 3. Build

Choose the medium:

- **A claude.ai Design canvas is available and the user wants one**: build the boards there (each board a
  fixed 1600 × 1000 artboard), then persist it with step 4.
- **Otherwise**: write the deck directly as one HTML file with one `<section class="slide">` per slide and the
  layout of [`DECK.md`](DECK.md).

Diagrams on slides are built from positioned boxes and short straight arrows, so each part stays editable;
link to the rendered archify diagrams in the study for the full, interactive versions. Use real `<a>`,
`<button>` and table markup; keep text contrast at 4.5:1 or more; label status with words as well as colour.

Done when every planned slide exists and nothing on it is placeholder text.

### 4. Persist a canvas as HTML

Copy the canvas source files (`canvas.json` and every `*.dc.html` board, read back from the canvas first in
case someone edited it) into `<study>/presentation/source/`, then run:

```bash
python3 -I scripts/export_canvas.py <study>/presentation   # the folder that holds source/
```

The script strips the Design runtime, fills each board's `{{prop}}` holes with their declared defaults, and
writes `index.html` with every board in canvas order. Check that the output contains no `{{`, `x-dc` or
`support.js`.

Done when `index.html` exists, the check above is empty, and the study hub links the deck and its sources.

### 5. Hand over

Tell the user where the deck lives, that a canvas link is private until shared, and how to regenerate the
HTML after editing the canvas.
