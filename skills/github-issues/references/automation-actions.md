# Issue Automation with GitHub Actions

Sources: GitHub Actions marketplace, production workflow patterns

GitHub Actions automates issue triage, assignment, staleness management, and
project tracking. Each workflow below is self-contained and copy-pasteable.
Substitute `YOUR_PROJECT_NUMBER` and `YOUR_ORG` with real values.

---

## Permissions Matrix

Declare permissions at the job level, not the workflow level, to follow
least-privilege. The `add-to-project` workflow requires a PAT with `project`
scope stored as `PROJECTS_TOKEN` — `GITHUB_TOKEN` cannot write to Projects v2.

| Workflow | `issues` | `pull-requests` | `contents` | `repository-projects` |
|---|---|---|---|---|
| Auto-label on open | `write` | — | — | — |
| Content-based labeler | `write` | `read` | `read` | — |
| Stale management | `write` | `write` | — | — |
| Auto-assignment | `write` | — | — | — |
| Add to project | — | — | — | `write` (PAT) |
| Template validation | `write` | — | — | — |
| Welcome bot | `write` | `write` | — | — |
| Lock closed issues | `write` | `write` | — | — |
| Instant unstale | `write` | — | — | — |

---

## 1. Auto-Label New Issues on Open

```yaml
# .github/workflows/label-on-open.yml
name: Label new issues
on:
  issues:
    types: [opened]
permissions:
  issues: write
jobs:
  label:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/github-script@v7
        with:
          script: |
            await github.rest.issues.addLabels({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              labels: ['status/triage', 'type/unclassified'],
            });
```

---

## 2. Content-Based Labeling with actions/labeler v5

`actions/labeler` applies labels based on changed file paths (PRs) or branch name
patterns. For issue body matching, use `actions/github-script` instead (see Section 6).

```yaml
# .github/workflows/labeler.yml
name: Labeler
on:
  issues:
    types: [opened, edited]
  pull_request:
    types: [opened, synchronize, reopened]
permissions:
  contents: read
  issues: write
  pull-requests: write
jobs:
  label:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/labeler@v5
        with:
          repo-token: ${{ secrets.GITHUB_TOKEN }}
          configuration-path: .github/labeler.yml
          sync-labels: false
```

```yaml
# .github/labeler.yml
area/frontend:
  - changed-files:
    - any-glob-to-any-file:
      - 'src/frontend/**'
      - '**/*.tsx'
      - '**/*.css'

area/backend:
  - changed-files:
    - any-glob-to-any-file:
      - 'src/api/**'
      - 'src/server/**'

area/docs:
  - changed-files:
    - any-glob-to-any-file:
      - 'docs/**'
      - '**/*.md'

type/bug:
  - head-branch: ['fix/*', 'bug/*', 'hotfix/*']

type/feature:
  - head-branch: ['feat/*', 'feature/*']
```

---

## 3. Stale Issue Management with actions/stale v9

Two-phase: warn at 60 days of inactivity, close 7 days after the warning.
Exempt issues with high-priority labels or an assigned milestone.

```yaml
# .github/workflows/stale.yml
name: Stale issue management
on:
  schedule:
    - cron: '0 1 * * *'
  workflow_dispatch:
permissions:
  issues: write
  pull-requests: write
jobs:
  stale:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/stale@v9
        with:
          repo-token: ${{ secrets.GITHUB_TOKEN }}
          days-before-issue-stale: 60
          days-before-issue-close: 7
          stale-issue-label: 'status/stale'
          close-issue-label: 'status/closed-stale'
          stale-issue-message: >
            This issue has been inactive for 60 days. It will be closed in 7 days
            unless there is new activity. Remove the `status/stale` label or leave
            a comment to keep it open.
          close-issue-message: >
            Closed automatically after 67 days of inactivity. Reopen if the
            problem persists.
          days-before-pr-stale: 30
          days-before-pr-close: 7
          stale-pr-label: 'status/stale'
          stale-pr-message: >
            This pull request has been inactive for 30 days and will be closed
            in 7 days unless there is new activity.
          exempt-issue-labels: >
            status/pinned,status/in-progress,status/blocked,
            priority/critical,priority/high
          exempt-pr-labels: 'status/pinned,status/in-progress'
          exempt-issue-milestones: true
          exempt-pr-milestones: true
          remove-stale-when-updated: true
          operations-per-run: 100
```

