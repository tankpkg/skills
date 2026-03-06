# Labels, Milestones, and Projects

Sources: GitHub documentation, production OSS label conventions

---

## Label Taxonomy

Labels are the primary classification layer for issues. Without a consistent
taxonomy, labels accumulate organically and become noise. Use namespaced
prefixes to enforce structure and make labels scannable at a glance.

### Namespace Prefixes

| Prefix | Purpose | Examples |
|--------|---------|---------|
| `type/` | What kind of work | `type/bug`, `type/feature`, `type/docs` |
| `priority/` | Urgency and impact | `priority/critical`, `priority/high` |
| `status/` | Workflow state | `status/needs-triage`, `status/blocked` |
| `area/` | Codebase or product domain | `area/auth`, `area/api`, `area/ui` |
| `effort/` | Estimated complexity | `effort/small`, `effort/large` |

The slash separator is a convention, not a GitHub feature. GitHub treats the
full string as the label name. The prefix groups labels visually in sorted
lists and enables consistent filtering.

### Recommended Label Schema

| Label | Color | Description |
|-------|-------|-------------|
| `type/bug` | `#d73a4a` | Something is not working as expected |
| `type/feature` | `#0075ca` | New capability or enhancement request |
| `type/docs` | `#0075ca` | Documentation addition or correction |
| `type/refactor` | `#e4e669` | Code change with no behavior change |
| `type/test` | `#e4e669` | Test coverage addition or fix |
| `type/chore` | `#fef2c0` | Maintenance, dependency updates, tooling |
| `type/security` | `#b60205` | Security vulnerability or hardening |
| `type/performance` | `#fbca04` | Performance regression or improvement |
| `priority/critical` | `#b60205` | Production down, data loss, blocking release |
| `priority/high` | `#d93f0b` | Significant impact, address this sprint |
| `priority/medium` | `#fbca04` | Normal priority, schedule accordingly |
| `priority/low` | `#0e8a16` | Nice to have, address when capacity allows |
| `status/needs-triage` | `#ededed` | Not yet reviewed by maintainers |
| `status/confirmed` | `#c5def5` | Reproduced or validated, ready to work |
| `status/in-progress` | `#0075ca` | Actively being worked on |
| `status/blocked` | `#d73a4a` | Cannot proceed, waiting on dependency |
| `status/needs-info` | `#fef2c0` | Waiting for reporter to provide details |
| `status/wont-fix` | `#ffffff` | Acknowledged but will not be addressed |
| `effort/small` | `#c2e0c6` | Less than half a day of work |
| `effort/medium` | `#bfd4f2` | One to three days of work |
| `effort/large` | `#d4c5f9` | More than three days, consider splitting |
| `effort/good-first-issue` | `#7057ff` | Suitable for new contributors |
| `effort/help-wanted` | `#008672` | Maintainers welcome external contributions |
| `area/api` | `#1d76db` | Public or internal API surface |
| `area/auth` | `#1d76db` | Authentication and authorization |
| `area/ui` | `#1d76db` | Frontend, components, styling |
| `area/infra` | `#1d76db` | Infrastructure, CI/CD, deployment |
| `area/data` | `#1d76db` | Database, migrations, data models |

### Color Coding Conventions

| Color | Hex | Semantic |
|-------|-----|---------|
| Red (dark) | `#b60205` | Critical severity, security, blocking |
| Red (medium) | `#d73a4a` | Bug, error, broken |
| Orange | `#d93f0b` | High priority, warning |
| Yellow | `#fbca04` | Medium priority, caution, needs attention |
| Green (dark) | `#0e8a16` | Low priority, good state, accepted |
| Green (light) | `#c2e0c6` | Small effort, positive signal |
| Blue (dark) | `#0075ca` | Feature, enhancement, informational |
| Blue (medium) | `#1d76db` | Area classification |
| Blue (light) | `#c5def5` | Confirmed, ready state |
| Purple | `#7057ff` | Good first issue, community |
| Teal | `#008672` | Help wanted, collaboration |
| Gray | `#ededed` | Needs triage, unknown state |
| White | `#ffffff` | Closed states, wont-fix |
| Yellow (pale) | `#fef2c0` | Chore, needs info, low signal |

---

## gh label Commands

### Create

```bash
gh label create <name> [flags]
```

| Flag | Short | Description |
|------|-------|-------------|
| `--color` | `-c` | 6-character hex color without `#` prefix; random if omitted |
| `--description` | `-d` | Short description shown in label picker |
| `--force` | `-f` | Update the label if it already exists |

```bash
gh label create "type/bug" \
  --color "d73a4a" \
  --description "Something is not working as expected"

# Idempotent: safe to run in setup scripts
gh label create "priority/critical" \
  --color "b60205" \
  --description "Production down, data loss, blocking release" \
  --force
```

