# Changelog

All notable changes to the taches-principled-light marketplace.

## [0.0.3] — 2026-06-23

Behavior-eval-validated router improvements + corrected eval pipeline. No new skills; no breaking changes. Mean lift +8.69pp over 17 evals, 6 lifts / 11 neutrals / **0 hurts**.

### Changed

- **6 zero-discovery skills gained 5-10 trigger phrases each** (commit `724f7b5`) per Microsoft best-practices guidance (`learn.microsoft.com/.../trigger-phrases-best-practices`). Affected: `crafting-skills` (82 words), `plan-lifecycle` (70), `deep-research` (60), `task-lifecycle` (71), `web-search` (71), `security` (67). The 0.0.2 ≤50-word target was relaxed for these skills because the targeted *trigger-phrase density* (varied sentence structure, short phrases, 5-10 per topic) matters more than total word count for routing precision. Trade-off documented in the iter-3 corrected REPORT.
- **2 skills rewritten with scope router** (commit `861df65`): `ingesting-skills` and `marketplace-validator`. Both now lead with explicit scope triggers (`Load when porting a skill into this marketplace from an external source`) followed by the original workflow. Subsequent iter-3 analysis showed the rewrites target the wrong root cause (the discovery failure is in the *agent* layer, not the *description* layer — see BUCKET-A-INSPECTION below), but the rewrites remain useful as routing-clarity improvements.

### Added

- **Iter-3 corrected evaluation pipeline** (`docs/principled/skill-evals/marketplace-routing-2026-06-22/iteration-3/`):
  - `scripts/grader.py` (357 lines) — 4-assertion taxonomy (consultation/structure/compliance/quality) with hybrid per-category + cross-category weighted scoring (Tessl + tau-bench `EvaluationCriteria`).
  - `scripts/run_iteration_3.py` (298 lines) — orchestrator for 17 evals × {with, without}-skill = 34 runs.
  - `REPORT.md` (corrected) — **canonical** eval report. Mean delta +8.69pp; 6 lifts / 11 neutrals / 0 hurts. Lift threshold ±5pp = neutral; > +5pp = lifts_quality; < -5pp = hurts.
  - `BUCKET-A-INSPECTION.md` — forensic split of 8 Bucket A neutrals into A1 (proxy 503 errors: plan-multi, task-small) / A2 (partial discovery: research) / A3 (true discovery failures: ingest-1, ingest-2, lint-2, craft-create, craft-review). Identifies plugin-shadowing (H1) as the most likely root cause of the 5 A3 failures.
  - `DISCOVERY-INVESTIGATION.md` — re-evaluates the 2 skill rewrites: KEEP both (they improve routing clarity) but don't expect them to fix Bucket A neutrals — they target the wrong root cause.
  - `iteration-3-design.md` — synthesizes 6 reference frameworks (SkillsBench arXiv 2602.12670v4, Tessl arXiv 2606.17819v1, tau-bench, Lee et al. ICML 2026 bias-adjusted estimator, Khullar 2026 self-attribution, Anthropic/Microsoft skill best practices) into the iter-3 design.
  - `INDEX.md` (new) — top-level discovery surface for the eval set; 4 iterations summarized.
- **Iter-3.1 per-skill `--add-dir` experiment** (`docs/.../iteration-3.1/`): tests whether Bucket A3 discovery failures are caused by (H1) plugin shadowing, (H2) description surfaces, or (H3) choice paralysis. 5 evals × 3 configs = 15 runs. In progress as of release; full write-up committed separately when complete.

### Fixed

- **`grader.py` consultation assertion bug** (commit `b45c40a`): the consultation check previously accepted ANY skill read (`any("SKILL.md" in p)`), inflating without-skill scores and producing 3 phantom `skill_hurts` results. Fixed to match the expected skill path. Per-skill results after fix: `lint-1` +45pp, `critic` +31.2pp, `release-2` +25pp, `audit-1` +16.5pp (previously hidden lift), `release-1` +15pp, `eval-skill` +15pp. The 3 phantom hurts collapsed to neutral.
- **`passed: null` judge verdicts** are now mapped to `unknown: true` and treated as FAIL for scoring; logged to `iteration-3/unknowns.md` for human review queue. Empty queue as of release (no UNKNOWN verdicts emitted).

### Archived

- `iteration-2.5/` orphan (3 evals, all `rc=1 duration_ms: 0`) → `.archive/iter-2.5-failed-runs/`. Never recovered; preserved for forensics only.
- `iteration-3/INTERIM-FINDINGS.md` (SUPERSEDED by corrected REPORT.md) → `.archive/INTERIM-FINDINGS-iter3-SUPERSEDED.md`.

### Verified

