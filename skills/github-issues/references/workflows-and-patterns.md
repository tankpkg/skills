# Issue Workflows and Patterns

Sources: GitHub documentation, production OSS issue management patterns

---

## Issue-Driven Development (IDD)

IDD treats every unit of work — bug, feature, task, spike — as an issue that drives the full development lifecycle. Nothing ships without a traceable issue.

### Full Lifecycle

```
Discovery
   |
   v
[Triage] -----> Closed (invalid / duplicate / won't fix)
   |
   v
[Planning] --> Milestone assigned, estimate added, priority set
   |
   v
[Development] --> Branch created from issue, commits reference #N
   |
   v
[Review] --> PR opened, linked to issue via closing keyword
   |
   v
[Verification] --> PR merged, issue auto-closed, release notes generated
```

Each stage has a clear entry and exit condition. An issue that skips triage is a liability — it may duplicate existing work or lack context to implement correctly.

### Stage Responsibilities

| Stage | Owner | Entry Condition | Exit Condition |
|-------|-------|-----------------|----------------|
| Discovery | Anyone | Problem identified | Issue created with reproduction or description |
| Triage | Maintainer | Issue created | Priority set, labels applied, milestone or backlog assigned |
| Planning | Team lead | Triaged | Estimate added, assignee set, acceptance criteria defined |
| Development | Assignee | Planned | Branch created, implementation complete |
| Review | Reviewer | PR opened | Code approved, CI green |
| Verification | QA / author | PR merged | Behavior confirmed in target environment |

---

## Triage Workflow

Triage is the highest-leverage activity in issue management. A well-triaged
backlog is a team asset. An untriaged backlog is noise.

### Triage Decision Tree

```
New issue arrives
       |
       v
Is it a duplicate?
  Yes --> Close with "Duplicate of #N", add `status/duplicate` label
  No  --> Continue
       |
       v
Is it actionable? (reproducible bug or clear feature request)
  No  --> Comment asking for more info, add `status/needs-info` label
          Wait 14 days. No response? Close with explanation.
  Yes --> Continue
       |
       v
Is it in scope for this project?
  No  --> Close with explanation, suggest alternatives if known
  Yes --> Continue
       |
       v
Assign priority (see matrix below)
Apply type label (bug / feature / task / docs)
Apply area label (area/auth, area/api, etc.)
Assign to milestone or backlog
```

### Priority Matrix: Impact x Urgency

| | High Urgency | Low Urgency |
|---|---|---|
| **High Impact** | P0 — Fix immediately, drop other work | P1 — Next sprint, no exceptions |
| **Low Impact** | P2 — Schedule soon, workaround exists | P3 — Backlog, revisit quarterly |

**Impact** = how many users affected, how severely.
**Urgency** = how quickly the situation degrades without a fix.

P0 issues should trigger an incident response, not just a GitHub label.
P3 issues should be reviewed quarterly and closed if still not prioritized.

### When to Close vs When to Ask for More Info

Close immediately when:
- The issue is a duplicate (link to original)
- The behavior is intentional and documented
- The request is out of scope for the project
- The issue is a support question (redirect to Discussions or forum)

Ask for more info when:
- The bug cannot be reproduced from the description
- The feature request lacks a use case or motivation
- The environment details are missing (OS, version, config)

Set a response deadline when asking for info. Fourteen days is a reasonable
default. Use a stale bot to automate follow-up and closure.

### Triage SLA Recommendations

| Issue Type | First Response | Triage Complete | Resolution Target |
|------------|---------------|-----------------|-------------------|
| Security vulnerability | 24 hours | 48 hours | Coordinated disclosure timeline |
| P0 bug (data loss, outage) | 2 hours | 4 hours | Same day |
| P1 bug | 48 hours | 72 hours | Current sprint |
| P2 bug / feature | 48 hours | 1 week | Next sprint |
| P3 / enhancement | 48 hours | 2 weeks | Backlog |
| Documentation | 48 hours | 1 week | Next sprint |

The 48-hour first response SLA applies to all public issues. Silence erodes
contributor trust faster than any other factor.

---

## Cross-Referencing and Linking

### Closing Keywords

When a PR description or commit message contains a closing keyword followed by
an issue reference, GitHub automatically closes the issue when the PR merges
into the default branch.

Supported keywords (case-insensitive):

| Keyword | Variants |
|---------|----------|
| `closes` | `close`, `closed` |
| `fixes` | `fix`, `fixed` |
| `resolves` | `resolve`, `resolved` |

Usage in PR body:

```
Closes #42
Fixes #42
Resolves #42

# Multiple issues
Closes #42, closes #43
Fixes #42 and fixes #43
```

**Critical rule:** Closing keywords only trigger auto-close when the PR targets
the repository's default branch. A PR merged into a feature branch or release
branch will not close the issue. If your workflow uses non-default merge
targets, close issues manually or via a workflow step.

