---
name: "@tank/github-docs"
description: |
  Write excellent GitHub documentation for libraries and developer tools.
  Covers README anatomy (hero, features, quick start, API reference),
  all GitHub Markdown features (alerts, mermaid, badges, collapsible,
  dark/light mode, math, footnotes), code example best practices, visual
  design for scannable docs, and supporting files (CHANGELOG, CONTRIBUTING,
  migration guides). Includes copy-paste templates for libraries, CLIs,
  APIs, and applications. Optimized for Gen-Z developers: front-loaded
  value, visual-first, scannable, instant gratification.

  Synthesized from: Google Developer Documentation Style Guide, Diataxis
  framework, top library READMEs (React, tRPC, Got, Bun, Drizzle, Biome),
  GitHub GFM spec, shields.io, awesome-readme patterns.

  Trigger phrases: "README", "documentation", "docs", "write docs",
  "library docs", "package docs", "GitHub docs", "improve docs",
  "project documentation", "getting started guide", "API docs",
  "contributing guide", "changelog", "badges", "mermaid diagram",
  "quick start", "document this library", "write a README",
  "make docs better", "doc structure"
---

# GitHub Docs

## Core Philosophy

1. **Respect the reader's time** -- Developers decide in 8 seconds whether
   docs are worth reading. Front-load value, never bury the lede.
2. **Show, don't tell** -- One code example beats ten paragraphs. Diagrams
   beat descriptions. GIFs beat step-by-step text.
3. **Copy-paste or bust** -- Every code snippet must work when pasted.
   Incomplete examples destroy trust instantly.
4. **Progressive disclosure** -- README is the storefront. Details live in
   docs/. Never overwhelm with everything at once.
5. **Use the platform** -- GitHub renders alerts, mermaid, math, badges,
   collapsible sections, dark/light images. Use them all.

## Quick-Start: What Are You Writing?

| Task | Start Here |
|------|-----------|
| New library README from scratch | Pick template from `@references/readme-templates.md`, customize |
| Improve existing README | Audit against `@references/readme-anatomy.md` section checklist |
| Add visual polish (badges, diagrams) | See `@references/visual-elements.md` |
| Write API reference section | See `@references/code-examples-and-api.md` |
| Add CHANGELOG, CONTRIBUTING, etc. | See `@references/supporting-docs.md` |
| Need specific GitHub Markdown syntax | See `@references/github-markdown-features.md` |

## The Documentation Workflow

### Phase 1: Analyze the Project

1. Read the codebase -- understand what the library does, its API surface,
   and target audience
2. Identify project type -- library, CLI, API service, or application
3. Check existing docs -- what exists, what is missing, what is outdated
4. Determine scope -- README-only or README + docs/ + supporting files

### Phase 2: Choose Template and Structure

1. Select the matching template from `@references/readme-templates.md`
2. Customize sections based on project needs (see anatomy reference)
3. Plan visual elements -- which badges, whether mermaid diagrams help
4. Decide progressive disclosure -- what stays in README vs docs/

### Phase 3: Write Content

1. **Hero section first** -- Logo, tagline, badges, quick links
2. **Quick Start next** -- Install + 5-line example + expected output
3. **Features list** -- Emoji + bold keyword + one-sentence benefit
4. **Usage examples** -- Progressive: basic, common, advanced
5. **API reference** -- Function signatures, parameter tables, examples
6. **Supporting sections** -- Contributing, license, comparison table

Follow writing conventions from `@references/writing-for-developers.md`.

### Phase 4: Polish and Review

1. Add visual elements -- badges, diagrams, collapsible sections
2. Check all code examples actually run
3. Verify GitHub Markdown renders correctly
4. Ensure every section is scannable (no walls of text)
5. Test the "8-second rule" -- does the hero section sell the project?

## Decision Trees

### README Length

| Project Size | README Target | Additional Docs |
|-------------|---------------|-----------------|
| Small utility (1-5 files) | 100-200 lines | None needed |
| Medium library (5-20 files) | 200-400 lines | Optional docs/ |
| Large framework (20+ files) | 300-500 lines | Required docs/ site |
| Monorepo | Root 200 lines + per-package READMEs | Required docs/ site |

### Which Sections to Include

| Section | Always | If Applicable | Skip If |
|---------|--------|---------------|---------|
| Hero (logo, tagline, badges) | Yes | -- | -- |
| What is X? | Yes | -- | -- |
| Features | Yes | -- | -- |
| Quick Start | Yes | -- | -- |
| Installation | Yes | -- | -- |
| Usage examples | Yes | -- | -- |
| API Reference | -- | Public API exists | Internal tool |
| Configuration | -- | Configurable | No config |
| Comparison table | -- | Alternatives exist | Unique tool |
| Contributing | -- | Accept contributions | Solo project |
| Changelog link | -- | Published package | -- |
| License | Yes | -- | -- |

### Visual Elements Selection

| Element | Use When | Skip When |
|---------|----------|-----------|
| Badges (4-7 max) | Published package | Internal/private project |
| Mermaid flowchart | Architecture has 3+ components | Simple linear flow |
| Mermaid sequence | Multi-service interactions | Single service |
| Screenshot/GIF | UI-visible tool | Pure library/SDK |
| Comparison table | 2+ competing alternatives | No alternatives |
| Dark/light images | Logo uses colors affected by theme | Text-only/simple shapes |
| Collapsible sections | Optional/advanced detail | Core content |

## Anti-Patterns

| Do Not | Do Instead |
|--------|-----------|
| Wall of text in README | Break into bullets, tables, collapsible sections |
| Installation before "What is this?" | Context first, install second |
| Incomplete code examples | Every snippet must copy-paste and run |
| 15+ badges | 4-7 strategically chosen badges |
| "Just run X" or "Simply do Y" | Direct imperative: "Run X" |
| Bury Quick Start below the fold | Quick Start within first 3 sections |
| Link to docs without any examples | At least one inline example, then link |
| Assume reader knows your jargon | Define terms on first use |
| Outdated screenshots | Automate or date-stamp visuals |
| No error handling in examples | Show at least one error case |

## Reference Files

| File | Contents |
|------|----------|
| `@references/github-markdown-features.md` | Complete GFM feature reference: alerts, mermaid, math, badges, collapsible, footnotes, kbd, dark/light, color swatches, diff, GeoJSON |
| `@references/readme-anatomy.md` | README structure, section ordering, hero design, F-pattern scanning, progressive disclosure, README vs docs site |
| `@references/writing-for-developers.md` | Writing tone, Gen-Z friendly style, scannable formatting, word choice, anti-patterns, Google style guide principles |
| `@references/code-examples-and-api.md` | Code example best practices, API reference patterns, options objects, HTTP API docs, TypeScript/JSDoc |
| `@references/visual-elements.md` | Badges, shields.io, mermaid diagrams, dark/light mode images, screenshots, comparison tables, visual hierarchy |
| `@references/supporting-docs.md` | CHANGELOG, CONTRIBUTING, LICENSE, CODE_OF_CONDUCT, SECURITY, docs/ structure, issue templates, migration guides |
| `@references/readme-templates.md` | Copy-paste templates: library/package, CLI tool, API service/SDK, framework/application |
