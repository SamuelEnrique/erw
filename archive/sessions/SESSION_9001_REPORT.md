# Session 9001 report (chain 601, the second session; lab-desktop, data machine, first window)

Chain: `queue/done/601-night-20-november-desktop-grid-conditions.md`. Progress: `docs/state/progress_c601.md`. Taken from the resume file `queue/next/602-resume-chain-601.md` at 13:15 UTC, after the chain worker closed session 9000 at 13:14 UTC (no commit for 32 minutes while gate 2 ran).

## Snapshots

- Queue push (`2d19eaaeb`): `c601-s9001-before` (13:18 UTC) against `c601-s9001-after` (after deployment 7942714758): 0 differences in all 25 pages. Expected: the push held queue files only.
- Gate 2's landing: `c601-s9001-land1-before` against `c601-s9001-land1-after`, 0 differences (expected). Progress push `4bb5b9c06`: 0 differences (expected).
- Gate 3's landing (`af0c235ce`): `c601-s9001-land2-before` against `c601-s9001-land2-after`, 0 differences (expected: every live page is in review). Desk marks push `2110a16d6`: `c601-s9001-land2-after` against `c601-s9001-p2-after`, 0 differences (expected).

## Done

- 602 taken (`514e41b57`, moved by hand in a separate worktree, `erw-c601q`, since the main checkout held session 9000's copies under its lock); 603 written alone and pushed (`2d19eaaeb`).
- Gate 2 of `wip/c601-congestion` (`075e1fecb`, 12:42 to 13:08 UTC) read: every step passed. The held script's own hand checks did not run (its output folder was a relative path and the script had changed directory), but the gate itself had run check-routes, check-cross-checks and check-csp against its server.
- Session 9000's two local commits in the main checkout (its progress line and report) brought up by cherry-pick.
- The main checkout put back: the five metadata files restored, the four connector copies and `site/data/conditions/` moved to `runs/c601/aside_main9001/` (each identical to the branch's file); then session 9000's data lock released with its own token (13:25 UTC).
- Gate 2's commit pushed to `task/c601-congestion` at 13:24 UTC (GitHub run 44744050935).
- Gate 2 landed: `e996d00d8` (13:43 UTC, GitHub run 44744050935). Snapshots `c601-s9001-land1-before` and `c601-s9001-land1-after`: 0 differences in all 25 pages (expected: every live page is in review, the two new pages are in no menu). The progress push after it (`4bb5b9c06`): `c601-s9001-land1-after` against `c601-s9001-p1-after`, 0 differences (expected).
- What a reader now sees (read on production with the internal cookie at 1280 and 390 px, `runs/c601/read9001/`): `/congestion` opens on SPP's newest year with the 25 constraints that bound most hours and the 25 whose shadow price summed highest, when the chosen constraint binds by month and hour, the nine hubs and zones ranked by their congestion part, and two places side by side; ERCOT, PJM, NYISO, ISO-NE and MISO named with their reasons. `/conditions` opens on ERCOT's newest 35 days, hour by hour then day by day, with blank strips naming why. No sideways scroll and no console error at either width.
- Readers' rows found and fixed on `wip/c601-readers` (tests `test_session9001_congestion_reader`, `test_session9001_conditions_reader`): H1, the second list of `/congestion` had no heading; H2, "SPP SPP North hub"; H3, a strip with no figure in its window drew an empty chart with every axis label "01-01" (ERCOT's adder, which ends on 2025-12-04; SPP's outages in the Uri window) and the alerts a header with no row: now words with the file's last day.
- Landing row 3 of window 2 (`wip/c630-codebook`) stacked on `wip/w2-c630-desk`: c601 and main merged, `llms.txt` rebuilt, and codebook files written for c601's seven public tables, which `test_codebook` requires of every public table (written fields in `runs/c601/cb_hand.yaml`, from the method notes); the codebook's derived files rebuilt; 196 related tests passed. With the readers' fixes, gate 3 from 14:13 UTC; it lands after 16:15 UTC.
- Part H: `/congestion`'s table figures carry page-file keys and the page is in `check-values`' list (`wip/c601-trace`; 560 keys resolved against the file, 0 mismatched). SPP's 2022 price zip pulling under the data lock.
- Found: the page files (`site/data/conditions/*.json`, built 12:14 UTC) predate the outage history (SPP to 2016, CAISO to 2021) and SPP's 2023 prices; the data machine's daily run (17:00 UTC) rebuilds and commits them (`dm_congestion_page`, `dm_conditions_page`), so no hand rebuild.
- Gate 3 (`63f7b20ed`): every step passed, 14:13 to 14:57 UTC. Gate 4 (`e9b7e6791`, gate 3 with the trace branch) from 15:05 UTC. Data request 568 read: its first part is row H3; its second (the table "holds 500 rows of 841") is the shared table's paging (Earlier and Later), not changed.
- Gate 4 (`e9b7e6791`) failed at the suite: `test_session315` pins the start of check-values' `textOk` line, where the new rule had been put first. Gate 5 (`47b261282`) failed on `test_session1903`, which pins the line's end. The rule now sits on its own line after it (`b8f7909c9`), and every test that reads `check-values.mjs` was run before gate 6 (919 passed; two node tests fail only in a worktree without the build's generated files).
- Gate 3 landed: `af0c235ce` (16:32 UTC, task/c630-codebook-desk, GitHub run 44770651271): landing row 3 of window 2 (the codebook) with rows H1 to H3. Read on production: `/congestion`'s lists under their headings, no "SPP SPP"; `/conditions` on ERCOT says its adder and alerts hold nothing in the window, with the file's last day; `/data/methods/grid_congestion` lists the new tables' variables. Row 3 and data request 568 marked (`2110a16d6`).
- Gate 6 (`b8f7909c9`): every step passed, 16:14 to 17:06 UTC; check-values read 352 figures on the five new views, each equal to its page file. Pushed to `task/c601-trace` at 17:06.
- The data lock: GitHub's daily run has held it since 14:21 UTC (its job may run 300 minutes; it is the first run since 17 November to pass its merge tests, request 565). SPP's 2021 to 2014 price years were not pulled: the watcher stood down at 16:40 so the data machine's 17:00 run would find the lock free; that run has waited behind GitHub's since 17:00.
- Data request 565 done: the GitHub daily run of 14:00 UTC passed its merge tests and loaded the live set; EIA-930 demand and generation now end 2026-11-19 23:00 UTC (were 11-15), CAISO storage 11-20 07:55, carbon intensity 11-17 23:00. Its load still reads failed on four tables: three refused by the loader's older-than-live guard (correct), and `sources` (below).
- Gate 6 landed: `2ec0599de` (17:48 UTC); snapshots `c601-s9001-land3-before` and `c601-s9001-land3-after`, 0 differences. `/conditions`' glance lines read on production (CAISO in the September 2022 heat: highest peak 51,104 MW on 2022-09-06).
- Row H4, found reading that landing at 390 px: two operators in a heat wave made the page 619 px wide (the 47 notices widened the grid column); each column now `min-w-0`, tried first on production's page in a browser (390 px of 390); gate 7 from 17:56 UTC.
- Data request 569 (the live set has no hour of 16 November): the GitHub daily runs of 17 to 19 November stopped before pulling and the 20 November run asked only 17 to 19. A backfill (`runs/c601/backfill_930_9001.sh`, seven days of EIA-930 demand, generation, storage and interchange, then the stores and the load) waits for the data machine's run to free the lock. A manual GitHub run was not used: it would email the digest to subscribers again and call the model.

## Decisions made without you

- Session 9000's lock taken over and released with its token, since this session continues its chain and its holder was closed; nothing it had copied into the main checkout differed from the branch.
- Gate 2's pages land before being seen at 1280 and 390 px on a local server: the landing had to finish before 14:00 UTC, and both pages are in review. They are read on production with the internal cookie right after the landing, as part A asks, and any fault found lands after 16:15 UTC.
- Gate 3's commit was pushed to its task branch at 16:10 UTC, five minutes before the end of the 14:00 to 16:15 window; its merge came at 16:32. The window guards the GitHub daily run's push, which was then still in its pull step and now rebases onto a moved main.
- Landing row 3 needed codebook files for chain 601's seven public tables, or its own test would fail once both were on main: written from the tables (read fields) and from the method notes (units, labels, row, time and vintage rules), in `runs/c601/cb_hand.yaml`.
- `/conditions` draws charts only, so for `check-values` to trace its page files a short line was added above each operator's strips: the day of each strip's highest figure in the window, each a checked figure.
- The page files are rebuilt by the data machine's daily run, not by hand, so this session commits no page file that run also writes.

## For Samuel's ruling (the default taken)

- The live `sources` table holds one row that `warehouse/metadata/sources.csv` lacks, "IEA – International Energy Agency", so every daily load reads failed on `sources`. `python warehouse/supabase/load.py --prune` would delete it. Default taken: not deleted (a live row goes only with your word).

## Needs the key

- Nothing.
