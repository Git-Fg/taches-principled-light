# Deviation Rules

## Sections
- [Rule 1: Auto-fix Bugs](#rule-1-auto-fix-bugs)
- [Rule 2: Auto-add Missing Critical Functionality](#rule-2-auto-add-missing-critical-functionality)
- [Rule 3: Auto-fix Blocking Issues](#rule-3-auto-fix-blocking-issues)
- [Rule 4: Stop for Architectural Changes](#rule-4-stop-for-architectural-changes)
- [Rule 5: Log Non-critical Enhancements](#rule-5-log-non-critical-enhancements)
- [Priority Order](#priority-order)
- [Documentation in Summary](#documentation-in-summary)

---

Rules for handling work discovered during execution that was not in the original plan. Apply automatically.

## Rule 1: Auto-fix Bugs

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

## Rule 2: Auto-add Missing Critical Functionality

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

## Rule 3: Auto-fix Blocking Issues

**Trigger:** Something prevents completing the current task

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

## Rule 4: Stop for Architectural Changes

**Trigger:** Fix/addition requires significant structural modification

**Action:** STOP, present to user, wait for decision

**Examples:**
- Adding new database table (not just column)
- Major schema changes (changing primary key, splitting tables)
- Introducing new service layer or architectural pattern
- Switching libraries/frameworks

**Numeric thresholds for "significant":**
- New file requiring architectural pattern integration (new service layer, new module type)
- Schema migration affecting 3+ tables or entities
- Dependency addition that changes execution model
- API surface change affecting 5+ endpoints
- Authentication/authorization model change

**How to count tables/endpoints:** Use `grep -c "CREATE TABLE"` for database tables; count endpoint definitions via `grep -c` on route decorators (`@router.get`, `@app.post`, etc.) or OpenAPI specs.

**Not significant (proceed automatically):**
- Adding columns to existing tables
- Adding utility functions to existing modules
- Adding error handling to existing functions
- Refactoring within existing architectural boundaries

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

## Rule 5: Log Non-critical Enhancements

**Trigger:** Improvement that would enhance code but isn't essential

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

## Priority Order

**Rule 4 always takes precedence.** It is the only rule that stops execution.

| Priority | Rule | Action |
|----------|------|--------|
| 1 (highest) | Rule 4: Architectural change | STOP, ask user |
| 2 | Rules 1-3: Auto-fix | Fix automatically, track |
| 3 | Rule 5: Enhancement | Log to ISSUES.md, continue |

**When multiple rules could apply:**
- Evaluate in priority order
- If Rule 4 applies, stop immediately (do not apply other rules first)
- If Rule 4 does not apply, apply the highest-priority rule that matches

---

## Documentation in Summary

Record all deviations in SUMMARY.md under a "Deviations" section:

```markdown
## Deviations

During execution, the following deviations from PLAN.md were discovered and handled:

### Auto-fixed Issues
- [ISSUE]: [brief description] — [resolution]
- [ISSUE]: [brief description] — [resolution]

### Logged Enhancements  
- ISS-XXX: [enhancement description]
- ISS-YYY: [enhancement description]
```

**Rule:** Document the deviation, not the fix. "Added null check for user ID" not "Added if (userId) guard clause."

**Authentication gates are NOT deviations.** Document separately under "Authentication Gates" section.