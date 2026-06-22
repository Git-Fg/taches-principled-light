---
name: orchestrating-subagents
description: "Load when designing multi-agent architectures or authoring agent definitions. Use when the user asks 'design a multi-agent system', 'define a custom agent', 'what coordinator pattern fits', or 'supervisor vs swarm vs hierarchical'. Do NOT use for running parallel code reviews (use reviewing-and-polishing), simple parallel fan-out (use superpowers' dispatching-parallel-agents), or single-skill orchestration (the skill itself is the orchestrator)."
when_to_use: "Use when user asks to spawn subagents, run reviews in parallel, define custom agents, or manage background workers."
license: MIT
---

## Routing Guidance

- **Hub Skill:** Combines agent definition authoring (DESIGN) and subagent execution (ORCHESTRATE).
- **Exclusion:** Do NOT use for multi-agent architecture decision-making (supervisor vs swarm) — read `references/patterns-reference.md` for pattern selection.
- Do NOT use for single-agent tasks, simple scripts, or non-agent workflows.

# Subagents

## Decision Router

This plugin uses **two platform-agnostic spawn patterns**. Never name a specific tool — use semantic verbs.

### The Two Spawn Patterns

**Explorer (read-only):**
```
spawn a subagent explorer with the prompt:
  "<task description>"
  Read-only. Return findings as a bounded summary — file:line citations, patterns found.
```
Use for: codebase mapping, external research, wiki search, verification reads, documentation lookup.

**Generalist (edit access):**
```
spawn a subagent generalist with the prompt:
  "<task description>"
  You have edit access. Implement the changes, verify they work, return what you changed.
```
Use for: implementation, code review, judgment/scoring, auditing, fixes, adversarial stress-testing.

### Execution-mode selection

| Task scale | Right primitive | When to choose it |
|---|---|---|
| Trivial — 1 file, <10 lines, or a single search/read | Inline in the main context | Quick edit, single lookup, glance-check |
| Non-trivial single-context — 3–10 files, single methodology, side task | Inline + spawn a subagent generalist for review | Main agent has the context; isolated review earns its cost |
| Multi-stage with fan-out → verify → synthesize | Multiple subagent generalists with different lenses + inline work | Same isolation benefit, no specialized agent proliferation |
| Codebase-wide or many-file or multi-methodology | Spawn a subagent explorer for the map + inline implementation + spawn a subagent generalist for review | Explorer maps; generalist reviews |
| Long-running with external triggers | Orchestration script + recurring checks + push channels | Reacts to CI, alerts, scheduled events; survives idle time |

Implicit signals that demote the mode: `--solo` or `--lightweight` flag → inline; sub-sentence ask touching ≤3 files → inline; context usage > 70% → inline for the remainder.

### When to Use Each Pattern

All specialization lives in the prompt, not in agent files. Before creating a new agent definition, ask: "Could this be a one-sentence lens in the prompt instead?" If yes, do not create an agent file.

**Reviewer:** spawn a subagent generalist with a lens prompt — "Review through the lens of: <angle>." The prompt specifies what to look for, severity levels, and output format.

**Codebase mapper:** spawn a subagent explorer with a scope — "Map the structure under <path>; find where <pattern> is implemented." Read-only.

**Researcher:** spawn a subagent explorer with a question — "Research <topic>. Use web search and docs. Synthesize with citations."

**Judge:** spawn a subagent generalist with a rubric — "Score this candidate against these criteria (1-5). Return per-criterion evidence."

---

## Gotchas

- Do NOT design a multi-agent system for a single-task problem. Single agents handle most tasks; multi-agent adds coordination overhead.
- Do NOT create agents with overlapping responsibilities — the coordinator won't know which to route to.
- Do NOT use subagents for simple parallelism. Use superpowers' `dispatching-parallel-agents` for fan-out of independent work.
- Do NOT define more than 5 agent types in one system. Beyond that, routing ambiguity degrades performance.
- When an agent definition includes `allowed-tools`, MUST verify every tool is actually needed — excess tools increase security surface.

## DESIGN Mode

Create and configure Claude Code subagent definitions. Produces complete agent files ready to use.

### Agent Scopes Principle

