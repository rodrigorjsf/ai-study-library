#!/usr/bin/env bash
# Usage: watchdog.sh <STATE> [idle-minutes] [deadline-minutes] [interval-seconds]
# Defaults: 120, 240, 600. Started with run_in_background, its exit wakes the dispatcher, which a dead subagent never does.
# It sleeps one interval before each check, then exits on the first of:
#   stalled: <id>     a ticket worktree <STATE>/wt/<id> with no <STATE>/status-<id>.md, no file change for idle-minutes,
#                     no process naming it, and no <STATE>/stalled-<id> marker touched within idle-minutes;
#                     or, naming the first worktree: every worktree has a status-<id>.md, none of those files and no
#                     stalled-<id> marker of theirs was touched within idle-minutes, and <STATE>/running is empty.
#                     The wave is then stuck: an implementer died after writing its status file, before its final message.
#   overdue: <label>  a marker <STATE>/running/<label> not touched for deadline-minutes
# It exits silently when <STATE>/wt holds no worktree and <STATE>/running holds no marker.
set -u
state=$1 idle=${2:-120} deadline=${3:-240} interval=${4:-600}
shopt -s nullglob
while :; do
  dirs=("$state"/wt/*/)
  markers=("$state"/running/*)
  [ ${#dirs[@]} -eq 0 ] && [ ${#markers[@]} -eq 0 ] && exit 0
  sleep "$interval"
  dirs=("$state"/wt/*/)
  markers=("$state"/running/*)
  stuck=${#dirs[@]}
  for d in "${dirs[@]}"; do
    id=$(basename "$d")
    [ -e "$state/status-$id.md" ] || stuck=0
    [ -n "$(find "$state/status-$id.md" "$state/stalled-$id" -mmin "-$idle" 2>/dev/null)" ] && stuck=0
  done
  if [ "$stuck" -gt 0 ] && [ ${#markers[@]} -eq 0 ]; then
    echo "stalled: $(basename "${dirs[0]}")"
    exit 0
  fi
  for d in "${dirs[@]}"; do
    id=$(basename "$d")
    [ -e "$state/status-$id.md" ] && continue
    [ -n "$(find "$state/stalled-$id" -mmin "-$idle" 2>/dev/null)" ] && continue
    recent=$(find "$d" \( -name .git -o -name node_modules -o -name .codegraph \) -prune -o -mmin "-$idle" -print -quit 2>/dev/null)
    [ -n "$recent" ] && continue
    pgrep -f "wt/${id}(/|\$|[[:space:]])" >/dev/null && continue
    echo "stalled: $id"
    exit 0
  done
  for m in "$state"/running/*; do
    [ -n "$(find "$m" -mmin "+$deadline" 2>/dev/null)" ] || continue
    echo "overdue: $(basename "$m")"
    exit 0
  done
done
