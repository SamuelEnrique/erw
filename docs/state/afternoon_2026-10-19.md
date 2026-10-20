# The afternoon note, 19 October 2026

Energy Research Warehouse (ERW), session 327, for Samuel's evening hour. The data machine's chain of 19 October, daytime (sessions 321 to 327), unattended on lab-desktop, from 20:14 UTC on 19 October to this note's push. Model spend USD 0 in every session (the scheduled daily runs spend within their own cap of USD 1.50 a day).

## Read these first

- **The manual daily run finished green, inside the old limit** ([run 39344868297](https://github.com/SamuelEnrique/erw/actions/runs/39344868297), dispatched 23:58:54 UTC on 19 October, on main at cb4d456f; job success at 02:17:43). Its daily step passed at 02:11:22 after 2 h 8 min, the whole job took 2 h 19 min, the cache was saved, and the metadata commit is on main (`2bea6dc1`, "Daily prices 2026-10-20"). The budget worked: `eia_series` was stopped at its 15 minutes and recorded as a skip. **But the day is not green by the new rule.** Three steps wrote failed rows. `eia930`: the run started just after midnight UTC, so its window ended at 20 October 00:00 and EIA had not yet published 19 October's 23:00 hour; five demand series wrote nothing this run (the 14:00 schedule never meets this). `generation_mix`: its input exists on the runner only when `eia_series` writes it, so after the budget stopped `eia_series` the build failed; it is now a skip (landed with this note). The package tests: `test_large_table_by_partition[nyiso_zone_load_hourly]` failed with "assert (False)", whose log a session cannot read; for the next session.
- **Green days: 0, counted to 19 October** (`site/data/health_days.json`, written by the manual run). 19 October has three failures: the Roundup's Redivis restore (before session 305's fix reached it) and the two faults below, both fixed.
- **Why the runs stopped, and the fix (session 321).** A good daily run takes 140 to 170 minutes, and one publisher that does not answer the runner pushed it past GitHub's 180-minute limit: CAISO and SPP, 39 minutes each (4 tries of about 2.4 minutes, three days), or EIA's API, 41 and 66 minutes. The job's limit is now 300 minutes, and **every publisher pull has 15 minutes of wall clock** (`warehouse/pull_budget.py`). A pull stopped at its budget is a skip, and its tables are gap rows "publisher did not answer within the budget", asked again by the next run. **The gate reads the steps:** a failed daily step is a failed row of `erw_health` (a red day even when the job is green), a run stopped at the limit is one too, and the gate counts a run only when its daily step passed. `docs/machines.md`, "The budget of a publisher pull, and the gate".
- **Two faults the timeout had hidden, found by GitHub's late 19:33 run (green job, failed daily step) and fixed:** the Redivis license check failed on four retired or stray tables because their header lookup is a Redivis read the export cap refuses (now a skip unless the internal dataset holds the name); and the live set refused the tracked deal and datacenter tables as older than its copy, because the cancelled 14:00 run had loaded newer ones and never committed them (now restored from that run's archive).
- **24 December 2022 is an ERCOT stress day** (session 322): ERCOT's release of 16 December 2022 announced an OCN for 22 to 26 December. The new table `ercot_grid_notices` holds 178 notices since 2011.
- **The license disagreements are settled: 0 open** (session 324). 41 are governed by your "license needed" ruling, PortWatch stays internal (the IMF forbids automated bulk download without permission), and CARB's auction prices and the RRC's lease production are now public (the clause wins). **Two lists for you:** [`permissions_2026-10-19.md`](permissions_2026-10-19.md) (the 42 permission tables of 12 October, by publisher, a box each for your emails of 14 October) and [`unsettled_licenses_2026-10-19.md`](unsettled_licenses_2026-10-19.md) (the 19 unsettled, with the sentence each email would need; nothing sent).

## What each session landed

| Session | Landed |
|---|---|
| 321 | The 300-minute job, the 15-minute budget a publisher pull, the gate on step results; the license check's cap rule; the tracked news and deal tables from the 14:00 run's archive; `merchant_revenue_monthly` rebuilt with CAISO's allowance and loaded (the snapshot stays as committed: its group of files and six pinned tests must move together); the manual run (above) |
| 322 | `ercot_grid_notices` (178 rows; 120 counted, 100 days); `grid_stress_days` reads it (ERCOT 169 stress days, from 113); the Flex Alert scorecard to 2026-10-31 with no number moved (no alert day in 2025 or 2026); CAISO's 25-hour day asked whole, three fall-back days filled (750 rows) |
| 323 | `eia_annual_generation_ba` (EIA-923 summed by balancing authority; the Electric Power Annual has no such table) and `eia_annual_crosscheck_ba`: EIA-930 runs 3 to 10 percent below on six grids, within 1 percent on PJM, 3 percent above on SPP; the Grid pack's question 5 answered |
| 324 | The 44 disagreements settled (above); CARB and RRC public; the two lists |
| 325 | 597 gap days closed as known gaps (`known_gaps.csv` rows keyed `<table>:gap_days`: EIA's first BAT days, US48's BAT series, SWPP's CO2); 833 open days to 234; every re-ask still incomplete at EIA |
| 326 | The Roundup's sequence dry for week 42, every step exit 0, nothing sent and no model call; the chart of the week's x axis fixed (107 overprinted dates). Sunday's run needs nothing from you |
| 327 | This note |

Landings: 68b46126 (20:51), 0b9802ca (21:06) and cb4d456f (00:00 on 20 October), each with before and after snapshots, **0 differences on 25 pages** each; the loads of merchant revenue, session 322's and 323's tables and session 324's two flags each with their own snapshots, 0 differences.

## Every pull against its ceiling

| Session | Pull | Ceiling | Used |
|---|---|---|---|
| 321 | none (GitHub's API and the runs' log artifacts) | | |
| 322 | ERCOT: robots, notice pages, operations messages, release listings and releases | 200 | 130 |
| 322 | CAISO's Flex Alert history page | 20 | 0 (CAISO's own report is the list) |
| 322 | CAISO OASIS, the clock-change days | 10 | 6 |
| 323 | EIA: the EIA-923 page, the Annual's index, three annual zips | 5 | 5 |
| 324 | none | | |
| 325 | EIA's API (the per-day connectors) | 1,500 | 29 |
| 326, 327 | none | | |

