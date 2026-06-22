# Steering skill authors to point at sources (with post-create and review modes)

**Date:** 2026-06-22
**Status:** Design — awaiting review
**Scope:** `skills/crafting-skills/SKILL.md` (router + 2 new modes POST-CREATE and REVIEW + frontmatter + CONTRAST) + `skills/crafting-skills/references/best-practices-compendium.md` (2 new rules: 15 "point to live sources", 16 "post-creation observation is part of the skill"). No other skill touched.

## Problem

When an AI agent writes a skill with `crafting-skills`, it sometimes inlines content that lives elsewhere instead of citing the source. Concrete failure reported by the user on `2026-06-22`:

> "Scout all the capacities from the agent-browser get skills to make sure to, without repeating what can be easily found, include all the proper guidance of must/should load when the agent-browser skill get commands with or without --full"

The right form is one line — `You MUST run \`agent-browser skills get core\` BEFORE running any \`agent-browser\` command.` The agent produced a paragraph that asks itself to scout and re-include, which (a) duplicates content the CLI already exposes, (b) will rot the moment the CLI changes, (c) wastes skill-body tokens that should go to gotchas, and (d) makes the skill slower to maintain.

The current `crafting-skills` allows this because:

1. **The compendium has no rule against inlining dynamic content.** Rule 4 ("audience-aware file citations") covers *how* to cite internal references, not *whether* to cite external content. Rule 10 ("skip what the model already knows") is about facts the model has, not content the model can fetch on demand.
2. **No mode catches the failure after the fact.** CREATE produces a skill. OPTIMIZE only retunes the *description* (routing), not the body. There is no mode that reads a skill and asks "did you just inline content that lives in a CLI/library/other-skill?"
3. **No mode observes the immediate post-creation use.** The user almost always uses a freshly-created skill right away. The transcripts of that use reveal exactly which parts of the skill failed to steer the agent — but nothing in the marketplace reads those transcripts and proposes edits.

The fix has three parts:

- A new **Rule 15** that *forbids* inlining content from dynamic, static, or cross-skill sources and *requires* citation by command/path/name.
- A new **Rule 16** that makes post-creation observation part of the skill contract.
- Two new modes in `crafting-skills/SKILL.md`: **REVIEW** (static critique against the compendium, including Rule 15) and **POST-CREATE** (read what happened during the immediate use, propose 3-5 targeted edits).

## Section 1 — The two new compendium rules

### Rule 15 — Point to live sources, don't inline them

Skills MUST cite the source of information instead of recreating it in the skill body. Three categories of "source":

| Category | What it is | Citation form | Example |
|---|---|---|---|
| **Dynamic** | CLIs, libraries, web APIs, `--help` output | Imperative command + `BEFORE` | `You MUST run \`agent-browser skills get core\` BEFORE running any \`agent-browser\` command.` |
| **Static intra-skill** | `references/X.md`, `scripts/Y.py`, `assets/Z.json` | Audience-aware imperative (Rule 4) | `You MUST read \`references/execute.md\` BEFORE writing the invocation.` |
| **Cross-skill** | Other marketplace skills (`evaluating-skills`, `general-critic`, etc.) | Name + protocol-applied form | `You MUST read \`evaluating-skills\` and apply its protocol BEFORE running the post-creation loop.` |

| Cross-skill references MUST use the canonical verb form: **"read and apply"**. (Variations like "consult and follow" or "read the protocol" are acceptable synonyms but "read and apply" is canonical.)
- "Load" and "delegate to" are wrong for skills. A skill is NOT a subagent — it is an injection of context/protocol the agent reads and applies directly. Using subagent verbs ("load", "delegate") makes the agent spawn unnecessary subagents or skip reading altogether.
- **"MUST"** for INTERNAL contracts (file references, subagent prompt contracts, command citations, cross-skill protocol citations).
- **Descriptive** (`describes`, `shows`, `is for`, `consult when`) for EXTERNAL framing.

The test for every paragraph in a skill body, applied in order:

1. *Does the agent need this fact?* If no → delete (Rule 10).
2. *Can the agent load this content on demand?* If yes → cite, don't inline (Rule 15).
3. *Is the citation INTERNAL (contract) or EXTERNAL (framing)?* Encode audience in the verb form (Rule 4 + Rule 7).
4. *Is this content already cited elsewhere in the skill?* If yes → deduplicate, do not repeat.

