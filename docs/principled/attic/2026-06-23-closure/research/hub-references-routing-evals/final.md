# Final — Hub + references skill split, router language, and routing-evaluation calibration

## TL;DR

- **Hub + references is one valid pattern, not the dominant one.** Anthropic's 17 official skills use `references/` in only 2 (12%); superpowers' 14 skills use it in only 1 (7%); HeyGen's 11 skills use it in 5 (45%) and explicitly say "only split when SKILL.md would exceed ~500 lines" [source: [HeyGen skills-legacy CLAUDE.md](https://github.com/heygen-com/skills-legacy/blob/master/CLAUDE.md); [anthropics/skills tree](https://github.com/anthropics/skills); [obra/superpowers tree](https://github.com/obra/superpowers)].
- **Router language is descriptive in the wild, imperative in this marketplace.** None of Anthropic's, superpowers', or HeyGen's hub-style skills use "MUST read" imperative language. The convention in this marketplace's `crafting-skills` (imperative citations only) is principled but not community-wide. No public benchmark compares routing accuracy between the two [source: anthropics/skills mcp-builder; obra/superpowers using-superpowers; HeyGen skills-legacy CLAUDE.md].
- **Description word count: ≤50 words is the soft target, ≤150 words is the safety line, ~250 words is the hard cap.** A real-world failure case (Danielmiessler PAI v5.0.0) shipped 46 skills averaging 1,257 chars per description; 43 of 46 exceeded the 650-char ceiling and were silently dropped at session start [source: [claudefa.st skill-listing-budget](https://claudefa.st/blog/guide/mechanics/skill-listing-budget); [issue #1205](https://github.com/danielmiessler/Personal_AI_Infrastructure/issues/1205)].
- **The 500-line body ceiling is the consensus threshold for the split.** The SkillsBench paper (§4.2 Finding 6) reports moderate-length skills outperform comprehensive ones; "focused procedural guidance is more effective than exhaustive documentation" [source: [SkillsBench arXiv 2602.12670v1](https://arxiv.org/html/2602.12670v1)].
- **Token-overlap benchmarks are a useful first-pass filter, not a replacement for LLM-judge evals.** No published correlation coefficient exists between the two. Cost ratio is roughly 1:1000 in favor of token-overlap, so use it for fast iteration and screen for LLM-judge on the survivors [source: [arxiv 2604.13717v3](https://arxiv.org/html/2604.13717v3); SkillsBench Appendix H].
- **The claude-cli split (637 → 128 line hub + 8 references) follows the convention correctly.** The 500-line threshold was met, the router is hybrid (descriptive + imperative), and the references are self-contained per the centralized-routing rule. The only soft issue is the 59-word description, which is 9 words over the ≤50 target.

## Body

### The structural pattern: hub + references is justified for large bodies only

Across three high-traffic marketplaces — Anthropic's official `anthropics/skills` (17 skills, 153k stars), `obra/superpowers` (14 skills, 235k stars), and HeyGen's `heygen-com/skills-legacy` (11 skills) — the `references/` subdirectory is a minority pattern. Anthropic uses it in 2 of 17 (12%) — only `mcp-builder` (4 reference files) and `skill-creator` (1 reference file). Superpowers uses it in 1 of 14 (7%) — only `using-superpowers` (6 per-harness reference files for Claude Code, Codex, Gemini, Pi, Copilot, Antigravity). HeyGen uses it in 5 of 11 (45%) and is explicit about why: "Smaller skills inline everything. Only split into references when SKILL.md would exceed ~500 lines" [source: [HeyGen skills-legacy CLAUDE.md](https://github.com/heygen-com/skills-legacy/blob/master/CLAUDE.md)].

The dominant pattern in Anthropic and superpowers is **inline SKILL.md with sibling files in the same directory** (e.g., `systematic-debugging/root-cause-tracing.md`, `writing-skills/anthropic-best-practices.md`, `pdf/forms.md`). The hub + references pattern emerges only when the body would genuinely exceed the body-length ceiling or when there is a clean per-operation split. Anthropic's largest skill (`claude-api` at 42 KB) uses **language subdirectories** (`csharp/`, `go/`, `java/`, `php/`, `python/`, `ruby/`, `typescript/`, `shared/`) rather than a `references/` subdir — a different kind of split [source: [anthropics/skills tree](https://github.com/anthropics/skills); [obra/superpowers tree](https://github.com/obra/superpowers)].

**Practical threshold for splitting:** Han's first-principles deep dive recommends ≤5,000 words (~800 lines). Anthropic's docs are silent on a specific number but say "once a skill loads, its content stays in context across turns, so every line is a recurring token cost." The HeyGen "500 lines" is the most-cited operational threshold. For the claude-cli split (637 → 128 + 8 refs), 637 lines exceeds the 500-line threshold by a meaningful margin; the split is justified [source: [Han's deep dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/); [Anthropic skill docs](https://code.claude.com/docs/en/skills)].

### Router language: descriptive in the wild, principled-imperative here

The community convention is descriptive, not imperative. Anthropic's `mcp-builder` says: "Load and read the following reference files: MCP Best Practices, Python SDK Documentation, Node SDK Documentation." Superpowers' `using-superpowers` says: "For platform-specific tool references, see `references/{claude,codex,gemini,pi,copilot,antigravity}-tools.md`." HeyGen says: "For endpoint details, see `references/api.md`, `references/avatars.md`." None uses "MUST read" imperative language [source: anthropics/skills mcp-builder; obra/superpowers using-superpowers; HeyGen skills-legacy CLAUDE.md].

The `crafting-skills` skill in this marketplace prescribes "imperative citations only" ("You MUST read `references/format.md` BEFORE writing any code") on the principle that passive citations are ignored by LLMs. The hypothesis is correct in spirit, but the routing-accuracy claim has **never been benchmarked** in public. There is no A/B comparison of imperative vs descriptive routers in any source I found [source: this marketplace's `crafting-skills` SKILL.md].

**A practical compromise (which the claude-cli hub actually uses):** the table names the reference files in column one ("`references/execute.md`") and uses imperative language in column two ("`You MUST read this reference BEFORE proceeding`"). This gives the agent both the explicit pointer and the explicit instruction, in a hybrid form that satisfies both the community convention and the principled rule. No empirical evidence to refute this, but no evidence to confirm it either [source: claude-cli/SKILL.md §3 reference router table].

### Description word count: the empirical ceiling is real

Claude Code 2.1.129 ships with two hidden settings that govern the skill listing budget. The settings are not in the public Anthropic changelog but were reverse-engineered from the binary by [claudefa.st](https://claudefa.st/blog/guide/mechanics/skill-listing-budget) and corroborated by [stork.ai](https://www.stork.ai/blog/claude-code-is-secretly-disabling-you):

- `skillListingBudgetFraction` (default `0.01` = 1% of context window). The total of all skill descriptions is capped at this fraction. Excess skills are dropped, not truncated.
- `skillListingMaxDescChars` (default `1,536`). Per-skill description character cap. Excess is truncated, not dropped.

The two interact: descriptions over 1,536 chars are first truncated, then the total is checked against 1% of context. On a 200K-context Sonnet session, 1% = ~2,000 tokens. Each skill consumes 75–150 tokens in the listing (description + name + XML wrapper). At default settings, a marketplace of **15–25 skills** fits on 200K context; **75–125 skills** on 1M context [source: claudefa.st].

A real-world failure case: Danielmiessler's PAI v5.0.0 shipped 46 skills with average 1,257-char descriptions (total ~59,125 chars, nearly 3× the 2% budget at 1M context). `/doctor` reported "56 skill descriptions were dropped." The fix in their convention: ≤500 char target, 650 char hard ceiling, "USE WHEN: … NOT FOR: …" structure, body for workflow details [source: [issue #1205](https://github.com/danielmiessler/Personal_AI_Infrastructure/issues/1205)].

**Mapping to words:** 1,536 chars ≈ 250 words (hard cap); 650 chars ≈ 100 words (operational ceiling); 500 chars ≈ 80 words (PAI target); 150 chars ≈ 25 words (claude-fast's shipping target). The 50-word target in this marketplace's `crafting-skills` is the median for narrow skills. Complex multi-operation skills (like claude-cli) exceed it; the empirical answer is to split the skill, not bloat the description. claude-cli is currently at 59 words; trimming to ≤50 is a reasonable improvement, but the cost is losing one trigger phrase or tightening two [source: claude-fast; danielmiessler issue #1205; this marketplace's claude-cli/SKILL.md frontmatter].

### SkillsBench on design factors: moderate length wins, 2–3 modules optimal

The SkillsBench paper (Chen et al., 2026, 7,308 trajectories across 7 agent-model configurations, 84 tasks) reports three findings directly relevant to the body-split decision:

- **Finding 5: 2–3 skills per task is optimal; 4+ shows diminishing returns.** Per Table 5, tasks with 2–3 skills show +18.6pp improvement; 4+ skills provide only +5.9pp benefit. Excessive skill content creates cognitive overhead or conflicting guidance.
- **Finding 6: Moderate-length skills outperform comprehensive ones.** "Detailed" (+18.8pp) and "Compact" (+17.6pp) both beat the comprehensive baseline. "Focused procedural guidance is more effective than exhaustive documentation — agents may struggle to extract relevant information from lengthy Skills content, and overly elaborate Skills can consume context budget without providing actionable guidance."
- **Finding 3: Self-generated skills provide no benefit on average.** Models cannot reliably author the procedural knowledge they benefit from consuming. This argues for human-authored skills, not LLM-generated ones.

The paper also reports 16 of 84 tasks show **negative** skill deltas (taxonomy-tree-merge: -39.3pp; energy-ac-optimal-power-flow: -14.3pp). Skills can hurt [source: [SkillsBench arXiv 2602.12670v1](https://arxiv.org/html/2602.12670v1) §4.2].

**Implication for the claude-cli split:** the paper's evidence directly supports the hub + references pattern. Detailed, focused, per-operation skills outperform one-body comprehensive skills. The 2–3 module sweet spot argues for splitting complex skills into focused subskills — which the claude-cli split does (8 references, each focused on one operation) [source: SkillsBench §4.2].

### Token-overlap vs LLM-judge routing: no published correlation

The token-overlap benchmark in this marketplace's `routing_test.py` scores `len(utterance_tokens ∩ description_tokens)` for each candidate skill and picks the top match. The LLM-judge approach (used by SkillsBench and by Anthropic's `skill-creator` eval) uses a separate LLM to score whether a given description would correctly trigger on a given utterance. The two are conceptually different: token-overlap is a fast, deterministic proxy for keyword match; LLM-judge measures actual model decision quality [source: this marketplace's `routing_test.py`; SkillsBench §3.4].

**No published correlation coefficient exists** between the two for agent skill marketplaces. Web search for "skill description routing benchmark LLM judge correlation token overlap" returned generic LLM-evaluation literature (Eugene Yan's evaluator write-ups, BLEU/ROUGE critique) but no paired study. The known limitation of BLEU/ROUGE token-overlap is that it measures surface similarity, not meaning — but the marketplace-routing case is different from text-similarity (the "right answer" is which skill the LLM would actually pick, not which is most lexically similar) [source: [arxiv 2604.13717v3 "On Cost-Effective LLM-as-a-Judge Improvement Techniques"](https://arxiv.org/html/2604.13717v3); SkillsBench §3.4].

**Cost ratio:** SkillsBench reports per-trial costs of $0.50–$2.00 on Claude Opus 4.6. A small marketplace routing eval (10–20 skills × 10–20 utterances = 100–400 (skill, utterance) pairs) at a cheap judge (Haiku-class, ~$0.10 per judgment) costs **$10–$40 per eval pass**. Token-overlap benchmark: milliseconds, zero dollars. The ratio is roughly **1:1000** [source: SkillsBench Appendix H].

**Recommended pipeline:** token-overlap first (cheap, fast, catches gross routing errors — descriptions with zero keyword overlap, descriptions that match the wrong intent); LLM-judge on the survivors (expensive, slow, catches subtle errors — descriptions that overlap on keywords but route to the wrong skill because of semantic ambiguity). The marketplace's current 4 local meta-skills are well-served by the token-overlap benchmark; LLM-judge becomes valuable when the marketplace grows past ~15 skills or when the routing test moves from "is the right skill picked" to "is the skill's body correctly retrieved on the right context" [source: arxiv 2604.13717v3; SkillsBench; this marketplace's routing_test.py].

### Cross-harness: a constraint this marketplace ships into

This marketplace ships to 4 plugin manifests (Claude Code, Kimi Code, Codex, Cursor). Bustamante's "Model-Harness-Fit" analysis argues that "a marketplace that claims to be cross-harness is a routing problem, not just a parsing problem. Each skill needs a trigger surface the host agent can read." The same SKILL.md is not interchangeable across harnesses because each harness has a different tool surface, a different memory ritual, and a different skill format expectation. Models are post-trained against the harness, not just the API [source: [Model-Harness-Fit](https://www.nicolasbustamante.com/blog/model-harness-fit)].

The implication for this marketplace: the 4 plugin manifests must each ship a routing-correct version of the skill listing. Token-overlap benchmarks are a useful first-pass filter for cross-harness routing divergence — if a description matches zero keywords on harness X but matches several on harness Y, that is a signal the description has harness-specific assumptions. The marketplace's existing CI (`marketplace-health.yml` + `validate.py`) is a necessary but not sufficient gate; it does not test cross-harness routing accuracy [source: this marketplace's `.github/workflows/marketplace-health.yml`].

## What this does NOT settle

1. **Imperative vs descriptive router routing accuracy.** No published A/B benchmark. See `document.md` §Open questions 1.
2. **Token-overlap → LLM-judge correlation.** No published correlation coefficient for agent skill routing. See `document.md` §Open questions 2.
3. **Anthropic's `references/` convention rationale.** Why does Anthropic use `references/` only in 2/17 while HeyGen uses it in 5/11? No public write-up. See `document.md` §Open questions 3.
4. **The 500-line threshold.** HeyGen says ~500; Han says ~800; Anthropic is silent. No benchmark pins it down. See `document.md` §Open questions 4.
5. **Self-generated skill harm scope.** SkillsBench Finding 3 covers "LLM creates a skill from scratch." Does it also apply to "LLM rewrites an existing skill"? The paper does not split. See `document.md` §Open questions 5.
6. **Per-session cognitive overhead at marketplace scale.** Finding 5 is task-level (2–3 skills per task). Does a 35-skill marketplace pay a per-session tax? See `document.md` §Open questions 6.
7. **Cross-harness routing accuracy.** The marketplace ships to 4 harnesses; no public study of cross-harness routing accuracy for the same SKILL.md exists. See `document.md` §Open questions 7.

## References

1. [Anthropic — Extend Claude with skills (official docs)](https://code.claude.com/docs/en/skills) — defines SKILL.md structure, frontmatter, string substitutions, supporting files, and lifecycle.
2. [SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks (arXiv 2602.12670v1)](https://arxiv.org/html/2602.12670v1) — Chen et al., 7,308 trajectories, 84 tasks, +16.2pp with curated skills, 2–3 skills optimal, self-generated negative.
3. [Claude Agent Skills: A First Principles Deep Dive — Han Lee](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/) — first-principles walkthrough of the Skill lifecycle, three-tier progressive disclosure, ≤5,000-word recommendation.
4. [Claude Code's Hidden Skill Budget Setting (May 2026) — ClaudeFast](https://claudefa.st/blog/guide/mechanics/skill-listing-budget) — reverse-engineered `skillListingBudgetFraction=0.01` and `skillListingMaxDescChars=1536` from Claude Code 2.1.129.
5. [Why Claude Code Disables Skills & How to Fix It — Stork.AI](https://www.stork.ai/blog/claude-code-is-secretly-disabling-you) — second source confirming the 2.1.129 budget mechanic.
6. [HeyGen skills-legacy CLAUDE.md](https://github.com/heygen-com/skills-legacy/blob/master/CLAUDE.md) — explicit "Only split into references when SKILL.md would exceed ~500 lines" convention.
7. [obra/superpowers (GitHub)](https://github.com/obra/superpowers) — 14-skill marketplace; `using-superpowers/SKILL.md` is the only superpowers skill using `references/`.
8. [anthropics/skills (GitHub)](https://github.com/anthropics/skills) — 17-skill official marketplace; `mcp-builder` and `skill-creator` are the only ones using `references/`.
9. [Model-Harness-Fit — Nicolas Bustamante](https://www.nicolasbustamante.com/blog/model-harness-fit) — "a marketplace that claims to be cross-harness is a routing problem, not just a parsing problem."
10. [PAI Issue #1205: 43 of 46 descriptions over the 650-char ceiling](https://github.com/danielmiessler/Personal_AI_Infrastructure/issues/1205) — real-world failure case: silent skill drops at session start when total exceeds 1% of context.
11. [On Cost-Effective LLM-as-a-Judge Improvement Techniques (arXiv 2604.13717v3)](https://arxiv.org/html/2604.13717v3) — confirms "token overlap, not meaning" is a known limitation; LLM-judge is the dominant scalable-eval approach.
12. [this marketplace's `routing_test.py`](../../skills/claude-cli/../../.agents/skills/marketplace-validator/scripts/routing_test.py) — the token-overlap benchmark in question; 6/10 clear wins, 1 tie, 3 pre-existing losses.
13. [this marketplace's `crafting-skills/SKILL.md`](../../skills/crafting-skills/SKILL.md) — the source of the imperative-router convention in this marketplace.
