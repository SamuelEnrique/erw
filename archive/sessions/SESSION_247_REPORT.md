# Session 247 report: stale and empty

13 October 2026, 07:39 to 08:45 UTC, unattended, on lab-desktop (the data machine), the fifth session of the chain of 12 to 13 October. Branch `task/247-stale-and-empty`. Model spend USD 0: no model call. Pulls: EIA, CAISO, ERCOT and the NRC, each within its connector's ceiling; nothing from NYISO, ISO-NE, MISO, SPP or PJM, nothing paused. Writes under the data lock: twelve tables' stores and five tables' live-set load. No page edited.

## Read these first

- **Session 218's stale tables have a schedule: one block of this machine's daily run, nine steps, run once tonight with every step ok.** Six run every day (EIA's daily total interchange, CAISO's and ERCOT's wind and solar forecasts, the NRC's reactor status, CAISO's notices, CAISO's evenings), three once a month (CAISO's curtailment reports, who owns the batteries, the shoulder hours), then the live-set load of the tables only this machine builds. `bash warehouse/run_data_machine_tables.sh --list` names each.
- **Three of session 218's lines are not on a schedule, each for a reason I could not rule on:** NOAA's weather (its approved ceiling of 3,000,000 rows is reached at the next refresh), the price board's statistics table (its page is retired), and ERCOT's storage disclosure (it waits for your approval). They are under "For Samuel's ruling".
- **The table of `/supply` that reads "not held" is "Day-ahead energy cleared, by grid": its two five-year columns are empty in all eight rows. Nothing was pulled, because nothing allowed would fill it.** ERCOT lists 31 days of that report; CAISO serves about 39 months, and the columns need five years; the other grids are not this chain's to ask.
- **The network's newest hour is two days behind because EIA publishes interchange two days behind. It cannot be closed from here.** At 07:57 UTC the page's file, EIA's API and EIA's own bulk file all ended at the same hour, 53 hours back. The page's file was current to EIA within the hour.
- **The price board's builder: green in the runner's condition, and now green whichever table is missing.** It failed in the daily runs of 9, 10, 11 and 12 October on a table the runner lacked. Before tonight's fix it built in 16 of 26 cases (each table it reads absent in turn) and crashed in 10. After the fix: 26 of 26.
- **California has four stress events now, not two.** The block's first run read CAISO's notices to 8 October 2026 (they were held to April 2025), and session 246's rule wrote 9 and 10 September 2026 and 5 to 8 October 2026 without a code change.
- **Session 246 landed:** pushed 07:38:55 UTC (`task/246-caiso-battery`), check run 38363995070 passed, merged as `cb3bb27f` at 07:44:55, deployed 07:46:27. Before snapshot `s246-after-load` (07:26:54), after snapshot `s246-after` (08:09:45, 25 pages, 0 failed); `compare`: 0 differences, as expected.

## 1. Session 218's lines, each one

| Table | Session 218's line | What was done | Tonight's run |
|---|---|---|---|
| `eia930_daily_total_interchange` | a daily step | `dm_eia930_total_interchange`, daily | ok: 798 rows pulled (it resumes by month), 211,644 held, to 11 October |
| `caiso_wind_solar_forecast` | schedule `refresh_mix.sh` | `dm_caiso_ws_forecast`, daily, two requests | ok: 288 new rows, to 13 October 06:00 UTC |
| `nrc_reactor_status` | the same | `dm_nrc_reactor_status`, daily, one request | ok: 0 new (the NRC's file ends 9 October) |
| `ercot_wind_solar_forecast` (in the same script; ERCOT keeps a week) | the same | `dm_ercot_ws_forecast`, daily | ok: 664 new rows from 170 postings |
| `caiso_curtailment_intervals` | a monthly step, about 290 requests | `dm_caiso_curtailment`, monthly, with a new option `--new-only`: saved reports are read from their files | ok: 284 days listed, 284 read from files, 0 requested (11 requests for the listing) |
| `storage_owners_monthly` | a monthly step | `dm_storage_owners`, monthly | ok: unchanged (EIA's August inventory is still the newest) |
| `caiso_reliability_daily` | a daily step | `dm_caiso_reliability`, daily, after the notices | ok: 20,552 rows, six more than before (the new notices) |
| `shoulder_hours_monthly` | a monthly step; "not rebuilt" | `dm_shoulder_hours`, monthly. Session 218's rebuild had in fact finished at 03:13 UTC but was never stored: stored tonight, then rebuilt by the block | ok: 27,197 rows; live set: 27,197 written, 43 deleted |
| `price_board_stats` | retire or schedule | not scheduled (a ruling). Session 218's rebuild of 03:13 UTC was not stored: stored tonight | validator, coverage, archive, Redivis draft: exit 0 each |
| `flex_alert_effects`, `flex_alert_model`, `caiso_dam_alert_day_hub_prices` | a pull of CAISO's emergencies list, then the scorecard | the list is read daily now (`dm_caiso_emergencies`): 1,906 rows, to 8 October 2026, six notices newer than April 2025. The scorecard was not run: its alert-day prices are a second pull for the new days | listed |
| `noaa_station_weather_hourly`, `noaa_grid_weather_hourly`, `noaa_grid_weather_daily` | a schedule, after a ruling on the ceiling | **not scheduled:** 2,777,645 of the approved 3,000,000 rows are read; the next refresh passes the ceiling and the connector stops | listed |
| `ercot_sced_esr_hourly`, `ercot_storage_rt_monthly`, `ercot_storage_node_basis` | the owner's approval | **not pulled:** the approval is yours | listed |
| `ercot_all_hub_prices_history` | an append from the live window | **not needed:** the live table has kept every interval since the history ends (26 August 2026) and no run trims it, so no gap opens. Session 218's "the window will move" was a guess | none |
| `generation_mix_records` | the mix's schedule | already monthly on GitHub (`mix_profile`, session 114) | none |
| `clean_energy_hourly` | the mix's schedule | **not scheduled:** its builder writes page files too | listed |
| `ercot_zone_load_hourly` | none needed | the Saturday step (session 206's patch) | none |
| six tables "by design" (histories, event windows), two at the publisher's lag (`carb_lcfs_credit_prices`, `eia930_all_emissions`) | nothing | nothing | none |
| `isone_rtm_zone_prices_hourly`, `nyiso_as_prices`, `spp_as_prices`, `spp_as_quantities` | not this chain's | nothing | none |

- **The live set** follows from this machine now: the block's last step loads the five tables it and session 244 build that the live set holds. Tonight: `caiso_grid_emergencies` 1,906 written, `caiso_reliability_daily` 20,552, `shoulder_hours_monthly` 27,197; `storage_owners_monthly` and `ercot_rtm_price_adders` unchanged. Database 1,443.9 MB of 7,500.
- **A failure of one of these steps is a `dm_` step failed:** it counts toward the green days and, since session 243, toward the one email of a red daily run.

## 2. `/supply`: the table that reads "not held"

| Table of the page | Rows | Hold a value | A year ago | The five-year average | The change against the five-year change |
|---|---|---|---|---|---|
| Natural gas in storage | 8 | 8 | 8 | 8 | 8 |
| Crude and product stocks | 5 | 5 | 5 | 5 | 5 |
| Production | 16 | 15 | 15 | 15 | 15 |
| Refining | 12 | 12 | 12 | 12 | 12 |
| Crude and product trade | 10 | 10 | 10 | 10 | 10 |
| Natural gas trade | 16 | 16 | 15 | 11 | 11 |
| Fuel burned for power | 20 | 16 | 16 | 12 | 12 |
| **Day-ahead energy cleared, by grid** | 8 | 6 | 3 | **0** | **0** |
| Managed money positioning | 5 | 4 | 4 | 4 | 4 |

- **Day-ahead energy cleared:** ERCOT (held from 23 September 2026; ERCOT lists 31 days), CAISO (from September 2025; about 39 months are served, three years at most), NYISO, ISO-NE and SPP (not this chain's to ask), MISO (paused), PJM (licensed). No pull allowed tonight fills a five-year column. The row-by-row table is in `docs/methods/supply_and_trade.md`.
- **The other "not held" cells** are what the publisher's file holds (LNG terminals younger than five years, a fuel EIA's hourly file leaves blank) or another publisher's under a license. Listed in the same section; nothing to pull.

## 3. The network's newest hour

| What, at 07:57 UTC on 13 October | Newest complete hour | Behind the clock |
|---|---|---|
| The page's file (built 07:05 UTC by the hourly job) | beginning 2026-10-11 03:00 UTC | 53 hours |
| EIA's API route for interchange | the same | 53 hours |
| EIA's own bulk file (last modified 12 October 14:38 GMT) | the same | 53 hours |

- **EIA publishes a local day's interchange on the second morning after it:** on 12 October it published through the end of each balancing authority's 10 October. So the page is between about 35 and about 59 hours behind, by the hour of the day.
- **The builder adds nothing to that** but its rule against half-filled hours (the next three hours had 129, 97 and 88 of 157 pairs).
- **Demand is not behind:** one to two hours.
- Written into `docs/methods/grid_network.md`. Nothing in the pipeline was changed: there was nothing in it to fix.

## 4. The price board's builder

- **What failed:** `board_page` in the daily runs of 9 October (`ercot_as_prices.csv` not on the runner) and 10, 11, 12 October (`carb_lcfs_credit_prices.csv`). Sessions 166 and 202 made the builder skip those two tables; session 202's fix landed after the run of 12 October, so no run has yet shown it.
- **The proof** (`runs/session247/board_green.py`): the builder run into a scratch folder against a folder of links to the tables, with tables left out, `GITHUB_ACTIONS=true` set. 26 cases: every table held; the eight tables the runner is known to lack absent at once; and each of the 24 tables the builder names absent by itself.
- **Before tonight's change: 16 of 26 built.** The runner's own case built (792 rows). Ten single absences crashed: the six EIA fuel and retail tables, the Federal Reserve's yields, the IMF's prices, and the two tables behind the week's summary. Each is pulled or restored in the same run, so each is a crash waiting for the day its pull fails.
- **The change:** every table the builder reads whole is asked for first; one that is absent is named in the log, its rows are not built, and `page_keep.py` keeps the held rows (it already kept the held week when the new one was empty).
- **After the change: 26 of 26 built** (`runs/session247/board_green.out`; the run before is `board_green_before.out`). Without a table its rows are simply not in the new build: 753 rows without the crude streams, 651 without the plant fuel costs, 546 without retail electricity, against 794 with everything; `page_keep.py` then keeps the held rows.
- **What this does not prove:** GitHub's runner itself. Its first run with session 202's fix and this one is today's, at 14:00 UTC.

## Checks

| What | Exit | Notes |
|---|---|---|
| `python scripts/precheck.py` | 0 | six of six |
| `table_stores.py shoulder_hours_monthly price_board_stats` | 0 | session 218's two unstored rebuilds |
| `MONTHLY=1 bash warehouse/run_data_machine_tables.sh`, under `lock.py run` | 0 | nine steps ok, nine stores ok, `dm_live_set` ok (five tables match) |
| `battery_stack.py`, its stores and its load, after the notices | 0, 0, 0 | stress table 1,512 rows (108 written); the monthly table unchanged |
| `network_hourly.py --dry-run`, `probe_interchange.py` | 0, 0 | the measurement above; nothing uploaded |
| `python -m unittest tests.test_session247 tests.test_session246` | 0 | 13 and 14 tests |
| the 19 test modules that name the changed builders and scripts | 0 | 452 tests |
| `runs/session247/board_green.py`, before and after the change | 1, then 0 | 16 of 26, then 26 of 26 |
| `python -m unittest discover -s tests` | 1 | 3,721 tests, 3 failures, the same three as before this chain |
| snapshots `s246-after-load` against `s246-after` | 0 | 0 differences (the block's loads fell between them) |

## Decisions made without you

1. **The schedule is this machine's daily run, not GitHub's.** Session 218 named `run_daily.sh` and `run_monthly.sh` for some lines. This machine holds every input (EIA-930's workbooks, the saved reports), so each step could be run for real tonight before it was scheduled; on GitHub a new step's first run would have been today's 14:00 run, unproven. The steps are the same.
2. **The block also loads the live set** for the tables only this machine builds. Without it the site's copy of them would move only when a person loaded it (session 244's ruling 4).
3. **CAISO's curtailment connector got a new option, `--new-only`,** so the monthly step asks for about 11 pages and the new days instead of every day of the year again.
4. **ERCOT's wind and solar forecast is in the block** though session 218's list did not name it: it is in the same script, and ERCOT keeps a week of postings, so each day without the pull loses a day.
5. **NOAA's weather is not scheduled:** a schedule would stop at its own ceiling on the first run. Raising a ceiling you approved is not mine to do.
6. **The page files of `/mix` and `/storage/owners` are not rebuilt by the block.** It refreshes tables; a page file joins a scheduled commit only with its own tests.
7. **The battery tables were rebuilt a second time tonight** so that the two new California events are in the table, its stores and the live set, and the method names four events.
8. **The interchange probe read EIA's whole six-month file (57.7 MB) once:** I asked for its last 6 MB and EIA's server answered with the whole file.
9. **The board builder's change is wider than the failure:** it skips any absent table, not only the two that failed. A row whose table is absent is kept as held, with its own date on it, never blanked.
10. **Session 218's report said two rebuilds "did not run". Its own log shows both finished at 03:13 UTC** (`runs/session214/s218_summary.out`). The tables were on disk and never stored, with coverage describing older files. Stored tonight.

## For Samuel's ruling

1. **NOAA's weather: a new ceiling?** It needs one before any schedule. The count is over every file kept (2,777,645 rows read of 3,000,000).
2. **`price_board_stats`: retire it with its page, or schedule its builder?**
3. **ERCOT's storage disclosure (`ercot_sced_esr_hourly`): approve the pull to continue?** Two derived tables wait on it.
4. **The Flex Alert scorecard:** run it again now that CAISO's notices reach October 2026? It needs the alert-day prices of six new notice days first (a pull of CAISO).
5. **`clean_energy_hourly`:** schedule its builder with the mix's page files?
6. **The network's two days:** say on the page that EIA publishes interchange two days after the day, or build the operators' own tie flows (seven connectors, four of them needing a license or a ruling)?
7. **Day-ahead energy cleared:** ask NYISO and SPP for their history (a chain that may), so that two rows gain their five years?

## Files

- New: `warehouse/run_data_machine_tables.sh`, `tests/test_session247.py`.
- Changed: `warehouse/run_data_machine.sh` (sources the block), `warehouse/connectors/caiso_curtailment_intervals.py` (`--new-only`), `warehouse/derived/board_page.py` (an absent table is skipped), `docs/machines.md`, `docs/methods/grid_network.md`, `docs/methods/supply_and_trade.md`, `docs/methods/battery_stack.md` and `tests/test_session246.py` (four events), and the metadata the stores wrote.
- On this machine, not in git: the refreshed tables, `runs/session247/` (the block's output, the probes, the board proof before and after, the supply counts), `runs/dm_monthly_2026-10.done`.

## The landing

- Freeze: `python scripts/freeze.py status` exit 0, no freeze. Main pulled and merged before the push. Before snapshot `s246-after` (08:09:45 UTC), then the push of `task/247-stale-and-empty`. The check run, the merge, the deployment's time, the after snapshot and the comparison are in session 248's report. Expected: 0 differences on the 25 pages.
