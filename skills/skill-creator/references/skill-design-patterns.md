# Skill Design Patterns

Sources: Anthropic skill architecture, OpenCode skill framework, production skill analysis

## The Context Window Is a Public Good

Skills share the context window with system prompt, conversation history, other
skills' metadata, and the user's request. Every line has a token cost.

**Default: the agent is already smart.** Only include information the agent
lacks. For every paragraph:

- Does the agent need this explanation?
- Does this paragraph justify its token cost?
- Could a concise example replace verbose description?

Prefer 3-line code blocks over 10-line paragraphs.

## Degrees of Freedom

Match specificity to task fragility. Agent explores a path: narrow bridge needs
guardrails (low freedom), open field allows many routes (high freedom).

### High Freedom (text instructions)

Multiple approaches valid, decisions depend on context:

```markdown
## Writing Style
Use professional tone. Adapt formality to audience — enterprise formal,
startup casual. Prioritize clarity over cleverness.
```

### Medium Freedom (pseudocode)

Preferred pattern exists with acceptable variation:

```markdown
## Generating Reports
1. Query data source for time range
2. Group by user-specified dimension
3. Apply standard template from assets/
4. Customize executive summary based on findings
```

### Low Freedom (specific scripts)

Fragile operations, consistency critical, exact sequence required:

```markdown
## Rotating a PDF
Run the rotation script — do not implement manually:
python3 scripts/rotate_pdf.py --input {file} --degrees {90|180|270}
```

### Selection Guide

| Signal | Freedom | Example |
|--------|---------|---------|
| Multiple valid approaches | High | Writing style, research strategy |
| One preferred pattern | Medium | Report generation, data analysis |
| Fragile operations | Low | PDF manipulation, API calls, deployments |
| User-facing output | Medium-High | Content creation, design |
| System integration | Low | File parsing, build scripts |

## Progressive Disclosure

Three-level loading system:

| Level | What | When Loaded | Size |
|-------|------|-------------|------|
| 1. Metadata | `name` + `description` | Always | ~100 words |
| 2. SKILL.md body | Instructions, workflows | On trigger | <200 lines |
| 3. Resources | references/, scripts/, assets/ | On demand | Unlimited |

### Pattern 1: High-Level Guide with References

SKILL.md as navigation hub:

```markdown
# PDF Processing

## Quick Start
Extract text with pdfplumber:
[brief example]

## Advanced
- **Forms**: See references/forms.md
- **API**: See references/api.md
- **Examples**: See references/examples.md
```

### Pattern 2: Domain-Specific Organization

For multi-domain skills:

```
bigquery-skill/
├── SKILL.md (overview + domain selection)
└── references/
    ├── finance.md (revenue, billing)
    ├── sales.md (opportunities, pipeline)
    ├── product.md (usage, features)
    └── marketing.md (campaigns, attribution)
```

### Pattern 3: Conditional Details

Basic inline, advanced linked:

```markdown
# Document Processing

## Creating Documents
Use docx-js for new documents. See references/docx-js.md.

## Editing
For simple edits, modify XML directly.

**Tracked changes**: See references/redlining.md
**OOXML details**: See references/ooxml.md
```

### Rules

- SKILL.md body under 200 lines (500 Anthropic convention)
- Split content when approaching limit
- Reference files MUST be linked from SKILL.md
- Keep references one level deep from SKILL.md
- Files over 100 lines: include scope summary

## Three Resource Types

```
skill-name/
├── SKILL.md              # Required: frontmatter + instructions
├── scripts/              # Executable code
├── references/           # Context-loaded docs
└── assets/               # Output templates
```

### Scripts (`scripts/`)

Deterministic reliability or repeated code:

| When | Examples |
|------|----------|
| Same code rewritten each time | rotate_pdf.py, convert_image.py |
| Deterministic reliability | validate_schema.py, run_migration.py |
| Multi-step automation | deploy.sh, setup_environment.py |

**Benefit**: Token efficient, executed without loading.

### References (`references/`)

Context-loaded documentation:

| When | Examples |
|------|----------|
| Domain knowledge | finance.md, policies.md |
| API documentation | api_docs.md |
| Workflow guides | deployment-guide.md |
| Synthesized books | copywriting.md, pricing.md |

**Best practice**: For large files, include grep patterns in SKILL.md.

### Assets (`assets/`)

Files used in output, not loaded:

| When | Examples |
|------|----------|
| Templates | report-template.pptx, email-template.html |
| Brand assets | logo.png, brand-fonts/ |
| Boilerplate | hello-world/ starter |
| Sample data | sample-data.csv, test-fixtures.json |

## SKILL.md Structuring Patterns

### Pattern A: Workflow-Based

Sequential procedures:

```markdown
# Document Editor

## Workflow Decision Tree
- Creating new? → Creation Workflow
- Editing existing? → Editing Workflow

## Creation Workflow
### Step 1: ...

## Editing Workflow
### Step 1: ...
```

### Pattern B: Task-Based

Different operations:

```markdown
# PDF Toolkit

## Quick Start
[Most common operation]

## Merge PDFs
[How to merge]

## Split PDFs
[How to split]

## Extract Text
[How to extract]
```

### Pattern C: Reference/Guidelines

Standards or specifications:

```markdown
# Brand Guidelines

## Colors
[Specifications]

## Typography
[Specifications]

## Voice and Tone
[Guidelines]
```

### Pattern D: Capabilities-Based

Interrelated features:

```markdown
# Product Management

## Core Capabilities
### 1. Context Building
### 2. Status Updates
### 3. Stakeholder Communication
```

## Output Patterns

### Template Pattern

Match strictness to requirements:

**Strict**:

```markdown
ALWAYS use this structure:

# [Title]

## Executive Summary
[One paragraph]

## Key Findings
- Finding 1 with data

## Recommendations
1. Actionable recommendation
```

**Flexible**:

```markdown
Sensible default — adapt as needed:

# [Title]
## Summary
## Findings (adapt sections)
## Recommendations (tailor)
```

### Examples Pattern

Input/output pairs teach style:

```markdown
## Commit Messages

**Example 1:**
Input: Added user authentication with JWT
Output: feat(auth): implement JWT-based authentication

**Example 2:**
Input: Fixed date display bug
Output: fix(reports): correct date formatting

Style: type(scope): brief description
```

## What NOT to Include

| Forbidden | Why |
|-----------|-----|
| README.md | Skill is for AI, not humans |
| INSTALLATION_GUIDE.md | Framework handles installation |
| QUICK_REFERENCE.md | SKILL.md IS the quick reference |
| CHANGELOG.md | Version history adds no value |
| CONTRIBUTING.md | Agent doesn't accept contributions |

Only include what the agent needs. No auxiliary context.
