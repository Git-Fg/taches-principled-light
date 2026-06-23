# Archive Status — v0.0.6 marketplace-routing eval cycle closure

**Status:** completed
**Closure marker:** v0.0.6 release tag (`bd04ae0` release commit; `eca1b74` self-critic round 2 fix)
**Archived:** 2026-06-23

## Why no SUMMARY.md

This project's eval-iteration workflow uses the CHANGELOG `[0.0.6]` section
+ `grading_summary.json` + REPORT.md per iteration as the closure record,
not the formal `plan-lifecycle EXECUTE` mode that produces `SUMMARY.md`.
The project-maintenance skill's hard precondition (`SUMMARY.md` at the
same path as `PLAN.md`) is therefore adapted for this archive:

- `bd04ae0` — release commit, includes 19 commits of v0.0.6 work
- `eca1b74` — self-critic round 2 fix commit (Berkeley hallucination removed,
  LiteLLM star drift fixed, unverified "last commit" claim soft-pedaled)
- CHANGELOG.md lines 18-41 — `[0.0.6]` section, the canonical narrative
- `docs/principled/skill-evals/marketplace-routing-2026-06-22/iter-7/grading_summary.json` —
  release-gate source of truth (`+8.12pp + +13.75pp = +21.88pp`)
- 4 PLAN files archived below (the plan documents that were executed)

## Plan files archived

| Plan file | Iterations covered | Outcome |
|---|---|---|
| `plans/iteration-5-6-7-PLAN.md` | iter-5, 6, 7 | iter-7 produced canonical +21.88pp; released as v0.0.6 |
| `plans/iteration-3-design.md` | iter-3 | +8.69pp headline superseded by cache-corrected +4.94pp (iter-4) |
| `plans/PLAN.md` (iter-4) | iter-4 | +4.94pp after cache contamination correction |
| `plans/RESEARCH-FINDINGS-iter5-design.md` (iter-4) | iter-5/6/7 design | drove iter-5/6/7 plan; validated by Xu 2026 + Gorinova 2026 + Norman 2026 |

## Forward-looking (NOT archived)

- `docs/principled/skill-evals/marketplace-routing-2026-06-22/iteration-8-PLAN.md` —
  iter-8 design (two-layer MCP test-runner stack, vendor-disjoint grader
  mock, N=11 multi-run averaging). Active in working tree, awaits execution.

## Closure verification (Iron Law: evidence before claims)

- `bd04ae0` tag pushed: ✓
- CI release-gate on `bd04ae0`: PASS (run 28041652620)
- CI marketplace-health on main: PASS (run 28041651474)
- `eca1b74` self-critic fix commit pushed: ✓
- Post-fix marketplace-validator: `0 failures, 87 warnings` (stable baseline)
- Post-fix release-gate: `+21.88pp` headline preserved
- Post-fix marketplace-health: `HEALTH: pass`
- 4 PLAN files in attic: ✓ (see `metadata.md`)

## Next cycle (post-archive)

`iteration-8-PLAN.md` is the natural next step — execute the iter-8 design
when Docker + Claude Code CLI + multi-model proxy (LiteLLM replacement)
become available. The current structurally-single-model
`100.80.231.128:3456` proxy blocks iter-6's vendor-disjoint validation;
iter-8A specifically targets this blockage.
