# iter-5/6/7 Plan — Revised 2026-06-23 (with baseline contamination revision)

**Status:** Research-informed design refresh. Supersedes the iter-4 PLAN.md
recommendations for iter-5/6/7. See
[`iteration-4/RESEARCH-FINDINGS-iter5-design.md`](RESEARCH-FINDINGS-iter5-design.md)
for the source synthesis and the **Baseline Contamination** finding that
motivated the iter-7 redesign.

---

## Why This Revision

iter-4's CHANGELOG marked iter-5 as N=3 reliability and iter-6 as sonnet-on-sonnet
homogeneous. **Both are methodologically wrong** per primary sources:

- **Yagubyan 2026** (arxiv:2606.13685): N=11 trials are required for 95% majority-vote
  recovery of the reference verdict. N=3 is in the high-noise regime.
- **Wataoka 2024** (arxiv:2410.21819) + **CoEval 2026** (arxiv:2606.03650):
  homogeneous judges inflate scores via self-preference bias. The rigorous design
  is **vendor-disjoint** judges (drop any judge sharing the model's vendor), not
  homogeneous.
- **SkillRouter 2026** (arxiv:2603.22455v4): full skill text is a critical routing
  signal (31-44pp routing drop when hidden). This validates iter-4's finding that
  the body matters, but also implies the marketplace being on disk (via
  `--add-dir <REPO>`) is a confound the harness does not isolate.

**iter-7 was not in the original plan** but the harness-patch design becomes
methodologically essential given the file-access vs skill-body confound iter-4
uncovered — and the **2026-06-23 baseline contamination discovery** (see
RESEARCH-FINDINGS) shows iter-4's `without_skill` baseline is contaminated
by the auto-loaded plugin, so iter-7 needs a true baseline via
`--disable-slash-commands`.

---

## iter-5: N=11 Reliability Study (REVISED from N=3)

**Goal:** Tighten the +4.94pp headline confidence interval using majority-vote
aggregation across N=11 trials per (eval, config) cell.

**Per Yagubyan 2026:** N=11 trials needed for 95% majority-vote recovery of
reference verdict (N=15 for high-variance). N=3 sits well inside the noise floor.

**Eval scope decision:** Full 18 evals × 11 × 2 = 396 runs ≈ 33h is impractical
for a single session. **Compromise: 4-eval subset × 11 × 2 = 88 runs ≈ 7h.**

Eval selection: 2 consultation-driven + 2 file-access-driven from iter-4.
| Eval | iter-4 lift | Mechanism |
|------|-------------|-----------|
| eval-skill | +15.0 | consultation |
| sec-audit | +17.5 | consultation |
| lint-1 | +25.0 | file-access |
| release-2 | +15.0 | file-access |

This subset lets us measure both lift mechanisms with adequate power.

**Aggregation:** Per Yagubyan 2026 reliability-curve methodology — majority vote
across 11 trials, report per-eval flip rate, per-config mean ± 95% CI, headline
consultation-driven + file-access-driven lift with CIs.

**If N=11 is infeasible at session time:** mark explicitly as "below Yagubyan
2026 threshold; do not interpret magnitude as effect size." Run N=3 anyway and
flag the limitation in REPORT.

**Deferral path:** If the 7h wall is unacceptable, defer iter-5 to a background
session. The marketplace is ship-ready at v0.0.3 regardless (per iter-4 verdict).

---

## iter-6: Vendor-Disjoint Judges (REVISED from sonnet-on-sonnet)

**Goal:** Rule out same-family bias in iter-4's grading by switching the judge
to a non-Anthropic model.

**Design:** haiku solver (Anthropic) + **glm-5.2** judge (non-Anthropic, available
on the same `100.80.231.128:3456` proxy). This is vendor-disjoint per the
CoEval 2026 definition.

**Per Wataoka 2024:** GPT-4 has significant self-preference bias. Mechanism is
**lower-perplexity preference** — judges prefer outputs more familiar to them.
Same-family bias is real but moderate: arxiv:2606.19544 (Norman/Rivera/Hughes
Berkeley, 17 Jun 2026) reports κ deflation 33.8-41.2pp is universal across
21 judges × 9 providers, but test-retest reliability >0.943; the
"consistency-bias paradox" is that test-retest ≠ correctness. Claude Opus 4.6
achieves κ=0.720 on JudgeBench. Cross-provider κ=0.51 (Yagubyan 2026).

**Why not sonnet-on-sonnet:** The original iter-4 CHANGELOG suggested this.
**Wrong direction** — it would inflate, not deflate, the headline. Heterogeneous
grading is the more conservative choice; vendor-disjoint is the rigorous
defense.

**Wall time:** 18 × 2 = 36 runs ≈ 1.2h.

**Comparison vs iter-4:** the delta between (sonnet judge over haiku) and
(glm-5.2 judge over haiku) isolates same-family bias contribution.

**Decision rule:**
- iter-6 mean within ±1pp of iter-4: same-family bias is negligible. iter-4 robust.
- iter-6 mean < iter-4 by >2pp: same-family bias inflates iter-4 by 2pp+. iter-4
  still positive (lower bound) but the corrected headline is closer to iter-6.

**Secondary option:** if glm-5.2 is unavailable, use gemini-3.1-pro-preview
(also non-Anthropic, also available via proxy). Either works.

---

## iter-7: Harness Fix to Isolate Consultation vs Filesystem Lift (REVISED 2026-06-23)

**Goal:** Disambiguate consultation-driven lift from file-access-driven lift
by running THREE configs: `baseline` (no plugin), `plugin_only` (plugin
auto-loaded, no filesystem), `plugin_with_add_dir` (plugin + filesystem).

**CRITICAL REVISION 2026-06-23:** while designing iter-7, I discovered that
**iter-4's `without_skill` baseline is contaminated by the auto-loaded
marketplace plugin.** Searching transcripts across all 18 evals showed that
the agent in the `without_skill` config invoked `/crafting-skills` (a
marketplace skill slash command) in event 4 of eval-eval-skill, and similar
slash-command references appear in all 18 evals for both configs. The
marketplace plugin auto-loads from `~/.claude/plugins/cache/`, so the
`--add-dir` flag only controls filesystem access — not plugin loading.

Therefore **iter-4's +4.94pp is the filesystem access lift, NOT the total
lift.** The pure consultation lift (baseline → plugin_only) is UNMEASURED.
The true total lift (baseline → plugin_with_add_dir) is at LEAST +4.94pp
(lower bound), likely more.

**Why this matters:** v0.0.3 is even more positive than iter-4 measured.
But the headline number needs revision: the marketplace is doing two things
(consultation + filesystem), and the iter-4 number only measures one
(filesystem).

**Design:** patch `run_iteration_4.py` to add 3 configs:
- **`baseline`** (NEW): `--disable-slash-commands --add-dir /tmp/empty-claude-project`
  → no plugin, no skills, no slash commands
- **`plugin_only`** (renamed from `without_skill`): `--add-dir /tmp/empty-claude-project`
  → plugin auto-loaded, slash commands work, no filesystem access
- **`plugin_with_add_dir`** (renamed from `with_skill`): `--add-dir <REPO>`
  → plugin auto-loaded + filesystem access to marketplace (current iter-4 `with_skill`)

The `--disable-slash-commands` flag ("Disable all skills") is provided by
the claude CLI specifically for this use case. The `--bare` flag does NOT
work (it still says "Skills still resolve via /skill-name").

**Eval scope:** 4-eval subset matching iter-5:
- eval-skill (consultation-driven in iter-4)
- sec-audit (consultation-driven in iter-4)
- lint-1 (file-access-driven in iter-4)
- release-2 (file-access-driven in iter-4)

**Wall time:** 4 × 3 configs = 12 runs ≈ 30 min.

**Three lifts computed:**

| Lift | Mechanism | Iter-4 analog |
|------|-----------|---------------|
| `baseline → plugin_only` | Pure consultation (skill body via slash cmd) | **UNMEASURED in iter-4** |
| `plugin_only → plugin_with_add_dir` | Pure filesystem access | **+4.94pp (iter-4 headline)** |
| `baseline → plugin_with_add_dir` | Total (consultation + filesystem) | **Lower bound = +4.94pp** |

**Disambiguation matrix (predicted):**

| Eval type | `baseline` | `plugin_only` | `plugin_with_add_dir` |
|-----------|-----------|---------------|-----------------------|
| Consultation-driven (eval-skill, sec-audit) | low score | **+lift** (skill body via slash cmd) | **+lift** (similar) |
| File-access-driven (lint-1, release-2) | low score | low (no scripts on disk) | **+lift** (scripts runnable) |

**Predicted outcomes:**
- `plugin_only → plugin_with_add_dir` lift on consultation evals: ~1-2pp
- `plugin_only → plugin_with_add_dir` lift on file-access evals: ~5-10pp
- `baseline → plugin_only` lift on consultation evals: ~5-10pp (iter-4 gap!)
- `baseline → plugin_only` lift on file-access evals: ~0-1pp (slash cmd alone doesn't unlock scripts)

**Decision rule:**
- If `baseline → plugin_only` lift on consultation evals is ≥5pp, iter-4's "+4.94pp lower bound" is correct and the true total lift is significantly higher.
- If `plugin_only → plugin_with_add_dir` lift on file-access evals is ≥5pp, file access is a meaningful driver.
- Both being true means the marketplace does two things: teaching (consultation) and tool-giving (filesystem).

---

## Order of Operations

| Order | Iteration | Wall | Rationale |
|-------|-----------|------|-----------|
| 1 | **iter-7** (harness fix, 4-eval subset × 3 configs) | 30 min | Cheapest, isolates the iter-4 confound. Most informative per minute. |
| 2 | **iter-6** (vendor-disjoint, 18 evals × 2 configs) | 1.2h | Rules out same-family bias. Second-most informative. |
| 3 | **iter-5** (N=11 reliability, 4-eval subset × 11 × 2) | 7h (deferrable) | Tightens magnitude CI. Largest cost; can be background. |
| 4 | Release tag at HEAD | 5 min | Admin. |
| 5 | Self-critic + self-review | 15 min | Final pass. |

**Total minimum session cost** (iter-7 + iter-6 only): ~1.8h.
**Total with iter-5:** ~9h. Recommend backgrounding iter-5 if pursued.

---

## Release Decision Rule

After iter-5/6/7, decide whether to retag v0.0.3:

| Scenario | Action |
|----------|--------|
| iter-5/6/7 confirm iter-4 (within 1pp, same lift pattern) | **No retag.** v0.0.3 stays as is. Add iter-5/6/7 REPORTs as "v0.0.3 confirmation" docs. |
| iter-5/6/7 show >2pp correction (e.g., same-family bias inflates by 2pp) | **Bump to v0.0.4** with corrected headline. Use `releasing-marketplace` skill. |
| iter-5/6/7 show a hurt (negative lift) that iter-4 missed | **BLOCK release.** Investigate. Likely a confound. |

Default: v0.0.3 is ship-ready as-is per iter-4. iter-5/6/7 are *measurement
refinements*, not blocking gates.

---

*This plan replaces the iter-4 PLAN.md "iter-5/6/7" section. iter-4 itself
remains canonical as the v0.0.3 behavioral evidence.*
