# Workflow: Execute Phase

## Sections
- [Process](#process)
- [Deviation Rules](#deviation-rules)
- [Verification Failure Gate](#verification-failure-gate)
- [Authentication Gates](#authentication-gates)
- [Success Criteria](#success-criteria)

---

Execute a phase prompt (PLAN.md) and create the outcome summary (SUMMARY.md).

---

## Process

### Step 1: Identify Plan

Find the next plan to execute:
- Check ROADMAP.md for "In progress" phase
- Find plans in that phase directory
- Identify first plan without corresponding SUMMARY

```bash
cat docs/principled/plans/ROADMAP.md
# Look for phase with "In progress" status
# Then find plans in that phase
ls docs/principled/plans/phases/XX-name/*-PLAN.md 2>/dev/null | sort
ls docs/principled/plans/phases/XX-name/*-SUMMARY.md 2>/dev/null | sort
```

**Logic:**
- If `01-01-PLAN.md` exists but `01-01-SUMMARY.md` doesn't → execute 01-01
- If `01-01-SUMMARY.md` exists but `01-02-SUMMARY.md` doesn't → execute 01-02
- Pattern: Find first PLAN file without matching SUMMARY file

Confirm with user if ambiguous.

Present:
```
Found plan to execute: {phase}-{plan}-PLAN.md
[Plan X of Y for Phase Z]

Proceed with execution?
```

### Step 2: Load Prompt

Read the plan prompt:
```bash
cat docs/principled/plans/phases/XX-name/{phase}-{plan}-PLAN.md
```

This IS the execution instructions. Follow it exactly.

### Step 3: Previous Phase Check

Before executing, check if previous phase had issues:

```bash
# Find previous phase summary
ls docs/principled/plans/phases/*/SUMMARY.md 2>/dev/null | sort -r | head -2
```

If previous phase SUMMARY.md has "Issues Encountered" or mentions blockers:

Ask user:
- "Previous phase had unresolved items. How to proceed?"
  - "Proceed anyway" - Issues won't block this phase
  - "Address first" - Resolve before continuing

### Step 4: Execute Tasks

Execute each task in the prompt. **Deviations are normal**—handle them automatically.

1. Read the @context files listed in the prompt

2. For each task:
   - Work toward task completion
   - **When you discover additional work not in plan:** Apply deviation rules (see below) automatically
   - Run the verification
   - Confirm done criteria met
   - Track any deviations for Summary documentation
   - Continue to next task

3. Run overall verification checks from `Verification` section
4. Confirm all success criteria from `Success Criteria` section met

### Step 5: Create Summary

Create `{phase}-{plan}-SUMMARY.md` as specified in the prompt's Output section.

**File location:** `docs/principled/plans/phases/XX-name/{phase}-{plan}-SUMMARY.md`

**Title format:** `# Phase [X] Plan [Y]: [Name] Summary`

The one-liner must be SUBSTANTIVE:
- **Good:** "JWT auth with refresh rotation using jose library"
- **Bad:** "Authentication implemented"

**Next Step section:**
- If more plans exist in this phase: "Ready for {phase}-{next-plan}-PLAN.md"
- If this is the last plan: "Phase complete, ready for transition"

### Step 6: Update Roadmap

Update ROADMAP.md:

**If more plans remain in this phase:**
- Update plan count: "2/3 plans complete"
- Keep phase status as "In progress"

**If this was the last plan in the phase:**
- Mark phase complete: status → "Complete"
- Add completion date

### Step 7: Git Commit

Commit plan completion (PLAN + SUMMARY + code):

```bash
git add docs/principled/plans/phases/XX-name/{phase}-{plan}-PLAN.md
git add docs/principled/plans/phases/XX-name/{phase}-{plan}-SUMMARY.md
git add docs/principled/plans/ROADMAP.md
git add src/  # or relevant code directories
git commit -m "feat({phase}-{plan}): [one-liner from SUMMARY.md]"
```

**Commit scope pattern:**
- `feat(01-01):` for phase 1 plan 1
- `feat(02-03):` for phase 2 plan 3

### Step 8: Offer Next

**If more plans in this phase:**
```
Plan {phase}-{plan} complete.
Summary: docs/principled/plans/phases/XX-name/{phase}-{plan}-SUMMARY.md

[X] of [Y] plans complete for Phase Z.

What's next?
1. Execute next plan ({phase}-{next-plan})
2. Review what was built
3. Done for now
```

**If phase complete (last plan done):**
```
Plan {phase}-{plan} complete.
Phase [Z]: [Name] COMPLETE - all [Y] plans finished.

What's next?
1. Transition to next phase
2. Review phase accomplishments
3. Done for now
```

---

## Deviation Rules

**While executing tasks, you WILL discover work not in the plan.** This is normal.

Apply these rules automatically. Track all deviations for Summary documentation.

---

**RULE 1: Auto-fix bugs**

**Trigger:** Code doesn't work as intended (broken behavior, incorrect output, errors)

**Action:** Fix immediately, track for Summary

**Examples:**
- Wrong SQL query returning incorrect data
- Logic errors (inverted condition, off-by-one, infinite loop)
- Type errors, null pointer exceptions, undefined references
- Broken validation (accepts invalid input, rejects valid input)
- Security vulnerabilities (SQL injection, XSS, CSRF, insecure auth)

**Process:**
1. Fix the bug inline
2. Add/update tests to prevent regression
3. Verify fix works
4. Continue task
5. Track in deviations list

---

**RULE 2: Auto-add missing critical functionality**

**Trigger:** Code is missing essential features for correctness, security, or basic operation

**Action:** Add immediately, track for Summary

**Examples:**
- Missing error handling (no try/catch, unhandled promise rejections)
- No input validation (accepts malicious data, type coercion issues)
- Missing null/undefined checks (crashes on edge cases)
- No authentication on protected routes
- Missing authorization checks (users can access others' data)

**Process:**
1. Add the missing functionality inline
2. Add tests for the new functionality
3. Verify it works
4. Continue task
5. Track in deviations list

---

**RULE 3: Auto-fix blocking issues**

**Trigger:** Something prevents you from completing current task

**Action:** Fix immediately to unblock, track for Summary

**Examples:**
- Missing dependency (package not installed, import fails)
- Wrong types blocking compilation
- Broken import paths (file moved, wrong relative path)
- Missing environment variable (app won't start)

**Process:**
1. Fix the blocking issue
2. Verify task can now proceed
3. Continue task
4. Track in deviations list

---

**RULE 4: Ask about architectural changes**

**Trigger:** Fix/addition requires significant structural modification

**Action:** STOP, present to user, wait for decision

**Examples:**
- Adding new database table (not just column)
- Major schema changes (changing primary key, splitting tables)
- Introducing new service layer or architectural pattern
- Switching libraries/frameworks

**Process:**
1. STOP current task
2. Present clearly:
```
⚠️ Architectural Decision Needed

Current task: [task name]
Discovery: [what you found]
Proposed change: [architectural modification]
Why needed: [rationale]
Impact: [what this affects]

Proceed with proposed change? (yes / different approach / defer)
```
3. WAIT for user response

---

**RULE 5: Log non-critical enhancements**

**Trigger:** Improvement that would enhance code but isn't essential now

**Action:** Add to docs/principled/plans/ISSUES.md automatically, continue task

**Examples:**
- Performance optimization (works correctly, just slower than ideal)
- Code refactoring (works, but could be cleaner)
- Better naming (works, but variables could be clearer)

**Process:**
1. Create docs/principled/plans/ISSUES.md if doesn't exist
2. Add entry with ISS-XXX number (auto-increment)
3. Brief notification: `📋 Logged enhancement: [brief] (ISS-XXX)`
4. Continue task without implementing

---

**RULE PRIORITY:**

1. **If Rule 4 applies** → STOP and ask
2. **If Rules 1-3 apply** → Fix automatically, track for Summary
3. **If Rule 5 applies** → Log to ISSUES.md, continue

---

## Verification Failure Gate

If any task verification fails:

STOP. Do not continue to next task.

Present inline:
```
Verification failed for Task [X]: [task name]

Expected: [verification criteria]
Actual: [what happened]

How to proceed?
1. Retry - Try the task again
2. Skip - Mark as incomplete, continue
3. Stop - Pause execution, investigate
```

Wait for user decision.

If user chose "Skip", note it in SUMMARY.md under "Issues Encountered".

---

## Authentication Gates

**When you encounter authentication errors during task execution:**

This is NOT a failure. Authentication gates are expected and normal.

**Authentication error indicators:**
- CLI returns: "Error: Not authenticated", "Not logged in", "Unauthorized"
- API returns: "Authentication required", "Invalid API key"
- Command fails with: "Please run {tool} login"

**Authentication gate protocol:**

1. **Recognize it's an auth gate** - Not a bug, just needs credentials
2. **STOP current task execution** - Don't retry repeatedly
3. **Present authentication steps** - Tell user exactly what to run
4. **Wait for user to authenticate** - Let them complete auth flow
5. **Verify authentication works** - Test that credentials are valid
6. **Retry the original task** - Resume automation where you left off
7. **Continue normally** - Don't treat this as an error in Summary

**Example: Vercel deployment hits auth error**

```
Task 3: Deploy to Vercel
Running: vercel --yes

Error: Not authenticated. Please run 'vercel login'

════════════════════════════════════
Authentication Required
════════════════════════════════════

I tried to deploy but got authentication error.

What you need to do:
Run: vercel login

This will open your browser - complete the authentication flow.

I'll verify after: vercel whoami returns your account

Type "done" when authenticated
════════════════════════════════════

[User types "done"]

Verifying authentication...
Running: vercel whoami
✓ Authenticated as: user@example.com

Retrying deployment...
✓ Deployed to: https://myapp-abc123.vercel.app
```

**In Summary documentation:**

Document authentication gates as normal flow, not deviations:

```markdown
## Authentication Gates

During execution, I encountered authentication requirements:

1. Task 3: Vercel CLI required authentication
   - Paused for `vercel login`
   - Resumed after authentication
   - Deployed successfully

These are normal gates, not errors.
```

---

## Success Criteria

- All tasks from PLAN.md completed
- All verifications pass
- SUMMARY.md created with substantive content
- ROADMAP.md updated