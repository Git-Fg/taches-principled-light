# Implementation Patterns

## Pattern A: Simple Step (No Verification)

Used for: directory creation, configuration changes, deletions, and other straightforward operations.

**Spawn an implementation subagent:**
- Execute ONLY the specific step
- Follow Expected Output and Success Criteria exactly
- Report files created/modified, confirmation, any issues

## Pattern B: Critical Step (Panel of 1 or 2 Judges)

Used for: artifacts requiring evaluation confidence. Single judge for non-critical, panel of 2 for critical.

**Flow:**
1. Spawn implementation subagent
2. Spawn judge subagent(s) after completion
3. Loop implementation until judge finds no HIGH findings

## Pattern C: Multi-Item Step (Per-Item Judges)

Used for: steps creating multiple similar items (validators, handlers, endpoints, test cases).

**Flow:**
1. Spawn implementation subagents in parallel (one per item)
2. Spawn evaluation subagents in parallel (one per item)
3. On any FAIL: re-implement only failing items
4. Loop until ALL pass or MAX_ITERATIONS reached

## Panel Voting Algorithm

1. **Collect**: table with each criterion and both judge scores
2. **Median**: average of both scores per criterion
3. **High variance check**: if |score1 - score2| > 2.0, flag for potential disagreement
4. **Weighted overall**: sum(median x weight) for all criteria
5. **Pass/fail**: overall >= threshold

If high variance is detected: present both evaluators' reasoning to the user and ask for resolution.

## Evaluation Integrity Rules

- **Score 5.0/5.0 is a hallucination** - reject and re-run the judge
- **Missing numerical score** - reject and re-run the judge
- **Excessively long reports** - reject and re-run the judge
- **Use thresholds from configuration**, not hardcoded values
- **Chain-of-thought required**: judges must provide justification BEFORE the score