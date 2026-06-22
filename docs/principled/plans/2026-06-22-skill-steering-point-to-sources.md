# Skill Steering — Point to Live Sources — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add two new rules to the `crafting-skills` Best-Practices Compendium (Rule 15 "point to live sources, don't inline them" + Rule 16 "post-creation observation is part of the skill") and two new modes to `crafting-skills` (REVIEW static critique + POST-CREATE immediate-use observation), so AI agents authoring skills cite external sources instead of inlining their content.

**Architecture:** Pure skill-content edits. Two files touched: (1) `skills/crafting-skills/references/best-practices-compendium.md` gets Rule 15 (with antipattern pitfall row) + Rule 16 inserted between current rules 14 and the Skill Anatomy section. (2) `skills/crafting-skills/SKILL.md` gets frontmatter updates (description, argument-hint, allowed-tools), a Decision Router expansion (2 new IF branches), and 2 new mode sections (POST-CREATE then REVIEW, each ~35 lines), plus 2 CONTRAST additions. Total: ~115 lines added. No code, no new files, no new directories.

**Tech Stack:** Markdown, marketplace-validator (Python), routing_test.py (Python), git. No application logic — pure skill-content edits.

**Spec:** `docs/principled/specs/2026-06-22-skill-steering-point-to-sources.md` (committed at `2f4bb41`)

**Self-review note:** The plan implements all 9 sections of the spec. Tasks 1–2 cover Section 1 (Rules 15–16 + pitfall row). Tasks 3–7 cover Section 4 (frontmatter, router, POST-CREATE, REVIEW, CONTRAST). Task 8 covers Section 7 (verification). Sections 2 and 3 of the spec are content that lives INSIDE Tasks 6 and 7 respectively, not separate tasks. Section 5 ("What this does NOT do") is a guardrail honored implicitly. Section 8 (Decisions made) is honored verbatim in the mode text.

---

## File structure

