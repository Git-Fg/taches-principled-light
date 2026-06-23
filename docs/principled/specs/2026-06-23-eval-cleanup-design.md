# Eval Cleanup & Sanitization Design

**Date:** 2026-06-23
**Status:** Approved (Approach B — aggressive consolidation)
**Author:** brainstormed with the user
**Supersedes:** v0.0.7 closure as the iteration phase's finalization release
**Tag:** v0.0.8 (proposed)

## Context

v0.0.7 (commit `06027bb`) archived 13 MB of historical eval iterations (iter-1/2/3/3.1/4, two plans, two design specs, one design note, 13 research work products) into `docs/principled/attic/2026-06-23-closure/`. The active tree still contains a 2.3 MB eval footprint under `docs/principled/skill-evals/marketplace-routing-2026-06-22/` that needs to be either consolidated or removed.

The user has directed:

1. **Delete** any remaining element related to evaluation of skills
2. **Keep and document** all findings, relevant elements, and information gathered
3. **Remove** any personal/risky information, "like proxy rs" (proxy results, the proxy script, the proxy URL, vendor model names, vendor aliases)

A risk-surface audit (run on 2026-06-23) confirmed the following are baked into the active tree:

- Private Tailscale IP `100.80.231.128:3456` in `baselines/MANIFEST.json:25`, `.github/workflows/eval-regression.yml:23`, and (historically) `.github/RELEASE-v0.0.5.md:124`, `.github/RELEASE-v0.0.6.md`, `.github/RELEASE-v0.0.7.md`, `CHANGELOG.md`, `docs/principled/memory/learnings.md`, `docs/principled/research/2026-06-23-iter8-design-supplements.md`, `docs/principled/research/vendor-disjoint-grader-mock-2026-06-23.md`
- Real backend model name `MiniMax-M3` in 8+ files including `README.md`, `CHANGELOG.md`, `ITERATION-PHASE-RETROSPECTIVE.md`, `iteration-6/REPORT.md`, `iteration-7/REPORT.md`, `iteration-7/GRADER-NOISE-INVESTIGATION.md`, `SKILL-DISCOVERY-ARCHITECTURE.md`, `iteration-8-PLAN.md`, `baselines/MANIFEST.json`
- Vendor aliases `claude-haiku-4-5-20251001`, `nex-agi/nex-n2-pro:free`, and 17 others all silently mapping to `MiniMax-M3`, referenced in `iteration-6/REPORT.md`, `baselines/MANIFEST.json`, `INDEX.md`
- Z.AI-specific error string `circuit_breaker_open: RateLimit` in `iteration-6/REPORT.md`, `RETROSPECTIVE.md`, `CHANGELOG.md`
- Eval scripts (`run_iteration_6.py`, `run_iteration_7.py`, 818 LOC) and a private-proxy CI workflow
- 36+ raw eval JSONL transcripts, 60+ grading JSONs, 12 grading logs
- 4 historical release notes (`.github/RELEASE-v0.0.5.md` through `v0.0.7.md`) — these are already published on GitHub Releases; in-repo files are scrubbed for repo-internal hygiene, but the public release pages on GitHub cannot be retroactively rewritten
- Auto-loaded durable memory file `docs/principled/memory/learnings.md` contains the proxy URL (lines 30, 73) — more sensitive than a regular doc because it auto-loads in every agent session per AGENTS.md

## Goal

Produce a finalized repo where:

1. The eval-iteration phase is documented by **one** canonical narrative document (`ITERATION-PHASE-RETROSPECTIVE.md`) — single source of truth.
2. The active tree contains **no** eval artifacts (no raw transcripts, no grading JSONs, no harness scripts, no eval task definitions, no per-eval directories, no logs, no eval JSONL files, no eval-regression CI).
3. The active tree contains **no** risky/personal information (no private IPs, no real model names, no vendor aliases, no proxy URLs, no `circuit_breaker_open` strings).
4. The `iteration-8-PLAN.md` and `iter-8 design supplements` notes remain as forward-looking design notes, scrubbed of proxy-specific and model-specific identifiers.
5. The repo can still pass `marketplace-health` and the release-gate contract is documented in CHANGELOG and the retrospective. Per AGENTS.md "Project Closure Convention," v0.0.8's durable closure marker is a `CHANGELOG.md [0.0.8]` entry + the v0.0.8 release tag. No `SUMMARY.md` is required for this documentation-only release.

