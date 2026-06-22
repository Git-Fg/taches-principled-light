# Taches Principled

You have both **superpowers** and **taches-principled-light** installed. They are designed to coexist.

## How They Fit Together

- **superpowers** is your foundation — brainstorming, TDD, systematic debugging, code review, git worktrees, verification, plan execution, skill writing.
- **taches-principled-light** adds specialist skills — code restructuring, first-principles reasoning, competitive solving, guardrails, MCP engineering, security, wiki management, session analysis, design systems (via `design-hub`), and skill evaluation methodology (via `evaluating-skills` and `general-critic`).

## When Both Cover a Topic

Each taches skill has a CONTRAST section. When a topic overlaps with superpowers, the skill redirects explicitly. Examples:

- Want Red-Green-Refactor TDD? → superpowers' `test-driven-development` (taches' `test-orchestration` handles strategy and repair only)
- Want to brainstorm a vague idea into a design? → superpowers' `brainstorming` (taches' `generating-ideas` generates alternatives only)
- Want root-cause debugging? → superpowers' `systematic-debugging`
- Want per-task subagent execution? → superpowers' `subagent-driven-development` (taches' `solving-competitively` does competitive generation)
- Want collaborative skill creation? → superpowers' `writing-skills` (taches' `crafting-skills` creates and optimizes agent skills)
- Want to evaluate whether a skill actually improves behavior? → taches' `evaluating-skills` (8-stage loop with behavioral JSONL review; works across Claude Code, `claude -p`, Codex, kimi-code, Reasonix)
- Want to run a multi-stage research pipeline? → taches' `deep-research` (5 stages writing to `docs/principled/research/<slug>/`)

**The pattern: superpowers for fundamentals, taches-principled-light for depth.**

## Skill Discovery

All taches skills use a uniform description pattern for fast routing:

- **Load when…** — the primary trigger describing user intent
- **Use when…** — concrete trigger phrases the user might say
- **Do NOT use for…** — negative boundary; if your task matches this, skip the skill

When scanning the skill index at startup, match user intent against the trigger phrases
first; the NOT clauses define hard exclusion boundaries between sibling skills.

## Subagent Convention

All skills use platform-agnostic phrasing. Never name a specific tool.

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

## Adding a Skill

1. Create `skills/<name>/SKILL.md` with frontmatter + body.
2. Follow `crafting-skills` CREATE mode for authoring new skills; use OPTIMIZE mode for routing improvements.
3. No other files to touch.
