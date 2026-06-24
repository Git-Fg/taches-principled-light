#!/usr/bin/env python3
"""Pre-commit gate for stale skill-budget fragments in the active tree.

The five-round independent subagent self-critic arc (commits 9927e3e,
5e26e36, a39e334) repeatedly caught the same class of error: a claim
about Claude Code's `skillListingBudgetFraction` was corrected in the
parent doc (AGENTS.md) but a downstream reference still carried the
prior framing. This hook enforces a minimal set of high-signal patterns
that have no legitimate use in the active tree outside META paths.

Patterns are matched case-sensitively. The hook runs on staged text
files and exits 1 if any pattern matches outside META-prefix paths.

META-doc paths (allowed to contain stale fragments):
- ``docs/principled/attic/`` (immutable closure archives)
- ``docs/principled/specs/`` (design docs that may quote prior framings)
- ``docs/superpowers/plans/`` (working plans that may reference old states)
- ``scripts/`` (the gatekeeper itself and its data files)
- ``research/`` (research notes that document the prior framing as part
  of correction-history sections; intentional historical references)
- ``CHANGELOG.md`` (historical entry text quotes prior claims)

Bypass with ``git commit --no-verify`` (not recommended; the safety
floor exists because the same-class-of-error pattern has cost us 5
rounds of critic fixes already).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# (regex, human label). Only high-signal/low-noise patterns.
# Each pattern corresponds to a stale framing the 5-round critic arc
# caught at least once. Patterns are restricted to phrasing that has no
# legitimate non-meta use after the corrections.
PATTERNS: tuple[tuple[str, str], ...] = (
    # Inverted direction: the default lowered from implicit 2% to
    # explicit 1%, not raised. Phrasing "raised from 1% to 2%" only
    # exists in intentional correction-history contexts (research notes
    # / CHANGELOG), which are in META prefixes.
    (
        r"\bdefault raised from 1% to 2%\b",
        "inverted-direction claim (default rose 1% to 2%; actual: lowered 2% to 1%)",
    ),
    # The original (now-superseded) Codex claim before the d18aef4 fix.
    (
        r"\bno exclude config\b",
        "stale Codex claim (Codex does have [[skills.config]] enabled=false)",
    ),
    # Truncation was silent AT v2.1.159 (bug #64606), not pre-v2.1.159.
    # The phrasing "silent pre-v2.1.159" is the wrong-direction version
    # that the 5th-critic pass caught in context-management.md.
    (
        r"\bsilent pre-v2\.1\.159\b",
        "wrong-direction silent-truncation version reference (silent AT v2.1.159, not pre-)",
    ),
    # Old Codex budget claim from openai/codex#24299 against v0.133.0:
    # "5,440 chars hard budget" was a model-specific calc, not the spec.
    (
        r"\b5,440 chars\b",
        "stale Codex budget (Codex spec is 8,000 chars fallback or 2% context)",
    ),
)

# Paths where stale fragments are allowed.
# - attic/ specs/ plans/: META-documentation describing the cleanup
# - scripts/: the gatekeeper itself contains patterns as data
# - research/: research notes that document prior framing in
#   correction-history sections (intentional historical references)
# - CHANGELOG.md: historical entries that quote prior claims
META_FILES: tuple[str, ...] = (
    "CHANGELOG.md",
)

META_PREFIXES: tuple[str, ...] = (
    "docs/principled/attic/",
    "docs/principled/specs/",
    "docs/superpowers/plans/",
    "scripts/",
    "research/",
    "docs/principled/marketplace-health/",  # verification reports quote prior framings
)


def is_meta(path: str) -> bool:
    if path in META_FILES:
        return True
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
        print("usage: check-stale-skill-fragments.py <file> [<file> ...]", file=sys.stderr)
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
        "Stale-skill-fragment safety floor FAILED "
        "(5-round critic arc: 9927e3e, 5e26e36, a39e334):",
        file=sys.stderr,
    )
    for path, line_no, label, match in all_hits:
        print(f"  {path}:{line_no}  [{label}]  -> {match!r}", file=sys.stderr)
    n_files = len({h[0] for h in all_hits})
    print(
        f"\n{len(all_hits)} stale-fragment match(es) across {n_files} file(s).",
        file=sys.stderr,
    )
    print(
        "These patterns correspond to framings the 5-round independent "
        "subagent self-critic caught at least once in the active tree. "
        "Move content to docs/principled/attic/, docs/principled/specs/, "
        "docs/superpowers/plans/, scripts/, research/, or "
        "docs/principled/marketplace-health/ if it's META-documentation. "
        "Otherwise, fix the underlying claim. "
        "Bypass with `git commit --no-verify`.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())