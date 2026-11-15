# Bugbot

> Source: https://cursor.com/docs/bugbot — mirrored 2026-11-15

Bugbot reviews pull requests and identifies bugs, security issues, and code quality problems.

Configure Bugbot in [Automations](https://cursor.com/automations/from-cursor/bugbot).

[Bugbot leaving comments on a PR](/docs-static/images/bugbot/bugbot-report-cropped.mp4)

## How it works

Bugbot analyzes PR diffs and leaves comments with explanations and fix suggestions. It runs automatically on each PR update or manually when triggered.

- Runs **automatic reviews** on every PR update
- **Manual trigger** by commenting `cursor review` or `bugbot run` on any PR. Bugbot ignores these commands when a bot account or GitHub App posts them.
- **Uses existing PR comments as context**: reads connected PR comments (top-level and inline) to avoid duplicate suggestions and build on prior feedback
- **Fix in Cursor** links open issues directly in Cursor
- **Fix in Web** links open issues directly in [cursor.com/agents](https://cursor.com/agents)

### Limits

- **PR size**: Bugbot skips PRs larger than its default review-size limit, measured in changed lines and diff characters, and posts a comment asking you to split the change. A skipped run records no review usage.
- **Generated files**: Bugbot leaves out files marked `linguist-generated` in `.gitattributes`. They don't count toward the PR size limit.
- **Bot-authored PRs**: Bugbot caps how many reviews it runs on PRs opened by bot accounts, per team. Every review counts, including repeat reviews of the same PR. The cap is a default, and your team's cap can differ.

## Setup

Connect your repositories through the Cursor dashboard to start using Bugbot.

- **Origin**: See the [Origin page](https://cursor.com/docs/origin.md)
- **GitHub** (including GitHub Enterprise Server): See the [GitHub integration page](https://cursor.com/docs/integrations/github.md)
- **GitLab** (including GitLab Self-Hosted): See the [GitLab integration page](https://cursor.com/docs/integrations/gitlab.md)
- **Bitbucket** (including Bitbucket Data Center): See the [Bitbucket integration page](https://cursor.com/docs/integrations/bitbucket.md)
- **Azure DevOps** (Azure DevOps Services): See the [Azure DevOps integration page](https://cursor.com/docs/integrations/azure-devops.md#set-up-bugbot)

After connecting, open [Bugbot in Automations](https://cursor.com/automations/from-cursor/bugbot) to manage which repositories Bugbot reviews.

On GitHub, connecting turns Bugbot on for the repositories you grant access to. Repositories stay off when someone who isn't a team admin connects an enterprise team, or a team that already has Bugbot on. On GitLab, Bitbucket, Azure DevOps, and Origin, turn Bugbot on per repository.

On a team, members who can't change an installation's settings see **Request access** instead of the switch on a repository where Bugbot is off. Requesting emails your team admins a one-click link to turn Bugbot on for that repository, and the button changes to **Requested**. The repository stays off until an admin turns it on.

For a comparison with Security Reviewer, see [Security Review source control support](https://cursor.com/docs/security-review.md#source-control-support).

## CI check statuses

Bugbot publishes a status for each review run. On GitHub, this appears as a check named `Cursor Bugbot`. On Bitbucket, this appears as a build status with the key `cursor-bugbot`. On Azure DevOps, this appears as a status with the context `cursor-bugbot/review`. The status uses these conclusions:

- `success`: Bugbot found no issues, and there are no unresolved Bugbot comments from earlier runs.
- `neutral`: Bugbot found issues, the run was cancelled by a newer commit, or Bugbot hit an internal error. This is the default conclusion when Bugbot reports findings.
- `failure`: Bugbot found issues and the check is configured to fail on unresolved issues.

If you use branch protection, require the Bugbot check or build status to make sure Bugbot runs before merge. Requiring the status alone does not block merges on findings because findings default to `neutral`. If fail-on-unresolved-issues behavior is available for your organization, enable it to make unresolved findings produce a failing status. Bugbot does not emit a `skipped` conclusion.

When Bugbot Autofix is enabled, GitHub may also show a separate `Cursor Bugbot Autofix` check. That check only uses `success` or `neutral`.

## Configuration

### Individual

### Repository settings

Enable or disable Bugbot per repository from your installations list. Bugbot runs only on PRs you author.

### Personal settings

- Run **only when mentioned** by commenting `cursor review` or `bugbot run`
- Run **only once** per PR, skipping subsequent commits

Turn learning on or off per organization from the organization's page in [Bugbot](https://cursor.com/automations/from-cursor/bugbot). Open **Organizations**, select an organization, and use the **Automatically Learn Rules** switch. **Manage learning** on the [repository rules](https://cursor.com/dashboard/bugbot/repository-rules) page opens the same switch. [Azure DevOps](https://cursor.com/docs/integrations/azure-devops.md#differences-from-other-providers) does not have this switch.

### Team

### Repository settings

Team users and admins can enable Bugbot per repository, configure allow/deny lists for reviewers, and set:

- Run **only once** per PR per installation, skipping subsequent commits

Bugbot runs for all contributors to enabled private repositories, regardless of team membership. On public repositories, the **Public repositories** switch in Bugbot's **Team** settings decides whether automatic reviews cover pull requests from people outside the team and from bots. If no admin has changed it, it's on for teams created before October 22, 2026 and off for teams created since. The switch doesn't affect manual reviews started with `cursor review` or `bugbot run`.

### Personal settings

Team members can override settings for their own PRs:

- Run **only when mentioned** by commenting `cursor review` or `bugbot run`
- Run **only once** per PR, skipping subsequent commits
- **Enable reviews on draft PRs** to include draft pull requests in automatic reviews

### Enterprise

### Repository settings

Enterprise admins can enable Bugbot per repository, configure allow/deny lists for reviewers, and set:

- Run **only once** per PR per installation, skipping subsequent commits

Bugbot runs for all contributors to enabled private repositories, regardless of team membership. On public repositories, the **Public repositories** switch in Bugbot's **Team** settings decides whether automatic reviews cover pull requests from people outside the team and from bots. If no admin has changed it, it's on for teams created before October 22, 2026 and off for teams created since. The switch doesn't affect manual reviews started with `cursor review` or `bugbot run`.

### Personal settings

Enterprise users can override settings for their own PRs:

- Run **only when mentioned** by commenting `cursor review` or `bugbot run`
- Run **only once** per PR, skipping subsequent commits
- **Enable reviews on draft PRs** to include draft pull requests in automatic reviews

### Repository config file

You can optionally configure Bugbot from a repo-level YAML file:

```yaml
# .cursor/config/bugbot.yaml
version: 1

triggers:
  drafts: false
  frequency: everyPush # everyPush | oncePerPr

review:
  effort: default # low | default | high | smart
  smartPrompt: ""
  incremental: true

prSummary:
  mode: comment # disabled | description | comment
  riskScore: true

autofix:
  mode: disabled # disabled | newBranch | existingBranch
```

All fields are optional. If the file is missing, Bugbot uses the same behavior as before. If a field is missing or invalid, Bugbot ignores that field and falls back to the next setting in the precedence order. Bugbot ignores files larger than 64 KB.

Bugbot reads `.cursor/config/bugbot.yaml` at the repo root from the PR's base branch, the branch the PR merges into. The file must be committed and pushed to the repo, and its settings apply only to that repo. Bugbot does not read the PR head version, so a PR cannot change how Bugbot reviews itself. Use code review and `CODEOWNERS` to control who can change this file.

Precedence order, from highest to lowest:

- The PR author's personal overrides, for their own PRs.
- `.cursor/config/bugbot.yaml`.
- Team and organization settings from the dashboard.

`autofix.mode` can lower the [Autofix](https://cursor.com/docs/bugbot.md#autofix) mode from your dashboard settings, but it can't raise it. For example, it can change **Commit to Existing Branch** to `newBranch` or `disabled`, but it can't turn Autofix on when the dashboard has it off.

## Analytics

Open [Bugbot in Automations](https://cursor.com/automations/from-cursor/bugbot) to view review activity and outcomes.

## API

Enterprise teams can use the Bugbot API to trigger reviews and retrieve per-review analytics. Create an API key from [Cursor Dashboard → API Keys](https://cursor.com/dashboard/api) and authenticate with [Basic Authentication](https://cursor.com/docs/api.md#basic-authentication).

### Trigger a review

POST

`/bugbot/review`

Queue a Bugbot review for a pull request or merge request. The request returns when the review is queued; the review runs asynchronously.

Requires an API key with `admin:*` scope. The endpoint is limited to 30 requests per minute per team.

Set `dryRun` to `true` to run the full analysis pipeline without posting review comments, inline comments, checks, or other SCM side effects. Dry-run reviews still persist findings and are billed like normal reviews. Retrieve them with `GET /analytics/team/bugbot-reviews`. Dry-run requests have an additional limit of 10 requests per minute per team.

#### Request Body

`prUrl` string (required)

Full GitHub pull request or GitLab merge request URL.

`dryRun` boolean (optional)

When `true`, run analysis and persist findings without posting anything to the SCM provider. Default: `false`.

```bash
curl --request POST \
  --url https://api.cursor.com/bugbot/review \
  -u YOUR_API_KEY: \
  --header 'Content-Type: application/json' \
  --data '{
    "prUrl": "https://github.com/your-org/your-repo/pull/42"
  }'
```

```bash
curl --request POST \
  --url https://api.cursor.com/bugbot/review \
  -u YOUR_API_KEY: \
  --header 'Content-Type: application/json' \
  --data '{
    "prUrl": "https://github.com/your-org/your-repo/pull/42",
    "dryRun": true
  }'
```

**Response:**

```json
{
  "outcome": "success",
  "message": "Bugbot review queued",
  "request_id": "6e0d261c-86a2-4383-89f0-9162c1c10662",
  "dry_run": false
}
```

A dry-run response uses `"message": "Bugbot dry-run review queued"` and `"dry_run": true`.

Save `request_id` so you can match the completed review in the analytics endpoint.

If Bugbot cannot review the pull request, the endpoint returns `400 Bad Request` with the reason:

```json
{
  "outcome": "error",
  "message": "Bugbot is disabled for this repository"
}
```

### Review analytics

GET

`/analytics/team/bugbot-reviews`

Return one item per completed Bugbot review, including the pull request author, reviewed commit, findings count, billed cost, and per-finding resolution data.

Includes both posted reviews and dry-run reviews. Posted findings are identified by `comment_id` and `resolution_status`. Dry-run findings return `title`, `description`, and `locations` instead because nothing is posted to the SCM.

Requires an API key with `read:*` scope.

#### Query Parameters

`startDate` string (optional)

Start of the analytics range. Defaults to 7 days ago. See [Date Formats](https://cursor.com/docs/account/teams/analytics-api.md#date-formats).

`endDate` string (optional)

End of the analytics range. Defaults to now. See [Date Formats](https://cursor.com/docs/account/teams/analytics-api.md#date-formats).

`repo` string (optional)

Repository filter in `host/owner/repo` form. Protocol and `.git` suffix are optional.

`prNumber` number (optional)

Pull request or merge request number.

`page` number (optional)

Page number for pagination. Default: `1`.

`pageSize` number (optional)

Number of reviews per page. Default: `100`, max: `250`.

`dryRun` boolean (optional)

Filter to dry-run (`true`) or posted (`false`) reviews only.

```bash
curl --get https://api.cursor.com/analytics/team/bugbot-reviews \
  -u YOUR_API_KEY: \
  --data-urlencode 'startDate=2026-06-01' \
  --data-urlencode 'endDate=2026-06-29' \
  --data-urlencode 'repo=github.com/your-org/your-repo' \
  --data-urlencode 'prNumber=42' \
  --data-urlencode 'page=1' \
  --data-urlencode 'pageSize=100'
```

```bash
curl --get https://api.cursor.com/analytics/team/bugbot-reviews \
  -u YOUR_API_KEY: \
  --data-urlencode 'dryRun=true' \
  --data-urlencode 'repo=github.com/your-org/your-repo' \
  --data-urlencode 'prNumber=42'
```

**Response (posted review):**

```json
{
  "data": [
    {
      "request_id": "6e0d261c-86a2-4383-89f0-9162c1c10662",
      "timestamp": "2026-06-29T19:42:18.000Z",
      "repo": "github.com/your-org/your-repo",
      "repo_node_id": "R_kgDOABCDEF",
      "pr_author": "octocat",
      "pr_number": 42,
      "commit_sha": "9f3c2a1b7d8e4f5061728394a5b6c7d8e9f0a1b2",
      "bugs_found": 2,
      "cost_cents": 42.5,
      "dry_run": false,
      "publication_status": "posted",
      "bugs": [
        {
          "comment_id": "2147483999",
          "resolution_status": "resolved",
          "severity": "high"
        },
        {
          "comment_id": "2147484000",
          "resolution_status": "unresolved",
          "severity": "medium"
        }
      ]
    }
  ],
  "pagination": {
    "page": 1,
    "pageSize": 100,
    "totalItems": 1,
    "totalPages": 1,
    "hasNextPage": false,
    "hasPreviousPage": false
  },
  "params": {
    "metric": "bugbot-reviews",
    "teamId": 12345,
    "startDate": "2026-06-01",
    "endDate": "2026-06-29",
    "repo": "github.com/your-org/your-repo",
    "prNumber": 42,
    "page": 1,
    "pageSize": 100
  }
}
```

**Response (dry-run review):**

```json
{
  "data": [
    {
      "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "timestamp": "2026-06-29T20:15:03.000Z",
      "repo": "github.com/your-org/your-repo",
      "repo_node_id": "R_kgDOABCDEF",
      "pr_author": "octocat",
      "pr_number": 42,
      "commit_sha": "9f3c2a1b7d8e4f5061728394a5b6c7d8e9f0a1b2",
      "bugs_found": 1,
      "cost_cents": null,
      "dry_run": true,
      "publication_status": "dry_run",
      "bugs": [
        {
          "comment_id": null,
          "resolution_status": null,
          "severity": "medium",
          "title": "Unbounded retry loop",
          "description": "retry() recurses without a ceiling.",
          "locations": [
            { "file": "src/net.ts", "start_line": 5, "end_line": 9 }
          ]
        }
      ]
    }
  ],
  "pagination": {
    "page": 1,
    "pageSize": 100,
    "totalItems": 1,
    "totalPages": 1,
    "hasNextPage": false,
    "hasPreviousPage": false
  },
  "params": {
    "metric": "bugbot-reviews",
    "teamId": 12345,
    "startDate": "2026-06-01",
    "endDate": "2026-06-29",
    "repo": "github.com/your-org/your-repo",
    "prNumber": 42,
    "dryRun": true,
    "page": 1,
    "pageSize": 100
  }
}
```

`pr_author` is the SCM username of the pull request author. Use it with `cost_cents` to attribute Bugbot spend to authors. `repo_node_id`, `pr_author`, `pr_number`, `commit_sha`, `cost_cents`, `bugs[].comment_id`, `bugs[].resolution_status`, and `bugs[].severity` may be `null` when unavailable. `cost_cents` is `null` when the review is not billed separately. For dry-run reviews, `bugs[].title`, `bugs[].description`, and `bugs[].locations` carry the finding content. Dry-run findings have `comment_id: null` and `resolution_status: null` because nothing is posted to the SCM.

### Trigger and retrieve a review

1. Call `POST /bugbot/review` with the pull request URL. Pass `"dryRun": true` to analyze without posting to the SCM.
2. Save the returned `request_id`.
3. Poll `GET /analytics/team/bugbot-reviews`, filtering by `repo` and `prNumber`. Use `dryRun=true` when you triggered a dry-run review.
4. Find the item whose `request_id` matches the trigger response.

Analytics may take a short time to become available after a review is queued.

## Incremental reviews

By default, Bugbot reviews only the changes since the previous Bugbot review. Turn off **Incremental Review** in [Bugbot Automations](https://cursor.com/automations/from-cursor/bugbot) to review the full pull request diff on every push.

![Incremental Review setting in Bugbot Automations](/docs-static/images/bugbot/incremental-review-setting.png)

## PR summaries

Bugbot writes a summary of each pull request it reviews. **Post PR Summary** in [Bugbot Automations](https://cursor.com/automations/from-cursor/bugbot) controls where the summary goes:

- **In Description** (default): Bugbot adds the summary to the pull request description and updates it on each review.
- **As Comment**: Bugbot posts the summary as a comment and updates that comment on each review.
- **Off**: Bugbot posts no summary.

Turn summaries on or off for your own PRs with the **PR Summaries** personal setting. Choose **On**, **Off**, or **Use Installation Default**.

## Effort Levels

Effort levels control how much time Bugbot spends reasoning during a review. Higher effort levels can find more bugs, but each review may take longer and take up more usage.

Choose from these effort levels:

- **Low**: Optimizes for cost, with quality close to Default. Reviews are cheaper and take longer.
- **Default**: Optimizes for efficiency and speed. Reviews are less expensive, but Bugbot may find fewer bugs.
- **High**: Spends more time reasoning. Reviews are more expensive and take longer, but Bugbot may find more bugs.
- **Smart**: Lets you describe when Bugbot should use Low, Default, or High. Cursor dynamically sets effort levels based on your instructions. To choose, Smart reads your instructions with the PR's title, author, repository name, and diff (trimmed on large PRs). It doesn't read the PR description, labels, or `BUGBOT.md`. Smart uses Low only when your instructions ask for it, and uses Default when they don't clearly call for another level. When Smart picks Default or High and the review finds issues, the review comment names the effort level it used.

Effort levels are available only for usage-based Bugbot plans.

## Rules

Guide reviews with team rules, repository rules, and project `.cursor/BUGBOT.md` files.

### Team rules

Team admins can create rules in [Bugbot Automations](https://cursor.com/automations/from-cursor/bugbot) that apply to all repositories in the team. These rules are available to every enabled repository, making it easy to enforce organization-wide standards.

When Team Rules, repository rules, and project rule files all apply, Bugbot merges them into one review-rules block. Order of inclusion: Team Rules → project .cursor/BUGBOT.md (including nested files) → learned rules → manual rules.

### Rule limits

Each rule is truncated at 30,000 characters when included in a review. Every `.md` or `.mdc` file linked from a `.cursor/BUGBOT.md` file counts as its own rule with its own 30,000-character limit, and Bugbot loads each linked path once. The combined rules Bugbot includes for a review are capped at 100,000 characters. If you exceed that combined cap, some rules may be omitted. Required team rules are prioritized over non-required rules.

### See which rules a review used

Comment `bugbot run verbose=true` or `cursor review verbose=true` on a pull request. Bugbot posts a table of every rule included in that run and flags any that were truncated or omitted.

### Repository rules

#### Project rules

Create `.cursor/BUGBOT.md` files to provide project-specific context for reviews. Bugbot always includes the root `.cursor/BUGBOT.md` file and any additional files found while traversing upward from changed files.

```bash
project/
  .cursor/BUGBOT.md          # Always included (project-wide rules)
  backend/
    .cursor/BUGBOT.md        # Included when reviewing backend files
    api/
      .cursor/BUGBOT.md      # Included when reviewing API files
  frontend/
    .cursor/BUGBOT.md        # Included when reviewing frontend files
```

Cursor [project rules](https://cursor.com/docs/rules.md) (`*.mdc` files in `.cursor/rules/`) do not apply to Bugbot runs.

#### Learned rules

Turn learning on or off per organization with the **Automatically Learn Rules** switch on the organization's page in [Bugbot](https://cursor.com/automations/from-cursor/bugbot). Open **Organizations** and select an organization, or use **Manage learning** on the [repository rules](https://cursor.com/dashboard/bugbot/repository-rules) page. Where that switch exists, manual rules apply only while learning is on, so turning learning off also stops manual rules from applying. [Azure DevOps](https://cursor.com/docs/integrations/azure-devops.md#differences-from-other-providers) does not have **Automatically Learn Rules**. Repository rules you write by hand still apply there.

Rules are generated automatically from your team's activity on GitHub for that repository or by manually backfilling from the history of the repository.

Bugbot learns from a pull request when it's merged or closed. It posts nothing on the pull request, and each learning run counts toward Bugbot usage like a review. Learning doesn't run on a repository set to manual-only or, on an individual account, when your personal settings run Bugbot **only when mentioned**. Turning off **Automatically Learn Rules** stops it for that organization.

You can also teach Bugbot new rules inline by commenting `@cursor remember [fact]` on any PR. Bugbot saves the fact as a learned rule and applies it to future reviews.

Cursor will automatically enable or disable rules as it learns more about your team's activity over time.

| Field            | Description                                                                                                    |
| :--------------- | :------------------------------------------------------------------------------------------------------------- |
| **Name**         | Short title for the rule.                                                                                      |
| **Rule content** | The instructions Bugbot should follow (i.e. style gates, paths, or review expectations).                       |
| **Scoped paths** | Optional glob patterns such as `src/components/**`. Leave empty to apply the rule across the whole repository. |

#### Manual rules

In [Bugbot repository rules](https://cursor.com/dashboard/bugbot/repository-rules), you can create manual rules for individual repositories. Like learned rules, manual rules apply only when learning is enabled for the organization and the repository. [Azure DevOps](https://cursor.com/docs/integrations/azure-devops.md#differences-from-other-providers) does not have that switch, so repository rules you write by hand still apply there.

| Field            | Description                                                                                                    |
| :--------------- | :------------------------------------------------------------------------------------------------------------- |
| **Name**         | Short title for the rule.                                                                                      |
| **Rule content** | The instructions Bugbot should follow (i.e. style gates, paths, or review expectations).                       |
| **Scoped paths** | Optional glob patterns such as `src/components/**`. Leave empty to apply the rule across the whole repository. |

#### Rule analytics

**Analytics** on a Bugbot rule show how it performs on real PRs:

| Metric              | Meaning                                                    |
| :------------------ | :--------------------------------------------------------- |
| **Issues found**    | Number of findings Bugbot reported that involve this rule. |
| **PRs reviewed**    | Number of pull requests where those findings appeared.     |
| **Accepted issues** | Number of findings your team accepted.                     |
| **Acceptance rate** | Percentage of findings that were accepted.                 |

#### Examples

### Security: Flag any use of eval() or exec()

```text
If any changed file contains the string pattern /\beval\s*\(|\bexec\s*\(/i, then:
- Add a blocking Bug with title "Dangerous dynamic execution" and body:
  "Usage of eval/exec was found. Replace with safe alternatives or justify with a detailed comment and tests."
- Assign the Bug to the PR author.
- Apply label "security".
```

### OSS licenses: Prevent importing disallowed licenses

```text
If the PR modifies dependency files (package.json, pnpm-lock.yaml, yarn.lock, requirements.txt, go.mod, Cargo.toml), then:
- Run the built-in License Scan.
- If any new or upgraded dependency has license in {GPL-2.0, GPL-3.0, AGPL-3.0}, then:
  - Add a blocking Bug titled "Disallowed license detected"
  - Include the offending package names, versions, and licenses in the Bug body
  - Apply labels "compliance" and "security"
```

### Language standards: Flag React componentWillMount usage

```text
For files matching **/*.{js,jsx,ts,tsx} in React projects:
If a changed file contains /componentWillMount\s*\(/, then:
- Add a blocking Bug titled "Deprecated React lifecycle method"
- Body: "Replace componentWillMount with constructor or useEffect. See React docs."
- Suggest an autofix snippet that migrates side effects to useEffect.
```

### Standards: Require tests for backend changes

```text
If the PR modifies files in {server/**, api/**, backend/**} and there are no changes in {**/*.test.*, **/__tests__/**, tests/**}, then:
- Add a blocking Bug titled "Missing tests for backend changes"
- Body: "This PR modifies backend code but includes no accompanying tests. Please add or update tests."
- Apply label "quality"
```

### Style: Disallow TODO comments

```text
If any changed file contains /(?:^|\s)(TODO|FIXME)(?:\s*:|\s+)/, then:
- Add a non-blocking Bug titled "TODO/FIXME comment found"
- Body: "Replace TODO/FIXME with a tracked issue reference, e.g., `TODO(#1234): ...`, or remove it."
- If the TODO already references an issue pattern /#\d+|[A-Z]+-\d+/, mark the Bug as resolved automatically.
```

## Run in your agent

Use the `/review-bugbot` or `/review` skills to run Bugbot from your agent before you push the code.

**What diff is reviewed:** By default, `/review-bugbot` reviews your branch changes: every change relative to the base branch, including committed and uncommitted changes. Ask it to review only your uncommitted changes when you want narrower feedback.

**Against which branch:** `/review-bugbot` compares against your default base branch. When your base branch isn't the default (such as `main`), tell the agent which branch to compare against or let it infer from the context.

![Running the /review-bugbot skill from the agent input](/docs-static/images/bugbot/review-bugbot-skill.png)

### Sync with your pull request

`/review-bugbot` reviews stay in sync with Bugbot on your connected SCM (GitHub, GitLab, or Bitbucket).

Under the hood, `/review-bugbot` stores the [patch ID](https://git-scm.com/docs/git-patch-id) of the reviewed diff. When Bugbot on your SCM sees a diff with the same patch ID, it skips the review and leaves a comment noting it already reviewed that diff.

A common use case: run `/review-bugbot`, then open a pull request with the same diff, and Bugbot recognizes the review and skips the remote PR review.

`/review` and `/review-bugbot` are available in Cursor 3.7+, at [cursor.com/agents](https://cursor.com/agents), and in the [Cursor CLI](https://cursor.com/docs/cli/overview.md).

## Autofix

Bugbot Autofix automatically spawns a [Cloud Agent](https://cursor.com/docs/cloud-agent.md) to fix bugs found during PR reviews.

### How it works

When Bugbot finds bugs during a PR review, it can automatically:

1. Spawn a Cloud Agent to analyze and fix the reported issues
2. Push fixes to the existing branch or a new branch (depending on your settings)
3. Post a comment on the original PR with the results

![Bugbot Autofix comment on a PR](/docs-static/images/bugbot/bugbot-autofix-comment.png)

### Configuration

Configure autofix behavior in [Bugbot Automations](https://cursor.com/automations/from-cursor/bugbot).

### Individual

Individual users can configure their autofix preference in their personal Bugbot settings:

- **Use Installation Default** — Follow your organization's settings
- **Off** — autofix is disabled; use manual "Fix in Cursor" or "Fix in Web" links
- **Create New Branch** (Recommended) — Push fixes to a new branch
- **Commit to Existing Branch** — Push fixes to your branch (max 3 attempts per PR to prevent loops)

User settings override team defaults for your own PRs.

### Team

Team admins can set a default autofix mode for all team members in a GitHub organization:

- **Off** — autofix is disabled by default
- **Create New Branch** (Recommended) — Push fixes to a new branch for team members
- **Commit to Existing Branch** — Push fixes directly to the PR branch (max 3 attempts per PR to prevent loops)

Individual team members can override these defaults in their personal settings.

Available autofix modes depend on your repository provider:

| Provider                                            | Create New Branch | Commit to Existing Branch |
| :-------------------------------------------------- | :---------------- | :------------------------ |
| GitHub, [Origin](https://cursor.com/docs/origin.md) | Yes               | Yes                       |
| GitLab, Bitbucket                                   | No                | Yes                       |
| Azure DevOps                                        | No                | No                        |

Installation settings offer only the modes your provider supports. If your personal setting picks a mode your provider doesn't support, Bugbot skips the autofix run for that PR.

On a stacked PR, where the base branch isn't the repository's default branch, **Commit to Existing Branch** doesn't push to your branch. On GitHub and Origin, Autofix delivers the fix on a new branch instead; apply it by commenting `@cursor push <sha>` on the PR. On GitLab and Bitbucket, Autofix skips stacked PRs.

Autofix uses your **Default agent model** from [Settings → Models](https://cursor.com/dashboard/settings). If you haven't set a personal model preference, autofix falls back to your team's default model (if you're on a team) or the system default.

### Requirements

Autofix requires:

- Additional usage available: [prepaid credit](https://cursor.com/docs/models-and-pricing.md#top-ups-and-spending-caps) on The X Subscription, or [on-demand usage](https://cursor.com/docs/account/pricing/legacy-cursor-plans.md#on-demand-usage-on-legacy-plans) enabled on a legacy Cursor plan
- Storage enabled (not in Legacy Privacy Mode)

### Billing

Autofix uses Cloud Agent credits and is billed at your plan rates. Cloud Agent billing follows your existing [pricing plan](https://cursor.com/docs/models-and-pricing.md).

## MCP support

Bugbot is integrated with your [MCP servers](https://cursor.com/docs/mcp.md) so your AI tools can interact with Bugbot directly. Use the MCP server to provide additional tools to guide Bugbot's review process.

To get started:

1. Follow the [MCP documentation](https://cursor.com/docs/mcp.md) for MCP server setup instructions.
2. Add the tools to [Bugbot in Automations](https://cursor.com/automations/from-cursor/bugbot).

MCP support is available on Team and Enterprise plans only.

## Admin Configuration API

Team admins can use the Bugbot Admin API to manage repositories and control which users can use Bugbot. Use it to automate repository management, enable Bugbot across multiple repositories, or integrate user provisioning with internal tools.

### Authentication

All endpoints require a team Admin API Key passed as a Bearer token:

```bash
Authorization: Bearer $API_KEY
```

To create an API key:

1. Visit [API Keys in the Cursor dashboard](https://cursor.com/dashboard/api)
2. Click **New API Key**
3. Save the API key

All endpoints are rate-limited to 60 requests per minute per team.

### Enabling or disabling repositories

Use the `/bugbot/repo/update` endpoint to toggle Bugbot on or off for a repository:

```bash
curl -X POST https://api.cursor.com/bugbot/repo/update \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "repoUrl": "https://github.com/your-org/your-repo",
    "enabled": true,
    "manualTriggerOnly": false
  }'
```

**Parameters:**

- `repoUrl` (string, required): The full URL of the repository
- `enabled` (boolean, required): `true` to enable Bugbot, `false` to disable it
- `manualTriggerOnly` (boolean, optional): When `true`, Bugbot won't run automatically on PR updates for this repository. Manual triggers, such as commenting `cursor review` or `bugbot run`, still work.

The Automations UI may take a moment to reflect changes made through the API due to caching. The API response shows the current state in the database.

For Azure DevOps repositories, turn Bugbot on or off in [Bugbot in Automations](https://cursor.com/automations/from-cursor/bugbot). This endpoint returns `400` for repository URLs on `dev.azure.com` or `*.visualstudio.com`.

### Listing repositories

Use the `/bugbot/repos` endpoint to list all repositories with their Bugbot settings for your team:

```bash
curl https://api.cursor.com/bugbot/repos \
  -H "Authorization: Bearer $API_KEY"
```

The response includes each repository's enabled status, manual-only setting, and timestamps.

### Managing user access

Use the `/bugbot/user/update` endpoint to control which GitHub, GitLab, or Bitbucket users can use your team's Bugbot licenses. Enterprises use this to integrate Bugbot provisioning with internal access-request tools.

#### Prerequisites

Before calling this endpoint, enable an allowlist or blocklist mode in your [team Bugbot settings](https://cursor.com/automations/from-cursor/bugbot):

- **Allowlist mode ("Only...")**: Only users on the list can use Bugbot
- **Blocklist mode ("Everyone but...")**: All users can use Bugbot except those on the list

If neither mode is enabled, the API returns an error.

#### Adding or removing a user

```bash
curl -X POST https://api.cursor.com/bugbot/user/update \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "octocat",
    "allow": true
  }'
```

**Parameters:**

- `username` (string, required): The GitHub, GitLab, or Bitbucket username (case-insensitive)
- `allow` (boolean, required): Whether to grant or revoke access

How `allow` behaves depends on the active mode:

| Mode      | `allow: true`                                | `allow: false`                             |
| --------- | -------------------------------------------- | ------------------------------------------ |
| Allowlist | Adds user to list (can use Bugbot)           | Removes user from list (cannot use Bugbot) |
| Blocklist | Removes user from blocklist (can use Bugbot) | Adds user to blocklist (cannot use Bugbot) |

**Response:**

```json
{
  "outcome": "success",
  "message": "Updated team-level allowlist for @octocat",
  "updatedTeamSettings": true,
  "updatedInstallations": 0
}
```

The allowlist is stored at the team level and applies across all GitHub, GitLab, and Bitbucket installations owned by that team. Usernames are normalized to lowercase.

#### Example: provisioning users through an internal tool

Connect this API to an internal access-request portal. When an employee requests Bugbot access, the portal calls the API to add them. When they leave or lose access, it calls the API to remove them.

**Grant access:**

```bash
curl -X POST https://api.cursor.com/bugbot/user/update \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"username": "employee-scm-username", "allow": true}'
```

**Revoke access:**

```bash
curl -X POST https://api.cursor.com/bugbot/user/update \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"username": "employee-scm-username", "allow": false}'
```

## Pricing

Bugbot uses usage-based billing.

Bugbot pricing changed with the May 2026 pricing update. See the [announcement blog post](https://cursor.com/blog/may-2026-bugbot-changes) for background. If you're still on the old seat-based plan, see [legacy Bugbot pricing](https://cursor.com/docs/bugbot/legacy-pricing.md).

### Billing

Each review is billed once, to the team or personal account that has Bugbot turned on for the repository. The team the PR author belongs to doesn't change who's billed.

### Individuals

### Usage-based billing

Bugbot includes:

- Reviews on all PRs across your repositories
- Access to Bugbot rules
- The ability to set the effort level Bugbot uses for reviews

Bugbot first consumes your included usage, then bills additional reviews from your prepaid credit, or from on-demand spend on a legacy Cursor plan. See the [pricing page](https://cursor.com/pricing#bugbot) for current rates.

### Getting started

Subscribe through your account settings.

### Teams

### Usage-based billing

Bugbot Teams includes:

- Code reviews on all PRs
- Analytics and reporting
- The ability to set the effort level Bugbot uses for reviews
- Advanced rules and settings

Bugbot Teams bills from the team's prepaid credit, or from on-demand spend on a legacy Teams plan. See the [pricing page](https://cursor.com/pricing#bugbot) for current rates.

### Getting started

Subscribe through your team dashboard to enable billing.

## Troubleshooting

If Bugbot isn't working:

1. **Enable verbose mode** by commenting `cursor review verbose=true` or `bugbot run verbose=true` for detailed logs, which Bugbot rules loaded, and a request ID
2. **Check permissions** to verify Bugbot has repository access
3. **Verify installation** to confirm your repository provider integration is installed and enabled

Include the request ID from verbose mode when reporting issues.

## FAQ

### Does Bugbot read PR comments?

Yes. Bugbot reads both top-level and inline pull request comments from connected providers and includes them as context during reviews. This helps avoid duplicate suggestions and allows Bugbot to build on prior feedback from reviewers.

### How do I see which rules Bugbot used?

Comment `bugbot run verbose=true` or `cursor review verbose=true` on the pull request. Bugbot posts a table of every rule included in that run and flags any that were truncated or omitted. See [Rule limits](https://cursor.com/docs/bugbot.md#rule-limits) if a rule is missing or cut off.

### Is Bugbot privacy-mode compliant?

Yes, Bugbot follows the same privacy compliance as Cursor and processes data identically to other Cursor requests.

### Does Bugbot read credential files?

Bugbot doesn't read the contents of files whose path looks like a credential file, such as `.env`, key files like `id_rsa` or `*.pem`, `credentials.json`, `*.tfvars`, and Terraform state. Templates such as `.env.example` are reviewed normally. Other files are reviewed as usual, including source code that hardcodes a key.

### What happens when I use all included Bugbot usage?

When you use all included Bugbot usage, additional Bugbot reviews bill from your prepaid credit, or from on-demand spend on a legacy Cursor plan.

### How do I give Bugbot access to a self-hosted source control instance?

See the setup and networking guides on the respective integration pages:

- [GitHub Enterprise Server](https://cursor.com/docs/integrations/github.md#setup)
- [GitLab Self-Hosted](https://cursor.com/docs/integrations/gitlab.md#setup)
- [Bitbucket Data Center](https://cursor.com/docs/integrations/bitbucket.md#setup)

## Related

- [Bugbot help](https://cursor.com/help/ai-features/bugbot.md)


---

## Sitemap

[Overview of all docs pages](/llms.txt)
