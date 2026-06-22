# workflows

End-to-end patterns that combine multiple operations. The hub is the sole router — for any single-operation detail, return there and follow the reference index.

**Workflow 1: One-shot task**

```bash
claude -p "Refactor user.rs to use the newtype pattern" --permission-mode acceptEdits
```

**Workflow 2: Multi-turn session with continuity**

```bash
# Turn 1
SESSION_ID=$(claude -p "Start a refactor of the auth module" --output-format json | jq -r '.session_id')

# Turn 2 (later)
claude --resume "$SESSION_ID" -p "Continue: also add tests"
```

**Workflow 3: Background agent + polling**

```bash
# Spawn (in a separate process / Bash background)
claude -p "Generate rustdoc for src/parser.rs" --output-format json > /tmp/doc-gen.json 2>&1 &

# Poll the result
while kill -0 $! 2>/dev/null; do sleep 5; done
cat /tmp/doc-gen.json | jq -r '.result'
```

Or use the agent view:

```bash
# List running agents
claude agents --json | jq '.[] | {name: .name, status: .status}'
```

**Workflow 4: Code review of a PR**

```bash
claude ultrareview <pr-number> --json | jq '.findings[]'
```

**Workflow 5: Structured output for downstream parsing**

```bash
claude -p "Classify this ticket: '$TICKET_TEXT'" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"category":{"type":"string","enum":["bug","feature","question"]},"priority":{"type":"string","enum":["low","medium","high"]}},"required":["category","priority"]}}' \
  | jq '{category: .result | fromjson | .category, priority: .result | fromjson | .priority}'
```

Or use `--json-schema` together with a prompt that tells Claude to populate the result with the structured object directly:

```bash
claude -p "Classify this ticket. Respond with a JSON object that matches the schema." \
  --output-format json \
  --json-schema '...' \
  | jq -r '.result' | jq .
```

The exact path depends on whether the model returns a JSON string (which it usually does) or a pre-parsed object.

**Workflow 6: Headless capture into a session for later review**

```bash
SESSION_ID=$(claude -p "Run a security audit" --output-format json | jq -r '.session_id')
# Later, resume and ask follow-ups:
claude --resume "$SESSION_ID" -p "Drill into the auth findings"
```
