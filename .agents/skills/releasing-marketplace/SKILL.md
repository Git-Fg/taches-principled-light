---
name: releasing-marketplace
description: "Load when cutting a marketplace version — bumping version across all 4 manifests, drafting the CHANGELOG, syncing README and AGENTS. Use when the user says 'cut a release', 'bump version', or 'tag and push'. Do NOT use for one-skill edits or health checks."
when_to_use: |
  Use whenever a coherent batch of changes is ready to ship. The skill
  enforces a fixed sequence: pre-release gate, version proposal, manifest
  sync, CHANGELOG draft, README/AGENTS check, approval, commit.
argument-hint: "[--propose] [--tag] [--no-push]"
allowed-tools: Read, Edit, Write, Bash, Glob, Grep
license: MIT
---

# Releasing Marketplace

The orchestrator that turns "I have a batch of changes" into "v2.2.0 is on origin/main." Approval-gated at every step. Calls existing skills rather than reinventing them.

## Decision Router

IF the user has uncommitted changes and wants a release → run the full workflow
IF the user wants to propose a version without cutting → use `--propose` (dry run)
IF the user wants a git tag (e.g., v2.2.0) on the release commit → add `--tag`
IF the user does not want to push to origin → add `--no-push`
IF unclear → run the full workflow; ask before pushing

## The 7-Step Release Workflow

Run in order. **No step is optional.** Each step is approval-gated — present the proposed change, get explicit yes, then proceed.

### Step 1 — Pre-release gate

```bash
python .agents/skills/marketplace-health/scripts/health.py
```

If the report has any hard failure (✗), the release is **blocked**. The skill should:
- Show the failing checks
- Ask the user whether to (a) fix the issues before cutting, (b) proceed anyway (only if the user explicitly accepts the failures), or (c) abort the release

If the report passes (✓ with warnings allowed), proceed.

**Scaling-knee check.** Count shipped skills under `skills/`:

```bash
MARKETPLACE_ROOT="$(git rev-parse --show-toplevel)"
python3 -c "
import pathlib, sys
root = pathlib.Path('$MARKETPLACE_ROOT') / 'skills'
n = sum(1 for _ in root.glob('*/SKILL.md'))
print(f'{n} shipped skills in {root}')
sys.exit(0 if n < 50 else 1)
"
```

