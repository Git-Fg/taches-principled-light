#!/usr/bin/env python3
"""Aggregate behavioral_comparison.json files into benchmark.json + benchmark.md.

Pure Python stdlib — no subprocess, no external dependencies. Reads the
per-eval behavioral_comparison.json files emitted by stage 4 of the
evaluating-skills methodology, and writes the iteration-level benchmark.json
(mean ± stddev per configuration + delta) plus a human-readable benchmark.md.

Usage:
    python scripts/aggregate_benchmark.py <workspace>/iteration-N \
        --skill-name <name> [--runs N]

Schema for inputs and outputs: see skills/evaluating-skills/references/schemas.md.
The output schema is identical to Anthropic's `skill-creator` benchmark.json,
plus a sibling benchmark.md for humans.
"""

import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

# Output schema mirror — keep in sync with references/schemas.md §benchmark.json
DELTA_KEYS = ("pass_rate", "time_seconds", "tokens")
METRIC_KEYS = ("pass_rate", "time_seconds", "tokens")


def discover_runs(iteration_dir: Path) -> list[tuple[int, str, int, Path]]:
    """Return [(eval_id, configuration, run_number, comparison_path), ...]

    Walks <iteration_dir>/eval-<name>/ and finds every *.{with_skill,without_skill}.json
    that is a behavioral_comparison.json. The eval id is parsed from a leading digit
    prefix (eval-0, eval-1, ...) for stability; if not present, falls back to dir index.
    """
    runs = []
    for eval_dir in sorted(iteration_dir.iterdir()):
        if not eval_dir.is_dir():
            continue
        # Parse eval id from "eval-N" or "eval-<descriptive-name-with-leading-digit>"
        name = eval_dir.name
        if name.startswith("eval-"):
            tail = name[len("eval-"):]
            digits = "".join(c for c in tail.split("-")[0] if c.isdigit())
            eval_id = int(digits) if digits else 0
        else:
            eval_id = 0

        for comp in eval_dir.glob("*.json"):
            # The reviewer subagent writes one of:
            #   with_skill.json     with_skill.json
            #   without_skill.json  without_skill.json
            config = comp.stem  # "with_skill" or "without_skill"
            if config not in ("with_skill", "without_skill"):
                continue
            try:
                data = json.loads(comp.read_text())
            except json.JSONDecodeError as e:
                print(f"WARN: skipping malformed {comp}: {e}", file=sys.stderr)
                continue
            if "dimensions" not in data:
                print(f"WARN: {comp} missing 'dimensions' field — not a behavioral_comparison.json", file=sys.stderr)
                continue
            run_number = data.get("run_number", 1)
            runs.append((eval_id, config, run_number, comp, data))
    return runs


def per_run_summary(data: dict) -> dict:
    """Extract the per-run result block from a behavioral_comparison.json.

    Mirrors the result shape Anthropic's benchmark.json expects:
        { pass_rate, passed, failed, total, time_seconds, tokens, tool_calls, errors }

    Precedence for pass_rate: explicit `expectations[]` carry the authoritative
    pass/fail signal (one PASS = the eval's expectation was met). When
    expectations are absent (stage-4 reviewer didn't populate them yet), we
    fall back to the mean of per-dimension scores / 5.0 as a proxy. The two
    paths produce different numbers; consumers should treat the
    expectations-derived value as authoritative when present.
    """
    dimensions = data.get("dimensions", [])
    expectations = data.get("expectations", [])

    if expectations:
        passed = sum(1 for e in expectations if e.get("passed"))
        total = len(expectations)
        pass_rate = passed / total if total else 0.0
    elif dimensions:
        # Fallback: mean of with_skill scores / 5.0, used only when the reviewer
        # didn't populate expectations. Document this is a proxy.
        valid = [d["with_skill"] for d in dimensions if d.get("with_skill") is not None]
        pass_rate = statistics.mean(valid) / 5.0 if valid else 0.0
        passed = sum(1 for d in dimensions if d.get("with_skill", 0) >= 4)  # "good enough" heuristic
        total = len(dimensions)
    else:
        return {"pass_rate": 0.0, "total": 0, "passed": 0, "failed": 0,
                "time_seconds": 0.0, "tokens": 0, "tool_calls": 0, "errors": 0}

    timing = data.get("timing", {})
    execution = data.get("execution_metrics", {})

    return {
        "pass_rate": round(pass_rate, 4),
        "passed": passed,
        "failed": total - passed,
        "total": total,
        "time_seconds": round(timing.get("total_duration_seconds", 0.0), 2),
        "tokens": timing.get("total_tokens", 0) or execution.get("total_tokens", 0),
        "tool_calls": execution.get("total_tool_calls", 0),
        "errors": execution.get("errors_encountered", 0),
    }


