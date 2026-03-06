# gh issue Commands

Sources: GitHub CLI official documentation (cli.github.com/manual), gh CLI v2.x reference

Scope: `gh issue *` subcommands only. For search, see `search-and-filter.md`. For API patterns, see `api-and-scripting.md`. For labels and milestones, see `labels-milestones-projects.md`.

**Aliases:** `gh issue ls` = `gh issue list` | `gh issue new` = `gh issue create`

---

## gh issue status

Show issues relevant to the current user in the current repository.

```
gh issue status [flags]
```

| Flag | Description |
|------|-------------|
| `--json <fields>` | Output JSON with specified fields |
| `--jq <expr>` | Filter JSON with a jq expression |
| `--template <tmpl>` | Format with a Go template |
| `-R, --repo <OWNER/REPO>` | Target a specific repository |

```bash
gh issue status
gh issue status --json assignedIssues --jq '.assignedIssues[].number'
```

---

## gh issue list

```
gh issue list [flags]
```

| Flag | Short | Description |
|------|-------|-------------|
| `--state <string>` | `-s` | `open`, `closed`, or `all` (default: `open`) |
| `--assignee <string>` | `-a` | Filter by assignee; `@me` for yourself |
| `--author <string>` | `-A` | Filter by author login |
| `--label <strings>` | `-l` | Filter by label; repeatable or comma-separated |
| `--milestone <string>` | | Filter by milestone title or number |
| `--search <query>` | `-S` | GitHub search syntax query |
| `--mention <string>` | | Filter by mention |
| `--app <string>` | | Filter by GitHub App slug |
| `--limit <int>` | `-L` | Maximum results (default: 30) |
| `--json <fields>` | | JSON output |
| `--jq <expr>` | `-q` | jq filter on JSON output |
| `--template <tmpl>` | `-t` | Go template output |
| `--web` | `-w` | Open in browser |
| `-R, --repo <OWNER/REPO>` | | Target a specific repository |

```bash
gh issue list --assignee @me
gh issue list --state closed --label bug --limit 100
gh issue list --json number,title,state --jq '.[] | "\(.number)\t\(.title)"'
```

---

## gh issue create

```
gh issue create [flags]
```

| Flag | Short | Description |
|------|-------|-------------|
| `--title <string>` | `-t` | Issue title |
| `--body <string>` | `-b` | Issue body text |
| `--body-file <file>` | | Read body from file (`-` for stdin) |
| `--label <strings>` | `-l` | Add labels; repeatable or comma-separated |
| `--assignee <strings>` | `-a` | Assign users; `@me` supported; repeatable |
| `--milestone <string>` | `-m` | Milestone title |
| `--project <strings>` | `-p` | Project title; repeatable |
| `--template <file>` | | Use a named issue template |
| `--editor` | | Open default editor for body |
| `--web` | `-w` | Open browser to create the issue |
| `--recover <file>` | | Recover a failed create from a file |
| `-R, --repo <OWNER/REPO>` | | Target a specific repository |

```bash
gh issue create
gh issue create --title "Login fails on Safari" --body "Steps: ..."
gh issue create --title "Refactor auth" --body-file ./body.md --assignee @me --label enhancement
```

---

## gh issue view

```
gh issue view <number|url> [flags]
```

| Flag | Short | Description |
|------|-------|-------------|
| `--comments` | `-c` | Include comments in output |
| `--json <fields>` | | JSON output |
| `--jq <expr>` | `-q` | jq filter |
| `--template <tmpl>` | `-t` | Go template |
| `--web` | `-w` | Open in browser |
| `-R, --repo <OWNER/REPO>` | | Target a specific repository |

```bash
gh issue view 42
gh issue view 42 --comments
gh issue view 42 --json title,body,labels,assignees
```

---

## gh issue edit

Accepts one or more issue numbers or URLs for bulk editing.

```
gh issue edit <number|url>... [flags]
```

