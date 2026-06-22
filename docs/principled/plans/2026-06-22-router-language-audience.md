# Router Language by Audience — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply the audience-aware imperative split (INTERNAL contract vs EXTERNAL framing) to `claude-cli`'s router table and codify the rule in `crafting-skills`, plus introduce the `references/prompts/` convention for subagent prompt contracts.

**Architecture:** Two coordinated edits to existing skill bodies plus one new directory. (1) Rewrite `claude-cli/SKILL.md` §3 router table to mix imperative and descriptive rows based on the contract test (6 INTERNAL operations stay imperative; 2 cross-cutting references move to descriptive). (2) Update three rules in `crafting-skills/SKILL.md` to document the audience split and add a Common Pitfalls row. (3) Create the empty `skills/claude-cli/references/prompts/` directory with a `.gitkeep` so git tracks it.

**Tech Stack:** Markdown, marketplace-validator (Python), git. No code, no application logic — pure skill-content edits.

**Spec:** `docs/principled/specs/2026-06-22-router-language-audience-design.md`

---

## File structure

| File | Action | What it does |
|---|---|---|
| `skills/claude-cli/SKILL.md` | Modify §3 only | 8-row router table changes from uniform-imperative to two-tone |
| `skills/crafting-skills/SKILL.md` | Modify 3 rules + add 1 rule + 1 pitfall row | Codifies the audience-aware rule |
| `skills/claude-cli/references/prompts/.gitkeep` | Create | Empty dir marker so git tracks the new directory |

No code files. No unit tests. Verification is the marketplace-validator (regression check) and line-count assertions.

---

## Task 1: Rewrite the claude-cli router table (two-tone)

**Files:**
- Modify: `skills/claude-cli/SKILL.md` §3 reference router table (8 rows in the markdown table)

- [ ] **Step 1: Locate the current router table**

Run: `grep -n "If you are" skills/claude-cli/SKILL.md`
Expected: a single line number where the table header starts (around line 75).

- [ ] **Step 2: Replace the entire router table (header + 8 rows) with the two-tone version**

Find this block in the file:

```markdown
| If you are… | You MUST read this reference BEFORE proceeding |
|---|---|
| Running a headless prompt with flags | `references/execute.md` |
| Resuming or managing a session lifecycle | `references/session.md` |
| Telling Claude about directories or worktrees | `references/context.md` |
| Running a cloud-hosted code review | `references/review.md` |
| Spawning or managing background agents | `references/agent.md` |
| Tuning model, effort, permission mode, settings | `references/config.md` |
| Parsing CLI output (text/json/stream-json/exit codes) | `references/output-contract.md` |
| Composing an end-to-end workflow | `references/workflows.md` |
```

Replace it with this exact block (note: 2 columns, same width, verb contrast encodes audience — MUST BEFORE = INTERNAL; "describes / shows — consult" = EXTERNAL):

```markdown
| If you are… | Reference guidance |
|---|---|
| Running a headless prompt with flags | You MUST read `references/execute.md` BEFORE writing the invocation |
| Resuming or managing a session lifecycle | You MUST read `references/session.md` BEFORE touching session state |
| Telling Claude about directories or worktrees | You MUST read `references/context.md` BEFORE setting `--add-dir` or `--worktree` |
| Running a cloud-hosted code review | You MUST read `references/review.md` BEFORE invoking `ultrareview` |
| Spawning or managing background agents | You MUST read `references/agent.md` BEFORE using `--agent` or `claude agents` |
| Tuning model, effort, permission mode, settings | You MUST read `references/config.md` BEFORE picking `--effort` or `--permission-mode` |
| Parsing CLI output | `references/output-contract.md` describes the text/json/stream-json shapes — consult when you need to parse |
| Composing an end-to-end workflow | `references/workflows.md` shows six end-to-end patterns — consult for composition ideas |
```

- [ ] **Step 3: Verify the new table is in place**

