# Stage-Specific Guidance

## Stage 1: Business Analysis

Focus on understanding what the user actually needs, not just what they asked for.

**Key questions:**
- What problem does this solve?
- Who benefits and how?
- What constraints exist?
- What's explicitly NOT in scope?

**Output:** Refined description, scope boundaries, acceptance criteria

## Stage 2: Architecture Synthesis

Synthesize research, codebase analysis, and business requirements into an architectural overview.

**Key questions:**
- What's the solution strategy?
- What are the key architectural decisions?
- What trade-offs were considered?
- What files will be created/modified/deleted?

**Output:** Architecture overview section in task file

## Stage 3: Decomposition

Break the architecture into ordered implementation steps.

**Key constraints:**
- No step larger than the large estimate threshold - split oversized steps
- Each step must have: clear goal, expected output files, success criteria
- Identify blockers, risks, and mitigations

**Output:** Implementation Process section with ordered steps

## Stage 4: Parallelize

Reorganize steps for maximum parallel execution.

**Key constraints:**
- Identify steps that can run in parallel (no transitive dependencies)
- Assign agent difficulty levels appropriately
- Generate parallelization diagram

**Output:** Steps with parallel execution directives

## Stage 5: Verifications

Add evaluation rubrics for each implementation step.

**Verification levels:**

| Level | When to Use | Configuration |
|-------|-------------|---------------|
| None | Simple operations (mkdir, delete) | Skip verification |
| Single Judge | Non-critical artifacts | 1 judge, standard threshold |
| Panel of 2 Judges | Critical artifacts | 2 judges, median voting |
| Per-Item Judges | Multiple similar items | 1 judge per item, parallel |

**Rubric requirements:**
- Weights must sum to 1.0
- Each criterion has clear, measurable description
- 3-6 criteria typical