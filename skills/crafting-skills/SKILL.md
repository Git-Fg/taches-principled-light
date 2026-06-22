---
name: crafting-skills
description: "Load when creating, optimizing, reviewing, or post-iterating an agent skill. Use when the user says 'create a skill', 'review this skill', 'self-review', 'I just used it — propose updates', or 'validate frontmatter'. Do NOT use for collaborative skill creation dialogue (use superpowers' writing-skills)."
allowed-tools: Read, Edit, Write, Grep, Glob, Agent
when_to_use: "Use when creating a new skill or optimizing an existing skill's routing."
argument-hint: "[create|optimize|review|post-create] [target-skill-path]"
license: MIT
---
# Crafting Skills

> **Overview.** A four-mode methodology for authoring and tuning agent skills. **CREATE** produces a new skill from scratch following the 6-step pipeline; **OPTIMIZE** audits and tightens an existing skill's routing without breaking its body; **REVIEW** statically critiques an existing skill against the inline 16-rule Best-Practices Compendium; **POST-CREATE** observes what happened during the user's immediate use of a freshly-created skill and proposes 3-5 targeted edits. All four modes use the inline 16-rule Best-Practices Compendium (below) and the same pre-commit validation (§2.6).

> **Table of contents**
> - §1 Decision Router
> - §2 CREATE mode (6 steps)
> - §3 OPTIMIZE mode
> - §4 Best-Practices Compendium — inline 16 rules (Descriptions, Naming, Body, Evidence) + supporting reference (skill anatomy, native tool referencing, split-vs-combine, common pitfalls, contrast)
> - §5 Reference files

Four modes (CREATE, OPTIMIZE, REVIEW, POST-CREATE). Start here — the router tells you which path to take.

## Decision Router

IF the user wants to **create a new skill from scratch** → use **CREATE** mode below.
IF the user wants to **optimize an existing skill's routing** → use **OPTIMIZE** mode below.
IF the user wants to **statically critique an existing skill** (per compendium rules) → use **REVIEW** mode below.
IF the user wants to **observe what happened during immediate post-creation use and propose edits** → use **POST-CREATE** mode below.
IF unclear → ask: "Are you creating, optimizing, reviewing, or post-creating a skill?"

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
- REVIEW mode (defined just above) — looks at the skill statically. POST-CREATE looks at what the agent *did* with the skill.


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
   - **Load tier** (SKILL.md body): ≤500 lines is a guideline, not a hard rule. Meta-skills and universally-applicable content legitimately exceed 500 lines; mode-specific content should still split to references/.
   - **Runtime tier** (scripts/, references/, assets/): unbounded, loaded only on demand.

10. **Skip what the model already knows.** If it's easy to explain, the model already knows it. Delete it. The test: "Would the agent get this wrong without this instruction?" If no, the sentence cannot afford to be there.

11. **Don't railroad.** Prescribe intent and judgment, not exact command sequences. The model does better recovering from errors when it understands the goal rather than following a brittle script.

12. **Point to live sources, don't inline them.** Skills MUST cite the source of information instead of recreating it in the skill body. Three categories:

    | Category | What it is | Citation form | Example |
    |---|---|---|---|
    | **Dynamic** | CLIs, libraries, web APIs, `--help` output | Imperative command + `BEFORE` | `You MUST run \`agent-browser skills get core\` BEFORE running any \`agent-browser\` command.` |
    | **Static intra-skill** | `references/X.md`, `scripts/Y.py`, `assets/Z.json` | Audience-aware imperative (Rule 7) | `You MUST read \`references/execute.md\` BEFORE writing the invocation.` |
    | **Cross-skill** | Other marketplace skills (`evaluating-skills`, `general-critic`, etc.) | `read and apply` (canonical verb form) | `You MUST read \`evaluating-skills\` and apply its protocol BEFORE running the post-creation loop.` |

    Cross-skill references MUST use the canonical verb form: **"read and apply"**. (Variations like "consult and follow" or "read the protocol" are acceptable synonyms but "read and apply" is canonical.)
    - "Load" and "delegate to" are wrong for skills. A skill is NOT a subagent — it is an injection of context/protocol the agent reads and applies directly. Using subagent verbs ("load", "delegate") makes the agent spawn unnecessary subagents or skip reading altogether.
    - "MUST" for INTERNAL contracts (file references, subagent prompt contracts, command citations, cross-skill protocol citations).
    - Descriptive (`describes`, `shows`, `is for`, `consult when`) for EXTERNAL framing.

    The test for every paragraph in a skill body, applied in order:
    1. *Does the agent need this fact?* If no → delete (Rule 10).
    2. *Can the agent load this content on demand?* If yes → cite, don't inline (Rule 12).
    3. *Is the citation INTERNAL (contract) or EXTERNAL (framing)?* Encode audience in the verb form (Rule 7).
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

