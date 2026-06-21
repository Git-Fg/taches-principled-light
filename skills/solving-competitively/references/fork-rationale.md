# Why this fork — `sadd`

`sadd` (Structured Agent-Driven Development) uses `context: fork` to run EXECUTE and JUDGE modes in an isolated subagent. This file justifies the fork flag .

## Isolation value

SADD does competitive evaluation — generating a candidate solution and scoring it with multiple independent judges from different angles. The intermediate work is:
- **EXECUTE:** implementing the candidate with self-critique and verification retry loops. Tool output (build logs, test results, reviewer findings) is verbose.
- **JUDGE:** running 1-3 a subagent generalist instances in parallel, each scoring the candidate against a rubric. Each judge's verdict is independent reasoning that should not pollute the others.

Running all this inline would flood the user's session with the candidate implementation attempts, the verification runs, and each judge's reasoning. The fork absorbs that; the user gets back the chosen candidate (EXECUTE) or the verdict report (JUDGE).

The fork's isolation is *especially* valuable for SADD because **the judges must be independent.** A judge that has seen the orchestrator's implementation biases isn't a true second opinion. Each a subagent generalist runs in its own isolated context; the fork coordinates them without leaking the orchestrator's reasoning into any one judge.

## What the fork inherits

- The user's literal `$ARGUMENTS` (problem statement + mode)
- Its own frontmatter + body
- Any `docs/principled/sadd/{task-id}/` artifacts from prior runs

## What the fork does NOT inherit

- The user's earlier conversation
- Skills loaded in the parent session (the fork gets only what its frontmatter preloads)

## Post-fork return

- **EXECUTE:** task output at `docs/principled/sadd/{task-id}/output/` with verification history
- **JUDGE:** an evaluation report at `docs/principled/sadd/{eval-id}/verdict.md` with per-criterion scores, evidence, and verdict

## Why the fork is not for inner parallelism

Pre-1.23.0, COMPETE mode spawned 3 parallel `sadd-generator` instances to produce 3 candidates simultaneously, then 6 a subagent generalist instances to score them. Post-1.23.0, the orchestrator generates one candidate inline within the fork; the parallelism that's preserved is the multi-judge review (N a subagent generalist instances scoring one candidate from different angles). The parallel-implementation advantage was dropped; the multi-judge isolation benefit — the real value of competitive evaluation — is preserved. The fork's value is outer isolation of the generate-then-judge loop, not inner parallel generation.