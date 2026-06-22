# Self-Eval Protocol for Local Meta-Skills

The 4 local meta-skills in `.agents/skills/` (`marketplace-validator`, `marketplace-health`, `ingesting-skills`, `releasing-marketplace`) should be evaluated using the same 8-stage methodology documented in `skills/evaluating-skills/SKILL.md`. This file is a condensed protocol for maintainers who want to validate that a local skill actually improves agent behavior on the workflows it claims to support.

## When to run

- After creating a new local skill
- After a substantive refactor of an existing local skill
- After trimming or rewording the description (routing signal)
- Before tagging a new marketplace version that includes local-skill changes

## Quick version (3 stages, ~15 min)

The full 8-stage loop is rigorous but heavy for small changes. A condensed 3-stage version captures most of the signal:

### Stage A — Routing test (10 utterances)

Run the script in `scripts/routing-test.md` (or the inline `python3 -c` one-liner in `evaluating-local-skills.md`) against 10 utterances covering the skill's main use cases. For each utterance, the top-scoring skill by description-token overlap should be the one under test. Target: **≥7/10 clear wins** (top score strictly greater than the runner-up). Ties indicate description overlap with adjacent skills — add a distinguishing trigger phrase or sharpen the negative trigger.

### Stage B — With-skill vs without-skill on 3 prompts

For each of the 3 evals in `evals/evals.json`:

1. **with_skill**: invoke the local skill on the eval prompt (e.g., `python3 .agents/skills/<skill>/scripts/<script>.py <args>` for skill scripts, or load the skill's body for workflow-only skills).
2. **without_skill**: solve the same eval prompt using only the marketplace's `crafting-skills` skill and the agent's native tools.
3. Compare the two transcripts (raw output + duration). The skill should produce measurably better output (correctness, completeness, formatting) in less time, or cover ground the without-skill run cannot.

Target: **≥2/3 prompts** show a clear, attributable improvement.

### Stage C — Adversarial review (1 critic dispatch)

Spawn a `general-critic` subagent with the lens `"review the local skill's behavior against its own description and evals"`. The critic should:
- Verify the skill does what its description claims
- Identify any silent failures (the skill runs but produces wrong output)
- Flag any side effects (the skill modifies files outside its scope, e.g., `marketplace-health` should not modify the marketplace, only report)
- Score the skill on the 5-dimension rubric in `skills/evaluating-skills/references/behavioral-review.md`

Target: **no HIGH findings** in the critic's report.

## Full 8-stage version

When the condensed version is insufficient (e.g., a major rework, or a new meta-skill whose behavior is hard to characterize), run the full loop from `skills/evaluating-skills/SKILL.md`. Stages 1-8, with adapters from `references/runtime-adapters.md` for each target CLI.

## Workspace layout

```
.principled/evaluations/<skill-name>/<date>/
├── evals.json              # the 3 prompts (copied from .agents/skills/<skill>/evals/)
├── with_skill/             # transcripts from with-skill runs
│   ├── eval-1.jsonl
│   ├── eval-2.jsonl
│   └── eval-3.jsonl
├── without_skill/          # baseline transcripts
│   ├── eval-1.jsonl
│   ├── eval-2.jsonl
│   └── eval-3.jsonl
├── benchmark.json          # aggregate from scripts/aggregate_benchmark.py
└── benchmark.md            # human-readable summary
```

## When NOT to run

- **Trivial edits** (typo fix, license field, version bump): not worth a full eval pass. Trust the validator + health sweep.
- **Cosmetic refactors** (whitespace, comment cleanup): the 3-stage condensed version is overkill. Skip.
- **New skills that aren't behavior-changing** (e.g., documentation-only, manifest metadata): the description routing test is sufficient.

## Reuse

- `skills/evaluating-skills/` — the canonical 8-stage loop and 5-dimension rubric
- `skills/general-critic` — the adversarial reviewer for stage C
- `.agents/skills/marketplace-validator/scripts/validate.py` — the description + frontmatter lint
- `.agents/skills/marketplace-validator/scripts/routing-test.py` — the routing test script (if present)
