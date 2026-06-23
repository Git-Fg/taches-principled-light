#!/usr/bin/env python3
"""Iteration-4 Phase A orchestrator.

Re-runs iter-2's transcript generation with a FRESH plugin cache (the
v2.0.0 cache that contaminated iter-2/3 was cleared on 2026-06-23),
then applies iter-3's assertion-based grader to the new transcripts.
This produces a direct iter-3 vs iter-4 comparison answering: "Does the
+8.69pp mean lift from iter-3 hold when the cache is fresh?"

Pipeline:
  1. preflight (proxy reachable on haiku)
  2. for each eval in evals.json:
       - run claude with --add-dir REPO (with_skill)
       - run claude with --add-dir /tmp/empty-claude-project (without_skill)
       - save NDJSON transcripts to iteration-4/eval-<id>/{with,without}_skill.jsonl
       - on timeout: write timeout.json marker (no empty dir)
  3. for each eval: invoke iter-3 grader.py on each transcript
  4. compute deltas (Gorinova-style IF + GC + overall) per iter-3
  5. aggregate into iteration-4/benchmark.{json,md}

Differences from iter-3:
  - transcripts regenerated against fresh cache (writes to iteration-4/)
  - iter-3 grader reused (assertion bug fixed in commit b45c40a)
  - timeout.json marker prevents ambiguous empty-dir state
  - heterogeneous judge (sonnet over haiku solver) — same as iter-3 default
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path("/Users/felix/Documents/AutoPluginClaw/taches-principled-light")
WORKSPACE = REPO / "docs/principled/skill-evals/marketplace-routing-2026-06-22"
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


def preflight() -> bool:
    print(f"[iter-4] preflight: {CLAUDE} --model {CLAUDE_MODEL}", flush=True)
    EMPTY_PROJECT.mkdir(parents=True, exist_ok=True)
    cmd = [CLAUDE, "--print", "--output-format", "stream-json",
           "--model", CLAUDE_MODEL, "--dangerously-skip-permissions",
           "--add-dir", str(EMPTY_PROJECT)]
    try:
        r = subprocess.run(cmd, input="echo ok", capture_output=True,
                           text=True, timeout=60)
    except subprocess.TimeoutExpired:
        print("[iter-4] preflight FAIL: 60s timeout", file=sys.stderr, flush=True)
        return False
    # Look only at the final result envelope, not the init/system events
    # which contain tool lists and MCP status that falsely match error
    # patterns (e.g. 'chrome-mcp-server failed' is normal).
    result_line = ""
    for line in (r.stdout or "").splitlines():
        if '"type":"result"' in line:
            result_line = line
            break
    if not result_line:
        print("[iter-4] preflight FAIL: no result envelope in stream",
              file=sys.stderr, flush=True)
        return False
    is_error = '"is_error":true' in result_line
    api_err_status = any(p in result_line for p in
                         ["529", "Overloaded", '"api_error_status":5',
                          '"api_error_status":4'])
    if r.returncode != 0 or is_error or api_err_status:
        print(f"[iter-4] preflight FAIL: rc={r.returncode} "
              f"is_error={is_error} api_err={api_err_status}",
              file=sys.stderr, flush=True)
        print(result_line[:300], file=sys.stderr)
        return False
    print("[iter-4] preflight OK", flush=True)
    return True


def run_one(utterance: str, with_skill: bool, eval_dir: Path) -> dict:
    cfg = "with" if with_skill else "without"
    add_dir = str(REPO) if with_skill else str(EMPTY_PROJECT)
    if not with_skill:
        EMPTY_PROJECT.mkdir(parents=True, exist_ok=True)
    out_path = eval_dir / f"{cfg}_skill.jsonl"
    log_path = eval_dir / f"{cfg}_skill.log"
    cmd = [CLAUDE, "--print", "--output-format", "stream-json",
           "--model", CLAUDE_MODEL, "--add-dir", add_dir,
           "--dangerously-skip-permissions"]
    start = time.time()
    try:
        with open(out_path, "wb") as fb:
            r = subprocess.run(cmd, input=utterance.encode("utf-8"),
                               stdout=fb, stderr=subprocess.PIPE,
                               timeout=TIMEOUT_S, cwd=add_dir)
        duration_ms = int((time.time() - start) * 1000)
        log_path.write_text(r.stderr.decode("utf-8", errors="replace"))
        status = "completed" if r.returncode == 0 else f"exit_{r.returncode}"
    except subprocess.TimeoutExpired:
        duration_ms = TIMEOUT_S * 1000
        log_path.write_text(f"TIMEOUT after {TIMEOUT_S}s\n")
        marker = eval_dir / f"{cfg}_skill_timeout.json"
        marker.write_text(json.dumps({
            "status": "timeout", "timeout_s": TIMEOUT_S,
            "timestamp": time.time(),
        }))
        status = "truncated_timeout"
    text = out_path.read_text() if out_path.exists() else ""
    n_events = sum(1 for ln in text.splitlines() if ln.strip())
    return {"config": cfg, "status": status, "duration_ms": duration_ms,
            "total_events": n_events}


def grade_one(eval_id: str, config: str, transcript: Path,
              out_dir: Path, judge_model: str) -> dict | None:
    assertions_path = ITER3_ASSERTIONS / f"{eval_id}.json"
    if not assertions_path.exists():
        print(f"[iter-4] {eval_id}: no assertions at {assertions_path}",
              file=sys.stderr)
        return None
    if not transcript.exists() or transcript.stat().st_size == 0:
        print(f"[iter-4] {eval_id} {config}: empty/missing transcript",
              file=sys.stderr)
        return None
    cmd = [sys.executable, str(ITER3_GRADER),
           "--assertions", str(assertions_path),
           "--transcript", str(transcript),
           "--eval-dir", str(out_dir),
           "--config", config,
           "--judge-model", judge_model]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        print(f"[iter-4] {eval_id} {config}: grader TIMEOUT", file=sys.stderr)
        return None
    if r.returncode != 0:
        print(f"[iter-4] {eval_id} {config}: grader rc={r.returncode}",
              file=sys.stderr)
        print((r.stderr or "")[:300], file=sys.stderr)
        return None
    out = out_dir / f"grading_{config}_skill.json"
    return json.loads(out.read_text()) if out.exists() else None


def compute_deltas(with_g: dict, without_g: dict) -> dict:
    s_w = with_g["summary"]
    s_wo = without_g["summary"]
    if_d = round(s_w["instruction_following_score"]
                 - s_wo["instruction_following_score"], 1)
    gc_d = round(s_w["goal_completion_score"]
                 - s_wo["goal_completion_score"], 1)
    overall_d = round(s_w["overall_score"] - s_wo["overall_score"], 1)
    if abs(overall_d) <= LIFT_THRESHOLD_PP:
        verdict = "skill_neutral"
    elif overall_d < -LIFT_THRESHOLD_PP:
        verdict = "skill_hurts"
    elif if_d <= 1 and gc_d <= 1:
        verdict = "skill_redundant"
    else:
        verdict = "skill_lifts_quality" if overall_d > 0 else "skill_neutral"
    return {
        "with_skill": {k: s_w[k] for k in
                       ("overall_score", "instruction_following_score",
                        "goal_completion_score", "passed", "failed",
                        "unknown", "total")},
        "without_skill": {k: s_wo[k] for k in
                          ("overall_score", "instruction_following_score",
                           "goal_completion_score", "passed", "failed",
                           "unknown", "total")},
        "delta": {"instruction_following_delta": if_d,
                  "goal_completion_delta": gc_d,
                  "overall_delta": overall_d},
        "verdict": verdict,
    }


def main() -> int:
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--judge-model", default=DEFAULT_JUDGE_MODEL)
    p.add_argument("--evals", nargs="*", default=None,
                   help="Subset of eval IDs; default = all 17")
    p.add_argument("--skip-transcripts", action="store_true",
                   help="Skip transcript generation (re-use existing)")
    args = p.parse_args()

    ITER4_DIR.mkdir(parents=True, exist_ok=True)
    EMPTY_PROJECT.mkdir(parents=True, exist_ok=True)

    evals = json.loads(EVALS_FILE.read_text())["evals"]
    if args.evals:
        ids = set(args.evals)
        evals = [e for e in evals if e["id"] in ids]
    n = len(evals)
    print(f"[iter-4] {n} evals x 2 configs = {n*2} transcript runs", flush=True)
    print(f"[iter-4] judge model: {args.judge_model}", flush=True)
    print(f"[iter-4] timeout per run: {TIMEOUT_S}s", flush=True)
    print(f"[iter-4] wall budget: ~{n*2*TIMEOUT_S//60} min worst case",
          flush=True)

    if not args.skip_transcripts and not preflight():
        print("[iter-4] abort: preflight failed", file=sys.stderr)
        return 3

    # Phase 1: transcript generation
    if not args.skip_transcripts:
        for i, ev in enumerate(evals, 1):
            eval_id = ev["id"]
            utterance = ev["utterance"]
            ed = ITER4_DIR / f"eval-{eval_id}"
            ed.mkdir(parents=True, exist_ok=True)
            print(f"\n[{i}/{n}] {eval_id} (expected={ev['expected']})",
                  flush=True)
            print(f"  utterance: {utterance}", flush=True)
            m_w = run_one(utterance, with_skill=True, eval_dir=ed)
            print(f"  with-skill:    {m_w['status']} "
                  f"dur={m_w['duration_ms']}ms events={m_w['total_events']}",
                  flush=True)
            m_wo = run_one(utterance, with_skill=False, eval_dir=ed)
            print(f"  without-skill: {m_wo['status']} "
                  f"dur={m_wo['duration_ms']}ms events={m_wo['total_events']}",
                  flush=True)
            (ed / "transcript_metadata.json").write_text(json.dumps({
                "eval_id": eval_id, "with_skill": m_w,
                "without_skill": m_wo}, indent=2))
    else:
        print("[iter-4] --skip-transcripts: reusing existing NDJSON",
              flush=True)

    # Phase 2: grading
    print(f"\n[iter-4] grading phase ({n} evals x 2 configs = {n*2} calls)",
          flush=True)
    all_cmp = []
    for i, ev in enumerate(evals, 1):
        eval_id = ev["id"]
        ed = ITER4_DIR / f"eval-{eval_id}"
        print(f"\n[{i}/{n}] grading {eval_id}", flush=True)
        g_w = grade_one(eval_id, "with", ed / "with_skill.jsonl",
                        ed, args.judge_model)
        if g_w:
            s = g_w["summary"]
            print(f"  with-skill:    overall={s['overall_score']} "
                  f"IF={s['instruction_following_score']} "
                  f"GC={s['goal_completion_score']}", flush=True)
        g_wo = grade_one(eval_id, "without", ed / "without_skill.jsonl",
                         ed, args.judge_model)
        if g_wo:
            s = g_wo["summary"]
            print(f"  without-skill: overall={s['overall_score']} "
                  f"IF={s['instruction_following_score']} "
                  f"GC={s['goal_completion_score']}", flush=True)
        if not (g_w and g_wo):
            print(f"  SKIP {eval_id} (missing grading)", file=sys.stderr)
            continue
        deltas = compute_deltas(g_w, g_wo)
        cmp_entry = {
            "eval_id": eval_id, "utterance": ev["utterance"],
            "expected_skill": ev["expected"],
            "category_class": ev.get("category", "?"), **deltas,
        }
        (ed / "comparison.json").write_text(json.dumps(cmp_entry, indent=2))
        d = deltas["delta"]
        print(f"  delta: IF={d['instruction_following_delta']:+5.1f} "
              f"GC={d['goal_completion_delta']:+5.1f} "
              f"overall={d['overall_delta']:+5.1f} → {deltas['verdict']}",
              flush=True)
        all_cmp.append(cmp_entry)

    if not all_cmp:
        print("[iter-4] no comparisons produced", file=sys.stderr)
        return 1

    # Phase 3: aggregate
    n_done = len(all_cmp)
    mean_if = round(sum(c["delta"]["instruction_following_delta"]
                        for c in all_cmp) / n_done, 2)
    mean_gc = round(sum(c["delta"]["goal_completion_delta"]
                        for c in all_cmp) / n_done, 2)
    mean_ov = round(sum(c["delta"]["overall_delta"]
                        for c in all_cmp) / n_done, 2)
    verdicts: dict[str, int] = {}
    for c in all_cmp:
        verdicts[c["verdict"]] = verdicts.get(c["verdict"], 0) + 1
    per_skill: dict[str, list[float]] = {}
    for c in all_cmp:
        per_skill.setdefault(c["expected_skill"], []).append(
            c["delta"]["overall_delta"])
    per_skill_mean = {s: round(sum(v)/len(v), 2) for s, v in per_skill.items()}

    bench = {
        "iteration": 4, "phase": "A",
        "scope": f"{n_done} of {n} evals",
        "judge_model": args.judge_model,
        "solver_model": CLAUDE_MODEL,
        "cache_state": "fresh (cleared 2026-06-23, smoke test passed)",
        "results": all_cmp,
        "summary": {
            "total_evals": n_done,
            "mean_instruction_following_delta": mean_if,
            "mean_goal_completion_delta": mean_gc,
            "mean_overall_delta": mean_ov,
            "verdict_distribution": verdicts,
            "per_skill_lift": per_skill_mean,
        },
        "iter3_reference": {
            "mean_overall_delta": 8.69,
            "verdict_distribution": {
                "skill_lifts_quality": 6, "skill_neutral": 11,
                "skill_hurts": 0},
            "caveat": "iter-3 was contaminated by stale v2.0.0 plugin cache",
        },
        "notes": (
            "Phase A: cache-refreshed re-run of iter-3 with heterogeneous "
            "judge (sonnet over haiku solver). Transcripts regenerated "
            f"against fresh cache; iter-3 grader.py reused (commit b45c40a "
            "consultation fix)."),
    }
    (ITER4_DIR / "benchmark.json").write_text(json.dumps(bench, indent=2))

    md = [
        f"# Iteration 4 Phase A — Cache-Refreshed Re-Run (N={n_done})",
        "",
        "## Configuration",
        f"- Judge model: `{args.judge_model}`",
        f"- Solver model: `{CLAUDE_MODEL}`",
        f"- Cache state: fresh (cleared 2026-06-23)",
        f"- Lift threshold: ±{LIFT_THRESHOLD_PP}pp for skill_neutral",
        "",
        "## Summary",
        f"- Evals graded: {n_done}/{n}",
        f"- Mean IF delta: {mean_if:+.2f}",
        f"- Mean GC delta: {mean_gc:+.2f}",
        f"- Mean overall delta: {mean_ov:+.2f}",
        f"- iter-3 reference: +8.69pp mean overall delta",
        "",
        "### Verdict distribution",
    ]
    for v, c in sorted(verdicts.items(), key=lambda x: -x[1]):
        md.append(f"- `{v}`: {c}/{n_done}")
    md.extend([
        "", "### Per-skill mean overall delta", "",
        "| Skill | Mean Δ | Evals |",
        "|-------|-------:|------:|",
    ])
    for s, lift in sorted(per_skill_mean.items(), key=lambda x: -x[1]):
        md.append(f"| {s} | {lift:+.2f} | {len(per_skill[s])} |")
    md.extend([
        "", "## Per-eval results", "",
        "| Eval | Expected | IF Δ | GC Δ | Overall Δ | Verdict |",
        "|------|----------|-----:|-----:|----------:|---------|",
    ])
    for c in all_cmp:
        d = c["delta"]
        md.append(f"| {c['eval_id']} | {c['expected_skill']} | "
                  f"{d['instruction_following_delta']:+5.1f} | "
                  f"{d['goal_completion_delta']:+5.1f} | "
                  f"{d['overall_delta']:+5.1f} | {c['verdict']} |")
    md.append("")
    (ITER4_DIR / "benchmark.md").write_text("\n".join(md))

    print(f"\n[iter-4] done. {n_done}/{n} evals graded.")
    print(f"[iter-4] mean overall delta: {mean_ov:+.2f} "
          f"(iter-3 ref: +8.69)")
    print(f"[iter-4] verdicts: {verdicts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
