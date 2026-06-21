# Memory Locations

Claude Code stores memory in multiple locations, each with a different lifecycle and audience. This reference is the canonical list of paths the project's `project-maintenance` skill audits and cleans.

## Required Reading Order

You MUST read this file BEFORE running `MEMORY-AUDIT`, `MEMORY-DEDUP`, `MEMORY-ARCHIVE`, or `MEMORY-CLEAN`. Do NOT skip this reference — paths vary by platform and Claude Code version.

## Locations

| Path | Owner | Lifetime | Audience |
|------|-------|----------|----------|
| `~/.claude/projects/*/memory/MEMORY.md` | Auto-memory (per project) | Long-lived; survives sessions | Cross-session project facts |
| `~/.claude/agent-memory/*/MEMORY.md` | Per-agent (e.g., critic, implementer) | Long-lived; agent-scoped | Agent-specific learnings across sessions |
| `~/.claude/agent-memory/*/*.md` | Per-agent supporting files | Long-lived | Same as above |
| `docs/principled/memory/learnings.md` | Project memory (plugin-managed) | Long-lived; reviewed periodically | Project-wide durable learnings |
| `docs/principled/scratch/` | Working scratchpad | Short-lived; cleaned after each phase | Current phase working state |

## Detection Rules

- **Per-project memory** lives at `~/.claude/projects/<encoded-cwd>/memory/MEMORY.md` where `<encoded-cwd>` is the absolute working directory with `/` replaced by `-`.
- **Per-agent memory** is one directory per agent under `~/.claude/agent-memory/`. The agent name matches the agent definition filename (e.g., `critic`, `implementer`).
- **Project memory** (`docs/principled/memory/`) is the canonical sink for both `project-maintenance` PLAN-ARCHIVE and `refine` MEMORIZE mode. Read this when running MEMORY-AUDIT.
- **Scratch** (`docs/principled/scratch/`) is ephemeral. Treat all entries as candidates for archive after the current phase closes.

## Issue Types

- **Duplicates** — same content hash or >80% keyword overlap across two or more files. Use inline duplicate detection (read files, compute Jaccard similarity at threshold 0.7) to detect.
- **Contradictions** — conflicting facts about the same entity (e.g., one file says library `X` is required, another says it is deprecated). Flag for human review.
- **Obsolescence** — references to deleted files, renamed projects, or removed agents. Detected by greping for paths that no longer exist on disk.
- **Orphans** — entries that belong to projects or agents that no longer exist.
- **Bloat** — individual files exceeding 100KB. Split or summarize.

## Health Scoring

| Score | Issues | Action |
|-------|--------|--------|
| **Green** | 0–1 | No action needed |
| **Yellow** | 2–3 | Schedule cleanup in next maintenance window |
| **Red** | 4+ | Cleanup is urgent — propose MEMORY-CLEAN to user |

## Platform Notes

- All paths above are POSIX-style. On Windows, the `~` expands to `%USERPROFILE%` and the separators are `\` — but Claude Code normalizes to POSIX paths in all internal references.
- The `~/.claude/` directory may be a symlink on systems with sandboxed homes. Resolve with `readlink -f` if scripts report path mismatches.
- Some installations nest `agent-memory` one level deeper (e.g., `~/.claude/agent-memory/<agent>/memory/`). Glob with `**/MEMORY.md` to catch both layouts.

## See Also

- `MEMORY-DEDUP` mode in the parent skill — uses inline duplicate detection (read files, compute Jaccard similarity at threshold 0.7) to find duplicate groups
- `MEMORY-ARCHIVE` mode — moves stale entries to `~/.claude/archive/memory/{category}/{date}/` with a recovery manifest
- `refine` MEMORIZE mode — the other writer to `docs/principled/memory/learnings.md`
- `rules-orchestration` SYNC mode — the reader that promotes memory entries to committed rules
