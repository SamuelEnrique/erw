# Session 2270 report: six held tables linked to the notes that describe them (ERCOT's reserve price roll-ups, storage offers and real time, the stress days)

24 October 2026, from 04:26 UTC, on lab-desktop (the data machine), chain 103, unattended. Model spend USD 0. Pulls: none.

## Read these first

- **How the tables were chosen:** 102 tables have an empty Method cell in `docs/coverage.md` on this branch, on main and on chains 101's and 102's branches (`runs/c103/s2270/empty.py`). Only two of them, this chain's own, are named in no note at all. The rest are described in notes whose `Tables:` line, if there is one, does not begin the line, so `build_coverage.py`'s lookup misses them. Chain 102's agent said its session 2256 takes `noaa_grid_weather_daily`, `noaa_grid_weather_hourly`, `noaa_station_weather_hourly`, `ercot_rtm_node_prices`, `ercot_wind_solar_hsl_daily` and `eia_annual_generation_ba`, so those are left to it.
- **Six `Tables:` lines,** in notes that already describe each table, each checked against the table read past its header lines:
  - `ercot_as_prices_daily` and `ercot_as_prices_monthly` in `docs/methods/ercot_as_prices_rollup.md`: 70,520 and 2,325 rows, five products, ECRS from 10 June 2023, the hours of a day 23 to 25 and of a month 672 to 744. The note's five variables are the tables' five.
  - `ercot_storage_dam_offers_daily` in `docs/methods/ercot_storage_dam_offers.md`, whose own line named only the monthly table: 20,280 rows, 78 variables, all covered by the note's variable table (by its `<service>` and `<P>` patterns).
  - `ercot_storage_rt_monthly` and `ercot_storage_node_basis` in `docs/methods/ercot_storage_realtime.md`. `ercot_rtm_node_prices`, named in the same note, is left to chain 102.
  - `grid_stress_days` in `docs/methods/stress_days.md`: 282 rows, by grid 169, 58, 10, 16, 17 and 12, and 74, 25, 2, 7, 9 and 3 events, as the note's table.
- **The six Method cells set** by `build_coverage.py`'s own `method_cell`; nothing else on the lines changed.

## Contradictions found, written into the notes, no code changed

1. **`ercot_storage_realtime.md` left six of the monthly table's variables unnamed:** `days_held`, `days_in_month`, `resources`, `resource_hours` and the two counts of resource-hours in one file only. They are now named, from the builder's lines 183 to 185.
2. **The same note calls the node basis "one week".** The table held today gives `whole_days` 21 and an `intervals_median` of 2,065 over 293 points (231 wider than the hub), on its one date, 28 September 2026. The note now says so and lists the summary entity's 13 variables.
3. **`stress_days.md` says only CAISO's notices are held,** and "the price test alone" holds on five grids. Since session 322, ERCOT's notices (`ercot_grid_notices`) count too: among ERCOT's stress days `x_notices` gives `weather_watch` 36 times and `conservation_appeal` 18. The note now says so (four grids by price alone) and names the `x_` columns.

## Checks

- `tests.test_session116`, `120`, `148`, `306`, `322`, `674`, `1000` and `1001`: 135 tests, OK (12 skipped).

## Decisions made without you

- **`Tables:` lines rather than new notes,** where an existing note describes the table, as session 2228 did.

## For Samuel's ruling

- None new.

## Files

- Changed: `docs/methods/ercot_as_prices_rollup.md`, `ercot_storage_dam_offers.md`, `ercot_storage_realtime.md`, `stress_days.md`, `docs/coverage.md` (six Method cells).
- New: this report. On the data machine only: `runs/c103/s2270/`.
