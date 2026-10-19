# Session 310: the public tables behind cadence

19 October 2026, 11:30 to about 12:10 UTC, unattended, on lab-desktop (the data machine), the sixth session of the chain of 19 October. Model spend USD 0. The list is the 33 tables of `docs/state/launch_2026-10-20.md`, "Public tables behind their cadence".

## Read these first

- **Of the 17 this machine may ask: 4 moved with today's pulls** (ERCOT's 60-day disclosure, EIA's daily interchange, CAISO's curtailment and forecast); **5 had already moved since 13 October** with their schedules and sessions 305 to 309 (ERCOT's large-load status, hub history and load zones, the NRC, EIA's emissions); **4 are stale or failing at the source** (CARB's LCFS, NOAA's three); and **4 do not move by design**: CAISO's alert-day prices (the scorecard's closed window) and three closed histories the cadence rule should not judge. The 3 are `eia930_all_history` (EIA's six-month files before the workbooks begin, 2018), `caiso_fuel_supply_history` (CAISO's own supply before `caiso_fuel_supply` begins, 1 June 2025) and `eia930_event_hourly_interchange` (the two fixed event windows of `/network`).
- **NOAA's data service answered HTTP 503 on both tries** (11:38 and 12:03 UTC), so the three NOAA tables stay at 3 and 4 October. Their weekly step on this machine asks again. **CARB's newest LCFS week is still 14 September** ("stale at source", a skip).
- **All 12 derived tables were rebuilt** (event_window_daily and event_study_estimates by session 308). The Flex Alert scorecard's three tables do not move: its window ends with the last alert season that has weather (`flex_alert_scorecard.py`, `END = "2025-10-31"`), a closed study, which is why no schedule refreshes them. `price_board_stats` is retired (the ruling of 14 October) and is not in coverage.
- **One table had no job: `generation_mix_records`** (and `generation_mix_hourly_profile`, the same builder). `warehouse/refresh_mix.sh` holds it and no run calls that script. It is now a weekly step of this machine (`dm_mix_profile`, `warehouse/run_data_machine_tables.sh`).
- **The 4 held tables stay as they are:** `nyiso_as_prices`, `spp_as_prices`, `spp_as_quantities` (no step until the licenses are answered, session 308's ruling 1) and `isone_rtm_zone_prices_hourly` (ISO-NE; the runner's daily step, 14 October now).

## The 33 tables

