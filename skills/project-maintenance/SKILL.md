---
name: project-maintenance
description: >
  Load when wrapping up a project — archiving completed plans, deduplicating
  stale memory, and cleaning auto-memory. Use when the user says 'wrap up this
  plan', 'archive the project', 'clean up files', 'deduplicate memory', or 'this
  project is done'. Do NOT use for managing CLAUDE.md or rules (use
  managing-rules) or capturing individual session insights (use the learn
  command).
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
when_to_use: "Use when wrapping up plans, deduplicating files, or running memory cleanup. CONTRAST: reviewing-and-polishing MEMORIZE (general insights); managing-rules SYNC (codify rules); managing-rules AUDIT (audit rules)."
argument-hint: "[plan-archive|memory-audit|memory-dedup|memory-archive|memory-clean] [path] [--abandoned] [--days 30]"
license: MIT
---

## Routing Guidance

- AFTER plan-lifecycle EXECUTE mode completes and `SUMMARY.md` is created (PLAN-ARCHIVE).
- On long-running VPS instances (30+ days) when memory files have accumulated (MEMORY-AUDIT, MEMORY-DEDUP, MEMORY-CLEAN).
- When the user wants to preserve plan artifacts before starting fresh (PLAN-ARCHIVE).
- When stale memory entries reference deleted projects or agents (MEMORY-ARCHIVE, MEMORY-CLEAN).
- Do NOT use for ongoing plans (no `SUMMARY.md` yet) — plan-lifecycle EXECUTE mode first.
- Do NOT use for auditing rules files — use managing-rules AUDIT mode.
- Do NOT use for capturing general session insights — use reviewing-and-polishing MEMORIZE.

## What This Skill Changes

**Default behavior:** completed plans linger in `docs/principled/plans/phases/`, memory files in `~/.claude/projects/*/memory/` and `~/.claude/agent-memory/` accumulate duplicates and stale entries. The next planning cycle inherits bloated context and the next session loads noise.

**With this skill:** closure work is a first-class step. Plans ship to `docs/principled/attic/` with learnings distilled into `docs/principled/memory/learnings.md`; memory files are deduplicated, stale entries archived, and the next cycle starts clean. Destructive operations default to a dry-run report; the agent then waits for explicit user confirmation before applying any change.

**Why it matters:** archive-preserve-distill is the only step that converts ephemeral execution into durable knowledge. Without it, every plan rediscovers the same lessons and every session loads the same stale context.

## CONTRAST with Other Skills

- **reviewing-and-polishing MEMORIZE** — captures general session insights into `docs/principled/memory/learnings.md` (one writer, ad-hoc insights).
- **THIS, PLAN-ARCHIVE** — bundles completed plan artifacts into `docs/principled/attic/` and distills plan-specific learnings into the same file (the other writer, plan-specific).
- **managing-rules SYNC** — the *reader* of `docs/principled/memory/learnings.md`; promotes durable entries into committed rules. Run PLAN-ARCHIVE (or MEMORIZE) before SYNC.
- **managing-rules AUDIT** — audits CLAUDE.md / `.claude/rules/` hierarchy; this skill's memory modes audit `~/.claude/...` and `docs/principled/memory/`.

## Decision Router

```
IF user says "archive plan", "wrap up plan", "ship plan", "done with plan", or names a plan path → PLAN-ARCHIVE
IF user says "dedup", "deduplicate", "merge memories", "duplicate memories" → MEMORY-DEDUP
IF user says "memory audit", "memory health", "memory overview" → MEMORY-AUDIT
IF user says "archive memory" or "stale memory" → MEMORY-ARCHIVE
IF user says "clean memory", "memory cleanup", "memory maintenance" → MEMORY-CLEAN (dedup + archive in one pass)
IF user names a plan path with --abandoned or --force → PLAN-ARCHIVE with abandonment flag
IF ambiguous → ask: "Which mode? plan-archive, memory-audit, memory-dedup, memory-archive, memory-clean"
```

