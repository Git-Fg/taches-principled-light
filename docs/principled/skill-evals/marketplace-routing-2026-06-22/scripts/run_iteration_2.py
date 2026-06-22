#!/usr/bin/env python3
"""Iteration-2: full N=18 behavioral eval runner.

For each eval in evals.json, runs the with-skill and without-skill
configurations via `claude --print --output-format stream-json` and
captures the NDJSON transcript. Parses each transcript for:
  - SKILL.md read tool_use events
  - Skill tool invocations
  - final text length
  - total event count

Writes per-eval behavioral_comparison.json and aggregates into
benchmark.json + benchmark.md at the end.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path("/Users/felix/Documents/AutoPluginClaw/taches-principled-light")
SKILLS_DIR = REPO / "skills"
WORKSPACE = REPO / "docs/principled/skill-evals/marketplace-routing-2026-06-22"
ITER_DIR = WORKSPACE / "iteration-2"
EVALS_FILE = WORKSPACE / "evals/evals.json"
CLAUDE = "/Users/felix/.local/bin/claude"
TIMEOUT_S = 180
EMPTY_PROJECT = Path("/tmp/empty-claude-project")


def parse_events(text: str) -> list[dict]:
    """Parse NDJSON stream into list of events."""
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return out


def extract_skill_md_reads(events: list[dict]) -> list[str]:
    """Find all Read tool_use calls on SKILL.md files."""
    out = []
    for ev in events:
        if ev.get("type") != "assistant":
            continue
        content = ev.get("message", {}).get("content", [])
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use" and block.get("name") == "Read":
                fp = block.get("input", {}).get("file_path", "")
                if fp and "SKILL.md" in fp:
                    out.append(fp)
    return out


def extract_skill_tool_invocations(events: list[dict]) -> list[str]:
    """Find all Skill tool invocations (anywhere in the structure)."""
    out = []
    for ev in events:
        if ev.get("type") != "assistant":
            continue
        content = ev.get("message", {}).get("content", [])
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use" and block.get("name") == "Skill":
                skill = block.get("input", {}).get("skill") or block.get("skill", "")
                if skill:
                    out.append(skill)
    return out


def run_one(utterance: str, with_skill: bool, eval_dir: Path) -> dict:
    """Run one eval configuration. Returns parsed metrics."""
    cfg = "with" if with_skill else "without"
    out_path = eval_dir / f"{cfg}_skill.jsonl"
    log_path = eval_dir / f"{cfg}_skill.log"

    add_dir = str(REPO) if with_skill else str(EMPTY_PROJECT)
    cmd = [
        CLAUDE, "--print",
        "--output-format", "stream-json",
        "--add-dir", add_dir,
        "--dangerously-skip-permissions",
        utterance,
    ]
    start = time.time()
    try:
        with open(out_path, "w") as f:
            result = subprocess.run(
                cmd,
                stdout=f, stderr=subprocess.PIPE,
                timeout=TIMEOUT_S, cwd=add_dir,
            )
        duration_ms = int((time.time() - start) * 1000)
        log_path.write_text(result.stderr.decode("utf-8", errors="replace"))
        status = "completed" if result.returncode == 0 else f"exit_{result.returncode}"
    except subprocess.TimeoutExpired:
        duration_ms = int(TIMEOUT_S * 1000)
        log_path.write_text(f"TIMEOUT after {TIMEOUT_S}s\n")
        status = "truncated_timeout"

    text = out_path.read_text() if out_path.exists() else ""
    events = parse_events(text)
    reads = extract_skill_md_reads(events)
    tools = extract_skill_tool_invocations(events)
    return {
        "config": cfg,
        "status": status,
        "duration_ms": duration_ms,
        "total_events": len(events),
        "skill_tool_invocations": tools,
        "skill_md_reads": reads,
        "marketplace_skill_md_reads": [
            p for p in reads if str(SKILLS_DIR) in p
        ],
    }


def main() -> int:
    ITER_DIR.mkdir(parents=True, exist_ok=True)
    evals = json.loads(EVALS_FILE.read_text())["evals"]
    print(f"[iter-2] running {len(evals)} evals x 2 configs = {len(evals) * 2} runs")
    print(f"[iter-2] timeout per run: {TIMEOUT_S}s, total wall budget ~{len(evals) * 2 * TIMEOUT_S // 60} min")
    print(f"[iter-2] workspace: {ITER_DIR}")

    all_results = []
    for i, ev in enumerate(evals, 1):
        eval_id = ev["id"]
        utterance = ev["utterance"]
        eval_dir = ITER_DIR / f"eval-{eval_id}"
        eval_dir.mkdir(parents=True, exist_ok=True)
        (eval_dir / "with_skill.jsonl").write_text("")
        (eval_dir / "without_skill.jsonl").write_text("")
        print(f"\n[{i}/{len(evals)}] {eval_id} (expected={ev['expected']})")
        print(f"  utterance: {utterance}")
        with_metrics = run_one(utterance, with_skill=True, eval_dir=eval_dir)
        print(f"  with-skill: {with_metrics['status']} dur={with_metrics['duration_ms']}ms "
              f"events={with_metrics['total_events']} reads={len(with_metrics['marketplace_skill_md_reads'])}")
        without_metrics = run_one(utterance, with_skill=False, eval_dir=eval_dir)
        print(f"  without-skill: {without_metrics['status']} dur={without_metrics['duration_ms']}ms "
              f"events={without_metrics['total_events']} reads={len(without_metrics['marketplace_skill_md_reads'])}")

        comparison = {
            "eval_id": eval_id,
            "utterance": utterance,
            "expected_skill": ev["expected"],
            "with_skill": with_metrics,
            "without_skill": without_metrics,
            "delta": {
                "marketplace_skill_md_reads_added": (
                    len(with_metrics["marketplace_skill_md_reads"])
                    - len(without_metrics["marketplace_skill_md_reads"])
                ),
            },
            "material_difference": (
                len(with_metrics["marketplace_skill_md_reads"])
                != len(without_metrics["marketplace_skill_md_reads"])
            ),
        }
        (eval_dir / "behavioral_comparison.json").write_text(
            json.dumps(comparison, indent=2)
        )
        all_results.append(comparison)

    n_total = len(all_results)
    n_material = sum(1 for r in all_results if r["material_difference"])
    sum_with = sum(len(r["with_skill"]["marketplace_skill_md_reads"]) for r in all_results)
    sum_without = sum(len(r["without_skill"]["marketplace_skill_md_reads"]) for r in all_results)
    benchmark = {
        "iteration": 2,
        "scope": f"full ({n_total} of 18 evals)",
        "runtime": "claude-code CLI",
        "timeout_per_run_s": TIMEOUT_S,
        "results": [
            {
                "eval_id": r["eval_id"],
                "expected_skill": r["expected_skill"],
                "with_skill_score": len(r["with_skill"]["marketplace_skill_md_reads"]),
                "without_skill_score": len(r["without_skill"]["marketplace_skill_md_reads"]),
                "delta": r["delta"]["marketplace_skill_md_reads_added"],
                "verdict": "material_difference" if r["material_difference"] else "no_difference",
                "details": f"docs/.../iteration-2/eval-{r['eval_id']}/behavioral_comparison.json",
            }
            for r in all_results
        ],
        "summary": {
            "total_evals": n_total,
            "n_material_difference": n_material,
            "n_no_difference": n_total - n_material,
            "with_skill_total_signals": sum_with,
            "without_skill_total_signals": sum_without,
            "with_skill_mean_per_eval": round(sum_with / n_total, 2) if n_total else 0,
            "without_skill_mean_per_eval": round(sum_without / n_total, 2) if n_total else 0,
        },
        "notes": (
            "Iteration 2 scales the pilot to full N=18 with 180s timeout. "
            "Signal: marketplace SKILL.md read counts. Limitation: read-counting is "
            "a necessary-but-not-sufficient proxy for skill application per the "
            "Tessl framework (arxiv 2606.17819v1). Iteration 3 would add "
            "assertion-based grading (per Anthropic skill-creator's executor/grader/"
            "comparator/analyzer pattern)."
        ),
    }
    (ITER_DIR / "benchmark.json").write_text(json.dumps(benchmark, indent=2))

    md = [
        f"# Iteration 2 — Marketplace Routing Behavioral Eval (full N={n_total})",
        "",
        "## Configuration",
        f"- Runtime: Claude Code CLI (`{CLAUDE}`)",
        f"- Timeout: {TIMEOUT_S}s per run",
        f"- Wall budget: ~{n_total * 2 * TIMEOUT_S // 60} min",
        "- Signal: `marketplace_skill_md_reads` count per eval",
        "",
        "## Summary",
        f"- Evals run: {n_total}",
        f"- Material differences: {n_material}/{n_total}",
        f"- No differences: {n_total - n_material}/{n_total}",
        f"- With-skill total signals: {sum_with}",
        f"- Without-skill total signals: {sum_without}",
        f"- With-skill mean per eval: {benchmark['summary']['with_skill_mean_per_eval']}",
        f"- Without-skill mean per eval: {benchmark['summary']['without_skill_mean_per_eval']}",
        "",
        "## Per-eval results",
        "",
        "| Eval | Expected | With-skill | Without-skill | Delta | Verdict |",
        "|------|----------|-----------:|--------------:|------:|---------|",
    ]
    for r in benchmark["results"]:
        md.append(
            f"| {r['eval_id']} | {r['expected_skill']} | "
            f"{r['with_skill_score']} | {r['without_skill_score']} | "
            f"{r['delta']:+d} | {r['verdict']} |"
        )
    md.extend([
        "",
        "## Methodology notes",
        "",
        "- **Signal strength:** read-counting measures consultation, not application.",
        "  A skill read but not applied would still show as a positive signal. The",
        "  Tessl framework (arxiv 2606.17819v1) and Anthropic's skill-creator evals",
        "  instead use assertion-based grading of the final output.",
        "- **Iteration 3 scope:** write `assertions[]` per eval (Anthropic pattern)",
        "  and grade the final response text against them with an LLM-as-judge.",
        "",
    ])
    (ITER_DIR / "benchmark.md").write_text("\n".join(md))

    print(f"\n[iter-2] done. {n_material}/{n_total} evals show material_difference.")
    print(f"[iter-2] aggregate: with={sum_with} without={sum_without} delta={sum_with - sum_without}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
