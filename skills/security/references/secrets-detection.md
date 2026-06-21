# Secrets Detection

Detect API keys, tokens, credentials, and sensitive data in code.

## What Counts as a Secret

| Category | Examples | Risk |
|----------|----------|------|
| **API Keys** | AWS access keys, Stripe keys, SendGrid API keys | Financial loss, service abuse |
| **Authentication Tokens** | JWT secrets, session secrets, OAuth client secrets | Account takeover |
| **Credentials** | Database passwords, SSH keys, certificates | System compromise |
| **Private Keys** | RSA/EC private keys, signing keys | Identity forgery |
| **Config Files** | .env with production values, config with secrets | Lateral movement |
| **Tokens** | GitHub tokens, Slack tokens, Twilio tokens | Service abuse, data exfiltration |

## Detection Patterns

### High-Confidence Patterns

```
# AWS credentials
AKIA[0-9A-Z]{16}
aws_secret_access_key|w.aws_access_key_id
xox[baprs]-[0-9a-zA-Z]{10,48}

# API keys
sk_live_[0-9a-zA-Z]{24,}
AIza[0-9A-Za-z_-]{35}
SG\.[0-9A-Za-z_-]{22}\.[0-9A-Za-z_-]{43}
```

### Entropy Detection

Secrets have high entropy. Flag strings where:
- Length > 20 characters
- Contains mixed case, numbers, special characters
- Matches no common word patterns
- Assigned to variables named `key`, `token`, `secret`, `password`, `credential`

## Decision Criteria

| Situation | Action |
|-----------|--------|
| After commit to main | Alert immediately, rotate keys |
| During code review | Flag before merge, block if critical |
| Scanning entire repo | Prioritize by secret type and environment |
| Found in PR | Comment inline, require rebase with secret removal |

## Remediation Workflow

1. **Immediate** — Rotate the exposed secret (it is compromised)
2. **Revoke** — Invalidate the exposed credential in the service
3. **Clean** — Remove secret from git history (git filter-repo or BFG)
4. **Prevent** — Add pre-commit hook, update detection patterns

## Anti-Patterns with Consequences

| Wrong | Right | Consequence |
|-------|-------|-------------|
| `.env` in version control | `.env` in .gitignore, .env.example committed | Full secret exposure on push |
| Reverting to remove secret | Rotating secret + history rewrite | Old commit still exposes credential |
| Commenting out secrets | Moving secrets to environment or secrets manager | Commented secrets often still searchable |
| Using secrets in tests | Using test fixtures or mock credentials | Real credentials appear in test output |