def aggregate(iteration_dir: Path, skill_name: str, runs_per_query: int = 3) -> dict:
    """Aggregate per-run behavioral_comparison files into the canonical benchmark.json."""
    raw = discover_runs(iteration_dir)
    if not raw:
        print(f"ERROR: no behavioral_comparison.json files found under {iteration_dir}", file=sys.stderr)
        sys.exit(1)

    # Group by (eval_id, configuration) so we can compute mean/stddev across runs.
    grouped: dict[tuple[int, str], list[tuple[int, dict, dict]]] = defaultdict(list)
    for eval_id, config, run_number, _path, data in raw:
        grouped[(eval_id, config)].append((run_number, per_run_summary(data), data))

    runs_out = []
    for (eval_id, config), items in sorted(grouped.items()):
        # Sort by run_number for deterministic ordering.
        items.sort(key=lambda x: x[0])
        for run_number, result, data in items:
            eval_name = f"eval-{eval_id}-{config.replace('_', '-')}"
            expectations = data.get("expectations", [])
            notes = data.get("summary") if isinstance(data.get("summary"), str) else None
            runs_out.append({
                "eval_id": eval_id,
                "eval_name": eval_name,
                "configuration": config,
                "run_number": run_number,
                "result": result,
                "expectations": expectations,
                "notes": [notes] if notes else [],
            })

    # run_summary: aggregate per config across all (eval_id, run_number) pairs.
    by_config: dict[str, list[dict]] = defaultdict(list)
    for r in runs_out:
        by_config[r["configuration"]].append(r["result"])

    def stat(key: str) -> dict:
        values = [r[key] for r in (by_config["with_skill"] if key in by_config.get("with_skill", [{}])[0] else [])]
        return {}  # placeholder; replaced below

    run_summary = {}
    for config in ("with_skill", "without_skill"):
        results = by_config.get(config, [])
        if not results:
            continue
        summary_per_metric = {}
        for metric in METRIC_KEYS:
            values = [r[metric] for r in results if r.get(metric) is not None]
            if not values:
                continue
            summary_per_metric[metric] = {
                "mean": round(statistics.mean(values), 4),
                "stddev": round(statistics.stdev(values), 4) if len(values) > 1 else 0.0,
                "min": round(min(values), 4),
                "max": round(max(values), 4),
            }
        run_summary[config] = summary_per_metric

    # delta: with_skill minus without_skill for each metric. Sign convention:
    # positive pass_rate delta = good; positive time/tokens delta = cost.
    delta = {}
    if "with_skill" in run_summary and "without_skill" in run_summary:
        for metric in DELTA_KEYS:
            if metric in run_summary["with_skill"] and metric in run_summary["without_skill"]:
                w = run_summary["with_skill"][metric]["mean"]
                wo = run_summary["without_skill"][metric]["mean"]
                diff = w - wo
                sign = "+" if diff >= 0 else ""
                # For time/tokens, format with one decimal to match Anthropic's convention.
                if metric in ("time_seconds", "tokens"):
                    delta[metric] = f"{sign}{round(diff, 1)}"
                else:
                    delta[metric] = f"{sign}{round(diff, 4)}"

    benchmark = {
        "metadata": {
            "skill_name": skill_name,
            "skill_path": str(iteration_dir.parent) if iteration_dir.name.startswith("iteration-") else str(iteration_dir),
            "timestamp": _now_iso(),
            "evals_run": sorted({r["eval_id"] for r in runs_out}),
            "runs_per_configuration": runs_per_query,
        },
        "runs": runs_out,
        "run_summary": run_summary,
        "delta": delta,
        "notes": _notes(runs_out, run_summary),
    }
    return benchmark


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _notes(runs_out: list, run_summary: dict) -> list[str]:
    """Auto-derived analyst notes — the human can rewrite these."""
    notes = []
    if "with_skill" in run_summary and "without_skill" in run_summary:
        wp = run_summary["with_skill"].get("pass_rate", {}).get("mean", 0)
        bp = run_summary["without_skill"].get("pass_rate", {}).get("mean", 0)
        if wp - bp >= 0.30:
            notes.append(f"With-skill pass_rate exceeds baseline by {round(wp - bp, 4)} — material improvement.")
        elif abs(wp - bp) < 0.05:
            notes.append(f"Pass_rate delta is small ({round(wp - bp, 4)}) — skill may not be moving the needle; investigate.")
    # Non-discriminating assertions
    for r in runs_out:
        if r["result"]["total"] > 0 and r["result"]["passed"] == r["result"]["total"]:
            notes.append(f"Eval {r['eval_id']} ({r['configuration']}) passes 100% — check if any expectations are trivially satisfied.")
    return notes


