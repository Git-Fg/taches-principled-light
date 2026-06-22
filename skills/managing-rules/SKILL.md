---
name: managing-rules
description: "Load when managing AGENTS.md — the primary, platform-agnostic agent guidance file — extracting conventions from sessions, adding new rules, restructuring existing rules, or auditing rule quality. Use when the user says 'add a rule', 'extract this convention', 'restructure my rules', 'audit my AGENTS.md', or 'codify this pattern'. Covers CLAUDE.md and .claude/rules/ only when they already exist in the workspace or the user explicitly asks for them. Do NOT use for archiving plans or cleaning auto-memory (use project-maintenance)."
allowed-tools: Read, Edit, Write, Bash, Grep
when_to_use: "Use when the user wants to update AGENTS.md, codify conventions, or extract rules from conversation. Covers CLAUDE.md only when it already exists or is explicitly requested."
argument-hint: "[ANALYZE|ADD|RESTRUCTURE|REVIEW|SYNC|AUDIT] [target]"
license: MIT
---

## File Target Resolution

Before any mode, determine the target files:

1. **Check what exists:** Read the workspace root. Look for `AGENTS.md`, `CLAUDE.md`, `.agents/rules/`, `.claude/rules/`.
2. **Apply this priority:**
   - `AGENTS.md` is **always** the primary target — it is the platform-agnostic standard.
   - If `AGENTS.md` does not exist, create it. Do NOT fall back to CLAUDE.md silently.
   - `CLAUDE.md` and `.claude/rules/` are secondary — only touch them when:
     - They already exist in the workspace (legacy), OR
     - The user explicitly says "CLAUDE.md" or "Claude rules"
   - When both `AGENTS.md` and `CLAUDE.md` exist, work with `AGENTS.md` primarily; sync changes to `CLAUDE.md` only if the user confirms.
3. **Rules directories** follow the same logic:
   - Primary: `.agents/rules/<name>.md`
   - Secondary (legacy/Claude-only): `.claude/rules/<name>.md`

**User query heuristics:**
- "update my rules", "add a rule", "restructure rules" → `AGENTS.md` / `.agents/rules/`
- "update CLAUDE.md", "fix my Claude rules" → `CLAUDE.md` / `.claude/rules/` (explicit)
- "audit my agent config" → audit both, report on `AGENTS.md` first

## Routing Guidance

- IMMEDIATELY after significant skill execution when conventions were established.
- FIRST when AGENTS.md exceeds 200 lines or `.agents/rules/` has more than 10 files.
- Do NOT use for one-off questions or temporary instructions.
- Do NOT modify managed/enterprise rules at system paths.

## CONTRAST

- NOT for: capturing session learnings to scratchpad — use reviewing-and-polishing MEMORIZE
- NOT for: archiving completed plans — use project-maintenance PLAN-ARCHIVE
- NOT for: one-off temp instructions that won't be repeated

## Decision Router

IF user wants to extract insights from current/last conversation → **ANALYZE** mode
IF user wants to restructure or audit existing rules → **RESTRUCTURE** mode
IF user wants to add a specific convention to rules → **ADD** mode
IF user wants to review and approve pending proposals → **REVIEW** mode
IF user wants to sync with recent skill execution or learn output → **SYNC** mode
IF user wants to find rule conflicts across hierarchy → **AUDIT** mode
IF target is ambiguous → ask: "Analyze current conversation, restructure existing rules, add a specific convention, review pending proposals, sync with recent work, or audit for conflicts?"

**Before every mode:** resolve file targets using the File Target Resolution rules above. State which file(s) you will operate on before proceeding.

---

## ANALYZE Mode

Extracts insights from conversation history or skill output and synthesizes them into structured rule proposals.

### When
After conversation or skill execution with discoverable conventions, anti-patterns, or decisions worth codifying.

### Process

1. **Resolve targets** — Determine whether AGENTS.md, CLAUDE.md, or both are in play (see File Target Resolution). State your target before proceeding.

2. **Capture context** — Read from `docs/principled/scratch/` or conversation summary. Determine the source: recent skill execution output, session transcript, or explicit user request.

3. **Extract insights** — Analyze the context inline (or spawn a subagent explorer with prompt "read this transcript/context and extract conventions, anti-patterns, tool preferences, architectural decisions, and domain knowledge as structured findings") when the source material is large and would flood your context. Write findings to `docs/principled/scratch/rules-analysis-{timestamp}.md`.

4. **Synthesize proposals** — Read the analysis output. Convert raw insights into structured proposals with:
   - **Category**: TECHNICAL | PROCESS | PATTERN | ANTI-PATTERN | DECISION
   - **Priority**: critical | important | nice-to-have
   - **Target**: AGENTS.md (primary) or `.agents/rules/<name>.md` (path-scoped). Only target `CLAUDE.md` or `.claude/rules/` if they already exist AND the user confirmed.
   - **Rationale**: Why this rule belongs in the project
   - **Rule text**: Draft rule content following `references/rule-writing-guide.md`

