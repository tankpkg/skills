# Ecosystem Patterns

Sources: skills.sh leaderboard analysis, tank-skills repo patterns, Agent Skills specification

## skills.sh Leaderboard (2025)

### Top Skills by Installs

| Rank | Skill | Publisher | Installs |
|------|-------|-----------|----------|
| 1 | find-skills | vercel-labs/skills | 277.9K |
| 2 | vercel-react-best-practices | vercel-labs | 151.5K |
| 3 | web-design-guidelines | vercel-labs | 114.6K |
| 4 | remotion-best-practices | vercel-labs | 101.5K |
| 5 | frontend-design | anthropics/skills | 84.9K |
| 6 | vercel-composition-patterns | vercel-labs | 49.6K |
| 7 | agent-browser | community | 48.5K |
| 8 | skill-creator | anthropics/skills | 41.3K |
| 9 | browser-use | community | 35.3K |
| 10 | vercel-react-native-skills | vercel-labs | 35.1K |

### Key Publishers

#### anthropics/skills

Official Anthropic skills with progressive disclosure patterns:

| Skill | Focus | Pattern |
|-------|-------|---------|
| frontend-design | UI/UX patterns | Reference-based |
| skill-creator | Skill creation | Workflow + references |
| pdf | PDF operations | Task-based |
| pptx | Presentations | Task-based |
| docx | Documents | Task-based |
| xlsx | Spreadsheets | Task-based |
| webapp-testing | E2E testing | Workflow-based |
| mcp-builder | MCP servers | Workflow-based |
| canvas-design | Visual design | Guidelines-based |
| brand-guidelines | Branding | Reference-based |

**Pattern**: Strong progressive disclosure, detailed reference files,
minimal SKILL.md body (often <100 lines).

#### vercel-labs/agent-skills

Impact-prioritized rules with before/after examples:

| Skill | Focus | Pattern |
|-------|-------|---------|
| react-best-practices | React patterns | Rules + examples |
| web-design-guidelines | Web design | Guidelines |
| composition-patterns | React composition | Examples-heavy |
| react-native-skills | React Native | Platform-specific |

**Pattern**: High-impact rules first, extensive code examples,
before/after comparisons.

#### obra/superpowers

Composable skill delegation, minimal surface area:

| Skill | Focus | Pattern |
|-------|-------|---------|
| brainstorming | Ideation | Workflow-based |
| systematic-debugging | Debugging | Methodology |
| writing-plans | Planning | Workflow |
| tdd | Test-driven | Methodology |
| executing-plans | Execution | Workflow |

**Pattern**: Clear phases, explicit outputs, composable (skills call other skills).

#### coreyhaines31/marketingskills

Domain-specific marketing skills:

| Skill | Focus |
|-------|-------|
| seo-audit | Technical SEO |
| copywriting | Ad copy, headlines |
| marketing-psychology | Persuasion principles |
| programmatic-seo | Scale SEO |
| content-strategy | Content planning |

**Pattern**: Deep domain expertise, book-synthesized references.

## Tank-Skills Patterns (20 Skills Analyzed)

### Skill Categories by Length

| Pattern | Lines | Example Skills | Structure |
|---------|-------|----------------|-----------|
| Best practices | 47-115 | react, typescript, python, clean-code | Hierarchical bullets, no code |
| Methodology | 143-291 | systematic-debugging, planning, tdd | Philosophy → phases → mistakes |
| Operational | 137-382 | playwright, security-review, gmail | Triggers → workflow → failure map |
| Integration | 100-250 | notion, slack, google-calendar | API patterns → operations |

### Directory Structure Convention

```
skills/[kebab-name]/
├── SKILL.md              # Required
├── skills.json           # Required (permissions)
├── LICENSE               # MIT standard
└── optional: references/, scripts/, assets/, .tankignore
```

### skills.json Permissions Pattern

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

**Rule**: Default to minimal permissions. Only add when actually needed.

| When Needed | Add |
|-------------|-----|
| API calls | `network: ["api.example.com"]` |
| File modification | `write: ["specific/path/**"]` |
| Running commands | `subprocess: true` |

### SKILL.md Structure Patterns

#### Best Practices Skills (react, typescript, python)

```markdown
---
name: [language]-best-practices
description: Best practices for [language] development.
  Triggers: "[language]", "[framework]", "best practices"
---

# [Language] Best Practices

## Core Principles
- Principle 1
- Principle 2

## [Topic 1]
- Bullet 1
- Bullet 2

## [Topic 2]
- Bullet 1
- Bullet 2
```

**Characteristics**: Hierarchical bullets, no code examples, <100 lines.

#### Methodology Skills (systematic-debugging, planning)

```markdown
---
name: [methodology]
description: Systematic approach to [task].
  Triggers: "debug", "plan", "investigate"
---

# [Methodology Name]

## Philosophy
[Core approach]

## When to Use
[Trigger conditions]

## The Process
### Phase 1: [Name]
1. Step
2. Step

### Phase 2: [Name]
1. Step

## Common Mistakes
- Mistake 1 → Fix
- Mistake 2 → Fix
```

**Characteristics**: Phases, explicit steps, mistake/fix pairs.

#### Operational Skills (playwright, security-review)

```markdown
---
name: [tool]-operations
description: Operate [tool] for [purpose].
  Triggers: "[tool]", "test", "audit"
---

# [Tool] Operations

## Trigger Phrases
- "phrase 1"
- "phrase 2"

## Critical Workflow
1. Step 1
2. Step 2

## Pattern: [Pattern 1]
[Details]

## Pattern: [Pattern 2]
[Details]

## Failure Map
| Error | Cause | Fix |
|-------|-------|-----|

## Output Contract
[What the skill produces]
```

**Characteristics**: Triggers explicit, failure map, output contract.

## Agent Skills Specification

### Supported Agents (2025)

| Agent | Support Level |
|-------|---------------|
| Claude Code | Full |
| Cursor | Full |
| Windsurf | Full |
| Cline | Full |
| Goose | Full |
| OpenCode | Full |
| Gemini CLI | Full |
| VS Code Copilot | Full |
| Databricks | Full |
| Amp | Full |

### Format Requirements

| Field | Required | Constraints |
|-------|----------|-------------|
| `name` | Yes | 1-64 chars, lowercase, digits, hyphens only |
| `description` | Yes | 1-1024 chars, includes triggers |
| `license` | No | Name or file reference |
| `compatibility` | No | 1-500 chars, environment requirements |
| `metadata` | No | Arbitrary key-value |
| `allowed-tools` | No | Space-delimited tool list (experimental) |

### Progressive Disclosure Levels

| Level | What | Size |
|-------|------|------|
| 1 | `name` + `description` | ~100 words |
| 2 | SKILL.md body | <500 lines (200 tank convention) |
| 3 | references/, scripts/, assets/ | Unlimited |

### File Reference Pattern

Use relative paths from skill root:

```markdown
See [reference guide](references/REFERENCE.md).

Run script:
scripts/extract.py
```

Keep references one level deep. Avoid nested chains.

## Quality Signals

### High-Performing Skills

- **Description specificity**: 10-15 trigger phrases + scenarios
- **Reference depth**: 5-9 files, 250-450 lines each
- **Cross-source synthesis**: 2+ book sources per reference
- **Actionable content**: Decision trees, tables, procedures
- **Progressive disclosure**: Lean SKILL.md, deep references
- **Composability**: Clear outputs, explicit boundaries

### Low-Performing Skills

- Generic description without triggers
- Single-source reference files
- Verbose SKILL.md (>200 lines)
- Missing file index
- No concrete examples
- Overlapping reference content
