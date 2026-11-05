# Chain of 21 October 2026, day and evening: sessions 460 and 476 to 482, data machine (lab-desktop), unattended

machine: data

Written by session 459, the last session of `queue/done/018-day-21-october-data.md`, as its 459 asks: at least eight sessions, from the next free numbers (460, then 476 onward past the code machine's 461 to 475). A number found taken is skipped upward and said so. Drawn from that chain's "To finish" lines and findings, `docs/roadmap.md` items 5, 6 and 9, and the open items of `docs/state/note_2026-10-22_day_data.md`. Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, no letter is sent; a change that alters what a page shows or how the daily run behaves goes on its own wip/ branch with its tests, not landed, for Samuel's ruling.

## Rules for every session

Every python command uses .venv\Scripts\python.exe (Git Bash at C:\Program Files\Git\bin\bash.exe for a shell script). Precheck first (exit 1: stop). Unattended: do not stop to ask; reversible choices under "Decisions made without you"; irreversible ones under "For Samuel's ruling", undone. A failed session stays on a pushed wip/ branch and the next starts. A job stopped for low memory is started again once, in the foreground; twice, the session goes to wip/ with its "To finish" and the next starts. Every data write under the data lock; the scheduled daily run (17:00 UTC, up to six hours) holds it first, and a session that finds it held does its lock-free work and writes the rest under "To finish". **No session waits for a time of day or for the lock** (session 434's rule). **A session marked "not before HH:MM UTC" that starts earlier is not run**: its report says so in one line and its part is copied, unchanged and with its mark, into the next file; the chain goes on. THE DATABASE GATE: before any load or any read heavier than a count, `python scripts/db_probe.py` (exit 0 under 3 seconds); exit 1 means no load this session, and the load goes under "To finish". Pulls only as a session's part names them, under its ceiling, nothing from a paused publisher, no new host without its robots file and terms read. Model spend USD 0. NO LANDING 14:00 to 16:15 UTC; the 22:30 to 23:45 UTC cutoff is Sundays only. coverage.csv rebuilt with --only, never whole, on this machine; the release package spliced, not rewritten. When a deployment does not appear, read the commit's status (`GET /repos/SamuelEnrique/erw/commits/<sha>/status`; Vercel rate-limited deployments on 21 October), take the after snapshot anyway and say so. Poll GitHub's API at most once a minute, or with this machine's GH_TOKEN for reads. `chain_queue.py next` commits the move and does not push it: pull main first (restore the main checkout's copies of files the branch carries, after checking they equal the branch's), then push the move with snapshots. `licenses.py status` writes files: run it in a worktree. A script's `--help` may run it (session 438: `ercot_peak_premium.py` has no options): read its source first. The main checkout stays on main, with the daily run's uncommitted page files as they are. No em dashes. Reports as session 364's, with "For Samuel's ruling" one item a line. Read `docs/state/note_2026-10-22_day_data.md`, `docs/state/morning_2026-10-22.md` and sessions 452 to 459's reports first; do not redo their work. Last step of the last session: the note, the next file if anything a session can do without a ruling remains (else none, and the note says so), the landing, then python scripts/chain_queue.py next.

## Session 460: restore_tables.py, the archive's latest run before an older stored copy

Long end 1:30. Pulls: the archive bucket only. Session 454's finding: for `price_board_spreads` and `policy_reads_evidence`, `warehouse/restore_tables.py --no-redivis --out-dir` restored "a copy in the archive bucket" that was the same older version this machine held, not the archive's latest run (GitHub's of 20 October), and `prove.py` still found them behind. Find why a stored copy was taken over a newer run (its check of the copy against the latest run's row count or run id). Then fix it so that a stored copy is used only when it is the latest run's, with a test that fails before the fix. Check with `--out-dir` into a scratch folder on the two tables: the latest run's rows (5,143 and 2,436). No change to `warehouse/output`. Land.

## Session 476: consolidate.py check against the members folder

Long end 1:00. Pulls: none. Session 452's finding: `consolidate.py check --family iso_rtm_hub_prices` reads MISMATCH, while its four members add up to the table's 57,312 rows. What it compares with is the older copies in `warehouse/output/members/`. Find whether the check should read the members it would split now, or `members/` should be refreshed by `build` (which said "unchanged since the split; not rewritten"). Fix it with a test, so that the check fails only on a real difference. No consolidated table rewritten. Land.

## Session 477: the gate inside the loader (a branch, not landed)

Long end 1:30. Pulls: none. On `wip/477-loader-gate`, from `wip/455-loader` (so the two can be ruled together). `warehouse/supabase/load.py` asks `scripts/db_probe.py`'s `probe()` before its first write; on exit 1 it loads nothing, writes "the database gate is closed (<time> s): nothing loaded" and exits 75 (a skip under `warehouse/health.py`). It also waits a few seconds between tables after a table that wrote more than 100,000 rows. With tests. The report: what the daily run would have done at 23:30 UTC on 20 October.

## Session 478: the stale tile (a branch, not landed)

Long end 1:30. Pulls: none. On `wip/478-stale-tile`. Session 433: a board tile kept by `warehouse/derived/page_keep.py` five days behind the board's newest day still reads `status: ok`. A tile whose last day is two or more days behind its group's newest gets `status: stale` and the tile's own line ("held from <day>: the newer build was shorter"), in `board.json` only, with tests. The site's rendering of `stale` is the code machine's, named in the report. Measured on the board of main at `e37f529f` (ERCOT 15 October against 20 October).

## Session 479: the streak's missing hours (a branch, not landed)

Long end 1:30. Pulls: none. On `wip/479-streak`. Session 387: `health_days.json` counts a day missing only when a job made no run at all, so six hours without a 15-minute run left 21 October green. `warehouse/health.py` writes, for each day and job, the runs against the expected count, and a day where a job made fewer than half its expected runs is marked `short`: shown, and counted against the streak only if Samuel rules so (a constant, off). With tests. The report: the days of 6 to 21 October that would be short.

## Session 480: 21 October, its whole day (not before 23:00 UTC)

Long end 1:00. Pulls: none. Carried from sessions 457 and 458. Not run before 23:00 UTC (the rules).
- `lock.py status`.
- Whether pg_cron dispatched `erw-daily` at 14:00 UTC (`runs/s387_dispatch.py`, read only).
- `warehouse/health.py summary --day 2026-10-21 --out runs/<folder>` copied over `queue/summary/2026-10-21-health.md`, sessions 387, 439 and 457's "## Root causes" kept. For every failed step after 09:11 UTC, its root cause, one paragraph each.
- This machine's daily run: when it took and released the lock, what it wrote and committed, and the Redivis uploads of the tables that moved (`ercot_node_prices_hourly`, `eia930_all_storage`: session 437).
- One line on whether 21 October counts green. `site/data/health_days.json` read, not written.

## Session 481: the board, the map and the node days after the daily commit (not before 23:00 UTC)

Long end 1:00. Pulls: none. Carried from session 458. Not run before 23:00 UTC. If this machine's daily run of 21 October has committed its page files:
- `board.json` on main: ERCOT's day-ahead and real-time tiles against CAISO's, NYISO's and SPP's newest days;
- `map.json`'s build date (9 October before);
- `node_basis_daily`'s real-time days (22 before) and `ercot_node_prices_hourly`'s rows against 500,000;
- `prove.py --fresh --only '^datacenter_queue_positions$'` (session 454 left it for the daily).

If the run has not committed, the checks run on the uncommitted files and the commit goes under "To finish".

## Session 482: the note, the next file, and the queue

Long end 1:00. `docs/state/note_2026-10-22_evening_data.md` in session 364's form: what each session landed, pulls against ceilings, the probe's log, decisions made without Samuel, waiting for him highest value first, the other machines. Then python scripts/chain_queue.py list: if nothing waits for this machine and a session can still do something without a ruling, write the next file before the queue step, at least eight sessions or as many as there is such work, machine: data, numbered from the next free number. Commit and push it to main on its own with snapshots, and say so in the note. If nothing can be done without a ruling, write no file and say so. Land this chain (merge origin/main, the whole suite, `scripts/freeze.py status`, rule 8's snapshots, a task/ branch, not between 14:00 and 16:15 UTC). Then python scripts/chain_queue.py next; exit 3: say CHAIN DONE.
