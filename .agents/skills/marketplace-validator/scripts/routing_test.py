#!/usr/bin/env python3
"""Routing test for skill descriptions.

For each test utterance, score every SKILL.md by counting content-word
overlap with the description. Report top match per utterance and whether
there's a clear winner (top score > runner-up).

Usage:
    python3 routing_test.py                    # default 10 utterances
    python3 routing_test.py --strict           # exit 1 on ties/losses
    python3 routing_test.py --expected NAME    # use custom expected skill

The 10 default utterances cover the 4 local meta-skills plus a few
adjacent marketplace skills to detect routing collisions.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def load_skills(root: Path) -> dict[str, str]:
    """Load all SKILL.md frontmatter descriptions."""
    skills: dict[str, str] = {}
    for p in root.rglob("SKILL.md"):
        text = p.read_text()
        m = re.search(r"^description:\s*>\s*\n((?:  .*\n)+)", text, re.MULTILINE)
        if not m:
            continue
        desc = re.sub(r"^  ", "", m.group(1), flags=re.MULTILINE).strip()
        skills[p.parent.name] = desc
    return skills


def tokens(s: str) -> set[str]:
    return {t for t in re.split(r"\W+", s.lower()) if len(t) > 2}


# Default utterance set: covers the 4 local meta-skills + 6 marketplace
# skills to detect routing collisions. Add more as new local skills ship.
DEFAULT_UTTERANCES: list[tuple[str, str]] = [
    ("marketplace-validator", "lint the marketplace and check the frontmatter"),
    ("marketplace-validator", "is this skill valid before I commit"),
    ("marketplace-health", "audit the marketplace and run the pre-release health check"),
    ("marketplace-health", "is the marketplace healthy, check for drift"),
    ("ingesting-skills", "port this skill from a github url into our collection"),
    ("ingesting-skills", "add this skill to our marketplace, import it"),
    ("releasing-marketplace", "cut a release and bump the version to 0.0.2"),
    ("releasing-marketplace", "tag and push the new version"),
    ("general-critic", "review this PR and find the worst issues"),
    ("deep-research", "do deep research on agent skill evaluation methodology"),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=Path("."), help="project root (default: cwd)")
    ap.add_argument("--strict", action="store_true", help="exit 1 on ties/losses")
    args = ap.parse_args()

    skills = load_skills(args.root)
    print(f"Loaded {len(skills)} skills\n")

    clear_wins = ties = losses = 0

    print(f"{'Exp':<25} {'Utterance':<58} {'Top match':<25} {'Score':>5} {'2nd':>4} Result")
    print("-" * 130)

    for expected, utterance in DEFAULT_UTTERANCES:
        utt_tokens = tokens(utterance)
        scores: list[tuple[int, str]] = []
        for name, desc in skills.items():
            s = len(utt_tokens & tokens(desc))
            if s > 0:
                scores.append((s, name))
        scores.sort(reverse=True)

        if not scores:
            print(f"{expected:<25} {utterance:<58} (no matches)")
            losses += 1
            continue

        top_score, top = scores[0]
        second = scores[1][0] if len(scores) > 1 else 0
        is_clear = top_score > second
        is_correct = top == expected

        if is_correct and is_clear:
            result = "✓"
            clear_wins += 1
        elif is_correct:
            result = "TIE"
            ties += 1
        else:
            result = "✗"
            losses += 1

        print(f"{expected:<25} {utterance:<58} {top:<25} {top_score:>5} {second:>4} {result}")

    print(f"\n=== Routing test summary ===")
    print(f"  Clear wins: {clear_wins}/{len(DEFAULT_UTTERANCES)}")
    print(f"  Ties:       {ties}/{len(DEFAULT_UTTERANCES)}")
    print(f"  Losses:     {losses}/{len(DEFAULT_UTTERANCES)}")

    if args.strict and (ties or losses):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
