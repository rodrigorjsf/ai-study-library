#!/usr/bin/env python3
"""
WHAT  The coordinator's tool over a gauntlet loop's $HANDOFF: opens a round, checks that a round is
      complete, prints the mechanical half of the trend table and the raw verdicts, and records the
      token usage of each task.
WHY   Every run used to hand-write its own parser over the verdict files, and a field-name bug in
      one of them silently dropped every blocking finding. One script makes the counts, the missing
      verdicts and the malformed files a check.
HOW   trend.py new-round <HANDOFF>                  open round N+1 and print its tag
      trend.py check     <HANDOFF>                  exit 0 only when the latest round has a valid
                                                    verdict for every key, else list what is
                                                    missing or invalid and exit 1
      trend.py rows      <HANDOFF>                  one trend row per round, then every missing or
                                                    invalid verdict; exit 1 when any is invalid
      trend.py raw       <HANDOFF> <N>              every verdict file of round N as written on
                                                    disk; exit 1 when any is invalid
      trend.py usage     <HANDOFF> <N> <task-id> <tokens> <errors>
                                                    record one task's usage against round N
                                                    (a workflow's <usage> subagent_tokens and
                                                    agents_error; an Agent's subagent_tokens and
                                                    0); idempotent per task id; exit 1 on an
                                                    unknown round
LAYOUT <HANDOFF>/state/<tag>-<key>.json  a critic's verdict: {"grade": "PASS|CLOSE|NOT_YET",
                                         "blocking": [...], "polish": [...]}; valid only when grade
                                         is PASS exactly when blocking is empty
       <HANDOFF>/trend/keys.json         JSON list of the keys every round grades, sweep included
       <HANDOFF>/trend/rounds.json       one opaque tag per round, in order: round N is the Nth.
                                         Coordinator-only, outside state/, like usage/
       <HANDOFF>/trend/usage/<tag>.json  written by `usage`
OLDER  A $HANDOFF (or its state/) holding v<N>-<key>.json files and no trend/rounds.json is an older
       loop: rows and raw read it; new-round, check and usage refuse it and exit 1, so its history
       is never overwritten.
EXIT   2 on bad arguments.
"""
import json
import re
import secrets
import sys
from pathlib import Path

GRADES = ("PASS", "CLOSE", "NOT_YET")
LEGACY = re.compile(r"^v(\d+)-(.+)\.json$")


def read_json(f: Path, default):
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else default


def validate(f: Path):
    """Return (verdict, None) or (None, reason)."""
    try:
        v = json.loads(f.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError) as e:
        return None, f"does not parse ({e})"
    if not isinstance(v, dict) or v.get("grade") not in GRADES:
        return None, f"grade is {v.get('grade') if isinstance(v, dict) else type(v).__name__!r}"
    if not isinstance(v.get("blocking"), list):
        return None, "blocking is not a list"
    if (v["grade"] == "PASS") != (len(v["blocking"]) == 0):
        return None, f"grade {v['grade']} with {len(v['blocking'])} blocking"
    return v, None


def legacy_dir(h: Path):
    """The directory holding an older loop's v<N>-<key>.json files, or None."""
    if (h / "trend" / "rounds.json").exists():
        return None
    for d in (h, h / "state"):
        if d.is_dir() and any(LEGACY.match(f.name) for f in d.iterdir()):
            return d
    return None


def is_legacy(h: Path) -> bool:
    return legacy_dir(h) is not None


def layout(h: Path):
    """Return [(N, tag, {key: path})] for every round, rounds with no verdict included."""
    if is_legacy(h):
        found = {}
        for f in legacy_dir(h).iterdir():
            m = LEGACY.match(f.name)
            if m and m.group(2) != "usage":
                found.setdefault(int(m.group(1)), {})[m.group(2)] = f
        return [(n, f"v{n}", found[n]) for n in sorted(found)]
    tags = read_json(h / "trend" / "rounds.json", [])
    state = h / "state"
    return [(n, t, {f.name[len(t) + 1:-5]: f for f in state.glob(f"{t}-*.json")})
            for n, t in enumerate(tags, 1)]


def keys_of(h: Path):
    return None if is_legacy(h) else read_json(h / "trend" / "keys.json", None)


def grade_round(files, keys):
    good, bad = {}, []
    for key, f in sorted(files.items()):
        v, why = validate(f)
        if v is None:
            bad.append(f"INVALID {f.name}: {why}")
        else:
            good[key] = v
    missing = [k for k in (keys or []) if k not in files]
    return good, bad, missing


def usage_total(h: Path, tag: str):
    tasks = read_json(h / "trend" / "usage" / f"{tag}.json", None)
    if not tasks:
        return None
    return sum(t["tokens"] for t in tasks.values()), sum(t["errors"] for t in tasks.values())


