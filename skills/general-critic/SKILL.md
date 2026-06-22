---
name: general-critic
description: >
  Load when a plan, code change, document, decision, rule set, or other
  deliverable needs adversarial review before delivery. Use when the user asks
  to critique, audit, pressure-test, or review a completed artifact for factual
  errors, security issues, broken contracts, logic gaps, unsupported claims, or
  missing required sections. Do NOT use for bug diagnosis in running code (use
  systematic-debugging) or for architectural redesign (use restructuring-code).
when_to_use: |
  Use for completed artifacts that need a severity-rated critique before they
  are delivered. The review should be adversarial but grounded in the artifact
  and the user's stated criteria.
argument-hint: "[artifact-path] [evaluation-criteria]"
allowed-tools: Read
license: MIT
---

# General Critic

Use this skill when a deliverable needs a disciplined, adversarial review before
it reaches the user. The goal is not to rewrite the artifact; the goal is to
surface the issues that would make delivery unsafe, misleading, incomplete, or
confusing.

## Input

- First argument = path to the artifact to review (file or directory)
- Second argument = evaluation criteria or context for the review

## Decision Router

- If the artifact is code and the user is asking why it fails at runtime → do not use this skill; diagnose the bug directly.
- If the artifact is an architecture decision that needs restructuring → use `restructuring-code` or `reasoning-from-principles`.
- If the artifact is a completed plan, doc, decision, rules file, or spec → use this skill.
- If the user asks for a quick review without criteria → review for factual accuracy, security exposure, broken contracts, internal consistency, and missing required sections.

## Review Process

1. Read the full artifact at the given path.
2. Read the evaluation criteria or context.
3. Classify findings by severity:

### HIGH (block delivery)

- Factual errors, hallucinations, or incorrect claims
- Security vulnerabilities or exposed secrets
- Broken contracts, API mismatches, or missing required fields
- Logic errors that would cause runtime failures
- Violations of explicit project rules (AGENTS.md, CLAUDE.md, etc.)
- Missing required sections per template/spec

### MEDIUM (should fix)

- Incomplete coverage of edge cases or important failure modes
- Inconsistent style or formatting that reduces readability
- Ambiguous language that could lead to wrong implementation
- Duplicate or redundant content
- Weak evidence or unsupported claims
- Deviations from established patterns in the codebase

### LOW (nice to fix)

- Minor typos or grammar issues
- Slightly verbose sections
- Missing cross-references
- Formatting inconsistencies that do not affect comprehension

4. Output a structured report:

```markdown
## Critique Report: {artifact-path}

### HIGH ({count})
- [ ] Finding 1: {description} — {location}
- [ ] Finding 2: {description} — {location}

### MEDIUM ({count})
- [ ] Finding 1: {description} — {location}

### LOW ({count})
- [ ] Finding 1: {description} — {location}

### Verdict
{PASS | FAIL} — {summary}

### Next Steps
{If FAIL: "Re-run critic after fixes. Loop until no HIGH findings remain."}
{If PASS: "Ready for delivery."}
```

## Loop Protocol

If the user asks you to fix the artifact, apply the fixes, then rerun the same critique. Continue until the verdict is **PASS with zero HIGH findings**.

**Note for calling hubs:** The hub is responsible for managing re-spawning. After each critique cycle, read the verdict. If FAIL, spawn the critic again with the updated artifact. If PASS, return the result to the user.

## Anti-patterns to Avoid

- Do not flag style preferences as HIGH unless they violate explicit rules.
- Do not invent criteria that are not in the user's context.
- Do not skip reading the full artifact.
- Do not mark PASS if any HIGH findings remain.
- Do not rewrite the artifact unless the user asks for fixes.

## Contrast With Nearby Skills

- `reviewing-and-polishing` is for PR review, simplification, polishing, or learning capture; use `general-critic` when the user wants a standalone severity-rated critique.
- `reasoning-from-principles` is for first-principles decisions and evidence freshness; use `general-critic` when the artifact already exists and needs pressure-testing.
- `security` is for production security audits, dependency scans, and compliance checks; use `general-critic` for general artifact review with security as one severity category.
