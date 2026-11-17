# Progress of chain 370 (data machine, lab-desktop, sessions 7050 to 7149)

The one record a restarted session needs (`queue/done/370-day-16-november-desktop-requests-and-reads.md`, "Restart safety and the progress file"). One line a request, landing or tool: its state and the session. States: `done (<commit>)`, `not a fault now` (what was checked), `needs the key` (the cost), `ruling` (the default taken), `waiting` (what for), `open`.

The chain's code branch: `wip/c370-data` (worktree `C:\Users\Shared\Documents\erw-c370`). The desk's stacks: `wip/c370-desk-<x>` (worktree `erw-c370d`). Tables are written in the main checkout under the data lock.

## Session 7050: the start

- Taken by chain 301's queue step (`e6b9450bb`); precheck passed (on duty for "session 7050" until 2026-11-17 15:28 UTC); session numbers 7050 to 7052 free. Resume pointer `queue/next/380-resume-chain-370.md` pushed alone (`4d511ff2f`); no other data machine resume file in `queue/next/` (chain 301's 311 removed by its last session). (7050)

## Part A: the desk

- Desk gate a (`wip/c370-desk-a`, `715e1b046`): old laptop rows 29, 30, 31, 32, 34, 35, 36 merged on main without a conflict; failed 3 tests (two headerless tables in reports 7531 and 7534 for the waits reader, test 188; test 7534's two replays need the site's packages); fixed (`a8431f37d` with main merged); desk gate b started 00:00 UTC. (7050)
- Desk gate b (`a8431f37d`): suite passed; check-values failed one figure of row 30's `/grid/caiso/alerts` ("-479,791" for -479791.0043). Gate c (`097c519a1`): the same (a key rule did not reach it: the figure is a `data-format="usd"` amount, read by check-values' own usd()); fixed at the cause (a usd amount under a million is also read as whole dollars; 395 of 395 on the page against gate c's build). Desk gate d (`3d44e533b`) started 01:10 UTC. (7050)
- Gate d failed test 315 (the textOk line's pinned first term), fixed; gate e (`8f10ebcfa`) passed every step at 02:09 UTC; landed through `task/7050-desk` (run 44000977927) at `695d8f9f4`; snapshots `before-8f10ebcf`, `after-8f10ebcf`: 0 differences. Rows marked landed (`79ea9acf0`; 0 differences). (7050)

## Part A: the data requests (`docs/state/data_requests_done_line.md` unless named)

- 30, 31, 35, 45, 47: done in session 7022 (chain 301), marked here. (7050)
- 69 done (the cost of power through October, loaded; a daily step `dm_cost_of_power`); 59 done (the Flex Alert of 1 October 2020 on its day, loaded); 79 done (a storage day written 48 hours after its end; test 7050_storage_settle) and 80 done (ERCOT's battery hours of 4 to 8 November pulled); 119 done (a board row the new build does not make anchors nothing; the board rebuilt); 120 answered (EIA's own repeat on holidays; the price board note); 110 done at the cause (request 40); 121 ruling (ruling 2); 122 checked in part (11 November SPP's own gap; the October days need a per-day option). (7050)
- 49 in part: the live set holds the build of 2026-10-19T09:43:29Z, 29,953 rows, the old laptop's; `replication/events/replicate.py` comes with desk row 29 and runs after the landing. 99 waits for desk row 34 (its figure script). 109 open: a queue position's proposed date carried into `energy_projects` (a new column of a live table) and the map's file. (7050)
- 49 done (the events replication on the live set's build: 1,149 of 1,149, 2,890 of 2,890, 186 of 186). 99 in part (the figure script fixed; the prices' rebuild moves the worked examples tests 294 and 7536 pin, to be recomputed with it). (7050)
- Chain 370's branch (`5926ae36f`: requests 59, 69, 79, 80, 119, 120 and the marks) passed gate f and landed through `task/7050-data` (run 44008498501) at `0ab3ec772`; snapshots `before-5926ae36`, `after-5926ae36`: 0 differences. (7050)
- New requests filed by the old laptop since (rows 89, 129, 130, 139 to 143, 149 to 154, 159 to 162, 169, 170, 179 to 183, 189, 190, 260): open, next in order. Also open: 99, 109, 122 (October days). (7050)

## Part B: the eight tools read as their reader

- Not started. (7050)

## Needs the key

## For Samuel's ruling

## Decisions made without you
