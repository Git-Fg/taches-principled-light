# Cross-Skill Discovery Reference

Skill routing, description patterns, name conventions, and how Claude Code matches skills to tasks.

## How Skill Discovery Works

**Discovery is metadata-only.** Claude decides which skill to load based exclusively on the combined text of `description` and `when_to_use` pre-injected into its system prompt. At runtime, Claude Code appends `when_to_use` to `description`.

**Routing participants — combined signal:**
- `description` (Primary signal) + `when_to_use` (Extended catalog)
- **Combined Truncation:** The concatenated string is truncated at **1,536 characters** (configurable via `maxSkillDescriptionChars`).
- Agent `description` (NOT the body prompt)
- Command `description`

---

## Description Writing

### The Combined Metadata is a Routing Prompt

The `description` and `when_to_use` fields are merged at runtime into a single semantic signal.

| Field | Runtime Role | Character Budget |
|-------|-------------|------------------|
| `description` | Primary trigger signal. "What the skill does and when to use it." | Combined with `when_to_use` |
| `when_to_use` | Extended trigger catalog (phrases, scenarios, exclusions). | **Appended to `description`** |
| **Combined cap** | Concatenated string is truncated at the cap | **1,536 characters** |

### Optimal Description Pattern

**Order matters.** Front-load critical trigger phrases in `description` because if the combined text exceeds the cap, the tail (often the `when_to_use` block) is truncated first.

**Formula:**
```yaml
description: "[Verb] [artifact] for [domain]. Use when [primary trigger phrases]."
when_to_use: |
  - Use when [synonym expansion]
  - Do NOT use for [exclusion1], [exclusion2]
  - Example: "[example request]"
```

### Character Limits

| Field | Limit | Why |
|-------|-------|-----|
| description | ≤1,024 chars (max) | Official limit; survivors of truncation |
| description | ≤150 chars (recommended) | Ensures core signal survives high-context sessions |
| when_to_use | ≤1,000 chars (approx) | Part of the combined 1,536 cap |
| Combined | **1,536 chars** | Hard truncation limit in skill listing |

### Front-Loading Triggers

**Critical:** Put the most important keywords and the "Use when..." sentence in the first 150–400 characters of `description`. This is the "reliable activation band."

| Good (trigger at start) | Bad (trigger at end) |
|------------------------|---------------------|
| "Reviews code for bugs. Use when user says 'review', 'check', or 'audit'" | "This skill helps with reviewing code when you want to check for bugs and issues in your PRs and scattered files" |

---

## Trigger Keywords

### User Vocabulary Matters

Describe what the user says, not how the skill works internally:

| Instead of (internal) | Use (user vocabulary) |
|----------------------|----------------------|
| "Uses A3 methodology" | "Documents root causes" |
| "Complete test lifecycle" | "Writes tests first" |
| "Implements CQRS pattern" | "Splits read/write operations" |

### Specific Phrases Over Generic Words

| Generic (triggers everything) | Specific (triggers correctly) |
|------------------------------|------------------------------|
| "improve" | "optimize query performance" |
| "fix" | "fix null pointer" |
| "help" | (avoid entirely) |
| "handle" | "handle authentication errors" |

### Number of Triggers

Include 3-10 specific trigger phrases. Fewer than 3 may miss legitimate uses; more than 10 dilutes signal.

---

## CONTRAST Sections

For skills in overlapping domains, add explicit negative cases:

```yaml
description: "Generates test cases. Use when user asks to 'write tests', 'add test coverage', or 'generate tests'."
when_to_use: |
  Do NOT use for running existing tests or test execution.
```

---

## Name Conventions

### Skill Names

- **Format:** kebab-case, lowercase letters and hyphens only
- **Max length:** 64 characters
- **Forbidden:** XML tags, "claude", "anthropic"
- **Content:** Semantic noun describing what the skill does

| Wrong | Right |
|-------|-------|
| "Helper" | "code-review" |
| "DoTheThing" | "deploy-staging" |
| "complex-workflow-skill" | "plan-execution" |

### Name vs. Description