### List

```bash
gh label list [flags]
```

| Flag | Short | Description |
|------|-------|-------------|
| `--limit` | `-L` | Maximum number of labels to return |
| `--search` | `-S` | Filter labels by name substring |
| `--sort` | | `created` or `name` (default: `created`) |
| `--order` | | `asc` or `desc` |
| `--json` | | Output as JSON with specified fields |
| `--jq` | `-q` | Apply jq filter to JSON output |
| `--web` | `-w` | Open label list in browser |

```bash
gh label list --sort name --order asc
gh label list --json name,color,description   # export for backup or migration
```

### Edit

```bash
gh label edit <name> [flags]
```

| Flag | Short | Description |
|------|-------|-------------|
| `--color` | | New hex color |
| `--description` | | New description |
| `--name` | `-n` | Rename the label |

```bash
# Rename without losing issue associations
gh label edit "bug" --name "type/bug" --color "d73a4a"
```

### Delete

```bash
gh label delete <name> [--yes]
```

Deleting a label removes it from all issues silently. Verify usage before
deleting:

```bash
gh issue list --label "old-label" --state all --json number | jq length
```

### Clone

```bash
gh label clone <source-repo> [flags]
```

| Flag | Short | Description |
|------|-------|-------------|
| `--force` | | Overwrite labels that already exist in destination |
| `--repo` | `-R` | Destination repository (defaults to current) |

```bash
gh label clone myorg/canonical-repo --repo myorg/new-repo --force
```

Clone is additive: it does not delete labels present in the destination but
absent from the source. Run a delete pass separately for exact parity.

---

## Label Syncing Across Repositories

### Org-Wide Propagation with gh label clone

Maintain a single canonical repository as the authoritative label source.
Propagate to all repositories in the organization:

```bash
gh repo list myorg --limit 100 --json nameWithOwner --jq '.[].nameWithOwner' | \
  xargs -I{} gh label clone myorg/canonical-repo --repo {} --force
```

### github-label-sync

The `github-label-sync` npm package provides declarative label management
from a YAML or JSON configuration file. It deletes labels not in the config,
making it stricter than `gh label clone`.

```bash
npm install -g github-label-sync
github-label-sync --access-token $GITHUB_TOKEN --labels labels.yaml myorg/repo
```

| Tool | Behavior | When to Use |
|------|---------|------------|
| `gh label clone` | Additive, no deletion | Quick propagation, no external deps |
| `github-label-sync` | Declarative, deletes unlisted | Strict parity, version-controlled config |

Store label definitions in `.github/labels.yaml` for version control and
code review. Reference this file in your sync workflow.

---

## Milestone Management

Milestones group issues into a named, time-bounded container with an optional
due date and completion percentage.

### Milestone Strategies

| Strategy | When to Use | Example |
|----------|------------|---------|
| Version-based | Shipping discrete releases | `v2.0.0`, `v2.1.0` |
| Sprint-based | Agile teams with fixed cadence | `Sprint 42`, `2026-Q1-W3` |
| Themed | Feature-driven development | `Auth Overhaul`, `Performance Pass` |
| Date-based | External deadline alignment | `2026-06-30 Launch` |

### Creating and Managing Milestones via gh api

The `gh` CLI has no `gh milestone` subcommand. Use `gh api` directly:

```bash
# Create
gh api repos/{owner}/{repo}/milestones \
  --method POST \
  --field title="v2.0.0" \
  --field description="Second major release" \
  --field due_on="2026-06-30T00:00:00Z"

# List with open/closed counts
gh api repos/{owner}/{repo}/milestones \
  --jq '.[] | {number, title, open: .open_issues, closed: .closed_issues}'

# Close after release
gh api repos/{owner}/{repo}/milestones/{milestone_number} \
  --method PATCH \
  --field state="closed"
```

### Assigning Issues to Milestones

```bash
# At creation
gh issue create --title "Fix login redirect" --milestone "v2.0.0"

# On existing issue
gh issue edit 42 --milestone "v2.0.0"

# Remove milestone
gh issue edit 42 --remove-milestone

# Bulk-assign open issues
gh issue list --state open --json number --jq '.[].number' | \
  xargs -I{} gh issue edit {} --milestone "v2.0.0"
```

### Milestone Hygiene

- Close milestones when the release ships; do not leave them open indefinitely.
- Move unfinished issues to the next milestone before closing.
- Keep milestone titles consistent with your versioning scheme.
- Set due dates even for approximate targets; they enable sorting by urgency.

---

## Projects v2

GitHub Projects v2 aggregates issues and pull requests across repositories
into a spreadsheet-style board with custom fields, multiple views (table,
board, roadmap), and built-in automation.

