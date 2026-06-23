# Iter-3.1 RESULTS — Final

The per-skill `--add-dir` experiment ran from 2026-06-23 12:58 to ~14:00
(60+ min, pid 43924 terminated). **9 of 15 runs completed; 6 timed out
at 180s/run and produced no `run.jsonl`.** This document captures the
9 completed runs and the partial verdict.

**Headline finding:** the original H1/H2/H3 framing was wrong. The
eval-harness baseline (`without_skill`) is **contaminated** because all
installed plugins load their skills into the `slash_commands` listing
globally, regardless of cwd. The discovery failure is not a marketplace
problem — it's an upstream agent-routing-heuristic problem.

**Bonus finding:** the iter-3 plugin cache is **stale (v2.0.0 from
2026-06-21)**, with 22 skill names that don't match the v0.0.3 working
marketplace. iter-3 and iter-3.1 results reflect v2.0.0 marketplace
behavior, not v0.0.3.

See [`../SKILL-DISCOVERY-ARCHITECTURE.md`](../SKILL-DISCOVERY-ARCHITECTURE.md)
v1.2 for the full architectural analysis.

## Final results table (9 of 15 runs)

| eval_id | config | tool_uses | skill invoked | expected skill | shadowed? |
|---------|--------|-----------|---------------|----------------|-----------|
| ingest-1 | without_skill | 0 | — | ingesting-skills | no skill picked |
| ingest-1 | with_full_marketplace | 0 | — | ingesting-skills | no skill picked |
| ingest-1 | with_skill_only | 0 | — | ingesting-skills | no skill picked |
| ingest-2 | without_skill | 0 | — | ingesting-skills | no skill picked |
| ingest-2 | with_full_marketplace | (timeout) | — | — | — |
| ingest-2 | with_skill_only | (timeout) | — | — | — |
| lint-2 | without_skill | 1 | `Glob **/*.md` (no skill) | marketplace-validator | partial; Glob instead of skill |
| lint-2 | with_full_marketplace | 0 | — | marketplace-validator | no skill picked |
| lint-2 | with_skill_only | (timeout) | — | — | — |
| craft-create | without_skill | 1 | `superpowers:writing-skills` | crafting-skills | **H1 confirmed** |
| craft-create | with_full_marketplace | (timeout) | — | — | — |
| craft-create | with_skill_only | (timeout) | — | — | — |
| craft-review | without_skill | 1 | `taches-principled-light:skill-authoring` | crafting-skills | wrong marketplace skill |
| craft-review | with_full_marketplace | (timeout) | — | — | — |
| craft-review | with_skill_only | 0 | — | crafting-skills | no skill picked |

## Hypothesis verdict (final)

| Hypothesis | Verdict | Evidence |
|------------|---------|----------|
| H1: Plugin shadowing | **CONFIRMED** | craft-create without_skill picked `superpowers:writing-skills` over `crafting-skills`/v2.0.0-cache `skill-authoring`. The v2.0.0 cache's `skill-authoring` description explicitly redirects creation tasks to superpowers, which is why. |
| H2: Descriptions don't differentiate | **CONFIRMED** | craft-review without_skill picked `taches-principled-light:skill-authoring` (the v2.0.0-cache alias for `crafting-skills`) because its description ("optimize, audit, benchmark") was more specific than the expected skill name. The expected skill's description was not visible. |
| H3: Choice paralysis | **NOT DOMINANT** | Agent picks the first matching skill and stops; choice paralysis doesn't matter when only one decision is made. |

**Bonus finding (H4 — upstream heuristic failure):** in 6 of 9 completed runs, the agent invoked ZERO skills. It just responded with text asking for more context. This is a routing-heuristic failure upstream of any marketplace configuration.

## Stale plugin cache invalidates iter-3 results

The plugin cache at `~/.claude/plugins/cache/taches-principled-light/taches-principled-light/2.0.0/` (installed 2026-06-21) has:

- 22 SKILL.md directories with **different names** than v0.0.3 working directory
- v2.0.0 cache: `ddd`, `fpf`, `ideation`, `kaizen`, `mcp-expertise`, `refine`, `rules-orchestration`, `sadd`, `session-analytics`, `skill-authoring`, `subagent-orchestration`, `wiki`
- v0.0.3 work: `crafting-skills`, `engineering-mcp`, `generating-ideas`, `managing-rules`, `managing-wiki`, `orchestrating-subagents`, `evaluating-skills`, etc.
- The agent's `slash_commands` listing reflects the v2.0.0 cache, not the working directory.

This means iter-3 and iter-3.1 results were evaluated against a marketplace state that has not existed since 2026-06-21 (the cache install date). The v0.0.3 release's skill changes (724f7b5 trigger phrase density, 861df65 scope router rewrites) were never actually visible to the eval agent.

**Action item for iter-4:** refresh the plugin cache before each eval run. Either `claude plugin update taches-principled-light` or remove and reinstall.

## What would actually fix the Bucket A3 evals

Given the discovery architecture and the cache issue:

1. **Refresh plugin cache** so iter-4 sees the v0.0.3 skill names. Without this, no marketplace description changes will have any effect on the eval.
2. **Update skill names** to match the working directory's SKILL.md directory names. The v2.0.0 cache aliases (`skill-authoring`, `subagent-orchestration`, etc.) confuse the agent because the descriptions don't match the directory names.
3. **Add anti-shadowing markers** in marketplace skill descriptions: "Use this instead of superpowers:writing-skills for [X]" patterns. Tests whether negative framing helps.
4. **Re-run iter-3** with the cache refresh + name sync + anti-shadowing markers. Measure lift.

## Methodology limitations of iter-3.1

- 6 of 15 runs timed out at 180s/run. The script doesn't gracefully handle timeouts; subsequent runs continue but the failed runs are lost.
- The cwd in `with_skill_only` was the specific skill directory (e.g., `skills/crafting-skills`), but the agent's slash_commands listing still showed all 22 v2.0.0-cache skills.
- The agent didn't Read any SKILL.md files in any completed run, even when cwd was the skill directory itself. This is a strong signal that the routing-heuristic is upstream of file-system proximity.

## Doc version

v1.0 (final) — 2026-06-23. 9 of 15 runs captured. The 6 timed-out runs are not recoverable from the partial data.

## Suggested follow-up

1. **iter-3.2 design:** refresh cache, rename skills to match directory names, add anti-shadowing markers, re-run iter-3 with the same 17 evals. Compare lift to iter-3's +8.69pp baseline.
2. **Multi-trial N=3 reliability:** re-run the 6 iter-3 lifts 3 times each, measure confidence interval. Currently single-sample.
3. **Same-family bias mitigation:** re-run the 6 lifts with `--judge-model sonnet` instead of heterogeneous judges. Currently heterogeneous.
4. **A1 evals re-run:** plan-multi and task-small hit proxy 503 in iter-3. Re-run on a clean proxy to confirm they are true discovery failures, not proxy errors.
5. **Plugin cache automation:** add a cache-refresh step to `iteration-3/scripts/run_iteration_3.py` so the cache is always fresh.