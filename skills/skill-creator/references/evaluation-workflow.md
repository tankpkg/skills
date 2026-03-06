# Evaluation and Iteration Workflow

Sources: Production skill testing patterns, inspired by anthropics/skills evaluation approach

Covers: test case creation, running evaluations, grading, iteration loop,
description optimization, evaluation schemas.

Does NOT cover: agent prompt definitions for grading/comparison (see
`references/quality-agents.md`).

## Why Evaluate

A skill that isn't tested is a skill that doesn't work. The most common
failure modes — wrong triggering, generic output, missed edge cases — are
only visible through systematic evaluation. Building a skill without
evaluating it is like shipping code without running tests.

The evaluation loop:

```
Draft skill → Create test cases → Run with/without skill
    ↑                                       ↓
    └── Improve skill ← Grade + Review ← Collect outputs
```

## Phase 3.5: Evaluate & Iterate

This phase sits between Phase 3 (Write Content) and Phase 4 (Deploy).
Do not skip it.

### Step 1 — Create Test Cases

Write 3-5 realistic test prompts — the kind of thing a user would
actually say. Not sanitized lab prompts. Include:

- Casual phrasing, typos, abbreviations
- Varied lengths (short commands, detailed requests)
- Edge cases the skill should handle
- Near-misses the skill should NOT handle

Save to `evals/evals.json`:

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's realistic task prompt",
      "expected_output": "Description of what success looks like",
      "files": [],
      "assertions": [
        "The output includes a summary table",
        "No placeholder text remains in the document"
      ]
    }
  ]
}
```

**Assertions** are objectively verifiable statements about the output.
Good assertions check concrete outcomes. Bad assertions are subjective.

| Good Assertion | Bad Assertion |
|---------------|---------------|
| "Output is a valid PDF file" | "Output looks professional" |
| "Contains all 5 required sections" | "Writing quality is high" |
| "Uses the skill's validation script" | "Follows best practices" |
| "Date field matches input data" | "Formatting is nice" |

For subjective skills (writing style, design), skip assertions and rely
on human review. Do not force quantitative evaluation onto qualitative work.

### Step 2 — Run Test Cases

For each test case, spawn two runs:

1. **With-skill run**: Agent uses the skill to complete the task
2. **Baseline run**: Same prompt, no skill (or previous skill version)

Launch both in parallel via delegation. Save outputs to workspace:

```
{skill-name}-workspace/
└── iteration-1/
    └── eval-descriptive-name/
        ├── eval_metadata.json
        ├── with_skill/
        │   └── outputs/
        └── without_skill/
            └── outputs/
```

**Delegation template for test run:**

```
TASK: Execute this task using the skill at {skill-path}.

EXPECTED OUTCOME: Complete the task and save all outputs to
{workspace}/iteration-N/eval-{id}/with_skill/outputs/

MUST DO:
- Read the skill's SKILL.md first
- Follow skill instructions to complete the task
- Save all output files to the outputs directory
- Save metrics.json with tool call counts

MUST NOT DO:
- Skip reading the skill
- Invent approaches not in the skill

