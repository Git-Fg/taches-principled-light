# Router Language by Audience — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply the audience-aware imperative split (INTERNAL contract vs EXTERNAL framing) to `claude-cli`'s router table and codify the rule in the `crafting-skills` Best-Practices Compendium, plus introduce the `references/prompts/` convention for subagent prompt contracts.

**Architecture:** Three coordinated edits to existing skill bodies plus one new directory. (1) Rewrite `skills/claude-cli/SKILL.md` §3 router table to mix imperative and descriptive rows based on the contract test (6 INTERNAL operations stay imperative; 2 cross-cutting references move to descriptive). **(2) Edit `skills/crafting-skills/references/best-practices-compendium.md`** (this is where the 14 rules and supporting reference actually live — `crafting-skills/SKILL.md` is unchanged) to replace rule 7 with the audience-aware version, extend rule 4 in Skill Anatomy, add new rule 6 for subagent prompt contracts, and add a Common Pitfalls row. (3) Create the empty `skills/claude-cli/references/prompts/` directory with a `.gitkeep` so git tracks it.

**Tech Stack:** Markdown, marketplace-validator (Python), git. No code, no application logic — pure skill-content edits.

**Spec:** `docs/principled/specs/2026-06-22-router-language-audience-design.md`

**Status:** Task 1 (claude-cli router table rewrite) is **already done** and committed at `7911eed`. Tasks 2–6 remain.

---

## File structure

| File | Action | What it does |
|---|---|---|
| `skills/claude-cli/SKILL.md` | Modify §3 (DONE in commit `7911eed`) | 8-row router table changed from uniform-imperative to two-tone |
| `skills/crafting-skills/references/best-practices-compendium.md` | Modify 2 rules + add 1 rule + add 1 pitfall row | Codifies the audience-aware rule |
| `skills/claude-cli/references/prompts/.gitkeep` | Create | Empty dir marker so git tracks the new directory |

**Important:** `skills/crafting-skills/SKILL.md` is **not** changed. It already points to the compendium at line 199 ("You MUST read `references/best-practices-compendium.md` BEFORE…"). All Tasks 2–5 touch the compendium file, not the SKILL.md.

No code files. No unit tests. Verification is the marketplace-validator (regression check on the skill frontmatter) and line-count assertions.

---

## Task 1: Rewrite the claude-cli router table (two-tone) — DONE

**Files:**
- Modify: `skills/claude-cli/SKILL.md` §3 reference router table (8 rows in the markdown table)

**Status:** This task was executed inline before the audit identified spec inaccuracies in the other tasks. The replacement was applied correctly and committed at `7911eed`. No further action needed.

**Verification (re-run for the record):**

Run: `grep -n -A 10 "^| If you are" skills/claude-cli/SKILL.md`
Expected: 11 lines (header + separator + 8 rows + 1 blank), with rows 1–6 starting with "You MUST read" and rows 7–8 starting with "`references/...` describes/shows".

If the table is not in this state, re-apply the replacement from the original plan archive (commit `cf3a060`).

---

## Task 2: Update crafting-skills Best-Practices rule 7 (audience-aware)

**Files:**
- Modify: `skills/crafting-skills/references/best-practices-compendium.md` — rule 7 in the "## 14 Rules" section (line 30)

**Self-contained subagent brief:**

