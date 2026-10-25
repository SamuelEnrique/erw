# ERCOT's four coincident peaks, each summer month's interval and ERCOT's load in it (ERCOT's Four Coincident Peak Calculations)

Energy Research Warehouse (ERW), method note written in session 2088 (chain 068) for a table first written on 20 October 2026 (session 359).

Tables: `ercot_4cp_intervals`

The table's purpose and its shape as planned are in `docs/methods/ercot_4cp.md` (session 359); this note describes the code and the rows as they stand.

## Publisher and address

Electric Reliability Council of Texas (ERCOT), "Four Coincident Peak Calculations" (Market Information, Data Aggregation, `https://www.ercot.com/mktinfo/data_agg/4cp`). The current years are data product NP9-83-M (report type 13037): the connector reads its list, `https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=13037`, and asks for each workbook at `https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=<DocID>`. The years before are one zip under the page's Key Documents, `https://www.ercot.com/files/docs/2022/01/13/1996-2020_FourCoincidentPeakCalculations.zip`. Source id `ercot:NP9-83-M`. Connector: `warehouse/connectors/ercot_4cp.py` (session 359), in two steps: `--pull` saves the files under `warehouse/raw/ercot_4cp/files/` with a manifest, and `--write` builds the table from the saved files only, under the data lock.

## Vintage and revision

Summers 2018 to 2025 in the file on the data machine, without 2021, written by run `20261020T102319Z` (20 October 2026). Header: "Years held: 2018, 2019, 2020, 2022, 2023, 2024, 2025. Not held: 2021 (2021 is on neither ERCOT's list, which keeps four years, nor the zip, which ends with 2020)." `ts_utc` runs from 2018-06-27T21:45:00Z to 2025-09-04T22:15:00Z.

| Years | Document | Rows | `x_published`, `vintage` | `retrieved_at` |
|---|---|---|---|---|
| 2018, 2019, 2020 | the 1996-2020 zip | 12 | empty: the zip states no date | 2026-10-20T10:12:47Z |
| 2022 | NP9-83-M, doclookupId 879528147 | 4 | 2022-11-28 | 2026-10-20T10:12:45Z |
| 2023 | doclookupId 961277079 | 4 | 2023-11-27 | 2026-10-20T10:12:43Z |
| 2024 | doclookupId 1055377059 | 4 | 2024-11-25 | 2026-10-20T10:12:41Z |
| 2025 | doclookupId 1164129560 | 4 | 2025-11-24 | 2026-10-20T10:12:39Z |

`x_published` is the date part of the list's PublishDate; `vintage` is that date at 00:00:00Z. Each `--write` deletes the file and builds the table again from every saved file. A file already in the manifest is not asked for again. When two saved workbooks hold one year, the one ERCOT published later is read. An interval is known only after its month: ERCOT names it from settlement data and posts the year's calculation in November, by 1 December (the header). The summer of 2026 is not held.

## Shape and variables

Series, 28 rows: 1 series, 4 rows a year. `entity` ercot:system; `variable` cp4_load_mw; `unit` MW; `freq` PT15M; `geo` US-TX; `market` ercot_4cp; `node` ERCOT. The value is the Total row of ERCOT's Four Coincident Peak Load Calculation: the sum of the load entities' load in the month's coincident-peak interval, with DC tie exports, block load transfer exports and wholesale storage load excluded, as ERCOT's note says (the header). Extra columns: `x_year`, `x_month` (YYYY-MM), `x_interval_local` (the time ERCOT prints), `x_published`, `x_document` (the workbook's file name).

The time ERCOT prints does not say whether it starts or ends the interval. The table reads it as the interval's end in Central prevailing time, as ERCOT's settlement and price reports name a 15-minute interval: `ts_utc` is 15 minutes before the printed time, converted to UTC (`interval`).

| Year | June | July | August | September |
|---|---|---|---|---|
| 2018 | 69,254.6 | 73,538.7 | 69,990.0 | 64,692.5 |
| 2019 | 68,369.8 | 71,254.4 | 75,006.1 | 69,293.2 |
| 2020 | 68,195.6 | 74,392.2 | 74,420.4 | 64,945.1 |
| 2022 | 76,803.5 | 80,233.2 | 78,669.1 | 71,149.6 |
| 2023 | 81,017.6 | 83,032.6 | 85,636.9 | 84,540.3 |
| 2024 | 79,749.8 | 81,184.4 | 85,357.6 | 77,878.8 |
| 2025 | 77,485.8 | 81,908.3 | 83,968.5 | 80,076.5 |

MW. The printed times run from 14:30 (1 September 2020) to 17:45 (8 June 2020 and 30 June 2024); 15 of the 28 are 17:00.

## Reading the source

- `--pull` stops at once while ERCOT is in `paused_sources.csv`. It asks for the list (an HTTP error stops it), then each listed workbook and the zip not yet in the manifest. A file that answers other than HTTP 200 is logged and not saved. At most `MAX_REQUESTS` (20) requests a run, `PAUSE` (1.5) seconds apart; no retry.
- `--write` reads the first sheet of each workbook (`read_book`): the row whose cells match `HEAD` (a month from June to September, then M/D/YYYY HH:MM) gives the intervals, and the one row with "Total" in its first three cells gives the loads. No month header, other than one Total row, a Total cell that is not a number, or months other than June to September stops the table. So does a printed time that does not exist, or exists twice, in Central time, and an interval whose year is not the workbook's.
- From the zip only `<year>/ERCOTFourCoincidentPeakLoadCalculation<year>.xlsx` from `FIRST_YEAR` (2018) on is read; from the list only a file named `4CP<YYYY><MMDD>.xlsx`, whose year is the posting year.
- No workbook read stops the table. The code counts no row ceiling.

## License

Public. `license_verdicts.csv` records ERCOT, read 2 (`https://www.ercot.com/help/terms`, 12 October 2026): "may be public", for public and for commercial use. The sentence: "raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices." `sources.csv` flags `ercot:NP9-83-M` public; `license_tables.csv` lists the table under ERCOT.

## Cross-checks (session 2088)

- The counts above were computed from the rows, read past the header lines, and agree with the manifest of the five saved files.
- Against `ercot_zone_load_hourly` (ercot:system, ERCOT's native load), in the hour that holds each interval as the table places it: the 4CP Total is 0.07 to 0.56 percent above the native load in all 28 months. The two are different measures (a 15-minute settlement figure and an hourly native load), so they need not agree.
- In 19 of the 28 months the interval as placed falls in the month's highest hour of native load; in 7 more, in the hour before it on the same day; in 2 (September 2018 and September 2024) on another day. Read as the interval's start instead, 18 of 28 would fall in that hour. The hourly comparison does not settle which reading is ERCOT's.

## What it does not hold

- 2021, which neither ERCOT's list nor the zip holds; it is not filled.
- Summers before 2018, though the zip holds 1996 on.
- The summer of 2026, until ERCOT posts it.
- Each load entity's load in the intervals: only the Total row is written.
