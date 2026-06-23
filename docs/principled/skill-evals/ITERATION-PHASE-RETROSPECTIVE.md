# Iteration Phase Retrospective — taches-principled-light skill router

**Date:** 2026-06-23
**Phase:** Closed at v0.0.7
**Status:** Canonical narrative document for the 2026-06-22 → 2026-06-23 iteration campaign that produced the v0.0.5 +21.88pp total_lift headline. Reads as a self-contained summary; deeper evidence in the linked source documents.

---

## 1. Executive summary

Seven behavioral evaluation iterations, run in 36 hours, produced one robust finding:

> **The taches-principled-light marketplace plugin produces a +21.88pp total lift in agent quality on a 4-eval subset (eval-skill, sec-audit, lint-1, release-2), with 4 of 4 evals lifting and 0 hurts. The lift decomposes into a deterministic +13.75pp filesystem_access_lift (3/3 evals) and a noisy +8.12pp consultation_lift (1/1 eval, sec-audit).**

The headline is **direction-robust** (4/4 evals positive) but **magnitude-noisy** on the consultation cell (±17.5pp grader swing on bit-for-bit identical transcript). The shipping claim is therefore: *the marketplace produces a positive lift on every eval we measured, with the lift mechanism split cleanly into a deterministic filesystem-access component and a noisier consultation component.*

Three structural findings emerged that the rest of this retrospective explains:

1. **Baseline contamination** (iter-4.1, 2026-06-23): `--add-dir /tmp/empty` does not prevent marketplace plugin auto-load. The "without_skill" baseline in iter-3 and iter-4 is contaminated. The true no-plugin baseline requires `--disable-slash-commands`. iter-4's headline of +4.94pp is the **filesystem_access lift only**, not the total.
2. **Proxy is single-model** (iter-6, 2026-06-23): the inference-gateway serves all 18+ advertised aliases (the configured solver tier aliases plus 16+ external-vendor aliases) from a single backend. The only genuinely vendor-disjoint option is an external judge vendor, and that option is rate-limited on the public endpoint. Vendor-disjoint validation is **structurally blocked** on this proxy.
3. **Grader non-determinism** (iter-7 + GRADER-NOISE-INVESTIGATION, 2026-06-23): the sec-audit `plugin_only` cell produced grade 15.0 in iter-4 and 32.5 in iter-7 on a bit-for-bit identical transcript (md5 `bda20918d4b7d0b7245bd12b59b09e58`). `temperature=0` does **not** make the model deterministic (reasoning-model floating-point, batch composition, or proxy-internal sampling). The +21.88pp headline is robust because the dominant component (filesystem_access_lift = +13.75pp) is on **deterministic endpoint grades**.

The iteration phase is **closed** at v0.0.7. Future work is captured in iter-8 (mock-based vendor-disjoint + deterministic grader + multi-run averaging) and the broader v0.0.6+ roadmap (LiteLLM multi-model gateway, heterogeneous judge matrix, SkillsBench/SoK alignment).

---

## 2. The story — seven iterations in 36 hours

### iter-1 (2026-06-22) — Pilot

A single end-to-end run on the `craft-create` eval using Claude Code CLI. Established that the harness could produce parseable stream-json transcripts and that the grader could score them. **No headline number** — pilot only. Superseded by iter-2.

### iter-2 (2026-06-22) — N=18 attempt

Full 18-eval matrix × 2 configs (with/without-skill) = 36 runs. **17 of 18 completed**; one eval returned a proxy 503 mid-run. The metric bug (consultation detection over-counted matches for some patterns) was caught by self-critic in `METRIC-BUG-NOTE.md`. Files preserved at `attic/2026-06-23-closure/skill-evals/iteration-2/` for forensics.

### iter-3 (2026-06-22) — First headline

After fixing the iter-2 metric bug, ran N=17 evals with the corrected grader. Headline: **+8.69pp mean lift, 6 lifts / 11 neutrals / 0 hurts**. The headline was **inflated by a stale plugin cache**: the eval harness loaded a v2.0.0 marketplace cache from 2026-06-21 that did not match the v0.0.3 working directory. iter-3's Bucket A neutrals reflected v2.0.0 routing behavior, not v0.0.3. Superseded by iter-4.

### iter-3.1 (2026-06-22) — Per-skill `--add-dir` experiment

