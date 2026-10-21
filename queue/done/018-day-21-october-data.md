# Chain of 21 October 2026, day: sessions 452 to 459, data machine (lab-desktop), unattended

machine: data

Written by session 440, the last session of the owner's `queue/done/016-night-21-october-data.md`, as its 440 asks: at least eight sessions, numbered from the next free number above 450. 441 to 451 are the third machine's and 461 to 475 the code machine's (`019`), so this file holds 452 to 459. A number found taken is skipped upward past 475 and said so. Drawn from that chain's "To finish" lines, `docs/roadmap.md` items 5, 6 and 9, and the open items of `docs/state/morning_2026-10-22.md`. Default-neutral: no page's default figure moves, no ruling is made, nothing is released on Redivis, no letter is sent. Session 440 withdrew this machine's `017-day-21-october-data-pm.md`: its two sessions repeated 439 and 440, and its first would have waited for the daily runs. The sessions that need today's daily runs are placed last here (457 and 458), so that no session waits for a time of day.

## Rules for every session

Every python command uses .venv\Scripts\python.exe (Git Bash at C:\Program Files\Git\bin\bash.exe for a shell script). Precheck first (exit 1: stop). Unattended: do not stop to ask; reversible choices under "Decisions made without you"; irreversible ones under "For Samuel's ruling", undone. A failed session stays on a pushed wip/ branch and the next starts. A job stopped for low memory is started again once, in the foreground; twice, the session goes to wip/ with its "To finish" and the next starts. Every data write under the data lock; the scheduled daily run (10:00 Pacific, 17:00 UTC, up to six hours) holds it first, and a session that finds it held does its lock-free work and writes the rest under "To finish": **no session waits for a time of day or for the lock** (session 434's rule). THE DATABASE GATE: before any load or any read heavier than a count, `python scripts/db_probe.py` (session 431; exit 0 under 3 seconds; it appends to runs/db_probe.log); exit 1 means no load this session, and the load goes under "To finish". Pulls only as a session's part names them, under its ceiling, nothing from a paused publisher, no new host without its robots file and terms read. Model spend USD 0. NO LANDING 14:00 to 16:15 UTC; the 22:30 to 23:45 UTC cutoff is Sundays only. coverage.csv rebuilt with --only, never whole, on this machine; the release package spliced, not rewritten. Vercel rate-limited deployments from about 06:30 UTC on 21 October: when a deployment does not appear, read the commit's status (`GET /repos/SamuelEnrique/erw/commits/<sha>/status`), take the after snapshot anyway and say so. Poll GitHub's API at most once a minute, or with this machine's GH_TOKEN for reads. `chain_queue.py next` commits the move and does not push it: pull main first, then push the move with snapshots. `licenses.py status` writes files: run it in a worktree. The main checkout stays on main, with the daily run's uncommitted page files as they are. No em dashes. Reports as session 364's, with "For Samuel's ruling" one item a line. Read `docs/state/morning_2026-10-22.md` and `docs/state/database_2026-10-21.md` and sessions 431 to 440's reports first; do not redo their work. Last step of the last session: the note, the next file if nothing waits, then python scripts/chain_queue.py next.

## Session 452: ercot_peak_premium, refreshed

Long end 2:00. Pulls: none. Session 438 held it: its inputs are the members of two consolidated tables (`ercot_rtm_hub_prices_<year>` and `ercot_rtm_hub_prices`), and the machine was short of memory. First, the free memory (`Get-CimInstance Win32_OperatingSystem`, FreePhysicalMemory) and the sizes of the two families. Then `warehouse/consolidate.py split --family` for the families the builder reads, `warehouse/derived/ercot_peak_premium.py`, and `warehouse/consolidate.py build --family` for the same families, all in the foreground, under the lock. Then check with `consolidate.py check` that the consolidated tables have the rows they had. Then validate, archive, coverage `--only` for the two peak premium tables, and load through the gate with rule 8's snapshots. The report gives the two tables' newest month before and after. "For Samuel's ruling": a step for it in `warehouse/run_data_machine.sh`, since no scheduled run can build it today.

## Session 453: the NOAA weather tables, refreshed

Long end 2:00. Pulls: NOAA's public station data through `warehouse/connectors/noaa_grid_weather.py --refresh`, under the year's ceiling of 6,000,000 rows (2,812,746 used on 21 October; `warehouse/raw/noaa_grid_weather/ceiling.json`). Free memory first, as in 452. The station table holds 4.7 million rows. Then validate, archive, and coverage `--only` for each table that moved; a load only for tables in `warehouse/supabase/live_set.yaml`, through the gate. The report: the newest hour before (10 and 11 October) and after, and the rows counted.

## Session 454: the archive's five mismatches, closed

Long end 1:00. Pulls: the archive bucket, and Redivis's metadata. Session 436's five (`docs/state/archive_proof_2026-10-21.csv`):
- `policy_reads_evidence` (this machine behind, 1,781 rows): restored from the archive (`scripts/sync.py --tables`, the archive first).
- `grid_network_links` (the copy here older): `--refresh`.
- `price_board_spreads`, `caiso_reliability_daily` and `datacenter_queue_positions` (both differ): read with `prove.py --refine` to tell a revision from two runs, and the newer side kept.

Under the lock. Then `prove.py --fresh --only` on the five: the count equal after. No load.

## Session 455: the loader, values not stamps (a branch, not landed)

Long end 2:00. Pulls: none. On `wip/455-loader`, with tests, not landed, for Samuel's ruling.
- (a) Session 384's draft of the guard (its report, part c): a table older by its stamps but equal in value loads as unchanged.
- (b) `sync_table` writes only the rows whose values changed, not the rows whose `retrieved_at` moved. Session 438 wrote 30,232 rows for 8 changed values.
- (c) `VACUUM (ANALYZE)` of `series` only when the load wrote or deleted more than a share of it (say 1%), else `ANALYZE` alone.

Each with its test. Measured with `load.py --dry-run` and the row hashes, never by a load. The report gives, for the loads of sessions 374, 432 and 438, the rows each would have written under (b).

## Session 456: the live set's two largest tables, sized for a ruling

Long end 1:00. Pulls: none. Reads only, behind the gate. For `node_basis_daily` (957,969 rows) and `ercot_rtm_price_adders` (601,810 rows, no page reads it): which pages read each, what rows each page reads (`site/lib/`), and what `series` would hold under each choice.
- A window for `node_basis_daily` of 35, 90 or 365 days, or none.
- The pages reading their own files as `/board` does.
- `ercot_rtm_price_adders` out of the live set.

Give each choice's rows and estimated megabytes, and its effect on `series_pkey` and `series_entity`. Then time three pages' reads now. `docs/state/live_set_size_2026-10-21.md`. No change to `live_set.yaml`.

## Session 457: 21 October, its whole day

Long end 1:00. Pulls: none. Placed here so that the day's runs have run: GitHub's daily is dispatched at 14:00 UTC and this machine's starts at 17:00 UTC. Start with `lock.py status`.
- **If this machine's daily run still holds the lock**: do GitHub's side now, and put this machine's under "To finish" for the next chain. Do not wait.
- **GitHub's side**: whether pg_cron dispatched `erw-daily` at 14:00 UTC (`runs/s387_dispatch.py`, read only), and `warehouse/health.py summary --day 2026-10-21 --out runs/<folder>` copied over `queue/summary/2026-10-21-health.md`, sessions 387 and 439's "## Root causes" kept. For every failed step after 08:12 UTC, its root cause, one paragraph each.
- **This machine's side**: when its daily run took and released the lock, and what it wrote and committed (`site/data/board.json` with ERCOT through 20 October or later; `site/data/map.json`; `dm_node_rt`'s days gained; the Redivis uploads of the tables that moved).

