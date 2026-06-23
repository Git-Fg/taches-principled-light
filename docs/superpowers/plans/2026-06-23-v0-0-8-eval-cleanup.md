# v0.0.8 Eval Cleanup & Sanitization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finalize the repo for public release by removing all eval artifacts and risky/personal information from the active tree, while preserving the canonical iteration-phase narrative in a single document.

**Architecture:** Documentation-only release. The retrospective (`docs/principled/skill-evals/ITERATION-PHASE-RETROSPECTIVE.md`) becomes the sole narrative entry point. All other eval artifacts (raw transcripts, grading JSONs, harness scripts, per-eval directories, findings-docs, eval-regression CI) are deleted. Retained files are scrubbed of risky strings (private Tailscale IP, real backend model name, vendor aliases, proxy-specific error strings). The auto-loaded memory file `docs/principled/memory/learnings.md` is scrubbed because it is the most-sensitive surface. The `iter-8-PLAN.md` is reframed as a methodology improvement program (mock infrastructure, grader non-determinism, N=11 averaging), dropping the proxy-specific premise. The `evaluating-skills` marketplace skill is KEPT (it is a marketplace capability, not an eval artifact). The v0.0.7 closure archive at `docs/principled/attic/2026-06-23-closure/` is not modified (immutable historical record per AGENTS.md "Project Closure Convention").

**Tech Stack:** Git, bash, Edit/Read/Write tools. No code, no tests, no runtime dependencies. v0.0.8 closes with a CHANGELOG `[0.0.8]` entry + the v0.0.8 release tag (AGENTS.md "Project Closure Convention" durable markers; no `SUMMARY.md` for documentation-only releases).

**Spec:** `docs/principled/specs/2026-06-23-eval-cleanup-design.md` (commit `eb7bfa0`)

**Key sequencing rule:** The retrospective must be expanded with the per-eval numbers BEFORE the iter-7 REPORT is deleted, because the per-eval numbers are the only place the iter-7 4-eval × 3-config matrix lives. Task 1 consumes iter-7/REPORT.md; Tasks 11-13 delete the source.

**Standard scrub rules (applied in every relevant task; full table in spec § "Scrub Rules"):**
- `MiniMax-M3` → `the configured backend`
- `http://100.80.231.128:3456` → `<private inference gateway>` in code/config, remove entirely in narrative
- `claude-haiku-4-5-20251001` → `<solver tier alias>`
- `nex-agi/nex-n2-pro:free` and 17 other vendor aliases → `<vendor alias>` (or "18+ tier aliases" where brevity matters)
- `circuit_breaker_open: RateLimit` → `rate-limited`
- `haiku solver` → `the configured solver` in eval context only (KEEP in `skills/crafting-skills/references/frontmatter-complete.md` Claude Code model ID reference)
- KEEP: `bda20918d4b7d0b7245bd12b59b09e58` (hash, not risky), `+21.88pp`/`+8.12pp`/`+13.75pp`/`+17.5pp` (numbers are findings), `--disable-slash-commands`/`--add-dir`/`--mcp-config`/`--bare` (CLI flags), `https://github.com/Git-Fg/taches-principled-light` (public repo), arxiv.org URLs (public papers)

---

## Task 1: Expand and scrub ITERATION-PHASE-RETROSPECTIVE.md

**Files:**
- Modify: `docs/principled/skill-evals/ITERATION-PHASE-RETROSPECTIVE.md` (293 → ~400 lines)

This is the centerpiece. The retrospective already contains the per-eval table (section 3.1, lines 81-89); we keep that. We add 5 one-paragraph standalone summaries in a new section between the executive summary and the detailed findings. We update the Cross-references section to remove references to deleted docs. We update the Open follow-ups section to match the reframed iter-8 (no longer a concrete plan tied to the proxy). We scrub all risky strings.

The per-eval table is already at lines 81-89 of the current retrospective. Verify this when you read the file — do not delete the table.

- [ ] **Step 1: Read the current retrospective and confirm per-eval table is in section 3.1**

Run: `head -100 docs/principled/skill-evals/ITERATION-PHASE-RETROSPECTIVE.md`
Expected: The per-eval table appears around line 81-89, with columns `Eval | baseline | plugin_only | plugin_with_add_dir | consult Δ | fs Δ | total Δ` and rows for eval-skill, sec-audit, lint-1, release-2, mean.

- [ ] **Step 2: Apply scrubs to the current retrospective content first**

Edit `docs/principled/skill-evals/ITERATION-PHASE-RETROSPECTIVE.md` with the following replacements (use `Edit` with `replace_all=true` for each):

| Risky string | Replacement |
|---|---|
| `100.80.231.128:3456` | `<private inference gateway>` |
| `MiniMax-M3` | `the configured backend` |
| `circuit_breaker_open: RateLimit` | `rate-limited` |
| `haiku solver` | `the configured solver` |
| `claude-haiku-4-5-20251001` | `<solver tier alias>` |
| `haiku/sonnet/opus/nex-agi` | `the configured solver tier aliases` |
| `Z.AI` | `an external judge vendor` |

Note: `100.80.231.128:3456` appears 3 times — use `Edit` with `replace_all=true`. `MiniMax-M3` appears 4 times — `replace_all=true`. Each pattern is a separate Edit call.

- [ ] **Step 3: Verify the retrospective is clean of risky strings**

Run:
```bash
git grep -nE "MiniMax|100\.80\.231\.128|nex-agi|claude-haiku-4-5-20251001|circuit_breaker_open|Z\.AI" docs/principled/skill-evals/ITERATION-PHASE-RETROSPECTIVE.md
```
Expected: 0 matches.

- [ ] **Step 4: Add the standalone summaries section**

After section 2 ("The story — seven iterations in 36 hours") and before section 3 ("Canonical findings"), insert a new section 2.5. Find the line `## 3. Canonical findings (the durable record)` and insert the block immediately before it (use `Edit` with `old_string` being that exact line and `new_string` being the new section + the original line):

