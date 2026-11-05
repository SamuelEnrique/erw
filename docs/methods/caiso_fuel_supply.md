# CAISO supply by fuel source, hourly, from 1 June 2025 (Today's Outlook, the daily table)

Energy Research Warehouse (ERW), method note written in session 2166 (chain 094) for a table first written in session 73 and kept daily since session 82. Its earlier years are `caiso_fuel_supply_history` (`docs/methods/caiso_fuel_supply_history.md`, June 2018 to May 2025), read with the same rules; this note gives what differs.

Tables: `caiso_fuel_supply`

## Publisher and address

California ISO (CAISO), Today's Outlook, supply by fuel source: one CSV a Pacific day, `https://www.caiso.com/outlook/history/YYYYMMDD/fuelsource.csv` (page `https://www.caiso.com/todays-outlook/supply`). Source id `caiso:todays_outlook_fuelsource` (the history table's is `caiso:todays_outlook_fuelsource_history`). Raw files under `warehouse/raw/caiso_fuel_supply/<run_id>/`.

Connector: `warehouse/connectors/caiso_fuel_supply.py` (session 73). `--start` pulls a range (session 73's approved pull from 2025-06-01); `--days N` pulls the N Pacific days ending yesterday and merges them into the table (session 82).

Schedule: the daily run, `warehouse/run_daily.sh`, step `caiso_fuel_supply` (`caiso_fuel_supply.py --days "$DAYS"`, 3 days by default, under the 15-minute pull budget), on the GitHub runner (`.github/workflows/daily-prices.yml`), followed by `carbon_intensity.py` and `caiso_join.py --apply`, which read California's generation here (`docs/methods/eia930_caiso_break.md`). `warehouse/scheduled.py mix_profile` (monthly) reads it too. The docstring: "On the runner the table is restored from Redivis first".

## Vintage and revision

Header line 1: rebuilt from the ERW archive as of run `20261023T152740Z-github`; the table's own header, run `20261023T143604Z`: "this run pulled Pacific days 2026-10-20 to 2026-10-22", "This run wrote 936 rows: 312 new, 624 replacing earlier rows with the same (entity, variable, ts_utc); 156312 rows are kept from earlier runs." So each day is read three times on consecutive runs, and the last read stands. `retrieved_at` runs from 2026-10-03T09:42:30Z to 2026-10-23T14:36:05Z (81 values); `vintage` is empty.

## Shape and variables

Series, 157,248 rows: 13 variables for each of 12,096 hours, entity `caiso:ISO`, `unit` MW, `freq` PT1H, `geo` US-CA, `market` and `node` empty, `source_url` the day's file (504 addresses, one per day written).

| `variable` | Lowest, MW (hour) | Highest, MW (hour) | Mean, MW |
|---|---|---|---|
| solar_mw | -83.33 (2026-09-21T02:00:00Z) | 23,780.42 (2026-08-19T18:00:00Z) | 7,163.56 |
| wind_mw | 63.5 (2025-12-14T16:00:00Z) | 8,253.5 (2026-05-15T08:00:00Z) | 2,827.85 |
| geothermal_mw | 488.42 | 846.33 | 735.87 |
| biomass_mw | 84.5 | 294.0 | 219.89 |
| biogas_mw | 109.5 | 179.58 | 159.27 |
| small_hydro_mw | 113.25 | 466.5 | 254.58 |
| coal_mw | -8.0 (2026-10-21T20:00:00Z) | 5.0 | 0.09 |
| nuclear_mw | 1,101.17 (2026-10-23T06:00:00Z) | 2,329.58 | 2,137.45 |
| natural_gas_mw | 261.75 (2026-05-10T20:00:00Z) | 22,240.25 (2026-09-10T02:00:00Z) | 6,197.82 |
| large_hydro_mw | -622.58 | 5,300.0 | 2,149.99 |
| batteries_mw | -11,548.5 (2026-10-06T16:00:00Z) | 12,680.5 (2026-08-20T02:00:00Z) | -268.86 |
| imports_mw | -6,799.42 (2025-06-09T23:00:00Z) | 11,015.5 (2026-01-16T10:00:00Z) | 3,804.52 |
| other_mw | 0.0 | 0.0 | 0.0 |

## Placing values in time, and what is filled

As in the history table: each `Time` of CAISO's file is placed on its Pacific day (`tz_localize(..., ambiguous="infer")`, no rule for a nonexistent time), and `ts_utc` is the start of the UTC hour. A day is written only with every 5-minute interval, no stamp twice and twelve in every hour; nothing is filled. A day missing from the table is asked again only while it is among the last 3 days.

## License

Header: "License: public (CAISO public system data; cite "California ISO, Today's Outlook")." `license_verdicts.csv` records CAISO, read 3: "may be public", for public and for commercial use. `docs/licenses.md`: "may be public", flag public, ERW verdict public.

## Checks (session 2166)

The figures in this note were computed from the rows of `warehouse/output/caiso_fuel_supply.csv`, read past its 12 header lines (scripts in `runs/c094/s2166/`).

- 157,248 rows, `ts_utc` from 2025-06-01T07:00:00Z to 2026-10-23T06:00:00Z, as the header states. No (entity, variable, ts_utc) twice; every hour holds all 13 variables; every Pacific day written holds 24 hours; every row's file is its own Pacific day.
- Days: 504 written of the 509 Pacific days from 2025-06-01 to 2026-10-22. Absent: 2025-11-02 and 2026-03-08 (the two clock-change days), 2026-08-21, 2026-09-22 and 2026-10-15.
- Continuity with the history table: its last hour is 2025-06-01T06:00:00Z, this table's first 2025-06-01T07:00:00Z.
- Against CAISO's own load (`caiso_area_load_hourly`, `caiso:system`, held to 2026-10-10T14:00:00Z): over 11,816 shared hours, the sum of the 13 sources falls below the load by a median of 2.30 percent; within 1 percent in 23.6 percent of the hours, within 3 percent in 52.6, within 5 percent in 63.1. (Over the history table's shared hours the sum ran 1.66 percent above the load.)
- Monthly means (MW): natural gas from 1,888.9 (May 2026) to 11,466.0 (August 2026); solar from 3,551.2 (December 2025) to 9,618.6 (June 2026); imports from 1,966.8 (July 2025) to 7,043.8 (December 2025); batteries between -328.6 and -182.0, net charging in every month.

## Where the description and the data disagree

1. **Clock-change days.** The docstring says a day needs "288, or 276 and 300 on the clock-change days" intervals; the code's localization cannot place a nonexistent or (without a pattern it can infer) a repeated time, and neither clock-change day of the span (2025-11-02, 2026-03-08) is in the table. The header calls the days not written "short of any 5-minute interval".
2. **The ceiling.** The docstring says "the run stops before writing if the table would exceed" 300,000 rows; the code compares the run's own rows with the ceiling (`len(s) > CEILING`), never the merged table. The table holds 157,248 rows.
3. **"Every day pulled since 2025-06-01".** Header line 3 says "the table holds every day pulled since 2025-06-01"; five days in that span are absent, and only the last run's skips are named.

Acted on in session 2166: the connector's docstring now says no clock-change day is written, names the three other days absent, and says the ceiling counts a run's own rows; its header's window line says the complete days. The table is as its runs wrote it.

## What it does not hold

- Days before 2025-06-01 (`caiso_fuel_supply_history`), the five days above, and any 5-minute value.
- Demand, curtailment, or generation by plant or area.
