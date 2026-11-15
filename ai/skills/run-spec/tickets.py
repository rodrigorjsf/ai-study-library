#!/usr/bin/env python3
"""Ticket-state oracle for the run-spec skill.

Reads only ticket metadata (ids, titles, blocking edges, state) from the
spec's tracker plus the work branch's `Ticket:` commit trailers and
failure records, and prints one JSON object. The orchestrator never reads
ticket bodies, code, or handoffs itself; it asks this script.

A ticket is done when a commit carrying its `Ticket:` trailer reaches the work
branch and is not on the default branch, or when the tracker already marks it
closed. The trailer alone counts: no other commit marks a ticket done. Trailers
already on the default branch belong to merged runs, whose tickets the tracker
records (`Closes #N`, or the local `Status: resolved`); local ids restart at 01
in every spec, so an earlier spec's `Ticket: 01` must not mark this spec's 01.
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
import subprocess
import sys

MAX_ATTEMPTS = 2


def sh(*cmd, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(f"command failed: {' '.join(cmd)}\n{r.stderr.strip()}")
    return r.stdout if r.returncode == 0 else ""


def kebab(s, n=40):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:n].strip("-")


def section(body, heading):
    m = re.search(rf"^##\s*{heading}\s*$(.*?)(?=^##\s|\Z)", body, re.M | re.S | re.I)
    return m.group(1) if m else ""


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
        m = re.search(r"Blocked by:\**\s*(.*)", text)
        blocked = m.group(1) if m else ""
        tickets.append({"id": num, "ref": str(f.resolve().relative_to(top)), "title": title, "_blocked": blocked,
                        "_status": (re.search(r"Status:\**\s*(\S+)", text) or [None, ""])[1]})
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
        text = section(i["body"], "Blocked by") + "\n" + " ".join(re.findall(r"^Blocked by:.*$", i["body"], re.M))
        blockers |= set(re.findall(r"#(\d+)", text))
        tickets.append({"id": f"#{m}", "ref": f"#{m}", "title": i["title"],
                        "blockers": sorted(f"#{b}" for b in blockers if b != m),
                        "_closed": i["state"] == "CLOSED",
                        "in_scope": i["state"] == "CLOSED" or "ready-for-agent" in {l["name"] for l in i["labels"]}})
    # blockers outside this spec gate the ticket until they are closed on the tracker
    own = {t["id"] for t in tickets}
    for b in {b for t in tickets for b in t["blockers"]} - own:
        state = sh("gh", "issue", "view", b.lstrip("#"), "--json", "state", "--jq", ".state", check=False).strip()
        tickets.append({"id": b, "ref": b, "title": "(outside this spec)", "blockers": [],
                        "_closed": state == "CLOSED", "in_scope": False})
    return f"{n}-{kebab(title)}", f"#{n}", tickets


def default_refs():
    head = sh("git", "symbolic-ref", "-q", "--short", "refs/remotes/origin/HEAD", check=False).strip()
    for name in ([head.removeprefix("origin/")] if head else []) + ["main", "master"]:
        refs = [r for r in (f"refs/heads/{name}", f"refs/remotes/origin/{name}")
                if sh("git", "rev-parse", "-q", "--verify", f"{r}^{{commit}}", check=False).strip()]
        if refs:
            return refs
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tracker", required=True, choices=["github", "local"])
    ap.add_argument("--spec", required=True)
    ap.add_argument("--work-branch", required=True)
    ap.add_argument("--failures-dir", required=True)
    a = ap.parse_args()

    slug, spec, tickets = (github_tickets if a.tracker == "github" else local_tickets)(a.spec)
    refs = default_refs()
    trailers = set(sh("git", "log", a.work_branch, *(["--not", *refs] if refs else []),
                      "--format=%(trailers:key=Ticket,valueonly)", check=False).split())
    fdir = pathlib.Path(a.failures_dir)
    by_id = {t["id"]: t for t in tickets}
    for t in tickets:
        closed = t.pop("_closed")
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
