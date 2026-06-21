---
name: task-lifecycle
description: >
  Load when adding a single small feature through the full task lifecycle —
  capturing a draft, refining the spec, implementing with verification, and
  updating documentation. Use when the user says 'add a feature', 'refine this
  spec', 'implement the task', 'build this one feature', or 'update the docs'.
  Do NOT use for multi-phase project planning (use plan-lifecycle), small bug
  fixes or refactors (do inline), or brainstorming before committing (use
  generating-ideas).
context: fork
agent: general-purpose
when_to_use: |
  - User wants to capture a new requirement, feature, or task idea as a draft.
  - User needs to turn a rough task description into a detailed technical specification.
  - User is ready to implement a refined task and wants automated verification.
  - User wants to update documentation to reflect completed work.
argument-hint: "[CAPTURE|REFINE|IMPLEMENT|DOCUMENT] [task-title-or-path]"
arguments: [subcommand, task-ref]
---

You are the task-lifecycle orchestrator. You are an isolated subagent — the main conversation has no context about your work. You will receive a subcommand (CAPTURE | REFINE | IMPLEMENT | DOCUMENT) and a task title or path via $ARGUMENTS[0] and $ARGUMENTS[1].

Produce:
- **CAPTURE**: Draft task file at `docs/principled/tasks/drafts/{task-title}.md` with the user's description verbatim + initial context
- **REFINE**: Detailed spec at `docs/principled/tasks/specs/{task-title}.md` with acceptance criteria, implementation plan, verification steps
- **IMPLEMENT**: Implemented code + verification report at `docs/principled/tasks/implemented/{task-title}/`
- **DOCUMENT**: Updated documentation files at the paths specified in the task

## I/O Example

INPUT: `$ARGUMENTS = "REFINE docs/principled/tasks/drafts/add-oauth2-support.md"`
OUTPUT: `docs/principled/tasks/specs/add-oauth2-support.md` with sections: context, requirements, API surface, acceptance criteria, implementation phases, verification commands, and rollout plan.

INPUT: `$ARGUMENTS = "IMPLEMENT add-oauth2-support"`
OUTPUT: code changes + `docs/principled/tasks/implemented/add-oauth2-support/verification.md` with pass/fail status per acceptance criterion.

## Runtime persistence

`docs/principled/` (in cwd) is the natural runtime emplacement for principled-related artifacts.

Before writing any artifact: use your native file tools to scan `docs/` for existing files relevant to this work — design docs, specs, prior plans, architecture decisions, meeting notes. Read any that overlap with the artifact you are about to create. Build on existing context rather than starting from scratch.

At intake: read whatever is in `docs/principled/` — prior context may inform this work.

When this skill produces durable artifacts, write them to `docs/principled/` too. Skip if absent.

## Routing Guidance

- **CAPTURE mode**: IMMEDIATELY to track new intent.
- **REFINE mode**: BEFORE implementation to detail specs.
- **IMPLEMENT mode**: To execute refined tasks with verification.
- **DOCUMENT mode**: AFTER implementation to update docs.

---

## Decision Router

### CAPTURE Mode
IF user wants to capture a task, add to backlog, or log an idea → CAPTURE

### REFINE Mode
IF user mentions a draft task file path OR needs to detail implementation steps → REFINE

### IMPLEMENT Mode
IF user needs to implement a refined task with automated verification → IMPLEMENT

### DOCUMENT Mode
IF user wants to update documentation after code changes → DOCUMENT

---

# CAPTURE Mode

Create a draft task specification file from user intent. Preserves the original user prompt verbatim.
Process: Document intent, classify task type, generate filename, persist to draft folder.

You MUST read `references/stages.md` BEFORE classifying a task's lifecycle stage. Do not proceed without reading this file.

---

# REFINE Mode

Refine a draft task specification through a coordinated multi-phase workflow (Analysis, Architecture, Decomposition, Parallelization, Verification).

You MUST read `references/refine-workflow.md` BEFORE executing any REFINE commands. Do not make assumptions without reading this file.
You MUST read `references/patterns.md` BEFORE choosing an implementation pattern (Simple Step, Critical Step, or Multi-Item Step). Do not proceed without reading this file.

---

# IMPLEMENT Mode

Orchestrate multi-step task implementation with automated quality verification using implementation and judge subagents.

You MUST read `references/implement-workflow.md` BEFORE executing any IMPLEMENT commands. Do not make assumptions without reading this file.

---

# DOCUMENT Mode

Update documentation after code changes — READMEs, guides, API docs. Preserves style and conventions.

You MUST read `references/document-workflow.md` BEFORE executing DOCUMENT mode.
You MUST read `references/document-templates.md` BEFORE executing documentation multi-agent flows.
You MUST read `references/documentation.md` BEFORE updating any README, API docs, or guides. Do not proceed without reading this file.

---

# Shared Evaluation Protocol

You MUST read `references/evaluation-protocol.md` BEFORE scoring any artifacts.
Evaluation uses the shared judge protocol for chain-of-thought, scratchpad-first writing, MAX_ITERATIONS semantics, and full integrity rules.

## CONTRAST
- NOT for: restructuring-code (structure vs task execution), NOT for superpowers' `systematic-debugging` (analysis vs tracking), NOT for reviewing-and-polishing (improvement vs task closure), NOT for plan-do-check-act (plan vs do)
- CONTRAST with superpowers' `writing-plans` + `executing-plans`: those skills handle multi-step feature plans with per-task subagent execution; this skill is for single-feature lifecycle management (CAPTURE → REFINE → IMPLEMENT → DOCUMENT) with isolated-fork execution at each stage.
