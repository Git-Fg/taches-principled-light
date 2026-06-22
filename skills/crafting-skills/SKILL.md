---
name: crafting-skills
description: >
  Load when creating a new agent skill from scratch or optimizing an existing
  skill's routing. Use when the user says 'create a skill', 'optimize this
  skill's routing', or 'validate frontmatter'. Do NOT use for collaborative
  skill creation dialogue (use superpowers' writing-skills).
allowed-tools: Read, Edit, Write, Grep, Glob
when_to_use: "Use when creating a new skill or optimizing an existing skill's routing."
argument-hint: "[create|optimize] [target-skill-path]"
license: MIT
---
# Crafting Skills

> **Overview.** A two-mode methodology for authoring and tuning agent skills. **CREATE** produces a new skill from scratch following the 6-step pipeline; **OPTIMIZE** audits and tightens an existing skill's routing without breaking its body. Both modes use the 14-rule Best-Practices Compendium in `references/best-practices-compendium.md` and the same pre-commit validation (§2.6).

> **Table of contents**
> - §1 Decision Router
> - §2 CREATE mode (6 steps)
> - §3 OPTIMIZE mode
> - §4 Best-Practices Compendium — pointer to `references/best-practices-compendium.md`
> - §5 Reference files

Two modes. Start here — the router tells you which path to take.

## Decision Router

IF the user wants to **create a new skill from scratch** → use **CREATE** mode below.
IF the user wants to **optimize an existing skill's routing** → use **OPTIMIZE** mode below.
IF unclear → ask: "Are you creating a new skill or improving an existing one?"

---

## CREATE Mode

*Author a new agent skill from scratch — description first, then body, then validate.*

### Step 1: Determine Scope

Skills live in one of two places. Default to local unless the user explicitly asks for global.

| Scope | Path | When |
|---|---|---|
| **Local** (default) | `.agents/skills/<skill-name>/` | This project only. Always start here. |
| **Global** | `~/.agents/skills/<skill-name>/` | User explicitly says "global", "every project", "all workspaces" |
| **Global (Claude Code)** | `~/.claude/skills/<skill-name>/` | User explicitly names this path |
| **Custom** | Any user-specified path | User gives an explicit path |

If the user says "create a skill for X" without specifying scope, create it locally in `.agents/skills/`. Only use global paths when the user says so explicitly.

### Step 2: Write Evals First

Before writing a single line of the skill, create three test categories:

1. **Should trigger (5-10 queries):** Real phrases users would say. Sample from production if available.
2. **Should NOT trigger (3-5 queries):** Adjacent but wrong domains. These are more valuable than positive examples.
3. **Forbidden loads:** Skills that must not load for this intent.

Example eval structure:
```json
{
  "skill": "processing-pdfs",
  "query": "Extract all text from this PDF and save it to output.txt",
  "expected_behavior": [
    "Reads the PDF using an appropriate library",
    "Extracts text from all pages without missing any",
    "Saves extracted text to output.txt"
  ]
}
```

### Step 3: Write the Description

The description is the hardest line in the skill. It is a **routing trigger** injected into the system prompt — not documentation. Every session pays its token cost.

**Template:**
```yaml
description: >
  Load when [user intent, 1 sentence]. Use when the user says [2-3 trigger
  phrases]. Do NOT use for [1-2 adjacent-but-wrong scenarios, referencing
  sibling skills by name].
```

**Rules:**
- Start with "Load when…" — this is the routing signal
- Target ≤50 words. Every word costs ~100 tokens per session, per user.
- Write in third person. "I" or "you" causes discovery problems.
- Include negative triggers. Reference sibling skills by exact name.
- Do NOT summarize the workflow. Describe user intent only.

**Example — Good:**
```yaml
description: >
  Load when extracting text and tables from PDF files, filling forms, or
  merging documents. Use when the user says 'extract from PDF', 'fill PDF
  form', or works with .pdf files. Do NOT use for spreadsheet analysis
  (use analyzing-spreadsheets) or image processing.
```

**Example — Bad:**
```yaml
description: Processes PDF files. Helps with documents.
```

### Step 4: Write the Body

Communicate workflows to an LLM, not a human colleague. The model already knows what git is, what PDFs are, how libraries work. Skip everything it already knows.

**Structure:**
```markdown
## Overview
[1-2 sentences on what this skill provides]

## Prerequisites
[Required tools, MCP servers, or context]

## Instructions
### Step 1: [First Action]
[Imperative. Concrete. Include the WHY behind requirements.]
### Step 2: [Next Action]

## Gotchas
- Do NOT [specific failure mode 1].
- MUST [constraint that prevents a known failure].

## Output Format
[Template or structure for results]
```

**Key rules:**
- **MUST, not should.** "MUST filter test accounts" not "always filter test accounts."
- **Third-person imperative.** "Extract the text…" not "You should extract…" or "I will extract…"
- **Don't railroad.** Prescribe intent and judgment, not exact command sequences. The agent needs room to recover when things go wrong.
  - ✓ `Cherry-pick the commit onto a clean branch. Resolve conflicts preserving intent.`
  - ✗ `git log --oneline; git checkout main; git checkout -b clean-branch; git cherry-pick abc123`
- **Gotchas are the highest-signal content.** Every time the agent fails, add a one-line gotcha. This section accrues the most value over time.
- **Keep SKILL.md under 500 lines.** Split heavy reference content into `references/`.
- **Progressive disclosure:** description → SKILL.md body → references/ (loaded only on demand).

### Step 5: Bundle Resources

```
skill-name/
├── SKILL.md              # Metadata + core instructions (<500 lines)
├── scripts/              # Deterministic code the agent runs, not reinvents
├── references/           # Heavy docs loaded only on demand (one level deep)
└── assets/               # Templates, schemas — copied and filled, not read
```

- **scripts/:** For fragile/repetitive operations where variation is a bug. Give the agent code to compose, not reconstruct.
- **references/:** Heavy documentation loaded only when a condition is met. "Read `references/api-errors.md` if the API returns non-200."
- **assets/:** Output templates the agent copies and fills. Keep JSON schemas, report templates, config stubs here.

### Step 6: Validate Before Shipping

You MUST run these checks before marking a skill complete:

1. **Discovery test:** Paste the description alone into a fresh LLM chat and ask: "Generate 3 prompts that should trigger this skill and 3 that should not." Verify the model's answers match your expectations.
2. **YAML validation:** Frontmatter parses without errors. `name` matches directory name exactly.
3. **Trigger test:** Run eval queries against the loaded skill. Measure precision (does it load when it should?) and recall (does it skip when it shouldn't?).
4. **File reference audit:** Every `references/X.md` or `scripts/Y.py` citation is a strict imperative ("You MUST read… BEFORE…"). No passive citations ("You can read…", "See reference…").

For pre-commit verification, spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review this skill through the lens of the Best-Practices Compendium below. Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix. Do NOT implement — identify what to change and why."
Loop until no HIGH findings remain.

---

## OPTIMIZE Mode

*Audit and tighten an existing skill's routing without breaking its body.*

### Step 1: Benchmark Current State

Run the existing description against evals:
1. **Should-trigger queries:** Does the skill load ≥90% of the time?
2. **Should-NOT-trigger queries:** Does the skill stay silent ≥90% of the time?
3. **Spillover check:** Does loading this skill cause any OTHER skill to stop triggering correctly?

### Step 2: Tighten

Apply these knobs based on symptoms:

| Symptom | Fix |
|---|---|
| Never triggers | Add "Use when user says 'X'" with explicit phrases |
| Triggers too often | Add negative trigger: "Do NOT use for…" |
| Triggers on wrong intent | Narrow the action verb. "Generating" vs "Reviewing" vs "Fixing" are different routing signals. |
| Too long (>50 words) | Cut everything the model already knows. Cut mode enumeration. Cut workflow summaries. |

### Step 3: Re-Validate

Run the same benchmark from Step 1. If metrics didn't improve, revert and try a different approach.
Small word changes in descriptions can have outsized impact on routing — including spillover effects on other skills.


## Best-Practices Compendium

You MUST read `references/best-practices-compendium.md` BEFORE applying Step 4 ("Write the Body") of CREATE mode, and BEFORE any audit in OPTIMIZE mode. The 14 rules (Descriptions, Naming, Body, Evidence) plus supporting reference material (skill anatomy, native tool referencing, split-vs-combine, common pitfalls, contrast) live there. Do not duplicate them inline.
