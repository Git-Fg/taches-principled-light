# Checkpoint Reference

Checkpoints are markers that tell the executor how to handle a task segment. The execution skill resolves them autonomously using defined strategies.

## Checkpoint Types

| Type | Strategy Resolution | Description |
|------|-------------------|-------------|
| `checkpoint:human-verify` | **Self-Verification** | Used for verification-only gates. The executor self-verifies via CLI commands, test outputs, or file state inspection. Logs the result and continues. |
| `checkpoint:decision` | **Heuristic Resolution** | Used when a choice must be made between paths. The executor applies heuristic rules (simplest path, plan recommendation, reversibility) to choose, then logs the rationale. |
| `checkpoint:human-action` | **Automation Search** | Used when an external action is required. The executor checks for a CLI/API alternative first; if none exists, it placeholds the result, logs an "unavoidable manual gate", and proceeds. |

## Strategy Mapping

Checkpoints determine the overall execution strategy:

- **No checkpoints**: Strategy A (Fully Autonomous)
- **Only `human-verify`**: Strategy B (Segmented Execution)
- **`decision` or `human-action`**: Strategy C (Sequential Execution)

## Authoring Guidelines

- **Be explicit**: State the verification command or criteria in the task.
- **Provide context for decisions**: When using `checkpoint:decision`, document the options and recommended path in the plan.
- **Prefer automation**: Always use `checkpoint:human-verify` for any task that can be verified via CLI (`npm test`, `curl`, etc.).

### Example: `checkpoint:human-verify`
```markdown
### Task 2: Deploy to production
Files: .env.production
Action: Run deployment via CLI, verify health endpoint
Verify: `curl https://api.production.com/health` returns 200
Done: Production deployed and healthy
Checkpoint: checkpoint:human-verify
```
