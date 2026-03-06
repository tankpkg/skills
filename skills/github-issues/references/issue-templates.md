# Issue Templates and Forms

Sources: GitHub documentation, production OSS template patterns (React, VS Code, Vue.js)

---

## Directory Structure

Place all template files under `.github/ISSUE_TEMPLATE/`. GitHub discovers them automatically.

```
.github/
└── ISSUE_TEMPLATE/
    ├── config.yml          # Template chooser configuration
    ├── bug-report.yml      # Issue Form (structured)
    ├── feature-request.yml # Issue Form (structured)
    └── custom.md           # Classic Template (freeform)
```

Rules:
- File names become the template slug used in URL pre-filling.
- Both `.yml` and `.yaml` extensions are accepted for Issue Forms.
- Classic templates use `.md` extension.
- `config.yml` is reserved for the template chooser; do not use it as a template.

---

## Classic Templates (.md)

Classic templates are Markdown files with a YAML frontmatter block. They pre-populate the issue body with freeform Markdown.

### Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Display name shown in the template chooser |
| `about` | string | No | Short description shown below the name in the chooser |
| `title` | string | No | Default issue title pre-filled in the title field |
| `labels` | string or list | No | Labels applied automatically on submission |
| `assignees` | string or list | No | GitHub usernames assigned automatically on submission |

Classic templates have no field-level validation — users can delete or ignore any section. Labels and assignees are applied but users can remove them before submitting. For new projects, prefer Issue Forms.

---

## Issue Forms (.yml)

Issue Forms replace freeform Markdown with structured YAML. Each field renders as a distinct UI element with optional validation. Supported on GitHub.com and GitHub Enterprise Server 3.3+.

### Top-Level Keys

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `name` | string | Yes | Display name in the template chooser |
| `description` | string | Yes | Short description shown in the chooser |
| `title` | string | No | Default issue title; supports static text |
| `labels` | list of strings | No | Labels applied on submission; must exist in the repository |
| `assignees` | list of strings | No | GitHub usernames assigned on submission |
| `projects` | list of strings | No | Project board paths (`org/project-number`) to add the issue to |
| `type` | string | No | Issue type slug (if issue types are enabled for the organization) |
| `body` | list of elements | Yes | Ordered list of form elements rendered in sequence |

---

## Form Element Reference

### markdown

Renders static Markdown text. Not submitted as part of the issue body. Use for instructions, warnings, or section headers.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | string | Yes | Must be `markdown` |
| `attributes.value` | string | Yes | Markdown content to render |

No `id` or `validations` keys are supported on `markdown` elements.

---

### input

Renders a single-line text field.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | string | Yes | Must be `input` |
| `id` | string | No | Unique identifier used in URL pre-filling |
| `attributes.label` | string | Yes | Field label displayed above the input |
| `attributes.description` | string | No | Helper text displayed below the label |
| `attributes.placeholder` | string | No | Placeholder text inside the input |
| `attributes.value` | string | No | Default value pre-filled in the input |
| `validations.required` | boolean | No | If `true`, submission is blocked when empty |

`id` values must be unique across all elements. Use lowercase letters, digits, and hyphens only.

---

### textarea

Renders a multi-line text area. Supports syntax highlighting via `render`.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | string | Yes | Must be `textarea` |
| `id` | string | No | Unique identifier used in URL pre-filling |
| `attributes.label` | string | Yes | Field label displayed above the textarea |
| `attributes.description` | string | No | Helper text displayed below the label |
| `attributes.placeholder` | string | No | Placeholder text inside the textarea |
| `attributes.value` | string | No | Default content pre-filled in the textarea |
| `attributes.render` | string | No | Language identifier for syntax highlighting (e.g., `javascript`, `bash`, `json`) |
| `validations.required` | boolean | No | If `true`, submission is blocked when empty |

When `render` is set, the textarea content is wrapped in a fenced code block in the submitted issue body. Use this for stack traces, configuration files, and log output.

---

### dropdown

Renders a single-select or multi-select dropdown menu.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | string | Yes | Must be `dropdown` |
| `id` | string | No | Unique identifier used in URL pre-filling |
| `attributes.label` | string | Yes | Field label displayed above the dropdown |
| `attributes.description` | string | No | Helper text displayed below the label |
| `attributes.multiple` | boolean | No | If `true`, allows selecting multiple options |
| `attributes.options` | list of strings | Yes | Ordered list of selectable options |
| `attributes.default` | integer | No | Zero-based index of the pre-selected option |
| `validations.required` | boolean | No | If `true`, submission is blocked when no option is selected |

Options cannot be empty strings. The string `"none"` is a reserved word and cannot be used as an option value.

---

### checkboxes

