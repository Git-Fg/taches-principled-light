# Judgment

## Chosen angle

**Build a quantitative, evidence-backed answer to part 1 (the degradation curve) using the empirical studies already in the literature, then anchor part 2 (production implementations) on the four platforms the user named — Claude Code, Cursor, Codex, kimi-code, Microsoft Agent Framework — plus the two leading scaling patterns (Skill Hub's on-demand tool-registration, SkillRouter's retrieve-and-rerank).**

## Why this angle over alternatives

- The two parts are not independent: the degradation curve *is* the pressure that forces the production implementations to evolve. Reading them in isolation misses the cause-and-effect chain (small marketplaces → description listing → large marketplaces → context-budget bugs → on-demand routing → trained rerankers).
- The user named five platforms. Skipping any of them leaves the answer incomplete for someone choosing where to ship a marketplace.
- Curve-shape questions need primary empirical data, not opinions. The cleanest studies (SkillRouter, SkillReducer, the Claude Code bug) are 2-3 months old as of 2026-06-23 and have not yet been aggregated into a single decision rule. There is room for synthesis here.

## Hypothesis to validate or refute

**H1 (curve shape = knee):** Per-skill trigger recall is roughly flat up to a marketplace size N*, then drops sharply. The drop is **not** linear (it would have to start degrading from skill #2), and not sigmoidal in the classical S-curve sense (no saturation plateau — once you cross the budget, the failure mode is binary truncation, not graceful degradation).

**H1a (knee location = 5-12 skills):** The empirical evidence (SkillReducer's 26.4% missing-description rate, the promptspace.in "around 7-8 skills" anecdote, the Claude Code bug's "20+ custom skills per project" finding, Microsoft Agent Framework's 2-level discovery depth) clusters the knee in the 5-12-skill range when using the standard ~200-char description budget and Claude Code's default `skillListingBudgetFraction=0.01`.

**H2 (production implementations converge on three strategies):** Every named platform (Claude Code, Cursor, Codex, kimi-code, MAF) implements some flavor of *progressive disclosure*. They differ on **how aggressively they prune the listing**:
- Conservative (load all descriptions): Claude Code by default, kimi-code by default.
- Aggressive (shard by directory, present only top-N per session): Microsoft Agent Framework's nested discovery, Cursor's agent-decides model.
- Externally mediated (skill-as-tool): Skill Hub's 14-tool pattern, SkillRouter's 1.2B reranker.

**H3 (scaling beyond 8 is rare in practice but well-served by tools):** Most production marketplaces stay below 20 skills per session. SkillReducer demonstrates that the *description quality* problem (26.4% missing descriptions) is the binding constraint, not the count itself. Scaling beyond 8 requires either (a) tighter descriptions, (b) external routing layer, or (c) on-demand loading — not "just add more skills."

## Out of scope (deliberately)

- **General-purpose agent routing (not skill-specific).** SkillOrchestra, Vex, civillizard/claude-lean-skill — model-selection routing, not skill-selection routing. Mention only where they help explain the curve or the platform implementations.
- **Skills marketplace economics / monetization.** Not what was asked.
- **Skills marketplace security.** The arXiv 2603.10092 paper (skills ecosystem as attack surface) is adjacent but not asked. Mention only briefly if it informs the scaling recommendation.
- **Tool routing (MCP servers, function calling).** Same shape problem, different scope.
- **Skills authoring tools.** `crafting-skills`, `evaluating-skills` are out of scope unless the user's own marketplace is the case study.

## Plan

Move to step 3 (analysis.md + research_plan.md), where I decompose this into 4-7 sub-questions, mark which can be researched in parallel, and prepare the deep-research execution.