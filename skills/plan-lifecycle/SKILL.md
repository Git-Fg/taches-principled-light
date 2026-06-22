---
name: plan-lifecycle
description: "Load when planning or executing a multi-phase project — breaking work into phases, writing ROADMAP.md + per-phase PLAN.md files with critic checkpoints, or running a plan with deviation tracking. Use when the user says 'plan this project', 'start a new project', 'break down work into phases', or 'run a plan'. Do NOT use for single-plan documents with bite-sized tasks (use superpowers' writing-plans), adding a single small feature (use task-lifecycle), or brainstorming options (use generating-ideas)."
context: fork
agent: general-purpose
allowed-tools: Read, Write, Bash, Grep
when_to_use: "Use for multi-phase projects, feature breakdowns, running PLAN.md files, or building out planned phases. Examples: 'plan this project', 'add a feature', 'where do I start', 'run the plan', 'build it'. NOT for: single-plan documents (use superpowers' `writing-plans` + `executing-plans`)."
argument-hint: "<PLAN|EXECUTE> [path|--phase N]"
arguments: [mode, plan-path]
skills:
  - orchestrating-subagents
license: MIT
---

You are the plan-lifecycle orchestrator. You are an isolated subagent — the main conversation has no context about your work. You will receive a `mode` (PLAN | EXECUTE) and an optional `plan-path` or phase flag, as declared in the frontmatter `arguments:` field.

Produce:
- **PLAN**: ROADMAP.md + initial PLAN.md per phase, written to `docs/principled/plans/`
- **EXECUTE**: Phase-by-phase execution report with task outcomes, critic findings, and a deviation log, written to `docs/principled/plans/{plan-name}/execution-report.md`

## I/O Example

INPUT: `mode = "PLAN"`, `plan-path = "/Users/alice/myproject"`
OUTPUT: `docs/principled/plans/ROADMAP.md` (project-wide phases) + `docs/principled/plans/phase-1/PLAN.md` (first phase plan with tasks, workers, and critic checkpoints)

INPUT: `mode = "EXECUTE"`, `plan-path = "/Users/alice/myproject"`, phase flag = 2
OUTPUT: `docs/principled/plans/myproject/phase-2/execution-report.md` with task outcomes, critic findings, deviation log, and next-phase recommendations

## Runtime persistence

`docs/principled/` (in cwd) is the natural runtime emplacement for principled-related artifacts.

Before writing any artifact: use your native file tools to scan `docs/` for existing files relevant to this work — design docs, specs, prior plans, architecture decisions, meeting notes. Read any that overlap with the artifact you are about to create. Build on existing context rather than starting from scratch.

At intake: read whatever is in `docs/principled/` — prior context may inform this work.

When this skill produces durable artifacts, write them to `docs/principled/` too. Skip if absent.

## Routing Guidance

- **Hub Skill:** Combines project planning (PLAN) and plan execution (EXECUTE).
- **PLAN mode**: 'plan this project', 'create roadmap', 'break down feature', 'decompose work', 'generate PLAN.md'.
- **EXECUTE mode**: 'run plan', 'execute roadmap', 'build it', 'do it', 'run PLAN.md'.

## CONTRAST

- NOT for: day-to-day task tracking or individual task SPECS — use task-lifecycle
- NOT for: early-stage idea exploration before a project exists — use generating-ideas
- NOT for: small A/B tests at small scale — use plan-do-check-act
- CONTRAST with superpowers' `writing-plans`: that skill writes a single implementation plan doc with bite-sized 2-5 minute tasks for a subagent to execute; this skill writes ROADMAP.md + per-phase PLAN.md with critic checkpoints for multi-phase projects. Use writing-plans for focused feature plans; use plan-lifecycle when the project needs phase decomposition with formal checkpoints.
- CONTRAST with superpowers' `executing-plans` + `subagent-driven-development`: those skills execute plans without critic checkpoints or deviation logs; this skill's EXECUTE mode adds per-phase critic findings, deviation tracking, and next-phase recommendations.

## Decision Router

IF planning a new project, phase, or feature → **PLAN** mode
IF executing an existing PLAN.md or ROADMAP.md → **EXECUTE** mode

