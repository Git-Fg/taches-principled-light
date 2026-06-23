# Iteration 4 — Cache-Refreshed Re-Run (Phase A)

**Status:** ✅ complete, **SUPERSEDED by iter-7** for headline numbers
**Started:** 2026-06-23 14:24
**Ended:** 2026-06-23 15:35 (≈71 min wall)
**Judge:** sonnet (heterogeneous over haiku solver)
**Cache state:** fresh (cleared 2026-06-23, smoke test confirmed `craft-create` picks `taches-principled-light:crafting-skills`)

> **iter-7 supersedes this headline (2026-06-23).** iter-4's `without_skill` baseline was contaminated: the marketplace plugin auto-loads into the agent's `slash_commands` regardless of `--add-dir`. iter-4's "+4.94pp" is the **filesystem_access_lift only**, not the total lift vs a no-plugin baseline. The true total lift on the 4-eval subset is **+21.88pp** (4 lifts / 0 neutrals / 0 hurts). See [`../iteration-7/REPORT.md`](../iteration-7/REPORT.md) and [`../iteration-6/REPORT.md`](../iteration-6/REPORT.md) for the follow-up campaign.

## Headline

| Metric | iter-3 (stale cache, N=17) | iter-4 (fresh cache, N=18) | Δ |
|---|---:|---:|---:|
| **Mean overall delta** | **+8.69pp** | **+4.94pp** | **−3.75pp** |
| Mean IF delta | n/a | +7.50pp | — |
| Mean GC delta | n/a | +2.78pp | — |
| Lifts (`skill_lifts_quality`) | 6/17 | 5/18 | −1 |
| Neutrals (`skill_neutral`) | 11/17 | 13/18 | +2 |
| Hurts (`skill_hurts`) | 0/17 | 0/18 | 0 |

**Verdict:** the **direction** of iter-3 holds (skills still lift quality, no hurts), but the **magnitude shrinks by ≈43%** (8.69 → 4.94) once the stale v2.0.0 cache is replaced with the live v0.0.3 marketplace. The previous +8.69pp was a real signal contaminated by a cache mismatch that produced a 3.75pp upward bias on the headline.

⚠️ **Read this carefully:** of the 5 lifts reported below, **only 2 actually involve skill-body consultation** (Read/Skill tool on the expected SKILL.md). The other 3 lifts are **file-access-driven** — the agent found the marketplace skill's *scripts* on disk and ran them without consulting the SKILL.md body. The marketplace being on disk (via `--add-dir <REPO>`) is the real lift mechanism for those 3, not the skill description or body. See "Lift mechanism" section below for the per-eval split.

## Motivation

iter-3 reported a mean +8.69pp overall lift across 18 evals. However, iter-3.1 discovered that the plugin cache at `~/.claude/plugins/cache/taches-principled-light/` was stale (v2.0.0 from 2026-06-21), containing 22 SKILL.md files with different names (`skill-authoring`, `mcp-expertise`, `ideation`, etc.) than the live v0.0.3 working tree (`crafting-skills`, `engineering-mcp`, `generating-ideas`, etc.).

This means iter-3 and iter-3.1 were measuring the **v2.0.0 cache's behavior**, not the v0.0.3 marketplace. iter-4 re-runs the experiment with a freshly-cleared cache to determine whether the +8.69pp lift holds.

## Configuration

- **N=18 evals** (Phase A added `rust-clippy` on top of the planned 17 — `rust-clippy` scored 0/0 in both configs and was neutral, no headline change)
- **Transcripts:** regenerated against fresh cache
- **Grader:** iter-3 `grader.py` reused (consultation assertion fix from commit b45c40a)
- **Timeout handling:** `timeout.json` marker written on `subprocess.TimeoutExpired` (iter-3.1 fix from commit b63b918). **Actual behavior:** grader runs on the truncated 300s/whatever-events transcript and scores whatever partial work is present. Timeouts do NOT auto-zero the score. See Caveats below.
- **Lift threshold:** ±5pp for `skill_neutral` verdict
- **Same-family bias mitigation:** iter-3 used heterogeneous judges (sonnet over haiku solver); we continue that here. **Wataoka 2024 same-family bias NOT yet mitigated** — see Recommendation #3.
- **Wall-clock:** 71 min vs PLAN budget 25-40 min. Overage driven by 4 timeout events (3 with-skill + 1 without-skill).

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

### Per-eval table

