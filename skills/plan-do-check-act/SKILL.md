---
name: plan-do-check-act
description: "Run a Plan-Do-Check-Act (PDCA) cycle to test a hypothesis with measurable success criteria. Use when user says 'run a PDCA cycle', 'test this hypothesis', 'A/B test this change', 'validate the improvement worked', 'standardize this change', 'experiment with X'. Four phases: PLAN (design the experiment), DO (implement small-scale), CHECK (measure results against success criteria), ACT (standardize or refine). NOT for: planning a multi-phase project (use `plan-lifecycle`); NOT for: continuous experimentation at scale (use `subagent-orchestration`)."
when_to_use: "Use for proof-of-concepts, A/B tests, and validating improvements before standardization. Do NOT use for debugging (use superpowers' `systematic-debugging`) or code style (use refine)."
argument-hint: "[improvement goal or problem to address] [--cycle N]"
---

## Runtime persistence

`docs/principled/` (in cwd) is the natural runtime emplacement for principled-related artifacts.

Before writing any artifact: use your native file tools to scan `docs/` for existing files relevant to this work — design docs, specs, prior plans, architecture decisions, meeting notes. Read any that overlap with the artifact you are about to create. Build on existing context rather than starting from scratch.

At intake: read whatever is in `docs/principled/` — prior context may inform this work.

When this skill produces durable artifacts, write them to `docs/principled/` too. Skip if absent.

## Routing Guidance

- IMMEDIATELY when solving problems where outcomes need measurement — BEFORE concluding, standardizing, or shipping.
- FIRST after a failed fix — validate the root cause was correct before closing the issue.
- DO NOT use for debugging (use superpowers' `systematic-debugging` instead), for code style decisions (use refine in POLISH mode), or for architectural design (use kaizen or ideation).
- CONTRAST with kaizen: kaizen prevents bad patterns from entering the codebase (proactive constraint); PDCA tests whether a change actually improves things (evidence-based validation). Use kaizen when writing new code; use PDCA when deciding whether to standardize or generalize an existing change.

## Decision Router

IF testing a hypothesis to solve a problem or improve a process → start a PDCA cycle with a clear success criterion
IF an experiment produced unexpected results → begin a new cycle with an adjusted hypothesis and measurement plan
IF an experiment succeeded → standardize the change in the Act phase and close the cycle
IF an experiment partially succeeded → standardize what worked and start a new cycle for what did not
IF stuck after three cycles on the same problem → revisit the root cause analysis before continuing

## Orchestration Shape

This methodology is a 4-phase pipeline that maps naturally to an orchestration script. Each phase delegates work to a single role, with parallelism available inside the Do and Check phases.

| Phase | Role | Output |
|-------|------|--------|
| **Plan** | planner agent | hypothesis, change list, success criteria |
| **Do** | implementer agents (one per change, parallel) | executed change with execution log |
| **Check** | verification fleet (independent evaluators, parallel) | structured pass/fail results against criteria |
| **Act** | synthesizer agent | standardize, adjust, or revert decision |

**Execution tier:** an orchestration script composing a 4-phase pipeline. Plan and Act run as single roles; Do and Check fan out work in parallel. Structured objects pass between phases so each role receives a complete handoff.

# Plan-Do-Check-Act

Four-phase iterative cycle for systematic experimentation and continuous improvement. Each cycle tests one hypothesis with measurable success criteria.

## Core Principle

Never implement a change without knowing how you will measure success. Never conclude without comparing results against the baseline. Every cycle either produces a standardized improvement or a validated learning that feeds the next cycle.

## Process

### Phase 1: Plan
1. Define the problem or improvement goal with baseline metrics
2. Identify root causes using deep analysis before hypothesizing
3. State the hypothesis explicitly: "If we change X, Y will improve by Z"
4. Design the experiment: what to change, how to measure, success criteria
5. **Verification:** Success criteria are numeric and measurable, not subjective

### Phase 2: Do

**Implement the change inline.** The change's files are already in your context. Execute it at small scale first:
- Implement the change at small scale first
- Document what was actually done and any deviations from plan
- Collect data throughout — include unexpected observations
- Write execution log to `docs/principled/pdca/[cycle]-do.md`

### Phase 3: Check

**spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why." for an isolated-context evaluation.** The isolated context matters here: a fresh critic evaluating the data is not biased by having run the experiment. It should:
- Measure results numerically against the hypothesis metrics
- Compare before vs. after with specific data points
- Determine whether the hypothesis held with objective evidence
- Identify why the hypothesis failed if it did not hold
- Write evaluation to `docs/principled/pdca/[cycle]-check.md`

### Phase 4: Act

**Document the cycle outcome inline.** Based on the Check evaluation:
- If successful: Document the standardized change, update relevant documentation, create monitoring/automation notes
- If unsuccessful: Document the refined hypothesis and planned adjustments for cycle N+1
- If partially successful: Document what was standardized and what remains for next cycle
- Write outcome to `docs/principled/pdca/[cycle]-act.md`

- **If successful:** Standardize the change — update documentation, train the team, add automation or monitoring
- **If unsuccessful:** Understand why the hypothesis failed, refine it, start a new cycle
- **If partially successful:** Standardize what worked, plan next cycle for remaining issues
- **Verification:** The Act phase outcome is explicit — either "cycle closed with standardization" or "cycle N+1 started with adjusted hypothesis"

## Output

Either: (1) a standardized improvement with documentation, monitoring, and team training, or (2) a validated learning that refines the hypothesis for the next cycle. Multiple cycles are normal — two to three cycles per problem is typical.

## Design Decisions

### Start small, escalate scope
Phase 2 always begins at small scale. Full rollout only after the Check phase confirms success. This prevents wasting effort on changes that do not produce results.

### Failed experiments are learning, not failure
---

## CONTRAST
- NOT for: ddd (structure vs design-time decisions), NOT for superpowers' `systematic-debugging` (debugging vs prevention), NOT for refine (artifact polishing), NOT for kaizen (incremental vs design-time)

## Agent Spawn Map

IF designing PDCA experiment (Plan) → design the experiment inline (or spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why." for an isolated pre-critique)
IF executing PDCA change (Do) → implement inline
IF evaluating PDCA results (Check) → spawn **a subagent generalist** with lens "evaluate results against the success criteria"
IF synthesizing PDCA outcome (Act) → document inline
