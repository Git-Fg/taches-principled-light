# JSON Schemas

The four schemas an evaluating-skills run produces. Vendored from Anthropic's `skill-creator` (`references/schemas.md`) for interoperability — outputs from this skill are readable by Anthropic's `aggregate_benchmark.py` and `eval-viewer/generate_review.py`, and vice-versa. Keep field names exact; downstream tooling depends on them.

---

## evals.json

Declares the evals for a skill. Located at `<workspace>/evals/evals.json`.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's example prompt",
      "expected_output": "Description of expected result",
      "files": ["evals/files/sample1.pdf"],
      "expectations": [
        "The output includes X",
        "The skill used script Y"
      ]
    }
  ]
}
```

**Fields:**
- `skill_name`: Name matching the skill's frontmatter
- `evals[].id`: Unique integer identifier
- `evals[].prompt`: The task to execute (make it realistic — file paths, context, the way a real user types)
- `evals[].expected_output`: Human-readable description of success
- `evals[].files`: Optional list of input file paths (relative to skill root)
- `evals[].expectations`: List of verifiable statements. May be empty at write-time; filled during grading (stage 4).

---

## behavioral_comparison.json

Output from the behavioral reviewer (stage 4). Located at `<run-dir>/behavioral_comparison.json`. This is the evaluating-skills addition over Anthropic's `grading.json` — it captures the *delta* between with-skill and without-skill behavior, which is what "is this skill good" actually means.

```json
{
  "eval_id": 1,
  "eval_name": "descriptive-name-here",
  "dimensions": [
    {
      "name": "followed-step-ordering",
      "with_skill": 4,
      "without_skill": 2,
      "delta": 2,
      "evidence_with": "Transcript line 47: agent executed steps in the skill's documented order",
      "evidence_without": "Transcript line 31: agent skipped verification and jumped to output"
    },
    {
      "name": "used-skill-patterns",
      "with_skill": 5,
      "without_skill": 1,
      "delta": 4,
      "evidence_with": "Agent used the skill's bundled validate.py at line 52",
      "evidence_without": "Agent improvised validation inline; missed 2 edge cases"
    }
  ],
  "expectations": [
    { "text": "Output includes the name field", "passed": true,
      "evidence": "with_skill line 60 produced it; without_skill omitted it" }
  ],
  "verdict": "PASS",
  "material_difference": true,
  "summary": "The skill changed behavior materially: with-skill runs followed the documented workflow and used the bundled validator; without-skill runs improvised and missed edge cases."
}
```

**Fields:**
- `dimensions[]`: Per-rubric-dimension scores for both runs + delta + evidence. Dimensions are configurable; the default set is in `behavioral-review.md`.
- `expectations[]`: Same field names as Anthropic's `grading.json` (`text`, `passed`, `evidence`) for interop — but the `evidence` here cites both transcripts.
- `verdict`: `PASS` | `FAIL` | `AMBIGUOUS` (AMBIGUOUS triggers a re-review loop).
- `material_difference`: `true` if the skill changed behavior enough to matter. A skill that loads but doesn't change behavior scores `false` here — that is the signal the load-event model cannot detect. **Default rule:** with-skill beats baseline by ≥ 2 points on ≥ 2 dimensions, or by ≥ 1.5 on the mean — otherwise `false`. State the rule used in `summary` so the verdict is re-derivable.

---

## grading.json (Anthropic-compatible, for single-run grading)

When you grade a single run (no baseline) or want Anthropic-tooling interop, use this schema. Located at `<run-dir>/grading.json`.

```json
{
  "expectations": [
    { "text": "...", "passed": true, "evidence": "..." }
  ],
  "summary": { "passed": 2, "failed": 1, "total": 3, "pass_rate": 0.67 },
  "execution_metrics": { "tool_calls": {}, "total_tool_calls": 15, "errors_encountered": 0 },
  "timing": { "total_duration_seconds": 191.0 },
  "claims": [ { "claim": "...", "type": "factual", "verified": true, "evidence": "..." } ],
  "eval_feedback": { "suggestions": [ { "assertion": "...", "reason": "trivially satisfied" } ] }
}
```

The grader's two non-obvious duties (from Anthropic's `agents/grader.md`): mark FAIL when evidence is superficial (correct filename but empty content), and critique the assertions themselves in `eval_feedback` — "a passing grade on a weak assertion is worse than useless."

---

## benchmark.json

Output from stage 5. Located at `<workspace>/iteration-N/benchmark.json`.

```json
{
  "metadata": {
    "skill_name": "pdf",
    "skill_path": "/path/to/pdf",
    "executor_model": "claude-sonnet-4-20250514",
    "timestamp": "2026-01-15T10:30:00Z",
    "evals_run": [1, 2, 3],
    "runs_per_configuration": 3
  },
  "runs": [
    {
      "eval_id": 1, "eval_name": "Ocean",
      "configuration": "with_skill",
      "run_number": 1,
      "result": { "pass_rate": 0.85, "passed": 6, "failed": 1, "total": 7,
                  "time_seconds": 42.5, "tokens": 3800, "tool_calls": 18, "errors": 0 },
      "expectations": [ { "text": "...", "passed": true, "evidence": "..." } ]
    }
  ],
  "run_summary": {
    "with_skill": {
      "pass_rate": { "mean": 0.85, "stddev": 0.05, "min": 0.80, "max": 0.90 },
      "time_seconds": { "mean": 45.0, "stddev": 12.0, "min": 32.0, "max": 58.0 },
      "tokens": { "mean": 3800, "stddev": 400, "min": 3200, "max": 4100 }
    },
    "without_skill": {
      "pass_rate": { "mean": 0.35, "stddev": 0.08, "min": 0.28, "max": 0.45 },
      "time_seconds": { "mean": 32.0, "stddev": 8.0, "min": 24.0, "max": 42.0 },
      "tokens": { "mean": 2100, "stddev": 300, "min": 1800, "max": 2500 }
    },
    "delta": { "pass_rate": "+0.50", "time_seconds": "+13.0", "tokens": "+1700" }
  },
  "notes": [
    "Assertion 'Output is a file' passes 100% in both — non-discriminating, drop or strengthen",
    "Eval 3 high variance (50% ± 40%) — possibly flaky",
    "Skill adds 13s avg but improves pass rate by 50%"
  ]
}
```

**Critical:** `configuration` must be exactly `"with_skill"` or `"without_skill"` (the viewer groups/colors by this string). `result` must be nested under each run, not at top level. `run_summary` needs `mean` and `stddev` per metric.

---

## history.json

Tracks version progression across iterations. Located at workspace root.

```json
{
  "started_at": "2026-01-15T10:30:00Z",
  "skill_name": "pdf",
  "current_best": "v2",
  "iterations": [
    { "version": "v0", "parent": null, "expectation_pass_rate": 0.65,
      "grading_result": "baseline", "is_current_best": false },
    { "version": "v1", "parent": "v0", "expectation_pass_rate": 0.75,
      "grading_result": "won", "is_current_best": false },
    { "version": "v2", "parent": "v1", "expectation_pass_rate": 0.85,
      "grading_result": "won", "is_current_best": true }
  ]
}
```

`grading_result` is one of `baseline`, `won`, `lost`, `tie`. Use this to prove each iteration actually improved, and to roll back if one didn't.
