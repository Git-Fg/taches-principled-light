# Why this fork — `task-lifecycle`

`task-lifecycle` uses `context: fork` to run the 4-stage task lifecycle (CAPTURE → REFINE → IMPLEMENT → DOCUMENT) in an isolated subagent. This file justifies the fork flag .

## Isolation value

Each stage of the lifecycle produces verbose intermediate output:
- **CAPTURE** drafts a task idea, often reading prior context
- **REFINE** turns a rough description into a detailed technical spec — iterating over multiple candidate approaches
- **IMPLEMENT** writes code with verification runs (test output, build logs, lint findings)
- **DOCUMENT** generates documentation from the completed work

Running all four inline would flood the user's session with the intermediate drafts, verification runs, and generated prose. The fork absorbs that work; the user gets back the final spec, the implemented code, or the documentation — not the noisy journey through each stage.

## What the fork inherits

- The user's literal `$ARGUMENTS` (subcommand + task title or spec path)
- Its own frontmatter + body

## What the fork does NOT inherit

- The user's earlier conversation
- Skills loaded in the parent session (the fork gets only what its frontmatter preloads)

## Post-fork return

- **CAPTURE:** a draft spec at `docs/principled/specs/<task-id>.draft.md`
- **REFINE:** a refined spec at `docs/principled/specs/<task-id>.spec.md`
- **IMPLEMENT:** the implemented code + verification results
- **DOCUMENT:** documentation reflecting the completed work

## Why the fork is not for inner parallelism

Pre-1.23.0, each stage spawned its own specialist subagent. Post-1.23.0, the orchestrator runs each stage inline within the fork and spawns only a subagent generalist for review at stage boundaries. The fork's value is the isolation of the 4-stage pipeline's intermediate output from the user's session, not inner-stage parallelism.