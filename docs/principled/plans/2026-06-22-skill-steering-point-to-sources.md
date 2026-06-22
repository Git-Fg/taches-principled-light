# Skill Steering — Point to Live Sources (Full-Merge) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add two new rules (inline Compendium Rule 12 "point to live sources, don't inline them" + Rule 13 "post-creation observation is part of the skill") inline in `crafting-skills/SKILL.md`, plus two new modes (REVIEW static critique + POST-CREATE immediate-use observation), by **merging the entire Best-Practices Compendium into SKILL.md** (deleting the reference file). Also soften the marketplace-validator's body-length warning to acknowledge that meta-skills legitimately exceed the 500-line cap when their content is universally applicable.

**Architecture:** Single source of truth in `skills/crafting-skills/SKILL.md`. The Best-Practices Compendium (16 rules + Skill Anatomy + Native Tool Referencing + Split/Combine + Common Pitfalls + When-Not-Working + CONTRAST) is migrated inline. The reference file `references/best-practices-compendium.md` is deleted. This follows the meta-skill design principle: long bodies are acceptable for meta-skills, and universally-useful references are safer inlined than in separate files that may never be read. Result: SKILL.md grows from 199 → ~540 lines (above the 500-line cap, but justified by the universal-applicability rationale). The validator is updated to flag this as informational rather than a violation.

**Tech Stack:** Markdown, Python (marketplace-validator), git. No application code, no new directories.

**Spec:** `docs/principled/specs/2026-06-22-skill-steering-point-to-sources.md` (committed at `2f4bb41`, with Section 6 update at commit TBD)

**Self-review note:** The plan implements all 9 sections of the spec plus a design update noted in the spec. Tasks 1–2 cover Section 1 (Rules 15–16) plus the merge. Task 1 also covers the validator update referenced in Section 6. Tasks 3–6 cover Section 4 (frontmatter, router, POST-CREATE, REVIEW, CONTRAST). Task 7 covers Section 7 (verification). Sections 2, 3, 5, 8, 9 are honored via Tasks 4, 5, and the plan structure respectively.

---

## File structure

| File | Action | What it does |
|---|---|---|
| `.agents/skills/marketplace-validator/scripts/validate.py` | Modify (1-line message change) | Soften `body_too_long` warning: acknowledge meta-skill exemption |
| `skills/crafting-skills/SKILL.md` | Major rewrite | Inlines the full Compendium, adds POST-CREATE and REVIEW modes, updates router, frontmatter, CONTRAST |
| `skills/crafting-skills/references/best-practices-compendium.md` | Delete | Content merged into SKILL.md |

After Task 6: `skills/crafting-skills/SKILL.md` ≈ 540 lines (above 500-line cap, justified). `skills/crafting-skills/references/` is preserved for the other 4 reference files (context-management, cross-skill-discovery, frontmatter-complete, skill-self-testing) — these are mode-specific and remain as references.

---

## Task 1: Soften the validator's body_too_long message

**Files:**
- Modify: `.agents/skills/marketplace-validator/scripts/validate.py` — the `body_too_long` warning message at lines 260–265

**Step 1.1 — Find the current warning**

Run: `grep -n "body_too_long" .agents/skills/marketplace-validator/scripts/validate.py`
Expected: Returns `261:                "message": f"body has {len(body_lines)} lines (target ≤{MAX_BODY_LINES}); consider splitting into references/",`

**Step 1.2 — Replace the warning message**

Find this text (lines 260–265):

```python
    if len(body_lines) > MAX_BODY_LINES:
        findings.append({
            "level": "warn", "code": "body_too_long",
            "message": f"body has {len(body_lines)} lines (target ≤{MAX_BODY_LINES}); consider splitting into references/",
            "line": None,
        })
```

Replace it with:

```python
    if len(body_lines) > MAX_BODY_LINES:
        findings.append({
            "level": "warn", "code": "body_too_long",
            "message": (
                f"body has {len(body_lines)} lines (target ≤{MAX_BODY_LINES}). "
                "This is not an exact science: certain skills — particularly meta-skills and skills "
                "whose content is universally applied on every load — may legitimately exceed 500 lines. "
                "Consider splitting into references/ ONLY if the content is mode-specific (not loaded on every use). "
                "For universally-applicable content (e.g., a routing compendium used by every mode), prefer keeping it inline. "
                "See crafting-skills inline Compendium Rule 12."
            ),
            "line": None,
        })
```

