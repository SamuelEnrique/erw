# Session 7051 report: the desk's second stack (old laptop rows 37 to 43); done-line requests 89, 129, 130, 139, 140, 143, 159 to 162, 169, 170, 179, 181, 260

Energy Research Warehouse (ERW). Chain 370, data machine (lab-desktop), 17 November 2026. Opus 5.5. Model spend USD 0.

Precheck passed. Session number 7051 free. Freeze: none.

## The landing desk

- Seven rows of the old laptop requested (37 `/prices` read, 38 `/prices/compare` read, 39 `/supply` read, 40 `/storage` read, 41 `/demand` read, 42 `/curtailment` read, 43 `/queues` read), merged in `wip/c370-desk-b` without a conflict; the waits reader 13,165 of 13,165 before the gate.
- **Gate g** (`751c3e358`): suite passed (10,008 tests); check-values failed 21 figures of row 41's `/demand?view=consumption`, twelve-month retail sales sums the page writes in whole MWh. A whole rule for that key added (26 of 26 against gate g's build).
- **Gate h** (`cb5a633c4`): suite passed; check-values failed `/learn/problems/know-your-grid`'s floor: the fault was mine (below), not the stack's. **Gate i** (the same commit) started after it.

## Done-line requests

- **139, done.** The comparison's site copy, in the public repository, carried every figure of ISO-NE's and NYISO's rows, held for license since 21 October. A held grid is now written there by name only (28 hubs held, not shown); test 7050_compare_held; test 96 follows.
- **129 and 140, done.** The windows' end was the earliest newest hour of every hub, MISO's (paused since 4 October) among them, so the comparison stood at September. A paused grid no longer holds it back: twelve months to October 2026 and the month October, loaded; the replication 270 of 270.
- **159, done.** The owners tab's copy stood at August because the monthly step ran without `--snapshot`; rebuilt (September 2026: 1,156 operating units of 662 companies) and the step fixed, the daily run committing the copy.
- **170, done.** Demand with the weather taken out rebuilt with NOAA's hours to 6 November and the comparison with session 126 (its copy now kept in `warehouse/derived/reference/`), and a weekly step from now (`dm_demand_weather`).
- **181, done.** ERCOT's whole months in the curtailment worth file: October 2026, 956,365 MWh below the High Sustained Limit, USD 25,385,334 at HB_HUBAVG real time (test 7051_ercot_worth; data_ready row 22).
- **89, done.** The battery game's solar level names its window's end (32 complete days, 2026-08-26 to 2026-09-26), read from its own log line; no date or price moved.
- **179, not a fault now** (the live set holds October). **169, not a fault** (EIA publishes no value for those months). **160, 161** done with requests 79 and 80. **260** read.
- **130 and 121, ruling** (ruling 2: ERCOT's days of 6 to 8 November not refilled). **143, ruling:** EIA's SPP workbook holds the CO2 generated for every hour of December 2025 to February 2026 but leaves the consumed side blank, and session 6's ruling (a) writes a day only with both. **162, checked:** CAISO's autumn days are missing from `caiso_battery_storage` itself (the Today's Outlook connectors' clock-change rule); the connector's fix open.

## Later in the session

- **Desk gate i** (`cb5a633c4`) passed every step; desk stack b landed through `task/7051-desk` (run 44024522952) at `4b7aa450b`. Snapshots `before-cb5a633c`, `after-cb5a633c`: **0 differences**. Rows 37 to 43 marked (`d4b3927fb`).
- **149, done.** The board set a weekly series beside the newest value at least 365 days back (EIA's storage week ending 2026-11-06 against 2025-10-31); now the same week a year before (2025-11-07), as `/supply` and EIA's report do; the board rebuilt; its replication 30,670 of 30,670.
- **154, done.** NYISO's and ISO-NE's cleared rows in the public supply file carry status and note only.
- **141, done.** The comparison's mean daily spread over whole days (ERCOT HB_BUSAVG 47.19 USD/MWh day-ahead, 365 days).
- **180, in part.** CAISO's real-time prices of 15 October pulled from OASIS into the hub history; the curtailment shares and worth rebuilt (SP15 October priced in 744 of 744 hours). Today's Outlook's hours of those days are open.
- **190, done.** Active MW by part type in the queue summary (US battery parts 544,128 MW, the note's cross-check); the replication 17,304 of 17,304.
- **153 and 182, ruling** (ruling 2's paths; session 149's rule on the Texas file).
- **Gate j** failed four tests, every one from this session's changes: the battery levels' rebuild had dropped the CAISO levels' rooftop solar shape (the builder now keeps a shape the moving window cannot rebuild), and three tests pinned text or positions I had moved. Fixed. **Gate k** (`b262bc871`) passed every step; chain 370's branch landed through `task/7051-data` (run 44032669821) at `f675235c5`. Snapshots `before-b262bc87`, `after-b262bc87`: **0 differences**.

## Errors

- **The live set lacked California's intensity of generation from 04:23 to 04:46 UTC.** For request 143 I rebuilt the carbon tables by hand and loaded them without the daily run's next step, `caiso_join.py --apply`, which writes California's rows from CAISO's own data. `/learn/problems/know-your-grid` then threw on a missing row (gate h's floor). The join was run and the three tables loaded again (79 daily and 7,472 hourly rows written). Every page is in review: no visitor saw it. Saved as a rule for later sessions.

## Needs the key

- None new.

## Decisions made without you

- Request 139: a held grid's rows by name only in the site copy; the table keeps them (it is held as a whole).
- Request 129: a paused grid no longer sets the comparison's window.
- Request 170: session 126's copy committed as a reference file so the weekly step can compare with it.

## For Samuel's ruling

- **SPP's carbon intensity (request 143).** Write the generated side alone on days EIA leaves the consumed side blank? Default: no, session 6's ruling (a) stands; SPP's twelve months read "not held".