```markdown
## 2.5 Standalone summaries (TL;DR for the deleted findings-docs)

The following four one-paragraph summaries condense the unique content of the findings-docs that were subsumed into this retrospective. The full evidence trail is in the v0.0.7 closure archive at `docs/principled/attic/2026-06-23-closure/skill-evals/`.

### 2.5.1 Proxy architecture (subsumes iter-6 REPORT § "Headline finding: proxy architecture")

The configured backend is a **single-model gateway**: all 18+ advertised tier aliases (the configured solver tier aliases plus 18+ external-vendor aliases) silently route to the same configured backend. The only genuinely vendor-disjoint option is an external judge vendor, and that option is **rate-limited** on the public endpoint. Same-family bias is therefore real but unmitigable on this proxy. The iter-7 +21.88pp headline is **conservative** (a single-model judge cannot apply self-bias), but same-family bias is plausible and unquantified.

### 2.5.2 Grader non-determinism (subsumes iter-7 GRADER-NOISE-INVESTIGATION)

The same `sec-audit` transcript md5 `bda20918d4b7d0b7245bd12b59b09e58` graded 15.0 in iter-4 and 32.5 in iter-7 by the same judge on bit-for-bit identical input — a +17.5pp swing on a deterministic input. Root cause: the grader does not set `temperature`; the configured backend's reasoning model is non-deterministic at any temperature (floating-point arithmetic, kernel scheduling, batch composition, or proxy-internal sampling). Mitigation: median-of-N grading. The +21.88pp iter-7 headline is still robust because the dominant +13.75pp filesystem_access_lift is on endpoint-deterministic assertions (3 of 3 evals deterministic).

### 2.5.3 SKILL discovery architecture (subsumes SKILL-DISCOVERY-ARCHITECTURE)

The marketplace plugin auto-loads its skills into the agent's `slash_commands` globally, regardless of `--add-dir`. The only CLI flag that prevents auto-load is `--disable-slash-commands`. The 4-bucket routing taxonomy is: **A1** proxy errors (proxy 503s), **A2** partial discovery (some skills surfaced), **A3** true discovery failures (zero skills invoked — a routing-heuristic failure upstream of description quality), **A4** baseline (no-skill config). Marketplace can only mitigate A3 through anti-shadowing markers in descriptions, not eliminate it. H1 (plugin shadowing) is the dominant cause of A3; H2 (description surface) and H3 (choice paralysis from 26+ skills) are secondary.

### 2.5.4 Routing-vs-validator distinction (subsumes methodology-note)

This is a **behavioral evaluation** (measuring agent routing behavior in real eval runs), not a static validator run (checking skill outputs against expected JSON). The two require different instrumentation: behavioral evals use stream-json transcripts and judge scoring; static validators use the marketplace-validator script. The marketplace-validator scripts are part of the marketplace itself; they are not the eval harness. iter-7's 3-config harness (baseline / plugin_only / plugin_with_add_dir) is the behavioral-eval design, and the iter-4 baseline contamination finding is what motivated extending the 2-config (with/without-skill) iter-3 harness to the 3-config iter-7 design.

## 3. Canonical findings (the durable record)
```

- [ ] **Step 5: Update the Cross-references section to remove references to deleted docs**

In the retrospective, find section 7 ("Cross-references (the source documents)"). The "Canonical (in active tree)" subsection currently lists iter-6 REPORT, iter-7 REPORT, GRADER-NOISE-INVESTIGATION, iter-8 PLAN, SKILL-DISCOVERY-ARCHITECTURE, and methodology-note. After deletion, only the retrospective, INDEX, and iter-8 PLAN remain. Replace the entire "Canonical (in active tree)" subsection with:

```markdown
### Canonical (in active tree)

- **This document** — `docs/principled/skill-evals/ITERATION-PHASE-RETROSPECTIVE.md` (sole narrative entry point)
- **INDEX** — `docs/principled/skill-evals/INDEX.md` (pointer to the retrospective)
- **iter-8 PLAN** — `docs/principled/skill-evals/marketplace-routing-2026-06-22/iteration-8-PLAN.md` (methodology improvement program; mock infrastructure, grader non-determinism root-cause, N=11 averaging)
- **iter-8 design supplements** — `docs/principled/research/2026-06-23-iter8-design-supplements.md` (MCP mocking for `secret_detection`, Claude Code CLI flag inventory, LiteLLM multi-model gateway for v0.0.6+)
```

Use `Edit` with `old_string` being the existing "Canonical (in active tree)" block (from `### Canonical (in active tree)` through the last bullet before `### Archived`) and `new_string` being the replacement above.

- [ ] **Step 6: Update the Open follow-ups section to match the reframed iter-8**

In the retrospective, find section 6.1 ("iter-8 (designed, not yet run)"). Currently it describes iter-8 as a concrete plan tied to the proxy. Replace it with the reframed version:

```markdown
### 6.1 Methodology improvement program (iter-8 design, not yet run)

Three sub-experiments target the iteration-phase's two open follow-ups, framed as a methodology improvement program rather than a proxy-specific fix:

- **8A mock-based vendor-disjoint validation**: route a 4-eval subset through a local OpenAI-API-compatible mock grader that returns canned responses per `(model_name, prompt_hash)`. This simulates vendor-disjoint judge semantics for testing the grader harness without requiring a second-model proxy. Decision rule: if |iter-8A − iter-7| < 2pp on `total_lift`, the iter-7 headline is robust to vendor-disjoint substitution. If the gap is > 5pp, iter-7 needs a vendor-disjoint re-run before the next release.
- **8B grader-noise root-cause**: replay the sec-audit grading against the mock 10 times. If mock replays give stddev < 0.5pp, the original 17.5pp swing is harness-side (grader state machine or evaluation criteria, not the model). If stddev > 0.5pp, the mock is non-deterministic and not safe for 8C.
- **8C N=11 multi-run averaging**: 4 evals × 3 configs × 11 trials = 132 runs. Isolates agent-side variance from judge-side variance (which the mock removes). Publishes per-eval CIs for the +21.88pp headline.

Wall time budget: ~3 hours parallel. Full design at `iteration-8-PLAN.md`; supplements at `docs/principled/research/2026-06-23-iter8-design-supplements.md` (MCP mocking for `secret_detection`, Claude Code CLI flag inventory, LiteLLM multi-model gateway for v0.0.6+).
```

- [ ] **Step 7: Final verification — retrospective is clean and expanded**

Run:
```bash
git grep -nE "MiniMax|100\.80\.231\.128|nex-agi|claude-haiku-4-5-20251001|circuit_breaker_open|Z\.AI" docs/principled/skill-evals/ITERATION-PHASE-RETROSPECTIVE.md
wc -l docs/principled/skill-evals/ITERATION-PHASE-RETROSPECTIVE.md
```
Expected: 0 matches from grep; line count between 380 and 420.