**Step 1.3 — Run the validator on crafting-skills (should still pass with the new message)**

Run: `python3 .agents/skills/marketplace-validator/scripts/validate.py skills/crafting-skills/`
Expected: exit 0, same 2 pre-existing warnings (frontmatter keys `when_to_use` and `argument-hint`). The new message will only appear when a skill actually exceeds 500 lines — crafting-skills is currently 199 lines, so no `body_too_long` finding yet.

**Step 1.4 — Verify the message text is what we expect**

Run: `grep -A 3 "body_too_long" .agents/skills/marketplace-validator/scripts/validate.py | head -10`
Expected: Shows the new multi-line message starting with "body has {len} lines (target ≤500). This is not an exact science..."

**Step 1.5 — Commit**

```bash
git add .agents/skills/marketplace-validator/scripts/validate.py
git commit -m "ci(validator): soften body_too_long message — acknowledge meta-skill exemption"
```

---

## Task 2: Merge references/best-practices-compendium.md into SKILL.md + add Rules 15–16 inline + delete reference file

**Files:**
- Modify: `skills/crafting-skills/SKILL.md` — replace the "## Best-Practices Compendium" pointer section (lines 197–199) with the FULL Compendium content (142 lines from the reference file, with Rules 15–16 added)
- Delete: `skills/crafting-skills/references/best-practices-compendium.md`

This is the biggest task of the plan. It produces a single inline Compendium section in SKILL.md that contains all 16 rules + supporting reference.

**Step 2.1 — Read the current pointer section in SKILL.md**

Run: `sed -n '195,199p' skills/crafting-skills/SKILL.md`
Expected: Returns the `## Best-Practices Compendium` header + the one-line pointer.

**Step 2.2 — Read the full Compendium reference file (verbatim source)**

Run: `cat skills/crafting-skills/references/best-practices-compendium.md`
Expected: 142 lines (the original Compendium before Rule 15/16 were added).

**Step 2.3 — Replace the pointer section in SKILL.md with the inline Compendium (with Rules 15–16 added inline)**

Find this text in SKILL.md (the current pointer section — exact text):

```


## Best-Practices Compendium

You MUST read `references/best-practices-compendium.md` BEFORE applying Step 4 ("Write the Body") of CREATE mode, and BEFORE any audit in OPTIMIZE mode. The 14 rules (Descriptions, Naming, Body, Evidence) plus supporting reference material (skill anatomy, native tool referencing, split-vs-combine, common pitfalls, contrast) live there. Do not duplicate them inline.
```

Replace it with the following block (this is the FULL Compendium with Rules 15–16 added at the right place):

