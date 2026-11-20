#!/usr/bin/env python3
"""Time ledger of Claude Code sessions: where the wall-clock of an agent's work went.

Reads session transcripts (`<session>.jsonl`) and the transcripts of the subagents each one spawned
(`<session>/subagents/**/*.jsonl`), and prints, summed over the sessions given:

  - per agent type: wall time, model time, tool time, and time spent waiting on background work;
  - time per tool, and per kind of shell command (tests, build, typecheck, lint, commit, push...);
  - background commands, from launch to their completion notice, per kind;
  - the slowest single commands.

Standard library only.

  session_ledger.py <project-dir-or-transcript>... [--last N] [--grep REGEX] [--top N]

A project directory is `~/.claude/projects/<slug>/`. `--last N` keeps the N most recently modified
sessions; `--grep` keeps the sessions whose transcript matches the regular expression (for example
the slash command that started the kind of work under study).
"""
import argparse
import collections
import datetime
import glob
import json
import os
import re
import sys

# The first pattern that matches a command names its kind. Order matters: a gate that runs tests is a gate.
KINDS = [
    ("gate", r"\b(pnpm|npm|yarn|bun) (run )?(check|ci|verify)\b|\bmake (check|ci|verify)\b|\bpre-commit run\b|\b(tox|nox)\b"),
    ("deploy", r"\bdeploy\b|\bkubectl (apply|rollout)\b|\bterraform apply\b"),
    ("vcs push", r"\bgit\b.*\bpush\b"),
    ("vcs commit", r"\bgit\b.*\bcommit\b"),
    ("install", r"\b(pnpm|npm|yarn|bun) (install|i|ci|add)\b|\bpip3? install\b|\buv (sync|pip)\b|\bpoetry install\b|\bbundle install\b|\bgo mod (download|tidy)\b|\bcargo fetch\b|\bcomposer install\b|\bdotnet restore\b"),
    ("test", r"\b(vitest|jest|mocha|playwright|pytest|unittest|rspec|phpunit|ctest)\b|\b(pnpm|npm|yarn|bun) (run )?test\b|\b(go|cargo|dotnet|mix|swift|zig) test\b|\b(mvnw?|gradlew?)\b.*\b(test|verify|check)\b|\bmake test\b|\bbazel test\b"),
    ("build", r"\b(pnpm|npm|yarn|bun) (run )?build\b|\b(go|cargo|dotnet|swift|zig|mix) (build|compile)\b|\b(mvnw?|gradlew?)\b.*\b(compile|build|package|assemble)\b|\bmake( all| build)?\s*$|\bdocker (build|compose build)\b|\bbazel build\b|\bcmake --build\b"),
    ("typecheck", r"\btypecheck\b|\btsc\b|\bmypy\b|\bpyright\b|\bcargo check\b|\bgo vet\b|\bflow check\b"),
    ("lint", r"\b(eslint|biome|oxlint|prettier|ruff|flake8|pylint|rubocop|clippy|golangci-lint|ktlint|checkstyle|shellcheck)\b|\b(pnpm|npm|yarn|bun) (run )?lint\b|\bcargo fmt\b|\bgofmt\b"),
    ("wait", r"(^|[;&|]\s*)sleep \d|\buntil\b.*\bdo\b|\bwhile\b.*\bdo\b"),
    ("tracker", r"(^|[;&|]\s*)(gh|glab) "),
    ("vcs", r"(^|[;&|]\s*)git "),
]
IDLE_GAP = 900  # a gap this long between two model turns is not model time: a rate limit, a sleeping machine


def kind_of(command):
    for name, pattern in KINDS:
        if re.search(pattern, command):
            return name
    return "other"


def seconds(stamp):
    return datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp()


def text_of(content):
    if isinstance(content, str):
        return content
    return " ".join(part.get("text") or "" for part in content or [] if isinstance(part, dict))


def read(path):
    """One transcript: its wall time, model time, tool times and waits."""
    out = dict(first=None, last=None, model=0.0, idle=0.0, wait=0.0, tool=collections.Counter(), calls=collections.Counter(),
               shell=collections.Counter(), shell_calls=collections.Counter(), background=collections.defaultdict(list), slow=[])
    uses, pending, previous = {}, {}, None
    with open(path, encoding="utf-8", errors="replace") as lines:
        for line in lines:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if entry.get("type") not in ("user", "assistant") or "timestamp" not in entry:
                continue
            now = seconds(entry["timestamp"])
            out["first"] = out["first"] if out["first"] is not None else now
            out["last"] = now
            content = (entry.get("message") or {}).get("content")
            if entry["type"] == "assistant":
                if previous is not None:
                    gap = now - previous
                    out["model" if gap < IDLE_GAP else "idle"] += gap
                for part in content or []:
                    if isinstance(part, dict) and part.get("type") == "tool_use":
                        uses[part["id"]] = (now, part["name"], part.get("input") or {})
            else:
                is_result = False
                for part in content if isinstance(content, list) else []:
                    if not isinstance(part, dict) or part.get("type") != "tool_result":
                        continue
                    is_result = True
                    use = uses.get(part.get("tool_use_id"))
                    if not use:
                        continue
                    started, name, given = use
                    took = now - started
                    out["tool"][name] += took
                    out["calls"][name] += 1
                    if name != "Bash":
                        continue
                    command = given.get("command", "")
                    launched = re.search(r"background with ID: (\w+)", text_of(part.get("content")))
                    if launched:
                        pending[launched.group(1)] = (started, command)
                        continue
                    kind = kind_of(command)
                    out["shell"][kind] += took
                    out["shell_calls"][kind] += 1
                    if took >= 60:
                        out["slow"].append((took, kind, " ".join(command.split())[:140]))
                if not is_result:
                    said = text_of(content)
                    for done in re.finditer(r"<task-id>(\w+)</task-id>", said):
                        launch = pending.pop(done.group(1), None)
                        if launch:
                            out["background"][kind_of(launch[1])].append(now - launch[0])
                    if previous is not None:
                        # The turn was resumed by something other than a tool result: a background job, another agent, a person.
                        out["wait" if "task-notification" in said or "agent-message" in said else "idle"] += now - previous
            previous = now
    return out


