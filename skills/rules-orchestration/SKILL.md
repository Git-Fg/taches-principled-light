---
name: rules-orchestration
description: "Manage CLAUDE.md and `.claude/rules/` — extract learnings from sessions, add new rules, restructure existing rules, and audit rule quality. Use when the user says 'add a rule', 'extract this convention', 'restructure my rules', 'audit my CLAUDE.md', 'codify this pattern'. Five modes: ANALYZE / ADD / RESTRUCTURE / REVIEW / SYNC. NOT for: archiving plans or cleaning auto-memory (use `project-maintenance`); NOT for: capturing individual session insights (use the `learn` command)."
allowed-tools: Read, Edit, Write, Bash, Grep
when_to_use: "Use when user wants to update rules, refine CLAUDE.md, codify conventions, or extract rules from conversation."
argument-hint: "[ANALYZE|ADD|RESTRUCTURE|REVIEW|SYNC] [target]"
---

## Routing Guidance

- IMMEDIATELY after significant skill execution (plan-lifecycle, refine) when conventions were established.
- FIRST when CLAUDE.md exceeds 200 lines or .claude/rules/ has more than 10 files.
- Do NOT use for one-off questions or temporary instructions.
- Do NOT modify managed/enterprise rules at system paths.

## CONTRAST

- NOT for: capturing session learnings to scratchpad — use refine MEMORIZE
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

---

## ANALYZE Mode

Extracts insights from conversation history or skill output and synthesizes them into structured rule proposals.

### When
After conversation or skill execution with discoverable conventions, anti-patterns, or decisions worth codifying.

### Process

1. **Capture context** — Read from `docs/principled/scratch/` or conversation summary. Determine the source: recent skill execution output, session transcript, or explicit user request.

2. **Extract insights** — Analyze the context inline (or spawn a a subagent explorer subagent with question "read this transcript/context and extract conventions, anti-patterns, tool preferences, architectural decisions, and domain knowledge as structured findings") when the source material is large and would flood your context. Write findings to `docs/principled/scratch/rules-analysis-{timestamp}.md`.

3. **Synthesize proposals** — Read the analysis output. Convert raw insights into structured proposals with:
   - **Category**: TECHNICAL | PROCESS | PATTERN | ANTI-PATTERN | DECISION
   - **Priority**: critical | important | nice-to-have
   - **Target**: CLAUDE.md (global) or `.claude/rules/<name>.md` (path-scoped)
   - **Rationale**: Why this rule belongs in the project
   - **Rule text**: Draft rule content following `references/rule-writing-guide.md`

4. **Write proposal file** — Save to `docs/principled/scratch/rules-proposals-{timestamp}.md` with all proposals in the structured format from the template.

5. **Present proposals** — Show user a numbered list of proposals with file targets and a one-line rationale. Ask: "Integrate these rules?"

6. **On approval** — Apply the changes inline: read each target file, apply the approved proposals with precise edits, validate frontmatter, and commit with a conventional message.

### Output
- Analysis: `docs/principled/scratch/rules-analysis-{timestamp}.md`
- Proposals: `docs/principled/scratch/rules-proposals-{timestamp}.md`
- Updated rules files (committed)

---

## RESTRUCTURE Mode

Audits and reorganizes existing rules to reduce bloat, eliminate duplication, and improve loading efficiency.

### When
CLAUDE.md exceeds 200 lines, `.claude/rules/` has more than 10 files, or rules feel disorganized.

### Process

1. **Audit current state** — Read all files in `.claude/rules/` and `CLAUDE.md`. Map: total line count, file count, any obvious duplication visible without analysis.

2. **Identify issues** — spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why." with full paths to all rules files. Instruct it to write findings to `docs/principled/scratch/rules-audit.md`.

3. **Design new structure** — Review the audit report. Design a reorganization:
   - Which files to split (target: under 200 lines each)
   - Which rules need `paths:` frontmatter added
   - Which duplicates to merge
   - Which deprecated rules to archive (move to `docs/principled/attic/rules/`)
   - Target directory structure

4. **Present plan** — Show before/after structure. For each blocker and warning from the audit, include the proposed fix. Ask: "Apply this restructure?"

5. **On approval** — Execute: create new files, move content, add frontmatter, delete originals, verify no broken references, commit.

---

## ADD Mode

Adds a single convention to the rules system with conflict checking and proper frontmatter.

### When
User explicitly wants to codify a specific convention.

### Process

1. **Capture intent** — Confirm what the user wants to codify. If vague, ask one clarifying question. If clear, proceed.