---

# Project Maintenance

Project hygiene hub with five modes spanning two concerns: plan archival (close the plan lifecycle) and memory hygiene (clean Claude's working memory).

| Mode | Concern | What It Does |
|---|---|---|
| **PLAN-ARCHIVE** | Plans | Discovery → Archive → Condense → Report |
| **MEMORY-AUDIT** | Memory | Discover locations, score health, flag issues |
| **MEMORY-DEDUP** | Memory | Find and merge duplicate memory files |
| **MEMORY-ARCHIVE** | Memory | Move stale entries to archive with manifest |
| **MEMORY-CLEAN** | Memory | Full maintenance: dedup + archive in one pass |

---

## PLAN-ARCHIVE Mode

The closure step in the plan lifecycle. Preserves plan artifacts and distills learnings into reusable knowledge. Copy (never move) originals — plans stay accessible in their original location.

### The 4-Phase Workflow

#### Phase 1: Discovery

1. Locate target plan artifacts: `PLAN.md`, `SUMMARY.md`, related scratchpad files.
2. Identify the milestone/phase from `ROADMAP.md` or directory structure.
3. **HARD PRECONDITION CHECK — ABORT if not satisfied:**
   - **A. Plan completed:** `SUMMARY.md` MUST exist at the same path as `PLAN.md`. If missing, emit `{"status": "failed", "reason": "no-summary", "retry_possible": false, "completed_portion": "discovery", "remediation": "Run plan-lifecycle EXECUTE mode to produce SUMMARY.md, or run /archive with --abandoned flag if the plan was intentionally abandoned."}` and STOP. Do NOT proceed.
   - **B. Plan abandoned (explicit override):** If user passes `--abandoned` or `--force`, accept the plan as abandoned. Archive bundle includes a `STATUS.md` placeholder noting the abandonment and reason (sourced from the user); learnings extraction is limited to whatever `PLAN.md` captured.
**Execution flags — there are no flag-based auto-confirm switches.** PLAN-ARCHIVE recognizes `--abandoned` (or `--force`) to override the `SUMMARY.md` precondition. MEMORY-ARCHIVE and MEMORY-CLEAN recognize `--days N` to override the default 30-day age threshold. The agent always presents a planned-action summary and waits for the user to say "yes" or "proceed" before any file move or delete. This is the safety boundary for all destructive operations. **Enforcement:** Phases 2 (Archive) and 3 (Condense) MUST NOT execute until Phase 1's precondition passes. This is a hard gate, not a warning.

#### Phase 2: Archive

1. Create archive directory at `docs/principled/attic/{milestone}/{plan-id}/`.
2. Copy all discovered artifacts to archive directory.
3. Generate metadata using the template at `templates/archive-bundle.md`.
4. Verify all files copied successfully (compare file counts).

#### Phase 3: Condense

1. Read all archived artifacts (`PLAN.md`, `SUMMARY.md`, scratchpad files).
2. Extract learnings per the taxonomy at `references/learning-taxonomy.md` — you MUST read this reference BEFORE classifying any learning. Do NOT skip it.
3. Classify each learning by category (TECHNICAL, PROCESS, PATTERN, ANTI-PATTERN, DECISION) and confidence (1–5).
4. Append learnings to `docs/principled/memory/learnings.md` with date and plan reference.
5. Deduplicate against existing learnings — merge, don't append duplicates.

#### Phase 4: Report

Present summary:
- Archive path: `docs/principled/attic/{milestone}/{plan-id}/`
- Files archived: {n}
- Learnings extracted: {n} new, {n} reinforced
- Knowledge base updated: yes/no

After archival, consider starting a new cycle with `plan-lifecycle PLAN mode` to scope the next phase or feature. Archive preserves context; planning resumes momentum.

### Boundary Policy

Do NOT archive:
- Plans currently being executed (no `SUMMARY.md`)
- Plans from external projects
- Generated code or build artifacts — only plan documents

---

## MEMORY-AUDIT Mode

Discover and analyze all Claude Code memory locations. Default mode for memory hygiene — run before DEDUP, ARCHIVE, or CLEAN to understand the landscape.

### Process

1. **Discover memory locations** — you MUST read `references/memory-locations.md` for the full path list and detection rules. Do NOT skip this reference; paths vary by Claude Code version and platform.
2. **For each location**: count files, total lines, total size, age range (oldest → newest entry).
3. **Detect issues**:
   - **Duplicates** — same content hash or >80% text overlap
   - **Contradictions** — conflicting facts about same entity
   - **Obsolescence** — references to deleted files/projects
   - **Orphans** — entries for projects that no longer exist
   - **Bloat** — individual files >100KB
4. **Score health** per location: Green (0–1 issues), Yellow (2–3 issues), Red (4+ issues).
5. **Output**:
   ```
   Memory Audit Report
   ===================
   Locations scanned: 5
   Total files: 47
   Total size: ~1.2MB

   ~/.claude/projects/foo/memory/: GREEN
   ~/.claude/agent-memory/critic/: YELLOW (2 duplicates)
   docs/principled/scratch/: RED (1 contradiction, 3 orphans)
   ```

---

## MEMORY-DEDUP Mode

Find and merge duplicate memory entries. Use after AUDIT confirms duplicates exist.

### Process

1. **Run audit** to discover duplicates.
2. **For each duplicate group** identified by the script:
   - Show content preview (first 10 lines each).
   - Read the script's recommendation (default: `keep_newest`).
   - Decide action per group: `keep_newest` / `merge` / `archive_older`.
3. **Dry-run** (default): the script reports findings and the agent proposes actions; the agent performs no destructive writes.
4. **Apply actions manually**: because duplicate detection is a discovery step, archival of the older copy is performed via MEMORY-ARCHIVE mode (or the `trash` command for local removal) — never in-line within this mode.

### Execution

inline duplicate detection (read files, compute Jaccard similarity at threshold 0.7) accepts a positional `directory` argument and `--threshold` (`-t`, default 0.7) and `--format` (`-f`, default `json`). The script is read-only — it never modifies files. Resolution actions are applied by the agent after reviewing the script's output.

```bash
# Dry-run (default): discover and report duplicates as JSON
# Run duplicate detection inline: read all files in the target directory, tokenize, compute pairwise Jaccard similarity. Flag pairs above threshold for review ~/.claude/projects --threshold 0.7

# Text output for human review
# Run duplicate detection inline: read all files in the target directory, tokenize, compute pairwise Jaccard similarity. Flag pairs above threshold for review ~/.claude/agent-memory --threshold 0.7 --format text
```

To apply a `keep_newest` resolution: the older file is moved via MEMORY-ARCHIVE mode (with a manifest entry recording the dedup group and the `keep_newest` decision). Never call the dedup script in an apply mode — it does not have one.

### Output Format

```
Duplicate Group: 3 files, similarity 87%
- ~/.claude/projects/foo/memory/MEMORY.md (updated YYYY-MM-DD)
- ~/.claude/agent-memory/critic/MEMORY.md (updated YYYY-MM-DD)
- docs/principled/scratch/context.md (updated YYYY-MM-DD)

Recommendation: Keep newest (context.md), archive older
Action: Move older to ~/.claude/archive/memory/projects/YYYY-MM/
```

---

## MEMORY-ARCHIVE Mode

Archive stale memory entries. Use when AUDIT reports entries older than the threshold or for projects/agents that no longer exist.

### Process

1. **Run audit** with age threshold (default 30 days, configurable via `--days`).
2. **Identify stale entries**:
   - Last modified > threshold days ago
   - Project no longer exists
   - Agent no longer exists
3. **Archive to**: `~/.claude/archive/memory/{category}/{date}/`.
4. **Create manifest**: track original paths for recovery.
5. **Present planned actions** to the user. Wait for explicit confirmation ("yes" or "proceed") before moving any file.
6. **On confirmation**: move files, update manifest, and record the archive timestamp.

### Manifest Format

```yaml
archived: YYYY-MM-DDTHH:MM:SSZ
entries:
  - original: ~/.claude/projects/old-project/memory/MEMORY.md
    archived: ~/.claude/archive/memory/projects/YYYY-MM/old-project-memory.md
    reason: project deleted
  - original: ~/.claude/agent-memory/deprecated-agent/
    archived: ~/.claude/archive/memory/agents/YYYY-MM/deprecated-agent/
    reason: agent no longer used
```

---

## MEMORY-CLEAN Mode

Full maintenance: deduplication + archiving in one pass. The default for "clean up my memory" requests.

### Process

1. **Run dedup** (review the JSON, decide resolutions per group).
2. **Run archive** for stale entries (MEMORY-ARCHIVE mode).
3. **Create backup** of the targeted memory location before any destructive action.
4. **Always requires explicit user confirmation** (no flag-based auto-confirm — the agent must list the planned actions and wait for the user to say "yes" or "proceed"). This is the safety boundary.
5. **Summary**: files removed, space freed, archived count.

### Execution

DEDUP and ARCHIVE are run as separate steps. The agent orchestrates: runs inline duplicate detection for discovery, then invokes MEMORY-ARCHIVE for the destructive step.

```bash
# Step 1: discover duplicates (read-only)
# Run duplicate detection inline: read all files in the target directory, tokenize, compute pairwise Jaccard similarity. Flag pairs above threshold for review ~/.claude/projects --threshold 0.7
# Run duplicate detection inline: read all files in the target directory, tokenize, compute pairwise Jaccard similarity. Flag pairs above threshold for review ~/.claude/agent-memory --threshold 0.7

# Step 2: archive stale entries (see MEMORY-ARCHIVE for the manifest flow)
# The agent moves files per the manifest, then updates MEMORY.md indexes.
```

After both steps complete, present the summary and a recovery pointer to the archive manifest.

### Safety
- Pre-flight check: confirm the user has approved the planned actions.
- Atomic operations: copy before delete; never `rm -rf` memory files.
- Recovery manifest: all archived files tracked with original paths.

---

## File References

- `references/learning-taxonomy.md` — categories, confidence scoring, extraction signals. Required reading in PLAN-ARCHIVE Phase 3.
- `references/memory-locations.md` — full list of Claude Code memory paths, detection rules, and per-platform variations. Required reading in MEMORY-AUDIT.
- `templates/archive-bundle.md` — structure for archived plan artifacts. Used in PLAN-ARCHIVE Phase 2.
- inline duplicate detection (read files, compute Jaccard similarity at threshold 0.7) — Jaccard-similarity duplicate detection. Used in MEMORY-DEDUP and MEMORY-CLEAN.
- Archive location: `docs/principled/attic/` (follows existing attic convention).
- Learnings location: `docs/principled/memory/learnings.md` (follows existing memory convention).

## Failure Signal

```json
{"status": "failed" | "success", "reason": "...", "completed_portion": "...", "retry_possible": true/false}
```

| status | reason | mode | retry_possible |
|--------|--------|------|----------------|
| `failed` | `no-completed-plans` | PLAN-ARCHIVE | `false` |
| `failed` | `no-summary` | PLAN-ARCHIVE | `false` |
| `failed` | `archive-write-failed` | PLAN-ARCHIVE | `true` |
| `failed` | `learnings-conflict` | PLAN-ARCHIVE | `true` |
| `failed` | `plan-not-found` | PLAN-ARCHIVE | `true` |
| `failed` | `memory-locations-unreachable` | MEMORY-AUDIT | `true` |
| `failed` | `dedup-threshold-invalid` | MEMORY-DEDUP | `true` |
| `failed` | `archive-manifest-write-failed` | MEMORY-ARCHIVE | `true` |
| `failed` | `backup-location-unwritable` | MEMORY-CLEAN | `false` |
