# Issue Search and Filtering

Sources: GitHub CLI documentation, GitHub search syntax reference

---

## Overview

Two commands handle issue search in the gh CLI:

- `gh search issues` — searches across GitHub globally, across repos, or across an org
- `gh issue list --search` — searches within a single repository using GitHub search syntax

Use `gh search issues` when you need cross-repo or org-wide results. Use `gh issue list --search` when you are already scoped to one repo and want to combine structured flags with search qualifiers.

---

## gh search issues

### Full Flag Reference

| Flag | Type | Description |
|------|------|-------------|
| `--assignee <login>` | string | Issues assigned to this user |
| `--author <login>` | string | Issues created by this user |
| `--closed <date>` | date | Filter by closed date (e.g. `>2024-01-01`) |
| `--commenter <login>` | string | Issues commented on by this user |
| `--comments <count>` | range | Filter by comment count (e.g. `>10`, `<5`, `5..20`) |
| `--created <date>` | date | Filter by creation date |
| `--include-prs` | bool | Include pull requests in results |
| `--interactions <count>` | range | Filter by total interaction count |
| `--involves <login>` | string | Issues involving this user (author, assignee, commenter, or mention) |
| `--label <name>` | string | Filter by label (repeatable for AND logic) |
| `--language <lang>` | string | Filter by repository primary language |
| `--limit, -L <n>` | int | Maximum results to return (default: 30) |
| `--locked` | bool | Only locked issues |
| `--match <field>` | string | Restrict text match to `title`, `body`, or `comments` |
| `--mentions <login>` | string | Issues mentioning this user |
| `--milestone <name>` | string | Filter by milestone title |
| `--no-assignee` | bool | Issues with no assignee |
| `--no-label` | bool | Issues with no label |
| `--no-milestone` | bool | Issues with no milestone |
| `--no-project` | bool | Issues not in any project |
| `--order <dir>` | string | `asc` or `desc` (default: desc) |
| `--owner <login>` | string | Filter by org or user owner |
| `--project <number>` | string | Filter by project |
| `--reactions <count>` | range | Filter by reaction count |
| `--repo, -R <repo>` | string | Filter by repo (repeatable) |
| `--sort <field>` | string | `comments`, `created`, `interactions`, `reactions`, `updated` |
| `--state <state>` | string | `open` or `closed` |
| `--team-mentions <team>` | string | Issues mentioning this team |
| `--updated <date>` | date | Filter by last updated date |
| `--visibility <vis>` | string | `public`, `private`, or `internal` |
| `--json <fields>` | string | Output as JSON with specified fields |
| `--jq, -q <expr>` | string | JQ filter applied to JSON output |
| `--template, -t <tmpl>` | string | Go template for output |
| `--web, -w` | bool | Open results in browser |

### Date and Numeric Range Syntax

Date values accept ISO 8601 dates; numeric fields (comments, reactions, interactions) accept the same operators:

| Syntax | Meaning |
|--------|---------|
| `>2024-01-01` | After January 1, 2024 |
| `<2024-06-01` | Before June 1, 2024 |
| `2024-01-01..2024-06-01` | Between two dates (inclusive) |
| `>=2024-01-01` | On or after |
| `>10` | More than 10 (numeric) |
| `5..20` | Between 5 and 20 inclusive (numeric) |

---

## gh issue list --search

`gh issue list` accepts a `--search` flag that passes a raw GitHub search query string. Structured flags and `--search` qualifiers are ANDed together.

```bash
gh issue list --search "<query>" [flags]
```

### Structured Flags for gh issue list

| Flag | Description |
|------|-------------|
| `--state, -s <state>` | `open`, `closed`, or `all` (default: open) |
| `--assignee, -a <login>` | Filter by assignee |
| `--author, -A <login>` | Filter by author |
| `--label, -l <name>` | Filter by label (repeatable) |
| `--milestone <name>` | Filter by milestone |
| `--mention <login>` | Filter by mention |
| `--limit, -L <n>` | Maximum results (default: 30) |
| `--json <fields>` | JSON output |
| `--jq, -q <expr>` | JQ filter |
| `--web, -w` | Open in browser |

---

## GitHub Search Qualifier Reference

