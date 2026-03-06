# API Access and Scripting

Sources: GitHub REST API documentation, GitHub GraphQL API reference, gh CLI manual

---

## gh api Core Mechanics

`gh api` makes authenticated HTTP requests to GitHub's REST (v3) or GraphQL (v4) API and prints the response. The endpoint argument is a path relative to `https://api.github.com`, or the literal string `graphql` for GraphQL requests.

### Flag Reference

| Flag | Short | Description |
|------|-------|-------------|
| `--method METHOD` | `-X` | HTTP method: GET, POST, PATCH, PUT, DELETE (default: GET, or POST when fields are provided) |
| `--raw-field key=value` | `-f` | Add a string field to the request body or query string |
| `--field key=value` | `-F` | Add a typed field: booleans, integers, `@filename` for file content, `{owner}`/`{repo}` placeholders |
| `--paginate` | | Fetch all pages of a paginated REST response automatically |
| `--slurp` | | Combine paginated results into a single JSON array (use with `--paginate`) |
| `--jq expression` | `-q` | Filter response through a jq expression before printing |
| `--template string` | `-t` | Format response using a Go template |
| `--silent` | | Suppress output; useful when only the exit code matters |
| `--cache duration` | | Cache responses for the given duration (e.g., `3600s`, `1h`) |
| `--hostname HOST` | | Target a GitHub Enterprise Server instance instead of github.com |
| `--header key:value` | `-H` | Add a custom HTTP header |
| `--input file` | | Read request body from a file (`-` for stdin) |

### Placeholder Substitution

`{owner}`, `{repo}`, and `{branch}` in endpoint paths are replaced from the current directory's repo context or `GH_REPO`. The `-F` flag also expands placeholders in field values.

```bash
gh api /repos/{owner}/{repo}/issues                    # current repo context
GH_REPO=org/repo gh api /repos/{owner}/{repo}/issues  # env override
gh api -R org/repo /repos/{owner}/{repo}/issues        # flag override
gh api graphql -F owner='{owner}' -F repo='{repo}' -f query='...'
```

---

## REST API Patterns for Issues

All issue endpoints are under `/repos/{owner}/{repo}/`. Responses include a `pull_request` key on pull requests; filter these out with `jq 'map(select(.pull_request == null))'` when needed.

### List, Get, Create, Update

```bash
# List open issues (up to 100 per page)
gh api '/repos/{owner}/{repo}/issues?state=open&per_page=100'

# Filter by label, assignee, sort
gh api '/repos/{owner}/{repo}/issues?labels=bug&assignee=alice&sort=updated&direction=desc'

# Get a single issue
gh api /repos/{owner}/{repo}/issues/42

# Create an issue
gh api --method POST /repos/{owner}/{repo}/issues \
  -f title='Regression in login flow' \
  -f body='Steps to reproduce...' \
  -f 'labels[]=bug' \
  -f 'assignees[]=alice'

# Close an issue
gh api --method PATCH /repos/{owner}/{repo}/issues/42 \
  -f state=closed -f state_reason=completed

# Reopen an issue
gh api --method PATCH /repos/{owner}/{repo}/issues/42 -f state=open
```

### Comments CRUD

```bash
# List comments
gh api /repos/{owner}/{repo}/issues/42/comments

# Create a comment
gh api --method POST /repos/{owner}/{repo}/issues/42/comments \
  -f body='Fixed in v2.1.0'

# Update a comment (use comment ID, not issue number)
gh api --method PATCH /repos/{owner}/{repo}/issues/comments/987654 \
  -f body='Corrected: fixed in v2.1.1'

# Delete a comment
gh api --method DELETE /repos/{owner}/{repo}/issues/comments/987654
```

### Labels CRUD

