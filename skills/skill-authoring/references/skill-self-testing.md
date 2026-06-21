# Skill Self-Testing Reference

YAML validation, threshold checks, trigger testing, and quality verification for Claude Code skills before committing.

## Pre-Commit Checklist

Before shipping any skill, verify all of the following:

### Threshold Checks

| Metric | Limit | Tool/Method |
|--------|-------|-------------|
| Description length | ≤1,024 chars (max) | Count characters |
| Description length | ≤150 chars (recommended) | Count characters |
| when_to_use length | ≤200 chars | Count characters |
| Combined description + when_to_use | ≤1,536 chars | Count characters |
| SKILL.md body | ≤500 lines | `wc -l SKILL.md` |
| Skill name | ≤64 chars, kebab-case, no XML tags, no "claude"/"anthropic" | Manual review |

### Frontmatter Validation

```yaml
---
# Required
description: "What this skill does and when to use it"

# Recommended
when_to_use: "Additional trigger contexts (optional)"

# Conditional
disable-model-invocation: true  # Only if manual-only
user-invocable: false           # Only if auto-only
context: fork                   # Only if subagent execution
agent: Explore                  # Only if context: fork
allowed-tools:                  # Optional pre-approval
disallowed-tools:               # Optional restriction
skills:                         # Only for subagent preloading
```

### Invalid Fields (Must Not Appear)

- `metadata` — not a valid frontmatter field
- `related_skills` — not a valid frontmatter field
- `tags` — not a valid frontmatter field
- `version` — version comes from git, not file metadata

---

## Trigger Testing

### Headless Validation

Test whether a skill triggers on intended inputs:

```bash
# Test should-trigger cases
claude -p "implement login" --output-format stream-json 2>&1 | grep -i "skill-name"
claude -p "add authentication" --output-format stream-json 2>&1 | grep -i "skill-name"

# Test should-NOT-trigger cases
claude -p "what is the weather" --output-format stream-json 2>&1 | grep -i "skill-name"
# Should return nothing for this skill
```

### Test Set Construction

Build a test set with three categories:

| Category | Count | Purpose |
|----------|-------|---------|
| Should trigger | 5-10 | Real phrases users might say |
| Should NOT trigger | 3-5 | Edge cases that are related but wrong |
| Boundary cases | 2-3 | Ambiguous queries |

### Measuring Success

| Metric | Target | Interpretation |
|--------|--------|-----------------|
| Trigger rate | >90% | Routes correctly on intended inputs |
| False positive rate | <10% | Doesn't trigger on off-topic inputs |
| Boundary handling | Depends | Document expected behavior |

### Overfitting Detection

If the skill passes 100% on training cases but fails on held-out test cases, the skill is overfitted to the training phrases. Rebuild with genuinely different queries that test the same intent.

---

## YAML Validation

### Schema Structure

```yaml
---
# String fields
name: skill-name                    # Required, unique identifier
description: "Skill description"    # Required, routing signal

# Optional scalar fields
when_to_use: "Additional contexts"  # Optional exclusions
argument-hint: "[arg]"              # Autocomplete hint
disable-model-invocation: true      # Manual-only trigger
user-invocable: false               # Auto-only, hidden from /

# List fields
arguments: [arg1, arg2]             # Named positional args
allowed-tools: [Read, Write]        # Pre-approved tools
disallowed-tools: [Edit]            # Blocked tools

# Override fields
model: sonnet                      # Model override
effort: high                        # Effort level override

# Execution fields
context: fork                      # Subagent isolation
agent: Explore                      # Subagent type
hooks:                             # Lifecycle hooks
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./validate.sh"

# Scope fields
paths: ["src/**/*.ts"]              # File path globs
shell: bash                         # bash or powershell
```

### Common YAML Errors

| Error | Detection | Fix |
|-------|-----------|-----|
| Invalid YAML syntax | Parse error on load | Use scalar strings, not block scalars |
| Invalid field name | Unknown field ignored | Remove invalid fields |
| Wrong field type | Type mismatch | Check schema above |

---

## Anti-Pattern Quality

### Test Anti-Patterns

Every skill should have concrete wrong/right pairs that explain consequences:

| Wrong | Right | Consequence |
|-------|-------|-------------|
| "Helps with coding" | "Reviews Python code for security vulnerabilities" | Vague triggers nothing; specific routes correctly |
| "Use when writing Go" (too broad) | "Use when user adopts library/foo" | Restricts to single concern |
| Generic name "helper" | Domain noun "security-audit" | "helper" has no semantic anchor |

### Anti-Patterns Without Consequences

Anti-patterns without consequence explanations don't teach judgment. Always include why the wrong approach is problematic.

---

## Skill Category Verification

Verify the skill fits one of the five categories:

| Category | Test | Example |
|----------|------|---------|
| Constraint/Guardrail | Does this change default agent behavior? | "NEVER use console.log" |
| Orchestration | Does this define WHEN to delegate? | "When scope unclear → delegate to explorer" |
| Domain Expertise | Would plausible-but-wrong outputs result without this? | Company pricing logic |
| Quality Assurance | Does this define what evidence must exist? | "Before marking complete: tests pass" |
| Creative Direction | Does this prevent generic AI output? | "Reject generic aesthetics" |

---

## Security Audit

For skills that bundle scripts:

1. Review scripts for unexpected network calls
2. Verify no unauthorized system access
3. Check that dependencies are documented
4. Ensure scripts are deterministic

---

## Integration Testing

After validation, test the skill in context:

```bash
# Start a new session with the skill loaded
claude

# Test the skill directly
/skill-name test argument

# Test auto-trigger
# (say something that should match the description)
```

---

## Validation Output Format

When spawning a reviewer subagent to validate:

```json
{
  "findings": [
    {
      "severity": "HIGH|MEDIUM|LOW",
      "category": "threshold|yaml|routing|anti-pattern",
      "description": "What was found",
      "location": "file:line or field",
      "recommendation": "How to fix"
    }
  ],
  "summary": "Overall assessment",
  "blocking_issues": ["HIGH findings that must be fixed before commit"]
}
```

---

## Test Query Examples

### For a code review skill

**Should trigger:**
- "review this code"
- "check the PR"
- "look at my changes"
- "find bugs"
- "audit this"

**Should NOT trigger:**
- "write new code"
- "implement the feature"
- "what did I change"

**Boundary:**
- "improve the code"
- "make it faster"