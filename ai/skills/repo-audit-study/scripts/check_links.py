"""Check relative links and same-folder heading anchors in a folder of Markdown chapters.

WHAT: For every `*.md` in the folder, resolves each relative link target on disk and, when the target is
      a Markdown file in the same folder, checks the `#anchor` against GitHub-style heading slugs.
WHY:  Chapters cross-link heavily (§ references, nav footers, diagram links); a renamed heading silently
      breaks them.
WHEN: After writing or editing any chapter, and once more before reporting the study as done.
HOW:  python3 -I check_links.py <chapter_folder>     (exit code 1 when any link is broken)
"""
import os
import re
import sys


def slug(heading):
    heading = re.sub(r"[^\w\- ]", "", heading.strip().lower(), flags=re.U)
    return heading.replace(" ", "-")


base = sys.argv[1]
anchors = {}
for name in os.listdir(base):
    if name.endswith(".md"):
        body = re.sub(r"```.*?```", "", open(os.path.join(base, name)).read(), flags=re.S)
        anchors[name] = {slug(h) for h in re.findall(r"^#+\s+(.*)$", body, flags=re.M)}

checked = broken = 0
for name in sorted(anchors):
    for link in re.findall(r"\]\(([^)\s]+)\)", open(os.path.join(base, name)).read()):
        if link.startswith(("http://", "https://", "mailto:")):
            continue
        checked += 1
        path, _, anchor = link.partition("#")
        target = os.path.normpath(os.path.join(base, path)) if path else os.path.join(base, name)
        if not os.path.exists(target):
            print(f"MISSING {name}: {link}")
            broken += 1
        elif anchor and target.endswith(".md") and os.path.dirname(target) == os.path.normpath(base) \
                and anchor not in anchors[os.path.basename(target)]:
            print(f"ANCHOR  {name}: {link}")
            broken += 1
print(f"links checked {checked}, broken {broken}")
sys.exit(1 if broken else 0)