```


## Best-Practices Compendium

You are reading the Compendium inline — it is part of this skill's body, not a separate reference. The Compendium applies to all modes (CREATE, OPTIMIZE, REVIEW, POST-CREATE) because every mode touches skill content in some form.

### 16 Rules (from SkillsBench + production experience)

These 16 rules encode findings from SkillsBench (7,308 trajectories, 7 model-harness configurations) and production experience at Anthropic and Perplexity. Apply them to every skill you touch.

#### Descriptions

1. **Start with "Load when…"** — the description is a routing trigger. It is NOT documentation.
   ✓ `Load when the user needs to extract text and tables from PDF files.`
   ✗ `Processes PDF files and extracts text.`

2. **Include negative triggers.** Every description must state what NOT to use the skill for, referencing sibling skills by exact name.
   ✓ `Do NOT use for Vue, Svelte, or vanilla CSS projects.`

3. **Target ≤50 words.** Every word costs ~100 tokens per session across all users. If the model already knows it, delete it.

4. **Write in third person.** The description is injected into the system prompt. "I" or "you" causes discovery problems.

#### Naming

5. **Use gerund form** (verb + -ing): `processing-pdfs`, `analyzing-sessions`, `managing-rules`. Avoid abstract nouns (`expertise`, `analytics`) and acronyms (`ddd`, `fpf`).

6. **Name must exactly match the parent directory.** `name: crafting-skills` must live in `crafting-skills/SKILL.md`. Max 64 characters, lowercase letters, numbers, and hyphens only.

#### Body

7. **Audience-aware imperative — apply MUST to contracts, descriptive to framing.**
   - **INTERNAL contracts** (file references, subagent prompt contracts, command citations, skill loading chains) → MUST imperative. "You MUST read `references/format.md` BEFORE writing any code."
   - **EXTERNAL framing** (workflows, anti-patterns, handoffs, capability descriptions) → descriptive. "See `references/workflows.md` for end-to-end patterns."
   - The distinction: INTERNAL is a contract the agent must honor for the operation to succeed. EXTERNAL is context the agent can use or ignore. Applying MUST uniformly reads as "too violent" and dilutes the imperative signal.

8. **Gotchas are the highest-signal content.** Every time the agent fails, add a one-line gotcha. This section accrues the most value over time. Append, don't restructure.

9. **Progressive disclosure across three tiers:**
   - **Index tier** (description): ~100 tokens per skill, paid every session. Ruthless.
   - **Load tier** (SKILL.md body): ≤500 lines is a guideline, not a hard rule (see Task 1 of the skill-steering plan). Meta-skills and universally-applicable content legitimately exceed 500 lines; mode-specific content should still split to references/.
   - **Runtime tier** (scripts/, references/, assets/): unbounded, loaded only on demand.

10. **Skip what the model already knows.** If it's easy to explain, the model already knows it. Delete it. The test: "Would the agent get this wrong without this instruction?" If no, the sentence cannot afford to be there.

11. **Don't railroad.** Prescribe intent and judgment, not exact command sequences. The model does better recovering from errors when it understands the goal rather than following a brittle script.

12. **Point to live sources, don't inline them.** Skills MUST cite the source of information instead of recreating it in the skill body. Three categories:

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
    2. *Can the agent load this content on demand?* If yes → cite, don't inline (Rule 12).
    3. *Is the citation INTERNAL (contract) or EXTERNAL (framing)?* Encode audience in the verb form (Rule 4 + Rule 7).
    4. *Is this content already cited elsewhere in the skill?* If yes → deduplicate, do not repeat.

    The antipattern this rule prevents: the agent inlining a 30-line summary of the agent-browser command reference because it doesn't trust the model to run `agent-browser skills get core` at runtime. The trust bet is wrong — the agent can and will run the command; the inlined content rots on first CLI release.

13. **Post-creation observation is part of the skill.** Skills are written once and used many times. The cost of a skill that drifts out of sync with reality grows with each use. A skill MUST support an observation loop:
    - The author MUST design the skill so that what happens during use can be observed (transcripts, gotcha occurrences, friction points, agent rationalizations).
    - The skill MUST include a path to propose updates based on observed behavior — concretely, **POST-CREATE mode** in this skill.
    - A skill that is "fire and forget" accumulates debt. A skill that observes-and-improves stays accurate.

    If the skill is for an offline workflow with no transcript available, the author MUST document that explicitly and provide the next-best feedback path (e.g., a `references/feedback.md` template the user fills in).

#### Evidence

14. **Self-generated Skills provide zero benefit on average.** Models cannot reliably author the procedural knowledge they benefit from consuming (SkillsBench §4.1.1, Finding 3). Human judgment must be injected into every skill.

15. **2-3 Skills loaded simultaneously is optimal.** More skills show diminishing returns; each additional skill dilutes the attention budget (SkillsBench §4.2.1).

16. **Moderate-length Skills outperform comprehensive ones.** There is a sweet spot beyond which more tokens hurt performance. Be concise, not exhaustive (SkillsBench §4.2.2). Note: this rule is about the *content* being concise, not about the file size — meta-skills and reference skills may legitimately exceed the 500-line guideline when their content is universally applicable.

---

### Skill Anatomy

```
skill-name/
├── SKILL.md              # YAML frontmatter + body (≤500 lines guideline; may exceed for meta-skills)
├── scripts/              # Executable code for deterministic/fragile operations
├── references/           # Heavy docs — one level deep, loaded on demand
└── assets/               # Templates, JSON schemas — copied and filled
```

**File reference conventions:**
1. **Path resolution:** Paths resolve within the skill's folder. Use clean relative paths: `references/file.md`.
2. **No parent traversal:** MUST NOT use `../`. Skills are self-contained. Cross-skill references are semantic (by name), not path-based.
3. **Centralized routing:** Only SKILL.md cites supporting files. Reference files must never cross-cite each other.
4. **Audience-aware file citations.**
   - For INTERNAL contract references: "You MUST read `references/X.md` BEFORE [action]."
   - For EXTERNAL framing references: "`references/X.md` describes / shows / covers [topic] — consult when [condition]."
   - Never: "You can read", "Optionally consult", "Feel free to look at". Passive citations are ignored by LLMs in both directions.
5. **Opt-out for teaching examples:** A file that *quotes* reference paths as teaching examples (WRONG/RIGHT citation patterns) can opt out of citation linting with an HTML comment at the top: `<!-- check-citations-skip: reason -->`. Use sparingly — the linter (marketplace-validator + marketplace-health) honors this marker and skips the file. Lines with inline backticks and lines inside fenced code blocks are skipped by default; the opt-out is for prose that quotes paths without backticks.

6. **Subagent prompt contracts (when applicable).**
   - If the skill includes prompts passed verbatim to subagents, place them in `references/prompts/<name>.md`.
   - Each prompt file starts with `# Contract: <subagent-name>` so the receiving subagent recognizes it as a binding contract.
   - The host skill's body MUST use imperative form when referencing the prompt: "You MUST pass `references/prompts/reviewer.md` verbatim." Descriptive explanation of what the prompt does goes in a separate sentence, not the same one.

