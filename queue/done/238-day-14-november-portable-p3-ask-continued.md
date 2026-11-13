# Chain of 14 November 2026: sessions 5250 to 5264, portable-laptop, window P3, unattended: the AI chat over the warehouse (master plan tool 20), continued

machine: portable-laptop-window3

Written first by session 5200 of chain 235 (`queue/done/235-day-13-november-portable-p3-ask.md`) on 13 November 2026 at about 09:50 UTC, as that chain's rules ask, and to be updated by its session 5249 with what chain 235 did not finish. The first queue number free on origin's main, on every branch and in this machine's shared checkout was 238 (P1 and P2 took 236 and were renumbering as this was written). It takes sessions 5250 to 5264, fifteen numbers after chain 235's last (5249); session 5250 checks each is free on origin's main and on every branch, skips a taken one upward and says so. Model: Fable, high effort.

## Who else runs on this machine

- **P1** (the five tools): sessions 5000 to 5099. The only window that builds.
- **P2** (security): sessions 5100 to 5199.
- **P3** (this window): sessions 5200 to 5299. **It never builds the site and never lands**: no `npm run build`, no `next start`, no `scripts/land_check.py`. Its proof is the Python and Node unit tests and the evaluation runs. It never changes the main checkout's branch or working files; all its work, the queue step included, happens in git worktrees beside `C:\Users\lossa\Documents\erw` named `erw-p3-<N>`, on `wip/5200-<topic>` stacks, with `C:\Users\lossa\Documents\erw\.venv\Scripts\python.exe`.

## Rules for every session

The rules of `queue/done/235-day-13-november-portable-p3-ask.md` hold word for word (precheck first; `git fetch origin` and `origin/main` merged before work; default-neutral; `site/lib/release.ts` untouched; nothing sent or posted; no warehouse data written; no layout redesign; no brand work; the report in short bullets with "Decisions made without you" and "For Samuel's ruling"; no em or en dash; never stop to ask; the weekly limit the only stop). Among them:

- **The non-negotiable: the chat never states a number it did not fetch from the warehouse.** Every number in an answer traces to a query result shown with its table, its source and its date; a question the warehouse cannot answer gets a plain refusal naming what is missing.
- **Model spend:** USD 2 a session and USD 20 the chain, the estimate written before each run, the actual after. No run larger than its estimate.
- **A stack ready to land** gets a requested row in `docs/state/landing_request_portable.md` (its numbering continued; port 5200 upward), committed and pushed.
- **No step waits on a landing or another window.**
- **Files this window owns:** the Ask engine and API route (`site/lib/ask*`, the Ask route), its evaluation and spec (`docs/reviews/ask-*`, the eval sets), `package/llms.txt` where the chat reads it, and their tests. **Not touched:** the `/network` and `/mix` pages and the Grid page composition (P1's), the security files (P2's), the Digest and the Roundup.
- **The queue step is always by name**, and taken from this window's own worktree under its own name (session 5200 of chain 235 says how: the script's `take(file=..., who="portable-laptop-window3")`, the one-commit move rebased on `origin/main` and pushed).

If the two lists below are still empty when session 5250 starts, chain 235 stopped before its session 5249, and session 5250 rebuilds them from chain 235's reports (`archive/sessions/SESSION_5200_REPORT.md` onward), its branches (`git branch -r | grep -E "wip/52"`) and `docs/reviews/ask-eval-2026-11-13.md`, and says so.

Read first: chain 235's note (`docs/state/note_<date>_portable_p3.md`), `docs/reviews/ask-eval-2026-11-13.md` with its last scores, `docs/reviews/ask-faults-2026-11-05.md`, the method note of the chat in `docs/methods/`, `docs/state/landing_request_portable.md`, `CLAUDE.md`.

## Session 5250: the next file, the ground

Long end 1:00. The next file first (the first queue number free on origin's main and every branch, the same machine line, the same goal, at least 14 sessions), committed alone and pushed. Then the precheck, `git fetch`, the worktrees of landed branches removed, and the ground: which of chain 235's stacks landed (each branch an ancestor of `origin/main` or not), the evaluation's last scores by class, the faults still open. Into the report.

## Sessions 5251 to 5256: chain 235's unfinished steps

Long end 1:00 each. One step a session, in chain 235's order, as session 5249 lists them below.

### Unfinished steps (written by session 5249 of chain 235)

(empty until session 5249 writes it)

## Sessions 5257 to 5261: the evaluation's open failures, by class

Long end 1:00 each. One class of failure a session (retrieval, table choice, units, dates, refusals), the largest first: the fix with a test, the evaluation run again on the class's questions and on a held-out slice, the scores before and after written to `docs/reviews/ask-eval-2026-11-13.md`. Never tuned to one question.

### Open failures (written by session 5249 of chain 235)

(empty until session 5249 writes it)

## Session 5262: the evaluation whole, the method note

Long end 1:00. The whole set run once more under the spend rule; the method note of the chat brought up to date with the scores.

## Session 5263: the note

Long end 1:00. `docs/state/note_<date>_portable_p3.md` (its name checked free first) in chain 235's note's form.

## Session 5264: the next file, the landing request, the queue

Long end 1:00. The next file (written by session 5250) updated with what is unfinished and pushed alone; the landing request row for the final stack; then the queue step by name, and that file run the same way.
