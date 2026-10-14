# Session 277 report: stale and empty, round two

14 October 2026, 10:40 to 12:20 UTC, unattended, on lab-desktop (the data machine), the seventh session of the overnight chain of 14 October, built in a worktree (`../erw-277`) beside session 273. Branch `task/277-stale-round-two`. Model spend USD 0: no model call. Pulls: EIA (the interchange probe: EIA's six-month file and its API route, as session 247 read them), CAISO (OASIS: ZP26's last nine days, after session 273's pull). Nothing from NYISO, ISO-NE, MISO, SPP, PJM or a paused publisher.

## Read these first

- **74 tables are over their limit by the state script's rule** (`scripts/data_state.py`, written to `runs/session277/data_2026-10-14.md`, not in git): 45 "stuck or not on a schedule", 29 refreshed with nothing newer at the source. After session 271's schedule, **two of the 45 had a cause this machine could fix, and both are fixed:**
  - **ERCOT's zone load** (`ercot_zone_load_hourly`, to 30 September): ERCOT posts its yearly native-load workbook about once a month, and the runner's run of 10 October failed with "the operator answered no hour" because its 10-day window asked for hours ERCOT had not posted. That is the publisher's lag: now "stale at source", a skip by session 271's CARB rule. A run that reads no file at all still fails.
  - **The zone price history's CAISO part** (ZP26 in `iso_zone_prices_history`, to 10 October): its weekly refresh lived in `refresh_supply.sh`, which asks it only where the table is held, and only the GitHub runner runs that script, where it is not held. So no run refreshed it. It is a weekly step of this machine's block now (`--iso caiso`), and was refreshed tonight.
- **The rest are the publisher's lag, a history or event table by design, a weekly table read by a daily rule, or another grid's.** Each is in the table below with its reason.
- **The network's newest hour is as close to now as EIA allows: 12 October 03:00 UTC, about 56 hours back at 11:00 UTC.** EIA's API route holds hours to 13 October 06:00, but only partly reported; the snapshot keeps to whole hours (all 157 pairs). EIA's own six-month file ends at the same whole hour. Nothing in the pipeline adds to EIA's delay.

## The 45, each with its reason

| Table | Newest row | What it is | Action |
|---|---|---|---|
| `ercot_zone_load_hourly` | 2026-10-01 04:00 | ERCOT's monthly workbook; the window asked for unposted hours | **fixed at the cause** (above) |
| `iso_zone_prices_history` | 2026-10-10 06:00 | the CAISO part had no run that could refresh it | **fixed at the cause** (above); refreshed |
| `eia930_all_history`, `caiso_fuel_supply_history`, `event_study_estimates`, `eia930_event_hourly_interchange`, `event_window_daily`, `eia_all_futures_prices` | 2018 to 2025 | closed histories and event windows | by design: nothing to fetch |
| `ferc_eqr_quarter_changes` | 2026-04-01 | FERC's quarterly filings; the third quarter is due 31 October | by design |
| `ercot_wind_solar_output_hourly` | 2026-01-01 | ERCOT's yearly file (2026's is posted after the year) | by design |
| `generation_mix_records` | 2026-09-27 | built monthly on the runner (the third of the month) | on its cadence: next 3 November |
| `caiso_area_load_hourly`, `ercot_dam_cleared_energy`, `caiso_dam_cleared_energy` | 2026-10-10 and 11 | refreshed weekly on Saturdays (`refresh_supply.sh`) | on their cadence: the rule reads an hourly table as behind after three days |
| `eia930_all_emissions` | 2026-10-10 23:00 | EIA's newest day lacks its CO2 values | stale at source |
| `portwatch_chokepoint_transits` | 2026-10-04 | IMF PortWatch posts weekly | stale at source |
| `eia_fuel_spot_prices`, `eia_product_spot_prices` | 2026-10-06 | EIA posts its spot prices weekly | stale at source |
| `price_board_spreads` | 2026-10-10 | built from the price legs above; the newest day all hold | stale at source |
| `carb_lcfs_credit_prices` | 2026-09-14 | CARB's weekly report | stale at source (session 271's rule) |
| `eia_sector_energy_consumption_monthly` and 10 more EIA monthly tables, `state_generation_mix_monthly`, `eia_crude_stream_prices`, `storage_buildout_monthly` | 2026-06 to 08 | EIA's monthly releases | stale at source |
| `isone_zone_load_hourly`, `isone_zone_prices_history`, `isone_as_prices`, `isone_dam_cleared_energy`, `nyiso_as_prices`, `nyiso_zone_load_hourly`, `spp_as_prices`, `spp_as_quantities`, `spp_dam_cleared_energy` | 2026-09 to 10 | ISO-NE, NYISO, SPP | not this chain's to ask |
| `miso_as_prices` | 2026-10-04 | MISO | paused since 4 October |
| `rrc_lease_production_monthly` | 2026-07-01 | internal, not public | out of this session's scope |

