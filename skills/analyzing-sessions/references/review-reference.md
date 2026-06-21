# REVIEW Mode Reference

Diagnoses behavioral anti-patterns in Claude Code session transcripts.

## Privacy Protocol

The a subagent generalist subagent spawned for this work MUST receive a privacy scrub directive in its spawn prompt — strip from output:
- File contents from the user's workspace
- User prompts verbatim — paraphrase intent only
- Project directory paths
- Environment variables, tokens, credentials

Output contains only: behavioral patterns, tool names, error categories, and suggestions.

## Severity Classification

| Severity | Definition | Action |
|----------|------------|--------|
| **HIGH** | Actionable PLUGIN root cause — skill or agent definition is the clear cause | Must appear in report |
| **MEDIUM** | Possible improvement — plugin could help but root cause ambiguous | Include with caveat |
| **LOW** | Informational — no actionable fix, pattern worth noting | Include at bottom |

## Scope Classification

| Scope | Definition | Reportable? |
|-------|------------|-------------|
| **PLUGIN** | Skill routing failure, agent misconfiguration, command defect | YES |
| **USER-FILE** | Custom rules, project CLAUDE.md, user settings | NO — outside plugin control |
| **ENVIRONMENT** | OS-level issues, PATH problems, permission errors | NO — outside plugin control |
| **MODEL** | LLM behavior, hallucination, reasoning failures | NO — not plugin issue |

## REVIEW Mode Process

1. **Discover session** — locate `~/.claude/sessions/{uuid}/raw-transcript.jsonl`
2. **spawn a subagent generalist for isolated review** with the lens "diagnose behavioral anti-patterns in this Claude Code session transcript — tool misuse, skill routing failures, skipped verifications, instruction-following failures, error recovery failures; classify each by severity (HIGH/MEDIUM/LOW) and scope (PLUGIN/USER-FILE/ENVIRONMENT/MODEL); extract what went well; produce a scope verdict". Include the privacy scrub directive and the output path.
3. **Critic reads full JSONL** — identifies anti-patterns in its isolated context.
4. **Critic writes findings** to `docs/principled/scratch/meta-review-{session_id}.md`
5. **Main agent reads output** — summarizes for user with scope verdict

### Critic Spawn Prompt

```
You are a a subagent generalist subagent reviewing a Claude Code session transcript.

Your task:
1. Read the full transcript at {transcript_path}
2. Identify behavioral anti-patterns:
   - Tool misuse or incorrect tool selection
   - Skill routing failures or suboptimal skill loading
   - Skipped verifications or missing checks
   - Instruction-following failures
   - Error recovery patterns that failed
3. Classify each finding by severity (HIGH/MEDIUM/LOW) and scope (PLUGIN/USER-FILE/ENVIRONMENT/MODEL)
4. Extract what went well — positive patterns observed
5. Produce a scope verdict: is this reportable to plugin maintainers?

Privacy scrub: strip workspace file contents, user prompts verbatim (paraphrase intent), project directory paths, environment variables, tokens, credentials. Output contains only: behavioral patterns, tool names, error categories, suggestions.

Write your findings to {output_path} in this format:

## Session Overview
- Session ID: {uuid}
- Duration: {ms}ms
- Cost: ${cost}

## Behavioral Anti-Patterns
1. **[HIGH/MEDIUM/LOW]** {Title}
   - Evidence: {specific events from transcript}
   - Scope: {PLUGIN|USER-FILE|ENVIRONMENT|MODEL}
   - Root cause: {why this happened}

## What Went Well
- {positive pattern 1}
- {positive pattern 2}

## Scope Verdict
- Actionable findings: {count} (PLUGIN scope)
- Excluded findings: {count} (USER-FILE/ENVIRONMENT/MODEL scope)
- Report status: {advised|NOT advised}
```

## INVESTIGATE Mode Process

For deep investigation of structural or recurring failures:

1. **Discover session** — same as REVIEW
2. **Spawn 2 parallel subagents**:

   **Diagnostic agent** (spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why."):
   ```
   Read {transcript_path}, identify anti-patterns, classify by severity and scope.
   Write to {output_dir}/diagnostic.md
   ```

   **Context & Outcome agent** (a subagent explorer w/ scope "analyze git state, environment, and behavioral outcomes — what worked vs what broke"):
   ```
   Analyze git state, environment, and behavioral outcomes (what worked vs what broke).
   Write to {output_dir}/context-outcome.md
   ```

3. **Synthesize** — after all subagents return:
   - Merge findings into unified report
   - Cross-reference: does git state explain any anti-patterns?
   - Deduplicate across subagents
   - Assign final severity and scope
4. **Scope gate**:
   - All findings USER-FILE/ENVIRONMENT/MODEL → Report NOT advised
   - Any PLUGIN findings → Report advised with specific suggestions
5. **Write unified report** to `docs/principled/scratch/meta-review-{session_id}.md`
6. **Present to user** — summary with next-step suggestion (ISSUE mode if actionable)

## INVESTIGATE Fan-Out Rationale

Two parallel isolated-context agents avoid cross-contamination in findings:
- Each agent reads the transcript independently in its own disposable context
- No agent influences another agent's interpretation
- Synthesis happens after independent analysis
- Reduces false positives from single-agent bias