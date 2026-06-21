# SAST Patterns

Static Application Security Testing — identify code-level vulnerabilities through pattern analysis.

## OWASP Top 10 Coverage

| OWASP Category | What to Find | Common Patterns |
|----------------|--------------|-----------------|
| **A01 Broken Access Control** | Missing authorization, IDOR, privilege escalation | Direct object references, role checks without DB verification, client-side auth |
| **A02 Cryptographic Failures** | Weak crypto, hardcoded keys, improper storage | MD5/SHA1 for passwords, ECB mode, keys in source |
| **A03 Injection** | SQL, NoSQL, OS, LDAP injection | String concatenation in queries, unsanitized input |
| **A04 Insecure Design** | Business logic flaws, missing rate limits | No throttling, predictable tokens, missing validation |
| **A05 Security Misconfiguration** | Default creds, verbose errors, open cloud storage | Stack traces in production, CORS wildcard, debug mode |
| **A06 Vulnerable Components** | Outdated libraries with known CVEs | (see DEPENDENCY-AUDIT) |
| **A07 Auth Failures** | Weak auth, session fixation, credential stuffing | No rate limiting on login, predictable session IDs |
| **A08 Data Integrity Failures** | Deserialization attacks, CI/CD injection | Pickle/yaml unsafe deserialization, unvalidated pipeline inputs |
| **A09 Logging Failures** | Missing audit trails, no breach detection | No login failure logging, missing transaction logs |
| **A10 SSRF** | Server-side request forgery | URL validation without allowlist, redirect following |

## Decision Criteria

| Situation | Action |
|-----------|--------|
| User input flows to database query | Flag injection risk, check parameterization |
| Auth checks missing on data access | Flag broken access control |
| External URL constructed from user input | Flag SSRF risk |
| Cryptographic operation with hardcoded key | Flag critical, suggest env vars |
| Error messages expose stack traces | Flag security misconfiguration |
| File upload without type validation | Flag injection and path traversal |
| Deserialization of untrusted input | Flag A08, suggest schema validation |

## Code Patterns to Flag

### Injection Patterns (Critical)

\`\`\`
# SQL Injection — flag all of these
query = "SELECT * FROM users WHERE id=" + userId
cursor.execute(f"SELECT * FROM users WHERE id={userId}")

# Safe patterns
cursor.execute("SELECT * FROM users WHERE id=%s", (userId,))
query = db.select(User).where(User.id == userId)
\`\`\`

### Broken Access Control (High)

\`\`\`
# IDOR — direct object reference without ownership check
def get_invoice(invoice_id):
    return db.get(Invoice, invoice_id)  # No user check

# Safe pattern
def get_invoice(invoice_id):
    invoice = db.get(Invoice, invoice_id)
    if invoice.user_id != current_user.id:
        raise Forbidden()
    return invoice
\`\`\`

### SSRF Patterns (High)

\`\`\`
# Unsafe — user input in URL construction
response = requests.get(user_provided_url)

# Safe patterns
parsed = urlparse(url)
if parsed.hostname not in ALLOWED_HOSTS:
    raise ValidationError()
if parsed.hostname.endswith('.internal'):
    raise ValidationError()
\`\`\`

## Anti-Patterns with Consequences

| Wrong | Right | Consequence |
|-------|-------|-------------|
| Client-side auth checks only | Server-side authorization on every request | Client-side checks are trivially bypassed |
| Input validation with allowlist bypass | Strict allowlist validation | Blocklists miss edge cases, allowlists miss future bypasses |
| Storing passwords with reversible encryption | Password hashing with salt (bcrypt/argon2) | Reversible encryption enables credential theft |
| Generic error messages | Structured error codes | Stack traces reveal internal architecture to attackers |
| Debug mode in production | Environment-specific logging levels | Debug output exposes sensitive context |
| CORS wildcard for development | Explicit origin allowlist | Wildcard allows cross-site data exfiltration |
