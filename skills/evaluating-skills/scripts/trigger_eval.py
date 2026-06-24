#!/usr/bin/env python3
"""Trigger-eval harness for evaluating-skills.

Measures whether a skill's ``description`` frontmatter causes correct routing —
i.e. does the agent invoke the skill when it should, and ignore it when it
shouldn't. Sister to ``aggregate_benchmark.py`` which measures execution
quality (with-skill vs without-skill behavioral delta); this script measures
description quality (does the description cause correct routing?).

Five subcommands, one entry point, all read/write JSON:

  init      Scaffold an --n-query trigger-eval set (default 20: 10 should-trigger, 10 should-not)
  split     Stratified 60/40 train/val split, preserving the should_trigger ratio
  detect    Parse a transcript, return 0/1 for whether <skill_name> triggered
  score     Per-query + aggregate trigger rate, threshold breach report
  stealing  Compare two trigger-rate reports, flag >10pp drops in siblings

Usage::

    python scripts/trigger_eval.py init --out /tmp/queries.json
    python scripts/trigger_eval.py split /tmp/queries.json /tmp/train.json /tmp/val.json
    python scripts/trigger_eval.py detect transcript.jsonl <skill-name> --runtime claude
    python scripts/trigger_eval.py score /tmp/queries.json results.jsonl --threshold 0.5
    python scripts/trigger_eval.py stealing before.json after.json --threshold 0.10

Pure Python stdlib — no subprocess, no external dependencies. The runtime
detection rules are inline; see ``references/runtime-adapters.md`` for the
per-runtime event shapes this script handles.

Schemas for inputs and outputs are documented in
``references/schemas.md`` (sections §trigger_evals.json, §results.jsonl,
§trigger-rate-report.json).
"""

import argparse
import json
import random
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# Per-runtime event-shape rules. Each rule is a callable (event_dict, skill_name) -> bool.
# The default rule is "any field anywhere equals skill_name" (loose), used as a fallback.