- `marketplace-health`: **HEALTH: pass** (validator 0/87 warnings across 31 skills; manifest consistency at 0.0.3; license coverage OK; cross-references OK; docs reflect state — README says 31, CHANGELOG latest = 0.0.3, INDEX.md lists 4 iterations).
- **Behavior eval (iter-3 corrected)**: 17 evals × {with, without}-skill = 34 runs on haiku solver (matches marketplace consumer base). Mean delta **+8.69pp** vs without-skill baseline; 6 lifts / 11 neutrals / **0 hurts**. Lifts: `lint-1` +45pp, `critic` +31.2pp, `release-2` +25pp, `audit-1` +16.5pp, `release-1` +15pp, `eval-skill` +15pp. Bucket A neutrals (8) split A1/A2/A3 per BUCKET-A-INSPECTION; A3 most likely caused by H1 plugin shadowing, to be confirmed by iter-3.1.
- **Methodology note** (`docs/.../methodology-note-routing-vs-validator.md`): distinguishes this as a behavioral eval (measuring agent routing behavior against graded assertion sets) not a static validator run.

### Known follow-up work

- iter-3.1 experiment in flight; commit `iteration-3.1/RESULTS.md` when complete.
- Re-run A1 evals (plan-multi, task-small) on clean proxy to get discovery-failure verdicts.
- Multi-trial N=3 reliability study for the 7 single-sample skills and 3 Bucket B neutrals.
- Re-run the 6 lifts with `--judge-model sonnet` for same-family bias mitigation (Wataoka 2024).

## [0.0.2] — 2026-06-22

First post-alpha iteration. Description-format refactor + routing-precision improvements + parser hardening + behavior eval pilot. No new skills; no breaking changes.

### Changed