---

## 4. Auto-Assignment Patterns

### 4a. Label-Based Round-Robin (actions/github-script)

Map labels to assignee pools. Pick the next assignee using a counter stored in
repository variable `ROUND_ROBIN_INDEX`. Update it after each assignment via a
PAT with `repo` scope.

```yaml
# .github/workflows/auto-assign-label.yml
name: Auto-assign by label
on:
  issues:
    types: [labeled]
permissions:
  issues: write
jobs:
  assign:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/github-script@v7
        env:
          ROUND_ROBIN_INDEX: ${{ vars.ROUND_ROBIN_INDEX || '0' }}
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            const label = context.payload.label.name;
            const pools = {
              'area/frontend': ['alice', 'bob', 'carol'],
              'area/backend':  ['dave', 'eve'],
              'area/docs':     ['frank'],
            };
            const assignees = pools[label];
            if (!assignees || assignees.length === 0) return;
            const idx = parseInt(process.env.ROUND_ROBIN_INDEX, 10) % assignees.length;
            await github.rest.issues.addAssignees({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              assignees: [assignees[idx]],
            });
            core.notice(`Assigned ${assignees[idx]} (pool index ${idx})`);
```

### 4b. pozil/auto-assign-issue

Stateless rotation without managing a counter variable.

```yaml
# .github/workflows/auto-assign-issue.yml
name: Auto-assign new issues
on:
  issues:
    types: [opened]
permissions:
  issues: write
jobs:
  assign:
    runs-on: ubuntu-latest
    steps:
      - uses: pozil/auto-assign-issue@v2
        with:
          assignees: alice,bob,carol
          numOfAssignee: 1
          allowSelfAssign: false
```

---

## 5. Issue-to-Project Automation with actions/add-to-project

```yaml
# .github/workflows/add-to-project.yml
name: Add issues to project
on:
  issues:
    types: [opened]
  pull_request:
    types: [opened]
jobs:
  add-to-project:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/add-to-project@v1.0.2
        with:
          project-url: https://github.com/orgs/YOUR_ORG/projects/YOUR_PROJECT_NUMBER
          github-token: ${{ secrets.PROJECTS_TOKEN }}
          labeled: status/triage
          label-operator: OR
```

For a user project, use `https://github.com/users/YOUR_USERNAME/projects/YOUR_PROJECT_NUMBER`.

---

## 6. Template Validation

Check that required sections are present in the issue body. Comment and label issues
that skip the template. Adjust `REQUIRED_SECTIONS` to match your headings.

```yaml
# .github/workflows/validate-template.yml
name: Validate issue template
on:
  issues:
    types: [opened, edited]
permissions:
  issues: write
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/github-script@v7
        with:
          script: |
            const body = context.payload.issue.body || '';
            const REQUIRED_SECTIONS = [
              '## Description',
              '## Steps to Reproduce',
              '## Expected Behavior',
              '## Actual Behavior',
            ];
            const missing = REQUIRED_SECTIONS.filter(s => !body.includes(s));
            if (missing.length === 0) return;
            const list = missing.map(s => `- \`${s}\``).join('\n');
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: `The following required sections are missing:\n\n${list}\n\nPlease edit the issue to include them.`,
            });
            await github.rest.issues.addLabels({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              labels: ['status/needs-info'],
            });
```

---

## 7. Welcome Bot for First-Time Contributors

```yaml
# .github/workflows/welcome.yml
name: Welcome first-time contributors
on:
  issues:
    types: [opened]
  pull_request:
    types: [opened]
