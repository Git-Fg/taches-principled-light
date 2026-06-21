# Evaluation Protocol

Shared judge/critic evaluation protocol. Any skill that runs independent quality evaluation MUST follow these rules. The skill that invokes the judge defines its own scoring scale, threshold, and trigger conditions — this document covers the rules common to all.

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

Used by `task-lifecycle` REFINE and IMPLEMENT modes:

| Score | Label | Meaning |
|-------|-------|---------|
| 1 | Poor | Missing essential elements, fundamental misunderstanding |
| 2 | Below Average | Some correct elements, significant gaps |
| 3 | Adequate | Meets basic requirements, functional but minimal |
| 4 | Good | Meets all requirements, few minor issues |
| 5 | Excellent | Exceptional quality, exceeds expectations |

## Weighted Rubric

Each rubric has 3-6 criteria. Weights MUST sum to 1.0. The overall score is the weighted sum: `sum(score_i * weight_i)` for all criteria.

## Score Integrity Rules

Reject the judge's output and re-run it when any of these conditions are true:

- **5.0/5.0 score** — perfect scores are practically impossible in rigorous evaluation; treat as hallucination
- **Missing numerical score** — every criterion must have a score
- **Excessively long reports** — output that ignores the structured format produces noise; reject
- **No chain-of-thought before score** — judgment must precede verdict

## MAX_ITERATIONS Cap

Default cap: **3 fix-to-verify cycles** per phase/step. After MAX_ITERATIONS, proceed to the next phase/step regardless of score and log a warning.

## Threshold Resolution

Use the configured THRESHOLD value. Never hardcode a threshold. The configuration flag (e.g., `--target-quality`) is the single source of truth.

**Default thresholds:**
- REFINE mode: 3.5/5.0
- IMPLEMENT mode: 4.0/5.0 (standard) or 4.5/5.0 (critical)

## Panel Voting Algorithm (IMPLEMENT mode)

1. **Collect**: both judge scores per criterion
2. **Median**: average scores per criterion
3. **High variance check**: if |score1 - score2| > 2.0, flag for potential disagreement
4. **Weighted overall**: sum(median x weight) for all criteria
5. **Pass/fail**: overall >= threshold

If high variance detected: present both perspectives to user for resolution.

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

---

# Design Decisions

IF entering a refinement stage (research, analysis, decomposition, verification) → BEFORE acting read `references/stages.md`. Do not skip stage-specific guidance.

IF implementing a verified step → BEFORE writing code read `references/patterns.md`. Do not assume implementation patterns without reading this file.

### Separate draft and todo folders
Draft is for unrefined tasks; todo is for tasks ready to implement. The separation enforces refinement as a required step.

### Type as file extension
The file extension encodes the task type directly, making it visible in file listings and grep searches without opening the file.

### Parallel analysis before synthesis
Running research, codebase analysis, and business analysis in parallel is faster than sequential. This prevents the common failure mode of designing architecture without understanding business requirements or codebase constraints.

### Independent judges per phase
Separate judge subagents prevent confirmation bias. Independent judges provide objective quality signals and catch blind spots.

### Scratchpad-first methodology
All analysis goes to a scratchpad before the task file. This prevents premature commitment to unverified findings.

### Separate standard and critical thresholds
Using a higher threshold for critical paths (4.5 vs 4.0) focuses quality effort where it matters most.
