# Semantic & Agentic Search

Agent combines multiple search tools to find relevant code across your codebase. You describe what you're looking for in natural language, and Agent picks the right strategy.

## Instant Grep

The fastest way to find code is an exact match: a function name, variable, error string, or regex pattern. Agent uses **grep** (powered by ripgrep) automatically when you reference specific symbols.

**Example:** Searching for `import.*PaymentService` in `middleware/session.ts`

## Semantic search

When you describe a concept rather than a specific symbol, Agent uses semantic (vector) search against its index of your codebase.

### How indexing works

Cursor breaks your code into meaningful chunks (functions, classes, logical blocks), converts each chunk into a vector embedding that captures its semantic meaning, and stores the results in a vector database. When you search, your query is converted into a vector using the same model and matched against the stored embeddings.

Indexing begins automatically when you open a workspace. Semantic search becomes available at **80% completion**. The index stays current through automatic sync every **5 minutes**, processing only changed files.

| Change | Action |
|---|---|
| New files | Added to the index automatically |
| Modified files | Old embeddings removed, new ones created |
| Deleted files | Removed from the index |

### Configuration

Navigate to **Cursor Settings > Indexing** to configure which files are indexed.

- Respects `.gitignore` and `.cursorignore` for exclusions
- View included files at **Cursor Settings > Indexing & Docs > View included files**

### Privacy and security

File paths are encrypted before being sent to Cursor's servers. Code content is never stored in plaintext; it is held in memory during indexing, then discarded. Embeddings are created without storing filenames or source code. When Agent searches, Cursor retrieves the embeddings and decrypts the chunks on the client side.

## How Agent combines search tools

Agent picks the right tool based on your prompt:

| Prompt style | Tools used | Example |
|---|---|---|
| Specific symbol or string | Instant grep | `PaymentService` |
| Concept or behavior | Semantic search, then grep to fill in details | *"where do we handle payment failures"* |
| Complex exploration | Multiple searches, file reads, reference following | *"understand the full auth flow"* |

You don't choose the tool. Describe what you need and Agent decides. For complex tasks, it chains searches together: semantic search to find entry points, grep to trace references, and file reads to build full context.

## Explore subagent

Agent uses the **Explore subagent** automatically when it decides a task benefits from broad search. You can also request it directly.

This is useful for context management. Searching through many files generates a lot of context. The subagent keeps the main conversation focused by summarizing results instead of dumping raw file contents.

## Tips for better search results

- **Start specific, then go broad.** Begin with a concrete symbol or function name (e.g., `processOrder`) before broadening to conceptual queries.
- **Explore before changing.** Use search to understand the codebase before making edits.
- **Reference concrete code.** Mention specific file names, function names, or error strings when possible.

## FAQ

### Is my source code stored on Cursor servers?

No. Cursor creates embeddings without storing filenames or source code. Filenames are obfuscated and code chunks are encrypted. When Agent searches, Cursor retrieves the embeddings and decrypts the chunks on the client side.

### How long are indexed codebases retained?

Indexed codebases are deleted after **6 weeks of inactivity**. Reopening the project triggers re-indexing.

### Can I customize path encryption?

Yes — configure custom encryption keys via `.cursor/keys`.

### How does team sharing work?

Indexes can be shared across team members for faster indexing of similar codebases. Cursor respects file access permissions and only shares accessible content.

### Does Cursor support multi-root workspaces?

Yes, Cursor supports multi-root workspaces. See the multi-root workspaces documentation for details.
