# Research plan

A step-by-step execution list. Each step has a goal, the sub-question(s) it advances, the queries / fetches to run, and the expected output section in `document.md`.

## Step 1 — Survey the popular marketplaces (sub-questions 1, 2, 3, 4)

**Goal:** Measure the empirical body length, references/ presence, router language, and description word count distribution in `obra/superpowers`, `anthropics/skills`, and `heygen-com/skills-legacy`.

**Queries / fetches:**
- `mcp__mcp-coderepo__github_repo anthropics/skills` (file tree)
- `mcp__mcp-coderepo__github_repo obra/superpowers` (file tree under `skills/`)
- Inspect SKILL.md line counts in both via `gh api` or `curl` (if MCP can't list the contents)
- For HeyGen, already have the layout from background research; sample 2–3 SKILL.md files via `mcp__mcp-coderepo__fetch` or the GitHub fetch tool

**Expected output in `document.md`:** Three subsections under "## Sub-question N":
- Body length table (skill name, marketplace, line count, has-references)
- Hub + references prevalence
- Router language samples (verbatim quotes from 3–5 skills)
- Description word count distribution

## Step 2 — Re-read SkillsBench §4.2 (sub-question 8)

**Goal:** Quantify the paper's findings on Skills quantity and complexity.

**Queries / fetches:**
- `mcp__mcp-searxng__extract url=https://arxiv.org/html/2602.12670v1 query="Skills quantity complexity 2-3 skills optimal moderate length"` (RAG-style extraction)
- Or re-read the section directly from the already-fetched arXiv markdown

**Expected output in `document.md`:** "## Sub-question 8: SkillsBench design factors" — table of findings (5, 6, 7) with effect sizes.

## Step 3 — Routing-eval methodology survey (sub-questions 6, 7)

**Goal:** Determine whether token-overlap benchmarks have any published correlation with LLM-judge routing scores, and what the cost/benefit picture looks like.

**Queries:**
- `mcp__mcp-searxng__web_search "skill description routing benchmark LLM judge correlation"`
- `mcp__mcp-searxng__web_search "agent skill routing evaluation methodology"`
- `mcp__mcp-searxng__web_search "Eugene Yan LLM evaluator skill selection"`

**Expected output in `document.md`:** "## Sub-questions 6 & 7: routing eval calibration" — verdict: token-overlap is a useful first-pass filter; LLM-judge is the gold standard but ~100x more expensive; no published correlation coefficient; the two should be used together.

## Step 4 — Cross-check the listing budget numbers (sub-question 5)

**Goal:** Confirm `skillListingBudgetFraction = 0.01` and `skillListingMaxDescChars = 1536` from a second source.

**Queries:**
- `mcp__mcp-searxng__web_search "Claude Code skillListingBudgetFraction changelog"`
- `mcp__mcp-searxng__web_search "Claude Code 2.1.129 skill budget"` (try different date or phrasing if first one is sparse)

**Expected output in `document.md`:** "## Sub-question 5: budget mechanics" — confirmation table, possibly a third source if found.

## Step 5 — Synthesis

**Goal:** Cross-cut the sub-question answers into a single thesis.

**Output:** `## Synthesis` section in `document.md` — 3–5 paragraphs that answer:
- Is the hub + references pattern the right move for a complex multi-operation skill? (Yes, dominant convention.)
- What router language should we use? (Mixed; imperative wins on routing accuracy; descriptive wins on readability.)
- What description word count is the empirical sweet spot? (~30–60 words for narrow skills, ~150 max for complex.)
- Is our token-overlap benchmark good enough? (Yes for first-pass; pair with LLM-judge for production routing confidence.)

## Step 6 — Open questions

**Goal:** Honest list of what the research did not settle.

**Output:** `## Open questions` section — things like "no published correlation between token-overlap and LLM-judge routing scores," "router language A/B not benchmarked at scale," "we did not sample 5+ marketplaces to confirm the 500-line split threshold."

---

## Execution order

Steps 1, 2, 3, 4 are independent. They can run in parallel via four subagent dispatches, or sequentially in the main agent. Given the sub-question scaffolding notes (1+2+4 share a corpus; 6+7 share web-search budget), the recommended dispatch is:

- **Dispatch A (subagent generalist, edit access):** Steps 1 + 4. Survey `anthropics/skills` and `obra/superpowers` SKILL.md files, measure line counts, identify hub + references patterns, sample router language, list description word counts. Cross-check the budget numbers if Anthropic has a public changelog entry. Returns a structured table.
- **Dispatch B (subagent explorer, read-only):** Step 2. Re-read SkillsBench §4.2 and extract the findings on quantity, length, complexity with the exact numbers.
- **Dispatch C (subagent explorer, read-only):** Step 3. Web search for token-overlap / LLM-judge correlation and Eugene Yan's evaluator methodology. Returns a verdict and a list of any published benchmarks.

The main agent writes `Synthesis` and `Open questions` in step 5–6 after merging the three dispatch results.

## Self-check before declaring done

- Every sub-question has a verdict in `document.md`.
- At least one citation per sub-question.
- The Synthesis section answers all three of: structural pattern, router language, description budget.
- The Open questions section is non-empty.
- No "as an AI" / "in conclusion" filler.
