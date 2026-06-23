#!/usr/bin/env python3
"""Inventory a source skill for ingestion.

Given a path to a source skill (local directory or a path under a
cloned repo), produce a structured inventory of what needs to change
to conform to the local marketplace convention. The output is JSON
suitable for driving the rest of the ingesting-skills workflow.

Usage:
    python scripts/inventory_source.py <source-skill-dir>
    python scripts/inventory_source.py ~/.agents/skills/<name>
    python scripts/inventory_source.py <cloned-repo>/skills/<name>

The inventory answers: what frontmatter fields are present, which are
non-spec, whether the name conforms, description word count, body line
count, hardcoded tool names, stale platform refs, files in scripts/ and
references/. The maintainer uses this to decide per-file: keep, port,
or drop.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Reuse the marketplace-validator's parser and code-block stripper — they handle
# folded (`>`), literal (`|`), single-quoted (`'…'`), and double-quoted (`"…"`)
# scalars correctly. The previous in-file copy of parse_frontmatter_safe lacked
# single/double-quote handling, so a description like `description: "Load when…"`
# returned a 49-char string (with the quotes) instead of 47, breaking the
# `starts_load_when` check.
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "marketplace-validator" / "scripts"))
from validate import parse_frontmatter_safe, strip_code_blocks  # noqa: E402

ALLOWED_FRONTMATTER = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_NAME_LEN = 64
MAX_DESCRIPTION_LEN = 1024
MAX_BODY_LINES = 500
DESCRIPTION_WORD_TARGET = 50

STALE_REFS = [
    "kimi-code edition",
    "disableModelInvocation",
    "$ARGUMENTS",
    "type: prompt",
    "whenToUse:",
]
HARDCODED_TOOL_NAMES = [
    "the Agent tool", "the Write tool", "the Read tool", "the Bash tool", "the Edit tool",
    "the Glob tool", "the Grep tool", "the NotebookEdit tool", "the WebFetch tool",
    "the WebSearch tool",
]


def inventory(source_dir: Path) -> dict:
    """Return a structured inventory of the source skill."""
    inv = {"source": str(source_dir), "skill_md_present": False, "files": []}
    skill_md = source_dir / "SKILL.md"
    if not skill_md.exists():
        return inv

    inv["skill_md_present"] = True
    text = skill_md.read_text()
    fm, body_offset = parse_frontmatter_safe(text)
    body = text[body_offset:]
    body_stripped = strip_code_blocks(body)

    # Frontmatter
    inv["frontmatter"] = {
        "all_keys": sorted(fm.keys()),
        "spec_keys": sorted(set(fm.keys()) & ALLOWED_FRONTMATTER),
        "non_spec_keys": sorted(set(fm.keys()) - ALLOWED_FRONTMATTER),
        "missing_required": sorted({"name", "description"} - set(fm.keys())),
    }
    # Name
    name = fm.get("name", "")
    if name:
        inv["name"] = {
            "value": name,
            "kebab_case": bool(NAME_PATTERN.match(name)),
            "length_ok": len(name) <= MAX_NAME_LEN,
            "matches_dir": name == source_dir.name,
        }
    # Description
    description = fm.get("description", "")
    if description:
        inv["description"] = {
            "length": len(description),
            "length_ok": len(description) <= MAX_DESCRIPTION_LEN,
            "word_count": len(re.findall(r"\b\w+\b", description)),
            "word_count_ok": len(re.findall(r"\b\w+\b", description)) <= DESCRIPTION_WORD_TARGET,
            "starts_load_when": description.lstrip().lower().startswith("load when"),
            "has_negative_trigger": bool(re.search(r"\bDo NOT use for\b", description, re.IGNORECASE)),
        }
    # Body
    inv["body_lines"] = sum(1 for _ in body.splitlines())
    inv["body_under_cap"] = inv["body_lines"] <= MAX_BODY_LINES
    # Stale platform refs in body (after code-block strip)
    inv["stale_platform_refs"] = sorted({
        s for s in STALE_REFS if s in body_stripped
    })
    # Hardcoded tool names in body
    inv["hardcoded_tool_names"] = sorted({
        t for t in HARDCODED_TOOL_NAMES if t in body_stripped
    })

    # File inventory: SKILL.md + scripts/ + references/ + assets/
    file_list: list[dict] = []
    for f in sorted(source_dir.rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(source_dir)
        try:
            size = f.stat().st_size
        except OSError:
            size = 0
        kind = "skill_md" if rel.name == "SKILL.md" else "other"
        if "scripts" in rel.parts:
            kind = "script"
        elif "references" in rel.parts:
            kind = "reference"
        elif "assets" in rel.parts:
            kind = "asset"
        file_list.append({"path": str(rel), "size_bytes": size, "kind": kind})
    inv["files"] = file_list
    inv["counts"] = {
        "total_files": len(file_list),
        "scripts": sum(1 for f in file_list if f["kind"] == "script"),
        "references": sum(1 for f in file_list if f["kind"] == "reference"),
        "assets": sum(1 for f in file_list if f["kind"] == "asset"),
    }
    return inv


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", type=Path, help="path to the source skill directory")
    args = ap.parse_args()

    if not args.source.is_dir():
        print(f"ERROR: {args.source} is not a directory", file=sys.stderr)
        sys.exit(1)
    inv = inventory(args.source)
    print(json.dumps(inv, indent=2))


if __name__ == "__main__":
    main()