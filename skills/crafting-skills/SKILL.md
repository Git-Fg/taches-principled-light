---
name: crafting-skills
description: >
  Load when creating a new agent skill from scratch or optimizing an existing
  skill's routing. Use when the user says 'create a skill', 'write a new skill',
  'optimize this skill's routing', 'fix the trigger phrases', 'benchmark my
  descriptions', or 'validate frontmatter'. Covers local workspace skills
  (.agents/skills/) by default; covers global skills (~/.agents/skills/,
  ~/.claude/skills/, custom paths) when explicitly requested. Do NOT use for
  collaborative skill creation dialogue (use superpowers' writing-skills).
allowed-tools: Read, Edit, Write, Grep, Glob
when_to_use: "Use when creating a new skill or optimizing an existing skill's routing."
---
# Crafting Skills

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

---

## Best-Practices Compendium

These 14 rules encode findings from SkillsBench (7,308 trajectories, 7 model-harness configurations) and production experience at Anthropic and Perplexity. Apply them to every skill you touch.

### Descriptions

1. **Start with "Load when…"** — the description is a routing trigger. It is NOT documentation.
   ✓ `Load when the user needs to extract text and tables from PDF files.`
   ✗ `Processes PDF files and extracts text.`

2. **Include negative triggers.** Every description must state what NOT to use the skill for, referencing sibling skills by exact name.
   ✓ `Do NOT use for Vue, Svelte, or vanilla CSS projects.`

3. **Target ≤50 words.** Every word costs ~100 tokens per session across all users. If the model already knows it, delete it.

4. **Write in third person.** The description is injected into the system prompt. "I" or "you" causes discovery problems.

### Naming

5. **Use gerund form** (verb + -ing): `processing-pdfs`, `analyzing-sessions`, `managing-rules`. Avoid abstract nouns (`expertise`, `analytics`) and acronyms (`ddd`, `fpf`).

6. **Name must exactly match the parent directory.** `name: crafting-skills` must live in `crafting-skills/SKILL.md`. Max 64 characters, lowercase letters, numbers, and hyphens only.

### Body

7. **MUST, not should.** Use imperative constraint language. "MUST filter test accounts" not "always filter test accounts."

8. **Gotchas are the highest-signal content.** Every time the agent fails, add a one-line gotcha. This section accrues the most value over time. Append, don't restructure.

9. **Progressive disclosure across three tiers:**
   - **Index tier** (description): ~100 tokens per skill, paid every session. Ruthless.
   - **Load tier** (SKILL.md body): ≤500 lines. Split to references/ if approaching.
   - **Runtime tier** (scripts/, references/, assets/): unbounded, loaded only on demand.

10. **Skip what the model already knows.** If it's easy to explain, the model already knows it. Delete it. The test: "Would the agent get this wrong without this instruction?" If no, the sentence cannot afford to be there.

11. **Don't railroad.** Prescribe intent and judgment, not exact command sequences. The model does better recovering from errors when it understands the goal rather than following a brittle script.

### Evidence

12. **Self-generated Skills provide zero benefit on average.** Models cannot reliably author the procedural knowledge they benefit from consuming (SkillsBench §4.1.1, Finding 3). Human judgment must be injected into every skill.

13. **2-3 Skills loaded simultaneously is optimal.** More skills show diminishing returns; each additional skill dilutes the attention budget (SkillsBench §4.2.1).

14. **Moderate-length Skills outperform comprehensive ones.** There is a sweet spot beyond which more tokens hurt performance. Be concise, not exhaustive (SkillsBench §4.2.2).

---

## Skill Anatomy

```
skill-name/
├── SKILL.md              # YAML frontmatter + body (<500 lines)
├── scripts/              # Executable code for deterministic/fragile operations
├── references/           # Heavy docs — one level deep, loaded on demand
└── assets/               # Templates, JSON schemas — copied and filled
```

**File reference conventions:**
1. **Path resolution:** Paths resolve within the skill's folder. Use clean relative paths: `references/file.md`.
2. **No parent traversal:** MUST NOT use `../`. Skills are self-contained. Cross-skill references are semantic (by name), not path-based.
3. **Centralized routing:** Only SKILL.md cites supporting files. Reference files must never cross-cite each other.
4. **Imperative citations only:** "You MUST read `references/format.md` BEFORE writing any code." Never "You can read" or "See reference." Passive citations are ignored by LLMs.

---

## Native Tool Referencing

Hardcoded tool names break when APIs rename. Use semantic natural language that delegates to whatever is currently available.

| Brittle (breaks on rename) | Forward-compatible |
|---|---|
| `Use the Agent tool to spawn` | `Use your native tools to spawn a subagent` |
| `Use the Write tool` | `Use your native tools to write the file` |
| `Use the Bash tool` | `Use your native tools to run shell commands` |

Exception: MCP fully-qualified names (`BigQuery:bigquery_schema`) must stay exact — those are server-level identities.

---

## When to Split vs Combine Skills

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

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Vague description | Add explicit "Use when user says 'X'" phrases |
| Missing negative trigger | Add "Do NOT use for…" referencing sibling skills by name |
| Guidelines-only `context:fork` | A forked skill without actionable tasks wastes the subagent. Use forks for executing workflows, not injecting reference knowledge. |
| Brittle path reference | Use clean relative paths — paths resolve within the skill's folder |
| Passive file citations | "You MUST read `references/X.md` BEFORE proceeding" — never "You can read" |
| Skill never triggers | Check for `disable-model-invocation: true`; add explicit trigger phrases |
| Skill triggers at wrong time | Add negative triggers; narrow the action verb |
| Too long (>500 lines) | Split heavy content into references/ |
| Self-generated content | Don't ask the model to write a skill for itself — inject human judgment |

### When Your Skill Isn't Working

- **Never triggers:** Add "Use when: [phrase1], [phrase2]" to description. Check `disable-model-invocation`.
- **Triggers at wrong time:** Add "Do NOT use for: [wrong contexts]". Narrow the action verb.
- **Loads but doesn't do what you want:** Rewrite as step-by-step imperatives. Check `allowed-tools:`.

---

## CONTRAST

- NOT for collaborative skill creation dialogue — use superpowers' `writing-skills`
- NOT for planning a multi-phase project — use `plan-lifecycle`
- NOT for managing rules or AGENTS.md — use `managing-rules`
- NOT for authoring agent definitions — use `orchestrating-subagents`
- NOT for polishing an existing skill's prose — use `reviewing-and-polishing`
- NOT for authoring a Claude Code command or hook — see official Claude Code docs