## Non-Goals

- No changes to marketplace manifest, plugin metadata, skill files, or skill descriptions.
- No changes to the `evaluating-skills` skill itself (it is a marketplace *capability*, not an eval *artifact*).
- No new behavioral data; v0.0.8 is a repository-finalization release.
- No new eval runs; iter-8 is designed, not executed.

## Post-Cleanup Tree

```
docs/principled/skill-evals/
├── INDEX.md                                              [minimal: pointer to retrospective only]
├── ITERATION-PHASE-RETROSPECTIVE.md                      [sole narrative; scrubbed of model names and proxy URLs]
└── marketplace-routing-2026-06-22/
    └── iteration-8-PLAN.md                                [forward-looking design; scrubbed of proxy-specific refs]

docs/principled/research/
└── 2026-06-23-iter8-design-supplements.md                [scrubbed of proxy IPs and model names]

docs/principled/memory/
└── learnings.md                                          [auto-loaded; scrubbed of proxy URLs and model names]

.github/
├── (eval-regression.yml DELETED)
├── (scripts/release-gate.py DELETED)
├── RELEASE-v0.0.5.md                                     [scrubbed]
├── RELEASE-v0.0.6.md                                     [scrubbed]
└── RELEASE-v0.0.7.md                                     [scrubbed]

README.md                                                  [eval summary section: model-name-abstracted]
CHANGELOG.md                                               [v0.0.8 entry added; v0.0.7/v0.0.6 and all other entries with risky strings scrubbed]
```

Estimated active tree reduction: `2.3 MB → ~80 KB` in `skill-evals/` (96% reduction in skill-evals/ footprint).

## Deletion List

### Eval artifacts under `docs/principled/skill-evals/marketplace-routing-2026-06-22/`

| Path | Reason |
|---|---|
| `.archive/` (entire directory) | Failed runs (iter-2.5) and superseded interim findings (iter-3). No canonical content. |
| `baselines/` (entire directory) | Raw baseline JSONL data; `MANIFEST.json` contains the private Tailscale IP and vendor model names. |
| `capabilities.json` | Eval metadata; not a finding. |
| `evals/evals.json` | Eval task definitions; not a finding. |
| `scripts/count_words.py` | Utility script, 115 LOC, not a finding. |
| `iteration-6/benchmark_iter4_vs_iter6.json` | Raw benchmark data. |
| `iteration-6/benchmark.json` | Raw benchmark data. |
| `iteration-6/eval-eval-skill/`, `eval-lint-1/`, `eval-release-2/`, `eval-sec-audit/` | Per-eval raw grading JSONs, comparisons, and grading logs. |
| `iteration-6/iter6_full_run.log` | Full run log; no canonical content. |
| `iteration-6/scripts/run_iteration_6.py` | Proxy script (the actual proxy code). |
| `iteration-6/REPORT.md` | Subsumed by retrospective. |
| `iteration-7/benchmark.json` | Raw benchmark data. |
| `iteration-7/benchmark.md` | Human-readable benchmark summary; subsumed by retrospective. |
| `iteration-7/eval-eval-skill/`, `eval-lint-1/`, `eval-release-2/`, `eval-sec-audit/` | Per-eval raw transcripts (`*.jsonl`), grading JSONs, and comparison data. |
| `iteration-7/iter7_full_run.log` | Full run log. |
| `iteration-7/scripts/run_iteration_7.py` | Harness script (703 LOC). |
| `iteration-7/REPORT.md` | Subsumed by retrospective. |
| `iteration-7/GRADER-NOISE-INVESTIGATION.md` | Subsumed by retrospective. |
| `methodology-note-routing-vs-validator.md` | Subsumed by retrospective. |
| `SKILL-DISCOVERY-ARCHITECTURE.md` | Subsumed by retrospective. |

### Per-iteration `iter-*` directory shells (kept as empty after deletion, or removed)

`iteration-6/` and `iteration-7/` directory shells should be **removed entirely** after the contents are deleted (the directory structure adds noise without information). `marketplace-routing-2026-06-22/` should be **kept** as the directory shell for `iteration-8-PLAN.md` (forward-looking design).