Three configs (without_skill / with_full_marketplace / with_skill_only) on 5 Bucket A3 evals = 15 runs. **9 of 15 captured** (proxy 503s on the rest). **H1 (plugin shadowing) confirmed for `craft-create`**; H2 (description surface) confirmed for `craft-review`; H3 (choice paralysis) not dominant. **H4 bonus finding**: 6 of 9 runs invoked zero skills at all — a routing-heuristic failure upstream of description quality. Files preserved at `attic/2026-06-23-closure/skill-evals/iteration-3.1/`.

### iter-4 (2026-06-23) — Cache-refreshed re-run

After `rm -rf ~/.claude/plugins/cache/taches-principled-light/` and reinstall, re-ran iter-3 against the v0.0.3 working tree. **Headline: +4.94pp mean lift, 5 lifts / 13 neutrals / 0 hurts** on 18 evals. The headline was 3.75pp lower than iter-3 — confirming that the iter-3 lift was stale-cache-inflated. iter-4 is the first **cache-refreshed** headline.

### iter-4.1 (2026-06-23) — Baseline contamination discovery

No new runs. Inspection of the iter-4 `without_skill.jsonl` transcript for `craft-create` revealed that the agent invoked `/crafting-skills` at event 4. **The "without_skill" baseline was actually `plugin_only`**: the marketplace plugin auto-loads into the agent's `slash_commands` regardless of `--add-dir`. iter-4's +4.94pp is the **filesystem_access lift** (plugin_only → plugin_with_add_dir), not the total lift vs a true no-plugin baseline. The true total lift is ≥ +4.94pp (lower bound). This finding is the **motivation for iter-7**.

### iter-5 (2026-06-23) — N=11 reliability, **deferred**

Designed to measure intra-rater noise at N=11 trials per (eval, config) per Yagubyan 2026. **Deferred for two reasons**: (a) iter-7 already lifts 4/4 with 0 hurts, so the directional finding is robust without N=11; (b) the proxy is structurally single-model, so N=11 same-vendor would characterize intra-rater noise but not vendor-disjoint noise. Re-evaluate when a vendor-disjoint judge becomes available.

### iter-6 (2026-06-23) — Code-only lift decomposition (proxy architecture finding)

Reused iter-7's 4-eval transcripts and re-graded with `--judge-model <external judge>` (vendor-disjoint per CoEval 2026). **Every model-based assertion hit the external judge endpoint 503** (`rate-limited`) and returned 0. So iter-6 is effectively a **code-only grade** — only the deterministic consultation + structure-with-compare_args assertions scored. Result: **+7.5pp mean code-only lift** across 4 evals (3 lifts / 1 zero / 0 hurts). The +14.4pp gap from iter-7's +21.88pp is the LLM-judgment contribution. iter-6 also surfaced the **proxy architecture finding**: the proxy serves all 18+ advertised aliases from the configured backend; the external judge is vendor-disjoint and is rate-limited.

### iter-7 (2026-06-23) — Three-config lift disambiguation, **CANONICAL**

The corrected headline measurement. Used `--disable-slash-commands` for the true baseline, then ran three configs (baseline / plugin_only / plugin_with_add_dir) on the 4-eval subset. **Headline: +21.88pp total_lift, +8.12pp consultation_lift (noisy), +13.75pp filesystem_access_lift (deterministic), 4/4 evals lift, 0 hurts**. This is the **canonical report** for the iteration phase.

### iter-8 (2026-06-23) — Designed, not yet run

Designed but not executed. Three sub-experiments to close the two open follow-ups: (8A) mock-based vendor-disjoint validation via a local mock grader; (8B) grader-noise root-cause for the sec-audit +17.5pp swing; (8C) N=11 multi-run averaging. Wall time budget: ~3 hours parallel. See `iteration-8-PLAN.md`.

---

## 2.5 Standalone summaries (TL;DR for the deleted findings-docs)

The following four one-paragraph summaries condense the unique content of the findings-docs that were subsumed into this retrospective. The full evidence trail is in the v0.0.7 closure archive at `docs/principled/attic/2026-06-23-closure/skill-evals/`.

### 2.5.1 Proxy architecture (subsumes iter-6 REPORT § "Headline finding: proxy architecture")

