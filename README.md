# TACHES Principled

**Version:** 1.0.0

A Claude Code plugin for building skills, subagents, hooks, and project plans — with principle-based guidance that teaches judgment over procedure. Pairs with superpowers for the complete development toolkit.

## Quick Start

```bash
# Install the plugin
claude plugin install taches-principled
```

### Try These First

Most skills (refine, fpf, sadd, plan-lifecycle, etc.) load automatically when their description matches your task.

## What You Get

### Skills (23)

Skills load automatically when their description matches your task. Categories:

| Domain | Skills |
|--------|--------|
| **Lifecycle** | `plan-lifecycle`, `task-lifecycle`, `ideation`, `plan-do-check-act` |
| **Quality** | `refine`, `ddd`, `kaizen`, `test-orchestration` |
| **Reasoning** | `fpf`, `sadd`, `web-search` |
| **Domain expertise** | `rust`, `mcp-expertise`, `security`, `git`, `wiki`, `claude-cli` |
| **Meta** | `session-analytics`, `skill-authoring`, `subagent-orchestration`, `rules-orchestration`, `project-maintenance` |

Skills spawn subagents using platform-agnostic phrasing: "spawn a subagent explorer" (read-only) or "spawn a subagent generalist" (edit access). See the `subagent-orchestration` skill for the canonical reference.

## Installation

```bash
claude plugin install taches-principled
```

### Reinstall / Reset

```bash
claude plugin uninstall taches-principled
claude plugin install taches-principled
```

### Manual install

```bash
# Clone then copy skills to your Claude skills directory
cp -r skills/* ~/.claude/skills/
```

## Design Philosophy

Skills in this marketplace teach through principles, not procedures. Each skill focuses on what to decide and when to decide it — the how is adapted to your context.

Key ideas:

1. **Goals over procedures** — State what to achieve, not the steps to get there
2. **Principles over steps** — A few guiding principles beats a long checklist
3. **Trust Claude** — Don't explain what Claude already knows
4. **Concise by default** — Every line competes for context; every line must earn its place
5. **Gotchas, not rules** — "Common mistake: X" teaches better than "you must always do Y"

## Origins

This plugin imports and refines from two sources:

**[taches-cc-resources](https://github.com/NeoLabHQ/taches-cc-resources)** — The mental models for skills, subagents, and plans in Claude Code come from here. This plugin takes that structure and streamlines it: same patterns, lighter implementation.

**[Context Engineering Kit](https://github.com/NeoLabHQ/context-engineering-kit)** — The methodology for token economy, subagent orchestration, and progressive disclosure is imported and refined here.

## Troubleshooting

- **Command not found?** Run `/help` to see all available slash commands.
- **Skill not loading?** Skills route by description — make sure your request matches the skill's purpose.
- **Developer issues?** See [AGENTS.md](./AGENTS.md) for contribution guidelines.

## License

MIT