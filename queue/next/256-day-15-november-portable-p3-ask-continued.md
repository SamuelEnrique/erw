# Chain of 15 November 2026: sessions 5265 to 5279, portable-laptop, window P3, unattended: the AI chat over the warehouse (master plan tool 20), continued

machine: portable-laptop-window3

Written first by session 5250 of chain 238 (`queue/done/238-day-14-november-portable-p3-ask-continued.md`) on 13 November 2026 at about 18:45 UTC, as that chain's rules ask, and to be updated by its session 5264 with what chain 238 did not finish. It is 256: session 5250 first pushed it as 247, the one number never used below P1's 255, and window P2 pushed its own 247 a moment before, so this file took the first number free above every taken one on origin's main, on every branch and in this machine's worktrees. It takes sessions 5265 to 5279, fifteen numbers after chain 238's last (5264); session 5265 checks each is free on origin's main and on every branch, skips a taken one upward and says so. Model: Fable, high effort.

## Who else runs on this machine

- **P1** (the five tools): sessions 5000 to 5099. The only window that builds.
- **P2** (security): sessions 5100 to 5199.
- **P3** (this window): sessions 5200 to 5299. **It never builds the site and never lands**: no `npm run build`, no `next start`, no `scripts/land_check.py`. Its proof is the Python and Node unit tests and the evaluation runs. It never changes the main checkout's branch or working files; all its work, the queue step included, happens in git worktrees beside `C:\Users\lossa\Documents\erw` named `erw-p3-<N>`, on `wip/5200-<topic>` stacks, with `C:\Users\lossa\Documents\erw\.venv\Scripts\python.exe`.

## Rules for every session

The rules of `queue/done/238-day-14-november-portable-p3-ask-continued.md` hold word for word, which are those of `queue/done/235-day-13-november-portable-p3-ask.md` (precheck first; `git fetch origin` and `origin/main` merged before work; default-neutral; `site/lib/release.ts` untouched; nothing sent or posted; no warehouse data written; no layout redesign; no brand work; the report in short bullets with "Decisions made without you" and "For Samuel's ruling"; no em or en dash; never stop to ask; the weekly limit the only stop). Among them:

- **The non-negotiable: the chat never states a number it did not fetch from the warehouse.** Every number in an answer traces to a query result shown with its table, its source and its date; a question the warehouse cannot answer gets a plain refusal naming what is missing.
- **Model spend:** USD 2 a session and USD 20 the chain, the estimate written before each run, the actual after. No run larger than its estimate.
- **A stack ready to land** gets a requested row in `docs/state/landing_request_portable.md` (its numbering continued; port 5200 upward), committed and pushed.
- **No step waits on a landing or another window.**
- **Files this window owns:** the Ask engine and API route (`site/lib/ask*`, the Ask route), its evaluation and spec (`docs/reviews/ask-*`, the eval sets), `package/llms.txt` where the chat reads it, and their tests. **Not touched:** the `/network` and `/mix` pages and the Grid page composition (P1's), the security files (P2's), the Digest and the Roundup.
- **The queue step is always by name**, and taken from this window's own worktree under its own name: `scripts/chain_queue.py next --file <name>` refuses the window's machine line on the code machine `portable-laptop`, as it should. Session 5250 of chain 238 says how: a worktree detached at `origin/main`, the script's own `take(file=..., who="portable-laptop-window3")` there, the one-commit move rebased on `origin/main` and pushed to main as a fast-forward.
- **The precheck is run from the main checkout** (`C:\Users\lossa\Documents\erw`): in a worktree its `daily_cap` check cannot read the ledger and fails (session 5200's report). It writes only `runs/precheck/` and the duty mark.

Chain 235 stopped inside its third session with files written and not committed. So session 5265 first looks at this window's worktrees (`git worktree list`, `git -C <each erw-p3-*> status -sb`): work a stopped session left there is read, tested and committed under the session that finds it, or said why not, before anything else is built on the branch.

If the two lists below are still empty when session 5265 starts, chain 238 stopped before its session 5264, and session 5265 rebuilds them from chain 238's reports (`archive/sessions/SESSION_5250_REPORT.md` onward, on `wip/5200-ask` and the branches stacked on it), its branches (`git branch -r | grep -E "wip/52"`) and `docs/reviews/ask-eval-2026-11-13.md`, and says so.

Read first: chain 238's note (`docs/state/note_<date>_portable_p3.md`), `docs/reviews/ask-eval-2026-11-13.md` with its last scores, `docs/reviews/ask-faults-2026-11-05.md`, the method note of the chat in `docs/methods/`, `docs/state/landing_request_portable.md`, `CLAUDE.md`.

## Session 5265: the next file, the ground

Long end 1:00. The precheck; then the next file (the first queue number free on origin's main and every branch, the same machine line, the same goal, at least 14 sessions), committed alone and pushed. Then `git fetch`, the worktrees of landed branches removed, and the ground: which of this window's stacks landed (each branch an ancestor of `origin/main` or not), the evaluation's last scores by class, the faults still open. Into the report.

## Sessions 5266 to 5271: chain 238's unfinished steps

Long end 1:00 each. One step a session, in chain 238's order, as session 5264 lists them below.

### Unfinished steps (written by session 5264 of chain 238)

(empty until session 5264 writes it)

## Sessions 5272 to 5276: the evaluation's open failures, by class

Long end 1:00 each. One class of failure a session (retrieval, table choice, units, dates, refusals), the largest first: the fix with a test, the evaluation run again on the class's questions and on a held-out slice, the scores before and after written to `docs/reviews/ask-eval-2026-11-13.md`. Never tuned to one question.

### Open failures (written by session 5264 of chain 238)

(empty until session 5264 writes it)

## Session 5277: the evaluation whole, the method note

Long end 1:00. The whole set run once more under the spend rule; the method note of the chat brought up to date with the scores.

## Session 5278: the note

Long end 1:00. `docs/state/note_<date>_portable_p3.md` (its name checked free first) in chain 238's note's form.

## Session 5279: the next file, the landing request, the queue

Long end 1:00. The next file (written by session 5265) updated with what is unfinished and pushed alone; the landing request row for the final stack; then the queue step by name, and that file run the same way.
