# Execution Strategies

## Sections
- [Strategy A: Fully Autonomous](#strategy-a-fully-autonomous)
- [Strategy B: Segmented Execution](#strategy-b-segmented-execution)
- [Strategy C: Sequential Execution](#strategy-c-sequential-execution)
- [Decision Tree](#decision-tree)
- [Context Budget](#context-budget)

---

Three strategies for plan execution, differentiated by checkpoint structure and autonomy level.

## Strategy A: Fully Autonomous (Intelligent Orchestration)

**Conditions:**
- Plan has no checkpoints, OR
- All checkpoints are informational only (no user action required)
- All tasks can complete without human decision points

**Core concept:** The executor acts as an intelligent orchestrator that:
1. Analyzes task dependencies
2. Decomposes into parallelizable vs sequential groups
3. Spawns multiple parallel workers for independent tasks
4. Spawns sequential workers for dependency chains
5. Loops subagent generalist for review at milestones until no HIGH findings remain
6. Aggregates results

**Executor responsibilities:**
- Build dependency graph (task to files)
- Identify conflict-free groups (different files, no data dependencies)
- Coordinate parallel workers (max 3-5 concurrent)
- Spawn subagent generalists for milestone review (haiku, read-only)
- Aggregate and verify all outputs
- Create SUMMARY

**⚠️ PRACTICAL CAP: 3-5 parallel workers.** While there is no hard system limit on concurrent subagents (tested successfully up to 12+), supervisor context grows non-linearly with worker count. Beyond 5 workers, the supervisor spends more tokens processing summaries, and outlier latency spikes (e.g., 20x median execution time) emerge due to system load.

**Parallel execution rules:**
- Parallel if: different files AND no output dependency
- Sequential if: same file OR output of one feeds input of another
- Max 3-5 parallel workers (cost/coordination balance)

**Milestone critique loop:**
- Every 2-3 tasks or phase boundary
- Spawn a subagent generalist for isolated review
- Loop until no HIGH findings
- Executor fixes issues before continuing

**Context budget for Strategy A:**
- Orchestrator (executor): ~10-15% (coordination overhead + milestone coordination)
- Each worker: fresh context ~20% (max 5 workers = 100% but they run sequentially within their slices)
- Milestone reviews: ~2% each
- Total: <30% overhead target (orchestrator ~10-15% + workers + milestone reviews)


---

## Strategy B: Segmented Execution

**Conditions:**
- Plan has checkpoints, AND
- All checkpoints are `checkpoint:human-verify` type (verification-only gates)
- Tasks between checkpoints form independent autonomous blocks

**Segment parsing:**
- Split PLAN.md at each `checkpoint:human-verify` marker
- Segment N = tasks between checkpoint N-1 and checkpoint N
- Final segment = tasks after last checkpoint to plan end

**Autonomous vs checkpoint handling:**

| Element | Action |
|---------|--------|
| Segment (autonomous block) | Spawn subagent to execute block |
| `checkpoint:human-verify` | Execute in orchestrator context, present to user |
| Verification pass | Continue to next segment |
| Verification fail | STOP, present failure gate |

**Checkpoint protocol:**
1. Orchestrator presents verification criteria
2. User confirms or rejects
3. On reject: follow Verification Failure Gate protocol
4. On confirm: record signal, proceed to next segment

**Strategy B: Segmented Execution**
- Use when: ONLY checkpoint:human-verify checkpoints exist
- Segments execute autonomously between verify checkpoints
- Human-verify checkpoints: present to user, wait for approval, continue
- If ANY decision or human-action checkpoint exists → Strategy C

**Context budget:**
- Each segment subagent: 20k tokens (focused execution)
- Orchestrator: 10k tokens (checkpoint management + state)
- Checkpoint verification: 5k tokens (user interaction context)
- Target total per segment: 35k tokens max

**Segment handoff format:**
```
Segment N completed:
- Tasks executed: [list]
- Files modified: [list]
- Deviations: [list]
- Verification status: [passed/failed]
```

---

## Strategy C: Sequential Decision-Dependent

**Conditions:**
- Plan has `checkpoint:decision` checkpoints, OR
- Plan has `checkpoint:human-action` checkpoints, OR
- Checkpoint outcomes affect subsequent task selection or parameters

**Execution model:** All tasks execute in orchestrator context, waiting at each decision/action checkpoint.

**When each checkpoint type applies:**

| Checkpoint Type | Trigger | Orchestrator Action |
|----------------|---------|-------------------|
| `checkpoint:decision` | User must choose between paths | Present options, wait, store decision |
| `checkpoint:human-action` | External system state required | Present action, wait, verify state change |
| `checkpoint:human-verify` | Verification gate | Present criteria, wait for confirm/reject |

**Protocol flow:**
1. Execute task(s) up to checkpoint
2. Present checkpoint to user with context
3. Wait for user response
4. On response: execute dependent tasks OR branch accordingly
5. Continue to next checkpoint or final SUMMARY

**Context budget:**
- Domain context: 15k tokens (files referenced in plan)
- Execution context: 7k tokens (execute-phase.md + deviation rules)
- Workspace: 10k tokens (orchestrator state + active implementation)
- User interaction: 3k tokens (checkpoint prompts + responses)
- Target total: 35k tokens max

---

## Strategy Selection Decision Tree

```
Does PLAN.md have checkpoints?
├─ No → Strategy A (Fully Autonomous)
└─ Yes ↓

Are ALL checkpoints human-verify type?
├─ Yes → Strategy B (Segmented Execution)
└─ No ↓

Does any checkpoint affect downstream tasks?
├─ Yes → Strategy C (Sequential)
│         Any of: checkpoint:decision OR checkpoint:human-action
│         These change the execution path based on user choice.
└─ No → Strategy B (Segmented)
          Only checkpoint:human-verify checkpoints exist.
          These don't change the path, just require verification.
```

**Selection heuristic:**
- Simple plan, no gates → A (fastest, minimal orchestration)
- Multiple verification gates, independent segments → B (parallelizable segments)
- Decision-dependent workflow, external actions → C (necessary sequencing)

---

## Context Budget Summary

| Strategy | Orchestrator | Subagent/Segment | Total |
|----------|--------------|-----------------|-------|
| A: Autonomous | 2,500-3,000 tokens (~10-15%) | 25,000 tokens per worker (fresh, isolated) | <30% overhead target |
| B: Segmented | 10k tokens (~10-15%) | 20k per segment | 35k max |
| C: Sequential | 10k tokens (~10-15%) | 15k domain + 7k execution | 35k max |

**Monitoring thresholds:**
- 25% remaining: Warning flag, consider flushing completed segments
- 15% remaining: Pause, aggregate partial progress
- 10% remaining: STOP, create partial SUMMARY, surface to user