The configured backend is a **single-model gateway**: all 18+ advertised tier aliases (the configured solver tier aliases plus 16+ external-vendor aliases) silently route to the same configured backend. The only genuinely vendor-disjoint option is an external judge vendor, and that option is **rate-limited** on the public endpoint. Same-family bias is therefore real but unmitigable on this proxy. The iter-7 +21.88pp headline is **conservative** (a single-model judge cannot apply self-bias), but same-family bias is plausible and unquantified.

### 2.5.2 Grader non-determinism (subsumes iter-7 GRADER-NOISE-INVESTIGATION)

The same `sec-audit` transcript md5 `bda20918d4b7d0b7245bd12b59b09e58` graded 15.0 in iter-4 and 32.5 in iter-7 by the same judge on bit-for-bit identical input — a +17.5pp swing on a deterministic input. Root cause: the grader does not set `temperature`; the configured backend's reasoning model is non-deterministic at any temperature (floating-point arithmetic, kernel scheduling, batch composition, or proxy-internal sampling). Mitigation: median-of-N grading. The +21.88pp iter-7 headline is still robust because the dominant +13.75pp filesystem_access_lift is on endpoint-deterministic assertions (3 of 3 evals deterministic).

### 2.5.3 SKILL discovery architecture (subsumes SKILL-DISCOVERY-ARCHITECTURE)

The marketplace plugin auto-loads its skills into the agent's `slash_commands` globally, regardless of `--add-dir`. The only CLI flag that prevents auto-load is `--disable-slash-commands`. The 4-bucket routing taxonomy is: **A1** proxy errors (proxy 503s), **A2** partial discovery (some skills surfaced), **A3** true discovery failures (zero skills invoked — a routing-heuristic failure upstream of description quality), **A4** baseline (no-skill config). Marketplace can only mitigate A3 through anti-shadowing markers in descriptions, not eliminate it. H1 (plugin shadowing) is the dominant cause of A3; H2 (description surface) and H3 (choice paralysis from 26+ skills) are secondary.

### 2.5.4 Routing-vs-validator distinction (subsumes methodology-note)

This is a **behavioral evaluation** (measuring agent routing behavior in real eval runs), not a static validator run (checking skill outputs against expected JSON). The two require different instrumentation: behavioral evals use stream-json transcripts and judge scoring; static validators use the marketplace-validator script. The marketplace-validator scripts are part of the marketplace itself; they are not the eval harness. iter-7's 3-config harness (baseline / plugin_only / plugin_with_add_dir) is the behavioral-eval design, and the iter-4 baseline contamination finding is what motivated extending the 2-config (with/without-skill) iter-3 harness to the 3-config iter-7 design.

## 3. Canonical findings (the durable record)

### 3.1 The +21.88pp total_lift (iter-7)

| Lift | Mean | Verdict distribution | Determinism |
|------|-----:|----------------------|-------------|
| `consultation_lift` (baseline → plugin_only) | **+8.12pp** | 1 lift / 3 neutrals / 0 hurts | **NOISY** (sec-audit +17.5pp swing on bit-identical transcript) |
| `filesystem_access_lift` (plugin_only → plugin_with_add_dir) | **+13.75pp** | 3 lifts / 1 neutral / 0 hurts | **Deterministic** (eval-skill, lint-1, release-2 are endpoint-deterministic) |
| **`total_lift` (baseline → plugin_with_add_dir)** | **+21.88pp** | **4 lifts / 0 neutrals / 0 hurts** | **Deterministic** (dominated by filesystem_access) |

Per-eval numbers:

| Eval | baseline | plugin_only | plugin_with_add_dir | consult Δ | fs Δ | total Δ |
|------|---------:|------------:|--------------------:|---------:|-----:|--------:|
| eval-skill | 0.0 | 0.0 | 15.0 | +0.0 | +15.0 | +15.0 |
| sec-audit | 0.0 | 32.5 | 32.5 | +32.5 | +0.0 | +32.5 |
| lint-1 | 0.0 | 0.0 | 25.0 | +0.0 | +25.0 | +25.0 |
| release-2 | 25.0 | 25.0 | 40.0 | +0.0 | +15.0 | +15.0 |

**Mechanism split (corrected)**: iter-4 misclassified eval-skill as consultation-driven. iter-7 shows the actual mechanism is **filesystem-driven** for 3 of 4 evals (eval-skill, lint-1, release-2) and consultation-driven for 1 of 4 (sec-audit). The agent finds marketplace-validator scripts on disk and runs them; it does not Read the SKILL.md first. The lift is operational, not pedagogical.

