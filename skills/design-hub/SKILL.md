---
name: design-hub
description: "Load when the user needs a color palette, font pairing, design tokens, spacing rules, or visual hierarchy guidance. Use when the user says 'pick palette', 'design system', 'color tokens', 'font pair', 'type scale', 'visual hierarchy', 'design review', 'mood palette', 'WCAG contrast', or 'design principles'. Covers the full design pipeline from mood to implementation. Do NOT use for accessibility-only audits (use security SAST) or browser automation."
when_to_use: |
  Route to the matching sub-skill based on the user's intent. Use browser
  automation for screenshot-based dogfood loops.
argument-hint: "[palette|typography|tokens|principles|examples|full-design-system]"
allowed-tools: Read
license: MIT
---

# Design Hub

Route to the right design sub-skill based on user intent.

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
