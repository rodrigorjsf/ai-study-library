#!/usr/bin/env bash
# Install the committed run-spec flow from this repository into ~/.claude, as copies.
#   skill          -> ~/.claude/skills/run-spec/   (SKILL.md, QUEUE.md, tickets.py, hygiene.py, watchdog.sh, axes/, guides/)
#   agents         -> ~/.claude/agents/            (the six run-spec agents)
#   follow-up-issue-> ~/.claude/skills/follow-up-issue/
# Installs from HEAD with core.autocrlf=false, so a CRLF working tree never reaches the installed files.
set -euo pipefail

repo=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
dest=${CLAUDE_HOME:-$HOME/.claude}
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

git -C "$repo" -c core.autocrlf=false archive HEAD ai/skills/run-spec ai/skills/follow-up-issue | tar -x -C "$tmp"
src=$tmp/ai/skills

mkdir -p "$dest/skills/run-spec" "$dest/agents" "$dest/skills/follow-up-issue"
cp -a "$src/run-spec/agents/." "$dest/agents/"
rsync -a --delete --delete-excluded --exclude agents --exclude install.sh --exclude README.md --exclude __pycache__ --exclude 'test_*.py' --exclude /GLOSSARY.md --exclude /docs/ \
  "$src/run-spec/" "$dest/skills/run-spec/"
rsync -a --delete "$src/follow-up-issue/" "$dest/skills/follow-up-issue/"

echo "installed run-spec $(git -C "$repo" rev-parse --short HEAD) into $dest"
