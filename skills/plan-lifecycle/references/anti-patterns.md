# Anti-Patterns in Plan Execution

## Skipping Verification

Marking a task complete without running the verify command. Verification is mandatory - it is the only proof the task actually succeeded.

## Treating Auth Gates as Errors

Retrying authentication failures repeatedly instead of pausing and presenting the auth steps clearly to the user.

## Continuing Past Rule 4

Attempting to proceed with an architectural change without user input. Rule 4 requires STOP + ASK + WAIT.

## Creating Vague Summaries

"Task completed" tells nothing. "JWT refresh rotation implemented using jose library with 15-minute access token expiry" tells everything.

## Ignoring Context Limits

Loading all project files instead of only those referenced in the plan. Context pressure degrades execution quality.

## Thought/Action/Observation Anti-Pattern

**The Problem:**
When Claude sees code blocks with `Thought:`, `Action:`, `Observation:` patterns, it interprets them as output templates to mimic, not as instructions to execute. Instead of calling Write() tool, it generates text that says "Thought: Let me analyze... Action: Write(...)".

**Why This Happens:**
1. Code blocks look like output format - Claude thinks "this is what my response should look like"
2. Pattern mimicking - The agent copies the structure as text instead of executing
3. Pseudo-code confusion - `Action: Write(...)` looks like code to output, not a command to run

**The Fix:**
Replace all Thought/Action/Observation examples with imperative natural language:
- Instead of: "Thought: I need to read the task file..."
- Write: "First, use your native tools to load the task file."

**This affects ANY skill that shows tool calls in a demonstrated output format.**