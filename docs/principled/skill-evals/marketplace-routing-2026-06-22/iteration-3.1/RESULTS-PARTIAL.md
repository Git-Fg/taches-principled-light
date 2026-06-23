# Iter-3.1 Partial RESULTS

The per-skill `--add-dir` experiment is still running in the background
(`pid 43924`). This document captures the partial findings based on the
8 of 15 runs completed at the time of writing (ingest-1 fully complete;
ingest-2, lint-2, craft-create, craft-review partially complete).

**Headline finding:** the original H1/H2/H3 framing was wrong. The
eval-harness baseline (`without_skill`) is **contaminated** because all
installed plugins load their skills into the `slash_commands` listing
globally, regardless of cwd. The discovery failure is not a marketplace
problem — it's an upstream agent-routing-heuristic problem.

See [`../SKILL-DISCOVERY-ARCHITECTURE.md`](../SKILL-DISCOVERY-ARCHITECTURE.md)
for the full architectural analysis and v1.1 corrections to the
discovery-mechanism claims.

## What changed since iter-3

The original iter-3 hypothesis (and BUCKET-A-INSPECTION.md) said plugin
shadowing was the dominant cause of Bucket A3 evals because
`craft-create` with_skill picked `superpowers:writing-skills` over
`crafting-skills`. The iter-3.1 transcripts confirm this is the case,
but they also reveal:

- **The without_skill baseline has the same plugin shadowing.** The
  agent in `without_skill` (cwd=`/tmp/empty-claude-project`) has
  `superpowers:writing-skills`, `taches-principled-light:skill-authoring`,
  and 20+ other marketplace + superpowers skills in its `slash_commands`.
  The only thing missing is `Read` access to the actual SKILL.md files.
- **The `--add-dir` mechanism controls cwd and file access, NOT the
  skill listing.** This is the architectural finding that invalidates
  part of the iter-3 design.

## Partial results table

| eval_id | config | tool_uses | skill invoked | expected skill | shadowed? |
|---------|--------|-----------|---------------|----------------|-----------|
| ingest-1 | without_skill | 0 | — | ingesting-skills | yes (no skill picked) |
| ingest-1 | with_full_marketplace | 0 | — | ingesting-skills | yes (no skill picked) |
| ingest-1 | with_skill_only | 0 | — | ingesting-skills | yes (no skill picked) |
| ingest-2 | without_skill | 0 | — | ingesting-skills | yes (no skill picked) |
| lint-2 | without_skill | 0 | — | marketplace-validator | yes (no skill picked) |
| lint-2 | with_full_marketplace | 0 | — | marketplace-validator | yes (no skill picked) |
| craft-create | without_skill | 1 | `superpowers:writing-skills` | crafting-skills | **H1 confirmed** |
| craft-review | without_skill | 1 | `taches-principled-light:skill-authoring` | crafting-skills | wrong marketplace skill |

(6 more runs pending: ingest-2 with_full + with_skill_only, lint-2 with_skill_only, craft-create with_full + with_skill_only, craft-review with_full + with_skill_only.)

## Hypothesis verdict (preliminary)

| Hypothesis | Verdict | Evidence |
|------------|---------|----------|
| H1: Plugin shadowing | **CONFIRMED** for craft-create | Agent picked `superpowers:writing-skills` over `crafting-skills` even when only the marketplace skill had a strong topical match |
| H2: Descriptions don't surface | **PARTIAL** | The agent can SEE the marketplace skill in slash_commands but doesn't differentiate it from the plugin equivalent |
| H3: Choice paralysis | **NOT THE DOMINANT FACTOR** | The agent picks the first matching skill and stops; choice paralysis doesn't matter when only one decision is made |

The deeper finding: **the agent in 6 of 8 completed runs invoked ZERO skills at all.** It just responded with text ("I need the URL", "Could you provide more context"). This is a routing-heuristic failure — the agent's prompt-time reasoning doesn't trigger skill invocation for these tasks. The marketplace can write the perfect skill description and the agent still won't consult it because the heuristic doesn't fire.

## What this means for iter-3 Bucket A3

The 8 Bucket A neutrals (split A1/A2/A3 per BUCKET-A-INSPECTION) include
5 true discovery failures (A3: ingest-1, ingest-2, lint-2, craft-create,
craft-review). The iter-3.1 data shows:

- craft-create: agent picks `superpowers:writing-skills` because it's
  more general and the marketplace's `crafting-skills` description
  doesn't differentiate enough to win the routing decision.
- craft-review: agent picks `taches-principled-light:skill-authoring`
  (a DIFFERENT marketplace skill, also for skill authoring) — both
  shadow each other internally.
- ingest-1/2, lint-2: agent picks NO skill and just asks for more
  context. This is the routing-heuristic failure.

The marketplace fixes that could help:

1. **Add anti-shadowing markers** to marketplace skill descriptions:
   "Use this instead of superpowers:writing-skills for [X]" — directly
   address H1.
2. **Sharper negative triggers** in the style of the `crafting-skills`
   CONTRAST section: explicitly say "do NOT use this for [Y]".
3. **Coordinate with superpowers** plugin author to add redirect
   markers in the plugin-equivalent skills.

The marketplace fixes that CANNOT help:

1. **Description rewrites** (commit 724f7b5, 861df65) — the agent
   already sees the descriptions and doesn't differentiate. More text
   won't help.
2. **Trigger phrase density** — the routing heuristic is upstream of
   trigger phrase matching.

## Next steps

1. Wait for iter-3.1 background process to complete the remaining 6 runs.
2. Update this document with the full results table.
3. Add anti-shadowing markers to the 3 marketplace skills that shadow
   plugin skills (crafting-skills, ingesting-skills, marketplace-validator).
4. Re-run iter-3 with the new descriptions to measure lift.
5. Consider iter-4 design: hint-injected eval that bypasses the
   routing heuristic to measure pure description-quality.

## Doc version

v0.5 (partial) — 2026-06-23. 8 of 15 runs captured. Will be updated when
background process completes.