| Eval | Expected | IF Δ | GC Δ | Overall Δ | Verdict |
|------|----------|----:|----:|----------:|---------|
| lint-1 | marketplace-validator | +0.0 | +50.0 | +25.0 | `skill_lifts_quality` |
| lint-2 | marketplace-validator | +0.0 | +0.0 | +0.0 | `skill_neutral` |
| audit-1 | marketplace-health | +40.0 | +0.0 | +16.5 | `skill_lifts_quality` |
| audit-2 | marketplace-health | +0.0 | +0.0 | +0.0 | `skill_neutral` |
| ingest-1 | ingesting-skills | +0.0 | +0.0 | +0.0 | `skill_neutral` |
| ingest-2 | ingesting-skills | +0.0 | +0.0 | +0.0 | `skill_neutral` |
| release-1 | releasing-marketplace | +0.0 | +0.0 | +0.0 | `skill_neutral` |
| release-2 | releasing-marketplace | +30.0 | +0.0 | +15.0 | `skill_lifts_quality` |
| critic | general-critic | +0.0 | +0.0 | +0.0 | `skill_neutral` |
| research | deep-research | +0.0 | +0.0 | +0.0 | `skill_neutral` |
| craft-create | crafting-skills | +0.0 | +0.0 | +0.0 | `skill_neutral` |
| craft-review | crafting-skills | +0.0 | +0.0 | +0.0 | `skill_neutral` |
| eval-skill | evaluating-skills | +30.0 | +0.0 | +15.0 | `skill_lifts_quality` |
| plan-multi | plan-lifecycle | +0.0 | +0.0 | +0.0 | `skill_neutral` |
| task-small | task-lifecycle | +0.0 | +0.0 | +0.0 | `skill_neutral` |
| web-rust | web-search | +0.0 | +0.0 | +0.0 | `skill_neutral` |
| sec-audit | security | +35.0 | +0.0 | +17.5 | `skill_lifts_quality` |
| rust-clippy | rust | +0.0 | +0.0 | +0.0 | `skill_neutral` |

### Per-skill mean overall delta

| Skill | Mean Δ | Evals | Verdict |
|-------|-------:|------:|---------|
| security | +17.5 | 1 | lift (consultation-driven) |
| evaluating-skills | +15.0 | 1 | lift (consultation-driven) |
| marketplace-validator | +12.5 | 2 | lift (file-access-driven, 1/2 evals) |
| marketplace-health | +8.25 | 2 | lift (file-access-driven, 1/2 evals) |
| releasing-marketplace | +7.5 | 2 | lift (file-access-driven, 1/2 evals) |
| ingesting-skills | +0.0 | 2 | neutral |
| general-critic | +0.0 | 1 | neutral |
| deep-research | +0.0 | 1 | neutral (timeout in without_skill) |
| crafting-skills | +0.0 | 2 | neutral |
| plan-lifecycle | +0.0 | 1 | neutral |
| task-lifecycle | +0.0 | 1 | neutral |
| web-search | +0.0 | 1 | neutral |
| rust | +0.0 | 1 | neutral |

### Verdict distribution

- `skill_lifts_quality`: **5/18** (28%)
- `skill_neutral`: **13/18** (72%)
- `skill_hurts`: **0/18** (0%)

## Key patterns

### 1. Lift mechanism: only 2 of 5 lifts are consultation-driven

The grader's `consulted_<skill>` assertion tracks whether the agent read or invoked the expected SKILL.md. Per `grading_with_skill.json` evidence:

| Eval | Expected skill | Consulted? | Lift mechanism |
|------|----------------|------------|----------------|
| lint-1 | marketplace-validator | ❌ NOT consulted | **File access** — agent ran `python3 .agents/skills/marketplace-validator/scripts/validate.py` (found script on disk) |
| audit-1 | marketplace-health | ❌ NOT consulted | **File access** — agent ran `.agents/skills/marketplace-health/scripts/health.py` (found script on disk) |
| release-2 | releasing-marketplace | ❌ NOT consulted | **File access + git** — agent ran git commands, not the skill body |
| eval-skill | evaluating-skills | ✅ CONSULTED | **Skill body** — agent read `skills/evaluating-skills/SKILL.md` |
| sec-audit | security | ✅ CONSULTED | **Skill body** — agent invoked `taches-principled-light:security` via Skill tool |

**Only 2 of 5 lifts are skill-body consultation. The other 3 are file-access-driven** — the marketplace being on disk (via `--add-dir <REPO>`) is the real lift mechanism, not the skill description or body. This means the +4.94pp headline conflates two mechanisms:
- **File access lift** (~3 lifts, mostly local-meta skills with co-located scripts)
- **Skill-body lift** (~2 lifts, the workflow skills with structured content)

The marketplace still has a real positive effect, but the iter-4 number is **not pure skill-body lift**. For pure skill-body lift, the lower bound is closer to `(17.5 + 15) / 18 = 1.81pp` (the average of the 2 consultation-driven lifts only).