5. **Write proposal file** — Save to `docs/principled/scratch/rules-proposals-{timestamp}.md` with all proposals in the structured format.

6. **Present proposals** — Show user a numbered list of proposals with file targets and a one-line rationale. Ask: "Integrate these rules?"

7. **On approval** — Apply the changes inline: read each target file, apply the approved proposals with precise edits, validate frontmatter, and commit with a conventional message.

### Output
- Analysis: `docs/principled/scratch/rules-analysis-{timestamp}.md`
- Proposals: `docs/principled/scratch/rules-proposals-{timestamp}.md`
- Updated rules files (committed)

---

## RESTRUCTURE Mode

Audits and reorganizes existing rules to reduce bloat, eliminate duplication, and improve loading efficiency.

### When
AGENTS.md exceeds 200 lines, `.agents/rules/` has more than 10 files, or rules feel disorganized. Also trigger when CLAUDE.md/.claude/rules/ are bloated if they exist.

### Process

1. **Resolve targets** — Determine which files are in play (see File Target Resolution). If both AGENTS.md and CLAUDE.md exist, restructure AGENTS.md primarily; propose syncing CLAUDE.md after.

2. **Audit current state** — Read all rules files in scope. Map: total line count, file count, any obvious duplication visible without analysis.

3. **Identify issues** — Spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: 'identify bloat, duplication, stale rules, and organizational issues in these rules files'. Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix. Do NOT implement — identify what to change and why." with full paths to all rules files. Instruct it to write findings to `docs/principled/scratch/rules-audit.md`.

4. **Design new structure** — Review the audit report. Design a reorganization:
   - Which files to split (target: under 200 lines each)
   - Which rules need `paths:` frontmatter added
   - Which duplicates to merge
   - Which deprecated rules to archive (move to `docs/principled/attic/rules/`)
   - Target directory structure

5. **Present plan** — Show before/after structure. For each blocker and warning from the audit, include the proposed fix. Ask: "Apply this restructure?"

6. **On approval** — Execute: create new files, move content, add frontmatter, delete originals, verify no broken references, commit.

---

## ADD Mode

Adds a single convention to the rules system with conflict checking and proper frontmatter.

### When
User explicitly wants to codify a specific convention.

### Process

1. **Resolve targets** — Determine the primary target (see File Target Resolution). If only CLAUDE.md exists and AGENTS.md does not, ask: "Create AGENTS.md as the primary rules file, or add to the existing CLAUDE.md?"

2. **Capture intent** — Confirm what the user wants to codify. If vague, ask one clarifying question. If clear, proceed.

3. **Determine placement** — Apply this decision tree:
   - Universal across all files → AGENTS.md (primary)
   - Specific to file types → `.agents/rules/<name>.md` with `paths:` frontmatter
   - Specific to a subsystem → `.agents/rules/<domain>/<name>.md`
   - Otherwise → `.agents/rules/<name>.md` (always-on)
   - If only CLAUDE.md exists and user chose not to create AGENTS.md → `.claude/rules/<name>.md`

4. **Draft rule** — Write the rule following `references/rule-writing-guide.md`. Include:
   - Frontmatter: `name`, `description` (one sentence), `paths:` if scoped
   - Body: clear directive, Bad/Good examples
   - Rationale: why this rule

5. **Conflict check** — Grep existing rules (both `.agents/rules/` and `.claude/rules/` if both exist) for overlap or contradiction. If found, show the conflict and ask: "Merge with existing rule, replace it, or keep both with different scope?"

6. **Integrate and commit** — Apply with your native tools (append to existing file or create new file). Run `git add <file>` and `git commit -m "feat(rules): add [rule name] to [target file]"`. Report the commit URL or hash.

---

## REVIEW Mode

Multi-judge evaluation of pending rule proposals before integration.

### When
Pending proposals exist from ANALYZE or SYNC that need approval before being committed.

### Process

1. **Load proposals** — Find proposal files: `ls docs/principled/scratch/rules-proposals-*.md`. If multiple exist, use the most recent. If none exist, report and exit.

2. **Spawn review panel** — Dispatch 2-3 subagent generalist subagents in parallel, each with a distinct lens:
   - Lens 1: "is the rule text actionable and the rationale clear?"
   - Lens 2: "does this contradict or duplicate an existing rule?"
   - Lens 3: "would adding this reduce or increase context cost? is it team-relevant or personal preference?"
   Give each the proposal file. Instruct each to write their verdict to `docs/principled/scratch/rules-review-{critic-id}.md`.

3. **Aggregate verdict** — Read all review outputs. For each proposal: count approve/revise/reject votes. Present consensus:
   ```markdown
   | Rule | Verdict | Votes |
   |------|---------|-------|
   | rule-name | APPROVE | 3/3 |
   | rule-name | REVISE | 2/3 |
   | rule-name | REJECT | 1/3 |
   ```
   For REVISE: include specific concerns. For REJECT: include reason.

