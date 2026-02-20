---
name: skill-creator
description: |
  Create skills that extend AI agent capabilities with synthesized domain expertise.
  Covers skill anatomy, progressive disclosure, research workflow (books + web),
  writing conventions, and ecosystem patterns.

  Trigger phrases: "create a skill", "new skill", "build a skill", "skill about",
  "make a skill for", "update skill", "improve skill", "write a skill"
---

# Skill Creator

Transform general-purpose agents into domain specialists by synthesizing
knowledge from authoritative books, web research, and reusable resources.

## Core Philosophy

1. **Context window is a public good** — Agent is already smart. Only add
   information it lacks. Challenge every paragraph's token cost.
2. **Synthesize, never summarize** — Extract frameworks, decision trees,
   actionable patterns. Never copy verbatim.
3. **Progressive disclosure** — SKILL.md under 200 lines. Deep knowledge in
   `references/`, deterministic code in `scripts/`, templates in `assets/`.
4. **Match freedom to fragility** — Text instructions for flexible tasks,
   pseudocode for preferred patterns, exact scripts for fragile operations.
5. **Understand before building** — Collect concrete examples before research.
   Skills from real examples outperform skills from abstract knowledge.
6. **Save research to disk** — Skill creation generates massive context.
   Save to `/tmp/{skill-name}-research/` immediately.

## Skill Anatomy

```
skill-name/
├── SKILL.md              # Entry point: frontmatter + workflow + file index
├── skills.json           # Permissions: filesystem, network, subprocess
├── references/           # Docs loaded on demand (250-450 lines each)
├── scripts/              # Executable code for deterministic tasks
└── assets/               # Templates, images (not loaded into context)
```

## Quick-Start: Common Problems

### "Skill doesn't activate"

1. Check `description` field — must include trigger phrases + scenarios
2. Add 10-15 trigger phrases covering user phrasings
3. Include specific file types, tools, tasks in description
4. The body loads AFTER triggering — "When to Use" sections are wasted

### "Agent gives generic advice"

1. Reference files need more specific, actionable content
2. Add decision trees, frameworks, concrete tables
3. Replace prose with step-by-step procedures
4. Verify agent is loading the right reference file

### "Reference files wrong length"

1. Target 250-450 lines per file
2. Split large files, merge small ones
3. Each file covers distinct subtopic — no overlap

## Workflow

### Phase 1: Scope and Research

1. **Define scope** — Ask: domain, tasks, triggers, style reference
2. **Study ecosystem** — Browse skills.sh leaderboard. Study top skills:
   - `anthropics/skills` (frontend-design, skill-creator)
   - `vercel-labs/agent-skills` (react, web-design)
   - `obra/superpowers` (debugging, tdd, planning)
3. **Collect examples** — Concrete queries skill should handle
4. **Research books** — 6-10 authoritative books (2018+)
5. **Acquire books** — Purchase or access through library/publisher
6. **Extract frameworks** — Use `look_at` on books. Save to `/tmp/`
7. **Quality gate** — 4+ books extracted before Phase 2

### Phase 2: Plan Structure

1. **Plan reference files** — 5-9 files, each from 2+ books
2. **Analyze resource types** — Script vs reference vs asset

### Phase 3: Write Content

1. **Write reference files** — Parallel agents, books as primary source
2. **Verify** — Format, length, sources, no overlap

### Phase 4: Deploy

1. **Write SKILL.md** — Under 200 lines
2. **Create skills.json** — Minimal permissions
3. **Git commit and push**

See `references/research-workflow.md` for detailed procedures.

## Decision Trees

### Resource Type Selection

| Content | Type | Loaded? |
|---------|------|---------|
| Domain knowledge, frameworks | `references/` | Yes, on demand |
| Deterministic code, automation | `scripts/` | No, executed |
| Templates, images, boilerplate | `assets/` | No, output |
| Core workflow, triggers | SKILL.md | Yes, on activate |

### SKILL.md Structure

| Skill Type | Pattern | Example |
|-----------|---------|---------|
| Sequential processes | Workflow-based | Editor: Create → Edit → Export |
| Multiple operations | Task-based | PDF: Merge, Split, Extract |
| Standards/rules | Guidelines | Brand: Colors, Typography, Voice |
| Interrelated features | Capabilities | PM: Context, Updates, Comms |

### Instruction Freedom Level

| Signal | Freedom | Format |
|--------|---------|--------|
| Multiple valid approaches | High | Text instructions |
| Preferred pattern + variation | Medium | Pseudocode |
| Fragile operation, exact sequence | Low | Specific script |

## Tank-Skill Patterns

Observed in 20 skills:

| Pattern | Lines | Example Skills |
|---------|-------|----------------|
| Best practices | 47-115 | react, typescript, python, clean-code |
| Methodology | 143-291 | systematic-debugging, planning, tdd |
| Operational | 137-382 | playwright, security-review, gmail |
| Integration | 100-250 | notion, slack, google-calendar |

### skills.json Permissions

```json
{
  "network": [],
  "filesystem": {
    "read": ["**/*"],
    "write": []
  },
  "subprocess": false
}
```

Only add permissions when actually needed.

## Reference Files

| File | Contents |
|------|----------|
| `references/skill-design-patterns.md` | Context window principle, degrees of freedom, progressive disclosure, resource types, SKILL.md patterns, what NOT to include |
| `references/research-workflow.md` | Scope definition, ecosystem study, book research, Anna's Archive, framework extraction, scratch file protocol, parallel writing delegation |
| `references/writing-conventions.md` | Frontmatter rules, body structure, reference file format, quality standards, completion checklist |
| `references/ecosystem-patterns.md` | skills.sh leaderboard analysis, top publisher patterns, tank-skills conventions, supported agents |