| Flag | Description |
|------|-------------|
| `--title <string>` | Set a new title |
| `--body <string>` | Set a new body |
| `--body-file <file>` | Read new body from file (`-` for stdin) |
| `--add-assignee <strings>` | Add assignees; `@me` and `@copilot` supported |
| `--remove-assignee <strings>` | Remove assignees |
| `--add-label <strings>` | Add labels (comma-separated) |
| `--remove-label <strings>` | Remove labels (comma-separated) |
| `--add-project <strings>` | Add to a project |
| `--remove-project <strings>` | Remove from a project |
| `--milestone <string>` | Set milestone by title |
| `--remove-milestone` | Remove the milestone |
| `-R, --repo <OWNER/REPO>` | Target a specific repository |

```bash
gh issue edit 10 --title "Updated: Login fails on Safari 16"
gh issue edit 10 --add-label "needs-triage" --add-assignee octocat
gh issue edit 5 6 7 --add-label "sprint-2"
```

---

## gh issue close

```
gh issue close <number|url> [flags]
```

| Flag | Short | Description |
|------|-------|-------------|
| `--comment <string>` | `-c` | Add a comment when closing |
| `--reason <string>` | `-r` | `completed` or `not planned` |
| `-R, --repo <OWNER/REPO>` | | Target a specific repository |

```bash
gh issue close 42
gh issue close 42 --reason "not planned" --comment "Out of scope for this release."
gh issue list --label wontfix --json number --jq '.[].number' | xargs -I{} gh issue close {} --reason "not planned"
```

---

## gh issue reopen

```
gh issue reopen <number|url> [flags]
```

| Flag | Short | Description |
|------|-------|-------------|
| `--comment <string>` | `-c` | Add a comment when reopening |
| `-R, --repo <OWNER/REPO>` | | Target a specific repository |

```bash
gh issue reopen 42
gh issue reopen 42 --comment "Reopening: the fix introduced a regression."
```

---

## gh issue comment

```
gh issue comment <number|url> [flags]
```

| Flag | Short | Description |
|------|-------|-------------|
| `--body <string>` | `-b` | Comment body text |
| `--body-file <file>` | `-F` | Read body from file (`-` for stdin) |
| `--edit-last` | | Edit the last comment instead of adding a new one |
| `--editor` | | Open default editor |
| `--web` | `-w` | Open browser to add comment |
| `-R, --repo <OWNER/REPO>` | | Target a specific repository |

```bash
gh issue comment 42 --body "Confirmed on v2.3.1 as well."
gh issue comment 42 --body-file ./triage-notes.md
gh issue comment 42 --edit-last
```

---

## gh issue delete

Permanently deletes an issue. This action is irreversible.

```
gh issue delete <number|url> [flags]
```

| Flag | Description |
|------|-------------|
| `--yes` | Skip the confirmation prompt |
| `-R, --repo <OWNER/REPO>` | Target a specific repository |

```bash
gh issue delete 99
gh issue delete 99 --yes
```

---

## gh issue transfer

```
gh issue transfer <number|url> <destination-repo> [flags]
```

| Flag | Description |
|------|-------------|
| `-R, --repo <OWNER/REPO>` | Source repository (if not current) |

```bash
gh issue transfer 15 myorg/backend-repo
gh issue transfer 15 myorg/backend-repo -R myorg/frontend-repo
```

---

## gh issue lock

```
gh issue lock <number|url> [flags]
```

| Flag | Short | Description |
|------|-------|-------------|
| `--reason <string>` | `-r` | `off-topic`, `too heated`, `resolved`, or `spam` |
| `-R, --repo <OWNER/REPO>` | | Target a specific repository |

```bash
gh issue lock 42 --reason resolved
gh issue lock 42 --reason "too heated"
```

---

## gh issue unlock

```
gh issue unlock <number|url> [flags]
```

| Flag | Description |
|------|-------------|
| `-R, --repo <OWNER/REPO>` | Target a specific repository |

```bash
gh issue unlock 42
```

---

## gh issue pin

Pin an issue to the top of the issue list (max 3 pinned per repo).

```
gh issue pin <number|url> [flags]
```

| Flag | Description |
|------|-------------|
| `-R, --repo <OWNER/REPO>` | Target a specific repository |

```bash
gh issue pin 1
```

---

## gh issue unpin