Renders a list of checkboxes. Each checkbox can be individually required.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | string | Yes | Must be `checkboxes` |
| `id` | string | No | Unique identifier used in URL pre-filling |
| `attributes.label` | string | Yes | Section label displayed above the checkboxes |
| `attributes.description` | string | No | Helper text displayed below the label |
| `attributes.options` | list of objects | Yes | List of checkbox option objects |
| `attributes.options[].label` | string | Yes | Markdown-supported label for the checkbox |
| `attributes.options[].required` | boolean | No | If `true`, this specific checkbox must be checked to submit |
| `validations.required` | boolean | No | If `true`, at least one checkbox must be checked |

Per-item `required` and top-level `validations.required` are independent. Use per-item `required` for mandatory acknowledgments.

---

## Template Chooser (config.yml)

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `blank_issues_enabled` | boolean | No | If `false`, hides the "Open a blank issue" link. Default: `true` |
| `contact_links` | list of objects | No | External links shown alongside templates in the chooser |
| `contact_links[].name` | string | Yes | Display name of the link |
| `contact_links[].url` | string | Yes | Absolute URL |
| `contact_links[].about` | string | Yes | Short description shown below the link name |

```yaml
blank_issues_enabled: false
contact_links:
  - name: Security Vulnerability
    url: https://example.com/security
    about: Report security vulnerabilities through our private disclosure process.
  - name: Community Forum
    url: https://github.com/org/repo/discussions
    about: Ask questions and discuss ideas with the community.
```

Setting `blank_issues_enabled: false` forces all issues through a template. Use this when unstructured reports consistently lack required information.

---

## URL Pre-Filling via Query Parameters

Pre-fill issue fields by appending query parameters to the new issue URL. Useful for linking from documentation, error messages, or CI output.

Base URL: `https://github.com/{owner}/{repo}/issues/new`

### Supported Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `template` | File name of the template (with extension) | `template=bug-report.yml` |
| `title` | Pre-fills the issue title field | `title=Bug%3A+login+fails` |
| `labels` | Comma-separated label names | `labels=bug,needs-triage` |
| `assignees` | Comma-separated GitHub usernames | `assignees=octocat` |
| `milestone` | Milestone ID (integer) | `milestone=4` |

For Issue Forms, use the element's `id` as the query parameter key to pre-fill its value:

```
https://github.com/org/repo/issues/new?template=bug-report.yml&reproduction-url=https%3A%2F%2Fcodesandbox.io%2Fs%2Fabc
```

Pre-filling works for `input`, `textarea`, and `dropdown` elements. Checkboxes cannot be pre-filled via URL parameters.

---

## Classic Templates vs. Issue Forms

| Capability | Classic (.md) | Issue Forms (.yml) |
|------------|--------------|-------------------|
| Required field enforcement | No | Yes (per field) |
| Dropdown menus | No | Yes |
| Checkbox lists | No | Yes |
| Syntax-highlighted code blocks | No | Yes (via `render`) |
| Per-item checkbox required | No | Yes |
| URL pre-filling by field id | No | Yes |
| Freeform Markdown body | Yes | No (structured only) |
| GitHub Enterprise Server | All versions | 3.3+ |
| Recommended for new projects | No | Yes |

---

## Common Validation Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `name is required` | Top-level `name` key missing | Add `name:` to the form |
| `description is required` | Top-level `description` key missing | Add `description:` to the form |
| `body is required` | `body` key missing or empty list | Add at least one element to `body` |
| `id must be unique` | Two elements share the same `id` value | Rename one `id` to be unique |
| `label must be unique` | Two elements share the same `label` value | Rename one label |
| `options cannot be empty` | A dropdown or checkbox has an empty `options` list | Add at least one option |
| `"none" is a reserved word` | A dropdown option is the string `"none"` | Rename the option |
| `default must be a valid index` | `default` value exceeds the options list length | Use a zero-based index within range |
| `label is required for input` | An `input` element has no `attributes.label` | Add `label:` under `attributes` |
| `value is required for markdown` | A `markdown` element has no `attributes.value` | Add `value:` under `attributes` |
| `labels must exist in repository` | A label in top-level `labels` does not exist | Create the label or correct the spelling |
| `id contains invalid characters` | An `id` uses uppercase letters, spaces, or special characters | Use only lowercase letters, digits, and hyphens |
| `type is not recognized` | An element `type` is misspelled | Use: `markdown`, `input`, `textarea`, `dropdown`, `checkboxes` |

---

## Production-Ready Examples

### Bug Report Form

