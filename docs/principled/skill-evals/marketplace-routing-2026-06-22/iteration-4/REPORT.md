# Iteration 4 — Cache-Refreshed Re-Run (Phase A)

**Status:** _in progress_ (transcript generation + grading running in background)
**Started:** 2026-06-23
**Judge:** sonnet (heterogeneous over haiku solver)
**Cache state:** fresh (cleared 2026-06-23, smoke test confirmed `craft-create` picks `taches-principled-light:crafting-skills`)

## Motivation

iter-3 reported a mean +8.69pp overall lift across 18 evals. However, iter-3.1 discovered that the plugin cache at `~/.claude/plugins/cache/taches-principled-light/` was stale (v2.0.0 from 2026-06-21), containing 22 SKILL.md files with different names (`skill-authoring`, `mcp-expertise`, `ideation`, etc.) than the live v0.0.3 working tree (`crafting-skills`, `engineering-mcp`, `generating-ideas`, etc.).

This means iter-3 and iter-3.1 were measuring the **v2.0.0 cache's behavior**, not the v0.0.3 marketplace. iter-4 re-runs the experiment with a freshly-cleared cache to determine whether the +8.69pp lift holds.

## Configuration

- **N=18 evals** (same set as iter-2/3)
- **Transcripts:** regenerated against fresh cache
- **Grader:** iter-3 `grader.py` reused (consultation assertion fix from commit b45c40a)
- **Timeout handling:** `timeout.json` marker written on `subprocess.TimeoutExpired` (iter-3.1 fix from commit b63b918)
- **Lift threshold:** ±5pp for `skill_neutral` verdict

## Upstream context

Web research confirms the plugin cache invalidation bug remains unfixed in Claude Code 2.1.186 (2026-06-22):

- **[Issue #14061](https://github.com/anthropics/claude-code/issues/14061)** (open since 2025-12-15, 23 comments, last updated 2026-05-26): `/plugin update` does not invalidate `~/.claude/plugins/cache/`. Workaround: `rm -rf ~/.claude/plugins/cache/{plugin}/`.
- **Three duplicate issues**: #15621, #17361, #28492.
- **[DEV Community article](https://dev.to/wkusnierczyk/claude-code-plugin-cache-1dn)** (2026-02-25) documents the same workaround.
- **2.1.186** added `display-name`, `default-enabled`, `fallback`, `metadata.*` frontmatter keys — these are display aliases, NOT cache invalidation triggers.

## Prior art (skill routing research)

iter-4 is positioned within emerging research on the **retrieval stage** of the agent skill lifecycle:

- **SkillRouter (Zheng et al. 2026, [arxiv 2603.22455](https://arxiv.org/abs/2603.22455))**: at 80K-skill scale, hiding the skill body causes a **31-44pp drop in routing accuracy**. Validates iter-3.1 H4 finding that descriptions alone are insufficient for routing.
- **Agent Skills Survey (Du et al. 2026, [arxiv 2605.07358](https://arxiv.org/abs/2605.07358))**: 4-stage lifecycle (representation, acquisition, retrieval, evolution).
- **Skill Evaluation Survey (Ding et al. 2026, [arxiv 2606.11435](https://arxiv.org/abs/2606.11435))**: 6 benchmark categories for skill evaluation.

## Results

_(to be filled in when iter-4 completes — see `benchmark.json` and `benchmark.md`)_

### Aggregate deltas

| Metric | iter-3 (stale cache) | iter-4 (fresh cache) | Δ |
|--------|---------------------:|---------------------:|---:|
| Mean overall delta | +8.69pp | _TBD_ | _TBD_ |
| Mean IF delta | _TBD_ | _TBD_ | _TBD_ |
| Mean GC delta | _TBD_ | _TBD_ | _TBD_ |
| Lifts (skill_lifts_quality) | 6/18 | _TBD_ | _TBD_ |
| Neutrals (skill_neutral) | 11/18 | _TBD_ | _TBD_ |
| Hurts (skill_hurts) | 0/18 | _TBD_ | _TBD_ |

### Verdict

_TBD — to be written after iter-4 benchmark.json is available._

## Methodology notes

- The without_skill baseline is contaminated by global plugin loading (per SKILL-DISCOVERY-ARCHITECTURE.md v1.1): all installed plugins inject their skills into `slash_commands` regardless of cwd. Both with/without configs see the same marketplace skill listing.
- iter-4 measures the marginal lift of Read-driven skill consultation (with_skill: cwd=REPO, agent can `Read` SKILL.md files) over listing-driven discovery (without_skill: cwd=`/tmp/empty-claude-project`, agent has skill names in `slash_commands` but cannot `Read` the bodies).
- This matches the SkillRouter finding: descriptions alone (without bodies) lose 31-44pp routing accuracy at scale.