4. **Apply approved** — For APPROVE: apply inline (read target files, edit precisely, validate frontmatter, commit). For REVISE: present revision options to user. For REJECT: archive proposal with reason.

---

## SYNC Mode

Bridges the gap between ephemeral memory captures and durable rules integration. The learn command stores to memory; SYNC promotes durable insights to rules.

**CONTRAST — feeds from:** project-maintenance PLAN-ARCHIVE and reviewing-and-polishing MEMORIZE, which both write to `docs/principled/memory/learnings.md`. SYNC is downstream of both — never the source.

### When
After `learn` command captures insights, or after skill execution that established conventions not yet codified.

### Process

1. **Resolve targets** — Determine which rules files to sync into (see File Target Resolution).

2. **Read sources** — Check for `docs/principled/memory/learnings.md`. Also scan `docs/principled/scratch/` for recent SUMMARY.md or execution output. If neither exists, report and exit.

3. **Extract candidates** — Read the memory/scratch files. Identify entries tagged with TECHNICAL, DECISION, or ANTI-PATTERN — these have the highest rule-worthiness.

4. **Check existing** — For each candidate, grep `AGENTS.md`, `.agents/rules/`, and `CLAUDE.md`/`.claude/rules/` (if they exist) for overlap. Skip duplicates. Flag near-matches for human review.

5. **Propose additions** — Write candidate rules to `docs/principled/scratch/rules-sync-proposals-{timestamp}.md`. Tag each:
   - `auto`: critical/correctness — safe to integrate without approval
   - `review`: important/nice-to-have — needs human review

6. **Auto-integrate low-risk** — For `auto` tagged candidates: apply inline directly to AGENTS.md (primary). Notify user of changes.

7. **Queue for REVIEW** — For `review` tagged candidates: present to user and suggest REVIEW mode.

---

## AUDIT Mode

Analyzes the agent guidance file hierarchy for conflicts, duplications, and cross-file contradictions.

### When
First when preparing for deployments, after major rule changes, or when diagnosing unexpected behavior between rules.

### Process

1. **Resolve scope** — Determine what to audit:
   - Default: `AGENTS.md` + `.agents/rules/**/*.md` (primary)
   - If CLAUDE.md exists: include `CLAUDE.md` + `.claude/rules/**/*.md` (secondary, cross-checked against primary)
   - If user explicitly requests Claude: audit CLAUDE.md hierarchy only

2. **Discover configs** — Recursive scan from CWD upward:
   - `AGENTS.md` at each directory level (primary)
   - `.agents/rules/**/*.md` at each project level (primary)
   - `CLAUDE.md` at each directory level (secondary, if exists)
   - `.claude/rules/**/*.md` at each project level (secondary, if exists)
   - `~/.claude/CLAUDE.md` (global, if exists)

3. **Map hierarchy** — Build tree showing file structure and line counts. Show AGENTS.md files first, CLAUDE.md files second with a `[legacy]` tag.

4. **Detect conflicts** — Compare rules pairwise across hierarchy levels. Flag:
   - **Critical**: opposite directives (tabs vs spaces, required vs forbidden)
   - **Warning**: inconsistent preferences (different naming conventions)
   - **Info**: redundant rules appearing in multiple files

5. **Detect duplicates** — Hash comparison to find same rule text in multiple files. Flag AGENTS.md ↔ CLAUDE.md duplicates specially — these should be resolved by removing from CLAUDE.md.

6. **Score health** per location:
   - Green: 0-1 issues
   - Yellow: 2-3 issues
   - Red: 4+ issues

7. **Output conflict pairs**:
   ```
   ### Conflict: Indentation Style
   - AGENTS.md (line 12): "Use tabs for indentation"
   - CLAUDE.md [legacy] (line 8): "Use 2 spaces for indentation"
   - Resolution: AGENTS.md wins (primary). Remove conflicting rule from CLAUDE.md.
   ```

8. **Save report** — Write to `docs/principled/scratch/rules-audit-{timestamp}.md`

### Safety
- Default: `--dry-run` (read-only, no writes)
- Never modifies files without explicit confirmation

---

## Design Decisions

**AGENTS.md is primary.** AGENTS.md is the platform-agnostic standard. CLAUDE.md is a legacy Claude-specific file. All new rules go to AGENTS.md by default.

**Propose-then-approve.** Never auto-apply without presenting proposals. Loop a subagent generalist subagent until no HIGH findings before applying.

**No managed rules.** Explicit check: do not modify files under `/etc/` or other system-managed paths.

**Minimal agents.** Three agents cover the full lifecycle: analyze (extract), audit (evaluate), integrate (apply). Reuse existing plugin-level agents where possible.