> You are an isolated implementer subagent. You have edit access to one file. Your task is to expand the "MUST, not should" rule in the crafting-skills Best-Practices Compendium to be audience-aware. The rule currently says to use imperative constraint language for everything; the new version splits the imperative obligation by audience (INTERNAL contract = MUST, EXTERNAL framing = descriptive).
>
> **File to modify:** `skills/crafting-skills/references/best-practices-compendium.md`
>
> **Exact text to find (do not include line numbers):**
> ```
> 7. **MUST, not should.** Use imperative constraint language. "MUST filter test accounts" not "always filter test accounts."
> ```
>
> **Replace with this exact text (preserve the leading `7. ` and the `**...**` heading style):**
> ```
> 7. **Audience-aware imperative — apply MUST to contracts, descriptive to framing.**
>    - **INTERNAL contracts** (file references, subagent prompt contracts, command citations, skill loading chains) → MUST imperative. "You MUST read `references/format.md` BEFORE writing any code."
>    - **EXTERNAL framing** (workflows, anti-patterns, handoffs, capability descriptions) → descriptive. "See `references/workflows.md` for end-to-end patterns."
>    - The distinction: INTERNAL is a contract the agent must honor for the operation to succeed. EXTERNAL is context the agent can use or ignore. Applying MUST uniformly reads as "too violent" and dilutes the imperative signal.
> ```
>
> **Verification:**
>
> Run: `grep -n "Audience-aware imperative" skills/crafting-skills/references/best-practices-compendium.md`
> Expected: one matching line with the line number. The new text should be on 5 lines (the heading line + 3 indented sub-bullets with `   -` prefix + the `**The distinction:**` paragraph).
>
> Run: `python3 .agents/skills/marketplace-validator/scripts/validate.py skills/crafting-skills/`
> Expected output (last line): `VALIDATION: 0 failures, 2 warnings across 1 skills`
> The 2 warnings are pre-existing (`when_to_use` extension and description length) and must not change.
>
> **Commit:**
> ```bash
> git add skills/crafting-skills/references/best-practices-compendium.md
> git commit -m "docs(crafting-skills): rule 7 — audience-aware imperative (contract vs framing)"
> ```
>
> Report back: (a) the line number where the new rule 7 starts, (b) the validator's last line of output, (c) the commit SHA.

---

## Task 3: Update crafting-skills Skill Anatomy rule 4 (audience-aware file citations)

**Files:**
- Modify: `skills/crafting-skills/references/best-practices-compendium.md` — rule 4 in the "## Skill Anatomy → File reference conventions" numbered list (line 67)

**Self-contained subagent brief:**

> You are an isolated implementer subagent. You have edit access to one file. Your task is to expand the "Imperative citations only" rule in the crafting-skills Skill Anatomy section to be audience-aware, mirroring the contract-vs-framing distinction from rule 7. The current rule is one line; the new version has a 3-line structure with sub-bullets.
>
> **File to modify:** `skills/crafting-skills/references/best-practices-compendium.md`
>
> **Exact text to find (do not include line numbers):**
> ```
> 4. **Imperative citations only:** "You MUST read `references/format.md` BEFORE writing any code." Never "You can read" or "See reference." Passive citations are ignored by LLMs.
> ```
>
> **Replace with this exact text:**
> ```
> 4. **Audience-aware file citations.**
>    - For INTERNAL contract references: "You MUST read `references/X.md` BEFORE [action]."
>    - For EXTERNAL framing references: "`references/X.md` describes / shows / covers [topic] — consult when [condition]."
>    - Never: "You can read", "Optionally consult", "Feel free to look at". Passive citations are ignored by LLMs in both directions.
> ```
>
> **Verification:**
>
> Run: `grep -n "Audience-aware file citations" skills/crafting-skills/references/best-practices-compendium.md`
> Expected: one matching line.
>
> Run: `python3 .agents/skills/marketplace-validator/scripts/validate.py skills/crafting-skills/`
> Expected output (last line): `VALIDATION: 0 failures, 2 warnings across 1 skills`
>
> **Commit:**
> ```bash
> git add skills/crafting-skills/references/best-practices-compendium.md
> git commit -m "docs(crafting-skills): rule 4 (Anatomy) — audience-aware file citations"
> ```
>
> Report back: (a) the line number of the new rule 4 heading, (b) the validator's last line of output, (c) the commit SHA.

---

## Task 4: Add new Skill Anatomy rule 6 (subagent prompt contracts)

**Files:**
- Modify: `skills/crafting-skills/references/best-practices-compendium.md` — Skill Anatomy "File reference conventions" numbered list, append rule 6 after the existing rule 5 (at line 68)

**Note on numbering:** The existing rule 5 in this list is "Opt-out for teaching examples" (line 68). The new rule about subagent prompt contracts is **rule 6**, not rule 5. Do not renumber the existing rules.