### 2. Local-meta skills dominate the file-access lifts

All 3 file-access lifts come from local-meta skills (marketplace-validator, marketplace-health, releasing-marketplace). These skills ship a `scripts/*.py` next to the SKILL.md, and the agent finds the script path via glob or directory listing without needing the body. This is a real and useful side effect of the colocated-scripts design.

### 3. Eight skills showed 0pp lift

`ingesting-skills`, `general-critic`, `deep-research`, `crafting-skills`, `plan-lifecycle`, `task-lifecycle`, `web-search`, `rust` — all zero. Two reasons emerge from inspecting the transcripts:

1. **Both configs score identically** (research, craft-create, craft-review, plan-multi, web-rust, rust-clippy): the agent invokes the marketplace skill **by name via slash_commands in both configs** (the H1 contamination documented in `SKILL-DISCOVERY-ARCHITECTURE.md` v1.4 — global plugin loading means the without_skill config also has the skill listing). Neither config gains marginal behavior from the SKILL.md body. The 4 deep-research invocations in the `research/without_skill` transcript produced the same 32.5 score as `with_skill`, confirming the body adds zero.
2. **Both configs score 0** (ingest-1, ingest-2, release-1, critic, task-small, lint-2): the agent fails the grader in both conditions, suggesting the eval utterance is **too vague for haiku to trigger the right behavior** without stronger skill activation. Note: `lint-2` and `critic` and `audit-2` (with-skill) and `research` (without-skill) timed out at 300s; partial work still scored 0/0 in these cases.

This is consistent with iter-3.1 H4: in 6/9 evals the agent did not consult any skill at all. The marketplace is not over-routing haiku to skill bodies in headless, single-utterance settings.

### 4. The +4.94pp is structurally sensitive to one eval

The `research/without_skill` config timed out at 300s, but the grader ran on the 4 deep-research invocations + 5-stage pipeline evidence already in the transcript and scored it 32.5 (the same as with_skill). This produced a 0 delta (neutral). Two scenarios:
- If the timeout had auto-zeroed the score (per the originally-stated convention), `research` would be a **+32.5 lift** → headline shifts to 6 lifts / 12 neutrals and mean overall delta to **+6.75pp** instead of +4.94pp.
- If `without_skill` had completed without timeout, the agent would likely have surfaced the disagreement assertion (per `research/with_skill` UNKNOWN verdict — see Caveats) and the delta could have been either still neutral or a *hurt*.

The +4.94pp headline is therefore sensitive to one timeout convention choice for one eval. The lower bound of the confidence interval, treating the 2-eval consultation-driven subset as the pure signal, is **+1.81pp**. The upper bound, treating all lifts at face value, is **+6.75pp**. Both are positive; both are within the N=1 noise floor (Yagubyan 2026: ±13.6%).

### 5. The +4.94pp survives pruning

Even after the 3.75pp cache correction, the +4.94pp mean overall lift is a positive signal. The 5 lifts in iter-4 are all from local-meta or well-defined workflow skills — there are no phantom lifts and no hurts. This is a more honest, conservative headline than iter-3.

## Verdict

**The corrected iter-4 headline is +4.94pp mean overall lift, with a structurally-bounded range of +1.81pp (consultation-driven only) to +6.75pp (all lifts, no timeout-penalty).** The marketplace is **safe to ship v0.0.3 as-is** — no skill changes needed, zero hurts, all lifts in the local-meta + well-defined workflow category, no phantom lifts.

