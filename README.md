# Taches Principled

**Version:** 2.0.0 · 22 skills

A specialist Claude Code plugin. Pairs with [superpowers](https://github.com/GoFaster/superpowers) for the complete development toolkit.

## Superpowers + Taches Principled

Install both. They're designed to coexist:

| Layer | Plugin | Role |
|-------|--------|------|
| **Foundation** | superpowers | Brainstorming, TDD, systematic debugging, code review, git worktrees, verification, plan execution, skill writing |
| **Specialist** | taches-principled-light | DDD, first-principles reasoning, structured agent-driven dev, Rust lifecycle, MCP expertise, security audit, wiki management, session analytics, full task lifecycle |

Skills know about each other. Taches skills redirect to superpowers when they overlap — every skill with adjacent-domain overlap has a CONTRAST section pointing to the superpowers equivalent.

## Quick Start

```bash
# Install both
claude plugin install superpowers
claude plugin install taches-principled-light
```

Skills load automatically when their description matches your task.

## What You Get

| Domain | Skills |
|--------|--------|
| **Lifecycle** | `plan-lifecycle`, `task-lifecycle`, `ideation`, `plan-do-check-act` |
| **Quality** | `refine`, `ddd`, `kaizen`, `test-orchestration` |
| **Reasoning** | `fpf`, `sadd`, `web-search` |
| **Domain** | `rust`, `mcp-expertise`, `security`, `git`, `wiki`, `claude-cli` |
| **Meta** | `session-analytics`, `skill-authoring`, `subagent-orchestration`, `rules-orchestration`, `project-maintenance` |

All skills use platform-agnostic subagent spawns — "spawn a subagent explorer" (read-only) or "spawn a subagent generalist" (edit access). See the `subagent-orchestration` skill for the canonical reference.

## Manual Install

```bash
git clone https://github.com/Git-Fg/taches-principled-light
cp -r taches-principled-light/skills/* ~/.claude/skills/
```

## License

MIT