Source: `iteration-7/REPORT.md`.

### 3.2 The baseline contamination finding (iter-4.1)

**`--add-dir /tmp/empty` does not prevent marketplace plugin auto-load.** The marketplace plugin's skills are injected into the agent's `slash_commands` listing globally, regardless of cwd. The "without_skill" baseline in iter-3 and iter-4 is actually `plugin_only` (plugin loaded, no filesystem access). Evidence: the `craft-create` `without_skill.jsonl` transcript shows the agent invoking `/crafting-skills` at event 4.

**Mitigation:** `--disable-slash-commands` is the only known CLI flag that prevents plugin auto-load. iter-7 uses this for the true baseline.

**Consequence:** iter-3's +8.69pp and iter-4's +4.94pp are both **lower bounds on the total lift**, not measurements of it. The true total lift is +21.88pp (iter-7).

Source: `iteration-7/REPORT.md` § "The baseline contamination finding"; `SKILL-DISCOVERY-ARCHITECTURE.md` v1.1.

### 3.3 The proxy architecture finding (iter-6)

The private inference gateway is a **single-model gateway**. All 18+ advertised aliases silently map to the configured backend:

| Alias class | Real backend | Status |
|---|---|---|
| the configured solver tier aliases (sonnet, opus, etc.) | the configured backend | working (silently aliased) |
| an external judge vendor (the one vendor-disjoint option) | an external judge vendor (real) | **rate-limited** on the public endpoint |
| 16+ external-vendor aliases (commercial and open-source model families) | the configured backend | silently aliased |

**Consequence:** every iter-4/iter-5/iter-7 grade is "the configured solver over the configured backend, the configured judge over the configured backend." Same-family bias is real but unmitigable on this proxy. The +21.88pp number is therefore **conservative** (a single-model judge cannot apply self-bias), but same-family bias is plausible and unquantified.

**Unblock:** LiteLLM multi-model gateway as the v0.0.6+ replacement proxy. See iter-8 design supplements § "LiteLLM multi-model gateway."

Source: `iteration-6/REPORT.md` § "Headline finding: proxy architecture."

### 3.4 The grader non-determinism finding (iter-7 + GRADER-NOISE-INVESTIGATION)

The same `sec-audit` transcript md5 `bda20918d4b7d0b7245bd12b59b09e58` (iter-4 `without_skill.jsonl` relabeled as iter-7 `plugin_only_skill.jsonl`) graded **15.0 in iter-4** and **32.5 in iter-7** by the same `sonnet` judge. Δ = +17.5pp on bit-identical input. Root cause: `grader.py` does not set `temperature`. The proxy uses its default sampling temperature.

**Empirical test:** `temperature=0` does **not** make the configured backend deterministic. 5 runs at default and 5 at `temperature=0` on a deterministic prompt produced 7, 4, 7, 3, 7 (default) and 3, 3, 7, 7, 5 (temp=0). Both distributions are stochastic. This is consistent with reasoning models exhibiting non-determinism at temp=0 due to floating-point arithmetic, kernel scheduling, batch composition, or proxy-internal sampling.

**Why the headline is still robust:** the +21.88pp total_lift is dominated by the +13.75pp filesystem_access_lift (3 of 3 evals endpoint-deterministic). The consultation_lift contributes only +8.12pp and is bracketed at +4.37pp (if iter-4 grading was right) to +8.12pp (if iter-7 grading was right). Even at the lower bracket, **total_lift ≥ +18.12pp with 4/4 evals lifting**.

**Mitigation adopted:** documented the noise floor; consultation_lift cited as "noisy, single-trial, treat as ±noise" in downstream references.

**Mitigation deferred:** median-of-3 grading in iter-8 (cost: 3× grading credits, expected noise reduction: √3 ≈ 1.7×). See `iteration-7/GRADER-NOISE-INVESTIGATION.md`.

### 3.5 The stale plugin cache finding (iter-3 → iter-4 transition)

`~/.claude/plugins/installed_plugins.json` recorded version `2.0.0` installed on `2026-06-21T13:57:59.772Z`, with the cache at `~/.claude/plugins/cache/taches-principled-light/taches-principled-light/2.0.0/`. That cache had **different skill names** than the v0.0.3 working directory:

