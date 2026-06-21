# Meta-Judge Evaluation Pattern

The meta-judge evaluation pattern is a two-phase verification system that separates criteria generation from criteria application.

## Core Loop

1. **Meta-Judge**: Dispatch a meta-judge (Opus model) to generate a YAML evaluation specification with rubrics, checklists, and scoring criteria tailored to the specific artifact type and evaluation focus
2. **Implementation**: One or more agents implement the work using CoT reasoning and self-critique
3. **Judge Verification**: Independent judge(s) evaluate output against the exact meta-judge specification — no modifications, no threshold leak
4. **Retry Loop**: If score < 4.0 with retries remaining, retry implementation with judge feedback, reusing the same meta-judge spec. Parse only structured header (VERDICT/SCORE/ISSUES/IMPROVEMENTS) from judge output.

## Critical Constraints

- **Never leak the pass threshold to the judge.** The judge must not know what score constitutes passing, to prevent score anchoring bias.
- **Reuse meta-judge spec on retries** — never re-run meta-judge. The evaluation criteria are invariant; reusing the same spec ensures consistent measurement across all attempts.
- **Parse only structured headers** (VERDICT/SCORE/ISSUES/IMPROVEMENTS) from judge output to avoid context pollution.

## YAML Specification Structure

The meta-judge produces a YAML document with:

```yaml
criteria:
  - name: <criterion name>
    weight: <0-1>
    indicators:
      - <indicator with specific, measurable states>
  - ...
scoring:
  Rubric: <0-5 scale with descriptions per score level>
  pass_threshold: <hidden from judge — do not include in spec>
checklist:
  - <verification step>
  - ...
```

## Threshold Scoring

| Score | Meaning |
|-------|---------|
| >= 4.0 | PASS |
| >= 3.0 with all low-priority issues | PASS |
| < 4.0 with retries remaining | Retry with judge feedback |
| < 4.0 after max retries | Escalate to user with failure analysis |

## Result Aggregation

- **Single judge**: Present verdict, key findings, follow-up options
- **Multi-judge (debate)**: Aggregate using ranked choice (1st=3 points, 2nd=2 points, 3rd=1 point); handle ties by comparing average criterion scores