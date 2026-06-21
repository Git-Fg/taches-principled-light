# Phase Prompt Template

Copy and fill this structure for `docs/principled/plans/phases/XX-name/{phase}-{plan}-PLAN.md`:

**Naming:** Use `{phase}-{plan}-PLAN.md` format (e.g., `01-02-PLAN.md` for Phase 1, Plan 2)

```markdown
---
phase: XX-name
type: execute
domain: [optional - if domain skill loaded]
checkpoint-mode: autonomous | segmented | sequential
---

## Objective

[What this phase accomplishes - from roadmap phase goal]

Purpose: [Why this matters for the project]
Output: [What artifacts will be created]

## Context

@docs/principled/plans/BRIEF.md
@docs/principled/plans/ROADMAP.md
[If research exists:]
@docs/principled/plans/phases/XX-name/FINDINGS.md
[Relevant source files:]
@src/path/to/relevant.ts

## Tasks

### Task 1: [Action-oriented name]
Files: path/to/file.ext, another/file.ext
Action: [Specific implementation - what to do, how to do it, what to avoid and WHY]
Verify: [Command or check to prove it worked]
Done: [Measurable acceptance criteria]

### Task 2: [Action-oriented name]
Files: path/to/file.ext
Action: [Specific implementation]
Verify: [Command or check]
Done: [Acceptance criteria]

### Task 3: [Action-oriented name]
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

After completion, create `docs/principled/plans/phases/XX-name/{phase}-{plan}-SUMMARY.md`:

# Phase [X] Plan [Y]: [Name] Summary

**[Substantive one-liner - what shipped, not "phase complete"]**

## Accomplishments
- [Key outcome 1]
- [Key outcome 2]

## Files Created/Modified
- `path/to/file.ts` - Description
- `path/to/another.ts` - Description

## Decisions Made
[Key decisions and rationale, or "None"]

## Issues Encountered
[Problems and resolutions, or "None"]

## Next Step
[If more plans in phase: "Ready for {phase}-{next-plan}-PLAN.md"]
[If phase complete: "Phase complete, ready for transition"]
```

---

## Key Elements

- **Objective** — What this phase accomplishes, why it matters, what gets created
- **Context** — @file references for files Claude needs to understand
- **Tasks** — 2-3 tasks max, each with files, action, verify, done
- **Verification** — Overall phase checks beyond individual task verification
- **Success Criteria** — Measurable completion criteria
- **Output** — SUMMARY.md structure specification

**Scope guidance:**
- Aim for 2-3 tasks per plan
- If planning >5 tasks, split into multiple plans (01-01, 01-02, etc.)
- Target ~50% context usage maximum

**Checkpoint mode:**
- `autonomous` — Execute all tasks without stopping (default)
- `segmented` — Pause at checkpoints for human verification/decision
- `sequential` — Stop after each task for confirmation

---

## Good Example

```markdown
---
phase: 01-foundation
type: execute
domain: next-js
---

## Objective

Set up Next.js project with authentication foundation.

Purpose: Establish the core structure and auth patterns all features depend on.
Output: Working Next.js app with JWT auth, protected routes, and user model.

## Context

@docs/principled/plans/BRIEF.md
@docs/principled/plans/ROADMAP.md
@src/lib/db.ts

## Tasks

### Task 1: Add User model to database schema
Files: prisma/schema.prisma
Action: Add User model with fields: id (cuid), email (unique), passwordHash, createdAt, updatedAt. Add Session relation. Use @db.VarChar(255) for email to prevent index issues.
Verify: npx prisma validate passes, npx prisma generate succeeds
Done: Schema valid, types generated, no errors

### Task 2: Create login API endpoint
Files: src/app/api/auth/login/route.ts
Action: POST endpoint that accepts {email, password}, validates against User table using bcrypt, returns JWT in httpOnly cookie with 15-min expiry. Use jose library for JWT (not jsonwebtoken - it has CommonJS issues with Next.js).
Verify: curl -X POST /api/auth/login -d '{"email":"test@test.com","password":"test"}' -H "Content-Type: application/json" returns 200 with Set-Cookie header
Done: Valid credentials return 200 + cookie, invalid return 401, missing fields return 400

## Verification

- [ ] `npm run build` succeeds without errors
- [ ] `npx prisma validate` passes
- [ ] Login endpoint responds correctly to valid/invalid credentials
- [ ] Protected route redirects unauthenticated users

## Success Criteria

- All tasks completed
- All verification checks pass
- No TypeScript errors
- JWT auth flow works end-to-end

## Output

After completion, create `docs/principled/plans/phases/01-foundation/01-01-SUMMARY.md`
```

---

## Bad Example

```markdown
# Phase 1: Foundation

## Tasks

### Task 1: Set up authentication
**Action**: Add auth to the app
**Done when**: Users can log in
```

This is useless. No context, no verification, no specificity.