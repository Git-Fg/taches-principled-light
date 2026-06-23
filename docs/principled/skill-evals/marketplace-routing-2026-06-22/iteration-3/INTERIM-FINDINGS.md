# Iter-3 Interim Findings (5/18 evals complete)

## Verdict distribution (so far)

| Verdict | Count | Notes |
|---|---|---|
| `skill_lifts_quality` | 1 | lint-1 only (+45.0pp) |
| `skill_neutral` | 2 | audit-1 (+4.1pp), audit-2 (0.0pp) |
| `skill_hurts` | 2 | ingest-1 (-15.0pp), lint-2 (-20.0pp) |

## Why `skill_hurts` is the most important signal

The two `skill_hurts` findings (with-skill underperforms without-skill) are
**invisible to iter-2's read-counting metric** but surfaced by iter-3's
assertion-based grading. This validates the entire iter-3 design rationale.

### Possible causes (ordered by likelihood)

1. **Assertion over-calibration**: the with-skill agent followed the skill's
   documented workflow, but the workflow was inappropriate for the actual
   test case. The agent "succeeded" by the skill's rubric but failed the
   user's underlying intent.
2. **Judge model bias (self-attribution)**: with-skill and without-skill
   both run on `haiku`; the judge also runs on `haiku` (per current
   default). Per the Lee et al. (2026) bias analysis, this can produce
   direction-dependent bias. With-skill outputs may LOOK more
   skill-compliant (verbose, structured) but the judge, sharing
   the solver's biases, may actually score them lower on quality
   criteria. Need calibration against `sonnet` or `glm-5.2` to disambiguate.
3. **Single-trial noise**: per Yagubyan (2026), single-trial flip rate is
   13.6%. The -15pp and -20pp deltas could partially be noise.
4. **Skill content drift**: the marketplace-validator / ingesting-skills
   SKILL.md may encode outdated or overly-prescriptive guidance.

### Recommended next steps

- Wait for full 18-eval run (~60-90 min from launch)
- Re-run the 2 `skill_hurts` evals with `--judge-model sonnet` (or `glm-5.2`)
  to test cause #2 (judge bias)
- Manually inspect 1 transcript from each verdict bucket (`lifts`, `neutral`,
  `hurts`) to look for cause #1 (assertion over-calibration)
- If cause #1 confirmed, the 2 affected skills need description rewrites
  to be less prescriptive (or the assertions need to be relaxed)

## Why this interim note exists

The full 18-eval run is in progress (background task). This note captures
the partial state in case the run is interrupted, so the partial findings
are not lost.
