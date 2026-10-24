# Session 2256 report: six held tables described

24 October 2026, from 04:03 UTC, on lab-desktop (the data machine), a session of `queue/done/102-day-5-november-data-poland-belgium-new-zealand-columbia.md`, run beside sessions 2257 to 2259. Model spend USD 0. Pulls: none (Supabase for the lock).

## Read these first

- **Six method notes for source tables that had none,** chosen among the 46 source tables that no note names on its `Tables:` line or by its file name, on this branch, main or the running chains' branches (`runs/c102/s2256/gap.out`). Chain 101's agent's list of its notes and chain 103's agent's list were checked so that none is written twice. The Method cells are filled.

| Note | Rows | Entities, variables | First and last (UTC) | First written |
|---|---|---|---|---|
| `docs/methods/noaa_grid_weather_daily.md` | 118,630 | 7, 6 | 1 January 2019 to 17 October 2026 | session 126 |
| `docs/methods/noaa_grid_weather_hourly.md` | 1,907,625 | 7, 4 | 1 January 2019 to 18 October 2026 | session 126 |
| `docs/methods/noaa_station_weather_hourly.md` | 4,747,179 | 35, 2 | 1 January 2019 to 18 October 2026 | session 129 |
| `docs/methods/ercot_rtm_node_prices.md` | 764,400 | 312, 1 | 28 September to 23 October 2026 | session 120 |
| `docs/methods/ercot_wind_solar_hsl_daily.md` | 198 | 1, 6 | 19 September to 22 October 2026 | session 18 |
| `docs/methods/eia_annual_generation_ba.md` | 515 | 68, 3 | 2023 to 2025 | session 323 |

- **Written by a helper agent in the chain's worktree, checked here:**
  - every count and first and last time recomputed from the tables;
  - each note's `Tables:` line;
  - no non-ASCII character.
  - The main finding below was read again in the table.

  The helper's own cross-checks passed:
  - the grid temperatures rebuilt from the stations;
  - the daily weather rebuilt from the hourly;
  - the HSL days from the hourly HSL table;
  - the EIA totals from the saved workbooks.
- **Found while writing, recorded in the notes and left in the code** (for a code chain):
  1. **`eia_annual_crosscheck_ba` counts storage plants twice.** EIA's storage sheet repeats every generator row of plants with storage, which `net_generation_mwh` already holds. `storage_net_generation_mwh` is called negative in the docstring and session 323's report, but 92 of its 113 values are positive (checked here). Without the double count, California's 2023 gap is about -2.0 percent, not -9.2.
  2. **`ercot_rt_spp.py` and `curtailment.py` use `/misapp` and `/misdownload`,** which ERCOT's robots file disallows (the standing question). `curtailment.py` asks no pause check at all, and the NOAA and ERCOT node connectors do not ask `paused_host()`.
  3. **`curtailment.py` still names ERCOT's report type 13483 NP4-745-CD,** where it is NP4-737-CD. A three-day read window lost 15 October during the gap in runs.
  4. **NOAA's grid tables label MISO's hours of April 2020 to November 2022 ISD-Lite,** where the readings came from the Local Climatological Data. Nine days are missing in every grid, and 42 of ISO-NE's.
  5. **Several docstrings are out of date:**
     - the NOAA table count, its row ceiling, and the dew points' filling;
     - ERCOT's "as printed" prices and the autumn day;
     - `demand_weather.py`'s fit.
- **A coverage row brought up to date:** the Method-cell run rebuilt `ercot_rtm_node_prices`' row from the table on the machine (764,400 rows to 23 October), which the note found stale (734,448 to 22 October). The archive manifest still holds the earlier run, until the table's next archive.

## Errors

- None.

## Decisions made without you

- **These six chosen,** public source tables of three publishers, none planned by the chains beside this one.
- **No code changed;** the faults are for a code chain.

## For Samuel's ruling

- None new. The ERCOT robots question stands.

## Files

- New: the six notes above, this report.
- Changed: `docs/coverage.md` (the six Method cells, the node prices' row) and `warehouse/metadata/coverage.csv` (the node prices' row).
- On the data machine only: `runs/c102/s2256/`.