| File | Action | What it does |
|---|---|---|
| `skills/crafting-skills/references/best-practices-compendium.md` | Modify (insert after Rule 14) | Adds Rule 15 (point to live sources, don't inline) + Rule 16 (post-creation observation is part of the skill) + pitfall row "Inlined-source skill" |
| `skills/crafting-skills/SKILL.md` | Modify (frontmatter + Decision Router + 2 new modes + CONTRAST) | Adds POST-CREATE and REVIEW modes + updates router and CONTRAST block |

`crafting-skills/SKILL.md` grows from 199 → ~290 lines (under the 500-line cap).

**Important:** The 14-rule Compendium becomes a 16-rule Compendium. All downstream references to "the 14-rule Compendium" should be updated to "16-rule" if any exist (none found in this repo as of `2f4bb41`).

---

## Task 1: Add Rule 15 + pitfall row to the Compendium

**Files:**
- Modify: `skills/crafting-skills/references/best-practices-compendium.md` — insert new section after Rule 14 (currently ends at line 52) and add a new row in the Common Pitfalls table (currently ends at line 125)

**Step 1.1 — Read the current file end of Rule 14 + Common Pitfalls table area**

Run: `sed -n '50,55p;120,128p' skills/crafting-skills/references/best-practices-compendium.md`
Expected: Shows line 52 ("14. **Moderate-length..."), lines 53–55 ("---", "## Skill Anatomy"), and the Common Pitfalls table ending at line 125 with the "Uniform-imperative skill" row.

**Step 1.2 — Insert Rule 15 after Rule 14**

Find this text at the end of Rule 14 (line 52):

```
14. **Moderate-length Skills outperform comprehensive ones.** There is a sweet spot beyond which more tokens hurt performance. Be concise, not exhaustive (SkillsBench §4.2.2).

---
```

Replace it with:

```
14. **Moderate-length Skills outperform comprehensive ones.** There is a sweet spot beyond which more tokens hurt performance. Be concise, not exhaustive (SkillsBench §4.2.2).

15. **Point to live sources, don't inline them.** Skills MUST cite the source of information instead of recreating it in the skill body. Three categories:

    | Category | What it is | Citation form | Example |
    |---|---|---|---|
    | **Dynamic** | CLIs, libraries, web APIs, `--help` output | Imperative command + `BEFORE` | `You MUST run \`agent-browser skills get core\` BEFORE running any \`agent-browser\` command.` |
    | **Static intra-skill** | `references/X.md`, `scripts/Y.py`, `assets/Z.json` | Audience-aware imperative (Rule 4) | `You MUST read \`references/execute.md\` BEFORE writing the invocation.` |
    | **Cross-skill** | Other marketplace skills (`evaluating-skills`, `general-critic`, etc.) | `read and apply` (canonical verb form) | `You MUST read \`evaluating-skills\` and apply its protocol BEFORE running the post-creation loop.` |

    Cross-skill references MUST use the canonical verb form: **"read and apply"**. (Variations like "consult and follow" or "read the protocol" are acceptable synonyms but "read and apply" is canonical.)
    - "Load" and "delegate to" are wrong for skills. A skill is NOT a subagent — it is an injection of context/protocol the agent reads and applies directly. Using subagent verbs ("load", "delegate") makes the agent spawn unnecessary subagents or skip reading altogether.
    - "MUST" for INTERNAL contracts (file references, subagent prompt contracts, command citations, cross-skill protocol citations).
    - Descriptive (`describes`, `shows`, `is for`, `consult when`) for EXTERNAL framing.

    The test for every paragraph in a skill body, applied in order:
    1. *Does the agent need this fact?* If no → delete (Rule 10).
    2. *Can the agent load this content on demand?* If yes → cite, don't inline (Rule 15).
    3. *Is the citation INTERNAL (contract) or EXTERNAL (framing)?* Encode audience in the verb form (Rule 4 + Rule 7).
    4. *Is this content already cited elsewhere in the skill?* If yes → deduplicate, do not repeat.

    The antipattern this rule prevents: the agent inlining a 30-line summary of the agent-browser command reference because it doesn't trust the model to run `agent-browser skills get core` at runtime. The trust bet is wrong — the agent can and will run the command; the inlined content rots on first CLI release.

---
```

**Step 1.3 — Add the "Inlined-source skill" row to the Common Pitfalls table**

Find this row (line 125) in the Common Pitfalls table:

```
| Uniform-imperative skill | Apply MUST to INTERNAL contracts only; relax to descriptive for EXTERNAL framing. Reading 8 rows of "You MUST…" is fatiguing and dilutes the imperative signal. |
```

Replace it with (note the new row added AFTER it):

```
| Uniform-imperative skill | Apply MUST to INTERNAL contracts only; relax to descriptive for EXTERNAL framing. Reading 8 rows of "You MUST…" is fatiguing and dilutes the imperative signal. |
| Inlined-source skill | Apply Rule 15: cite the source by command/path/name instead of inlining CLI flags, library APIs, or other-skill content. The antipattern is the agent re-writing the agent-browser command reference inline instead of `agent-browser skills get core`. |
```

**Step 1.4 — Run the marketplace validator**

Run: `python3 .agents/skills/marketplace-validator/scripts/validate.py skills/crafting-skills/`
Expected: exit 0, no failures. Warnings about `when_to_use` and `argument-hint` and description word-count are pre-existing and acceptable (4 warnings expected, not 5+).

**Step 1.5 — Commit**

```bash
git add skills/crafting-skills/references/best-practices-compendium.md
git commit -m "docs(crafting-skills): rule 15 — point to live sources, don't inline them"
```

---

## Task 2: Add Rule 16 to the Compendium

**Files:**
- Modify: `skills/crafting-skills/references/best-practices-compendium.md` — insert Rule 16 immediately after Rule 15 (which was just added in Task 1)

**Step 2.1 — Find the current end of Rule 15 (just inserted in Task 1)**

Run: `grep -n "## Skill Anatomy" skills/crafting-skills/references/best-practices-compendium.md`
Expected: Returns the line where the Skill Anatomy section starts. Rule 16 must be inserted immediately before that line.

**Step 2.2 — Insert Rule 16 before the "## Skill Anatomy" header**

Find this text (the closing `---` of Rule 15 followed by the Skill Anatomy header):

```

---

## Skill Anatomy
```

Replace it with:

```

16. **Post-creation observation is part of the skill.** Skills are written once and used many times. The cost of a skill that drifts out of sync with reality grows with each use. A skill MUST support an observation loop:
    - The author MUST design the skill so that what happens during use can be observed (transcripts, gotcha occurrences, friction points, agent rationalizations).
    - The skill MUST include a path to propose updates based on observed behavior — concretely, **POST-CREATE mode** in `crafting-skills`.
    - A skill that is "fire and forget" accumulates debt. A skill that observes-and-improves stays accurate.

    If the skill is for an offline workflow with no transcript available, the author MUST document that explicitly and provide the next-best feedback path (e.g., a `references/feedback.md` template the user fills in).

---

## Skill Anatomy
```

**Step 2.3 — Verify both rules present**

Run: `grep -nE "^(15|16)\. \*\*" skills/crafting-skills/references/best-practices-compendium.md`
Expected: Two lines: `15. **Point to live sources, don't inline them.**` and `16. **Post-creation observation is part of the skill.**`

**Step 2.4 — Run the marketplace validator**

Run: `python3 .agents/skills/marketplace-validator/scripts/validate.py skills/crafting-skills/`
Expected: exit 0, same warnings as Task 1 (no new failures).

**Step 2.5 — Commit**

```bash
git add skills/crafting-skills/references/best-practices-compendium.md
git commit -m "docs(crafting-skills): rule 16 — post-creation observation is part of the skill"
```

---

## Task 3: Update `crafting-skills/SKILL.md` frontmatter + Decision Router

**Files:**
- Modify: `skills/crafting-skills/SKILL.md` — frontmatter (lines 2–12) and Decision Router (lines 26–30)

**Step 3.1 — Read the current frontmatter + Decision Router**

Run: `sed -n '2,12p;26,30p' skills/crafting-skills/SKILL.md`
Expected: Shows the YAML frontmatter (description, allowed-tools, when_to_use, argument-hint, license) and the 5-line Decision Router block.

**Step 3.2 — Update the frontmatter description**

Find this text at lines 2–8:

```yaml
description: >
  Load when creating a new agent skill from scratch or optimizing an existing
  skill's routing. Use when the user says 'create a skill', 'optimize this
  skill's routing', or 'validate frontmatter'. Do NOT use for collaborative
  skill creation dialogue (use superpowers' writing-skills).
allowed-tools: Read, Edit, Write, Grep, Glob
```

Replace it with:

```yaml
description: >
  Load when creating, optimizing, reviewing, or post-iterating an agent skill.
  Use when the user says 'create a skill', 'review this skill', 'self-review',
  'I just used it — propose updates', or 'validate frontmatter'. Do NOT use for
  collaborative skill creation dialogue (use superpowers' writing-skills).
allowed-tools: Read, Edit, Write, Grep, Glob, Agent
```

**Step 3.3 — Update the argument-hint**

Find this text at line 10:

```
argument-hint: "[create|optimize] [target-skill-path]"
```

Replace it with:

```
argument-hint: "[create|optimize|review|post-create] [target-skill-path]"
```

**Step 3.4 — Update the Decision Router**

Find this text at lines 26–30:

```
IF the user wants to **create a new skill from scratch** → use **CREATE** mode below.
IF the user wants to **optimize an existing skill's routing** → use **OPTIMIZE** mode below.
IF unclear → ask: "Are you creating a new skill or improving an existing one?"
```

Replace it with:

```
IF the user wants to **create a new skill from scratch** → use **CREATE** mode below.
IF the user wants to **optimize an existing skill's routing** → use **OPTIMIZE** mode below.
IF the user wants to **statically critique an existing skill** (per compendium rules) → use **REVIEW** mode below.
IF the user wants to **observe what happened during immediate post-creation use and propose edits** → use **POST-CREATE** mode below.
IF unclear → ask: "Are you creating, optimizing, reviewing, or post-creating a skill?"
```

**Step 3.5 — Verify description word count**

Run: `python3 -c "import re; d=open('skills/crafting-skills/SKILL.md').read(); m=re.search(r'description:.*?(?=allowed-tools:|\Z)', d, re.S); txt=' '.join(m.group(0).split()); print(f'words={len(txt.split())}')"`
Expected: `words=46` or `words=47` (≤50 per Rule 3). If higher, the description has been modified during implementation — re-edit to compress.

**Step 3.6 — Run the marketplace validator**

Run: `python3 .agents/skills/marketplace-validator/scripts/validate.py skills/crafting-skills/`
Expected: exit 0. Description word-count warning will appear if word count > 50 (acceptable but try to keep ≤50).

**Step 3.7 — Commit**

```bash
git add skills/crafting-skills/SKILL.md
git commit -m "docs(crafting-skills): frontmatter + router — REVIEW, POST-CREATE modes"
```

---

## Task 4: Add POST-CREATE mode to `crafting-skills/SKILL.md`

**Files:**
- Modify: `skills/crafting-skills/SKILL.md` — insert new section after the OPTIMIZE mode (currently ends at line 195, before the "## Best-Practices Compendium" header at line 197)

**Step 4.1 — Find the insertion point**

Run: `grep -n "^## Best-Practices Compendium" skills/crafting-skills/SKILL.md`
Expected: Returns `197:## Best-Practices Compendium` (line number may shift ±2 after Task 3 commits; locate by content).

**Step 4.2 — Insert POST-CREATE mode**

Find this text (the end of OPTIMIZE mode followed by the Best-Practices Compendium header):

```


## Best-Practices Compendium
```

Replace it with:

```


## POST-CREATE Mode

*Observe what happened during the user's immediate use of a freshly-created skill and propose 3-5 targeted edits.*

**Trigger.** A skill was just created (CREATE mode completed) AND the user is about to use it or has just used it in the same session. The trigger is *behavioral*, not by a fixed timer: the agent watches for the signal "the user is now running the skill we just wrote" and proposes POST-CREATE once.

**Step 1 — Confirm scope.** Ask: "Do you want me to (a) read transcripts of the just-completed use if any exist, or (b) accept your verbal summary of friction points?" If transcripts are available (Claude Code JSONL, kimi-code session, etc.), prefer them.

**Step 2 — Read the skill and the use.** Read the `SKILL.md` + the transcript or summary. For each tool call the agent made, ask: "Did the skill predict this? If yes, PASS. If no, classify (Step 3)."

**Step 3 — Diff against the skill.** For each unpredicted behavior, classify:

| Class | Symptom | Proposed edit |
|---|---|---|
| **Missed gotcha** | Agent failed in a way the skill should have warned against | Add one-line gotcha to the skill's `## Gotchas` section |
| **Trigger miss** | Skill loaded when it shouldn't have, or didn't load when it should | Tighten description: add `Use when`, add `Do NOT use for` |
| **Inlined content** (Rule 15 violation) | Agent recreated content that lives in a CLI/library/other-skill | Replace paragraph with imperative citation |
| **Stale instruction** | Skill said X but the underlying tool/library has changed | Update to current behavior |
| **Friction** | Agent struggled but recovered — procedure worked, UX didn't | Add a hint or example to the relevant step |

**Step 4 — Propose 3-5 targeted edits.** For each finding, write the proposed edit with file:line and exact text. Do NOT apply without user confirmation. Group by class. Order by impact (HIGH first).

**Step 5 — Apply and validate.** User confirms which of the 3-5 proposed edits to apply (any subset, including all-or-none). Write only the confirmed edits → run `python3 .agents/skills/marketplace-validator/scripts/validate.py <skill_dir>/` → if 0 failures, commit each applied edit with `docs(<skill-name>): post-create <class> from <date>` message (one commit per edit, or grouped if multiple edits of the same class). If validator finds warnings, surface them and ask whether to fix. Do NOT commit if any edit was rejected — rejected findings are kept in the report for future POST-CREATE invocations.

**Contrast (do not confuse with):**
- `evaluating-skills` RUN mode — heavyweight behavioral loop with separate transcripts, multiple iterations, statistical aggregation. POST-CREATE is *lightweight and immediate* — same session, no separate harness, 3-5 edits.
- `evaluating-skills` ITERATE (Stage 7) — same goal (rewrite skill from observed behavior) but driven by formal evals. POST-CREATE is driven by what just happened in the current session.
- REVIEW mode — looks at the skill statically. POST-CREATE looks at what the agent *did* with the skill.


## Best-Practices Compendium
```

**Step 4.3 — Run the marketplace validator**

Run: `python3 .agents/skills/marketplace-validator/scripts/validate.py skills/crafting-skills/`
Expected: exit 0, no new warnings beyond the 4 pre-existing.

**Step 4.4 — Commit**

```bash
git add skills/crafting-skills/SKILL.md
git commit -m "docs(crafting-skills): POST-CREATE mode — observe immediate post-creation use"
```

---

## Task 5: Add REVIEW mode to `crafting-skills/SKILL.md`

**Files:**
- Modify: `skills/crafting-skills/SKILL.md` — insert REVIEW mode immediately AFTER the POST-CREATE mode (just added in Task 4) and BEFORE the "## Best-Practices Compendium" header

**Step 5.1 — Find the insertion point**

Run: `grep -n "^## POST-CREATE Mode\|^## Best-Practices Compendium" skills/crafting-skills/SKILL.md`
Expected: Two line numbers, with POST-CREATE first.

**Step 5.2 — Insert REVIEW mode between POST-CREATE and Best-Practices Compendium**

Find this text (the end of POST-CREATE contrast block + the Best-Practices Compendium header):

```
- REVIEW mode — looks at the skill statically. POST-CREATE looks at what the agent *did* with the skill.


## Best-Practices Compendium
```

Replace it with:

```
- REVIEW mode — looks at the skill statically. POST-CREATE looks at what the agent *did* with the skill.


## REVIEW Mode

*Critique an existing skill against the 16-rule Best-Practices Compendium and propose fixes.*

**Step 1 — Read the skill.** Read `SKILL.md` + `references/` (one file at a time, on demand) + `scripts/` + `assets/`. If the skill exceeds 1000 lines total, read `SKILL.md` first, then references one at a time.

**Step 2 — Spawn a critic subagent.** Apply the `general-critic` contract (HIGH/MEDIUM/LOW) with the compendium as the lens. The critic MUST NOT modify files — return findings only, with file:line, severity, and proposed fix. The critic prompt MUST include: "Your lens is the 16-rule Best-Practices Compendium at `skills/crafting-skills/references/best-practices-compendium.md`. Read it BEFORE reviewing. Score each rule PASS / FAIL / N/A. For each FAIL, emit HIGH/MEDIUM/LOW and a concrete fix."

**Step 3 — Aggregate findings.** Per-rule pass/fail matrix. Severity counts: HIGH = breaks a contract (Rule 15 violation, broken file reference, triggers on wrong intent), MEDIUM = degrades quality (passive citation, missing gotcha, vague description), LOW = cosmetic (line count, naming style).

**Step 4 — Loop until no HIGH remain, capped at 3 iterations.** Apply HIGH fixes with user confirmation. Re-spawn critic. Loop. Stop when 0 HIGH OR 3 iterations reached. If 3 iterations reached with HIGH still present, surface the full report to the user and let them decide whether to continue, defer, or downgrade to MEDIUM. Report MEDIUM and LOW for the user to decide.

**Step 5 — Report.** Inline if small. Otherwise write `references/review-<date>.md` (note: this lives in `crafting-skills/references/`, not in the reviewed skill's directory, to avoid polluting the reviewed skill).

**Contrast (do not confuse with):**
- `evaluating-skills` RUN mode — *behavioral* comparison (with-skill vs baseline, with transcripts). REVIEW is *static* (just reads the skill).
- `general-critic` directly — generic artifact critique. REVIEW is skill-specific and uses the compendium as lens.


## Best-Practices Compendium
```

**Step 5.3 — Verify both modes + compendium header in correct order**

Run: `grep -n "^## \(OPTIMIZE\|POST-CREATE\|REVIEW\|Best-Practices Compendium\) Mode\?$" skills/crafting-skills/SKILL.md`
Expected: 4 matches in order: OPTIMIZE (existing), POST-CREATE (Task 4), REVIEW (just added), Best-Practices Compendium.

**Step 5.4 — Run the marketplace validator**

Run: `python3 .agents/skills/marketplace-validator/scripts/validate.py skills/crafting-skills/`
Expected: exit 0, no new warnings.

**Step 5.5 — Commit**

```bash
git add skills/crafting-skills/SKILL.md
git commit -m "docs(crafting-skills): REVIEW mode — static critique against compendium"
```

---

## Task 6: Update CONTRAST section in `crafting-skills/SKILL.md`

**Files:**
- Modify: `skills/crafting-skills/SKILL.md` — append 2 bullets to the existing CONTRAST block (currently ends at line 142 with "NOT for authoring a Claude Code command or hook — see official Claude Code docs")

**Step 6.1 — Find the CONTRAST block**

Run: `grep -n "^## CONTRAST\|^- NOT for" skills/crafting-skills/SKILL.md | head -10`
Expected: Returns the CONTRAST header line and all `NOT for` bullets. The last existing bullet ends at line 142.

**Step 6.2 — Append 2 CONTRAST bullets**

Find this text (the last existing CONTRAST bullet — line 142):

```
- NOT for authoring a Claude Code command or hook — see official Claude Code docs
```

Replace it with:

```
- NOT for authoring a Claude Code command or hook — see official Claude Code docs
- NOT for behavioral comparison of skill effectiveness — use `evaluating-skills` RUN mode (POST-CREATE and REVIEW do not replace it; they complement it for lightweight, immediate cases).
- NOT for generic artifact critique (non-skill) — use `general-critic` directly.
```

**Step 6.3 — Run the marketplace validator**

Run: `python3 .agents/skills/marketplace-validator/scripts/validate.py skills/crafting-skills/`
Expected: exit 0.

**Step 6.4 — Commit**

```bash
git add skills/crafting-skills/SKILL.md
git commit -m "docs(crafting-skills): CONTRAST — defer behavioral critique to evaluating-skills"
```

---

## Task 7: Final verification (validator + routing test + line counts)

**Files:** None (read-only verification)

**Step 7.1 — Run marketplace validator**

Run: `python3 .agents/skills/marketplace-validator/scripts/validate.py skills/crafting-skills/`
Expected: exit 0, no failures, no NEW warnings beyond the 4 pre-existing (`when_to_use` notice, `argument-hint` notice, description word count, one structural note). If a NEW warning appears, fix inline and amend the offending task's commit.

**Step 7.2 — Run the routing test**

Run: `python3 .agents/skills/marketplace-validator/scripts/routing_test.py`
Expected: Same baseline as before this plan (6/10 wins, 1 tie, 3 pre-existing losses). Any regression (a previously-passing query now fails, or vice-versa) is a HIGH finding — fix the routing description in Task 3 or revert.

**Step 7.3 — Verify line counts**

Run:
```bash
wc -l skills/crafting-skills/SKILL.md skills/crafting-skills/references/best-practices-compendium.md
```

Expected:
- `SKILL.md`: ~290 lines (started at 199, +~90)
- `compendium.md`: ~170 lines (started at 142, +~28)
- Both well under 500-line cap.

**Step 7.4 — Verify spec coverage**

Read aloud each section of `docs/principled/specs/2026-06-22-skill-steering-point-to-sources.md` and confirm a task implements it:
- Section 1 (Rules 15-16) → Tasks 1, 2
- Section 2 (REVIEW mode) → Task 5
- Section 3 (POST-CREATE mode) → Task 4
- Section 4 (frontmatter + router) → Task 3
- Section 5 (what this does NOT do) → honored implicitly (no OPTIMIZE change, no behavioral harness, etc.)
- Section 6 (files to change) → Tasks 1–6 cover both files
- Section 7 (verification) → Task 7
- Section 8 (decisions made) → baked into Tasks 4, 5 content

If any section lacks a corresponding task, stop and add one before proceeding.

**Step 7.5 — Read-aloud check of POST-CREATE Step 3 classification**

Open `skills/crafting-skills/SKILL.md`, find the POST-CREATE Step 3 table, and verify the 5 classes (Missed gotcha, Trigger miss, Inlined content, Stale instruction, Friction) are present with correct symptoms and proposed edits. If any class is missing or mis-worded, fix inline.

**Step 7.6 — Read-aloud check of Rule 15 verb distinction**

Open `skills/crafting-skills/references/best-practices-compendium.md`, find Rule 15, and verify:
- The 3-row table (Dynamic, Static intra-skill, Cross-skill) is present with examples
- The "read and apply" canonical form is stated
- The 4-step test (need this fact, can load on demand, audience-aware, deduplicate) is present
- The antipattern paragraph is present

If any element is missing, fix inline.

**Step 7.7 — No commit (verification only)**

If all checks pass, report "Plan complete, all tasks green." If any check fails, fix the relevant task's commit (amend if local, follow-up commit if pushed) and re-run the failing check.

---

## Execution handoff

This plan is written for the **subagent-driven-development** skill (recommended for this work — each task is small, self-contained, and benefits from two-stage review per the pattern used in the previous router-language plan). 6 implementation tasks + 1 verification task. No external dependencies beyond the marketplace-validator and routing_test.py scripts (already in `.agents/skills/marketplace-validator/scripts/`).
