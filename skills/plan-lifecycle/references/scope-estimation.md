# Scope Estimation & Quality-Driven Plan Splitting

## Sections
- [The Quality Degradation Curve](#the-quality-degradation-curve)
- [Target: 50% Context Maximum](#target-50-context-maximum)
- [The 2-3 Task Rule](#the-2-3-task-rule)
- [Signals to Split](#signals-to-split)
- [Splitting Strategies](#splitting-strategies)
- [Estimating Context Usage](#estimating-context-usage)
- [The Atomic Commit Philosophy](#the-atomic-commit-philosophy)
- [Summary](#summary)

---

## What is Context Usage?

Context usage is measured in **tokens** — the input capacity for the AI model.

**How to measure:**
- Claude Code shows context bar in UI (~X% remaining)
- CLI: `claude -p` shows token estimates in verbose mode
- Rough formula: 1 line of code ≈ 10-15 tokens; 1 file reference ≈ 50-100 tokens

**Why tokens matter:**
- Quality degrades when >50% context used
- Planning/implementation quality drops as context fills
- Subagent spawn prompts compete with workspace tokens

---

Plans must maintain consistent quality from first task to last. This requires understanding the quality degradation curve and splitting aggressively to stay in the peak quality zone.

---

## The Quality Degradation Curve

**Critical insight:** Claude doesn't degrade at arbitrary percentages—it degrades when it perceives context pressure and enters "completion mode."

Three signals indicate context is degrading quality before hitting hard limits:

| Signal | What Happens | Prevention |
|--------|-------------|------------|
| **Lost-in-middle effect** | Attention weakens for mid-context content | Put critical info at start/end of context |
| **Attention scarcity** | Too many competing items in context | Aggressive prioritization |
| **Context poisoning** | Irrelevant content displaces useful content | Strict context hygiene |

```
Context Usage  │  Quality Level   │  Mental State
─────────────────────────────────────────────────────
0-30%          │  PEAK           │  "I can be thorough"
               │                  │  No anxiety, full detail

30-50%         │  GOOD           │  "Still have room"
               │                  │  Engaged, confident

50-70%         │  DEGRADING      │  "Getting tight"
               │                  │  Efficiency mode begins

70%+           │  POOR           │  "Running out"
               │                  │  Rushed, minimal
```

**The 40-50% inflection point:**

This is where quality breaks. Claude sees context mounting and thinks "I'd better conserve now." Result: "I'll complete the remaining tasks more concisely."

**The fundamental rule:** Stop BEFORE quality degrades, not at context limit.

---

## Target: 50% Context Maximum

**Plans should complete within ~50% of context usage.**

Why 50% not 80%?
- Huge safety buffer
- No context anxiety possible
- Quality maintained from start to finish
- Room for unexpected complexity
- Space for iteration and fixes

**If you target 80%, you're planning for failure.** By the time you hit 80%, you've already spent 40% in degradation mode.

---

## The 2-3 Task Rule

**Each plan should contain 2-3 tasks maximum.**

Why this number?

**Task 1 (0-15% context):** Fresh context, peak quality, comprehensive implementation
**Task 2 (15-35% context):** Still in peak zone, quality maintained
**Task 3 (35-50% context):** Beginning to feel pressure, natural stopping point
**Task 4+ (50%+ context):** DEGRADATION ZONE—should have split before this

**The principle:** Each task is independently committable. 2-3 focused changes per commit creates surgical git history.

---

## Signals to Split

### Always Split If:

1. **More than 3 tasks** — Even if tasks seem small, each additional task increases degradation risk

2. **Multiple subsystems**
   ```
   ❌ Bad (1 plan):
   - Database schema (3 files)
   - API routes (5 files)
   - UI components (8 files)
   Total: 16 files, 1 plan → guaranteed degradation

   ✅ Good (3 plans):
   - 01-01-PLAN.md: Database schema (2 tasks)
   - 01-02-PLAN.md: API routes (3 tasks)
   - 01-03-PLAN.md: UI components (2 tasks)
   ```

3. **Any task with >5 file modifications** — Large tasks burn context fast, split by file groups

4. **Research + implementation** — Research produces FINDINGS.md (separate plan), implementation consumes it (separate plan)

### Consider Splitting If:

1. **Estimated >5 files modified total** — Context from reading existing code adds up faster than expected

2. **Complex domains (auth, payments, data modeling)** — Burns more context per task, split more aggressively

3. **Any uncertainty about approach** — "Figure out X" phase separate from "implement X"

4. **Natural semantic boundaries** — Setup → Core → Features

**Also watch for:**
- Sequential dependency chain >8 tasks — parallelization opportunity lost
- If a chain exceeds 8 tasks, split into multiple plans with checkpoint between

---

## Splitting Strategies

### By Subsystem

**Phase:** "Authentication System"
```
- 03-01-PLAN.md: Database models (User, Session tables + relations)
- 03-02-PLAN.md: Auth API (register, login, logout endpoints)
- 03-03-PLAN.md: Protected routes (middleware, JWT validation)
- 03-04-PLAN.md: UI components (login form, registration form)
```

### By Dependency

**Phase:** "Payment Integration"
```
- 04-01-PLAN.md: Stripe setup (env vars, test mode)
- 04-02-PLAN.md: Subscription logic (plans, checkout)
- 04-03-PLAN.md: Frontend integration (pricing page, payment flow)
```

Later plans depend on earlier completion. Sequential execution, fresh context each time.

### By Complexity

**Phase:** "Dashboard Buildout"
```
- 05-01-PLAN.md: Layout shell (simple: sidebar, header, routing)
- 05-02-PLAN.md: Data fetching (moderate: API integration)
- 05-03-PLAN.md: Data visualization (complex: charts, tables)
```

---

## Estimating Context Usage

### File Counts
- 0-3 files modified: Small task (~10-15% context)
- 4-6 files modified: Medium task (~20-30% context)
- 7+ files modified: Large task (~40%+)—split this

### Complexity
- Simple CRUD: ~15% per task
- Business logic: ~25% per task
- Complex algorithms: ~40% per task
- Domain modeling: ~35% per task

### 2-Task Plan (Safe)
- 2 simple tasks: ~30% total ✅
- 2 medium tasks: ~50% total ✅
- 2 complex tasks: ~80% total ❌ Too tight, split

### 3-Task Plan (Risky)
- 3 simple tasks: ~45% total ✅
- 3 medium tasks: ~75% total ⚠️ Pushing it
- 3 complex tasks: 120% total ❌

**Conservative principle:** When in doubt, split. Better to have an extra plan than degraded quality.

---

## The Atomic Commit Philosophy

**What we're optimizing for:** Beautiful git history where each commit is:
- Focused (2-3 related changes)
- Complete (fully implemented, tested)
- Documented (clear commit message)
- Reviewable (small enough to understand)
- Revertable (surgical rollback possible)

**Bad git history (large plans):**
```
feat(auth): Complete authentication system
- Added 16 files, modified 8 files
- 1200 lines changed
```
Impossible to review, hard to understand, can't revert without losing everything.

**Good git history (atomic plans):**
```
feat(auth-01): Add User and Session database models
feat(auth-02): Implement register and login API endpoints
feat(auth-03): Add protected route middleware
feat(auth-04): Build login and registration forms
```

Each commit tells a story. Each is reviewable. Each is revertable.

---

## Summary

**Old way (3-6 tasks, 80% target):**
- Tasks 1-2: Good
- Tasks 3-4: Degrading
- Tasks 5-6: Poor
- Quality: Inconsistent

**New way (2-3 tasks, 50% target):**
- All tasks: Peak quality
- Git: Atomic, surgical commits
- Quality: Consistent excellence

**The principle:** Aggressive atomicity. More plans, smaller scope, consistent quality.

**The rule:** If in doubt, split. Quality over consolidation. Always.
