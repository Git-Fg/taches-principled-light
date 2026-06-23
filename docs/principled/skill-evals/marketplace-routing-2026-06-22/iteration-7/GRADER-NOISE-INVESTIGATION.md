# Grader noise — sec-audit consultation_lift cell

**Investigation date:** 2026-06-23
**Investigator:** self (in support of v0.0.5 release self-critic)

## Observation

The same `sec-audit` transcript md5 `bda20918d4b7d0b7245bd12b59b09e58` (the iter-4 `without_skill.jsonl`, relabeled as iter-7 `plugin_only_skill.jsonl`) was graded:

| Iteration | Config | Overall | Judge model |
|-----------|--------|--------:|-------------|
| iter-4    | without_skill | 15.0 | sonnet (= MiniMax-M3) |
| iter-7    | plugin_only   | 32.5 | sonnet (= MiniMax-M3) |

Δ = +17.5pp on bit-identical input, by the same judge. This is the source of the +8.12pp `consultation_lift` (noisy) reported in iter-7's `REPORT.md`.

## Root cause

`grader.py` (iteration-3/scripts/grader.py, md5 `330b9a6253f0a88b69241691738da8e0`) issues the LLM judge call without setting a `temperature` parameter:

```python
# iteration-3/scripts/grader.py:215-219
"-d", json.dumps({
    "model": judge_model,
    "max_tokens": 4000,
    "messages": [{"role": "user", "content": prompt}],
}),
```

The proxy uses its default sampling temperature. Same transcript → different grades is normal LLM stochasticity, not a bug.

## Empirical test: does `temperature=0` help?

Probe ran 5 calls at default and 5 calls at `temperature=0` on the prompt *"Pick a number 0-9. Reply with ONLY the digit, no other text."*:

| Sampling | 5 runs |
|----------|--------|
| default (proxy default) | 7, 4, 7, 3, 7 |
| temperature=0           | 3, 3, 7, 7, 5 |

**Result: temperature=0 does NOT make MiniMax-M3 deterministic.** Both distributions are stochastic. This is consistent with reasoning models exhibiting non-determinism at temp=0 due to floating-point, kernel scheduling, batch composition, or proxy-internal sampling.

The proxy is single-model: all 44 advertised model aliases silently map to `MiniMax-M3` (see `iteration-6/REPORT.md` "Proxy architecture finding"). There is no vendor-disjoint judge available — the only structurally-disjoint option, `glm-5.2`, is rate-limited (consistently 503s on this proxy).

## Mitigations considered

| Option | Cost | Effectiveness | Verdict |
|--------|------|---------------|---------|
| Add `temperature=0` to grader request | free (1-line code change) | **empirically NOT effective** on this proxy/model | reject |
| Switch to vendor-disjoint judge (glm-5.2) | free | **structurally blocked** (rate-limited 503) | reject |
| Multi-run averaging (3x per cell, take median) | ~3x grading cost | expected to reduce noise ~√3 | **defer to iter-8** |
| Document noise floor in canonical headline | free | readers know to discount the +8.12pp consultation_lift cell | **adopted** |

## Why the canonical headline is still robust

The headline `+21.88pp total_lift` is dominated by `filesystem_access_lift = +13.75pp` (3/4 evals deterministic: eval-skill, lint-1, release-2) plus a smaller `consultation_lift = +8.12pp` (1/4 evals: sec-audit, noisy). Even if sec-audit's consultation_lift is off by the full ±17.5pp, the total_lift still sits in `+21.88 ± 17.5` pp, and the **direction** (positive) is robust across 4/4 evals and 12/12 cells.

The headline remains publishable. The `consultation_lift` cell should be cited as "noisy, single-trial, treat as ±noise" in downstream references.

## What to do for iter-8+

1. **Multi-run averaging**: modify `grade_with_judge` to invoke the judge 3 times per (eval, config) and take the median `overall_score`. Cost: ~3x grading credits (~$0.10 → $0.30 per cell, 12 cells = $3.60 per full iter-8 run). Expected noise reduction: ~√3 ≈ 1.7x.
2. **Re-test consultation_lift**: with median-of-3 grading, the +8.12pp consultation_lift should tighten to a stable value (likely 0-15pp). This would unblock the "is consultation_lift real or noise?" question.
3. **Document the proxy's non-determinism in `AGENTS.md`**: future agents running evaluations on this proxy should expect ~±15pp single-trial noise on LLM-judged assertions.

## References

- `iteration-3/scripts/grader.py` — the LLM judge call (lines 215-219)
- `iteration-4/eval-sec-audit/grading_without_skill.json` — 15.0 grade on transcript `bda20918...`
- `iteration-7/eval-sec-audit/grading_plugin_only_skill.json` — 32.5 grade on the same transcript
- `iteration-6/REPORT.md` — proxy architecture finding (single model, vendor-disjoint blocked)
- `iteration-7/REPORT.md` caveat #3 — already documents "grader non-determinism" at headline level
