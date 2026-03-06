# Quality Assurance Agents

Sources: Production evaluation patterns, inspired by anthropics/skills agent architecture

Covers: grader agent prompt, blind comparator agent prompt, spawning patterns,
output schemas.

Does NOT cover: the evaluation workflow process itself (see
`references/evaluation-workflow.md`).

## Overview

Two reusable agent prompts for evaluating skill output quality:

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| Grader | Evaluate assertions against outputs | After every test run |
| Blind Comparator | Judge two outputs without bias | When comparing skill versions |

Spawn these via delegation with the relevant prompt section as instructions.

## Grader Agent

### Role

The Grader reviews execution transcripts and output files, then determines
whether each assertion passes or fails. Provides evidence for every judgment.

Two jobs: grade the outputs AND critique the assertions themselves. A passing
grade on a weak assertion creates false confidence.

### Delegation Template

```
TASK: Grade the outputs for eval "{eval_name}" against its assertions.

EXPECTED OUTCOME: grading.json with pass/fail for each assertion, evidence,
summary stats, and optionally eval improvement suggestions.

MUST DO:
- Read the transcript at {transcript_path}
- Examine all files in {outputs_dir}
- For each assertion, search for evidence in BOTH transcript and outputs
- PASS only when clear evidence exists AND reflects genuine task completion
- FAIL when evidence is missing, contradicts, or is merely surface-level
- Extract and verify implicit claims from the output
- Check {outputs_dir}/user_notes.md if it exists
- Critique assertions that are too easy or non-discriminating
- Write results to {outputs_dir}/../grading.json

MUST NOT DO:
- Give partial credit (pass or fail, no middle ground)
- Pass assertions based on surface compliance (right filename but wrong content)
- Skip reading the actual output files
- Assume transcript claims are true without verification
- Nitpick every assertion — only flag genuinely problematic ones

CONTEXT:
- Assertions to evaluate: {assertions_list}
- Transcript path: {transcript_path}
- Outputs directory: {outputs_dir}
```

### Grading Criteria

**PASS when:**
- Transcript or outputs clearly demonstrate the assertion is true
- Specific evidence can be cited
- Evidence reflects genuine substance, not surface compliance

**FAIL when:**
- No evidence found
- Evidence contradicts the assertion
- Cannot be verified from available information
- Evidence is superficial (technically satisfied but outcome is wrong)
- Output meets assertion by coincidence, not by doing the work

**When uncertain:** Burden of proof is on the assertion to pass.

### Claim Extraction

Beyond predefined assertions, extract implicit claims from outputs:

| Claim Type | Example | How to Verify |
|-----------|---------|---------------|
| Factual | "The form has 12 fields" | Count in output file |
| Process | "Used pypdf to fill the form" | Check transcript tool calls |
| Quality | "All fields filled correctly" | Inspect output vs input |

Flag unverifiable claims. These may reveal issues assertions miss.

### Eval Self-Critique

After grading, assess whether the assertions themselves are good:

**Flag when:**
- An assertion passed but would also pass for a clearly wrong output
- An important outcome has no assertion covering it
- An assertion can't actually be verified from available outputs

**Don't flag when:**
- Assertion is working as intended
- Suggestion would be nitpicking without real value

### Grader Output Schema

```json
{
  "expectations": [
    {
      "text": "The output includes a summary table",
      "passed": true,
      "evidence": "Found 3-column table in output.md, lines 15-28"
    },
    {
      "text": "Date fields use ISO 8601 format",
      "passed": false,
      "evidence": "Dates use MM/DD/YYYY format (line 7: '03/15/2025')"
    }
  ],
  "summary": {
    "passed": 4,
    "failed": 1,
    "total": 5,
    "pass_rate": 0.80
  },
  "claims": [
    {
      "claim": "The report covers all 3 regions",
      "type": "factual",
      "verified": true,
      "evidence": "Sections found for North, South, West regions"
    }
  ],
  "eval_feedback": {
    "suggestions": [
      {
        "assertion": "Output includes summary table",
        "reason": "A table with wrong data would also pass. Consider checking column headers match expected schema."
      }
    ],
    "overall": "Assertions check presence but not correctness for 2 of 5 checks."
  }
}
```

## Blind Comparator Agent

### Role

Compare two outputs WITHOUT knowing which skill produced them. Prevents
bias toward a particular approach. Judges purely on output quality and
task completion.

### When to Use

- Comparing a new skill version against the previous version
- Deciding between two alternative skill approaches
- Validating that improvements actually improved quality

Not needed for every iteration. The grader + human review loop is usually
sufficient. Use blind comparison when you want rigorous evidence that
version B is better than version A.

### Delegation Template

