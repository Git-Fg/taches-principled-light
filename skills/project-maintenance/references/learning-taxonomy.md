# Learning Taxonomy

Classification system for extracting insights from plan artifacts.

## Categories

| Category | Signal | Example |
|----------|--------|---------|
| **TECHNICAL** | Tool choice, library gotcha, API behavior, config issue | "bcrypt's compare function requires exact buffer encoding" |
| **PROCESS** | Workflow failure, estimation miss, dependency surprise | "Phase 2 took 3x longer due to undocumented API changes" |
| **PATTERN** | Reusable approach that worked, abstraction that simplified | "Data-driven state machine replaced 12 conditional branches" |
| **ANTI-PATTERN** | Approach that failed, abstraction that complicated | "Premature extraction into 5 functions made debugging harder" |
| **DECISION** | Architectural choice with rationale and outcome | "Chose JWT over sessions for mobile compatibility — enabled offline auth" |

## Confidence Scoring

| Score | Meaning | When to Use |
|-------|---------|-------------|
| 1 | Speculative | Pattern observed once, may be coincidental |
| 2 | Preliminary | Pattern observed 2+ times, no contradictory evidence |
| 3 | Moderate | Pattern confirmed across multiple files/modules |
| 4 | Strong | Pattern validated by test results or benchmark data |
| 5 | Certain | Universal truth for this codebase (e.g., "we use ESM") |

Default confidence is 2. Score 4-5 requires evidence (test output, benchmark, git history).

## Extraction Signals

Scan plan artifacts for these patterns:

- **Error messages** → likely TECHNICAL or ANTI-PATTERN
- **Deviation log entries** → likely PROCESS or DECISION
- **Comments starting with "worked around" or "had to"** → likely TECHNICAL or ANTI-PATTERN
- **Verification that passed on first try** → likely PATTERN
- **"surprisingly" or "unexpectedly"** → likely TECHNICAL or PROCESS
- **Choice between alternatives** → DECISION
- **Time estimates vs actual** → PROCESS

## Output Format

Each learning entry:

```markdown
### [CATEGORY] [confidence-score] Title

**Source:** plan-id, date
**Insight:** One sentence capturing the learning.
**Evidence:** File path or specific observation that supports this.
**Action:** What to do differently next time.
```

## Deduplication Rules

Before appending to `docs/principled/memory/learnings.md`:

1. Search existing learnings for same category + topic overlap
2. If match found: reinforce (increment confidence, merge evidence) — do not create duplicate entry
3. If contradictory: keep both with notes on when each applies
4. If novel: append as new entry
