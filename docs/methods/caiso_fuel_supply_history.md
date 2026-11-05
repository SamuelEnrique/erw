# CAISO supply by fuel source, hourly, June 2018 to May 2025 (Today's Outlook history files)

Energy Research Warehouse (ERW), method note written in session 2124 (chain 079) for a table first written on 6 October 2026 (session 133).

Tables: `caiso_fuel_supply_history`

## Publisher and address

California ISO (CAISO), Today's Outlook, supply by fuel source: one CSV a Pacific day, `https://www.caiso.com/outlook/history/YYYYMMDD/fuelsource.csv`; the page is `https://www.caiso.com/todays-outlook/supply`. Source id `caiso:todays_outlook_fuelsource_history` (in `sources.csv`, license public, first and last seen 2026-10-06). Raw files: `warehouse/raw/caiso_fuel_supply_history/<run_id>/`.

Connector: `warehouse/connectors/caiso_fuel_supply_history.py` (session 133, an approved pull), which borrows the address, the 13 source columns and their names from `caiso_fuel_supply.py` (the table from 2025-06-01 on). It asks the days of its fixed window, 2018-06-01 to 2025-05-31 (2,557 days), with four threads and a quarter second's pause each, and refuses a window that could pass the ceiling of 800,000 rows. `--start`, `--end`, `--dry-run` and `--out-dir` narrow or try it. No schedule runs it: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh` or `.github/workflows/` names it. Readers named in `license_tables.csv`: `generation_mix_hourly_profile`, `generation_mix_records`. Its reason (the docstring): EIA-930 holds no California hydro from October 2019 to August 2020; `docs/methods/generation_mix_hourly.md` ("California's hydro gap") reads this table for those months.

## Vintage and revision

