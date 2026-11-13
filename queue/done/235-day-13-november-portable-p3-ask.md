# Chain of 13 November 2026: sessions 5200 to 5249, portable-laptop, window P3, unattended: the AI chat over the warehouse (master plan tool 20) made trustworthy and broad

machine: portable-laptop-window3

Written on 13 November 2026 at about 09:40 UTC from the owner's prompt for a third Claude Code window on portable-laptop (16 GB). Model: Fable, high effort. It runs about 13 hours, through the weekly reset and beyond. It takes sessions 5200 to 5249 (its window's range is 5200 to 5299); each session checks its number is free on origin's main and on every branch, skips a taken one upward and says so. Numbers up to 234 were taken on origin's main and every branch when this was written (P1 took 233 and P2 took 234 minutes before), so this file is 235.

## Who else runs on this machine

- **P1** (the five tools): sessions 5000 to 5099. The only window that builds.
- **P2** (security): sessions 5100 to 5199.
- **P3** (this window): sessions 5200 to 5299. **It never builds the site and never lands**: no `npm run build`, no `next start`, no `scripts/land_check.py`. Its proof is the Python and Node unit tests and the evaluation runs. It never changes the main checkout's branch or working files (except the queue commits `scripts/chain_queue.py` makes); all its work happens in git worktrees beside `C:\Users\lossa\Documents\erw` named `erw-p3-<N>`, on `wip/5200-<topic>` stacks, with `C:\Users\lossa\Documents\erw\.venv\Scripts\python.exe`.

## Rules for every session

The rules of `queue/done/225-day-18-november-code-continued.md` hold where they apply: precheck first; `git fetch origin` and `origin/main` merged before work; default-neutral; `site/lib/release.ts` untouched; nothing sent or posted; no warehouse data written; no layout redesign; no brand work; the report in short bullets with "Decisions made without you" and "For Samuel's ruling"; no em or en dash. Never stop to ask: a reversible choice goes under "Decisions made without you", anything that waits for Samuel goes under "For Samuel's ruling" with a default, and the chain continues. Never end a session by stopping; the weekly limit is the only stop. Plus:

- **The non-negotiable: the chat never states a number it did not fetch from the warehouse.** Every number in an answer traces to a query result shown with its table, its source and its date; a question the warehouse cannot answer gets a plain refusal naming what is missing.
- **Model spend:** the chat's evaluation runs call the Claude API under the owner's key; USD 2 a session and USD 20 the chain, the estimate written before each run, the actual after. No run larger than its estimate.
- **A stack ready to land** gets a requested row in `docs/state/landing_request_portable.md` (its numbering continued; port 5200 upward), committed and pushed.
- **No step waits on a landing or another window:** the next step is stacked on this window's own branch; when blocked, the next is taken.
- **Files this window owns:** the Ask engine and API route (`site/lib/ask*`, the Ask route), its evaluation and spec (`docs/reviews/ask-*`, the eval sets), `package/llms.txt` where the chat reads it, and their tests. **Not touched:** the `/network` and `/mix` pages and the Grid page composition (P1's), the security files (P2's), the Digest and the Roundup.
- **The queue step is always by name** (`scripts/chain_queue.py next --file <name>`), never bare `next`.

## Session 5200: the next file, the ground

Long end 1:00. The next file first (the same machine line, the same goal, sessions 5250 upward, at least 14 sessions), committed alone and pushed. Then the precheck, `git fetch`, and the ground: `docs/reviews/ask-faults-2026-11-05.md`, `ask-sixty-2026-10-25.md`, `ask-refusals.md`, `ask-replay.md`, the current evaluation set and its last scores. Into the report: the open faults and the last score.

## Sessions 5201 to 5235: the chat made trustworthy and broad

Long end 1:00 each.

- **First** every open row of `docs/reviews/ask-faults-2026-11-05.md` fixed with a test.
- **Then** the evaluation set widened to the whole platform (power, gas, oil, nuclear, renewables, storage, transmission, prices, projects, deals, policy, datacenters): at least 120 questions with expected answers drawn from the warehouse, including questions it must refuse, `docs/reviews/ask-eval-2026-11-13.md`.
- **Then** run, score (correct, correctly refused, wrong, unsupported number), and fix the classes of failure (retrieval, table choice, units, dates, refusals), re-running after each class. Never tune to one question.

## Sessions 5236 to 5247: what remains, the method note

Long end 1:00 each. What remains; then the method note of the chat (internal, `docs/methods/`), with the evaluation's scores before and after.

## Session 5248: the note

Long end 1:00. `docs/state/note_<date>_portable_p3.md` in short bullets: the score before and after by class, the faults closed, what waits in which landing row, the rulings waiting with their defaults, the model spend.

## Session 5249: the next file, the queue

Long end 1:00. The next file (written by session 5200) updated with what is unfinished and pushed alone; then `scripts/chain_queue.py next --file <the next file's name>`, and that file run the same way.