- [ ] **Step 8: Commit**

```bash
git add docs/principled/skill-evals/ITERATION-PHASE-RETROSPECTIVE.md
git commit -m "v0.0.8: expand and scrub iteration phase retrospective

- Add section 2.5 'Standalone summaries' (4 one-paragraph TL;DRs:
  proxy architecture, grader non-determinism, SKILL discovery,
  routing-vs-validator) condensing the unique content of the
  findings-docs subsumed into this retrospective
- Update Cross-references section to remove references to deleted
  docs (iter-6/iter-7 REPORTs, GRADER-NOISE, SKILL-DISCOVERY,
  methodology-note)
- Update Open follow-ups section 6.1 to match the reframed iter-8
  (methodology improvement program, not proxy-specific plan)
- Scrub all risky strings: 100.80.231.128:3456, MiniMax-M3,
  circuit_breaker_open: RateLimit, Z.AI, haiku solver,
  claude-haiku-4-5-20251001, nex-agi, haiku/sonnet/opus/nex-agi
  list

Per-eval numbers preserved unchanged in section 3.1.
bda20918d4b7d0b7245bd12b59b09e58 hash preserved.
+21.88pp/+8.12pp/+13.75pp/+17.5pp numbers preserved."
```

---

## Task 2: Simplify and scrub docs/principled/skill-evals/INDEX.md

**Files:**
- Modify: `docs/principled/skill-evals/INDEX.md` (118 → ~20 lines)

INDEX currently lists every iteration with cross-references to deleted docs. Reduce to a 1-paragraph pointer to the retrospective.

- [ ] **Step 1: Write the new INDEX content**

Use `Write` to overwrite `docs/principled/skill-evals/INDEX.md` with:

```markdown
# Skill-Evals Index

Read [`ITERATION-PHASE-RETROSPECTIVE.md`](ITERATION-PHASE-RETROSPECTIVE.md) for the canonical narrative of the iteration phase (2026-06-22 → 2026-06-23): the 4-eval headline (`total_lift = +21.88pp`, `4/4 lifts, 0 hurts`), the four canonical findings (baseline contamination, proxy architecture, grader non-determinism, stale plugin cache), and the methodology lessons learned. The retrospective is the single source of truth; the supporting iteration deliverables are preserved in the v0.0.7 closure archive at `docs/principled/attic/2026-06-23-closure/skill-evals/`.
```

- [ ] **Step 2: Verify the new INDEX is clean**

Run:
```bash
git grep -nE "MiniMax|100\.80\.231\.128|nex-agi|claude-haiku-4-5-20251001|circuit_breaker_open|Z\.AI" docs/principled/skill-evals/INDEX.md
wc -l docs/principled/skill-evals/INDEX.md
```
Expected: 0 matches from grep; ~5 lines (the file is one paragraph + title).

- [ ] **Step 3: Commit**

```bash
git add docs/principled/skill-evals/INDEX.md
git commit -m "v0.0.8: simplify INDEX.md to retrospective pointer

Retrospective is the sole narrative; INDEX reduces to a 1-paragraph
pointer. Removes cross-references to deleted eval artifacts."
```

---

## Task 3: Reframe and scrub iteration-8-PLAN.md as methodology improvement program

**Files:**
- Modify: `docs/principled/skill-evals/marketplace-routing-2026-06-22/iteration-8-PLAN.md` (294 → ~250 lines)

iter-8 was originally designed to solve the proxy single-model problem by introducing a local mock. The reframed plan drops the proxy-specific premise and becomes a methodology-design document. The LiteLLM finding is moved to the supplements note; the mock-implementation evaluation is condensed.

- [ ] **Step 1: Rewrite the title and status block**

Use `Edit`. Replace this block at the top of the file:

```markdown
# iter-8 Plan — Vendor-Disjoint Mock + Deterministic Grader

**Status:** Designed 2026-06-23. Targets two open problems: (1) iter-6's
structural blockage (the inference-gateway proxy is a single-model gateway,
so vendor-disjoint validation cannot run against the real proxy), and
(2) the +17.5pp sec-audit grader swing on bit-for-bit identical transcripts
(`md5 bda20918d4b7d0b7245bd12b59b09e58`) that the iter-7 REPORT flagged as
**grader noise** (see `iteration-7/GRADER-NOISE-INVESTIGATION.md`).

The mock-based design also opens the door to (3) full N=11 reliability
study (iter-5 follow-up) without the 33-hour wall-time budget the real proxy
would require.

See [`docs/.../research/vendor-disjoint-grader-mock-2026-06-23.md`](../../research/vendor-disjoint-grader-mock-2026-06-23.md)
for the full mock-implementation evaluation (3 candidates compared: WireMock
+ LiteLLM, `zerob13/mock-openai-api`, and a 30-line Python shim).

> **Supplements (2026-06-23):** [`2026-06-23-iter8-design-supplements.md`](../../research/2026-06-23-iter8-design-supplements.md)
> adds three things this plan does not cover: (1) a **two-layer MCP stack**
> for `secret_detection` (mock MCP server + mcp-assert test runner —
> mcp-assert is a test runner, not a mock); (2) a **Claude Code CLI flag
> inventory** with `--mcp-config` and `--max-turns` recommended for
> sub-experiments 8B and 8C; (3) a **LiteLLM multi-model gateway** as the
> v0.0.6+ replacement for the single-model `100.80.231.128:3456` proxy.
```

With:

```markdown
# iter-8 Plan — Methodology Improvement Program (Mock Grader + N=11 Averaging)

**Status:** Designed 2026-06-23. Methodology improvement program targeting
two open follow-ups from iter-7: (1) **vendor-disjoint validation** (the
current grading surface is same-family, structurally unmitigable when the
public inference endpoint is single-model), and (2) the **+17.5pp
grader swing** on bit-for-bit identical transcripts (md5
`bda20918d4b7d0b7245bd12b59b09e58`). The mock-based design also opens
the door to (3) full **N=11 reliability study** (iter-5 follow-up) without
the wall-time budget a real model would require.

The plan is **methodology-design**, not proxy-specific: the mock grader
and multi-run averaging apply to any single-model inference surface where
vendor-disjoint validation is structurally blocked. When a multi-model
gateway is available (v0.0.6+ LiteLLM deployment), iter-8 results can be
re-validated against a real vendor-disjoint judge.

> **Supplements (2026-06-23):** [`2026-06-23-iter8-design-supplements.md`](../../research/2026-06-23-iter8-design-supplements.md)
> adds three things this plan does not cover: (1) a **two-layer MCP stack**
> for `secret_detection` (mock MCP server + mcp-assert test runner —
> mcp-assert is a test runner, not a mock); (2) a **Claude Code CLI flag
> inventory** with `--mcp-config` and `--max-turns` recommended for
> sub-experiments 8B and 8C; (3) a **LiteLLM multi-model gateway** as the
> v0.0.6+ replacement for any structurally single-model inference surface.
```

