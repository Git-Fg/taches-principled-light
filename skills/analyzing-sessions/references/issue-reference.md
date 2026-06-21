# ISSUE Mode Reference

Creates a GitHub issue from meta-review findings. Always apply privacy audit before creating any issue.

## Privacy Audit Checklist

Before building the issue body, scan the meta-review file for:

- [ ] Absolute file paths → replace with generic placeholders
- [ ] User prompt text → paraphrase intent only, never quote verbatim
- [ ] Environment variable values → show name only, redact value
- [ ] Token or credential strings → remove entirely
- [ ] Project-specific file contents → summarize without including
- [ ] Session IDs that could identify the user → use generic references

**If any sensitive content is found: ABORT and report what needs to be redacted before proceeding.**

## Issue Body Template

Build from the meta-review file using this structure:

```markdown
## What Happened
{1-3 sentence summary of the behavioral pattern — no file paths, no user quotes}

## Session Context
- Session scope: {marketplace-only | custom-rules | mixed}
- Plugins loaded: {list or NONE}
- Rules active: {list or NONE — use "NONE" for marketplace-only sessions}

## Behavioral Anti-Patterns
{PLUGIN-scope findings only — numbered list with evidence, no file paths}

## Suggestions
{Concrete improvement proposals — numbered, each with rationale}

## What Went Well
{2-3 positive patterns observed — helps balance the report}

## Scope
- Actionable findings: {count}
- Excluded (user-file/environment scope): {count}
- Report status: {advised|NOT advised}
```

## CREATE Mode (default)

### Prerequisites

1. **Verify `gh` is available** — `which gh`
   - If missing: tell user to install GitHub CLI first
2. **Verify git remote** — `git remote get-url origin`
   - If missing: tell user this only works in a git repo with a GitHub remote
3. **Verify review file exists** — read from `docs/principled/scratch/meta-review-{session_id}.md`

### Process

1. **Privacy audit** — scan meta-review file, redact sensitive content
2. **Build issue body** — use template above, apply privacy scrub
3. **Write to temporary file** — `docs/principled/scratch/issue-body-{session_id}.md`
4. **Ensure label exists (best-effort — non-admin users may lack permissions)**:
   ```bash
   if ! gh label view "meta-review" >/dev/null 2>&1; then
     if ! gh label create "meta-review" \
         --description "Behavioral review from session analysis" \
         --color "1D76DB" >/dev/null 2>&1; then
       echo "Note: 'meta-review' label unavailable (insufficient permissions or repo policy). Issuing without the label." >&2
       META_LABEL_FLAG=""
     else
       META_LABEL_FLAG='-l "meta-review"'
     fi
   else
     META_LABEL_FLAG='-l "meta-review"'
   fi
   ```

5. **Create issue**:
   ```bash
   gh issue create \
     -t "[meta] {1-line summary from behavioral pattern}" \
     -F {body_file} \
     $META_LABEL_FLAG
   ```
6. **Report URL** to user. If the issue was filed without the label, note this in your report so the user can add the label manually.

## DRY-RUN Mode (--dry-run flag)

Build the issue body from the meta-review file (same template as CREATE mode) and print to stdout with `cat`. Do not invoke `gh issue create`. Return the full body so the user can review before running CREATE.

## Scope Exclusion Gate

If meta-review file shows `Report NOT advised`:

> "The review found no actionable plugin-scope findings. All issues trace to user configuration or environment state. Creating a public issue is not recommended — the root cause is outside the plugin's control."

The user can override with explicit confirmation. If they confirm, proceed with CREATE mode.

## Subagent Pattern

For privacy audit and body construction, spawn a subagent generalist for isolated reviewwith lens "sanitize this meta-review finding for public GitHub issue creation — strip workspace file contents, user prompts verbatim (paraphrase intent), project paths, environment variables, tokens, credentials; construct a public-friendly issue body":

```
spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why.":
Input: {meta_review_path}
Output: {issue_body_path}
```

The main agent then uses Bash to invoke `gh issue create` with the sanitized body.