# Chain of 21 October 2026, night: sessions 431 to 440, data machine (lab-desktop), unattended

machine: data

The data machine's night, written by the owner on 21 October at 22:00 Pacific. Session numbers 431 to 440 are reserved for this file (the code machine's self-written chains use 416 to 430; the third machine's 441 to 450); a number found taken is skipped upward past 450 and said so. Samuel's standing instruction: the machines run 24 hours a day; a chain that ends with nothing waiting writes the next file before it idles.

The one fact that shapes this chain: since about 23:30 UTC on 20 October Supabase answers the heavier reads with statement timeouts (57014); production prints "The live set could not be read" on some pages, every site build fails, and the code machine's work waits on branches. The likely cause is this machine's loads of 20 October (the restore of 71 tables, the node real-time pull, the live-set load) against the compute tier's disk budget. So: this chain reads the database before it writes to it, writes to it only through a gate, and does its file and archive work first.

## Rules for every session

Every python command uses .venv\Scripts\python.exe (Git Bash at C:\Program Files\Git\bin\bash.exe for a shell script). Precheck first (exit 1: stop). Unattended: do not stop to ask; reversible choices under "Decisions made without you"; irreversible ones under "For Samuel's ruling", undone. A failed session stays on a pushed wip/ branch and the next starts. A job stopped for low memory is started again once (the chain worker sets CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP=1); twice, the session goes to wip/ with its "To finish" and the next starts. Every data write under the data lock; the scheduled daily run (10:00 Pacific, up to six hours) holds it first. THE DATABASE GATE: before any load or any read heavier than a count, run the probe python scripts/db_probe.py (session 431 writes it: one ordered read of the series table with a 5 second timeout, exit 0 under 3 seconds, exit 1 otherwise, the time printed and appended to runs/db_probe.log); exit 1 means no load this session: the files go to warehouse/output and the archive, the coverage row is rebuilt with --only, and the load is listed under "To finish" for a later session. Pulls only as a session's part names them, under its ceiling, nothing from a paused publisher, no new host without its robots file and terms read. Model spend USD 0 unless a part says otherwise. NO LANDING 14:00 to 16:15 UTC; the 22:30 to 23:45 UTC cutoff is Sundays only. coverage.csv rebuilt with --only, never whole, on this machine; the release package spliced, not rewritten. No em dashes. Reports as session 364's, with "For Samuel's ruling" one item a line. Read docs/state/morning_2026-10-21_day.md, docs/state/review_2026-10-21_night_code.md (on wip/381-382-land until it lands) and sessions 373 to 385's reports first; do not redo their work. Last step of the last session: the morning note, the next file if nothing waits, then python scripts/chain_queue.py next.

## Session 431: the database, read before anything is written