The `git rev-parse --show-toplevel` anchor removes the cwd-fragility of `Path.cwd()` (which would silently return 0 if the maintainer is cd'd into a subdirectory). Run from any subdirectory of the marketplace; the count is always correct.

> **High-risk path: changes to AGENTS.md → Marketplace Scaling.** If this release modifies the Marketplace Scaling section (or its cross-platform table, or the research notes at `research/claude-code-skill-budget-evolution.md` / `research/cross-platform-skill-budget-comparison.md`), spawn an **independent subagent critic** before cutting the release. The 5-round critic arc on commits `5adb44c`, `9927e3e`, `5e26e36`, `a39e334` demonstrated that this code path is high-risk for stale-reference drift: the parent doc is updated, but downstream references (catalog-size table, cross-platform table cells, user-facing reference docs, verification reports) routinely carry the prior framing. Five rounds of independent review were needed to converge. Treat the critic as required when:
>
> - The commit diff touches `AGENTS.md` Marketplace Scaling (anywhere in the section, including the audit-trail paragraph)
> - The commit diff touches the cross-platform table (any cell)
> - The commit diff touches `skills/crafting-skills/references/context-management.md` (this doc ships to users via the plugin and historically propagated the same class of error)
> - The commit diff touches any research note in `research/` that modifies a version-anchored claim in the Marketplace Scaling section or its tables
>
> **Minimal critic prompt:** *"Verify the changes against primary sources (Anthropic docs at `code.claude.com/docs/en/settings`, claudefa.st, anthropics/claude-code#64606). Specifically check for: (a) the v2.1.105 vs v2.1.129 distinction is preserved everywhere a Claude Code budget claim appears; (b) 'silently truncated' or 'silently dropped' framing has not been reintroduced; (c) the cross-platform table cells are mutually consistent; (d) the version reference in `context-management.md` line 79 matches the corrected 'silent AT v2.1.159; non-silent in post-v2.1.159 releases' framing. Report findings as HIGH/MEDIUM/LOW."*

Then cross-reference the count against AGENTS.md → Marketplace Scaling (the source of truth — do not invent new thresholds here):

> **Version anchor.** The defaults below assume **Claude Code v2.1.105+** (the release that introduced `skillListingBudgetFraction` as an explicit setting). Pre-v2.1.105 clients used an implicit 2% scaling formula from v2.1.32; both rows are documented in AGENTS.md's cross-platform table. If you need to support both, the binding constraint is the smaller budget — read both rows before deciding gate severity.

| Count range | AGENTS.md action | Gate severity |
|---|---|---|
| <50 skills | "Continue adding; run the trigger-eval harness on each new description." | Silent (progressive disclosure works). |
| 25–50 skills | "Tighten descriptions toward the 50-word soft target; disable rarely-used skills (`/skills` → disable) instead of deleting them — disabled skills don't count against the budget." | Warning — surface to maintainer; do not block. |
| 50–100 skills | "**Consolidation is mandatory**" (AGENTS.md wording). | **Block** — release cannot ship until the maintainer confirms a consolidation plan exists in the release notes. |
| 100–200 skills | "Pattern 2 becomes appropriate toward the upper end of this range." | Warning — recommend noting which clusters were consolidated in the CHANGELOG; the lower end of this range does not require Pattern 2. |
| 200–500 skills | "Pattern 2 in full: collapse the catalog behind ~14 router tools." | **Block** — release cannot ship until Pattern 2 migration is complete. |
| 500–1,000 skills | "Pattern 3 (external retrieval, semantic-index tier)." | **Block** — release cannot ship until Pattern 3 semantic-index is deployed. |
| >1,000 skills | "Pattern 3 (external retrieval, trained-reranker tier) is **required**." | **Block** — release cannot ship until Pattern 3 trained-reranker is deployed. |

The gate severity column comes from AGENTS.md's own wording — "mandatory" / "required" are block conditions; "appropriate" / "recommended" are warnings. The gate does not add new thresholds of its own. If the AGENTS.md table is updated, the gate severity follows.

### Step 2 — Determine scope and propose version

Inspect the `git diff` between the current HEAD and the last release tag (or `main` if no tags):

```bash
git log --oneline <last-release>..HEAD
git diff --stat <last-release>..HEAD
```

Apply the version-bump knob rules from `crafting-skills/references/best-practices-compendium.md`:
- **Major** (e.g. 2.0.0 → 3.0.0) — breaking changes, restructured convention, removed skills
- **Minor** (e.g. 2.1.0 → 2.2.0) — new skills, new manifest features, new commands
- **Patch** (e.g. 2.1.0 → 2.1.1) — bug fixes, doc updates, manifest version sync only

Present the proposal with reasoning, e.g.: "4 new skills added, no breaking changes → propose **2.2.0**."

### Step 3 — Sync the 4 manifests

Bump version in all of:
- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json` (in the `plugins[0]` object)
- `.codex-plugin/plugin.json`
- `.cursor-plugin/plugin.json`
- `.kimi-plugin/plugin.json`

Also refresh the `description` field if the marketplace scope meaningfully changed (new skill domain, new category, etc.). The skill-self-testing reference says "if your description is stale, update it."

For skills added since the last release, ensure they appear in any per-skill manifest entries (e.g., `plugins[].skills` in `marketplace.json`). The current convention is auto-discovery; only named entries need an update.

### Step 4 — Draft the CHANGELOG entry

Prepend a new section to `CHANGELOG.md` matching the existing format (see prior entries for tone and structure). Use the `git log` and `git diff` from Step 2 as the source. The entry should have:

- A version heading: `## [X.Y.Z] — YYYY-MM-DD`
- An `### Added` section for new skills, scripts, or commands
- An `### Changed` section for manifest updates, doc rewrites
- A `### Fixed` section for bug fixes
- An `### Verified` section for the marketplace-health sweep result (proves the release was health-checked)

For patch releases with no user-facing change, the entry can be terse: a single line.

### Step 5 — Sync README and AGENTS

Check if either needs updating:
- **README.md** — skill count (if it changed), category table (if new categories), What's New section (if user-facing). Don't touch if nothing changed.
- **AGENTS.md** — only if a new skill changes the contrast examples or the spawning convention. Don't touch otherwise.

If both are unchanged, the skill should say "README/AGENTS unchanged" and skip edits.

### Step 6 — Present the full diff

Show the user the complete proposed change:

```
=== PROPOSED RELEASE 2.2.0 ===
[manifest diff: 4 files changed, version 2.1.0 → 2.2.0]
[CHANGELOG diff: +N lines, new [2.2.0] section]
[README diff: N files changed, 0 lines if unchanged]
[AGENTS diff: N files changed, 0 lines if unchanged]
======================================
Proceed? (yes / edit / abort)
```

**Do not commit until the user says yes.** "Edit" routes to a 6.5 step where the user can request changes; "abort" cleans up any staged changes and exits.

### Step 7 — Commit (and tag, and push)

```bash
git add <changed-files>
git commit -m "release: <version> — <one-line summary>"
git tag v<version> 2>/dev/null  # only if --tag
git push origin main  # unless --no-push
git push origin v<version>  # only if --tag and not --no-push
```

The commit body should match the prior `release:` style: lead with `release: X.Y.Z — ` followed by a comma-separated list of the biggest changes. Body should have 5–15 lines covering Added / Changed / Fixed / Verified.

After committing, report back with:
- New version
- Commit hash
- Tag (if created)
- Push status (skipped if --no-push)
- A pointer to the CHANGELOG entry

## Reuse

- **`marketplace-health`** — the pre-release gate (Step 1).
- **`crafting-skills` OPTIMIZE mode** — for any version-bump-knob reasoning.
- **Native git + file editing** — the actual work; no marketplace skill needed for the mechanics.

## Contrast

- `marketplace-validator` — per-skill lint, runs as a step inside this skill.
- `marketplace-health` — pre-release audit, runs as Step 1 of this skill.
- `crafting-skills` OPTIMIZE — fixes routing, the knob this skill turns.
- This skill — orchestrates the release end-to-end with approval gates.

## When NOT to load

- A pre-release health check alone (without cutting) → `marketplace-health`.
- A single-skill edit (description trim, body split) → `crafting-skills` CREATE/OPTIMIZE.
- A new skill being added to the marketplace → `ingesting-skills` (then the next release picks it up).
- An evaluation of whether an existing skill materially changes behavior → `evaluating-skills`.