One run, `20261006T091710Z` (6 October 2026); `retrieved_at` runs from 2026-10-06T09:17:10Z to 2026-10-06T09:22:05Z (296 distinct values; each row carries the time its day's file was read). Header: "This run wrote 782808 rows: 782808 new, 0 replacing earlier rows with the same (entity, variable, ts_utc); 0 rows are kept from earlier runs." The last header line: "Restored from the Redivis draft (energy_research_warehouse) by scripts/sync.py". `vintage` is empty: the file states no publication time. No schedule asks the files again.

## Shape and variables

Series, 782,808 rows: 13 variables for each of 60,216 hours, entity `caiso:ISO`, `unit` MW, `freq` PT1H, `geo` US-CA; `market`, `node` and `vintage` empty; `source_url` the day's file (2,509 distinct addresses, one per day written).

| `variable` | Lowest, MW (hour) | Highest, MW (hour) | Mean, MW |
|---|---|---|---|
| solar_mw | -132.0 (2019-11-13T02:00:00Z) | 21,446.5 (2025-05-22T19:00:00Z) | 4,268.76 |
| wind_mw | -1,939.33 (2020-10-17T22:00:00Z) | 6,289.42 (2022-05-28T20:00:00Z) | 2,238.46 |
| geothermal_mw | 206.58 (2019-11-01T20:00:00Z) | 1,131.25 (2021-11-07T06:00:00Z) | 859.25 |
| biomass_mw | 37.58 (2025-04-08T13:00:00Z) | 480.58 (2020-08-18T23:00:00Z) | 292.50 |
| biogas_mw | 79.33 (2025-04-18T17:00:00Z) | 491.67 (2018-12-12T08:00:00Z) | 201.99 |
| small_hydro_mw | -334.0 (2019-07-19T22:00:00Z) | 36,178.67 (2019-10-01T17:00:00Z) | 257.95 |
| coal_mw | -8.0 (2022-09-12T08:00:00Z) | 29.83 (2018-11-09T17:00:00Z) | 8.85 |
| nuclear_mw | -74.0 (2020-11-02T08:00:00Z) | 2,309.25 (2025-04-13T02:00:00Z) | 1,979.39 |
| natural_gas_mw | -35,159.67 (2019-10-01T17:00:00Z) | 26,482.17 (2022-09-07T03:00:00Z) | 8,449.18 |
| large_hydro_mw | -549.25 (2021-02-20T19:00:00Z) | 6,241.92 (2019-06-05T02:00:00Z) | 2,026.57 |
| batteries_mw | -8,029.08 (2025-01-11T19:00:00Z) | 9,355.5 (2025-04-22T02:00:00Z) | -19.18 |
| imports_mw | -15,207.58 (2019-10-02T22:00:00Z) | 11,869.42 (2018-08-17T03:00:00Z) | 4,886.16 |
| other_mw | 0.0 | 2.0 (2022-03-21T09:00:00Z) | 0.0013 |

`batteries_mw` is positive when discharging (header). The value is the mean of the hour's twelve 5-minute values, rounded to 4 decimals, so it is also the hour's MWh.

## Placing values in time

- Each row of CAISO's file has a `Time` (HH:MM) within the Pacific day named in the address. The connector places it on that day in America/Los_Angeles (`tz_localize(..., ambiguous="infer")`, with no rule for a time that does not exist), converts to UTC and takes the hour by flooring: `ts_utc` is the start of the UTC hour, and each `Time` is read as the start of its 5-minute interval.
- A column is matched to its source whatever its case (CAISO wrote "Natural gas" and "Large hydro" in lower case until 2021).

## What is and is not filled

- A day is written only when it holds exactly the expected number of 5-minute intervals (288 on an ordinary day), no stamp twice, and twelve in every hour. An interval with any of the 13 sources empty is dropped first, so it makes its day short.
- A day that falls short, fails to parse or fails its request is logged and skipped; nothing is filled. Header line 3 lists the first eight of the 48 days skipped.

## License

Header: "License: public (CAISO public system data; cite "California ISO, Today's Outlook")." `license_verdicts.csv` records CAISO, read 3: "may be public", for public and for commercial use, with the note "Credit the California ISO and keep its notices." `docs/licenses.md` lists `caiso_fuel_supply_history` under CAISO: "may be public", flag public, ERW verdict public.

## Checks (session 2124)

The figures in this note were computed from the rows of `warehouse/output/caiso_fuel_supply_history.csv`, read past its 12 header lines.

- 782,808 rows, `ts_utc` from 2018-06-01T07:00:00Z to 2025-06-01T06:00:00Z, as the header states; "Rows: 782,808 of the 800,000 ceiling" agrees.
- No (entity, variable, ts_utc) is given twice. Every one of the 60,216 hours holds all 13 variables; every one of the 2,509 Pacific days written holds 24 hours.
- Days: 2,509 written and 48 absent of the window's 2,557, as the header says. Absent by year: 2018: 3, 2019: 10, 2020: 5, 2021: 10, 2022: 10, 2023: 2, 2024: 7, 2025: 1. The 48: 2018-09-22, 2018-11-04, 2018-11-27, 2019-01-02, 2019-02-14, 2019-03-10, 2019-03-13, 2019-03-26, 2019-05-10, 2019-09-07, 2019-09-16, 2019-09-25, 2019-11-03, 2020-02-18, 2020-03-08, 2020-09-05, 2020-11-01, 2020-12-03, 2021-03-14, 2021-05-19, 2021-06-15, 2021-08-05, 2021-08-06, 2021-08-09, 2021-08-10, 2021-08-13, 2021-08-16, 2021-11-07, 2022-03-13, 2022-03-28, 2022-03-29, 2022-03-30, 2022-05-06, 2022-05-11, 2022-05-17, 2022-05-18, 2022-05-19, 2022-11-06, 2023-03-12, 2023-11-05, 2024-01-11, 2024-03-10, 2024-06-27, 2024-06-29, 2024-08-29, 2024-09-24, 2024-11-03, 2025-03-09.
- All 14 clock-change days of the window are among the 48 (seven of 25 hours: 2018-11-04, 2019-11-03, 2020-11-01, 2021-11-07, 2022-11-06, 2023-11-05, 2024-11-03; seven of 23 hours: 2019-03-10, 2020-03-08, 2021-03-14, 2022-03-13, 2023-03-12, 2024-03-10, 2025-03-09).
- One hour stands out: at 2019-10-01T17:00:00Z natural gas is -35,159.67 MW and small hydro 36,178.67 MW, the table's extremes for both; the 13 sources still sum to 18,073.42 MW.
- Against CAISO's own load (`caiso_area_load_hourly`, entity `caiso:system`, held from 2021-09-17): over the 31,974 hours both tables hold, the sum of the 13 sources (imports and battery charging included, with their signs) exceeds the load by a median of 1.66 percent; it is within 1 percent of the load in 17.3 percent of the hours, within 3 percent in 49.9 percent and within 5 percent in 73.6 percent. The widest gaps are spring middays of 2025, the sum below the load: 2025-04-06T19:00:00Z, 12,328.2 MW against 18,518 MW. The two tables measure different things (supply by source here, the TAC areas' integrated load there); the comparison says how far apart they run, not that either is wrong.

## Where the description and the data disagree

1. **No clock-change day can be written.** The docstring allows "325 on the day the clocks go back" and the ceiling check counts a 25th hour; the code localizes with `ambiguous="infer"` and no rule for a nonexistent time. In the data every Pacific day has 24 hours, and all 14 clock-change days of the window are absent. Header line 3 gives the reasons for two of them, `AmbiguousTimeError('2018-11-04 01:00:00')` and `NonExistentTimeError('2019-03-10 02:00:00')`, while the same line describes the skipped days as "short of any 5-minute interval".
2. **"Eight days in the window have a 25th hour"** (the code's comment on the ceiling). The window holds seven: 2018-11-04, 2019-11-03, 2020-11-01, 2021-11-07, 2022-11-06, 2023-11-05 and 2024-11-03.
3. **Hydro "throughout".** The docstring gives the table's reason: "CAISO's own supply by fuel has hydro throughout" for October 2019 to August 2020. The table has no row on three days of those months: 2019-11-03, 2020-02-18 and 2020-03-08.

Acted on in session 2124: the code's comment now says seven days, and the docstring says no clock-change day is written and that 2020-02-18 is absent from the hydro months. The table is as its run wrote it.

## What it does not hold

- Days from 2025-06-01 on (`caiso_fuel_supply`), the 48 days above, and any 5-minute value.
- CAISO's demand, its curtailment, or generation by plant or area.
