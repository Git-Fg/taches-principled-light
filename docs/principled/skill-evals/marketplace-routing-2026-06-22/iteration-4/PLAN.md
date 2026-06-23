# Iter-4 Plan — Cache Refresh + v0.0.3 Re-run

## Background

iter-3 reported a mean lift of +8.69pp across 17 evals (6 lifts / 11 neutrals / 0 hurts). The iter-3.1 per-skill `--add-dir` experiment then revealed two problems:

1. **Stale plugin cache** (`~/.claude/plugins/cache/taches-principled-light/`, v2.0.0 installed 2026-06-21) — has 22 SKILL.md directories with names that don't match the v0.0.3 working marketplace. The agent's `slash_commands` listing reflected the cache, not the live working directory.

2. **H1 (plugin shadowing) confirmed** in iter-3.1 craft-create eval — the v2.0.0 cache's `skill-authoring` description explicitly redirected creation tasks to `superpowers:writing-skills`, which is why the agent picked the plugin skill over the marketplace skill.

3. **H4 (upstream heuristic failure)** confirmed — in 6 of 9 completed iter-3.1 runs, the agent invoked zero skills and just responded with text.

iter-4 measures the lift **after** the cache is refreshed, so the eval reflects the actual v0.0.3 marketplace state.

## What we learned about cache invalidation

Web research confirms two open bugs in Claude Code's plugin cache:

