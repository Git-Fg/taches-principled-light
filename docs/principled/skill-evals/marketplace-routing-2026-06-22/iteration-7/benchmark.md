# Iteration 7 Phase A — Three-Config Lift Disambiguation (N=4)

## Configuration
- Judge model: `sonnet`
- Solver model: `haiku`
- Cache state: fresh (cleared 2026-06-23)
- Lift threshold: ±5pp for skill_neutral

## Three Configs
- `baseline`: `--disable-slash-commands --add-dir /tmp/empty` (no plugin)
- `plugin_only`: default plugin loading, `--add-dir /tmp/empty` (plugin + slash commands, no filesystem)
- `plugin_with_add_dir`: default plugin loading, `--add-dir REPO` (plugin + filesystem)

## Three Lifts
- **consultation_lift** (baseline → plugin_only): IF=+16.25 GC=+0.00 overall=+8.12
- **filesystem_access_lift** (plugin_only → plugin_with_add_dir): IF=+15.00 GC=+12.50 overall=+13.75
- **total_lift** (baseline → plugin_with_add_dir): IF=+31.25 GC=+12.50 overall=+21.88

### iter-4 reference (filesystem access lift only): +4.94pp

## Per-eval Results

| Eval | iter-4 mech | baseline | plugin_only | plugin_with_add_dir | Consult Δ | FS Δ | Total Δ |
|------|-------------|---------:|------------:|--------------------:|---------:|-----:|--------:|
| eval-skill | consultation | 0.0 | 0.0 | 15.0 |  +0.0 | +15.0 | +15.0 |
| sec-audit | consultation | 0.0 | 32.5 | 32.5 | +32.5 |  +0.0 | +32.5 |
| lint-1 | file-access | 0.0 | 0.0 | 25.0 |  +0.0 | +25.0 | +25.0 |
| release-2 | file-access | 25.0 | 25.0 | 40.0 |  +0.0 | +15.0 | +15.0 |

## Per-mechanism breakdown (consultation_lift)

| iter-4 mechanism | mean overall Δ | n |
|------------------|---------------:|--:|
| consultation | +16.25 | 2 |
| file-access | +0.00 | 2 |

## Per-mechanism breakdown (total_lift)

| iter-4 mechanism | mean overall Δ | n |
|------------------|---------------:|--:|
| consultation | +23.75 | 2 |
| file-access | +20.00 | 2 |

## Verdict distribution

- consultation_lift: {'skill_neutral': 3, 'skill_lifts_quality': 1}
- filesystem_access_lift: {'skill_lifts_quality': 3, 'skill_neutral': 1}
- total_lift: {'skill_lifts_quality': 4}

## Notes

- This is N=4 (4-eval subset). Below Yagubyan 2026's N=11 reliability threshold; do not interpret magnitude as effect size.
- 4 transcripts reused from iter-4 (plugin_only + plugin_with_add_dir).
- 4 transcripts freshly generated for baseline (--disable-slash-commands).
- The total_lift is what iter-4 SHOULD have measured; it is ≥ the iter-4 +4.94pp (the iter-4 number is a lower bound on total_lift).