- **The 29 refreshed with nothing newer** include the tables session 271 scheduled (NOAA's four, to 4 October; the SCED disclosure, to 14 August; the storage tables) and the disclosures that run 60 days behind: all at their publisher's date.

## The zone history's CAISO part, refreshed

- `zone_price_history.py --pull --iso caiso --recent 9` (12:07 UTC, two requests to OASIS, after session 273's pull had finished), then `--write --iso caiso --recent 9` under the lock: 1,665,045 rows; this run wrote the CAISO rows from the saved files, 600 of them new. ZP26's day-ahead now reaches 14 October (hour start 2026-10-15 06:00 UTC); its real-time, 13 October. Stores: validator, coverage, archive, Redivis draft, each exit 0. Not in the live set (no rule names it).
- **The pull's ceiling is near:** 2,885,403 rows of these series read of 3,000,000, counted over every run since session 140. The weekly step reads about 5,000 rows, so the ceiling holds about 20 more weeks (until early March 2027). A ruling (4).

## The network's newest hour

| What, at 10:58 UTC on 14 October | Newest whole hour (start) |
|---|---|
| The page's snapshot (Storage, built 10:05 UTC) | 2026-10-12 03:00 UTC |
| A dry run of the builder now (`network_hourly.py --dry-run`) | the same: 157 pairs in that hour |
| EIA's six-month file (Last-Modified 13 October 14:40 GMT) | the same (hour end 04:00); later hours 214, 150, 129 of 288 reports |
| EIA's API route | partial hours to 13 October 06:00 (hour end) |

- **What would bring it closer:** nothing within EIA's interchange. The page could say so beside the hour (session 247's ruling 6, still open), or draw demand, which EIA posts within two hours, separately: a page change, the code machine's.

## Checks

| What | Exit | Notes |
|---|---|---|
| `python scripts/precheck.py --what "session 277"` | 0 | six of six |
| `scripts/sync.py --check --no-git`, `scripts/data_state.py` | 0, 0 | 199 tables; 74 over their limit |
| `network_hourly.py --dry-run`; the probe of session 247 | 0, 0 | above |
| `python -m unittest tests.test_session277` (with 271, 247, 138) | 0 | 86 tests |

## Decisions made without you

1. **ERCOT's lag is told from a failure by what was read:** files read and no hour in the window is the publisher's lag; no file read at all stays a failure.
2. **The zone history's weekly step asks CAISO only.** NYISO's zones and SPP South are in the same table and are not this machine's to ask tonight; their part stays as it was.
3. **The weekly tables read by a daily rule are not called stale.** The state script's limit comes from the table's interval (an hourly table: three days), not from its schedule (Saturdays); the report says so instead of refreshing them early.
4. **The refresh's stores went in with session 273's commit** on the main checkout, because the two sessions write the same metadata files and the refresh ran beside 273's pull of the same publisher.

## For Samuel's ruling

1. NYISO's zones and SPP South in `iso_zone_prices_history`: ask them on the same weekly step, once their publishers allow?
2. The state script's rule: read a table's limit from its schedule where it has one (a weekly table, eight days)?
3. The network: say on the page that EIA posts interchange about two days after the hour (session 247's ruling 6)?
4. The zone history's ceiling (3,000,000 rows read, 2,885,403 used): raise it before the weekly step reaches it, about March 2027?

## Files

- Changed: `warehouse/connectors/zone_load.py`, `warehouse/run_data_machine_tables.sh` (two weekly steps), `tests/test_session271.py` and `tests/test_session247.py` (the step count).
- New: `tests/test_session277.py`, this report.
- On this machine, not in git: `runs/session277/` (the state document, the sync check, the probe, the dry run).

## The landing

- In session 278's report.
