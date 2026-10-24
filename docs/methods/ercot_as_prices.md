# Prices of ERCOT's ancillary services in the day-ahead market, an hour, from 2018 (ERCOT NP4-181-ER and NP4-188-CD, MCPC)

Energy Research Warehouse (ERW), method note written in session 2152 (chain 092) for a table first written on 2 October 2026 (session 65).

Tables: `ercot_as_prices`

## Publisher and address

Electric Reliability Council of Texas (ERCOT), the Market Clearing Price for Capacity (MCPC) of each ancillary service in the day-ahead market, from two reports on ERCOT's public reports site:

- NP4-181-ER, "Historical DAM Clearing Prices for Capacity" (report type 13091): one zip a year (ERCOT's name `DAMASMCPC_<year>`), a row per delivery hour and a column per service. The current year's file is republished; since 4 October 2026 its zip holds one Excel workbook in place of a CSV (the connector's docstring; the raw file kept on the data machine from 5 October 2026 holds `rpt.00013091.0000000000000000.20261004.080005.DAMASMCPC_2026.xlsx`, and the 2025 file a CSV).
- NP4-188-CD, "DAM Clearing Prices for Capacity" (report type 12329): one zip a day-ahead run, read only for the days after the newest yearly file ends.

`https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=<13091 or 12329>` (the document list, JSON)

`https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=<DocID>` (each zip)

The product pages `https://www.ercot.com/mp/data-products/data-product-details?id=NP4-181-ER` and `?id=NP4-188-CD` are named in the header and are not asked. Every request goes to the host `www.ercot.com`, under the paths `/misapp/` and `/misdownload/`, which ERCOT's robots file disallows (read by session 850, and again by session 2002 at 15:11:50 UTC on 23 October 2026, read 170 of `warehouse/metadata/license_reads.csv`). The connector does not read the robots file and sends no User-Agent of its own (the requests library's default). Source ids `ercot:NP4-181-ER` and `ercot:NP4-188-CD`. Connector: `warehouse/connectors/ercot_as_prices.py` (session 65), its only table; the method of the services is `docs/methods/capacity_and_ancillary.md`, which the header names.

It is run every day by `warehouse/run_daily.sh` (step `ercot_as_prices`, under `warehouse/health.py run --strict` and a pull budget of 15 minutes, `warehouse/pull_budget.py`), which `.github/workflows/daily-prices.yml` runs on GitHub's runner; `warehouse/derived/ercot_as_prices_rollup.py` then rebuilds the daily and monthly tables from it. `run_status.csv` records 17 runs: the first on 4 October 2026 on GitHub (failed), the first good one at 01:00 UTC on 5 October 2026 (local), and the last `20261023T150243Z`: "338492 rows of 500000". The first date is from session 65's report (2 October 2026, about 14:55 to 19:30 UTC, the table written to `runs/session65/ercot_as_prices/`, 335,972 rows, 2018-01-01 to 2026-10-02) and from the rows: the earliest `retrieved_at` is 2 October 2026 15:15:21 UTC, and `sources.csv` first saw both reports on 2026-10-02.

## Vintage and revision

Central days 1 January 2018 to 23 October 2026 (1 January 2018 06:00 UTC to 24 October 2026 04:00 UTC), 3,218 days, in the file on the data machine, rebuilt from the ERW archive by `warehouse/restore_tables.py` as of run `20261023T152740Z-github`, with the header of the connector's run `20261023T150243Z`. `vintage` is the document's PublishDate:

- NP4-181-ER, 337,772 rows from nine yearly files. The files of 2018 to 2025 were each published on 1 January of the next year at about 13:00 UTC (2025's at 13:18:09 UTC on 1 January 2026); 2026's was published at 13:01:06 UTC on 18 October 2026 and holds to 17 October (Central).
- NP4-188-CD, 720 rows from six daily files: delivery days 18 to 23 October 2026, each published the day before at about 17:33 UTC.

The rows' `retrieved_at` are 2 October 2026 (302,977 rows), 19 October (35,155), and 21, 22 and 23 October (120 each). The rebuild from the archive keeps a row's `retrieved_at` from the run that first archived its value. `coverage.csv` gives the same 338,492 rows, 2018-01-01T06:00:00Z to 2026-10-24T04:00:00Z, five nodes: it agrees.

Every run reads the whole series again: every yearly file from 2018 to the current year, then the daily files for the days after the last yearly hour. `ip.write_csv` merges the rows into the file on (entity, variable, ts_utc), so an hour read again replaces the one held. A day first held from NP4-188-CD is replaced by the yearly file's row once the republished yearly file reaches it. A document saved by an earlier run of this connector is read from `warehouse/raw/ercot_as_prices/` and not asked again (the lists are always asked again); the GitHub runner keeps no raw file between runs, so each scheduled run asks for every file.

## Shape and variables

Series, 338,492 rows, five entities. `entity` `ercot:<service>`; `variable` `mcpc_dam`; `value` ERCOT's MCPC for the service and hour, as printed; `unit` USD/MW-hour (US dollars per MW of capacity held for one hour); `freq` PT1H; `ts_utc` the hour's start, from the delivery date and hour ending (Central) less one hour, the repeated-hour flag Y marking the second 01:00 to 02:00 hour of the autumn clock change; `market` `ercot_dam`; `geo` US-TX; `node` the service; `source_url` the zip's address.

| Entity | Variable | Hours | Mean USD/MW-hour | Lowest | Highest |
|---|---|---|---|---|---|
| `ercot:REGUP` (Regulation Up) | `mcpc_dam` | 77,231 | 39.80 | 0.00 (66 hours, first 8 February 2019, 02:00 UTC) | 24,992.90 (17 February 2021, 11:00 UTC) |
| `ercot:REGDN` (Regulation Down) | `mcpc_dam` | 77,231 | 16.27 | 0.00 (102 hours, first 3 April 2025, 04:00 UTC) | 17,925.10 (17 February 2021, 14:00 UTC) |
| `ercot:RRS` (Responsive Reserve) | `mcpc_dam` | 77,231 | 47.92 | 0.05 (3 hours, 19 August 2026, 17:00 to 19:00 UTC) | 25,674.30 (17 February 2021, 13:00 UTC) |
| `ercot:NSPIN` (Non-Spin) | `mcpc_dam` | 77,231 | 24.49 | 0.04 (4 hours, 7 to 14 September 2025) | 12,866.70 (20 February 2021, 01:00 UTC) |
| `ercot:ECRS` (ERCOT Contingency Reserve Service) | `mcpc_dam` | 29,568 | 13.33 | 0.01 (9 hours, 4 March to 9 April 2026) | 4,085.33 (26 August 2023, 00:00 UTC) |

ECRS begins on 10 June 2023 (00:00 Central, 05:00 UTC); its column is empty before and an empty cell is no row. The five highest prices are all RRS, on 17 and 18 February 2021. Means by Central year:

| Year | REGUP | REGDN | RRS | NSPIN | ECRS |
|---|---|---|---|---|---|
| 2018 | 13.71 | 4.39 | 18.46 | 8.09 | |
| 2019 | 23.33 | 8.00 | 28.81 | 15.21 | |
| 2020 | 10.32 | 7.20 | 11.61 | 4.37 | |
| 2021 | 244.37 | 95.57 | 312.24 | 134.00 | |
| 2022 | 21.67 | 8.46 | 20.31 | 22.49 | |
| 2023 | 26.79 | 13.63 | 21.26 | 19.05 | 58.15 |
| 2024 | 6.01 | 3.44 | 5.67 | 6.22 | 8.23 |
| 2025 | 2.98 | 1.62 | 2.76 | 3.05 | 2.46 |
| 2026 (to 23 October) | 2.08 | 1.32 | 1.60 | 4.19 | 1.97 |

## Reading ERCOT's reports site

- Both lists are asked afresh each run. NP4-181-ER must list a `DAMASMCPC_<year>` file for every year from 2018 to the current Central year, or the run stops and nothing is written.
- A yearly zip must hold exactly one CSV or exactly one Excel workbook; anything else stops the run. A workbook must have one sheet and one header row (Delivery Date, Hour Ending, Repeated Hour Flag), every header cell named, and each price a number.
- The yearly columns must be Delivery Date, Hour Ending, Repeated Hour Flag and then services among REGUP, REGDN, RRS, NSPIN and ECRS, REGUP among them, none twice; a daily file's columns must be exactly DeliveryDate, HourEnding, AncillaryType, MCPC, DSTFlag, and an unknown service stops the run.
- Only daily documents whose name ends `_csv.zip` are read, and of them only those published less than two days before the last yearly hour; of each, only the hours after the last yearly hour are kept.
- The hour ending must read HH:00, from 1 to 24, and the flag Y or N; an hour the spring clock change skips stops the run. An empty cell gives no row; a value that is not a number stops the run. A (service, hour) given twice stops the run.
- Never filled: a (service, Central day) is written only when it holds every hour of the day (24, or 23 and 25 at the clock changes). A shorter day is left out, logged and recorded as a gap in the run's status; the run of 23 October left out none.
- Ceiling: 500,000 rows kept after the complete-day rule (not rows read). Past it the run stops and writes nothing. This run: 338,492.
- A request is tried up to four times, 5, 10 and 15 seconds apart (`iso_prices.with_retries`; no retry once the pull budget has passed). HTTP 404 is not retried and stops the run. Three seconds after each request asked of ERCOT.
- `--offline` reads the raw files only; `--out-dir` writes a trial elsewhere.
- No pause check: the connector does not ask `iso_prices.paused()` before its requests (ERCOT is not in `warehouse/metadata/paused_sources.csv`).

## License

The header: "License: public. ERCOT terms of use, item 5: raw data in public portions of the website may be used, reproduced, and redistributed in compilations, charts, and analyses." `coverage.csv`: public. `license_tables.csv` names ERCOT as the table's one publisher (from the source registry); `license_verdicts.csv` gives ERCOT "may be public" (read 2 of `license_reads.csv`, 12 October 2026), noting that item 6 forbids use that harms the site's performance. `docs/licenses.md`: flag and verdict agree; ERW verdict public.

## Cross-checks (session 2152)

- The counts above were computed from the rows, read past the 13 header lines; no hour is given twice and no value is blank.
- Hours complete: each service holds every hour from its first to its last, autumn repeated hours included (77,231 hours from 1 January 2018 06:00 UTC to 24 October 2026 04:00 UTC; ECRS 29,568 from 10 June 2023 05:00 UTC).
- The connector has no cross-check of its own beyond its reading rules.

## Found while writing this note

- The connector asks `/misapp/` and `/misdownload/` on `www.ercot.com`, paths ERCOT's robots file disallows (read 23 October 2026, session 2002). Neither its docstring nor its header says so.
- `CLAUDE.md` says every connector that reaches a publisher's servers asks `iso_prices.paused()` first. This one does not.
- The docstring says "a file already there is not requested again". That holds on a machine that keeps `warehouse/raw/`; the scheduled run is on GitHub's runner, which keeps none, so every daily run downloads all nine yearly files again.

## What it does not hold

- The quantities ERCOT plans to buy (`ercot_as_quantities`), awards to resources, and real-time prices of the services.
- Days before 1 January 2018: the connector starts there (`FIRST_YEAR`).
