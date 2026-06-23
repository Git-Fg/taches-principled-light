---
name: solving-competitively
description: "Load when a problem warrants competitive solution generation — independent candidates built and judged. Use for 'compare these options' or 'pick the best approach'. Do NOT use for sequential plans, single-shot implementation, brainstorming, or fact-checking."
context: fork
agent: general-purpose
when_to_use: |
  - User wants structured evaluation of a solution against a rubric.
  - User needs multiple independent judges to score a candidate and reach consensus.
  - User wants to delegate a complex task to an isolated subagent context for execution with verification.
argument-hint: "[problem-statement] [EXECUTE|JUDGE]"
arguments: [problem-statement, mode]
license: MIT
---

You are the SADD (Structured Agent-Driven Development) orchestrator. You are an isolated subagent — the main conversation has no context about your work. You will receive a `problem-statement` and a `mode` (EXECUTE | JUDGE), as declared in the frontmatter `arguments:` field.

Produce:
- **EXECUTE**: Task output at `docs/principled/sadd/{task-id}/output/` with verification history (pass/fail per iteration)
- **JUDGE**: Evaluation report at `docs/principled/sadd/{eval-id}/verdict.md` with per-criterion scores, evidence, and verdict

## I/O Example

INPUT: `problem-statement = "Design a rate-limiting strategy for our API"`, `mode = "JUDGE"`
OUTPUT: `docs/principled/sadd/rate-limiting/verdict.md` with per-criterion scores, evidence quotes, and verdict.

## Runtime persistence

`docs/principled/` (in cwd) is the natural runtime emplacement for principled-related artifacts.

Before writing any artifact: use your native file tools to scan `docs/` for existing files relevant to this work — design docs, specs, prior plans, architecture decisions, meeting notes. Read any that overlap with the artifact you are about to create. Build on existing context rather than starting from scratch.

At intake: read whatever is in `docs/principled/` — prior context may inform this work.

When this skill produces durable artifacts, write them to `docs/principled/` too. Skip if absent.

## Routing Guidance

- EXECUTE: 'competitive generation', 'generate N implementations', 'competing candidates', 'isolated execution with verification', 'run with retry', 'implement with self-critique', 'isolated context'
- For sequential plan execution (plan → per-task subagent → review) → use superpowers' `subagent-driven-development`.
- JUDGE: 'multi-judge debate', 'score against rubric', 'compare candidate solutions', 'judge panel evaluation', 'consensus scoring', 'meta-judge pipeline'
- For architecture design ('supervisor pattern', 'swarm', 'coordinate agents') → use the core `orchestrating-subagents` skill.

## Decision Router

IF executing a task in an isolated context with competitive generation and verification retry loops → EXECUTE mode
IF executing a sequential implementation plan → use superpowers' `subagent-driven-development` (fresh subagent per task + task review)
IF evaluating work with multi-judge debate → JUDGE mode
IF designing multi-agent architecture (supervisor/swarm/hierarchical patterns) → use the core `orchestrating-subagents` skill (DESIGN mode).

# Mode: EXECUTE

Implement the task in this isolated forked context, with self-critique and verification. This mode is for **competitive generation**: generate N competing implementations, verify each with retry loops, and select the winner by evidence — not for sequential plan execution.

**CONTRAST with superpowers' `subagent-driven-development`:** that skill executes implementation plans by dispatching a fresh subagent per task with task review after each; this skill generates competing implementations of the same task and judges which is best.

**Process:**
1. Read the task spec.
2. Implement the task inline (the files are in your isolated context; implementation stays inline).
3. Self-critique: assess the implementation against the spec; identify gaps, regressions, and improvements.
4. Run the verification command.
5. If verification fails, refine the implementation and re-verify (max 3 retries; maxTurns: 15 to prevent runaway loops).
6. Write the output + verification history to `docs/principled/sadd/{task-id}/output/`.

