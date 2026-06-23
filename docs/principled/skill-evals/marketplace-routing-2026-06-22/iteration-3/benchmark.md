# Iteration 3 — Assertion-Based Skill Grading (N=2)

## Configuration
- Judge model: `haiku`
- Solver model: haiku (project convention)
- Lift threshold: ±5pp for skill_neutral

## Summary
- Evals: 2
- Mean IF delta: +25.00
- Mean GC delta: +25.00
- Mean overall delta: +24.55

### Verdict distribution
- `skill_lifts_quality`: 1/2
- `skill_neutral`: 1/2

### Per-skill mean overall delta

| Skill | Mean Δ | Evals |
|-------|-------:|------:|
| marketplace-validator | +45.00 | 1 |
| marketplace-health | +4.10 | 1 |

## Per-eval results

| Eval | Expected | IF Δ | GC Δ | Overall Δ | Verdict |
|------|----------|-----:|-----:|----------:|---------|
| lint-1 | marketplace-validator | +40.0 | +50.0 | +45.0 | skill_lifts_quality |
| audit-1 | marketplace-health | +10.0 |  +0.0 |  +4.1 | skill_neutral |

## Methodology

- Tessl-style per-category 0-100 scoring (IF + GC, weighted 50/50 by default)
- Two assertions per category minimum; some evals use weight overrides
- Code-based checks (consultation, structure with compare_args) bypass the LLM
- UNKNOWN verdicts (judge couldn't determine) are treated as FAIL for scoring
  but logged in `iteration-3/unknowns.md` for human review