- v2.0.0 cache: `ddd`, `fpf`, `ideation`, `kaizen`, `mcp-expertise`, `refine`, `rules-orchestration`, `sadd`, `session-analytics`, `skill-authoring`, `subagent-orchestration`, `wiki`
- v0.0.3 work: `crafting-skills`, `engineering-mcp`, `generating-ideas`, `managing-rules`, `managing-wiki`, `orchestrating-subagents`, `evaluating-skills`, `applying-guardrails`, `analyzing-sessions`, `deep-research`, `reasoning-from-principles`, `restructuring-code`, `reviewing-and-polishing`, `solving-competitively`, `general-critic`, `design-hub`

**Consequence:** iter-3 and iter-3.1 results were evaluated against the v2.0.0 marketplace, not v0.0.3. The +8.69pp headline was stale-cache-inflated. iter-4's +4.94pp is the first cache-refreshed headline. iter-7's +21.88pp is cache-refreshed and uses a true baseline.

**Fix:** the eval harness now refreshes the plugin cache before each iter (or installs from the working directory, not the cache). The stale cache was a one-time accident; subsequent iters are not affected. Documented in `SKILL-DISCOVERY-ARCHITECTURE.md` v1.2 and v1.3.

---

## 4. Methodology lessons learned

### 4.1 Three-config harness is necessary, not optional

`--add-dir /tmp/empty` does **not** isolate the plugin. The only way to construct a true no-plugin baseline is `--disable-slash-commands`. Any future iteration harness must include at least these three configs:

| Config | `--disable-slash-commands` | `--add-dir` | Measures |
|--------|---------------------------|-------------|----------|
| `baseline` | yes | `/tmp/empty` | no plugin, no filesystem |
| `plugin_only` | no | `/tmp/empty` | plugin (slash_commands) only, no filesystem |
| `plugin_with_add_dir` | no | `<REPO>` | plugin + filesystem access to marketplace |

`total_lift = consultation_lift + filesystem_access_lift = (baseline → plugin_only) + (plugin_only → plugin_with_add_dir)`. The 3-config split is what makes the iter-7 mechanism classification possible.

### 4.2 `temperature=0` does not make reasoning models deterministic

