# Compliance Checklists

Verify adherence to security standards and compliance frameworks.

## Supported Frameworks

| Framework | Focus Areas | Key Requirements |
|-----------|------------|------------------|
| **OWASP ASVS** | Application security | 14 requirement categories, 3 assurance levels |
| **GDPR** | Data privacy | Consent, right to erasure, breach notification |
| **SOC2** | Service organization controls | Security, availability, confidentiality |
| **PCI-DSS** | Payment card data | Secure transmission, access control, testing |
| **HIPAA** | Healthcare data | PHI protection, access controls, audit trails |

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Pre-audit preparation | Map requirements to implementation, identify gaps |
| Security review for compliance | Score against framework, prioritize gaps |
| New feature compliance | Verify feature meets applicable requirements |
| Third-party vendor review | Assess against security questionnaire |

## Compliance Assessment Process

1. **Scope Definition** — Identify applicable frameworks and requirements
2. **Evidence Collection** — Gather implementation evidence (code, configs, logs)
3. **Gap Analysis** — Map evidence to requirements, identify missing controls
4. **Risk Assessment** — Evaluate gaps by likelihood and impact
5. **Remediation Planning** — Prioritize fixes, assign owners, set timelines

## Key Compliance Areas

### Access Control (OWASP A01, SOC2 CC6)

- [ ] Authentication enforced on all sensitive endpoints
- [ ] Authorization checked server-side, not just client-side
- [ ] Session management with appropriate timeout and rotation
- [ ] Principle of least privilege applied

### Data Protection (GDPR, PCI-DSS)

- [ ] Sensitive data encrypted at rest and in transit
- [ ] No sensitive data in logs or error messages
- [ ] Data retention policies implemented
- [ ] Right to erasure implemented

### Security Configuration (OWASP A05)

- [ ] Default credentials changed
- [ ] Debug mode disabled in production
- [ ] Error messages don't expose stack traces
- [ ] Security headers configured (CSP, HSTS, X-Frame-Options)

### Logging and Monitoring (OWASP A09)

- [ ] Authentication events logged
- [ ] Authorization failures logged
- [ ] Logs protected from tampering
- [ ] Alerts configured for suspicious activity

## Anti-Patterns with Consequences

| Wrong | Right | Consequence |
|-------|-------|-------------|
| Self-certifying compliance | Independent audit verification | False sense of security, audit failures |
| Checking only new code | Continuous compliance monitoring | Legacy code accumulates compliance debt |
| Paper compliance (docs only) | Evidence-based verification | Gap between policy and implementation |
| One-time audit | Ongoing compliance monitoring | New code introduces new gaps |
