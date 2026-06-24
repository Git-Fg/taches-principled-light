# Trigger-Eval Guide

How to write a 20-query trigger-eval set, run it through the harness, and interpret the report. This is the description-quality side of the evaluating-skills harness; the body-quality side (8-stage loop, behavioral comparison) is in `SKILL.md`.

## Why trigger evals are different from execution evals

| | Execution eval (8-stage loop) | Trigger eval (this guide) |
|---|---|---|
| Question | Does the skill make the agent *behave* better? | Does the skill's *description* cause correct *routing*? |
| Comparison | with_skill vs without_skill on the same prompt | trigger on a should-trigger prompt vs not-trigger on a should-not prompt |
| Unit of evidence | behavioral transcript + grader verdict | binary triggered/not-triggered per query per run |
| Where it lives | stage 5 of the 8-stage loop | OPTIMIZE mode (or pre-step of it) |
| Tooling | `aggregate_benchmark.py` | `trigger_eval.py` (this skill) |

A skill can pass execution evals but fail trigger evals (the agent does well when it lands on the skill, but the description doesn't make it land on the skill). A skill can pass trigger evals but fail execution evals (the description routes correctly, but the body doesn't help). Both are needed.

## How to write the 20-query set

Scaffold the set with `trigger_eval.py init --out trigger-queries.json` (uses the `assets/trigger-queries-template.json` shape). Then fill in `query` for every entry, preserving `should_trigger`.

### Discipline that makes the queries useful

Per `references/behavioral-review.md` §trigger-evals:

- **Realistic, not abstract.** Include file paths, column names, personal context, typos, casual speech. "ok so my boss just sent me this xlsx..." not "format this data".
- **Should-not must be near-misses.** "Write a fibonacci function" as a negative for a PDF skill tests nothing. The valuable negatives share keywords/concepts with the skill but need something else — adjacent domains where a naive keyword match would wrongly fire.
- **Substantive enough to need the skill.** Trivial one-step queries ("read file X") won't trigger any skill regardless of description quality, because the agent handles them with basic tools. The query must be complex enough that consulting the skill would actually help.

Per AGENTS.md Description-as-Routing-Signal rule 7: **weighted to near-misses, not obvious negatives.** An obvious negative is one where no description could ever fire on it. A near-miss is one where a vague description *would* fire on it but a precise description *would not*. The near-misses are the load-bearing tests.

### How many should-trigger vs should-not

Default is 10/10 (the template alternates). Adjust to 8/12 if your skill's natural domain is narrow (the should-not side is more informative for narrow skills), or 12/8 if your skill is broad and you're worried about missing trigger conditions. The split must be balanced enough that the train/val split (next section) preserves the ratio in both halves.

## How to run the eval

The 4-step flow:

```bash
# 1. Scaffold
python3 scripts/trigger_eval.py init --out /tmp/queries.json --skill-name my-skill

# 2. Edit the scaffolded file: fill in `query` for every entry.

# 3. Split 60/40 train/val
python3 scripts/trigger_eval.py split /tmp/queries.json /tmp/train.json /tmp/val.json --seed 42

# 4. Run the 20 queries against the agent, capturing transcripts.
#    For each (query, run_number), produce a transcript.jsonl and run:
python3 scripts/trigger_eval.py detect transcript.jsonl my-skill --runtime claude
# (exit 0 = triggered, 1 = not triggered)
# Append {"query_id": N, "run_number": K, "triggered": bool} to results.jsonl

# 5. Score
python3 scripts/trigger_eval.py score /tmp/queries.json /tmp/results.jsonl --threshold 0.5
# Writes trigger-rate-report.json + trigger-rate-report.md
```

For step 4, repeat the per-query run ≥3 times to get a stable trigger rate. The 0.5 threshold is the AGENTS.md rule 7 default; raise to 0.7 for critical routing (where false positives are expensive) or lower to 0.4 for a permissive skill (where false negatives are expensive).

## How to read the report

`trigger-rate-report.md` has three sections:

### Aggregate

