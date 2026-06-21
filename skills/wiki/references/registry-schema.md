# Wiki Registry Schema

This file is the single source of truth for the format of `~/.claude/wiki-root.md`. The hub skill (`SKILL.md`) and a subagent explorer all cite this file imperatively before performing any wiki operation. Read it once at the start of any wiki work and the rest of the operation flows from what is here.

The registry tells the orchestrator three things: *which wikis exist on disk*, *how to pick the right one when the user's intent is vague*, and *what to read inside each wiki before doing anything else*. Everything in this document serves one of those three jobs.

## Canonical Example

A registry file holds one TOML table per wiki. The annotations are part of the canonical example — keep similar comments in real registries so a human editing the file knows what each field is for.

```toml
# Wiki registry — one [<alias>] table per wiki. Add a new table to register a new wiki.
# See your installed tp-wiki plugin's references/registry-schema.md for the full spec.

[pharma]
# Absolute path on disk. No environment variable substitution.
path = "/Users/felix/Documents/PharmaWiki"

# Free-form tags that classify the WIKI itself (used to pick the right wiki when
# the user's intent is vague, e.g., "check the medical notes" → match `medical`).
# These do NOT constrain the page-level tag taxonomy inside the wiki — that
# stays in each wiki's own SCHEMA.md.
tags = ["medical", "reference", "french"]

# Files the agent MUST read before any operation on this wiki, in order.
# Bare filenames only; the orchestrator prepends `path`. Forbidden:
# absolute paths, $WIKI_ROOT/... substitution, [[wikilinks]].
what_to_read = ["SCHEMA.md", "index.md", "log.md"]

# Natural-language description, ≤1500 chars. The first ~200 chars MUST be terse
# routing keywords (what this wiki covers, when to pick it). The remainder is
# behavioral steering prose.
description = """
Pharmacology reference wiki covering CGRP antagonists, prescription logic,
and drug interactions. Source of truth for prescribing decisions in primary
care. Use this when the user asks about drug names, interactions, or French
prescription rules.

When operating on this wiki, prefer precision over completeness — every claim
must cite the source page. Drug names follow ANSM nomenclature; cross-reference
with INN when relevant. Never recommend off-label use without flagging the source.
"""
```

There are no markdown wrappers, no YAML frontmatter blocks, no fenced code sections around the tables. The file is pure TOML from the first non-comment line to the last.

## The Four Fields

**`path`** is a TOML string holding the absolute filesystem path to the wiki's root directory. It is a literal path — no `~` expansion, no `$HOME` substitution, no environment variable lookup. The user writes the resolved path directly. The orchestrator uses `path` as the working directory for every file operation against that wiki.

**`tags`** is a TOML array of strings. Each tag classifies the WIKI ITSELF — its subject matter, its language, its purpose. Tags are free-form: there is no controlled vocabulary, no enum, no validation. The orchestrator uses `tags` at routing time, when the user's signal is a topic word ("the medical notes", "my French stuff") rather than a wiki name. Tags MUST NEVER be used to describe the page-tag taxonomy inside the wiki — that lives in each wiki's own `SCHEMA.md` and is unrelated to this field.

**`what_to_read`** is a TOML array of strings. Each entry is a bare filename, relative to the wiki's `path`. Common entries are `SCHEMA.md` (the wiki's own conventions), `index.md` (the page index), and `log.md` (the change log). The orchestrator MUST prepend the wiki's `path` to each entry before opening the file. Absolute paths, `$WIKI_ROOT/...` substitution, and `[[wikilinks]]` are forbidden — they break portability and force the agent to do template resolution it does not need to do.