### Cross-Repository References

Reference an issue in another repository using the `owner/repo#N` format:

```
# Same organization, different repo
See also: myorg/backend#123

# Different organization
See also: facebook/react#12345
```

Cross-repo closing keywords work only within the same organization:

```
# In a PR in myorg/frontend, this closes myorg/backend#123
Fixes myorg/backend#123
```

Cross-org closing keywords are not supported. Close the issue manually.

### Linking Without Closing

To reference an issue without closing it, omit the closing keyword:

```
Related to #42
See #42 for context
Blocked by #42
Part of #42
```

GitHub renders these as hyperlinks and adds a cross-reference to the referenced
issue's timeline, creating bidirectional visibility.

---

## Sub-Issues (Parent-Child Hierarchy)

Sub-issues model hierarchical work: an epic broken into stories, a story broken
into tasks. GitHub supports sub-issues natively as of 2025.

### Limits

| Constraint | Value |
|------------|-------|
| Sub-issues per parent | 100 |
| Nesting depth | 8 levels |
| Cross-repo sub-issues | Supported within same organization |

### Creating Sub-Issues

From the issue sidebar, use "Add sub-issue" to attach an existing issue or
create a new one. Sub-issues appear as a progress tracker on the parent with
a completion percentage.

### When to Use Sub-Issues vs Task Lists vs Separate Issues

| Situation | Recommended Approach |
|-----------|---------------------|
| Work items need individual assignees | Sub-issues |
| Work items need separate PR tracking | Sub-issues |
| Work items are steps in a single task | Task list (checkboxes in body) |
| Work items are independent and may ship separately | Separate issues, linked by reference |
| Work items belong to different repositories | Sub-issues (cross-repo, same org) |
| Checklist for a single developer | Task list in issue body |

### Epic Pattern

Use a parent issue as an epic tracker. The parent issue body describes the
goal, acceptance criteria, and links to sub-issues. The parent stays open until
all sub-issues close.

Recommended epic body structure:

```
## Goal
One sentence describing the outcome.

## Acceptance Criteria
- [ ] Criterion one
- [ ] Criterion two

## Sub-Issues
Tracked automatically via GitHub sub-issue hierarchy.

## Notes
Design decisions, constraints, external dependencies.
```

Close the epic manually after verifying all acceptance criteria, even if all
sub-issues are closed. Automated closure of epics based on sub-issue completion
can mask incomplete acceptance criteria.

---

## Discussion to Issue Conversion

### When to Use Discussions vs Issues

| Signal | Use Discussions | Use Issues |
|--------|----------------|------------|
| Outcome is uncertain | Yes | No |
| Seeking community input | Yes | No |
| Work is clearly defined | No | Yes |
| Needs assignee and milestone | No | Yes |
| Exploratory / RFC | Yes | No |
| Bug report | No | Yes |
| Feature request (early stage) | Yes | No |
| Feature request (approved) | No | Yes |
| Support question | Yes | No |
| Tracking deliverable | No | Yes |

Discussions are for conversations. Issues are for work. When a discussion
reaches a decision — "yes, we will build this" — convert it to an issue.

### Conversion Workflow

1. In the Discussion, click the three-dot menu and select "Convert to issue."
2. GitHub creates an issue with the discussion body and links back to the discussion.
3. Add triage labels, milestone, and assignee to the new issue.
4. Post a comment in the original discussion linking to the new issue.
5. Lock the discussion to prevent further replies (optional but recommended).

---

## Security Advisory Pattern

Security issues must never be filed as public issues. Public disclosure before
a fix is available puts users at risk.

### Private Vulnerability Reporting Setup

Enable private vulnerability reporting in repository Settings > Security >
Vulnerability reporting. This allows reporters to submit vulnerabilities
directly to maintainers without public disclosure.

### SECURITY.md Requirements

Place `SECURITY.md` in the repository root or `.github/` directory. It must
include: supported version table, instructions to use private vulnerability
reporting instead of public issues, contact email, acknowledgment timeline
(24 hours), and disclosure policy (90-day coordinated disclosure is standard).

### Advisory Workflow

1. Reporter submits via private vulnerability reporting or email.
2. Maintainer acknowledges within 24 hours.
3. Maintainer creates a GitHub Security Advisory (draft) in the Security tab.
4. Maintainer develops fix in a private fork linked to the advisory.
5. Maintainer requests a CVE identifier through GitHub if applicable.
6. Fix is reviewed in the private fork.
7. Coordinated disclosure: fix merges, advisory publishes, CVE assigned.
8. Release notes reference the CVE without technical exploit details.

Never discuss vulnerability details in public issues, PRs, or commit messages
until the advisory is published.

---

## Monorepo Issue Management

Monorepos host multiple packages or applications in a single repository.
Without structure, issues become impossible to route.

