# Archive: 2026-06-23-closure

**Archived:** 2026-06-23
**Milestone:** v0.0.7 release — iteration phase closure marker (repo finalization)
**Phase:** post-v0.0.6 cleanup + archival of superseded artifacts
**Status:** completed
**Closure marker:** v0.0.7 release tag (this commit)

## Why this archive exists

The v0.0.6 release consolidated the marketplace-routing eval cycle. With iter-7
as the canonical headline (+21.88pp, 4/4 lifts, 0 hurts) and the iter-8 design
locked in for the next cycle, the active working tree was carrying 13 MB of
historical artifacts (iter-1 through iter-4 transcripts, intermediate research
work products, executed plans without SUMMARY.md, design notes for already-shipped
features). This bundle preserves those artifacts as audit trail while the
active tree keeps only the canonical signal (iter-6, iter-7, iter-8-PLAN, plus
reusable baselines / evals / scripts / architecture docs).

## Files archived

### plans/ (2 files)
- `2026-06-22-router-language-audience.md` — Task 1 executed (commit 7911eed), rest abandoned
- `2026-06-22-skill-steering-point-to-sources.md` — partial execution; current `crafting-skills/SKILL.md` is 199 lines (not the 540-line full-merge design in the plan)

### specs/ (2 files)
- `2026-06-22-router-language-audience-design.md` — design spec for the above plan
- `2026-06-22-skill-steering-point-to-sources.md` — design spec for the above plan

### design/ (1 file)
- `hub-subskills-compatibility.md` — design analysis from 2026-06-23, not referenced from any active artifact (no grep hits in active tree)

### research/ (13 files across 2 bundles)
- `agent-skills-evaluation/` (6 files) — intermediate work products from the 2026-06-22 `evaluating-skills` methodology research. The `final.md` is the canonical artifact; the other 5 (analysis, background, document, judgment, research_plan) are superseded. Historical reference: cited in CHANGELOG `v0.0.1-alpha` entry.
- `hub-references-routing-evals/` (7 files) — intermediate research from 2026-06-22 that informed the claude-cli split + skill-steering plans. Only referenced from the archived specs above.

### skill-evals/ (5 historical iterations, ~12.5 MB)
- `iteration-1/` (296K) — pilot (single eval `craft-create`), superseded by iter-2
- `iteration-2/` (4.4M) — broken by API overload incident (5/18 partial runs, all-zero signal); see `API-OVERLOAD-INCIDENT.md` and `METRIC-BUG-NOTE.md`
- `iteration-3/` (396K) — +8.69pp headline (stale v2.0.0 plugin cache), corrected to +4.94pp by iter-4
- `iteration-3.1/` (336K) — per-skill `--add-dir` experiment (H1/H2/H3/H4 hypotheses)
- `iteration-4/` (7.2M) — cache-refreshed +4.94pp headline (filesystem_access_lift only; true total_lift measured at +21.88pp by iter-7)

## Active tree (kept in working tree)

The active `docs/principled/skill-evals/marketplace-routing-2026-06-22/` directory now contains only:

- `iteration-6/` — canonical proxy architecture finding (vendor-disjoint validation structurally blocked)
- `iteration-7/` — canonical headline (+21.88pp, 4/4 lifts, 0 hurts)
- `iteration-8-PLAN.md` — forward-looking (two-layer MCP test-runner stack, vendor-disjoint grader mock)
- `baselines/` — canonical iter-7 baselines, used by release-gate CI
- `evals/` — eval definitions
- `scripts/` — reusable evaluation scripts
- `capabilities.json` — eval capabilities manifest
- `SKILL-DISCOVERY-ARCHITECTURE.md` — foundational architecture reference (v1.4)
- `methodology-note-routing-vs-validator.md` — behavioral vs static eval distinction
- `.archive/` — already-archived `INTERIM-FINDINGS-iter3-SUPERSEDED.md` and `iter-2.5-failed-runs/`

Active tree size: **2.4 MB** (down from 15 MB).

## Cross-reference updates

The following cross-references were updated to point to the new attic paths:

- `docs/principled/skill-evals/INDEX.md` — simplified; iter-1/2/3/3.1/4 entries now point to closure archive
- `docs/principled/skill-evals/marketplace-routing-2026-06-22/iteration-7/REPORT.md` (line 151) — `iteration-4/REPORT.md` link updated to closure archive
- `docs/principled/skill-evals/marketplace-routing-2026-06-22/iteration-7/GRADER-NOISE-INVESTIGATION.md` (lines 19, 22, 68, 69) — `iteration-3/scripts/grader.py` and `iteration-4/eval-sec-audit/grading_without_skill.json` references updated to closure archive

## Closures

- 4 plugin manifests synchronized to 0.0.7
- CHANGELOG `[0.0.7]` section written (replaces stale `[Unreleased]` note)
- README closure note added
- CI release-gate CI release-gate: passes on iter-7 grading_summary.json (unaffected by archive)
- Local dev cruft (`.pytest_cache/`) removed via `trash`

## Next cycle (post-archive)

`iteration-8-PLAN.md` is the natural next step — execute the iter-8 design
when Docker + Claude Code CLI + multi-model proxy (LiteLLM replacement) become
available. The current structurally-single-model proxy at
`100.80.231.128:3456` blocks iter-6's vendor-disjoint validation; iter-8A
specifically targets this blockage.