Agents exist at five scopes with priority: Managed (org-wide, highest), Session (CLI flag), Project, User, Plugin (lowest). Project scope for workspace-specific agents; User scope for cross-project personal agents.

### Core Loop Principle

1. Determine scope based on agent's intended use
2. Identify purpose and required capabilities
3. Configure skills, memory, isolation (omit tools/model/effort by default)
4. Generate the agent file
5. Validate structure and field values

**Architecture design:** IF designing multi-agent architectures (supervisor vs swarm vs hierarchical), IF selecting coordination patterns, or IF sizing contexts for parallel agents → BEFORE designing read `references/patterns-reference.md`. Do not proceed or make assumptions without reading this file.

**Framework comparisons:** IF evaluating LangGraph, AutoGen, CrewAI, or other orchestration frameworks → BEFORE comparing read `references/frameworks.md`. Do not proceed or make assumptions without reading this file.

**Tool design for agents:** IF designing tool interfaces that agents will call, IF debugging tool-selection failures, or IF standardizing tool conventions across a codebase → BEFORE writing tool descriptions read `references/tool-design.md`. Do not proceed or make assumptions without reading this file.

### Frontmatter Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique identifier. Lowercase letters and hyphens only. Required. |
| `description` | string | When Claude should delegate to this subagent. Required. |
| `tools` | list[string] | Tools the subagent can use. Allowlist. **Set only when restriction IS the point** (currently only a subagent explorer). |
| `disallowedTools` | list[string] | Tools to remove from inherited list |
| `model` | string | `sonnet`, `opus`, `haiku`, full model ID, or `inherit` — inherit by default |
| `permissionMode` | string | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan` |
| `maxTurns` | integer | Max agentic turns before subagent stops |
| `skills` | list[string] | Skills to preload (full content injected at startup) |
| `mcpServers` | map | MCP servers scoped to this subagent |
| `hooks` | map | Lifecycle hooks scoped to this subagent |
| `memory` | string | Persistent memory scope: `user`, `project`, or `local` |
| `background` | boolean | `true` = always run as background task |
| `effort` | string | Effort level: `low`, `medium`, `high`, `xhigh`, `max` |
| `isolation` | string | `worktree` = run in temporary git worktree |
| `color` | string | Display color: `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan` |
| `initialPrompt` | string | Auto-submitted as first user turn |

### Tool Restriction — Iterative Refinement Principle

Start with no tool restrictions. Omit both `tools` and `disallowedTools` from the initial definition. Ship it, verify it works, then restrict only if a specific tool causes problems. Premature restriction is the most common cause of silent agent failures.

### Model & Effort Principle

Never set `model` or `effort` unless explicitly requested. Both default to `inherit` — correct for 95% of agents. Setting them prematurely locks the agent to a configuration that may be wrong.

### Skills Preloading Principle

**"Better too much than not enough."**

Subagents do not inherit skills from the parent — list them explicitly. The `skills` field injects full base SKILL.md content at startup. Missing or disabled skills are silently skipped.

**Mandatory preload across all agent types.** All potentially relevant skills MUST be preloaded on all agents unconditionally. This is not a performance optimization — it is a deterministic capability access requirement. The cost of preloading an unused skill is tokens; the cost of missing a needed skill mid-task is capability failure.

**Progressive disclosure keeps preloading efficient.** Properly authored skills use progressive disclosure: frontmatter metadata is lightweight, deeper reference files load only on demand. Baseline context consumption from preloading a skill is extremely low.

**The AI retains lazy-loading autonomy.** While base skills are preloaded deterministically, the AI retains full autonomy to decide whether it needs to lazily load deeper reference files from those skills based on the specific task at hand. Preloading is not the same as processing all referenced content.

Do not filter or conditionally load skills based on narrow task assumptions. Cast wide and let the agent's task requirements drive depth.

### Cross-Plugin Skill Preloading

**It is perfectly safe and highly recommended to preload skills from plugins that may not currently be installed on the user's machine.** Claude Code evaluates the `skills:` frontmatter array dynamically at startup; if a requested skill is unavailable or uninstalled, the system gracefully ignores it without throwing an error. Because properly authored skills rely on progressive disclosure, their baseline context consumption is extremely low. Aggressively preloading all potentially relevant methodology skills ensures maximum deterministic capability access with zero risk of breaking the agent. An agent can list `solving-competitively`, `reasoning-from-principles`, `tdd`, and `restructuring-code` in its `skills:` array even when the user has only the core plugin installed — unsupported skills are silently skipped.

### Memory Architecture Principle

Enable memory on every subagent by default. `project` scope for team-shared knowledge; `user` scope for cross-project expertise; `local` scope for sensitive output (gitignored).

### Body Prompt Philosophy

Keep the markdown body general and concise — a short role statement and behavioral guardrails. If writing more than ~30 lines, you're duplicating a skill. Reference it in the `skills` field instead.

### Spawning Topology Constraint

NEVER place spawn, fan-out, or delegation instructions inside agent definition markdown files. Because the `Agent` tool is strictly removed from the subagent tool registry at the implementation level, nested spawning directives will cause a fatal failure. *(Note: Subagents CAN invoke skills via the `Skill` tool)*. If nested orchestration or multi-agent coordination is required, you must instead create a skill with `context: fork` frontmatter to establish an isolated orchestration environment.

### Routing Principle

The `description` field is the routing oracle — write it like a trigger rule with specific conditions, not capability lists. For the 6 marketplace keepers, front-load the role and the input contract ("lens/scope/question/dimension").

### File Templates

BEFORE writing spawn prompts, you MUST read `references/agent-templates.md` for reusable templates (Researcher, Analyst, Monitor, Explorer). Do not proceed or make assumptions without reading this file.

### Contract Design (6 principles)

When defining an agent's `tools:` and body contract, BEFORE shipping the agent definition file you MUST read `references/subagent-contract-design.md`. The 6 design principles (P1 source-of-truth, P2 bind Reads to Writes, P3 ordered operations with verification, P4 explicit link resolution, P5 failure-mode footer, P6 ground truth) apply to every agent in the marketplace. The reference also documents the 4 tool-source patterns and the 3-phase testing methodology (static read → real invocation → JSONL trace). Do not proceed or make assumptions without reading this file.

### Fork Mode Principle

Fork mode creates a subagent that inherits the full conversation context and shares the parent's prompt cache. Use when the subagent needs to understand the full conversation or reference earlier decisions. Do not use for independent tasks or parallel workstreams. The 4 fork skills in the marketplace (`plan-lifecycle`, `solving-competitively`, `task-lifecycle`, `reasoning-from-principles`) all use this pattern — they implement inline within the fork and spawn a subagent generalist for isolated review (see subagent-orchestration skill for the pattern).

### Architecture Design (Multi-Agent Patterns)

DESIGN mode also covers the *shape* of a multi-agent system: which pattern fits the task, how agents coordinate, and how context is partitioned across them. For exhaustive coverage (framework comparisons, consensus mechanisms, failure-mode deep dives), read `references/patterns-reference.md`. The three primary patterns:

**Supervisor/Orchestrator** — Central agent decomposes, spawns, and synthesizes. Use when tasks have clear decomposition and human oversight matters. Trade-off: supervisor context becomes a bottleneck and failures cascade to all workers.

**Peer-to-Peer/Swarm** — No central control; agents communicate via filesystem or explicit handoff protocols. Use for flexible exploration where rigid planning is counterproductive. Trade-off: coordination complexity and divergence risk rise with agent count.

**Hierarchical** — Strategy → Planning → Execution layers. Use for large-scale projects with layered abstraction. Trade-off: coordination overhead between layers and strategy/execution misalignment risk.

**Core principle:** Context isolation is the primary benefit — subagents exist to give each execution a clean context window, not to anthropomorphize role division. Reach for multi-agent only when a single agent's context window is the binding constraint.

**Design guidelines:**
- Default to filesystem-based inter-agent communication; reserve message-passing for state that one consumer needs faithfully
- Use debate protocols for consensus, not simple voting — voting treats hallucinations as equal to reasoning
- Set iteration limits on all agent execution
- Start simple — add multi-agent complexity only when single-agent fails
- **Default to inline implementation; reach for subagents only when isolation earns the cost**

---

## ORCHESTRATE Mode

Spawn isolated-context subagents — primarily a subagent generalist (parameterized by a lens) for parallel reviews, plus a subagent explorer and a subagent explorer for large exploration. The main agent implements inline; the subagents self-review against the lens/scope/question.

When the task scale is at the *multi-stage* tier or higher, prefer composing the orchestration as a script: the script holds the loop, the branching, and the intermediate results; the conversation only holds the final answer. The mode covers both inline fan-out and script-based composition — pick the tier and the runtime resolves the underlying mechanic.

### Core Mental Model

Four rules govern every delegation decision:

1. **Default to inline** — the main agent implements unless isolation earns the cost.
2. **Assign unambiguous scope** — each spawned subagent gets an exclusive lens/scope/question.
3. **Validate before integrating** — run success criteria, never assume.
4. **Persist state to disk** — subagents don't share conversation memory.

### Cost-Capability Spectrum

| Type | Model | Best for |
|------|-------|----------|
| `Bash` | — | Git ops, build commands, script execution |
| `Explore` | Haiku | Codebase discovery, targeted lookups |
| `Plan` | Sonnet | Architecture analysis, implementation planning |
| `general-purpose` | Inherit | Custom workflows, complex orchestration |

### Delegation Protocol

#### Decompose

Break the task into independent workstreams. Each stream must:
- Own its lens/scope/question exclusively (no overlapping reviews)
- Have a clear deliverable (file path + format)
- Have passing success criteria (test, lint, type-check, build)
- Have a one-command rollback

#### Context Harden (RACE Framework)

Structure every spawn prompt with RACE. For the 6 marketplace keepers, the RACE fields become:
- **Role**: subagent type (a subagent generalist, a subagent explorer, a subagent explorer, a subagent generalist, a subagent generalist, a subagent explorer)
- **Action**: concrete, scoped task — imperative form, one clear objective
- **Context**: what the orchestrator has done; what this agent should do next; output contract
- **Expectation**: output format/schema; success criteria; coverage rule

For a subagent generalist, the Action carries a **lens** ("review through the lens of OWASP Top 10"). For a subagent explorer, a **scope** ("map the structure under src/auth"). For a subagent explorer, a **question** ("what's the current best practice for X"). The lens/scope/question is the one-sentence specialization.

Key constraints: Positive framing (tell agents what to do), minimal high-signal context, explicit scope boundaries, coverage rule (comprehensive vs curated).

**Failure signal:** Return structured JSON with status, reason, completed_portion, retry_possible.

**MANDATORY:** You MUST read `references/agent-templates.md` BEFORE writing any RACE prompt. Do not proceed without reading this file. The reference contains the full RACE Component Details table, RACE Anti-Patterns table, and role-based agent templates (Researcher, Explorer, Implementer, Monitor, Architect) — all spawn prompts MUST conform to these templates.

#### Spawn and Collect

Spawn with appropriate model/tools/background. Read subagent results from the shared scratchpad files — for exploration use `docs/principled/scratch/{plan-id}.md`; for review use `docs/principled/scratch/{plan-id}-review.md`. Inspect raw transcript files at `{{CLAUDE_WORKING_DIR}}/.claude/projects/{project-id}/` for detailed per-agent logs. Use SendMessage to resume background agents.

#### Synthesize

Cross-domain consistency check + full integration test before presenting results. A bounded summary from each subagent (severity + file:line + fix) integrates cleanly; raw exploration results are a delegation tax.

### Self-Review Loop

Implement (inline) → spawn a subagent generalist for isolated revieww/ lens → [pass] → integrate → [fail] → Fix inline → Respawn a subagent generalist for isolated revieww/ same lens

The reviewer must report ALL findings including low-confidence ones. A downstream filter ranks severity.

### Parallel Patterns

**Horizontal Split** — Investigation streams run in parallel, each as a a subagent generalist w/ distinct lens (security, perf, style). Not for shared dependencies.

**Vertical Slice** — Each team owns their service end-to-end (frontend, backend, tests). Not for features requiring mid-implementation coordination.

**Pipeline** — Chained execution where one stage must complete before the next. Not for parallelizable work.

**Contest** — Competing hypotheses tested simultaneously via a subagent generalist instances. Not when one hypothesis is already strongly supported.

### Output discipline

Every spawned subagent returns a **bounded summary**. The subagent's internal exploration is disposable; what it returns is permanent in the parent. A 12k-token review of a 3k-token artifact is a delegation tax, not a benefit.