# Iteration 2 Metric Bug — `marketplace_skill_md_reads` filter

## Bug

`run_iteration_2.py:170` filters Read tool_use paths with:

```python
"marketplace_skill_md_reads": [
    p for p in reads if str(SKILLS_DIR) in p
],
```

where `SKILLS_DIR = REPO / "skills"` (line 24). This resolves to an absolute path under the top-level `skills/` folder.

The marketplace has **4 skills under `.agents/skills/`** that are also marketplace skills:

```
.agents/skills/marketplace-health/SKILL.md
.agents/skills/marketplace-validator/SKILL.md
.agents/skills/ingesting-skills/SKILL.md
.agents/skills/releasing-marketplace/SKILL.md
```

Reads of these paths are filtered out. The agent IS reading them (confirmed by inspecting `eval-lint-1/with_skill.jsonl` — the agent Read `.agents/skills/marketplace-health/SKILL.md` and `.agents/skills/marketplace-validator/SKILL.md`), but the metric doesn't count them.

## Impact

`material_difference` (line 225-228) compares `with_skill` vs `without_skill` marketplace reads. Both filter through the same broken filter, so the field will report `false` for ALL 18 evals even when the agent's behavior is materially different between configs.

Concrete example from `eval-lint-1/with_skill.jsonl`:

- Read `.agents/skills/marketplace-health/SKILL.md`
- Read `.agents/skills/marketplace-validator/SKILL.md`
- Ran `python3 marketplace-validator/scripts/validate.py skills/` → 0/82
- Ran `python3 marketplace-health/scripts/health.py` → wrote 2026-06-23.md

`marketplace_skill_md_reads: []` despite the agent doing exactly the right thing. The `material_difference: false` is misleading.

## Why this is acceptable for iteration 2

The metric is a known limitation that motivates iteration 3's assertion-based grading (per `iteration-3-design.md`). Iteration 2's purpose is to scale the pilot to N=18 with the Haiku chain and a longer timeout; the metric bug is documented but not fixed because:

1. The bug affects BOTH `with_skill` and `without_skill` equally — relative comparison still meaningful in some ways (both filter out the same paths).
2. The `total_events` and `duration_ms` signals are NOT filtered and remain accurate (lint-1: 30 events/145s with vs 12 events/27s without — agent did meaningfully more work in the with-skill condition).
3. Iteration 3 replaces read-counting with assertion-based grading of the final response, which is a cleaner signal.

## Fix for iteration 3

Two changes:

1. **Widen the filter** to include `.agents/skills/`:

   ```python
   MARKETPLACE_SKILL_DIRS = [REPO / "skills", REPO / ".agents/skills"]
   "marketplace_skill_md_reads": [
       p for p in reads if any(str(d) in p for d in MARKETPLACE_SKILL_DIRS)
   ],
   ```

2. **Switch the primary signal** from read-count to assertion-based grading (already designed in `iteration-3-design.md`):
   - Per-eval `assertions[]` (Anthropic pattern)
   - LLM-as-judge grades final response against assertions
   - `material_difference` becomes `pass_rate_with vs pass_rate_without` (a percentage, not a binary)
   - Reads become a secondary signal, not primary

## Action

- Document (this file) — done.
- Don't fix iter-2 mid-run (would waste 3/18 progress).
- Iter-3 fix lands when `iteration-3-design.md` is implemented.
