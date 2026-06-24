# Claude Code Skill Budget System — Evolution (Feb 2026 → Jun 2026)

This note documents the Claude Code skill-budget system's evolution that was NOT captured in the original deep-research `research/marketplace-routing-scaling/final.md` (dated earlier in this work arc). The findings here superseded 5 claims in the Marketplace Scaling section of AGENTS.md; this note is the audit trail.

## Summary of changes

| Setting | Earlier (deep-research cited) | Current (May/June 2026) | Source |
|---|---|---|---|
| `skillListingBudgetFraction` default | 1% (claimed) | **1% — but verified as such via `code.claude.com/docs/en/settings` and claudefa.st's v2.1.129 binary extraction. The prior research note incorrectly stated "default raised from 1% to 2%" — the actual direction was 2% (implicit) → 1% (explicit) when the setting was made user-tunable.** | `code.claude.com/docs/en/settings`; claudefa.st (May 2026); v2.1.32 CHANGELOG entry on the prior implicit 2% scaling formula |
| Per-skill listing cost | ~50 tokens (name + description) | **75–150 tokens** including XML wrapper, name, location, frontmatter overhead | claudefa.st (May 2026) |
| Truncation user-visible? | "silently removed" (Anthropic bug #64606, v2.1.159) | **NO** — startup warning, `/doctor` breakdown, `/context` percentage line | Claude Code CHANGELOG: "added a startup warning when descriptions are truncated"; "Skill-listing truncation is no longer shown as a startup notification — run `/doctor` for the full breakdown"; "Improved the skill listing truncation warning to show how many skill descriptions are affected" |
| Selection logic for which skills survive | Position-based truncation in `formatCommandsWithinBudget` (priority → truncate → names-only modes) | **Recency + frequency**: most-invoked survives, least-invoked drops | claudefa.st: "The selection logic uses recency and frequency. Claude Code tracks which skills you invoke and ranks descriptions by usage." |
| Per-description cap (`skillListingMaxDescChars`) | 1,536 chars | 1,536 chars (unchanged) | claudefa.st + Anthropic docs |
| Practical marketplace ceiling at 200K context | (deep-research did not specify; assumed to scale with default) | **~15–25 skills** at current 1% default; **~75–125** at 1M context with 1% | claudefa.st: "2,000-token budget (1% on 200K): Around 15-25 skills before truncation" |

## Correction history (supersedes earlier text)

Earlier versions of this note (and AGENTS.md) claimed "default raised from 1% to 2%" based on a misreading of the v2.1.32 CHANGELOG entry "Skill character budget now scales with context window (2% of context)." That entry describes the *prior implicit scaling formula*, not the current default. The actual timeline:

- **Before v2.1.32**: fixed 15,000-character budget (per Anthropic docs that were never updated; tracked in `anthropics/claude-code#23406`).
- **v2.1.32 (Feb 5, 2026)**: switched to implicit 2% scaling formula. CHANGELOG: "Skill character budget now scales with context window (2% of context), so users with larger context windows can see more skill descriptions without truncation."
- **v2.1.105+**: `skillListingBudgetFraction` setting introduced as a user-tunable override. Per `code.claude.com/docs/en/settings` (min-version annotation: `2.1.105`), the default was **`0.01` (1%) from the moment the setting was introduced** — i.e., the explicit 1% default supersedes the v2.1.32 implicit 2% scaling formula. Anthropic docs do not separately document a 2%-period window for this setting.
- **v2.1.129 (May 2026)**: claudefa.st publicly reverse-engineered the setting's binary schema and confirmed the `0.01` default, becoming the first widely-available public documentation of the knob. Anthropic docs were updated later; `code.claude.com/docs/en/settings` now reflects the same default.

Net direction: **default lowered from 2% (implicit, v2.1.32–v2.1.104) to 1% (explicit, v2.1.105+)** — the lowering happened when the explicit setting was introduced, not at v2.1.129. The earlier note's "raised from 1% to 2%" claim was the inverse of the actual change. Anthropic docs (`code.claude.com/docs/en/settings`), claudefa.st's May 2026 binary analysis, and Anthropic bug #64606 (filed 2026-06-02 against v2.1.159) all confirm the 1% default. Sources: `https://claudefa.st/blog/guide/mechanics/skill-listing-budget`, `https://code.claude.com/docs/en/settings`, `https://github.com/anthropics/claude-code/issues/23406`.

## Implications for the Marketplace Scaling table

The corrections above force these corrections in the AGENTS.md → Marketplace Scaling section:

1. **Default budget is 1%, not 2%** — the 200K context gives ≈2,000 tokens / ≈8,000 chars, not 16,000. The "~15–25 skills at 200K, ~75–125 at 1M" ceiling from claudefa.st is the operative range. The earlier note's "~30–50 at 200K" was double-counted because it was based on the wrong 2% default.

2. **Truncation is no longer silent** — practitioners hitting the 25+ skill range get explicit warnings (startup, `/doctor`, `/context`). The prior deep-research claim "system silently discards them" was true as of v2.1.159 (May 2026) but has been superseded by Anthropic's subsequent warning improvements.

3. **Selection logic is recency + frequency, not positional** — `formatCommandsWithinBudget` priority/truncate/names-only modes still exist in the code, but the user-facing behavior is now "drop least-used skills first, keep most-used." A marketplace with 80 skills where 30 are heavily used behaves correctly even though the listing exceeds the budget.

4. **Practical recommendation for 25-50 row** — the original AGENTS.md advice was "tighten descriptions / split into hubs." With the recency + frequency protection, the cheaper fix is `/skills` → disable rarely-used skills (disabled skills don't count against the budget). The Marketplace Scaling 25-50 row now recommends this first; hub-splitting only becomes mandatory past 50.

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
5. **Why did Anthropic choose 1% as the explicit default (vs the v2.1.32 implicit 2% scaling formula)?** The setting was added in v2.1.105 with `0.01` as the default; the rationale is not yet documented in Anthropic's published changelog. Not yet documented in Anthropic's published changelog.

## Source URLs

- Anthropic docs `code.claude.com/docs/en/settings` (current settings table): https://code.claude.com/docs/en/settings
- Anthropic docs `code.claude.com/docs/en/skills` (skill behavior): https://code.claude.com/docs/en/skills
- Anthropic bug #64606 (silent truncation, v2.1.159, May 2026): https://github.com/anthropics/claude-code/issues/64606
- Anthropic bug #23406 (docs still claim 15,000-char fixed default after v2.1.32): https://github.com/anthropics/claude-code/issues/23406
- Anthropic bug #62562 (Opus 4.7 compliance cliff, May 2026): https://github.com/anthropics/claude-code/issues/62562
- claudefa.st "Hidden Skill Budget Setting" (May 2026, v2.1.129 binary extraction): https://claudefa.st/blog/guide/mechanics/skill-listing-budget
- Claude Code CHANGELOG (current): https://code.claude.com/docs/en/changelog