The antipattern the rule prevents: the agent inlining a 30-line summary of the agent-browser command reference because it doesn't trust the model to run `agent-browser skills get core` at runtime. The trust bet is wrong — the agent can and will run the command; the inlined content rots on first CLI release.

### Rule 16 — Post-creation observation is part of the skill

Skills are written once and used many times. The cost of a skill that drifts out of sync with reality grows with each use. A skill MUST support an observation loop:

- The author MUST design the skill so that what happens during use can be observed (transcripts, gotcha occurrences, friction points, agent rationalizations).
- The skill MUST include a path to propose updates based on observed behavior — concretely, **POST-CREATE mode** in `crafting-skills`.
- A skill that is "fire and forget" accumulates debt. A skill that observes-and-improves stays accurate.

This rule creates the *reason d'être* of POST-CREATE mode (Section 3 below). It also creates an obligation on skill authors: if you cannot observe the skill's use (e.g., the skill is for an offline workflow with no transcript), document that explicitly and provide the next-best feedback path.

## Section 2 — REVIEW mode (static critique)

*Critique an existing skill against the 16-rule Best-Practices Compendium and propose fixes.*

**Step 1 — Read the skill.** Read `SKILL.md` + `references/` (one file at a time, on demand) + `scripts/` + `assets/`. If the skill exceeds 1000 lines total, read `SKILL.md` first, then references one at a time.

**Step 2 — Spawn a critic subagent.** Apply the `general-critic` contract (HIGH/MEDIUM/LOW) with the compendium as the lens. The critic MUST NOT modify files — return findings only, with file:line, severity, and proposed fix. The critic prompt MUST include: "Your lens is the 16-rule Best-Practices Compendium at `skills/crafting-skills/references/best-practices-compendium.md`. Read it BEFORE reviewing. Score each rule PASS / FAIL / N/A. For each FAIL, emit HIGH/MEDIUM/LOW and a concrete fix."

**Step 3 — Aggregate findings.** Per-rule pass/fail matrix. Severity counts: HIGH = breaks a contract (Rule 15 violation, broken file reference, triggers on wrong intent), MEDIUM = degrades quality (passive citation, missing gotcha, vague description), LOW = cosmetic (line count, naming style).

**Step 4 — Loop until no HIGH remain, capped at 3 iterations.** Apply HIGH fixes with user confirmation. Re-spawn critic. Loop. Stop when 0 HIGH OR 3 iterations reached. If 3 iterations reached with HIGH still present, surface the full report to the user and let them decide whether to continue, defer, or downgrade to MEDIUM. Report MEDIUM and LOW for the user to decide.