**`description`** is a TOML triple-quoted string carrying a natural-language description of the wiki, up to 1500 characters. The description does two jobs at once: it steers routing (helping the orchestrator decide which wiki fits the user's request) and it steers behavior once a wiki has been chosen (telling the agent what matters, what to prioritise, what to avoid). The front-load convention below explains how to write the description so it serves both jobs cleanly.

## Parsing the Registry

At the start of any wiki operation, read the file at `~/.claude/wiki-root.md`. If the file does not exist, or contains no `[alias]` tables, fall through to the no-registry flow described below. Otherwise, walk the file from top to bottom collecting tables.

A new table begins at any line that matches the pattern `[<alias>]` (a single word in square brackets, alone on its line). Everything between that line and the next `[alias]` line (or end of file) belongs to that table. Inside the table, each `field = value` line carries one of the four schema fields. Strings are quoted with `"..."`; arrays are bracketed with `[...]`; the description is a triple-quoted block whose contents run from the opening `"""` to the next standalone `"""` line. Lines starting with `#` and blank lines are ignored.

Build a list of wiki objects, one per table — each object carries the alias (the bracket label), the `path`, the `tags`, the `what_to_read` list, and the `description`. That list is the operating registry for the rest of this session.

## Picking the Right Wiki — Disambiguation Rules

When several wikis are configured, the orchestrator MUST pick one before spawning any subagent. Apply these rules in order; stop at the first match.

| User signal | Action |
|---|---|
| User named a specific wiki by alias or number ("the pharma wiki", "wiki 2") | Match against alias labels or 1-based file order. If no match, ask the user to clarify. |
| User said a topic word that matches the `tags` of exactly one wiki ("check the medical notes" → `tags` contains `medical`) | Use that wiki without asking. |
| User said a topic word that matches `tags` of multiple wikis | Ask the user to disambiguate, listing the candidate aliases and their `tags`. |
| User's wording matches the routing portion of a `description` (the first ~200 chars) | Use that wiki without asking. |
| User said nothing about which wiki, and exactly one is configured | Use it without asking. |
| User said nothing about which wiki, and multiple are configured | Ask: "Which wiki? You have: <aliases listed with their first-line description>. Or 'set up a new one'." |
| User said "all wikis" or wants an operation across them | Run the operation once per configured wiki and aggregate results. |

Alias numbering is 1-based by the order the `[alias]` tables appear in the file. The first table is wiki 1, the second is wiki 2, and so on.

## When No Registry Exists

If `~/.claude/wiki-root.md` does not exist, or has no `[alias]` tables (only comments and blank lines), tell the user:

> "No wikis configured. To set up:
> 1. Create the directory for your wiki (e.g., `mkdir -p ~/notes/main`).
> 2. Add a `[<alias>]` table to `~/.claude/wiki-root.md` with at minimum a `path` field pointing to that directory. See your installed tp-wiki plugin's references/registry-schema.md for the full schema.
> 3. Re-run the command. Or say 'create a new wiki at <path>' and I'll do steps 1-2 for you."

NEVER guess a path or fabricate a wiki. NEVER write to a wiki the user has not registered.

## Confirming Before Mutating

For INGEST and LINT operations — anything that writes or modifies files inside a wiki — confirm the chosen wiki with the user before doing anything destructive:

> "Operating on: `[<alias>]` at `<path>`. Proceed?"

The confirmation MUST happen after the disambiguation rules pick a wiki and BEFORE any subagent that can write is spawned. QUERY operations (read-only) skip the confirmation — they cannot mutate state.

## The Front-Load Convention for Descriptions

The `description` field does two jobs: routing (picking this wiki over others) and steering (guiding behavior once this wiki is picked). Write the description so the routing keywords come first and the steering prose follows.

The first ~200 characters MUST carry the routing signal — terse keywords naming the subject domain, the language, the source-of-truth claim, and the typical user query that should pick this wiki. The remainder, up to 1500 characters total, carries the steering prose — what matters most when operating on this wiki, what to prioritise, what conventions to honor, what to flag.

This convention mirrors the 200-character front-load rule for Claude Code skill descriptions: high-context sessions truncate metadata from the end, so the routing signal must survive truncation. A description whose routing keywords sit at character 800 is invisible to the orchestrator when context pressure is high.

Write the routing portion as a single dense sentence or two. Write the steering portion as natural paragraphs — prose, not bullet lists. The orchestrator reads prose far more reliably than it reads structured fragments.

## TOML Gotchas for LLM Readers

Use `"""..."""` (triple-double-quote) for multi-line descriptions. Three consecutive `"` characters inside the string are the ONLY content restriction — `[`, `]`, `=`, and markdown links like `[text](url)` are parsed as content without escaping. NEVER use `'''..'''` (triple-single-quote) for descriptions; its content rules are stricter and the failure modes are subtle.

Prefer LF line endings. CRLF leaks into triple-quoted descriptions verbatim — a description authored on Windows can carry stray `\r` characters that the orchestrator passes through to downstream prompts.

The `#` character starts a comment ONLY at the start of a line or after whitespace outside a string. Inside `"..."` or `"""..."""` it is a literal `#`. A description containing `#tag` is safe; do not try to escape it.

## Adding a New Wiki

To register a new wiki: create the wiki's directory on disk (with at minimum a `SCHEMA.md` and `index.md`); open `~/.claude/wiki-root.md`; append a new `[<alias>]` table with the four fields filled in. The alias is the short label you will use to refer to the wiki ("pharma", "work", "personal"). Save the file. The next wiki operation will pick up the new entry automatically — there is no daemon to restart and no cache to invalidate.

When filling in `description` for a new wiki, write the first 200 characters first, treating them as a one-shot routing pitch ("this wiki is for X; pick it when the user asks about Y"). Then expand into the steering paragraphs. A vague or empty description means the orchestrator cannot tell when to pick this wiki over the others.