One line on whether 21 October counts green. `site/data/health_days.json` read, not written.

## Session 458: the board, the map and the node days after the daily commit

Long end 1:00. Pulls: none. If this machine's daily run of 21 October has committed its page files, check what they hold:
- `board.json`'s ERCOT tiles (day-ahead and real time) against CAISO's, NYISO's and SPP's newest days (session 433's three causes);
- `map.json`'s build date (it was 9 October);
- `node_basis_daily`'s real-time days (22 before: session 435), with `ercot_node_prices_hourly`'s rows against 500,000.

If the run has not committed by the session's start, the same checks run on the uncommitted files and the commit goes under "To finish". A tile still behind gets its cause, and a fix with its test where the cause is code.

## Session 459: the note, the next file, and the queue

Long end 1:00. `docs/state/note_2026-10-22_day_data.md` in session 364's form: what each session landed, pulls against ceilings, the probe's log through the day, decisions made without Samuel, waiting for him highest value first, the other machines. Then python scripts/chain_queue.py list: if nothing waits for this machine, write the next file before the queue step, at least eight sessions, machine: data, numbered from the next free number, from this chain's "To finish" lines, docs/roadmap.md items 5, 6 and 9, and the notes' open items; commit and push it to main on its own with snapshots; say so in the note. Land this chain (merge origin/main, the whole suite, `scripts/freeze.py status`, rule 8's snapshots, a task/ branch, not between 14:00 and 16:15 UTC). Then python scripts/chain_queue.py next.
