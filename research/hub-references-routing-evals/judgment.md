# Direction judgment

## Chosen angle

**Empirical convention survey** — examine the actual SKILL.md files in the highest-traffic agent-skill marketplaces (Anthropic's `anthropics/skills` repository, `obra/superpowers`, and the HeyGen multi-skill marketplace) to determine: (a) the dominant split pattern between body-inlined and references-split, (b) the dominant router language (imperative vs descriptive), (c) the body-length and description-word-count distributions, and (d) the practical response to the 50-word description target when the skill is genuinely complex. Then, in a smaller second pass, assess whether token-overlap routing benchmarks have any published correlation with LLM-judge evals, or whether the field treats them as complementary rather than substitutable.

## Why this angle over alternatives

- The user has just executed the hub + references split (claude-cli: 637 → 128 lines) and the immediate question is "is this the right way to do it?" — i.e., a survey of what the dominant marketplaces do, not a deep dive into one theory.
- The user's marketplace is a multi-skill, cross-platform distribution (4 plugin manifests, 35+ skills). Their routing problem is closer to HeyGen's "many skills, same distribution channel" than to a single-skill author's question. So the empirical reference set should match.
- The token-overlap benchmark is local, recent, and the user is the maintainer. They want to know whether to invest further in it (LLM-judge evals) or leave it as-is. A short verdict on that is more useful than a 3,000-word survey of LLM-judge methodology.
- The SkillsBench paper is the obvious source of evidence for the "Skills are net-positive" claim but it is one paper, with a specific scope (86 tasks, deterministic verifiers). A more grounded answer notes the paper, anchors on the body-length findings, and moves on.

## Hypothesis to validate or refute

- **H1 (likely true):** The dominant convention in multi-skill marketplaces is "SKILL.md body inline, references/ only when body would exceed ~500 lines." This is exactly what the HeyGen CLAUDE.md says. We expect the empirical survey of superpowers + Anthropic-bundled skills to confirm a body median in the 200–400 line range with a long tail up to ~1,000 lines for the most complex.
- **H2 (likely true):** Router language, when present, is descriptive ("X is for Y") far more often than imperative ("You MUST read X BEFORE Y"). The imperative convention in this marketplace's `crafting-skills` is principled but rare in the wild.
- **H3 (likely true):** Description word count is empirically bimodal: 30–50 words for "do one thing" skills, 150–250 words for "do many things" skills, with the >300-word tail punished by the listing budget. The 50-word target is achievable for narrow skills; complex multi-operation skills either pay the cost or split.
- **H4 (untested, weaker):** Token-overlap benchmarks are a useful first-pass filter but cannot substitute for LLM-judge evals in production routing. The two are complementary, not substitutable. Published correlation data is scarce.

## Out of scope

- A full tutorial on how to write a skill (covered by `crafting-skills` in this marketplace).
- Deep-dive on the Agent Skills open standard at https://agentskills.io — only the parts relevant to body length and routing.
- Tool-spec portability across harnesses (Bustamante's "model-harness fit" topic) — relevant to cross-platform marketplaces but a separate research question.
- Quantitative cost analysis of large skill bodies (claudefa.st's token-cost table) beyond the qualitative finding that description length is a recurring per-session cost.
- The LLM-judge eval methodology itself (SkillsBench, Eugene Yan's evaluator library) — only the question of whether token-overlap can replace it.
- Routing for non-Claude harnesses (Codex, Gemini, Kimi) — we sample them for cross-platform sanity but the primary evidence is from Claude-side sources.
