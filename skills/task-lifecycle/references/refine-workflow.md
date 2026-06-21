# Refine Workflow

Refine a draft task specification through a coordinated multi-phase workflow. The workflow runs parallel analysis (research, codebase impact, business requirements), synthesizes findings into architecture, decomposes into implementation steps, reorganizes for parallel execution, and adds verification rubrics. Each phase includes an independent quality evaluation before the next phase proceeds.

## Core Principle

Specification quality is a prerequisite for implementation speed. Analysis, architecture, and verification before writing code reduces rework and produces measurably better outcomes.

## Configuration

### Argument Definitions

| Argument | Format | Default | Description |
|----------|--------|---------|-------------|
| `task-file` | Path | Required | Path to draft task file in `docs/principled/specs/tasks/draft/` |
| `--continue` | `[stage]` | None | Resume from a specific stage. Auto-detect from task file completion markers if omitted. |
| `--target-quality` | `X.X` | `3.5` | Minimum weighted score (out of 5.0) for judge pass/fail |
| `--max-iterations` | `N` | `3` | Maximum fix-to-verify cycles per phase |
| `--included-stages` | `stage1,...` | All | Comma-separated stages to include |
| `--skip` | `stage1,...` | None | Comma-separated stages to exclude |
| `--fast` | flag | N/A | Alias: `--target-quality 3.0 --max-iterations 1 --included-stages business analysis,decomposition,verifications` |
| `--one-shot` | flag | N/A | Alias: `--included-stages business analysis,decomposition --skip-judges` |
| `--human-in-the-loop` | `phase,...` | None | Pause for human review after specified phases |
| `--skip-judges` | flag | false | Skip all quality evaluations |
| `--refine` | flag | false | Incremental refinement: detect changes via git, re-run only affected stages |

### Stage Names

| Stage | Phase | Purpose |
|-------|-------|---------|
| `research` | 2a | Gather relevant resources, documentation, prior art |
| `codebase analysis` | 2b | Identify affected files, interfaces, integration points |
| `business analysis` | 2c | Refine description, create acceptance criteria |
| `architecture synthesis` | 3 | Synthesize research and analysis into architectural overview |
| `decomposition` | 4 | Break into implementation steps with success criteria and risks |
| `parallelize` | 5 | Reorganize steps for maximum parallel execution |
| `verifications` | 6 | Add evaluation rubrics for each implementation step |

### Usage Examples

```bash
# Full refinement with all stages
/task-lifecycle refine docs/principled/specs/tasks/draft/add-validation.feature.md

# Fast mode
/task-lifecycle refine docs/principled/specs/tasks/draft/quick-fix.bug.md --fast

# Continue from interruption
/task-lifecycle refine docs/principled/specs/tasks/draft/complex-api.feature.md --continue architecture synthesis

# Incremental refinement after edits
/task-lifecycle refine docs/principled/specs/tasks/todo/my-task.feature.md --refine
```

## Sub-Agent Dispatch

Every phase subagent must receive: scope (specific phase and task file path), context (prior artifact paths), artifact directive (scratchpad, update task, or new document), output format (structured report with file paths and findings).

**Spawn Footer**: Your context starts fresh — no access to prior conversation or other subagents' outputs. Return structured output (file paths, findings, artifacts) to the orchestrator. If you encounter anything unexpected or have any question or doubt, stop and report back. Do not proceed silently on assumptions.

**Failure Signal**: If unable to complete the task, return: `{"status": "failed", "reason": "...", "completed_portion": "...", "retry_possible": true/false}`

### Phase Agent Prompt Structure

```
Phase: [Phase Name]
Task File: <TASK_FILE>
Prior Artifacts: <paths to scratchpad/analysis files from prior phases>

Your task: <specific actions for this phase>

CRITICAL: Write findings to scratchpad first at docs/principled/specs/scratchpad/<unique-id>.md.
Only update the task file with validated conclusions.
Do NOT output your analysis inline — write everything to files.

Report: artifact paths created/updated, key findings summary, any issues.
```

### Judge Agent Prompt Structure

```
Evaluate artifact at: <artifact_path>

Role: <phase role>
Rubric: <criteria table>

Context: Task File <TASK_FILE>, Phase [Name]

Score each criterion 1-5. Provide chain-of-thought justification BEFORE each score.
Compute weighted overall. Return PASS/FAIL with specific improvements if FAIL.
```

## Phase Workflow

### Phase 2: Parallel Analysis

Launch three analysis sub-phases in parallel. Each phase uses a dedicated subagent and produces a scratchpad file plus task artifacts. Each phase has an independent judge evaluation.

**Synchronization Point**: Wait for ALL three phases AND their judges to pass before proceeding to Phase 3. If one phase finishes significantly before others, spawn its judge immediately rather than waiting.

### Phase 2a: Research

- Search for documentation, existing patterns, and libraries relevant to the task
- Identify common pitfalls, best practices, and reference implementations
- Create a reusable skill document with findings
- Write all research to scratchpad first, then create the skill document
- Do NOT output research results inline — write everything to files

**Artifacts**: Scratchpad at `docs/principled/specs/scratchpad/<hex-id>.md`, skill document at `.claude/skills/<topic>/SKILL.md`

