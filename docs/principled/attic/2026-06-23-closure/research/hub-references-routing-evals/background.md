# Background

## Question restatement

The user is asking for an evidence-based answer to two coupled questions about Claude Code / agent-skill design:

1. **Structural** — When a skill body grows past a comfortable size, how do popular ecosystems actually split it? Do their router sections (which point readers at per-operation references) use imperative language ("read X before Y") or descriptive summaries ("X is for Y")? What is the established ceiling for body length, and what trade-offs do they accept when a description exceeds the recommended 50-word target for a multi-operation skill?

2. **Routing evaluation** — Token-overlap benchmarks (like the one we wrote for the marketplace's 4 local meta-skills) are convenient and deterministic, but are they predictive of real agent loading behavior? Should production routing confidence require LLM-judge evals instead, and if so, in what proportion relative to the cheaper automated test?

## Key terms and disambiguation

- **SKILL.md** — the single-file `SKILL.md` entrypoint in a skill directory, with YAML frontmatter (name, description, optional metadata) and a markdown body. Required by the [Agent Skills](https://agentskills.io) open standard and used by Claude Code, Codex CLI, Gemini CLI, Kimi Code, Cursor, etc.
- **Progressive disclosure** — the three-tier loading model: (1) description only in the system prompt's skill listing, paid every session; (2) full SKILL.md body loaded on demand when the skill is selected; (3) `references/`, `scripts/`, `assets/` loaded only when explicitly cited. Anthropic's docs frame this as the "concision test": "Would the agent get this wrong without this instruction? If no, the sentence cannot afford to be there."
- **Routing** — at session start, the agent sees a formatted listing of every available skill's name + description (concatenated) and picks one. There is no algorithmic router; the LLM reads the listing and decides. The SkillsBench paper confirms this: "The decision-making happens entirely within Claude's reasoning process based on the skill descriptions provided."
- **Skill listing budget** — Claude Code 2.1.129 caps total skill metadata at `skillListingBudgetFraction` (default 0.01 = 1% of context window) and individual descriptions at `skillListingMaxDescChars` (default 1,536 chars). Excess skills lose their description entirely (drop), not truncate.
- **Hub + references pattern** — a skill whose body acts as a router pointing to per-operation `references/*.md` files, with the hub staying under the body-length ceiling and each reference self-contained for one operation.
- **Imperative vs descriptive router** — "You MUST read `references/execute.md` BEFORE writing any CLI invocation" (imperative) vs "execute.md covers CLI invocation" (descriptive). The former is the convention in `crafting-skills`; the latter is the convention in most "table of contents" style routing.
- **Token-overlap benchmark** — a deterministic, regex-based routing test that scores `len(utterance_tokens ∩ description_tokens)` for each candidate skill and picks the top match. Used in our `routing_test.py` for the marketplace's 4 local meta-skills.
- **LLM-judge eval** — an eval where a separate LLM scores whether a given skill description would correctly trigger on a given utterance. Used by the SkillsBench team and by Anthropic's own skill-creator.

## Top sources

| # | Title | URL | Author / Org | Date | 1-line takeaway |
|---|---|---|---|---|---|
| 1 | Extend Claude with skills | https://code.claude.com/docs/en/skills | Anthropic | 2026 (live) | Authoritative spec: frontmatter, string substitutions, supporting files, lifecycle. Body should be "concise — once loaded, content stays in context across turns, so every line is recurring token cost." |
| 2 | SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks | https://arxiv.org/html/2602.12670v1 | Chen et al. (Berkeley Sky + community) | 2026-02-16 | 7,308 trajectories on 84 tasks. Curated Skills +16.2pp avg, 2–3 skills optimal, self-generated skills negative, moderate-length beats comprehensive. |
| 3 | Claude Agent Skills: A First Principles Deep Dive | https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/ | Han Lee | 2025-10-26 | Walks the Skill lifecycle from frontmatter → file load → context injection. Proposes three-tier progressive disclosure and recommends SKILL.md ≤ 5,000 words. |
| 4 | Claude Code's Hidden Skill Budget Setting (May 2026) | https://claudefa.st/blog/guide/mechanics/skill-listing-budget | ClaudeFast | 2026-05 | Documents the v2.1.129 `skillListingBudgetFraction` (default 0.01) and per-skill cap (1,536 chars). Empirically: 15–25 skills at 200K, 75–125 skills at 1M. Each description is 75–150 tokens. |
| 5 | obra/superpowers (agentic skills framework) | https://github.com/obra/superpowers | Jesse Vincent / Prime Radiant | 2026-06-22 | 235k stars, 14+ skills shipped as a methodology. Each skill is self-contained; `brainstorming`, `test-driven-development`, `subagent-driven-development` etc. The marketplace's primary empirical reference for cross-harness skill design. |
| 6 | HeyGen skills-legacy CLAUDE.md | https://github.com/heygen-com/skills-legacy/blob/master/CLAUDE.md | HeyGen | 2026-04-14 | Multi-skill marketplace convention. Explicit: "Smaller skills inline everything. Only split into references when SKILL.md would exceed ~500 lines." Each skill self-contained — no cross-skill file refs. |
| 7 | Model-Harness-Fit | https://www.nicolasbustamante.com/blog/model-harness-fit | Nicolas Bustamante | 2026-04-30 | "A marketplace that claims to be cross-harness is a routing problem, not just a parsing problem. Each skill needs a trigger surface the host agent can read." Argues skills carry tool-spec assumptions — same SKILL.md is not interchangeable across harnesses. |
| 8 | Issue #1205: v5.0.0 — 43 of 46 descriptions over the 650-char ceiling | https://github.com/danielmiessler/Personal_AI_Infrastructure/issues/1205 | @michaelandersonLFO | 2026-05-20 | Real-world case study: 46 skills × 1,257 char avg = 59,125 chars total → 3× the budget → 43 dropped. Fix: "USE WHEN: … NOT FOR: …" structure, body for workflow details, ≤500 char target. |

## Open threads (what the searches did NOT answer yet)

- **Imperative vs descriptive router** — Anthropic's docs do not prescribe a router tone. The `crafting-skills` skill (in this marketplace) prescribes "imperative citations only" but the empirical evidence in popular marketplaces (superpowers, HeyGen) is ambiguous. Need to inspect a sample of real skills to see which convention wins.
- **Token-overlap vs LLM-judge correlation** — SkillsBench runs LLM-judge evals (skills must be discoverable by an autonomous agent), but does not run a token-overlap benchmark in parallel. No public study correlates the two. We have no published correlation coefficient.
- **Hub router surface** — does the hub use a table, a bullet list, or a flowchart? Need to inspect superpowers, HeyGen, and a few high-traffic Anthropic-bundled skills to see what dominates.
- **Description word count vs 50-word target** — Han recommends ≤ 5,000 words total body but says nothing about the description. ClaudeFast's empirical 200-char per-skill target (with a 1,536-char cap) maps to roughly 30–50 words. The 50-word recommendation in this marketplace's `crafting-skills` is closer to the practical observed median; Danielmiessler's PAI recommends ≤ 500 char (~75–100 words). Real-world distribution: superpowers skills tend to be terser (50–80 words); PAI v5.0.0 averaged 200+ words and got 43/46 dropped.
- **Self-hosted benchmark construction** — would our token-overlap benchmark predict the SkillsBench LLM-judge scores? Not testable without running the full LLM-judge harness, which is expensive.

## Notes on the source quality

- Anthropic docs (source 1) are the primary spec but omit hard limits ("once a skill loads, its content stays in context across turns" — a soft guidance, not a number).
- SkillsBench (source 2) is the only quantitative, peer-shaped benchmark; numbers (16.2pp, 2-3 skills optimal, self-gen negative) are the strongest evidence in the field.
- claudefa.st (source 4) reverse-engineered the budget setting from the Claude Code 2.1.129 binary, since Anthropic has not yet published the changelog entry. Their numbers are the best available.
- Danielmiessler's issue (source 8) is the cleanest real-world failure case — a v4.0.0 marketplace (11 skills, 6,070 chars, working) became v5.0.0 (46 skills, 59,125 chars, 43 dropped) by expanding description length not skill count.
- Bustamante (source 7) is opinionated and analytical, not a benchmark; the key insight is that "cross-harness" marketplaces cannot assume uniform routing semantics, which is a separate problem from the body-length question.
