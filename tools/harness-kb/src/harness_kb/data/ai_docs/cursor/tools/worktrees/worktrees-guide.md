# Worktrees

Use `/worktree` for one isolated run and `/best-of-n` to compare multiple models on the same task in isolated worktrees.

A worktree is a separate Git checkout that lives beside your main checkout. Cursor uses it to keep local agent work isolated while still working against the same repository.

Each worktree has its own files and uncommitted changes. Your main checkout stays untouched until you apply a result back.

The [Cursor CLI](/docs/cli/using#cli-worktrees) supports the same isolation with the global `--worktree` flag. Those sessions use the same `~/.cursor/worktrees` storage and cleanup behavior as editor worktrees (see [How are old worktrees cleaned up?](#how-are-old-worktrees-cleaned-up)).

## Use /worktree for one isolated run

Start a task with `/worktree` when you want Cursor to do the rest of that chat in a separate checkout.

- Keep experimental edits away from your main checkout
- Run installs, builds, and tests without disturbing your current branch
- Work on risky refactors with a simple cleanup path

```
/worktree fix the failing auth tests and update the login copy
```

In a lot of cases, you should be able to commit/push directly from the worktree. You can do this by asking the agent directly:

```
Commit and push these changes, then open a PR
```

However, if you want to bring the changes into your main checkout to test them, use `/apply-worktree`. When you are done with the isolated checkout, use `/delete-worktree`.

If you want to see all worktrees in your repository, run:

```
git worktree list
```

## Use /best-of-n to compare multiple models

`/best-of-n` runs the same task across multiple models at once. Each run gets its own worktree, so the candidates stay isolated from each other and from your main checkout.

```
/best-of-n sonnet, gpt, composer fix the flaky logout test
```

Use it when you want to:

- Compare different models on the same prompt
- Try multiple approaches for a hard change
- Pick the strongest result before applying anything

`/best-of-n` compares runs only. It does not merge changes back into your main checkout for you. After you pick a winner, you can commit/push directly from the worktree or use `/apply-worktree` to bring the changes into your main checkout.

## How does worktree setup work?

You can customize worktree setup with `.cursor/worktrees.json`. Cursor looks for this file in the following order:

1. In the worktree path
2. In the root path of your project

### Configuration options

The `worktrees.json` file supports three configuration keys:

- **`setup-worktree-unix`**: Commands or script path for macOS and Linux. This takes precedence over `setup-worktree` on Unix systems.
- **`setup-worktree-windows`**: Commands or script path for Windows. This takes precedence over `setup-worktree` on Windows.
- **`setup-worktree`**: Generic fallback for all operating systems.

Each key accepts either:

- **An array of shell commands**: executed sequentially in the worktree
- **A string filepath**: path to a script file relative to `.cursor/worktrees.json`

## Example setup configurations

You could manually create worktrees with `git worktree add <...>`. However, using these commands provides several advantages.

- You can use Cursor's built-in tooling to ensure that the worktree is set up correctly for the project.
- Cursor's automatic worktree cleanup documented below will run for these worktrees.
- Our prompts have been tuned for the most common use cases.

### Using command arrays

#### Node.js project

```
{
  "setup-worktree": [
    "npm ci",
    "cp $ROOT_WORKTREE_PATH/.env .env"
  ]
}
```

We do not recommend symlinking dependencies into the worktree. This can cause issues in the main worktree. Use a fast package manager such as `bun`, `pnpm`, or `uv` instead.

#### Python project with virtual environment

```
{
  "setup-worktree": [
    "python -m venv venv",
    "source venv/bin/activate && pip install -r requirements.txt",
    "cp $ROOT_WORKTREE_PATH/.env .env"
  ]
}
```

#### Project with database migrations

```
{
  "setup-worktree": [
    "npm ci",
    "cp $ROOT_WORKTREE_PATH/.env .env",
    "npm run db:migrate"
  ]
}
```

#### Build and link dependencies

```
{
  "setup-worktree": [
    "pnpm install",
    "pnpm run build",
    "cp $ROOT_WORKTREE_PATH/.env.local .env.local"
  ]
}
```

### Using script files

For more complex setups, reference script files instead of inline commands:

```
{
  "setup-worktree-unix": "setup-worktree-unix.sh",
  "setup-worktree-windows": "setup-worktree-windows.ps1",
  "setup-worktree": [
    "echo 'Using generic fallback. For better support, define OS-specific scripts.'"
  ]
}
```

Place your scripts in the `.cursor/` directory next to `worktrees.json`.

**setup-worktree-unix.sh** (Unix and macOS):

```
#!/bin/bash
set -e

# Install dependencies
npm ci

# Copy environment file
cp "$ROOT_WORKTREE_PATH/.env" .env

# Run database migrations
npm run db:migrate

echo "Worktree setup complete!"
```

**setup-worktree-windows.ps1** (Windows):

```
$ErrorActionPreference = 'Stop'

# Install dependencies
npm ci

# Copy environment file
Copy-Item "$env:ROOT_WORKTREE_PATH\.env" .env

# Run database migrations
npm run db:migrate

Write-Host "Worktree setup complete!"
```

### OS-specific configurations

You can provide different setup commands for different operating systems:

```
{
  "setup-worktree-unix": [
    "npm ci",
    "cp $ROOT_WORKTREE_PATH/.env .env",
    "chmod +x scripts/*.sh"
  ],
  "setup-worktree-windows": [
    "npm ci",
    "copy %ROOT_WORKTREE_PATH%\\.env .env"
  ]
}
```

### Debugging

If you want to debug worktree setup, open the Output panel in the editor and select `Worktrees Setup`.

## How are old worktrees cleaned up?

You can always remove a worktree yourself with `/delete-worktree`. Cursor can also clean up older worktrees automatically to limit disk usage.

Worktrees created from the CLI with [`--worktree`](/docs/cli/using#cli-worktrees) live under `~/.cursor/worktrees` together with editor worktrees, so the same automatic cleanup applies.

```
{
  "cursor.worktreeCleanupIntervalHours": 6,
  "cursor.worktreeMaxCount": 20
}
```

## How is this different from the previous parallel agents feature in Cursor?

Automatic management of worktrees was removed in Cursor 3.0 and replaced with the new commands `/worktree` and `/best-of-n`. We also have added worktree support for the Cursor CLI.

Management of worktrees is now fully agentic. This makes it simpler to support use cases such as starting an agent, and only doing work in a worktree later on in the chat's lifecycle.

`/best-of-n` makes comparing the results of multiple models much easier. The parent agent will provide commentary on the different results and you can pick the best one. Additionally, you can even ask the parent agent to merge different parts of the different implementations into a single commit.

If you had agents that were previously running in a worktree, those chats will still work. However, you will need to use the new commands to start new agents in worktrees.
