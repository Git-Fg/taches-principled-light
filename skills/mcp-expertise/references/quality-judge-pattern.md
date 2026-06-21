# MCP Quality Judge Pattern: Parallel Evaluation with N Dimension Judges

Reference for the execution pattern that QUALITY mode uses to score an MCP server against the 8-dimension rubric. The pattern is a parallel-judge approach specialized for MCP servers. Read it before running a judge evaluation.

## §1. Why parallel judges, not sequential

A single judge evaluating all 8 dimensions will:
- Anchor on the first dimension (over-weight it)
- Skip dimensions that are hard to test ("looks fine, ship it")
- Mix up evaluation criteria across dimensions

**One judge per dimension, running in parallel**, forces independent evidence-gathering per dimension and produces a more reliable report. The trade-off is N× the agent spawn cost; in practice 8 parallel judges complete in roughly the time of 1 sequential judge (latency-bound, not compute-bound).

## §2. Judge contract

Each judge is a focused, single-dimension evaluator. The judge receives:

1. **The server artifacts** — the source code, the compiled binary (if available), the `.mcp.json` entry, the README
2. **The dimension to evaluate** — one of the 8 from `references/quality-rubric.md` §1
3. **The scoring rubric** — the EXEMPLARY/PASS/PARTIAL/FAIL scale with the specific evidence requirements for that dimension
4. **The output format** — a JSON object with `{ score, evidence, recommendation }`

Each judge returns:
```json
{
  "score": "PASS",
  "evidence": "Ran `claude mcp list` — server connects cleanly. Ran Inspector --cli --method tools/list — 5 tools returned, no JSON-RPC errors. The 5 tools are: read_file, write_file, list_dir, delete_file, search. All have descriptions and schemas.",
  "recommendation": "Ship it."
}
```

**Judges do NOT fix problems.** They score and recommend. Fixing is a separate downstream task routed to DESIGN/SCHEMA/IMPLEMENT mode after the report.

## §3. Spawning the judges

In QUALITY mode, the orchestrating agent (Claude itself, or a meta-judge) spawns 8 judges in parallel — one per dimension. Each judge is invoked as a subagent with a focused prompt:

```
You are Dimension 3 (Context Efficiency) judge for the MCP server at <path>.

Evaluate against the rubric in <expertise-hub>/references/quality-rubric.md §1.3.

Server artifacts:
- Source: <path-to-source>
- Compiled binary: <path-to-binary> (if available)
- .mcp.json entry: <the relevant config block>
- README: <path-to-readme>

Run the evidence-gathering commands (Inspector, claude mcp list, file measurements).
Score EXEMPLARY / PASS / PARTIAL / FAIL based on the rubric.
Return JSON: { "score": "...", "evidence": "...", "recommendation": "..." }
```

Repeat for dimensions 1, 2, 4, 5, 6, 7, 8 — all in parallel.

## §4. Aggregation and tiebreaks

After all 8 judges return:

1. **Tally scores** — count EXEMPLARYs, PASSes, PARTIALs, FAILs.
2. **Pass threshold check** — if any FAIL → fail. If more than 2 PARTIALs → fail.
3. **Tiebreak rule** — if two judges on the same dimension disagree by more than 1 tier (e.g., one says EXEMPLARY, another says PARTIAL), spawn a tiebreak judge for that dimension. The tiebreak judge sees both prior reports and renders the final call.
4. **Synthesize report** — write the markdown table.

## §5. Report format

The output is a single markdown report with this structure:

```markdown
# MCP Quality Evaluation: <server-name>

**Date:** <iso-date>
**Evaluator:** <orchestrator-id> (8 parallel judges)
**Verdict:** PASS / FAIL

## Summary

| Dimension | Score | One-line evidence |
|---|---|---|
| 1. Tool discovery | PASS | All 5 tools load on first try |
| 2. Single-shot accuracy | EXEMPLARY | 20/20 tests pass first attempt |
| 3. Context efficiency | PASS | 4.2 KB total, 850 B per tool |
| 4. Pass-through integrity | N/A | Server is stateless |
| 5. Session continuity | PASS | session_id round-trips across 3 tools |
| 6. Headless reliability | PASS | Inspector --cli works; stdin=/dev/null OK |
| 7. Error distinction | PARTIAL | Schema vs domain distinguished; internal errors collapse to -32603 |
| 8. Schema hygiene | EXEMPLARY | 100% compliance on all checks |

**Result:** 2 EXEMPLARYs, 5 PASSes, 1 PARTIAL, 0 FAILs, 1 N/A → **PASS** (with caveat on dimension 7)

## Findings

### FAIL (none)

(no findings)

### PARTIAL

**Dimension 7 — Error distinction**
- Evidence: Sent a `write_file` request to a nonexistent path; server returned `-32603 internal_error("path validation failed: ...")`. Should have returned a custom `-32001` (or a `PARTIAL-pass` `is_error: true` content result).
- Recommendation: Map the `path validation` category in `map_domain_error()` to a custom error code. See `references/implement-runtime.md` §error-mapping for the constructor shapes.

## EXEMPLARY dimensions

**Dimension 2 — Single-shot argument accuracy**
- 20/20 first-attempt success across: read_file(5 cases), write_file(5), list_dir(5), delete_file(3), search(2).

**Dimension 8 — Schema hygiene**
- 100% compliance: every object has `additionalProperties: false`, every property has a description, every required field is in `required`, all bounded choices use `enum`, `$schema` is explicit.
```

## §6. Where this pattern differs from generic code-judge

A generic code-judge pattern evaluates generated code for correctness, style, and adherence to specs. The MCP quality pattern is specialized:

- **Domain-specific rubric** — generic code-judges cover correctness, completeness, style. MCP quality judges are specialized for the 8 dimensions of the Claude-Optimal rubric. Each judge loads the dimension-specific evidence requirements from `quality-rubric.md`.
- **Live tool calls** — generic code-judges primarily read code. MCP quality judges run *live commands* (`claude mcp list`, Inspector, etc.) to gather evidence. They need network + filesystem + the MCP binary.
- **Schema-level and runtime-level checks** — generic code-judges are static-only. MCP quality mixes static (schema hygiene) and runtime (headless reliability, single-shot accuracy) checks.
- **No code-fix phase** — generic patterns may include a judge → fix → re-judge loop. MCP quality's judge produces a report; fixing is delegated to the user (who routes to DESIGN/SCHEMA/IMPLEMENT mode as needed).

## §7. Anti-patterns (judge pattern)

❌ **One judge evaluating all 8 dimensions** — collapses into the anchoring + skip-when-hard problem the pattern is designed to prevent.
❌ **Judges that suggest fixes inline** — judges score and recommend. The orchestrator routes the fix, not the judge.
❌ **Skipping the tiebreak on >1-tier disagreements** — a single judge's miscalibration can swing the verdict. Always tiebreak.
❌ **Re-using a judge from a previous evaluation** — judges should re-gather evidence each time. Servers change, schemas change, host versions change.
❌ **Reporting EXEMPLARY without a specific observation** — "I checked the schema and it's clean" is not evidence. "Ran `claude mcp list` — server connects; ran Inspector --cli --method tools/list — returned 5 tools with descriptions totaling 850 chars" is evidence.
