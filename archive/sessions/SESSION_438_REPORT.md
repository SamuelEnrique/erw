# Session 438 report: the stale tables, refreshed where the pull is approved

21 October 2026, from 08:03 UTC, unattended, on lab-desktop (the data machine), the eighth session of the chain of 21 October, night (`queue/done/016-night-21-october-data.md`). Model spend USD 0. Pulls: none (NOAA not asked, below). Two tables refreshed and loaded through the gate.

## Read these first

The code machine's list of 20 October, against this machine's tables on 21 October. Dates are the newest row; "run" is coverage's `last_run`.

| Table | Before | After | What happened |
|---|---|---|---|
| `caiso_curtailment_profile` | to Sept 2026, run 5 Oct | to Sept 2026, run 21 Oct 08:06 UTC | **refreshed**: 4 values revised (September's battery charging, from CAISO's revised inputs); validated, archived, coverage `--only`, loaded |
| `eia930_demand_growth` | 2026 year to date through Sept, run 5 Oct | the same through Sept, run 21 Oct 08:07 UTC | **refreshed**: 4 values revised (US48 August and September from EIA's revisions; the year's growth 10.25% to 10.26%); the same gates; loaded |
| `ercot_peak_premium_annual`, `_monthly` | to Sept 2026, run 29 Sept | unchanged | **not refreshed**: its inputs are the members of two consolidated tables (`ercot_rtm_hub_prices_<year>` from the 3.1-million-row ERCOT history, and `ercot_rtm_hub_prices`), so it needs `consolidate.py split` and `build` around it. Claude Code had just stopped two jobs for low memory, and a split and rebuild of that family cut short would put the consolidated table at risk. For a session with memory to spare, or the daily run if the step is added there |
| NOAA weather (`noaa_grid_weather_*`, `noaa_station_weather_hourly`) | to 10 and 11 Oct, run 19 Oct | unchanged | **not refreshed** for the same reason: `noaa_grid_weather.py --refresh` rebuilds the 4.7-million-row station table. NOAA was not asked (the year's rows: 2,812,746 of 6,000,000) |
| `site/data/map.json` | built 9 Oct | unchanged | this machine's daily step `dm_project_map` (session 349) rebuilds and commits it from today's run, 17:00 UTC; a page file of the daily, not rebuilt by a session |
| `energy_projects` | 19 Oct, run 19 Oct | | current (stale only on the code machine's copy) |
| `datacenter_operator_sites` | 19 Oct, run 19 Oct | | current |
| `ercot_large_load_status` | June 2026, run 20 Oct | | current: ERCOT's newest report is of June |
| `eia_retail_electricity_prices` | July 2026, run 20 Oct | | current: EIA's lag of about two months |
| `noaa_isd_hourly` | Aug 2025, run 1 Oct | | an earlier table, not on the list |

- **Accidental run**: `ercot_peak_premium.py --help` ran the builder, since it takes no options. It failed at once ("input table ercot_rtm_hub_prices is missing") and wrote only its log (`warehouse/output/logs/ercot_peak_premium_20261021T073809Z.log`), no table.
- **The loader rewrote both tables whole** (6,124 and 24,108 rows written) for 8 changed values, because every row's `retrieved_at` moved. The database went from 2,317.9 to 2,322.3 MB. This is the write amplification that `docs/state/database_2026-10-21.md` points at; recorded there for Samuel.

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py` | 0 | |
| trial builds into `runs/s438_trial/` | 0, 0 | the same rows and ranges; 4 values changed in each |
| `warehouse/lock.py acquire` | 0 | 08:06 UTC; released 08:11 UTC |
| `curtailment_profile.py`, `demand_growth.py` (no `--snapshot`: no page file) | 0, 0 | |
| `erw_validate.py` (both) | 0 | |
| `archive.py write` | 0 | 4 and 4 rows new or changed |
| `build_coverage.py --only` | 0 | two rows: the run's time |
| `db_probe.py` before and after the load | 0, 0 | 0.48 s, 0.47 s |
| `load.py --only` (both) | 0 | 6,124 and 24,108 written, 0 deleted |

Rule 8: `s438-load-before` and `s438-load-after`, 0 differences on 25 pages, expected (every page in review).

## Decisions made without you

1. Trial builds first, to see what a refresh changes before any write.
2. No `--snapshot` (the site's own copies are page files).
3. `ercot_peak_premium` and the NOAA tables not refreshed while memory is short.

## For Samuel's ruling

- `ercot_peak_premium` has no scheduled step that can run it. The runner lacks the ERCOT history, and this machine's daily does not run it. Should it be added to `run_data_machine.sh`?
- The loader writing a whole table when only its `retrieved_at` stamps move (the database note).

## Files

- Changed: `warehouse/metadata/coverage.csv`, `docs/coverage.md` (two rows). New: this report.
- On this machine (not in git): the two tables, `runs/s438_*`.