```yaml
name: Bug Report
description: Report a reproducible bug in the project.
title: "[Bug]: "
labels: ["bug", "needs-triage"]
body:
  - type: markdown
    attributes:
      value: |
        Reports missing a reproduction link or steps to reproduce will be closed
        without investigation.

  - type: checkboxes
    id: pre-submission
    attributes:
      label: Pre-Submission Checklist
      options:
        - label: I have searched existing issues and this is not a duplicate.
          required: true
        - label: I can reproduce this bug on the latest release.
          required: true

  - type: input
    id: reproduction-url
    attributes:
      label: Reproduction URL
      description: Link to a minimal reproduction (CodeSandbox, StackBlitz, or public GitHub repo).
      placeholder: https://codesandbox.io/s/...
    validations:
      required: true

  - type: textarea
    id: steps-to-reproduce
    attributes:
      label: Steps to Reproduce
      placeholder: "1. \n2. \n3. "
    validations:
      required: true

  - type: textarea
    id: expected-behavior
    attributes:
      label: Expected Behavior
    validations:
      required: true

  - type: textarea
    id: actual-behavior
    attributes:
      label: Actual Behavior
    validations:
      required: true

  - type: textarea
    id: error-output
    attributes:
      label: Error Output
      description: Paste the full error message or stack trace.
      render: bash

  - type: dropdown
    id: os
    attributes:
      label: Operating System
      options: [macOS, Windows, Linux, Other]
    validations:
      required: true

  - type: input
    id: version
    attributes:
      label: Package Version
      placeholder: "1.2.3"
    validations:
      required: true

  - type: input
    id: node-version
    attributes:
      label: Node.js Version
      placeholder: "v20.0.0"
    validations:
      required: true
```

---

### Feature Request Form

```yaml
name: Feature Request
description: Propose a new feature or enhancement.
title: "[Feature]: "
labels: ["enhancement"]
body:
  - type: checkboxes
    id: pre-submission
    attributes:
      label: Pre-Submission Checklist
      options:
        - label: I have searched existing issues and this feature has not been requested.
          required: true

  - type: textarea
    id: problem-statement
    attributes:
      label: Problem Statement
      description: >
        Describe the problem you are trying to solve. Focus on the problem,
        not the solution.
    validations:
      required: true

  - type: textarea
    id: proposed-solution
    attributes:
      label: Proposed Solution
      description: Describe the solution you would like, including API design or UI changes.
    validations:
      required: true

  - type: textarea
    id: alternatives
    attributes:
      label: Alternatives Considered
      description: Alternative solutions or workarounds you have considered.

  - type: dropdown
    id: priority
    attributes:
      label: Priority
      options:
        - Critical — blocking my use of the project
        - High — significantly impacts my workflow
        - Medium — would be a meaningful improvement
        - Low — nice to have
      default: 2
    validations:
      required: true

  - type: dropdown
    id: affected-areas
    attributes:
      label: Affected Areas
      multiple: true
      options: [API, Configuration, CLI, Documentation, Performance, TypeScript types, Other]

  - type: textarea
    id: additional-context
    attributes:
      label: Additional Context
      description: Links to related issues, prior art, or other supporting context.
```

---

## Best Practices

**Pre-submission checklist.** Always include a `checkboxes` element with `required: true` per item for duplicate search confirmation, latest version verification, and contributing guidelines acknowledgment. This reduces duplicate reports without requiring maintainer intervention.

**Reproduction links.** Make the reproduction URL an `input` element with `validations.required: true`. Name accepted platforms in the `description` (CodeSandbox, StackBlitz, GitHub repo). Unverifiable bugs without reproductions consume disproportionate maintainer time.

**Environment dropdowns.** Use `dropdown` elements for OS, browser, and runtime rather than freeform `input` fields. Structured values enable filtering and searching across issues. Supplement with an `input` for the exact version string.

**Code blocks via render.** Set `render` on `textarea` elements that collect stack traces, configuration files, or log output. The submitted issue body wraps the content in a fenced code block automatically, preserving formatting and enabling syntax highlighting.

**Label strategy.** Declare labels in the top-level `labels` key of Issue Forms rather than relying on users to apply them. Combine with `blank_issues_enabled: false` in `config.yml` to ensure every issue enters the triage queue with at least one label.

**Title prefixes.** Set `title` to a prefix such as `"[Bug]: "` to make the issue list scannable without opening each issue. Keep prefixes short and consistent across templates.

**Field order.** Order fields from highest to lowest diagnostic value: pre-submission checklist, reproduction URL, description and steps, environment details, optional context. Users who abandon the form mid-way are more likely to have completed the high-value fields.

**Form length.** Limit forms to 8-12 fields. Forms with more than 15 fields see significantly lower completion rates. Consolidate optional context into a single freeform `textarea` at the end rather than creating dedicated fields for every edge case.