These qualifiers work inside `--search` strings and as positional query arguments to `gh search issues`.

### State and Type

| Qualifier | Description |
|-----------|-------------|
| `is:open` | Open issues |
| `is:closed` | Closed issues |
| `is:issue` | Issues only (excludes PRs) |
| `is:pr` | Pull requests only |
| `is:locked` | Locked conversations |
| `is:merged` | Merged pull requests |

### People

| Qualifier | Description |
|-----------|-------------|
| `author:<login>` | Created by user |
| `assignee:<login>` | Assigned to user |
| `mentions:<login>` | Mentions user |
| `commenter:<login>` | Commented on by user |
| `involves:<login>` | Author, assignee, commenter, or mention |
| `team:<org/team>` | Mentions team |
| `@me` | The authenticated user (usable in any people qualifier) |

### Labels, Milestones, Projects

| Qualifier | Description |
|-----------|-------------|
| `label:<name>` | Has this label (use multiple for AND) |
| `no:label` | Has no labels |
| `milestone:<name>` | In this milestone |
| `no:milestone` | Not in any milestone |
| `project:<number>` | In this project |
| `no:project` | Not in any project |

### Dates and Counts

| Qualifier | Description |
|-----------|-------------|
| `created:<date>` | Created on/before/after date |
| `updated:<date>` | Last updated on/before/after date |
| `closed:<date>` | Closed on/before/after date |
| `comments:<n>` | Number of comments |
| `reactions:<n>` | Number of reactions |
| `interactions:<n>` | Total interactions (comments + reactions) |

### Repository and Visibility

| Qualifier | Description |
|-----------|-------------|
| `repo:<owner>/<repo>` | Scoped to specific repo |
| `user:<login>` | All repos owned by user |
| `org:<name>` | All repos in org |
| `language:<lang>` | Repo primary language |
| `is:public` | Public repos only |
| `is:private` | Private repos only |

### Linked, Reason, and Sorting

| Qualifier | Description |
|-----------|-------------|
| `linked:pr` | Issues linked to a pull request |
| `linked:issue` | PRs linked to an issue |
| `reason:completed` | Closed as completed |
| `reason:"not planned"` | Closed as not planned |
| `sort:created-desc` | Newest first (default) |
| `sort:updated-desc` | Recently updated first |
| `sort:comments-desc` | Most commented first |
| `sort:reactions-desc` | Most reacted first |

---

## Cross-Repo and Org-Wide Search

Use `--owner` to scope `gh search issues` to all repos in an org. Use `--repo` (repeatable) to target specific repos.

```bash
# All open bugs in an org
gh search issues --owner my-org --label bug --state open

# All open issues assigned to me across an org
gh search issues --owner my-org --assignee @me --state open

# All open issues with no assignee in an org
gh search issues --owner my-org --no-assignee --state open

# Unassigned bugs in an org, sorted by reactions
gh search issues --owner my-org --label bug --no-assignee --sort reactions

# Search across two specific repos
gh search issues --repo owner/repo-a --repo owner/repo-b "authentication"

# Find issues with a specific label across org, sorted by age
gh search issues --owner my-org --label "needs-triage" --sort created --order asc

# Text search scoped to title only, org-wide
gh search issues --match title "authentication" --owner my-org
```

---

## Combining Search with --json and --jq

### Available JSON Fields

**gh issue list:** `number`, `title`, `state`, `author`, `assignees`, `labels`, `milestone`, `createdAt`, `updatedAt`, `closedAt`, `comments`, `url`, `body`, `reactions`, `projectItems`

**gh search issues:** `number`, `title`, `state`, `author`, `assignees`, `labels`, `repository`, `createdAt`, `updatedAt`, `url`, `comments`, `reactions`

### Extraction Patterns

