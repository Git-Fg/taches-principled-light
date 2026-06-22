# Taches Principled

**Version:** 2.1.0 · 26 top-level skills (5 design-hub sub-skills = 31 SKILL.md total)

A specialist plugin for Claude Code, Kimi Code, Codex, and Cursor. Pairs with [superpowers](https://github.com/GoFaster/superpowers) for the complete development toolkit.

## Superpowers + Taches Principled

Install both. They're designed to coexist:

| Layer | Plugin | Role |
|-------|--------|------|
| **Foundation** | superpowers | Brainstorming, TDD, systematic debugging, code review, git worktrees, verification, plan execution, skill writing |
| **Specialist** | taches-principled-light | DDD, first-principles reasoning, structured agent-driven dev, Rust lifecycle, MCP expertise, security audit, wiki management, session analytics, full task lifecycle |

Skills know about each other. Taches skills redirect to superpowers when they overlap — every skill with adjacent-domain overlap has a CONTRAST section pointing to the superpowers equivalent.

## Installation by Platform

### Claude Code

```bash
# Install from marketplace (recommended)
/plugin marketplace add Git-Fg/taches-principled-light
/plugin install taches-principled-light

# Or install directly from GitHub
claude plugin install https://github.com/Git-Fg/taches-principled-light
```

### Kimi Code

```bash
# In the TUI, run:
/plugins install https://github.com/Git-Fg/taches-principled-light

# Then reload to activate:
/reload
```

Pin to a specific branch/tag/commit:
```bash
/plugins install https://github.com/Git-Fg/taches-principled-light/tree/main
/plugins install https://github.com/Git-Fg/taches-principled-light/releases/tag/v2.0.0
```

### Codex

```bash
# One-time marketplace registration (shell)
codex plugin marketplace add Git-Fg/taches-principled-light

# Then inside a Codex session, browse and install:
/plugins
```

### Cursor

Install via Cursor's plugin manager using the GitHub URL:
```
https://github.com/Git-Fg/taches-principled-light
```

## What You Get

| Domain | Skills |
|--------|--------|
| **Lifecycle** | `plan-lifecycle`, `task-lifecycle`, `plan-do-check-act` |
| **Quality** | `reviewing-and-polishing`, `general-critic`, `applying-guardrails`, `restructuring-code`, `test-orchestration` |
| **Reasoning** | `reasoning-from-principles`, `solving-competitively`, `web-search`, `deep-research` |
| **Domain** | `engineering-mcp`, `rust`, `security`, `git`, `managing-wiki`, `managing-rules`, `claude-cli` |
| **Meta** | `crafting-skills`, `evaluating-skills`, `orchestrating-subagents`, `analyzing-sessions`, `project-maintenance` |
| **Design** | `design-hub` (hub) with 5 sub-skills: `pdf-design-guide`, `design-system-palettes`, `typography-guide`, `design-principles`, `design-good-bad-examples` |
| **Idea** | `generating-ideas` |

All skills use platform-agnostic subagent spawns — "spawn a subagent explorer" (read-only) or "spawn a subagent generalist" (edit access). See the `orchestrating-subagents` skill for the canonical reference.

## What's New in 2.1.0

Four skills added since 2.0.0, plus research methodology and a portable benchmark aggregator:

- **`design-hub`** — router for design system work: palette picker, typography guide, design principles, BAD-vs-GOOD examples, pdf-design-guide. Five sub-skills under one hub.
- **`evaluating-skills`** — 8-stage skill evaluation methodology (capability probe → evals → run → grade → aggregate → review → iterate → optimize). Behavioral review via raw JSONL transcripts — works across Claude Code, `claude -p`, Codex, kimi-code, and Reasonix. Ships a portable `scripts/aggregate_benchmark.py` (pure Python stdlib, no subprocess) that emits Anthropic-schema-compatible `benchmark.json` + human-readable `benchmark.md`.
- **`deep-research`** — 5-stage research pipeline (background → judgment → analysis → deep-research → final). Output goes to `docs/principled/research/<slug>/` with six artifacts per run. Example output at `docs/principled/research/agent-skills-evaluation/` is the methodology source for `evaluating-skills`.
- **`general-critic`** — reusable severity-rated critic subagent with HIGH/MEDIUM/LOW and "loop until PASS" contract. Used as the inline grader in `evaluating-skills` stage 4. Includes a decision router and contrast with nearby skills.

The session also dogfooded the new methodology by writing `evals/evals.json` for `general-critic` and `deep-research` — three realistic eval prompts per skill with documented with-vs-without behavioral deltas.

## Manual Install

```bash
git clone https://github.com/Git-Fg/taches-principled-light
cp -r taches-principled-light/skills/* ~/.claude/skills/
```

## License

MIT