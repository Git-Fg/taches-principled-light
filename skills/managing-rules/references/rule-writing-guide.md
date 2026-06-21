# Rule Writing Guide

How to write rules that Claude follows reliably. Good rules are actionable; bad rules invite misinterpretation.

## Anatomy of a Good Rule

```markdown
---
name: <short-name>
description: One sentence describing when this rule applies.
---

# Rule: <title>

**Why:** What problem this solves or what behavior it prevents.

## Rule

[Clear, direct statement of the required behavior]

## Bad / Good

**Bad:** [Vague or incorrect approach]
**Good:** [Correct approach with specific details]
```

## Actionability

Rules must give Claude enough to act on without ambiguity.

| Vague (avoid) | Actionable (prefer) |
|---------------|---------------------|
| "Be careful with authentication" | "Always validate JWT expiry before trusting user identity" |
| "Use proper error handling" | "Catch specific exceptions; never swallow errors silently" |
| "Follow best practices" | "Use early returns to avoid arrow code nesting beyond 3 levels" |

## Scope with `paths:`

Path scoping reduces always-on context. Apply it when a rule only matters for specific file types.

```yaml
---
name: <name>
description: <one sentence>
paths: "src/**/*.ts"
---

# TypeScript-specific rule content
```

Default (no `paths:`): loaded at every session start. Cost: always-on context.
With `paths:` — loaded only when matching file is edited. Cost: zero until needed.

**When to scope:**
- Rule is specific to a language or framework
- Rule applies only during certain phases (planning, testing)
- Rule is team-specific and not universal

**When NOT to scope:**
- Rule is a universal principle (e.g., "explain before acting")
- Rule governs behavior across all file types
- Rule is a meta-convention (how to write CLAUDE.md)

## Bad / Good Examples

Good rules include concrete contrast between wrong and right:

```markdown
**Bad:** Use a library for date handling.
**Good:** Use `date-fns` for date manipulation — never use `new Date()` arithmetic for range calculations.
```

```markdown
**Bad:** Write tests.
**Good:** Every exported function needs at least one happy-path test and one edge-case test.
```

## Length

- **Target: 20-50 lines.** Rules that exceed 100 lines have usually drifted into procedure or documentation.
- **One rule per file.** Separate concerns into separate `.claude/rules/` files.
- **Trim CLAUDE.md.** Move general principles to CLAUDE.md; put specifics in `.claude/rules/`.

## Priority Markers

Prefix rule titles to signal severity without creating fake severity systems:

- `MUST`: Non-negotiable correctness requirement
- `PREFER`: Recommended approach, acceptable to deviate with rationale
- `AVOID`: Anti-pattern to prevent

```markdown
# Rule: MUST validate external input before use
# Rule: PREFER early returns over nested conditionals
# Rule: AVOID premature abstraction
```

## Update Triggers

Rules become stale. Review when:
- Tool version changes invalidate assumptions
- Project tech stack shifts
- Errors repeat despite rules against them (rule unclear or wrong)
- New convention established that contradicts existing rule
