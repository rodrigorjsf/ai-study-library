"""Export the claude.ai Design canvas boards (.dc.html) into one standalone HTML deck.

WHAT: Reads `source/canvas.json` and every board listed in its `order`, strips the Design runtime
      (`support.js`, `<x-dc>`, `<helmet>`, the `data-dc-script` block), substitutes each board's
      `{{prop}}` holes with the `default` values declared in its `data-props`, and writes
      `index.html`: every board as a fixed 1600x1000 slide, scaled to the viewport.
WHY:  A claude.ai Design canvas needs the claude.ai runtime and is private until shared; this keeps a
      self-contained copy versioned in the repository.
WHEN: After any board is changed on the canvas. Re-read the boards from the artifact into `source/`
      first, then run this script.
HOW:  python3 -I export_canvas.py <deck_dir>
      <deck_dir> holds `source/` (canvas.json + *.dc.html); index.html is written into <deck_dir>.
      Without an argument the script uses its own directory. No dependencies.
"""
import html
import json
import os
import re
import sys

HERE = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "source")


def board_parts(text):
    props = {}
    m = re.search(r"data-props='([^']*)'", text)
    if m:
        for key, spec in json.loads(html.unescape(m.group(1))).items():
            if isinstance(spec, dict) and "default" in spec:
                props[key] = spec["default"]
    helmet = re.search(r"<helmet>(.*?)</helmet>", text, re.S)
    head = helmet.group(1) if helmet else ""
    body = re.search(r"<x-dc>(.*?)</x-dc>", text, re.S).group(1)
    body = re.sub(r"<helmet>.*?</helmet>", "", body, flags=re.S)
    body = re.sub(r"\{\{\s*([\w.]+)\s*\}\}", lambda k: str(props.get(k.group(1), "")), body)
    title = re.search(r"<title>(.*?)</title>", text, re.S)
    return head, body, title.group(1) if title else ""


def main():
    index = json.load(open(os.path.join(SRC, "canvas.json")))
    heads, slides = [], []
    for name in index["order"]:
        head, body, title = board_parts(open(os.path.join(SRC, name), encoding="utf-8").read())
        for line in re.findall(r"<link[^>]+>", head):
            if line not in heads:
                heads.append(line)
        board = index["boards"][name]
        slides.append(
            f'<section class="slide" aria-label="{html.escape(board.get("title", title))}">'
            f'<div class="board" style="width:{board["w"]}px;height:{board["h"]}px">{body}</div></section>'
        )
    out = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(index["title"])}</title>
{chr(10).join(heads)}
<style>
:root{{--ground:#DDE2E8;--ink:#10151C}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--ground:#0B0F14;--ink:#E6EAF0}}}}
:root[data-theme="dark"]{{--ground:#0B0F14;--ink:#E6EAF0}}
html,body{{margin:0;background:var(--ground);color:var(--ink)}}
.deck{{display:flex;flex-direction:column;align-items:center;gap:24px;padding:24px 16px}}
.slide{{width:1600px;height:1000px;transform-origin:top left;box-shadow:0 2px 12px rgba(0,0,0,.18)}}
.board{{position:relative;overflow:hidden}}
.wrap{{overflow:hidden}}
</style>
</head>
<body>
<main class="deck">
{chr(10).join(f'<div class="wrap">{s}</div>' for s in slides)}
</main>
<script>
function fit(){{var w=Math.min(1,(document.documentElement.clientWidth-32)/1600);
document.querySelectorAll('.wrap').forEach(function(x){{x.style.width=(1600*w)+'px';x.style.height=(1000*w)+'px';
x.firstElementChild.style.transform='scale('+w+')';}});}}
window.addEventListener('resize',fit);fit();
</script>
</body>
</html>
"""
    target = os.path.join(HERE, "index.html")
    open(target, "w", encoding="utf-8").write(out)
    print(f"wrote {target} with {len(slides)} boards")


if __name__ == "__main__":
    sys.exit(main())
