# Router language by audience — two-tone split

**Date:** 2026-06-22
**Status:** Design — awaiting review
**Scope:** `claude-cli/SKILL.md` (router table) + `crafting-skills/references/best-practices-compendium.md` (the actual 14-rule Best-Practices Compendium and supporting reference — `crafting-skills/SKILL.md` itself is unchanged) + a new `references/prompts/` convention for subagent prompt contracts.

## Problem

The current `claude-cli` router table applies imperative "You MUST read … BEFORE proceeding" uniformly to all 8 references. The empirical research in `research/hub-references-routing-evals/final.md` shows this is **principled but unusual**: Anthropic, superpowers, and HeyGen all use descriptive ("see", "is for", "consult when") form. The user finds uniform imperative "too violent" — but also correctly observes that agents genuinely forget to read references when the language is too soft. The fix is not "soften everything" or "keep everything imperative" — it is **differentiate by audience**.

## Section 1 — The separation criterion

The criterion is **contract vs framing**, not content type.

- **INTERNAL (contract)** — the skill enforces an obligation between itself and the agent. If the agent does not read / does not act, the operation fails or produces wrong output. Targets: file reference citations, subagent prompt contracts, command citations, skill loading chains.
- **EXTERNAL (framing)** — the skill sets context for the agent or the user. If the agent ignores, the operation still works — just less well or less idiomatically. Targets: workflow guidance, anti-patterns, handoffs, capability descriptions.

Form:

| Audience | Person | Verbs | Example |
|---|---|---|---|
| INTERNAL | 2nd | MUST / NEVER / DO NOT | "You MUST read `references/execute.md` BEFORE writing the invocation." |
| EXTERNAL | 3rd | is for / shows / describes / consult | "`references/output-contract.md` describes the text/json/stream-json shapes — consult when you need to parse." |

Why the audience is the right axis: a single reference can be both, depending on context. `output-contract.md` is INTERNAL when the agent is about to parse JSON output (MUST read or risk parsing failure), but EXTERNAL when the operation is a simple `text` invocation. Encoding audience per-row is more honest than per-file.

## Section 2 — Application to the `claude-cli` router

Contract test applied to each of the 8 references:

| Reference | If the agent ignores… | Audience |
|---|---|---|
| `execute.md` | …it invents the flags, the invocation fails | INTERNAL |
| `session.md` | …it invents `--session-resume` or loses the UUID | INTERNAL |
| `context.md` | …it forgets `--add-dir` or misses the worktree | INTERNAL |
| `review.md` | …it does a review by prompt instead of `ultrareview` | INTERNAL |
| `agent.md` | …it invents `--subagent` instead of `--agent` | INTERNAL |
| `config.md` | …it guesses `--effort` values instead of reading the list | INTERNAL |
| `output-contract.md` | …it tries to parse text with `jq` — fails, but recoverable | EXTERNAL |
| `workflows.md` | …it composes a homegrown workflow — suboptimal, but works | EXTERNAL |

Resulting router (replaces the current 8-row table in `claude-cli/SKILL.md` §3):

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

Verb contrast encodes audience: **"You MUST read … BEFORE"** = contract; **"describes / shows — consult"** = framing. No audience column, no tags — the right column's verb form is the signal.

## Section 3 — Meta-rule in `crafting-skills`

Three edits to the compendium file `references/best-practices-compendium.md` (which is the file that holds the 14 rules and the supporting reference sections — `crafting-skills/SKILL.md` itself is a router that points to it and is **not** changed by this design):

### 3.1 — Best-Practices Compendium (in `references/best-practices-compendium.md`), replace rule 7

Current (line 30 of the compendium):
> 7. **MUST, not should.** Use imperative constraint language. "MUST filter test accounts" not "always filter test accounts."

New:
> 7. **Audience-aware imperative — apply MUST to contracts, descriptive to framing.**
> - **INTERNAL contracts** (file references, subagent prompt contracts, command citations, skill loading chains) → MUST imperative. "You MUST read `references/format.md` BEFORE writing any code."
> - **EXTERNAL framing** (workflows, anti-patterns, handoffs, capability descriptions) → descriptive. "See `references/workflows.md` for end-to-end patterns."
> - The distinction: INTERNAL is a contract the agent must honor for the operation to succeed. EXTERNAL is context the agent can use or ignore. Applying MUST uniformly reads as "too violent" and dilutes the imperative signal.

### 3.2 — Skill Anatomy (in `references/best-practices-compendium.md`), extend rule 4

Current (line 67 of the compendium):
> 4. **Imperative citations only:** "You MUST read `references/format.md` BEFORE writing any code." Never "You can read" or "See reference." Passive citations are ignored by LLMs.

New:
> 4. **Audience-aware file citations.**
> - For INTERNAL contract references: "You MUST read `references/X.md` BEFORE [action]."
> - For EXTERNAL framing references: "`references/X.md` describes / shows / covers [topic] — consult when [condition]."
> - Never: "You can read", "Optionally consult", "Feel free to look at". Passive citations are ignored by LLMs in both directions.

### 3.3 — Common Pitfalls (in `references/best-practices-compendium.md`), add new row

The Common Pitfalls table is at line 101–113 of the compendium.

