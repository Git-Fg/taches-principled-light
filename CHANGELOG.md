# Changelog

All notable changes to the taches-principled-light marketplace.

## [0.0.1-alpha] — 2026-06-22

First alpha cut. All four plugin manifests (Claude Code, Codex, Cursor, Kimi Code) are centralized at version 0.0.1. The marketplace ships 26 top-level skills (31 SKILL.md total including 5 design-hub sub-skills) plus 4 local meta-marketplace skills in `.agents/skills/`.

### Skills shipped (26 top-level)

| Domain | Skills |
|--------|--------|
| **Lifecycle** | `plan-lifecycle`, `task-lifecycle`, `plan-do-check-act` |
| **Quality** | `reviewing-and-polishing`, `general-critic`, `applying-guardrails`, `restructuring-code`, `test-orchestration` |
| **Reasoning** | `reasoning-from-principles`, `solving-competitively`, `web-search`, `deep-research` |
| **Domain** | `engineering-mcp`, `rust`, `security`, `git`, `managing-wiki`, `managing-rules`, `claude-cli` |
| **Meta** | `crafting-skills`, `evaluating-skills`, `orchestrating-subagents`, `analyzing-sessions`, `project-maintenance` |
| **Design** | `design-hub` (hub) with 5 sub-skills: `pdf-design-guide`, `design-system-palettes`, `typography-guide`, `design-principles`, `design-good-bad-examples` |
| **Idea** | `generating-ideas` |

### Local meta-marketplace skills (`.agents/skills/`)

- **`marketplace-validator`** — frontmatter + body linter (canonical spec + local convention), machine-readable JSON output
- **`ingesting-skills`** — 9-step porting workflow for adding external skills from any source
- **`marketplace-health`** — pre-release sweep: validator + manifest consistency + license coverage + cross-reference integrity + docs-reflect-state
- **`releasing-marketplace`** — 7-step approval-gated release orchestrator

### Convention compliance

- All 31 SKILL.md files have `license: MIT` in frontmatter
- All skills pass `marketplace-validator` (0 failures; 119 advisory warnings — mostly `description_word_count` and `unexpected_fm_key` for local frontmatter extensions)
- All cross-references resolve (no broken `references/X.md` or `scripts/Y.py` citations)
- README reflects current skill count (31 SKILL.md total)
- All 4 plugin manifests at version 0.0.1

### Research artifacts

- `docs/principled/research/agent-skills-evaluation/` — 6 artifacts documenting the `evaluating-skills` methodology (background, judgment, analysis, plan, document, final)
- `docs/principled/marketplace-health/2026-06-22.md` — first automated health sweep report

---

## Pre-alpha lineage

Before centralizing on 0.0.1-alpha, the marketplace went through a rapid evolution (May–June 2026) from an 11-plugin multi-component marketplace (skills + agents + commands + hooks + scripts) to the current flat skills-only structure. Key milestones, preserved as git history:

1. **Multi-plugin era (0.1.0–1.10.0):** 11 separate plugins (`core-principled`, `tp-rust`, `tp-git`, `tp-mcp`, `tp-sadd`, `tp-fpf`, `tp-security`, `tp-session-audit`, `tp-wiki`, `claude-cli-wrapper`, `tp-discipline`) with agents, commands, hooks, and scripts. Hub-and-spoke consolidation reduced 34 skills to 20, then grew back as domain expertise deepened.

2. **Consolidation era (1.11.0–1.23.1):** Agent roster reduced from 55 named subagents to 6 keepers (`tp-critic`, `tp-explorer`, `tp-researcher`, `mcp-quality-judge`, `sadd-judge`, `wiki-searcher`) using the lens-prompt pattern. Inline MCP server (`claude-cli-wrapper`) replaced with direct CLI skill. Description optimization pass across all routing signals.

3. **Flat restructure (2.0.0–2.1.0):** All agents, commands, hooks, and scripts removed. Skills-only plugin with platform-agnostic subagent spawning ("spawn a subagent explorer" / "spawn a subagent generalist"). Four new skills added: `design-hub` (+5 sub-skills), `evaluating-skills`, `deep-research`, `general-critic`. `crafting-skills` body split into hub + `references/best-practices-compendium.md`.

4. **Alpha centralization (this release):** Version reset to 0.0.1-alpha across all 4 plugin manifests. License coverage (MIT) added to all skills. 4 local meta-marketplace skills created in `.agents/skills/`. Cross-skill reference bugs fixed. README and health-sweep tooling brought online.
