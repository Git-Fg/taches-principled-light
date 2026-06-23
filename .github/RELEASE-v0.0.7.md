# v0.0.7 — iteration phase closure marker (repo finalization)

**Headline:** No new skills; no breaking changes; no new behavioral
data. The iter-7 **`+21.88pp total_lift`** headline is unchanged.
This release ships a **repo finalization** that archives ~13 MB of
historical artifacts (5 superseded eval iterations, 2 executed plans
with no `SUMMARY.md`, 2 design specs, 1 design note for an
already-shipped feature, 13 intermediate research work products) into
`docs/principled/attic/2026-06-23-closure/`. Active tree shrinks from
15 MB → 2.4 MB (84% reduction). All 4 plugin manifests synchronized
to **0.0.7**.

Full changelog: [`CHANGELOG.md`](../../CHANGELOG.md) →
`## [0.0.7] — iteration phase closure marker (repo finalization) — 2026-06-23`

## What's in the box

Same as v0.0.6 — no changes to the public surface:

- **26 top-level skills** in `skills/`
- **4 marketplace-scoped skills** in `.agents/skills/`
  (marketplace-validator, marketplace-health, releasing-marketplace,
  ingesting-skills)
- **5 design-hub sub-skills** (typography, color, motion, layout,
  content) — kept as subskills of `design-hub`
- **4 plugin manifests** at version **0.0.7** (Claude Code, Codex,
  Cursor, Kimi) — version synced across all manifests

## What changed since v0.0.6

### Added

- **Closure archive bundle** at
  [`docs/principled/attic/2026-06-23-closure/`](../../docs/principled/attic/2026-06-23-closure/)
  (~13 MB → 2.4 MB working tree). Contains:
  - [`STATUS.md`](../../docs/principled/attic/2026-06-23-closure/STATUS.md)
    **(39 lines)**: closure record per the AGENTS.md "Project Closure
    Convention" — documents the v0.0.7 release as the iteration phase
    closure marker, the adapted closure contract (no `SUMMARY.md` for
    a cleanup release; `STATUS.md` + `metadata.md` + CHANGELOG
    `[0.0.7]` + release tag is the durable record), and the
    cross-reference update list.
  - [`metadata.md`](../../docs/principled/attic/2026-06-23-closure/metadata.md)
    **(102 lines)**: file inventory, key decisions, and the 4
    cross-reference files updated in the active tree.
  - `plans/` (2 files): 2 executed plans without `SUMMARY.md` (Task 1
    done, rest abandoned in each).
  - `specs/` (2 files): design specs for the above plans.
  - `design/` (1 file): `hub-subskills-compatibility.md` — 2026-06-23
    design analysis for an already-shipped feature, no longer
    referenced from any active artifact (zero grep hits).
  - `research/` (13 files): 2 intermediate research bundles —
    `agent-skills-evaluation/` (6 files) and
    `hub-references-routing-evals/` (7 files). The canonical artifacts
    are either already cited in CHANGELOG or preserved in
    `skill-evals/`.
  - `skill-evals/iteration-1/`, `iteration-2/`, `iteration-3/`,
    `iteration-3.1/`, `iteration-4/`: 5 superseded eval iterations
    (~12.5 MB total) — iter-1 (pilot, +8.69pp pilot data), iter-2
    (broken by API overload), iter-3 (corrected pipeline, +8.69pp
    headline superseded by cache-refreshed iter-4), iter-3.1
    (per-skill `--add-dir` experiment), iter-4 (filesystem_access
    lift only, +4.94pp on 18 evals). The canonical **iter-7
    +21.88pp total_lift** (4/4 lifts, 0 hurts) stays in the active
    tree.
- **v0.0.7 release notes** (this file): long-form GitHub release
  page description for the v0.0.7 tag.

### Changed

- **Version bump 0.0.6 → 0.0.7** across all 4 plugin manifests
  (`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`,
  `.codex-plugin/plugin.json`, `.cursor-plugin/plugin.json`,
  `.kimi-plugin/plugin.json`).
- **Active tree reduction: 15 MB → 2.4 MB** (84% reduction). The
  active tree now contains only the canonical signal:
  `iteration-6/` (proxy architecture finding), `iteration-7/`
  (canonical headline), `iteration-8-PLAN.md` (forward-looking),
  `baselines/`, `evals/`, `scripts/`, `capabilities.json`,
  `SKILL-DISCOVERY-ARCHITECTURE.md`,
  `methodology-note-routing-vs-validator.md`, `.archive/`.
- **Cross-reference updates** in 4 active files:
  - [`docs/principled/skill-evals/INDEX.md`](../../docs/principled/skill-evals/INDEX.md)
    (rows 11-15, 16, 50-55, 66-70, 88-101) — iter-1/2/3/3.1/4
    entries now point to `attic/2026-06-23-closure/skill-evals/iteration-N/`.
  - [`iteration-7/REPORT.md`](../../docs/principled/skill-evals/marketplace-routing-2026-06-22/iteration-7/REPORT.md)
    (line 151) — `iteration-4/REPORT.md` reference updated.
  - [`iteration-7/GRADER-NOISE-INVESTIGATION.md`](../../docs/principled/skill-evals/marketplace-routing-2026-06-22/iteration-7/GRADER-NOISE-INVESTIGATION.md)
    (lines 19, 22, 68, 69) — `iteration-3/scripts/grader.py` and
    `iteration-4/eval-sec-audit/grading_without_skill.json` paths
    updated.
  - [`SKILL-DISCOVERY-ARCHITECTURE.md`](../../docs/principled/skill-evals/marketplace-routing-2026-06-22/SKILL-DISCOVERY-ARCHITECTURE.md)
    (line 164) — v1.4 changelog entry updated.
