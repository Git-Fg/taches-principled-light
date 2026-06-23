# Iteration 3 Report — Marketplace Skill Behavioral Validation (N=17)

**Date**: 2026-06-23
**Scope**: 17 of 18 evals (rust-clippy skipped — no iter-2 transcript)
**Solver**: `haiku` chain via inference-gateway proxy (VPS port 3456)
**Judge**: `haiku` (same family as solver; bias mitigation deferred to iter-3.1)
**Method**: Assertion-based grading per Tessl framework ([arxiv 2606.17819v1](https://arxiv.org/html/2606.17819v1))

## TL;DR

The marketplace's skills produce a **mean overall delta of +4.21pp** when
consulted versus when omitted — small but positive. The signal is **highly
polarized**: 5 skills lift quality, 3 hurt it, and 9 are neutral (most of
those are 0/0 with vs without skill — both scored zero).

**Top priority actions**:
1. **Rewrite `ingesting-skills`** — consistent -16.25pp hurt on both ingest
   evals. The skill workflow is over-prescriptive for the test cases.
2. **Investigate `marketplace-validator` polarity** — +45pp on lint-1,
   -20pp on lint-2. Same skill, similar utterances, opposite effects.
3. **Validate the 9 `skill_neutral` 0/0 results** — most are 0/0 (both
   with and without scored zero on all assertions). Need manual transcript
   inspection to distinguish "task too hard for haiku" from "judge
   bias".
4. **Re-run with `--judge-model sonnet` or `glm-5.2`** for the 3 hurt
   evals to control same-family judge bias (haiku solver + haiku judge).

## Verdict distribution

| Verdict | Count | % of N=17 |
|---|---|---|
| `skill_lifts_quality` (overall delta > +5pp) | 5 | 29% |
| `skill_neutral` (\|delta\| ≤ 5pp) | 9 | 53% |
| `skill_hurts` (overall delta < -5pp) | 3 | 18% |
| `skill_redundant` (no lift in either IF or GC) | 0 | 0% |

## Per-eval results

| Eval | Skill | Δ IF | Δ GC | Δ Overall | Verdict |
|---|---|---:|---:|---:|---|
| lint-1 | marketplace-validator | +40 | +50 | **+45.0** | skill_lifts_quality |
| release-2 | releasing-marketplace | 0 | +50 | **+25.0** | skill_lifts_quality |
| critic | general-critic | -30 | +50 | **+20.0** | skill_lifts_quality |
| release-1 | releasing-marketplace | +30 | 0 | **+15.0** | skill_lifts_quality |
| eval-skill | evaluating-skills | +30 | 0 | **+15.0** | skill_lifts_quality |
| audit-1 | marketplace-health | +10 | 0 | +4.1 | skill_neutral |
| audit-2 | marketplace-health | 0 | 0 | 0 | skill_neutral |
| research | deep-research | 0 | 0 | 0 | skill_neutral |
| craft-create | crafting-skills | 0 | 0 | 0 | skill_neutral |
| craft-review | crafting-skills | 0 | 0 | 0 | skill_neutral |
| plan-multi | plan-lifecycle | 0 | 0 | 0 | skill_neutral |
| task-small | task-lifecycle | 0 | 0 | 0 | skill_neutral |
| web-rust | web-search | 0 | 0 | 0 | skill_neutral |
| sec-audit | security | 0 | 0 | 0 | skill_neutral |
| ingest-1 | ingesting-skills | -30 | 0 | **-15.0** | skill_hurts |
| ingest-2 | ingesting-skills | -35 | 0 | **-17.5** | skill_hurts |
| lint-2 | marketplace-validator | -40 | 0 | **-20.0** | skill_hurts |

## Per-skill mean lift

| Skill | N evals | Mean lift | Pattern | Verdict |
|---|---:|---:|---|---|
| `releasing-marketplace` | 2 | **+20.0pp** | Both evals lift | Strong positive |
| `general-critic` | 1 | **+20.0pp** | Single sample | Promising |
| `evaluating-skills` | 1 | **+15.0pp** | Single sample | Promising |
| `marketplace-validator` | 2 | +12.5pp | POLARIZED (+45/-20) | Needs investigation |
| `marketplace-health` | 2 | +2.05pp | Both near-neutral | Mildly positive |
| `crafting-skills` | 2 | 0.0pp | Both 0/0 | Neutral |
| `deep-research` | 1 | 0.0pp | Single 0/0 | Insufficient data |
| `plan-lifecycle` | 1 | 0.0pp | Single 0/0 | Insufficient data |
| `task-lifecycle` | 1 | 0.0pp | Single 0/0 | Insufficient data |
| `web-search` | 1 | 0.0pp | Single 0/0 | Insufficient data |
| `security` | 1 | 0.0pp | Single 0/0 | Insufficient data |
| `ingesting-skills` | 2 | **-16.25pp** | Both hurt | Needs rewrite |

## High-priority findings

### F1. `ingesting-skills` reliably underperforms (N=2, consistent)

Both `ingest-1` ("port this skill from a github url into our collection")
and `ingest-2` ("add this skill to our marketplace, import it") show
~-16pp overall delta. The with-skill agent **scored 0/5** on both evals;
the without-skill agent scored 1/5 (IF=30, IF=35).

This is the strongest signal in the dataset: same direction, two
independent evals, large magnitude. The without-skill agent (using its
general-purpose LLM knowledge) outperformed the agent following the
skill's prescribed workflow.

**Root cause hypothesis**: The `ingesting-skills` workflow encodes a
multi-step "port → verify → commit" pattern with explicit verification
steps. The test utterances ask for simple port/import actions where the
extra workflow overhead causes the agent to lose track of the core task.
The with-skill agent spent its effort on the prescribed workflow;
without-skill agents did the simple port directly and got the
underlying task done.

**Recommended action**: 
1. Add a "quick port" mode to `ingesting-skills` for utterances like
   "port this" or "import this", bypassing the full verification flow.
2. Re-run the two ingest evals with `--judge-model sonnet` to rule out
   same-family judge bias before rewriting the skill.

### F2. `marketplace-validator` polarized (+45 vs -20)

Same skill, two similar utterances, opposite effects:
- `lint-1` ("lint the marketplace and check the frontmatter") → +45pp
- `lint-2` ("is this skill valid before I commit") → -20pp

The with-skill agent for `lint-2` scored 0/5; the without-skill agent
scored 1/5 (IF=40). This is the inverse of the lift signal: with-skill
underperformed.

**Root cause hypothesis**: The `lint-2` assertion set tests the agent's
ability to perform a focused pre-commit validation, but the skill
prescribes a general-purpose marketplace lint workflow. With-skill
agents followed the broader workflow and missed the focused check;
without-skill agents (knowing nothing of the skill) naturally focused
on what the user asked for.

This is a **meta-finding**: marketplace skills can be over-prescriptive
when the user's actual intent is narrower than the skill's scope. The
skill is not "wrong", but its routing boundary is too wide.

**Recommended action**:
1. Split `marketplace-validator` into two sub-routes:
   - "marketplace-validator: full" for "lint the marketplace"
   - "marketplace-validator: precommit" for "is this skill valid before I commit"
2. Re-run both lint evals with the new routing.

### F3. The 9 `skill_neutral` results are mostly 0/0 (not "close to neutral")

Looking at the raw scores, **7 of 9 neutrals are 0/0** (both with and
without scored zero on all assertions). Only `audit-1` (+4.1pp) and
`research` (0.0pp but both scored 12.5) are interesting.

The 0/0 result is suspicious. Either:
1. The assertions are too strict for haiku to satisfy (rubric design issue)
2. The judge (haiku, same family) is biased toward low scores
3. Both with and without ran into the same error and neither produced
   useful output

**Recommended action**: Sample 2-3 transcripts from the 0/0 bucket
(e.g., `craft-review`, `plan-multi`, `task-small`) and inspect
manually. If the transcripts are substantively different but scored
identically, the judge is the problem → re-run with `--judge-model glm-5.2`.

### F4. `releasing-marketplace` is the only consistent strong lift

Both release evals show positive lift:
- `release-1` ("cut a release and bump the version to 0.0.2") → +15pp (IF only)
- `release-2` ("tag and push the new version") → +25pp (GC only)

The IF/GC split is informative: release-1 helps the agent follow the
prescribed version-bump workflow; release-2 helps the agent complete the
goal (successfully tag and push). The skill is well-tuned to both.

**Recommended action**: Use `releasing-marketplace` as the **positive
reference** when authoring or rewriting other marketplace skills. Its
description, triggers, and workflow all aligned with the actual test
utterances.

## Cross-cutting findings

### C1. Goal completion (GC) discriminates more than instruction following (IF) for marketplace skills

The Tessl paper ([arxiv 2606.17819v1](https://arxiv.org/html/2606.17819v1))
found that on coding tasks, **IF is the discriminating metric** (GC
saturates near 100% for most models). For our marketplace skill evals,
the opposite pattern holds: **GC discriminates strongly** (mean +8.8pp
across 17 evals) while **IF is nearly flat** (mean -1.5pp).

This makes sense: marketplace skills encode **outcomes** (do X, then Y,
then verify with Z) rather than **code style** (use snake_case, indent
with 4 spaces). Goal completion is the metric that captures this.

### C2. Same-family judge bias is uncontrolled

Both solver (`haiku`) and judge (`haiku`) are the same underlying model
family (nex-agi via the inference-gateway proxy). Per Wataoka et al.
([arXiv 2410.21819](https://arxiv.org/abs/2410.21819), NeurIPS 2024
Workshop), same-family judges share systematic biases with their
solver, which can inflate or deflate apparent deltas. Per Lee et al.
(ICML 2026, [arXiv 2511.21140v2](https://arxiv.org/abs/2511.21140)),
the fix is to use a different-family judge (sonnet or glm-5.2 in our
proxy).

The 3 `skill_hurts` results in particular are concerning because
haiku-judge-on-haiku-solver could systematically under-credit the
with-skill runs if they "look more skill-compliant" to the judge.

**Recommended action**: Re-run the 3 hurt evals (`ingest-1`, `ingest-2`,
`lint-2`) with `--judge-model sonnet`. If the deltas flip sign or
shrink toward zero, the hurts are judge artifacts.

### C3. Single-trial noise floor limits per-eval confidence

Per Yagubyan (2026, [arXiv 2606.13685](https://arxiv.org/abs/2606.13685)),
single-trial LLM judge ratings have a **±13.6% flip rate**. The deltas
in this dataset range from -20pp to +45pp, so the strong signals (+45,
+25, -20) are outside the noise band. The 0/0 and ±5pp signals may be
noise.

Multi-trial majority vote is the proper fix (deferred to iter-3.1).

## What iter-3 validates vs iter-2

Iter-2 measured only **how many marketplace SKILL.md files** the agent
consulted. Iter-3 measures **whether the consultation actually helped**.

The comparison is stark:

| Metric | iter-2 | iter-3 |
|---|---|---|
| Reads per with-skill run | 0 (529 errors blocked consultation) | (not measured) |
| Assertion pass rate | n/a | 1.16/5 avg |
| Verdict classification | n/a | 5 lifts, 9 neutral, 3 hurts |
| Surfaced `skill_hurts`? | No | Yes (3 evals) |
| Surfaced `skill_lifts_quality`? | No | Yes (5 evals) |

**Iter-3 is strictly more informative than iter-2.** The assertion-based
grading surfaces signals that read-counting cannot.

## Methodology limitations

1. **N=1 trials**: 6 skills have only 1 eval each (general-critic,
   evaluating-skills, deep-research, plan-lifecycle, task-lifecycle,
   web-search, security). The "1-sample lifts" (general-critic +20,
   evaluating-skills +15) are not yet reliable signals.
2. **Same-family judge**: haiku solver + haiku judge. Bias mitigation
   deferred to iter-3.1 (sonnet / glm-5.2 re-runs).
3. **Single-trial noise floor**: ±13.6% per Yagubyan. Multi-trial
   majority vote deferred to iter-3.1.
4. **No `rust-clippy` eval**: iter-2 never produced a transcript for it
   (probably the 529-overload incident). The eval assertion set exists
   but is ungraded.
5. **0/0 `skill_neutral` results are ambiguous**: could be (a)
   assertions too strict, (b) judge bias, or (c) actual parity. Need
   manual transcript inspection.

## Recommended next steps (iter-3.1)

1. **Re-run 3 hurt evals with `--judge-model sonnet`** to test same-family
   judge bias (C2). ~15-30 min.
2. **Re-run 5 lift evals with `--judge-model sonnet`** for consistency
   check. ~25-50 min.
3. **Sample-inspect 2-3 0/0 transcripts** to distinguish (a)/(b)/(c) for
   F3. ~15 min.
4. **Rewrite `ingesting-skills`** with a "quick port" mode (F1).
5. **Split `marketplace-validator`** routing (F2).
6. **Multi-trial majority vote**: re-run 3 evals per skill at N=3
   (deferred — full budget ~3 hours).

## Files produced

- `iteration-3-design.md` — design doc (synthesizes Tessl, Anthropic
  skill-creator, Anthropic Complete Guide, tau-bench, SkillsBench)
- `iteration-3/scripts/grader.py` — LLM-as-judge runner
- `iteration-3/scripts/run_iteration_3.py` — orchestrator
- `iteration-3/assertions/*.json` — 18 assertion sets (17 evaluated, 1
  unused for rust-clippy)
- `iteration-3/eval-*/comparison.json` — 17 per-eval comparisons
- `iteration-3/eval-*/grading_*.json` — 17 per-config gradings (34 files)
- `iteration-3/benchmark.json` — final aggregate results
- `iteration-3/benchmark.md` — human-readable report
- `iteration-3/INTERIM-FINDINGS.md` — earlier (corrected) interim note
- `iteration-3/unknowns.md` — human-review queue (empty; no UNKNOWN verdicts)
- `iteration-3/JUDGE-BIAS-CAVEATS.md` — LLM-judge reliability caveats
  (Lee et al., Yagubyan, Wataoka, Khullar)

## Citation

Methodology drawn from:
- Tessl framework, [arXiv 2606.17819v1](https://arxiv.org/html/2606.17819v1)
- Anthropic skill-creator (Create/Eval/Improve/Benchmark modes)
- Anthropic Complete Guide to Building Skills
- tau-bench `EvaluationCriteria`
- SkillsBench, [arXiv 2602.12670v4](https://arxiv.org/abs/2602.12670)
- Lee et al. 2026 (LLM-judge bias mitigation), [arXiv 2511.21140v2](https://arxiv.org/abs/2511.21140)
- Yagubyan 2026 (single-trial noise), [arXiv 2606.13685](https://arxiv.org/abs/2606.13685)
- Wataoka et al. 2024 (same-family judge bias), [arXiv 2410.21819](https://arxiv.org/abs/2410.21819)
- Khullar et al. 2026 (self-attribution bias), [arXiv 2603.04582](https://arxiv.org/abs/2603.04582)