```bash
# List labels on an issue
gh api /repos/{owner}/{repo}/issues/42/labels

# Add labels (POST appends; PUT replaces all)
gh api --method POST /repos/{owner}/{repo}/issues/42/labels \
  -f 'labels[]=priority:high' -f 'labels[]=needs-review'

gh api --method PUT /repos/{owner}/{repo}/issues/42/labels \
  -f 'labels[]=bug'

# Remove a single label
gh api --method DELETE /repos/{owner}/{repo}/issues/42/labels/bug
```

### Assignees, Reactions, Timeline

```bash
# Add assignees
gh api --method POST /repos/{owner}/{repo}/issues/42/assignees \
  -f 'assignees[]=alice' -f 'assignees[]=bob'

# Remove assignees
gh api --method DELETE /repos/{owner}/{repo}/issues/42/assignees \
  -f 'assignees[]=bob'

# Add a reaction (+1, -1, laugh, confused, heart, hooray, rocket, eyes)
gh api --method POST /repos/{owner}/{repo}/issues/42/reactions \
  -f content='+1'

# Get full timeline (labeled, assigned, closed, referenced events)
gh api /repos/{owner}/{repo}/issues/42/timeline \
  --jq '[.[] | select(.event == "closed")]'
```

---

## GraphQL Patterns

Use `gh api graphql` with `-f query='...'` for string fields and `-F` for typed variables.

### Query Issues with Pagination

```bash
gh api graphql -F owner='{owner}' -F repo='{repo}' -f query='
  query($owner: String!, $repo: String!, $cursor: String) {
    repository(owner: $owner, name: $repo) {
      issues(first: 100, after: $cursor, states: OPEN) {
        pageInfo { hasNextPage endCursor }
        nodes {
          number title createdAt
          author { login }
          labels(first: 10) { nodes { name } }
        }
      }
    }
  }
'
```

Loop through all pages:

```bash
cursor=""
while true; do
  result=$(gh api graphql \
    -F owner='{owner}' -F repo='{repo}' -F cursor="$cursor" \
    -f query='
      query($owner: String!, $repo: String!, $cursor: String) {
        repository(owner: $owner, name: $repo) {
          issues(first: 100, after: $cursor, states: OPEN) {
            pageInfo { hasNextPage endCursor }
            nodes { number title }
          }
        }
      }
    ')
  echo "$result" | jq '.data.repository.issues.nodes[]'
  has_next=$(echo "$result" | jq -r '.data.repository.issues.pageInfo.hasNextPage')
  [ "$has_next" = "true" ] || break
  cursor=$(echo "$result" | jq -r '.data.repository.issues.pageInfo.endCursor')
done
```

### Mutations

GraphQL mutations require node IDs, not issue numbers. Fetch the node ID first:

```bash
ISSUE_ID=$(gh api /repos/{owner}/{repo}/issues/42 --jq '.node_id')
```

**Close / reopen:**

```bash
gh api graphql -F id="$ISSUE_ID" -f query='
  mutation($id: ID!) {
    closeIssue(input: { issueId: $id, stateReason: COMPLETED }) {
      issue { number state }
    }
  }
'

gh api graphql -F id="$ISSUE_ID" -f query='
  mutation($id: ID!) {
    reopenIssue(input: { issueId: $id }) { issue { number state } }
  }
'
```

**Add labels (requires label node IDs):**

```bash
LABEL_ID=$(gh api /repos/{owner}/{repo}/labels/bug --jq '.node_id')
gh api graphql -F labelableId="$ISSUE_ID" -F labelIds="[\"$LABEL_ID\"]" -f query='
  mutation($labelableId: ID!, $labelIds: [ID!]!) {
    addLabelsToLabelable(input: { labelableId: $labelableId, labelIds: $labelIds }) {
      labelable { ... on Issue { number } }
    }
  }
'
```

**Update title/body, transfer, add comment:**

