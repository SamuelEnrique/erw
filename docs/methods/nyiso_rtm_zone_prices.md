# NYISO real-time LBMPs, 15-minute means of the 5-minute prices, 11 load zones (P-24A)

Energy Research Warehouse (ERW), method note written in session 2214 (chain 098) for a table of the shared price connector. The day-ahead table beside it is `docs/methods/nyiso_dam_zone_prices.md`.

Tables: `nyiso_rtm_zone_prices`

## Publisher and address

New York Independent System Operator (NYISO), Real-Time Market LBMP, zonal, RTD 5-minute, report P-24A (`http://mis.nyiso.com/public/P-24Alist.htm`): a CSV a day, `http://mis.nyiso.com/public/csv/realtime/<YYYYMMDD>realtime_zone.csv`, and a zip a month (`.../realtime/<YYYYMM>01realtime_zone_csv.zip`), read with gridstatus 0.36.0 (`NYISO.get_lmp`, REAL_TIME_5_MIN). Source id `nyiso:realtime`. Raw files under `warehouse/raw/nyiso/<run_id>/`.

Connector: `warehouse/connectors/iso_prices.py`, `pull_nyiso`: the N complete operating days before today in New York time; a market's file is written only if every zone has every quarter hour of the window.

Schedule: the daily run, `warehouse/run_daily.sh`, in its ISO loop: `iso_prices.py nyiso --days 3` under the 15-minute pull budget, on the GitHub runner (`.github/workflows/daily-prices.yml`). The table is one of the rolling-window tables restored before each run (`warehouse/redivis/config.yaml`).

## Vintage and revision

Header line 1: rebuilt from the ERW archive as of run `20261023T152740Z-github`; the table's own header, run `20261023T141819Z`: "Window: NYISO operating days 2026-10-20 to 2026-10-22", "This run wrote 3168 rows: 1056 new, 2112 replacing ...; 57024 rows are kept from earlier runs." `retrieved_at` runs from 2026-09-25T07:13:04Z to 2026-10-23T14:18:21Z (57 values); `vintage` the file's Last-Modified, 35 values from 2026-09-01T03:57:09Z to 2026-10-23T03:57:06Z, never before the interval it prices.

## Shape and variables

Series, 60,192 rows: 11 zones for each of 5,472 quarter hours. `entity` `nyiso:<zone>` (CAPITL, CENTRL, DUNWOD, GENESE, HUD VL, LONGIL, MHK VL, MILLWD, N.Y.C., NORTH, WEST), `node` the zone, `variable` lmp_rtm_15m_mean, `unit` USD/MWh, `freq` PT15M, `geo` US-NY, `market` nyiso_rtm.

| Zone | Mean | Lowest | Highest |
|---|---|---|---|
| WEST | 37.05 | -14.0933 | 647.5833 |
| GENESE | 38.35 | -5.2067 | 663.3267 |
| CENTRL | 39.50 | -5.31 | 682.13 |
| NORTH | 39.62 | -345.4867 | 692.8 |
| MHK VL | 40.64 | -28.29 | 712.4333 |
| CAPITL | 41.05 | -65.53 | 715.5367 |
| HUD VL | 42.18 | -47.4667 | 718.5767 |
| MILLWD | 42.47 | 3.7667 | 1,159.6633 |
| DUNWOD | 42.91 | 3.79 | 1,383.92 |
| N.Y.C. | 43.54 | -43.0567 | 2,840.39 |
| LONGIL | 46.21 | 3.8 | 1,165.6367 |

39 values are negative; the lowest is NORTH's -345.4867 (2026-10-22T11:15:00Z), the highest N.Y.C.'s 2,840.39 (2026-10-16T22:00:00Z).

## Placing values in time, and what is filled

NYISO stamps each RTD price at its interval's end and adds irregular intervals between the regular 5-minute stamps; each 15-minute value is the time-weighted mean of the prices covering the quarter hour (each weighted from the previous stamp to its own, an interval crossing a quarter-hour boundary split at it), rounded to 4 decimals; no interval may exceed 5 minutes and every quarter hour must be fully covered, or the run writes nothing for the market (the header's note). `ts_utc` is the quarter hour's start. Nothing is filled.

## License

The header carries no license line. `docs/licenses.md` gives verdict "needs written permission", decided by NYISO, flag public, "ruled: license needed from 2026-10-21", ERW verdict "unsettled". That ruling of 21 October 2026, which governs NYISO's tables (`docs/methods/nyiso_dam_zone_prices.md`), governs this table's standing.

## Checks (session 2214)

The figures in this note were computed from the rows of `warehouse/output/nyiso_rtm_zone_prices.csv`, read past its 11 header lines (scripts in `runs/c098/s2214/`).

- 60,192 rows, `ts_utc` from 2026-08-26T04:00:00Z to 2026-10-23T03:45:00Z, as the header states; no (entity, variable, ts_utc) twice; all 11 zones in every quarter hour held.
- One whole day is absent: the 96 quarter hours of New York's 15 October 2026 (from 2026-10-15T04:00:00Z), at every zone; the span holds 5,568 quarter hours, the table 5,472.
- Against the zone price history (`iso_zone_prices_history`, NYISO's hourly `lmp_rtm`): the mean of each hour's four quarter hours is within 0.01 USD/MWh of it in 11,646 of 11,660 hours, within 0.15 in all.
- Against the day-ahead table (`nyiso_dam_zone_prices`): over 15,048 zone-hours the real-time hourly mean is below the day-ahead price in 64.8 percent, by 1.69 USD/MWh on average.

## Where the description and the data disagree

1. **No license in the header.** The header names source, run and files but no license, while the license record rules NYISO's data "needs written permission" from 2026-10-21; the daily run still pulls the table.
2. **A day missing without a word.** The header's "File holds 60192 rows, 2026-08-26T04:00:00Z to 2026-10-23T03:45:00Z" reads as a complete span; 15 October 2026 is absent at every zone (its runs' windows were not complete), and with a 3-day window no later run asks for it again.

Recorded, not changed in session 2214: the license record governs the table's standing whatever its header lacks, as for NYISO's other tables. 15 October is not filled: a backfill is a request to NYISO, whose data the license record rules unsettled, and session 2214 made no request; a reader of this table counts the quarter hours of a day before using it.

## What it does not hold

- Day-ahead prices (`nyiso_dam_zone_prices`), NYISO's generator nodes, the 5-minute prices themselves, the loss and congestion parts, and days before 2026-08-26 (the hourly history is in `iso_zone_prices_history`).
