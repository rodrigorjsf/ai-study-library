#!/usr/bin/env bash
# PreToolUse validator for the `dreamer` subagent.
# Allows narrow operations on Claude Code memory directories; denies everything else.
#
# Tools matched: Bash, Write, Edit.
# Allowed Bash commands: `ls`, `ls -R`, `ls -la`, `mkdir -p`, `rm`, `rm -f`, `wc -l`.
# Allowed Write/Edit targets: paths under one of the allowed memory roots.
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

        # Reject shell metacharacters and substitution.
        case "$COMMAND" in
            *';'*|*'&&'*|*'||'*|*'|'*|*'&'*|*'$('*|*'`'*|*'>'*|*'<'*|*$'\n'*)
                deny "shell metachar/substitution not allowed: $COMMAND"
                ;;
        esac

        # Reject `..` path traversal anywhere in the command string.
        case "$COMMAND" in
            *'..'*) deny "path traversal '..' not allowed: $COMMAND" ;;
        esac

        # Split into argv via word-splitting (no globbing).
        set -f
        # shellcheck disable=SC2086
        set -- $COMMAND
        set +f

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
                    path_under_allowed_root "$arg" || deny "ls path outside allowed roots: $arg"
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
                    path_under_allowed_root "$arg" || deny "wc path outside allowed roots: $arg"
                done
                print_allow
                ;;
            *)
                deny "command not in allowlist: $BIN (allowed: ls, mkdir -p, rm, wc -l)"
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
