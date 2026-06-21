# Roadmap Template

Copy and fill this structure for `docs/principled/plans/ROADMAP.md`:

**Naming:** Always `ROADMAP.md` in the `docs/principled/plans/` directory

```markdown
# Project Roadmap: [Project Name]

**Based on:** @docs/principled/plans/BRIEF.md
**Created:** YYYY-MM-DD
**Last Updated:** YYYY-MM-DD

---

## Vision

[Brief statement of what this project achieves and why it matters]

---

## Milestones

### v1.0 — [MVP Name] (Planned: QX YYYY)

**Goal:** [What this milestone delivers]

### v1.1 — [Feature Name] (Planned: QX YYYY)

**Goal:** [What this milestone delivers]

---

## Phases

### Phase 1: [Name] — [2-3 word description]

**Goal:** [What this phase accomplishes]
**Milestone:** v1.0
**Status:** [planned | in_progress | complete]

**Deliverables:**
- [ ] [Deliverable 1]
- [ ] [Deliverable 2]

**Exit Criteria:**
- [ ] [Measurable criterion]
- [ ] [Measurable criterion]

---

### Phase 2: [Name] — [2-3 word description]

**Goal:** [What this phase accomplishes]
**Milestone:** v1.0
**Status:** planned

**Deliverables:**
- [ ] [Deliverable 1]

**Exit Criteria:**
- [ ] [Measurable criterion]

---

### Phase 3: [Name] — [2-3 word description]

**Goal:** [What this phase accomplishes]
**Milestone:** v1.1
**Status:** planned

**Deliverables:**
- [ ] [Deliverable 1]

**Exit Criteria:**
- [ ] [Measurable criterion]

---

## Phase Dependencies

```
Phase 1 (Foundation)
    ↓
Phase 2 (Features)     [depends on: Phase 1 complete]
    ↓
Phase 3 (Polish)       [depends on: Phase 2 complete]
```

---

## Current Status

**Active Phase:** Phase 1
**Progress:** X of Y phases complete
**Last Activity:** YYYY-MM-DD

---

## Notes

[Any context, constraints, or decisions that affect the roadmap]
```

---

## Key Elements

- **Milestones** — Shipping targets (v1.0, v1.1) with dates
- **Phases** — Logical groupings of work within a milestone
- **Status** — Current state of each phase
- **Exit Criteria** — Measurable requirements to leave a phase
- **Dependencies** — Explicit ordering constraints

---

## Phase Naming Convention

Format: `{number}-{short-name}`

Examples:
- `01-foundation`
- `02-authentication`
- `03-core-features`
- `04-polish`
- `05-launch`

Phases sort alphabetically (number prefix ensures chronological order).

---

## Good Example

```markdown
# Project Roadmap: Checkout Redesign

**Based on:** @docs/principled/plans/BRIEF.md
**Created:** 2026-05-01

---

## Vision

Redesign the checkout flow to increase conversion rate and reduce cart abandonment.

---

## Milestones

### v1.0 — Launch Redesigned Checkout (Planned: Q2 2026)

**Goal:** 30% reduction in cart abandonment via streamlined checkout

---

## Phases

### Phase 1: foundation — Payment infrastructure

**Goal:** Establish payment processing foundation
**Milestone:** v1.0
**Status:** complete

**Deliverables:**
- [ ] Stripe integration
- [ ] Payment method UI components
- [ ] Error handling system

**Exit Criteria:**
- [ ] Stripe test mode working
- [ ] All card types supported

### Phase 2: checkout-flow — Core checkout UX

**Goal:** Implement streamlined checkout experience
**Milestone:** v1.0
**Status:** in_progress

**Deliverables:**
- [ ] Single-page checkout
- [ ] Address autocomplete
- [ ] Order summary sidebar

**Exit Criteria:**
- [ ] Checkout completes in < 3 steps
- [ ] Mobile responsive

---

## Phase Dependencies

```
Phase 1 (Foundation - complete)
    ↓
Phase 2 (Checkout Flow - in progress)
    ↓
Phase 3 (Polish)         [depends on: Phase 2]
```

---

## Current Status

**Active Phase:** Phase 2
**Progress:** 1 of 5 phases complete
**Last Activity:** 2026-05-15
```

---

## Anti-Patterns

### ❌ Vague phases

```
Phase 1: Do stuff
Phase 2: More stuff
```

Each phase needs a clear goal and specific deliverables.

### ❌ Missing dependencies

```
Phase 1: Auth
Phase 2: User Dashboard  # Depends on auth but not documented
```

Always document which phases depend on prior phases.

### ❌ No exit criteria

```
Phase 1: Implement feature X
```

How do you know when the phase is truly done? Include measurable exit criteria.