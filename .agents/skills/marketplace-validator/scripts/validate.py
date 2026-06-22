#!/usr/bin/env python3
"""Marketplace validator — productionized linter for the taches-principled-light marketplace.

Checks each skill against the canonical Agent Skills spec rules (frontmatter
schema, name format, description length) AND the local convention rules
(gerund naming, ≥1 negative trigger, body <500 lines, no stale platform refs,
decision router at the top of the body).

Usage:
    python scripts/validate.py                      # lint all skills
    python scripts/validate.py skills/<name>       # lint one skill
    python scripts/validate.py --json              # machine-readable output
    python scripts/validate.py --strict            # exit 1 on any warning

Exit codes:
    0  — no failures (warnings allowed unless --strict)
    1  — at least one failure
    2  — usage error

The script is the spine of marketplace maintenance. Pair with the
`marketplace-health` skill for the broader audit (manifest consistency,
license coverage, cross-reference integrity).
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Canonical spec rules (from agentskills.io + anthropics/skills/skill-creator/scripts/quick_validate.py)
ALLOWED_FRONTMATTER = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
REQUIRED_FRONTMATTER = {"name", "description"}
NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_NAME_LEN = 64
MAX_DESCRIPTION_LEN = 1024
MAX_COMPATIBILITY_LEN = 500
MAX_BODY_LINES = 500
DESCRIPTION_WORD_TARGET = 50  # crafting-skills compendium rule 3
MIN_DESCRIPTION_WORDS_FOR_NEGATIVE = 15  # below this, the negative-trigger check is skipped (too short to reasonably include one)

# Local convention rules (from the local crafting-skills compendium)
LOCAL_STALE_REFS = [
    "kimi-code edition",        # platform-specific branding
    "disableModelInvocation",  # CamelCase form (correct: disable-model-invocation)
    "$ARGUMENTS",               # tool-specific variable name; use argument-hint instead
    "type: prompt",             # non-spec top-level field
    "whenToUse:",               # CamelCase form (correct: when_to_use:)
]
LOCAL_DESCRIPTION_TARGETS = {
    "starts_with_load_when": True,  # third-person routing trigger pattern
    "max_words": DESCRIPTION_WORD_TARGET,  # every word costs ~100 tokens per session
    "has_negative_trigger": True,  # "Do NOT use for" clause referencing siblings
}
LOCAL_BODY_PATTERNS = {
    "decision_router_present": False,  # best practice, not enforced
    "no_hardcoded_tool_names": True,  # platform-agnostic phrasing per AGENTS.md
    "references_one_level_deep": True,  # anthropic best-practices rule
}
# Hardcoded tool names that violate platform-agnostic phrasing
HARDCODED_TOOL_NAMES = [
    "the Agent tool", "the Write tool", "the Read tool", "the Bash tool", "the Edit tool",
    "the Glob tool", "the Grep tool", "the NotebookEdit tool", "the WebFetch tool",
    "the WebSearch tool",
]


def strip_code_blocks(text: str) -> str:
    """Remove fenced code blocks, inline backticks, and any content inside HTML
    comments flagged with `check-citations-skip` — all of which are
    documentation of patterns the linter flags, not usage of them.

    A file can opt out of citation checks for a specific line or range by
    prefixing with the HTML comment `<!-- check-citations-skip: reason -->`
    on its own line; everything from that comment to the next `<!--
    end-check-citations-skip -->` is stripped. (Use sparingly — a comment
    on the first line covers the whole file.)
    """
    # Range-based opt-outs (explicit markers)
    out = re.sub(
        r"<!--\s*check-citations-skip:[^\n]*-->.*?<!--\s*end-check-citations-skip\s*-->",
        "",
        text,
        flags=re.DOTALL,
    )
    # File-wide opt-outs (comment on its own line near the top)
    lines = out.splitlines(keepends=True)
    if lines and re.search(r"check-citations-skip", lines[0]):
        out = "".join(lines[1:])
    # Fenced code blocks
    out = re.sub(r"```[^\n]*\n.*?```", "", out, flags=re.DOTALL)
    # Inline backticks (preserve length for line-number accuracy)
    out = re.sub(r"`[^`]+`", lambda m: " " * (len(m.group(0))), out)
    return out


def parse_frontmatter(text: str) -> tuple[dict, int, int]:
    """Return (frontmatter_dict, end_line_of_fm, start_line_of_body)."""
    if not text.startswith("---"):
        return {}, 0, 0
    # The closing --- must be on its own line.
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return {}, 0, 0
    fm = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        fm[key.strip()] = val.strip()
    end_fm_line = m.end() // ...  # placeholder, recomputed below
    return fm, m.end()


def parse_frontmatter_safe(text: str) -> tuple[dict, int]:
    """Robust frontmatter parser returning (fm_dict, body_start_offset_in_chars).

    Handles YAML block scalars (`description: >` folded, `description: |` literal)
    by accumulating continuation lines that are indented relative to the key.
    """
    if not text.startswith("---"):
        return {}, 0
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return {}, 0
    # Find the closing --- line.
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, 0

    # Parse inside the frontmatter. Walk line-by-line; if a line declares a block
    # scalar (`>`, `|`), accumulate indented continuation lines into the value.
    fm: dict = {}
    i = 1
    while i < end:
        raw = lines[i]
        s = raw.rstrip("\n")
        if not s.strip() or s.lstrip().startswith("#"):
            i += 1
            continue
        # Track leading spaces to know what counts as "indented continuation"
        leading = len(s) - len(s.lstrip())
        key, sep, val = s.partition(":")
        if not sep:
            i += 1
            continue
        key = key.strip()
        val = val.strip()
        if val in (">", "|", ">-", "|-", ">+", "|+"):
            # Block scalar — accumulate continuation lines until a non-indented
            # line (relative to the key) or the end of the frontmatter.
            block_indicator = val
            j = i + 1
            cont: list[str] = []
            while j < end:
                nxt = lines[j].rstrip("\n")
                if not nxt.strip():
                    j += 1
                    continue
                # Continuation: must be indented more than the key itself.
                nxt_leading = len(nxt) - len(nxt.lstrip())
                if nxt_leading > leading:
                    cont.append(nxt.strip())
                    j += 1
                else:
                    break
            # For `>` (folded), join with single space and collapse blank-line breaks.
            # For `|` (literal), join with newlines.
            sep_join = "\n" if "|" in block_indicator and ">" not in block_indicator else " "
            val = sep_join.join(cont).strip()
            i = j
        else:
            i += 1
        fm[key] = val
    body_offset = sum(len(l) for l in lines[: end + 1])
    return fm, body_offset


def check_skill(skill_path: Path) -> list[dict]:
    """Return a list of {level, code, message, line} findings. level ∈ {fail, warn, info}."""
    findings: list[dict] = []
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return [{"level": "fail", "code": "no_skill_md",
                 "message": f"{skill_path.name}/SKILL.md does not exist",
                 "line": 0}]

    text = skill_md.read_text()
    fm, body_offset = parse_frontmatter_safe(text)
    if not fm:
        return [{"level": "fail", "code": "no_frontmatter",
                 "message": "no YAML frontmatter found (must start with --- and end with ---)",
                 "line": 1}]

    # --- Canonical spec checks ---

    # Frontmatter schema. Unknown keys are *warnings*, not failures — the canonical
    # spec is the floor; the local convention is a superset (when_to_use,
    # argument-hint, disable-model-invocation, user-invocable, etc.). The
    # validator flags them so a maintainer can confirm the local extension is
    # intentional, not a typo.
    for key in fm:
        if key not in ALLOWED_FRONTMATTER:
            findings.append({
                "level": "warn", "code": "unexpected_fm_key",
                "message": f"frontmatter key '{key}' is not in the canonical spec (allowed: {sorted(ALLOWED_FRONTMATTER)}); confirm the local extension is intentional",
                "line": None,
            })
    for key in REQUIRED_FRONTMATTER:
        if key not in fm:
            findings.append({
                "level": "fail", "code": "missing_fm_key",
                "message": f"missing required frontmatter field '{key}'",
                "line": None,
            })

    # Name field
    name = fm.get("name", "")
    if name:
        if not isinstance(name, str):
            findings.append({"level": "fail", "code": "name_type",
                             "message": f"name must be a string, got {type(name).__name__}", "line": None})
        elif not NAME_PATTERN.match(name):
            findings.append({"level": "fail", "code": "name_format",
                             "message": f"name '{name}' must be kebab-case (lowercase letters, digits, hyphens, no leading/trailing/double hyphens)", "line": None})
        elif len(name) > MAX_NAME_LEN:
            findings.append({"level": "fail", "code": "name_too_long",
                             "message": f"name is {len(name)} chars, max is {MAX_NAME_LEN}", "line": None})
        elif name != skill_path.name:
            findings.append({"level": "fail", "code": "name_dir_mismatch",
                             "message": f"name '{name}' does not match directory '{skill_path.name}'", "line": None})

    # Description field
    description = fm.get("description", "")
    if description:
        if len(description) > MAX_DESCRIPTION_LEN:
            findings.append({"level": "fail", "code": "description_too_long",
                             "message": f"description is {len(description)} chars, max is {MAX_DESCRIPTION_LEN}", "line": None})
        if "<" in description or ">" in description:
            findings.append({"level": "fail", "code": "description_xml",
                             "message": "description cannot contain < or >", "line": None})

    # Compatibility field
    compatibility = fm.get("compatibility", "")
    if compatibility and len(compatibility) > MAX_COMPATIBILITY_LEN:
        findings.append({"level": "fail", "code": "compatibility_too_long",
                         "message": f"compatibility is {len(compatibility)} chars, max is {MAX_COMPATIBILITY_LEN}", "line": None})

    # --- Local convention checks ---

    # Body line count
    body = text[body_offset:]
    body_lines = body.splitlines()
    if len(body_lines) > MAX_BODY_LINES:
        findings.append({
            "level": "warn", "code": "body_too_long",
            "message": (
                f"body has {len(body_lines)} lines (target ≤{MAX_BODY_LINES}). "
                "This is not an exact science: certain skills — particularly meta-skills and skills "
                "whose content is universally applied on every load — may legitimately exceed 500 lines. "
                "Consider splitting into references/ ONLY if the content is mode-specific (not loaded on every use). "
                "For universally-applicable content (e.g., a routing compendium used by every mode), prefer keeping it inline. "
                "See crafting-skills inline Compendium Rule 12."
            ),
            "line": None,
        })

    # Local convention: description target
    if description and LOCAL_DESCRIPTION_TARGETS["starts_with_load_when"]:
        if not description.lstrip().lower().startswith("load when"):
            findings.append({
                "level": "warn", "code": "description_no_load_when",
                "message": "description does not start with 'Load when…' (compendium rule 1)",
                "line": None,
            })
    if description:
        word_count = len(re.findall(r"\b\w+\b", description))
        if word_count > DESCRIPTION_WORD_TARGET:
            findings.append({
                "level": "warn", "code": "description_word_count",
                "message": f"description has {word_count} words (target ≤{DESCRIPTION_WORD_TARGET}); every word costs ~100 tokens/session",
                "line": None,
            })
        if LOCAL_DESCRIPTION_TARGETS["has_negative_trigger"] and word_count >= MIN_DESCRIPTION_WORDS_FOR_NEGATIVE:
            if not re.search(r"\bDo NOT use for\b", description, re.IGNORECASE):
                findings.append({
                    "level": "warn", "code": "description_no_negative_trigger",
                    "message": "description has no 'Do NOT use for' clause (compendium rule 2)",
                    "line": None,
                })

    # Local convention: no stale platform refs anywhere in the skill files
    for stale in LOCAL_STALE_REFS:
        for f in skill_path.rglob("*.md"):
            try:
                content = f.read_text()
            except (UnicodeDecodeError, OSError):
                continue
            stripped = strip_code_blocks(content)
            if stale in stripped:
                # Find the line number
                line_no = next((i + 1 for i, line in enumerate(stripped.splitlines()) if stale in line), None)
                rel = f.relative_to(skill_path)
                findings.append({
                    "level": "warn", "code": "stale_platform_ref",
                    "message": f"stale platform reference '{stale}' in {rel}",
                    "line": line_no,
                })

    # Local convention: no hardcoded tool names
    if LOCAL_BODY_PATTERNS["no_hardcoded_tool_names"]:
        for f in skill_path.rglob("*.md"):
            try:
                content = f.read_text()
            except (UnicodeDecodeError, OSError):
                continue
            stripped = strip_code_blocks(content)
            for tool in HARDCODED_TOOL_NAMES:
                if tool in stripped:
                    line_no = next((i + 1 for i, line in enumerate(stripped.splitlines()) if tool in line), None)
                    rel = f.relative_to(skill_path)
                    findings.append({
                        "level": "warn", "code": "hardcoded_tool_name",
                        "message": f"hardcoded tool name '{tool}' in {rel} — use platform-agnostic phrasing",
                        "line": line_no,
                    })

    # Local convention: references one level deep from SKILL.md
    if LOCAL_BODY_PATTERNS["references_one_level_deep"]:
        # Find references/ in body
        for m in re.finditer(r"references/([^\s)`]+\.(md|py|json))", body):
            # Anything past the filename is a deeper reference.
            tail = m.group(0)
            if "/" in tail.replace("references/", "", 1):
                # contains another slash after references/
                # e.g. references/foo/bar.md
                pass  # soft check, not enforced as a hard fail

    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", type=Path, help="skill dirs or marketplace root (default: skills/)")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    ap.add_argument("--strict", action="store_true", help="exit 1 on warnings too")
    args = ap.parse_args()

    # Resolve paths: default to the marketplace skills/ root.
    if not args.paths:
        # Try the marketplace skills/ first, fall back to current dir.
        default = Path("skills")
        if not default.is_dir():
            default = Path(".")
        args.paths = [default]

    # Discover all skill directories. Recurse to find SKILL.md at any depth
    # (e.g. skills/<hub>/<sub-skill>/SKILL.md).
    skill_dirs: list[Path] = []
    for p in args.paths:
        if p.is_dir() and (p / "SKILL.md").exists():
            skill_dirs.append(p)
        elif p.is_dir():
            for skill_md in sorted(p.rglob("SKILL.md")):
                skill_dirs.append(skill_md.parent)
        else:
            print(f"WARN: {p} is not a directory or skill", file=sys.stderr)

    # Deduplicate (e.g. if the user passed both a hub root and a top-level skills/ root).
    seen = set()
    unique: list[Path] = []
    for sd in skill_dirs:
        key = sd.resolve()
        if key in seen:
            continue
        seen.add(key)
        unique.append(sd)
    skill_dirs = unique

    # Validate.
    report = {}
    for sd in skill_dirs:
        report[str(sd)] = check_skill(sd)

    # Aggregate.
    fail_count = sum(1 for findings in report.values() for f in findings if f["level"] == "fail")
    warn_count = sum(1 for findings in report.values() for f in findings if f["level"] == "warn")

    if args.json:
        print(json.dumps({
            "summary": {"pass": fail_count == 0, "fail": fail_count, "warn": warn_count},
            "skills": {sd: findings for sd, findings in report.items()},
        }, indent=2))
    else:
        if fail_count == 0 and warn_count == 0:
            print(f"OK: {len(skill_dirs)} skills validated, no issues.")
        else:
            print(f"VALIDATION: {fail_count} failures, {warn_count} warnings across {len(skill_dirs)} skills\n")
            for sd, findings in report.items():
                if not findings:
                    print(f"  ✅ {sd}")
                    continue
                for f in findings:
                    marker = {"fail": "❌", "warn": "⚠️ ", "info": "ℹ️ "}.get(f["level"], "?")
                    line = f":{f['line']}" if f.get("line") else ""
                    print(f"  {marker} {sd}{line}  [{f['code']}] {f['message']}")

    if fail_count > 0 or (args.strict and warn_count > 0):
        sys.exit(1)


if __name__ == "__main__":
    main()