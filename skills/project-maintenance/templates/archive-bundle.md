# Archive Bundle Template

Structure for archived plan artifacts in `docs/principled/attic/{milestone}/{plan-id}/`.

## Directory Structure

```
{plan-id}/
├── PLAN.md          # Original plan (copied)
├── SUMMARY.md       # Execution summary (copied)
├── metadata.md      # Archive metadata (generated)
└── scratchpad/      # Related scratch files (copied, if any)
```

## metadata.md Format

```markdown
# Archive: {plan-id}

**Archived:** {date}
**Milestone:** {milestone-name}
**Phase:** {phase-number}
**Status:** {completed | abandoned}
**Learnings extracted:** {count} (see docs/principled/memory/learnings.md)

## Files
- {file1}: {description}
- {file2}: {description}

## Key Decisions
- {decision 1}
- {decision 2}
```

## Rules

- **Copy, never move** — originals stay in `docs/principled/plans/phases/`
- **Include all artifacts** — PLAN.md, SUMMARY.md, any scratch files referenced in SUMMARY.md
- **metadata.md is generated** — not copied from source, created during archival
- **Scratch files** — only include those referenced in SUMMARY.md or PLAN.md, not the entire scratch directory