Run: `grep -n -A 10 "^| If you are" skills/claude-cli/SKILL.md`
Expected: 11 lines (header + separator + 8 rows + 1 blank).

- [ ] **Step 4: Run the marketplace-validator (regression check)**

Run: `python3 .agents/skills/marketplace-validator/scripts/validate.py skills/claude-cli/`
Expected output (last line): `VALIDATION: 0 failures, 2 warnings across 1 skills`
The 2 warnings are the pre-existing `when_to_use` extension warning and the 59-word description warning. Both were present before this task; this task must not add new failures.

- [ ] **Step 5: Body line count check**

Run: `wc -l skills/claude-cli/SKILL.md`
Expected: ≤200 lines (currently 128 after the split, the table is the same line count).

- [ ] **Step 6: Commit**

```bash
git add skills/claude-cli/SKILL.md
git commit -m "refactor(claude-cli): two-tone router language (INTERNAL contract, EXTERNAL framing)"
```

---

## Task 2: Update crafting-skills Best-Practices rule 7 (audience-aware)

**Files:**
- Modify: `skills/crafting-skills/SKILL.md` — rule 7 in the Best-Practices Compendium

- [ ] **Step 1: Locate the current rule 7**

Run: `grep -n "MUST, not should" skills/crafting-skills/SKILL.md`
Expected: 1 line number. Read 3 lines after to see the full current rule.

- [ ] **Step 2: Replace rule 7 with the audience-aware version**

Find this exact text in the file (one bullet, ~2 lines):

```
7. **MUST, not should.** Use imperative constraint language. "MUST filter test accounts" not "always filter test accounts."
```

Replace it with this exact text (one bullet, ~6 lines — keep the same number/heading style):

```
7. **Audience-aware imperative — apply MUST to contracts, descriptive to framing.**
   - **INTERNAL contracts** (file references, subagent prompt contracts, command citations, skill loading chains) → MUST imperative. "You MUST read `references/format.md` BEFORE writing any code."
   - **EXTERNAL framing** (workflows, anti-patterns, handoffs, capability descriptions) → descriptive. "See `references/workflows.md` for end-to-end patterns."
   - The distinction: INTERNAL is a contract the agent must honor for the operation to succeed. EXTERNAL is context the agent can use or ignore. Applying MUST uniformly reads as "too violent" and dilutes the imperative signal.
```

- [ ] **Step 3: Run the validator (regression check)**

Run: `python3 .agents/skills/marketplace-validator/scripts/validate.py skills/crafting-skills/`
Expected output (last line): `VALIDATION: 0 failures, 2 warnings across 1 skills`

- [ ] **Step 4: Commit**

```bash
git add skills/crafting-skills/SKILL.md
git commit -m "docs(crafting-skills): rule 7 — audience-aware imperative (contract vs framing)"
```

---

## Task 3: Update crafting-skills Skill Anatomy rule 4 (audience-aware file citations)

**Files:**
- Modify: `skills/crafting-skills/SKILL.md` — rule 4 in the Skill Anatomy section

- [ ] **Step 1: Locate the current rule 4**

Run: `grep -n "Imperative citations only" skills/crafting-skills/SKILL.md`
Expected: 1 line number. Read 3 lines after to see the full current rule.

- [ ] **Step 2: Replace rule 4 with the audience-aware version**

Find this exact text in the file:

```
4. **Imperative citations only:** "You MUST read `references/format.md` BEFORE writing any code." Never "You can read" or "See reference." Passive citations are ignored by LLMs.
```

Replace it with this exact text:

```
4. **Audience-aware file citations.**
   - For INTERNAL contract references: "You MUST read `references/X.md` BEFORE [action]."
   - For EXTERNAL framing references: "`references/X.md` describes / shows / covers [topic] — consult when [condition]."
   - Never: "You can read", "Optionally consult", "Feel free to look at". Passive citations are ignored by LLMs in both directions.
```

- [ ] **Step 3: Run the validator (regression check)**

