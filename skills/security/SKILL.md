---
name: security
description: "Load when auditing for security vulnerabilities before production deployment — SAST scanning, dependency auditing, secrets detection, or compliance checks against OWASP, GDPR, SOC2, or PCI-DSS. Use when the user says 'security audit', 'find secrets', 'check for vulnerabilities', or 'is this safe to ship'. Do NOT use for general code review (use reviewing-and-polishing) or Rust-specific dependency policy (use rust)."
allowed-tools: Read, Grep, Glob, Bash, Edit
when_to_use: |
  - User is preparing for production deployment or major release.
  - User wants to audit code for OWASP Top 10 vulnerabilities.
  - User wants to check for outdated or vulnerable dependencies.
  - User needs to find exposed API keys, tokens, or credentials.
  - User requires a compliance check against standards like GDPR, SOC2, or PCI-DSS.
argument-hint: "[mode] [target] [--severity critical|high|medium|low]"
license: MIT
---

## Routing Guidance

- IMMEDIATELY before production deployment, before merging security-related PRs, or when fixing vulnerabilities.
- Do NOT use for architecture design (use restructuring-code) or general code quality (use reviewing-and-polishing REVIEW).

## CONTRAST

- NOT for: investigating root causes of known bugs — use superpowers' `systematic-debugging`
- NOT for: general code quality or polish — use reviewing-and-polishing
- NOT for: architecture design and layering — use restructuring-code
- NOT for: incident postmortem of a past failure — use superpowers' `systematic-debugging`

| If you need to... | Use this mode |
|-------------------|---------------|
| Find code vulnerabilities (injection, auth, access control) | SAST |
| Check for outdated/vulnerable dependencies | DEPENDENCY-AUDIT |
| Find API keys or credentials in code | SECRETS-DETECTION |
| Verify compliance with security standards | COMPLIANCE |

**Quick routing:** Scan code patterns = SAST. Scan packages = DEPENDENCY-AUDIT. Scan for secrets = SECRETS-DETECTION. Audit compliance = COMPLIANCE.

---

## Orchestration Shape

This skill runs as **an orchestration script** — a multi-modal sweep with adversarial reproducibility verification across specialized security dimensions.

**Pattern:** Multi-modal sweep + adversarial reproducibility verify

1. **Sweep** — Dimension-specialist scanners fan out across distinct attack surfaces in parallel.
2. **Verify** — Reproducer agents independently attempt to reproduce the findings.
3. **Triage** — Severity classifier synthesizer prioritizes verified findings.

---

## Decision Router

IF scanning for injection, auth, or access control patterns in code → **SAST** mode — ALWAYS spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why.". You MUST read `references/sast-patterns.md` BEFORE proceeding. Do not make assumptions without reading this file.
IF checking for vulnerable or outdated dependencies → **DEPENDENCY-AUDIT** mode — ALWAYS spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why.". You MUST read `references/dependency-audit.md` BEFORE proceeding. Do not make assumptions without reading this file.
IF finding exposed API keys, tokens, credentials, or private keys in code → **SECRETS-DETECTION** mode — ALWAYS spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why.". You MUST read `references/secrets-detection.md` BEFORE proceeding. Do not make assumptions without reading this file.
IF verifying compliance with security standards or certifications → **COMPLIANCE** mode — ALWAYS spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why.". You MUST read `references/compliance-checklists.md` BEFORE proceeding. Do not make assumptions without reading this file.
IF ambiguous → ask: "Are you scanning code patterns, dependencies, exposed secrets, or compliance standards?"

---

# Security Hub

Four modes targeting distinct security surfaces. Each mode addresses a different attack vector or compliance requirement.

| Mode | Attack Surface | Key Methodology |
|------|---------------|-----------------|
| **SAST** | Code-level vulnerabilities | Pattern matching, AST analysis |
| **DEPENDENCY-AUDIT** | Supply chain vulnerabilities | Package audit, CVE databases |
| **SECRETS-DETECTION** | Credential exposure | Pattern scanning, entropy analysis |
| **COMPLIANCE** | Standards compliance | Checklist mapping, gap analysis |

---

## Mode Relationships

| Mode | Depends On | Informs |
|------|------------|--------|
| SAST | None | Code patterns for COMPLIANCE |
| DEPENDENCY-AUDIT | None | Vulnerability data for COMPLIANCE |
| SECRETS-DETECTION | None | Credential hygiene for COMPLIANCE |
| COMPLIANCE | SAST, DEPENDENCY-AUDIT, SECRETS-DETECTION | Overall security posture |

---

## Failure Signal

```json
{"status": "failed" | "success", "reason": "...", "completed_portion": "...", "retry_possible": true/false}
```

| status | reason | retry_possible |
|--------|--------|----------------|
| `failed` | `sast-inconclusive` | `false` |
| `failed` | `dependency-scan-error` | `true` |
| `failed` | `secrets-found-critical` | `false` |
| `failed` | `compliance-scope-unclear` | `true` |
| `failed` | `no-evidence-collected` | `false` |