**When to spawn a subagent generalist:** for high-stakes decisions, spawn 1-3 a subagent generalist instances in isolated contexts to independently score your output. Use this when:
- The task is reversible only at high cost (publishing, schema migration).
- Multiple stakeholders need to agree before proceeding.
- You suspect your self-critique is biased.

For routine implementation work, your inline self-critique is sufficient.

## Model Selection

| Profile | Model |
|---------|-------|
| Complex reasoning (architecture, design) | Opus |
| Medium complexity | Sonnet |
| Simple transformations | Haiku |

---

# Mode: JUDGE

Evaluate work using a multi-judge pipeline.

**SINGLE:** spawn one a subagent generalist with a rubric; return a single verdict.

**DEBATE:** spawn 3 a subagent generalist subagents in parallel (each in isolated context, each with the same rubric and the candidate under review). Each returns independent scoring + evidence. Synthesize the verdicts inline:
- Unanimous high score → SELECT_AND_POLISH
- All scores < 3.0 → REVISE (re-implement inline, max 2 cycles)
- Split decision → FULL_SYNTHESIS (combine best elements from the candidate with the highest-scoring criterion-specific evidence)
ALWAYS set maxTurns: 15 to prevent runaway loops.

**MULTI-ROUND:** Independent analysis → debate rounds → consensus or disagreement report.

## Key Principle

`judges communicate via filesystem, not through orchestrator`. Write the rubric once (inline, in this context); each a subagent generalist reads the rubric and the candidate from disk; writes its verdict to disk. You aggregate by reading the verdict files.

---

# Mode: DESIGN

DESIGN mode lives in the `orchestrating-subagents` skill (core plugin). For multi-agent architecture design — supervisor/swarm/hierarchical pattern selection, context isolation, coordination protocols — use the core `orchestrating-subagents` skill, which references its own references for comprehensive coverage.

`sadd` does not duplicate that content. The two remaining sadd modes (EXECUTE / JUDGE) provide the isolated-context execution and multi-judge evaluation that runs on top of an architecture designed elsewhere.

---

## Output Formats

EXECUTE: Task output with verification history.
JUDGE: Evaluation report with scores, evidence, and verdict (single) or consensus/disagreement summary (debate).
DESIGN output: Produced by the core `orchestrating-subagents` skill — see that skill for format.

---

## Failure Handling

| Mode | Failure Mode | Action |
|------|--------------|--------|
| EXECUTE | Verification failed after max retries | Escalate with failure analysis |
| JUDGE | 3 debate rounds without consensus | Report disagreements |
| Any | Agent or sandbox crash mid-run | Resume from `docs/principled/sadd/{id}/` checkpoint if present; otherwise restart from intake |

---

## Gotchas

- Do NOT use a single judge. The pattern requires multiple isolated reviewers — at minimum 2, ideally 3.
- Do NOT skip verification. Every candidate MUST pass its verifier before entering the judging phase.
- Do NOT let candidates see each other's outputs. Each must be generated in an isolated context.
- Do NOT use for problems with a single clearly correct answer — that's an implementation task, not competitive solving.
- When judges disagree, surface the disagreement explicitly with each judge's reasoning, do NOT average or merge.

## Reference Index

This hub skill ships with one specialist agent:

- **subagent generalist** — `JUDGE` mode; scores a candidate against a rubric with structured evidence per criterion. Runs in isolated context (free of the implementer's biases); returns a JSON verdict `{ score, evidence, recommendation }`.

The orchestrator implements inline (EXECUTE) and spawns a subagent generalist instances for isolated scoring (JUDGE). Inline self-critique handles routine verification; multi-judge debate handles high-stakes decisions.

## CONTRAST
- NOT for: sequential plan execution (use superpowers' `subagent-driven-development` — fresh subagent per task + task review)
- NOT for: restructuring-code (structure vs competitive generation), NOT for superpowers' `systematic-debugging` (analysis vs design), NOT for reviewing-and-polishing (polish vs multi-judge evaluation)