### Research directory

| Path | Reason |
|---|---|
| `docs/principled/research/vendor-disjoint-grader-mock-2026-06-23.md` | Proxy-specific architecture; superseded by the iter-8-PLAN abstraction. |
| `docs/principled/research/2026-06-23-iter8-design-supplements.md` | **Keep**, scrubbed. LiteLLM finding is generalizable; mock-proxy details are abstracted. |

### CI

| Path | Reason |
|---|---|
| `.github/workflows/eval-regression.yml` | Depends on `iter-7/benchmark.json` (deleted). Documents the release-gate contract in CHANGELOG instead. |
| `.github/scripts/release-gate.py` | Companion to the deleted workflow. |

### Archive

The v0.0.7 closure archive at `docs/principled/attic/2026-06-23-closure/` is **not** modified. It is the historical record per AGENTS.md "Project Closure Convention."

## Retention List (with scrub rules)

| Path | Scrub rules |
|---|---|
| `docs/principled/skill-evals/ITERATION-PHASE-RETROSPECTIVE.md` | See "Scrub Rules" below. Becomes the **sole narrative entry point**. Cross-references section updated to remove references to deleted docs. "Open follow-ups" section updated to match the reframed iter-8 (no longer a concrete plan, now forward-looking). |
| `docs/principled/skill-evals/INDEX.md` | Simplified to a 1-paragraph pointer: "Read `ITERATION-PHASE-RETROSPECTIVE.md` for the canonical narrative of the iteration phase (2026-06-22 → 2026-06-23)." |
| `docs/principled/skill-evals/marketplace-routing-2026-06-22/iteration-8-PLAN.md` | Scrubbed. **Reframing:** iter-8 was originally designed to solve the proxy single-model problem by introducing a local mock. The reframed plan drops the proxy-specific premise and is presented as a **methodology improvement program**: (1) design mock infrastructure for grader isolation, (2) root-cause grader non-determinism (the +17.5pp sec-audit swing on identical transcripts), (3) N=11 multi-run averaging. The plan becomes a methodology-design document, not a proxy-specific design. |
| `docs/principled/research/2026-06-23-iter8-design-supplements.md` | Scrubbed. LiteLLM and Claude Code CLI flag inventory kept as generalizable findings; mock-proxy details abstracted. |
| `docs/principled/memory/learnings.md` | Scrubbed (auto-loaded; most-sensitive surface). All `100.80.231.128:3456` references → `<private inference gateway>`. All `MiniMax-M3` references → `the configured backend`. The LiteLLM lesson is preserved (LiteLLM is a real public project, not risky). |
| `README.md` | Eval-summary section rewritten to use abstract backend naming. The 4-line summary currently mentions "haiku solver", the +21.88pp headline, the 4-eval subset, and the iter-7 REPORT link — the rewrite preserves the +21.88pp number and the 4-eval subset, but uses `the configured solver` instead of `haiku solver` and links to the retrospective instead of iter-7/REPORT.md. |
| `CHANGELOG.md` | All entries with risky strings scrubbed, not just v0.0.6/v0.0.7. Lines 52, 61, 63, 70, 72, 73, 107, 108, 109, 110, 124, 201, 245 are known to contain `MiniMax-M3`, `100.80.231.128:3456`, `circuit_breaker_open`, `zerob13/mock-openai-api`, or specific vendor aliases — all scrubbed. New `[0.0.8]` entry added. The v0.0.7 release-gate-CI claim is preserved but qualified: the workflow was a v0.0.7 add-on and is removed in v0.0.8 (see `[0.0.8]` entry). |
| `.github/RELEASE-v0.0.5.md` | Scrubbed (historical release note, repo-internal hygiene). |
| `.github/RELEASE-v0.0.6.md` | Scrubbed (historical release note, repo-internal hygiene). |
| `.github/RELEASE-v0.0.7.md` | Scrubbed (historical release note, repo-internal hygiene). |

**Note on historical release pages:** `.github/RELEASE-v*.md` files are sanitized in-repo for the public clone. The corresponding GitHub Releases pages for v0.0.5/v0.0.6/v0.0.7 cannot be retroactively rewritten; the in-repo scrub closes the gap for anyone reading the source tree.

## Scrub Rules

The following risky strings are replaced consistently across all retained files.

