#!/usr/bin/env python3
"""Pre-commit safety floor for risky-string scrub.

Implements the verification gate from
``docs/principled/specs/2026-06-23-eval-cleanup-design.md`` (L145-162, Approach B).

Runs on staged text files. Exits 1 if any risky pattern is found in the
active tree (excluding META-documentation paths, which may legitimately
describe the cleanup).

Patterns are restricted to high-signal/low-noise identifiers (specific
model IDs, error formats, private IPs). The spec's broad vendor list
(``qwen|llama|gpt-4o|...``) is intentionally NOT used here because those
names collide with legitimate tool/platform references in this repo
(Kimi Code, Claude Code, etc.). The full scrub table lives in the spec;
this hook enforces the patterns that have no legitimate non-eval use.

META-doc paths (allowed to contain risky strings):
- ``docs/principled/attic/`` (immutable closure archives)
- ``docs/principled/specs/`` (design docs that may quote scrubbed strings)
- ``docs/superpowers/plans/`` (working plans that may reference redacted data)
- ``scripts/`` (the gatekeeper itself and its data files)

Bypass with ``git commit --no-verify`` (not recommended; the safety floor
exists for a reason).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# (regex, human label). Only high-signal/low-noise patterns.
# Broader vendor-name sweeps live in the spec, not here.
# Patterns are matched case-sensitively to avoid false positives on prose like
# "We use a Haiku solver in production" or "z.ai offers...". Vendor identifiers
# are case-specific in the spec.
PATTERNS: tuple[tuple[str, str], ...] = (
    (r"100\.80\.231\.128(?::\d+)?", "private Tailscale inference IP"),
    (r"\bMiniMax-M\d+\b", "vendor model alias"),
    (r"claude-haiku-4-5-20251001", "solver tier alias"),
    (r"circuit_breaker_open: RateLimit", "rate-limit error format"),
    (r"\bnex-agi/nex-n2-pro:free\b", "vendor alias (nex-agi/nex-n2-pro:free)"),
    (r"\bhaiku solver\b", "solver tier alias"),
    (r"\bZ\.AI\b", "external judge vendor"),
)

# Paths where risky strings are allowed.
# - attic/ specs/ plans/: META-documentation describing the cleanup
# - scripts/: the gatekeeper itself contains patterns as data
META_PREFIXES: tuple[str, ...] = (
    "docs/principled/attic/",
    "docs/principled/specs/",
    "docs/superpowers/plans/",
    "scripts/",
)


def is_meta(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in META_PREFIXES)


def scan(path: str) -> list[tuple[int, str, str]]:
    p = Path(path)
    if not p.is_file():
        return []
    try:
        content = p.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    hits: list[tuple[int, str, str]] = []
    for pattern, label in PATTERNS:
        for m in re.finditer(pattern, content):
            line_no = content.count("\n", 0, m.start()) + 1
            hits.append((line_no, label, m.group(0)))
    return hits


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: check-risky-strings.py <file> [<file> ...]", file=sys.stderr)
        return 2

    all_hits: list[tuple[str, int, str, str]] = []
    for path in sys.argv[1:]:
        if is_meta(path):
            continue
        for line_no, label, match in scan(path):
            all_hits.append((path, line_no, label, match))

    if not all_hits:
        return 0

    print(
        "Risky-string safety floor FAILED "
        "(spec: docs/principled/specs/2026-06-23-eval-cleanup-design.md L145-162):",
        file=sys.stderr,
    )
    for path, line_no, label, match in all_hits:
        print(f"  {path}:{line_no}  [{label}]  -> {match!r}", file=sys.stderr)
    n_files = len({h[0] for h in all_hits})
    print(
        f"\n{len(all_hits)} risky-string match(es) across {n_files} file(s).",
        file=sys.stderr,
    )
    print(
        "Move content to docs/principled/attic/, docs/principled/specs/, "
        "docs/superpowers/plans/, or scripts/ if it's META-documentation. "
        "Otherwise, scrub the string per the spec. "
        "Bypass with `git commit --no-verify`.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