| Pitfall | Fix |
|---|---|
| Uniform-imperative skill | Apply MUST to INTERNAL contracts only; relax to descriptive for EXTERNAL framing. Reading 8 rows of "You MUST…" is fatiguing and dilutes the imperative signal. |

## Section 4 — Subagent prompt contract convention

A subagent prompt is a **nested contract**: the host skill binds the calling agent to pass the prompt verbatim; the prompt itself binds the subagent to its MUST/NEVER rules. Both layers are INTERNAL.

### 4.1 — New `references/prompts/` subdirectory

Optional subdirectory of `references/` for verbatim subagent prompts. Each file is a self-contained contract.

### 4.2 — First-line marker

Every prompt file starts with `# Contract: <subagent-name>` so the receiving subagent recognizes it as a binding contract. Body uses MUST / SHOULD / NEVER.

### 4.3 — Three-level form

| Level | Audience | Form | Example |
|---|---|---|---|
| Host skill body | INTERNAL | Imperative contract for the calling agent | "You MUST pass the prompt in `references/prompts/reviewer.md` verbatim to the reviewer subagent." |
| Prompt file | INTERNAL | Imperative contract for the subagent (MUST / SHOULD / NEVER) | "Review the diff. MUST cite file:line for every finding. NEVER propose architectural rewrites." |
| Description in hub table | EXTERNAL | Descriptive in the table of contents | "`references/prompts/reviewer.md` — verbatim prompt for the reviewer subagent." |

### 4.4 — Why the contract marker matters

If the calling agent paraphrases the prompt instead of passing it verbatim, the subagent loses the imperatives (MUST / NEVER). Verbatim fidelity is part of the host-level contract. The `# Contract:` first line gives the subagent a strong signal that the body is binding, not a draft.

### 4.5 — Add to `references/best-practices-compendium.md` Skill Anatomy (new rule 6 — the existing rule 5 is "Opt-out for teaching examples", at line 68)

The Skill Anatomy "File reference conventions" numbered list is at lines 64–68. The new rule 6 goes immediately after rule 5.

> 5. **Subagent prompt contracts (when applicable).**
> - If the skill includes prompts passed verbatim to subagents, place them in `references/prompts/<name>.md`.
> - Each prompt file starts with `# Contract: <subagent-name>` so the receiving subagent recognizes it as a binding contract.
> - The host skill's body MUST use imperative form when referencing the prompt: "You MUST pass `references/prompts/reviewer.md` verbatim." Descriptive explanation of what the prompt does goes in a separate sentence, not the same one.

## Section 5 — What this does NOT do

- Does not change the description field in any frontmatter. The two-tone split is about body language, not description routing.
- Does not change the 50-word description target. The 59-word `claude-cli` description remains as-is.
- Does not introduce MUST/SHOULD/MAY three-tier. The empirical evidence from `research/hub-references-routing-evals/final.md` is that LLMs do not distinguish SHOULD from MUST reliably; two tones (imperative / descriptive) is the maximum that is robust.
- Does not add new subagent prompts to `claude-cli`. The skill currently has no subagent; the convention is in place for when one is added.

## Section 6 — Files to change

| File | Change |
|---|---|
| `skills/claude-cli/SKILL.md` | Replace the router table in §3 with the two-tone table from Section 2. |
| `skills/crafting-skills/references/best-practices-compendium.md` | Edit rule 7 (audience-aware), rule 4 in Skill Anatomy (audience-aware file citations), add new rule 6 in Skill Anatomy (subagent prompt contracts), and add a new Common Pitfalls row. **Note: `crafting-skills/SKILL.md` itself is not changed — it already points to the compendium at line 199 ("You MUST read `references/best-practices-compendium.md`…").** |
| `skills/claude-cli/references/prompts/` | Create the directory (empty, awaiting first contract). |

## Section 7 — Verification

1. `python3 .agents/skills/marketplace-validator/scripts/validate.py skills/claude-cli/ skills/crafting-skills/` → 0 failures, only expected `when_to_use` and description-length warnings. The compendium file in `references/` is not directly validated (the validator only inspects SKILL.md frontmatter), so its 0-failure check is structural — the Edit operations must produce valid markdown tables and numbered lists.
2. Body line count: `skills/claude-cli/SKILL.md` must stay under 200 lines (currently 128, the table is the same row count).
3. `skills/crafting-skills/references/best-practices-compendium.md` net addition: ~20 lines (rule 7 expansion +2 lines, rule 4 Anatomy expansion +3 lines, new rule 6 +5 lines, new Common Pitfalls row +1 line, blank-line adjustments ~+9 lines; total ~+20).
4. `references/prompts/` exists as an empty directory in `skills/claude-cli/references/prompts/` (with `.gitkeep`).

## Open questions

- **A/B test of the two-tone vs uniform imperative on routing accuracy** — no public benchmark exists; this design rests on the principle that the contrast sharpens the imperative signal. Future: a 100-pair (skill, utterance) eval comparing the two forms.
- **Where the `# Contract:` marker should appear in long prompts** — first line vs first heading. First line keeps it in the body Claude parses; first heading might be skipped by some parsers. Default: first non-frontmatter line.
- **Whether to add a `MUST NOT paraphrase` rule at the host level** — would be redundant with the "MUST pass verbatim" rule but might be more memorable. Skip unless we have evidence the paraphrase rate is high.
