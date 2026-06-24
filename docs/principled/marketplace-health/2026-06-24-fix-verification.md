# Marketplace Health + Verification Report — 2026-06-24

_Generated after the `5adb44c` H1 fix and four rounds of independent subagent self-critic (`9927e3e`, `5e26e36`, plus this round)._

## Health sweep

| Check | Result |
|---|---|
| Validator | 0 failures, 0 warnings across 30 skills |
| Manifest Consistency | ✓ all manifests at version 0.0.9 |
| License Coverage | ✓ all skills declare a license |
| Cross References | ✓ all references and scripts resolve |
| Skill Count | 30 SKILL.md files in skills |
| Docs Reflect State | ✓ README reflects current count (30); CHANGELOG latest (0.0.9) matches |

`HEALTH: pass (validator=0/0)`

## Third-critic pass (`9927e3e`)

The independent subagent review of `5adb44c` caught one HIGH and two MEDIUM findings:

### HIGH-1 — Fixed

`skills/crafting-skills/references/context-management.md` line 79 still said *"descriptions are dropped silently"*. This is the same class of error the H1 fix was meant to correct (user-visible docs contradicting AGENTS.md's "Truncation is NOT silent" framing). Rewritten to match AGENTS.md: three user-visible signals enumerated (startup warning, `/doctor`, `/context`), selection noted as recency + frequency, citations to `code.claude.com/docs/en/settings` and `anthropics/claude-code#64606` included.

### MEDIUM-1 — Fixed

AGENTS.md line 140 audit-trail paragraph read *"supersedes the prior budget claims in `research/marketplace-routing-scaling/final.md`"*, which misleadingly implied the upstream research was wrong. Reframed: the error was in the AGENTS.md integration layer (misreading the v2.1.32 CHANGELOG line as a default change); the upstream research was already correct at 1% / 8,000 chars.

### MEDIUM-2 — Fixed

`research/claude-code-skill-budget-evolution.md` timeline conflated two events: the explicit `skillListingBudgetFraction` setting being introduced (v2.1.105 with default `0.01`) versus claudefa.st's public documentation of the same setting (v2.1.129). Reframed: the lowering from 2% (implicit, v2.1.32–v2.1.104) to 1% (explicit, v2.1.105+) happened when the setting was introduced. v2.1.129 is when the public documentation caught up.

### Other third-critic-pass fixes

- AGENTS.md → Marketplace Scaling: version-anchor blockquote added at the top of the section, making the v2.1.105+ dependency explicit.
- `.agents/skills/releasing-marketplace/SKILL.md` Step 1: version-anchor blockquote added before the catalog-size severity table.
- `CHANGELOG.md` line 59: the `ced6d05` entry now flags that its inverted-direction claim was superseded by `5adb44c`.
- Sweep of `docs/principled/specs/`: no stale `2% default` references found.

## Fourth-critic pass (`5e26e36`)

The fourth-critic pass caught four residual v2.1.129-framing one-liners the third-critic propagation sweep missed:

1. AGENTS.md cross-platform table cell (line 124): `(v2.1.105+; current default since v2.1.129)` → `(v2.1.105+)` with the cell body now distinguishing v2.1.105 (default introduced with the setting) from v2.1.129 (claudefa.st first publicly documented the knob).
2. `research/cross-platform-skill-budget-comparison.md` line 7 (snapshot date): same fix pattern.
3. `research/cross-platform-skill-budget-comparison.md` line 42 (critical finding bullet 1): `v2.1.129 default lowering` → `v2.1.105 explicit 1% default`.
4. `research/claude-code-skill-budget-evolution.md` line 53 (open-questions bullet): reframed to align with the corrected timeline 28 lines above it.

## Fifth-critic pass (this verification round)

The fifth-critic pass caught a wrong version reference in the user-facing `context-management.md` plus three MEDIUM wording residuals:

### HIGH-1 — Fixed

`skills/crafting-skills/references/context-management.md` line 79 originally said *"Truncation is no longer silent as of v2.1.159+"*. This was wrong — bug #64606 was **filed against v2.1.159** documenting that the truncation was **silent at v2.1.159** (no warning, no log, no status indicator). The change happened in **post-v2.1.159 releases** with Anthropic's subsequent warning improvements. Rewritten to: "Truncation was silent at v2.1.159 per `anthropics/claude-code#64606`; post-v2.1.159 releases added three user-visible signals (startup warning, `/doctor`, `/context`)."

### MEDIUM-1 — Fixed (this report)

This verification report itself was stale after the fourth-critic pass. Updated to document all five critic passes and the fixes applied in each.

### MEDIUM-2 — Fixed

`AGENTS.md` line 87 attribution parenthetical cited two sources without distinguishing which says what. Updated to clarify that `code.claude.com/docs/en/settings` is the Anthropic docs source (default `0.01` introduced at v2.1.105 min-version), and claudefa.st's v2.1.129 binary extraction first publicly documented the knob.

### MEDIUM-3 — Acknowledged in research note

`research/marketplace-routing-scaling/document.md:53` still uses the v2.1.129 behavior-split framing (per claudefa.st's binary analysis). Anthropic docs and a third-party reference (shanraisshan) say v2.1.105; claudefa.st and danielmiessler (Personal_AI_Infrastructure#1307) say v2.1.129. The marketplace chose v2.1.105 as authoritative because Anthropic docs are more authoritative for runtime min-version annotations. This tension is now acknowledged in the research note's open-questions section rather than silently resolved.

### MEDIUM-4 — Fixed

`research/cross-platform-skill-budget-comparison.md` line 29 summary table cell had the same attribution issue as AGENTS.md line 87. Same fix pattern applied.

### LOW-1 — Fixed

`research/claude-code-skill-budget-evolution.md` line 53 had a duplicate trailing sentence "Not yet documented in Anthropic's published changelog." (introduced accidentally in the fourth-critic pass edit). Removed.

## Verified-true claims (cumulative across all 5 rounds)

| Claim | Source |
|---|---|
| `skillListingBudgetFraction` default = 0.01 (1%) | `code.claude.com/docs/en/settings`; claudefa.st; anthropics/claude-code#64606 |
| Min-version v2.1.105 | `code.claude.com/docs/en/settings` (live, verified) |
| 200K: ~2,000 tokens / ~8,000 chars | Math: 0.01 × 200K |
| 200K: ~15-25 skills | claudefa.st: "Around 15-25 skills before truncation" |
| 1M: ~75-125 skills | claudefa.st: "Around 75-125 skills before truncation" |
| 75-150 tokens per skill listing | claudefa.st |
| Recency + frequency selection | claudefa.st |
| `/doctor` shows truncation breakdown | Anthropic docs (live) |
| Hub count: ~40 at 200K, ~200 at 1M | Math: 2,000 / 50 tokens per hub |
| Silent truncation at v2.1.159 (bug #64606) | anthropics/claude-code#64606 (filed 2026-06-02 against v2.1.159) |
| Post-v2.1.159 user-visible signals | Anthropic docs + claudefa.st |

## Source-tension note (unresolved)

Two primary sources disagree on when `skillListingBudgetFraction` was introduced:

- **Anthropic docs** (`code.claude.com/docs/en/settings`): setting min-version `2.1.105`. A third-party settings-reference (`shanraisshan/claude-code-best-practice`) agrees.
- **claudefa.st blog post** (May 2026) + **danielmiessler/Personal_AI_Infrastructure#1307** (27 May 2026): both binary analyses say the setting was introduced at v2.1.129.

The marketplace chose v2.1.105 (Anthropic docs authoritative for runtime min-version). This is defensible but not definitively resolved; the binary-analysis community may have observed v2.1.129 because that's when the setting became prominently configurable or when the docs lag caught up.

## Aggregate verdict

After five rounds of independent subagent self-critic, the Marketplace Scaling section + 2 research notes + cross-platform comparison + user-facing reference doc + verification report + CHANGELOG are internally consistent on:

- The 1% default for Claude Code (v2.1.105+)
- The 8,000-char budget at 200K context
- The ~15-25 skill practical ceiling at 200K
- The ~40-hub Pattern 2 ceiling (Codex and Claude Code tied at 200K; Claude Code extends to ~200 at 1M)
- The non-silent truncation behavior in post-v2.1.159 releases
- The recency + frequency selection logic

**The recursion has not fully converged at depth 5** — the fifth critic found a HIGH version-reference error (silent AT v2.1.159 vs silent pre-v2.1.159, opposite of what the user-facing doc claimed) and three MEDIUM attribution residuals. Each was one-line to fix, and all are now fixed.

**Recommendation:** A sixth critic pass with a narrower scope (just the line-79 fix and the verification-report updates) is warranted before declaring convergence. Cost-vs-confidence suggests a 6th round is worthwhile given the same-class-of-error pattern.

`HEALTH: pass (validator=0/0)` — the marketplace remains in a clean release state.