# Plan Format Reference

## Sections
- [Core Principle](#core-principle)
- [Plan Structure](#plan-structure)
- [Task Anatomy](#task-anatomy)
- [Specificity Levels](#specificity-levels)
- [Anti-Patterns](#anti-patterns)
- [Sizing Tasks](#sizing-tasks)
- [Context References](#context-references)
- [Summary Output](#summary-output)

---

PLAN.md is the executable prompt. This reference defines what makes a plan executable vs. vague.

---

## Core Principle

A plan is Claude-executable when Claude can read PLAN.md and immediately start implementing without asking clarifying questions.

If Claude has to guess, interpret, or make assumptions—the task is too vague.

---

## Plan Structure

Every PLAN.md follows this structure:

```markdown
---
phase: XX-name
type: execute
domain: [optional]
---

## Objective

[What this phase accomplishes]

Purpose: [Why this matters]
Output: [What artifacts will be created]

## Context

@docs/principled/plans/BRIEF.md
@docs/principled/plans/ROADMAP.md
@[relevant/source/files]

## Tasks

### Task 1: [Action-oriented name]
Files: path/to/file.ext
Action: [Specific implementation - what to do, how, what to avoid and WHY]
Verify: [Command or check to prove it worked]
Done: [Measurable acceptance criteria]

### Task 2: [Action-oriented name]
...

## Verification

Before declaring phase complete:
- [ ] [Specific test command]
- [ ] [Build/type check passes]
- [ ] [Behavior verification]

## Success Criteria

- All tasks completed
- All verification checks pass
- No errors or warnings introduced
- [Phase-specific criteria]

## Output

After completion, create SUMMARY.md with accomplishments, files modified, deviations, and next step.
```

---

## Task Anatomy

Every task has four required fields:

### Files
**What it is:** Exact file paths that will be created or modified.

**Good:** `src/app/api/auth/login/route.ts`, `prisma/schema.prisma`
**Bad:** "the auth files", "relevant components"

Be specific. If you don't know the file path, figure it out first.

### Action
**What it is:** Specific implementation instructions, including what to avoid and WHY.

**Good:** "Create POST endpoint that accepts {email, password}, validates using bcrypt against User table, returns JWT in httpOnly cookie with 15-min expiry. Use jose library (not jsonwebtoken—CommonJS issues with Next.js Edge runtime)."

**Bad:** "Add authentication", "Make login work"

Include: technology choices, data structures, behavior details, pitfalls to avoid.

### Verify
**What it is:** How to prove the task is complete.

**Good:**
- `npm test` passes
- `curl -X POST /api/auth/login` returns 200 with Set-Cookie header
- Build completes without errors

**Bad:** "It works", "Looks good", "User can log in"

Must be executable—a command, a test, an observable behavior.

### Done
**What it is:** Acceptance criteria—the measurable state of completion.

**Good:** "Valid credentials return 200 + JWT cookie, invalid credentials return 401"

**Bad:** "Authentication is complete"

Should be testable without subjective judgment.

### Checkpoint (Optional)

**What it is:** An optional field declaring a checkpoint type after task completion.

**When to use:** When a task requires human verification, decision, or action before the next task can proceed.

**Canonical syntax:**
```markdown
Checkpoint: checkpoint:human-verify  # Human confirms output
```

**Checkpoint types:**

| Type | Trigger | Use when |
|------|---------|----------|
| `checkpoint:human-verify` | Human confirms results | Visual checks, reviewing generated content |
| `checkpoint:decision` | Human chooses path | Architecture, library selection, API design |
| `checkpoint:human-action` | Human performs action | Email verification, 2FA, account approval |

**Note:** This is the canonical checkpoint syntax for PLAN.md files. The `type="checkpoint:..."` attribute syntax is an alternative representation — both are recognized by plan-lifecycle, but prefer the `Checkpoint:` field syntax for consistency.

**When to add checkpoints:**
- One checkpoint per 5-10 tasks maximum
- Checkpoints that require thinking = plan needed more specificity upstream
- Checkpoints for things Claude can do via CLI = anti-pattern

**Anti-pattern:** Using checkpoints when Claude can verify automatically.

---

## Specificity Levels

### Too Vague

```markdown
### Task 1: Add authentication
Files: ???
Action: Implement auth
Verify: ???
Done: Users can authenticate
```

Claude: "How? What type? What library? Where?"

### Just Right

```markdown
### Task 1: Create login endpoint with JWT
Files: src/app/api/auth/login/route.ts
Action: POST endpoint accepting {email, password}. Query User by email, compare password with bcrypt. On match, create JWT with jose library, set as httpOnly cookie (15-min expiry). Return 200. On mismatch, return 401. Use jose instead of jsonwebtoken (CommonJS issues with Edge).
Verify: curl -X POST localhost:3000/api/auth/login -H "Content-Type: application/json" -d '{"email":"test@test.com","password":"test123"}' returns 200 with Set-Cookie header containing JWT
Done: Valid credentials → 200 + cookie. Invalid → 401. Missing fields → 400.
```

Claude can implement this immediately.

### Too Detailed

Writing the actual code in the plan. Trust Claude to implement from clear instructions.

---

## Anti-Patterns

### Vague Actions

- "Set up the infrastructure"
- "Handle edge cases"
- "Make it production-ready"
- "Add proper error handling"

These require Claude to decide WHAT to do. Specify it.

### Unverifiable Completion

- "It works correctly"
- "User experience is good"
- "Code is clean"
- "Tests pass" (which tests? do they exist?)

These require subjective judgment. Make it objective.

### Missing Context

- "Use the standard approach"
- "Follow best practices"
- "Like the other endpoints"

Claude doesn't know your standards. Be explicit.

---

## Sizing Tasks

Good task size: 15-60 minutes of Claude work.

**Too small:** "Add import statement for bcrypt" (combine with related task)
**Just right:** "Create login endpoint with JWT validation" (focused, specific)
**Too big:** "Implement full authentication system" (split into multiple plans)

If a task takes multiple sessions, break it down.
If a task is trivial, combine with related tasks.

If a phase has >7 tasks or spans multiple subsystems, split into multiple plans using the naming convention `{phase}-{plan}-PLAN.md`.

---

## Context References

Use @file references to load context:

```markdown
## Context

@docs/principled/plans/BRIEF.md           # Project vision
@docs/principled/plans/ROADMAP.md         # Phase structure
@src/lib/db.ts                # Existing database setup
@src/types/user.ts            # Existing type definitions
```

Reference files that Claude needs to understand before implementing.

---

## Summary Output

The authoritative SUMMARY.md template is in the SKILL.md "What Good Looks Like" section.
