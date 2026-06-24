---
name: self-correcting
description: "Load when 3+ tool calls haven't converged, the result is bad, or the agent ignored a guidance field / system-reminder. Use this skill to diagnose what happened from context — no new tool calls — and propose one specific fix. Do NOT use for bug root-cause (use systematic-debugging), post-success insight capture (use reviewing-and-polishing MEMORIZE), or routine tool-call sequences that are still converging."
when_to_use: |
  Load when an agent session shows a failure cascade: 3+ tool calls without
  progress, a bad result that the agent is about to retry with the same
  approach, or explicit guidance/system-reminder that the agent skipped.
  The skill forces a no-tool-call reflection block from existing context.
  Do NOT load for bug root cause diagnosis (systematic-debugging), for
  capturing insights after a successful task (reviewing-and-polishing
  MEMORIZE), or for routine exploratory tool calls that are still
  converging.
allowed-tools: Read, Grep, Glob
argument-hint: "[failure-symptom]"
license: MIT
---

# Self-Correcting

## Why This Skill Exists

When something goes wrong, the temptation is to try again — same approach, minor variation. Push forward because stopping feels like falling behind. This is the failure cascade: the dominant anti-pattern in agent tool-usage. Each retry erodes trust in the agent's reliability and burns context on a hypothesis that was already wrong. The discipline this skill enforces is simple but rare: **stop, look at what just happened, name the gap, propose one concrete fix**. From context. Without firing more tools.

## The Core Rule

**No tool calls during analysis. The data is already in your context.**

This rule is non-negotiable. The failure cascade is fed by re-firing tools on the same broken hypothesis; the analysis step exists to break that loop. Read your own tool-call history from the conversation context. Quote any guidance fields verbatim. Diagnose. Then output the fix.

## The Four-Step Protocol

### Step 1: What did I do?

List each tool call verbatim — not "I searched" but:
```
search intent=web query=X results=10
fetch url=A
fetch url=B
...
```

### Step 2: What did guidance say?

Every tool result that carries instructions (guidance fields, system-reminders, hints in metadata) is telling you something. Quote it. Then admit the gap:
```
Guidance said: "Fetch top 2-3 results"
What I did: fetched all 10
Gap: I was in cascade mode
```

### Step 3: Why did I do it that way?

```
Was the hypothesis wrong, or just the execution?
Did I skip guidance because I "already knew"?
```

### Step 4: One adjustment

```
Not: "read guidance first"
Yes: "fetch top 2-3 per guidance, then stop"
```

The fix must be specific and enforceable on the next attempt. Generic discipline reminders ("be more careful") do not break cascades.

## Tool-Result Guidance Audit

| Signal | Check |
|--------|-------|
| 3+ calls in rapid succession | Strategy not converging — pause |
| Guidance said top 2-3, fetched all | Ignored it — admit it |
| Wrong intent routing | intent=web vs intent=code |
| Generic output | Method didn't match the question |

## The Guidance Field Is Not Decoration

If you ignored guidance, diagnose why:
- Was the text too long? → guidance should be shorter
- Was it mixed with suggestions? → needs to be separate
- Did you skip it? → this is the diagnosis

Output format:
```
Guidance said: "..."
What I did: "..."
Gap: ...
Why: ...
One fix: ...
```

## Cross-Runtime Note

> **Tool-result guidance surfaces differ by runtime.** Claude Code surfaces guidance via `<system-reminder>` blocks and tool-result hints. Codex uses system instructions and tool-call comments. kimi-code embeds hints in tool-result metadata. The discipline is identical — quote the guidance, admit the gap, fix the execution — only the surface signal differs. MCP servers are the richest guidance-field source today; standalone CLI tools may produce no guidance at all, in which case the cascade trigger is "3+ calls without progress" alone.

## CONTRAST

- **vs `systematic-debugging`:** That skill diagnoses *why the code is wrong*. This skill diagnoses *why the agent's tool usage is wrong*. Same root-cause discipline, different object of analysis. If the bug is in code, use systematic-debugging. If the agent ignored guidance / fetched all 10 results instead of top 2-3 / repeated the same approach 3 times, use self-correcting.
- **vs `reviewing-and-polishing` MEMORIZE:** MEMORIZE captures insights *after a successful task* and writes them to memory. This skill diagnoses *a failed task* and produces one in-session fix. Use MEMORIZE to remember; use self-correcting to repair.
- **Not contrasted with** `crafting-skills`, `evaluating-skills`, `applying-guardrails`: those operate on a different layer (skill authorship, skill measurement, design discipline) and don't trigger on tool-usage failure cascades. Explicit contrast would invent nearness that doesn't exist.

## When to Stop Diagnosing

Invoke self-correcting at most once per failure: produce one diagnosis block, apply the one fix, retry. If a second cascade happens in the same session, escalate to the user with the diagnosis block as context, or invoke `crafting-skills` for a routing audit (the cascade may be a symptom of a skill description that triggers incorrectly). Do not loop self-correcting on itself.