- [Issue #14061](https://github.com/anthropics/claude-code/issues/14061) (open since 2025-12-15): `/plugin update` does NOT invalidate plugin cache. Workaround: `rm -rf ~/.claude/plugins/cache/{marketplace-name}/`.
- [Issue #17361](https://github.com/anthropics/claude-code/issues/17361) (open since 2026-01-10): plugin cache never refreshes even with `autoUpdate: true`.

These are documented upstream limitations. The eval harness must refresh the cache manually before each iter-4 run.

## Cache refresh smoke test (2026-06-23)

Cleared the stale cache:
```bash
rm -rf ~/.claude/plugins/cache/taches-principled-light/
```

After cache clear, smoke-tested with `claude --print --add-dir <REPO>`:
- slash_commands now exposes 20 `taches-principled-light:*` skills with **v0.0.3 names** (was 22 with v2.0.0 aliases)
- `crafting-skills` is visible (was `skill-authoring` in v2.0.0)
- `engineering-mcp` is visible (was `mcp-expertise` in v2.0.0)
- `generating-ideas` is visible (was `ideation` in v2.0.0)
- ...10 more renames

Smoke-tested craft-create eval after cache refresh:
- **Agent invoked `taches-principled-light:crafting-skills`** directly via Skill tool
- **H1 resolved** for craft-create (was `superpowers:writing-skills` in iter-3.1)
- This confirms the cache refresh fixes the shadowing mechanism at the description-content level

## What iter-4 measures

iter-4 re-runs the iter-3 evaluation against the cache-refreshed marketplace to measure:

1. **Actual v0.0.3 lift** — does the +8.69pp iter-3 baseline hold, increase, or decrease when the eval reflects the current marketplace state?
2. **Bucket A3 true failures** — were the 5 Bucket A3 neutrals (ingest-1, ingest-2, lint-2, craft-create, craft-review) really discovery failures, or were they artifacts of the v2.0.0 cache?
3. **Bucket A1 A2 retro-classification** — now that we have proper context, do plan-multi, task-small, and research get re-classified correctly?
4. **Bucket B/C re-measurement** — the 6 lifts and 5 neutrals re-measured against cache-refreshed state.

## iter-4 design

### Setup

1. **Cache refresh**: `rm -rf ~/.claude/plugins/cache/taches-principled-light/` (one-time before iter-4 starts; harness should also do it before each run for safety).

2. **Run script**: reuse `iteration-3/scripts/run_iteration_3.py` (already supports N=17 evals × 2 configs).

3. **Eval set**: the 17 evals from iter-3 (excluding `rust-clippy`, which had no iter-2 transcript).

4. **Solver**: `haiku` chain via inference-gateway proxy (matches iter-3).

5. **Judge**: `sonnet` (homogeneous, NOT heterogeneous like iter-3) — implements the Wataoka 2024 same-family bias mitigation as a follow-up to iter-3's mixed judge.

### Code changes

1. **`iteration-3/scripts/run_iteration_3.py`**: add a cache-refresh step at the top:
   ```python
   import shutil
   cache_dir = Path.home() / ".claude" / "plugins" / "cache" / "taches-principled-light"
   if cache_dir.exists():
       print(f"[iter-4] refreshing stale plugin cache at {cache_dir}")
       shutil.rmtree(cache_dir)
   ```

2. **`iteration-3/scripts/grader.py`**: keep the consultation assertion fix from iter-3; no changes needed.

3. **`docs/principled/skill-evals/marketplace-routing-2026-06-22/iteration-4/`**: new directory mirroring iter-3 structure:
   - `eval-<id>/{with_skill,without_skill,grading_with_skill,grading_without_skill,comparison}.json`
   - `benchmark.json` and `benchmark.md`
   - `REPORT.md` (corrected from iter-3's methodology notes)
   - `scripts/run_iteration_4.py` (copy of run_iteration_3.py with cache-refresh step)

### Anti-shadowing markers (optional, post-iter-4)

After iter-4 baseline is established, experiment with adding anti-shadowing markers to the 3 marketplace skills that historically shadow plugin skills:
- `crafting-skills` (shadowed by `superpowers:writing-skills`)
- `ingesting-skills` (shadowed by `superpowers:writing-skills` for "import skill" tasks)
- `marketplace-validator` (shadowed by `taches-principled-light:skill-authoring` in v2.0.0 cache)

Suggested marker pattern: `Use this instead of superpowers:writing-skills for [specific case]`.

These markers can be added in iter-4.1 after measuring the baseline.

## Expected outcomes

If cache was the dominant artifact:
- Bucket A3 (5 neutrals) should improve: lift on ingest-1, ingest-2, lint-2, craft-create, craft-review.
- craft-create should pick `crafting-skills` reliably (confirmed by smoke test).
- Mean lift should increase from +8.69pp to something larger.

If cache was not the dominant artifact:
- Bucket A3 may stay neutral; the routing-heuristic failure (H4) is upstream.
- iter-4 should document the H4 finding and recommend next steps.

## Wall-clock budget

- Cache refresh: instant
- 17 evals × 2 configs = 34 runs at 30-60s each on healthy proxy: 17-34 min
- Grading: ~5 min
- Total: ~22-40 min on a warm proxy

## Success criteria

1. iter-4 REPORT.md written and committed.
2. Lift comparison table: iter-3 vs iter-4, per-eval delta.
3. Bucket A3 re-classification: which went from neutral to lift, lift to neutral, or stayed.
4. Updated INDEX.md with iter-4 entry.

## Known limitations

- iter-4 measures a single trial per eval; no N=3 reliability.
- The `display-name` frontmatter key (added in Claude Code 2.1.186) might enable cleaner skill aliasing in the future, but iter-4 doesn't test it.

## Self-critic findings (added 2026-06-23)

### Weakness 1: Judge change conflates two experiments

The original plan switches to `sonnet` homogeneous judge, which conflates the cache-refresh effect with the same-family-bias-mitigation effect. Cannot attribute lift cleanly.

**Fix:** run iter-4 in two phases:

- **iter-4 Phase A**: cache refresh + same heterogeneous judges as iter-3. Measures pure cache-refresh effect. Direct numerical comparison to iter-3.
- **iter-4 Phase B (optional, follow-up)**: + sonnet homogeneous judge. Measures combined effect. Only if Phase A is conclusive.

### Weakness 2: Anti-shadowing markers deferred too aggressively

If Phase A shows some Bucket A3 evals still fail, the remaining failures could be:
- Routing-heuristic (H4) — can't fix from marketplace
- Description-quality (need anti-shadowing markers)

To distinguish: include a small set of evals with anti-shadowing markers in Phase A. If those lift and the cache-only evals don't, the markers help.

**Fix:** Phase A includes 2 evals with anti-shadowing markers added (e.g., `crafting-skills` with "Use this instead of superpowers:writing-skills for [X]"). Compare to Phase A cache-only evals.

### Weakness 3: No control for judge change

Even with the two-phase design, Phase A is the only fully controlled comparison (cache refresh only). Phase B cannot be cleanly attributed.

**Fix:** document Phase A as the canonical iter-4 measurement. Phase B is exploratory.

### Weakness 4: Single trial per eval

iter-3 had ±13.6% flip rate per Yagubyan 2026. iter-4 single-trial results will have similar noise. The lift threshold (±5pp) partially absorbs this but a 6pp lift could be noise.

**Fix:** for the 6 lifts in iter-3, run N=3 trials. For Bucket A3 (originally neutral), N=2 trials minimum to confirm "still neutral".

### Updated wall-clock budget

- Phase A cache refresh only, heterogeneous judge, single trial: ~25-40 min (similar to iter-3)
- + N=3 trials for 6 lifts: +90-180 min (large additional cost)
- + N=2 trials for 5 Bucket A3: +25-50 min
- Phase B sonnet judge: ~25-40 min
- **Recommended minimum:** Phase A single trial only (~30 min). Defer multi-trial to a separate session.

## Recommended execution plan

1. **Session 1 (this session, after plan review)**: Phase A cache refresh only, single trial. ~30 min. Produce iter-4 REPORT.md.
2. **Session 2 (follow-up)**: N=3 reliability study on the 6 lifts. ~90-180 min. Produce reliability report.
3. **Session 3 (follow-up)**: Phase B sonnet judge if Phase A is conclusive. ~30 min.
4. **Optional session 4**: anti-shadowing marker experiment. ~60 min.

This breaks the work into bounded sessions with clean handoffs. Each session ends with a written report and committed artifacts.

## Doc version

v1.1 — 2026-06-23. Self-critic added; recommended execution plan split into 4 bounded sessions.