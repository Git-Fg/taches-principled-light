---
name: ideation
description: "Generate 6 creative alternatives before committing to an approach — 3 high-probability anchors + 3 low-probability tails with trade-offs. Use when the user says 'generate ideas for X', 'what are the options', 'give me alternatives', 'show me different approaches'. Single mode: CREATE-IDEAS (6 distinct approaches inline, optional a subagent generalist challenge). NOT for: collaborative idea refinement (use superpowers' `brainstorming`); NOT for: scoring competitive solutions (use `sadd` JUDGE); NOT for: first-principles reasoning on a hard decision (use `fpf`)."
when_to_use: |
  - User needs a list of creative alternatives or diverse approaches to a problem.
  - Use for early-stage conceptualization before architecture or implementation begins.
  - NOT for: collaborative idea-to-design dialogue (use superpowers' `brainstorming`).
argument-hint: "[feature concept, problem, or topic]"
---

## Runtime persistence

`docs/principled/` (in cwd) is the natural runtime emplacement for principled-related artifacts.

Before writing any artifact: use your native file tools to scan `docs/` for existing files relevant to this work — design docs, specs, prior plans, architecture decisions, meeting notes. Read any that overlap with the artifact you are about to create. Build on existing context rather than starting from scratch.

At intake: read whatever is in `docs/principled/` — prior context may inform this work.

When this skill produces durable artifacts, write them to `docs/principled/` too. Skip if absent.

## Routing Guidance

- IMMEDIATELY when a concept is vague or unformed — BEFORE sketching architecture or writing code.

## Decision Router

IF user wants to explore or refine an unformed idea through dialogue → use superpowers' `brainstorming` (collaborative Q&A, design doc, spec self-review)
IF user wants creative idea generation (not refinement) → use **create-ideas** mode
IF user has simple task capture needs → use task-lifecycle CAPTURE mode instead
IF user needs formal planning with milestones → use plan-lifecycle PLAN mode instead
IF user already knows exactly what they want → skip to design capture directly
IF combining with development workflow → produce `docs/principled/specs/plans/<topic>.design.md` then create task file
IF user needs structured evaluation rather than generation → use evaluation workflow instead
IF idea is fully formed and documented → no need for this skill

---

## DO NOT Boundaries

- **DO NOT use for simple task capture** — use `task-lifecycle` CAPTURE mode instead for task capture
- **DO NOT use for formal planning** — use `plan-lifecycle PLAN mode` instead for project planning

## CONTRAST

- CONTRAST with superpowers' `brainstorming`: that skill does collaborative Q&A to turn vague ideas into approved design docs with spec self-review; this skill generates 6 diverse alternatives at once without dialogue. Use brainstorming when you need to refine a vague idea with the user; use ideation when you need a spread of options fast.
- CONTRAST with task-lifecycle CAPTURE: ideation generates alternatives from a concept; task-lifecycle CAPTURE mode captures clear intent as a draft. Use ideation when options are needed; use task-lifecycle CAPTURE when the intent is already clear.
- CONTRAST with plan-lifecycle PLAN mode: ideation generates options; plan-lifecycle PLAN mode decomposes a project into phases and tasks. Use ideation when the concept needs exploration; use plan-lifecycle PLAN mode when scope is clear and decomposition is needed.

---

## What This Skill Changes

**Default behavior:** Claude treats "design this" as design-capture — it asks for requirements and jumps to a solution. "Brainstorm" requests get flattened to a list rather than explored through dialogue.

**With this skill:** Idea exploration is preceded by constraint elicitation. "Design this" requests trigger collaborative dialogue before any solution generation. create-ideas mode generates 6 probability-weighted options (3 anchors, 3 tail) rather than 1-2 variations.

**Why probability sampling:** High-probability anchors cover the obvious solutions. Low-probability tail explorations prevent premature convergence on the first plausible option. Without both, brainstorming produces safe consensus, not creative options.

---

## Execution Mode

**Default: inline divergent generation.** Ideation benefits from diverse angles, but spawning 6 subagents to generate 6 ideas duplicates reasoning you can do in-context at lower cost. Generate the 6 approaches inline in this order: 3 high-probability central solutions, then 3 low-probability distinct regions. After generating, optionally spawn 2 a subagent generalist instances in parallel — one with lens "challenge these 3 anchor candidates for feasibility", one with lens "challenge these 3 tail candidates for feasibility" — for isolated-context stress tests.

**Process for create-ideas mode:**
- Generate 3 high-probability central solutions inline (anchor candidates)
- Generate 3 low-probability distinct solutions inline (tail candidates)
- Optionally spawn 2 a subagent generalist instances in parallel with the challenge lenses above
- Present all 6 ranked options to the user (do not merge or average)
- Scope: the topic, the generative brief, constraints from prior brainstorming (if any)
- Output: `docs/principled/specs/plans/<topic>.design.md`

# Create Ideas Mode

Generate 6 distinct responses for a given topic.

- **Anchor candidates:** 3 high-probability central solutions, generated inline (you are the anchor).
- **Tail candidates:** 3 low-probability distinct solutions, generated inline (you are the tail).
- **Stress test (optional):** spawn 2 a subagent generalist instances in parallel — "challenge these anchor candidates" + "challenge these tail candidates".
- **Synthesis:** Do not merge or average — present 6 distinct ranked options to the user.
- **Ranked presentation:** Order options by combined anchor/tail interest; do not flatten diversity.
- **Output:** Write ranked design to `docs/principled/specs/plans/<topic>.design.md` and commit to git.

## Failure Signal

```json
{"status": "failed", "reason": "no-viable-options|user-abandoned|scope-too-broad", "completed_portion": "...", "retry_possible": true|false}
```

---

## CONTRAST

- NOT for: structured agent-driven development — use sadd
- NOT for: first-principles reasoning — use fpf
- NOT for: code quality improvement — use refine
- NOT for: root cause diagnosis — use superpowers' `systematic-debugging`
- NOT for: design constraint decisions — use kaizen

## Reference Index

IF performing convergent ideation (high-probability) → generate inline (you are the anchor)
IF performing divergent ideation (low-probability) → generate inline (you are the tail)
IF performing codebase research for constraints → spawn **a subagent explorer**
