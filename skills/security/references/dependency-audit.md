# Dependency Audit

Scan dependencies for known vulnerabilities and supply chain risks.

## Decision Criteria

| Situation | Action |
|-----------|--------|
| After adding new dependency | Audit immediately, check for known CVEs |
| Periodic security review | Check for outdated packages with known vulnerabilities |
| After vulnerability disclosure | Identify affected projects and prioritize updates |
| Before major release | Full dependency audit with remediation plan |

## Audit Process

1. **Inventory** — List all direct and transitive dependencies with versions
2. **Vulnerability Check** — Query CVE databases (NVD, OSV, GitHub Advisory)
3. **Severity Assessment** — Rate by CVSS score, exploitability, impact
4. **Remediation** — Update to patched version, find alternative, or accept risk with mitigation

## Vulnerability Severity Mapping

| CVSS Score | Rating | Action |
|------------|--------|--------|
| 9.0-10.0 | Critical | Update immediately, consider removal |
| 7.0-8.9 | High | Update within 7 days |
| 4.0-6.9 | Medium | Update within 30 days |
| 0.1-3.9 | Low | Update at next release cycle |

## Common Supply Chain Risks

| Risk | Indicator | Remediation |
|------|-----------|-------------|
| Typosquatting | Similar names to popular packages | Verify exact package name, check publisher |
| Maintainer takeover | Abandoned packages with new commits | Find maintained alternative |
| Malicious code | Unexpected network calls, file I/O | Review source, use lockfiles |
| Dependency confusion | Internal package shadowing public | Use scoped namespaces, verify registry |

## Anti-Patterns with Consequences

| Wrong | Right | Consequence |
|-------|-------|-------------|
| No lockfile committed | Commit lockfiles for reproducible builds | Mismatched versions expose vulnerabilities |
| Auto-update without review | Review changelogs before updating | Breaking changes introduce new vulnerabilities |
| Ignoring audit warnings | Treat audit output as blocking | Known vulnerabilities become exploitable |
| Using latest without checking | Pin to tested versions in CI | Latest may introduce regressions |
