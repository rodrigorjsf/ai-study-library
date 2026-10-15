"""Check every verbatim quote of a findings file against the raw copies of its sources.

WHAT: Reads the bibliography section of a findings file, extracts every double-quoted string of 8+ chars
      on a numbered entry line ("12. ... — "quote"; "quote""), normalises HTML tags, entities, curly
      quotes, dashes, backticks and whitespace on both sides, and reports each quote found in no raw file.
WHY:  A subagent that says "verified" is not evidence. The main thread re-runs this over the saved
      sources, so a quote is labelled verified only when it is actually in the downloaded text.
WHEN: After a research pass, before any quote is cited in a durable report.
HOW:  python3 -I verify_quotes.py <findings.md> <raw_dir> [--heading "## Bibliography"]
      Exit code 1 when any quote is missing. A miss is either a paraphrase (fix or drop the quote),
      a source that was never saved (fetch it into raw_dir and re-run), or markup the normaliser does
      not undo (LaTeX, elisions with "…"): confirm those by hand with grep and say so in the report.
"""
import argparse
import html
import os
import re
import sys


def norm(text):
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'),
                 ("–", "-"), ("—", "-"), ("`", ""), ("*", ""), ("--", "-")):
        text = text.replace(a, b)
    return re.sub(r"\s+", " ", text).lower().strip()


parser = argparse.ArgumentParser()
parser.add_argument("findings")
parser.add_argument("raw_dir")
parser.add_argument("--heading", default="## Bibliography")
args = parser.parse_args()

corpus = {f: norm(open(os.path.join(args.raw_dir, f), errors="ignore").read())
          for f in os.listdir(args.raw_dir) if os.path.isfile(os.path.join(args.raw_dir, f))}
text = open(args.findings).read()
if args.heading not in text:
    sys.exit(f"heading {args.heading!r} not found in {args.findings}")
bibliography = text.split(args.heading, 1)[1]

matched = missing = 0
for line in bibliography.splitlines():
    entry = re.match(r"\s*(\d+)\. ", line)
    if not entry:
        continue
    for quote in re.findall(r'"([^"]{8,})"', line):
        needle = norm(quote).rstrip(".")
        if any(needle in body for body in corpus.values()):
            matched += 1
        else:
            missing += 1
            print(f"MISS [{entry.group(1)}] {quote[:100]}")
print(f"matched {matched}, missing {missing}")
sys.exit(1 if missing else 0)
