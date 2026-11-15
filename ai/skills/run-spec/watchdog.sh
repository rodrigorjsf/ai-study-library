#!/usr/bin/env bash
# Usage: watchdog.sh <STATE> [idle-minutes]
# Exits, printing `stalled: <id>`, when a ticket worktree under <STATE>/wt has had no file change for idle-minutes (default
# 120) and no process names it. Exits silently when <STATE>/wt holds no worktree. Started with run_in_background, its exit
# wakes the dispatcher, which a dead subagent never does.
set -u
state=$1 idle=${2:-120}
while :; do
  shopt -s nullglob
  dirs=("$state"/wt/*/)
  [ ${#dirs[@]} -eq 0 ] && exit 0
  for d in "${dirs[@]}"; do
    id=$(basename "$d")
    recent=$(find "$d" \( -name .git -o -name node_modules -o -name .codegraph \) -prune -o -type f -mmin "-$idle" -print -quit 2>/dev/null)
    [ -n "$recent" ] && continue
    pgrep -f "wt/$id" >/dev/null && continue
    echo "stalled: $id"
    exit 0
  done
  sleep 600
done
