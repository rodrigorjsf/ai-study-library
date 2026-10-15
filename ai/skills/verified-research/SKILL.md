---
name: verified-research
description: Research a topic from primary sources and keep only claims whose verbatim quotes are confirmed in saved copies of the sources. Use when a report needs a literature or state-of-the-art section, when vendor or API facts must be cited, or when a deep-research skill is unavailable.
---

# Verified Research

Produces a **findings file**: claims grouped by topic, each with an `[n]` citation, and a numbered
bibliography where every entry carries the URL, the date fetched, and a verbatim **quote** that is present in a
saved raw copy of the source. A claim whose quote cannot be found in the saved source is dropped.

## Steps

### 1. Frame

Write the topics as questions, and next to each the kind of primary source that can answer it: papers
(arXiv abstract plus full text), official vendor documentation, official repositories, standards bodies.
Secondary blogs are leads to a primary source, never the citation.

Done when every topic names at least one primary-source kind.

### 2. Fetch and save

For each source, save the raw text before reading it:

```bash
mkdir -p <scratch>/raw
curl -sL -A "Mozilla/5.0" -o <scratch>/raw/<short-name>.html "<url>"
```

Prefer machine-readable forms: the `.md` suffix of documentation sites that serve one, `raw.githubusercontent.com`
for repository files, and the full-text page of a paper (ar5iv) next to its abstract. Give every saved file a
distinct name; two sources saved under one name silently overwrite each other.

Done when every source you intend to cite has a file in `raw/`.

### 3. Extract

Write the findings file. Every claim gets `[n]`; every bibliography entry is one line:

```text
12. Author / org. *Title*. Date. https://url — "verbatim quote one"; "verbatim quote two"
```

Copy quotes character for character from the saved file. Mark your own reasoning *(inference)*. Report
vendor benchmark numbers as self-reported. List what you could not confirm in a "Dropped" section.

Done when every claim has a citation and every citation has at least one quote.

### 4. Verify

```bash
python3 -I scripts/verify_quotes.py <findings.md> <scratch>/raw --heading "## Bibliography"
```

For each miss: fix a paraphrase into the real wording, fetch an unsaved source, or confirm by hand with
`grep -F` the cases the normaliser cannot undo (LaTeX markup, quotes with an ellipsis) and note it next to
the entry. Remove the claim when none of these works.

Done when the script reports zero misses, or every remaining miss has a recorded manual confirmation.

When the research was delegated to a subagent, run this step again in the main thread before any quote is
cited in a durable document: the subagent's "verified" is not evidence.

### 5. Map

Close the findings with a short section mapping the literature onto the subject of the report (for example
each tool's design choices against the criteria the literature sets), keeping inferences labelled.
