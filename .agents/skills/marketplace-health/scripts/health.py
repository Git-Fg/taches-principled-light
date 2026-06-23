#!/usr/bin/env python3
"""Marketplace health sweep — broader pre-release audit for taches-principled-light.

Aggregates the marketplace-validator output with manifest consistency,
license coverage, cross-reference integrity, and orphan-skill checks.
Produces a single Markdown report at
`docs/principled/marketplace-health/<YYYY-MM-DD>.md` and exits 1 if any
hard-fail check failed (use --no-fail for advisory mode).

Usage:
    python scripts/health.py                                  # full sweep, default report path
    python scripts/health.py --date 2026-06-22                # custom date
    python scripts/health.py --output /tmp/health.md          # custom output
    python scripts/health.py --no-fail                       # always exit 0

The script reads the validator's --json output via subprocess and combines it
with checks specific to the marketplace-health lens.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Where the marketplace's skills/ root lives (relative to repo root).
SKILLS_ROOT = Path("skills")
# The 5 marketplace files: 1 catalog (marketplace.json) + 4 plugin manifests.
# The 4 plugin manifests must declare the same version; the catalog's top-level
# has no version (it's the catalog's metadata, not a plugin's). The catalog's
# plugins[0] does declare a version and must match the 4 plugin manifests.
MANIFESTS = [
    Path(".claude-plugin/marketplace.json"),
    Path(".claude-plugin/plugin.json"),
    Path(".codex-plugin/plugin.json"),
    Path(".cursor-plugin/plugin.json"),
    Path(".kimi-plugin/plugin.json"),
]
# Top-level docs that should reflect current state.
DOCS = ["README.md", "AGENTS.md", "CHANGELOG.md"]


def run_validator(skills_root: Path) -> dict:
    """Run the marketplace-validator on the whole marketplace and return its JSON."""
    validator = Path(".agents/skills/marketplace-validator/scripts/validate.py")
    if not validator.exists():
        return {"summary": {"fail": -1, "warn": -1}, "skills": {}, "_error": "validator not found"}
    proc = subprocess.run(
        [sys.executable, str(validator), str(skills_root), "--json"],
        capture_output=True, text=True,
    )
    if proc.returncode not in (0, 1):  # validator exits 1 on failures; that's fine
        return {"summary": {"fail": -1, "warn": -1}, "skills": {}, "_error": proc.stderr.strip()}
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        return {"summary": {"fail": -1, "warn": -1}, "skills": {}, "_error": f"validator JSON parse: {e}"}


def get_manifest_version(repo_root: Path) -> str | None:
    """Return the canonical version (the unique value across the 4 plugin manifests
    and marketplace.json's plugins[0]). Returns None if versions diverge, are missing,
    or no plugin manifest exists.
    """
    versions: set[str] = set()
    missing: list[str] = []
    for m in MANIFESTS:
        p = repo_root / m
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text())
        except json.JSONDecodeError:
            continue
        if m.name == "marketplace.json":
            # Catalog version lives in plugins[0].version, not at the top level.
            plugins = data.get("plugins", [])
            v = plugins[0].get("version") if plugins else None
        else:
            v = data.get("version")
        if v:
            versions.add(v)
        else:
            missing.append(str(m))
    # If any manifest lacks a version, the canonical version is undefined —
    # return None so downstream checks (e.g., CHANGELOG cross-check) treat
    # this as "not all manifests agree" instead of trusting a partial set.
    if missing:
        return None
    if len(versions) == 1:
        return versions.pop()
    return None


def check_manifest_consistency(repo_root: Path) -> list[dict]:
    """All 5 manifests should have the same version. Descriptions are checked
    for non-emptiness (a missing or very short description is a real bug);
    cross-platform differences in phrasing are intentional and not enforced.
    """
    findings: list[dict] = []
    versions: dict[str, str] = {}
    descriptions: dict[str, str] = {}
    missing: list[str] = []
    for m in MANIFESTS:
        p = repo_root / m
        if not p.exists():
            findings.append({"check": "manifest_consistency", "level": "fail",
                             "path": str(m), "message": "manifest missing"})
            continue
        try:
            data = json.loads(p.read_text())
        except json.JSONDecodeError as e:
            findings.append({"check": "manifest_consistency", "level": "fail",
                             "path": str(m), "message": f"JSON parse error: {e}"})
            continue
        if m.name == "marketplace.json":
            plugins = data.get("plugins", [])
            v = plugins[0].get("version", "(no version)") if plugins else "(no version)"
        else:
            v = data.get("version", "(no version)")
        if v != "(no version)":
            versions[str(m)] = v
        else:
            # Missing version is a real bug — emit a finding so it doesn't
            # silently pass when only some manifests have it.
            missing.append(str(m))
            findings.append({"check": "manifest_consistency", "level": "fail",
                             "path": str(m),
                             "message": f"{m.name} is missing the 'version' field"})
        # Description: top-level for plugin.json, in plugins[0] for marketplace.json
        d = data.get("description") or ""
        if not d and "plugins" in data and data["plugins"]:
            d = data["plugins"][0].get("description", "")
        descriptions[str(m)] = d

    if versions:
        unique = set(versions.values())
        if len(unique) > 1:
            findings.append({"check": "manifest_consistency", "level": "fail",
                             "message": f"manifest versions diverge: {versions}"})
        elif not missing:
            # Only emit the aggregate "all manifests at version X" pass when
            # every manifest provided a version. If any are missing, the
            # per-manifest fail findings above carry the signal and a pass
            # summary would contradict them.
            findings.append({"check": "manifest_consistency", "level": "pass",
                             "message": f"all manifests at version {unique.pop()}"})

    # Description sanity: missing or very short descriptions are a real bug,
    # even if cross-platform phrasing differs intentionally.
    short_or_missing = {p: d for p, d in descriptions.items() if len(d.strip()) < 80}
    if short_or_missing:
        findings.append({"check": "manifest_consistency", "level": "warn",
                         "message": f"{len(short_or_missing)} manifest(s) have short or missing descriptions",
                         "details": [{"path": p, "len": len(d.strip())} for p, d in short_or_missing.items()]})
    return findings


def check_license_coverage(skills_root: Path) -> list[dict]:
    """Each skill should declare `license:` in frontmatter."""
    findings: list[dict] = []
    missing: list[str] = []
    # Reuse the validator's parser: it handles single/double-quoted scalars,
    # block scalars, and inline comments correctly. Importing avoids drift.
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).parent.parent.parent / "marketplace-validator" / "scripts"))
    from validate import parse_frontmatter_safe  # type: ignore  # noqa: E402

    for skill_md in sorted(skills_root.rglob("SKILL.md")):
        text = skill_md.read_text()
        fm, _ = parse_frontmatter_safe(text)
        if "license" not in fm:
            missing.append(str(skill_md.parent.relative_to(skills_root.parent)))
    if missing:
        findings.append({"check": "license_coverage", "level": "warn",
                         "message": f"{len(missing)} skill(s) missing `license:` field",
                         "details": missing})
    else:
        findings.append({"check": "license_coverage", "level": "pass",
                         "message": "all skills declare a license"})
    return findings


def strip_code_blocks(text: str) -> str:
    """Same stripper as the validator: handles `>` and `|` block scalars,
    inline backticks, fenced code blocks, and the `check-citations-skip`
    HTML-comment opt-out marker.
    """
    out = re.sub(
        r"<!--\s*check-citations-skip:[^\n]*-->.*?<!--\s*end-check-citations-skip\s*-->",
        "",
        text,
        flags=re.DOTALL,
    )
    lines = out.splitlines(keepends=True)
    if lines and re.search(r"check-citations-skip", lines[0]):
        out = "".join(lines[1:])
    out = re.sub(r"```[^\n]*\n.*?```", "", out, flags=re.DOTALL)
    out = re.sub(r"`[^`]+`", lambda m: " " * (len(m.group(0))), out)
    return out


def check_cross_references(skills_root: Path) -> list[dict]:
    """Every `references/X.md` and `scripts/X.py` citation should resolve.

    Skips lines that contain inline backticks (documentation that *describes*
    reference patterns), lines inside fenced code blocks, and files that
    opt out via the `<!-- check-citations-skip: ... -->` HTML-comment
    marker (used by reference files that quote path patterns as teaching
    examples).
    """
    findings: list[dict] = []
    broken: list[dict] = []
    for md in skills_root.rglob("*.md"):
        text = md.read_text()
        # File-level opt-out: a `<!-- check-citations-skip: ... -->` comment
        # on its own line near the top exempts the whole file.
        first_lines = text.splitlines()[:3]
        if any("check-citations-skip" in l for l in first_lines):
            continue
        in_fence = False
        for line in text.splitlines():
            stripped = line.lstrip()
            if stripped.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            # Strip inline backticks rather than skipping the line entirely.
            # This catches real citations like `references/foo.md` mentioned
            # alongside backticked prose like `code` on the same line.
            line_stripped = re.sub(r"`[^`]+`", lambda mm: " " * len(mm.group(0)), line)
            for m in re.finditer(r"\b(references|scripts)/([\w./-]+\.(?:md|py|json))\b", line_stripped):
                rel = m.group(0)
                # Skip placeholder patterns (X.md, Y.py) which are
                # documentation examples, not real citations.
                if re.search(r"\bX\.md\b|\bY\.py\b", rel):
                    continue
                candidate = (md.parent / rel).resolve()
                try:
                    candidate.relative_to(skills_root.resolve())
                except ValueError:
                    continue
                if not candidate.exists():
                    broken.append({
                        "from": str(md.relative_to(skills_root.parent)),
                        "to": rel,
                    })
    if broken:
        findings.append({"check": "cross_references", "level": "fail",
                         "message": f"{len(broken)} broken reference(s)",
                         "details": broken[:10]})
    else:
        findings.append({"check": "cross_references", "level": "pass",
                         "message": "all references and scripts resolve"})
    return findings


def check_orphan_skills(skills_root: Path, repo_root: Path) -> list[dict]:
    """A skill is 'orphan' if it exists in skills/ but is not advertised in any manifest.

    Convention: most skills don't need manifest entries (they're auto-discovered
    from the directory tree). But if a skill IS named in a manifest, that's a hint
    it matters; report it. Otherwise: just count skills and report.
    """
    findings: list[dict] = []
    skill_count = sum(1 for _ in skills_root.rglob("SKILL.md"))
    # Parse marketplace.json for any per-skill entries.
    mentioned: set[str] = set()
    mp = repo_root / ".claude-plugin/marketplace.json"
    if mp.exists():
        data = json.loads(mp.read_text())
        for plugin in data.get("plugins", []):
            for k in ("skills",):
                for s in plugin.get(k, []) or []:
                    if isinstance(s, str):
                        mentioned.add(s)
    findings.append({"check": "skill_count", "level": "info",
                     "message": f"{skill_count} SKILL.md files in {skills_root}"})
    if mentioned:
        findings.append({"check": "orphan_skills", "level": "info",
                         "message": f"{len(mentioned)} skill(s) named in marketplace.json (auto-discovery covers the rest)"})
    return findings


def check_docs_reflect_state(skills_root: Path, repo_root: Path) -> list[dict]:
    """README, AGENTS.md, and CHANGELOG should reflect current state.

    Specifically: README should mention the current skill count, and the
    CHANGELOG's latest version must match the canonical manifest version.
    A version mismatch between CHANGELOG and shipped manifests is a hard fail.
    """
    findings: list[dict] = []
    actual = sum(1 for _ in skills_root.rglob("SKILL.md"))
    readme = repo_root / "README.md"
    if readme.exists():
        text = readme.read_text()
        # Prefer a `= N SKILL.md total` or `= N total` claim when present;
        # it accurately reflects the recursion count. Fall back to the first
        # `\d+ skills` (or `top-level skills`) pattern.
        preferred = re.search(r"=\s*(\d+)\s+SKILL\.md(?:\s+total)?", text)
        if not preferred:
            preferred = re.search(r"(\d+)\s+SKILL\.md\s+total", text)
        m = preferred or re.search(r"\b(\d+)\s+(?:skills|top-level skills|specialist skills)\b", text)
        if m:
            claimed = int(m.group(1))
            if claimed != actual:
                findings.append({"check": "docs_reflect_state", "level": "warn",
                                 "message": f"README says {claimed} skills, actual is {actual}"})
            else:
                findings.append({"check": "docs_reflect_state", "level": "pass",
                                 "message": f"README reflects current count ({actual})"})
    cl = repo_root / "CHANGELOG.md"
    if cl.exists():
        text = cl.read_text()
        # Match both bracketed `## [X.Y.Z]` and unbracketed `## X.Y.Z` headers.
        cl_versions = re.findall(r"##\s*\[?(\d+\.\d+\.\d+)\]?", text)
        if cl_versions:
            cl_latest = cl_versions[0]
            manifest_version = get_manifest_version(repo_root)
            if manifest_version is None:
                findings.append({"check": "docs_reflect_state", "level": "fail",
                                 "message": f"manifests disagree on version (cannot cross-check CHANGELOG {cl_latest})"})
            elif cl_latest != manifest_version:
                findings.append({"check": "docs_reflect_state", "level": "fail",
                                 "message": f"CHANGELOG latest is {cl_latest} but manifests are at {manifest_version}"})
            else:
                findings.append({"check": "docs_reflect_state", "level": "pass",
                                 "message": f"CHANGELOG latest ({cl_latest}) matches manifest version"})
    return findings


def render_report(date: str, validator_out: dict, all_findings: list[dict]) -> str:
    val_summary = validator_out.get("summary", {})
    val_skills = validator_out.get("skills", {})
    n_skills = len(val_skills)
    n_fail = val_summary.get("fail", 0)
    n_warn = val_summary.get("warn", 0)

    md = []
    md.append(f"# Marketplace Health Report — {date}\n")
    md.append(f"_Generated by `.agents/skills/marketplace-health/scripts/health.py`._\n\n")

    md.append("## Summary\n\n")
    md.append("| Check | Result |\n|---|---|\n")
    md.append(f"| Validator | {n_fail} failures, {n_warn} warnings across {n_skills} skills |\n")
    for f in all_findings:
        marker = {"pass": "✓", "fail": "✗", "warn": "⚠️ ", "info": "ℹ️ "}.get(f.get("level", "info"), "?")
        md.append(f"| {f.get('check', '?').replace('_', ' ').title()} | {marker} {f.get('message', '')} |\n")
    md.append("\n")

    md.append("## Validator findings (aggregated)\n\n")
    if n_fail == 0 and n_warn == 0:
        md.append("No issues.\n\n")
    else:
        # Group by skill.
        per_skill_warns: dict[str, list[str]] = {}
        for sd, findings in sorted(val_skills.items()):
            skill_name = Path(sd).name
            for f in findings:
                per_skill_warns.setdefault(skill_name, []).append(
                    f"[{f['code']}] {f['message']}"
                )
        for skill_name, warns in sorted(per_skill_warns.items()):
            md.append(f"### {skill_name}\n\n")
            for w in warns[:5]:  # cap per skill to keep report readable
                md.append(f"- {w}\n")
            if len(warns) > 5:
                md.append(f"- … and {len(warns) - 5} more\n")
            md.append("\n")

    md.append("## Detail\n\n")
    for f in all_findings:
        if "details" in f and f["details"]:
            md.append(f"### {f.get('check', '?').replace('_', ' ').title()} — {f.get('message', '')}\n\n")
            if isinstance(f["details"], list) and f["details"] and isinstance(f["details"][0], dict):
                for d in f["details"]:
                    md.append(f"- `{d.get('from', '?')}` → `{d.get('to', '?')}`\n")
            else:
                for d in f["details"]:
                    md.append(f"- `{d}`\n")
            md.append("\n")

    md.append("\n## Next actions\n\n")
    if n_fail > 0:
        md.append(f"- Fix the {n_fail} validator failure(s) listed above before any release cut.\n")
    if any(f.get("level") == "fail" and f.get("check") != "validator" for f in all_findings):
        md.append("- Resolve the cross-reference / manifest / doc-state failures.\n")
    if n_warn > 0 and not any(f.get("level") == "fail" for f in all_findings):
        md.append(f"- Warnings are advisory; address at leisure. {n_warn} total.\n")
    if not any(f.get("level") == "fail" for f in all_findings) and n_fail == 0:
        md.append("- No blocking issues. Safe to cut a release.\n")
    return "".join(md)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skills-root", type=Path, default=SKILLS_ROOT, help="path to the skills/ directory")
    ap.add_argument("--repo-root", type=Path, default=Path("."), help="path to the repo root")
    ap.add_argument("--date", default=None, help="report date (default: today, YYYY-MM-DD)")
    ap.add_argument("--output", type=Path, default=None, help="output path (default: docs/principled/marketplace-health/<date>.md)")
    ap.add_argument("--no-fail", action="store_true", help="always exit 0 (advisory mode)")
    args = ap.parse_args()

    from datetime import datetime, timezone
    date = args.date or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # 1. Validator
    validator_out = run_validator(args.skills_root)

    # 2. Manifest consistency
    manifest_findings = check_manifest_consistency(args.repo_root)

    # 3. License coverage
    license_findings = check_license_coverage(args.skills_root)

    # 4. Cross-reference integrity
    xref_findings = check_cross_references(args.skills_root)

    # 5. Orphan skills
    orphan_findings = check_orphan_skills(args.skills_root, args.repo_root)

    # 6. Docs reflect state
    docs_findings = check_docs_reflect_state(args.skills_root, args.repo_root)

    all_findings = manifest_findings + license_findings + xref_findings + orphan_findings + docs_findings
    report = render_report(date, validator_out, all_findings)

    out_path = args.output or (args.repo_root / "docs" / "principled" / "marketplace-health" / f"{date}.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report)
    print(f"Wrote {out_path}")
    # Print a one-line summary to stdout for CI.
    n_val_fail = validator_out.get("summary", {}).get("fail", 0)
    n_other_fail = sum(1 for f in all_findings if f.get("level") == "fail")
    total_fail = (n_val_fail if n_val_fail >= 0 else 0) + n_other_fail
    if total_fail == 0:
        print(f"HEALTH: pass (validator={n_val_fail}/{validator_out.get('summary', {}).get('warn', 0)})")
    else:
        print(f"HEALTH: {total_fail} hard failure(s) — see {out_path}")
    if total_fail > 0 and not args.no_fail:
        sys.exit(1)


if __name__ == "__main__":
    main()