permissions:
  issues: write
  pull-requests: write
jobs:
  welcome:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/first-interaction@v1
        with:
          repo-token: ${{ secrets.GITHUB_TOKEN }}
          issue-message: >
            Welcome, and thank you for opening your first issue. A maintainer
            will review it shortly. If you have a question rather than a bug
            report or feature request, consider opening a Discussion instead.
          pr-message: >
            Thank you for your first pull request. A maintainer will review it
            soon. Please ensure your branch is up to date with `main` and that
            all CI checks pass.
```

---

## 8. Lock Closed Issues with dessant/lock-threads v5

```yaml
# .github/workflows/lock-closed.yml
name: Lock closed issues
on:
  schedule:
    - cron: '0 2 * * *'
  workflow_dispatch:
permissions:
  issues: write
  pull-requests: write
jobs:
  lock:
    runs-on: ubuntu-latest
    steps:
      - uses: dessant/lock-threads@v5
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          issue-inactive-days: 30
          issue-lock-reason: resolved
          issue-comment: >
            This issue has been locked after 30 days of inactivity since it was
            closed. If you are experiencing a similar problem, open a new issue
            with a link to this one.
          pr-inactive-days: 14
          pr-lock-reason: resolved
          pr-comment: ''
          issue-exclude-labels: 'status/pinned,status/known-issue'
          log-output: true
```

---

## 9. Instant Unstale on Activity

`actions/stale` removes the stale label on its next scheduled run when
`remove-stale-when-updated: true` is set. This workflow removes it immediately
on comment or edit.

```yaml
# .github/workflows/unstale-on-activity.yml
name: Remove stale label on activity
on:
  issue_comment:
    types: [created]
  issues:
    types: [edited]
permissions:
  issues: write
jobs:
  unstale:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/github-script@v7
        with:
          script: |
            const issue = context.payload.issue;
            if (!issue) return;
            const hasStale = issue.labels.some(l => l.name === 'status/stale');
            if (!hasStale) return;
            await github.rest.issues.removeLabel({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: issue.number,
              name: 'status/stale',
            });
            core.notice(`Removed status/stale from #${issue.number}`);
```

---

## Recommended Deployment Order

For a new repository, deploy workflows in this sequence:

1. `label-on-open.yml` — immediate triage signal on every new issue
2. `labeler.yml` + `.github/labeler.yml` — content-based classification
3. `auto-assign-issue.yml` — distribute incoming work across the team
4. `add-to-project.yml` — populate the project board automatically
5. `validate-template.yml` — enforce template compliance from day one
6. `welcome.yml` — onboard first-time contributors
7. `stale.yml` — keep the backlog clean on a daily schedule
8. `unstale-on-activity.yml` — prevent false positives from the stale bot
9. `lock-closed.yml` — reduce noise on resolved issues

Store `PROJECTS_TOKEN` under Settings > Secrets and variables > Actions >
Repository secrets. Store `ROUND_ROBIN_INDEX` under Repository variables.

---

## Troubleshooting

**Workflow does not trigger on issue events** — Verify the `on:` block uses
`issues:` (plural). Check that the event type matches exactly: `opened`,
`labeled`, `edited`, `closed`, `reopened`.

**`GITHUB_TOKEN` permission denied on Projects v2** — Projects v2 requires a
PAT with `project` scope. Create a fine-grained PAT, add project read/write,
and store it as `PROJECTS_TOKEN`.

**Stale bot closes issues with active milestones** — Set `exempt-issue-milestones: true`.
A typo in this option silently disables the exemption.

**`actions/labeler` v5 does not apply labels to issues** — `actions/labeler`
matches file paths for PRs. For issue body matching, use `actions/github-script`
with a regex against `context.payload.issue.body`.

**Round-robin always picks the same person** — Writing `ROUND_ROBIN_INDEX` back
requires a PAT with `repo` scope. If that step fails, the counter stays at 0.
Use `pozil/auto-assign-issue` for stateless rotation without variable management.
