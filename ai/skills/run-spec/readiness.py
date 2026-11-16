#!/usr/bin/env python3
import argparse
import json
import pathlib
import re
import subprocess
import sys

CHECK_KEYS = ("typecheck", "lint", "test")
RUN_SPEC_FILE = "docs/agents/run-spec.md"
RECIPE_LOCATIONS = ((".claude/skills", "verify*"), (".claude/skills", "run-*"), (".cursor/skills", "verify-*"))
SEARCHED = ", ".join(f"{parent}/{pattern}/" for parent, pattern in RECIPE_LOCATIONS)
TICKETS = pathlib.Path(__file__).resolve().parent / "tickets.py"
CODE_SPAN = re.compile(r"`[^`]*[^`\s][^`]*`")


def declared_commands(repo):
    try:
        text = (repo / RUN_SPEC_FILE).read_bytes().decode("utf-8", errors="replace")
    except OSError:
        return {}
    lines = text.replace("\r", "").split("\n")
    commands = {}
    for key in CHECK_KEYS:
        line = next((line for line in lines if line.startswith(f"{key}:")), None)
        command = line[len(key) + 1:].strip(" \t\v\f") if line is not None else ""
        if command:
            commands[key] = command
    return commands


def check_command_lines(commands):
    return "\n".join(f"{key.upper()}: {commands.get(key, 'none')}" for key in CHECK_KEYS)


def find_recipe(repo):
    for parent, pattern in RECIPE_LOCATIONS:
        try:
            candidates = sorted((repo / parent).glob(pattern))
            for directory in candidates:
                if (directory / "SKILL.md").is_file():
                    return f"{parent}/{directory.name}/"
        except OSError:
            continue
    return None


def read_tickets(repo, spec):
    tracker = "github" if re.fullmatch(r"#?\d+", spec) else "local"
    result = subprocess.run([sys.executable, "-I", str(TICKETS), "--tracker", tracker, "--spec", spec, "--criteria"],
                            cwd=repo, capture_output=True, text=True, errors="replace")
    if result.returncode != 0:
        reason = next((line for line in reversed(result.stderr.splitlines()) if line.strip()), f"exit {result.returncode}")
        return None, reason.strip()
    try:
        return json.loads(result.stdout)["tickets"], None
    except (ValueError, KeyError):
        return None, "tickets.py printed no ticket list"


def surface_report(tickets, error):
    if error:
        return "unchecked", [f"could not read ticket criteria: {error}"]
    scoped = [ticket for ticket in tickets if ticket["in_scope"]]
    if not scoped:
        return "unchecked", ["no ticket in scope to check"]
    warnings = []
    for ticket in scoped:
        if not ticket["criteria"]:
            warnings.append(f"{ticket['id']}: no acceptance criteria found")
        warnings += [f"{ticket['id']}: {criterion}" for criterion in ticket["criteria"] if not CODE_SPAN.search(criterion)]
    if warnings:
        return f"warnings: {len(warnings)}", warnings
    count = sum(len(ticket["criteria"]) for ticket in scoped)
    return "ok", [f"every criterion names a surface (tickets: {len(scoped)}, criteria: {count})"]


def render(spec, commands, recipe, surface):
    missing = [key for key in CHECK_KEYS if key not in commands]
    summary = f"readiness {spec}: check commands {len(commands)} of {len(CHECK_KEYS)} declared"
    if missing:
        summary += f" (missing: {', '.join(missing)})"
    summary += f"; app recipe {recipe}" if recipe else "; no app recipe"
    surface_state, surface_lines = surface
    summary += f"; surface {surface_state}"
    lines = [summary, "### Check commands"]
    lines += [f"- {key}: declared ({commands[key]})" if key in commands else f"- {key}: missing" for key in CHECK_KEYS]
    lines.append("### App recipe")
    if recipe:
        lines.append(f"- found: {recipe}")
    else:
        lines.append(f"- none found in {SEARCHED}")
        lines.append("- suggestion: run Claude Code's `/run-skill-generator` to create one")
    lines.append("### Surface")
    lines += [f"- {line}" for line in surface_lines]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(prog="readiness.py")
    parser.add_argument("--repo", required=True, type=pathlib.Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--spec")
    mode.add_argument("--check-commands", action="store_true",
                      help="print only the TYPECHECK, LINT and TEST prompt lines, none for a key not declared")
    args = parser.parse_args()
    if args.spec is not None and not args.spec.strip():
        parser.error("--spec is empty")
    if not args.repo.is_dir():
        parser.error(f"--repo {args.repo} is not a directory")
    if args.check_commands:
        print(check_command_lines(declared_commands(args.repo)))
        return
    print(render(args.spec, declared_commands(args.repo), find_recipe(args.repo), surface_report(*read_tickets(args.repo, args.spec))))


if __name__ == "__main__":
    main()
