# Iter-3.1 Status (in progress)

The per-skill `--add-dir` experiment is running in the background
(`pid 43924`, ~14 min elapsed at last check). It tests whether the 5
Bucket A3 discovery failures are caused by:

- **H1**: Plugin skills shadowing marketplace skills in the discovery path
- **H2**: Marketplace descriptions don't surface in the discovery path
- **H3**: Choice paralysis from 26+ marketplace skills in scope

## Method

For each Bucket A3 eval, run the with-skill config TWO ways:

1. **CONTROL**: full marketplace in scope (matches iter-2 behavior)
2. **TREATMENT**: only the EXPECTED marketplace skill in scope (no plugins)

If treatment lifts and control doesn't, the issue is choice paralysis (H3) or
plugin shadowing (H1) — NOT description content (H2).

## Bucket A3 evals (5)

| eval_id | expected_skill_dir | hypothesis |
|---|---|---|
| `ingest-1` | `.agents/skills/ingesting-skills` | shadowed by `superpowers:writing-skills` (H1) |
| `ingest-2` | `.agents/skills/ingesting-skills` | shadowed by `superpowers:writing-skills` (H1) |
| `lint-2` | `.agents/skills/marketplace-validator` | shadowed by `taches:skill-authoring` (H1) |
| `craft-create` | `skills/crafting-skills` | shadowed by `superpowers:writing-skills` (H1) — direct evidence in iter-3 transcript |
| `craft-review` | `skills/crafting-skills` | shadowed by `superpowers:writing-skills` (H1) |

## Progress (snapshot)

Total runs: **15** (5 evals × 3 configs). See `eval-<id>/<config>/run.jsonl`
for completed runs and `eval-<id>/experiment_metadata.json` for per-eval config.

Updated in real time by the background script. Last update at the bottom of this
file when committed.

## When the experiment completes

1. The background script prints "[iter-3.1] done."
2. Grade each config with the iter-3 grader.
3. Compare lift per condition: `without_skill` baseline vs `with_full_marketplace`
   (matches iter-3) vs `with_skill_only` (treatment).
4. Write `RESULTS.md` with hypothesis verdict.
5. Commit + update INDEX.md.

## If the experiment times out

- The script runs each `claude` invocation with a 180s timeout.
- Partial results are preserved in `eval-<id>/<config>/run.jsonl`.
- A failed run has a non-empty `run.stderr` and an empty or near-empty `run.jsonl`.
- Archive what's there and write `RESULTS.md` with what's complete.