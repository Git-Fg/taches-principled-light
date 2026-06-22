# Best-Practices Compendium & Supporting Reference

You MUST read this file BEFORE applying Step 4 ("Write the Body") of CREATE mode, and before any audit in OPTIMIZE mode. The 14 rules below are the load-bearing constraints; everything else in this file is supporting reference.

## 14 Rules (from SkillsBench + production experience)

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

7. **Audience-aware imperative — apply MUST to contracts, descriptive to framing.**
   - **INTERNAL contracts** (file references, subagent prompt contracts, command citations, skill loading chains) → MUST imperative. "You MUST read `references/format.md` BEFORE writing any code."
   - **EXTERNAL framing** (workflows, anti-patterns, handoffs, capability descriptions) → descriptive. "See `references/workflows.md` for end-to-end patterns."
   - The distinction: INTERNAL is a contract the agent must honor for the operation to succeed. EXTERNAL is context the agent can use or ignore. Applying MUST uniformly reads as "too violent" and dilutes the imperative signal.

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