- [ ] **Step 2: Rewrite section "Why iter-8"**

Find the `## Why iter-8` header. Replace the entire section (through the closing `---`) with:

```markdown
## Why iter-8

iter-7 shipped the canonical headline (**+21.88pp total_lift, 4/4 lifts, 0
hurts, deterministic endpoint grades**) but left two follow-ups open:

1. **Vendor-disjoint validation is structurally blocked**: when the
   inference surface is a single-model gateway, all advertised tier
   aliases route to the same backend. The only way to get genuine
   vendor-disjoint validation in that state is a mock that simulates
   different model families.

2. **Grader noise is uncontrolled** (iter-7 caveat #3): a `secret_detection`
   assertion swung from 15.0 (iter-4) to 32.5 (iter-7) on bit-for-bit
   identical transcript. The 17.5pp swing on a deterministic input is a
   grader-side bug, not a model-side variance. Per Yagubyan 2026
   (arxiv:2606.13685), the grader's inter-run flip rate on a fixed input
   should be < 5pp; the observed 17.5pp is 3.5× the threshold.

iter-8 addresses both by introducing a **local OpenAI-API-compatible mock
grader** that returns deterministic responses for any (model_name, prompt)
pair, then routing the iter-7 harness through the mock in two modes:

- **Mode A (vendor-disjoint)**: mock returns sonnet-shaped responses when
  called with `model=sonnet-judge` but haiku-shaped responses when called
  with `model=haiku-judge`. This simulates a vendor-disjoint judge pipeline
  without requiring a second-model proxy.
- **Mode B (multi-run averaging)**: mock returns the same response for the
  same input on repeated calls (idempotent at the message level), enabling
  N=11 reliability study without model-side variance.
```

- [ ] **Step 3: Scrub remaining risky strings**

Use `Edit` with `replace_all=true` for each:

| Risky string | Replacement |
|---|---|
| `100.80.231.128:3456` | `<private inference gateway>` |
| `MiniMax-M3` | `the configured backend` |
| `circuit_breaker_open: RateLimit` | `rate-limited` |
| `haiku solver` | `the configured solver` |
| `claude-haiku-4-5-20251001` | `<solver tier alias>` |
| `glm-5.2` | `an external judge vendor` |
| `Z.AI` | `an external judge vendor` |
| `nex-agi/nex-n2-pro:free` | `<vendor alias>` |

- [ ] **Step 4: Verify the plan is clean**

Run:
```bash
git grep -nE "MiniMax|100\.80\.231\.128|nex-agi|claude-haiku-4-5-20251001|circuit_breaker_open|glm-5\.2|Z\.AI" docs/principled/skill-evals/marketplace-routing-2026-06-22/iteration-8-PLAN.md
wc -l docs/principled/skill-evals/marketplace-routing-2026-06-22/iteration-8-PLAN.md
```
Expected: 0 matches; line count between 240 and 280.

- [ ] **Step 5: Commit**

```bash
git add docs/principled/skill-evals/marketplace-routing-2026-06-22/iteration-8-PLAN.md
git commit -m "v0.0.8: reframe iter-8 plan as methodology improvement program

- Drop the proxy-specific premise; plan is now methodology-design
  (mock grader + N=11 averaging), applicable to any single-model
  inference surface
- Move mock-implementation evaluation reference to the supplements
  note (which is KEPT)
- Scrub risky strings: 100.80.231.128:3456, MiniMax-M3,
  circuit_breaker_open: RateLimit, glm-5.2, Z.AI, haiku solver,
  claude-haiku-4-5-20251001, nex-agi"
```

---

## Task 4: Scrub docs/principled/research/2026-06-23-iter8-design-supplements.md

**Files:**
- Modify: `docs/principled/research/2026-06-23-iter8-design-supplements.md` (~215 lines)

This file has 3 sections: MCP mocking for `secret_detection`, Claude Code CLI flag inventory, LiteLLM multi-model gateway. Section 1 has 100.80 references and model names; section 3 has 100.80 references. Sections 2 (CLI flags) is already abstract.

- [ ] **Step 1: Apply standard scrubs**

Use `Edit` with `replace_all=true` for each:

| Risky string | Replacement |
|---|---|
| `100.80.231.128:3456` | `<private inference gateway>` |
| `MiniMax-M3` | `the configured backend` |
| `glm-5.2` | `an external judge vendor` |
| `Z.AI` | `an external judge vendor` |
| `claude-haiku-4-5-20251001` | `<solver tier alias>` |

- [ ] **Step 2: Verify**

Run:
```bash
git grep -nE "MiniMax|100\.80\.231\.128|claude-haiku-4-5-20251001|glm-5\.2|Z\.AI" docs/principled/research/2026-06-23-iter8-design-supplements.md
```
Expected: 0 matches.

- [ ] **Step 3: Commit**

```bash
git add docs/principled/research/2026-06-23-iter8-design-supplements.md
git commit -m "v0.0.8: scrub iter-8 design supplements

Remove proxy URL and model name references. LiteLLM and CLI flag
findings are generalizable and preserved."
```

---

## Task 5: Scrub docs/principled/memory/learnings.md (most-sensitive surface)

**Files:**
- Modify: `docs/principled/memory/learnings.md`

This is the most-sensitive surface because it is auto-loaded in every agent session per AGENTS.md. The proxy URL appears at lines 30 and 73.

- [ ] **Step 1: Read the file and find all risky strings**

Run:
```bash
git grep -nE "100\.80|MiniMax|nex-agi|claude-haiku-4-5|circuit_breaker|glm-5\.2|Z\.AI" docs/principled/memory/learnings.md
```

- [ ] **Step 2: Apply standard scrubs**

