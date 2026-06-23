# Iter-3 UNKNOWN Verdicts — Human Review Queue

When the LLM judge returns `unknown: true` for a `compliance` or `quality`
assertion, the grader logs the verdict here for human review. UNKNOWN is
treated as FAIL for scoring purposes but flagged separately so a human can
decide whether the assertion should be:

- **Resolved**: re-grade manually with the evidence; update `passed` accordingly.
- **Retired**: the assertion is genuinely hard to grade automatically; remove it.
- **Reformulated**: rewrite the assertion text so it's less ambiguous.

## Schema

| Column | Type | Description |
|---|---|---|
| `date` | ISO-8601 | When the UNKNOWN was emitted |
| `eval_id` | string | e.g. `craft-create` |
| `assertion_id` | string | e.g. `applied_routing_pattern` |
| `judge_model` | string | The judge model that emitted the UNKNOWN (e.g. `sonnet`) |
| `evidence_excerpt` | string (≤500 chars) | The relevant transcript/skill/response excerpt the judge based its decision on |
| `judge_rationale` | string | Why the judge returned UNKNOWN |
| `human_verdict` | enum | Pending / Resolved / Retired / Reformulated |
| `human_notes` | string | Optional review notes |

## Log

| date | eval_id | assertion_id | judge_model | verdict |
|---|---|---|---|---|
| _no UNKNOWN verdicts yet — iter-3 has not run_ |

## Process

1. The grader appends a new row to this log whenever it emits `unknown: true`.
2. A human reviews the queue periodically (suggested cadence: end of each
   iter-3 run, before the next iter-3.1).
3. Resolved verdicts update the corresponding `grading_iter3.json` in-place
   so the `benchmark.json` aggregate reflects the correct human judgment.
4. Retired verdicts are removed from the eval's assertions.json in iter-3.1.
5. Reformulated verdicts replace the original assertion in assertions.json
   (with a `_v2` suffix on the id to preserve history).

## Why this queue exists

Anthropic's `Demystifying evals` guide: *"Give the LLM a way out —
instruction to return `"Unknown"` when uncertain."* The queue is the
follow-through: an UNKNOWN verdict without a human-review path is the
worst of both worlds (the LLM abdicates, but no one picks it up).