```
TASK: Compare two outputs for the task "{eval_prompt}" and determine
which is better. You do NOT know which approach produced which output.

EXPECTED OUTCOME: comparison.json with winner, rubric scores, reasoning,
and optionally assertion results.

MUST DO:
- Read output A at {output_a_path}
- Read output B at {output_b_path}
- Generate a task-specific rubric (content + structure dimensions)
- Score each output 1-5 on each criterion
- Determine a winner based on overall quality
- If assertions provided, check them for both outputs (secondary signal)
- Write results to {output_path}

MUST NOT DO:
- Try to guess which skill produced which output
- Favor outputs based on style preferences over correctness
- Declare a tie unless outputs are genuinely equivalent
- Use assertion scores as primary decision factor

CONTEXT:
- Task prompt: {eval_prompt}
- Output A: {output_a_path}
- Output B: {output_b_path}
- Assertions (optional): {assertions_list}
```

### Rubric Generation

The comparator generates a task-specific rubric with two dimensions:

**Content Rubric** (what the output contains):

| Criterion | 1 (Poor) | 3 (Acceptable) | 5 (Excellent) |
|-----------|----------|----------------|---------------|
| Correctness | Major errors | Minor errors | Fully correct |
| Completeness | Missing key elements | Mostly complete | All present |
| Accuracy | Significant issues | Minor inaccuracies | Accurate |

**Structure Rubric** (how the output is organized):

| Criterion | 1 (Poor) | 3 (Acceptable) | 5 (Excellent) |
|-----------|----------|----------------|---------------|
| Organization | Disorganized | Reasonable | Clear, logical |
| Formatting | Inconsistent | Mostly consistent | Professional |
| Usability | Difficult to use | Usable with effort | Easy to use |

Adapt criteria to the task. PDF form → "Field alignment", "Data placement".
Document → "Section structure", "Heading hierarchy". Data → "Schema correctness".

### Decision Priority

1. **Primary**: Overall rubric score (content + structure)
2. **Secondary**: Assertion pass rates (if provided)
3. **Tiebreaker**: If truly equal, declare TIE (should be rare)

### Comparator Output Schema

```json
{
  "winner": "A",
  "reasoning": "Output A provides complete solution with proper formatting. Output B is missing the date field and has inconsistencies.",
  "rubric": {
    "A": {
      "content": {"correctness": 5, "completeness": 5, "accuracy": 4},
      "structure": {"organization": 4, "formatting": 5, "usability": 4},
      "content_score": 4.7,
      "structure_score": 4.3,
      "overall_score": 9.0
    },
    "B": {
      "content": {"correctness": 3, "completeness": 2, "accuracy": 3},
      "structure": {"organization": 3, "formatting": 2, "usability": 3},
      "content_score": 2.7,
      "structure_score": 2.7,
      "overall_score": 5.4
    }
  },
  "output_quality": {
    "A": {
      "score": 9,
      "strengths": ["Complete solution", "All fields present"],
      "weaknesses": ["Minor style inconsistency in header"]
    },
    "B": {
      "score": 5,
      "strengths": ["Readable output", "Correct basic structure"],
      "weaknesses": ["Missing date field", "Formatting issues"]
    }
  },
  "expectation_results": {
    "A": {"passed": 4, "total": 5, "pass_rate": 0.80},
    "B": {"passed": 3, "total": 5, "pass_rate": 0.60}
  }
}
```

## Post-Comparison Analysis

After blind comparison identifies a winner, optionally analyze WHY it won.
Read both skills and transcripts to extract actionable improvements.

### Analysis Delegation Template

```
TASK: Analyze why the winning output was better and generate improvement
suggestions for the losing skill.

MUST DO:
- Read the comparison result at {comparison_path}
- Read both skills (winner at {winner_skill_path}, loser at {loser_skill_path})
- Read both transcripts if available
- Identify instruction-following differences
- Generate prioritized improvement suggestions
- Focus on changes that would have changed the outcome

MUST NOT DO:
- Suggest cosmetic changes that wouldn't affect quality
- Speculate without evidence from transcripts
- Recommend changes that would only help this specific test case
```

### Analysis Output Schema

```json
{
  "comparison_summary": {
    "winner": "A",
    "winner_skill": "path/to/winner",
    "loser_skill": "path/to/loser"
  },
  "winner_strengths": [
    "Clear step-by-step instructions for multi-page documents",
    "Included validation script that caught formatting errors"
  ],
  "loser_weaknesses": [
    "Vague instruction 'process appropriately' led to inconsistent behavior",
    "No validation step, errors went uncaught"
  ],
  "improvement_suggestions": [
    {
      "priority": "high",
      "category": "instructions",
      "suggestion": "Replace 'process appropriately' with explicit steps",
      "expected_impact": "Eliminates ambiguity causing inconsistent behavior"
    }
  ]
}
```

### Suggestion Categories

| Category | What to Change |
|----------|---------------|
| `instructions` | Prose instructions in SKILL.md or references |
| `tools` | Scripts or utilities to add/modify |
| `examples` | Input/output examples to include |
| `error_handling` | Guidance for handling failures |
| `structure` | Reorganization of skill content |
| `references` | Additional reference docs to add |

### Priority Levels

- **high**: Would likely change the outcome of comparison
- **medium**: Improves quality but may not change win/loss
- **low**: Nice to have, marginal improvement
