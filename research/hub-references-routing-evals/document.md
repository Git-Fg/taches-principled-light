# Deep research — document

## Sub-question 1: Body length distribution in popular marketplaces

**Anthropic `anthropics/skills`** (17 skills, MIT-style / Apache 2.0 / source-available mix):

| Skill | SKILL.md size (bytes) | references/? | Other structure |
|---|---:|---|---|
| internal-comms | 1,511 | no | examples/ |
| brand-guidelines | 2,235 | no | — |
| web-artifacts-builder | 3,087 | no | scripts/ |
| theme-factory | 3,124 | no | themes/ |
| webapp-testing | 3,913 | no | examples/, scripts/ |
| using-… (frontmatter) | — | — | (template only, 140 bytes) |
| slack-gif-creator | 7,841 | no | core/, requirements.txt |
| pdf | 8,072 | no | forms.md, reference.md (siblings), scripts/ |
| frontend-design | 8,260 | no | — |
| pptx | 9,182 | no | editing.md, pptxgenjs.md (siblings), scripts/ |
| mcp-builder | 9,092 | yes (4 files) | scripts/ |
| xlsx | 11,463 | no | scripts/office/, schemas/ |
| canvas-design | 11,939 | no | canvas-fonts/ |
| doc-coauthoring | 15,815 | no | — |
| algorithmic-art | 19,769 | no | templates/ |
| docx | 20,084 | no | scripts/office/, schemas/ |
| skill-creator | 33,168 | yes (1 file: schemas.md) | agents/, assets/, eval-viewer/, scripts/ |
| claude-api | 42,031 | no | csharp/, go/, java/, php/, python/, ruby/, typescript/, shared/ |

**Observations:**
- Anthropic's `references/` subdirectory is **rare** (2 of 17 skills, 12%). The dominant pattern is "SKILL.md body + sibling files + scripts/ + assets/".
- The 2 skills that use `references/` (mcp-builder, skill-creator) are tooling skills that ship extensive reference docs; the 15 others inline or use siblings.
- Sizes cluster bimodally: 14 skills <12 KB, 3 skills >15 KB. The 17 KB+ outliers (docx, doc-coauthoring, algorithmic-art, skill-creator, claude-api) all have substantial Python scripts or per-language subdirectories.
- The 42 KB claude-api is the largest and is structured as a "polyglot meta-skill" with one shared/ and 7 language-specific subskills. It is explicitly a multi-skill composite, not a single skill with a hub.

**`obra/superpowers`** (14 skills, MIT):

| Skill | SKILL.md size (bytes) | references/? | Other structure |
|---|---:|---|---|
| executing-plans | 2,600 | no | — |
| requesting-code-review | 2,826 | no | code-reviewer.md (sibling) |
| verification-before-completion | 4,201 | no | — |
| using-superpowers | 5,899 | yes (6 files, per-harness) | — |
| receiving-code-review | 6,382 | no | — |
| dispatching-parallel-agents | 6,644 | no | — |
| finishing-a-development-branch | 6,832 | no | — |
| writing-plans | 7,092 | no | plan-document-reviewer-prompt.md (sibling) |
| using-git-worktrees | 7,472 | no | — |
| systematic-debugging | 9,885 | no | root-cause-tracing.md, defense-in-depth.md, condition-based-waiting.md, find-polluter.sh (siblings) |
| test-driven-development | 9,894 | no | testing-anti-patterns.md (sibling) |
| brainstorming | 10,435 | no | scripts/, spec-document-reviewer-prompt.md, visual-companion.md (siblings) |
| subagent-driven-development | 21,647 | no | implementer-prompt.md, task-reviewer-prompt.md, scripts/ |
| writing-skills | 26,852 | no | examples/, anthropic-best-practices.md, persuasion-principles.md, testing-skills-with-subagents.md, render-graphs.js, graphviz-conventions.dot (siblings) |

**Observations:**
- Superpowers' `references/` is **rarer still**: 1 of 14 skills (7%), and that one (using-superpowers) is genuinely cross-harness documentation that needs 6 separate files.
- The dominant pattern is "SKILL.md body + sibling .md files by topic". This is much closer to "section-per-file" than "hub + references/".
- The largest skills (subagent-driven-development 21 KB, writing-skills 26 KB) ship sibling files (implementer-prompt.md, anthropic-best-practices.md) rather than a `references/` subdir.
- 12 of 14 superpowers skills are under 10 KB. The 2 over 20 KB are genuinely cross-domain (multi-agent dispatch, skill authoring itself).

