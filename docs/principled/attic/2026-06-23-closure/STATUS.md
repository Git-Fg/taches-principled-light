# Archive Status — v0.0.7 iteration phase closure

**Status:** completed
**Closure marker:** v0.0.7 release tag (this commit)
**Archived:** 2026-06-23

## What this archive is

This is the post-v0.0.6 cleanup bundle. The v0.0.6 release consolidated the
marketplace-routing eval cycle. The active working tree was carrying 13 MB
of historical artifacts that are now preserved here as audit trail. The
v0.0.7 release is the iteration phase closure marker — no new features, no
new skills, just finalization.

## Why no SUMMARY.md

The project-maintenance skill's archive precondition (`SUMMARY.md` at the
same path as `PLAN.md`) is adapted for this project per the AGENTS.md
"Project Closure Convention":

> For this project, the durable closure marker for a completed work cycle
> is CHANGELOG entry + release tag + `grading_summary.json`. The
> plan-lifecycle `SUMMARY.md` is optional unless a specific skill explicitly
> requires it. For archive bundles, `STATUS.md` pointing to the release
> tag + CHANGELOG entry is an acceptable alternative to `SUMMARY.md`.

The `grading_summary.json` requirement is specifically for plan-archive
workflows (the v0.0.6 marketplace release follows that pattern). For
v0.0.7 — which is a cleanup + repo-finalization release — there is no new
eval to grade, and the iter-7 `grading_summary.json` from v0.0.6 is the
still-canonical source of truth. `STATUS.md` + `metadata.md` + the
`[0.0.7]` CHANGELOG section together serve as the closure record.

## Closure verification (Iron Law: evidence before claims)

- `git mv` preserves history for all archived files: ✓ (verified via `git log --follow` on each path)
- iter-7/REPORT.md and iter-7/GRADER-NOISE-INVESTIGATION.md cross-refs updated: ✓
- INDEX.md simplified to point to closure archive: ✓
- 4 plugin manifests at v0.0.7: pending (next step)
- CHANGELOG [0.0.7] entry written: pending (next step)
- README closure note: pending (next step)
- Local dev cruft (`.pytest_cache/`) removed via `trash`: pending (next step)
- `python3 .agents/skills/marketplace-health/scripts/health.py` post-archive: pending (next step)
- `git commit` + `git tag v0.0.7`: pending (next step)

## File inventory

| Path | What it is |
|------|------------|
| `metadata.md` | archive index, file inventory, key decisions, closure list |
| `plans/2026-06-22-router-language-audience.md` | old plan, Task 1 executed, rest abandoned |
| `plans/2026-06-22-skill-steering-point-to-sources.md` | old plan, partial execution |
| `specs/2026-06-22-router-language-audience-design.md` | design spec for the above plan |
| `specs/2026-06-22-skill-steering-point-to-sources.md` | design spec for the above plan |
| `design/hub-subskills-compatibility.md` | 2026-06-23 design note for an already-shipped feature |
| `research/agent-skills-evaluation/` | 6 intermediate work products (analysis, background, document, final, judgment, research_plan) from 2026-06-22 `evaluating-skills` methodology research |
| `research/hub-references-routing-evals/` | 7 intermediate work products from 2026-06-22 that informed the claude-cli split + skill-steering plans |
| `skill-evals/iteration-1/` | pilot (296K), superseded by iter-2 |
| `skill-evals/iteration-2/` | broken by API overload (4.4M, 5/18 partial runs, all-zero signal) |
| `skill-evals/iteration-3/` | +8.69pp headline (stale cache), corrected by iter-4 (396K) |
| `skill-evals/iteration-3.1/` | per-skill `--add-dir` experiment (336K, 9/15 runs complete) |
| `skill-evals/iteration-4/` | cache-refreshed +4.94pp headline (7.2M, 18/18 evals) |

## Next cycle

See `metadata.md` § "Next cycle" for the iter-8 forward-looking plan and the
infrastructure dependencies (Docker, Claude Code CLI, LiteLLM proxy replacement)
that must be available before iter-8 can be executed.