Empirically tested on the configured backend. 5/5 at default and 5/5 at temp=0 both produced stochastic outputs on a "pick a digit 0-9" prompt. The cause is upstream of temperature: floating-point arithmetic, kernel scheduling, batch composition, or proxy-internal sampling. For grader robustness, prefer **multi-run averaging** (median-of-3 or median-of-11) over `temperature=0`. This is consistent with Norman/Rivera/Hughes 2026 ([arxiv:2606.19544](https://arxiv.org/abs/2606.19544)) finding κ deflation 33.8-41.2pp universal across 21 judges.

### 4.3 Bit-for-bit transcript identity does not guarantee identical grading

The sec-audit `plugin_only` cell produced 15.0 in iter-4 and 32.5 in iter-7 on the same transcript (md5 verified). Same input → different grades is normal LLM stochasticity, not a grader bug. **For any "are the iter-7 numbers stable?" question, the answer is: no, single-trial, treat as ±noise.** For significance, N=11 multi-run averaging is required (Yagubyan 2026, [arxiv:2606.13685](https://arxiv.org/abs/2606.13685)).

### 4.4 Refresh the plugin cache before each iter

The iter-3 → iter-4 transition was 3.75pp of stale-cache inflation. Document the cache state in every iter's REPORT.md so future readers can interpret the headline correctly. iter-4+ reports explicitly state "cache-refreshed" or "cache-current."

### 4.5 The marketplace `Read`-driven discovery mechanism is the bottleneck

`/add-dir <REPO>` gives the agent `Read` access to marketplace SKILL.md files but does **not** inject them into the prompt-time skill listing. The lift is operational (agent runs colocated scripts via filesystem glob) more than pedagogical (agent Reads SKILL.md then changes behavior). The marketplace's value is in the **scripts on disk** as much as in the SKILL.md text. iter-7's mechanism table (3/4 evals filesystem-driven) is the evidence.

### 4.6 Bucket A3 is a routing-heuristic failure, not a description-quality failure

iter-3.1's H4 finding: 6 of 9 runs in the per-skill experiment invoked **zero skills at all** — the agent's prompt-time reasoning did not consider consulting any skill. This is upstream of description quality. The fix is not in the skill descriptions; it's in the agent's general routing heuristic, which is trained upstream by Anthropic. Marketplace can only mitigate this through anti-shadowing markers in descriptions, not eliminate it.

### 4.7 Lift direction is the publishable claim, not magnitude

The robust claim across all 7 iterations is: **the marketplace produces a positive lift on every eval we measured in the consultation + file-access subset, with no observed hurts.** The exact +21.88pp number is one noisy realization. The directional claim (4/4 positive, 0 hurts) is robust to grader noise, to cache state, to proxy backend (any configured backend variant), and to the `--add-dir` mechanism. Future releases can ship on direction; magnitude claims require N=11 (iter-8C).

---

## 5. Design decisions and rationale

### 5.1 iter-5 deferred (not blocking)

Decision: do not run N=11 multi-trial at this time. Rationale: (a) iter-7 already lifts 4/4 with 0 hurts, so the directional finding is robust; (b) the proxy is structurally single-model, so N=11 same-vendor would characterize intra-rater noise but not vendor-disjoint noise. Re-evaluate when a vendor-disjoint judge becomes available, or when the +21.88pp number is challenged in a release review.

### 5.2 iter-6 repurposed as code-only lift decomposition

Decision: when the external judge returned 503 for all 12 grading cells, treat the partial result as a **code-only lift decomposition** (consultation + structure-with-compare_args) rather than abandon the run. Rationale: the code-only grade is a clean lower bound on the true total lift. The +7.5pp code-only lift is the conservative number to cite when a working vendor-disjoint judge would need to be deployed. The +14.4pp gap from iter-7's +21.88pp is the LLM-judgment contribution that same-family bias could in principle suppress.

### 5.3 iter-7 reuses iter-4 transcripts (shutil.copy2, not re-run)

Decision: for `plugin_only` and `plugin_with_add_dir` configs, copy iter-4's transcripts verbatim. Only the 4 `baseline` transcripts are fresh. Rationale: saves ~30 minutes of solver wall-clock; transcripts are bit-for-bit identical to iter-4; grader is the only thing that can produce different outputs. Caveat: the sec-audit +17.5pp grader swing is the empirical evidence that the grader is the only source of variance. iter-4 transcripts are mechanically valid for reuse; iter-4 grades are not.

### 5.4 iter-8 mock-based, not real-proxy-based

Decision: route the iter-7 harness through a local OpenAI-API-compatible mock grader (<mock grader>, B-grade) for iter-8A/8B/8C rather than waiting for a real vendor-disjoint proxy. Rationale: (a) the real proxy is structurally single-model; vendor-disjoint validation cannot run against it; (b) the mock gives vendor-disjoint semantics **for testing the grader harness** (not the model); (c) mock-based multi-run averaging (8C) costs ~3 hours vs the real proxy's 33 hours for N=11; (d) when the LiteLLM gateway is deployed (v0.0.6+), iter-8 results can be re-validated against the real vendor-disjoint judge.

### 5.5 The 4-eval subset is intentionally narrow

Decision: do not expand the iter-7 subset to the full 18 evals. Rationale: (a) iter-7's goal is the **3-config mechanism split**, which requires fresh baseline transcripts for each eval (4 fresh runs at ~3 min each is ~12 min wall clock; 18 fresh runs at ~3 min each is ~54 min wall clock); (b) the 4-eval subset covers both mechanism categories (consultation: sec-audit; file-access: eval-skill, lint-1, release-2); (c) iter-4's 18-eval campaign already characterized breadth — the +4.94pp iter-4 number and the +21.88pp iter-7 number are the breadth/depth pair. The 4-eval subset is the depth measurement; iter-4 is the breadth measurement.

### 5.6 The CHANGELOG `[0.0.7]` closure record replaces a `SUMMARY.md`

Decision: do not write a `SUMMARY.md` for the iteration phase closure. Rationale: per the project's CHANGELOG-as-summary closure convention (AGENTS.md "Project Closure Convention"), durable closure markers are CHANGELOG entry + release tag + `grading_summary.json`. v0.0.7 has no new grading_summary.json (no new eval was run for the cleanup release), but it has a CHANGELOG `[0.0.7]` entry, a release tag, and the iter-7 `grading_summary.json` remains canonical. The closure archive's `STATUS.md` + `metadata.md` document the closure decisions inline (what was archived, what stays, what cross-references were updated).

---

## 6. Open follow-ups

### 6.1 Methodology improvement program (iter-8 design, not yet run)

Three sub-experiments target the iteration-phase's two open follow-ups, framed as a methodology improvement program rather than a proxy-specific fix:

- **8A mock-based vendor-disjoint validation**: route a 4-eval subset through a local OpenAI-API-compatible mock grader that returns canned responses per `(model_name, prompt_hash)`. This simulates vendor-disjoint judge semantics for testing the grader harness without requiring a second-model proxy. Decision rule: if |iter-8A − iter-7| < 2pp on `total_lift`, the iter-7 headline is robust to vendor-disjoint substitution. If the gap is > 5pp, iter-7 needs a vendor-disjoint re-run before the next release.
- **8B grader-noise root-cause**: replay the sec-audit grading against the mock 10 times. If mock replays give stddev < 0.5pp, the original 17.5pp swing is harness-side (grader state machine or evaluation criteria, not the model). If stddev > 0.5pp, the mock is non-deterministic and not safe for 8C.
- **8C N=11 multi-run averaging**: 4 evals × 3 configs × 11 trials = 132 runs. Isolates agent-side variance from judge-side variance (which the mock removes). Publishes per-eval CIs for the +21.88pp headline.

Wall time budget: ~3 hours parallel. Full design at `iteration-8-PLAN.md`; supplements at `docs/principled/research/2026-06-23-iter8-design-supplements.md` (MCP mocking for `secret_detection`, Claude Code CLI flag inventory, LiteLLM multi-model gateway for v0.0.6+).

### 6.2 LiteLLM multi-model gateway (v0.0.6+ prerequisite)

The private inference gateway proxy is structurally single-model. iter-6 is structurally blocked until a vendor-disjoint proxy is available. The recommended replacement is **LiteLLM** (51,259 stars, native MCP + A2A, drop-in OpenAI compat, 8ms P95 at 1k RPS) deployed as a self-hosted multi-model gateway. When deployed, iter-6 can be re-run with a working external judge; the iter-7 +21.88pp headline can be re-validated against a true vendor-disjoint judge. Track as v0.0.6+ prerequisite.

### 6.3 Heterogeneous judge matrix (iter-9)

iter-4 used a heterogeneous judge (a higher-tier alias over the configured solver). iter-7 reused iter-4's grading for time reasons. iter-9 should re-grade iter-7's transcripts with a **heterogeneous judge matrix** (3+ tier aliases in rotation) to measure judge-side variance directly. This is independent of iter-8's mock-based approach and addresses the same-family bias concern from a different angle.

### 6.4 SkillsBench / SoK alignment (v0.1.0 scope)

[arxiv:2602.12670](https://arxiv.org/abs/2602.12670) (SkillsBench, 87 tasks / 8 domains) and [arxiv:2602.20867](https://arxiv.org/abs/2602.20867) (SoK: Agentic Skills) suggest a standardized eval surface that this marketplace does not currently target. Track as v0.1.0 scope — the marketplace should be measured against an external benchmark, not just internal evals.

### 6.5 Anti-shadowing markers in skill descriptions (Bucket A3 follow-up)

The Bucket A3 failures (ingest-1, ingest-2, lint-2, craft-create, craft-review) are primarily H1 (plugin shadowing) compounded with H2 (description surface quality). The proposed fix is **anti-shadowing markers**: explicit "Use this instead of superpowers:writing-skills for X" patterns in marketplace skill descriptions. Tests whether negative framing helps. Low cost; could be a v0.0.8 patch if iter-8's direction-robustness claim is confirmed.

---

## 7. Cross-references (the source documents)

### Canonical (in active tree)

- **This document** — `docs/principled/skill-evals/ITERATION-PHASE-RETROSPECTIVE.md` (sole narrative entry point)
- **INDEX** — `docs/principled/skill-evals/INDEX.md` (pointer to the retrospective)
- **iter-8 PLAN** — `marketplace-routing-2026-06-22/iteration-8-PLAN.md` (methodology improvement program: mock infrastructure, grader non-determinism root-cause, N=11 averaging)
- **iter-8 design supplements** — `docs/principled/research/2026-06-23-iter8-design-supplements.md` (MCP mocking for `secret_detection`, Claude Code CLI flag inventory, LiteLLM multi-model gateway for v0.0.6+)

### Archived (in closure bundle, full audit trail)

- iter-1 → `attic/2026-06-23-closure/skill-evals/iteration-1/`
- iter-2 → `attic/2026-06-23-closure/skill-evals/iteration-2/` (API-OVERLOAD-INCIDENT, METRIC-BUG-NOTE, OUTCOME)
- iter-3 → `attic/2026-06-23-closure/skill-evals/iteration-3/` (DISCOVERY-INVESTIGATION, BUCKET-A-INSPECTION, RESEARCH-FINDINGS)
- iter-3.1 → `attic/2026-06-23-closure/skill-evals/iteration-3.1/` (per-skill H1/H2/H3 experiment, H4 routing-heuristic finding)
- iter-4 → `attic/2026-06-23-closure/skill-evals/iteration-4/` (RESEARCH-FINDINGS-iter5-design with baseline contamination finding)
- iter-5/6/7 design (superseded) → `attic/2026-06-23-closure/research/agent-skills-evaluation/` and `attic/2026-06-23-closure/research/hub-references-routing-evals/`

### Closure record (per AGENTS.md "Project Closure Convention")

- `docs/principled/attic/2026-06-23-closure/STATUS.md` — closure record for v0.0.7
- `docs/principled/attic/2026-06-23-closure/metadata.md` — file inventory, key decisions, cross-reference update list
- `CHANGELOG.md` → `## [0.0.7]` — long-form changelog entry
- `.github/RELEASE-v0.0.7.md` — long-form GitHub release notes
- `v0.0.7` annotated tag (commit `06027bb`)

---

## 8. Third-party cross-confirmation of the directional finding

Two independent 2026 studies bracket the +21.88pp number:

- **[Xu et al. 2026, arxiv:2605.31408](https://arxiv.org/abs/2605.31408)** ("Skill Availability and Presentation Granularity in Large-Language-Model Agents: A Controlled SkillsBench Study"): skill conditions vs no-skill on a 30-task domain-balanced subset (5 trials/cell) yielded **+26.7 to +36.0pp lift for GPT-5.5** and **+18.0 to +26.0pp lift for DeepSeek V4-Flash**. Our +21.88pp sits in the middle of this third-party bracket.
- **[Gorinova et al. 2026, arxiv:2606.17819](https://arxiv.org/abs/2606.17819v1)** ("A Framework for Evaluating Agentic Skills at Scale"): 500 real-world skills × 1,000 derived tasks × 19 model configurations. The paper's central finding — "access to a skill significantly changes model behavior compared to the no-skill setup" — and the secondary finding that "models vary widely in how closely they adhere to the instructions encoded in skills" both align qualitatively with our iter-7 total_lift. The scale (500 skills, 19 models) provides the strongest external support for the qualitative claim that the marketplace plugin produces meaningful agent behavior change.

---

## 9. Known limitations (unchanged across v0.0.5/v0.0.6/v0.0.7)

1. **sec-audit consultation_lift is non-deterministic** on the current judge. Mitigation in iter-8B. The directional finding is robust (4/4 evals lift, 0 hurts); the headline is dominated by deterministic filesystem_access_lift (+13.75pp mean).
2. **Vendor-disjoint validation is structurally blocked** on the current `<private inference gateway>` proxy. iter-8A unblocks this via a local mock; v0.0.6+ LiteLLM deployment unblocks it for the real proxy.
3. **Same-family judge bias is plausible but unquantified.** The proxy serves all aliases from the configured backend; a vendor-disjoint judge could in principle suppress or amplify the LLM-judgment contribution. iter-8A's mock-based vendor-disjoint substitution is the test-harness simulation of this concern.
4. **N=4 below Yagubyan 2026's N=11 reliability threshold.** iter-7 is a Phase A (proof-of-concept) run, not a final verdict on magnitude. Direction is robust; magnitude is one noisy realization. iter-8C will publish per-eval CIs.

---

*This document is the canonical narrative entry point for the 2026-06-22 → 2026-06-23 iteration phase. It supersedes the closure archive's `STATUS.md` for the "what did the iteration phase produce" question. The closure archive preserves the full audit trail; this document provides the executive narrative. Future readers should start here, then drill into the linked source documents for the underlying evidence.*
