# Checks

How step 11 turns a mechanical rule into a check, in any ecosystem. The repo's own tools come first: a check lives where the repo already runs checks (its linter, its test runner, its hooks or CI), never in a new tool when an existing one can carry it.

## Choosing the first batch

Recommend first the checks that are deterministic, cheap to run and already true of the code (zero or a handful of violations): a banned construct, a required naming or import shape, a file-location rule, a required header in a kind of file. A check with hundreds of existing violations is its own piece of work: propose it with the measured count and an adoption path (fix all, or a suppression file that only shrinks), not as part of the batch.

## Where a check goes

| Kind of rule | Usual home |
|---|---|
| a construct, call, import or naming pattern in source | the language's linter: a built-in rule by name, a restricted-syntax or restricted-import rule, a plugin rule (ESLint/typescript-eslint, Ruff, golangci-lint, Checkstyle or ArchUnit, Clippy, RuboCop, detekt) |
| a compiler or type-checker guarantee | a compiler flag in the shared config |
| a fact about files (every migration has a header, every script passes a shell linter, a template lists every variable) | a repo-level test that reads the files or runs the tool, in the repo's test runner |
| a fact about config (a container drops capabilities, a package setting is declared) | a repo-level test that parses the config |
| something only a human can see in the diff | not a check: it stays a judgement rule |

## Writing the check

- **Test first, with the real tool.** Run the linter or the tool on an offender snippet and on a legitimate one, and assert on the rule it reports, so the check provably fires and provably stays quiet. Where the linter needs real files for type information, use paths that exist.
- **Prove the red.** For a repo-level test over the real files, inject one temporary offender (a file, a line), watch the test fail, remove it.
- **Mind rule overriding.** Many linters replace a rule's options wholesale when a later config block matches the same file: a second block that sets a restricted-imports or restricted-syntax rule drops what the first one banned. Repeat the earlier entries in the later block, and say so in a comment.
- **Mind false positives in other languages.** A comment-marker rule that is case-insensitive flags words of another language (the Portuguese "todo" means "every"); match the marker in its exact case, or only where it opens a comment.
- **Use the platform's own lists** over hand-written ones (the runtime's list of built-in modules, the tool's list of severities), so a new entry is never missed.
- **Fix or scope what the check reveals.** Existing violations are fixed in the same change, or the check is scoped with the user's agreement and a comment saying why.
- **Tests that spawn tools in a temporary repository** pass a clean environment: a git hook exports variables (`GIT_DIR`, `GIT_INDEX_FILE`) that would point a spawned git at the real repository.

## The exemplar check

Add a repo-level test that reads `CODING_STANDARDS.md`, collects every cited `path:line`, and fails when the file is gone or has fewer lines than cited. It runs in the check command, so a refactor that moves or deletes the exemplar of a rule fails the build instead of leaving the reviewer a pointer to nothing. Whether the line still shows the rule stays the reviewer's call.

## After the checks land

Move each rule a check now enforces out of the file: drop the bullet, or keep only its judgement part, and add the check to that section's "Enforced by tooling" line with what it guarantees and where it is proved.