**Evaluation dimensions (weight)**:
- Resource coverage (0.30): documentation and references gathered
- Pattern relevance (0.25): identified patterns are applicable and actionable
- Issue anticipation (0.20): common pitfalls identified with solutions
- Reusability (0.15): skill is general enough for multiple tasks
- Task integration (0.10): task file updated with skill reference

**On judge FAIL**: Re-launch with judge feedback incorporated. Do not proceed until PASS or MAX_ITERATIONS reached.

### Phase 2b: Codebase Impact Analysis

- Identify all files that will be modified, created, or deleted
- Document key functions, classes, and interfaces affected
- Map integration points and dependencies between components
- Assess risk level for each affected area with mitigations
- Write all analysis to scratchpad first, then create the analysis document

**Artifacts**: Scratchpad at `docs/principled/specs/scratchpad/<hex-id>.md`, analysis file at `docs/principled/specs/analysis/analysis-<name>.md`

**Evaluation dimensions (weight)**:
- File identification accuracy (0.35): all affected files identified with specific paths
- Interface documentation (0.25): key functions and classes documented with signatures
- Integration mapping (0.25): integration points identified with impact assessment
- Risk assessment (0.15): high-risk areas identified with mitigations

### Phase 2c: Business Analysis

- Use a scratchpad to capture the complete analysis process
- Do NOT accept surface-level descriptions at face value — probe for underlying intent
- Define scope boundaries (included, excluded, boundary cases)
- Extract core elements: actors, actions/behaviors, data entities, constraints
- Break requirements into functional and non-functional categories
- Verify testability: clear Given/When/Then, measurable outcomes
- Synthesize the refined description (2-3 paragraphs: what, why, who, constraints)
- Write validated conclusions to the task file: Description, Scope, User Scenarios, Acceptance Criteria

**Artifacts**: Scratchpad at `docs/principled/specs/scratchpad/<hex-id>.md`, updated task file with Description, Scope, User Scenarios, Acceptance Criteria sections

**Evaluation dimensions (weight)**:
- Description clarity (0.30): what/why clearly explained, scope boundaries defined
- Acceptance criteria quality (0.35): criteria are specific, testable, use Given/When/Then for complex cases
- Scenario coverage (0.20): primary flow documented, error scenarios considered
- Scope definition (0.15): in-scope/out-of-scope explicit, no implementation details in description

### Phase 3: Architecture Synthesis

Spawn after all Phase 2 phases and judges pass. Synthesize research, codebase analysis, and business requirements into an architectural overview.

- Read scratchpad and analysis files from Phase 2a, 2b, 2c
- Define the solution strategy and approach with reasoning
- Document key architectural decisions and trade-offs
- Specify components, responsibilities, and interfaces
- List expected file changes (create/modify/delete) consistent with codebase analysis
- Update task file with Architecture Overview section
- Only include sections relevant to task complexity — do not add boilerplate sections

**Artifacts**: Scratchpad at `docs/principled/specs/scratchpad/<hex-id>.md`, updated task file with Architecture Overview section

### Phase 4: Decomposition

Spawn after Phase 3 passes. Break the architecture into ordered implementation steps.

- Define ordered implementation steps with clear dependencies
- Each step must have: clear goal, expected output files, success criteria, subtasks
- No step larger than the large estimate threshold — split oversized steps
- Identify blockers, risks, and mitigations for each step
- Organize in phases: Setup, Foundational, User Stories, Polish
- Include Definition of Done section at task level listing completion criteria
- Write to scratchpad first, then update the task file

**Artifacts**: Scratchpad at `docs/principled/specs/scratchpad/<hex-id>.md`, updated task file with Implementation Process section

### Phase 5: Parallelize

Spawn after Phase 4 passes. Reorganize implementation steps for maximum parallel execution.

- Reorganize steps with explicit dependency chains
- Identify steps that can run in parallel (no transitive dependencies between them)
- Assign appropriate agent difficulty levels to each step
- Generate a parallelization diagram showing execution order and parallel tracks
- Add parallel execution directive with MUST requirements for each parallel group
- Only parallelize within the current task scope — do not plan or create tasks for future work
- Write to scratchpad first, then update the task file

**Artifacts**: Scratchpad at `docs/principled/specs/scratchpad/<hex-id>.md`, updated task file with parallelization annotations and agent assignments

### Phase 6: Verifications

Spawn after Phase 5 passes. Add evaluation rubrics for each implementation step.

- For each implementation step, determine verification level:

| Level | When to Use | Configuration |
|-------|-------------|---------------|
| None | Simple operations (mkdir, delete, config changes) | Skip verification entirely |
| Single Judge | Non-critical artifacts | 1 judge, threshold from task context |
| Panel of 2 Judges | Critical artifacts (business logic, security, data) | 2 judges, median voting, higher threshold |
| Per-Item Judges | Multiple similar items (validators, handlers, endpoints) | 1 judge per item, parallel execution |

- Create role-specific weighted rubrics for each step with measurable criteria
- Weights must sum to 1.0 for each rubric
- Set context-appropriate thresholds
- Include a verification summary table at the end of the task file

**Artifacts**: Scratchpad at `docs/principled/specs/scratchpad/<hex-id>.md`, updated task file with `#### Verification` sections for each step

### Phase 7: Promote

After all phases complete, move the refined task from draft to todo:

```bash
git mv <TASK_FILE> docs/principled/specs/tasks/todo/
```