The name (directory name) sets the command. The `name` frontmatter field sets the display label.

| Location | Name Source | Example |
|----------|-------------|---------|
| `~/.claude/skills/deploy/` | Directory name | `/deploy` |
| `.claude/commands/deploy.md` | File name | `/deploy` |
| `skills/review/SKILL.md` in plugin `my-plugin` | Directory name, namespaced | `/my-plugin:review` |

---

## Routing Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|--------------|--------------|-----|
| Everything in `description` | Bloats primary signal, wastes budget | Move extended catalogs to `when_to_use` |
| Vague description, no `when_to_use` | No semantic signal to match against | Add "Use when..." phrases |
| Redundant keyword stuffing | Wastes character budget | Use 3-5 high-signal synonyms |
| Critical triggers at the end | Truncated by the 1,536-character cap | Front-load in `description` |
| Technical jargon | User won't use it in prompts | Use user vocabulary |
| No negative cases | False positives | Add exclusions in `when_to_use` |

---

## Decision Matrix: `description` vs `when_to_use`

| Situation | Use `description` | Use `when_to_use` |
|-----------|-------------------|-------------------|
| One-liner summary of capability | ✅ Yes | ❌ No |
| Primary "Use when..." trigger sentence | ✅ Yes | ❌ No |
| 3–5 core high-signal synonym verbs | ✅ Yes | ⚠️ Optional |
| Extended bullet list of scenarios | ❌ No | ✅ Yes |
| Negative triggers / exclusions | ❌ No | ✅ Yes |
| File-type or path-specific rules | ❌ No | ✅ Yes |
| Example user requests | ❌ No | ✅ Yes |
| Content that MUST survive truncation | ✅ Yes | ❌ No (tail risk) |

---

## Routing Validation

### Test Pattern

```bash
# Should match - test multiple phrasings
claude -p "generate a presentation" --output-format stream-json 2>&1 | grep -i "skill-name"
claude -p "make slides" --output-format stream-json 2>&1 | grep -i "skill-name"

# Should NOT match - test false positives
claude -p "what is the weather" --output-format stream-json 2>&1 | grep -i "skill-name"
```

### The Trigger Testing Loop

1. Write candidate description
2. Test with 10+ queries (5 should trigger, 5 should not)
3. Analyze misses and false positives
4. Refine description
5. Repeat until trigger rate >90%, false positive rate <10%

---

## Skill Interaction Patterns

### Hub Skills

Skills that dispatch to internal modes should name the modes explicitly:

```yaml
---
description: "Create or refine project plans. Use when user says 'make a plan', 'plan this', or 'sketch a roadmap'."
---
## Routing

IF creating → load CREATE mode
IF refining → load REFINE mode
```

### Compositional Pairs

Pairs that create then execute should be clearly named:

| Create | Execute |
|--------|---------|
| `plan-lifecycle` | `task-lifecycle` |
| `task-lifecycle` (REFINE mode) | `task-lifecycle` (IMPLEMENT mode) |

### Cross-Skill References

When referencing other skills in body text, use the skill name (not the file path):

| Wrong | Right |
|-------|-------|
| "use the skill-authoring skill for guidance" | "use the skill-authoring skill for guidance" |

---

## Skill Discovery Limitations

### Nesting Limit

Automatic discovery scans only 1 level deep. Skills nested 2+ levels deep require manual Glob scanning:

| Structure | Discoverable | Notes |
|-----------|-------------|-------|
| `skills/skill-name/SKILL.md` | Yes | Standard |
| `skills/category/skill-name/SKILL.md` | **No** | 2 levels deep, requires manual scan |

### Discovery Timing

- Skills load at session start
- Edits to skill files take effect within current session
- New skill directories require session restart to be watched

---

## Skill Priority

When multiple skills could match, Claude Code resolves by:

1. **Enterprise** (org-wide) — highest priority
2. **Personal** (`~/.claude/skills/`)
3. **Project** (`.claude/skills/`)
4. **Plugin** (`skills/` directory) — lowest priority

Plugin skills use namespace prefix to prevent conflicts: `/my-plugin:skill-name`