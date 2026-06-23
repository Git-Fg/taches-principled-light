---
name: applying-guardrails
description: "Load when making design decisions that resist over-engineering — incremental improvement, error-proofing, standardization, or YAGNI. Use when the user says 'should I add this feature' or 'apply YAGNI'. Do NOT use for improving an existing artifact or correctness checks."
when_to_use: "Use when user wants to avoid over-engineering, apply YAGNI, or make architectural and code design decisions. Background guardrails applied to every code change; for deep structural analysis on tangled files, invoke a separate structural-analysis workflow as needed."
argument-hint: Applied automatically when implementing, refactoring, designing, or handling errors
user-invocable: false
license: MIT
---

## Routing Guidance

- IMMEDIATELY before writing code — these constraints apply to every decision.
- FIRST when tempted to add abstractions, speculate about future needs, or fix everything in one pass.
- DO NOT use when implementing trivial one-liners — use for architectural decisions, refactoring, and non-trivial implementation choices.
- CONTRAST with generating-ideas: that explores WHAT to build; kaizen shapes HOW to build it.
- CONTRAST with plan-do-check-act: that tests changes; kaizen prevents bad patterns from entering the codebase.
- CONTRAST with restructuring-code: kaizen is a lightweight filter of 4 design-time constraints applied to every code change; restructuring-code is a detailed analysis methodology with 4 modes (ARCHITECTURE, QUALITY, TRANSPARENCY, API) invoked when structural issues need a deep review. Run kaizen continuously; invoke restructuring-code when a specific structural question surfaces.
- CONTRAST with superpowers' `verification-before-completion`: that skill enforces evidence-before-claims at completion time (a gate); kaizen applies design-time guardrails before and during code decisions (a filter). They operate at different points in the workflow and are complementary.

## What This Skill Changes

**Default behavior:** Claude makes code decisions on intuition — adds abstractions for anticipated flexibility, fixes multiple issues at once, handles errors after they occur, and introduces new patterns without checking existing conventions.

**With this skill:** Every code decision gets filtered through four design-time constraints. Abstractions require concrete current need (YAGNI/JIT). Fixes land one at a time, verified between each. Errors are prevented at design time through type systems and validation layers. New patterns require team consensus before entering the codebase.

**Why this matters:** Design-level constraints are 10x cheaper than runtime fixes. Catching bad abstractions and speculative code at decision time prevents months of refactoring debt.

---

## Decision Router

IF implementing code, refactoring, making architecture decisions, or handling errors → apply all four kaizen pillars as design-time constraints
IF a problem is complex or has unclear causes → use a structured analysis method (tracing backward, asking why iteratively) before taking action
IF faced with "we might need this someday" requirements → apply JIT/YAGNI to cut speculation before it enters the codebase
IF the team introduces a new pattern without discussion → flag against Standardized Work and require team consensus
IF tempted to fix all quality issues in one pass → enforce Incremental Improvement: one change at a time, verify between each

# Kaizen

Continuous improvement applied as four design-time constraints on every code decision. Not a checklist to follow, but constraints that shape how code gets written, reviewed, and maintained.

## Core Principle

Small improvements continuously. Prevent errors at design time. Follow proven patterns. Build only what is needed now. These are not aspirations — they are quality gates applied at every decision point.

## The Four Pillars

### 1. Continuous Improvement — Incremental over revolutionary

The smallest change that improves quality, then verify, then repeat. Never try to fix everything in one pass.

- Make it work, then make it clear, then make it efficient — never all three at once
- Always leave code slightly better than you found it (fix small issues as you encounter them)
- One improvement per iteration, verified before the next
- Accept "better than before" even if not perfect — diminishing returns are real

**Red flag:** "I will refactor it later" without an immediate action. Either do it now or accept it as-is.

### 2. Poka-Yoke (error-proofing) — Error proofing at design time

Design systems that make errors impossible or immediately visible, not systems that handle errors gracefully after they occur.

- Use the type system to make invalid states unrepresentable
- Validate at system boundaries once, use safely everywhere
- Fail fast and loudly with clear messages
- Validate before use, not after
- Required configuration over optional with defaults — fail at startup, not in production

