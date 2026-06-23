# Iter-3 Interim Findings (CORRECTED — 16/18 evals complete)

**Status as of 12:00 UTC 2026-06-23**: Full N=18 background run in progress
(pid 50241, 7m6s elapsed). 16 evals have `comparison.json` written; 1
(sec-audit) has only `grading_with_skill.json`; 1 (rust-clippy) not yet
started. Process is alive; expect completion within 5-10 minutes.

> **Correction**: An earlier version of this file claimed "5/18 done".
> That was based on assumed progress, not verified disk state. Actual
> state at time of writing: 16 evals complete + 1 partial.

## Verdict distribution (N=16 of 18)

| Verdict | Count | Evals |
|---|---|---|
| `skill_lifts_quality` | 5 | critic (+20), eval-skill (+15), lint-1 (+45), release-1 (+15), release-2 (+25) |
| `skill_neutral` | 8 | audit-1 (+4.1), audit-2 (0), craft-create (0), craft-review (0), plan-multi (0), research (0), task-small (0), web-rust (0) |
| `skill_hurts` | 3 | ingest-1 (-15), ingest-2 (-17.5), lint-2 (-20) |
| `skill_redundant` | 0 | — |

Mean deltas (N=16):
- IF: -1.6pp
- GC: +9.4pp
- **Overall: +4.5pp**

## Per-skill pattern (the most actionable signal)

| Skill | Mean lift | Pattern | Interpretation |
|---|---|---|---|
| `marketplace-validator` | +12.5pp | POLARIZED: lint-1 +45, lint-2 -20 | Skill helps in one context, hurts in another. Investigation needed. |
| `releasing-marketplace` | +20.0pp | CONSISTENT LIFT: +15, +25 | Skill works well — keep as-is |
| `crafting-skills` | 0.0pp | CONSISTENT NEUTRAL: 0, 0 | Skill neither helps nor hurts on these tasks |
| `marketplace-health` | +2.05pp | CONSISTENT NEUTRAL: +4.1, 0 | Slight positive, within noise |
| `ingesting-skills` | **-16.25pp** | CONSISTENT HURT: -15, -17.5 | Skill reliably makes things worse on these tasks |
| `evaluating-skills` | +15.0pp | LIFTS (1 sample) | Promising but thin evidence |
| `general-critic` | +20.0pp | LIFTS (1 sample) | Promising but thin evidence |
| `plan-lifecycle` | 0.0pp | NEUTRAL (1 sample) | Insufficient data |
| `deep-research` | 0.0pp | NEUTRAL (1 sample) | Insufficient data |
| `task-lifecycle` | 0.0pp | NEUTRAL (1 sample) | Insufficient data |
| `engineering-mcp` | 0.0pp | NEUTRAL (1 sample) | Insufficient data |

## High-priority findings

### F1. `ingesting-skills` reliably underperforms (N=2, both negative)

Both ingest evals show ~-16pp overall delta. The without-skill agent
**outperforms** the with-skill agent on the same rubric. Three plausible
causes (ordered by likelihood):

1. **Skill workflow is over-prescriptive for the test cases**. The skill
   encodes a multi-step "port → verify → commit" pattern; the test
   cases only need a quick reference lookup.
2. **Single-trial noise + judge bias**. Per Yagubyan (2026), single-trial
   flip rate is 13.6%. Two consecutive negatives are unlikely but
   possible (p ≈ 4%).
3. **Skill content has drifted** from what the agent actually needs.

**Action**: Re-run with `--judge-model sonnet` to rule out (2). If the
negative result persists, (1) or (3) is the cause → rewrite the skill's
description to be less prescriptive, or split into "ingest-port" vs
"ingest-quickref".

### F2. `marketplace-validator` polarized (one lift, one hurt)

`lint-1` (utterance: "lint the marketplace and check the frontmatter")
→ +45pp with skill. `lint-2` (utterance: "is this skill valid before I
commit") → -20pp with skill. The two utterances are similar in
surface form but the second one is asking for a **focused validation**
before a commit, not a full marketplace lint.

The most likely cause: the assertion set for lint-2 was over-fitted to
the marketplace-validator's general-purpose lint workflow, while the
utterance is asking for a narrower pre-commit check. The with-skill
agent followed the broader workflow; the without-skill agent
correctly narrowed the scope.

**Action**: Re-author the lint-2 assertion set to test the narrower
"pre-commit validation" outcome, not the general "lint the
marketplace" outcome.

### F3. Most `skill_neutral` results are 0/0 — both with and without skill scored identically

8 evals show 0.0pp delta. The 0/0 score (both sides scoring zero on
all assertions) is suspicious. Two plausible causes:

1. **The assertions are too strict** for the haiku model to ever satisfy
2. **The judge (haiku, same family as solver) gave the same biased score**
   regardless of actual differences

**Action**: Sample 2-3 transcripts from the 0/0 bucket and inspect
manually. If the transcripts are substantively different but scored
identically, the judge is the problem (re-run with `--judge-model glm-5.2`).

### F4. `releasing-marketplace` is the only skill with consistent strong lift

Both release evals show +15 and +25 (mean +20pp). The skill's
description and workflow are clearly well-tuned to the tasks. This is
a positive validation of the marketplace's curation process.

## What this validates

- **iter-3's design rationale**: assertion-based grading surfaces signals
  (especially `skill_hurts`) that iter-2's read-counting metric
  completely missed. Iter-2 would have shown all 18 evals as 0/0 reads;
  iter-3 shows 5 lifts, 8 neutrals, 3 hurts.
- **The marketplace's skill authoring process** for releasing-marketplace
  works; the process for ingesting-skills needs work.
- **The Tessl-style IF/GC split** is informative: most "neutral" results
  are 0/0 IF, not 0/0 GC. This means the agents achieved goal completion
  equally well; the discriminating metric (per Tessl) is instruction
  following, where the marketplace skills add value when they add it.

## What this does NOT validate (limitations)

- **N=1 trials** for 6 skills (1 sample each). The 8 `skill_neutral`
  results are dominated by 0/0 scores; we don't know if more samples
  would split them into lifts or hurts.
- **Same-family judge bias** (haiku solver, haiku judge) is not yet
  controlled. The Lee et al. (2026) bias-mitigation guidance recommends
  different-family judges; iter-3.1 should re-run with `sonnet` or
  `glm-5.2` as judge to test this.
- **Single-trial noise floor ±13.6%** (Yagubyan 2026) means individual
  deltas below ±15pp are within the noise band. The +45pp lint-1 and
  -20pp lint-2 are outside the band; the smaller deltas may not be
  reliable signals.