| Table | Kind | Newest row on 13 Oct | Now | Who refreshes it, and when |
|---|---|---|---|---|
| `eia930_all_history` | ask (EIA) | 2018-07-01 | the same | none: a closed history (2018-01 to 2018-07); nothing to add |
| `caiso_fuel_supply_history` | ask (CAISO) | 2025-06-01 | the same | none: closed where `caiso_fuel_supply` begins |
| `eia930_event_hourly_interchange` | ask (EIA) | 2025-06-29 | the same | none: two fixed event windows |
| `caiso_dam_alert_day_hub_prices` | ask (CAISO) | 2025-08-25 | the same (0 days to ask; 160 wanted days are older than OASIS serves) | none: the scorecard's closed window |
| `ercot_large_load_status` | ask (ERCOT) | 2026-03-26 | 2026-06-19 | this machine, daily (`dm_ercot_large_load`); ERCOT's reports since June state no figure (session 285) |
| `ercot_sced_esr_hourly` | ask (ERCOT) | 2026-08-06 | **2026-08-21** | this machine, weekly (`dm_ercot_sced_pull`, `_write`); 60 days behind by ERCOT's design |
| `ercot_all_hub_prices_history` | ask (ERCOT) | 2026-08-26 | 2026-10-16 | this machine, daily (`dm_ercot_hub_append`) |
| `ercot_zone_load_hourly` | ask (ERCOT) | 2026-09-01 | 2026-10-01 | the runner, Saturdays (`refresh_supply.sh`); ERCOT posts by month |
| `carb_lcfs_credit_prices` | ask (CARB) | 2026-09-14 | the same: stale at source | this machine, daily (`dm_carb_lcfs`) |
| `noaa_grid_weather_daily`, `_hourly`, `noaa_station_weather_hourly` | ask (NOAA) | 09-27, 09-28, 09-28 | 10-03, 10-04, 10-04: **HTTP 503 today** | this machine, weekly (`dm_noaa_weather`) |
| `eia930_daily_total_interchange` | ask (EIA) | 2026-10-01 | **2026-10-18** | this machine, daily |
| `caiso_curtailment_intervals` | ask (CAISO) | 2026-10-03 | **2026-10-18** | this machine, monthly |
| `nrc_reactor_status` | ask (NRC) | 2026-10-05 | 2026-10-16 | this machine, daily |
| `caiso_wind_solar_forecast` | ask (CAISO) | 2026-10-06 | **2026-10-19** | this machine, daily |
| `eia930_all_emissions` | ask (EIA) | 2026-10-09 | 2026-10-15 | the runner, daily; session 309 rewrote it from EIA's workbooks |
| `flex_alert_effects`, `flex_alert_model` | derived | 2024-07-25, 2025-08-24 | rebuilt, the same | none: a closed study |
| `event_study_estimates`, `event_window_daily` | derived | 2025-06-28 | **2026-02-02** | rebuilt by session 308 (`cold_2026`); by hand when an event is defined |
| `ercot_storage_rt_monthly`, `ercot_storage_node_basis` | derived | 2026-08-01, 09-28 | rebuilt, the same | this machine, weekly; they move with the disclosure and the node pull |
| `storage_owners_monthly` | derived | 2026-08-01 | rebuilt, the same (EIA-860M's inventory of August) | this machine, monthly |
| `generation_mix_records` | derived | 2026-09-27 | **2026-10-07** | **new: this machine, weekly (`dm_mix_profile`)** |
| `caiso_reliability_daily` | derived | 2026-09-28 | **2026-10-16** | this machine, daily |
| `shoulder_hours_monthly` | derived | 2026-10-03 | 2026-10-06 | this machine, monthly |
| `clean_energy_hourly` | derived | 2026-10-04 | **2026-10-17** | this machine, weekly (`dm_clean_energy`) |
| `price_board_stats` | derived | 2026-10-05 | retired | none (retired 14 October) |
| `nyiso_as_prices`, `spp_as_prices`, `spp_as_quantities` | held | 10-05, 10-04, 10-05 | the same | none, by ruling |
| `isone_rtm_zone_prices_hourly` | held | 2026-10-09 | 2026-10-14 | the runner, daily (ISO-NE's own step) |

## Pulls against their ceilings

About 120 requests of the 300, by each connector's own count where it prints one: ERCOT's meeting pages for the large-load status, about 76 (session 271's figure for the step); ERCOT's 60-day disclosure, 6; NOAA, about 21 (all 503); EIA's daily interchange, CAISO's forecast and curtailment, the NRC, ERCOT's load and CARB, about 15 together; CAISO's alert-day prices, 0. Nothing was asked of NYISO, ISO-NE, MISO, SPP or PJM.

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py --what "session 310"` | 0 | |
| the twelve connectors under the lock | 0, except `carb_lcfs` 75 (stale at source) and `noaa_grid_weather` 1 (HTTP 503) | `runs/s310_pulls.out` |
| the seven builders under the lock | 0 | `runs/s310_derived.out` |
| `table_stores.py` on the 19 tables that moved | 0 | every Redivis count(*) equal to the CSV |
| `load.py --no-vacuum --only` the 19 | 0 | 11 in the live set, all match; sources 317 |
| `noaa_grid_weather.py --refresh`, again | 1 | HTTP 503 |
| tests 247, 254, 271, 277, 310 | 0 | 49 tests; three pins follow the new step |

## The landing

See below (filled at the push).

## Decisions made without you

1. **The three closed histories and the closed study are not put on a schedule**: a daily step would ask for nothing. A first daily step for the alert-day prices and the scorecard was written and taken out again.
2. **`dm_mix_profile` is weekly**, like `dm_clean_energy`, which reads the same workbooks; it was added last in the list so that the earlier sessions' order holds. Its two tables joined the weekly live-set load.

## For Samuel's ruling

- The Flex Alert scorecard: extend its window to the 2026 season (it needs the season's weather), or keep it closed.
- The launch list's cadence rule: mark the three closed histories so that they stop showing as behind.

## Files

- New: `tests/test_session310.py`, this report.
- Changed: `warehouse/run_data_machine_tables.sh`, `tests/test_session247.py`, `tests/test_session277.py`, `coverage.csv`, `docs/coverage.md`, `archive_manifest.csv`, `redivis_uploads.csv`, `warehouse/metadata/sources.csv`, `run_status.csv`; session 309's report (its landing).
