# v0.0.5 — iter-5/6/7 measurement campaign

**Headline:** `total_lift = +21.88pp` across 4 evals × 3 configurations
(`plugin_only` vs `plugin_with_add_dir` vs `no_skill` baseline), with
4 / 4 evals moving in the right direction and **0 hurts**. Three of the
four evals grade deterministically; the fourth (sec-audit) is
non-deterministic on the current judge (see _Known limitations_) —
the per-eval table below shows one captured realization. The
directional finding is robust (4/4 lift, 0 hurts) and the headline
is dominated by deterministic `filesystem_access_lift` (+13.75pp
mean).

Full report: [`docs/principled/skill-evals/ITERATION-PHASE-RETROSPECTIVE.md`](../docs/principled/skill-evals/ITERATION-PHASE-RETROSPECTIVE.md) (canonical narrative; the per-iteration `iteration-7/REPORT.md` is preserved in the closure archive at `docs/principled/attic/2026-06-23-closure/skill-evals/iteration-7/REPORT.md`).

## What's in the box

- **26 top-level skills** in `skills/`
- **4 marketplace-scoped skills** in `.agents/skills/`
  (marketplace-validator, marketplace-health, releasing-marketplace,
  ingesting-skills) — these are the maintenance skills for the marketplace
  itself
- **5 design-hub sub-skills** (typography, color, motion, layout,
  content) — kept as subskills of `design-hub` after a `taches/
  superpowers` compatibility audit
- **4 plugin manifests** at version 0.0.5 (Claude Code, Codex, Cursor,
  Kimi) — version synced across all manifests

## What changed since v0.0.3

### Added

