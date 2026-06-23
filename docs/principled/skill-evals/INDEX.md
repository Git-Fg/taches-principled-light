# Skill-Evals Index

Behavioral evaluation of the marketplace skill router.
Tracks the 5+ iterations run against the haiku solver (via inference-gateway proxy
on port 3456) using the `evaluating-skills` 8-stage harness.

## Iterations

| # | Date | What it tested | Status | Verdict |
|---|------|----------------|--------|---------|
| 1 | 2026-06-22 | Pilot — single eval `craft-create` end-to-end on Claude Code CLI | superseded by iter-2 | passed. Archived at [`attic/2026-06-23-closure/skill-evals/iteration-1/`](../../attic/2026-06-23-closure/skill-evals/iteration-1/) |
| 2 | 2026-06-22 | Full N=18 evals × {with, without}-skill = 36 runs | superseded by iter-3 | 17/18 completed; 1 proxy 503. Archived at [`attic/2026-06-23-closure/skill-evals/iteration-2/`](../../attic/2026-06-23-closure/skill-evals/iteration-2/) |
| 3 | 2026-06-22 | Full N=17 evals, fixed consultation assertion bug + judge heterogeneity | **superseded by iter-4** | mean delta +8.69pp, 6 lifts / 11 neutrals / 0 hurts. ⚠️ results reflect stale v2.0.0 plugin cache; see `SKILL-DISCOVERY-ARCHITECTURE.md` v1.3. Archived at [`attic/2026-06-23-closure/skill-evals/iteration-3/`](../../attic/2026-06-23-closure/skill-evals/iteration-3/) |
| 3.1 | 2026-06-22 | Per-skill `--add-dir` experiment: H1 (plugin shadowing) vs H2 (description surfaces) vs H3 (choice paralysis) | **complete** (9/15 runs) | H1 confirmed for `craft-create`; H2 confirmed for `craft-review`; H3 not dominant; **H4 bonus**: zero-skill invocations in 6/9 runs (routing-heuristic failure upstream). Archived at [`attic/2026-06-23-closure/skill-evals/iteration-3.1/`](../../attic/2026-06-23-closure/skill-evals/iteration-3.1/) |
| 4 | 2026-06-23 | Cache-refreshed re-run of iter-3 with fresh v0.0.3 cache (heterogeneous judges) | **complete** (18/18 evals) | mean delta **+4.94pp**, 5 lifts / 13 neutrals / **0 hurts**. 3 of 5 lifts are file-access-driven (agent ran colocated scripts via filesystem glob), 2 are consultation-driven (eval-skill, sec-audit). Consultation-driven lower bound: +1.81pp. Archived at [`attic/2026-06-23-closure/skill-evals/iteration-4/`](../../attic/2026-06-23-closure/skill-evals/iteration-4/) |
| 4.1 | 2026-06-23 | **Baseline contamination finding** (no new runs) | **discovered** | iter-4's `without_skill` is contaminated: the marketplace plugin auto-loads into the agent's `slash_commands` regardless of `--add-dir`, so the "no-skill" baseline is actually `plugin_only` (no filesystem access). The agent invoked `/crafting-skills` at event 4 of the without_skill.jsonl. **iter-4's +4.94pp is the FILESYSTEM ACCESS lift, not the total lift vs no-plugin baseline.** True total lift is ≥ +4.94pp (lower bound). See [`attic/2026-06-23-closure/skill-evals/iteration-4/RESEARCH-FINDINGS-iter5-design.md`](../../attic/2026-06-23-closure/skill-evals/iteration-4/RESEARCH-FINDINGS-iter5-design.md) § Baseline Contamination. |
| 5 | 2026-06-23 | N=11 reliability study (4-eval subset, 88 runs) per Yagubyan 2026 (N=3 underpowered) | **designed, deferred** | Will measure intra-rater noise on the +21.9pp iter-7 headline. Deferred because iter-7 already lifts 4/4 with 0 hurts, and the proxy is structurally single-model (no vendor-disjoint judge available). See [`iteration-5-6-7-PLAN.md`](marketplace-routing-2026-06-22/iteration-5-6-7-PLAN.md) § iter-5. Subset: eval-skill, sec-audit, lint-1, release-2. Documented as future-work in iter-7 REPORT. |
| 6 | 2026-06-23 | Vendor-disjoint judge (haiku solver + glm-5.2 judge) per CoEval 2026 | **complete — proxy architecture finding** | glm-5.2 returned 503 `circuit_breaker_open: RateLimit` for all 12 grading cells. Re-purposed as **code-only lift decomposition**: mean **+7.5pp** across 4 evals (consultation + structure-with-compare_args only). The +14.4pp gap to iter-7's +21.9pp is the LLM-judgment contribution. Vendor-disjoint validation structurally blocked: the proxy is a single-model gateway (haiku/sonnet/opus/nex-agi all silently map to MiniMax-M3; only glm-5.2 is vendor-disjoint and is rate-limited). See [`iteration-6/REPORT.md`](marketplace-routing-2026-06-22/iteration-6/REPORT.md). |
| 7 | 2026-06-23 | 3-config lift disambiguation (baseline/plugin_only/plugin_with_add_dir on 4-eval subset) | **complete** | consultation_lift=+8.12pp (NOISY, sec-audit +17.5pp swing on identical transcript), filesystem_access_lift=+13.75pp (deterministic), **total_lift=+21.88pp**. 4/4 evals lift, 0 hurts. **Canonical headline.** True no-plugin baseline uses `--disable-slash-commands`. Cross-link to iter-4 caveat #8 (sec-audit grader noise). See [`iteration-7/REPORT.md`](marketplace-routing-2026-06-22/iteration-7/REPORT.md). |
| 8 | 2026-06-23 | Vendor-disjoint mock + deterministic grader (zerob13/mock-openai-api, 3 sub-experiments: 8A vendor-disjoint, 8B grader-noise root-cause, 8C multi-run averaging) | **designed, not yet run** | Iter-6 vendor-disjoint validation is structurally blocked (proxy is single-model gateway). iter-8 introduces a local OpenAI-API-compatible mock grader that returns canned responses per `(model_name, prompt_hash)`, enabling vendor-disjoint semantics and deterministic grading without a second-model proxy. Wall time: ~3 hours (parallel). See [`iteration-8-PLAN.md`](marketplace-routing-2026-06-22/iteration-8-PLAN.md), [`vendor-disjoint-grader-mock research note`](../../research/vendor-disjoint-grader-mock-2026-06-23.md), and the [`iter-8 design supplements note`](../../research/2026-06-23-iter8-design-supplements.md) (adds a two-layer MCP stack: mock MCP server + mcp-assert test runner; a Claude Code CLI flag inventory; and a LiteLLM multi-model gateway recommendation for v0.0.6+). |