Run: `python3 .agents/skills/marketplace-validator/scripts/validate.py skills/crafting-skills/`
Expected output (last line): `VALIDATION: 0 failures, 2 warnings across 1 skills`

- [ ] **Step 4: Commit**

```bash
git add skills/crafting-skills/SKILL.md
git commit -m "docs(crafting-skills): rule 4 (Anatomy) — audience-aware file citations"
```

---

## Task 4: Add new Skill Anatomy rule 5 (subagent prompt contracts)

**Files:**
- Modify: `skills/crafting-skills/SKILL.md` — Skill Anatomy section, append rule 5 immediately after rule 4

- [ ] **Step 1: Locate the end of the Skill Anatomy section**

Run: `grep -n "Native Tool Referencing\|^## " skills/crafting-skills/SKILL.md`
Expected: the line where the next H2 section (`## Native Tool Referencing` or similar) starts. The new rule 5 goes immediately before that heading.

- [ ] **Step 2: Insert rule 5 right after rule 4 and before the next H2**

Find the last numbered rule in the Skill Anatomy section (currently rule 4, ending with the line about passive citations). Insert this block after it, with one blank line above and below:

```
5. **Subagent prompt contracts (when applicable).**
   - If the skill includes prompts passed verbatim to subagents, place them in `references/prompts/<name>.md`.
   - Each prompt file starts with `# Contract: <subagent-name>` so the receiving subagent recognizes it as a binding contract.
   - The host skill's body MUST use imperative form when referencing the prompt: "You MUST pass `references/prompts/reviewer.md` verbatim." Descriptive explanation of what the prompt does goes in a separate sentence, not the same one.
```

- [ ] **Step 3: Run the validator (regression check)**

Run: `python3 .agents/skills/marketplace-validator/scripts/validate.py skills/crafting-skills/`
Expected output (last line): `VALIDATION: 0 failures, 2 warnings across 1 skills`

- [ ] **Step 4: Commit**

```bash
git add skills/crafting-skills/SKILL.md
git commit -m "docs(crafting-skills): rule 5 (Anatomy) — subagent prompt contracts"
```

---

## Task 5: Add the new Common Pitfalls row (uniform-imperative)

**Files:**
- Modify: `skills/crafting-skills/SKILL.md` — Common Pitfalls table, append a new row at the end

- [ ] **Step 1: Locate the Common Pitfalls table**

Run: `grep -n "Common Pitfalls\|^| " skills/crafting-skills/SKILL.md`
Expected: the table is identified by the heading `## Common Pitfalls` followed by a markdown table with `| Pitfall | Fix |` columns.

- [ ] **Step 2: Add a new row to the end of the Pitfall/Fix table**

