# Analysis

## Sub-question table

| # | Sub-question | What we already know | What we still need | Best queries / sources | parallel |
|---|---|---|---|---|---|
| 1 | **Body length distribution** — what is the empirical median and p95 of SKILL.md line count in high-traffic marketplaces? | HeyGen: "Only split into references when SKILL.md would exceed ~500 lines." Anthropic docs: "Keep the body itself concise." Han: ≤ 5,000 words (~800 lines) recommended. | Actual measured numbers from superpowers (14+ skills) and Anthropic's `anthropics/skills` repo. | Inspect `obra/superpowers/skills/*/SKILL.md` line counts. Inspect `anthropics/skills/skills/*/SKILL.md` line counts. The HeyGen `video-understand` is a known complex skill (has references/) — measure it. | parallel: true |
| 2 | **Hub + references prevalence** — in popular marketplaces, what fraction of skills use references/ vs inline everything? | HeyGen: 5 of 11 skills use references/ (45%). The other 6 inline everything. Han's `skill-creator` does NOT use references/ (only scripts/). | Empirical ratio across superpowers, Anthropic, HeyGen. | Read each marketplace's skill directory listings; classify by presence of `references/` subdirectory. | parallel: true |
| 3 | **Router language convention** — when a skill has a body that points to references/, is the pointer imperative or descriptive? | This marketplace's `crafting-skills` prescribes "imperative citations only." Real-world convention is unknown. | Sample of 5–10 skills with hub + references — what does the router text actually say? | Inspect `references/`-using skills' SKILL.md body for the router table or section. | parallel: true |
| 4 | **Description word count vs 50-word target** — what's the empirical distribution of skill descriptions? | claude-fast: 200–400 char (30–60 words) is "typical." Danielmiessler PAI: 500 char target, 650 hard ceiling. PAI v5.0.0 averaged 1,257 chars (~200 words) and got 43/46 skills dropped. | Direct measurement: word counts of all skills in our marketplace vs superpowers vs Anthropic official. | `wc -w` on description fields. Visual inspection of extreme cases. | parallel: true |
| 5 | **Listing budget mechanics** — what are the actual hard numbers in Claude Code 2.1.129? How do they interact with marketplace size? | claude-fast reverse-engineered: `skillListingBudgetFraction` default 0.01, `skillListingMaxDescChars` default 1,536. 15–25 skills at 200K, 75–125 at 1M. Per-skill cost 75–150 tokens. | Confirm the cap values from a second source (Anthropic changelog, GitHub release notes, or another reverse-engineer). | `claude code changelog`, `anthropics/claude-code CHANGELOG.md`. | parallel: true |
| 6 | **Token-overlap benchmark calibration** — has anyone published correlation between token-overlap and LLM-judge routing scores? | None observed in our background search. | Look for benchmark papers, blog posts, or evaluation frameworks that ran both in parallel. | "skill description routing benchmark LLM judge", "routing evaluation correlation", "agent skill benchmark design". | parallel: true |
| 7 | **LLM-judge eval cost/benefit** — when is the extra fidelity worth it? | SkillsBench runs 7,308 trajectories. Eugene Yan's evaluator library provides templates. No published ROI analysis for small marketplaces. | A back-of-envelope cost comparison: token-overlap runs in milliseconds; LLM-judge requires API calls per (skill, utterance) pair. | Eugene Yan's evaluator write-ups, SkillsBench paper Appendix C for cost analysis. | parallel: true |
| 8 | **SkillsBench design-factor findings** — what does the empirical paper say about quantity, length, complexity? | SkillsBench abstract: "Focused Skills with 2–3 modules outperform comprehensive documentation, and smaller models with Skills can match larger models without them." Full Finding 5, 6, 7 are in §4.2. | The full quantitative table: how much do 1-skill, 2–3-skill, 10+-skill configurations differ? What is the optimal SKILL.md length? | Re-read SkillsBench §4.2 in detail. | parallel: true |

## Shared scaffolding

- All sub-questions feed into the final answer in step 5.
- Sub-questions 1–4 and 8 produce the structural half of `final.md`.
- Sub-questions 5–7 produce the routing-evaluation half.
- Sub-question 3 (router language) is the single most direct evidence for the user's `crafting-skills` "imperative citations only" rule.

## Synchronization points

- Sub-questions 1, 2, 4 all inspect the same corpus (popular marketplaces) — they should be done by a single subagent to avoid duplicate fetches.
- Sub-questions 6 and 7 are both routing-eval questions and share web-search budget — also one subagent.
- Sub-question 8 is a deep re-read of one paper, independent.
- Sub-question 5 is a single, targeted fetch.

## Open questions that may persist into the final answer

- Does the Anthropic `anthropics/skills` repo use a hub + references pattern at all, or is it a single bundle of self-contained skills?
- Do superpowers skills ever exceed 500 lines? Which ones? What do they do instead of splitting?
- Is the "imperative" router convention the marketplace-specific rule, or is it observable in any external marketplace?

These will be answered (or not) by the document.md research pass.
