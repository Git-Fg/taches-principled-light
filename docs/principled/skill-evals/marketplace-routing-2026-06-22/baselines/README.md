# Baseline transcript cache

Canonical `--disable-slash-commands` baseline transcripts for the marketplace-routing evals. Reusable across iter-N iterations to skip the ~20 min regeneration cost of the 4 baseline runs.

## What's in here

4 files (`<eval_id>.jsonl`), each a full Claude Code session transcript captured via `claude --print --output-format stream-json`. Every baseline was generated in `/private/tmp/empty-claude-project` (no plugin/marketplace files) with `slash_commands: []` and `permissionMode: bypassPermissions`.

| Eval | Events | Size (KB) | MD5 |
|------|-------:|----------:|-----|
| `eval-eval-skill` | 6 | 43.5 | `5bce0f70fd49029891c5e1ea30cf79a5` |
| `eval-lint-1` | 13 | 27.1 | `822b0c0c77eaab9a356352e9446880b6` |
| `eval-release-2` | 9 | 21.6 | `983984a810a180646511b5196b6b2128` |
| `eval-sec-audit` | 12 | 28.6 | `d628f2f2e45c8cb37312d36d4baa9af8` |

Full metadata: see `MANIFEST.json` (init event fields, model, session_id, timestamp, proxy config).

## Why cache baselines

The baseline is a **fixed reference point** — same prompt, same empty cwd, same model, same `--disable-slash-commands` invocation. It does not depend on the marketplace plugin state under test. As long as the prompt and proxy config are stable, the baseline transcript is stable across iterations.

iter-7 used these as the `--disable-slash-commands` reference for the 3-config lift decomposition (`baseline → plugin_only → plugin_with_add_dir`). Reusing the baselines in iter-8+ saves 4 transcript generations (~20 min wall time, ~$1.20 in proxy credits).

## When to NOT reuse

- The eval prompt for an `eval_id` changes → regenerate.
- The proxy config changes (model, base URL, toolset) → regenerate.
- The `claude` CLI changes in a way that affects the baseline output shape (init fields, tool result format) → regenerate.
- You're testing a hypothesis that requires a fresh baseline (e.g., grader drift, prompt sensitivity) → regenerate.

## How to use

The iter-7 runner (`iteration-7/scripts/run_iteration_7.py`) is the reference integration. It exposes a `cache_baseline(eval_id, eval_dir)` helper:

```python
def cache_baseline(eval_id: str, eval_dir: Path) -> bool:
    """Copy canonical baseline from baselines/ to eval_dir/baseline_skill.jsonl.
    Returns True on cache hit, False on miss (caller should regenerate)."""
    src = REPO / "docs/principled/skill-evals/marketplace-routing-2026-06-22/baselines" / f"{eval_id}.jsonl"
    dst = eval_dir / "baseline_skill.jsonl"
    if not src.exists():
        return False
    shutil.copy2(src, dst)
    return True
```

To force regeneration, delete the canonical file from `baselines/` and re-run, or pass `--refresh-baseline` (if the runner supports it).

## Source of truth

- **Generation command**: see `iteration-7/scripts/run_iteration_7.py:run_baseline()` (`--print --output-format stream-json --model claude-haiku-4-5-20251001 --add-dir /private/tmp/empty-claude-project --disable-slash-commands --dangerously-skip-permissions`)
- **Eval prompts**: `iteration-7/evals/<eval_id>.md` (the user utterance passed via stdin)
- **Proxy**: `http://100.80.231.128:3456` (inference-gateway; haiku/sonnet/opus all silently map to `MiniMax-M3` — see `iteration-6/REPORT.md`)

## Iter-7 contamination finding (why this cache exists)

iter-4's `without_skill` baseline was contaminated by the auto-loaded marketplace plugin (agent invoked `/crafting-skills` at event 4 of the `without_skill.jsonl`). iter-4's +4.94pp = filesystem_access_lift only. The true baseline requires `--disable-slash-commands` to prevent the global plugin load. See `iteration-7/REPORT.md` "Authoritative finding" section for the full diagnosis.

These 4 transcripts are the iter-7 production of the corrected baseline. They are the reference for all future iter-N comparisons.