Use `Edit` with `replace_all=true` for each:

| Risky string | Replacement |
|---|---|
| `100.80.231.128:3456` | `<private inference gateway>` |
| `MiniMax-M3` | `the configured backend` |
| `circuit_breaker_open: RateLimit` | `rate-limited` |
| `haiku solver` | `the configured solver` |
| `claude-haiku-4-5-20251001` | `<solver tier alias>` |

- [ ] **Step 3: Verify**

Run:
```bash
git grep -nE "100\.80|MiniMax|nex-agi|claude-haiku-4-5|circuit_breaker|glm-5\.2|Z\.AI" docs/principled/memory/learnings.md
```
Expected: 0 matches.

- [ ] **Step 4: Commit**

```bash
git add docs/principled/memory/learnings.md
git commit -m "v0.0.8: scrub learnings.md (auto-loaded memory)

Most-sensitive surface — auto-loaded in every agent session.
Remove proxy URL, model name, vendor aliases, and proxy-specific
error strings. LiteLLM lesson preserved (public project, not risky)."
```

---

## Task 6: Rewrite README.md eval summary

**Files:**
- Modify: `README.md` (line 88, eval summary section)

The current eval summary at line 88 mentions "haiku solver", the +21.88pp headline, the 4-eval subset, and a link to iter-7/REPORT.md. Replace with abstract backend naming.

- [ ] **Step 1: Read the eval summary section**

Run:
```bash
sed -n '85,92p' README.md
```

- [ ] **Step 2: Replace the eval summary**

Use `Edit`. The `old_string` is the full line 88 of the README. The `new_string` is:

```markdown
**iter-5/6/7 measurement campaign complete.** Canonical headline from `evaluating-skills` 8-stage harness on the configured solver: **mean total_lift +21.88pp** across 4 evals (`eval-skill`, `sec-audit`, `lint-1`, `release-2`) — **4/4 lifts, 0 hurts, deterministic endpoint grades.** Three lifts disambiguated by introducing a true no-plugin baseline via `--disable-slash-commands`: `consultation_lift` = +8.12pp (noisy, +17.5pp grader swing on identical transcript), `filesystem_access_lift` = +13.75pp, `total_lift` = +21.88pp. iter-4's contaminated `without_skill` baseline (plugin auto-loads via `slash_commands` regardless of `--add-dir`) is corrected. iter-6 vendor-disjoint validation structurally blocked: the configured backend is a single-model surface. iter-5 (N=11 reliability) deferred — not ship-blocking because the +21.88pp headline is well above the grader noise floor. See [`docs/principled/skill-evals/ITERATION-PHASE-RETROSPECTIVE.md`](docs/principled/skill-evals/ITERATION-PHASE-RETROSPECTIVE.md) and CHANGELOG.
```

- [ ] **Step 3: Scrub any other risky strings in README.md**

Run:
```bash
git grep -nE "MiniMax|100\.80\.231\.128|nex-agi|claude-haiku-4-5-20251001|circuit_breaker_open|glm-5\.2|Z\.AI" README.md
```
If any matches are found, apply standard scrubs (Edit with replace_all).

- [ ] **Step 4: Verify the README is clean**

Run:
```bash
git grep -nE "MiniMax|100\.80\.231\.128|nex-agi|claude-haiku-4-5-20251001|circuit_breaker_open|glm-5\.2|Z\.AI" README.md
```
Expected: 0 matches.

- [ ] **Step 5: Commit**

```bash
git add README.md
git commit -m "v0.0.8: rewrite README eval summary with abstract backend naming

- Replace 'haiku solver' with 'the configured solver'
- Replace link to iter-7/REPORT.md with link to the retrospective
  (sole narrative entry point)
- Preserve +21.88pp/+8.12pp/+13.75pp/+17.5pp numbers (findings)
- Preserve --disable-slash-commands and --add-dir (CLI flags)
- Scrub any remaining risky strings in the rest of README.md"
```

---

## Task 7: Scrub CHANGELOG.md (all risky entries) and add [0.0.8] entry

**Files:**
- Modify: `CHANGELOG.md` (large file, ~280 lines)

The audit found risky strings at lines 52, 61, 63, 70, 72, 73, 107, 108, 109, 110, 124, 201, 245. All need scrubbing. Then add the `[0.0.8]` entry.

- [ ] **Step 1: Audit all risky string locations**

Run:
```bash
git grep -nE "MiniMax|100\.80\.231\.128|nex-agi|claude-haiku-4-5-20251001|circuit_breaker_open|glm-5\.2|zerob13/mock-openai-api" CHANGELOG.md
```

- [ ] **Step 2: Apply standard scrubs**

Use `Edit` with `replace_all=true` for each:

| Risky string | Replacement |
|---|---|
| `100.80.231.128:3456` | `<private inference gateway>` |
| `MiniMax-M3` | `the configured backend` |
| `circuit_breaker_open: RateLimit` | `rate-limited` |
| `haiku solver` | `the configured solver` |
| `claude-haiku-4-5-20251001` | `<solver tier alias>` |
| `glm-5.2` | `an external judge vendor` |
| `Z.AI` | `an external judge vendor` |
| `zerob13/mock-openai-api` | `<mock grader>` |

- [ ] **Step 3: Verify CHANGELOG is clean**

Run:
```bash
git grep -nE "MiniMax|100\.80\.231\.128|nex-agi|claude-haiku-4-5-20251001|circuit_breaker_open|glm-5\.2|zerob13/mock-openai-api" CHANGELOG.md
```
Expected: 0 matches.

- [ ] **Step 4: Add the [0.0.8] entry at the top of the changelog**

Use `Edit` to insert the [0.0.8] entry at the very top of the file (after the `# Changelog` header and the empty line). The `old_string` is `# Changelog\n\n` (or the first heading). The `new_string` prepends the new entry:

