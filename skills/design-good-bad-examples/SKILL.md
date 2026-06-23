---
name: design-good-bad-examples
description: "Load when the user needs side-by-side BAD-vs-GOOD design examples for documents or UI. Use when reviewing a UI, teaching design taste, or answering 'what's wrong with this layout?'. Do NOT use for general critique, palette selection, or typography."
when_to_use: |
  Load for design review or taste coaching. Pair with browser automation when
  checking whether the issues appear in a live app.
allowed-tools: Read
argument-hint: "[artifact-or-design-review] [criteria]"
license: MIT
---

# Good vs Bad Design Examples

A side-by-side reference showing common design mistakes and their fixes, with exact OpenXML parameter values. Use this to develop an intuitive sense of what makes a document look professional versus amateur.

## How to use this skill

This skill is a catalog of common BAD/GOOD pairs. The detailed examples (10 categories, ~800 lines) live in [`references/examples-catalog.md`](references/examples-catalog.md) — load that file when you need the full OpenXML parameter values for a specific category.

**Categories in the catalog:**

1. Font Size Disasters — missing hierarchy, oversized titles, undersized body
2. Spacing Crimes — collapsed paragraphs, uniform line-height, no spacing-before
3. Margin Mistakes — wall-to-wall text, asymmetric margins, page-edge bleed
4. Table Ugliness — gridless spreadsheets, headerless tables, oversize borders
5. Font Pairing Failures — decorative body fonts, all-italic headers, monospace UI
6. Color Abuse — pure-black backgrounds, rainbow text, low-contrast accents
7. List Formatting Issues — bullets as paragraphs, mixed bullet styles, hang-indent loss
8. Header/Footer Problems — missing page numbers, oversized titles, blank-zone pages
9. CJK-Specific Mistakes — mojibake, full-width punctuation in Latin runs, mixed alignment
10. Overall Document Feel — Word-defaults look vs intentionally-curated look

Format: Each comparison shows the **BAD** version first (the mistake), then the **GOOD** version (the fix), with OpenXML markup and a short explanation.

---

## Quick Reference: Safe Defaults

A cheat sheet of values that produce a professional result for most Western business documents:

| Element | Value | OpenXML |
|---------|-------|---------|
| Body font | Calibri 11pt | `w:sz="22"` |
| H1 | Calibri Light 20pt | `w:sz="40"` |
| H2 | Calibri Light 16pt | `w:sz="32"` |
| H3 | Calibri 13pt bold | `w:sz="26"`, `w:b` |
| Body color | #333333 | `w:color="333333"` |
| Heading color | #1F4E79 | `w:color="1F4E79"` |
| Line spacing | 1.15x | `w:line="276" w:lineRule="auto"` |
| Para spacing after | 8pt | `w:after="160"` |
| H1 spacing | 24pt before, 10pt after | `w:before="480" w:after="200"` |
| H2 spacing | 16pt before, 6pt after | `w:before="320" w:after="120"` |
| Margins | 1in all around | `w:pgMar` all `"1440"` |
| Table cell padding | 0.08in / 0.12in | `w:w="115"` / `w:w="173"` |
| Header/footer size | 9pt gray | `w:sz="18" w:color="808080"` |
| List indent | 0.25in per level | `w:left="360" w:hanging="360"` |
| List item spacing | 2pt after | `w:after="40"` |