```bash
# List issue numbers and titles as TSV
gh issue list --json number,title --jq '.[] | [.number, .title] | @tsv'

# Extract URLs of all open bugs
gh issue list --label bug --json url --jq '.[].url'

# Export to CSV
gh issue list --json number,title,state,createdAt \
  --jq '.[] | [.number, .title, .state, .createdAt] | @csv'

# Count open issues by label
gh issue list --state open --json labels \
  --jq '[.[].labels[].name] | group_by(.) | map({label: .[0], count: length}) | sort_by(-.count)'

# Count issues per assignee
gh issue list --state open --json assignees \
  --jq '[.[].assignees[].login] | group_by(.) | map({user: .[0], count: length})'

# Top 10 feature requests by reaction count
gh issue list --label enhancement --state open --json number,title,reactions \
  --jq 'sort_by(-.reactions.total_count) | .[:10] | .[] | "\(.reactions.total_count) \(.number): \(.title)"'

# Org health: unassigned open issues per repo
gh search issues --owner my-org --no-assignee --state open \
  --json number,repository \
  --jq 'group_by(.repository.nameWithOwner) | map({repo: .[0].repository.nameWithOwner, count: length}) | sort_by(-.count)'
```

---

## Common Search Recipes

### Unassigned Bugs

```bash
# In current repo
gh issue list --label bug --search "no:assignee" --state open

# Across org
gh search issues --owner my-org --label bug --no-assignee --state open
```

### Stale Issues (No Activity in 60+ Days)

```bash
# Issues not updated in 60 days
gh issue list --state open \
  --search "updated:<$(date -d '60 days ago' +%Y-%m-%d 2>/dev/null || date -v-60d +%Y-%m-%d)"

# Stale issues with no comments
gh issue list --state open --search "updated:<2024-01-01 comments:0"
```

### My Issues Across an Org

```bash
# Assigned to me
gh search issues --owner my-org --assignee @me --state open

# Authored by me
gh search issues --owner my-org --author @me --state open

# Involving me in any role
gh search issues --owner my-org --involves @me --state open
```

### High-Reaction Feature Requests

```bash
# In current repo, 10+ reactions
gh issue list --label enhancement --search "reactions:>10" --state open

# Across org, sorted by reactions
gh search issues --owner my-org --label enhancement --sort reactions --state open
```

### Issues Without Labels (Triage Queue)

```bash
# In current repo, oldest first
gh issue list --search "no:label" --state open --json number,title,createdAt,url \
  --jq 'sort_by(.createdAt) | .[] | "\(.number)\t\(.title)\t\(.url)"'

# Across org
gh search issues --owner my-org --no-label --state open --sort created --order asc
```

### Issues Closed as "Not Planned"

```bash
gh issue list --state closed --search 'reason:"not planned"'
```

### Issues Linked to Pull Requests

```bash
gh issue list --search "linked:pr" --state open
```

### Issues by Date Range

```bash
# Created in Q1 2024
gh issue list --search "created:2024-01-01..2024-03-31"

# Created this week
gh issue list \
  --search "created:>$(date -d '7 days ago' +%Y-%m-%d 2>/dev/null || date -v-7d +%Y-%m-%d)"
```

### Active Discussions (Many Comments)

```bash
# In current repo
gh issue list --search "comments:>20" --state open

# Across org, sorted by comment count
gh search issues --owner my-org --comments ">20" --sort comments --state open
```

### Text Search Scoped to Title Only

```bash
# Avoids false positives from body or comment matches
gh issue list --search "authentication in:title" --state open
```

### Issues I Commented On (Follow-Up)

```bash
gh search issues --owner my-org --commenter @me --state open \
  --sort updated --order desc --limit 50
```

### Weekly Closed Issues Report

```bash
gh issue list --state closed \
  --search "closed:>$(date -d '7 days ago' +%Y-%m-%d 2>/dev/null || date -v-7d +%Y-%m-%d)" \
  --json number,title,closedAt \
  --jq '.[] | "\(.number): \(.title)"'
```

---

## Pagination and Large Result Sets

Both commands default to 30 results. Increase with `--limit` (maximum 1000 for search API):

```bash
# Return up to 200 issues from a repo
gh issue list --limit 200 --state open

# Return up to 100 search results
gh search issues --owner my-org --label bug --limit 100
```

When a query would exceed 1000 results, split it by date range:

```bash
gh search issues --owner my-org --label bug --created "<2024-01-01" --limit 100
gh search issues --owner my-org --label bug --created ">=2024-01-01" --limit 100
```

For datasets beyond 1000 results, use the REST or GraphQL API with cursor-based pagination (covered in api-and-scripting.md).
