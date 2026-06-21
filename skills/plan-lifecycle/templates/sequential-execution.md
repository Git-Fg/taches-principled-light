# Sequential Execution Template

This template is used for Strategy C: Autonomous Sequential Execution. It is used when the plan contains `checkpoint:decision` or `checkpoint:human-action` markers.

## Execution Mechanism

1. **Load context** — read `execution_context` and `context` from the PLAN.md.
2. **For each task/checkpoint**:
   - **IF type="auto"**:
     - Execute inline in the forked context (the files are already loaded). Implementation on files you are editing stays inline.
     - Track all deviations (bugs, critical additions, blockers).
   - **IF checkpoint:decision**:
     - Evaluate heuristic rules (simplest path, plan recommendation, reversibility).
     - Choose the path and log the rationale to the scratchpad.
     - Status update: "Decision: [choice]"
   - **IF checkpoint:human-action**:
     - Check for a CLI/API alternative first.
     - If CLI exists: execute via automation.
     - If no CLI: placehold the result, log in SUMMARY.md as an "unavoidable manual gate".
3. **Handle Deviations** automatically based on priority (Architectural > Bugs/Blockers > Enhancements).
4. **Create SUMMARY.md** documenting all decisions, deviations, and manual gates.
5. **Update ROADMAP.md** and **Commit** the changes.

## Heuristic Decision Rules
- **Default to simplest path** — choose B if A is complex and B is sufficient.
- **Follow plan's recommended option** — respect "recommended" or "preferred" markers.
- **Break ties with reversibility** — choose the option that is easier to undo.
- **Log every decision** — format: `Decision: chose X over Y because [reason]`.
