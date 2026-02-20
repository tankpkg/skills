# Writing Conventions

Sources: Production skill analysis, Anthropic framework, OpenCode conventions

## SKILL.md Conventions

### Frontmatter

Every SKILL.md starts with YAML frontmatter:

```yaml
---
name: skill-name
description: |
  What the skill does — 2-3 lines covering scope and capabilities.
  Source attribution — books, frameworks, research synthesized.

  Trigger phrases: "phrase 1", "phrase 2", "phrase 3"
---
```

**`name`**: Kebab-case matching directory name. Lowercase, digits, hyphens.
Max 64 characters.

**`description`**: PRIMARY triggering mechanism. Agent reads ONLY description
to decide loading. Body loads AFTER triggering.

Must include:
- What skill does (scope, capabilities)
- Source attribution (books, frameworks)
- Trigger phrases (10-15 specific words/phrases)

Do not include: `version`, `author`, `tags`, `license` (unless legally required).

### Body Structure

```markdown
# {Skill Title}

## Core Philosophy
{3-5 foundational principles, 1-2 lines each}

## Quick-Start: {Primary Workflow or Problems}
### "{Common Problem 1}"
1. Step
2. Step
-> See `references/{file}.md`

### "{Common Problem 2}"
1. Step
-> See `references/{file}.md`

## Decision Trees
### {Decision Point}
| Signal | Recommendation |
|--------|---------------|
| ... | ... |

## Reference Files
| File | Contents |
|------|----------|
| references/{file}.md | One-line description |
```

### Body Rules

- **Under 200 lines** (stricter than Anthropic's 500)
- **Imperative form**: "Run the script" not "You should run"
- **Problem-solution pairs**: Frame as problems users bring
- **Decision trees as tables**: Not prose
- **Reference index at end**: Map every file to one-line description

### What NOT in SKILL.md

| Content | Where |
|---------|-------|
| Detailed workflows (20+ steps) | `references/` |
| API documentation | `references/` |
| Code examples (10+ lines) | `scripts/` or `references/` |
| Templates | `assets/` |
| "When to Use This Skill" | `description` field |
| Installation instructions | Not in skill |
| Changelog | Not in skill |
| README | Not in skill |

## Reference File Conventions

### Format

```markdown
# {Title}

Sources: Author1 (Book1), Author2 (Book2), {year} industry research

## {Major Section}

{Content: tables, frameworks, examples}

### {Subsection}

{More specific content}
```

### Rules

| Rule | Requirement |
|------|-------------|
| First line | `# Title` (H1) |
| Second line | Blank |
| Third line | `Sources: {attribution}` |
| Sections | `##` major, `###` subsection |
| Line count | 250-450 lines |
| Frontmatter | None (only SKILL.md) |
| Emoji | None |
| Tone | Professional, imperative |
| Tables | Use for comparisons, frameworks |
| Code blocks | Include language annotation |

### Content Quality

**Synthesize, never summarize**: Extract frameworks, decision trees, patterns.
Should feel like practitioner cheat sheet, not book report.

**Cross-source synthesis**: Draw from 2+ sources. Combine Author A's framework
with Author B's examples into unified reference.

**Actionable over theoretical**: Every section answers "What do I DO?"
If section only explains concept without framework/table/procedure, revise.

**No verbatim copying**: Synthesize into own frameworks. Direct quotes only
for short, attributed phrases that capture concepts uniquely.

### Scope Summary

For 250-450 line files, include brief scope after Sources:

```markdown
# Dashboard Design

Sources: Cotgreave (Dashboards That Deliver), 2025 research

Covers: dashboard types, layout patterns, chart selection, real-time UX.

## Dashboard Types
...
```

### Avoiding Overlap

Each file covers distinct subtopic. Create boundary map:

| File | Covers | Does NOT Cover |
|------|--------|----------------|
| onboarding.md | Signup → activation | Post-activation retention |
| retention.md | Post-activation engagement | Initial onboarding |
| pricing.md | Pricing page design | General conversion |
| conversion.md | Non-pricing conversion | Pricing patterns |

When overlap possible, assign to one file and cross-reference:

```markdown
For pricing conversion patterns, see `references/pricing.md`.
```

## Style Reference

Read existing skill before writing:

| Reference | Use For |
|-----------|---------|
| meta-ads-mastery/SKILL.md | SKILL.md structure and tone |
| meta-ads-mastery/references/copywriting.md | Reference file formatting |
| saas-ux-expert/SKILL.md | Problem-solution Quick-Start |
| saas-ux-expert/references/ai-native-ux.md | Technical reference with tables |

Read BEFORE writing. Do not rely on memory.

## Completion Checklist

### SKILL.md

- [ ] YAML frontmatter has `name` and `description` only
- [ ] `description` includes trigger phrases (10-15)
- [ ] `description` includes scope, capabilities, sources
- [ ] Body under 200 lines
- [ ] Imperative form throughout
- [ ] Core Philosophy section (3-5 principles)
- [ ] Quick-Start or problem-solution section
- [ ] 2-3 decision trees or tables
- [ ] Reference Files index table as final section
- [ ] Every reference file listed in index

### Reference Files

- [ ] 5-9 reference files
- [ ] Each 250-450 lines
- [ ] Each starts with `# Title` then `Sources:` line
- [ ] No YAML frontmatter
- [ ] No emoji
- [ ] No content overlap
- [ ] No verbatim copying
- [ ] Professional tone, imperative form
- [ ] Tables for frameworks/comparisons

### Deployment

- [ ] Git committed with descriptive message
- [ ] Git pushed
- [ ] `install.sh` run
- [ ] `install.sh status` shows skill linked

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Passive voice | "Should be generated" weak | "Generate the report" — imperative |
| Generic advice | "Use best practices" teaches nothing | "Use 3-tier pricing with center-stage" — specific |
| Wall of text | Agent skips paragraphs | Break into tables, lists, short paras |
| Missing cross-refs | Agent doesn't know related content | Link to other reference files |
| Duplicate content | Same info in SKILL.md and reference | Pick one location, reference from other |
| Description too short | Skill never triggers | 10-15 triggers + scenarios |
| No examples | Agent guesses format | Add input/output pairs or templates |
| Over-explaining basics | Token waste | Only include what agent lacks |
| Missing file index | Agent can't discover files | Always end with reference table |
| Too many decisions | Agent paralyzed | Recommend default, note alternatives |