2. **Determine placement** — Apply the decision tree from `references/rule-taxonomy.md`:
   - Universal across all files → CLAUDE.md
   - Specific to file types → `.claude/rules/<name>.md` with `paths:` frontmatter
   - Specific to a subsystem → `.claude/rules/<domain>/<name>.md`
   - Otherwise → `.claude/rules/<name>.md` (always-on)

3. **Draft rule** — Write the rule following `references/rule-writing-guide.md`. Include:
   - Frontmatter: `name`, `description` (one sentence), `paths:` if scoped
   - Body: clear directive, Bad/Good examples
   - Rationale: why this rule

4. **Conflict check** — Grep existing rules for overlap or contradiction. If found, show the conflict and ask: "Merge with existing rule, replace it, or keep both with different scope?"

5. **Integrate and commit** — Apply with your native tools (append to existing file or create new file). Run `git add <file>` and `git commit -m "feat(rules): add [rule name] to [target file]"`. Report the commit URL or hash.

---

## REVIEW Mode

Multi-judge evaluation of pending rule proposals before integration.

### When
Pending proposals exist from ANALYZE or SYNC that need approval before being committed.

### Process

1. **Load proposals** — Find proposal files: `ls docs/principled/scratch/rules-proposals-*.md`. If multiple exist, use the most recent. If none exist, report and exit.

2. **Spawn review panel** — Dispatch 2-3 a subagent generalist subagents in parallel, each with a distinct lens:
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

**CONTRAST — feeds from:** project-maintenance PLAN-ARCHIVE and refine MEMORIZE, which both write to `docs/principled/memory/learnings.md`. SYNC is downstream of both — never the source.

### When
After `learn` command captures insights, or after skill execution that established conventions not yet codified.

### Process

1. **Read sources** — Check for `docs/principled/memory/learnings.md`. Also scan `docs/principled/scratch/` for recent SUMMARY.md or execution output. If neither exists, report and exit.

2. **Extract candidates** — Read the memory/scratch files. Identify entries tagged with TECHNICAL, DECISION, or ANTI-PATTERN — these have the highest rule-worthiness.

3. **Check existing** — For each candidate, grep `.claude/rules/` and `CLAUDE.md` for overlap. Skip duplicates. Flag near-matches for human review.

4. **Propose additions** — Write candidate rules to `docs/principled/scratch/rules-sync-proposals-{timestamp}.md`. Tag each:
   - `auto`: critical/correctness — safe to integrate without approval
   - `review`: important/nice-to-have — needs human review

5. **Auto-integrate low-risk** — For `auto` tagged candidates: apply inline directly. Notify user of changes.

6. **Queue for REVIEW** — For `review` tagged candidates: present to user and suggest REVIEW mode.

---

## AUDIT Mode

Analyzes CLAUDE.md hierarchy for conflicts, duplications, and cross-file contradictions. Extracted from config-auditor.

### When
First when preparing for VPS deployments, after major rule changes, or when diagnosing unexpected behavior between rules.

### Process

1. **Discover configs** — Recursive scan from CWD upward:
   - `CLAUDE.md` at each directory level
   - `.claude/rules/**/*.md` at each project level
   - `~/.claude/CLAUDE.md` (global)
   - `~/.claude/rules/**/*.md` (global rules)

2. **Map hierarchy** — Build tree showing file structure and line counts.

3. **Detect conflicts** — Compare rules pairwise across hierarchy levels. Flag:
   - **Critical**: opposite directives (tabs vs spaces, required vs forbidden)
   - **Warning**: inconsistent preferences (different naming conventions)
   - **Info**: redundant rules appearing in multiple files

4. **Detect duplicates** — Hash comparison to find same rule text in multiple files.

5. **Score health** per location:
   - Green: 0-1 issues
   - Yellow: 2-3 issues
   - Red: 4+ issues

6. **Output conflict pairs**:
   ```
   ### Conflict: Indentation Style
   - Global (line 12): "Use tabs for indentation"
   - Project (line 8): "Use 2 spaces for indentation"
   - Resolution: Project-level wins (more specific scope)
   ```

7. **Save report** — Write to `docs/principled/scratch/rules-audit-{timestamp}.md`

### Safety
- Default: `--dry-run` (read-only, no writes)
- Never modifies files without explicit confirmation

---

## Design Decisions

**Files as source of truth.** Rules are files on disk, not conversation state. All coordination via filesystem, not message passing.

**Propose-then-approve.** Never auto-apply without presenting proposals. Loop a a subagent generalist subagent until no HIGH findings before applying.

**No managed rules.** Explicit check: do not modify files under `/etc/claude-code/` or other system-managed paths.

**Minimal agents.** Three agents cover the full lifecycle: analyze (extract), audit (evaluate), integrate (apply). Reuse existing plugin-level agents where possible.
