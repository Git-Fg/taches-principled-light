# Iteration 2 — API Overload Incident (2026-06-22 ~01:20-01:44 UTC)

## What happened

The iteration-2 runner (`scripts/run_iteration_2.py`) was launched at 01:20 UTC to process 18 evals × 2 configurations (with-skill / without-skill) = 36 total runs. After 5 evals × 2 configs completed (10 of 36 runs), every transcript showed the same error:

```
API Error: Repeated 529 Overloaded errors. The API is at capacity —
this is usually temporary. Try again in a moment. If it persists,
check your inference gateway (100.80.231.128:3456).
```

The error originates from the inference gateway at `100.80.231.128:3456`, not from any local code. The runner's per-eval timeout (180s) and the underlying retries (up to 10 attempts with 10s backoff per the `api_retry` system event) were not enough to recover.

The runner was stopped at 01:44 UTC via `TaskStop` to avoid wasting ~70 more minutes on 26 more failed runs.

## What this is NOT

- Not a script bug. The pilot (commit `2fae0b1`, `iteration-1/eval-craft-create/`) ran cleanly with the same script pattern and produced 3 SKILL.md reads in the with-skill run.
- Not a parser bug. The behavioral_comparison.json files written so far are correctly structured; the `with_skill_score` and `without_skill_score` are correctly 0 because no SKILL.md reads occurred.
- Not a routing regression. The eval utterances that did run (`lint-1`, `lint-2`, `audit-1`, `audit-2`, `ingest-1`) all failed before the agent could consult any skill — the 529 error happens in the first assistant turn.

## What the partial data shows

The 5 partial behavioral_comparison.json files are valid artifacts (correct schema, correct delta computation, correct material_difference=False) but they contain **zero signal** because the agent never reached the skill-consultation step. The numbers (with=0, without=0, delta=0) are all noise from the API failure, not real measurements.

The 5 dirs are kept on disk for forensic purposes but are excluded from any aggregation in `benchmark.json` (which was never written because the runner was stopped before the aggregation step).

## Re-launch plan

When the gateway recovers (no specific ETA — this is a vendor-side issue), re-launch with the **same** `run_iteration_2.py` script. The script has been hardened post-launch:

- `TIMEOUT_S` raised from 180 to 300 (per the iteration-3 design's plan)
- `evals.json` schema validation at startup (refuses to start if any eval is missing `id`/`category`/`expected`/`utterance`)
- `count_words.py` reproducible script committed for the methodology note

If the API is still degraded at re-launch time, the runner will produce the same kind of all-zeros signal. A simple pre-flight check would be to run `claude --print --output-format stream-json "hello"` once and confirm a non-error response before launching the full 36-run sweep.

## Alternative approach (for future iterations)

For more robust evals, the runner could:
- Skip evals that errored (re-run them once after a 60s backoff)
- Or use a different model/provider as a fallback
- Or batch evals by routing-test category (since the 18 evals include 4 local-meta and 14 marketplace skills) and report per-category pass rates

These are scope-expansion items for iteration-3+, not blockers for re-running iteration-2 as-is.

## Files

- 5 partial `eval-*/` dirs in `iteration-2/` — preserved for forensics
- `iteration-2/runner.log` — removed (was empty due to stdout buffering through `tee`)
- The script and supporting files (`run_iteration_2.py`, `count_words.py`, `methodology-note-routing-vs-validator.md`, `iteration-3-design.md`) are all committed and unchanged.