CONTEXT:
- Task prompt: {eval prompt}
- Input files: {eval files or "none"}
```

### Step 3 — Draft Assertions While Runs Execute

Do not wait idle for runs to finish. Use the time to:

1. Draft quantitative assertions for each test case
2. Write `eval_metadata.json` for each eval directory
3. Plan what the human reviewer should look for

```json
{
  "eval_id": 1,
  "eval_name": "descriptive-name",
  "prompt": "The user's task prompt",
  "assertions": [
    "The output includes a summary table with 3 columns",
    "All date fields use ISO 8601 format"
  ]
}
```

### Step 4 — Grade Results

Once runs complete, evaluate each assertion against the outputs.

**For programmatically verifiable assertions**: Write and run a script.
Scripts are faster, more reliable, and reusable across iterations.

**For judgment-required assertions**: Spawn a grader agent with the
prompt from `references/quality-agents.md`. The grader reads outputs
and transcript, then evaluates each assertion with evidence.

Save grading results to `grading.json` in each run directory:

```json
{
  "expectations": [
    {
      "text": "Output includes summary table",
      "passed": true,
      "evidence": "Found 3-column table in output.md lines 15-28"
    }
  ],
  "summary": {
    "passed": 4,
    "failed": 1,
    "total": 5,
    "pass_rate": 0.80
  }
}
```

**Critical**: Use field names `text`, `passed`, `evidence` exactly.

### Step 5 — Human Review

Present results to the user. For each test case, show:

- The prompt
- The outputs (with and without skill)
- Assertion pass/fail results
- What to focus feedback on

Collect feedback. Empty feedback means "looks good." Focus improvements
on test cases where the user had specific complaints.

### Step 6 — Iterate

After review:

1. Identify what to improve (from feedback + grading failures)
2. Apply improvements to the skill
3. Rerun ALL test cases into `iteration-N+1/`
4. Grade again, review again
5. Repeat until satisfied

**Stop conditions:**
- User says they're happy
- All feedback is empty
- No meaningful progress after 2 iterations

## Improvement Philosophy

When improving a skill based on evaluation feedback:

### 1. Generalize, Don't Overfit

The skill will be used across many prompts. A few test cases help
iterate fast, but fiddly changes that only fix those specific examples
are worthless. Think about the CATEGORY of failure, not the specific
instance.

| Bad Fix | Good Fix |
|---------|----------|
| "When user says 'quarterly report', always add Q4 header" | "Add guidance for detecting report period from context" |
| Hardcode format for one test file | Explain format detection strategy |
| Add 15 MUST/NEVER rules | Explain the reasoning behind 3 key principles |

### 2. Keep the Prompt Lean

Read the transcripts, not just final outputs. If the skill makes the
agent waste time on unproductive steps, remove the instructions causing
that behavior. Every line must justify its token cost.

### 3. Explain the Why

Today's LLMs are smart. They have good theory of mind. Explaining WHY
something matters is more effective than rigid MUST/NEVER rules. If you
find yourself writing ALWAYS in all caps, reframe it as reasoning.

| Rigid Rule | Better Approach |
|-----------|-----------------|
| "ALWAYS use ISO 8601 dates" | "Use ISO 8601 dates because downstream parsers expect them" |
| "NEVER use inline styles" | "Prefer CSS classes — inline styles break when themes change" |

### 4. Bundle Repeated Work

Read transcripts from test runs. If all runs independently wrote
similar helper scripts or took the same multi-step approach, that's a
signal the skill should bundle that script in `scripts/`. Write it once
so every future invocation avoids reinventing it.

## Description Optimization

The `description` field is the PRIMARY triggering mechanism. Optimizing
it directly solves "Skill doesn't activate" — the #1 reported problem.

### Creating Trigger Eval Queries

Write 15-20 eval queries — a mix of should-trigger and should-not-trigger:

```json
[
  {"query": "realistic user prompt that needs this skill", "should_trigger": true},
  {"query": "realistic prompt that sounds related but shouldn't trigger", "should_trigger": false}
]
```

**Should-trigger queries (8-10)**:
- Different phrasings of the same intent (formal, casual)
- Cases where user doesn't name the skill but clearly needs it
- Uncommon use cases the skill covers
- Competitive cases where this skill should win over others

**Should-not-trigger queries (8-10)**:
- Near-misses that share keywords but need something different
- Adjacent domains with ambiguous phrasing
- Cases where another tool is more appropriate

**Bad**: Obviously irrelevant queries ("write fibonacci function" for a PDF skill)
**Good**: Genuinely tricky near-misses that test discrimination

### Testing Triggers

Test each query manually or via automation:

1. Present the query to the agent with the skill available
2. Check: did the skill activate?
3. Compare against `should_trigger` expectation

Track results:

| Query | Should Trigger | Did Trigger | Pass? |
|-------|---------------|-------------|-------|
| "help me fill out this tax form PDF" | Yes | Yes | ✓ |
| "what's the best PDF reader app" | No | Yes | ✗ |

### Improving the Description

Based on failures, rewrite the description. Key principles:

- **Imperative phrasing**: "Use this skill for..." not "This skill does..."
- **Focus on user intent**: What they're trying to achieve, not implementation
- **Be distinctive**: Compete with other skills for attention
- **Be slightly pushy**: Claude tends to under-trigger. Include edge cases.
- **Stay under 1024 characters**: Hard limit from the specification
- **100-200 words target**: Even if accuracy suffers slightly

Example of a "pushy" description:

```
Instead of:
  "Process PDF documents."

Write:
  "Use this skill whenever the user needs to work with PDF files —
   filling forms, extracting text, merging documents, converting formats.
   Trigger for any mention of PDF, form filling, document extraction,
   or page manipulation, even if the user doesn't explicitly say 'PDF'."
```

### Iteration Strategy

If description optimization stalls after 2-3 attempts:

- Change sentence structure entirely (don't just add more keywords)
- Try different metaphors or framings
- Focus on user scenarios rather than feature lists
- Test with a fresh set of queries to avoid overfitting

## Evaluation Schemas

### evals.json

```json
{
  "skill_name": "string",
  "evals": [
    {
      "id": "integer",
      "prompt": "string — the task",
      "expected_output": "string — human description of success",
      "files": ["optional — input file paths"],
      "assertions": ["string — verifiable statements"]
    }
  ]
}
```

### eval_metadata.json

```json
{
  "eval_id": "integer",
  "eval_name": "string — descriptive name",
  "prompt": "string — the task",
  "assertions": ["string — verifiable statements"]
}
```

### grading.json

```json
{
  "expectations": [
    {
      "text": "string — the assertion",
      "passed": "boolean",
      "evidence": "string — specific quote or finding"
    }
  ],
  "summary": {
    "passed": "integer",
    "failed": "integer",
    "total": "integer",
    "pass_rate": "float 0.0-1.0"
  }
}
```

### timing.json

```json
{
  "total_duration_seconds": "float",
  "total_tokens": "integer (if available)"
}
```

## Common Evaluation Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Skipping baseline runs | Can't tell if skill helps or hurts | Always compare with/without |
| Subjective assertions | "Output looks good" can't be graded | Use verifiable, concrete checks |
| Too few test cases | One example proves nothing | 3-5 minimum, cover edge cases |
| Only testing happy path | Skill breaks on unexpected input | Include edge cases, near-misses |
| Not reading transcripts | Miss process issues (wasted steps) | Read HOW the agent worked, not just output |
| Overfitting to test cases | Skill works for 3 examples, fails elsewhere | Generalize fixes, don't hardcode |
| Assertions that always pass | "File exists" passes even if content is wrong | Check substance, not just surface |
| Ignoring timing/tokens | Skill works but costs 10x more | Track resource usage across iterations |
| Skipping human review | Quantitative metrics miss quality issues | Always get human eyes on outputs |
| One-and-done evaluation | Skill degrades as context changes | Re-evaluate after major changes |
