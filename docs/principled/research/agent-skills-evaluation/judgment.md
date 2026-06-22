# Chosen Angle

Distill the Anthropic `skill-creator` evaluation methodology into a **runtime-agnostic evaluating-skills skill** that preserves its core loop (evals → parallel runs → grading → aggregation → iteration → description optimization) while collapsing every Claude-Code-specific dependency (browser viewer, `claude -p` subprocess, `claude -p` stream-json parsing, MCP-server-rendered HTML) into orchestrator-native equivalents that work in (a) interactive agents like Claude Code and Cursor, (b) headless invocations like `claude -p` and CI, and (c) alternative runtimes like Reasonix and kimi-code.

The deliverable is **two artifacts**: (1) the actual `evaluating-skills/SKILL.md` that lives in `taches-principled-light/skills/`, and (2) this research record showing how the design was derived from the official source and adapted for portability.

# Why this angle over alternatives

- **Over replicating skill-creator verbatim:** the official skill is Claude-Code-centric (uses `claude -p` subprocess, `.claude/commands/` command-file injection, `webbrowser.open()` for the HTML viewer). Taches-principled-light ships as a **multi-runtime plugin** (Claude Code + Codex + Cursor manifests), and the user explicitly named Reasonix and kimi-code headless CLI. Verbatim import would not work for the majority of targets.

- **Over building only a headless-mode skill:** headless-only loses the rich interactive iteration loop Anthropic designed. The same loop, with graceful degradation, serves both audiences.

- **Over abstracting skill-creator's loop without referencing its schemas:** Anthropic's `evals.json`, `grading.json`, `benchmark.json`, and `history.json` are public schemas. Re-using them means existing skill-creator outputs are importable, and tooling is interoperable.

- **Over focusing only on description optimization:** trigger accuracy is one of three things skill-creator teaches (alongside output-quality grading and iteration). Trimming to description-only loses the output-quality loop, which is where most of the local marketplace's value sits (the marketplace's skills produce artifacts, not just skill-loading events).

# Hypothesis to validate or refute

**Hypothesis:** the skill-creator loop is a **5-stage pipeline** — `Capture → Eval → Run → Grade → Iterate → Optimize-trigger` — of which only stages 3 (Run) and 5 (Optimize-trigger) are runtime-specific. Stages 1, 2, 4 are pure orchestration the calling agent already has, and can be reframed as platform-agnostic imperatives. The runtime-specific bits can be factored into **adapter stubs** that an interactive agent fills with subprocess calls and a headless agent fills with inline grading.

If the hypothesis holds: a single `evaluating-skills/SKILL.md` with inline adapters can serve both audiences, and the marketplace can drop `skill-creator` as a single-CLI dependency.

If the hypothesis fails: the answer is to ship two skills (an interactive and a headless variant), and the marketplace needs adapter-aware routing. This is more invasive and is the contingency plan.

# Out of scope (explicit non-goals)

- **Re-implementing skill-creator's Python scripts.** The local marketplace does not need its own `run_eval.py`, `run_loop.py`, etc. — they assume Claude Code. The generalistic skill teaches the *methodology*; the calling runtime picks the implementation.
- **Adding a packaged `.skill` output.** Anthropic's `package_skill.py` produces a binary `.skill` file. The local marketplace ships directory skills, not packaged files. Not a gap to address here.
- **Building a browser-based viewer.** The marketplace does not have a web frontend. Inline report files are the right output medium.
- **Description optimization at scale (60/40 train/test split, 3-run averages).** This requires many parallel agent invocations. The generalistic skill teaches *how* to do it with whatever parallelism the runtime supports; the runtime decides whether to do it.
- **Maintaining the marketplace's existing 28 skills' eval infrastructure.** That's a separate task — this research designs the *methodology skill*, not the per-skill evals.
- **Skill-creator's "Blind comparison" and "Analyzer" subagents.** These are quality-of-life extras, not core methodology. Worth mentioning in passing; out of scope to port.