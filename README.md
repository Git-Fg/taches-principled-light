# Taches Principled

**Version:** 0.0.1-alpha · 26 top-level skills (5 design-hub sub-skills = 31 SKILL.md total)

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
/plugins install https://github.com/Git-Fg/taches-principled-light/releases/tag/v0.0.1
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

## What's New in 0.0.1-alpha

First alpha cut. The 26 top-level skills are frozen as the public surface; everything else is internal tooling or pre-alpha history. See CHANGELOG for the long-form breakdown.

## Manual Install

```bash
git clone https://github.com/Git-Fg/taches-principled-light
cp -r taches-principled-light/skills/* ~/.claude/skills/
```

## License

MIT