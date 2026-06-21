# ADJUDICATE Mode Protocol

*Validates cross-analyze findings against evidence with adversarial challenge.*

## When to Use

After CROSS-ANALYZE has produced findings. Validates each finding against evidence and runs adversarial challenge.

## Input

Findings from CROSS-ANALYZE output (passed as file path argument or previous session-inspect output).

## Execution

**Phase 1 — Collect findings:**
- Read cross-analyze output from `docs/principled/scratch/` or receive as file path argument

**Phase 2 — Parallel validation per finding:**

For each finding, spawn two agents concurrently with `background: true`:
- **a subagent explorer** (scope: "cross-reference this finding with the JSONL artifact; find direct supporting AND contradicting evidence") ← finding + JSONL artifact → "evidence supports" or "L1-speculative"
- **a subagent generalist** ← finding → try to refute it (refuted=true if uncertain)

Spawn all evidence-validators and all adversarial challengers concurrently.

**Phase 3 — Await all results:**
- Use `TaskOutput` with `block: true` for all concurrent tasks

**Phase 4 — Classify each finding:**

| Evidence Check | Adversarial Check | Classification |
|---|---|---|
| "supports" | "not_refuted" | **Validated** |
| "L1-speculative" OR "no-evidence" | — | **Speculative** |
| — | "refuted" | **Speculative** |
| "no-evidence" | "refuted" | **Rejected** |

**Phase 5 — Report:**

```json
{
  "status": "complete",
  "mode": "adjudicate",
  "findings": [
    {
      "finding": "<text>",
      "classification": "validated|speculative|rejected",
      "evidence_check": "supports|L1-speculative|no-evidence",
      "adversarial_check": "not_refuted|refuted",
      "reason": "<explanation>"
    }
  ],
  "summary": { "validated": N, "speculative": M, "rejected": K }
}
```

## Fallback Agents

- If the first-pass exploration is too narrow, re-spawn a subagent explorer with a broader scope
- If a subagent generalist is not available → use a subagent generalist (lens "try to refute this finding; refuted=true if uncertain") as fallback adversarial agent

## Evidence Validation Procedure

The a subagent explorer subagent:
1. Reads the finding text
2. Reads the associated JSONL artifact
3. Searches for direct evidence supporting the claim
4. Searches for evidence contradicting the claim
5. Returns: "supports" (direct evidence found), "L1-speculative" (circumstantial only), or "no-evidence" (none found)

## Adversarial Challenge Procedure

The a subagent generalist agent:
1. Reads the finding text
2. Actively seeks reasons the finding might be wrong, misattributed, or overstated
3. Returns: "not_refuted" (no strong counter-evidence found) or "refuted" (significant doubt cast)
4. **Note:** "refuted=true if uncertain" — the threshold favors skepticism

## Convergence with Cross-Analyze

Adjudicate runs after CROSS-ANALYZE. High-convergence findings from cross-analyze (≥2 analysts agreed) are most likely to be validated. Low-convergence findings (single analyst) frequently become "rejected" or "speculative" under adversarial challenge.