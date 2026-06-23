# iter-4 Unknowns Queue

UNKNOWN judge verdicts from iter-4. Per the `evaluating-skills` convention, `passed: null`
is mapped to `unknown: true` and treated as FAIL for scoring.

## 2026-06-23 — 1 UNKNOWN emitted

| Eval | Config | Assertion | Evidence | Disposition |
|------|--------|-----------|----------|-------------|
| research | with_skill | `surfaced_disagreement` | Truncated transcript (300s timeout, 57 events). No evidence to grade. | Treated as FAIL. `points_awarded: 0`. Logged for human review. |

**Note:** the 1 UNKNOWN is from a with_skill run that hit the 300s timeout. The corresponding
without_skill run for `research` also timed out (300s, 841 events), but the grader ran on the
4 deep-research invocations + 5-stage pipeline evidence already in the transcript and scored
32.5 (same as with_skill) — so no UNKNOWN was emitted for the without_skill side.

**Comparison to iter-3:** iter-3 reported "0 UNKNOWN verdicts emitted" in the 0.0.3 release
CHANGELOG. iter-4 emits 1, but the eval that emits it (research) was not in iter-3's N=17
set. The iter-3 set would have produced 0 UNKNOWNs if re-run with the same conditions.

## Resolution

No action needed for iter-4 release. The UNKNOWN did not affect the headline (research/with_skill
overall_score was 32.5, with 1 UNKNOWN counted as FAIL among 5 assertions = 2 passed / 3 failed
/ 1 unknown → overall 32.5 = 65 IF + 0 GC). The same eval was classified `skill_neutral` with
delta 0 because without_skill scored the same 32.5 on a partial transcript.

## Pattern

UNKNOWNs in iter-4 are correlated with timeouts. iter-3.1 fix (commit `b63b918`) writes
`timeout.json` on `subprocess.TimeoutExpired`, but does not change the grader's behavior —
the grader still runs on partial output. A future iter-5 enhancement could short-circuit
the grader when `timeout.json` is present and emit UNKNOWN for all assertions, making the
scoring rule explicit. (Currently: partial work scores; missing work does not.)