## Canonical report

The iter-7 results are the canonical headline:
[`marketplace-routing-2026-06-22/iteration-7/REPORT.md`](marketplace-routing-2026-06-22/iteration-7/REPORT.md).
This supersedes iter-4 as the citation target.

**iter-7 headline (4-eval subset, deterministic endpoint grades):**
- consultation_lift = **+8.12pp** (NOISY: sec-audit swung +17.5pp on bit-for-bit identical transcript, md5 `bda20918d4b7d0b7245bd12b59b09e58`)
- filesystem_access_lift = **+13.75pp** (deterministic)
- **total_lift = +21.88pp** (deterministic)
- Verdict: **4 lifts / 0 neutrals / 0 hurts**

iter-4's report remains the canonical citation for "the marketplace plugin
helps the agent across diverse evals" (5 lifts / 13 neutrals / 0 hurts, 18
evals). The +4.94pp iter-4 number is the FILESYSTEM ACCESS lift (plugin_only
→ plugin_with_add_dir), now confirmed by iter-7's +13.75pp (over a 4-eval
subset, but covering the strongest 4 evals in iter-4).

**iter-6 caveat:** vendor-disjoint validation is structurally blocked on
this proxy. The proxy is a single-model gateway — haiku/sonnet/opus/nex-agi
all silently map to `MiniMax-M3`; only `glm-5.2` is vendor-disjoint and it
is rate-limited (HTTP 429/503 `circuit_breaker_open: RateLimit`). See
[`iteration-6/REPORT.md`](marketplace-routing-2026-06-22/iteration-6/REPORT.md)
for the proxy architecture finding and the code-only lift decomposition
(+7.5pp mean across 4 evals, the conservative lower bound on the true
total lift under a working vendor-disjoint judge).

iter-3's REPORT is preserved at
[`attic/2026-06-23-closure/skill-evals/iteration-3/REPORT.md`](../../attic/2026-06-23-closure/skill-evals/iteration-3/REPORT.md)
for the historical record (the +8.69pp number is now understood as
stale-cache-inflated).

The intermediate `INTERIM-FINDINGS.md` is SUPERSEDED and archived at
[`marketplace-routing-2026-06-22/.archive/INTERIM-FINDINGS-iter3-SUPERSEDED.md`](marketplace-routing-2026-06-22/.archive/INTERIM-FINDINGS-iter3-SUPERSEDED.md).

## Supporting documents