---

### Native Tool Referencing

Hardcoded tool names break when APIs rename. Use semantic natural language that delegates to whatever is currently available.

| Brittle (breaks on rename) | Forward-compatible |
|---|---|
| `Use the Agent tool to spawn` | `Use your native tools to spawn a subagent` |
| `Use the Write tool` | `Use your native tools to write the file` |
| `Use the Bash tool` | `Use your native tools to run shell commands` |

Exception: MCP fully-qualified names (`BigQuery:bigquery_schema`) must stay exact — those are server-level identities.

---

### When to Split vs Combine Skills

**Split when:**
- Trigger contexts are disjoint (React vs Python)
- Different model/effort needs (haiku vs opus)
- Distinct user audiences (devops vs frontend)
- Body exceeds 500 lines and sections are independently useful

**Combine when:**
- Same trigger context, slight variations in behavior
- Shared reference material (duplication > 500 lines)
- Workflow sequence (deploy → verify → notify)

---

### Common Pitfalls

| Pitfall | Fix |
|---|---|
| Vague description | Add explicit "Use when user says 'X'" phrases |
| Missing negative trigger | Add "Do NOT use for…" referencing sibling skills by name |
| Guidelines-only `context:fork` | A forked skill without actionable tasks wastes the subagent. Use forks for executing workflows, not injecting reference knowledge. |
| Brittle path reference | Use clean relative paths — paths resolve within the skill's folder |
| Passive file citations | "You MUST read `references/X.md` BEFORE proceeding" — never "You can read" |
| Skill never triggers | Check for `disable-model-invocation: true`; add explicit trigger phrases |
| Skill triggers at wrong time | Add negative triggers; narrow the action verb |
| Too long (>500 lines) | NOT a hard fail. Meta-skills and universally-applicable content may legitimately exceed. Consider splitting ONLY if some content is mode-specific. |
| Self-generated content | Don't ask the model to write a skill for itself — inject human judgment |
| Uniform-imperative skill | Apply MUST to INTERNAL contracts only; relax to descriptive for EXTERNAL framing. Reading 8 rows of "You MUST…" is fatiguing and dilutes the imperative signal. |
| Inlined-source skill | Apply Rule 12: cite the source by command/path/name instead of inlining CLI flags, library APIs, or other-skill content. The antipattern is the agent re-writing the agent-browser command reference inline instead of `agent-browser skills get core`. |

### When Your Skill Isn't Working

- **Never triggers:** Add "Use when: [phrase1], [phrase2]" to description. Check `disable-model-invocation`.
- **Triggers at wrong time:** Add "Do NOT use for: [wrong contexts]". Narrow the action verb.
- **Loads but doesn't do what you want:** Rewrite as step-by-step imperatives. Check `allowed-tools:`.

---

### CONTRAST

