---
name: design-principles
description: "Load when explaining why a design choice works — white space, contrast, proximity, alignment, repetition, and visual hierarchy. Use when the user asks why a design looks good or bad. Do NOT use for typography specs, palettes, or visual examples."
when_to_use: |
  Load for any design-taste or "why" question. For concrete specs,
  load `typography-guide`; for before/after examples, load
  `design-good-bad-examples`.
allowed-tools: Read
argument-hint: "[design-question] [context]"
license: MIT
---

# Design Principles

The original perceptual and cognitive research summary.

## Related skills (load together)

- `typography-guide` — the *what* (specs, sizes, line heights)
- `design-good-bad-examples` — the *how* (BAD-vs-GOOD markup)
- `design-system-palettes` — color tokens
- `pdf-design-guide` — mood + contrast
- Browser automation — confirms the principles actually held

## How to use this skill

1. When a spec is missing, fall back on the perceptual research cited
   in [`references/principles-catalog.md`](references/principles-catalog.md) (saccade-based reading, 60-70% coverage, 1.2-1.45× line height, 1-inch margins for academic / luxury documents, etc.).
2. Cite the principle number in your reply so the user can audit.
3. When you've made a layout decision, run browser automation to
   confirm it actually rendered the way the principle predicts.

---

WHY certain typographic choices look good — the perceptual and psychological
reasons behind professional document design. Use this to make judgment calls
when exact specs are not provided.

## Table of Contents

1. [White Space & Breathing Room](references/principles-catalog.md#1-white-space--breathing-room)
2. [Contrast & Scale](references/principles-catalog.md#2-contrast--scale)
3. [Proximity & Grouping](references/principles-catalog.md#3-proximity--grouping)
4. [Alignment & Grid](references/principles-catalog.md#4-alignment--grid)
5. [Repetition & Consistency](references/principles-catalog.md#5-repetition--consistency)
6. [Visual Hierarchy & Flow](references/principles-catalog.md#6-visual-hierarchy--flow)

---

## Summary: Decision Checklist

When you are unsure about a typographic choice, run through these checks:

| Principle | Question | If No... |
|-----------|----------|----------|
| White Space | Does the page have at least 30% white space? | Increase margins or spacing |
| Contrast | Can I count heading levels by squinting? | Increase size ratios (target 1.25x) |
| Proximity | Does each heading clearly belong to text below it? | Make space-before > space-after (2:1) |
| Alignment | Is English left-aligned and CJK justified? | Switch alignment mode |
| Repetition | Do all same-level elements use the same style? | Replace direct formatting with styles |
| Hierarchy | Can I see the document structure at arm's length? | Add more differentiation signals |

**When two principles conflict, prioritize in this order:**

1. **Readability** (white space, line spacing) — always wins
2. **Hierarchy** (contrast, scale) — readers must find what they need
3. **Consistency** (repetition) — builds trust
4. **Aesthetics** (alignment, grouping) — the finishing touch