### Adding Issues to a Project

```bash
# Add a single issue by URL
gh project item-add <project-number> \
  --owner <owner> \
  --url https://github.com/owner/repo/issues/42

# Capture URL from gh issue view, then add
ISSUE_URL=$(gh issue view 42 --json url --jq '.url')
gh project item-add 1 --owner myorg --url "$ISSUE_URL"

# Bulk-add all open issues from a repository
gh issue list --state open --json url --jq '.[].url' | \
  xargs -I{} gh project item-add 1 --owner myorg --url {}
```

### Custom Fields

| Field Type | Use Case | Example Values |
|------------|---------|----------------|
| Status | Workflow state (built-in) | Todo, In Progress, Done |
| Single Select | Custom categorical data | Quarter, Team, Component |
| Text | Free-form notes | Acceptance criteria, links |
| Number | Numeric tracking | Story points, weight |
| Date | Scheduling | Target date, review date |
| Iteration | Sprint or cycle tracking | Sprint 1, Sprint 2 |

Edit a field value on a project item using `gh project item-edit`:

```bash
# Retrieve the item node ID
gh project item-list 1 --owner myorg --format json \
  --jq '.items[] | select(.content.number == 42) | .id'

# Set a single-select field
gh project item-edit \
  --project-id <project-node-id> \
  --id <item-node-id> \
  --field-id <field-node-id> \
  --single-select-option-id <option-node-id>
```

For text or number fields, use `--text` or `--number` flags respectively.
For date fields, use `--date` with an ISO 8601 value.

### Iteration Fields

Iteration fields define recurring time boxes (sprints, cycles). Configure
them in the project settings with a start date and duration. GitHub
automatically advances iterations and provides a "current iteration" filter
in views. Iteration fields support custom names, durations, and break periods
between cycles.

### Auto-Add Workflows

Projects v2 includes built-in automation that adds items automatically based
on repository events. Configure these in the project Workflows settings panel.

| Trigger | Condition Options | Action |
|---------|------------------|--------|
| Item added to repository | Label matches, issue type matches | Add to project |
| Item reopened | Any | Set Status field |
| Item closed | Any | Set Status field |
| Pull request merged | Any | Set Status field |
| Code changes requested | Any | Set Status field |
| Code review approved | Any | Set Status field |

Auto-add workflows accept filter syntax to match specific issues:

```
is:issue label:type/bug
is:issue label:priority/critical
is:issue label:area/api label:priority/high
is:issue no:assignee
```

### Hierarchy View and Sub-Issues

Projects v2 displays parent-child issue relationships in a hierarchy view.
Sub-issues appear nested under their parent in the table view.

Sub-issue constraints:
- Up to 100 sub-issues per parent issue
- Up to 8 levels of nesting depth
- Sub-issues can span repositories within the same organization

Add sub-issues through the GitHub web UI or via the GraphQL API using the
`addSubIssue` mutation with parent and child node IDs.

---

## Issue Types (Organization Level)

Issue Types are an organization-level classification layer above labels.
They appear as a structured field on issues and enable filtering across all
repositories in the organization.

| Type | Purpose |
|------|---------|
| Bug | Defect or unintended behavior |
| Feature | New capability or enhancement |
| Task | Operational or maintenance work |
| Epic | Large body of work spanning multiple issues |

Issue Types differ from `type/` labels:
- Enforced at the organization level, not per-repository.
- Appear as a dedicated field, queryable separately from labels.
- Available on GitHub Team and Enterprise plans.

Do not duplicate both systems. Use Issue Types for organization-wide
consistency; use `type/` labels for repository-specific classification or
when on a plan without Issue Types.

---

## Combining Labels, Milestones, and Projects

These three systems serve different purposes and complement each other:

| System | Answers | Scope |
|--------|---------|-------|
| Labels | What kind of issue is this? | Per issue |
| Milestones | When will this ship? | Per repository |
| Projects | What is the team working on? | Cross-repository |

### Triage Workflow

Apply this sequence when a new issue arrives:

1. Auto-add workflow applies `status/needs-triage` and adds to project.
2. Reviewer applies `type/*` and `area/*` labels.
3. Reviewer applies `priority/*` based on impact and urgency.
4. If reproducible, replace `status/needs-triage` with `status/confirmed`.
5. If more information is needed, apply `status/needs-info`.
6. Assign to a milestone when the issue is scheduled for work.
7. Apply `status/in-progress` when work begins.

A well-organized issue carries one `type/` label, one `priority/` label,
one or more `area/` labels, one `status/` label, a milestone when scheduled,
and a project item when actively tracked. Five to seven labels per issue is
a signal that the taxonomy needs consolidation or the issue needs splitting.