| Doc | Purpose |
|-----|---------|
| `SKILL-DISCOVERY-ARCHITECTURE.md` | **Foundational.** Documents how Claude Code actually loads skills. Critical findings: `--add-dir` controls cwd + file access only; installed plugins load their skills into `slash_commands` globally regardless of cwd; the iter-3/iter-3.1 plugin cache is **stale (v2.0.0 from 2026-06-21)** and doesn't match the v0.0.3 working marketplace, invalidating parts of the iter-3 results. iter-3's `without_skill` baseline is contaminated; H1 (plugin shadowing) IS the dominant cause of Bucket A3. |
| `iteration-3-design.md` | Synthesizes 6 reference frameworks (SkillsBench, Gorinova 2026, tau-bench, Lee et al. ICML 2026, Khullar 2026, Anthropic/Microsoft best practices) into the iter-3 design |
| `iteration-3/DISCOVERY-INVESTIGATION.md` | Re-evaluates skill rewrites: they target the wrong root cause but remain useful improvements |
| `iteration-3/BUCKET-A-INSPECTION.md` | Splits the 8 Bucket A neutrals into A1 (proxy errors) / A2 (partial discovery) / A3 (true discovery failures) |
| `iteration-3/unknowns.md` | Empty queue for UNKNOWN judge verdicts — schema + log |
| `methodology-note-routing-vs-validator.md` | Why this is a behavioral eval (measuring agent routing behavior) not a static validator run |
| `iteration-2/API-OVERLOAD-INCIDENT.md` | Forensic record of iter-2 partial failure (archived at `attic/2026-06-23-closure/skill-evals/iteration-2/API-OVERLOAD-INCIDENT.md`) |
| `iteration-2/METRIC-BUG-NOTE.md` | Forensic record of grader bug found by self-critic (archived at `attic/2026-06-23-closure/skill-evals/iteration-2/METRIC-BUG-NOTE.md`) |
| `iteration-2/OUTCOME.md` | iter-2 final outcome summary (archived at `attic/2026-06-23-closure/skill-evals/iteration-2/OUTCOME.md`) |
| `iteration-3.1/RESULTS-PARTIAL.md` | 8 of 15 runs captured. H1 confirmed for `craft-create`; craft-review picked wrong marketplace skill; 6 of 8 runs invoked zero skills (routing-heuristic failure) (archived at `attic/2026-06-23-closure/skill-evals/iteration-3.1/RESULTS-PARTIAL.md`) |
| `iteration-4/RESEARCH-FINDINGS-iter5-design.md` | Web-research synthesis driving iter-5/6/7 designs: Yagubyan 2026 (N=11), CoEval 2026 (vendor-disjoint), Wataoka 2024 (self-preference), SkillRouter 2026 (body-hidden drop), Paik Kim 2026 (power analysis), Belmadani 2026 (generator-aware). **Includes the baseline-contamination finding (CRITICAL) that motivates iter-7.** (archived at `attic/2026-06-23-closure/skill-evals/iteration-4/RESEARCH-FINDINGS-iter5-design.md`) |
| `iteration-5-6-7-PLAN.md` | Revised iter-5/6/7 designs. Supersedes iter-4 PLAN's recommended designs based on research findings + baseline contamination. |

## Archived experiments

| Path | Contents |
|------|----------|
| `.archive/iter-2.5-failed-runs/` | iter-2.5 mid-iteration failed runs (3 evals, all `rc=1`) — never recovered, preserved for forensics only |

## Methodology at a glance

- **Solver target**: `haiku` (Claude Haiku 4.5 via proxy) — matches the marketplace's actual consumer base
- **Judge model**: heterogeneous across evals (`sonnet` for complex compliance, `haiku` for simple quality)
- **Lift threshold**: ±5pp = neutral, > +5pp = lifts_quality, < -5pp = hurts (matches `evaluating-skills` `material_difference` rule)
- **Bucket taxonomy**: A (without-skill baseline ≥ 0) / B (without-skill baseline = 0, neutral) / C (lift)
- **Unknown verdicts** (`passed: null` from judge) are mapped to `unknown: true` and treated as FAIL for scoring; see `iteration-3/unknowns.md`

## Reproducing iter-3

```bash
cd docs/principled/attic/2026-06-23-closure/skill-evals/iteration-3
python scripts/run_iteration_3.py    # 17 evals x 2 configs = 34 runs
python scripts/grader.py             # reads benchmarks/, writes REPORT.md
```

Wall-clock budget: ~50 min for runs + ~5 min for grading on a warm proxy.

## Reproducing iter-3.1 (in progress)

```bash
cd docs/principled/attic/2026-06-23-closure/skill-evals/iteration-3.1
python scripts/run_per_skill_experiment.py
```

5 Bucket A3 evals x 3 configs (without_skill / with_full_marketplace / with_skill_only)
= 15 runs. Tests whether the discovery failure is H1 (plugin shadowing), H2 (description
doesn't surface), or H3 (choice paralysis from 26+ marketplace skills).