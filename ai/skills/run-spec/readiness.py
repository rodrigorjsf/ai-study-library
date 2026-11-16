#!/usr/bin/env python3
import argparse
import pathlib

CHECK_KEYS = ("typecheck", "lint", "test")
RUN_SPEC_FILE = "docs/agents/run-spec.md"
RECIPE_LOCATIONS = ((".claude/skills", "verify*"), (".claude/skills", "run-*"), (".cursor/skills", "verify-*"))
SEARCHED = ", ".join(f"{parent}/{pattern}/" for parent, pattern in RECIPE_LOCATIONS)


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


def render(spec, commands, recipe):
    missing = [key for key in CHECK_KEYS if key not in commands]
    summary = f"readiness {spec}: check commands {len(commands)} of {len(CHECK_KEYS)} declared"
    if missing:
        summary += f" (missing: {', '.join(missing)})"
    summary += f"; app recipe {recipe}" if recipe else "; no app recipe"
    lines = [summary, "### Check commands"]
    lines += [f"- {key}: declared ({commands[key]})" if key in commands else f"- {key}: missing" for key in CHECK_KEYS]
    if missing:
        lines.append(f'- declare a missing key as a "<key>: <command>" line in {RUN_SPEC_FILE}')
    lines.append("### App recipe")
    if recipe:
        lines.append(f"- found: {recipe}")
    else:
        lines.append(f"- none found in {SEARCHED}")
        lines.append("- suggestion: run Claude Code's `/run-skill-generator` to create one")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(prog="readiness.py")
    parser.add_argument("--repo", required=True, type=pathlib.Path)
    parser.add_argument("--spec", required=True)
    args = parser.parse_args()
    if not args.spec.strip():
        parser.error("--spec is empty")
    if not args.repo.is_dir():
        parser.error(f"--repo {args.repo} is not a directory")
    print(render(args.spec, declared_commands(args.repo), find_recipe(args.repo)))


if __name__ == "__main__":
    main()
