# Session 7022 report: chain 301 resumed; gate l landed; the daily run's refused push rebased and guarded; done-line requests 1, 5, 25, 37 to 48; the Texas 2026 matrices approved

Energy Research Warehouse (ERW). Chain 301, data machine (lab-desktop), 16 November 2026. Opus 5.5. Model spend USD 0.

Started by the queue step (`310-resume-chain-301.md` taken at `5eed3497e`; the pointer `311-resume-chain-301.md` pushed alone at `d3a145d91`). Precheck passed (on duty for "session 7022" until 2026-11-17 11:17 UTC). Freeze: none. Session number 7022 free on origin/main and every branch. No other Claude session on the machine.

## The landing desk

- No row requested in the four landing request files beyond those gate j landed (old laptop 17 to 28, portable 34 to 37: all marked landed on `wip/c301-last`); no data request row of the other files since 16 November except the done line's (below).

## Landings

- **Gate l** (`wip/c301-last`, `34b9cc9eb`: sessions 7019 to 7021 with gate k's one fix) passed every step at 19:11 UTC. Landed through `task/7022-landing` (run 43938253588), merged at `1f7bd79c9`. Snapshots `before-34b9cc9e` and `after-34b9cc9e`, the second after Vercel's status read success: **0 differences** (expected: every page is in review).
- The queue push before it (`d3a145d91`): `after-e6ffcaa6` against `before-34b9cc9e`: **0 differences**. No before snapshot was taken just before that push (a queue file only); the last after snapshot stands for it.

## The daily run's refused push (the race the landed retry fixes)

- The data machine's own daily run (17:00 UTC) pulled at about 19:33 and ran its guard's suite; gate l merged at 19:34, so its one push was refused ("fetch first"), as `landing-races-daily-push` describes. The landing had been pushed at 19:20, while the run was in its page files. The retry that fixes this landed with gate l itself, after the run had started.
- Under the data lock (taken at 19:49 UTC when the run released it): the run's commit rebased onto `1f7bd79c9`. Twelve files conflicted, every one a page file or metadata that both session 7020's writes (carried by gate l) and the daily run had rebuilt; the daily run's side, built later from the same tables, was taken; `package/llms.txt` written again by `scripts/build_llms.py`. The guard ran again on the rebased commit (`d2ec8ec58`) through `runs/c301/s7022/guard_push.sh`: passed at 20:14:46 UTC, pushed at 20:14:52. Snapshots `after-34b9cc9e` (the state before the push) and `after-d2ec8ec5` (after Vercel's status read success): **0 differences** (expected).

## Done-line requests (`docs/state/data_requests_done_line.md`)

