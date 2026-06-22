---
name: ingesting-skills
description: >
  Load when porting a skill from an external source — local path, GitHub
  URL, plugin directory, or another collection. Use when the user says
  'add this skill', 'port this', or 'import this plugin'. Do NOT use for
  authoring from scratch (use crafting-skills) or evaluating (use
  evaluating-skills).
when_to_use: |
  Use whenever a new skill enters the marketplace, whether by porting from
  ~/.agents/skills, cloning from anthropics/skills, copying from a teammate's
  branch, or any other external source. The workflow enforces the local
  convention systematically.
argument-hint: "[source-path-or-url] [target-skill-name]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
license: MIT
---

# Ingesting Skills

The repeatable workflow for bringing a skill into this marketplace from anywhere else. Runs in a fixed order so no step is forgotten; delegates each step's *how* to the right existing skill.

## Decision Router

IF the source is a local directory → path is the path; read it directly
IF the source is a GitHub URL (`github.com/owner/repo` or `https://…`) → `git clone` to `/tmp/` then read the resulting path
IF the source is `~/.agents/skills/<name>` → path is `~/.agents/skills/<name>` directly
IF the source is a tarball / archive → extract to `/tmp/` then read
IF unclear → ask which source

After the source is local:
IF the user wants to do the porting themselves with guidance → walk through steps 2–9 interactively
IF the user wants hands-off porting → execute steps 2–9 in one shot, present the diff, ask for approval before commit

## The 9-Step Porting Workflow

Run these in order. Skip a step only with explicit justification.

### 1. Inventory the source skill

```bash
python .agents/skills/ingesting-skills/scripts/inventory_source.py <source-dir>
```

Outputs structured JSON: frontmatter keys (spec vs non-spec), name conformance, description metrics, body line count, stale platform refs, hardcoded tool names, file inventory (scripts/, references/, assets/). Use the output to plan steps 3–7.

### 2. Pick a target name

If the source `name` is gerund-form (`processing-…`, `managing-…`, `analyzing-…`), keep it. Otherwise propose a gerund name. The directory name must match the `name:` field exactly. Run `marketplace-validator` on a temp directory to confirm.

### 3. Decide per-file

For each file in the source (skill_md + scripts + references + assets):

| Source state | Action |
|---|---|
| Frontmatter keys all in canonical spec, name gerund, body clean | **keep** as-is |
| Has non-spec frontmatter keys (`when_to_use`, `argument-hint`, `context`, etc.) | **port** — these are local extensions; keep them and document in CHANGELOG |
| Has `type: prompt`, `kimi-code edition`, `$ARGUMENTS`, `whenToUse:` (CamelCase), `disableModelInvocation` | **port** — rewrite to local convention |
| Body hardcodes tool names (`the Agent tool`, etc.) | **port** — rewrite to platform-agnostic phrasing per AGENTS.md |
| Script shells out to a runtime-specific CLI (e.g., `claude -p`) | **port** — make it runtime-agnostic or scope it explicitly with `--runtime` flag |
| Runtime-specific script that *cannot* be portable | **drop** — note in CHANGELOG with rationale |
| Body >500 lines | **port** — split into references/ per Anthropic best-practices progressive-disclosure |
| `evals/evals.json` absent | **scaffold** in step 7 |

### 4. Create the directory

```bash
mkdir -p skills/<name>/evals skills/<name>/scripts  # if scripts needed
```

### 5. Port SKILL.md frontmatter

Apply the **field-name migration table**:

| Source field | Local field |
|---|---|
| `name` | `name` (unchanged) |
| `description` | `description` (rewrite per step 6) |
| `license` | `license` (unchanged; default `MIT` if absent) |
| `allowed-tools` | `allowed-tools` (unchanged) |
| `type: prompt` | drop (non-spec; obsolete) |
| `whenToUse:` | `when_to_use:` (CamelCase → snake_case) |
| `trigger_keywords:` | drop (subsumed by description triggers) |
| `arguments:` | replace with `argument-hint:` |
| `allowed_tools:` (snake) | `allowed-tools:` (kebab) |
| `user-invocable:` | drop or move to `metadata:` if needed |
| `disable-model-invocation:` | drop or move to `metadata:` if needed |
| `context:` | drop or move to `metadata:` if needed |
| `agent:` | drop or move to `metadata:` if needed |
| `disallowed-tools:` | drop or move to `metadata:` if needed |
| `skills:` | drop or move to `metadata:` if needed |

If the source uses `metadata:` for these (already in spec), keep them inside `metadata:`.

### 6. Rewrite the description

The description is the routing trigger — the load-bearing frontmatter field for discovery. Apply the `crafting-skills` compendium rules:

- Start with `Load when …` — third person
- ≤50 words target (≤1024 hard cap)
- Include ≥1 `Do NOT use for …` clause referencing a sibling skill by exact name
- Use the user's actual trigger phrases, not paraphrase

If the source has no negative trigger, draft one. The most common mistake is a generic "this skill is bad at everything else" — name the actual sibling that covers the adjacent task.

### 7. Scaffold `evals/evals.json`

```bash
# The new skill should have evals/evals.json with 3 realistic prompts.
# Delegate the actual prompt-writing to evaluating-skills (COMPARE mode):
#   "Scaffold 3 realistic evals for skills/<name> that test whether the
#    skill materially changes the agent's behavior."
# Or write them by hand using the pattern in:
#   skills/general-critic/evals/evals.json
#   skills/deep-research/evals/evals.json
```

Realistic prompts have: file paths, real-world context (a colleague sent this, this is what the boss wants, etc.), lowercase typos, casual speech. Generic prompts ("format this data") test nothing.

### 8. Run the validator

```bash
python .agents/skills/marketplace-validator/scripts/validate.py skills/<name>/
```

Fix any *failures* (frontmatter schema, name format, description length, name-dir mismatch). Warnings about non-spec keys (`when_to_use`, `argument-hint`) are *intentional local extensions* — confirm and proceed. Warnings about hardcoded tool names or stale refs must be fixed.

### 9. Update docs

- **CHANGELOG.md** — add an entry under `[Unreleased]` or the next version, naming the skill and the source it came from.
- **The 4 plugin manifests** (`marketplace.json`, `.codex-plugin/plugin.json`, etc.) — only if the new skill should be listed by name in the marketplace catalog. Most marketplace skills don't need a manifest entry; the catalog auto-discovers them from the directory tree.
- **README.md** — only if the new skill fills a gap in the existing category table.
- **AGENTS.md** — only if the new skill overlaps with superpowers and needs a contrast example.

## When to load

- The user has a skill they want to bring in (from `~/.agents/skills/`, a GitHub repo, a teammate's branch, etc.).
- The user is reviewing a contribution and asking "is this skill ready for our marketplace?" — walk through steps 1–8 against the contribution.
- The user wants to know what the convention is — this skill IS the convention reference for ingestion.

## When NOT to load

- The user wants to write a brand-new skill from scratch → `crafting-skills` CREATE mode.
- The user wants to fix or improve an existing marketplace skill's routing → `crafting-skills` OPTIMIZE mode.
- The user wants to evaluate whether an existing skill actually changes behavior → `evaluating-skills`.
- The user wants the broader pre-release audit (manifests, license, cross-refs) → `marketplace-health`.