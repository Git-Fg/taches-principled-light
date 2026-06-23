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