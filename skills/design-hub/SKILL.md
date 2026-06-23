---
name: design-hub
description: "Load when the user needs design guidance — palette, typography, tokens, spacing, or visual hierarchy. Use when the user says 'pick palette', 'design system', or 'font pair'. Covers the full design pipeline from mood to implementation. Do NOT use for accessibility-only audits (use security SAST) or browser automation."
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

This file is a **router**, not a workflow. Each of the 5 sub-skills below is a self-contained, independently-discoverable skill per the [Agent Skills open standard](https://agentskills.io/). Compliant agents (Claude Code, Cursor, Codex, Gemini CLI, VS Code Copilot) see all 6 skills (this hub + 5 leaves) in their startup index and route directly to the right leaf without consulting this body.

The hub exists for **two audiences**: (a) agents that don't recurse into subdirectories and need a single entry point that mentions every leaf, and (b) humans and `agent-device` workflows that want the workflow order, routing table, and companion-skill links in one place.

If you're an agent that recursed here from a top-level scan: you don't need this router. Match the user's intent directly against the sub-skill descriptions — they all have `Do NOT use for X (use Y)` negative triggers that disambiguate siblings.

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

- `security` — for WCAG/accessibility audits
- `reviewing-and-polishing` — for design doc review and polishing
- Any browser-automation skill — for screenshot verification of design implementation
