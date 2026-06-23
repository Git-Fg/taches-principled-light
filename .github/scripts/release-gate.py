#!/usr/bin/env python3
"""release-gate.py — assert iter-7 lift thresholds and emit a release summary.

Reads docs/principled/skill-evals/marketplace-routing-2026-06-22/iteration-7/benchmark.json
and verifies the v0.0.5 release contract:
  - summary.total_lift.mean_overall_delta >= +15pp
  - summary has 3 lifts: consultation_lift, filesystem_access_lift, total_lift
  - no per-eval result.lifts.total_lift.overall_delta < 0pp

Usage:
  python3 .github/scripts/release-gate.py
  python3 .github/scripts/release-gate.py --benchmark <path>
  python3 .github/scripts/release-gate.py --json        # machine-readable output

Exit codes:
  0 = all thresholds met, safe to ship
  1 = threshold violation (build fails)
  2 = benchmark.json missing or malformed
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_BENCHMARK = (
    REPO
    / "docs/principled/skill-evals/marketplace-routing-2026-06-22/iteration-7/benchmark.json"
)

# Release thresholds (v0.0.5 contract)
MIN_TOTAL_LIFT_PP = 15.0
REQUIRED_LIFTS = ("consultation_lift", "filesystem_access_lift", "total_lift")


def load_benchmark(path: Path) -> dict:
    if not path.exists():
        print(f"[release-gate] FAIL: benchmark not found at {path}", file=sys.stderr)
        sys.exit(2)
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as e:
        print(f"[release-gate] FAIL: benchmark.json malformed: {e}", file=sys.stderr)
        sys.exit(2)


def evaluate(b: dict) -> tuple[bool, list[str]]:
    """Return (passed, list of failure reasons)."""
    failures: list[str] = []
    summary = b.get("summary", {})
    missing = [k for k in REQUIRED_LIFTS if k not in summary]
    if missing:
        failures.append(
            f"summary missing lifts: {missing} "
            f"(expected: {', '.join(REQUIRED_LIFTS)})"
        )
    total = summary.get("total_lift", {})
    total_mean = total.get("mean_overall_delta")
    if total_mean is None:
        failures.append("summary.total_lift.mean_overall_delta missing")
    elif total_mean < MIN_TOTAL_LIFT_PP:
        failures.append(
            f"summary.total_lift.mean_overall_delta = {total_mean:+.2f}pp "
            f"< MIN_TOTAL_LIFT_PP = {MIN_TOTAL_LIFT_PP:+.2f}pp"
        )
    for r in b.get("results", []):
        eid = r.get("eval_id", "?")
        tl = (r.get("lifts", {}).get("total_lift") or {}).get("overall_delta")
        if tl is None:
            continue
        if tl < 0:
            failures.append(
                f"per-eval hurt: {eid} total_lift.overall_delta = {tl:+.2f}pp"
            )
    return (len(failures) == 0, failures)


def render_summary(b: dict) -> str:
    s = b.get("summary", {})
    parts = []
    for key in REQUIRED_LIFTS:
        v = s.get(key, {})
        delta = v.get("mean_overall_delta")
        parts.append(f"{key} = {delta:+.2f}pp" if delta is not None else f"{key} = n/a")
    parts.append(f"n_results = {len(b.get('results', []))}")
    return " | ".join(parts)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK)
    p.add_argument("--json", action="store_true",
                   help="emit a single JSON object: {passed, failures, summary}")
    args = p.parse_args()

    b = load_benchmark(args.benchmark)
    passed, failures = evaluate(b)
    summary = render_summary(b)
    if args.json:
        print(json.dumps({
            "passed": passed,
            "failures": failures,
            "summary": summary,
            "benchmark_path": str(args.benchmark),
        }, indent=2))
    else:
        if passed:
            print(f"[release-gate] PASS: {summary}")
        else:
            print(f"[release-gate] FAIL: {summary}", file=sys.stderr)
            for f in failures:
                print(f"  - {f}", file=sys.stderr)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
