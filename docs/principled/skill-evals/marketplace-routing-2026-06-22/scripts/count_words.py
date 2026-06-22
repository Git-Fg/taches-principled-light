#!/usr/bin/env python3
r"""Word-count methodology comparison for skill descriptions.

Reads the three "exception" skill descriptions and counts their words
under three different methodologies:

  - validator:  re.findall(r"\b\w+\b", desc)        — what marketplace-validator uses
  - routing:    re.split(r"\W+", desc.lower()) with len > 2 filter
                                                      — what routing_test.py uses
  - split:      desc.split()                        — naive whitespace split

Prints a markdown table suitable for inclusion in the methodology note.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path("/Users/felix/Documents/AutoPluginClaw/taches-principled-light")
TARGETS = [
    ("crafting-skills",        REPO / "skills" / "crafting-skills" / "SKILL.md"),
    ("test-orchestration",     REPO / "skills" / "test-orchestration" / "SKILL.md"),
    ("marketplace-validator",  REPO / ".agents" / "skills" / "marketplace-validator" / "SKILL.md"),
]


def parse_frontmatter_description(text: str) -> str:
    """Extract the `description:` value from a SKILL.md's YAML frontmatter.

    Handles single-line `"…"` quoted and multi-line `>` folded scalars.
    """
    if not text.startswith("---"):
        return ""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return ""
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return ""
    i = 1
    while i < end:
        s = lines[i]
        if not s.strip() or s.lstrip().startswith("#"):
            i += 1
            continue
        leading = len(s) - len(s.lstrip())
        key, sep, val = s.partition(":")
        if not sep:
            i += 1
            continue
        key = key.strip()
        if key != "description":
            i += 1
            continue
        val = val.strip()
        if val.startswith('"') and val.endswith('"') and len(val) >= 2:
            inner = val[1:-1]
            inner = inner.replace("\\\\", "\x00")
            inner = (
                inner.replace('\\"', '"')
                .replace("\\n", "\n")
                .replace("\\t", "\t")
                .replace("\\r", "\r")
                .replace("\\/", "/")
            )
            return inner.replace("\x00", "\\")
        if val in (">", "|", ">-", "|-", ">+", "|+"):
            block_indent = None
            chunks = []
            j = i + 1
            while j < end:
                row = lines[j]
                if not row.strip():
                    j += 1
                    continue
                row_lead = len(row) - len(row.lstrip())
                if block_indent is None:
                    block_indent = row_lead
                if row_lead < block_indent:
                    break
                chunks.append(row.lstrip() if val.startswith(">") else row[block_indent:])
                j += 1
            sep = " " if val.startswith(">") else "\n"
            return sep.join(chunks).strip()
        return val
    return ""


def main() -> int:
    rows = []
    for name, path in TARGETS:
        text = path.read_text()
        desc = parse_frontmatter_description(text)
        if not desc:
            print(f"[warn] no description found in {path}", file=sys.stderr)
            continue
        v = len(re.findall(r"\b\w+\b", desc))
        r = len({t for t in re.split(r"\W+", desc.lower()) if len(t) > 2})
        s = len(desc.split())
        rows.append((name, v, r, s))
    print(f"\nWord-count methodology comparison (current HEAD = 0.0.2 + eeaca8b refactor)\n")
    print(f"| {'Skill':24} | {'validator':>9} | {'routing':>7} | {'split':>5} |")
    print(f"|{'-'*26}|{'-'*11}|{'-'*9}|{'-'*7}|")
    for name, v, r, s in rows:
        print(f"| {name:24} | {v:>9} | {r:>7} | {s:>5} |")
    print()
    print("validator = re.findall(r'\\b\\w+\\b', desc)  (marketplace-validator)")
    print("routing   = re.split(r'\\W+', desc.lower()) with len > 2  (routing_test.py)")
    print("split     = desc.split()  (naive whitespace)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
