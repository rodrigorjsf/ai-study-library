#!/usr/bin/env bash
# Start one product-pipeline stage in a fresh Claude Code session.
#
# Usage: run-stage.sh <stage> <run-id> [idea-file]
#   stage    discovery | prd | architecture | tasks
#   run-id   e.g. 20261002-invoice-reminders (letters, digits, dot, dash, underscore)
#   idea-file  discovery only: bootstraps docs/pipeline/<run-id>/00-intake/idea-brief.md
#              if it does not exist yet. A file with YAML frontmatter is copied as is;
#              plain text is wrapped in a brief template whose required fields are TODO
#              (the discovery-orchestrator resolves them in its clarifying round).
#
# Run from the target project root (the folder that contains .claude/agents/).
set -euo pipefail

usage() {
  echo "Usage: $(basename "$0") <discovery|prd|architecture|tasks> <run-id> [idea-file]" >&2
  exit 64
}

[[ $# -ge 2 && $# -le 3 ]] || usage
stage="$1"
run_id="$2"
idea_file="${3:-}"

case "$stage" in
  discovery)    orchestrator="discovery-orchestrator" ;;
  prd)          orchestrator="prd-orchestrator" ;;
  architecture) orchestrator="arch-orchestrator" ;;
  tasks)        orchestrator="tasks-orchestrator" ;;
  *) echo "Unknown stage: $stage" >&2; usage ;;
esac

if [[ ! "$run_id" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
  echo "Invalid run-id '$run_id' (use letters, digits, '.', '-', '_'; e.g. 20261002-my-idea)" >&2
  exit 64
fi

run_dir="docs/pipeline/$run_id"
intake_dir="$run_dir/00-intake"
brief="$intake_dir/idea-brief.md"

if [[ -n "$idea_file" ]]; then
  if [[ "$stage" != "discovery" ]]; then
    echo "Note: idea-file is only used by the discovery stage; ignoring $idea_file" >&2
  elif [[ -e "$brief" ]]; then
    echo "Idea brief already exists, leaving it unchanged: $brief"
  else
    [[ -f "$idea_file" ]] || { echo "Idea file not found: $idea_file" >&2; exit 1; }
    mkdir -p "$intake_dir/evidence"
    if [[ "$(head -n 1 "$idea_file")" == "---" ]]; then
      cp "$idea_file" "$brief"
    else
      {
        cat <<EOF
---
run_id: $run_id
created_at: $(date -u +%Y-%m-%dT%H:%M:%SZ)
source: $(basename "$idea_file")
problem_hypothesis: TODO
target_segment_hypothesis: TODO
business_objective: TODO          # or non_commercial_objective
decision_owner: TODO              # a named human
time_box: TODO
constraints: []
evidence_inventory: []            # files placed in 00-intake/evidence/
known_non_goals: []               # optional
# domain: / jurisdiction:         # required when the domain is regulated
---

# Idea brief

## Raw idea

EOF
        cat "$idea_file"
      } > "$brief"
    fi
    echo "Created $brief"
  fi
fi

if [[ "$stage" == "discovery" && ! -e "$brief" ]]; then
  echo "Warning: $brief does not exist; discovery-orchestrator will ask for the idea in its clarifying round." >&2
fi

if [[ ! -e ".claude/agents/$orchestrator.md" && ! -e "$HOME/.claude/agents/$orchestrator.md" ]]; then
  echo "Warning: $orchestrator.md not found in .claude/agents/ or ~/.claude/agents/ (run install.sh first?)" >&2
fi

rubric_stage="$stage"; [[ "$stage" == "architecture" ]] && rubric_stage="arch"
if [[ ! -e "docs/pipeline/gates/$rubric_stage-exit-rubric.md" ]]; then
  echo "Warning: docs/pipeline/gates/$rubric_stage-exit-rubric.md is missing; $orchestrator will stop with 'blocked' (run install.sh)." >&2
fi

command -v claude >/dev/null 2>&1 || { echo "The 'claude' CLI is not on PATH." >&2; exit 127; }

exec claude --agent "$orchestrator" "Run the $stage stage for run-id $run_id."
