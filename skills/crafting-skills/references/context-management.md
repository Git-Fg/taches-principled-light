# Context Management Reference

<!-- check-citations-skip: this file's body quotes `references/patterns.md` as teaching examples for the WRONG/RIGHT citation rule. The cited path is a string inside the example, not a navigation pointer. -->

Context window principles, SKILL.md vs references/ load strategy, and progressive disclosure patterns for Claude Code skills.

## Context Loading Architecture

Claude Code has three context tiers that load at different times:

| Tier | What Loads | When | Cost |
|------|------------|------|------|
| **Level 1** | Frontmatter (description, when_to_use) | Always at startup | ~1% context per skill |
| **Level 2** | SKILL.md body | When skill is invoked | Full skill content |
| **Level 3** | references/* files | Only when cited by SKILL.md | Zero until accessed |

**Principle:** Skills share the context window with everything else. Every token competes. Progressive disclosure ensures essential routing loads cheaply; details load on demand.

---

## Progressive Disclosure Pattern

### Level 1 — Frontmatter (Always Loaded)

Frontmatter provides the routing signal. Keep it lean and precise.

```yaml
---
description: "Summarizes uncommitted changes and flags anything risky. Use when user asks what changed, wants a commit message, or asks to review their diff."
when_to_use: "Do NOT use when there are no uncommitted changes."
---
```

**Cap:** Combined `description` + `when_to_use` ≤ 1,536 characters. Front-load trigger phrases in first 200 chars.

### Level 2 — SKILL.md Body (On Invocation)

The skill body provides the mechanism. Keep it under 500 lines.

```markdown
## Current changes
!`git diff HEAD`

## Instructions
Summarize the changes above in two or three bullet points, then list any risks you notice such as missing error handling, hardcoded values, or tests that need updating.
If the diff is empty, say there are no uncommitted changes.
```

**Cap:** SKILL.md body ≤ 500 lines. If content exceeds this, split into multiple skills or move details to references/.

### Level 3 — References/ (On Demand)

Reference files provide deep detail only when SKILL.md explicitly mandates loading them. Reference files are **pure content** — they have no loading logic, no self-referential directives, no "When to Read" sections. The SKILL.md is the only router.

**Citation rule:** SKILL.md uses strict imperative citations:
- WRONG: "You can read references/patterns.md for examples"
- WRONG: "When to read this file: before..."
- RIGHT: "You MUST read `references/patterns.md` BEFORE writing code. Do not proceed or make assumptions without this file."

---

## When to Use References/

| Situation | Strategy | Why |
|-----------|----------|-----|
| Essential for every invocation | Put in SKILL.md body | Must always be available |
| Needed for edge cases (>20% of calls) | Put in SKILL.md body | Too frequent to load from reference |
| Needed for specific subtasks (~5-20%) | Reference in body | Progressive disclosure |
| Rarely needed (<5%) | Reference in body | Zero cost until accessed |
| Large schemas, extensive data | Always in references/ | Would bloat context |
| Scripts/automated tooling | Always in scripts/ | Never enters context |

---

## Context Budget Management

### The 1% Rule

Skill descriptions collectively must fit within ~1% of the model's context window (≈2,000 tokens / ≈8,000 chars at 200K context, per `code.claude.com/docs/en/settings` and `claudefa.st`'s v2.1.129 binary extraction). Truncation was **silent at v2.1.159** per `anthropics/claude-code#64606` (filed 2026-06-02 against v2.1.159; no warning, no log, no status indicator). Post-v2.1.159 releases added three **user-visible signals**: a startup warning (`Skill listing will be truncated` with `X%/Y% of context`), the `/doctor` command listing which skills were dropped, and a `Skills:` percentage line in `/context`. Selection is recency + frequency — most-invoked survives, least-invoked drops.

**Mitigation:**
1. Keep descriptions ≤150 characters
2. Put key triggers in first 200 characters
3. Use `when_to_use` for exclusions, not additions
4. Set low-priority skills to `"name-only"` in skillOverrides

### Compaction Behavior

When context fills up, Claude Code:
1. Summarizes the conversation
2. Re-attaches skills (first 5,000 tokens each, 25,000 combined budget)
3. Skills re-attach starting from most recently invoked

**Implication:** Only keep the most recently invoked skills fully loaded. Skills that haven't been used recently may be dropped entirely after compaction.

---

## Skill Content Lifecycle

When a skill is invoked:
1. The rendered SKILL.md content enters the conversation as a single message
2. It stays for the rest of the session
3. Claude Code does NOT re-read the file on later turns

**Implication:** Write standing instructions (should apply throughout a task) in SKILL.md, not one-time procedural steps.

---

## Context vs. Memory

| Mechanism | What it does | Scope |
|-----------|--------------|-------|
| Skill body | Loaded into active context | Per-session |
| Reference files | Loaded on demand via SKILL.md citation | Per-session |
| Agent memory | Persisted to disk | Cross-session |
| Project CLAUDE.md | Loaded at startup | Cross-session |

**Use skill content for session-specific guidance. Use agent memory for cross-session knowledge accumulation.**

---

## The Chicken-and-Egg Reference Anti-Pattern

**The Paradox:** Placing loading triggers or "When to read" instructions inside a reference file is a logical impossibility. The AI agent must consume the context tokens to read the file before it ever sees the instruction on whether it should have read it. If the agent reads the file because the trigger was satisfied, the trigger's condition is already fulfilled — making the condition self-referential and meaningless.

**Why it fails:**
1. The agent must load the reference file to see the "When to read" instruction
2. Loading the file consumes the very tokens the instruction is trying to govern
3. The instruction cannot prevent the agent from reading the file — by the time the agent sees the instruction, it has already read the file
4. Any conditional logic inside the reference file creates a circular dependency

**The strict rule:** Reference files must be pure content — no frontmatter, no loading triggers, no "When to read" sections, no conditional loading paragraphs. All conditional loading logic must reside exclusively in the parent SKILL.md router. The SKILL.md cites references imperatively; reference files never cite themselves or contain routing logic.

**Correct pattern:**
- SKILL.md body: "You MUST read `references/patterns.md` BEFORE writing code."
- references/patterns.md: Pure content, no loading instructions

**Wrong pattern (chicken-and-egg):**
- references/patterns.md: "When to read this file: before writing code" — LOGICAL IMPOSSIBILITY
- The agent reads the file to see the instruction; the instruction cannot prevent reading

---

## Skill-Internal File References

### Rule 1: Local Resolution
Any path written within a skill MUST resolve within that skill's own folder. A reference to `references/X.md` resolves to `skills/SKILL/references/X.md`.

### Rule 2: No Parent Traversal
File paths MUST NOT use `../` to traverse outside the skill directory. Skills are self-contained. If a skill needs a reference file used by another skill, it must have its own local copy or the reference must be merged. Cross-skill citations must be semantic ("See the [Name] skill") rather than path-based.

### Rule 3: Centralized Routing (SKILL.md only)
ONLY the main SKILL.md file is permitted to cite supporting files. Reference files (in `references/`, `agents/`, `templates/`, `scripts/` folders) must never cross-cite other reference files. The SKILL.md is the sole, centralized router for all internal citations.

---

## Common Mistakes

| Mistake | Result | Fix |
|---------|--------|-----|
| Use `../` to reach other skills | Brittle paths, breaks when moved | Use local paths only; cite skills by name |
| Put "When to Read" in reference files | Recursive loading logic, defeats lazy design | Reference files are pure content — only SKILL.md has loading logic |
| Put everything in SKILL.md | Context bloat, slow loading | Move details to references/ |
| Passive citations in SKILL.md | Ignored by LLM | Use strict imperatives with mandatory language |
| Overly long descriptions | Truncated mid-phrase, broken routing | ≤150 chars, front-load triggers |
| No progressive disclosure | High token cost always | Split at 500 lines or 7 tools |
| Cross-referencing references | Brittle dependency chain | SKILL.md is the only router |

---

## Validation Commands

Check if context is overflowing:

```bash
claude -p "What skills are available?" --output-format stream-json 2>&1 | grep -i skill
```

Run `/doctor` to see:
- Which skills are affected by budget overflow
- Skill description truncation status
- Recommendations for recovery