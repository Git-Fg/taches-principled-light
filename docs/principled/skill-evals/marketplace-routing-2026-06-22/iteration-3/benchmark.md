# Iteration 3 — Assertion-Based Skill Grading (N=17)

## Configuration
- Judge model: `haiku`
- Solver model: haiku (project convention)
- Lift threshold: ±5pp for skill_neutral

## Summary
- Evals: 17
- Mean IF delta: +8.24
- Mean GC delta: +8.82
- Mean overall delta: +8.69

### Verdict distribution
- `skill_neutral`: 11/17
- `skill_lifts_quality`: 6/17

### Per-skill mean overall delta

| Skill | Mean Δ | Evals |
|-------|-------:|------:|
| general-critic | +31.20 | 1 |
| marketplace-validator | +22.50 | 2 |
| releasing-marketplace | +20.00 | 2 |
| evaluating-skills | +15.00 | 1 |
| marketplace-health | +8.25 | 2 |
| ingesting-skills | +0.00 | 2 |
| deep-research | +0.00 | 1 |
| crafting-skills | +0.00 | 2 |
| plan-lifecycle | +0.00 | 1 |
| task-lifecycle | +0.00 | 1 |
| web-search | +0.00 | 1 |
| security | +0.00 | 1 |

## Per-eval results

| Eval | Expected | IF Δ | GC Δ | Overall Δ | Verdict |
|------|----------|-----:|-----:|----------:|---------|
| lint-1 | marketplace-validator | +40.0 | +50.0 | +45.0 | skill_lifts_quality |
| lint-2 | marketplace-validator |  +0.0 |  +0.0 |  +0.0 | skill_neutral |
| audit-1 | marketplace-health | +40.0 |  +0.0 | +16.5 | skill_lifts_quality |
| audit-2 | marketplace-health |  +0.0 |  +0.0 |  +0.0 | skill_neutral |
| ingest-1 | ingesting-skills |  +0.0 |  +0.0 |  +0.0 | skill_neutral |
| ingest-2 | ingesting-skills |  +0.0 |  +0.0 |  +0.0 | skill_neutral |
| release-1 | releasing-marketplace | +30.0 |  +0.0 | +15.0 | skill_lifts_quality |
| release-2 | releasing-marketplace |  +0.0 | +50.0 | +25.0 | skill_lifts_quality |
| critic | general-critic |  +0.0 | +50.0 | +31.2 | skill_lifts_quality |
| research | deep-research |  +0.0 |  +0.0 |  +0.0 | skill_neutral |
| craft-create | crafting-skills |  +0.0 |  +0.0 |  +0.0 | skill_neutral |
| craft-review | crafting-skills |  +0.0 |  +0.0 |  +0.0 | skill_neutral |
| eval-skill | evaluating-skills | +30.0 |  +0.0 | +15.0 | skill_lifts_quality |
| plan-multi | plan-lifecycle |  +0.0 |  +0.0 |  +0.0 | skill_neutral |
| task-small | task-lifecycle |  +0.0 |  +0.0 |  +0.0 | skill_neutral |
| web-rust | web-search |  +0.0 |  +0.0 |  +0.0 | skill_neutral |
| sec-audit | security |  +0.0 |  +0.0 |  +0.0 | skill_neutral |

## Methodology

- Tessl-style per-category 0-100 scoring (IF + GC, weighted 50/50 by default)
- Two assertions per category minimum; some evals use weight overrides
- Code-based checks (consultation, structure with compare_args) bypass the LLM
- UNKNOWN verdicts (judge couldn't determine) are treated as FAIL for scoring
  but logged in `iteration-3/unknowns.md` for human review