def render_markdown(benchmark: dict) -> str:
    md = []
    md.append(f"# Benchmark — `{benchmark['metadata']['skill_name']}`\n")
    md.append(f"_Generated {benchmark['metadata']['timestamp']}_\n")
    md.append(f"Evals run: `{benchmark['metadata']['evals_run']}` · "
              f"Runs per configuration: `{benchmark['metadata']['runs_per_configuration']}`\n\n")

    if benchmark.get("run_summary"):
        md.append("## Run Summary\n\n")
        md.append("| Configuration | Metric | Mean | Stddev | Min | Max |\n")
        md.append("|---|---|---|---|---|---|\n")
        for config, metrics in benchmark["run_summary"].items():
            for metric, stats in metrics.items():
                md.append(f"| `{config}` | {metric} | {stats['mean']} | {stats['stddev']} | {stats['min']} | {stats['max']} |\n")
        md.append("\n")

    if benchmark.get("delta"):
        md.append("## Delta (with_skill − without_skill)\n\n")
        for metric, value in benchmark["delta"].items():
            md.append(f"- **{metric}**: `{value}`\n")
        md.append("\n")

    if benchmark.get("notes"):
        md.append("## Analyst Notes\n\n")
        for n in benchmark["notes"]:
            md.append(f"- {n}\n")
        md.append("\n")

    md.append("## Per-Run Detail\n\n")
    md.append("| Eval | Config | Run | pass_rate | time_s | tokens | tool_calls |\n")
    md.append("|---|---|---|---|---|---|---|\n")
    for r in benchmark.get("runs", []):
        md.append(f"| {r['eval_id']} | `{r['configuration']}` | {r['run_number']} | "
                  f"{r['result']['pass_rate']} | {r['result']['time_seconds']} | "
                  f"{r['result']['tokens']} | {r['result']['tool_calls']} |\n")
    return "".join(md)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("iteration_dir", type=Path, help="Path to <workspace>/iteration-N/")
    ap.add_argument("--skill-name", required=True, help="Skill name (for benchmark.metadata.skill_name)")
    ap.add_argument("--runs", type=int, default=3, help="Runs per configuration (for metadata only; default 3)")
    args = ap.parse_args()

    if not args.iteration_dir.is_dir():
        print(f"ERROR: {args.iteration_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    benchmark = aggregate(args.iteration_dir, args.skill_name, args.runs)
    out_json = args.iteration_dir / "benchmark.json"
    out_md = args.iteration_dir / "benchmark.md"
    out_json.write_text(json.dumps(benchmark, indent=2))
    out_md.write_text(render_markdown(benchmark))
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()