**Self-contained subagent brief:**

> You are an isolated implementer subagent. You have edit access to one file. Your task is to add a new rule 6 to the Skill Anatomy "File reference conventions" numbered list in the crafting-skills Best-Practices Compendium. The new rule codifies the `references/prompts/` convention and the `# Contract:` first-line marker. It must be numbered 6 (the existing rule 5 is "Opt-out for teaching examples").
>
> **File to modify:** `skills/crafting-skills/references/best-practices-compendium.md`
>
> **Insertion location:** Immediately after the existing rule 5 (line 68, the line that begins `5. **Opt-out for teaching examples:**`), and before the `---` horizontal rule on line 51 that ends the "## Skill Anatomy" section.
>
> **Exact text to find (this is the existing rule 5, used as the anchor — do not change it):**
> ```
> 5. **Opt-out for teaching examples:** A file that *quotes* reference paths as teaching examples (WRONG/RIGHT citation patterns) can opt out of citation linting with an HTML comment at the top: `<!-- check-citations-skip: reason -->`. Use sparingly — the linter (marketplace-validator + marketplace-health) honors this marker and skips the file. Lines with inline backticks and lines inside fenced code blocks are skipped by default; the opt-out is for prose that quotes paths without backticks.
> ```
>
> **Action:** Append the following block immediately after that line, with one blank line separating it from rule 5:
>
> ```
> 6. **Subagent prompt contracts (when applicable).**
>    - If the skill includes prompts passed verbatim to subagents, place them in `references/prompts/<name>.md`.
>    - Each prompt file starts with `# Contract: <subagent-name>` so the receiving subagent recognizes it as a binding contract.
>    - The host skill's body MUST use imperative form when referencing the prompt: "You MUST pass `references/prompts/reviewer.md` verbatim." Descriptive explanation of what the prompt does goes in a separate sentence, not the same one.
> ```
>
> **Verification:**
>
> Run: `grep -n "Subagent prompt contracts" skills/crafting-skills/references/best-practices-compendium.md`
> Expected: one matching line.
>
> Run: `grep -n "^[0-9]\. \*\*" skills/crafting-skills/references/best-practices-compendium.md | grep -E "5\.|6\."`
> Expected: 4 lines — the four "## 14 Rules" rules numbered 5/6 (gerund form + Name must match) AND the two "Skill Anatomy → File reference conventions" rules numbered 5/6 (Opt-out for teaching examples + Subagent prompt contracts). Both number-5s and both number-6s must be present in document order.
>
> Run: `python3 .agents/skills/marketplace-validator/scripts/validate.py skills/crafting-skills/`
> Expected output (last line): `VALIDATION: 0 failures, 2 warnings across 1 skills`
>
> **Commit:**
> ```bash
> git add skills/crafting-skills/references/best-practices-compendium.md
> git commit -m "docs(crafting-skills): rule 6 (Anatomy) — subagent prompt contracts"
> ```
>
> Report back: (a) the line number of the new rule 6 heading, (b) confirmation that rule 5 is unchanged, (c) the validator's last line of output, (d) the commit SHA.

---

## Task 5: Add the new Common Pitfalls row (uniform-imperative)

**Files:**
- Modify: `skills/crafting-skills/references/best-practices-compendium.md` — Common Pitfalls table (lines 101–113), append a new row at the end

**Self-contained subagent brief:**

> You are an isolated implementer subagent. You have edit access to one file. Your task is to add a new row to the "Common Pitfalls" markdown table in the crafting-skills Best-Practices Compendium. The new row codifies the "uniform-imperative" anti-pattern that motivated this whole design.
>
> **File to modify:** `skills/crafting-skills/references/best-practices-compendium.md`
>
> **Table location:** The "## Common Pitfalls" section is at line 101. The table starts at line 103 (`| Pitfall | Fix |`) and currently has 9 data rows (lines 105–113), ending with:
>
> ```
> | Self-generated content | Don't ask the model to write a skill for itself — inject human judgment |
> ```
>
> **Action:** Insert one new row immediately after that line, preserving the table's 2-column structure (single pipe separators, no trailing whitespace). The new row text:
>
> ```
> | Uniform-imperative skill | Apply MUST to INTERNAL contracts only; relax to descriptive for EXTERNAL framing. Reading 8 rows of "You MUST…" is fatiguing and dilutes the imperative signal. |
> ```
>
> **Verification:**
>
> Run: `grep -n "Uniform-imperative skill" skills/crafting-skills/references/best-practices-compendium.md`
> Expected: one matching line.
>
> Run: `grep -c "^| " skills/crafting-skills/references/best-practices-compendium.md`
> Expected: was `12` (1 header + 1 separator + 9 data rows + 1 row from the frontmatter or another table). After this task: `13` (one more data row in the Common Pitfalls table).
>
> Run: `python3 .agents/skills/marketplace-validator/scripts/validate.py skills/crafting-skills/`
> Expected output (last line): `VALIDATION: 0 failures, 2 warnings across 1 skills`
>
> **Commit:**
> ```bash
> git add skills/crafting-skills/references/best-practices-compendium.md
> git commit -m "docs(crafting-skills): pitfall row — uniform-imperative skill"
> ```
>
> Report back: (a) the line number of the new row, (b) the validator's last line of output, (c) the commit SHA.

---

## Task 6: Create the empty `references/prompts/` directory

**Files:**
- Create: `skills/claude-cli/references/prompts/.gitkeep`

**Self-contained subagent brief:**

> You are an isolated implementer subagent. You have edit access to the filesystem. Your task is to create an empty directory `skills/claude-cli/references/prompts/` with a `.gitkeep` file so git tracks it. The directory is a placeholder for future subagent prompt contracts (Task 4 of the spec introduces the convention; no concrete prompt is added yet).
>
> **Commands to run, in order:**
>
> ```bash
> mkdir -p skills/claude-cli/references/prompts
> touch skills/claude-cli/references/prompts/.gitkeep
> ```
>
> **Verification:**
>
> Run: `ls -ld skills/claude-cli/references/prompts`
> Expected: a single line ending with `… skills/claude-cli/references/prompts` (the directory itself).
>
> Run: `ls -la skills/claude-cli/references/prompts/`
> Expected: the only file listed is `.gitkeep`.
>
> **Commit:**
> ```bash
> git add skills/claude-cli/references/prompts/.gitkeep
> git commit -m "chore(claude-cli): create references/prompts/ dir for subagent prompt contracts"
> ```
>
> Report back: (a) confirmation that the directory exists, (b) the commit SHA.

---

## Task 7: Final validation

This is a single-session task, not dispatched to a subagent. The orchestrator (you, reading this) runs all the verification commands and reports the final state.

- [ ] **Step 1: Run validator on both modified skills**

Run: `python3 .agents/skills/marketplace-validator/scripts/validate.py skills/claude-cli/ skills/crafting-skills/`
Expected output (last line): `VALIDATION: 0 failures, 4 warnings across 2 skills`
The 4 warnings are the pre-existing `when_to_use` extension warnings (1 per skill) and the description-length warnings (1 per skill). No new failures.

- [ ] **Step 2: Body line count check (claudi-cli, unchanged from Task 1)**

Run: `wc -l skills/claude-cli/SKILL.md`
Expected: 128 lines (the router table replacement was 9 lines for 9 lines, no net change).

- [ ] **Step 3: Body line count check (compendium, +20 lines expected)**

Run: `wc -l skills/crafting-skills/references/best-practices-compendium.md`
Expected: ~150 lines (was 130, +20 net: rule 7 expansion +4 lines, rule 4 Anatomy expansion +3 lines, new rule 6 +5 lines, new pitfall row +1 line, blank-line separators +7 lines; total ~+20). Acceptable range: 145–160 lines.

- [ ] **Step 4: Routing test rerun (regression check)**

Run: `python3 .agents/skills/marketplace-validator/scripts/routing_test.py`
Expected: 6/10 wins, 1 tie, 3 pre-existing losses (no regression — the router table is internal to the skill body, not the description that the routing test scores).

- [ ] **Step 5: Confirm git history**

Run: `git log --oneline -10`
Expected: 6 new commits on top of `75ae9d3` (the last commit before this plan), plus the existing `7911eed` (Task 1). Commit messages match the `refactor:` / `docs:` / `chore:` convention used in the project. Total commits from this plan: 5 (Tasks 2, 3, 4, 5, 6) — Task 1 was already done.

- [ ] **Step 6: Optional push (only if user asks)**

```bash
git push origin main
```
Docs-only change, push is safe but not automatic.

---

## Self-review

**1. Spec coverage** — each spec section maps to a task:

| Spec § | Section name | Task |
|---|---|---|
| 1 | The separation criterion | No standalone task; codified in Tasks 2-5 (compendium rules) |
| 2 | Application to claude-cli router | Task 1 (DONE) |
| 3.1 | Best-Practices rule 7 audience-aware | Task 2 |
| 3.2 | Anatomy rule 4 audience-aware | Task 3 |
| 3.3 | New Common Pitfalls row | Task 5 |
| 4.1-4.4 | `references/prompts/` convention + `# Contract:` marker + 3-level form | Codified in Task 4 (rule 6) + Task 6 (empty dir) |
| 4.5 | Skill Anatomy rule 6 (subagent prompt contracts) | Task 4 |
| 6 | Files to change | All 6 tasks |
| 7 | Verification | Task 7 |

