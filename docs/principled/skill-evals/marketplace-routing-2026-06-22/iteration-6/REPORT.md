# iter-6 — Code-only lift decomposition (proxy architecture finding)

**Date:** 2026-06-23
**Author:** marketplace-routing evaluation harness
**Verdict:** INCONCLUSIVE for vendor-disjoint validation (proxy limitation), but reveals a clean **code-only lift decomposition** of iter-7's headline number.

---

## Headline finding: proxy architecture

While running iter-6, we probed the proxy at `http://100.80.231.128:3456` to understand the model alias surface. The findings shape the interpretation of every iteration that used a "different" model:

| Alias | Returns `model:` field | Real backend | Status |
|---|---|---|---|
| `haiku` | (timeout) | unknown | broken |
| `sonnet` | `MiniMax-M3` | MiniMax-M3 | working |
| `opus` | `MiniMax-M3` | MiniMax-M3 | working |
| `nex-agi/nex-n2-pro:free` | `MiniMax-M3` | MiniMax-M3 | alias-only, no real route |
| `glm-5.2` | (error) | Z.AI (real) | 503 `circuit_breaker_open: RateLimit` |
| `qwen`, `llama`, `gpt-4o`, `gemini`, `deepseek`, `mistral`, `claude-3*`, `doubao`, `kimi`, `minimax`, `phi-4`, `mixtral`, `command-r`, `jamba`, `cerebras`, `fireworks`, `deepinfra` | `MiniMax-M3` | MiniMax-M3 | silently aliased |

**Conclusion:** the proxy is architecturally a single-model gateway. The "haiku/sonnet/opus" labels are tier trackers, not different models. Every "vendor" alias in the catalog except `glm-5.2` falls back to the same `MiniMax-M3` backend. The only genuinely vendor-disjoint option is `glm-5.2` (Z.AI), and it is currently rate-limited with `circuit_breaker_open: RateLimit` (HTTP 429/503, `retry-after: 10`).

**Implication for the campaign:** every iter-4/iter-5/iter-7 grade is "haiku solver over MiniMax-M3, sonnet judge over MiniMax-M3." Same-family bias is real but unmitigable on this proxy right now. iter-6 was designed to mitigate it and is structurally blocked.

---

## What iter-6 actually measured

iter-6 reused the 4-eval subset transcripts (eval-skill, sec-audit, lint-1, release-2) from iter-7 and re-graded them with `--judge-model glm-5.2`. The grader's contract:

1. **Code-based assertions** (consultation detection, structure with `compare_args`) — bypass the LLM entirely.
2. **Model-based assertions** (compliance, quality, open-ended structure) — call the judge and parse `response["choices"][0]["message"]["content"]`.

Every model-based assertion in iter-6 hit the `glm-5.2` 503 and returned `unknown=true, evidence="judge parse error: KeyError('choices')", points_awarded=0`. So iter-6 is effectively a **code-only grade** — exactly the consultation + structure-with-compare_args signals, with all LLM-judgment slots forced to 0 by the proxy failure.

That is not what iter-6 was designed to measure, but it is a clean decomposition: it isolates the **deterministic, code-only lift** that the marketplace plugin produces. The LLM-judgment contribution is whatever sits on top.

---

## Results: code-only lift per eval (4 evals × 3 configs = 12 cells)

| Eval | iter-4 mechanism | baseline | plugin_only | plugin_with_add_dir | iter-6 total_lift (code-only) | iter-7 total_lift (sonnet, full) | Gap (sonnet adds) |
|---|---|---:|---:|---:|---:|---:|---:|
| eval-skill | consultation | 0.0 | 0.0 | 15.0 | **+15.0** | +15.0 | 0.0 |
| sec-audit | consultation | 0.0 | 15.0 | 15.0 | **+15.0** | +32.5 | +17.5 |
| lint-1 | file-access | 0.0 | 0.0 | 0.0 | **0.0** | +25.0 | +25.0 |
| release-2 | file-access | 0.0 | 0.0 | 0.0 | **0.0** | +15.0 | +15.0 |
| **mean** | | | | | **+7.5pp** | **+21.9pp** | **+14.4pp** |

`benchmark.json` and `benchmark_iter4_vs_iter6.json` contain the per-cell data. `comparison_glm5-2.json` is the per-eval lift decomposition.

### What this table tells us

