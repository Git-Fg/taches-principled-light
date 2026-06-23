# Skill-Evals Index

Behavioral evaluation of the marketplace skill router.
Tracks the 4 iterations run against the haiku solver (via inference-gateway proxy
on port 3456) using the `evaluating-skills` 8-stage harness.

## Iterations

| # | Date | What it tested | Status | Verdict |
|---|------|----------------|--------|---------|
| 1 | 2026-06-22 | Pilot — single eval `craft-create` end-to-end on Claude Code CLI | superseded by iter-2 | passed |
| 2 | 2026-06-22 | Full N=18 evals × {with, without}-skill = 36 runs | superseded by iter-3 | 17/18 completed; 1 proxy 503 |
| 3 | 2026-06-22 | Full N=17 evals, fixed consultation assertion bug + judge heterogeneity | **canonical, with caveat** | mean delta **+8.69pp**, 6 lifts / 11 neutrals / **0 hurts**. ⚠️ results reflect stale v2.0.0 plugin cache; see `SKILL-DISCOVERY-ARCHITECTURE.md` v1.2 |
| 3.1 | 2026-06-22 | Per-skill `--add-dir` experiment: H1 (plugin shadowing) vs H2 (description surfaces) vs H3 (choice paralysis) | **complete** (9/15 runs) | H1 confirmed for `craft-create`; H2 confirmed for `craft-review`; H3 not dominant; **H4 bonus**: zero-skill invocations in 6/9 runs (routing-heuristic failure upstream). See [`iteration-3.1/RESULTS.md`](marketplace-routing-2026-06-22/iteration-3.1/RESULTS.md) |
| 4 | planned | Cache-refreshed re-run of iter-3 (Phase A: heterogeneous judges; Phase B: sonnet only) | **designed** | [`iteration-4/PLAN.md`](marketplace-routing-2026-06-22/iteration-4/PLAN.md) v1.1. Cache refresh smoke test PASSED — `craft-create` now picks `crafting-skills` directly |

## Canonical report

The corrected iter-3 results live at
[`marketplace-routing-2026-06-22/iteration-3/REPORT.md`](marketplace-routing-2026-06-22/iteration-3/REPORT.md).
This is the report to cite.

The intermediate `INTERIM-FINDINGS.md` is SUPERSEDED and archived at
[`marketplace-routing-2026-06-22/.archive/INTERIM-FINDINGS-iter3-SUPERSEDED.md`](marketplace-routing-2026-06-22/.archive/INTERIM-FINDINGS-iter3-SUPERSEDED.md).

## Supporting documents

| Doc | Purpose |
|-----|---------|
| `SKILL-DISCOVERY-ARCHITECTURE.md` | **Foundational.** Documents how Claude Code actually loads skills. Critical findings: `--add-dir` controls cwd + file access only; installed plugins load their skills into `slash_commands` globally regardless of cwd; the iter-3/iter-3.1 plugin cache is **stale (v2.0.0 from 2026-06-21)** and doesn't match the v0.0.3 working marketplace, invalidating parts of the iter-3 results. iter-3's `without_skill` baseline is contaminated; H1 (plugin shadowing) IS the dominant cause of Bucket A3. |
| `iteration-3-design.md` | Synthesizes 6 reference frameworks (SkillsBench, Tessl, tau-bench, Lee et al. ICML 2026, Khullar 2026, Anthropic/Microsoft best practices) into the iter-3 design |
| `iteration-3/DISCOVERY-INVESTIGATION.md` | Re-evaluates skill rewrites: they target the wrong root cause but remain useful improvements |
| `iteration-3/BUCKET-A-INSPECTION.md` | Splits the 8 Bucket A neutrals into A1 (proxy errors) / A2 (partial discovery) / A3 (true discovery failures) |
| `iteration-3/unknowns.md` | Empty queue for UNKNOWN judge verdicts — schema + log |
| `methodology-note-routing-vs-validator.md` | Why this is a behavioral eval (measuring agent routing behavior) not a static validator run |
| `iteration-2/API-OVERLOAD-INCIDENT.md` | Forensic record of iter-2 partial failure |
| `iteration-2/METRIC-BUG-NOTE.md` | Forensic record of grader bug found by self-critic |
| `iteration-2/OUTCOME.md` | iter-2 final outcome summary |
| `iteration-3.1/RESULTS-PARTIAL.md` | 8 of 15 runs captured. H1 confirmed for `craft-create`; craft-review picked wrong marketplace skill; 6 of 8 runs invoked zero skills (routing-heuristic failure) |

## Archived experiments

| Path | Contents |
|------|----------|
| `.archive/iter-2.5-failed-runs/` | iter-2.5 mid-iteration failed runs (3 evals, all `rc=1`) — never recovered, preserved for forensics only |

## Methodology at a glance

- **Solver target**: `haiku` (Claude Haiku 4.5 via proxy) — matches the marketplace's actual consumer base
- **Judge model**: heterogeneous across evals (`sonnet` for complex compliance, `haiku` for simple quality)
- **Lift threshold**: ±5pp = neutral, > +5pp = lifts_quality, < -5pp = hurts (matches `evaluating-skills` `material_difference` rule)
- **Bucket taxonomy**: A (without-skill baseline ≥ 0) / B (without-skill baseline = 0, neutral) / C (lift)
- **Unknown verdicts** (`passed: null` from judge) are mapped to `unknown: true` and treated as FAIL for scoring; see `iteration-3/unknowns.md`

## Reproducing iter-3

```bash
cd docs/principled/skill-evals/marketplace-routing-2026-06-22
python iteration-3/scripts/run_iteration_3.py    # 17 evals x 2 configs = 34 runs
python iteration-3/scripts/grader.py             # reads benchmarks/, writes REPORT.md
```

Wall-clock budget: ~50 min for runs + ~5 min for grading on a warm proxy.

## Reproducing iter-3.1 (in progress)

```bash
python iteration-3.1/scripts/run_per_skill_experiment.py
```

5 Bucket A3 evals x 3 configs (without_skill / with_full_marketplace / with_skill_only)
= 15 runs. Tests whether the discovery failure is H1 (plugin shadowing), H2 (description
doesn't surface), or H3 (choice paralysis from 26+ marketplace skills).