# Why this fork — `plan-lifecycle`

`plan-lifecycle` uses `context: fork` to run PLAN and EXECUTE modes in an isolated subagent. This file justifies the fork flag .

## Isolation value

Multi-phase project planning reads every referenced file in the plan (specs, ROADMAP.md, PLAN.md, source files cited as dependencies). Running this inline would flood the user's main conversation with file contents they won't reference again. The fork absorbs that exploration; the user's session gets back a structured PLAN.md or execution report.

In EXECUTE mode, the fork runs a phase-by-phase implementation loop with milestone critique. The intermediate tool output (file reads, verification runs, critic findings) is verbose — exactly the noise the fork exists to contain. The user gets back the execution report and any deviation log; the noisy intermediate work stays in the fork's disposable context.

## What the fork inherits

- The user's literal `$ARGUMENTS` (mode + plan path or phase flag)
- Its own frontmatter + body (the skill content becomes the task prompt)
- No main-conversation history — the forked subagent starts fresh

## What the fork does NOT inherit

- The user's earlier conversation (prior requests, decisions, context)
- Skills loaded in the parent session (the fork gets only what its frontmatter preloads)
- The parent's accumulated state about the project

## Post-fork return

- **PLAN mode:** a `PLAN.md` and `ROADMAP.md` written to `docs/principled/plans/`
- **EXECUTE mode:** an execution report at `docs/principled/plans/{plan-name}/execution-report.md` with task outcomes, critic findings, and a deviation log

## Why the fork is not for inner parallelism

Pre-1.23.0, EXECUTE mode spawned parallel worker subagents (`a subagent generalist` × N). Post-1.23.0, the orchestrator implements inline within the fork and spawns only a subagent generalist for isolated milestone review. The parallelism that mattered most (multiple critics reviewing the same milestone from different angles) is preserved; the parallelism that didn't (N implementations of the same code) was removed. The fork's value is outer isolation of a long reasoning chain, not inner parallelism.