```bash
# updateIssue
gh api graphql -F id="$ISSUE_ID" -f title='New title' -f body='New body' -f query='
  mutation($id: ID!, $title: String, $body: String) {
    updateIssue(input: { id: $id, title: $title, body: $body }) {
      issue { number title }
    }
  }
'

# transferIssue
TARGET_REPO_ID=$(gh api /repos/org/other-repo --jq '.node_id')
gh api graphql -F issueId="$ISSUE_ID" -F repositoryId="$TARGET_REPO_ID" -f query='
  mutation($issueId: ID!, $repositoryId: ID!) {
    transferIssue(input: { issueId: $issueId, repositoryId: $repositoryId }) {
      issue { number url }
    }
  }
'

# addComment
gh api graphql -F subjectId="$ISSUE_ID" -f body='Comment text' -f query='
  mutation($subjectId: ID!, $body: String!) {
    addComment(input: { subjectId: $subjectId, body: $body }) {
      commentEdge { node { id } }
    }
  }
'
```

### Sub-Issues Query (2025+)

```bash
gh api graphql -F id="$ISSUE_ID" -f query='
  query($id: ID!) {
    node(id: $id) {
      ... on Issue {
        number title
        subIssues(first: 50) {
          nodes { number title state url }
        }
      }
    }
  }
'
```

---

## Pagination Patterns

### REST: --paginate and --slurp

`--paginate` follows GitHub's `Link` response headers to fetch all pages. Each page is printed as a separate JSON array. Add `--slurp` to merge all pages into one array:

```bash
# All open issues as a single JSON array
gh api --paginate --slurp '/repos/{owner}/{repo}/issues?state=open&per_page=100'

# Pipe to jq for processing (jq -s merges the stream of arrays)
gh api --paginate '/repos/{owner}/{repo}/issues?state=open&per_page=100' \
  | jq -s 'add | map(select(.pull_request == null))'
```

`--slurp` is incompatible with `--jq` and `--template`. Process with a separate `jq` invocation after `--slurp`.

### GraphQL: Cursor-Based Pagination

GraphQL responses include `pageInfo.hasNextPage` and `pageInfo.endCursor`. Pass `endCursor` as the `after` argument on the next request. See the shell loop in the GraphQL section above.

---

## JQ Filtering Recipes

All examples use `--paginate` to fetch all pages. Pipe through `jq -s 'add'` to merge the stream of arrays before filtering.

```bash
# TSV: number, state, title
gh api --paginate '/repos/{owner}/{repo}/issues?state=all&per_page=100' \
  | jq -r '.[] | select(.pull_request == null) | [.number, .state, .title] | @tsv'

# CSV export (number, state, author, created, closed, title)
gh api --paginate '/repos/{owner}/{repo}/issues?state=all&per_page=100' \
  | jq -r '.[] | select(.pull_request == null) |
    [.number, .state, .user.login, .created_at, .closed_at // "", .title] | @csv' \
  > issues.csv

# Count open issues by label, sorted descending
gh api --paginate '/repos/{owner}/{repo}/issues?state=open&per_page=100' \
  | jq -s 'add | [.[].labels[].name] | group_by(.) |
    map({label: .[0], count: length}) | sort_by(-.count)'

# Issues opened per month
gh api --paginate '/repos/{owner}/{repo}/issues?state=all&per_page=100' \
  | jq -s 'add | map(select(.pull_request == null)) |
    group_by(.created_at[0:7]) | map({month: .[0].created_at[0:7], count: length})'

# Average close time in days
gh api --paginate '/repos/{owner}/{repo}/issues?state=closed&per_page=100' \
  | jq -s 'add | map(select(.pull_request == null and .closed_at != null)) |
    map(((.closed_at | fromdateiso8601) - (.created_at | fromdateiso8601)) / 86400) |
    add / length | . * 10 | round / 10'

# Top 10 issue authors
gh api --paginate '/repos/{owner}/{repo}/issues?state=all&per_page=100' \
  | jq -s 'add | map(select(.pull_request == null)) |
    group_by(.user.login) | map({author: .[0].user.login, count: length}) |
    sort_by(-.count) | .[0:10]'
```

