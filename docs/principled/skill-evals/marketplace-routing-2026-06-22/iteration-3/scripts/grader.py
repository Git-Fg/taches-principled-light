#!/usr/bin/env python3
"""Iteration-3 grader: LLM-as-judge runner.

For each (eval, config) pair, grades the eval's assertions[] against the
agent's transcript. Per the iter-3 design (iteration-3-design.md), code-based
assertions (consultation, structure) bypass the LLM call entirely; only
compliance and quality assertions invoke the judge.

Inputs:
  --assertions  Path to assertions.json for this eval
  --transcript  Path to with_skill.jsonl or without_skill.jsonl
  --eval-dir    Directory where outputs are written
  --config      "with" or "without" (for output filename)
  --judge-model Alias to use as judge (default: sonnet -> MiniMax-M3)

Outputs (in eval-dir/):
  grading_iter3.json — the new schema documented in iteration-3-design.md
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Literal

# Per the iter-3 design, judge model is the proxy 'sonnet' alias (= MiniMax-M3),
# a different underlying family from the 'haiku' solver. The 'glm-5.2' alias
# is a stronger alternative (Intelligence Index v4.1 score 51 vs 44 for
# MiniMax-M3 per Simon Willison's June 17 2026 review) but is deferred to
# iter-3.1 calibration. Override via --judge-model glm-5.2 to test.
DEFAULT_JUDGE_MODEL = "sonnet"
PROXY_BASE_URL = "http://100.80.231.128:3456"
JUDGE_PROMPT = """\
You are an evaluator grading an AI agent's run against a list of assertions.

You will be given:
1. A list of assertions (compliance/quality only — code-based checks have
   already been applied and are not in your scope).
2. The agent's transcript (NDJSON, parsed for you below).
3. The relevant skill's SKILL.md (if applicable).
4. A reference_solution describing what a complete passing response looks like.

Your job: for each assertion, determine whether the agent satisfied it.
Respond ONLY with valid JSON, no markdown fences.

Schema:
{{
  "expectations": [
    {{"id": "<assertion_id>", "text": "<assertion_text>",
     "passed": true|false, "evidence": "<one-sentence justification>",
     "points_awarded": <0|points>, "unknown": false}}
  ]
}}

Rules:
- `unknown: true` is reserved for evidence that is genuinely ambiguous
  (not just uncertain — you cannot tell from the transcript). When in
  doubt, set `unknown: false` and grade based on the strongest signal.
- `evidence` should cite specific transcript events or output text.
- `points_awarded` is the full points value if passed, else 0.

Assertions:
{assertions}

Reference solution (what a complete passing response looks like):
{reference_solution}