```
gh issue unpin <number|url> [flags]
```

| Flag | Description |
|------|-------------|
| `-R, --repo <OWNER/REPO>` | Target a specific repository |

```bash
gh issue unpin 1
```

---

## gh issue develop

Create or list branches linked to an issue.

```
gh issue develop <number|url> [flags]
```

| Flag | Short | Description |
|------|-------|-------------|
| `--base <branch>` | `-b` | Base branch for the new branch |
| `--branch-repo <OWNER/REPO>` | | Repository where the branch will be created |
| `--checkout` | | Check out the branch locally after creating |
| `--issue-repo <OWNER/REPO>` | | Repository containing the issue (when different from branch repo) |
| `--list` | `-l` | List branches linked to the issue |
| `--name <string>` | `-n` | Name for the new branch |
| `-R, --repo <OWNER/REPO>` | | Target a specific repository |

```bash
gh issue develop 42 --checkout
gh issue develop 42 --name "fix/login-safari" --base main
gh issue develop 42 --list
```

---

## JSON Output Fields

Use `--json <fields>` with `list`, `view`, and `status`. Combine with `--jq` for filtering.

| Field | Type | Description |
|-------|------|-------------|
| `assignees` | array | Assigned users |
| `author` | object | Issue author (login, name) |
| `body` | string | Issue body |
| `closed` | boolean | Whether closed |
| `closedAt` | string | ISO 8601 closure timestamp |
| `comments` | array | Comments (requires `--comments` on `view`) |
| `createdAt` | string | ISO 8601 creation timestamp |
| `id` | string | GraphQL node ID |
| `isPinned` | boolean | Whether pinned |
| `labels` | array | Attached labels |
| `milestone` | object | Milestone (title, number, dueOn) |
| `number` | integer | Issue number |
| `projectItems` | array | Projects v2 items |
| `state` | string | `OPEN` or `CLOSED` |
| `stateReason` | string | `COMPLETED`, `NOT_PLANNED`, or null |
| `title` | string | Issue title |
| `updatedAt` | string | ISO 8601 last-updated timestamp |
| `url` | string | HTML URL |

```bash
# TSV of number and title
gh issue list --json number,title --jq '.[] | [.number, .title] | @tsv'

# Issues closed as "not planned"
gh issue list --state closed --json number,stateReason \
  --jq '.[] | select(.stateReason == "NOT_PLANNED") | .number'
```

---

## Quick-Reference Card

```
STATUS / LIST
  gh issue status                           Issues relevant to you
  gh issue list                             Open issues
  gh issue list -s closed -l bug -L 100     Closed bug issues, up to 100
  gh issue list -a @me                      Assigned to you
  gh issue list --json number,title         JSON output

CREATE
  gh issue create                           Interactive
  gh issue create -t "Title" -b "Body"      Inline
  gh issue create -t "Title" --body-file f  From file
  gh issue create -a @me -l bug            With assignee + label

VIEW / EDIT
  gh issue view 42                          View issue
  gh issue view 42 -c                       With comments
  gh issue edit 42 --title "New title"      Change title
  gh issue edit 42 --add-label bug          Add label
  gh issue edit 5 6 7 --add-label sprint    Bulk edit

CLOSE / REOPEN
  gh issue close 42 -r "not planned"        Close with reason
  gh issue close 42 -c "Closing because…"   Close with comment
  gh issue reopen 42 -c "Regression found"  Reopen with comment

COMMENT
  gh issue comment 42 -b "Text"             Add comment
  gh issue comment 42 -F notes.md           From file
  gh issue comment 42 --edit-last           Edit last comment

LIFECYCLE
  gh issue delete 42 --yes                  Delete (irreversible)
  gh issue transfer 42 org/other-repo       Transfer
  gh issue lock 42 -r resolved              Lock
  gh issue unlock 42                        Unlock
  gh issue pin 42 / gh issue unpin 42       Pin / unpin

DEVELOP
  gh issue develop 42 --checkout            Create + checkout branch
  gh issue develop 42 -n "fix/bug" -b main  Custom name + base
  gh issue develop 42 --list               List linked branches
```
