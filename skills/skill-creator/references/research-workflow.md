# Research and Content Workflow

Sources: Production skill creation experience, Anna's Archive integration

## Phase 1: Scope and Research

### Step 1 — Define Scope

Establish boundaries before researching:

| Question | Purpose |
|----------|---------|
| What domain? | Scope research |
| What tasks? | Define reference topics |
| Trigger phrases? | Write description field |
| Style reference? | Match conventions |

Do not proceed until scope is clear.

### Step 2 — Study the Ecosystem (MANDATORY)

Study existing skills before writing. Prevents reinventing patterns.

**Browse skills.sh**:

1. Go to https://skills.sh, search leaderboard
2. For relevant skills, read SKILL.md on GitHub
3. Note: structure, triggers, brevity/depth balance
4. Save to `/tmp/{skill-name}-research/00-ecosystem.md`

**Study top publishers**:

| Repo | Study For |
|------|-----------|
| `anthropics/skills` | Official conventions, progressive disclosure |
| `vercel-labs/agent-skills` | Impact-prioritized rules, code examples |
| `obra/superpowers` | Composable delegation, minimal surface |
| `coreyhaines31/marketingskills` | Domain-specific marketing |

**Study local repo**: Read 2-3 existing skills in same domain.

Do NOT skip this step.

### Step 3 — Collect Concrete Examples

Understand HOW the skill will be used:

```
Example queries for "image-editor" skill:
- "Remove red-eye from this photo"
- "Resize to 1200x630 for social"
- "Convert PNG to WebP"
- "Add watermark to folder"
```

For each, identify:
1. What knowledge/procedure is needed?
2. Is knowledge reusable across examples?
3. Would script/reference/asset help?

Skills from examples outperform skills from abstract knowledge.

### Step 4 — Research Books

Find 6-10 authoritative books:

| Criterion | Requirement |
|-----------|-------------|
| Focus | Actionable frameworks, not theory |
| Date | 2018+ preferred |
| Breadth | Different subtopics across list |
| Reputation | Practitioner reviews |

**Process**:

1. Search "best books on [domain] for practitioners"
2. Cross-reference Amazon/Goodreads/expert blogs
3. Check table of contents for practical content
4. Ensure breadth

Get user approval before downloading.

### Step 5 — Search Anna's Archive

Use annas-archive-ebooks skill:

```bash
python3 @annas.py search "Book Title Author" --format pdf --limit 5
```

Verify correct edition:
- Title matches exactly
- Author matches
- Publication year matches
- Page count reasonable

Prefer PDF, fall back to EPUB.

### Step 6 — Download Books

**CRITICAL: One at a time with 15-20s gaps.**

LibGen CDN aggressively throttles concurrent downloads. Parallel = IP ban.

```bash
# Correct: sequential
python3 @annas.py download <md5_1> --output /tmp/skill-books/
# wait 15-20s
python3 @annas.py download <md5_2> --output /tmp/skill-books/
```

Some downloads fail due to throttling. Normal — proceed with what you have.
4-6 books sufficient for quality skill.

**Browser fallback**: If free download fails, use Playwriter MCP to click
via real Chrome. LibGen blocks Python/curl TLS fingerprints.

### Step 7 — Extract Frameworks (MANDATORY)

**This is the entire point. Do NOT skip.**

After downloading, read each book and extract actionable frameworks
before Phase 2. Books are PRIMARY — web supplements books.

**For each book**:

1. Use `look_at` to read table of contents
2. For relevant chapters, extract:
   - Frameworks, models, decision trees
   - Step-by-step procedures
   - Real-world examples
   - Metrics, benchmarks
   - Domain terminology
3. Save immediately to `/tmp/{skill-name}-research/book-{short-name}.md`

**Extraction format**:

```markdown
# {Book Title} by {Author}

## Key Frameworks
- Framework 1: brief description
- Framework 2: brief description

## Actionable Procedures
### Procedure Name
1. Step
2. Step

## Notable Examples
- Example with details

## Quantified Claims
- Metric with context

## Quotes (attributed)
- "Short quote" — Author, p.XX
```

**Quality gate**: Do NOT proceed to Phase 2 until 4+ books extracted.
If fewer downloaded, supplement with deep web research.

**Cross-reference**: Identify where authors agree (strong signal) and
disagree (note both perspectives).

## Scratch File Protocol (Critical)

Skill creation generates enormous context. Background agents, book extractions,
codebase exploration add thousands of lines. Without discipline, compaction
destroys research.

**Rule: Save every research result to disk immediately. Never hold research
only in conversation context.**

### Setup

```bash
mkdir -p /tmp/{skill-name}-research
```

### When to Save

| Event | Filename | Contents |
|-------|----------|----------|
| Background agent completes | `01-{topic}.md` | Full output, findings |
| Book extracted | `02-{book}.md` | Frameworks, quotes |
| Codebase explored | `03-{area}.md` | Paths, patterns |
| Web research done | `04-{topic}.md` | URLs, findings |
| User provides context | `05-user-{topic}.md` | Requirements |