**Layers, in order:** Type system (compile time) → Validation (runtime, early) → Guards (preconditions) → Error boundaries (graceful degradation)

**Red flag:** "Users should just be careful" or optional config with no validation.

### 3. Standardized Work — Follow established patterns

Consistency over cleverness. New patterns require team consensus. Documentation lives with code.

- Before introducing a new pattern, search the codebase for similar solved problems
- Match existing file structure, naming conventions, error handling, import locations
- Comments explain "why", not "what" — code explains itself
- Automate standards via linters, type checks, CI/CD gates
- When a new standard emerges, document it

**Red flag:** "I prefer to do it my way" without checking existing patterns.

### 4. Just-In-Time (JIT) (just-in-time) — Build only what is needed now

YAGNI (you aren't gonna need it) applied rigorously. No "just in case" features, no premature optimization, no speculative abstractions.

- Implement only current requirements — delete speculative code
- Wait for the Rule of Three (three similar cases) before abstracting
- Profile before optimizing, measure before and after
- Prefer duplication over the wrong abstraction
- Add complexity only when a current requirement demands it, not when you anticipate future needs

**Red flag:** "We might need this someday" without a concrete, imminent requirement.

## Relationship to restructuring-code

Applying-guardrails and restructuring-code are complementary, not redundant. They operate at different layers of the same concern (preventing bad code from entering the codebase).

**Kaizen** is a lightweight 4-pillar filter applied to every code decision. It runs continuously in the background as guardrails — a developer does not "invoke" kaizen, they apply it as they write. No artifact, no analysis mode, no spawned subagent. The output is shaped code, not a written report.

**restructuring-code** is a detailed analysis methodology with 4 modes (ARCHITECTURE, QUALITY, TRANSPARENCY, API) invoked when a specific structural question surfaces. It produces a written analysis, may spawn subagents (codebase scanner, endpoint auditor), and is selected per mode based on the question at hand.

**When to use which:**

- Routine implementation, refactoring, or design decision → kaizen (apply the 4 pillars as guardrails)
- "Where should this business logic live?", "function does too much", "is this side effect visible?", "design a REST endpoint" → restructuring-code (select the matching mode for deep analysis)
- Both at once → apply applying-guardrails constraints while restructuring-code analyzes structure; they do not conflict

**Conceptual layering:** applying-guardrails is the immune system (always on, lightweight, prevents infection); restructuring-code is the specialist (called in for specific diagnoses, produces a treatment plan).

## Output

This skill produces no standalone artifact. It applies as behavioral constraints during development — every implementation, refactoring, architecture decision, and error handling path is shaped by these four pillars.

## Design Decisions

### Four pillars, not a checklist
These are design-time constraints, not a post-hoc audit. The pillars guide decisions as they are made. A post-hoc audit is too late — the code is already written.

### No code examples here
The patterns these pillars enforce (making invalid states unrepresentable, validating at boundaries, following conventions) are widely documented. The skill states the constraint; the developer (Claude) knows how to apply it.

### Guardrail stance, not procedure
This skill does not define a workflow. It defines invariants that apply across all workflows. The structured analysis methods (tracing, Five Whys, Fishbone, PDCA, A3) are complementary tools invoked when these guardrails surface a problem worth analyzing in depth.

## Gotchas

- Do NOT apply guardrails to throwaway scripts or one-off experiments — the overhead isn't justified.
- Do NOT let guardrails block velocity on trivial changes (<5 lines, no logic change).
- Do NOT use YAGNI to skip essential error handling or security checks. YAGNI applies to features, not safety.
- Do NOT apply all four guardrails mechanically. Pick the ones relevant to the decision at hand.
- When standardizing, MUST reference an existing project convention — never invent a new standard.

## CONTRAST
- NOT for: restructuring-code (structure vs design-time decisions), NOT for superpowers' `systematic-debugging` (debugging vs prevention), NOT for reviewing-and-polishing (artifact polishing), NOT for plan-do-check-act (experimentation vs design constraints), NOT for superpowers' `verification-before-completion` (completion gate vs design-time filter — complementary, not substitutes)
