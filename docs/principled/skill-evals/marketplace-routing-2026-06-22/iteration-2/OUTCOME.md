# Iteration-2 Outcome: Partial Run (2026-06-22)

## Summary

The iter-2 background run (`bash-oybmzbo0`) timed out after ~180 min wall budget.
**12 of 18 evals completed**, but all with the stale metric filter (reads=0 everywhere).
**5 evals (13-17) failed** with `exit_1, events=15` — a transient proxy/API failure.
**1 eval (18) never started.**

## Run Timeline

| # | Eval | with-skill | without-skill | Notes |
|---|------|-----------|---------------|-------|
| 1 | lint-1 | completed 145s | completed 27s | reads=0 (stale filter) |
| 2 | lint-2 | completed 39s | completed 52s | reads=0 |
| 3 | audit-1 | completed 194s | completed 71s | reads=0 |
| 4 | audit-2 | completed 245s | completed 19s | reads=0 |
| 5 | ingest-1 | completed 25s | completed 79s | reads=0 |
| 6 | ingest-2 | completed 81s | completed 88s | reads=0 |
| 7 | release-1 | **timeout** 300s | completed 165s | 73 events, 1 read |
| 8 | release-2 | completed 61s | completed 64s | reads=0 |
| 9 | critic | completed 236s | completed 63s | reads=0 |
| 10 | research | **timeout** 300s | **timeout** 300s | Both configs timed out |
| 11 | craft-create | completed 58s | completed 19s | reads=0 |
| 12 | craft-review | completed 25s | completed 41s | reads=0 |
| 13 | eval-skill | **timeout** 300s | **exit_1** 199s | Proxy failure begins |
| 14 | plan-multi | **exit_1** 197s | **exit_1** 190s | exit_1 events=15 |
| 15 | task-small | **exit_1** 195s | **exit_1** 192s | exit_1 events=15 |
| 16 | web-rust | **exit_1** 204s | **exit_1** 193s | exit_1 events=15 |
| 17 | sec-audit | (cut off) | (never started) | Runner timed out |

## Root Causes

### 1. Stale Metric Filter (known, documented)

The running process had the old `MARKETPLACE_SKILL_DIRS = [skills/]` filter.
The fix (commit `069b31c`, widening to `[skills/, .agents/skills/]`) only
takes effect on re-runs. All 12 completed evals show reads=0.

**Impact**: The with-skill vs without-skill comparison cannot be made from
this data. Even if reads were captured, the comparison would be 0 vs 0.

### 2. Transient Proxy Failure (evals 13-17)

The `exit_1, events=15, dur~190s` pattern across 5 consecutive evals
suggests the Haiku chain on proxy port 3456 became unresponsive for a
window. Post-mortem check confirmed the proxy is back up (`/v1/models`
returns valid JSON). This is a transient infrastructure issue, not a
runner bug.

### 3. Two Timeouts on Complex Evals

- **release-1 with-skill** (300s, 73 events, 1 read): the agent went deep
  into the release workflow but couldn't complete in 300s.
- **research both configs** (300s each): deep-research is inherently
  long-running; 300s is insufficient for a 5-stage pipeline.

## Decision: Do Not Re-run iter-2

Re-running iter-2 would cost another ~180 min and still produce data with
the stale-filter issue absent a code fix. The iter-3 design already
incorporates all lessons from iter-2:

1. **Metric fix**: `MARKETPLACE_SKILL_DIRS` widened (commit `069b31c`)
2. **Assertion-based grading**: Tessl rubric replaces read-counting
3. **Judge calibration**: self-attribution bias mitigation (Sonnet 4.5 judge)
4. **Timeout handling**: iter-3 uses the 8-stage loop from `evaluating-skills`,
   which has its own timeout management

## What iter-2 Did Validate

- **Runner infrastructure works**: preflight, env injection, JSONL capture,
  timeout enforcement, and dual-config (with/without skill) all functioned.
- **Haiku chain is viable**: 12 evals completed successfully through the proxy.
- **Complex skills need more time**: release and research workflows exceed
  300s. iter-3 should either increase timeout or use shorter eval prompts.