1. **The code-only lift is +7.5pp (4 evals).** That's consultation + filesystem-access signals that the LLM judge did not influence. Three of four evals lift; one (release-2) shows zero code-only lift because the goal-completion rubric (created_annotated_tag, no_force_push_used) is purely model-judged.
2. **The +14.4pp gap is the LLM-judgment contribution.** Sonnet was more lenient/accurate on the model-only assertions (followed_8_stage_loop, ran_secrets_scan, named_specific_findings, etc.) that glm-5.2 could not grade.
3. **The lift direction is robust.** 3/4 evals show a positive code-only lift; 0/4 hurts. The 1/4 that is zero (release-2) lifts under the sonnet judge, so the plugin still helps on that eval — just on model-judged criteria, not code-based ones.
4. **The +7.5pp mean is a lower bound.** A working vendor-disjoint judge that grades the same way as sonnet would likely recover the +14.4pp gap. A working vendor-disjoint judge that grades more strictly would lower the mean. We do not know which.

### What this does NOT tell us

- **Whether a true vendor-disjoint judge (working glm-5.2) would agree with sonnet.** The proxy is structurally blocked from answering this question right now. The sec-audit swing between iter-4 (15.0) and iter-7 (32.5) on bit-for-bit identical transcripts (md5 `bda20918d4b7d0b7245bd12b59b09e58`) shows same-judge intra-iteration noise is itself +17.5pp. Same-family bias on top of that is plausible but unquantified.

---

## Reproduction

```bash
cd /Users/felix/Documents/AutoPluginClaw/taches-principled-light/docs/principled/skill-evals/marketplace-routing-2026-06-22/iteration-6
python3 scripts/run_iteration_6.py        # ~10s after transcripts are symlinked
# Reuses iter-7 transcripts via symlinks: eval-*/{baseline,plugin_only,plugin_with_add_dir}_skill.jsonl
# Calls grader.py with --judge-model glm-5.2 for every cell.
```

To re-run when glm-5.2 recovers, simply re-invoke the same command — no transcript regeneration needed. The grader will re-call glm-5.2 and parse `response["choices"]` correctly.

---

## Caveats

1. **Vendor-disjoint not validated.** The proxy's `glm-5.2` is the only real different model, and it is rate-limited. iter-6 cannot rule out same-family bias in the sonnet grades. We have a `+7.5pp` code-only lower bound and a `+21.9pp` same-family upper bound.
2. **iter-6 grader transcript reuse depends on iter-7 symlinks.** If iter-7 is moved/deleted, the symlinks break. They are explicit `../../` paths, not relative-from-CWD.
3. **Grader noise still applies.** iter-6's code-only assertions are deterministic and not subject to grader noise. iter-7's model-based assertions are; the sec-audit +17.5pp swing is the canonical example.
4. **No agent transcript was re-run in iter-6.** Only the grader is re-invoked. The 4-eval × 3-config transcripts are taken verbatim from iter-7. The numbers are valid for the iter-7 transcript set; they are not valid for any other transcript set.
5. **The proxy architecture finding is from a single probe session** (2026-06-23 ~14:38). It is not a structural test of the proxy across time. A future probe should retest after glm-5.2 recovers.

---

## What would unblock vendor-disjoint validation

1. **Wait for glm-5.2 to recover.** The 503 has `retry-after: 10`, but circuit breakers typically stay open for minutes to hours. Probe with `curl` before re-running.
2. **Or: route through a different proxy.** None is currently configured.
3. **Or: extend iter-5 to N=11 and use it as an intra-rater reliability floor.** Same-family but bigger N puts error bars on the +21.9pp headline. This is the path forward in the absence of glm-5.2.

---

## Files

- `iteration-6/eval-<id>/grading_{baseline,plugin_only,plugin_with_add_dir}_skill_glm5-2.json` — per-cell grades
- `iteration-6/eval-<id>/comparison_glm5-2.json` — per-eval lift decomposition
- `iteration-6/eval-<id>/{baseline,plugin_only,plugin_with_add_dir}_skill.jsonl` — symlinks to iter-7 transcripts
- `iteration-6/benchmark.json` — aggregate 4-eval table
- `iteration-6/benchmark_iter4_vs_iter6.json` — cross-iteration comparison
- `iteration-6/scripts/run_iteration_6.py` — runner (re-runnable)
- `iteration-6/iter6_full_run.log` — execution log