- **Skill descriptions:** all 31 `skills/*/SKILL.md` descriptions refactored from multi-line YAML `>` folded scalar to single-line YAML `"…"` quoted scalar (commit `904e11e`). Maximum compatibility with all consumer agents and all YAML 1.2 parsers. The 4 meta-marketplace SKILL.md under `.agents/skills/` (marketplace-validator, marketplace-health, ingesting-skills, releasing-marketplace) remain in the old `>` format — out of scope for the consumer-facing refactor.
- **Description length:** 27 descriptions tightened to ≤50 words per Compendium Rule 3 (commit `32f7142`). Two skills in `skills/` retained signal qualifiers and ended slightly above the ≤50 target (test-orchestration 52, crafting-skills 53 by the project's `\b\w+\b` word-count methodology). Separately, `marketplace-validator` (`.agents/skills/`) ended this release at 52 words after the routing-collision fix in `7617c0a` — incidental, not a deliberate exception.
- **4 of 5 design-hub sub-skills** (`design-good-bad-examples`, `typography-guide`, `design-system-palettes`, `pdf-design-guide`) gained `Do NOT use for X (use Y)` negative triggers per Compendium Rule 2 (commit `8dc1306`). `design-principles` is still pending a negative trigger and is tracked separately.

### Fixed

- **`parse_frontmatter_safe`** (validator): added single-quoted scalar support (`'…'` with `''` doubling convention) and YAML 1.2 double-quoted escape sequence support (`\"`, `\\`, `\n`, `\t`, `\r`, `\/`) (commit `559f086`). Real-world fix: `skills/design-hub/design-good-bad-examples/SKILL.md` description containing `\"` now resolves correctly.
- **`routing_test.py`:** was loading only 5 of 35 skills due to a regex that matched only the old `description: >` multi-line format (commit `004e5e1`). Switched to reuse `parse_frontmatter_safe` directly. Pool is now 35; the prior `7W / 0T / 3L` baseline was vacuous (measured against a 5-skill pool). Restored two signal qualifiers (`idea-to-design` in generating-ideas; `new-feature` in test-orchestration) that had been casualties of the `32f7142` OPTIMIZE tightening — not the regex bug.
- **2 of 4 routing collisions** broken via targeted description edits (commit `7617c0a`): marketplace-validator ↔ marketplace-health and crafting-skills ↔ marketplace-validator. The remaining 2 collisions (general-critic ↔ security, deep-research ↔ orchestrating-subagents) are inherent word-overlap scoring limitations and accepted as ties.

### Verified

- `marketplace-health`: **HEALTH: pass** (validator 0/82 warnings, manifest consistency at 0.0.2, license coverage OK, cross-references OK, docs reflect state).
- `routing_test.py`: **15W / 1T / 2L** over 18 utterances × 35 skills (was 7W over 5 skills — vacuous baseline). The 2 ties are documented above; the 2 losses were the general-critic/security and deep-research/orchestrating-subagents ambiguities not broken in this release.
- **Behavioral eval pilot** (commit `2fae0b1`, [`docs/principled/skill-evals/marketplace-routing-2026-06-22/`](docs/principled/skill-evals/marketplace-routing-2026-06-22/)): single-eval pilot (`craft-create`) demonstrating the `evaluating-skills` 8-stage harness works end-to-end on Claude Code CLI. Material difference observed: with-skill run consulted 3 marketplace SKILL.md files (crafting-skills + pdf-design-guide + deep-research), without-skill run consulted 0. Iteration-2 (full N=18 with 180-300s timeout) queued for a future session.

---

## [0.0.1-alpha] — 2026-06-22

First alpha cut. All four plugin manifests (Claude Code, Codex, Cursor, Kimi Code) are centralized at version 0.0.1. The marketplace ships 26 top-level skills (31 SKILL.md total including 5 design-hub sub-skills) plus 4 local meta-marketplace skills in `.agents/skills/`.

### Skills shipped (26 top-level)

| Domain | Skills |
|--------|--------|
| **Lifecycle** | `plan-lifecycle`, `task-lifecycle`, `plan-do-check-act` |
| **Quality** | `reviewing-and-polishing`, `general-critic`, `applying-guardrails`, `restructuring-code`, `test-orchestration` |
| **Reasoning** | `reasoning-from-principles`, `solving-competitively`, `web-search`, `deep-research` |
| **Domain** | `engineering-mcp`, `rust`, `security`, `git`, `managing-wiki`, `managing-rules`, `claude-cli` |
| **Meta** | `crafting-skills`, `evaluating-skills`, `orchestrating-subagents`, `analyzing-sessions`, `project-maintenance` |
| **Design** | `design-hub` (hub) with 5 sub-skills: `pdf-design-guide`, `design-system-palettes`, `typography-guide`, `design-principles`, `design-good-bad-examples` |
| **Idea** | `generating-ideas` |

### Local meta-marketplace skills (`.agents/skills/`)

- **`marketplace-validator`** — frontmatter + body linter (canonical spec + local convention), machine-readable JSON output
- **`ingesting-skills`** — 9-step porting workflow for adding external skills from any source
- **`marketplace-health`** — pre-release sweep: validator + manifest consistency + license coverage + cross-reference integrity + docs-reflect-state
- **`releasing-marketplace`** — 7-step approval-gated release orchestrator

### Convention compliance

- All 31 SKILL.md files have `license: MIT` in frontmatter
- All skills pass `marketplace-validator` (0 failures; 119 advisory warnings — mostly `description_word_count` and `unexpected_fm_key` for local frontmatter extensions)
- All cross-references resolve (no broken `references/X.md` or `scripts/Y.py` citations)
- README reflects current skill count (31 SKILL.md total)
- All 4 plugin manifests at version 0.0.1

### Research artifacts

- `docs/principled/research/agent-skills-evaluation/` — 6 artifacts documenting the `evaluating-skills` methodology (background, judgment, analysis, plan, document, final)
- `docs/principled/marketplace-health/2026-06-22.md` — first automated health sweep report

---

## Pre-alpha lineage

Before centralizing on 0.0.1-alpha, the marketplace went through a rapid evolution (May–June 2026) from an 11-plugin multi-component marketplace (skills + agents + commands + hooks + scripts) to the current flat skills-only structure. Key milestones, preserved as git history:

1. **Multi-plugin era (0.1.0–1.10.0):** 11 separate plugins (`core-principled`, `tp-rust`, `tp-git`, `tp-mcp`, `tp-sadd`, `tp-fpf`, `tp-security`, `tp-session-audit`, `tp-wiki`, `claude-cli-wrapper`, `tp-discipline`) with agents, commands, hooks, and scripts. Hub-and-spoke consolidation reduced 34 skills to 20, then grew back as domain expertise deepened.

2. **Consolidation era (1.11.0–1.23.1):** Agent roster reduced from 55 named subagents to 6 keepers (`tp-critic`, `tp-explorer`, `tp-researcher`, `mcp-quality-judge`, `sadd-judge`, `wiki-searcher`) using the lens-prompt pattern. Inline MCP server (`claude-cli-wrapper`) replaced with direct CLI skill. Description optimization pass across all routing signals.

3. **Flat restructure (2.0.0–2.1.0):** All agents, commands, hooks, and scripts removed. Skills-only plugin with platform-agnostic subagent spawning ("spawn a subagent explorer" / "spawn a subagent generalist"). Four new skills added: `design-hub` (+5 sub-skills), `evaluating-skills`, `deep-research`, `general-critic`. `crafting-skills` body split into hub + `references/best-practices-compendium.md`.

4. **Alpha centralization (this release):** Version reset to 0.0.1-alpha across all 4 plugin manifests. License coverage (MIT) added to all skills. 4 local meta-marketplace skills created in `.agents/skills/`. Cross-skill reference bugs fixed. README and health-sweep tooling brought online.
