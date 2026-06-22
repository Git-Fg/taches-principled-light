# review — code review

The CLI has a dedicated `ultrareview` subcommand for cloud-hosted multi-agent code reviews. This is the right way to do code review from the CLI — it's not a prompt pattern, it's a real subcommand with structured output.

## Run a review of the current branch

```bash
claude ultrareview
```

Reviews the current branch's diff against the default branch. Prints findings to stdout.

## Review a specific PR

```bash
claude ultrareview <pr-number>                              # PR number
claude ultrareview https://github.com/<owner>/<repo>/pull/<pr-number>   # PR URL
claude ultrareview feature-branch                           # branch name (compared to default branch)
```

## Get structured findings (JSON)

```bash
claude ultrareview --json
```

Prints the raw `bugs.json` payload instead of the formatted findings. Use this when an agent will parse the findings.

## Set a timeout

```bash
claude ultrareview --timeout 60         # wait up to 60 minutes
```

Default timeout is 30 minutes. The review aborts and prints partial findings on timeout.

## Review as a prompt pattern (no ultrareview)

If you need a quick, local review (not cloud-hosted, no multi-agent), use the prompt pattern:

```bash
claude -p "Review the changes in this branch for bugs, security issues, and code quality. Be specific: cite file:line for each finding. Do not propose architectural rewrites — focus on what's actually wrong in the diff." \
  --output-format json \
  --add-dir .
```

The structured-output skill (`--json-schema`) can enforce a finding-shape contract:

```bash
claude -p "Review the changes in this branch" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"findings":{"type":"array","items":{"type":"object","properties":{"file":{"type":"string"},"line":{"type":"integer"},"severity":{"type":"string","enum":["blocker","warning","suggestion"]},"description":{"type":"string"}},"required":["file","line","severity","description"]}}}}'
```

Prefer `claude ultrareview` for serious reviews. The prompt pattern is a fallback for "I just want a quick sanity check" cases.
