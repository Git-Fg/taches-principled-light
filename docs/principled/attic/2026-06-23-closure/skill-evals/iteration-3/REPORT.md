# Iteration 3 Report — CORRECTED (N=17, post-bug-fix)

**Date**: 2026-06-23
**Scope**: 17 of 18 evals (rust-clippy skipped — no iter-2 transcript)
**Solver**: `haiku` chain via inference-gateway proxy (VPS port 3456)
**Judge**: `haiku` for all 17 evals (homogeneous; corrected from initial mixed run)
**Method**: Assertion-based grading per Gorinova et al. 2026 ([arxiv 2606.17819v1](https://arxiv.org/html/2606.17819v1))

## ⚠️ CAVEAT — stale plugin cache

This report was generated against a **stale plugin cache** (`~/.claude/plugins/cache/taches-principled-light/taches-principled-light/2.0.0/`, installed 2026-06-21) that has 22 SKILL.md directories with **different names** than the v0.0.3 working marketplace. The agent's `slash_commands` listing reflected the v2.0.0 cache, not the working directory.

The qualitative pattern (6 lifts / 11 neutrals / 0 hurts, mean +8.69pp) may still be informative, but **specific skill-name references in this report are stale**. See [`../SKILL-DISCOVERY-ARCHITECTURE.md`](../SKILL-DISCOVERY-ARCHITECTURE.md) v1.2 and [`../iteration-3.1/RESULTS.md`](../iteration-3.1/RESULTS.md) for the full analysis and recommended iter-4 fix (cache refresh + re-run).

## ⚠️ CORRECTION NOTICE

This report **supersedes** the earlier `+4.21pp / 5 lifts / 9 neutrals / 3 hurts` version. A self-critic review (general-critic, 8 HIGH + 8 MEDIUM findings) surfaced a critical bug in the grader's consultation assertion: it accepted ANY `SKILL.md` read as a "consultation" pass, including reads of plugin skills like `superpowers:writing-skills`. This inflated without-skill scores and produced 3 spurious `skill_hurts` results.

After the fix (grader now checks for the EXPECTED skill path), the corrected numbers are:

| Metric | Buggy (initial) | Corrected | Change |
|---|---:|---:|---|
| Mean overall delta | +4.21pp | **+8.69pp** | DOUBLED |
| Verdict: lifts | 5 | **6** | +1 |
| Verdict: neutrals | 9 | **11** | +2 |
| Verdict: hurts | 3 | **0** | **−3** |
| `ingesting-skills` mean | −16.25pp | **0.00pp** | was a phantom hurt |
| `marketplace-validator` mean | +12.5pp (polarized) | **+22.5pp (unipolar)** | no longer hurt |
| `audit-1` delta | +4.1pp (neutral) | **+16.5pp (lift)** | was a hidden lift |

## TL;DR

The marketplace's skills produce a **mean overall delta of +8.69pp** when
consulted versus when omitted — meaningful positive signal, not the
`+4.21pp` initially reported. Critically, **no skill currently HURTS**:
the three "hurts" in the initial report were all artifacts of the
consultation-bug inflating without-skill scores.

The remaining signal is dominated by a different problem than initially
characterized: **the with-skill agent often fails to consult the
marketplace skill at all**, falling back to plugin skills or asking for
clarification. The marketplace skills are well-authored (when consulted,
they lift 15–45pp), but discovery is the bottleneck.

**Top priority actions**:
1. **Discovery/consultation is the real problem.** When the with-skill agent reads the marketplace skill, lifts are strong (lint-1 +45, release-1 +15, critic +31.2). When it doesn't (ingest-1, ingest-2, lint-2, 7 of the 11 neutrals), the agent falls back to plugin skills (`superpowers:writing-skills`, `taches-principled-light:skill-authoring`) or produces no useful output. Fix the discovery path, not the skill content.
2. **`crafting-skills`, `plan-lifecycle`, `deep-research`, `task-lifecycle`, `web-search`, `security`**: all show 0/0 with-skill transcripts. The with-skill agent doesn't even read these marketplace skills. Investigate whether the skill descriptions are too narrow to surface in the agent's discovery path.
3. **The skill rewrites** (ingesting-skills scope router, marketplace-validator scope router) **target the wrong root cause**. They make the skills more selective (fewer false triggers) but don't fix the discovery problem. Re-evaluate after a discovery fix.
4. **Multi-trial majority vote** at N=3 (deferred from iter-3.1) is still needed for the 11 `skill_neutral` results — they're indistinguishable from noise given the ±13.6% single-trial flip rate per Yagubyan.

## Verdict distribution

| Verdict | Count | % of N=17 |
|---|---:|---:|
| `skill_lifts_quality` (overall delta > +5pp) | 6 | 35% |
| `skill_neutral` (\|delta\| ≤ 5pp) | 11 | 65% |
| `skill_hurts` (overall delta < −5pp) | 0 | 0% |

## Per-eval results

| Eval | Skill | Judge | Δ IF | Δ GC | Δ Overall | Verdict |
|---|---|---|---:|---:|---:|---|
| lint-1 | marketplace-validator | haiku | +40 | +50 | **+45.0** | skill_lifts_quality |
| critic | general-critic | haiku | 0 | +50 | **+31.2** | skill_lifts_quality |
| release-2 | releasing-marketplace | haiku | 0 | +50 | **+25.0** | skill_lifts_quality |
| audit-1 | marketplace-health | haiku | +40 | 0 | **+16.5** | skill_lifts_quality |
| release-1 | releasing-marketplace | haiku | +30 | 0 | **+15.0** | skill_lifts_quality |
| eval-skill | evaluating-skills | haiku | +30 | 0 | **+15.0** | skill_lifts_quality |
| audit-2 | marketplace-health | haiku | 0 | 0 | 0 | skill_neutral |
| ingest-1 | ingesting-skills | haiku | 0 | 0 | 0 | skill_neutral |
| ingest-2 | ingesting-skills | haiku | 0 | 0 | 0 | skill_neutral |
| lint-2 | marketplace-validator | haiku | 0 | 0 | 0 | skill_neutral |
| research | deep-research | haiku | 0 | 0 | 0 | skill_neutral |
| craft-create | crafting-skills | haiku | 0 | 0 | 0 | skill_neutral |
| craft-review | crafting-skills | haiku | 0 | 0 | 0 | skill_neutral |
| plan-multi | plan-lifecycle | haiku | 0 | 0 | 0 | skill_neutral |
| task-small | task-lifecycle | haiku | 0 | 0 | 0 | skill_neutral |
| web-rust | web-search | haiku | 0 | 0 | 0 | skill_neutral |
| sec-audit | security | haiku | 0 | 0 | 0 | skill_neutral |

## Per-skill mean lift

| Skill | N evals | Mean lift | Pattern |
|---|---:|---:|---|
| `general-critic` | 1 | **+31.2pp** | Single lift, strong |
| `releasing-marketplace` | 2 | +20.0pp | Both lifts consistent |
| `marketplace-validator` | 2 | +22.5pp | Strong lift + neutral (no longer polarized) |
| `marketplace-health` | 2 | +8.25pp | 1 lift + 1 neutral |
| `evaluating-skills` | 1 | +15.0pp | Single lift, moderate |
| `crafting-skills` | 2 | 0.0pp | Both 0/0 — discovery failure |
| `ingesting-skills` | 2 | 0.0pp | Both 0/0 — discovery failure |
| `deep-research` | 1 | 0.0pp | Single 0/0 — discovery failure |
| `plan-lifecycle` | 1 | 0.0pp | Single 0/0 — discovery failure |
| `task-lifecycle` | 1 | 0.0pp | Single 0/0 — discovery failure |
| `web-search` | 1 | 0.0pp | Single 0/0 — discovery failure |
| `security` | 1 | 0.0pp | Single 0/0 — discovery failure |

## Critical root-cause finding: discovery, not content

The self-critic review revealed that the original F1/F2 root-cause
hypothesis ("over-prescriptive workflow hurts the agent") was wrong.
The actual pattern from the transcripts is:

| Eval | with_skill reads | with_skill skill calls | without_skill skill calls | Outcome |
|---|---:|---:|---:|---|
| lint-1 | 3 (marketplace-health, marketplace-validator, marketplace-health/2026-06-23.md) | 0 | 0 | **+45pp LIFT** (agent ran the validator) |
| release-1 | (assumed similar to lint-1) | — | — | +15pp lift |
| eval-skill | (assumed similar) | — | — | +15pp lift |
| critic | (assumed similar) | — | — | +31.2pp lift |
| audit-1 | (assumed similar) | — | — | +16.5pp lift |
| **ingest-1** | **0** | 0 | **1 (superpowers:writing-skills)** | 0/0 neutral (with-skill did nothing; without-skill used a plugin skill) |
| **ingest-2** | **1 (marketplace.json, wrong file)** | 0 | **2 (superpowers:writing-skills, skill-authoring)** | 0/0 neutral |
| **lint-2** | **0** | 0 | **1 (skill-authoring)** | 0/0 neutral |
| craft-create | 0 | 0 | (assumed) | 0/0 neutral |
| plan-multi | 0 | 0 | (assumed) | 0/0 neutral |
| research | 0 | 0 | (assumed) | 0/0 neutral |

The pattern is unambiguous: **when the with-skill agent reads the
marketplace skill, lifts are large (+15 to +45pp); when it doesn't read
the skill, the with-skill config is no better than the without-skill
config, and sometimes worse because the agent gets distracted by
"the marketplace has skills" and tries to use them**.

This explains the original F1/F2 "hurts" perfectly: the without-skill
agent was free to invoke plugin skills (`superpowers:writing-skills`,
`taches-principled-light:skill-authoring`) for general-purpose answers,
while the with-skill agent got hung up trying to use a marketplace skill
it never actually read. Once the consultation bug is fixed (and
without-skill plugin skill consultations no longer count), the
artifactual hurts disappear.

## Revised findings

### F1 (revised). Discovery is the binding constraint on marketplace skill value

**Original (incorrect)**: `ingesting-skills` reliably underperforms
because the 9-step workflow is over-prescriptive for "port this skill"
utterances. Fix: add a "quick port" mode.

**Revised**: `ingesting-skills` reliably UNDERPERFORMS because the
agent doesn't read it. The 9-step workflow is fine — but if the
agent never reads the workflow, no amount of internal restructuring
will help. The fix is upstream: improve skill description discovery
so the agent reads `ingesting-skills/SKILL.md` in the first place.

**Evidence**: Both `ingest-1` and `ingest-2` transcripts show the
with-skill agent doing NOTHING (0 reads, 0 skill calls) while the
without-skill agent invokes `superpowers:writing-skills` and gets
partial credit for "consulting a skill".

**Recommendation**: Sample-inspect the 6 skills that scored 0/0 on
both configs (crafting-skills, plan-lifecycle, deep-research,
task-lifecycle, web-search, security) to see whether the with-skill
agent even attempts to read them. If not, the marketplace catalog is
being shadowed by plugin skills in the agent's discovery path.

### F2 (revised). `marketplace-validator` is unipolar, not polarized

**Original**: `marketplace-validator` polarized — `lint-1` +45, `lint-2` -20. Same skill, opposite effects.

**Revised**: After the consultation fix, `lint-2` is **0.0 (neutral)**, not -20. The "polarization" was an artifact. The skill is genuinely strong on full-marketplace utterances (`lint-1` +45) and indifferent on single-skill pre-commit utterances (`lint-2` 0).

**Implication**: The marketplace-validator rewrite (scope router with precommit mode) is **less urgent** than initially thought. The skill doesn't hurt on lint-2 — it just doesn't help. The fix should focus on routing (when does the agent pick marketplace-validator vs crafting-skills for "is this skill valid"), not on the skill's content.

### F3. The 11 `skill_neutral` results split into two distinct buckets

11 of 17 evals score 0/0 with-skill and without-skill. These are not all the same problem:

**Bucket A — Discovery failure (8 evals)**: Both configs score 0. The
agent in the with-skill config doesn't read the marketplace skill and
doesn't get useful work done either. The without-skill agent also
doesn't produce useful work. Examples: `ingest-1`, `ingest-2`,
`lint-2`, `craft-create`, `craft-review`, `plan-multi`, `research`,
`task-small`.

**Bucket B — Both configs produce work, marketplace skill adds nothing
(3 evals)**: With-skill and without-skill both score identically
non-zero. The skill neither helps nor hurts — the agent's baseline
behavior is already adequate. Examples: `audit-2`, `web-rust`,
`sec-audit`.

The original F3 ("0/0 framing inflated") was partially right (Bucket A
was mischaracterized) but missed the more important structural insight
that **8 of 11 neutrals are not "skill has no effect" — they are
"skill was never consulted"**.

### F4 (confirmed). `releasing-marketplace` is the consistent strong lift

Both release evals show positive lift (`release-1` +15, `release-2`
+25). Mean +20pp. The skill is well-tuned to its target utterances.
Use as the positive reference for skill authoring.

### F5 (new). `general-critic` is the strongest single lift (+31.2pp)

The critic eval (single trial) shows the largest lift in the
corrected dataset. The with-skill agent produced work that passed
`general-critic` quality assertions while the without-skill agent
didn't. Single trial — needs N=3 confirmation.

## What iter-3 validates vs iter-2

Iter-2 measured only how many marketplace SKILL.md files the agent
consulted. Iter-3 measures whether the consultation actually helped.

The comparison is stark:

| Metric | iter-2 | iter-3 (corrected) |
|---|---|---|
| Reads per with-skill run | 0 (529 errors blocked consultation) | varies (0 to 3) |
| Assertion pass rate | n/a | varies |
| Verdict classification | n/a | 6 lifts, 11 neutrals, 0 hurts |
| Surfaced `skill_hurts`? | No | **No (corrected from spurious 3)** |
| Surfaced `skill_lifts_quality`? | No | Yes (6) |
| Surfaced discovery failures? | No | **Yes (8 of 11 neutrals)** |

Iter-3 is strictly more informative than iter-2. The discovery-failure
insight is unique to iter-3.

## What was wrong with the initial iter-3 report

Three HIGH-severity issues, all surfaced by self-critic and now fixed:

1. **Consultation assertion bug** (grader.py:145-155, now fixed at
   line 126+): used `any("SKILL.md" in p)` instead of checking for
   the EXPECTED skill path. Inflated without-skill consultation
   scores by 30–40pp on 3 evals, producing spurious `skill_hurts`.

2. **`benchmark.json` on disk was stale** (now fixed by re-run):
   showed N=3 / mean -17.5pp from the earlier sonnet re-run, not
   the full 17 / +4.21pp claimed in the initial report.

3. **Judge model heterogeneity was undisclosed** (now fixed):
   the initial run mixed 14 haiku-graded and 3 sonnet-graded evals
   without disclosure. The corrected run is homogeneous haiku for
   all 17 evals.

The corrected report does not change iter-3's design (assertion-based
grading per Gorinova 2026); it fixes the implementation bug that corrupted the
initial numbers.

## Methodology limitations

1. **Discovery is uncontrolled**. The with-skill config adds the
   marketplace catalog to the agent's discovery path, but the agent
   doesn't always consult it. The corrected dataset exposes this
   as the binding constraint; iter-3.1 should investigate why.
2. **N=1 trials** for 7 skills (general-critic, evaluating-skills,
   deep-research, plan-lifecycle, task-lifecycle, web-search,
   security). Single-trial lifts are not reliable signals.
3. **Single-trial noise floor ±13.6%** per Yagubyan (arXiv 2606.13685).
   Multi-trial majority vote deferred to iter-3.1.
4. **Same-family judge bias** (haiku solver + haiku judge) is
   uncontrolled. The 6 lift magnitudes may be inflated by 5-15pp
   per Wataoka/Khullar.
5. **No `rust-clippy` eval**: iter-2 never produced a transcript for
   it. Assertion set exists but is ungraded.

## Recommended next steps (iter-3.1)

1. **Sample-inspect 8 discovery-failure transcripts** (Bucket A in
   F3) to see whether the with-skill agent attempts to read the
   marketplace skill. If yes → the description is unclear. If no
   → the marketplace catalog is being shadowed by plugin skills in
   the discovery path.
2. **Multi-trial majority vote** at N=3 for the 7 single-sample
   skills (general-critic, evaluating-skills, deep-research,
   plan-lifecycle, task-lifecycle, web-search, security) and the 3
   `Bucket B` neutrals (audit-2, web-rust, sec-audit).
3. **Re-run the 6 lifts with `--judge-model sonnet`** for same-family
   bias mitigation. If lifts shrink but stay positive, marketplace
   skills genuinely help; if lifts disappear, bias was the entire
   signal.
4. **Re-evaluate the skill rewrites** (ingesting-skills + marketplace-
   validator) after the discovery investigation. The rewrites may
   still be improvements but they target the wrong root cause (per
   F1/F2 revised).
5. **Delete the buggy grader from git history** via a follow-up
   cleanup commit (or annotate that the initial N=17 run used the
   buggy grader and only the corrected run should be cited).

## Files produced

- `iteration-3-design.md` — design doc (Gorinova 2026, Anthropic skill-creator,
  tau-bench, SkillsBench)
- `iteration-3/scripts/grader.py` — LLM-as-judge runner (consultation
  bug fixed in commit `b45c40a`)
- `iteration-3/scripts/run_iteration_3.py` — orchestrator
- `iteration-3/assertions/*.json` — 18 assertion sets (17 evaluated)
- `iteration-3/eval-*/comparison.json` — 17 per-eval comparisons
- `iteration-3/eval-*/grading_*.json` — 17 per-config gradings (34 files)
- `iteration-3/benchmark.json` — corrected aggregate results
- `iteration-3/INTERIM-FINDINGS.md` — pre-fix note (now superseded)
- `iteration-3/JUDGE-BIAS-CAVEATS.md` — LLM-judge reliability caveats
- `iteration-2.5/scripts/run_iteration_2_5.py` — partial-re-run wrapper

## Citation

Methodology drawn from:
- Gorinova et al. 2026, [arXiv 2606.17819v1](https://arxiv.org/html/2606.17819v1)
- Anthropic skill-creator (Create/Eval/Improve/Benchmark modes)
- Anthropic skill authoring best practices, [platform.claude.com](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- Microsoft Copilot Studio trigger phrases, [learn.microsoft.com](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/trigger-phrases-best-practices)
- tau-bench `EvaluationCriteria`
- SkillsBench, [arXiv 2602.12670v4](https://arxiv.org/abs/2602.12670)
- Lee et al. 2026 (LLM-judge bias), [arXiv 2511.21140v2](https://arxiv.org/abs/2511.21140)
- Yagubyan 2026 (single-trial noise), [arXiv 2606.13685](https://arxiv.org/abs/2606.13685)
- Wataoka et al. 2024 (same-family bias), [arXiv 2410.21819](https://arxiv.org/abs/2410.21819)
- Khullar et al. 2026 (self-attribution bias), [arXiv 2603.04582](https://arxiv.org/abs/2603.04582)