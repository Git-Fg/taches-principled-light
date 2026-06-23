#!/usr/bin/env python3
"""Iteration-6 orchestrator: vendor-disjoint judge re-grade.

Resolves the 2026-06-23 grader-noise / same-family-bias question. iter-4 and
iter-7 used `sonnet` as the judge, which is from the same family as the `haiku`
solver. Per Wataoka 2024 (arxiv:2410.21819) LLM judges can inflate scores for
outputs from the same family. CoEval 2026 (arxiv:2606.03650) recommends a
vendor-disjoint judge.

iter-6 re-grades the existing iter-7 transcripts (baseline, plugin_only,
plugin_with_add_dir) with `glm-5.2` (Z.AI) as the judge. No new solver runs.
The transcripts are already correct for the 4-eval subset; iter-6 only varies
the judge.

Scope: 4 evals x 3 configs = 12 grading cells with glm-5.2.

Eval scope (same as iter-7, N=4):
  - eval-skill  (iter-4 mechanism: consultation)
  - sec-audit   (iter-4 mechanism: consultation)
  - lint-1      (iter-4 mechanism: file-access)
  - release-2   (iter-4 mechanism: file-access)

Wall time: ~10-15 min for 12 grading cells on a warm proxy.

Outputs (per eval, in iteration-6/eval-<id>/):
  grading_{config}_skill_glm5-2.json — raw grader output
  comparison_glm5-2.json             — 3-lift summary
  iter6_grading_{config}.log         — per-cell wall log

Outputs (top-level):
  benchmark.json
  benchmark.md
  benchmark_iter4_vs_iter6.json    — direct comparison (sonnet vs glm-5.2 deltas)
  benchmark_iter4_vs_iter6.md
  iter6_full_run.log
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path("/Users/felix/Documents/AutoPluginClaw/taches-principled-light")
WORKSPACE = REPO / "docs/principled/skill-evals/marketplace-routing-2026-06-22"
ITER6_DIR = WORKSPACE / "iteration-6"
ITER7_DIR = WORKSPACE / "iteration-7"
ITER3_ASSERTIONS = (WORKSPACE / "iteration-3") / "assertions"
ITER3_GRADER = (WORKSPACE / "iteration-3") / "scripts" / "grader.py"
PROXY_BASE_URL = "http://100.80.231.128:3456"
DEFAULT_JUDGE_MODEL = "glm-5.2"
LIFT_THRESHOLD_PP = 5

# 4-eval subset (same as iter-7).
ITER6_EVALS = [
    ("eval-skill", "consultation"),
    ("sec-audit", "consultation"),
    ("lint-1", "file-access"),
    ("release-2", "file-access"),
]

# Three configs. iter-6 re-grades the iter-7 transcripts; the grader's
# --config flag accepts only "with" or "without" (hardcoded), so we
# translate: baseline -> without, plugin_only -> without, plugin_with_add_dir -> with.
GRADER_CONFIG_MAP = {
    "baseline": "without",
    "plugin_only": "without",
    "plugin_with_add_dir": "with",
}


def grade_one(eval_id: str, iter6_config: str, transcript_path: Path,
              eval_dir: Path, judge_model: str) -> dict | None:
    """Run the iter-3 grader on one (eval, config) pair with a chosen judge."""
    assertions = ITER3_ASSERTIONS / f"{eval_id}.json"
    if not assertions.exists():
        print(f"[iter-6] SKIP {eval_id} {iter6_config}: assertions missing",
              file=sys.stderr, flush=True)
        return None
    if not transcript_path.exists():
        print(f"[iter-6] SKIP {eval_id} {iter6_config}: transcript missing "
              f"({transcript_path})", file=sys.stderr, flush=True)
        return None

    grader_config = GRADER_CONFIG_MAP[iter6_config]
    out_path = eval_dir / f"grading_{iter6_config}_skill_glm5-2.json"
    log_path = eval_dir / f"iter6_grading_{iter6_config}.log"

    cmd = [
        sys.executable, str(ITER3_GRADER),
        "--assertions", str(assertions),
        "--transcript", str(transcript_path),
        "--eval-dir", str(eval_dir),
        "--config", grader_config,
        "--judge-model", judge_model,
    ]
    print(f"  grading {eval_id} {iter6_config} (grader={grader_config}, "
          f"judge={judge_model})...", end="", flush=True)
    t0 = time.time()
    try:
        with open(log_path, "w") as logf:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            logf.write(f"cmd: {' '.join(cmd)}\n")
            logf.write(f"returncode: {r.returncode}\n")
            logf.write("--- stdout ---\n")
            logf.write(r.stdout or "")
            logf.write("\n--- stderr ---\n")
            logf.write(r.stderr or "")
    except subprocess.TimeoutExpired:
        print(f" TIMEOUT", file=sys.stderr, flush=True)
        return None
    if r.returncode != 0:
        print(f" rc={r.returncode}", file=sys.stderr, flush=True)
        return None
    # Grader writes to eval_dir/grading_{config}_skill.json (hardcoded suffix)
    grader_out = eval_dir / f"grading_{grader_config}_skill.json"
    if not grader_out.exists():
        print(f" (no output at {grader_out})", file=sys.stderr, flush=True)
        return None
    data = json.loads(grader_out.read_text())
    data["iter6_config"] = iter6_config
    data["iter6_judge"] = judge_model
    data["iter6_grader_config"] = grader_config
    # Persist under our iter-6 naming (don't disturb the grader's own file)
    iter6_out = eval_dir / f"grading_{iter6_config}_skill_glm5-2.json"
    iter6_out.write_text(json.dumps(data, indent=2))
    dt = time.time() - t0
    print(f" {dt:.1f}s", flush=True)
    return data


def score(g: dict) -> dict:
    s = g["summary"]
    return {
        "overall_score": s["overall_score"],
        "instruction_following_score": s["instruction_following_score"],
        "goal_completion_score": s["goal_completion_score"],
        "passed": s["passed"], "failed": s["failed"],
        "unknown": s["unknown"], "total": s["total"],
    }


def compute_three_way_deltas(baseline_g, plugin_only_g, plugin_with_add_dir_g):
    s_b = baseline_g["summary"]
    s_po = plugin_only_g["summary"]
    s_pa = plugin_with_add_dir_g["summary"]

    def delta(a, b, key):
        return round(a[key] - b[key], 1)

    consult = {
        "instruction_following_delta": delta(s_po, s_b, "instruction_following_score"),
        "goal_completion_delta": delta(s_po, s_b, "goal_completion_score"),
        "overall_delta": delta(s_po, s_b, "overall_score"),
    }
    fs = {
        "instruction_following_delta": delta(s_pa, s_po, "instruction_following_score"),
        "goal_completion_delta": delta(s_pa, s_po, "goal_completion_score"),
        "overall_delta": delta(s_pa, s_po, "overall_score"),
    }
    total = {
        "instruction_following_delta": delta(s_pa, s_b, "instruction_following_score"),
        "goal_completion_delta": delta(s_pa, s_b, "goal_completion_score"),
        "overall_delta": delta(s_pa, s_b, "overall_score"),
    }

    def verdict_for(d):
        if abs(d["overall_delta"]) <= LIFT_THRESHOLD_PP:
            return "skill_neutral"
        if d["overall_delta"] < -LIFT_THRESHOLD_PP:
            return "skill_hurts"
        if (d["instruction_following_delta"] <= 1
                and d["goal_completion_delta"] <= 1):
            return "skill_redundant"
        return "skill_lifts_quality"

    return {
        "baseline": score(baseline_g),
        "plugin_only": score(plugin_only_g),
        "plugin_with_add_dir": score(plugin_with_add_dir_g),
        "lifts": {
            "consultation_lift": {**consult, "verdict": verdict_for(consult)},
            "filesystem_access_lift": {**fs, "verdict": verdict_for(fs)},
            "total_lift": {**total, "verdict": verdict_for(total)},
        },
    }


def main() -> int:
    ITER6_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[iter-6] 4-eval subset x 3 configs = 12 grading cells with "
          f"judge=glm-5.2 (vendor-disjoint from haiku solver)", flush=True)
    print(f"[iter-6] reuses iter-7 transcripts (symlinked)", flush=True)

    # Phase 1: grading
    print(f"\n[iter-6] phase 1: grading", flush=True)
    iter6_results = []
    for i, (eval_id, mechanism) in enumerate(ITER6_EVALS, 1):
        ed = ITER6_DIR / f"eval-{eval_id}"
        ed.mkdir(parents=True, exist_ok=True)
        print(f"\n[{i}/4] grading {eval_id} (iter-4 mechanism: {mechanism})",
              flush=True)
        g_b = grade_one(eval_id, "baseline", ed / "baseline_skill.jsonl",
                        ed, DEFAULT_JUDGE_MODEL)
        g_po = grade_one(eval_id, "plugin_only", ed / "plugin_only_skill.jsonl",
                         ed, DEFAULT_JUDGE_MODEL)
        g_pa = grade_one(eval_id, "plugin_with_add_dir",
                         ed / "plugin_with_add_dir_skill.jsonl",
                         ed, DEFAULT_JUDGE_MODEL)
        for label, g in [("baseline", g_b), ("plugin_only", g_po),
                         ("plugin_with_add_dir", g_pa)]:
            if g:
                s = g["summary"]
                print(f"  {label:>20}: overall={s['overall_score']:5.1f} "
                      f"IF={s['instruction_following_score']:5.1f} "
                      f"GC={s['goal_completion_score']:5.1f}", flush=True)
        if not (g_b and g_po and g_pa):
            print(f"  PARTIAL {eval_id}: some configs failed", file=sys.stderr,
                  flush=True)
            continue
        deltas = compute_three_way_deltas(g_b, g_po, g_pa)
        cmp_entry = {
            "eval_id": eval_id,
            "iter4_mechanism": mechanism,
            "judge_model": DEFAULT_JUDGE_MODEL,
            **deltas,
        }
        (ed / "comparison_glm5-2.json").write_text(json.dumps(cmp_entry, indent=2))
        iter6_results.append(cmp_entry)

    if not iter6_results:
        print("[iter-6] abort: no eval produced results", file=sys.stderr)
        return 4

    # Aggregate summary
    consult_lifts = [r["lifts"]["consultation_lift"]["overall_delta"]
                     for r in iter6_results]
    fs_lifts = [r["lifts"]["filesystem_access_lift"]["overall_delta"]
                for r in iter6_results]
    total_lifts = [r["lifts"]["total_lift"]["overall_delta"]
                   for r in iter6_results]
    summary = {
        "total_evals": len(iter6_results),
        "judge_model": DEFAULT_JUDGE_MODEL,
        "consultation_lift": {
            "mean_overall_delta": round(sum(consult_lifts) / len(consult_lifts), 2),
        },
        "filesystem_access_lift": {
            "mean_overall_delta": round(sum(fs_lifts) / len(fs_lifts), 2),
        },
        "total_lift": {
            "mean_overall_delta": round(sum(total_lifts) / len(total_lifts), 2),
        },
    }
    iter6_benchmark = {
        "iteration": 6,
        "phase": "A",
        "scope": f"{len(iter6_results)} of 4 evals (4-eval subset)",
        "judge_model": DEFAULT_JUDGE_MODEL,
        "solver_model": "haiku",
        "results": iter6_results,
        "summary": summary,
    }
    (ITER6_DIR / "benchmark.json").write_text(json.dumps(iter6_benchmark, indent=2))
    print(f"\n[iter-6] summary written: {ITER6_DIR / 'benchmark.json'}",
          flush=True)

    # Compare with iter-4 + iter-7 (sonnet) deltas
    print(f"\n[iter-6] cross-judge comparison (sonnet vs glm-5.2)",
          flush=True)
    iter4_dir = WORKSPACE / "iteration-4"
    iter4_data = json.loads((iter4_dir / "benchmark.json").read_text())
    iter4_by_id = {r["eval_id"]: r for r in iter4_data["results"]}
    iter7_data = json.loads((ITER7_DIR / "benchmark.json").read_text())
    iter7_by_id = {r["eval_id"]: r for r in iter7_data["results"]}
    cmp_rows = []
    for r in iter6_results:
        eid = r["eval_id"]
        iter4 = iter4_by_id.get(eid, {})
        iter7 = iter7_by_id.get(eid, {})
        iter4_total = iter4.get("delta", {}).get("overall_delta")
        iter7_total = iter7.get("lifts", {}).get("total_lift", {}).get("overall_delta")
        iter6_total = r["lifts"]["total_lift"]["overall_delta"]
        iter4_fs = iter4_total  # iter-4's "delta" is the marginal filesystem_access lift
        iter7_fs = iter7.get("lifts", {}).get("filesystem_access_lift", {}).get("overall_delta")
        iter6_fs = r["lifts"]["filesystem_access_lift"]["overall_delta"]
        cmp_rows.append({
            "eval_id": eid,
            "iter4_total_lift_sonnet": iter4_total,
            "iter7_filesystem_access_lift_sonnet": iter7_fs,
            "iter7_total_lift_sonnet": iter7_total,
            "iter6_filesystem_access_lift_glm5-2": iter6_fs,
            "iter6_total_lift_glm5-2": iter6_total,
            "delta_sonnet_vs_glm5-2_total_lift": (
                None if iter7_total is None or iter6_total is None
                else round(iter7_total - iter6_total, 2)
            ),
        })
    cmp_data = {
        "purpose": "Rule out same-family bias (sonnet over haiku) by "
                   "re-grading with vendor-disjoint glm-5.2",
        "rows": cmp_rows,
        "verdict": "computed below",
    }
    (ITER6_DIR / "benchmark_iter4_vs_iter6.json").write_text(
        json.dumps(cmp_data, indent=2))
    print(f"[iter-6] comparison written: "
          f"{ITER6_DIR / 'benchmark_iter4_vs_iter6.json'}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
