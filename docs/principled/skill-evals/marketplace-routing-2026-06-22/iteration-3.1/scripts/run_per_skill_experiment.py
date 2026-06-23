#!/usr/bin/env python3
"""Per-skill --add-dir experiment for iter-3.1.

Tests whether Bucket A3 discovery failures are caused by:
- (H1) Plugin skills shadowing marketplace skills in the discovery path
- (H2) Marketplace descriptions don't surface in the discovery path
- (H3) Choice paralysis from 26+ marketplace skills in scope

Method: for each Bucket A3 eval, run the with-skill config TWO ways:
1. CONTROL: full marketplace in scope (matches iter-2 behavior)
2. TREATMENT: only the EXPECTED marketplace skill in scope (no plugins)

If treatment lifts and control doesn't, the issue is choice paralysis
(H3) or plugin shadowing (H1) -- NOT description content (H2).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path("/Users/felix/Documents/AutoPluginClaw/taches-principled-light")
WORKSPACE = REPO / "docs/principled/skill-evals/marketplace-routing-2026-06-22"
OUT_DIR = WORKSPACE / "iteration-3.1"
EVALS_FILE = WORKSPACE / "evals/evals.json"
ITER3_EVALS = [
    {"id": "ingest-1", "skill_dir": ".agents/skills/ingesting-skills"},
    {"id": "ingest-2", "skill_dir": ".agents/skills/ingesting-skills"},
    {"id": "lint-2", "skill_dir": ".agents/skills/marketplace-validator"},
    {"id": "craft-create", "skill_dir": "skills/crafting-skills"},
    {"id": "craft-review", "skill_dir": "skills/crafting-skills"},
]
CLAUDE = "/Users/felix/.local/bin/claude"
CLAUDE_MODEL = "haiku"
TIMEOUT_S = 180


def preflight() -> bool:
    cmd = [CLAUDE, "--model", CLAUDE_MODEL, "--print",
           "--output-format", "stream-json", "say ok"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return r.returncode == 0
    except Exception as e:
        print(f"[iter-3.1] preflight failed: {e}", file=sys.stderr)
        return False


def run_one(utterance: str, with_skill: bool, eval_dir: Path,
            skill_only: bool = False, skill_dir: str | None = None) -> dict:
    cmd = [CLAUDE, "--print",
           "--output-format", "stream-json",
           "--model", CLAUDE_MODEL,
           "--dangerously-skip-permissions"]
    if with_skill:
        if skill_only and skill_dir:
            add_dir = str(REPO / skill_dir)
        else:
            add_dir = str(REPO)
    else:
        EMPTY_PROJECT = Path("/tmp/empty-claude-project")
        EMPTY_PROJECT.mkdir(exist_ok=True)
        add_dir = str(EMPTY_PROJECT)
    cmd.extend(["--add-dir", add_dir])
    # Note: claude CLI requires stdin for the prompt when using --print;
    # passing it as the final cmd arg doesn't work (verified empirically).

    try:
        r = subprocess.run(cmd, input=utterance, capture_output=True, text=True,
                           timeout=TIMEOUT_S, cwd=add_dir)
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "duration_ms": TIMEOUT_S * 1000,
                "total_events": 0}
    eval_dir.mkdir(parents=True, exist_ok=True)
    out_path = eval_dir / "run.jsonl"
    out_path.write_text(r.stdout)
    err_path = eval_dir / "run.stderr"
    err_path.write_text(r.stderr)
    return {
        "status": "completed" if r.returncode == 0 else f"rc={r.returncode}",
        "duration_ms": 0,
        "total_events": sum(1 for line in r.stdout.splitlines() if line.strip()),
        "stderr_tail": (r.stderr or "")[-500:],
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    evals_data = json.loads(EVALS_FILE.read_text())
    all_evals = {e["id"]: e for e in evals_data["evals"]}

    print(f"[iter-3.1] per-skill --add-dir experiment")
    print(f"[iter-3.1] target model: {CLAUDE_MODEL} via inference-gateway proxy (port 3456)")
    print(f"[iter-3.1] testing {len(ITER3_EVALS)} Bucket A3 evals x 3 configs = {len(ITER3_EVALS) * 3} runs")

    if not preflight():
        print("[iter-3.1] aborting: preflight failed", file=sys.stderr)
        return 3

    for i, ev in enumerate(ITER3_EVALS, 1):
        eval_id = ev["id"]
        utterance = all_evals[eval_id]["utterance"]
        skill_dir = ev["skill_dir"]
        eval_dir = OUT_DIR / f"eval-{eval_id}"
        eval_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n[{i}/{len(ITER3_EVALS)}] {eval_id} (expected={skill_dir.split('/')[-1]})")
        print(f"  utterance: {utterance}")

        print("  [1/3] without-skill ...")
        m = run_one(utterance, with_skill=False, eval_dir=eval_dir / "without_skill")
        print(f"    {m['status']} events={m['total_events']}")

        print("  [2/3] with full marketplace ...")
        m = run_one(utterance, with_skill=True, eval_dir=eval_dir / "with_full_marketplace")
        print(f"    {m['status']} events={m['total_events']}")

        print("  [3/3] with expected skill ONLY ...")
        m = run_one(utterance, with_skill=True, eval_dir=eval_dir / "with_skill_only",
                    skill_only=True, skill_dir=skill_dir)
        print(f"    {m['status']} events={m['total_events']}")

        comparison = {
            "eval_id": eval_id,
            "utterance": utterance,
            "expected_skill_dir": skill_dir,
            "configs": ["without_skill", "with_full_marketplace", "with_skill_only"],
        }
        (eval_dir / "experiment_metadata.json").write_text(json.dumps(comparison, indent=2))

    print(f"\n[iter-3.1] done. Run grader on each config to measure lift per condition.")
    return 0


if __name__ == "__main__":
    sys.exit(main())