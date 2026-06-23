# Iteration 4 Phase A — Cache-Refreshed Re-Run (N=18)

## Configuration
- Judge model: `sonnet`
- Solver model: `haiku`
- Cache state: fresh (cleared 2026-06-23)
- Lift threshold: ±5pp for skill_neutral

## Summary
- Evals graded: 18/18
- Mean IF delta: +7.50
- Mean GC delta: +2.78
- Mean overall delta: +4.94
- iter-3 reference: +8.69pp mean overall delta

### Verdict distribution
- `skill_neutral`: 13/18
- `skill_lifts_quality`: 5/18

### Per-skill mean overall delta

| Skill | Mean Δ | Evals |
|-------|-------:|------:|
| security | +17.50 | 1 |
| evaluating-skills | +15.00 | 1 |
| marketplace-validator | +12.50 | 2 |
| marketplace-health | +8.25 | 2 |
| releasing-marketplace | +7.50 | 2 |
| ingesting-skills | +0.00 | 2 |
| general-critic | +0.00 | 1 |
| deep-research | +0.00 | 1 |
| crafting-skills | +0.00 | 2 |
| plan-lifecycle | +0.00 | 1 |
| task-lifecycle | +0.00 | 1 |
| web-search | +0.00 | 1 |
| rust | +0.00 | 1 |

## Per-eval results

| Eval | Expected | IF Δ | GC Δ | Overall Δ | Verdict |
|------|----------|-----:|-----:|----------:|---------|
| lint-1 | marketplace-validator |  +0.0 | +50.0 | +25.0 | skill_lifts_quality |
| lint-2 | marketplace-validator |  +0.0 |  +0.0 |  +0.0 | skill_neutral |
| audit-1 | marketplace-health | +40.0 |  +0.0 | +16.5 | skill_lifts_quality |
| audit-2 | marketplace-health |  +0.0 |  +0.0 |  +0.0 | skill_neutral |
| ingest-1 | ingesting-skills |  +0.0 |  +0.0 |  +0.0 | skill_neutral |
| ingest-2 | ingesting-skills |  +0.0 |  +0.0 |  +0.0 | skill_neutral |
| release-1 | releasing-marketplace |  +0.0 |  +0.0 |  +0.0 | skill_neutral |
| release-2 | releasing-marketplace | +30.0 |  +0.0 | +15.0 | skill_lifts_quality |
| critic | general-critic |  +0.0 |  +0.0 |  +0.0 | skill_neutral |
| research | deep-research |  +0.0 |  +0.0 |  +0.0 | skill_neutral |
| craft-create | crafting-skills |  +0.0 |  +0.0 |  +0.0 | skill_neutral |
| craft-review | crafting-skills |  +0.0 |  +0.0 |  +0.0 | skill_neutral |
| eval-skill | evaluating-skills | +30.0 |  +0.0 | +15.0 | skill_lifts_quality |
| plan-multi | plan-lifecycle |  +0.0 |  +0.0 |  +0.0 | skill_neutral |
| task-small | task-lifecycle |  +0.0 |  +0.0 |  +0.0 | skill_neutral |
| web-rust | web-search |  +0.0 |  +0.0 |  +0.0 | skill_neutral |
| sec-audit | security | +35.0 |  +0.0 | +17.5 | skill_lifts_quality |
| rust-clippy | rust |  +0.0 |  +0.0 |  +0.0 | skill_neutral |