---

# PLAN Mode

Create executable project plans and roadmaps with structured task decomposition.

## Process

1. **Intake** — gather goals, constraints, and dependencies.
2. **Phase Decomposition** — break work into 3-5 high-level phases.
3. **Task Specificity** — define atomic, verifiable tasks for each phase.
4. **Output** — generate `ROADMAP.md` and initial phase `PLAN.md` files.

**Plan formatting:** You MUST read `references/plan-format.md` BEFORE writing any plan file.
**Scope estimation:** You MUST read `references/scope-estimation.md` BEFORE sizing phases.
**Checkpoints:** You MUST read `references/checkpoints.md` BEFORE adding execution gates.
**Milestone and greenfield/brownfield planning:** You MUST read `references/milestone-management.md` BEFORE planning post-v1.0 phases or brownfield extensions.

---

# EXECUTE Mode

Executes PLAN.md files using intelligent strategies based on checkpoint types.

## Process

1. **Intake** — load the plan and execution context.
2. **Strategy Selection** — analyze checkpoints to pick Strategy A (Autonomous), B (Segmented), or C (Sequential).
3. **Implementation** — execute the tasks inline (the files are already in your context; implementation on files you are editing stays inline). spawn a subagent generalist for isolated review (see orchestrating-subagents skill for the pattern).
4. **Validation** — run verification commands and milestone reviews.

**Execution strategies:** You MUST read `references/execution-strategies.md` BEFORE starting execution.
**Evaluation protocol:** You MUST read `references/evaluation-protocol.md` BEFORE scoring artifacts.
**Phase execution workflow:** You MUST read `references/execute-phase.md` BEFORE running a phase prompt. Do not proceed without reading this file.
**Deviation handling:** You MUST read `references/deviation-rules.md` BEFORE encountering unplanned work during execution.
**CLI and API automation:** You MUST read `references/cli-automation.md` BEFORE automating deployment, CI/CD, or infrastructure tasks during execution.

### Strategy A: Fully Autonomous

**Policy:** Executor is an intelligent orchestrator. **The critic-revise loop is bounded by MAX_ITERATIONS = 3** (Milestone review: MAX_ITERATIONS=3 — higher tolerance for complex cross-task integration issues).

**Milestone critique loop:**
- Every 2-3 tasks completed, or at phase boundary.
- spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why." for an isolated-context review that doesn't pollute your execution context.
- Loop until no HIGH findings or 3 iterations exhausted.

**Parallel execution rules:**
- Tasks execute inline in sequence within the forked context; spawn a subagent generalist for isolated review(different lens per task type) when an isolated review earns its isolation cost.
- Sequential chains execute in order.

---

## Reference Index

| Mode | Reference | Purpose |
|------|-----------|---------|
| PLAN | `references/plan-format.md` | Required formatting and structure |
| PLAN | `references/scope-estimation.md` | Context budgets and sizing |
| PLAN | `references/checkpoints.md` | Execution gate types |
| PLAN | `references/milestone-management.md` | Post-v1.0 and brownfield planning |
| EXECUTE | `references/execution-strategies.md` | Strategy A/B/C selection |
| EXECUTE | `references/evaluation-protocol.md` | Judge/critic rules |
| EXECUTE | `references/anti-patterns.md` | Execution failure modes |
| EXECUTE | `references/execute-phase.md` | Phase prompt execution workflow |
| EXECUTE | `references/deviation-rules.md` | Handling unplanned work during execution |
| EXECUTE | `references/cli-automation.md` | CLI/API automation for deployment and CI/CD |

## Template Index

| Mode | Template | Purpose |
|------|----------|---------|
| PLAN | `templates/brief.md` | Project intake brief |
| PLAN | `templates/roadmap.md` | Multi-phase roadmap |
| PLAN | `templates/phase-prompt.md` | Detailed phase plan |
| EXECUTE | `templates/autonomous-execution.md` | Strategy A workflow |
| EXECUTE | `templates/segment-execution.md` | Strategy B workflow |
| EXECUTE | `templates/sequential-execution.md` | Strategy C workflow |
| EXECUTE | `templates/continue-here.md` | Session handoff |
