#!/usr/bin/env python3
"""Iteration-7 Phase A orchestrator.

Resolves the 2026-06-23 baseline contamination finding: iter-4's
"without_skill" baseline is contaminated by the auto-loaded marketplace
plugin (the agent invokes /crafting-skills etc. via slash commands even
without --add-dir). iter-4's +4.94pp is therefore the FILESYSTEM ACCESS
LIFT, not the total lift.

iter-7 adds a TRUE baseline via --disable-slash-commands, producing three
configs that fully disambiguate the lift mechanism:

  baseline            = --disable-slash-commands --add-dir /tmp/empty
  plugin_only         = (default plugin)       --add-dir /tmp/empty
  plugin_with_add_dir = (default plugin)       --add-dir REPO

Three lifts computed per eval:
  baseline -> plugin_only          = pure consultation lift
  plugin_only -> plugin_with_add_dir = pure filesystem access lift
  baseline -> plugin_with_add_dir  = total lift (the number iter-4 SHOULD have measured)

Eval scope: 4-eval subset chosen to span both lift mechanisms (2 consultation-
driven + 2 file-access-driven per iter-4):
  - eval-skill  (consultation)
  - sec-audit   (consultation)
  - lint-1      (file-access)
  - release-2   (file-access)

Optimization: reuses iter-4 transcripts for the 2 non-baseline configs (the
"without_skill" → "plugin_only" relabeling is bit-for-bit the same run). Only
the "baseline" config needs fresh transcript generation (4 runs ≈ 20 min).

Wall time: ~20 min for baseline generation + ~5 min for grading = 25 min.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path("/Users/felix/Documents/AutoPluginClaw/taches-principled-light")
WORKSPACE = REPO / "docs/principled/skill-evals/marketplace-routing-2026-06-22"
ITER7_DIR = WORKSPACE / "iteration-7"
ITER4_DIR = WORKSPACE / "iteration-4"
ITER3_ASSERTIONS = (WORKSPACE / "iteration-3") / "assertions"
ITER3_GRADER = (WORKSPACE / "iteration-3") / "scripts" / "grader.py"
EVALS_FILE = WORKSPACE / "evals/evals.json"
CLAUDE = "/Users/felix/.local/bin/claude"
CLAUDE_MODEL = "haiku"
TIMEOUT_S = 300
EMPTY_PROJECT = Path("/tmp/empty-claude-project")
DEFAULT_JUDGE_MODEL = "sonnet"
LIFT_THRESHOLD_PP = 5

# 4-eval subset, ordered for clarity in the output.
# (eval_id, lift_mechanism_in_iter4)
ITER7_EVALS = [
    ("eval-skill", "consultation"),
    ("sec-audit", "consultation"),
    ("lint-1", "file-access"),
    ("release-2", "file-access"),
]


def preflight() -> bool:
    """Preflight with --disable-slash-commands to confirm flag works."""
    print(f"[iter-7] preflight: {CLAUDE} --model {CLAUDE_MODEL} "
          f"--disable-slash-commands", flush=True)
    EMPTY_PROJECT.mkdir(parents=True, exist_ok=True)
    cmd = [CLAUDE, "--print", "--output-format", "stream-json",
           "--model", CLAUDE_MODEL, "--dangerously-skip-permissions",
           "--disable-slash-commands",
           "--add-dir", str(EMPTY_PROJECT)]
    try:
        r = subprocess.run(cmd, input="echo ok", capture_output=True,
                           text=True, timeout=60)
    except subprocess.TimeoutExpired:
        print("[iter-7] preflight FAIL: 60s timeout", file=sys.stderr,
              flush=True)
        return False
    result_line = ""
    for line in (r.stdout or "").splitlines():
        if '"type":"result"' in line:
            result_line = line
            break
    if not result_line:
        print("[iter-7] preflight FAIL: no result envelope in stream",
              file=sys.stderr, flush=True)
        return False
    is_error = '"is_error":true' in result_line
    api_err_status = any(p in result_line for p in
                         ["529", "Overloaded", '"api_error_status":5',
                          '"api_error_status":4'])
    if r.returncode != 0 or is_error or api_err_status:
        print(f"[iter-7] preflight FAIL: rc={r.returncode} "
              f"is_error={is_error} api_err={api_err_status}",
              file=sys.stderr, flush=True)
        print(result_line[:300], file=sys.stderr)
        return False
    print("[iter-7] preflight OK (--disable-slash-commands works)", flush=True)
    return True


def run_baseline(utterance: str, eval_dir: Path) -> dict:
    """Run the TRUE baseline: no plugin, no skills, no slash commands."""
    out_path = eval_dir / "baseline_skill.jsonl"
    log_path = eval_dir / "baseline_skill.log"
    cmd = [CLAUDE, "--print", "--output-format", "stream-json",
           "--model", CLAUDE_MODEL, "--add-dir", str(EMPTY_PROJECT),
           "--disable-slash-commands",
           "--dangerously-skip-permissions"]
    start = time.time()
    try:
        with open(out_path, "wb") as fb:
            r = subprocess.run(cmd, input=utterance.encode("utf-8"),
                               stdout=fb, stderr=subprocess.PIPE,
                               timeout=TIMEOUT_S, cwd=str(EMPTY_PROJECT))
        duration_ms = int((time.time() - start) * 1000)
        log_path.write_text(r.stderr.decode("utf-8", errors="replace"))
        status = "completed" if r.returncode == 0 else f"exit_{r.returncode}"
    except subprocess.TimeoutExpired:
        duration_ms = TIMEOUT_S * 1000
        log_path.write_text(f"TIMEOUT after {TIMEOUT_S}s\n")
        marker = eval_dir / "baseline_skill_timeout.json"
        marker.write_text(json.dumps({
            "status": "timeout", "timeout_s": TIMEOUT_S,
            "timestamp": time.time(),
        }))
        status = "truncated_timeout"
    text = out_path.read_text() if out_path.exists() else ""
    n_events = sum(1 for ln in text.splitlines() if ln.strip())
    return {"config": "baseline", "status": status,
            "duration_ms": duration_ms, "total_events": n_events}


def copy_iter4_transcripts(eval_id: str, dest_dir: Path) -> dict:
    """Copy iter-4 transcripts (without_skill → plugin_only, with_skill →
    plugin_with_add_dir) to the iter-7 eval dir."""
    src = ITER4_DIR / f"eval-{eval_id}"
    dest_dir.mkdir(parents=True, exist_ok=True)
    mapping = {
        "without_skill.jsonl": "plugin_only_skill.jsonl",
        "with_skill.jsonl": "plugin_with_add_dir_skill.jsonl",
    }
    copied = []
    for src_name, dst_name in mapping.items():
        src_path = src / src_name
        dst_path = dest_dir / dst_name
        if not src_path.exists():
            print(f"[iter-7] WARN: missing {src_path}", file=sys.stderr)
            continue
        shutil.copy2(src_path, dst_path)
        copied.append(dst_name)
    return {"copied": copied}


def grade_one(eval_id: str, iter7_config: str, transcript: Path,
              out_dir: Path, judge_model: str) -> dict | None:
    """Grade a single iter-7 config cell. Translates iter-7 config names
    (baseline, plugin_only, plugin_with_add_dir) to the grader's choices
    (without, with) since iter-3's grader.py is hardcoded to those values.
    After grading, renames the output to the iter-7 config name."""
    assertions_path = ITER3_ASSERTIONS / f"{eval_id}.json"
    if not assertions_path.exists():
        print(f"[iter-7] {eval_id}: no assertions at {assertions_path}",
              file=sys.stderr)
        return None
    if not transcript.exists() or transcript.stat().st_size == 0:
        print(f"[iter-7] {eval_id} {iter7_config}: empty/missing transcript",
              file=sys.stderr)
        return None
    # Translate iter-7 config → grader config
    grader_config = "with" if iter7_config == "plugin_with_add_dir" else "without"
    cmd = [sys.executable, str(ITER3_GRADER),
           "--assertions", str(assertions_path),
           "--transcript", str(transcript),
           "--eval-dir", str(out_dir),
           "--config", grader_config,
           "--judge-model", judge_model]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        print(f"[iter-7] {eval_id} {iter7_config}: grader TIMEOUT",
              file=sys.stderr)
        return None
    if r.returncode != 0:
        print(f"[iter-7] {eval_id} {iter7_config}: grader rc={r.returncode}",
              file=sys.stderr)
        print((r.stderr or "")[:300], file=sys.stderr)
        return None
    # Grader writes grading_<grader_config>_skill.json
    grader_out = out_dir / f"grading_{grader_config}_skill.json"
    # Rename to iter-7 config name and update internal config field
    iter7_out = out_dir / f"grading_{iter7_config}_skill.json"
    if grader_out.exists():
        data = json.loads(grader_out.read_text())
        data["config"] = iter7_config
        data["iter7_config_translation"] = {
            "iter7": iter7_config, "grader": grader_config,
        }
        iter7_out.write_text(json.dumps(data, indent=2))
        grader_out.unlink()  # remove the translated file
    return json.loads(iter7_out.read_text()) if iter7_out.exists() else None


def score(g: dict) -> dict:
    s = g["summary"]
    return {
        "overall_score": s["overall_score"],
        "instruction_following_score": s["instruction_following_score"],
        "goal_completion_score": s["goal_completion_score"],
        "passed": s["passed"], "failed": s["failed"],
        "unknown": s["unknown"], "total": s["total"],
    }


def compute_three_way_deltas(baseline_g: dict, plugin_only_g: dict,
                             plugin_with_add_dir_g: dict) -> dict:
    """Compute the three lifts per Yagubyan/CoEval/SkillRouter 2026 design."""
    s_b = baseline_g["summary"]
    s_po = plugin_only_g["summary"]
    s_pa = plugin_with_add_dir_g["summary"]

    def delta(a: dict, b: dict, key: str) -> float:
        return round(a[key] - b[key], 1)

    # Three lifts:
    # 1. baseline -> plugin_only        = pure consultation lift
    # 2. plugin_only -> plugin_with_add_dir = pure filesystem access lift
    # 3. baseline -> plugin_with_add_dir = total lift
    consult_lift = {
        "instruction_following_delta": delta(s_po, s_b, "instruction_following_score"),
        "goal_completion_delta": delta(s_po, s_b, "goal_completion_score"),
        "overall_delta": delta(s_po, s_b, "overall_score"),
    }
    fs_lift = {
        "instruction_following_delta": delta(s_pa, s_po, "instruction_following_score"),
        "goal_completion_delta": delta(s_pa, s_po, "goal_completion_score"),
        "overall_delta": delta(s_pa, s_po, "overall_score"),
    }
    total_lift = {
        "instruction_following_delta": delta(s_pa, s_b, "instruction_following_score"),
        "goal_completion_delta": delta(s_pa, s_b, "goal_completion_score"),
        "overall_delta": delta(s_pa, s_b, "overall_score"),
    }

    # Per-lift verdicts: same logic as iter-4 compute_deltas
    def verdict_for(d: dict) -> str:
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
            "consultation_lift": {
                **consult_lift,
                "verdict": verdict_for(consult_lift),
            },
            "filesystem_access_lift": {
                **fs_lift,
                "verdict": verdict_for(fs_lift),
            },
            "total_lift": {
                **total_lift,
                "verdict": verdict_for(total_lift),
            },
        },
    }


def _fmt_lift(d: dict, key: str) -> str:
    v = d.get(key)
    return f"{v:+.2f}" if isinstance(v, (int, float)) else "  N/A "


def _fmt_score(d: dict | None) -> str:
    if d is None:
        return " N/A "
    v = d.get("overall_score")
    return f"{v:.1f}" if isinstance(v, (int, float)) else " N/A "


def _fmt_delta(d: dict | None) -> str:
    if d is None:
        return "  N/A"
    v = d.get("overall_delta")
    return f"{v:+5.1f}" if isinstance(v, (int, float)) else "  N/A"


def main() -> int:
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--judge-model", default=DEFAULT_JUDGE_MODEL)
    p.add_argument("--skip-transcripts", action="store_true",
                   help="Skip baseline transcript generation (re-use existing)")
    args = p.parse_args()

    ITER7_DIR.mkdir(parents=True, exist_ok=True)
    EMPTY_PROJECT.mkdir(parents=True, exist_ok=True)

    # Load evals once; used in baseline generation and grading
    evals_all = json.loads(EVALS_FILE.read_text())["evals"]
    evals_by_id = {e["id"]: e for e in evals_all}

    print(f"[iter-7] 4-eval subset x 3 configs = 12 grading cells", flush=True)
    print(f"[iter-7] judge model: {args.judge_model}", flush=True)
    print(f"[iter-7] solver model: {CLAUDE_MODEL}", flush=True)
    print(f"[iter-7] baseline run timeout: {TIMEOUT_S}s", flush=True)
    print(f"[iter-7] baseline wall budget: ~{4*TIMEOUT_S//60} min worst case",
          flush=True)

    # Phase 0: preflight
    if not args.skip_transcripts and not preflight():
        print("[iter-7] abort: preflight failed", file=sys.stderr)
        return 3

    # Phase 1a: copy iter-4 transcripts (plugin_only + plugin_with_add_dir)
    print(f"\n[iter-7] phase 1a: copy iter-4 transcripts", flush=True)
    for eval_id, _ in ITER7_EVALS:
        ed = ITER7_DIR / f"eval-{eval_id}"
        info = copy_iter4_transcripts(eval_id, ed)
        print(f"  {eval_id}: copied {info['copied']}", flush=True)

    # Phase 1b: generate fresh baseline transcripts
    if not args.skip_transcripts:
        print(f"\n[iter-7] phase 1b: generate baseline transcripts "
              f"(--disable-slash-commands)", flush=True)
        for i, (eval_id, _) in enumerate(ITER7_EVALS, 1):
            ev = evals_by_id[eval_id]
            utterance = ev["utterance"]
            ed = ITER7_DIR / f"eval-{eval_id}"
            ed.mkdir(parents=True, exist_ok=True)
            print(f"\n[{i}/4] {eval_id} baseline", flush=True)
            print(f"  utterance: {utterance}", flush=True)
            m = run_baseline(utterance, ed)
            print(f"  baseline:     {m['status']} "
                  f"dur={m['duration_ms']}ms events={m['total_events']}",
                  flush=True)
    else:
        print("[iter-7] --skip-transcripts: reusing existing baseline NDJSON",
              flush=True)

    # Phase 2: grading
    print(f"\n[iter-7] phase 2: grading (4 evals x 3 configs = 12 cells)",
          flush=True)
    all_cmp = []
    for i, (eval_id, mechanism) in enumerate(ITER7_EVALS, 1):
        ed = ITER7_DIR / f"eval-{eval_id}"
        print(f"\n[{i}/4] grading {eval_id} (iter-4 mechanism: {mechanism})",
              flush=True)
        g_b = grade_one(eval_id, "baseline", ed / "baseline_skill.jsonl",
                        ed, args.judge_model)
        g_po = grade_one(eval_id, "plugin_only",
                         ed / "plugin_only_skill.jsonl",
                         ed, args.judge_model)
        g_pa = grade_one(eval_id, "plugin_with_add_dir",
                         ed / "plugin_with_add_dir_skill.jsonl",
                         ed, args.judge_model)
        for label, g in [("baseline", g_b), ("plugin_only", g_po),
                         ("plugin_with_add_dir", g_pa)]:
            if g:
                s = g["summary"]
                print(f"  {label:>20}: overall={s['overall_score']:5.1f} "
                      f"IF={s['instruction_following_score']:5.1f} "
                      f"GC={s['goal_completion_score']:5.1f}", flush=True)
        if not (g_b and g_po and g_pa):
            missing = [c for c, g in [("baseline", g_b), ("plugin_only", g_po),
                                       ("plugin_with_add_dir", g_pa)]
                       if g is None]
            print(f"  PARTIAL {eval_id}: missing {missing} (computing "
                  f"available lifts only)", file=sys.stderr, flush=True)
            # Compute partial deltas if we have at least 2 of 3
            available = [(c, g) for c, g in [("baseline", g_b),
                                              ("plugin_only", g_po),
                                              ("plugin_with_add_dir", g_pa)]
                          if g is not None]
            if len(available) < 2:
                print(f"  SKIP {eval_id} (need ≥2 configs, have {len(available)})",
                      file=sys.stderr)
                continue
            # Use whatever configs are available; missing fields default to None
            deltas = {
                "baseline": score(g_b) if g_b else None,
                "plugin_only": score(g_po) if g_po else None,
                "plugin_with_add_dir": score(g_pa) if g_pa else None,
                "lifts": {},
            }
            # Compute each lift if both endpoints are available
            lift_specs = [
                ("consultation_lift", "baseline", "plugin_only"),
                ("filesystem_access_lift", "plugin_only", "plugin_with_add_dir"),
                ("total_lift", "baseline", "plugin_with_add_dir"),
            ]
            for lift_name, lo, hi in lift_specs:
                lo_g = {"baseline": g_b, "plugin_only": g_po,
                        "plugin_with_add_dir": g_pa}[lo]
                hi_g = {"baseline": g_b, "plugin_only": g_po,
                        "plugin_with_add_dir": g_pa}[hi]
                if lo_g is None or hi_g is None:
                    deltas["lifts"][lift_name] = None
                else:
                    s_lo = lo_g["summary"]
                    s_hi = hi_g["summary"]
                    d = {
                        "instruction_following_delta": round(
                            s_hi["instruction_following_score"]
                            - s_lo["instruction_following_score"], 1),
                        "goal_completion_delta": round(
                            s_hi["goal_completion_score"]
                            - s_lo["goal_completion_score"], 1),
                        "overall_delta": round(
                            s_hi["overall_score"] - s_lo["overall_score"], 1),
                    }
                    if abs(d["overall_delta"]) <= LIFT_THRESHOLD_PP:
                        d["verdict"] = "skill_neutral"
                    elif d["overall_delta"] < -LIFT_THRESHOLD_PP:
                        d["verdict"] = "skill_hurts"
                    elif (d["instruction_following_delta"] <= 1
                          and d["goal_completion_delta"] <= 1):
                        d["verdict"] = "skill_redundant"
                    else:
                        d["verdict"] = ("skill_lifts_quality"
                                        if d["overall_delta"] > 0
                                        else "skill_neutral")
                    deltas["lifts"][lift_name] = d
        else:
            deltas = compute_three_way_deltas(g_b, g_po, g_pa)
        cmp_entry = {
            "eval_id": eval_id,
            "iter4_mechanism": mechanism,
            "expected_skill": evals_by_id[eval_id]["expected"],
            **deltas,
        }
        (ed / "comparison.json").write_text(json.dumps(cmp_entry, indent=2))
        lifts = deltas["lifts"]
        for lift_name in ["consultation_lift", "filesystem_access_lift",
                          "total_lift"]:
            d = lifts.get(lift_name)
            if d is None:
                print(f"  {lift_name}: NOT COMPUTED (missing config)",
                      flush=True)
            else:
                print(f"  {lift_name}: "
                      f"IF={d['instruction_following_delta']:+5.1f} "
                      f"GC={d['goal_completion_delta']:+5.1f} "
                      f"overall={d['overall_delta']:+5.1f} "
                      f"→ {d['verdict']}", flush=True)
        all_cmp.append(cmp_entry)

    if not all_cmp:
        print("[iter-7] no comparisons produced", file=sys.stderr)
        return 1

    # Phase 3: aggregate
    n = len(all_cmp)

    def mean_of(field: str, lift_name: str) -> float | None:
        vals = [c["lifts"][lift_name][field] for c in all_cmp
                if c["lifts"].get(lift_name) is not None
                and c["lifts"][lift_name].get(field) is not None]
        if not vals:
            return None
        return round(sum(vals) / len(vals), 2)

    summary = {
        "consultation_lift": {
            "mean_instruction_following_delta": mean_of(
                "instruction_following_delta", "consultation_lift"),
            "mean_goal_completion_delta": mean_of(
                "goal_completion_delta", "consultation_lift"),
            "mean_overall_delta": mean_of("overall_delta", "consultation_lift"),
        },
        "filesystem_access_lift": {
            "mean_instruction_following_delta": mean_of(
                "instruction_following_delta", "filesystem_access_lift"),
            "mean_goal_completion_delta": mean_of(
                "goal_completion_delta", "filesystem_access_lift"),
            "mean_overall_delta": mean_of(
                "overall_delta", "filesystem_access_lift"),
        },
        "total_lift": {
            "mean_instruction_following_delta": mean_of(
                "instruction_following_delta", "total_lift"),
            "mean_goal_completion_delta": mean_of(
                "goal_completion_delta", "total_lift"),
            "mean_overall_delta": mean_of("overall_delta", "total_lift"),
        },
    }

    # Per-mechanism breakdown
    per_mech_consult: dict[str, list[float]] = {}
    per_mech_total: dict[str, list[float]] = {}
    for c in all_cmp:
        m = c["iter4_mechanism"]
        cl = c["lifts"].get("consultation_lift")
        if cl is not None and cl.get("overall_delta") is not None:
            per_mech_consult.setdefault(m, []).append(cl["overall_delta"])
        tl = c["lifts"].get("total_lift")
        if tl is not None and tl.get("overall_delta") is not None:
            per_mech_total.setdefault(m, []).append(tl["overall_delta"])

    per_mech_consult_mean = {m: round(sum(v)/len(v), 2)
                             for m, v in per_mech_consult.items()}
    per_mech_total_mean = {m: round(sum(v)/len(v), 2)
                           for m, v in per_mech_total.items()}

    # Verdict counts (skip None lifts)
    consult_verdicts: dict[str, int] = {}
    fs_verdicts: dict[str, int] = {}
    total_verdicts: dict[str, int] = {}
    for c in all_cmp:
        for kind, vdicts in [("consultation_lift", consult_verdicts),
                             ("filesystem_access_lift", fs_verdicts),
                             ("total_lift", total_verdicts)]:
            d = c["lifts"].get(kind)
            if d is None or d.get("verdict") is None:
                continue
            v = d["verdict"]
            vdicts[v] = vdicts.get(v, 0) + 1

    bench = {
        "iteration": 7, "phase": "A",
        "scope": f"{n} of {len(ITER7_EVALS)} evals (4-eval subset)",
        "judge_model": args.judge_model,
        "solver_model": CLAUDE_MODEL,
        "cache_state": "fresh (cleared 2026-06-23)",
        "harness_design": {
            "configs": {
                "baseline": "--disable-slash-commands --add-dir /tmp/empty",
                "plugin_only": "(default plugin) --add-dir /tmp/empty",
                "plugin_with_add_dir": "(default plugin) --add-dir REPO",
            },
            "rationale": "iter-4 baseline contamination finding: --add-dir "
                         "only controls filesystem access, not plugin auto-load. "
                         "--disable-slash-commands gives a true no-plugin baseline.",
        },
        "results": all_cmp,
        "summary": {
            "total_evals": n,
            **summary,
            "verdict_distribution": {
                "consultation_lift": consult_verdicts,
                "filesystem_access_lift": fs_verdicts,
                "total_lift": total_verdicts,
            },
            "per_mechanism_consult_lift": per_mech_consult_mean,
            "per_mechanism_total_lift": per_mech_total_mean,
        },
        "iter4_reference": {
            "mean_overall_delta": 4.94,
            "verdict_distribution": {
                "skill_lifts_quality": 5, "skill_neutral": 13,
                "skill_hurts": 0},
            "caveat": "iter-4 measured FILESYSTEM ACCESS lift only "
                      "(plugin_only -> plugin_with_add_dir), NOT the total "
                      "lift vs no-plugin baseline.",
        },
        "notes": (
            "Phase A: 3-config harness to resolve the 2026-06-23 baseline "
            "contamination finding. Reuses iter-4 transcripts for the "
            "2 non-baseline configs (the relabeling is bit-for-bit the same). "
            "Generates fresh baseline runs only (4 runs ≈ 20 min)."),
    }
    (ITER7_DIR / "benchmark.json").write_text(json.dumps(bench, indent=2))

    # Markdown summary
    md = [
        "# Iteration 7 Phase A — Three-Config Lift Disambiguation (N=4)",
        "",
        "## Configuration",
        f"- Judge model: `{args.judge_model}`",
        f"- Solver model: `{CLAUDE_MODEL}`",
        f"- Cache state: fresh (cleared 2026-06-23)",
        f"- Lift threshold: ±{LIFT_THRESHOLD_PP}pp for skill_neutral",
        "",
        "## Three Configs",
        "- `baseline`: `--disable-slash-commands --add-dir /tmp/empty` "
        "(no plugin)",
        "- `plugin_only`: default plugin loading, `--add-dir /tmp/empty` "
        "(plugin + slash commands, no filesystem)",
        "- `plugin_with_add_dir`: default plugin loading, `--add-dir REPO` "
        "(plugin + filesystem)",
        "",
        "## Three Lifts",
    ]
    for lift_name, lo, hi in [("consultation_lift", "baseline", "plugin_only"),
                              ("filesystem_access_lift", "plugin_only",
                               "plugin_with_add_dir"),
                              ("total_lift", "baseline", "plugin_with_add_dir")]:
        d = summary[lift_name]
        md.append(f"- **{lift_name}** ({lo} → {hi}): "
                  f"IF={_fmt_lift(d, 'mean_instruction_following_delta')} "
                  f"GC={_fmt_lift(d, 'mean_goal_completion_delta')} "
                  f"overall={_fmt_lift(d, 'mean_overall_delta')}")
    md.extend([
        "",
        "### iter-4 reference (filesystem access lift only): +4.94pp",
        "",
        "## Per-eval Results",
        "",
        "| Eval | iter-4 mech | baseline | plugin_only | plugin_with_add_dir | "
        "Consult Δ | FS Δ | Total Δ |",
        "|------|-------------|---------:|------------:|--------------------:|"
        "---------:|-----:|--------:|",
    ])
    for c in all_cmp:
        b = c.get("baseline")
        po = c.get("plugin_only")
        pa = c.get("plugin_with_add_dir")
        cl = c["lifts"].get("consultation_lift")
        fl = c["lifts"].get("filesystem_access_lift")
        tl = c["lifts"].get("total_lift")
        md.append(f"| {c['eval_id']} | {c['iter4_mechanism']} | "
                  f"{_fmt_score(b)} | {_fmt_score(po)} | {_fmt_score(pa)} | "
                  f"{_fmt_delta(cl)} | {_fmt_delta(fl)} | {_fmt_delta(tl)} |")
    md.extend([
        "",
        "## Per-mechanism breakdown (consultation_lift)",
        "",
        "| iter-4 mechanism | mean overall Δ | n |",
        "|------------------|---------------:|--:|",
    ])
    for m, lift in per_mech_consult_mean.items():
        md.append(f"| {m} | {lift:+.2f} | {len(per_mech_consult[m])} |")
    md.extend([
        "",
        "## Per-mechanism breakdown (total_lift)",
        "",
        "| iter-4 mechanism | mean overall Δ | n |",
        "|------------------|---------------:|--:|",
    ])
    for m, lift in per_mech_total_mean.items():
        md.append(f"| {m} | {lift:+.2f} | {len(per_mech_total[m])} |")
    md.extend([
        "",
        "## Verdict distribution",
        "",
        f"- consultation_lift: {consult_verdicts}",
        f"- filesystem_access_lift: {fs_verdicts}",
        f"- total_lift: {total_verdicts}",
        "",
        "## Notes",
        "",
        "- This is N=4 (4-eval subset). Below Yagubyan 2026's N=11 reliability "
        "threshold; do not interpret magnitude as effect size.",
        "- 4 transcripts reused from iter-4 (plugin_only + plugin_with_add_dir).",
        "- 4 transcripts freshly generated for baseline (--disable-slash-commands).",
        "- The total_lift is what iter-4 SHOULD have measured; it is ≥ "
        "the iter-4 +4.94pp (the iter-4 number is a lower bound on total_lift).",
    ])
    (ITER7_DIR / "benchmark.md").write_text("\n".join(md))

    print(f"\n[iter-7] done. {n}/{len(ITER7_EVALS)} evals graded.")
    print(f"[iter-7] consultation_lift: "
          f"{_fmt_lift(summary['consultation_lift'], 'mean_overall_delta')}")
    print(f"[iter-7] filesystem_access_lift: "
          f"{_fmt_lift(summary['filesystem_access_lift'], 'mean_overall_delta')}")
    print(f"[iter-7] total_lift: "
          f"{_fmt_lift(summary['total_lift'], 'mean_overall_delta')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