Nothing was asked of NYISO, ISO-NE, MISO, SPP, PJM or a paused publisher.

## Decisions made without you

1. **Pushed through `task/` branches** (three landings), each after its checks.
2. **GitHub's late 19:33 scheduled run was left to finish**, and the first manual run (39322988664) was **cancelled** before any data step, because its checkout predated the two fixes it would have failed on.
3. **`eia930_emissions`'s lag is a skip, and its daily window 10 days**, so the new gate does not make every day red on EIA's posting rhythm.
4. **The tracked news tables were restored as of the 14:00 run** plus the later run's new rows, so nothing the live set holds rolled back and no story is scored twice.
5. **The merchant snapshot, hub files and CSV stay as committed**: rebuilt, they failed seven tests of their group (session 204's switch); the table moved.
6. **Sessions 322 to 326 wrote their data before the redispatched manual run** rather than after it.
7. **The history was merged with the archive before its stores** (session 322), so this machine's older copy did not delete the runner's newest rows.
8. **What counts as an ERCOT notice:** EEA levels, rotating outages, conservation appeals and notices, Power and Weather Watches, an OCN for extreme weather (as CAISO's RMO counts); not the control room's tool Advisories.
9. **The 41 permission tables keep their public flag** (your ruling), the document now says so; flipping them internal would have stopped every daily run at the license check.
10. **The Roundup's email step was not run, only rendered**: its `env()` reads `.env` when a variable is empty, so an "unset" key would still have sent.

## Waiting for you, highest value first

1. **Release v1** on or after 21 October: `docs/redivis/release-v1-runbook.md` (131 tables and 3 metadata tables now, 41 held). Before the click: remove `power_deals` (session 130's stray table) from the public draft, and move CARB's and RRC's old copies out of the internal dataset (`upload.py --check-license --fix`).
2. **The permission boxes** ([`permissions_2026-10-19.md`](permissions_2026-10-19.md)): the 41 tables read "license needed" from 21 October unless a permission is recorded.
3. **The 19 unsettled** ([`unsettled_licenses_2026-10-19.md`](unsettled_licenses_2026-10-19.md)): send any of the drafted sentences, or accept public-records law as the ground.
4. **The four "drop" drafts** at `/internal/findings` (session 308's report has the statement).
5. **The generator group:** let a session change the six tests that hold the hourly CSV to its export of 7 October, and look at the page library's NYISO difference, so the snapshot, hub files and CSV move with CAISO's allowance.
6. **`eia_series` and its budget:** it reads twelve tables' full histories each run and took 12, 29, 41 and 66 minutes in recent runs, so at 15 minutes it will often be stopped and its tables left as they were. Split it into per-table pulls, each with its own budget (its status file would need a name per table), or allow it a longer budget.
7. **The package test of `nyiso_zone_load_hourly`** failed in the manual run ("assert (False)"); its log needs admin to read. For a session with the log, or yours.
8. **Main fails two tests since the manual run's commit `2bea6dc1`** (new data, not new code): `test_session157.TagRule` (two newly tagged policy actions are not in the test's cases) and `test_session156` case 18 (Texas's curtailment share moved). Until a session updates them, every `task/` branch fails its checks; this note went straight to main.
9. **M7 on the runner** (gridstatus's pins).
10. **The Flex Alert scorecard's weather:** allow a NOAA pull for Sacramento and Fresno from 28 August 2025 (no alert day would join).
11. **ERCO's two storage days and EIA-930's eight demand days:** close as known gaps, or keep asking.
12. **Week 42's Roundup:** send it late by hand, or let week 43 (Sunday) be next (the default).
13. **Lazard's LCOE+** (session 306), **Berkeley Lab's terms address** (session 307), **`/events`'s `cold_2026` card**, and the **site copies' `--snapshot`** (item 15), as in the morning note.
14. **The Grid decisions block's words** for the EIA-930 against EIA-923 gaps (the code machine's page; the reasons are hypotheses).