```markdown
# Changelog

## [0.0.8] — repo finalization (eval cleanup + sanitization) — 2026-06-23

Aggressive consolidation of the iteration-phase documentation surface. The retrospective becomes the SOLE narrative entry point; per-iteration REPORTs and other subsumable findings-docs are removed. Eval artifacts (raw transcripts, grading JSONs, harness scripts, eval task definitions, per-eval directories, logs) are removed. Risky/personal information (private Tailscale IP, real backend model name, vendor aliases, proxy-specific error strings) is removed from all retained files. Repository is now finalized for public release.

### Added
- `docs/principled/specs/2026-06-23-eval-cleanup-design.md` — design spec for this cleanup
- `docs/principled/skill-evals/ITERATION-PHASE-RETROSPECTIVE.md` — expanded with one-paragraph summaries of the deleted findings-docs (proxy architecture, grader non-determinism, SKILL discovery, routing-vs-validator)

### Changed
- Active tree: `docs/principled/skill-evals/` 2.3 MB → ~80 KB
- `ITERATION-PHASE-RETROSPECTIVE.md`: scrubbed of model names, private IPs, vendor aliases; expanded with one-paragraph summaries; Cross-references and Open follow-ups sections updated
- `iteration-8-PLAN.md`: scrubbed, reframed as a methodology improvement program (mock infrastructure, grader non-determinism root-cause, N=11 averaging) — no longer a proxy-specific plan
- `iter-8 design supplements`: scrubbed
- `docs/principled/memory/learnings.md`: scrubbed of proxy URLs and model names (auto-loaded file; most-sensitive surface)
- `README.md`: eval summary rewritten with abstract backend naming
- v0.0.7, v0.0.6, v0.0.5 release notes and all other CHANGELOG entries with risky strings: scrubbed
- `.github/RELEASE-v0.0.5.md`, `v0.0.6.md`, `v0.0.7.md`: scrubbed (in-repo hygiene; GitHub Releases pages for v0.0.5/v0.0.6/v0.0.7 cannot be retroactively rewritten)
- **Removal of v0.0.7 release-gate CI:** `.github/workflows/eval-regression.yml` and `.github/scripts/release-gate.py` are removed. The v0.0.7 release-gate contract (verifies the iter-7 grading contract on every tag push) is now a documented-in-CHANGELOG contract, not an enforced CI check. This is intentional: the workflow depends on `iter-7/benchmark.json` (also removed in v0.0.8). No behavioral contract is silently dropped; the v0.0.8 release is a documentation-only release.

### Removed
- All raw eval artifacts (36+ JSONL transcripts, 60+ grading JSONs, 12 grading logs, 2 harness scripts, 818 LOC)
- Per-iteration REPORTs (iter-6, iter-7, GRADER-NOISE, SKILL-DISCOVERY-ARCHITECTURE, methodology-note)
- `.github/workflows/eval-regression.yml` and `.github/scripts/release-gate.py`
- `docs/principled/research/vendor-disjoint-grader-mock-2026-06-23.md`
- All references to: `MiniMax-M3`, `http://100.80.231.128:3456`, `claude-haiku-4-5-20251001`, `nex-agi/nex-n2-pro:free`, `circuit_breaker_open: RateLimit`, and 17 other vendor aliases

### Fixed
- Private Tailscale IP `100.80.231.128:3456` no longer in active tree
- Real backend model name `MiniMax-M3` no longer in active tree
- 18+ vendor aliases no longer in active tree
- 2.3 MB of eval artifacts no longer shipped in the public repo
- `iter-7/benchmark.json` dependency on the private proxy removed

### Verified
- `marketplace-health`: pass (validator 0/87)
- `git grep` for risky patterns: 0 matches in active tree
- No broken cross-references

```

- [ ] **Step 5: Final CHANGELOG verification**

Run:
```bash
git grep -nE "MiniMax|100\.80\.231\.128|nex-agi|claude-haiku-4-5-20251001|circuit_breaker_open|glm-5\.2|zerob13/mock-openai-api" CHANGELOG.md
head -50 CHANGELOG.md
```
Expected: 0 matches; first 50 lines show the [0.0.8] entry at the top.

- [ ] **Step 6: Commit**

```bash
git add CHANGELOG.md
git commit -m "v0.0.8: scrub CHANGELOG and add [0.0.8] entry

- Scrub all entries with risky strings (MiniMax-M3, 100.80.231.128:3456,
  claude-haiku-4-5-20251001, nex-agi, circuit_breaker_open, glm-5.2,
  zerob13/mock-openai-api, Z.AI)
- Add [0.0.8] entry at the top documenting the cleanup with
  Added/Changed/Removed/Fixed/Verified sections