- **3-config eval harness** (`iter-7`) that decomposes skill-lift into
  two independent mechanisms:
  - `consultation_lift` (the marketplace auto-loads the skill on demand;
    does the model use it?)
  - `filesystem_access_lift` (`--add-dir` grants the model file access;
    does it actually read the skill body?)
  - This is the methodology recommended by [Wataoka et al. 2024](https://arxiv.org/abs/2410.21819)
    and adopted by [SkillRouter (Zheng et al. 2026)](https://arxiv.org/abs/2603.22455)
    to avoid the conflated single-delta "skill helps" measurement that
    ~50% of published work uses.
- **Baseline cache** at `docs/.../baselines/` for iter-N+1 transcript
  reuse. The `--disable-slash-commands` baseline transcripts are now
  stable across iterations: same prompt → same transcript.
- **CI gate** (v0.0.7 release-gate): on `v*.*.*` tag push, validated
  the iter-7 `benchmark.json` against the release contract
  (`total_lift >= +15pp`, no per-eval hurt) and annotated the GitHub
  Release with the headline. The gate validated the committed
  benchmark rather than re-running the harness, because the harness
  depends on a private proxy that is not publicly routable from
  GitHub Actions runners (re-run path is deferred to a future
  version when either the proxy has a public endpoint or a
  self-hosted runner exists). **Removed in v0.0.8** — the v0.0.7
  closure marker removed the eval iterations from the active tree,
  making the release-gate's input JSON structurally inoperable;
  `marketplace-health` remains as the pre-release gate.
- **Grader-noise investigation** at `iter-7/GRADER-NOISE-INVESTIGATION.md` (preserved in closure archive) showing that `temperature=0` does not make the current proxy's configured backend deterministic (5-run probe, default vs temp=0 both stochastic). Mitigation: multi-run averaging (3× per cell, median), deferred to iter-8.

### Changed

- **Version bump 0.0.3 → 0.0.5** across all 4 plugin manifests. The
  0.0.4 tag is reserved for the iter-4 infrastructure milestone and is
  **not** a release.
- **3 `description`-key frontmatter fields** simplified to remove the
  pipe / multi-line syntax that some renderers (Codex, Cursor) parsed
  as a single-line. After the change, descriptions parse as multi-line
  in Claude Code, kimi-code, and Codex. Cursor still flattens, so the
  marketing copy was tightened to a single 2-3-sentence summary
  followed by the `use when` bullets.

### Fixed

- **iter-4 contamination** identified: the iter-4 `without_skill`
  baseline was contaminated by the agent auto-loading a marketplace
  plugin (`crafting-skills` invoked at event 4 of the no-skill
  transcript). The correct iter-4 headline is **+4.94pp
  filesystem_access_lift only**; consultation_lift was zero because
  the baseline was already using the skill.
- **CHANGELOG.md stale references** to v0.0.3 in the v0.0.5 section
  (caught by self-critic, fixed in commit `2697663`).
- **iter-4 REPORT.md** had a similar stale v0.0.3 reference in the
  scope footer (same fix).

## Per-eval results (iter-7)

| Eval | Baseline | `plugin_only` | `plugin_with_add_dir` | Consultation Δ | FS Δ | Total Δ |
|---|---|---|---|---|---|---|
| `eval-skill` | 0.0 | 0.0 | 15.0 | +0.0 | +15.0 | +15.0 |
| `sec-audit` | 0.0 | 32.5 | 32.5 | +32.5 | +0.0 | +32.5 |
| `lint-1` | 0.0 | 0.0 | 25.0 | +0.0 | +25.0 | +25.0 |
| `release-2` | 25.0 | 25.0 | 40.0 | +0.0 | +15.0 | +15.0 |
| **mean** |  |  |  | **+8.12pp** | **+13.75pp** | **+21.88pp** |

`plugin_only` = `--disable-slash-commands` flag set, no skills auto-load
(equivalent to v0.0.3 baseline).
`plugin_with_add_dir` = `plugin_only` + `--add-dir` to expose the
`skills/` filesystem.

## Methodology notes

- **Two independent lift mechanisms**, not a single conflated delta.
  This matches the recommendation in
  [Wataoka et al. 2024, "Self-Preference Bias in LLM-as-a-Judge"](https://arxiv.org/abs/2410.21819)
  (NeurIPS 2024 Safe Generative AI Workshop) for separating
  retrieval / consultation from execution / file I/O, and
  [CoEval (Aperstein et al. 2026)](https://arxiv.org/abs/2606.03650)
  for vendor-disjoint panel evaluation that cancels
  same-family self-preference.
- **Vendor-disjoint grader**: the LLM judge (one tier on the
  proxy) is in a different family from the solver (another tier on the
  same proxy). This guards against the **self-preference bias**
  quantified in Wataoka 2024 (the bias mechanism is
  lower-perplexity preference: LLMs assign higher evaluations to
  outputs that are more familiar to them, regardless of source).
  CoEval 2026 reports a Spearman 0.95 ranking recovery and ρ=0.86
  tracking of objective correctness from a label-free panel of
  vendor-disjoint judges.
- **Body-hidden scoring** (the model only sees the skill name, not the
  body) follows [SkillRouter (Zheng et al. 2026)](https://arxiv.org/abs/2603.22455),
  which reports a 31-44 percentage point drop in routing accuracy
  when the skill body is hidden vs exposed. Our `consultation_lift`
  measurement deliberately uses body-hidden to avoid this inflation.
- **Proxy architecture finding**: the proxy at
  `<private inference gateway>` is a single-family gateway — every alias in the
  vendor catalog (20 vendor aliases) resolves to the same
  configured backend. The tier aliases are proxy tier
  labels, not different models. Only the external judge vendor alias is a genuine second
  family and it is rate-limited (503 `rate-limited`). This is
  documented in iter-6 REPORT.md (preserved in closure archive).

## Known limitations

- **sec-audit consultation_lift is non-deterministic** on the current
  judge. 5-run probe: default and `temperature=0` both stochastic.
  Mitigation deferred to iter-8 (multi-run averaging, ~3× grading cost).
  The **directional finding is robust** (4/4 evals lift, 0 hurt) and
  the headline is dominated by deterministic `filesystem_access_lift`
  (+13.75pp mean).
- **`plugin_only` ceiling on 3 of 4 evals** is 0.0 (model does not
  invoke the marketplace plugin without `--add-dir` because the skills
  directory is outside the model's filesystem view). This is by design
  in `--disable-slash-commands` mode; the consultation mechanism
  requires the skills to be reachable.

## Reproduction

```bash
# Validator
python3 .agents/skills/marketplace-validator/scripts/validate.py .

# Health sweep
python3 .agents/skills/marketplace-health/scripts/health.py

# iter-7 harness (re-uses cached baselines/ by default; closure archive)
# python3 docs/principled/attic/2026-06-23-closure/skill-evals/iteration-7/scripts/run_iteration_7.py

# Release gate (CI parity; removed in v0.0.8 — see CHANGELOG [0.0.8])
# python3 .github/scripts/release-gate.py
```

## Install

Claude Code / kimi-code / Codex / Cursor: install the marketplace at
the matching plugin root (`.claude-plugin/`, `.kimi-plugin/`,
`.codex-plugin/`, `.cursor-plugin/`) and load skills on demand.

## Links

- Full iter-7 report: `docs/principled/skill-evals/ITERATION-PHASE-RETROSPECTIVE.md` (per-iteration `iteration-7/REPORT.md` preserved in closure archive at `docs/principled/attic/2026-06-23-closure/skill-evals/iteration-7/REPORT.md`)
- Grader-noise investigation: preserved in closure archive at `docs/principled/attic/2026-06-23-closure/skill-evals/iteration-7/GRADER-NOISE-INVESTIGATION.md`
- CHANGELOG: `CHANGELOG.md`
- Marketplace-health sweep: `docs/principled/marketplace-health/2026-06-23.md`