def refuse_legacy(h: Path, cmd: str) -> bool:
    if is_legacy(h):
        print(f"{cmd}: {h} holds an older loop's v<N>-<key>.json state; start the new loop in a new $HANDOFF")
        return True
    return False


def cmd_rows(h: Path) -> int:
    keys = keys_of(h)
    problems = []
    print("| Round | PASS | Blocking | Died | Tokens | Rejected (reason in handoff) | Self-caused |")
    print("|---|---|---|---|---|---|---|")
    for n, tag, files in layout(h):
        good, bad, missing = grade_round(files, keys)
        total = len(keys) if keys else len(files)
        passed = sum(1 for v in good.values() if v["grade"] == "PASS")
        blocking = sum(len(v["blocking"]) for v in good.values())
        u = usage_total(h, tag)
        tokens, died = (f"{u[0] / 1e6:.1f}M", str(u[1])) if u else ("?", "?")
        print(f"| {n} | {passed}/{total} | {blocking} | {died} | {tokens} | | |")
        problems += [f"round {n}: {b}" for b in bad]
        if missing:
            problems.append(f"round {n}: no verdict for {', '.join(missing)}")
    for p in problems:
        print(p)
    return 1 if any("INVALID" in p for p in problems) else 0


def cmd_check(h: Path) -> int:
    if refuse_legacy(h, "check"):
        return 1
    keys, rounds = keys_of(h), layout(h)
    if keys is None or not rounds:
        print("check: needs trend/keys.json and a round opened with new-round")
        return 1
    n, tag, files = rounds[-1]
    good, bad, missing = grade_round(files, keys)
    for b in bad:
        print(f"round {n}: {b}")
    if missing:
        print(f"round {n}: no verdict for {', '.join(missing)}")
    if bad or missing:
        return 1
    print(f"round {n} ({tag}): {len(good)} valid verdicts, none missing")
    return 0


def cmd_raw(h: Path, n: int) -> int:
    for m, tag, files in layout(h):
        if m != n:
            continue
        bad = 0
        for key, f in sorted(files.items()):
            _, why = validate(f)
            bad += why is not None
            print(f"== {f.name}" + (f"  (INVALID: {why})" if why else ""))
            print(f.read_text(encoding="utf-8", errors="replace").rstrip())
        return 1 if bad else 0
    print(f"raw: no round {n}")
    return 1


def cmd_new_round(h: Path) -> int:
    if refuse_legacy(h, "new-round"):
        return 1
    (h / "trend").mkdir(parents=True, exist_ok=True)
    (h / "state").mkdir(parents=True, exist_ok=True)
    f = h / "trend" / "rounds.json"
    tags = read_json(f, [])
    tag = "g" + secrets.token_hex(3)
    tags.append(tag)
    f.write_text(json.dumps(tags) + "\n", encoding="utf-8")
    print(f"round {len(tags)}: tag {tag}")
    return 0


def cmd_usage(h: Path, n: int, task: str, tokens: int, errors: int) -> int:
    if refuse_legacy(h, "usage"):
        return 1
    rounds = layout(h)
    if not 1 <= n <= len(rounds):
        print(f"usage: no round {n} in trend/rounds.json")
        return 1
    tag = rounds[n - 1][1]
    d = h / "trend" / "usage"
    d.mkdir(parents=True, exist_ok=True)
    tasks = read_json(d / f"{tag}.json", {})
    tasks[task] = {"tokens": tokens, "errors": errors}
    (d / f"{tag}.json").write_text(json.dumps(tasks, indent=2) + "\n", encoding="utf-8")
    total = usage_total(h, tag)
    print(f"round {n}: {len(tasks)} task(s), {total[0]} tokens, {total[1]} agents errored")
    return 0


def main(argv) -> int:
    try:
        cmd, h = argv[1], Path(argv[2])
        if not h.is_dir():
            raise ValueError(f"{h} is not a directory")
        if cmd == "rows" and len(argv) == 3:
            return cmd_rows(h)
        if cmd == "check" and len(argv) == 3:
            return cmd_check(h)
        if cmd == "new-round" and len(argv) == 3:
            return cmd_new_round(h)
        if cmd == "raw" and len(argv) == 4:
            return cmd_raw(h, int(argv[3]))
        if cmd == "usage" and len(argv) == 7:
            return cmd_usage(h, int(argv[3]), argv[4], int(argv[5]), int(argv[6]))
        raise ValueError("unknown command or wrong number of arguments")
    except (IndexError, ValueError) as e:
        print(f"trend.py: {e}\n{__doc__}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
