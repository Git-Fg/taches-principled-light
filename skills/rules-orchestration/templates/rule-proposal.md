# Rule Proposal

**Created:** {date}
**Mode:** {ANALYZE|ADD|RESTRUCTURE|REVIEW|SYNC}
**Status:** pending | approved | rejected | auto-integrated

---

## Proposals

### Rule: {short title}

**Category:** TECHNICAL | PROCESS | PATTERN | ANTI-PATTERN | DECISION
**Priority:** critical | important | nice-to-have
**Target:** CLAUDE.md | `.claude/rules/<name>.md`
**Source:** {plan-id or conversation context}

**Insight:** {One sentence capturing the learning or observation}

**Rule text:**
```markdown
---
name: {short-name}
description: {One sentence describing when this rule applies.}
paths: "**/*.{ext}"  {# remove if not path-scoped #}
---

# Rule: {title}

**Why:** {What problem this solves or prevents}

{Direct, actionable rule statement}

**Bad:** {Vague or incorrect approach}
**Good:** {Correct approach with specifics}
```

**Rationale:** {Why this belongs in the project rules}

---

## Review Notes

**Conflicts checked:** {yes|no}
**Existing rule overlap:** {none|conflict found — see below}
**Notes:** {additional context}

---

## Deduplication Checklist

- [ ] Searched existing rules for topic overlap
- [ ] No duplicate rule text found
- [ ] No contradicting rule found
- [ ] Placement decision made (CLAUDE.md vs .claude/rules/)
