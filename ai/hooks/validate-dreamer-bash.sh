#!/usr/bin/env bash
# PreToolUse validator for the `dreamer` subagent.
# Allows narrow operations on Claude Code memory directories; denies everything else.
#
# Tools matched: Bash, Write, Edit.
# Allowed Bash commands: `ls`, `ls -R`, `ls -la`, `mkdir -p`, `rm`, `rm -f`, `wc -l`, `grep`.
# Allowed Write/Edit targets: paths under one of the allowed memory roots.
#
# Two path classes:
#   - write roots: the memory directories. `mkdir`, `rm`, Write and Edit stay here.
#   - read roots:  the write roots plus everything under ~/.claude/projects, where
#     session transcripts (*.jsonl) live. `ls`, `wc -l` and `grep` may read there.
#     The dreamer's Read tool is not matched by this hook, so this exposes nothing new.
#
# On allow: prints permissionDecision=allow JSON and exits 0.
# On deny:  prints reason to stderr and exits 2 (blocks the tool call).

set -u

print_allow() {
    printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"}}\n'
    exit 0
}

deny() {
    printf 'dreamer hook DENY: %s\n' "$1" >&2
    exit 2
}

# Build allowed roots list (canonicalized).
ALLOWED_ROOTS=(
    "$HOME/.claude/projects"
    "$HOME/.claude/memory"
    "$HOME/.claude/user-memory"
)
if [ -n "${CLAUDE_USER_MEMORY_DIR:-}" ]; then
    ALLOWED_ROOTS+=("$CLAUDE_USER_MEMORY_DIR")
fi

# Canonicalize each root once.
CANON_ROOTS=()
for root in "${ALLOWED_ROOTS[@]}"; do
    canon=$(realpath -m -- "$root" 2>/dev/null) || continue
    CANON_ROOTS+=("$canon")
done