Long end 1:30. Pulls: none. First scripts/db_probe.py as the rules describe, with a test. Then, read-only, through the service connection this machine holds: pg_stat_activity (every query older than 30 seconds, its start, its state, its text's first line, its role), pg_stat_statements if enabled (the twenty heaviest by total time since reset), the size of every table and index (the twenty largest), bloat where the extension allows, the connection count by role, and whatever erw_health holds for 20 October's loads with their start and end times. Cancel nothing but this session's own queries. docs/state/database_2026-10-21.md: what was running, what the day's loads did and when, which reads time out and on which tables, and the three likeliest causes in order with the evidence for each. Then the probe every five minutes for the rest of the session, its times in the note. Push the note on a branch; land nothing. "For Samuel's ruling": the compute tier, if the evidence points there.

## Session 432: iso_queue_statistics rebuilt whole

Long end 2:00. Pulls: none (the raw files are held). Session 367's finding: the builder cut every row at a "#" inside a cell, so 450 ERCOT rows and rows in the other five queues lost their queue date; the reader's fix is on task/367-372 (queue_statistics reads by the header's count of lines). Take that fix from the branch (cherry-pick the one commit; say its hash), rebuild the table from the raw files held here, validate, write it to warehouse/output and the archive, rebuild its coverage row with --only, and load it through the database gate (exit 1: "To finish"). The method note's line about the fault is replaced by the rebuild's date and the rows regained, counted. The release package's row follows.

## Session 433: the board's ERCOT day-ahead, stopped on 15 October

Long end 1:30. Pulls: ERCOT's day-ahead settlement point prices for 16 to 21 October only, ceiling 12 requests, the same source as the daily step. The code machine's note: the board's ERCOT tiles stop on 15 October (day-ahead) while its week table holds 20 October. Find which step feeds the tiles' table, why it stopped (a step that failed quietly, a file not read, the hold of 21 October), fix the step with its test, run it for the missing days, archive, load through the gate. The report names the table, the days regained and the cause.

## Session 434: what happened to session 386, and the note it owed

Long end 1:00. Pulls: none. This machine stopped after session 385 at about 22:05 UTC on 20 October and never ran 386 (no note, no next file, nothing in the queue). Read the local state: the last session's transcript under runs/, the git reflog, the worker and duty logs, the health table's rows for lab-desktop, the Task Scheduler's history for the daily run. One page in docs/state/morning_2026-10-21.md under a new heading "Why the machine stopped on 20 October, evening", with the cause as far as the evidence goes and the rule that would have caught it. Then the note 386 owed: what 384 and 385 landed, in session 364's form.

## Session 435: the real-time node prices, the days held

Long end 1:30. Pulls: ERCOT's real-time settlement point price list and its day files for the days ercot_node_prices_hourly lacks, ceiling 40 requests. The daily step dm_node_rt (session 376): did it run at 10:00 Pacific on 21 October, what it held before and after, the ceiling's room (500,000 rows). Run it for the days missing; node_basis_daily's real-time columns and node_basis_summary recomputed for the days gained; archive; load through the gate. The report gives the days held before and after and the rows against the ceiling.

## Session 436: the archive proven again

Long end 2:00. Pulls: the archive bucket only. After the restore of 20 October: every table of coverage.csv against the archive (session 362's proof, run again), the tables this machine now holds newer than the archive written to it, docs/state/archive_proof_2026-10-21.csv, the count equal, newer, behind. No database read beyond counts; no load.

## Session 437: the Redivis draft, what fits

Long end 1:30. Pulls: Redivis reads, and uploads only of tables behind that fit under the 10 GB cap (node_basis_daily and ercot_all_hub_prices_history stay held for storage, as 385 ruled). scripts/sync.py --check: the tables behind, each one's size; upload those that fit, newest first; docs/redivis/release-v1-runbook.md's draft section brought to today with the bytes used and free. "For Samuel's ruling": the storage, with the bytes the two held tables need.

## Session 438: the stale tables, refreshed where the pull is approved

Long end 3:00. Pulls: only the sources below, each under the ceiling its connector records; nothing else. The code machine's note of 20 October lists the tables stale on the data machine: ercot_peak_premium_annual and _monthly (29 September), site/data/map.json (9 October) and energy_projects (5 October), eia930_demand_growth and caiso_curtailment_profile (5 October), the NOAA weather tables (3 and 4 October), datacenter_operator_sites (12 October), ercot_large_load_status (newest row June), eia_retail_electricity_prices (July). For each: the connector's --check, then its refresh where the source is not paused and the connector names its ceiling, in that order; validate, archive, coverage --only, load through the gate. A table whose refresh fails or whose source is paused is listed with the reason. The report: a table of the ten with newest date before and after.

## Session 439: 21 October, green or not

Long end 1:00. Pulls: none. warehouse/health.py summary --day 2026-10-21 and the GitHub runs of the day: every failed step with its root cause in queue/summary/2026-10-21-health.md; site/data/health_days.json read, not written; the daily run of 21 October: when it took the lock, when it released it, what it wrote. One line on whether 21 October counts green and, if not, what would have made it.

## Session 440: the morning note of 22 October, the next file, and the queue

Long end 1:00. docs/state/morning_2026-10-22.md in session 364's form: what each session landed, pulls against ceilings, the database's state through the night (the probe log), decisions made without Samuel, waiting for him highest value first, the other machines. Then python scripts/chain_queue.py list: if nothing waits for this machine, write the next file before the queue step, at least eight sessions, machine: data, numbered from the next free number above 450, from the "To finish" lines of this chain (the loads the gate refused), docs/roadmap.md items 5, 6 and 9, and the open items of the notes; commit and push it to main; say so in the note. Push, then python scripts/chain_queue.py next.
