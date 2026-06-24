# Claude Code Skill Budget System — Evolution (May 2026 → Jun 2026)

This note documents the Claude Code skill-budget system's evolution that was NOT captured in the original deep-research `research/marketplace-routing-scaling/final.md` (dated earlier in this work arc). The findings here superseded 5 claims in the Marketplace Scaling section of AGENTS.md; this note is the audit trail.

## Summary of changes

| Setting | Earlier (deep-research cited) | Current (May/June 2026) | Source |
|---|---|---|---|
| `skillListingBudgetFraction` default | 0.01 (1%) | **0.02 (2%)** | Claude Code CHANGELOG, `Skill character budget now scales with context window (2% of context)` |
| Per-skill listing cost | ~50 tokens (name + description) | **75–150 tokens** including XML wrapper, name, location, frontmatter overhead | claudefa.st (May 2026) |
| Truncation user-visible? | "silently removed" (Anthropic bug #64606, v2.1.159) | **NO** — startup warning, `/doctor` breakdown, `/context` percentage line | Claude Code CHANGELOG: "added a startup warning when descriptions are truncated"; "Skill-listing truncation is no longer shown as a startup notification — run `/doctor` for the full breakdown"; "Improved the skill listing truncation warning to show how many skill descriptions are affected" |
| Selection logic for which skills survive | Position-based truncation in `formatCommandsWithinBudget` (priority → truncate → names-only modes) | **Recency + frequency**: most-invoked survives, least-invoked drops | claudefa.st: "The selection logic uses recency and frequency. Claude Code tracks which skills you invoke and ranks descriptions by usage." |
| Per-description cap (`skillListingMaxDescChars`) | 1,536 chars | 1,536 chars (unchanged) | claudefa.st + Anthropic docs |
| Practical marketplace ceiling at 200K context | ~15–25 skills (at old 1% default) | **~30–50 skills** at current 2% default; **~75–125** at 1M context with 1% | claudefa.st: "2,000-token budget (1% on 200K): Around 15-25 skills before truncation" |

## Implications for the Marketplace Scaling table

The 5 changes above force these corrections in the AGENTS.md → Marketplace Scaling section (committed in the same commit as this note):

1. **Default budget is 2%, not 1%** — the 200K context gives 16,000 chars, not 8,000. The "~16 skills at 500-char descriptions, ~40 at 200-char, ~80 at 100-char" math from the deep-research is **stale at the 200K context window** — at the current 2% default, those numbers roughly double.

2. **Truncation is no longer silent** — practitioners hitting the 25+ skill range get explicit warnings (startup, `/doctor`, `/context`). The prior deep-research claim "system silently discards them" was true as of v2.1.159 (May 2026) but has been superseded by Anthropic's subsequent warning improvements.

3. **Selection logic is recency + frequency, not positional** — `formatCommandsWithinBudget` priority/truncate/names-only modes still exist in the code, but the user-facing behavior is now "drop least-used skills first, keep most-used." A marketplace with 80 skills where 30 are heavily used behaves correctly even though the listing exceeds the budget.

4. **Practical recommendation for 25-50 row changed** — the original AGENTS.md advice was "tighten descriptions / split into hubs." With the recency + frequency protection, the cheaper fix is `/skills` → disable rarely-used skills (disabled skills don't count against the budget). The Marketplace Scaling 25-50 row now recommends this first; hub-splitting only becomes mandatory past 50.

5. **The 50-skill warning threshold is unchanged** — even with the recency + frequency protection, the selection logic's safety margin breaks down past ~50 skills (per claudefa.st's observation that warning fires at 25 skills but actively-used skills still get full descriptions up to ~50).

## What was NOT changed

- The deep-research's *knee-curve shape* finding (piecewise-linear with a hard knee at the budget) is **still correct** — the warning-vs-budget behavior is still piecewise-linear, just with a more graceful user-facing fallback than the original "names-only" mode implied.
- The *three scaling patterns* (in-place tightening / tool-facade hub / external retrieval) and their ranges are **unchanged** — they describe response strategies past the knee, which is independent of where the warning fires.
- The Klymentiev observation that "past about 1,000 entries the agent starts making wrong picks" is **still valid** as the >1,000 row's symptom.

## Open questions for future research

1. **Does Cursor, Codex, kimi-code, or Microsoft Agent Framework emit any analogous warning?** This research only covered Claude Code. Other platforms may have different visibility characteristics.
2. **What happens at 1M-context models?** claudefa.st reports 75–125 skills at 1M context with 1% — does the same recency + frequency protection apply, or does the larger budget introduce a different failure mode?
3. **Is there empirical data on the "actively-used" hit rate** at 50-100 skills? The recency + frequency protection is plausible but the safety margin is unstudied in the public literature.
4. **Does the Claude Code Opus 4.7 compliance cliff (issue #62562, 24-26 May 2026) interact with the budget system?** The two bugs may compound: a clamped description + a model that skips Skill tool_use = silent routing failure at any size.

## Source URLs

- Anthropic bug #64606 (silent truncation, May 2026): https://github.com/anthropics/claude-code/issues/64606
- Anthropic bug #62562 (Opus 4.7 compliance cliff, May 2026): https://github.com/anthropics/claude-code/issues/62562
- claudefa.st "Hidden Skill Budget Setting" (May 2026): https://claudefa.st/blog/guide/mechanics/skill-listing-budget
- Claude Code CHANGELOG (most recent warnings + 2% default): https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md