# v0.0.6 — post-v0.0.5 polish, iter-8 design, citation audit

**Headline:** No new skills; no breaking changes; **19 commits, 35 files
changed (+1613/-7)** since v0.0.5. The iter-7 `+21.88pp total_lift`
headline is unchanged. This release ships the **iter-8 design** (a
two-layer MCP test-runner architecture that addresses the two open
follow-ups from iter-7), a **citation hallucination audit** (4
fabricated arXiv IDs + 1 fabricated number replaced with verified
sources), and a **CI action bump** to current major versions
(checkout v7, setup-python v6, upload-artifact v7).

Full changelog: [`CHANGELOG.md`](../../CHANGELOG.md) →
`## [0.0.6] — post-v0.0.5 polish, iter-8 design, citation audit — 2026-06-22`

## What's in the box

Same as v0.0.5 — no changes to the public surface:

- **26 top-level skills** in `skills/`
- **4 marketplace-scoped skills** in `.agents/skills/`
  (marketplace-validator, marketplace-health, releasing-marketplace,
  ingesting-skills)
- **5 design-hub sub-skills** (typography, color, motion, layout,
  content) — kept as subskills of `design-hub`
- **4 plugin manifests** at version **0.0.6** (Claude Code, Codex,
  Cursor, Kimi) — version synced across all manifests

## What changed since v0.0.5

### Added

- **iter-8 plan** at
  [`docs/principled/skill-evals/marketplace-routing-2026-06-22/iteration-8-PLAN.md`](../../docs/principled/skill-evals/marketplace-routing-2026-06-22/iteration-8-PLAN.md)
  **(295 lines)**: three sub-experiments to address the two open
  follow-ups from iter-7.
  - **8A vendor-disjoint grader mock** — local
    mock OpenAI-compatible grader (B-grade) or
    WireMock+LiteLLM (A-grade) running on
    `http://localhost:4010/v1/chat/completions`; the configured solver
    continues against the real `<private inference gateway>` proxy;
    `JUDGE_FIXTURE_MODE=1` env flag routes the judge tier to the
    mock.
  - **8B grader-noise root-cause** — re-grades 4 bit-for-bit
    identical transcripts 11 times each, isolating whether the
    sec-audit +17.5pp swing is from the LLM-judge tier or upstream
    transcript variability.
  - **8C N=11 multi-run averaging** — re-grades the iter-7 12-cell
    grid 11 times to bound the noise floor and confirm the
    `+21.88pp` headline survives median-of-11.
- **iter-8 design supplements** at
  [`docs/principled/research/2026-06-23-iter8-design-supplements.md`](../../docs/principled/research/2026-06-23-iter8-design-supplements.md)
  **(215 lines)**: three findings that refine the iter-8 plan after
  the initial draft.
  - **MCP mocking for `secret_detection`**: a two-layer architecture
    — mock MCP server (Tyk mock-mcp-server, AIMock MCPMock, or a
    custom Python mock) feeds captured golden responses, and
    **mcp-assert** (Go, MIT, github.com/blackwell-systems/mcp-assert,
    18 stars, 0 open issues, project created 2026-04-23) is the test
    runner that asserts YAML expectations against the mock's
    outputs. mcp-assert is a **test runner**, not a mock. The
    integration point is `claude --mcp-config <file>` (added in
    Claude Code v2.1.27+).
  - **Claude Code CLI flag inventory**: `--bare`, `--plugin-dir`,
    `--settings`, `--model`, `--effort`, `--allowedTools`,
    `--max-turns`, `--permission-mode`, `--mcp-config`. The
    iter-8B sub-experiment uses `--mcp-config` pointing at the
    mock MCP server to surgically disambiguate the
    `+17.5pp sec-audit` grader swing.
  - **LiteLLM** (51,259 stars, native MCP + A2A, drop-in OpenAI
    compat, 8ms P95 at 1k RPS) as the recommended self-hosted
    replacement for the structurally-single-family
    `<private inference gateway>` proxy; unblocks iter-6 vendor-disjoint
    validation in v0.0.6+ once deployed.
- **CI release-gate job** (v0.0.7 release-gate): triggered on
  `v*.*.*` tag push. Read the committed iter benchmark JSON, asserted
  `summary.total_lift.mean_overall_delta >= +15pp` AND no per-eval
  `lifts.total_lift.overall_delta < 0pp`. The v0.0.6 tag push ran
  the gate in 10s and **PASSED**. **Removed in v0.0.8** — see the
  v0.0.8 entry for the rationale.