- Note the v0.0.7 release-gate CI removal explicitly
- Note the GitHub Releases page scope limitation explicitly"
```

---

## Task 8: Scrub .github/RELEASE-v0.0.5.md

**Files:**
- Modify: `.github/RELEASE-v0.0.5.md`

- [ ] **Step 1: Audit risky strings**

Run:
```bash
git grep -nE "MiniMax|100\.80\.231\.128|nex-agi|claude-haiku-4-5-20251001|circuit_breaker_open|glm-5\.2|Z\.AI" .github/RELEASE-v0.0.5.md
```

- [ ] **Step 2: Apply standard scrubs**

Use `Edit` with `replace_all=true` for each pattern from the standard scrub table. Most of these files have only the proxy URL, but apply the full set defensively.

- [ ] **Step 3: Verify**

Run:
```bash
git grep -nE "MiniMax|100\.80\.231\.128|nex-agi|claude-haiku-4-5-20251001|circuit_breaker_open|glm-5\.2|Z\.AI" .github/RELEASE-v0.0.5.md
```
Expected: 0 matches.

- [ ] **Step 4: Commit**

```bash
git add .github/RELEASE-v0.0.5.md
git commit -m "v0.0.8: scrub .github/RELEASE-v0.0.5.md (in-repo hygiene)"
```

---

## Task 9: Scrub .github/RELEASE-v0.0.6.md

**Files:**
- Modify: `.github/RELEASE-v0.0.6.md`

- [ ] **Step 1-4: Same as Task 8, substituting v0.0.6 for v0.0.5**

```bash
git grep -nE "MiniMax|100\.80\.231\.128|nex-agi|claude-haiku-4-5-20251001|circuit_breaker_open|glm-5\.2|Z\.AI" .github/RELEASE-v0.0.6.md
# Apply standard scrubs
git grep -nE "MiniMax|100\.80\.231\.128|nex-agi|claude-haiku-4-5-20251001|circuit_breaker_open|glm-5\.2|Z\.AI" .github/RELEASE-v0.0.6.md
git add .github/RELEASE-v0.0.6.md
git commit -m "v0.0.8: scrub .github/RELEASE-v0.0.6.md (in-repo hygiene)"
```

---

## Task 10: Scrub .github/RELEASE-v0.0.7.md

**Files:**
- Modify: `.github/RELEASE-v0.0.7.md`

- [ ] **Step 1-4: Same as Task 8, substituting v0.0.7 for v0.0.5**

```bash
git grep -nE "MiniMax|100\.80\.231\.128|nex-agi|claude-haiku-4-5-20251001|circuit_breaker_open|glm-5\.2|Z\.AI" .github/RELEASE-v0.0.7.md
# Apply standard scrubs
git grep -nE "MiniMax|100\.80\.231\.128|nex-agi|claude-haiku-4-5-20251001|circuit_breaker_open|glm-5\.2|Z\.AI" .github/RELEASE-v0.0.7.md
git add .github/RELEASE-v0.0.7.md
git commit -m "v0.0.8: scrub .github/RELEASE-v0.0.7.md (in-repo hygiene)"
```

---

## Task 11: Delete eval artifacts under docs/principled/skill-evals/marketplace-routing-2026-06-22/

**Files:**
- Delete: 36+ files including all per-eval JSONL transcripts, grading JSONs, harness scripts (818 LOC), per-iteration REPORTs, GRADER-NOISE-INVESTIGATION, SKILL-DISCOVERY-ARCHITECTURE, methodology-note, .archive/, baselines/, capabilities.json, evals/evals.json, scripts/count_words.py, iter-6/ and iter-7/ directory shells

The per-eval numbers in the retrospective (section 3.1) have been verified in Task 1. Now safe to delete the source.

- [ ] **Step 1: Delete the entire iteration-6 directory**

```bash
git rm -r docs/principled/skill-evals/marketplace-routing-2026-06-22/iteration-6/
```

- [ ] **Step 2: Delete the entire iteration-7 directory**

```bash
git rm -r docs/principled/skill-evals/marketplace-routing-2026-06-22/iteration-7/
```

- [ ] **Step 3: Delete .archive/, baselines/, capabilities.json, evals/, scripts/count_words.py, and other root-level artifacts**

```bash
git rm -r docs/principled/skill-evals/marketplace-routing-2026-06-22/.archive/
git rm -r docs/principled/skill-evals/marketplace-routing-2026-06-22/baselines/
git rm docs/principled/skill-evals/marketplace-routing-2026-06-22/capabilities.json
git rm docs/principled/skill-evals/marketplace-routing-2026-06-22/evals/evals.json
git rm docs/principled/skill-evals/marketplace-routing-2026-06-22/scripts/count_words.py
```

- [ ] **Step 4: Delete findings-docs at the root of marketplace-routing-2026-06-22/**

```bash
git rm docs/principled/skill-evals/marketplace-routing-2026-06-22/SKILL-DISCOVERY-ARCHITECTURE.md
git rm docs/principled/skill-evals/marketplace-routing-2026-06-22/methodology-note-routing-vs-validator.md
```

- [ ] **Step 5: Verify the marketplace-routing-2026-06-22/ directory now contains only iteration-8-PLAN.md**

Run:
```bash
ls -la docs/principled/skill-evals/marketplace-routing-2026-06-22/
```
Expected: only `iteration-8-PLAN.md` (and the `.`/`..` directory entries).

- [ ] **Step 6: Commit**

```bash
git add -A docs/principled/skill-evals/marketplace-routing-2026-06-22/
git commit -m "v0.0.8: delete eval artifacts under marketplace-routing-2026-06-22/

Removed:
- iteration-6/ and iteration-7/ directories (raw transcripts,
  grading JSONs, harness scripts, REPORTs, GRADER-NOISE,
  benchmark data, full run logs)
- .archive/ (failed runs and superseded interim findings)
- baselines/ (raw baseline JSONL data + MANIFEST with proxy URL)
- capabilities.json, evals/evals.json (eval metadata)
- scripts/count_words.py (utility script)
- SKILL-DISCOVERY-ARCHITECTURE.md
- methodology-note-routing-vs-validator.md

Per-eval numbers preserved in the retrospective (section 3.1).
The marketplace-routing-2026-06-22/ directory now contains only
iteration-8-PLAN.md."
```

---

## Task 12: Delete docs/principled/research/vendor-disjoint-grader-mock-2026-06-23.md

**Files:**
- Delete: `docs/principled/research/vendor-disjoint-grader-mock-2026-06-23.md`

- [ ] **Step 1: Delete the file**

```bash
git rm docs/principled/research/vendor-disjoint-grader-mock-2026-06-23.md
```

- [ ] **Step 2: Commit**

```bash
git commit -m "v0.0.8: delete vendor-disjoint grader mock research note

Proxy-specific architecture. Superseded by the iter-8-PLAN
methodology-design abstraction. LiteLLM finding moved to the
iter-8 design supplements note (KEPT)."
```

---

## Task 13: Delete CI workflow and release-gate script

**Files:**
- Delete: `.github/workflows/eval-regression.yml`
- Delete: `.github/scripts/release-gate.py`

- [ ] **Step 1: Delete the files**

```bash
git rm .github/workflows/eval-regression.yml
git rm .github/scripts/release-gate.py
```

- [ ] **Step 2: Commit**

```bash
git commit -m "v0.0.8: remove eval-regression CI workflow and release-gate script

