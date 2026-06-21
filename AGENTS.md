# Taches Principled — Maintainer Note

Single-plugin repo. Skills only.

## Directory Layout

- `skills/` — 23 self-contained skills. Each fully autonomous.
- `.claude-plugin/plugin.json` — plugin manifest.
- `CHANGELOG.md`, `README.md`, `LICENSE` — standard.

## Adding a Skill

1. Create `skills/<name>/SKILL.md` with frontmatter + body.
2. Follow `skill-authoring` METHODOLOGY mode for routing.
3. No other files to touch.

## Subagent Spawn Convention

Skills use platform-agnostic phrasing. Never name a specific tool.

### Explorer (read-only)

```
spawn a subagent explorer with the prompt:
  "<task>"
  Read-only. Return findings as a bounded summary.
```

Use for: codebase mapping, external research, wiki search, verification reads.

### Generalist (edit access)

```
spawn a subagent generalist with the prompt:
  "<task>"
  You have edit access. Implement, verify, return what you changed.
```

Use for: implementation, review, judgment, auditing, fixes.

## Reference

The `subagent-orchestration` skill is the canonical reference for
multi-agent patterns. All other skills follow its conventions.
