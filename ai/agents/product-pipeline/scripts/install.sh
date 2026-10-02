#!/usr/bin/env bash
# Install the product-pipeline personas and the conventions skill into a target project.
#
# Usage: install.sh [--symlink] <target-project-dir>
#
# - Every persona .md under the stage folders (discovery/, prd/, architecture/,
#   tasks/, shared/) is installed FLAT into <target>/.claude/agents/<name>.md.
#   Loading agent files from nested subfolders of .claude/agents/ is unverified,
#   so the install does not depend on it.
# - Every skill folder under skills/ is installed into <target>/.claude/skills/<skill>/.
# - README.md and scripts/ are never installed.
# - --symlink creates absolute symlinks instead of copies (edits in this repo propagate).
set -euo pipefail

usage() {
  echo "Usage: $(basename "$0") [--symlink] <target-project-dir>" >&2
  exit 64
}

mode="copy"
target=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --symlink) mode="symlink"; shift ;;
    -h|--help) usage ;;
    -*) echo "Unknown option: $1" >&2; usage ;;
    *)
      [[ -z "$target" ]] || usage
      target="$1"; shift ;;
  esac
done
[[ -n "$target" ]] || usage
[[ -d "$target" ]] || { echo "Target directory does not exist: $target" >&2; exit 1; }

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
src_root="$(cd "$script_dir/.." && pwd)"
target="$(cd "$target" && pwd)"
agents_dir="$target/.claude/agents"
skills_dir="$target/.claude/skills"

# Collect persona files: depth-2 .md files in stage folders, excluding skills/ and scripts/.
personas=()
while IFS= read -r -d '' f; do
  personas+=("$f")
done < <(find "$src_root" -mindepth 2 -maxdepth 2 -type f -name '*.md' \
           -not -path "$src_root/skills/*" -not -path "$src_root/scripts/*" \
           -not -name 'README.md' -print0 | sort -z)

[[ ${#personas[@]} -gt 0 ]] || { echo "No persona files found under $src_root" >&2; exit 1; }

# Refuse duplicate basenames: a flat install would silently overwrite one of them.
dupes="$(for f in "${personas[@]}"; do basename "$f"; done | sort | uniq -d)"
if [[ -n "$dupes" ]]; then
  echo "Duplicate persona file names (flat install would collide):" >&2
  echo "$dupes" >&2
  exit 1
fi

mkdir -p "$agents_dir" "$skills_dir"

install_file() {  # <src> <dest>
  if [[ "$mode" == "symlink" ]]; then
    ln -sfn "$1" "$2"
  else
    rm -f "$2"   # replace a previous symlink instead of writing through it
    cp "$1" "$2"
  fi
}

declare -A per_stage=()
for f in "${personas[@]}"; do
  install_file "$f" "$agents_dir/$(basename "$f")"
  stage="$(basename "$(dirname "$f")")"
  per_stage[$stage]=$(( ${per_stage[$stage]:-0} + 1 ))
done

skills_installed=()
if [[ -d "$src_root/skills" ]]; then
  for d in "$src_root"/skills/*/; do
    [[ -d "$d" ]] || continue
    name="$(basename "$d")"
    dest="$skills_dir/$name"
    rm -rf "$dest"
    if [[ "$mode" == "symlink" ]]; then
      ln -sfn "${d%/}" "$dest"
    else
      cp -R "${d%/}" "$dest"
    fi
    skills_installed+=("$name")
  done
fi

echo "Installed product-pipeline into $target ($mode)"
echo "  agents -> $agents_dir: ${#personas[@]} files"
for stage in $(printf '%s\n' "${!per_stage[@]}" | sort); do
  printf '    %-14s %d\n' "$stage" "${per_stage[$stage]}"
done
echo "  skills -> $skills_dir: ${skills_installed[*]:-(none)}"
echo
echo "Next: restart Claude Code (or open /agents), add gates/<stage>-exit-rubric.md files, then run:"
echo "  $script_dir/run-stage.sh discovery <run-id> <idea-file>"
