#!/usr/bin/env python3
"""Iteration 2.5 — targeted re-run of N=3 hurt evals with new skill content.

The iter-2 runner doesn't accept --evals or --output-dir flags, so this is
a minimal wrapper that re-invokes claude with the same settings as iter-2
but only for the 3 hurt evals (ingest-1, ingest-2, lint-2) and writes
outputs to iteration-2.5/.

After the rewrites committed in 861df65, the with-skill SKILL.md content
includes scope routers that should prevent the over-prescriptive workflow
problem observed in iter-3.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path("/Users/felix/Documents/AutoPluginClaw/taches-principled-light")
SKILLS_DIR = REPO / "skills"
WORKSPACE = REPO / "docs/principled/skill-evals/marketplace-routing-2026-06-22"
ITER_DIR = WORKSPACE / "iteration-2.5"
EVALS_FILE = WORKSPACE / "evals/evals.json"
ITER3_EVALS = ["ingest-1", "ingest-2", "lint-2"]
CLAUDE = "/Users/felix/.local/bin/claude"
CLAUDE_MODEL = "haiku"
TIMEOUT_S = 300
EMPTY_PROJECT = Path("/tmp/empty-claude-project")


def preflight() -> bool:
    cmd = [CLAUDE, "--model", CLAUDE_MODEL, "--print",
           "--output-format", "stream-json", "echo ok"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return r.returncode == 0
    except Exception as e:
        print(f"[iter-2.5] preflight failed: {e}", file=sys.stderr)
        return False


def run_one(utterance: str, with_skill: bool, eval_dir: Path) -> dict:
    cmd = [CLAUDE, "--model", CLAUDE_MODEL, "--print",
           "--output-format", "stream-json",
           "--add-dir", str(REPO),
           "--permission-mode", "bypassPermissions"]
    if with_skill:
        cmd.extend(["--add-dir", str(SKILLS_DIR)])
        cmd.extend(["--add-dir", str(REPO / ".agents/skills")])
    else:
        EMPTY_PROJECT.mkdir(exist_ok=True)
        cmd.extend(["--add-dir", str(EMPTY_PROJECT)])
    cmd.append(utterance)

    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "duration_ms": TIMEOUT_S * 1000,
                "total_events": 0, "marketplace_skill_md_reads": []}
    out_path = eval_dir / ("with_skill.jsonl" if with_skill else "without_skill.jsonl")
    out_path.write_text(r.stdout)
    return {
        "status": "completed" if r.returncode == 0 else f"rc={r.returncode}",
        "duration_ms": 0,
        "total_events": sum(1 for line in r.stdout.splitlines() if line.strip()),
        "marketplace_skill_md_reads": [],
    }


def main() -> int:
    ITER_DIR.mkdir(parents=True, exist_ok=True)
    evals_data = json.loads(EVALS_FILE.read_text())
    all_evals = {e["id"]: e for e in evals_data["evals"]}
    evals = [all_evals[eid] for eid in ITER3_EVALS if eid in all_evals]

    print(f"[iter-2.5] running {len(evals)} evals x 2 configs = {len(evals) * 2} runs")
    print(f"[iter-2.5] target model: {CLAUDE_MODEL} via inference-gateway proxy (port 3456)")
    print(f"[iter-2.5] workspace: {ITER_DIR}")

    if not preflight():
        print("[iter-2.5] aborting: preflight failed", file=sys.stderr)
        return 3

    for i, ev in enumerate(evals, 1):
        eval_id = ev["id"]
        utterance = ev["utterance"]
        eval_dir = ITER_DIR / f"eval-{eval_id}"
        eval_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n[{i}/{len(evals)}] {eval_id} (expected={ev['expected']})")
        print(f"  utterance: {utterance}")
        with_metrics = run_one(utterance, with_skill=True, eval_dir=eval_dir)
        print(f"  with-skill: {with_metrics['status']} events={with_metrics['total_events']}")
        without_metrics = run_one(utterance, with_skill=False, eval_dir=eval_dir)
        print(f"  without-skill: {without_metrics['status']} events={without_metrics['total_events']}")
        comparison = {
            "eval_id": eval_id,
            "utterance": utterance,
            "expected_skill": ev["expected"],
            "with_skill": with_metrics,
            "without_skill": without_metrics,
        }
        (eval_dir / "behavioral_comparison.json").write_text(
            json.dumps(comparison, indent=2)
        )

    print(f"\n[iter-2.5] done. {len(evals)} evals re-run with new skill content.")
    return 0


if __name__ == "__main__":
    sys.exit(main())