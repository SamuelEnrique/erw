# ERCOT wind and solar output, system-wide, an hour, 2023 to 2025 (ERCOT PG7-126-M, Hourly Aggregated Wind and Solar Output)

Energy Research Warehouse (ERW), method note written in session 2152 (chain 092) for a table first written on 7 October 2026 (session 144).

Tables: `ercot_wind_solar_output_hourly`

## Publisher and address

Electric Reliability Council of Texas (ERCOT), report PG7-126-M, "Hourly Aggregated Wind and Solar Output" (report type 13424), on its public reports site: one Excel workbook a year. The public list kept three, 2023, 2024 and 2025, on 7 October 2026 (the connector's docstring: display duration 1,095 days). Of each workbook the connector reads the sheets Wind Data and Solar Data, and of each the column Time (Hour-Ending), Central clock time, and the output column, ERCOT.WIND.GEN or ERCOT.PVGR.GEN (or the names "Total Wind Output, MW" and "Total Solar Output, MW"). ERCOT.LOAD, installed capacity and the ratios are not read; the workbooks hold no High Sustained Limit and no region.

`https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=13424` (the document list, JSON)

`https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=<DocID>` (each workbook)

Product page `https://www.ercot.com/mp/data-products/data-product-details?id=PG7-126-M`, named in the header and not asked. Every request goes to the host `www.ercot.com`, under `/misapp/` and `/misdownload/`, paths ERCOT's robots file disallows (read by session 850, and again by session 2002 at 15:11:50 UTC on 23 October 2026, read 170 of `warehouse/metadata/license_reads.csv`), with the User-Agent "Mozilla/5.0 (Energy Research Warehouse; https://github.com/SamuelEnrique/erw)". Source id `ercot:PG7-126-M`. Connector: `warehouse/connectors/ercot_wind_solar_history.py` (session 144), which also writes `ercot_wind_solar_hsl_hourly` and `ercot_wind_solar_hsl_monthly` (`docs/methods/curtailment.md`).

It is run every day by `warehouse/run_daily.sh` (`pull ercot_wind_solar_history ... --pull --write`, under a pull budget of 15 minutes, `warehouse/pull_budget.py`), which `.github/workflows/daily-prices.yml` runs on GitHub's runner; `--write` rebuilds this table whole from the saved workbooks on every run. `run_status.csv` records the table in every run from 7 October 2026, the last `20261023T144737Z`: "52,608 rows this run, 2023-01-01T06:00:00Z to 2026-01-01T05:00:00Z". The first date is from session 144's report ("Run on 7 October 2026 (UTC)"; `ercot_wind_solar_output_hourly` 52,608 rows, 2023 to 2025) and from the rows: every `retrieved_at` is 7 October 2026, the earliest 09:22:54 UTC.

## Vintage and revision

Central years 2023 to 2025 (1 January 2023 06:00 UTC to 1 January 2026 05:00 UTC) in the file on the data machine, rebuilt from the ERW archive by `warehouse/restore_tables.py` as of run `20261020T063359Z-github`, with the header of the connector's run `20261020T061137Z`: "ERCOT_2023_Hourly_WindSolar_Output 2023-01-01T06Z to 2024-01-01T05Z, 17,520 values; ERCOT_2024_Hourly_WindSolar_Output 2024-01-01T06Z to 2025-01-01T05Z, 17,568 values; ERCOT_2025_Hourly_WindSolar_Output 2025-01-01T06Z to 2026-01-01T05Z, 17,520 values." Each row's `source_url` is its workbook's address (three); `retrieved_at` is 7 October 2026 for every row (09:22:54 UTC for 2025, 09:32:46 and 09:32:54 UTC for 2023 and 2024), kept by the archive from the run that first archived the values; `vintage` is empty (the publish time is in the raw manifest only). `coverage.csv` gives the same 52,608 rows and dates: it agrees.

`--pull` asks the list afresh each run and saves any workbook not already saved under `warehouse/raw/ercot_wind_solar_history/` (its `manifest.csv`); `--write` reads every saved workbook, and where two hold the same hour the later published is kept. When ERCOT posts the 2026 workbook the next run adds it. `ip.write_csv` merges into the file held, but this table is not one the runner restores before the run (`warehouse/redivis/config.yaml`), so on the runner the file is written from that run's workbooks only.

## Shape and variables

Series, 52,608 rows, one entity. `entity` `ercot:system`; `variable` `wind_generation_mw` (ERCOT.WIND.GEN) and `solar_generation_mw` (ERCOT.PVGR.GEN); `value` the workbook's hourly aggregated output as stored, not rounded (for example 1.0000046131608542e-05); `unit` MW; `freq` PT1H; `ts_utc` the hour's start, from the hour ending (Central clock time) less one hour, the first of an hour ending listed twice in autumn taken as daylight time; `market` and `node` empty; `geo` US-TX; `vintage` empty.

| Entity | Variable | Hours | Mean MW | Lowest | Highest |
|---|---|---|---|---|---|
| `ercot:system` | `wind_generation_mw` | 26,304 | 12,722 | 37.93 (6 June 2023, 14:00 UTC) | 28,264.50 (4 March 2025, 02:00 UTC) |
| `ercot:system` | `solar_generation_mw` | 26,304 | 5,594 | 0.00001 (3 hours, 26 December 2023, 07:00 to 09:00 UTC) | 29,503.09 (9 September 2025, 17:00 UTC) |

Means by Central year: wind 12,327 MW (2023), 12,718 (2024), 13,121 (2025); solar 3,638, 5,436 and 7,707. Solar is below 1 MW in 10,883 hours (the nights); no value is zero or negative.

## Reading ERCOT's reports site

- Before any request the pull asks `ip.paused("ercot")` (ERCOT is not paused); a paused publisher is a log line and no request.
- The list is asked afresh each pull. A document is fetched only if its Extension is xlsx and it is not already saved and on disk (a manifest line of kind workbook, HTTP 200).
- Each request: a timeout of 180 seconds, up to three tries, 10, 20 and 30 seconds after each failure; HTTP 401 or 403, or a body that is not a zip or workbook where a file should be, stops the pull (an access control, never worked around) and no table is written that run. Two seconds after each request.
- Ceiling: 2,000,000 rows of these series read, over every run and probe, counted in the manifest's `series_rows`; before each workbook the pull checks that 17,600 more rows would not pass it; if they would, the pull stops and no table is written that run. The header of 20 October: 59,088 rows, 24 requests, 10,177,213 bytes.
- A workbook must have both sheets, Time (Hour-Ending) and an output column in each header, every time a date and hour on the hour; a blank output gives no row, an output that is not a number stops the run, an hour listed twice (beyond the autumn repeat) stops it, and an hour the spring clock change skips stops it.
- `--write` checks each saved workbook against its manifest sha256, and each year must step hour by hour in UTC from 1 January 00:00 Central to the next 1 January, or the table is not written. Each of the three tables is its own stage: a failure of one does not stop the others.
- `--out-dir` and `--raw-dir` write a trial elsewhere.

## License

The header: "License: public. ERCOT's terms: "raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices." (https://www.ercot.com/help/terms, read 6 October 2026). Cite "ERCOT"." `coverage.csv`: public. `license_tables.csv` names ERCOT as the table's one publisher (from the source registry); `license_verdicts.csv` gives ERCOT "may be public" (read 2 of `license_reads.csv`, 12 October 2026). `docs/licenses.md`: flag and verdict agree; ERW verdict public.

## Cross-checks (session 2152)

- The counts above were computed from the rows, read past the 15 header lines; no hour is given twice.
- Hours complete: each variable holds every hour from 1 January 2023 06:00 UTC to 1 January 2026 05:00 UTC (26,304), as the header says.
- No hour is shared with `ercot_wind_solar_hsl_hourly` or `ercot_wind_solar_forecast`, which begin in September 2026, so the workbooks cannot be set against the hourly reports from the rows held.
- The connector has no cross-check of its own beyond its reading rules.

## Found while writing this note

- The docstring says a file "is saved once ... and never asked for again", and counts the ceiling "over every run". The scheduled run is on GitHub's runner, which keeps no `warehouse/raw/` between runs: each daily run starts with an empty manifest, asks for the three workbooks (about 10 MB) again, and counts only its own rows against the ceiling. The headers of 20 and 23 October both count 24 requests "every run and probe", and the data machine's manifest holds 35 entries, all of 7 October.
- When the 2023 workbook leaves ERCOT's list, a run on the runner (no saved workbook, the table not restored) will write the table without 2023; whether the archive's rebuild then keeps those rows was not tested here.
- The connector asks `/misapp/` and `/misdownload/` on `www.ercot.com`, paths ERCOT's robots file disallows (read 23 October 2026, session 2002). Neither its docstring nor its header says so.

## What it does not hold

- The High Sustained Limit and output by region: the workbooks hold neither; for September 2026 on they are in `ercot_wind_solar_hsl_hourly`.
- Years before 2023 (not on ERCOT's list) and 2026 (not yet posted).
- ERCOT.LOAD, installed capacity and the ratios the workbooks also hold.