**Step 5 — Report.** Inline if small. Otherwise write `references/review-<date>.md` (note: this lives in `crafting-skills/references/`, not in the reviewed skill's directory, to avoid polluting the reviewed skill).

**Contrast (do not confuse with):**
- `evaluating-skills` RUN mode — *behavioral* comparison (with-skill vs baseline, with transcripts). REVIEW is *static* (just reads the skill).
- `general-critic` directly — generic artifact critique. REVIEW is skill-specific and uses the compendium as lens.

## Section 3 — POST-CREATE mode (immediate-use observation)

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

## Section 4 — Frontmatter and router updates

### Decision Router (in `SKILL.md`)

```
IF the user wants to **create a new skill from scratch** → use **CREATE** mode below.
IF the user wants to **optimize an existing skill's routing** → use **OPTIMIZE** mode below.
IF the user wants to **statically critique an existing skill** → use **REVIEW** mode below.
IF the user wants to **observe immediate post-creation use and propose edits** → use **POST-CREATE** mode below.
IF unclear → ask: "Are you creating, optimizing, reviewing, or post-creating a skill?"
```

### Frontmatter

- `description:` (≤50 words, audience-aware):
  > Load when creating, optimizing, reviewing, or post-iterating an agent skill. Use when the user says 'create a skill', 'review this skill', 'self-review', 'I just used it — propose updates', or 'validate frontmatter'. Do NOT use for collaborative skill creation dialogue (use superpowers' writing-skills).

- `argument-hint:` `[create|optimize|review|post-create] [target-skill-path]`

- `allowed-tools:` extend with `Agent` (for REVIEW mode critic spawning)

### CONTRAST additions

Add to existing CONTRAST block:
- NOT for behavioral comparison of skill effectiveness → use `evaluating-skills` RUN mode (POST-CREATE and REVIEW do not replace it; they complement it for lightweight, immediate cases).
- NOT for generic artifact critique (non-skill) → use `general-critic` directly.

## Section 5 — What this does NOT do

- **Does not change the OPTIMIZE mode.** OPTIMIZE is about description/routing only. It stays.
- **Does not add a behavioral evaluation harness.** That is `evaluating-skills`. POST-CREATE is the lightweight sibling for the same-session case.
- **Does not prescribe the form of POST-CREATE transcripts.** The mode says "if transcripts exist, read them" — it does not require a specific format.
- **Does not auto-apply edits.** All proposed edits require user confirmation in Step 4/5. This is non-negotiable.
- **Does not bump the marketplace version.** This is a skill-body change, no version implications.

## Section 6 — Files to change

| File | Change | Lines added |
|---|---|---|
| `skills/crafting-skills/SKILL.md` | Update Decision Router, add POST-CREATE and REVIEW modes, update frontmatter, update CONTRAST | +90 |
| `skills/crafting-skills/references/best-practices-compendium.md` | Add Rule 15 (point to live sources) and Rule 16 (post-creation observation is part of the skill) | +25 |

Net: ~115 lines added. `crafting-skills/SKILL.md` goes from 199 → ~290 lines (under the 500-line cap).

## Section 7 — Verification

1. `python3 .agents/skills/marketplace-validator/scripts/validate.py skills/crafting-skills/` — must report 0 failures, only pre-existing warnings (4 expected: `when_to_use` and `argument-hint` notices, description word-count).
2. `python3 .agents/skills/marketplace-validator/scripts/routing_test.py` — must not regress on the 10 default utterances.
3. Manual test: read the new SKILL.md and the new compendium rules aloud and verify (a) the router table covers the 4 modes, (b) Rule 15 forbids inlining with concrete examples, (c) POST-CREATE Step 3 classification covers the 5 known failure modes.
4. Cross-check: any skill in the marketplace that currently inlines dynamic content (e.g., lists of CLI flags instead of `--help`) should now trigger a Rule 15 violation when REVIEW'd. This is a useful canary.

## Section 8 — Decisions made during brainstorming

1. **REVIEW mode loop depth.** Capped at 3 iterations. If HIGH remains after 3 iterations, surface to user. (Baked into Section 2 Step 4.)
2. **POST-CREATE transcript scope.** Current session only. Prior sessions are `evaluating-skills` territory. (Baked into Section 3.)
3. **Rule 15 verb form for cross-skill references.** Canonical: "read and apply". (Baked into Section 1.)
4. **Frontmatter `allowed-tools: Agent`.** Approved — needed for REVIEW mode critic spawning. Same trust model as `evaluating-skills` (which has `Read, Write, Edit, Bash, Glob, Grep`). REVIEW is more restricted (no Write/Edit), which is appropriate for a critique-only mode.
5. **Implementation shape.** Modes live inline in `crafting-skills/SKILL.md` (no separate reference files), per user choice. SKILL.md goes from 199 → ~290 lines.

## Section 9 — Risks and mitigations

| Risk | Mitigation |
|---|---|
| Agent interprets "read and apply" as "delegate" and spawns a subagent to read the skill | CONTRAST section + Rule 15 examples make the distinction explicit; marketplace-validator can flag "delegate to <skill-name>" as an antipattern |
| POST-CREATE proposes too many edits (5+ classes fire at once) | Cap at 5 edits; group by class; require user pick which to apply |
| REVIEW critic gets stuck on N/A rules (e.g., "this skill has no references") | Pass/fail/N/A matrix; the critic must justify each N/A |
| Rule 15 example using `agent-browser` becomes stale if the CLI renames | Example is illustrative; the rule is structural. Even if `skills get core` becomes `skills load core`, the rule still applies. Validator doesn't enforce example syntax. |
| Description word count exceeds 50 after the update | Drafted at 47 words; if reviewer wants fewer, drop "or post-iterating" |
