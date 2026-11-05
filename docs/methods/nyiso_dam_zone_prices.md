# NYISO day-ahead LBMPs by the hour, 11 load zones (P-2A, damlbmp)

Energy Research Warehouse (ERW), method note written in session 2166 (chain 094) for a table of the shared price connector.

Tables: `nyiso_dam_zone_prices`

## Publisher and address

New York Independent System Operator (NYISO), Day-Ahead Market LBMP, zonal, report P-2A (`http://mis.nyiso.com/public/P-2Alist.htm`): a CSV a day, `http://mis.nyiso.com/public/csv/damlbmp/<YYYYMMDD>damlbmp_zone.csv`, and a zip a month for days the month's archive holds, `.../damlbmp/<YYYYMM>01damlbmp_zone_csv.zip`; read with gridstatus 0.36.0 (`NYISO.get_lmp`, DAY_AHEAD_HOURLY). Source id `nyiso:damlbmp`. Raw files under `warehouse/raw/nyiso/<run_id>/` with a manifest.

Connector: `warehouse/connectors/iso_prices.py`, `pull_nyiso` (session 1 and 2 rules): the N complete operating days before today in New York time, and any later day whose day-ahead results are published and complete (the next-day auction); a market's file is written only if every zone has every hour of the window.

Schedule: the daily run, `warehouse/run_daily.sh`, in its ISO loop (`ISOS` "ercot caiso nyiso spp isone"): `iso_prices.py nyiso --days 3` under the 15-minute pull budget, on the GitHub runner (`.github/workflows/daily-prices.yml`). The table is one of the rolling-window tables restored before each run (`warehouse/redivis/config.yaml`, `restore_before_run`). `warehouse/scheduled.py price_compare` (monthly) reads it.

## Vintage and revision

Header line 1: rebuilt from the ERW archive as of run `20261023T152740Z-github`; the table's own header, run `20261023T141819Z`: "Window: NYISO operating days 2026-10-20 to 2026-10-22", "Forward DAM days also included (published before retrieval): 2026-10-23, 2026-10-24", "This run wrote 1320 rows: 264 new, 1056 replacing earlier rows with the same (entity, variable, ts_utc); 14520 rows are kept from earlier runs." Each operating day is read on several consecutive runs; the last read stands. `retrieved_at` runs from 2026-09-25T07:12:46Z to 2026-10-23T14:18:19Z (40 values). `vintage` is the file's publication (its HTTP Last-Modified), 38 values from 2026-08-30T13:33:05Z to 2026-10-23T13:34:02Z, none blank.

## Shape and variables

Series, 15,840 rows: 11 zones for each of 1,440 hours. `entity` `nyiso:<zone>` (CAPITL, CENTRL, DUNWOD, GENESE, HUD VL, LONGIL, MHK VL, MILLWD, N.Y.C., NORTH, WEST), `node` the zone, `variable` lmp_dam, `unit` USD/MWh, `freq` PT1H, `geo` US-NY, `market` nyiso_dam, `source_url` the file the row came from: the August zip (1,584 rows), the September zip (4,752 rows), and a daily CSV for each later day (264 rows each).

| Zone | Mean, USD/MWh | Lowest | Highest |
|---|---|---|---|
| WEST | 38.84 | 15.13 | 86.65 |
| GENESE | 39.91 | 14.2 | 87.93 |
| CENTRL | 41.20 | 15.7 | 90.64 |
| NORTH | 41.78 | 15.4 | 89.83 |
| MHK VL | 42.65 | 16.06 | 95.14 |
| CAPITL | 42.91 | 16.16 | 93.07 |
| HUD VL | 43.63 | 16.59 | 98.91 |
| MILLWD | 44.60 | 16.89 | 142.18 |
| DUNWOD | 44.68 | 17.05 | 104.82 |
| N.Y.C. | 45.21 | 17.1 | 119.6 |
| LONGIL | 46.48 | 17.38 | 122.02 |

All rows: mean 42.90; lowest 14.2 (GENESE, 2026-10-05T20:00:00Z), highest 142.18 (MILLWD, 2026-09-01T21:00:00Z); none negative.

## Placing values in time

`ts_utc` is the hour's start in UTC (the header: "ts_utc is interval start, UTC"), converted from NYISO's New York time; the window's days are New York operating days, so each holds 24 hours from 04:00 UTC in daylight time (and 23 or 25 at the clock changes, none in this span).

## What is and is not filled

A run's market is written only when every zone has every hour of every day of its window; a forward day only when complete. Nothing is filled. Rows are merged by (entity, variable, ts_utc) and never dropped by the connector: the table begins where its first pull began (the oldest rows, 26 to 31 August 2026, were retrieved on 2026-09-25).

## License

The header carries no license line. `license_verdicts.csv` records NYISO, read 5: "needs written permission", for public and for commercial use. `docs/licenses.md`: verdict "needs written permission", decided by NYISO, flag public, "ruled: license needed from 2026-10-21", ERW verdict "unsettled".

## Checks (session 2166)

The figures in this note were computed from the rows of `warehouse/output/nyiso_dam_zone_prices.csv`, read past its 11 header lines (scripts in `runs/c094/s2166/`).

- 15,840 rows, `ts_utc` from 2026-08-26T04:00:00Z to 2026-10-25T03:00:00Z, as the header states: New York operating days 2026-08-26 to 2026-10-24, 60 days of 24 hours, every hour of the span present with all 11 zones. No (entity, variable, ts_utc) twice.
- Against the zone price history (`iso_zone_prices_history`, NYISO's `lmp_dam` rows): of the 11,880 zone-hours both tables hold, all 11,880 are equal to the cent.
- N.Y.C. against WEST: N.Y.C. is the higher in 99.8 percent of the hours, by 6.37 USD/MWh on average.
- `vintage` is later than the row's own hour on 5,918 rows: the monthly zips' Last-Modified times (2026-08-30 and later) postdate many of the days they hold.

## Where the description and the data disagree

1. **No license in the header.** The table's header names its source, run and files but no license; the license record rules NYISO's data "needs written permission" (from 2026-10-21), and the daily run still pulls the table (run `20261023T141819Z`).
2. **`vintage` as the publication time.** The connector's docstring gives `vintage` as "the ISO's publish time where it gives one ... else the file's HTTP Last-Modified header". For the 6,336 rows from NYISO's monthly zips it is the zip's last update, later than the hour priced on 5,918 rows, not when that day's prices were published.

Recorded, not changed in session 2166: the license record (the ruling of 21 October 2026, license needed) governs the table's standing, whatever its header lacks.

## What it does not hold

- Real-time prices (`nyiso_rtm_zone_prices`), NYISO's generator nodes, days before 2026-08-26 (the history is in `iso_zone_prices_history`), and the loss and congestion parts of the LBMP.