### Format

```markdown
# {Topic}

## Source
{Agent, book, URL, or user}

## Key Findings
- Finding 1
- Finding 2

## Raw Data
{Full output, code, schemas}
```

Keep raw data verbose. Files read from disk later, not held in context.

### Recovery After Compaction

1. List files: `ls /tmp/{skill-name}-research/`
2. Read each to rebuild context
3. Resume from checkpoint

### Writing from Scratch Files

When writing reference files in Phase 3:

```
Read /tmp/{skill-name}-research/01-api-client.md
Read /tmp/{skill-name}-research/02-deployment.md
... then synthesize into references/api-reference.md
```

Decouples research (high context) from writing (focused synthesis).

## Phase 2: Plan Structure

### Step 8 — Plan Reference Files

Based on extracted frameworks, plan 5-9 files:

Each file should:
- Cover distinct subtopic (no overlap)
- Draw from 2+ source books
- Target 250-450 lines

Present planning table for approval:

| File | Covers | Primary Sources |
|------|--------|-----------------|
| references/topic-a.md | Subtopic A details | Book 1, Book 3 |
| references/topic-b.md | Subtopic B details | Book 2, Book 4 |

### Resource Type Analysis

For each example from Step 3:

| Example Task | Resource Type | Rationale |
|-------------|---------------|-----------|
| Repetitive code | `scripts/` | Same code rewritten |
| Domain knowledge | `references/` | Agent needs context |
| Template/boilerplate | `assets/` | Used in output |
| Decision guidance | SKILL.md | Frequency dependent |

Most skills only need `references/`. Add `scripts/` for deterministic
operations, `assets/` for templates.

## Phase 3: Write Content

### Step 9 — Write Reference Files

Fire one background agent per file using `delegate_task`:

1. **Book scratch files (PRIMARY)** — extracted frameworks from Step 7
2. **File plan** — subtopic, target length
3. **Style reference** — existing reference file for conventions
4. **Ecosystem research** — patterns from skills.sh
5. **Web research** — supplement books (secondary)

**Delegation template**:

```
TASK: Write references/{filename}.md for {skill-name} skill.

EXPECTED OUTCOME: 250-450 line file covering {subtopic}, synthesizing
book frameworks as primary knowledge source.

MUST DO:
- Read book scratch files FIRST:
  /tmp/{skill-name}-research/book-*.md
- Read ecosystem research:
  /tmp/{skill-name}-research/00-ecosystem.md
- Read {style_reference_path} for conventions
- If scratch files lack depth, use look_at on source books
- Start with `# Title` then `Sources: Author (Book), Author (Book)`
- Sources MUST cite 2+ book authors
- Use ## for major, ### for subsections
- Include markdown tables
- Synthesize ACROSS sources
- Professional tone, no emoji
- 250-450 lines
- Imperative form

MUST NOT DO:
- Write primarily from web research — books are foundation
- Copy text directly from books
- Include YAML frontmatter
- Exceed 450 lines or under 250
- Write generic advice
- Overlap with: {list of other files}
- Skip book scratch files

CONTEXT:
- Skill: {skill-name}
- Covers: {detailed subtopic}
- Scratch files: /tmp/{skill-name}-research/
```

Use `category="writing"` and `load_skills=["annas-archive-ebooks"]`.

**Fallback**: If delegated writes fail, write sequentially yourself.

### Step 10 — Verify Files

| Check | Requirement |
|-------|-------------|
| Format | `# Title` then `Sources:` line |
| Sources | 2+ book authors cited |
| Length | 250-450 lines |
| Foundation | Content draws from books |
| Quality | Actionable patterns, not summaries |
| No overlap | Distinct subtopics |
| No frontmatter | Only SKILL.md has YAML |
| Tone | Professional, no emoji, imperative |

Fix failures immediately.

## Phase 4: Deploy

### Step 11 — Write SKILL.md

Follow `references/writing-conventions.md`. Under 200 lines.

### Step 12 — Git and Install

```bash
git add skill-name/
git commit -m "Add {skill-name} skill: {description}"
git push
bash install.sh
bash install.sh status
```

## Phase 5: Iterate

After testing:

| Symptom | Fix |
|---------|-----|
| Skill doesn't activate | Improve description with triggers |
| Generic advice | More specific reference content |
| Wrong reference loaded | Improve file descriptions |
| Format inconsistent | Add template/examples patterns |
| Same code rewritten | Extract to `scripts/` |
| Reference feels thin | Add more sources |
| Disorganized | Restructure using patterns |

## Troubleshooting Downloads

| Error | Cause | Fix |
|-------|-------|-----|
| HTTP 429 | CDN rate limit | Wait 5min, retry one file |
| HTTP 503 | Server overload | Different mirror or wait 30min |
| Timeout | Server unresponsive | Try later or browser |
| File corrupted | Incomplete download | Delete, re-download |
| TLS failure | Python/curl blocked | Use Playwriter browser |
