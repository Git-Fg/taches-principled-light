# Implement Workflow

Orchestrate multi-step task implementation with automated quality verification. Each implementation step spawns a dedicated subagent, then verified by an independent judge subagent. Supports three verification patterns plus final Definition of Done verification.

## Core Principle

Context is the orchestrator's most precious resource. Protecting it means delegating everything: implementations to developer agents, evaluations to judge agents. The orchestrator that reads artifacts stops being able to orchestrate.

## Configuration

### Argument Definitions

| Argument | Format | Default | Description |
|----------|--------|---------|-------------|
| `task-file` | Path or filename | Auto-detect | Task file to implement. Auto-select from todo/ or in-progress/ if omitted. |
| `--continue` | flag | false | Resume from last completed step. Launches judge to verify last incomplete step state. |
| `--refine` | flag | false | Detect git changes to project files, map to affected steps, re-verify from earliest affected. |
| `--human-in-the-loop` | `[step,step,...]` | None | Pause for human review after specified steps. |
| `--target-quality` | `X.X` or `X.X,Y.Y` | `4.0,4.5` | Single value sets both thresholds. Two comma-separated values set standard,critical separately. |
| `--max-iterations` | `N` or `unlimited` | `3` | Maximum fix-to-verify cycles per step. |
| `--skip-judges` | flag | false | Skip all verification — steps proceed directly without quality gates |

### Threshold Resolution

- Standard components threshold: default 4.0/5.0. Used for steps not marked as critical.
- Critical components threshold: default 4.5/5.0. Used for steps marked as critical.
- Single `--target-quality X.X` sets both thresholds to the same value.

### Usage Examples

```bash
# Implement a specific task
/task-lifecycle implement add-validation.feature.md

# Auto-select from todo/ or in-progress/
/task-lifecycle implement

# Continue from interruption
/task-lifecycle implement add-validation.feature.md --continue

# Human review after every step
/task-lifecycle implement add-validation.feature.md --human-in-the-loop
```

## Implementation Phases

### Phase 0: Select Task and Move to In-Progress

**Task Resolution**: search in order `in-progress/`, `todo/`, `done/`. If argument empty, auto-select single file.

**Continue Mode**: Detect `[DONE]` markers on step titles. Launch judge to verify last completed step state. Resume from next step if PASS, re-implement if FAIL.

**Refine Mode**: Detect git changes to project files. Map changed files to implementation steps via Expected Output and Verification sections.

### Phase 1: Load and Analyze Task

This is the ONLY phase where the orchestrator reads a file.

**Verification Level Classification**:
- No verification section → Pattern A (skip)
- Single Judge → Pattern B, 1 judge, standard threshold
- Panel of 2 Judges → Pattern B, 2 judges, critical threshold
- Per-Item Judges → Pattern C, 1 judge per item

Critical steps always use critical threshold regardless of verification level.

### Phase 2: Execute Implementation Steps

Execute steps in dependency order. Steps marked `Parallel with:` run simultaneously.

#### Verification Patterns

**Pattern A: Simple Step**
No verification needed. Spawn implementation agent, mark done, proceed.

**Pattern B: Single Item with Verification**
Implementation with 1-2 independent judges. Aggregation uses median. Iterate on FAIL.

**Pattern C: Multi-Item with Per-Item Judges**
1 judge per item, parallel execution. Iterate only failing items on FAIL.

#### Human-in-the-Loop Checkpoint

Triggered after a step PASSES if the step is in `HUMAN_IN_THE_LOOP_STEPS`. Present judge feedback and artifacts.

### Phase 3: Final Verification (Definition of Done)

After all steps complete, spawn DoD verification subagent to verify each checkbox item.

**On any FAIL**: Launch fix subagents for failing items, then re-verify. Iterate until all PASS.

### Phase 4: Route to DOCUMENT Mode

After DoD verification passes, route to DOCUMENT mode to update documentation for completed changes. This ensures docs reflect the implementation before committing.

### Phase 5: Move Task to Done

```bash
git mv docs/principled/specs/tasks/in-progress/<TASK_FILE> docs/principled/specs/tasks/done/
```

### Phase 6: Report

Generate implementation summary with step status, verification results, DoD verification, and documentation updates.
