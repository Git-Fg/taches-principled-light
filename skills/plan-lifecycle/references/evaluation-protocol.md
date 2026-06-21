# Evaluation Protocol

Shared judge/critic evaluation protocol used by `plan-lifecycle EXECUTE mode` and `task-lifecycle`. Any skill that runs independent quality evaluation MUST follow these rules. The skill that invokes the judge defines its own scoring scale, threshold, and trigger conditions — this document covers the rules common to all.

## Independent Judge Subagent

The judge is a separate subagent with no connection to the implementation agent that produced the artifact. Spawn it after the artifact is written to disk, never inline.

**Why:** Confirmation bias is real. The same agent that wrote the code will rationalize its own choices. An independent subagent with fresh context catches blind spots and prevents the executor from grading its own homework.

## Scratchpad-First Writing

The judge writes findings to disk before returning. The orchestrator reads findings from the scratchpad — never from the subagent's verbal summary.

**Why:** Subagent output text is a lossy summary. Reading the scratchpad directly gives the orchestrator ground truth and prevents telephone-game degradation as findings are passed up the chain.

## Chain-of-Thought Required

When scoring, the judge must provide written justification BEFORE the numerical score for each criterion. Reasoning first, conclusion second.

**Why:** Without explicit reasoning, judges anchor on the final score and produce post-hoc rationalization. Chain-of-thought forces the judge to confront the evidence before committing to a verdict, producing more accurate and defensible scores.

## Scoring Scale (Numeric Variant)

When the skill uses numeric scoring (task-lifecycle REFINE and IMPLEMENT modes):

| Score | Label | Meaning |
|-------|-------|---------|
| 1 | Poor | Missing essential elements, fundamental misunderstanding |
| 2 | Below Average | Some correct elements, significant gaps |
| 3 | Adequate | Meets basic requirements, functional but minimal |
| 4 | Good | Meets all requirements, few minor issues |
| 5 | Excellent | Exceptional quality, exceeds expectations |

When the skill uses qualitative judging (plan-lifecycle EXECUTE mode critic), the labels are `HIGH` / `MEDIUM` / `LOW` findings instead of numeric scores — but chain-of-thought and the integrity rules below still apply.

## Weighted Rubric

Each rubric has 3-6 criteria. Weights MUST sum to 1.0. The overall score is the weighted sum: `sum(score_i * weight_i)` for all criteria.

**Why:** Unweighted rubrics let weak criteria hide strong ones, or vice versa. Explicit weights force the rubric author to declare relative importance, and the weighted sum produces a single defensible overall score.

## Score Integrity Rules

Reject the judge's output and re-run it when any of these conditions are true:

- **5.0/5.0 score** — perfect scores are practically impossible in rigorous evaluation; treat as hallucination
- **Missing numerical score** — every criterion must have a score
- **Excessively long reports** — output that ignores the structured format produces noise; reject
- **No chain-of-thought before score** — judgment must precede verdict

**Why:** These are the failure modes most likely to slip past the orchestrator. A 5.0/5.0 is the canonical hallucination signature — judges over-confident about their own work produce uniform high scores. Missing scores mean the judge didn't actually evaluate.

## MAX_ITERATIONS Cap

Default cap: **3 fix-to-verify cycles** per phase/step. After MAX_ITERATIONS, proceed to the next phase/step regardless of score and log a warning.

The implementation agent retries with the judge's feedback incorporated into the spawn prompt. The judge then re-evaluates the new artifact. Loop until PASS or MAX_ITERATIONS.

**Why:** A single judge review creates false confidence — the judge might miss issues in the first pass, or the fix might introduce new problems. The loop structure produces diminishing returns naturally: most issues are caught in round 1, edge cases in round 2, and round 3+ catches are noise. The cap preserves throughput.

## Threshold Resolution

Use the configured THRESHOLD value. Never hardcode a threshold. The configuration flag (e.g., `--target-quality`) is the single source of truth.

**Why:** Hardcoded thresholds become invisible invariants that drift across skills. A single configured value lets the user tune quality vs. speed without rewriting skill bodies.

**Default thresholds per skill:**

| Skill | Default | Critical Override |
|-------|---------|-------------------|
| task-lifecycle REFINE mode | 3.5/5.0 | n/a |
| task-lifecycle IMPLEMENT mode | 4.0/5.0 | 4.5/5.0 for critical steps |
| plan-lifecycle EXECUTE mode | n/a (qualitative HIGH-finding critic) | n/a |

## Retry Flow

```
Phase Implementation Agent
  → Judge Evaluation
    → PASS (score >= THRESHOLD) → Next Phase
    → FAIL (score < THRESHOLD)
      → Re-implement with judge feedback
        → Judge Evaluation
          → PASS → Next Phase
          → FAIL → Re-implement (up to MAX_ITERATIONS)
            → MAX_ITERATIONS reached → Next Phase (with warning)
```

If a human-in-the-loop phase is configured, trigger the human checkpoint after re-implementation but before the next judge retry — the user may have context that prioritizes which feedback to address.

## Judge Output Format

The judge returns structured output:

1. **Per-criterion chain-of-thought + score** (one block per criterion, reasoning first)
2. **Weighted overall score** (sum of score × weight)
3. **PASS / FAIL verdict** (overall >= threshold)
4. **Specific improvements on FAIL** — actionable items the implementation agent can address

Excessively long output that buries these four sections in prose is itself a rejection signal.

## Per-Skill Variants

Skills that consume this protocol MAY specialize the trigger conditions, scoring scale, and aggregation:

- **plan-lifecycle EXECUTE mode** — qualitative critic. Looks for HIGH findings (correctness, edge cases, regressions, deviation handling). Loop ends when no HIGH findings remain. No numeric scoring, no weighted rubric, but integrity rules (chain-of-thought, scratchpad-first, MAX_ITERATIONS) still apply.
- **task-lifecycle REFINE mode** — single judge per phase, 1-5 weighted rubric, threshold 3.5.
- **task-lifecycle IMPLEMENT mode** — single judge or panel of 2 judges per step. Panel uses median voting with high-variance check (|score1 - score2| > 2.0 → flag for user resolution). 1-5 weighted rubric, threshold 4.0 (standard) or 4.5 (critical).

When a skill uses this protocol, the skill body defines the variant; this document covers the invariant rules.
