#!/usr/bin/env python3
"""Iteration-3 orchestrator: runs grader.py for each (eval, config) pair and
aggregates with-skill vs without-skill deltas.

Mirrors run_iteration_2.py's structure but replaces the read-counting
metrics with assertion-based grading. The comparator + analyzer logic
lives inline here for iter-3 (defer split to separate files in iter-3.1
per the project's anti-abstraction principle: don't extract until
3+ consumers).

Inputs (per eval, from iteration-3/assertions/<eval_id>.json):
  assertions[] with text + type + category + points summing to 100
  per category; weight override; reference_solution

Outputs (per eval, in iteration-3/eval-<id>/):
  grading_with_skill.json
  grading_without_skill.json
  comparison.json (per-eval deltas + verdict)

Aggregate outputs (in iteration-3/):
  benchmark.json — full results
  benchmark.md — human-readable report
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path("/Users/felix/Documents/AutoPluginClaw/taches-principled-light")
WORKSPACE = REPO / "docs/principled/skill-evals/marketplace-routing-2026-06-22"
ITER_DIR = WORKSPACE / "iteration-3"
ASSERTIONS_DIR = ITER_DIR / "assertions"
GRADER = ITER_DIR / "scripts/grader.py"
TIMEOUT_S = 300
DEFAULT_JUDGE_MODEL = "sonnet"  # override with --judge-model
LIFT_THRESHOLD_PP = 5  # per Tessl Table 4 norms; matches marketplace material_difference


def run_grader(eval_id: str, config: str, transcript_path: Path,
               output_dir: Path, judge_model: str = DEFAULT_JUDGE_MODEL) -> dict | None:
    """Invoke grader.py for one (eval, config) pair. Returns parsed grading
    or None on failure.

    transcript_path: where the with/without-skill NDJSON is read from
                     (typically iteration-2/eval-<id>/<config>_skill.jsonl)
    output_dir:       where grading_<config>_skill.json is written
                     (typically iteration-3/eval-<id>/)
    """
    assertions_path = ASSERTIONS_DIR / f"{eval_id}.json"
    if not assertions_path.exists():
        print(f"[iter-3] FATAL: no assertions for {eval_id} at {assertions_path}", file=sys.stderr)
        return None
    if not transcript_path.exists():
        print(f"[iter-3] {eval_id} {config}: no transcript at {transcript_path}; skipping",
              file=sys.stderr)
        return None
    cmd = [
        sys.executable, str(GRADER),
        "--assertions", str(assertions_path),
        "--transcript", str(transcript_path),
        "--eval-dir", str(output_dir),
        "--config", config,
        "--judge-model", judge_model,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT_S)
    except subprocess.TimeoutExpired:
        print(f"[iter-3] {eval_id} {config}: grader TIMEOUT after {TIMEOUT_S}s", file=sys.stderr)
        return None
    if result.returncode != 0:
        print(f"[iter-3] {eval_id} {config}: grader rc={result.returncode}",
              file=sys.stderr)
        print((result.stderr or "")[:500], file=sys.stderr)
        return None
    out_path = output_dir / f"grading_{config}_skill.json"
    if not out_path.exists():
        return None
    return json.loads(out_path.read_text())


def compute_deltas(with_grading: dict, without_grading: dict) -> dict:
    """Compute Tessl-style deltas + verdict classification."""
    s_with = with_grading["summary"]
    s_without = without_grading["summary"]
    if_delta = round(s_with["instruction_following_score"] - s_without["instruction_following_score"], 1)
    gc_delta = round(s_with["goal_completion_score"] - s_without["goal_completion_score"], 1)
    overall_delta = round(s_with["overall_score"] - s_without["overall_score"], 1)
    # Verdict classification
    if abs(overall_delta) <= LIFT_THRESHOLD_PP:
        verdict = "skill_neutral"
    elif if_delta > 5 and abs(gc_delta) <= 2:
        verdict = "skill_lifts_quality"
    elif overall_delta < -LIFT_THRESHOLD_PP:
        verdict = "skill_hurts"
    elif if_delta <= 1 and gc_delta <= 1:
        verdict = "skill_redundant"
    else:
        verdict = "skill_lifts_quality" if overall_delta > 0 else "skill_neutral"
    return {
        "with_skill": {
            "instruction_following_score": s_with["instruction_following_score"],
            "goal_completion_score": s_with["goal_completion_score"],
            "overall_score": s_with["overall_score"],
            "passed": s_with["passed"], "failed": s_with["failed"],
            "unknown": s_with["unknown"], "total": s_with["total"],
        },
        "without_skill": {
            "instruction_following_score": s_without["instruction_following_score"],
            "goal_completion_score": s_without["goal_completion_score"],
            "overall_score": s_without["overall_score"],
            "passed": s_without["passed"], "failed": s_without["failed"],
            "unknown": s_without["unknown"], "total": s_without["total"],
        },
        "delta": {
            "instruction_following_delta": if_delta,
            "goal_completion_delta": gc_delta,
            "overall_delta": overall_delta,
        },
        "verdict": verdict,
    }


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--judge-model", default=DEFAULT_JUDGE_MODEL)
    parser.add_argument("--evals", nargs="*", default=None,
                        help="Subset of eval IDs to run; default = all 18")
    parser.add_argument("--iter2-dir", default=None,
                        help="Path to iter-2 eval directories; default = "
                             "WORKSPACE/iteration-2/eval-<id>/")
    args = parser.parse_args()

    evals_data = json.loads((WORKSPACE / "evals/evals.json").read_text())
    evals = evals_data.get("evals", [])
    if args.evals:
        evals = [e for e in evals if e["id"] in set(args.evals)]
    iter2_root = Path(args.iter2_dir) if args.iter2_dir else (WORKSPACE / "iteration-2")

    print(f"[iter-3] running grader for {len(evals)} evals x 2 configs = {len(evals) * 2} grading calls")
    print(f"[iter-3] judge model: {args.judge_model}")
    print(f"[iter-3] reading transcripts from: {iter2_root}")
    print(f"[iter-3] writing outputs to: {ITER_DIR}")

    all_comparisons = []
    for i, ev in enumerate(evals, 1):
        eval_id = ev["id"]
        output_dir = ITER_DIR / f"eval-{eval_id}"
        output_dir.mkdir(parents=True, exist_ok=True)
        iter2_eval_dir = iter2_root / f"eval-{eval_id}"
        print(f"\n[{i}/{len(evals)}] {eval_id} (expected={ev['expected']})")
        with_grading = run_grader(
            eval_id, "with",
            transcript_path=iter2_eval_dir / "with_skill.jsonl",
            output_dir=output_dir,
            judge_model=args.judge_model,
        )
        if with_grading:
            s = with_grading["summary"]
            print(f"  with-skill:    overall={s['overall_score']} IF={s['instruction_following_score']} "
                  f"GC={s['goal_completion_score']} P/F/U={s['passed']}/{s['failed']}/{s['unknown']}")
        without_grading = run_grader(
            eval_id, "without",
            transcript_path=iter2_eval_dir / "without_skill.jsonl",
            output_dir=output_dir,
            judge_model=args.judge_model,
        )
        if without_grading:
            s = without_grading["summary"]
            print(f"  without-skill: overall={s['overall_score']} IF={s['instruction_following_score']} "
                  f"GC={s['goal_completion_score']} P/F/U={s['passed']}/{s['failed']}/{s['unknown']}")
        if not (with_grading and without_grading):
            print(f"  SKIP comparison (missing one or both gradings)", file=sys.stderr)
            continue
        deltas = compute_deltas(with_grading, without_grading)
        comparison = {
            "eval_id": eval_id,
            "utterance": ev["utterance"],
            "expected_skill": ev["expected"],
            "category_class": ev.get("category", "?"),
            **deltas,
        }
        (output_dir / "comparison.json").write_text(json.dumps(comparison, indent=2))
        d = deltas["delta"]
        print(f"  delta: IF={d['instruction_following_delta']:+5.1f} "
              f"GC={d['goal_completion_delta']:+5.1f} "
              f"overall={d['overall_delta']:+5.1f} → {deltas['verdict']}")
        all_comparisons.append(comparison)

    if not all_comparisons:
        print("[iter-3] no comparisons produced", file=sys.stderr)
        return 1

    # Aggregate
    n = len(all_comparisons)
    mean_if = round(sum(c["delta"]["instruction_following_delta"] for c in all_comparisons) / n, 2)
    mean_gc = round(sum(c["delta"]["goal_completion_delta"] for c in all_comparisons) / n, 2)
    mean_overall = round(sum(c["delta"]["overall_delta"] for c in all_comparisons) / n, 2)
    verdict_counts: dict[str, int] = {}
    for c in all_comparisons:
        verdict_counts[c["verdict"]] = verdict_counts.get(c["verdict"], 0) + 1
    per_skill_lift: dict[str, list[float]] = {}
    for c in all_comparisons:
        per_skill_lift.setdefault(c["expected_skill"], []).append(c["delta"]["overall_delta"])
    per_skill_mean = {
        skill: round(sum(v) / len(v), 2)
        for skill, v in per_skill_lift.items()
    }
    benchmark = {
        "iteration": 3,
        "scope": f"{n} of 18 evals",
        "judge_model": args.judge_model,
        "results": all_comparisons,
        "summary": {
            "total_evals": n,
            "mean_instruction_following_delta": mean_if,
            "mean_goal_completion_delta": mean_gc,
            "mean_overall_delta": mean_overall,
            "verdict_distribution": verdict_counts,
            "per_skill_lift": per_skill_mean,
        },
        "notes": (
            "Iteration 3 uses assertion-based grading per the Tessl framework "
            "(arxiv 2606.17819v1). Judge model = "
            f"{args.judge_model} (proxy alias; see iteration-3-design.md for "
            "the bias mitigation rationale). Solver model = haiku chain. "
            "Lift threshold for skill_lifts_quality = +5pp (matches "
            "evaluating-skills' material_difference rule)."
        ),
    }
    (ITER_DIR / "benchmark.json").write_text(json.dumps(benchmark, indent=2))

    # Human-readable report
    md = [
        f"# Iteration 3 — Assertion-Based Skill Grading (N={n})",
        "",
        "## Configuration",
        f"- Judge model: `{args.judge_model}`",
        f"- Solver model: haiku (project convention)",
        f"- Lift threshold: ±{LIFT_THRESHOLD_PP}pp for skill_neutral",
        "",
        "## Summary",
        f"- Evals: {n}",
        f"- Mean IF delta: {mean_if:+.2f}",
        f"- Mean GC delta: {mean_gc:+.2f}",
        f"- Mean overall delta: {mean_overall:+.2f}",
        "",
        f"### Verdict distribution",
    ]
    for verdict, count in sorted(verdict_counts.items(), key=lambda x: -x[1]):
        md.append(f"- `{verdict}`: {count}/{n}")
    md.extend([
        "",
        f"### Per-skill mean overall delta",
        "",
        "| Skill | Mean Δ | Evals |",
        "|-------|-------:|------:|",
    ])
    for skill, lift in sorted(per_skill_mean.items(), key=lambda x: -x[1]):
        md.append(f"| {skill} | {lift:+.2f} | {len(per_skill_lift[skill])} |")
    md.extend([
        "",
        "## Per-eval results",
        "",
        "| Eval | Expected | IF Δ | GC Δ | Overall Δ | Verdict |",
        "|------|----------|-----:|-----:|----------:|---------|",
    ])
    for c in all_comparisons:
        d = c["delta"]
        md.append(
            f"| {c['eval_id']} | {c['expected_skill']} | "
            f"{d['instruction_following_delta']:+5.1f} | "
            f"{d['goal_completion_delta']:+5.1f} | "
            f"{d['overall_delta']:+5.1f} | {c['verdict']} |"
        )
    md.extend([
        "",
        "## Methodology",
        "",
        "- Tessl-style per-category 0-100 scoring (IF + GC, weighted 50/50 by default)",
        "- Two assertions per category minimum; some evals use weight overrides",
        "- Code-based checks (consultation, structure with compare_args) bypass the LLM",
        "- UNKNOWN verdicts (judge couldn't determine) are treated as FAIL for scoring",
        "  but logged in `iteration-3/unknowns.md` for human review",
        "",
    ])
    (ITER_DIR / "benchmark.md").write_text("\n".join(md))

    print(f"\n[iter-3] done. {n} evals graded.")
    print(f"[iter-3] mean overall delta: {mean_overall:+.2f}")
    print(f"[iter-3] verdict distribution: {verdict_counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
