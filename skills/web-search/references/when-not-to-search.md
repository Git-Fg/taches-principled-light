# When NOT to Search

Searching is not always the right move. This file is a reference for when to skip the search and either answer from training knowledge, re-route to a different skill, or admit the question is unanswerable.

## The five stop conditions

### 1. The answer is in the conversation already

If the user supplied the answer inline, do not search. Re-quoting their own words back at them is bad UX and signals you didn't read the conversation.

**Example**: User: "I just released version 2.0 of my library. What's the best way to announce it?" Do not search for "library release announcement best practices" — the user just told you the context.

### 2. The question is about the model's own behavior, design, or capabilities

Questions like "what model are you", "what can you do", "how do you handle X" are about the runtime, not the world. Search the model's own documentation, its skills, or its configuration — not the open web.

**Re-route to**: the relevant plugin/skill (e.g. for capabilities, the `mavis` skill; for runtime config, the `claude-cli` skill plus Read `.claude-plugin/marketplace.json` for the installed catalog).

### 3. The question requires private or internal context

Questions about the user's own codebase, the user's own data, internal company documents, or a specific prior conversation. The open web cannot have these. Searching is a waste of time and risks surfacing adjacent but unrelated public content.

**Re-route to**: the file-search, code-search, or context skills. For the user's own prior work, use the session history.

### 4. The question is speculative about the future

Questions like "will X release in 2027", "what will AI look like in 10 years", "will the stock market crash next quarter". The open web has opinions, not answers. Searching surfaces confident-sounding speculation that is no more accurate than random guessing.

**Action**: tell the user the question does not have a public answer; offer to discuss the question as a thought exercise (without pretending to predict).

### 5. The question is value-laden or contested

Questions about taste ("what's the best X"), ethics in a specific situation ("is it OK to X"), or any question where the open web is mostly noise. There is no authoritative source for "what is good" or "what is right".

**Action**: surface the relevant considerations honestly; do not pretend a search result settles the question. If the user wants a personal recommendation, ask them about their values, not the internet.

## Stops that look like searches but aren't

Some questions LOOK like search queries but should be handled by other skills:

| User query | Looks like search but... | Re-route to |
|------------|--------------------------|-------------|
| "find me a function that does X" | Search inside a codebase | code-search skill |
| "where is the auth code in this repo" | Local file search | file-search skill |
| "show me my last 5 sessions" | Internal session history | session-analytics skill |
| "what plugins do I have installed" | Local config | `claude plugin list` via Bash + Read `.claude-plugin/marketplace.json` |
| "what is the syntax for Python decorators" | Could be search, but training knowledge is faster and accurate | Answer from training |

## The "is this a search?" heuristic

Before searching, ask:

1. **Could the open web have a better answer than my training data?**
   - Yes (current events, recent releases, new regulations) → search
   - No (timeless facts, established practices) → answer from training
2. **Does the question require specific private context?**
   - Yes (user's codebase, internal docs) → re-route, do not search
3. **Is the question speculative or value-laden?**
   - Yes → tell the user, do not search

If all three answers are "no", you have a search. If any is "yes", handle it the way that answer says.

## The cost of searching

Every search has a cost: tokens, time, and the risk of the model anchoring on a noisy first result. The default-failure is to search when not needed. The discipline is to ask "is this a search?" before each query, not after.