**2. Placeholder scan** — no TBD, TODO, "implement later", "similar to Task N", or "add appropriate error handling" in the plan. Every step has the exact replacement text, exact grep commands, and expected output. The new subagent brief format makes each task self-contained for a fresh implementer subagent.

**3. Type consistency / path consistency** — every file path referenced in the plan now matches the actual filesystem:
- `skills/claude-cli/SKILL.md` — verified to exist with the new router table.
- `skills/crafting-skills/references/best-practices-compendium.md` — verified to contain rules 1–14 (line 30 is rule 7), the Skill Anatomy section with 5 numbered rules (lines 64–68), and the Common Pitfalls table (lines 101–113).
- `skills/crafting-skills/SKILL.md` — confirmed unchanged by this plan; it points to the compendium at line 199.

**4. Rule numbering check** — the plan's "new rule 6" refers to the Skill Anatomy numbered list, not the "## 14 Rules" list. The Skill Anatomy list already has 5 rules; the new rule about subagent prompt contracts is rule 6 in that list. The "## 14 Rules" list is unchanged.

---

## Out of scope (not in this plan)

- No new subagent prompt files in `references/prompts/` — the dir is created empty (Task 6) but no concrete prompt is added. The convention is in place for when one is needed.
- No change to the claude-cli description (still 59 words). The two-tone split is body language, not description.
- No three-tier MUST/SHOULD/MAY scale. Two tones (imperative vs descriptive) is the maximum that survives contact with how LLMs parse instruction language.
- No A/B test of imperative vs descriptive router accuracy. That requires an LLM-judge eval and is documented as an open question in the spec.
- No change to the "File reference audit" item in `crafting-skills/SKILL.md` Step 6 (CREATE mode validation rule). It is related but not identical to the compendium's "Audience-aware file citations" rule. Out of scope for this design; left as a follow-up.

---

## Execution

This plan is structured for **subagent-driven execution**: each of Tasks 2–6 has a self-contained "Self-contained subagent brief" block that can be pasted directly into an Agent dispatch (subagent_type `coder`, edit access). The orchestrator (this session) reads the brief, dispatches one subagent per task, reviews the report, then dispatches the next.

**Recommended sequence:** Tasks 2 → 3 → 4 → 5 → 6 in order. Tasks 2–5 all touch the same file (`crafting-skills/references/best-practices-compendium.md`) so each commit is surgical and the file can be reviewed incrementally. Task 6 is independent (creates a new dir in `claude-cli/references/prompts/`) and can run in parallel with any of the others if needed.

**Task 7** is the orchestrator's final check — run all verification commands, confirm no regressions, report the final state to the user.