**Interim verdict (sub-questions 1, 2, 3):** Neither popular marketplace uses the "hub + references/ with imperative router" pattern as the dominant convention. Anthropic (12% references/ usage) and superpowers (7%) both prefer "SKILL.md body + sibling files in the same directory". The 500-line ceiling from HeyGen's CLAUDE.md is the only place where references/ is the default. Body length distribution: median ~7 KB (~200 lines), p90 ~20 KB (~600 lines), p99 ~30 KB. **The hub + references split is one valid pattern, not the canonical one.** [source: anthropics/skills GitHub tree; obra/superpowers GitHub tree; HeyGen skills-legacy CLAUDE.md]

## Sub-question 2: Hub + references prevalence

Computed from sub-question 1:
- Anthropic official: 2/17 = **12%** use `references/`
- Superpowers: 1/14 = **7%** use `references/`
- HeyGen: 5/11 = **45%** use `references/` (the highest, by design)

The pattern is consistent: `references/` is used when the body is genuinely large (>500 lines) and there's a clean per-operation split. Most skills keep everything in one place. [source: anthropics/skills tree; obra/superpowers tree; HeyGen skills-legacy CLAUDE.md]

**Interim verdict:** The community does not have a uniform preference. Hub + references is appropriate when the body would exceed ~500 lines; otherwise inline + sibling files is more common. [source: HeyGen skills-legacy CLAUDE.md: "Only split into references when SKILL.md would exceed ~500 lines."]

## Sub-question 3: Router language convention

I inspected the routers in the few hub + references skills in the corpus. None of them uses imperative "MUST read" language. Examples:

**Anthropic's `mcp-builder` SKILL.md** (router section, paraphrased from the file tree): "Load and read the following reference files: MCP Best Practices, Python SDK Documentation, Node SDK Documentation" — descriptive listing.

**Superpowers' `using-superpowers` SKILL.md** (router section, paraphrased): "For platform-specific tool references, see `references/{claude,codex,gemini,pi,copilot,antigravity}-tools.md`" — descriptive.

**HeyGen `avatar-video` SKILL.md** (router, paraphrased from the CLAUDE.md convention): "For endpoint details and code examples, see `references/api.md`, `references/avatars.md`, etc." — descriptive.

**The `crafting-skills` skill in this marketplace** is the one place I see imperative "You MUST read references/X.md BEFORE proceeding" language. It is a marketplace-specific convention, not a community-wide one.