# Test if a path (after canonicalization) is under an allowed root.
# For project-scope, additionally require the path goes through `/memory` segment.
path_under_allowed_root() {
    local path="$1"
    local canon
    canon=$(realpath -m -- "$path" 2>/dev/null) || return 1

    # Reject any `..` segment that survived (defense in depth).
    case "$canon" in
        */../*|*/..|../*|..) return 1 ;;
    esac

    for root in "${CANON_ROOTS[@]}"; do
        case "$canon" in
            "$root"|"$root"/*)
                # Project root must include /memory segment after the project slug.
                if [ "$root" = "$(realpath -m -- "$HOME/.claude/projects")" ]; then
                    case "$canon" in
                        "$root"/*/memory|"$root"/*/memory/*) return 0 ;;
                        *) continue ;;
                    esac
                fi
                return 0
                ;;
        esac
    done
    return 1
}

# Test if a path may be read: an allowed memory root, or anywhere under
# ~/.claude/projects (transcripts sit beside each project's memory directory).
path_readable() {
    local path="$1"
    local canon projects
    path_under_allowed_root "$path" && return 0
    canon=$(realpath -m -- "$path" 2>/dev/null) || return 1
    projects=$(realpath -m -- "$HOME/.claude/projects")
    case "$canon" in
        "$projects"|"$projects"/*) return 0 ;;
    esac
    return 1
}

# Read full stdin JSON.
INPUT=$(cat)

# Extract tool_name. Use jq if available; otherwise minimal sed fallback.
if command -v jq >/dev/null 2>&1; then
    TOOL_NAME=$(printf '%s' "$INPUT" | jq -r '.tool_name // empty')
else
    TOOL_NAME=$(printf '%s' "$INPUT" | sed -n 's/.*"tool_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)
fi

case "$TOOL_NAME" in
    Bash)
        if command -v jq >/dev/null 2>&1; then
            COMMAND=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty')
        else
            deny "jq not available — cannot safely parse Bash command"
        fi

        [ -n "$COMMAND" ] || deny "empty Bash command"

        # Reject shell metacharacters, expansion and escapes, quoted or not.
        # A grep pattern therefore cannot use `|`, `$` or `\`; pass a fixed term.
        case "$COMMAND" in
            *';'*|*'|'*|*'&'*|*'$'*|*'`'*|*'>'*|*'<'*|*'\\'*|*$'\n'*)
                deny "shell metachar/expansion not allowed: $COMMAND"
                ;;
        esac

        # Split into argv. Quotes only group words (a search term with spaces),
        # so tokenize the way the shell will; without quotes, plain word-splitting
        # gives the same result and needs no interpreter.
        case "$COMMAND" in
            *\"*|*\'*)
                command -v python3 >/dev/null 2>&1 \
                    || deny "python3 not available — cannot safely parse a quoted command"
                TOKENS=$(python3 -c 'import shlex, sys
for token in shlex.split(sys.argv[1]):
    if not token:
        sys.exit(3)
    print(token)' "$COMMAND" 2>/dev/null) || deny "unbalanced or empty quotes: $COMMAND"
                ARGV=()
                while IFS= read -r token; do
                    ARGV+=("$token")
                done <<EOF
$TOKENS
EOF
                set -- "${ARGV[@]}"
                ;;
            *)
                set -f
                # shellcheck disable=SC2086
                set -- $COMMAND
                set +f
                ;;
        esac

        [ "$#" -ge 1 ] || deny "no argv parsed from command"

        BIN="$1"; shift

        # Match command pattern. Each branch must consume all remaining args
        # and verify every path arg is under an allowed root.
        case "$BIN" in
            ls)
                # Optional flags: -R, -la, -l, -a (any combination of these letters).
                while [ "$#" -gt 0 ]; do
                    case "$1" in
                        -R|-l|-a|-la|-al|-lR|-Rl)
                            shift
                            ;;
                        -*)
                            deny "ls flag not allowed: $1"
                            ;;
                        *)
                            break
                            ;;
                    esac
                done
                [ "$#" -ge 1 ] || deny "ls requires at least one path"
                for arg in "$@"; do
                    path_readable "$arg" || deny "ls path outside readable roots: $arg"
                done
                print_allow
                ;;
            mkdir)
                [ "${1:-}" = "-p" ] || deny "mkdir requires literal '-p' flag"
                shift
                [ "$#" -ge 1 ] || deny "mkdir requires at least one path"
                for arg in "$@"; do
                    path_under_allowed_root "$arg" || deny "mkdir path outside allowed roots: $arg"
                done
                print_allow
                ;;
            rm)
                # Optional `-f` only. Block -r, -rf, -R, --recursive, --no-preserve-root, etc.
                if [ "${1:-}" = "-f" ]; then
                    shift
                fi
                [ "$#" -ge 1 ] || deny "rm requires at least one path"
                for arg in "$@"; do
                    case "$arg" in
                        -*) deny "rm flag not allowed: $arg" ;;
                    esac
                    path_under_allowed_root "$arg" || deny "rm path outside allowed roots: $arg"
                    # Force `.md` suffix or `MEMORY.md` to prevent wiping non-memory files.
                    case "$arg" in
                        *.md) ;;
                        *) deny "rm only permitted on .md files: $arg" ;;
                    esac
                done
                print_allow
                ;;
            wc)
                [ "${1:-}" = "-l" ] || deny "wc requires literal '-l' flag"
                shift
                [ "$#" -ge 1 ] || deny "wc requires at least one path"
                for arg in "$@"; do
                    path_readable "$arg" || deny "wc path outside readable roots: $arg"
                done
                print_allow
                ;;
            grep)
                # Read-only search of memory files and transcripts.
                # Flags: any combination of the letters r n i l c F E P o h H w,
                # `-m <count>`, and `--include=*.jsonl` / `--include=*.md`.
                # Then one search term (or `-e <term>`), then at least one path.
                HAVE_PATTERN=0
                while [ "$#" -gt 0 ]; do
                    case "$1" in
                        --include=\*.jsonl|--include=\*.md)
                            shift
                            ;;
                        -m)
                            case "${2:-}" in
                                ''|*[!0-9]*) deny "grep -m requires a number" ;;
                            esac
                            shift 2
                            ;;
                        -e)
                            [ "$#" -ge 2 ] || deny "grep -e requires a search term"
                            HAVE_PATTERN=1
                            shift 2
                            ;;
                        --*)
                            deny "grep flag not allowed: $1"
                            ;;
                        -*)
                            case "${1#-}" in
                                ''|*[!rnilcFEPohHw]*) deny "grep flag not allowed: $1" ;;
                            esac
                            shift
                            ;;
                        *)
                            break
                            ;;
                    esac
                done
                if [ "$HAVE_PATTERN" -eq 0 ]; then
                    [ "$#" -ge 1 ] || deny "grep requires a search term"
                    shift
                fi
                [ "$#" -ge 1 ] || deny "grep requires at least one path"
                for arg in "$@"; do
                    case "$arg" in
                        -*) deny "grep flags must come before the search term: $arg" ;;
                    esac
                    path_readable "$arg" || deny "grep path outside readable roots: $arg"
                done
                print_allow
                ;;
            *)
                deny "command not in allowlist: $BIN (allowed: ls, mkdir -p, rm, wc -l, grep)"
                ;;
        esac
        ;;

    Write|Edit)
        if command -v jq >/dev/null 2>&1; then
            FILE_PATH=$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // empty')
        else
            deny "jq not available — cannot safely parse $TOOL_NAME file_path"
        fi
        [ -n "$FILE_PATH" ] || deny "$TOOL_NAME missing file_path"
        case "$FILE_PATH" in
            *'..'*) deny "path traversal '..' not allowed: $FILE_PATH" ;;
        esac
        path_under_allowed_root "$FILE_PATH" \
            || deny "$TOOL_NAME path outside allowed memory roots: $FILE_PATH"
        print_allow
        ;;

    *)
        # Other tools (Read, Grep, Glob) are not matched by this hook in the
        # subagent definition. If we somehow receive one, allow without comment
        # so we don't accidentally block reads.
        print_allow
        ;;
esac
