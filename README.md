# Taches Principled

**Version:** 0.0.6 · 26 top-level skills (5 design-hub sub-skills = 31 SKILL.md total)

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
/plugins install https://github.com/Git-Fg/taches-principled-light/releases/tag/v0.0.6
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

## What's New in 0.0.6

**Post-v0.0.5 polish, iter-8 design, and citation audit.** No new skills; no breaking changes; 19 commits, 35 files changed (+1613/-7). Four areas of work: (1) **iter-8 design** — 286-line plan + 213-line design supplements note addressing the two open follow-ups from iter-7 (proxy is structurally single-model → vendor-disjoint validation blocked; sec-audit +17.5pp grader swing on identical transcripts). The iter-8 architecture is a two-layer MCP test-runner stack: a mock MCP server (Tyk / AIMock / custom) feeds captured golden responses to the agent, and **mcp-assert** (Go, MIT, 18 stars, 0 open issues) acts as the test runner that asserts YAML expectations. (2) **Citation hallucination remediation** — 4 fabricated arXiv IDs (2406.01574, 2602.12345, 2603.12345) replaced with verified real ones (Wataoka 2024 / CoEval 2026 / SkillRouter 2026), 1 fabricated Claude-on-Claude κ=0.770 number replaced with the actual JudgeBench κ=0.720 from Norman/Rivera/Hughes Berkeley 2026 (arxiv:2606.19544). (3) **CI action bumps** — `actions/checkout` v4→v7, `actions/setup-python` v5→v6, `actions/upload-artifact` v4→v7 across both workflows. PR #1 (dependabot's auto-PR for these bumps) closed with an explanation comment; the local-application workflow is preferred for this repo. (4) **v0.0.5 self-critic pass** — 4 rounds of self-critic found 1 HIGH, 2 MEDIUM issues, all fixed. iter-8 design reviewed at 3 levels (PLAN.md ↔ supplements ↔ INDEX.md) for cross-reference integrity. See CHANGELOG for the long-form breakdown and the iter-8 supplements note for the MCP test-runner architecture detail.

## What's New in 0.0.5

**iter-5/6/7 measurement campaign complete.** Canonical headline from `evaluating-skills` 8-stage harness on the haiku solver: **mean total_lift +21.88pp** across 4 evals (`eval-skill`, `sec-audit`, `lint-1`, `release-2`) — **4/4 lifts, 0 hurts, deterministic endpoint grades.** Three lifts disambiguated by introducing a true no-plugin baseline via `--disable-slash-commands`: `consultation_lift` = +8.12pp (noisy, +17.5pp grader swing on identical transcript), `filesystem_access_lift` = +13.75pp, `total_lift` = +21.88pp. iter-4's contaminated `without_skill` baseline (plugin auto-loads via `slash_commands` regardless of `--add-dir`) is corrected. iter-6 vendor-disjoint validation structurally blocked: the inference-gateway proxy is a single-model gateway (all 18+ aliases serve `MiniMax-M3`; only `glm-5.2` is vendor-disjoint and is rate-limited). iter-5 (N=11 reliability) deferred — not ship-blocking because the +21.88pp headline is well above the grader noise floor. See [`docs/principled/skill-evals/marketplace-routing-2026-06-22/iteration-7/REPORT.md`](docs/principled/skill-evals/marketplace-routing-2026-06-22/iteration-7/REPORT.md) and CHANGELOG.

## What's New in 0.0.4

Iter-4 measurement infrastructure (combined `run_iteration_4.py` runner, subprocess timeout marker, stale cache invalidation documentation). iter-4's headline is +4.94pp on 18 evals (5 lifts / 13 neutrals / 0 hurts) — but the `without_skill` baseline was contaminated by the marketplace plugin auto-loading via `slash_commands`, so this is the **filesystem_access_lift only**, not the total lift. See CHANGELOG.

## What's New in 0.0.3

Behavior-eval-validated router improvements. Mean lift **+8.69pp** across 17 behavior evals (6 lifts / 11 neutrals / **0 hurts**) over the prior release. Six zero-discovery skills gained 5-10 trigger phrases each (Microsoft best-practices density); `ingesting-skills` and `marketplace-validator` rewritten with explicit scope routers. Iter-3 corrected evaluation pipeline added (`docs/principled/skill-evals/marketplace-routing-2026-06-22/iteration-3/`) — `grader.py` + `run_iteration_3.py` + corrected REPORT.md + BUCKET-A-INSPECTION + DISCOVERY-INVESTIGATION. Iter-3.1 per-skill `--add-dir` experiment in flight to confirm the plugin-shadowing hypothesis behind 5 Bucket A3 discovery failures. CHANGELOG has the long-form breakdown.

## What's New in 0.0.2

First post-alpha iteration. Routing precision improved from a vacuous `7W / 0T / 3L` (5-skill pool, broken regex) to a real `15W / 1T / 2L` (35-skill pool, fixed parser). Skill descriptions in `skills/*/SKILL.md` refactored to single-line YAML for max compatibility; 27 tightened to ≤50 words; 4 of 5 design-hub sub-skills gained negative triggers (design-principles pending). Parser hardened for single-quoted scalars and YAML 1.2 escape sequences. Behavioral eval harness validated with a pilot run — see CHANGELOG for the long-form breakdown.

## What's New in 0.0.1-alpha

First alpha cut. The 26 top-level skills are frozen as the public surface; everything else is internal tooling or pre-alpha history. See CHANGELOG for the long-form breakdown.

## Manual Install

```bash
git clone https://github.com/Git-Fg/taches-principled-light
cp -r taches-principled-light/skills/* ~/.claude/skills/
```

## License

MIT