---

## Bulk Operations via Shell

Use a `while read` loop to process issue numbers one at a time with controlled pacing. Insert `sleep` between calls to stay within secondary rate limits (900 REST points/minute).

```bash
# Bulk close by label
gh issue list --label 'wontfix' --state open --limit 500 --json number \
  | jq -r '.[].number' \
  | while read -r num; do
      gh issue close "$num" --reason 'not planned'; sleep 0.5
    done

# Bulk add label
gh issue list --state open --limit 500 --json number \
  | jq -r '.[].number' \
  | while read -r num; do
      gh issue edit "$num" --add-label 'needs-triage'; sleep 0.5
    done

# Bulk assign
gh issue list --label 'backend' --state open --limit 200 --json number \
  | jq -r '.[].number' \
  | while read -r num; do
      gh issue edit "$num" --add-assignee alice; sleep 0.5
    done

# Bulk transfer to another repo
gh issue list --label 'move-to-docs' --state open --limit 100 --json number \
  | jq -r '.[].number' \
  | while read -r num; do
      gh issue transfer "$num" org/docs-repo; sleep 1
    done

# Bulk comment
gh issue list --label 'stale' --state open --limit 200 --json number \
  | jq -r '.[].number' \
  | while read -r num; do
      gh issue comment "$num" --body 'Stale: closes in 14 days without activity.'; sleep 0.5
    done
```

Sleep guidelines: `0.5s` for most operations, `1s` for mutations or transfers, `2s` when processing hundreds of items. Check remaining quota with:

```bash
gh api /rate_limit --jq '{core: .resources.core.remaining, graphql: .resources.graphql.remaining}'
```

---

## gh alias Patterns for Issue Shortcuts

`gh alias set` defines shorthand commands. Use `--shell` for expansions that require piping or positional arguments (`$1`, `$2`).

```bash
gh alias set mine 'issue list --assignee @me'
gh alias set bugs 'issue list --label bug --state open'
gh alias set wontfix 'issue close --reason "not planned"'
gh alias set ib 'issue view --web'

# Positional args: gh ic "Title" "Body"
gh alias set --shell ic 'gh issue create --title "$1" --body "${2:-}"'

# Bulk close by label: gh bulk-close wontfix
gh alias set --shell bulk-close \
  'gh issue list --label "$1" --state open --limit 500 --json number |
   jq -r ".[].number" | xargs -I{} gh issue close {}'

gh alias list   # show all defined aliases
```

---

## Authentication

Token precedence: `GH_TOKEN` env var (highest) > `GITHUB_TOKEN` env var > stored credentials from `gh auth login`.

```bash
# Single-command token override
GH_TOKEN=ghp_xxxx gh api /repos/{owner}/{repo}/issues

# GitHub Actions — runner injects GITHUB_TOKEN automatically
GH_TOKEN=${{ secrets.GITHUB_TOKEN }} gh issue create --title 'Automated issue' --body '...'
```

### GitHub Enterprise Server (GHES)

```bash
gh api --hostname github.example.com /repos/{owner}/{repo}/issues

# Session-level
export GH_HOST=github.example.com

# Authenticate
gh auth login --hostname github.example.com
```

Fine-grained PATs require explicit `Issues: Read` or `Issues: Write` permissions scoped to specific repositories. Classic PATs use the `repo` scope.

---

## Rate Limits Reference

| Limit Type | Authenticated | Unauthenticated |
|------------|--------------|-----------------|
| REST core | 5,000 req/hour | 60 req/hour |
| REST search | 30 req/minute | 10 req/minute |
| GraphQL | 5,000 points/hour | Not available |
| Secondary REST | 900 points/minute | — |
| Secondary GraphQL | 2,000 points/minute | — |

GitHub App installations receive 15,000 REST requests/hour. GraphQL cost scales with nodes requested; each node counts as one point.
