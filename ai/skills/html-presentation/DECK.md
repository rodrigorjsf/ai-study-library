# Deck layout (direct HTML)

The same frame the canvas exporter produces, so a hand-written deck and an exported canvas look and behave
alike: fixed 1600 × 1000 slides, scaled down to the viewport width, with an explicit page background in light
and dark mode.

```html
<!doctype html>
<html lang="<study language, e.g. pt-BR>">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title><Deck name, two to four words></title>
<!-- Design tokens: from DESIGN.md (quote the source section) or the system you committed to. -->
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=<Display>:wght@700;800&family=<Body>:wght@400;600&display=swap">
<style>
:root{--ground:#DDE2E8;--ink:#10151C;--slide:#F3F5F7;--accent-a:#1F4FD1;--accent-b:#B9480F}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--ground:#0B0F14;--ink:#E6EAF0}}
:root[data-theme="dark"]{--ground:#0B0F14;--ink:#E6EAF0}
html,body{margin:0;background:var(--ground);color:var(--ink)}
.deck{display:flex;flex-direction:column;align-items:center;gap:24px;padding:24px 16px}
.wrap{overflow:hidden}
.slide{width:1600px;height:1000px;transform-origin:top left;background:var(--slide);color:#10151C;
       position:relative;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.18)}
</style>
</head>
<body>
<main class="deck">
  <div class="wrap"><section class="slide" aria-label="01 · Cover">…</section></div>
  <!-- one .wrap > .slide per slide -->
</main>
<script>
function fit(){var w=Math.min(1,(document.documentElement.clientWidth-32)/1600);
document.querySelectorAll('.wrap').forEach(function(x){x.style.width=(1600*w)+'px';x.style.height=(1000*w)+'px';
x.firstElementChild.style.transform='scale('+w+')';});}
window.addEventListener('resize',fit);fit();
</script>
</body>
</html>
```

## Inside a slide

- Pad 56–88 px; lay sibling groups out with flex or grid and `gap`.
- One headline (40–56 px), one mono eyebrow line with the slide number and its source chapter.
- Comparisons: a grid table with a status pill per cell whose **word** (OK / MÉDIO / ALTO, or the study
  language's equivalents) carries the meaning, colour only reinforcing it.
- Diagrams: a `position: relative` host with absolutely positioned boxes and one small `<svg>` per straight
  arrow segment; keep boxes on a grid with gaps of 48 px or more and keep every arrow off the boxes it does
  not connect.
- Scores: bars as plain `div`s whose width is proportional to the score (score ÷ max × track width).
