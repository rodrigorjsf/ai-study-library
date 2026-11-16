#!/usr/bin/env python3
"""Ticket-state oracle for the run-spec skill.

Reads only ticket metadata (ids, titles, blocking edges, state) from the
spec's tracker plus the work branch's `Ticket:` commit trailers and
failure records, and prints one JSON object. The orchestrator never reads
ticket bodies, code, or handoffs itself; it asks this script.

A ticket is done when a commit carrying its `Ticket:` trailer reaches the work
branch and is not on the default branch, or when the tracker already marks it
closed. The trailer alone counts: no other commit marks a ticket done. Local ids
restart at 01 in every spec, so an earlier spec's `Ticket: 01` must not mark
this spec's 01. Two rules keep them apart. A `Ticket:` trailer counts only on a
commit whose `Spec:` trailer is absent (commits older than that trailer) or
equals this spec's slug, the `slug` this script prints; this covers a work
branch stacked on an earlier spec's unmerged commits. Trailers already on the
default branch belong to merged runs, whose tickets the tracker records
(`Closes #N`, or the local `Status: resolved`), so they never count.
The default branch is `refs/remotes/origin/HEAD`, else `main`, else `master`.

Usage:
  tickets.py --tracker github|local --spec <#N|path> --work-branch <branch> --failures-dir <dir>

Output keys: slug, spec, tickets[{id, ref, title, blockers, in_scope, done,
attempts, skipped, ready}], ready (ids ready now, in order), remaining (ids
neither done nor skipped). `ready` appears only on in-scope tickets.
"""
import argparse
import json
import pathlib
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gitcmd import default_refs, run as sh

MAX_ATTEMPTS = 2


def kebab(s, n=40):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:n].strip("-")


def section(body, heading):
    m = re.search(rf"^##\s*{heading}\s*$(.*?)(?=^##\s|\Z)", body, re.M | re.S | re.I)
    return m.group(1) if m else ""


CHECKBOX = re.compile(r"^(\s*)[-*+]\s+\[[ xX]\]\s+(.*\S)\s*$")


def criteria(text):
    found, indent = [], None
    for line in re.split(r"\r?\n", text):
        checkbox = CHECKBOX.match(line)
        if checkbox:
            found.append(checkbox.group(2))
            indent = len(checkbox.group(1))
        elif line.strip() and indent is not None and len(line) - len(line.lstrip()) > indent:
            found[-1] += " " + line.strip()
        elif line.strip():
            indent = None
    return found


def local_tickets(spec):
    p = pathlib.Path(spec)
    root = p.parent if p.suffix == ".md" else p
    files = sorted(f for f in (root / "issues").glob("*.md") if f.name[0].isdigit())
    if not files:
        sys.exit(f"no tickets under {root / 'issues'}")
    top = pathlib.Path(sh("git", "rev-parse", "--show-toplevel").strip())
    tickets = []
    for f in files:
        text = f.read_text()
        num = re.match(r"(\d+)", f.name).group(1)
        title = re.sub(r"^#\s*\d+\s*[—:-]\s*", "", text.splitlines()[0]).strip()
        m = re.search(r"^\**Blocked by:\**\s*(.*)", text, re.M)
        blocked = m.group(1) if m else ""
        tickets.append({"id": num, "ref": str(f.resolve().relative_to(top)), "title": title, "_blocked": blocked,
                        "criteria": criteria(text),
                        "_status": (re.search(r"^\**Status:\**\s*(\S+)", text, re.M) or [None, ""])[1]})
    ids = {t["id"].lstrip("0"): t["id"] for t in tickets}
    for t in tickets:
        b = t.pop("_blocked")
        found = set()
        if not re.match(r"\s*none", b, re.I):
            # an unknown number stays a blocker: it can never be satisfied, so the ticket gets stuck, not run early
            found |= {ids.get(n.lstrip("0"), n) for n in re.findall(r"\b(\d{1,3})\b", b)}
            found |= {o["id"] for o in tickets if o is not t and len(o["title"]) >= 4
                      and re.search(rf"\b{re.escape(o['title'].lower())}\b", b.lower())}
        t["blockers"] = sorted(found - {t["id"]})
        status = t.pop("_status").lower()
        t["_closed"] = status in ("resolved", "done", "closed")
        t["in_scope"] = t["_closed"] or status == "ready-for-agent"
    return root.name, str((root / "spec.md").resolve().relative_to(top)), tickets


