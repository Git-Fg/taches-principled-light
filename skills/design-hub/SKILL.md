---
name: design-hub
description: "Load when the user needs design guidance — palette, typography, tokens, spacing, or visual hierarchy. Use when the user says 'pick palette', 'design system', or 'font pair'. Covers the full design pipeline from mood to implementation. Do NOT use for accessibility-only audits or browser automation."
when_to_use: |
  Route to the matching sub-skill based on the user's intent. Use browser
  automation for screenshot-based dogfood loops.
argument-hint: "[palette|typography|tokens|principles|examples|full-design-system]"
allowed-tools: Read
license: MIT
---

# Design Hub

Route to the right design sub-skill based on user intent.

## Hub Contract (cross-agent compatibility)

This file is a **router** that documents a recommended workflow order; the file itself is not a workflow to execute. Each of the 5 sub-skills below is a self-contained, independently-discoverable skill per the [Agent Skills open standard](https://agentskills.io/) (developed by Anthropic, adopted by Microsoft Agent Framework as of May 2026, and implemented by 30+ clients including Claude Code, OpenAI Codex, GitHub Copilot, VS Code, Roo Code, JetBrains Junie, Mistral Vibe, and Amp — see the [Agent Skills client showcase](https://agentskills.io/clients)).

**Why this layout works across agents.** The Agent Skills spec uses a three-stage progressive-disclosure pattern — advertise name+description (~100 tokens), load full SKILL.md on activation, read resources on demand — and the Microsoft implementation explicitly searches **up to two levels deep** for `SKILL.md` files ([Microsoft Learn, Agent Skills](https://learn.microsoft.com/en-us/agent-framework/agents/skills)). This layout (`skills/design-hub/SKILL.md` at level 1, `skills/design-hub/subskills/<name>/SKILL.md` at level 2) is therefore at the spec's recursive depth limit. Each sub-skill carries its own `Do NOT use for X (use Y)` clause in its description, so recursive agents route directly to the right leaf by description-match alone and never need this body. The hub exists for non-recursive agents and humans who want the routing table and companion-skill links in one place. Reference files inside each sub-skill stay one level deep from that sub-skill's `SKILL.md`, per Anthropic's authoring best practice ([Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices): "Keep references one level deep from SKILL.md").

## Workflow Order

The design pipeline flows in this order:

1. **pdf-design-guide** — Entry: mood → palette picker, 1-accent rule, 4.5:1 WCAG contrast
2. **design-system-palettes** — Token library: 18 palettes, 25-1000 scales, Tailwind/CSS vars
3. **typography-guide** — Specs: font pairs, type scale, line/paragraph spacing, table design
4. **design-principles** — Theory: why white space, contrast, proximity, alignment work
5. **design-good-bad-examples** — Reference: BAD-vs-GOOD markup, common mistakes

## Routing Table

| User intent | Sub-skill |
|---|---|
| "What color should this be?" / "Pick a palette" / "Mood-based colors" | `pdf-design-guide` |
| "Design tokens" / "Color scale 25-1000" / "Tailwind palette" | `design-system-palettes` |
| "Font pairing" / "Type scale" / "Line spacing" / "Table typography" | `typography-guide` |
| "Why does this look bad?" / "Visual hierarchy" / "White space" / "Contrast" | `design-principles` |
| "Show me examples" / "BAD vs GOOD" / "Common design mistakes" | `design-good-bad-examples` |
| "Design a full page" / "Complete design system" | Start with `pdf-design-guide`, then chain through all |

## Companion Skills

- `reviewing-and-polishing` — for design doc review and polishing
- Any browser-automation skill — for screenshot verification of design implementation