- **`.gitignore` broadened**: `__pycache__` coverage extended from
  `plugins/**/__pycache__/` to cover all paths
  (`skills/**/__pycache__/`, `.agents/**/__pycache__/`,
  `docs/**/__pycache__/`, `**/__pycache__/`). Added `.pytest_cache/`.

### Removed

- 5 historical eval iterations (`iteration-1/`, `iteration-2/`,
  `iteration-3/`, `iteration-3.1/`, `iteration-4/`) — total ~12.5 MB
  of eval transcripts preserved in the closure archive.
- 2 plans without `SUMMARY.md` (one Task each, rest abandoned).
- 2 design specs for the above plans.
- 1 design note for an already-shipped feature
  (`hub-subskills-compatibility.md`).
- 13 intermediate research work products (2 bundles) where the
  canonical artifact is either the closure archive or already cited
  in the CHANGELOG.
- 1 orphan `run_iteration_2.py` (hardcoded
  `ITER_DIR = WORKSPACE / "iteration-2"` path that no longer exists
  in the active tree).
- 7 untracked `__pycache__` directories, 10 `.pyc` files, 1
  `.DS_Store`, 1 `.pytest_cache/` — removed via `trash` per the
  AGENTS.md "USE TRASH" mandate.

### Fixed

- **Stale CHANGELOG `[Unreleased]` section**: the pre-v0.0.7
  CHANGELOG header said "v0.0.6 release tag (pending) is the latest
  published release" — but v0.0.6 was already tagged (`bd04ae0`).
  Replaced with the v0.0.7 closure entry. The `[Unreleased]` section
  is removed (no active development; the iteration phase is closed).
- **Orphan `scripts/run_iteration_2.py`**: hardcoded path to a
  directory that no longer exists in the active tree. Moved to the
  closure archive.
- **`hub-subskills-compatibility.md` design note**: zero grep hits
  in the active tree. Moved to the closure archive.

## Verification

`marketplace-health` runs cleanly post-archive: **HEALTH: pass
(validator 0/87 across 31 skills; manifest consistency at 0.0.7;
license coverage OK; cross-references OK)**. Report at
[`docs/principled/marketplace-health/2026-06-23.md`](../../docs/principled/marketplace-health/2026-06-23.md).

The `release-gate` CI job is unaffected by the archive moves —
`iter-7/grading_summary.json` is in the active tree, and the gate
contract (`summary.total_lift.mean_overall_delta >= +15pp` AND no
per-eval `lifts.total_lift.overall_delta < 0pp`) is unchanged.

## Known limitations (unchanged from v0.0.5/v0.0.6)

- **sec-audit consultation_lift is non-deterministic** on the current
  judge. Mitigation in iter-8B (multi-run averaging, ~3× grading
  cost). The **directional finding is robust** (4/4 evals lift, 0
  hurts) and the headline is dominated by deterministic
  `filesystem_access_lift` (+13.75pp mean).
- **Vendor-disjoint validation is structurally blocked** on the
  current `100.80.231.128:3456` proxy (single-model gateway; only
  `glm-5.2` is vendor-disjoint and rate-limited). iter-8A unblocks
  this via a local mock; v0.0.6+ LiteLLM deployment unblocks it for
  the real proxy. iter-8-PLAN.md is preserved in the active tree
  awaiting execution.

## Reproduction

```bash
# Validator (post-v0.0.7 should still pass with 0 errors)
python3 .agents/skills/marketplace-validator/scripts/validate.py .

# Health sweep (manifest consistency at 0.0.7)
python3 .agents/skills/marketplace-health/scripts/health.py

# Release-gate (CI parity, validates committed iter-7 benchmark JSON)
python3 .github/scripts/release-gate.py
```

## Install

Claude Code / kimi-code / Codex / Cursor: install the marketplace at
the matching plugin root (`.claude-plugin/`, `.kimi-plugin/`,
`.codex-plugin/`, `.cursor-plugin/`) and load skills on demand. Pin
to a tag:

```bash
# Kimi Code example
/plugins install https://github.com/Git-Fg/taches-principled-light/releases/tag/v0.0.7
```

## Links

- Full v0.0.7 changelog: [`CHANGELOG.md`](../../CHANGELOG.md) →
  `## [0.0.7]`
- Closure archive: `docs/principled/attic/2026-06-23-closure/`
  ([`STATUS.md`](../../docs/principled/attic/2026-06-23-closure/STATUS.md)
  ·
  [`metadata.md`](../../docs/principled/attic/2026-06-23-closure/metadata.md))
- iter-7 canonical headline:
  [`iteration-7/REPORT.md`](../../docs/principled/skill-evals/marketplace-routing-2026-06-22/iteration-7/REPORT.md)
- iter-8 forward-looking plan:
  [`iteration-8-PLAN.md`](../../docs/principled/skill-evals/marketplace-routing-2026-06-22/iteration-8-PLAN.md)
- v0.0.6 release notes: [`.github/RELEASE-v0.0.6.md`](RELEASE-v0.0.6.md)
- Marketplace-health sweep:
  [`docs/principled/marketplace-health/2026-06-23.md`](../../docs/principled/marketplace-health/2026-06-23.md)