- **Marked** (done in sessions 7016 to 7020, never marked): 4 (in part), 6, 8, 24, 32, 36, 25 (a), and 1 (the eight tools of sessions 7010 to 7014).
- **5, done.** The shoulder replication on the warehouse's tables (3 November): 21,592 of 21,593 page figures inside the tolerance over 195 views (the one a rounding edge); `from_hourly.py` on EIA's workbooks of 16 November over every month and year the table holds, 22,230 of 22,230. A year still running is now ranked only through the table's newest month (a newer workbook held twelve November days the table never saw). The do-file's expected values (ERCOT September 2026: 6 hours, 64,370.37 MWh, 1.65, 3.35, 6.76 over 9 days), test 7503 and the note follow.
- **37, code.** `eia930_demand_growth` gains `avg_demand_growth_since_2019_mw` and `peak_demand_growth_since_2019_mw` on the last whole year's row and `ytd_avg_demand_growth_since_2019_mw` on the newest year's: ERCOT 2025, 55,717.2 less 43,797.6 = **11,919.6 MW**, on EIA's workbook of 16 November. Built by the GitHub daily run from its next build.
- **38, answered.** EIA's California demand of 26 February to 31 March 2019 averages 19,547.7 MW where CAISO's own Historical EMS Hourly Load gives 22,438.6; elsewhere in 2019 EIA is 0.9865 of CAISO. The hours pass the screen, so they stand as published, named in the register (`eia930_ciso_demand_low_early_2019`). Read from CAISO's own load at that ratio, March 2019 would be 22,036.7 MW and 2019's mean 24,717.6 in place of 24,475.8: California's change to 2025 would be 847.5 MW, not 1,089.3. For Samuel's ruling.
- **39, answered in part.** California's batteries' charging (CAISO's own supply by fuel): 8.6 MW on average in 2019, 1,621.3 in 2025. EIA's ERCO demand of 2025 is 0.9996 of ERCOT's own load: it counts charging exactly as ERCOT's own load does. Not yet in a table.
- **40, code.** gridstatus 0.36.0 writes ERCOT "Completed" for any filled "IA Signed" day. The queue connector now takes ERCOT's own milestones: "Approved for Synchronization" (completed), "IA Signed" (active), "Active". On the archive's pull of 16 November, 474 of 577 "completed" positions have no day of approval to synchronize. From the runner's next pull.
- **41, code and rebuild.** `iso_queue_statistics` by technology group (storage, solar, solar_storage, wind, gas, other, not_stated) as entities `<iso>:tech_<group>:queue_<year>`, outside the pages' reads; the rows for all unchanged (1,734 of 1,734) and the groups add up to them in every count and MW (139 queue years).
- **44, code.** `carbon_intensity_monthly` gains each month's hours held and, where at least 90 percent are held, the value over those hours; the short days are named in the header (CISO: 19 days of the last twelve months). From the GitHub daily run's next build.
- **45, code and rebuild.** The Commission's Order in Docket No. 59080 (item 88, filed 5 November 2026) approves 2026 matrix A (bills of 1 January to 11 March) and matrix B (from 12 March) of Staff's filing of 16 March. The matrix connector says so with the Order's words; the table and the page file are rebuilt under the lock.
- **25 (b), 42, 43, 48:** ruling (the defaults stand). **46:** waiting for ERCOT's publication by 1 December. **20:** waits for the contracts' next build (the live set's are newer than this machine's and the archive's).
- **The daily run's failed `dm_storage_offers_rollup`:** the offers builder pivoted every entity of the awards table, which since session 7020 also holds the duration classes. Fixed (the fleet's rows only; test 116).

## The lock's writes (`runs/c301/lock3.sh` from 19:51 UTC, `runs/c301/lock4.sh` from 20:49)

- **31:** the awards table by duration class (1,244 rows) and the real-time tables (node basis 2,064 rows) rebuilt with gate l's builders.
- **35:** `ercot_peak_premium_node_monthly`, 17,472 rows, new.
- **30:** `ercot_storage_rt_offers_monthly`, 175 rows (February to August 2026), new. The validator refused the first write for its unit `MWh/MW/day`; `MWh/MW-day` joined the vocabulary (Decision 78) and the table was written again in lock4.
- **45:** the Order (item 88) and its page pulled through the connector (requests 16 and 17 of the 20 allowed); `texas_transmission_matrix` written, 572 rows; the page file `site/data/datacenter/texas_delivery.json` rebuilt, the 2026 rate's `status` now "approved".
- **28:** `impact_tax_rules`, 130 rows; one differs from the build before, Nevada's rule gaining `"abates": "tax"`, as the request said.
- **47:** `scarcity_hours_by_grid`, 201,873 rows, built again so October 2026 is whole (the live set's ran to 30 October 04:00 UTC: the monthly build of 3 November came before October's last day and a half was held).
- **41:** `iso_queue_statistics`, 8,990 rows from the six queues as the archive holds them.
- The day-ahead offers rollup with today's fix: 819 monthly rows. The register of source faults: 30 faults, its site copy written.
- lock3's load refused every table while the refused offers table had no coverage row (the loader's rule since session 65); lock4 loads them all after the offers table is written again.

## Goal 3

- 19:23 UTC: CAISO's large-loads process page has the same bytes (sha256 `578c69995d9a0388`), its robots file 404 in a call of its own: not filed.

## Needs the key

- None new. Unchanged: deals 10, 11, 13 (about USD 3), policy 25 (USD 0.02), attention 15 (USD 0.10), periodicals 77 (USD 0.70).

## Decisions made without you

- The daily run's refused commit: rebased by hand and guarded again rather than left for tomorrow's run. In each conflict the daily run's side was taken, being built later from the same tables.
- Request 41: the groups are written as entities of their own, outside every page's read, rather than as a new column; blanks are their own group, `not_stated`, not "other".
- Request 44: "most hours held" set at 90 percent of the month's hours.
- Request 5: the hourly check run over every month the table holds (the default sample is four months); a running year ranked only through the table's newest month.

## For Samuel's ruling

- **California's 2019 base.** Read EIA's 26 February to 31 March 2019 from CAISO's own load at the year's ratio? Default taken: as EIA publishes it. California's change to 2025 is then 1,089.3 MW, against 847.5 the other way.