- **Vendor-disjoint grader mock research**: three implementations
  evaluated. **Removed in v0.0.8** — absorbed into the iter-8 design supplements note.
  - **A-grade**: WireMock + LiteLLM (most flexible, but ~120 lines
    of stub config).
  - **B-grade**: a popular OpenAI-compatible mock (single binary, 30-line
    python `scenario.yaml` config, recommended for iter-8A).
  - **C-grade fallback**: 30-line Python shim with FastAPI +
    `openai` SDK (lowest dependency surface, but no fixtures /
    snapshot / replay features).
- **v0.0.5 release notes** at
  [`.github/RELEASE-v0.0.5.md`](RELEASE-v0.0.5.md) (174 lines,
  added in commit `df91ef8`; previously not committed): long-form
  GitHub release page description for the v0.0.5 release.

### Changed

- **Version bump 0.0.5 → 0.0.6** across all 4 plugin manifests.
- **Cached `--disable-slash-commands` baselines preserved** for
  iter-N+1 reuse. Each iter that adds evals only needs to run
  fresh baselines for the new evals, not the full subset.

### Fixed

- **4 fabricated arXiv IDs replaced with verified real ones**
  (caught in citation audit, commits `ab33fa8` + `d4d0cb7`):
  - `2406.01574` → `2410.21819` (Wataoka et al. 2024, "Self-Preference
    Bias in LLM-as-a-Judge", NeurIPS 2024 Safe Generative AI Workshop)
  - `2602.12345` → `2606.03650` (CoEval 2026 v2, vendor-disjoint
    panel evaluation)
  - `2603.12345` → `2603.22455v4` (SkillRouter 2026, body-hidden
    skill routing accuracy)
  - `tesslio/task-evals-for-skills` reference split: the dataset is
    hosted under Tessl AI's `tesslio/` org, distinct from
    [Gorinova et al. 2026 (arxiv:2606.17819)](https://arxiv.org/abs/2606.17819)
    skill-evaluation framework. The two had been cited as a single
    source.
- **1 fabricated κ=0.770 number replaced** with the actual JudgeBench
  κ=0.720 from Norman/Rivera/Hughes 2026
  ([arxiv:2606.19544](https://arxiv.org/abs/2606.19544), 21 judges ×
  9 providers × 3 benchmarks; kappa deflation 33.8-41.2pp universal
  across all 21 judges).
- **iter-8 design self-critic** (4 rounds, commits
  `7e52e6c`/`096437f`/`eadd9ca`/`cedb30d`):
  - mcp-assert correctly characterized as a **test runner**, not a
    mock. The right architecture is a two-layer stack (mock MCP
    server feeds captured responses, mcp-assert asserts YAML
    expectations).
  - `iteration-8-PLAN.md` and the supplements note cross-reference
    each other (added a "Supplements (2026-06-23)" blockquote to
    the plan).
  - Fabricated npm package names (`@tyk/mock-mcp`,
    `@anthropic-ai/secret-detection-server`) replaced with explicit
    placeholders.
  - Invented `--output` flag removed in favor of the documented
    `snapshot --update` flag.
  - `INDEX.md` iter-8 row references the supplements note with
    a one-line summary.
- **CI action bumps** (commit `7f4da98`):
  - `actions/checkout` v4 → v7 (security fix for
    `pull_request_target` / `workflow_run`)
  - `actions/setup-python` v5 → v6
  - `actions/upload-artifact` v4 → v7
  - PR #1 (dependabot's auto-PR for these bumps) closed with a
    comment explaining the local-application workflow.
- **CHANGELOG stale iter-8 supplements entry** (commit `cedb30d`):
  the original entry described a one-layer mock architecture; the
  entry now correctly states the two-layer stack and notes
  mcp-assert's role as a test runner.

## Verification

The `release-gate` CI job ran on the v0.0.6 tag push (workflow
run `28041652620`) and **PASSED** in 10 seconds. The job validates
the committed iter-7 `benchmark.json` against the release
contract: `summary.total_lift.mean_overall_delta >= +15pp` (iter-7
+21.88pp PASSES) AND no per-eval
`lifts.total_lift.overall_delta < 0pp` (4/4 evals lift, 0 hurts
PASSES).

`marketplace-health` (workflow run `28041651474`) also **PASSED** in
10 seconds: HEALTH: pass, validator 0/87 warnings across 31 skills,
manifest consistency at 0.0.6, license coverage OK, cross-references
OK, docs reflect state.

## Third-party cross-confirmation of iter-7 headline

The v0.0.6 research round surfaced two independent
cross-confirmations of the iter-7 +21.88pp headline:

- **[Xu et al. 2026, arxiv:2605.31408](https://arxiv.org/abs/2605.31408)**
  (29 May 2026, "Skill Availability and Presentation Granularity
  in Large-Language-Model Agents: A Controlled SkillsBench Study").
  Skill conditions vs no-skill on a 30-task domain-balanced
  subset (5 trials/cell) yielded **+26.7 to +36.0pp lift for
  GPT-5.5** and **+18.0 to +26.0pp lift for DeepSeek V4-Flash**.
  Our +21.88pp total_lift sits in the middle of this third-party
  bracket, providing external confirmation that the magnitude is
  plausible.
- **[Gorinova et al. 2026, arxiv:2606.17819](https://arxiv.org/abs/2606.17819v1)**
  (16 Jun 2026, "A Framework for Evaluating Agentic Skills at
  Scale"). 500 real-world skills × 1,000 derived tasks × 19 model
  configurations (proprietary + open-source), evaluated with
  instruction-following and goal-completion rubrics. The paper's
  central finding — **"access to a skill significantly changes
  model behavior compared to the no-skill setup"** — and the
  secondary finding that "models vary widely in how closely they
  adhere to the instructions encoded in skills, leading to
  substantial differences in their performance gains" both align
  with our iter-7 total_lift. Qualitative cross-confirmation (no
  specific lift number in the abstract), but the scale (500
  skills, 19 models) provides the strongest external support for
  the qualitative claim that the marketplace plugin produces
  meaningful agent behavior change.

## Known limitations (unchanged from v0.0.5)

- **sec-audit consultation_lift is non-deterministic** on the
  current judge. 5-run probe: default and `temperature=0` both
  stochastic. Mitigation in iter-8B (multi-run averaging, ~3×
  grading cost). The **directional finding is robust** (4/4 evals
  lift, 0 hurts) and the headline is dominated by deterministic
  `filesystem_access_lift` (+13.75pp mean).
- **Vendor-disjoint validation is structurally blocked** on the
  current `<private inference gateway>` proxy (single-family gateway; only
  the external judge vendor alias is vendor-disjoint and rate-limited). iter-8A
  unblocks this via a local mock; v0.0.6+ LiteLLM deployment
  unblocks it for the real proxy.

## Reproduction

```bash
# Validator (post-v0.0.6 should still pass with 0 errors)
python3 .agents/skills/marketplace-validator/scripts/validate.py .

# Health sweep (manifest consistency at 0.0.6)
python3 .agents/skills/marketplace-health/scripts/health.py

# Release-gate (CI parity, validates committed iter-7 benchmark JSON; removed in v0.0.8 — see CHANGELOG [0.0.8])
# python3 .github/scripts/release-gate.py

# iter-8 (when Docker + Claude Code CLI are available)
# python3 docs/principled/attic/2026-06-23-closure/skill-evals/iteration-8/scripts/run_iteration_8.py
```

## Install

Claude Code / kimi-code / Codex / Cursor: install the marketplace
at the matching plugin root (`.claude-plugin/`, `.kimi-plugin/`,
`.codex-plugin/`, `.cursor-plugin/`) and load skills on demand.
Pin to a tag:

```bash
# Kimi Code example
/plugins install https://github.com/Git-Fg/taches-principled-light/releases/tag/v0.0.6
```

## Links

- Full v0.0.6 changelog: [`CHANGELOG.md`](../../CHANGELOG.md) →
  `## [0.0.6]`
- iter-8 plan: `docs/principled/skill-evals/marketplace-routing-2026-06-22/iteration-8-PLAN.md`
- iter-8 design supplements: `docs/principled/research/2026-06-23-iter8-design-supplements.md`
- v0.0.5 release notes: [`.github/RELEASE-v0.0.5.md`](RELEASE-v0.0.5.md)
- iter-7 report: `docs/principled/skill-evals/ITERATION-PHASE-RETROSPECTIVE.md` (per-iteration `iteration-7/REPORT.md` preserved in closure archive)
- Marketplace-health sweep: `docs/principled/marketplace-health/2026-06-23.md`