def hours(value):
    return f"{value / 3600:6.1f}h"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--last", type=int)
    parser.add_argument("--grep")
    parser.add_argument("--top", type=int, default=12)
    args = parser.parse_args()

    sessions = []
    for path in args.paths:
        path = os.path.expanduser(path)
        if os.path.isdir(path):
            sessions += sorted(glob.glob(os.path.join(path, "*.jsonl")))
        elif os.path.isfile(path):
            sessions.append(path)
        else:
            sys.exit(f"not a transcript or a project directory: {path}")
    if args.grep:
        wanted = re.compile(args.grep)
        sessions = [path for path in sessions if wanted.search(open(path, encoding="utf-8", errors="replace").read())]
    sessions.sort(key=os.path.getmtime)
    if args.last:
        sessions = sessions[-args.last:]
    if not sessions:
        sys.exit("no session transcript found")

    by_agent = collections.defaultdict(lambda: collections.Counter())
    tool, calls, shell, shell_calls = (collections.Counter() for _ in range(4))
    background, slow = collections.defaultdict(list), []
    for session in sessions:
        transcripts = [("main session", session)]
        for sub in glob.glob(os.path.join(session[: -len(".jsonl")], "subagents", "**", "*.jsonl"), recursive=True):
            try:
                kind = json.load(open(sub[: -len(".jsonl")] + ".meta.json", encoding="utf-8")).get("agentType", "subagent")
            except (OSError, ValueError):
                kind = "subagent"
            transcripts.append((kind, sub))
        for agent, path in transcripts:
            one = read(path)
            if one["first"] is None:
                continue
            row = by_agent[agent]
            row["runs"] += 1
            row["wall"] += one["last"] - one["first"]
            row["model"] += one["model"]
            row["tool"] += sum(one["tool"].values())
            row["wait"] += one["wait"]
            row["idle"] += one["idle"]
            tool.update(one["tool"]); calls.update(one["calls"]); shell.update(one["shell"]); shell_calls.update(one["shell_calls"])
            for kind, runs in one["background"].items():
                background[kind] += runs
            slow += one["slow"]

    print(f"{len(sessions)} sessions, {sum(row['runs'] for row in by_agent.values()) - len(sessions)} subagent runs\n")
    print("BY AGENT          runs      wall     model      tool   waiting  idle/human")
    for agent, row in sorted(by_agent.items(), key=lambda item: -item[1]["wall"]):
        print(f"{agent[:16]:16} {row['runs']:5} {hours(row['wall'])} {hours(row['model'])} {hours(row['tool'])} {hours(row['wait'])} {hours(row['idle'])}")
    print("\n`waiting` is time blocked on background work or another agent; a main session's wall includes the time people took to answer.")
    print("\nTIME PER TOOL (foreground)")
    for name, took in tool.most_common(args.top):
        print(f"  {name[:36]:36} {hours(took)}  calls={calls[name]}")
    print("\nSHELL COMMANDS BY KIND (foreground)")
    for kind, took in shell.most_common():
        print(f"  {kind:12} {hours(took)}  calls={shell_calls[kind]:6}  mean={took / shell_calls[kind]:7.1f}s")
    print("\nBACKGROUND COMMANDS BY KIND (launch to completion notice; an `other` that runs for hours is a watcher, not work)")
    for kind, runs in sorted(background.items(), key=lambda item: -sum(item[1])):
        runs.sort()
        print(f"  {kind:12} {hours(sum(runs))}  runs={len(runs):5}  median={runs[len(runs) // 2]:6.0f}s  p90={runs[int(len(runs) * 0.9)]:6.0f}s")
    print(f"\nSLOWEST FOREGROUND COMMANDS (of {len(slow)} that took a minute or more)")
    for took, kind, command in sorted(slow, reverse=True)[: args.top]:
        print(f"  {took:6.0f}s  {kind:10} {command}")


if __name__ == "__main__":
    main()