def _walk(obj, path=()):
    """Yield (path, value) for every leaf in a nested dict/list."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _walk(v, path + (k,))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk(v, path + (i,))
    else:
        yield (path, obj)


def _loose_match(event: dict, skill_name: str) -> bool:
    """Fallback: any leaf value equals the skill name (case-insensitive)."""
    needle = skill_name.lower()
    for _, v in _walk(event):
        if isinstance(v, str) and v.lower() == needle:
            return True
    return False


def detect_claude(event: dict, skill_name: str) -> bool:
    """Claude Code / Cursor stream-json: ``tool_use`` event with name=Skill + skill in input."""
    if not isinstance(event, dict):
        return False
    evt_type = event.get("type", "")
    if evt_type == "tool_use":
        name = event.get("name", "")
        if isinstance(name, str) and name.lower() == "skill":
            input_skill = event.get("input", {}).get("skill", "") if isinstance(event.get("input"), dict) else ""
            if isinstance(input_skill, str) and input_skill == skill_name:
                return True
    # Claude also streams content_block_start events for tool_use blocks.
    if evt_type == "content_block_start":
        block = event.get("content_block", {})
        if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") == "Skill":
            input_block = block.get("input", {})
            if isinstance(input_block, dict) and input_block.get("skill") == skill_name:
                return True
    return False


def detect_codex(event: dict, skill_name: str) -> bool:
    """Codex CLI: ``tool_use`` event with name=skill + skill in input (case-insensitive)."""
    if not isinstance(event, dict):
        return False
    evt_type = event.get("type", "")
    if evt_type == "tool_use":
        name = event.get("name", "")
        if isinstance(name, str) and name.lower() == "skill":
            input_skill = event.get("input", {}).get("skill", "") if isinstance(event.get("input"), dict) else ""
            if isinstance(input_skill, str) and input_skill.lower() == skill_name.lower():
                return True
    return False


def detect_kimi(event: dict, skill_name: str) -> bool:
    """kimi-code: assistant message with ``tool_calls`` whose function name is a skill invocation.

    Matches exact-prefix skill tool calls (``run_skill_<name>``, ``use_skill_<name>``,
    ``skill_<name>``). Substring matching on the bare function name caused false
    positives on short skill names (e.g. ``t`` would match ``extract_table``), so
    we anchor on the conventional prefix and verify the suffix matches the skill.
    """
    if not isinstance(event, dict):
        return False
    if event.get("role") != "assistant":
        return False
    tool_calls = event.get("tool_calls", [])
    if not isinstance(tool_calls, list):
        return False
    needle = skill_name.lower()
    for tc in tool_calls:
        if not isinstance(tc, dict):
            continue
        func = tc.get("function", {})
        if not isinstance(func, dict):
            continue
        name = func.get("name", "")
        if not isinstance(name, str):
            continue
        lname = name.lower()
        # Conventional prefixes: run_skill_<name>, use_skill_<name>, skill_<name>
        for prefix in ("run_skill_", "use_skill_", "skill_"):
            if lname == prefix + needle or lname.startswith(prefix + needle + "_"):
                return True
    return False


def detect_reasonix(event: dict, skill_name: str) -> bool:
    """Reasonix: ``ToolDispatch`` event with tool=run_skill + skill field."""
    if not isinstance(event, dict):
        return False
    if event.get("type") != "ToolDispatch":
        return False
    if event.get("tool") != "run_skill":
        return False
    return event.get("skill") == skill_name


DETECTORS = {
    "claude": detect_claude,
    "codex": detect_codex,
    "kimi": detect_kimi,
    "reasonix": detect_reasonix,
    "cursor": detect_claude,  # cursor uses claude-compatible stream-json
}


# ---------- init ----------

def cmd_init(args) -> int:
    """Scaffold an --n-query trigger-eval set (default 20) with empty query text."""
    if args.n < 1:
        print(f"ERROR: --n must be >= 1; got {args.n}", file=sys.stderr)
        return 1
    queries = []
    for i in range(1, args.n + 1):
        should_trigger = (i % 2 == 1)  # alternate T/F starting with T
        queries.append({
            "id": i,
            "query": "",
            "should_trigger": should_trigger,
            "notes": "",
        })
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "skill_name": args.skill_name or "",
        "n_queries": len(queries),
        "queries": queries,
        "_notes": (
            "Fill in `query` for every entry. The should_trigger flag must be "
            "preserved. Per AGENTS.md Description-as-Routing-Signal rule 7: "
            "8-10 should-trigger, 8-10 should-not, weighted to near-misses "
            "not obvious negatives. See references/trigger-eval-guide.md for "
            "query-writing discipline."
        ),
    }
    out_path.write_text(json.dumps(payload, indent=2) + "\n")
    n_should = sum(1 for q in queries if q["should_trigger"])
    n_not = len(queries) - n_should
    print(f"Wrote {out_path} ({n_should} should-trigger, {n_not} should-not, {len(queries)} total)")
    return 0


# ---------- split ----------

def cmd_split(args) -> int:
    """Stratified 60/40 split preserving the should_trigger ratio.

    For each stratum (should_trigger true/false), round the cut point to the
    nearest integer and clamp so both halves always contain ≥1 of each kind
    when the stratum has ≥2 items. This preserves the ratio even for
    imbalanced small datasets.
    """
    if not (0.0 < args.ratio < 1.0):
        print(f"ERROR: --ratio must be between 0 and 1 (exclusive); got {args.ratio}", file=sys.stderr)
        return 1
    src = json.loads(Path(args.in_path).read_text())
    queries = src.get("queries", [])
    if not queries:
        print("ERROR: input has no queries", file=sys.stderr)
        return 1

    should = [q for q in queries if q.get("should_trigger")]
    should_not = [q for q in queries if not q.get("should_trigger")]

    rng = random.Random(args.seed) if args.seed is not None else random.Random()
    rng.shuffle(should)
    rng.shuffle(should_not)

    def partition(items, ratio):
        n = len(items)
        if n == 0:
            return [], []
        if n == 1:
            # Single item: put in train; nothing to put in val.
            return items, []
        # Round to nearest integer; clamp so both halves have ≥1 when n≥2.
        cut = round(n * ratio)
        cut = max(1, min(n - 1, cut))
        return items[:cut], items[cut:]

    s_train, s_val = partition(should, args.ratio)
    n_train, n_val = partition(should_not, args.ratio)
    train = s_train + n_train
    val = s_val + n_val
    rng.shuffle(train)
    rng.shuffle(val)

    def write_split(path, items, name):
        payload = {
            "skill_name": src.get("skill_name", ""),
            "split": name,
            "ratio": args.ratio,
            "n_queries": len(items),
            "queries": items,
        }
        Path(path).write_text(json.dumps(payload, indent=2) + "\n")
        n_s = sum(1 for q in items if q.get("should_trigger"))
        print(f"Wrote {path} ({n_s} should-trigger, {len(items) - n_s} should-not, {len(items)} total)")

    write_split(args.train_path, train, "train")
    write_split(args.val_path, val, "val")
    return 0


# ---------- detect ----------

def cmd_detect(args) -> int:
    """Parse a streaming transcript; exit 0 if <skill_name> triggered, 1 if not."""
    detector = DETECTORS.get(args.runtime, _loose_match)
    transcript = Path(args.transcript)
    triggered = False
    evidence = None
    error = None
    try:
        with transcript.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if detector(event, args.skill_name):
                    triggered = True
                    evidence = line[:200]
                    break
    except FileNotFoundError:
        error = f"transcript not found: {transcript}"

    out = {
        "skill_name": args.skill_name,
        "runtime": args.runtime,
        "transcript": str(transcript),
        "triggered": triggered,
        "evidence": evidence,
    }
    if error:
        out["error"] = error
    print(json.dumps(out))
    return 1 if (error or not triggered) else 0


# ---------- score ----------

def load_results(results_path: Path) -> list[dict]:
    """Load results.jsonl — one JSON object per line."""
    out = []
    with results_path.open() as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"WARN: skipping malformed line {lineno}: {e}", file=sys.stderr)
                continue
            if "query_id" not in obj or "triggered" not in obj:
                print(f"WARN: line {lineno} missing query_id or triggered; skipping", file=sys.stderr)
                continue
            out.append(obj)
    return out


def cmd_score(args) -> int:
    """Per-query + aggregate trigger rate, threshold breach report."""
    queries_data = json.loads(Path(args.queries).read_text())
    queries = {q["id"]: q for q in queries_data.get("queries", [])}
    skill_name = queries_data.get("skill_name", "")
    results = load_results(Path(args.results))

    if not queries:
        print("ERROR: queries file has no queries", file=sys.stderr)
        return 1
    if not results:
        print("ERROR: results file is empty", file=sys.stderr)
        return 1

    # Group results by query_id.
    by_query: dict[int, list[bool]] = defaultdict(list)
    matched_query_ids = set()
    for r in results:
        if r["query_id"] not in queries:
            print(f"WARN: result query_id={r['query_id']} not in queries; dropping", file=sys.stderr)
            continue
        matched_query_ids.add(r["query_id"])
        by_query[r["query_id"]].append(bool(r["triggered"]))

    # Per-query: trigger_rate + pass.
    threshold = args.threshold
    per_query = []
    for qid in sorted(queries):
        q = queries[qid]
        should = bool(q.get("should_trigger"))
        runs = by_query.get(qid, [])
        n = len(runs)
        if n == 0:
            per_query.append({
                "query_id": qid,
                "should_trigger": should,
                "runs": 0,
                "trigger_count": 0,
                "trigger_rate": None,
                "pass": None,
            })
            continue
        triggered_count = sum(1 for r in runs if r)
        rate = triggered_count / n
        if should:
            passed = rate >= threshold
        else:
            passed = rate <= (1.0 - threshold)
        per_query.append({
            "query_id": qid,
            "should_trigger": should,
            "runs": n,
            "trigger_count": triggered_count,
            "trigger_rate": round(rate, 4),
            "pass": passed,
        })

    # Aggregate: per-config mean trigger_rate.
    should_rates = [p["trigger_rate"] for p in per_query if p["should_trigger"] and p["trigger_rate"] is not None]
    should_not_rates = [p["trigger_rate"] for p in per_query if not p["should_trigger"] and p["trigger_rate"] is not None]

    def _stat(rates):
        if not rates:
            return None
        return {
            "mean": round(statistics.mean(rates), 4),
            "stddev": round(statistics.stdev(rates), 4) if len(rates) > 1 else 0.0,
            "min": round(min(rates), 4),
            "max": round(max(rates), 4),
        }

    aggregate = {
        "trigger_rate_should": _stat(should_rates),
        "trigger_rate_should_not": _stat(should_not_rates),
    }
    # threshold_pass: should side >= threshold AND should-not side <= (1 - threshold).
    if aggregate["trigger_rate_should"] and aggregate["trigger_rate_should_not"]:
        aggregate["threshold_pass"] = (
            aggregate["trigger_rate_should"]["mean"] >= threshold
            and aggregate["trigger_rate_should_not"]["mean"] <= (1.0 - threshold)
        )
    else:
        aggregate["threshold_pass"] = False

    notes = _score_notes(per_query, aggregate, threshold)

    report = {
        "metadata": {
            "skill_name": skill_name,
            "timestamp": _now_iso(),
            "threshold": threshold,
            "n_queries": len(queries),
            "n_results": len(results),
        },
        "per_query": per_query,
        "aggregate": aggregate,
        "notes": notes,
    }

    out_json = Path(args.out_json)
    out_md = Path(args.out_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2) + "\n")
    out_md.write_text(render_score_markdown(report))
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    return 0


def _score_notes(per_query, aggregate, threshold) -> list[str]:
    notes = []
    fails_should = [p for p in per_query if p["should_trigger"] and p["pass"] is False]
    fails_should_not = [p for p in per_query if not p["should_trigger"] and p["pass"] is False]
    if fails_should:
        ids = ", ".join(str(p["query_id"]) for p in fails_should[:5])
        notes.append(f"{len(fails_should)} should-trigger queries below threshold (ids: {ids}) — broaden the description.")
    if fails_should_not:
        ids = ", ".join(str(p["query_id"]) for p in fails_should_not[:5])
        notes.append(f"{len(fails_should_not)} should-not queries above threshold (ids: {ids}) — narrow the description.")
    if aggregate.get("trigger_rate_should") and aggregate.get("trigger_rate_should_not"):
        sd = aggregate["trigger_rate_should"]["mean"]
        sn = aggregate["trigger_rate_should_not"]["mean"]
        if not aggregate["threshold_pass"]:
            notes.append(f"Threshold not met: should={sd}, should-not={sn} (threshold={threshold}).")
    return notes


def render_score_markdown(report: dict) -> str:
    md = []
    md.append(f"# Trigger Rate — `{report['metadata']['skill_name']}`\n")
    md.append(f"_Generated {report['metadata']['timestamp']}_\n")
    md.append(f"Threshold: `{report['metadata']['threshold']}` · "
              f"Queries: `{report['metadata']['n_queries']}` · "
              f"Results: `{report['metadata']['n_results']}`\n\n")
    if report.get("aggregate"):
        md.append("## Aggregate\n\n")
        md.append("| Config | Mean | Stddev | Min | Max |\n")
        md.append("|---|---|---|---|---|\n")
        for config, stats in report["aggregate"].items():
            if config == "threshold_pass":
                continue
            if stats is None:
                md.append(f"| `{config}` | — | — | — | — |\n")
            else:
                md.append(f"| `{config}` | {stats['mean']} | {stats['stddev']} | {stats['min']} | {stats['max']} |\n")
        if "threshold_pass" in report["aggregate"]:
            verdict = "PASS" if report["aggregate"]["threshold_pass"] else "FAIL"
            md.append(f"\n**Verdict:** `{verdict}`\n\n")
    md.append("## Per-Query\n\n")
    md.append("| ID | should_trigger | runs | triggered | trigger_rate | pass |\n")
    md.append("|---|---|---|---|---|---|\n")
    for p in report.get("per_query", []):
        rate_str = "—" if p['trigger_rate'] is None else f"{p['trigger_rate']}"
        pass_str = "—" if p['pass'] is None else str(p['pass'])
        md.append(f"| {p['query_id']} | {p['should_trigger']} | {p['runs']} | "
                  f"{p['trigger_count']} | {rate_str} | {pass_str} |\n")
    if report.get("notes"):
        md.append("\n## Notes\n\n")
        for n in report["notes"]:
            md.append(f"- {n}\n")
    return "".join(md)


# ---------- stealing ----------

def cmd_stealing(args) -> int:
    """Compare two trigger-rate reports; flag siblings with >10pp drop in should-trigger rate.

    The "before" and "after" files are trigger-rate-report.json from a previous
    `score` run (or a multi-skill aggregator). The script identifies siblings
    whose `aggregate.trigger_rate_should.mean` dropped by more than the
    threshold (default 10pp = 0.10) between before and after.
    """
    before = json.loads(Path(args.before).read_text())
    after = json.loads(Path(args.after).read_text())
    threshold = args.threshold

    def per_skill_mean(report):
        """Extract (skill_name, should_trigger_mean) pairs from a report.

        Accepts either a single-skill report (has aggregate.trigger_rate_should)
        or a multi-skill aggregator report (a dict of skill_name -> report).
        """
        if "aggregate" in report:
            # Single-skill report.
            skill = report.get("metadata", {}).get("skill_name", "")
            stats = report.get("aggregate", {}).get("trigger_rate_should")
            mean = stats["mean"] if stats else None
            return {skill: mean}
        # Multi-skill aggregator.
        out = {}
        for skill, sub in report.items():
            if isinstance(sub, dict) and "aggregate" in sub:
                stats = sub.get("aggregate", {}).get("trigger_rate_should")
                out[skill] = stats["mean"] if stats else None
        return out

    b = per_skill_mean(before)
    a = per_skill_mean(after)
    shared = set(b) & set(a)
    only_before = set(b) - set(a)
    only_after = set(a) - set(b)
    if only_before or only_after:
        only_before_str = ", ".join(sorted(only_before)) or "(none)"
        only_after_str = ", ".join(sorted(only_after)) or "(none)"
        print(f"WARN: skill sets differ between before and after. "
              f"Only in before: {only_before_str}. Only in after: {only_after_str}.",
              file=sys.stderr)
    alerts = []
    for skill in sorted(shared):
        if b[skill] is None or a[skill] is None:
            continue
        delta = a[skill] - b[skill]
        if delta < -threshold:
            alerts.append({
                "skill_name": skill,
                "before": b[skill],
                "after": a[skill],
                "delta": round(delta, 4),
                "pp_drop": round(-delta * 100, 2),
                "verdict": "STOLEN",
            })

    report = {
        "metadata": {
            "timestamp": _now_iso(),
            "threshold": threshold,
            "before_path": str(args.before),
            "after_path": str(args.after),
        },
        "before_per_skill": b,
        "after_per_skill": a,
        "alerts": alerts,
        "summary": {
            "n_shared": len(shared),
            "n_alerts": len(alerts),
        },
    }

    out_json = Path(args.out_json)
    out_md = Path(args.out_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2) + "\n")
    out_md.write_text(render_stealing_markdown(report))
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    if alerts:
        print(f"ALERT: {len(alerts)} sibling(s) with >{int(threshold * 100)}pp drop in should-trigger rate.")
    return 0


def render_stealing_markdown(report: dict) -> str:
    md = []
    threshold_pct = int(report['metadata']['threshold'] * 100)
    md.append(f"# Sibling-Stealing Detection\n\n")
    md.append(f"_Generated {report['metadata']['timestamp']}_\n")
    md.append(f"Threshold: `{report['metadata']['threshold']}` (drop >{threshold_pct}pp) · "
              f"Skills compared: `{report['summary']['n_shared']}` · "
              f"Alerts: `{report['summary']['n_alerts']}`\n\n")
    if not report["alerts"]:
        md.append("_No siblings crossed the threshold._\n")
        return "".join(md)
    md.append("## Alerts\n\n")
    md.append("| Skill | before | after | delta | pp_drop | verdict |\n")
    md.append("|---|---|---|---|---|---|\n")
    for a in report["alerts"]:
        md.append(f"| `{a['skill_name']}` | {a['before']} | {a['after']} | "
                  f"{a['delta']} | {a['pp_drop']}pp | **{a['verdict']}** |\n")
    md.append(f"\n> Per AGENTS.md Description-as-Routing-Signal rule 6: a >{threshold_pct}pp drop in a "
              "sibling's should-trigger rate means the new or changed description is stealing "
              "routing signal. Narrow the new description or merge the skills.\n")
    return "".join(md)


# ---------- utils ----------

def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    # init
    p_init = sub.add_parser("init", help="Scaffold an --n-query trigger-eval set (default 20).")
    p_init.add_argument("--out", required=True, help="Output JSON path.")
    p_init.add_argument("--skill-name", default="", help="Skill name (for metadata).")
    p_init.add_argument("--n", type=int, default=20, help="Total queries (default 20).")
    p_init.set_defaults(func=cmd_init)

    # split
    p_split = sub.add_parser("split", help="Stratified 60/40 train/val split.")
    p_split.add_argument("in_path", help="Input trigger-queries JSON.")
    p_split.add_argument("train_path", help="Output train JSON path.")
    p_split.add_argument("val_path", help="Output val JSON path.")
    p_split.add_argument("--ratio", type=float, default=0.6, help="Train ratio (default 0.6).")
    p_split.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility.")
    p_split.set_defaults(func=cmd_split)

    # detect
    p_detect = sub.add_parser("detect", help="Detect whether a skill triggered in a transcript.")
    p_detect.add_argument("transcript", help="Path to a JSONL transcript.")
    p_detect.add_argument("skill_name", help="Skill name to detect.")
    p_detect.add_argument("--runtime", required=True, choices=sorted(DETECTORS),
                          help="Target runtime (determines event shape).")
    p_detect.set_defaults(func=cmd_detect)

    # score
    p_score = sub.add_parser("score", help="Per-query + aggregate trigger rate.")
    p_score.add_argument("queries", help="trigger-queries JSON path.")
    p_score.add_argument("results", help="results.jsonl path.")
    p_score.add_argument("--threshold", type=float, default=0.5,
                         help="Pass threshold (default 0.5).")
    p_score.add_argument("--out-json", default="trigger-rate-report.json",
                         help="Output JSON report path (default trigger-rate-report.json).")
    p_score.add_argument("--out-md", default="trigger-rate-report.md",
                         help="Output Markdown report path (default trigger-rate-report.md).")
    p_score.set_defaults(func=cmd_score)

    # stealing
    p_steal = sub.add_parser("stealing", help="Flag siblings with >threshold drop.")
    p_steal.add_argument("before", help="Before trigger-rate-report.json.")
    p_steal.add_argument("after", help="After trigger-rate-report.json.")
    p_steal.add_argument("--threshold", type=float, default=0.10,
                         help="Drop threshold (default 0.10 = 10pp).")
    p_steal.add_argument("--out-json", default="stealing-alerts.json",
                         help="Output JSON alerts path.")
    p_steal.add_argument("--out-md", default="stealing-alerts.md",
                         help="Output Markdown alerts path.")
    p_steal.set_defaults(func=cmd_stealing)

    args = ap.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