- NOT for collaborative skill creation dialogue — use superpowers' `writing-skills`
- NOT for planning a multi-phase project — use `plan-lifecycle`
- NOT for managing rules or AGENTS.md — use `managing-rules`
- NOT for authoring agent definitions — use `orchestrating-subagents`
- NOT for polishing an existing skill's prose — use `reviewing-and-polishing`
- NOT for authoring a Claude Code command or hook — see official Claude Code docs
- NOT for behavioral comparison of skill effectiveness — use `evaluating-skills` RUN mode (POST-CREATE and REVIEW do not replace it; they complement it for lightweight, immediate cases).
- NOT for generic artifact critique (non-skill) — use `general-critic` directly.
```

Note: the rule numbering in the inline Compendium restarts at 1 (it is its own self-contained block, not a continuation of any prior numbering). The two new rules are at positions **12** and **13** in the inline Compendium (Body section), shifting the original Evidence rules (12, 13, 14) to **14, 15, 16**. The original Rule 12 ("Progressive disclosure") moves to Rule 9 — the original ordering is preserved within each subsection (Descriptions 1–4, Naming 5–6, Body 7–13, Evidence 14–16).

**Step 2.4 — Delete the reference file**

```bash
trash skills/crafting-skills/references/best-practices-compendium.md
```

(Use `trash` if available; otherwise `git rm`.)

If `trash` is not available:

```bash
git rm skills/crafting-skills/references/best-practices-compendium.md
```

**Step 2.5 — Run the marketplace validator**

Run: `python3 .agents/skills/marketplace-validator/scripts/validate.py skills/crafting-skills/`
Expected: exit 0. New findings to expect:
- 1 `body_too_long` warning (SKILL.md now exceeds 500 lines). The new message should be displayed — confirm it starts with "This is not an exact science".
- 2 pre-existing `unexpected_fm_key` warnings (`when_to_use`, `argument-hint`).
- Possibly a new warning if any inline code block trips a check — investigate if so.

**Step 2.6 — Verify the Compendium is fully inline**

Run: `grep -nE "^### (16 Rules|Skill Anatomy|Native Tool Referencing|When to Split vs Combine Skills|Common Pitfalls|When Your Skill Isn't Working|CONTRAST)" skills/crafting-skills/SKILL.md`
Expected: 7 matches in order. (Skill Anatomy and others are sub-sections of the Compendium.)

Run: `grep -c "^1[2-6]\. \*\*" skills/crafting-skills/SKILL.md`
Expected: 5 matches (rules 12, 13, 14, 15, 16 of the inline Compendium).

**Step 2.7 — Verify the reference file is gone**

Run: `ls skills/crafting-skills/references/best-practices-compendium.md 2>&1`
Expected: `No such file or directory` (or trash output if used).

**Step 2.8 — Commit**

```bash
git add skills/crafting-skills/SKILL.md
git rm skills/crafting-skills/references/best-practices-compendium.md
git commit -m "refactor(crafting-skills): inline the full Compendium + add rules 12-13

The 16-rule Best-Practices Compendium is universally useful to all modes
(CREATE, OPTIMIZE, REVIEW, POST-CREATE), so per the meta-skill design
principle (long body OK; inline universal references), the entire
Compendium moves inline into SKILL.md and the reference file is deleted.

