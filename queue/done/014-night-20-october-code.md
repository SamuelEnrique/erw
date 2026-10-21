# Chain of 20 to 21 October 2026, night: sessions 381 to 383, code machine (samueloldlaptop), unattended

machine: code

Written by session 372 (the last session of `queue/done/012-day-20-october-code.md`) so that the code machine does not idle, from `docs/roadmap.md` "This week" items 2 and 8, as that chain asked. Default-neutral: no page's default figure moves, no ruling is made. Rulings in force: `docs/roadmap.md` "Rulings" and the chains of 20 October (`queue/done/010-night-20-october-code.md`, `queue/done/012-day-20-october-code.md`). Read `docs/state/review_2026-10-20_day_code.md` first: sessions 367 to 371 wait on `wip/367-372-day`, unlanded after a memory stop, with every command under "To finish".

## Rules for every session of this chain

Every python command of this chain names the repository's interpreter, `.venv\Scripts\python.exe` on Windows.

1. **Precheck first.** `python scripts/precheck.py --what "session <N>"`; exit 1: stop, start no work.
2. **Unattended.** Reversible choices under "Decisions made without you"; irreversible ones under "For Samuel's ruling", undone.
3. **A failed session does not stop the chain.** Its work stays on a pushed `wip/` branch and the next session starts.
4. **Landing.** `python scripts/freeze.py status`; a snapshot before and after, each its own command, every difference listed; check-values on the landing build; pull and merge origin/main first (the data machine lands today too); list remote `task/` branches and trial-merge them. NO LANDING 14:00 to 16:15 UTC or 22:30 to 23:45 UTC.
5. **No warehouse data written; no pulls; model spend USD 0.**
6. **One heavy process at a time** (the build mutex, `runs/build.lock`); `python scripts/duty.py beat` before each build. A job Claude Code stops for low memory is not started again unattended: the session goes to `wip/`, writes the exact commands under "To finish", and the next session starts.
7. **Writing:** no em dashes. tokens.css and the shared components only; Impeccable once per page touched; screenshots at 1280 and 390.
8. **Reports:** `archive/sessions/SESSION_<N>_REPORT.md` as the chain of 20 October's: "Read these first", "What to review" with addresses, checks with exit codes, the landing and its comparison, "Decisions made without you", "For Samuel's ruling".
9. **Last step of the last session: the queue.** `python scripts/chain_queue.py next`: exit 0, run the printed file, starting with its precheck; exit 3, say CHAIN DONE.

## Session 381: the waiting branch landed, then the five tools' replications and cross-checks

Long end 3:00. Model spend cap USD 0. Pulls: none.

- First, if `wip/367-372-day` is not on main: run "To finish" of `docs/state/review_2026-10-20_day_code.md` in its order (session 370's cycle, the landing checks with `FLOOR=1`, the landing, the download check against production, the branches deleted). Record it in this session's report.
- Then roadmap item 2, "Five tools sellable": for each of the battery, generator, datacenter, Automated Analysis and Grid tools, a table in `docs/reviews/packs/<tool>.md` of what the tool has and lacks against the item's "done": a method note (signed or not), a replication a reader can run (where it is, and whether it runs today: run it), a cross-check table against published figures (`site/scripts/check-cross-checks.mjs` and `check-grid-replication.mjs` show the form), a decisions block. Build what is missing and needs no ruling: a replication that reruns a page's default figure from its downloads, a cross-check row whose published figure the ERW already holds with its source. A figure the ERW does not hold is listed, not fetched.
- Done: every tool's row of that table filled; each new replication and cross-check run with its exit code; no page's default figure moved (check-values passes). Land.

## Session 382: the trader path, click by click

Long end 2:00. Model spend cap USD 0. Pulls: none.

- Roadmap item 8: the trader path (the users the roadmap names) through `/cost-of-power/seller`, `/cost-of-power/battery` and `/board`, written click by click in `docs/reviews/trader-path.md`: each step's address, what the reader does, what they should see (the checked figure with its key), and what a trader would ask that the page does not answer (listed, not built). Walk it on the local build with the browser and take a shot at each step at 1280 and 390 into `docs/brand/review-382/`. The On.Energy walkthrough gets the same form if `docs/reviews/` holds its scope; if not, list what is needed.
- No page changes unless a step finds a fault that needs no ruling (a broken link, a figure that fails its check): fix it with its test and say so. Land if anything under `site/` changed; otherwise push the documents with the next landing.

## Session 383: the note, and the queue

Long end 0:45. Model spend cap USD 0. Pulls: none.

- `docs/state/review_2026-10-21_night_code.md`: one line a session with its address, every screenshot folder, every decision made without Samuel, every item waiting for him, the state of `queue/next` for this machine (`python scripts/chain_queue.py list`). If nothing waits for this machine, write the next chain from `docs/roadmap.md` "This week" (two to three sessions, default-neutral, `machine: code`, the next free number), commit and push it to main with its snapshot, so the machine does not idle; say so in the note. Push, then the queue step.