Find the last existing row in the table. The table currently ends after the "Skill never triggers" row. Add this row immediately after the last existing row (preserve the table's column structure — 2 columns, single pipe separators):

```
| Uniform-imperative skill | Apply MUST to INTERNAL contracts only; relax to descriptive for EXTERNAL framing. Reading 8 rows of "You MUST…" is fatiguing and dilutes the imperative signal. |
```

- [ ] **Step 3: Run the validator (regression check)**

Run: `python3 .agents/skills/marketplace-validator/scripts/validate.py skills/crafting-skills/`
Expected output (last line): `VALIDATION: 0 failures, 2 warnings across 1 skills`

- [ ] **Step 4: Commit**

```bash
git add skills/crafting-skills/SKILL.md
git commit -m "docs(crafting-skills): pitfall row — uniform-imperative skill"
```

---

## Task 6: Create the empty `references/prompts/` directory

**Files:**
- Create: `skills/claude-cli/references/prompts/.gitkeep`

- [ ] **Step 1: Create the directory and the .gitkeep placeholder**

```bash
mkdir -p skills/claude-cli/references/prompts
touch skills/claude-cli/references/prompts/.gitkeep
```

- [ ] **Step 2: Verify the directory exists**

Run: `ls -ld skills/claude-cli/references/prompts`
Expected: `drwxr-xr-x … skills/claude-cli/references/prompts` (the directory itself, not its contents).

Run: `ls -la skills/claude-cli/references/prompts/`
Expected: the only file listed is `.gitkeep`.

- [ ] **Step 3: Commit**

```bash
git add skills/claude-cli/references/prompts/.gitkeep
git commit -m "chore(claude-cli): create references/prompts/ dir for subagent prompt contracts"
```

---

## Task 7: Final validation

- [ ] **Step 1: Run validator on both modified skills**

Run: `python3 .agents/skills/marketplace-validator/scripts/validate.py skills/claude-cli/ skills/crafting-skills/`
Expected output (last line): `VALIDATION: 0 failures, 4 warnings across 2 skills`
The 4 warnings are the pre-existing `when_to_use` extension warnings (1 per skill) and the description-length warnings (1 per skill). No new failures.

- [ ] **Step 2: Body line count check**

Run: `wc -l skills/claude-cli/SKILL.md skills/crafting-skills/SKILL.md`
Expected:
- `skills/claude-cli/SKILL.md` — ≤200 lines (the router table is the same number of rows, just different verb forms)
- `skills/crafting-skills/SKILL.md` — +20 lines vs the pre-plan baseline (net of rule 7 expansion +2 lines, rule 4 expansion +3 lines, new rule 5 +5 lines, new pitfall row +1 line, blank-line adjustments ~+9 lines; total ~+20)

- [ ] **Step 3: Routing test rerun (regression check)**

Run: `python3 .agents/skills/marketplace-validator/scripts/routing_test.py`
Expected: 6/10 wins, 1 tie, 3 pre-existing losses (no regression from the router language change — the router table is internal to the skill body, not the description that the routing test scores).

- [ ] **Step 4: Confirm git history**

Run: `git log --oneline -10`
Expected: 7 new commits on top of `75ae9d3` (the last commit before this plan). Commit messages match the `refactor:` / `docs:` / `chore:` convention used in the project.

- [ ] **Step 5: Optional push**

```bash
git push origin main
```
Only run if the user wants to publish; this is a docs-only change so the push is safe but optional.

---

## Self-review

**1. Spec coverage** — each spec section maps to a task:

| Spec § | Section name | Task |
|---|---|---|
| 1 | The separation criterion | No standalone task; codified in Tasks 2-5 (crafting-skills rules) |
| 2 | Application to claude-cli router | Task 1 |
| 3.1 | Best-Practices rule 7 audience-aware | Task 2 |
| 3.2 | Anatomy rule 4 audience-aware | Task 3 |
| 3.3 | New Common Pitfalls row | Task 5 |
| 4.1-4.4 | `references/prompts/` convention + `# Contract:` marker + 3-level form | Codified in Task 4 (rule 5) + Task 6 (empty dir) |
| 6 | Files to change | All 7 tasks |
| 7 | Verification | Task 7 |

**2. Placeholder scan** — no TBD, TODO, "implement later", "similar to Task N", or "add appropriate error handling" in the plan. Every step has the exact replacement text, exact grep commands, and expected output.

**3. Type consistency** — no code, no types to mismatch. Markdown structure is consistent (rule numbering 7, 4, 5 stays in the right sections; pitfall row added at the end of the table, not inserted in the middle).

---

## Out of scope (not in this plan)

- No new subagent prompt files in `references/prompts/` — the dir is created empty (Task 6) but no concrete prompt is added. The convention is in place for when one is needed.
- No change to the claude-cli description (still 59 words). The two-tone split is body language, not description.
- No three-tier MUST/SHOULD/MAY scale. Two tones (imperative vs descriptive) is the maximum that survives contact with how LLMs parse instruction language.
- No A/B test of imperative vs descriptive router accuracy. That requires an LLM-judge eval and is documented as an open question in the spec.
