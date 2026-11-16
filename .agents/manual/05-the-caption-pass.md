# The caption pass — write, score, rewrite, then gate

> Part of the engine manual. Index, read order and precedence: [AGENTS.md](../../AGENTS.md).

A caption is two passes, because writing and judging are different jobs and one pass does both
badly. It is the same shape as the batch: score before you spend.

1. **Write** the three parts to the formulas in [Content rules](11-content-rules.md) — the title,
   the description of 3–5 sentences doing five jobs in order, the 4–5 tags — not to taste.
2. **Score it yourself** out of 100 on the page's five weights ([Content
   rules](11-content-rules.md)) and **rewrite anything under 80**, then score the rewrite. The
   number is not decoration: it goes in `plan/SCRIPT.md` and `queue` reads it.
3. **Run the grounding test on the title:** could this title sit on a different car's post? If yes
   it is a mood line, not a headline — rewrite it. `Doors That Opened To Sky` passed every length
   rule in this file and still failed that one test.
4. **Gate it.** `queue` checks the caption with `tools/caption.py` before a row exists: the word
   and sentence bands, the year and model in the title, the power word, the second person, the
   question, the tag rule, and the 80 floor. A failure is a rewrite; `--force` queues it anyway
   and records why in the row's `error` column.

A caption is never written once. The sentence that reads fine to its author is the one that scores
64, and 64 is the caption nobody answers.