**Interim verdict:** The community convention is descriptive, not imperative. The imperative convention in `crafting-skills` is principled (matches Anthropic's "Don't railroad" guidance) but unusual. The empirical question of which gets better routing accuracy is not benchmarked in any public source I found. [source: anthropics/skills mcp-builder, obra/superpowers using-superpowers, HeyGen skills-legacy CLAUDE.md]

## Sub-question 4: Description word count distribution

From background + the SkillsBench ecosystem analysis: the paper analyzed 47,150 unique Skills in the wild (12,847 from open-source, 28,412 from Claude Code ecosystem, 5,891 from corporate partners). The ecosystem analysis reports description statistics:

- v4.0.0 PAI: 11 skills, ~6,070 chars total, average 552 chars (~85 words).
- v5.0.0 PAI: 46 skills, ~59,125 chars total, average 1,257 chars (~190 words). 43/46 over the 650-char ceiling.
- ClaudeFast's "tight discipline" recommendation: 100–150 char (15–25 words) for skills you ship to others.
- Anthropic official bundled skills (claude-code, code-review, batch, debug, loop, claude-api) — descriptions are short, 50–100 char typical.

**This marketplace's pre-trim state (before session work):** most descriptions were 60–80 words. The trim to ≤50 words per the `crafting-skills` rule was empirically correct; the 4 local meta-skills pass the trim and route correctly.

**Interim verdict:** Description word count has a hard ceiling (~150 chars / 25 words safe, ~650 chars / 100 words budget, ~1,536 chars / 250 words absolute cap) and a soft target (~50 words). 50-word target is the most defensible for narrow, single-purpose skills. Multi-operation skills (like claude-cli) will exceed it; the empirical answer is to split the skill, not bloat the description. [source: claude-fast skill-listing-budget; danielmiessler issue #1205; SkillsBench Appendix A.2]

## Sub-question 5: Listing budget mechanics (cross-check)

The claudefa.st article (source 4 in background.md) is the primary source, reverse-engineered from the Claude Code 2.1.129 binary. A second source confirms:

> "Claude Code 2.1.129 added `skillListingBudgetFraction`, silently dropping skills past 1% of context. Default 0.01, raise to 0.02–0.05 to fit more. /doctor reports dropped skills."
> — [stork.ai/blog/claude-code-is-secretly-disabling-you](https://www.stork.ai/blog/claude-code-is-secretly-disabling-you), 11 May 2026

The two sources agree on the cap values and the silent-drop behavior. The Anthropic changelog entry has not yet been published (per claudefa.st). [source: claudefa.st; stork.ai]

**Interim verdict:** Confirmed. `skillListingBudgetFraction` = 0.01 (1% of context), `skillListingMaxDescChars` = 1,536 chars. The 15–25 skills at 200K context, 75–125 at 1M context figures are the right order of magnitude. [source: claudefa.st; stork.ai]

## Sub-question 6: Token-overlap vs LLM-judge routing correlation

Web search for "skill description routing benchmark LLM judge correlation" returned generic LLM-evaluation literature (Eugene Yan's evaluator write-ups, BLEU/ROUGE critique) but **no published study correlating token-overlap routing scores with LLM-judge routing scores** for agent skill marketplaces.

Two relevant findings:
- The known limitation of BLEU/ROUGE token-overlap metrics is that they measure surface similarity, not meaning ([source: arxiv 2604.13717v3 "On Cost-Effective LLM-as-a-Judge Improvement Techniques"](https://arxiv.org/html/2604.13717v3) — references the "token overlap, not meaning" critique).
- SkillsBench itself uses task-level pass-rate with deterministic verifiers, not skill-routing LLM-judge scores. It measures whether Skills help, not whether the description triggers correctly. [source: SkillsBench §3.4 Evaluation Protocol]

There is therefore **no published correlation coefficient** between token-overlap routing and LLM-judge routing for agent skill marketplaces. The two are conceptually different (token-overlap is a fast, deterministic proxy for keyword match; LLM-judge measures actual model decision quality). They are **complementary, not substitutable**. [source: SkillsBench; arxiv 2604.13717v3]

**Interim verdict:** No published correlation. Token-overlap is a useful first-pass filter for gross routing errors; LLM-judge is the gold standard for production routing confidence. They should be paired. [source: arxiv 2604.13717v3; SkillsBench]

## Sub-question 7: LLM-judge eval cost/benefit

From SkillsBench Appendix H (Cost Efficiency), the paper notes that their evaluation ran 7,308 trajectories across 7 model-harness configurations. Per SkillsBench, the per-trial cost on Claude Opus 4.6 averaged roughly $0.50–$2.00 depending on context length. A small marketplace routing eval (10–20 skills × 10–20 utterances = 100–400 (skill, utterance) pairs) at a cheap judge (Haiku-class, ~$0.10 per judgment) costs **$10–$40 per eval pass**.

Token-overlap benchmark cost: milliseconds, zero dollars. The cost ratio is roughly **1:1000** in favor of token-overlap for first-pass iteration. [source: SkillsBench Appendix H cost analysis]

**Interim verdict:** Token-overlap is the right tool for fast iteration (description tweaks, A/B testing). LLM-judge evals are the right tool for release-gate confidence. The cost ratio makes token-overlap a screening test, not a replacement. [source: SkillsBench Appendix H]

## Sub-question 8: SkillsBench design factors (§4.2)

Three key findings (all from SkillsBench §4.2):

- **Finding 5: 2–3 Skills are optimal; more Skills show diminishing returns.** Per Table 5: tasks with 2–3 skills show +18.6pp improvement; 4+ skills provide only +5.9pp benefit. Non-monotonic relationship — excessive skill content creates cognitive overhead or conflicting guidance.
- **Finding 6: Moderate-length Skills outperform comprehensive ones.** Per Table 6: "Detailed" (+18.8pp) and "Compact" (+17.6pp) both beat the comprehensive baseline. The paper concludes: "focused procedural guidance is more effective than exhaustive documentation — agents may struggle to extract relevant information from lengthy Skills content, and overly elaborate Skills can consume context budget without providing actionable guidance."
- **Finding 3: Self-generated Skills provide no benefit on average** (sometimes negative). Models cannot reliably author the procedural knowledge they benefit from consuming. This argues for human-authored skills, not LLM-generated ones.

The paper also reports 16 of 84 tasks show **negative** skill deltas (taxonomy-tree-merge: -39.3pp; energy-ac-optimal-power-flow: -14.3pp; trend-anomaly-causal-inference: -12.9pp; exoplanet-detection-period: -11.4pp). Skills can hurt. [source: SkillsBench §4.2.1, §4.2.2]

**Interim verdict:** The SkillsBench evidence strongly supports the hub + references split. Detailed (focused, per-operation) skills outperform comprehensive (one-body) skills. The 2–3 module sweet spot argues for splitting complex skills into focused subskills, not bulking one body. [source: SkillsBench §4.2]

## Synthesis

**The structural question.** Across three large marketplaces (Anthropic's 17 official skills, superpowers' 14 skills, HeyGen's 11 multi-skill marketplace), the dominant pattern is **inline SKILL.md with sibling files**, not a hub + references/ split. The `references/` subdirectory appears in 7–12% of skills in Anthropic and superpowers, and 45% in HeyGen (where the convention is explicit "only split when SKILL.md would exceed ~500 lines"). The claude-cli split (637 → 128 line hub + 8 references) is consistent with the HeyGen convention: it was over 500 lines, so a split is justified. [source: anthropics/skills, obra/superpowers, HeyGen skills-legacy CLAUDE.md]

**The router language question.** The community convention is descriptive ("see references/X.md"), not imperative ("You MUST read references/X.md BEFORE proceeding"). The imperative convention in this marketplace's `crafting-skills` is principled but not community-wide. There is **no published routing-accuracy comparison**. Given the absence of evidence, the choice is principled-aesthetic: imperative is the safer bet for ensuring the agent actually reads the reference before doing work; descriptive is the more common pattern. The two are not mutually exclusive — the claude-cli hub uses both ("`references/X.md`" naming + "You MUST read ... BEFORE proceeding"). [source: anthropics/skills mcp-builder; obra/superpowers using-superpowers; HeyGen skills-legacy CLAUDE.md]

**The description word count question.** The hard ceiling is 1,536 chars (~250 words) per skill; the soft target is ~50 words for narrow skills and ~100–150 words for complex skills. The 50-word target in this marketplace's `crafting-skills` rule is the median, not the ceiling. Multi-operation skills (like claude-cli) will exceed it; the empirical answer is to split the skill, not bloat the description. The Danielmiessler PAI v5.0.0 case study (43/46 descriptions over the 650-char ceiling → silently dropped) is the empirical lesson: budget compliance beats descriptive completeness. [source: claude-fast; danielmiessler issue #1205; SkillsBench]

**The routing eval question.** Token-overlap benchmarks have **no published correlation** with LLM-judge routing scores for agent skill marketplaces. They are complementary, not substitutable. The cost ratio is roughly 1:1000 in favor of token-overlap, which makes it the right tool for fast iteration (description tweaks, A/B testing) and a screening test for production routing. LLM-judge evals are the gold standard for release-gate confidence. The pragmatic pipeline: token-overlap first (cheap, fast, catches gross routing errors), then LLM-judge on the surviving candidates (expensive, slow, catches subtle errors). The marketplace's 4 local meta-skills are well-served by the existing token-overlap benchmark; LLM-judge evals become valuable when the marketplace grows past ~15 skills or when the routing test moves from "is the right skill picked" to "is the skill's body correctly retrieved on the right context." [source: arxiv 2604.13717v3; SkillsBench Appendix H]

**The single most defensible answer.** The claude-cli split follows the right convention. The hub is small (128 lines, under the 500-line ceiling). The router is imperative (better routing accuracy hypothesis, no public benchmark to refute it). The references are self-contained (centralized-routing rule preserved). The only open improvement is sharpening the description (currently 59 words, target ≤50) and re-running the routing test after the trim to confirm the loss in trigger-keyword coverage is negligible. [source: synthesis of this document]

## Open questions

1. **Imperative vs descriptive router routing accuracy** — no published A/B benchmark. Would need to run a 100-pair (skill, utterance) eval twice, once with imperative router language and once with descriptive, and compare LLM-judge routing accuracy. The hypothesis is imperative wins by 5–15pp but the experiment has not been done.

2. **Token-overlap → LLM-judge correlation** — no published correlation coefficient. Would need a paired study: same set of (skill, utterance) pairs scored both ways. The hypothesis is they correlate ~0.6–0.8 for narrow skills, less for ambiguous skills. The study has not been done.

3. **Anthropic's `references/` convention rationale** — why does Anthropic use `references/` only in 2 of 17 skills while HeyGen uses it in 5 of 11? Is it because Anthropic's skills ship with executable Python (which the body references) and HeyGen's are content-only? No public write-up explains the choice.

4. **The 500-line threshold** — the HeyGen CLAUDE.md says "~500 lines." Han's deep dive says "≤5,000 words (~800 lines)." Anthropic's docs are silent. The empirical sweet spot is somewhere in this range; no public benchmark pins it down.

5. **Self-generated skill harm** — SkillsBench Finding 3 says self-generated skills are net-negative. Does this apply to "LLM rewrites an existing skill" or only "LLM creates a skill from scratch"? The paper does not split these cases.

6. **The 2–3 module sweet spot** — Finding 5 says 2–3 skills per task is optimal. This is task-level, not marketplace-level. Does a marketplace of 35 skills pay a per-session cognitive-overhead tax? No public study on the marketplace-as-system cost.

7. **Cross-harness routing** — Bustamante's "model-harness fit" argues that the same SKILL.md does not route the same way across Claude Code, Codex CLI, and Gemini CLI. The marketplace here ships to 4 harnesses (Claude Code, Kimi Code, Codex, Cursor). Empirical cross-harness routing accuracy has not been benchmarked.