However, the iter-4 number is **not pure skill-body lift**. Of 5 lifts, only 2 reflect actual SKILL.md consultation. The other 3 are file-access-driven (agent found the skill's colocated scripts via filesystem glob). To claim "skills lift quality by 5pp" in the future, we need either:

1. A harness that controls for `--add-dir` (e.g., remove the marketplace from disk to isolate the body consultation effect), or
2. An eval where the marketplace skill has no colocated scripts and the body is the only source of behavior.

Recommended actions:
1. **Release v0.0.3 as-is** — no skill changes needed.
2. **Document the cache workaround** in `AGENTS.md` and `README.md` so other marketplaces avoid the iter-3 trap.
3. **Plan iter-5 (REQUIRED, not optional)** — N=3 reliability study to measure the noise floor and confirm the +1.81pp consultation-driven lower bound is stable. Yagubyan 2026 shows ±13.6% flip rate for single trials; a 3-trial mean would tighten the CI enough to claim a publishable magnitude.
4. **Plan iter-6 (COMPLETE with proxy caveat)** — vendor-disjoint validation via glm-5.2 judge. **Outcome:** blocked by proxy architecture (haiku/sonnet/opus/nex-agi all silently map to MiniMax-M3; only glm-5.2 is vendor-disjoint and is rate-limited). Re-purposed as code-only lift decomposition (+7.5pp mean across 4 evals). See [`../iteration-6/REPORT.md`](../iteration-6/REPORT.md).
5. **Plan iter-7 (COMPLETE)** — 3-config lift disambiguation. **Outcome:** canonical headline is **+21.88pp total_lift** (4 lifts / 0 neutrals / 0 hurts) on 4-eval subset. See [`../iteration-7/REPORT.md`](../iteration-7/REPORT.md).

## Methodology notes

- The without_skill baseline is contaminated by global plugin loading (per SKILL-DISCOVERY-ARCHITECTURE.md v1.3): all installed plugins inject their skills into `slash_commands` regardless of cwd. Both with/without configs see the same marketplace skill listing.
- iter-4 measures the marginal lift of Read-driven skill consultation (with_skill: cwd=REPO, agent can `Read` SKILL.md files) over listing-driven discovery (without_skill: cwd=`/tmp/empty-claude-project`, agent has skill names in `slash_commands` but cannot `Read` the bodies).
- This matches the SkillRouter finding: descriptions alone (without bodies) lose 31-44pp routing accuracy at scale.

## Caveats

1. **N=1 per (eval, config)**: single-trial noise is high (Yagubyan 2026: ±13.6% flip rate). The +4.94pp headline has wide confidence intervals and is plausibly within the noise floor. **iter-5 N=11 study is deferred** (see iter-7 REPORT "iter-5 future work" for rationale).
2. **Solver/judge family**: haiku solver + sonnet judge is heterogeneous. Wataoka 2024 shows LLM-judge same-family bias can swing scores by single-digit pp. **iter-6 vendor-disjoint validation: blocked by proxy architecture** (haiku/sonnet/opus/nex-agi all silently map to MiniMax-M3; only glm-5.2 is vendor-disjoint and is rate-limited). See [`../iteration-6/REPORT.md`](../iteration-6/REPORT.md).
3. **Timeouts**: 4/36 runs hit the 300s cap (lint-2, audit-2, critic with-skill; research without-skill). The grader runs on the partial transcript and scores whatever work is present (does NOT auto-zero). For `research/without_skill` this produced 32.5 pts, equal to `with_skill`, which masks a potential +32.5 lift in the headline. See "Key pattern #4" above for the sensitivity analysis.
4. **Cache freshness single-shot**: iter-4 measures one snapshot of the cache. iter-5 would re-run to confirm +4.94pp is stable; deferred.
5. **UNKNOWN verdict**: 1 UNKNOWN judge verdict emitted (research/with_skill, `surfaced_disagreement` assertion — truncated transcript, no evidence to grade). Treated as FAIL per the iter-3 `evaluating-skills` convention. Logged in `unknowns.md`.
6. **Lift mechanism confound**: 3 of 5 lifts (lint-1, audit-1, release-2) are file-access-driven, not skill-body consultation. The agent ran the marketplace skill's colocated scripts without reading the SKILL.md. The +4.94pp headline therefore measures "(file access to marketplace) + (skill body consultation)" combined. Pure skill-body lift, isolated, is closer to **+1.81pp** (average of the 2 consultation-driven lifts only). **iter-7 disambiguates this**: filesystem_access_lift = +13.75pp, consultation_lift = +8.12pp (noisy), total_lift = +21.88pp.
7. **Contaminated baseline**: the without_skill baseline still has all marketplace skills in slash_commands (global plugin loading). The iter-4 number is a **marginal** lift over an already-contaminated baseline. **iter-7 resolves this** via `--disable-slash-commands` for the true no-plugin baseline.
8. **Cross-iteration noise check (added 2026-06-23)**: iter-7 cross-checked iter-4 grading on bit-for-bit identical transcripts (md5 verified). Result: 3 of 4 evals (eval-skill, lint-1, release-2) produced identical grading across iter-4 and iter-7. **sec-audit without_skill graded 15.0 in iter-4 but 32.5 in iter-7 — a +17.5pp swing on the same input.** This proves the grader has non-deterministic noise on at least one assertion (model-judge based). The sec-audit lift magnitude in this REPORT (+17.5pp) is one realization; the expected value is bracketed between +0 and +35 (the IF-delta range). The lift DIRECTION (positive) is robust. See `../iteration-7/REPORT.md` "Caveats #3" for the full analysis. iter-5 (N=11) is deferred (not blocking); iter-6 (vendor-disjoint judge) is structurally blocked on this proxy.