| Risky string pattern | Replacement | Notes |
|---|---|---|
| `MiniMax-M3` | `the configured backend` | Narrative + config files |
| `http://100.80.231.128:3456` | `<private inference gateway>` | In code/config: `<private inference gateway>`. In narrative: remove the URL entirely. |
| `claude-haiku-4-5-20251001` | `<solver tier alias>` | MANIFEST, REPORTs (now deleted) |
| `nex-agi/nex-n2-pro:free` | `<vendor alias>` | iter-6 REPORT (deleted) |
| `qwen`, `llama`, `gpt-4o`, `gemini-*`, `deepseek-*`, `mistral-*`, `claude-3*`, `doubao`, `kimi`, `minimax`, `phi-4`, `mixtral`, `command-r`, `jamba`, `cerebras`, `fireworks`, `deepinfra` | `<vendor alias>` | iter-6 REPORT (deleted) — these all mapped to the same backend; in the retrospective, replace the full list with the phrase `<vendor alias>` (or, where brevity matters, with the count "18+ tier aliases"). |
| `circuit_breaker_open: RateLimit` | `rate-limited` | iter-6 REPORT (deleted), RETROSPECTIVE, CHANGELOG |
| `haiku solver` | `the configured solver` | In eval-context (README's "haiku solver" eval summary line, CHANGELOG, INDEX, REPORTs) replace. In skills-reference context (`skills/crafting-skills/references/frontmatter-complete.md:154` lists `sonnet, opus, haiku` as Claude Code model ID values) **KEEP** — that is a Claude Code CLI reference, not an eval-iteration reference. |
| `bda20918d4b7d0b7245bd12b59b09e58` | KEEP | iter-7 REPORT (deleted), RETROSPECTIVE — hash, not risky |
| `+21.88pp`, `+8.12pp`, `+13.75pp`, `+17.5pp`, `+4.94pp`, `+4.37pp` | KEEP | Numbers are findings |
| `--disable-slash-commands`, `--add-dir`, `--mcp-config`, `--bare` | KEEP | CLI flags, not risky |
| `https://github.com/Git-Fg/taches-principled-light` | KEEP | Public repo URL |
| arxiv.org URLs (Xu et al. 2026, Gorinova et al. 2026) | KEEP | Public papers |
| `MiniMax-M3` in `CHANGELOG.md` | `the configured backend` | Same as above |
| `the proxy is single-model`, `single-model gateway` | `the configured backend is single-model`, `single-model gateway` | RETROSPECTIVE, INDEX, REPORTs |
| `haiku/sonnet/opus/nex-agi` lists | `the configured solver tier aliases` | RETROSPECTIVE, INDEX |
| `Z.AI` | `an external judge vendor` | Where it identifies the specific vendor; the existence of a vendor-disjoint option is the finding, not the vendor name |

## Retrospective Expansion (required for B)

`ITERATION-PHASE-RETROSPECTIVE.md` is the sole narrative; it must be expanded to absorb the unique content of the deleted docs that the user might want to reference. Specifically:

1. **Add a brief per-eval table** (eval-skill, sec-audit, lint-1, release-2 × 3 configs = headline numbers) — currently only the aggregate is in the retrospective. The table is reconstructed from iter-7/REPORT.md (slated for deletion) and should look like:

   | Eval | total_lift (pp) | consultation_lift (pp) | filesystem_access_lift (pp) | Notable |
   |---|---|---|---|---|
   | eval-skill | +X | +X | +X | (consultation-heavy) |
   | sec-audit | +X | +X | +X | +17.5pp grader swing on bit-identical transcript `bda20918d4b7d0b7245bd12b59b09e58` |
   | lint-1 | +X | +X | +X | (structure-with-compare_args heavy) |
   | release-2 | +X | +X | +X | (multi-mode selection heavy) |
   | **Mean (4 evals)** | **+21.88** | **+8.12** | **+13.75** | **4/4 lifts, 0 hurts** |

   The implementation MUST extract the per-cell numbers from the iter-7 REPORT before deletion. The +X placeholders above must be filled with the actual numbers from `docs/principled/skill-evals/marketplace-routing-2026-06-22/iteration-7/REPORT.md` (lines covering the 4-eval × 3-config matrix). The `Notable` column preserves the eval-specific findings the aggregate hides.

2. **Add a brief proxy architecture summary** (1 short paragraph: "the configured backend is single-model; all tier aliases map to it; one external judge is rate-limited") — replaces iter-6 REPORT's detail.

3. **Add a brief grader non-determinism summary** (1 short paragraph: "grader temperature=0 is not deterministic; sec-audit showed +17.5pp swing on bit-identical transcript; the +21.88pp headline is well above the noise floor and the consultation lift's direction is robust despite the noise") — replaces GRADER-NOISE-INVESTIGATION.

4. **Add a brief SKILL discovery architecture summary** (1 short paragraph: "the marketplace plugin auto-loads skills into slash_commands regardless of --add-dir; only --disable-slash-commands prevents auto-load; the 4-bucket routing taxonomy is A1 proxy errors, A2 partial discovery, A3 true discovery failures, A4 baseline") — replaces SKILL-DISCOVERY-ARCHITECTURE.

5. **Add a brief routing vs validator note** (1 short paragraph: "iter-4's without_skill baseline was contaminated because --add-dir does not prevent plugin auto-load; iter-7's true baseline uses --disable-slash-commands; the 3-config harness decomposes total_lift into consultation_lift + filesystem_access_lift") — replaces methodology note.

6. **Update the Cross-references section** to remove references to deleted docs (iter-6/REPORT.md, iter-7/REPORT.md, GRADER-NOISE-INVESTIGATION.md, SKILL-DISCOVERY-ARCHITECTURE.md, methodology-note-routing-vs-validator.md, .archive/ paths). Add references to the per-eval table, the proxy architecture summary, the grader non-determinism summary, etc., now in the retrospective itself.

7. **Update the Open follow-ups section** to match the reframed iter-8 (methodology improvement program, no longer a concrete iter-8 plan tied to the proxy). The follow-ups become: (a) mock-infrastructure design when a vendor-disjoint judge is needed, (b) grader non-determinism root-cause when +17.5pp swings recur, (c) N=11 multi-run averaging when evaluator reliability matters.

After expansion, the retrospective grows from 293 lines to ~400 lines. It is now the **single source of truth** for the iteration phase.

## Verification

After implementation:

1. `python3 .agents/skills/marketplace-health/scripts/health.py` — pass with `validator=0/0` (note: original spec said `0/87`; the reduction to 0 reflects codifying the 8 marketplace extension keys in `ALLOWED_FRONTMATTER` + the sibling-name sweep + whitelisting 7 documented description-word-count exceptions).
2. `git grep -nE "MiniMax|100\.80\.231\.128|nex-agi|claude-haiku-4-5-20251001|circuit_breaker_open"` returns 0 matches in the active tree (i.e., the working tree, excluding `docs/principled/attic/`).
3. `git grep -nE "MiniMax|100\.80\.231\.128|nex-agi"` in the active tree returns 0 matches.
4. `INDEX.md` and `ITERATION-PHASE-RETROSPECTIVE.md` are the only two files in `docs/principled/skill-evals/` (plus `iteration-8-PLAN.md` under `marketplace-routing-2026-06-22/`).
5. No broken cross-references in retained files. The retrospective's "Cross-references" section is updated to remove references to deleted docs.
6. `docs/principled/memory/learnings.md` is scrubbed (most-sensitive surface; auto-loaded every session).
7. The retrospective's per-eval table contains the actual numbers (not +X placeholders) extracted from iter-7/REPORT.md before deletion. **Verification: open the retrospective, find the per-eval table, confirm each cell is a number, not a placeholder.**
8. `CHANGELOG.md` `[0.0.8]` entry documents the cleanup with: Added (none), Changed (active tree 2.3 MB → 80 KB; one canonical narrative; release-gate CI removed; GitHub Releases page scope limitation noted), Removed (eval artifacts and findings-docs; see metadata for inventory), Fixed (private Tailscale IP, real model name, vendor aliases removed from active tree).

## CHANGELOG [0.0.8] Entry Sketch

```markdown
## [0.0.8] — repo finalization (eval cleanup + sanitization) — 2026-06-23

Aggressive consolidation of the iteration-phase documentation surface. The retrospective becomes the SOLE narrative entry point; per-iteration REPORTs and other subsumable findings-docs are removed. Eval artifacts (raw transcripts, grading JSONs, harness scripts, eval task definitions, per-eval directories, logs) are removed. Risky/personal information (private Tailscale IP, real backend model name, vendor aliases, proxy-specific error strings) is removed from all retained files. Repository is now finalized for public release.

### Added
- `docs/principled/specs/2026-06-23-eval-cleanup-design.md` — design spec for this cleanup
- `docs/principled/skill-evals/ITERATION-PHASE-RETROSPECTIVE.md` — expanded with per-eval table and one-paragraph summaries of the deleted findings-docs (proxy architecture, grader non-determinism, SKILL discovery, routing-vs-validator)

### Changed
- Active tree: `docs/principled/skill-evals/` 2.3 MB → ~80 KB
- `ITERATION-PHASE-RETROSPECTIVE.md`: scrubbed of model names, private IPs, vendor aliases; expanded with per-eval table and one-paragraph summaries of the deleted findings-docs (proxy architecture, grader non-determinism, SKILL discovery, routing-vs-validator); Cross-references and Open follow-ups sections updated
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
- `marketplace-health`: pass (validator 0/0 — the 8 marketplace extension keys are codified in `ALLOWED_FRONTMATTER`, and 7 documented description-word-count exceptions are whitelisted)
- `git grep` for risky patterns: 0 matches in active tree
- No broken cross-references
```

## Rollback

If v0.0.8 needs to be reverted, the v0.0.7 release tag and the closure archive at `docs/principled/attic/2026-06-23-closure/` preserve the iteration phase. Note: v0.0.8 is a documentation-only change; reverting it reverts no behavioral contracts. The v0.0.7 CHANGELOG entry can be un-scrubbed from git history if needed.

## Resolved Design Decisions

- **What about `.github/RELEASE-v0.0.6.md` (historical)?** → Scrubbed. Reasoning: the user's directive removes risky info from the repo, not just from current docs. Even historical release notes that still ship in the public repo should be sanitized.
- **What about the `evaluating-skills` skill itself?** → Kept. It is a marketplace *capability*, not an eval *artifact*. Removing it would remove a shipped product feature.
- **What about the bit-identical transcript md5 `bda20918d4b7d0b7245bd12b59b09e58`?** → Kept. It is a SHA256-style hash, not risky, and it is the canonical evidence for the grader-non-determinism finding.
- **What about the v0.0.7 closure archive at `docs/principled/attic/2026-06-23-closure/`?** → Not modified. Per AGENTS.md "Project Closure Convention" the archive is the historical record and is immutable. v0.0.8 follows the same closure convention: CHANGELOG `[0.0.8]` entry + v0.0.8 tag are the durable closure markers; no `SUMMARY.md` is required for a documentation-only release.
- **What about `skills/crafting-skills/references/frontmatter-complete.md` reference to `sonnet, opus, haiku`?** → Kept. That reference documents the Claude Code CLI model ID format. It is not an eval-iteration reference and does not name the marketplace's configured backend.
- **What about the `100.80.231.128` reference in `baselines/MANIFEST.json`?** → Whole `baselines/` directory is deleted; no scrub needed.
- **What if the marketplace-health report flags a post-cleanup issue?** → Fix inline. The cleanup must pass `validator=0/0` (originally spec'd as 0/87; reduced after codifying 8 marketplace extension keys + whitelisting 7 documented description-word-count exceptions); if any validator fails, the cleanup is incomplete.
- **What about the GitHub Releases pages for v0.0.5/v0.0.6/v0.0.7?** → Cannot be retroactively rewritten. The in-repo `.github/RELEASE-v*.md` files are scrubbed for repo-internal hygiene (so anyone reading the source tree doesn't see the proxy URL), but the public release pages on GitHub still show the original content. The v0.0.8 CHANGELOG entry documents this scope limitation explicitly. Future releases should follow the same in-repo scrub pattern from the start.
- **What about the cross-references in the v0.0.7 closure archive at `docs/principled/attic/2026-06-23-closure/`?** → The archive is immutable. Dangling cross-references inside the archive are acceptable because the archive is a historical snapshot, not a live document. The archive's own STATUS.md / metadata.md should be the entry point; readers do not follow internal cross-references from the archive back into the active tree.
