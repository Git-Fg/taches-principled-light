# Self-Correcting Skill Ingest — Design Spec

**Date:** 2026-06-24
**Status:** Approved (brainstorming phase), pending spec-file review
**Author:** Main agent (post-`devadmin@100.80.231.128:tailnet` skill import investigation)
**Target release:** next marketplace version cut (v0.1.1 or later)

## Goal

Ingest the `self-correcting` discipline skill from `~/.claude/skills/self-correcting/SKILL.md` on the devadmin VPS (`openclaw-devadmin-tailscale`) into the `taches-principled-light` marketplace as a new top-level skill, with portability edits for cross-runtime use (Claude Code + Codex + kimi-code) and a CONTRAST block that disambiguates it from `systematic-debugging` and `reviewing-and-polishing` MEMORIZE.

## Source

- **Path on VPS:** `~/.claude/skills/self-correcting/SKILL.md` (user `devadmin`, host `100.80.231.128`)
- **Local copy:** `/tmp/vps-skills/literal-claude-skills/self-correcting/SKILL.md` (75 lines, scp'd for analysis)
- **VPS scope note:** that directory contained only this one skill; the other `marketplaces/` under `~/.claude/plugins/marketplaces/` (`taches-principled-light`, `agent-browser`, `minimax-skills`) were excluded by user instruction.

## Why this skill fills a catalog gap

The marketplace currently has no skill that triggers on a *tool-usage failure cascade* — the pattern of "I tried three times with minor variations and got nowhere." The closest neighbour, `reviewing-and-polishing`'s MEMORIZE mode, captures **post-success** insights. `self-correcting` is the missing complement: **post-failure** diagnosis, in-context, with no extra tool calls.

Distinctive elements worth preserving:

1. The "no tool calls during analysis" rule — forces reflection from existing context, prevents meta-loops.
2. A structured 5-line output block (`Guidance said / What I did / Gap / Why / One fix`) — reusable as a within-session eval template.
3. A specific audit table for tool-result guidance adherence — rare discipline in the marketplace.

## Scope (in / out)

### In scope

- Create `skills/self-correcting/SKILL.md` with portability edits + CONTRAST block.
- CHANGELOG entry: `### Added — self-correcting: post-failure meta-analysis for tool-usage cascades.`
- Validation passes (marketplace-validator + marketplace-health).

### Out of scope (deferred to separate cycles)

- Refinements to `crafting-skills` (failure-cascade recognition rule).
- Narrowing `reviewing-and-polishing` MEMORIZE scope to post-success only.
- Citing `self-correcting`'s output block inside `evaluating-skills`.
- Any change to sibling skills.
- Manifest bumps beyond the standard CHANGELOG note (deferred to next release cut).

## Decisions made during brainstorm

| Decision | Choice | Rationale |
|---|---|---|
| Scope | Ingest only (no sibling-skill edits) | Cleanest marketplace discipline; sibling edits deserve their own cycles |
| Portability | Moderate port — generalize surface language, keep MCP as primary worked example, add cross-runtime note | Discipline generalizes; MCP is the dominant guidance-field runtime today; Codex/kimi-code value preserved without over-expanding body |
| CONTRAST siblings | `systematic-debugging` and `reviewing-and-polishing` (MEMORIZE mode specifically) | These are the only two skills with meaningful overlap; explicit contrast prevents trigger-steal |
| `allowed-tools` | `Read, Grep, Glob` (read-only) | Skill rule is "no tool calls during analysis"; read-only tools cover the rare re-inspection case without contradicting the rule |
| `argument-hint` | `[failure-symptom]` | Short label naming the cascade mode (e.g. `3-tool-no-progress`, `ignored-guidance`, `bad-result`) |
| `license` | `MIT` | Marketplace default |
| `name` | `self-correcting` | Source-faithful; lowercase-hyphenated is validator-standard |
| Body restructure | Source-faithful with four additions | Preserves the original's working structure; only adds framing, cross-runtime note, CONTRAST block, and a "when to stop" rule |

## Target frontmatter (final)

```yaml
---
name: self-correcting
description: "Use this skill when 3+ tool calls haven't converged, the result is bad, or the agent ignored a guidance field / system-reminder. Diagnose what happened from context — no new tool calls — and propose one specific fix. Do NOT use for bug root-cause (use systematic-debugging), post-success insight capture (use reviewing-and-polishing MEMORIZE), or routine tool-call sequences that are still converging."
when_to_use: |
  Load when an agent session shows a failure cascade: 3+ tool calls without
  progress, a bad result that the agent is about to retry with the same
  approach, or explicit guidance/system-reminder that the agent skipped.
  The skill forces a no-tool-call reflection block from existing context.
  Do NOT load for bug root cause diagnosis (systematic-debugging), for
  capturing insights after a successful task (reviewing-and-polishing
  MEMORIZE), or for routine exploratory tool calls that are still
  converging.
allowed-tools: Read, Grep, Glob
argument-hint: "[failure-symptom]"
license: MIT
---
```

**Description word count:** ~57 words. Above the 50-word soft target by 7. Trade-off: keeping "no new tool calls" in the description strengthens the routing signal more than the 7 extra words cost in budget. Validator hard ceiling is 1024 chars / well under.

## Target body structure

| § | Section | Source / new | Word budget |
|---|---|---|---|
| 1 | Why this skill exists (framing paragraph: failure cascade anti-pattern) | NEW | ~80 |
| 2 | Core rule (no tool calls during analysis; data is in context) | source-faithful | ~30 |
| 3 | Four-step protocol (verbatim listing → quote guidance → diagnose → one fix) | source-faithful | ~250 |
| 4 | Tool-result guidance audit table (signals + checks) | source-faithful | ~80 |
| 5 | Output format block (Guidance said / What I did / Gap / Why / One fix) | source-faithful | ~50 |
| 6 | Cross-runtime note (Claude Code `<system-reminder>`, Codex instructions, kimi-code tool hints; MCP is richest source today) | NEW | ~80 |
| 7 | CONTRAST (vs systematic-debugging, vs reviewing-and-polishing MEMORIZE) | NEW | ~80 |
| 8 | When to stop diagnosing (invoke self-correcting at most once per failure; produce one diagnosis block; second cascade in the same session → escalate to user or invoke `crafting-skills` for a routing audit) | NEW | ~40 |

**Estimated total body:** ~700-800 words / ~90-110 lines. Comparable to existing skills (`crafting-skills`, `evaluating-skills`).

## CONTRAST block content (final)

- **vs `systematic-debugging`:** Diagnoses *why the code is wrong* vs diagnoses *why the agent's tool usage is wrong*. Same root-cause discipline, different object. If the bug is in code, use systematic-debugging. If the agent ignored guidance / fetched all 10 results instead of top 2-3 / repeated the same approach 3 times, use self-correcting.
- **vs `reviewing-and-polishing` MEMORIZE:** MEMORIZE captures insights *after a successful task* and writes them to memory. This skill diagnoses *a failed task* and produces one in-session fix. Use MEMORIZE to remember; use self-correcting to repair.
- **Not contrasted with** `crafting-skills`, `evaluating-skills`, `applying-guardrails`: those operate on a different layer (skill authorship, skill measurement, design discipline) and don't trigger on tool-usage failure cascades. Explicit contrast would invent nearness that doesn't exist.

## Cross-runtime note (final text)

> **Tool-result guidance surfaces differ by runtime.** Claude Code surfaces guidance via `<system-reminder>` blocks and tool-result hints. Codex uses system instructions and tool-call comments. kimi-code embeds hints in tool-result metadata. The discipline is identical — quote the guidance, admit the gap, fix the execution — only the surface signal differs. MCP servers are the richest guidance-field source today; standalone CLI tools may produce no guidance at all, in which case the cascade trigger is "3+ calls without progress" alone.

## Validation flow (run before commit)

1. Write `skills/self-correcting/SKILL.md` with the design above.
2. Run `python3 .agents/skills/marketplace-validator/scripts/validate.py skills/self-correcting/` — fail fast on frontmatter, description length, hardcoded tool names, stale refs.
3. Run `python3 .agents/skills/marketplace-health/scripts/health.py` — confirm CONTRAST references to `systematic-debugging` and `reviewing-and-polishing` resolve; no doc-state drift; no missing cross-refs.
4. Adversarial-sibling check (per AGENTS.md rule 6): query a test set including "I just made 5 tool calls and got nowhere" / "the system told me to do X and I did Y instead" / "fetch returned junk and I'm retrying" — verify the agent routes to `self-correcting` and not to `crafting-skills`/`evaluating-skills`/`applying-guardrails`/`reviewing-and-polishing`.
5. CHANGELOG entry under the next version (no version bump in this commit; deferred to release cut).

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Description triggers on routine "3+ tool calls" sequences that are still converging | Description lists 3 distinct triggers (3+ calls, bad result, ignored guidance); any single one fires. The NOT clause explicitly excludes "still converging" sequences. |
| MCP-specific language limits Codex/kimi-code utility | Moderate port: surface language generalized; cross-runtime note explicitly enumerates per-runtime guidance surfaces. |
| Agent loops: invokes self-correcting → diagnoses → invokes again → diagnoses → ... | "When to stop" section caps at one round; second cascade escalates to crafting-skills or user. |
| CONTRAST references break if sibling skills are renamed | Validation step 3 catches broken cross-refs. Marketplace-health already enforces this at release time. |
| Description length exceeds soft target | Acknowledged (57 vs 50); trade-off documented above. |

## Sequencing rule

The implementation plan must:

1. Write the SKILL.md file before running validators.
2. Run marketplace-validator before marketplace-health (faster, narrower; fail-fast).
3. CHANGELOG entry last (after validation passes).
4. No release tag or version bump in this commit (deferred to next release cut per project convention).

## Acceptance criteria

- `skills/self-correcting/SKILL.md` exists and passes `marketplace-validator`.
- `marketplace-health` reports zero HIGH/MEDIUM findings attributable to the new skill.
- CHANGELOG entry added under the next-version header.
- No sibling skill modified.
- Adversarial-sibling check passes for the trigger test set.