Transcript (relevant excerpts):
{transcript_excerpt}
"""


def parse_events(text: str) -> list[dict]:
    out: list[dict] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return out


def extract_transcript_excerpt(events: list[dict], max_chars: int = 8000) -> str:
    """Return a compact textual excerpt: assistant text + tool_use summary."""
    lines: list[str] = []
    total = 0
    for ev in events:
        if total >= max_chars:
            lines.append("... [truncated]")
            break
        ev_type = ev.get("type", "?")
        if ev_type == "assistant":
            content = ev.get("message", {}).get("content", [])
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict):
                    continue
                btype = block.get("type")
                if btype == "text":
                    text = block.get("text", "")
                    if text.strip():
                        lines.append(f"[assistant] {text[:500]}")
                        total += len(text[:500])
                elif btype == "tool_use":
                    name = block.get("name", "?")
                    inp = json.dumps(block.get("input", {}))[:300]
                    lines.append(f"[tool_use] {name}({inp})")
                    total += len(name) + len(inp) + 20
        elif ev_type == "user":
            content = ev.get("message", {}).get("content", [])
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        out = str(block.get("content", ""))[:300]
                        lines.append(f"[tool_result] {out}")
                        total += len(out) + 20
    return "\n".join(lines)


def grade_code_based_assertion(assertion: dict, events: list[dict]) -> tuple[bool, str, int]:
    """Grade consultation + structure assertions without an LLM call.

    Returns (passed, evidence, points_awarded).

    consultation: count Read on SKILL.md + Skill tool invocations + Bash that
                  invokes skill-named scripts (weak signal)
    structure:    if compare_args set, parse Bash tool_use args and match;
                  otherwise return None to signal "needs LLM judge fallback".
    """
    atype = assertion.get("type")
    points = assertion.get("points", 0)
    text = assertion.get("text", "")
    tool_uses: list[tuple[str, dict]] = [
        (b.get("name", ""), b.get("input", {}))
        for ev in events if ev.get("type") == "assistant"
        for b in (ev.get("message", {}).get("content", []) or [])
        if isinstance(b, dict) and b.get("type") == "tool_use"
    ]
    if atype == "consultation":
        read_paths = [inp.get("file_path", "") for n, inp in tool_uses if n == "Read"]
        skill_calls = [inp.get("skill", "") for n, inp in tool_uses if n == "Skill"]
        any_read = any("SKILL.md" in p for p in read_paths)
        any_skill = any(s for s in skill_calls)
        if any_read or any_skill:
            paths_str = ", ".join(p for p in read_paths if "SKILL.md" in p)[:200]
            skills_str = ", ".join(s for s in skill_calls if s)[:200]
            evidence = f"agent read {paths_str}; Skill tool: {skills_str}"
            return True, evidence, points
        return False, "agent did not read or invoke any skill", 0
    if atype == "structure":
        compare_args = assertion.get("compare_args")
        if compare_args:
            # Find Bash tool_use; verify each named arg matches assertion's expected value
            # (The expected value is implicit in the assertion text for now;
            # a richer schema would encode it. We pass if at least one Bash call has
            # all compare_args keys present and non-empty.)
            for name, inp in tool_uses:
                if name == "Bash":
                    if all(inp.get(k) for k in compare_args):
                        evidence = f"Bash call has args {compare_args}: {json.dumps(inp)[:200]}"
                        return True, evidence, points
            return False, f"no Bash call had all of {compare_args}", 0
        # No compare_args → fall back to LLM judge
        return None, "structure assertion without compare_args falls back to LLM judge", 0
    return None, f"unknown assertion type {atype!r} for code grader; falls back to LLM judge", 0


def grade_with_judge(assertions: list[dict], transcript_excerpt: str,
                     reference_solution: str, judge_model: str) -> list[dict]:
    """Invoke the judge LLM for compliance/quality assertions."""
    judge_assertions = [
        a for a in assertions if a.get("type") in ("compliance", "quality")
    ]
    if not judge_assertions:
        return []
    prompt = JUDGE_PROMPT.format(
        assertions=json.dumps(judge_assertions, indent=2),
        reference_solution=reference_solution,
        transcript_excerpt=transcript_excerpt[:8000],
    )
    cmd = [
        "curl", "-sS", "--max-time", "180",
        f"{PROXY_BASE_URL}/v1/chat/completions",
        "-H", "Authorization: Bearer dummy",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({
            "model": judge_model,
            "max_tokens": 4000,
            "messages": [{"role": "user", "content": prompt}],
        }),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        return [
            {"id": a["id"], "text": a.get("text", ""),
             "passed": False, "evidence": "judge call timed out (180s)",
             "points_awarded": 0, "unknown": True}
            for a in judge_assertions
        ]
    try:
        resp = json.loads(result.stdout)
        content = resp["choices"][0]["message"]["content"] or ""
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        return [
            {"id": a["id"], "text": a.get("text", ""),
             "passed": False, "evidence": f"judge parse error: {e!r}",
             "points_awarded": 0, "unknown": True}
            for a in judge_assertions
        ]
    # Extract JSON from response (judges sometimes wrap in fences)
    content = content.strip()
    if content.startswith("```"):
        content = content.split("```", 2)[1]
        if content.startswith("json"):
            content = content[4:]
    try:
        judge_output = json.loads(content)
        expectations = judge_output.get("expectations", [])
    except json.JSONDecodeError:
        return [
            {"id": a["id"], "text": a.get("text", ""),
             "passed": False, "evidence": f"judge returned non-JSON: {content[:200]!r}",
             "points_awarded": 0, "unknown": True}
            for a in judge_assertions
        ]
    # Map by id; fill missing with UNKNOWN
    out_by_id = {e.get("id"): e for e in expectations if e.get("id")}
    return [
        {
            "id": a["id"],
            "text": a.get("text", ""),
            "passed": out_by_id.get(a["id"], {}).get("passed", False),
            "evidence": out_by_id.get(a["id"], {}).get("evidence", "no judge output for this assertion"),
            "points_awarded": out_by_id.get(a["id"], {}).get("points_awarded", 0) if out_by_id.get(a["id"], {}).get("passed") else 0,
            "unknown": out_by_id.get(a["id"], {}).get("unknown", False),
        }
        for a in judge_assertions
    ]


def compute_summary(expectations: list[dict], assertions: list[dict],
                   weight: dict[str, float]) -> dict:
    """Compute per-category and overall scores via Tessl-style weighted average."""
    by_category: dict[str, list[tuple[int, int]]] = {}
    for a in assertions:
        cat = a.get("category", "?")
        # Find matching expectation
        exp = next((e for e in expectations if e.get("id") == a.get("id")), None)
        awarded = exp.get("points_awarded", 0) if exp else 0
        by_category.setdefault(cat, []).append((awarded, a.get("points", 0)))
    category_scores: dict[str, float] = {}
    for cat, pairs in by_category.items():
        total_awarded = sum(p[0] for p in pairs)
        total_possible = sum(p[1] for p in pairs)
        category_scores[cat] = (
            round(100 * total_awarded / total_possible, 1)
            if total_possible else 0.0
        )
    # Weighted average across reward_basis (default: both)
    reward_basis = list(by_category.keys())
    w_sum = sum(weight.get(c, 1.0) for c in reward_basis)
    if w_sum == 0:
        overall = 0.0
    else:
        overall = round(
            100 * sum(category_scores[c] * weight.get(c, 1.0) for c in reward_basis) / w_sum
            / 100, 1
        )
    n_passed = sum(1 for e in expectations if e.get("passed") and not e.get("unknown"))
    n_failed = sum(1 for e in expectations if not e.get("passed") and not e.get("unknown"))
    n_unknown = sum(1 for e in expectations if e.get("unknown"))
    return {
        "instruction_following_score": category_scores.get("instruction_following", 0.0),
        "goal_completion_score": category_scores.get("goal_completion", 0.0),
        "overall_score": overall,
        "passed": n_passed, "failed": n_failed,
        "unknown": n_unknown, "total": len(expectations),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assertions", required=True, type=Path)
    parser.add_argument("--transcript", required=True, type=Path)
    parser.add_argument("--eval-dir", required=True, type=Path)
    parser.add_argument("--config", choices=["with", "without"], required=True)
    parser.add_argument("--judge-model", default=DEFAULT_JUDGE_MODEL)
    args = parser.parse_args()

    assertions_data = json.loads(args.assertions.read_text())
    assertions = assertions_data.get("assertions", [])
    weight = assertions_data.get("weight", {
        "instruction_following": 1.0, "goal_completion": 1.0,
    })

    transcript_text = args.transcript.read_text() if args.transcript.exists() else ""
    events = parse_events(transcript_text)
    transcript_excerpt = extract_transcript_excerpt(events)

    # Code-based grading (consultation + structure-with-compare_args only;
    # structure without compare_args returns None and falls through to judge)
    expectations: list[dict] = []
    fallback_to_judge: list[dict] = []
    for a in assertions:
        if a.get("grader") != "code":
            continue
        result = grade_code_based_assertion(a, events)
        if result is None:
            fallback_to_judge.append(a)
            continue
        passed, evidence, awarded = result
        expectations.append({
            "id": a["id"], "text": a.get("text", ""),
            "passed": passed, "evidence": evidence,
            "points_awarded": awarded, "unknown": False,
        })

    # Model-based grading (one batched call per (eval, config))
    judge_pool = fallback_to_judge + [
        a for a in assertions if a.get("grader") == "model"
    ]
    judge_expectations = grade_with_judge(
        judge_pool, transcript_excerpt,
        assertions_data.get("reference_solution", ""),
        args.judge_model,
    )
    expectations.extend(judge_expectations)

    summary = compute_summary(expectations, assertions, weight)
    out = {
        "judge_model": args.judge_model,
        "config": args.config,
        "eval_id": assertions_data.get("eval_id", args.eval_dir.name),
        "expectations": expectations,
        "summary": summary,
        "weight": weight,
    }
    args.eval_dir.mkdir(parents=True, exist_ok=True)
    out_path = args.eval_dir / f"grading_{args.config}_skill.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(f"[grader] {out_path}: overall={summary['overall_score']} "
          f"IF={summary['instruction_following_score']} "
          f"GC={summary['goal_completion_score']} "
          f"P/F/U={summary['passed']}/{summary['failed']}/{summary['unknown']}",
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