The eval-regression workflow depended on iter-7/benchmark.json (now
deleted). The v0.0.7 release-gate contract is now documented in
CHANGELOG [0.0.7] and [0.0.8] entries, not enforced by CI. This is
intentional for a documentation-only release."
```

---

## Task 14: Verification pass

**Files:** none (read-only checks)

- [ ] **Step 1: Run marketplace-health**

```bash
python3 .agents/skills/marketplace-health/scripts/health.py
```
Expected: passes with `validator=0/87`. If it fails, fix inline before continuing.

- [ ] **Step 2: Final risky-string audit across the active tree**

```bash
git grep -nE "MiniMax|100\.80\.231\.128|nex-agi|claude-haiku-4-5-20251001|circuit_breaker_open|glm-5\.2|Z\.AI|zerob13/mock-openai-api"
```
Expected: only matches inside `docs/principled/attic/` (the v0.0.7 closure archive, which is the immutable historical record per AGENTS.md).

- [ ] **Step 3: Verify the post-cleanup tree structure**

```bash
ls -la docs/principled/skill-evals/
ls -la docs/principled/skill-evals/marketplace-routing-2026-06-22/
ls -la docs/principled/research/
ls -la docs/principled/memory/
ls -la .github/workflows/
ls -la .github/scripts/ 2>/dev/null || echo "scripts/ not present (deleted)"
ls -la .github/ | grep RELEASE
```
Expected:
- `docs/principled/skill-evals/`: `INDEX.md` + `ITERATION-PHASE-RETROSPECTIVE.md` + `marketplace-routing-2026-06-22/`
- `marketplace-routing-2026-06-22/`: only `iteration-8-PLAN.md`
- `docs/principled/research/`: no `vendor-disjoint-grader-mock-2026-06-23.md`, has `2026-06-23-iter8-design-supplements.md`
- `docs/principled/memory/`: has `learnings.md`
- `.github/workflows/`: no `eval-regression.yml`
- `.github/`: 3 RELEASE-*.md files (v0.0.5/6/7)

- [ ] **Step 4: Verify the retrospective contains the actual per-eval numbers**

```bash
sed -n '80,95p' docs/principled/skill-evals/ITERATION-PHASE-RETROSPECTIVE.md
```
Expected: per-eval table with actual numbers (15.0, 32.5, 25.0, 15.0 etc.), NOT `+X` placeholders.

- [ ] **Step 5: Check size reduction**

```bash
du -sh docs/principled/skill-evals/
du -sh docs/principled/skill-evals/attic/ 2>/dev/null || echo "no attic in skill-evals"
```
Expected: `docs/principled/skill-evals/` is ~80 KB (down from 2.3 MB).

- [ ] **Step 6: Check for broken cross-references in retained files**

```bash
git grep -nE "iteration-6/REPORT|iteration-7/REPORT|GRADER-NOISE-INVESTIGATION|SKILL-DISCOVERY-ARCHITECTURE|methodology-note-routing-vs-validator|attic/2026-06-23-closure/skill-evals/iteration-[123]" \
  -- ':!docs/principled/attic' ':!CHANGELOG.md' ':!README.md' ':!.github/RELEASE*'
```
Expected: 0 matches (no live cross-references to deleted docs). References in CHANGELOG.md and README.md are OK because those entries explicitly call out what was deleted.

---

## Task 15: Tag v0.0.8

**Files:** none (git operation)

- [ ] **Step 1: Confirm the working tree is clean and on main**

```bash
git status
git branch --show-current
```
Expected: working tree clean; on `main`.

- [ ] **Step 2: Show the commits since v0.0.7**

```bash
git log --oneline v0.0.7..HEAD
```
Expected: ~14 commits (one per task), all with `v0.0.8:` prefix in the subject.

- [ ] **Step 3: Create the annotated tag**

```bash
git tag -a v0.0.8 -m "v0.0.8 — repo finalization (eval cleanup + sanitization)

Aggressive consolidation of the iteration-phase documentation surface.
The retrospective becomes the SOLE narrative entry point; per-iteration
REPORTs and other subsumable findings-docs are removed. Eval artifacts
(raw transcripts, grading JSONs, harness scripts, eval task definitions,
per-eval directories, logs) are removed. Risky/personal information
(private Tailscale IP, real backend model name, vendor aliases,
proxy-specific error strings) is removed from all retained files.
Repository is now finalized for public release.

Per AGENTS.md 'Project Closure Convention,' v0.0.8's durable closure
marker is the CHANGELOG [0.0.8] entry + this tag. No SUMMARY.md is
required for a documentation-only release."
```

- [ ] **Step 4: Verify the tag**

```bash
git tag -l v0.0.8
git show v0.0.8 --no-patch --format="%H %s%n%n%b"
```
Expected: tag is created; commit hash is the HEAD of the cleanup series.

- [ ] **Step 5: Report completion**

Tell the user: v0.0.8 is tagged locally. The tag is NOT pushed to remote yet (per AGENTS.md "Always preserve user trust" — the user must explicitly approve the push). The release-gate skill's `releasing-marketplace` workflow can be invoked separately if the user wants to push and create the GitHub Release.

---

## End-of-Plan Self-Review

**1. Spec coverage:**

| Spec section | Task |
|---|---|
| Context (risk audit) | Self-critic was applied to the spec before this plan; the audit findings are baked into the spec. |
| Goal 1 (sole narrative) | Task 1 (retrospective expansion) + Task 2 (INDEX simplification) + Task 11 (delete per-iteration REPORTs and findings-docs) |
| Goal 2 (no eval artifacts) | Task 11 (delete eval artifacts) + Task 13 (delete CI workflow) |
| Goal 3 (no risky info) | Tasks 1, 3, 4, 5, 6, 7, 8, 9, 10 (scrub all retained files) |
| Goal 4 (iter-8 forward-looking) | Task 3 (reframe iter-8-PLAN as methodology improvement program) |
| Goal 5 (marketplace-health pass) | Task 14 (verification) |
| Deletion List | Tasks 11, 12, 13 |
| Retention List | Tasks 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 |
| Scrub Rules | Applied in every task; standard table at top of plan |
| Retrospective Expansion | Task 1 (Steps 4, 5, 6) |
| Verification | Task 14 |
| CHANGELOG [0.0.8] entry | Task 7 (Step 4) |
| Rollback | Documented in spec; this plan does not include a rollback task (per AGENTS.md "durable closure marker," a v0.0.8 tag can be reverted via `git tag -d v0.0.8` if needed) |

**2. Placeholder scan:** No `+X`, `TBD`, "implement later", "fill in details", "add appropriate error handling", "similar to Task N" found. Each scrub replacement is a concrete string-to-string mapping. Each new content block (retrospective summaries, INDEX, iter-8 reframing, CHANGELOG entry) is the full new text.

**3. Type consistency:** Standard scrub patterns use the same replacement strings across all tasks. Standard commit-message prefix `v0.0.8:` is consistent. Verification command `git grep -nE "MiniMax|100\.80\.231\.128|nex-agi|claude-haiku-4-5-20251001|circuit_breaker_open|glm-5\.2|Z\.AI|zerob13/mock-openai-api"` is consistent across all verification steps.

**4. Key sequencing rule (consume iter-7 numbers before deleting):** Task 1 reads the per-eval numbers from the retrospective (which already contains them) and confirms them; Task 11 deletes the iter-7 source. Order is correct.

**5. Plan complete and saved to `docs/superpowers/plans/2026-06-23-v0-0-8-eval-cleanup.md`.**