def github_tickets(spec):
    n = spec.lstrip("#")
    repo = sh("gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner").strip()
    title = sh("gh", "issue", "view", n, "--json", "title", "--jq", ".title").strip()
    nums = set(sh("gh", "api", f"repos/{repo}/issues/{n}/sub_issues", "--paginate",
                  "--jq", ".[].number", check=False).split())
    found = json.loads(sh("gh", "issue", "list", "--state", "all", "--limit", "500",
                          "--search", f'"#{n}" in:body', "--json", "number,body") or "[]")
    # a ticket belongs to the spec only when #N is its PRIMARY parent: the first issue ref of
    # `## Parent`, or a `Part of #N` line. "(includes story 23 of #7)" does not make a ticket of #7.
    def parent(body):
        m = re.search(r"#(\d+)", section(body, "Parent")) or re.search(r"^Part of #(\d+)", body, re.M)
        return m.group(1) if m else None
    nums |= {str(i["number"]) for i in found if parent(i["body"]) == n}
    nums.discard(n)
    if not nums:
        sys.exit(f"no tickets found for spec #{n}: expected sub-issues or a '## Parent' / 'Part of #{n}' reference")
    tickets = []
    for m in sorted(nums, key=int):
        i = json.loads(sh("gh", "issue", "view", m, "--json", "number,title,state,body,labels"))
        blockers = set(sh("gh", "api", f"repos/{repo}/issues/{m}/dependencies/blocked_by",
                          "--jq", ".[].number", check=False).split())
        text = section(i["body"], "Blocked by") + "\n" + " ".join(re.findall(r"^\**Blocked by:.*$", i["body"], re.M))
        blockers |= set(re.findall(r"#(\d+)", text))
        tickets.append({"id": f"#{m}", "ref": f"#{m}", "title": i["title"],
                        "criteria": criteria(section(i["body"], "Acceptance criteria")),
                        "blockers": sorted(f"#{b}" for b in blockers if b != m),
                        "_closed": i["state"] == "CLOSED",
                        "in_scope": i["state"] == "CLOSED" or "ready-for-agent" in {l["name"] for l in i["labels"]}})
    # blockers outside this spec gate the ticket until they are closed on the tracker
    own = {t["id"] for t in tickets}
    for b in {b for t in tickets for b in t["blockers"]} - own:
        state = sh("gh", "issue", "view", b.lstrip("#"), "--json", "state", "--jq", ".state", check=False).strip()
        tickets.append({"id": b, "ref": b, "title": "(outside this spec)", "blockers": [], "criteria": [],
                        "_closed": state == "CLOSED", "in_scope": False})
    return f"{n}-{kebab(title)}", f"#{n}", tickets


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tracker", required=True, choices=["github", "local"])
    ap.add_argument("--spec", required=True)
    ap.add_argument("--work-branch")
    ap.add_argument("--failures-dir")
    ap.add_argument("--criteria", action="store_true",
                    help="print each ticket's id, scope and acceptance criteria, and need no --work-branch or --failures-dir")
    a = ap.parse_args()
    if not a.criteria and (a.work_branch is None or a.failures_dir is None):
        ap.error("--work-branch and --failures-dir are required unless --criteria is given")

    slug, spec, tickets = (github_tickets if a.tracker == "github" else local_tickets)(a.spec)
    if a.criteria:
        print(json.dumps({"slug": slug, "spec": spec,
                          "tickets": [{key: t[key] for key in ("id", "in_scope", "criteria")} for t in tickets]}, indent=1))
        return
    refs = default_refs()
    log = sh("git", "log", a.work_branch, *(["--not", *refs] if refs else []),
             "--format=%x1e%(trailers:only,unfold)", check=False)
    trailers = set()
    for record in log.split("\x1e"):
        pairs = [(k.strip().lower(), v.strip()) for k, _, v in
                 (line.partition(":") for line in record.splitlines() if ":" in line)]
        specs = {v for k, v in pairs if k == "spec"}
        if not specs or slug in specs:
            trailers |= {t for k, v in pairs if k == "ticket" for t in v.split()}
    fdir = pathlib.Path(a.failures_dir)
    by_id = {t["id"]: t for t in tickets}
    for t in tickets:
        closed = t.pop("_closed")
        t.pop("criteria")
        t["done"] = t["id"] in trailers or closed
        t["attempts"] = len(list(fdir.glob(f"{t['id'].lstrip('#')}-attempt*.md"))) if fdir.is_dir() else 0
        t["skipped"] = not t["done"] and t["attempts"] >= MAX_ATTEMPTS
    # out-of-scope tickets (follow-ups, needs-info, ready-for-human…) never run, but still block while open
    run = [t for t in tickets if t["in_scope"]]
    changed = True
    while changed:  # a ticket blocked by a skipped ticket is skipped too
        changed = False
        for t in tickets:
            if not t["done"] and not t["skipped"] and any(by_id.get(b, {}).get("skipped") for b in t["blockers"]):
                t["skipped"] = changed = True
    for t in run:
        # an unknown blocker never counts as done: order and blocking edges are hard constraints
        t["ready"] = not t["done"] and not t["skipped"] and all(by_id.get(b, {"done": False})["done"] for b in t["blockers"])
    print(json.dumps({"slug": slug, "spec": spec, "tickets": tickets,
                      "ready": [t["id"] for t in run if t["ready"]],
                      "remaining": [t["id"] for t in run if not t["done"] and not t["skipped"]]}, indent=1))


if __name__ == "__main__":
    main()