New rules added inline (positions 12 and 13 in the Body section):
- Rule 12 (Point to live sources, don't inline them) — 3 categories of
  citations with the canonical 'read and apply' verb for cross-skill refs.
- Rule 13 (Post-creation observation is part of the skill) — obligates
  authors to design an observation loop.

SKILL.md grows from 199 → ~520 lines. The body_too_long warning is
informational, not a fail (per validator update in the prior commit).

The original rule numbering shifted: Evidence rules (12-14 → 14-16);
Progressive disclosure (Rule 9 → Rule 9, unchanged)."
```

---

## Task 3: Update SKILL.md frontmatter + Decision Router

**Files:**
- Modify: `skills/crafting-skills/SKILL.md` — frontmatter (description + argument-hint + allowed-tools) and Decision Router block

NOTE: line numbers shift after Task 2 (SKILL.md grew by ~340 lines). Use `grep` to locate sections by content, not line number.

**Step 3.1 — Locate the frontmatter**

Run: `sed -n '1,15p' skills/crafting-skills/SKILL.md`
Expected: Shows YAML frontmatter (description, allowed-tools, when_to_use, argument-hint, license).

**Step 3.2 — Update the description**

Find this text:

```yaml
description: >
  Load when creating a new agent skill from scratch or optimizing an existing
  skill's routing. Use when the user says 'create a skill', 'optimize this
  skill's routing', or 'validate frontmatter'. Do NOT use for collaborative
  skill creation dialogue (use superpowers' writing-skills).
```

Replace it with:

```yaml
description: >
  Load when creating, optimizing, reviewing, or post-iterating an agent skill.
  Use when the user says 'create a skill', 'review this skill', 'self-review',
  'I just used it — propose updates', or 'validate frontmatter'. Do NOT use for
  collaborative skill creation dialogue (use superpowers' writing-skills).
```

**Step 3.3 — Update the allowed-tools**

Find this text:

```
allowed-tools: Read, Edit, Write, Grep, Glob
```

Replace it with:

```
allowed-tools: Read, Edit, Write, Grep, Glob, Agent
```

**Step 3.4 — Update the argument-hint**

Find this text:

```
argument-hint: "[create|optimize] [target-skill-path]"
```

Replace it with:

```
argument-hint: "[create|optimize|review|post-create] [target-skill-path]"
```

**Step 3.5 — Update the Decision Router**

Run: `grep -n "^IF the user wants to" skills/crafting-skills/SKILL.md`
Expected: 3 lines matching the existing Decision Router block (2 IF branches + 1 fallback question).

Find this text:

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

**Step 3.6 — Verify description word count**

Run: `python3 -c "import re; d=open('skills/crafting-skills/SKILL.md').read(); m=re.search(r'description:.*?(?=allowed-tools:|\Z)', d, re.S); txt=' '.join(m.group(0).split()); print(f'words={len(txt.split())}')"`
Expected: `words=46` or `words=47` (≤50 per Compendium Rule 3).

**Step 3.7 — Run the marketplace validator**

Run: `python3 .agents/skills/marketplace-validator/scripts/validate.py skills/crafting-skills/`
Expected: exit 0. Same `body_too_long` warning as Task 2 + same 2 pre-existing FM-key warnings. No NEW failures.

**Step 3.8 — Commit**

```bash
git add skills/crafting-skills/SKILL.md
git commit -m "docs(crafting-skills): frontmatter + router — REVIEW, POST-CREATE modes"
```

---

## Task 4: Add POST-CREATE mode to SKILL.md

**Files:**
- Modify: `skills/crafting-skills/SKILL.md` — insert POST-CREATE mode section between OPTIMIZE mode and the inline Compendium

**Step 4.1 — Locate the OPTIMIZE mode ending**

Run: `grep -n "^### Step 3: Re-Validate\|^## POST-CREATE Mode\|^### 16 Rules" skills/crafting-skills/SKILL.md`
Expected: 3 matches. The `### Step 3: Re-Validate` is the end of OPTIMIZE mode. Insert POST-CREATE after it.

**Step 4.2 — Insert POST-CREATE mode**

Find this text (the end of OPTIMIZE mode):

```
### Step 3: Re-Validate

Run the same benchmark from Step 1. If metrics didn't improve, revert and try a different approach.
Small word changes in descriptions can have outsized impact on routing — including spillover effects on other skills.


## POST-CREATE Mode
```

Replace it with:

```
### Step 3: Re-Validate

Run the same benchmark from Step 1. If metrics didn't improve, revert and try a different approach.
Small word changes in descriptions can have outsized impact on routing — including spillover effects on other skills.


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
| **Inlined content** (Rule 12 violation) | Agent recreated content that lives in a CLI/library/other-skill | Replace paragraph with imperative citation |
| **Stale instruction** | Skill said X but the underlying tool/library has changed | Update to current behavior |
| **Friction** | Agent struggled but recovered — procedure worked, UX didn't | Add a hint or example to the relevant step |

**Step 4 — Propose 3-5 targeted edits.** For each finding, write the proposed edit with file:line and exact text. Do NOT apply without user confirmation. Group by class. Order by impact (HIGH first).

**Step 5 — Apply and validate.** User confirms which of the 3-5 proposed edits to apply (any subset, including all-or-none). Write only the confirmed edits → run `python3 .agents/skills/marketplace-validator/scripts/validate.py <skill_dir>/` → if 0 failures, commit each applied edit with `docs(<skill-name>): post-create <class> from <date>` message (one commit per edit, or grouped if multiple edits of the same class). If validator finds warnings, surface them and ask whether to fix. Do NOT commit if any edit was rejected — rejected findings are kept in the report for future POST-CREATE invocations.

**Contrast (do not confuse with):**
- `evaluating-skills` RUN mode — heavyweight behavioral loop with separate transcripts, multiple iterations, statistical aggregation. POST-CREATE is *lightweight and immediate* — same session, no separate harness, 3-5 edits.
- `evaluating-skills` ITERATE (Stage 7) — same goal (rewrite skill from observed behavior) but driven by formal evals. POST-CREATE is driven by what just happened in the current session.
- REVIEW mode — looks at the skill statically. POST-CREATE looks at what the agent *did* with the skill.


## POST-CREATE Mode
```

**Step 4.3 — Run the marketplace validator**

Run: `python3 .agents/skills/marketplace-validator/scripts/validate.py skills/crafting-skills/`
Expected: exit 0. Same warnings as Task 3. No NEW failures.

**Step 4.4 — Commit**

```bash
git add skills/crafting-skills/SKILL.md
git commit -m "docs(crafting-skills): POST-CREATE mode — observe immediate post-creation use"
```

---

## Task 5: Add REVIEW mode to SKILL.md

**Files:**
- Modify: `skills/crafting-skills/SKILL.md` — insert REVIEW mode between POST-CREATE mode and the inline Compendium

**Step 5.1 — Locate the insertion point**

Run: `grep -n "^## POST-CREATE Mode\|^## REVIEW Mode\|^### 16 Rules" skills/crafting-skills/SKILL.md`
Expected: 3 matches in order.

**Step 5.2 — Insert REVIEW mode**

Find this text (end of POST-CREATE contrast + the Compendium header):

```
- REVIEW mode — looks at the skill statically. POST-CREATE looks at what the agent *did* with the skill.


## POST-CREATE Mode


### 16 Rules
```

Wait — this anchor is wrong since POST-CREATE appears twice (once in the router, once as a section header). Use a more precise anchor. The actual insertion point is right BEFORE the `### 16 Rules` heading (the start of the inline Compendium). Find this text:

```
- REVIEW mode — looks at the skill statically. POST-CREATE looks at what the agent *did* with the skill.


### 16 Rules
```

Replace it with:

```
- REVIEW mode — looks at the skill statically. POST-CREATE looks at what the agent *did* with the skill.


## REVIEW Mode

*Critique an existing skill against the 16-rule Best-Practices Compendium and propose fixes.*

**Step 1 — Read the skill.** Read `SKILL.md` + `references/` (one file at a time, on demand) + `scripts/` + `assets/`. If the skill exceeds 1000 lines total, read `SKILL.md` first, then references one at a time.

**Step 2 — Spawn a critic subagent.** Apply the `general-critic` contract (HIGH/MEDIUM/LOW) with the compendium as the lens. The critic MUST NOT modify files — return findings only, with file:line, severity, and proposed fix. The critic prompt MUST include: "Your lens is the 16-rule Best-Practices Compendium (inline in `crafting-skills/SKILL.md`). Read it BEFORE reviewing. Score each rule PASS / FAIL / N/A. For each FAIL, emit HIGH/MEDIUM/LOW and a concrete fix."

**Step 3 — Aggregate findings.** Per-rule pass/fail matrix. Severity counts: HIGH = breaks a contract (Rule 12 violation, broken file reference, triggers on wrong intent), MEDIUM = degrades quality (passive citation, missing gotcha, vague description), LOW = cosmetic (line count, naming style).

**Step 4 — Loop until no HIGH remain, capped at 3 iterations.** Apply HIGH fixes with user confirmation. Re-spawn critic. Loop. Stop when 0 HIGH OR 3 iterations reached. If 3 iterations reached with HIGH still present, surface the full report to the user and let them decide whether to continue, defer, or downgrade to MEDIUM. Report MEDIUM and LOW for the user to decide.

**Step 5 — Report.** Inline if small. Otherwise write `references/review-<date>.md` (note: this lives in `crafting-skills/references/`, not in the reviewed skill's directory, to avoid polluting the reviewed skill).

**Contrast (do not confuse with):**
- `evaluating-skills` RUN mode — *behavioral* comparison (with-skill vs baseline, with transcripts). REVIEW is *static* (just reads the skill).
- `general-critic` directly — generic artifact critique. REVIEW is skill-specific and uses the compendium as lens.


### 16 Rules
```

**Step 5.3 — Verify mode ordering**

Run: `grep -n "^## \(CREATE\|OPTIMIZE\|POST-CREATE\|REVIEW\)\|^### 16 Rules" skills/crafting-skills/SKILL.md`
Expected: 5 matches in order: CREATE, OPTIMIZE, POST-CREATE, REVIEW, `### 16 Rules` (Compendium).

**Step 5.4 — Run the marketplace validator**

Run: `python3 .agents/skills/marketplace-validator/scripts/validate.py skills/crafting-skills/`
Expected: exit 0. Same warnings as Task 4.

**Step 5.5 — Commit**

```bash
git add skills/crafting-skills/SKILL.md
git commit -m "docs(crafting-skills): REVIEW mode — static critique against compendium"
```

---

## Task 6: Update CONTRAST block in SKILL.md

**Files:**
- Modify: `skills/crafting-skills/SKILL.md` — append 2 bullets to the inline Compendium's CONTRAST subsection

NOTE: After Task 2, CONTRAST is now a `### CONTRAST` subsection (h3) under the inline Compendium section, NOT a top-level `## CONTRAST` (h2). Find it accordingly.

**Step 6.1 — Locate the CONTRAST block**

Run: `grep -n "^### CONTRAST\|^- NOT for authoring a Claude Code" skills/crafting-skills/SKILL.md`
Expected: 1 CONTRAST header + the last existing bullet about Claude Code commands.

**Step 6.2 — Append 2 CONTRAST bullets**

Find this text (the last existing CONTRAST bullet — under `### CONTRAST`):

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
Expected: exit 0. Same warnings as Task 5.

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
Expected: exit 0. Expected findings:
- 1 `body_too_long` warning (SKILL.md is ~520 lines) — message starts with "This is not an exact science"
- 2 `unexpected_fm_key` warnings (`when_to_use`, `argument-hint`) — pre-existing
- 0 failures

**Step 7.2 — Run the routing test**

Run: `python3 .agents/skills/marketplace-validator/scripts/routing_test.py`
Expected: Same baseline as before this plan (6/10 wins, 1 tie, 3 pre-existing losses). Any regression (a previously-passing query now fails, or vice-versa) is a HIGH finding — fix the routing description in Task 3 or revert.

**Step 7.3 — Verify line counts**

Run: `wc -l skills/crafting-skills/SKILL.md`
Expected: ~520 lines (started at 199, +~320 net after the merge and new modes).

**Step 7.4 — Verify reference file is gone**

Run: `ls skills/crafting-skills/references/ 2>&1`
Expected: Directory exists with 4 files (context-management.md, cross-skill-discovery.md, frontmatter-complete.md, skill-self-testing.md). `best-practices-compendium.md` is NOT in the list.

**Step 7.5 — Spec coverage check**

For each spec section, identify the task that implements it:
- Section 1 (Rules 12–13) → Task 2
- Section 2 (REVIEW mode) → Task 5
- Section 3 (POST-CREATE mode) → Task 4
- Section 4 (frontmatter + router) → Task 3
- Section 5 (what this does NOT do) → honored implicitly
- Section 6 (files to change) → Tasks 1–6 cover all listed files
- Section 7 (verification) → Task 7
- Section 8 (decisions made) → baked into Tasks 4, 5 content
- Section 9 (risks and mitigations) → first risk (delegation misreading) addressed in Tasks 2 (Rule 12 verb distinction) + 5 (REVIEW Step 2 prompt)

**Step 7.6 — Read-aloud check**

Open `skills/crafting-skills/SKILL.md` and verify:
- POST-CREATE Step 3 has all 5 classes (Missed gotcha, Trigger miss, Inlined content, Stale instruction, Friction)
- REVIEW Step 2 prompt instructs the critic to read the inline compendium (not a reference file)
- The `## POST-CREATE Mode`, `## REVIEW Mode` headers are present
- The `### CONTRAST` block has the 2 new bullets about evaluating-skills and general-critic

If any element is missing or mis-worded, fix inline.

**Step 7.7 — No commit (verification only)**

If all checks pass, report "Plan complete, all tasks green." If any check fails, fix the relevant task's commit and re-run the failing check.

---

## Execution handoff

This plan is written for the **subagent-driven-development** skill (recommended). 6 implementation tasks + 1 verification task. Each task is small, self-contained, and benefits from two-stage review per the pattern used in the previous router-language plan.