### Label Strategy Per Package or App

Use area labels with package-specific prefixes:

```
area/pkg-auth
area/pkg-api
area/pkg-ui
area/app-dashboard
area/app-cli
```

Apply these labels at triage. Teams subscribe to label notifications to receive
only relevant issues.

### Routing Issues to Teams

Use CODEOWNERS to define team ownership, then reference teams in issue
comments when routing:

```
/cc @myorg/team-auth — this looks like an auth issue
```

For automated routing, a labeler workflow can apply area labels based on
file paths mentioned in the issue body or based on keywords. Once labeled,
team members with label subscriptions receive notifications automatically.

### Milestone Strategy in Monorepos

Avoid version-based milestones when packages release independently. Use
sprint-based (Sprint 2026-W10) or theme-based (Q1 Performance) milestones
that apply across packages. Per-package versioning belongs in changelogs and
release workflows, not GitHub milestones.

---

## Anti-Patterns

| Anti-Pattern | Problem | Better Approach |
|--------------|---------|-----------------|
| Issue as conversation thread | Loses actionability, hard to triage | Use Discussions for exploration; convert to issue when decision is made |
| Vague title ("Bug in login") | Unsearchable, no context | Descriptive title: "Login fails with SSO when session cookie is expired" |
| No reproduction steps | Cannot verify or fix | Require steps, expected behavior, actual behavior in template |
| Assigning to multiple people | Diffuses ownership | One assignee per issue; use sub-issues for parallel work |
| Closing without explanation | Alienates contributors | Always comment explaining why before closing |
| Reopening closed issues | Breaks audit trail | Open a new issue referencing the closed one |
| Mega-issues ("Improve performance") | Never closes, hard to prioritize | Break into specific, measurable sub-issues |
| Labels as status only | Misses type and area signal | Use namespaced labels: type/*, priority/*, area/*, status/* |
| Milestone as wishlist | Milestones become meaningless | Only add to milestone if committed to shipping in that cycle |
| Skipping triage | Backlog becomes noise | Triage every issue within 48 hours of creation |
| Using issues for secrets | Security risk | Never put credentials, tokens, or PII in issues |
| Linking without context | Reader must guess relationship | Explain the relationship: "Blocked by #42 because..." |
| Auto-closing stale issues | Closes valid but deprioritized work | Review before closing; add `status/deferred` instead |

---

## Issue Quality Checklist

### What Makes a Good Bug Report

A good bug report enables a developer who has never seen the problem to
reproduce it independently and verify a fix.

Required elements:

- **Title:** Describes the symptom, not the suspected cause. Includes the
  affected component if not obvious.
- **Environment:** OS, browser or runtime version, package version, relevant
  configuration.
- **Steps to reproduce:** Numbered, minimal, deterministic. Each step is a
  single action.
- **Expected behavior:** What should happen.
- **Actual behavior:** What actually happens. Include error messages verbatim,
  not paraphrased.
- **Reproduction rate:** Always, sometimes, once. If intermittent, describe
  conditions.
- **Minimal reproduction:** A link to a repository, CodeSandbox, or snippet
  that isolates the issue. This is the single highest-value element.

Optional but valuable:

- Screenshots or screen recordings for visual bugs.
- Logs with timestamps.
- Workaround if one exists.

### What Makes a Good Feature Request

A good feature request explains the problem being solved, not just the
solution. Required elements: problem statement (what is painful or impossible),
proposed solution (one concrete approach), alternatives considered, and use
case (who benefits and how often). Maintainers need motivation to evaluate fit
and design alternatives.

### Bug Report Quality Scoring

| Element | Present | Missing |
|---------|---------|---------|
| Descriptive title | +2 | -2 |
| Environment details | +2 | -1 |
| Steps to reproduce | +3 | -3 |
| Expected vs actual | +2 | -2 |
| Minimal reproduction | +4 | 0 |
| Error messages verbatim | +2 | -1 |

Score 10+: Ready to implement. Score 5-9: Needs clarification. Score below 5:
Request more information before triaging.

### Checklist Before Closing a Feature Request

- Is this covered by an existing feature the reporter may not know about?
- Is this a duplicate of a previously declined issue?
- If declining, is the reason documented so future reporters can find it?
- If accepting, is the issue triaged with priority, milestone, and labels?

---

## Summary: Workflow Principles

1. Every issue must pass triage before development begins.
2. Closing keywords link PRs to issues — use them consistently.
3. Sub-issues model hierarchy; task lists model steps within a single issue.
4. Security issues are never public until a fix is available.
5. Discussions are for decisions; issues are for work.
6. A good bug report includes a minimal reproduction. Everything else is secondary.
7. Triage SLAs protect contributor trust. Silence is the fastest way to lose contributors.
8. Anti-patterns compound over time. A backlog of vague issues is a team dysfunction.