| Config | What it measures | Target |
|---|---|---|
| `trigger_rate_should` | mean trigger rate across should-trigger queries | ≥ threshold (default 0.5) |
| `trigger_rate_should_not` | mean trigger rate across should-not queries | ≤ 1 - threshold (default 0.5) |

If `threshold_pass: false`, look at the per-query table to see which queries flipped. A high should-side failure rate means the description is **too narrow** — broaden it. A high should-not-side failure rate means the description is **too broad** — narrow it.

### Per-query

Each row is one query. `pass: true` means the per-query trigger rate is on the right side of threshold given `should_trigger`. A query with `pass: null` had no results (the eval didn't actually run it) — investigate before drawing conclusions.

`runs` should be ≥3 per query for a stable rate. If you ran 1 run, treat the report as suggestive, not decisive.

### Notes

Auto-derived signals. The "broaden the description" note means many should-triggers are below threshold — your description is too specific. The "narrow the description" note means many should-nots are above threshold — your description is too broad.

## Sibling-stealing detection

When you add or change a skill, run the trigger-eval set of every sibling in the same thematic cluster before and after. If a sibling's `trigger_rate_should` drops by more than 10pp, the new or changed description is stealing routing signal.

```bash
# Compare two trigger-rate reports (one per skill in the cluster)
python3 scripts/trigger_eval.py stealing before.json after.json --threshold 0.10
```

The script writes `stealing-alerts.json` and `stealing-alerts.md`. The markdown has a table of alerts. Each row is a skill whose should-trigger rate dropped by more than the threshold.

`stealing` accepts both single-skill reports (one `aggregate` block) and multi-skill aggregator reports (a dict of skill_name → report). For a cluster comparison, build a small aggregator JSON that contains the `aggregate.trigger_rate_should.mean` for every skill in the cluster, before and after, and pass both aggregator files.

**What to do with an alert:** narrow the new or changed description, or merge the two skills (per `crafting-skills` Compendium Rule 2 tightly-coupled-cluster exception). Do NOT raise the threshold to hide the alert — the threshold is a discipline, not a knob.

## The 60/40 train/val split + 3-runs + 0.5-threshold discipline

Why these numbers:

- **3 runs per query** — fewer runs means the per-query trigger rate is dominated by sampling noise. AGENTS.md rule 7 sets ≥3 as the floor. For a publishable headline, use 5+ runs.
- **60/40 train/val, stratified by should_trigger** — the split must preserve the should-trigger ratio in both halves; otherwise the val set is over- or under-weighted. `--seed 42` makes the split reproducible.
- **0.5 threshold** — symmetric (should-trigger needs ≥0.5, should-not needs ≤0.5). A symmetric threshold is the easiest to interpret. Use asymmetric thresholds (0.7 should / 0.3 should-not) only when the cost asymmetry is real (e.g., a security skill where false positives are very expensive).

When iterating the description (the OPTIMIZE-mode loop), use the train failures to propose improvements and validate on the val set. Picking best by train score overfits to the train queries. Picking best by val score generalizes.

Cap at 5 iterations — beyond that, the description is being tuned to noise.

## When trigger evals are not enough

If the runtime can't be driven as a subprocess or can't capture transcripts (per `references/runtime-adapters.md` §when-no-subprocess), skip trigger evals. The trigger-eval loop requires a transcript stream; without one, `trigger_eval.py detect` has nothing to parse. In that case, rely on `crafting-skills` OPTIMIZE mode + `skill-self-testing.md`'s grep-based pre-commit checks, matching Anthropic's Claude.ai guidance.

## See also

- `SKILL.md` — the main evaluating-skills methodology + 8-stage loop
- `references/behavioral-review.md` §trigger-evals — the trigger-eval query discipline
- `references/schemas.md` §trigger_evals.json — the input schema
- `references/schemas.md` §trigger-rate-report.json — the output schema
- `references/schemas.md` §results.jsonl — the per-run results format
- `assets/trigger-queries-template.json` — the 20-query skeleton
- `assets/shadow-skill-scaffold.md` — adversarial shadow-skill generation
- AGENTS.md "Description as Routing Signal" rules 6 + 7
