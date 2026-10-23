# California ISO's grid emergencies by notice type and day, 1998 to 2026 (CAISO's Grid Emergencies History Report)

Energy Research Warehouse (ERW), method note written in session 2088 (chain 068) for a table first written on 1 October 2026 (session 58).

Tables: `caiso_grid_emergencies`

## Publisher and address

California Independent System Operator (CAISO), "Grid Emergencies History Report (1998 to present)", one PDF revised by CAISO operations: `https://www.caiso.com/documents/grid-emergencies-history-report-1998-to-present.pdf`. One request a run. Source id `caiso:grid_emergencies_history`. Connector: `warehouse/connectors/caiso_emergencies.py` (session 58), which reads the PDF's tables with pdfplumber.

## Vintage and revision

30 May 1998 to 8 October 2026 in the file on the data machine, written by run `20261023T173350Z` (23 October 2026). The report read was revised 10/09/2026; its log: "1,048,832 bytes, 196 pages", "1909 rows read from the report's tables, 1906 after removing repeated pages". The docstring's "191 pages on 2026-10-01" was an earlier revision.

Each run deletes the file and writes the whole table again from the report's current revision, so CAISO's changes to past years are taken. The table has no `retrieved_at` column; the header names the run and the report's revision date.

## Shape and variables

Events, 1,906 rows on 815 distinct days. `event_id` is `caiso_awe:<day>:<type>:<key>`, the key the first 10 hex characters of a SHA-1 of the day, type, region (lower case) and time frame; every `event_id` is distinct. `event_date` is the local (Pacific) day the notice covered: a notice of several days is one row a day, because CAISO's own yearly counts are days (Decision 35). `parties` is "California ISO" and `status` "declared" on every row; `entity_ids`, `mw`, `price` and `currency` are empty.

| `event_type` | Rows | Days | First | Last |
|---|---|---|---|---|
| rmo (Restricted Maintenance Operations; also No Touch, RMO*, Generation RMO) | 766 | 689 | 1998-07-27 | 2026-10-08 |
| warning | 320 | 320 | 1998-07-27 | 2021-07-29 |
| alert | 245 | 245 | 1998-05-30 | 2020-10-15 |
| flex_alert (also Power Watch) | 155 | 137 | 2000-05-22 | 2022-09-09 |
| stage1 | 146 | 146 | 1998-07-27 | 2017-05-03 |
| stage2 | 118 | 118 | 1998-07-27 | 2021-07-09 |
| transmission_emergency | 82 | 77 | 2004-01-12 | 2025-04-30 |
| stage3 | 41 | 41 | 2000-12-07 | 2020-08-15 |
| eea_watch | 12 | 12 | 2022-08-31 | 2024-07-24 |
| vlrp (Voluntary Load Reduction Program) | 8 | 8 | 2004-02-03 | 2006-07-25 |
| eea1 | 7 | 7 | 2022-08-31 | 2023-07-20 |
| eea2 | 4 | 4 | 2022-09-05 | 2022-09-08 |
| eea3 | 1 | 1 | 2022-09-06 | 2022-09-06 |
| load_interruption (1-Hour Probable Load Interruptions) | 1 | 1 | 2020-08-18 | 2020-08-18 |

The extra columns: `x_label` the name as printed (Power Watch on 79 flex_alert rows, No Touch on 265 rmo rows); `x_region` (ISO on 1,616 rows, Southern CA 214, Northern CA 42, CAISO Grid 26, and three other spellings on 8); `x_time_frame`, `x_start`, `x_end`; `x_notice` (151 rows) and `x_issued_at` (138 rows); `x_reason` (576 rows, cut to 300 characters); `x_layout`, the code path the row was read by; `x_page`, the PDF's page (6 to 196).

| `x_layout` | Rows | Days from | to | Pages |
|---|---|---|---|---|
| records | 576 | 2011-02-03 | 2026-10-08 | 6 to 171 |
| stages | 452 | 1998-07-27 | 2010-09-28 | 172 to 193 |
| day_lists | 878 | 1998-05-30 | 2004-09-14 | 179 to 196 |

No row has `x_layout` matrix.

## Reading the source

- The request: one GET with a browser-like agent, timeout 180 seconds, no retry. An answer that is not HTTP 200 or does not begin "%PDF" stops the run.
- Each page's tables are read in four code paths (`records`): a table whose header holds "AWE Event" is read one notice a row; a table headed "Date" with stage columns is read as `stages`; another table headed "Date" as the matrix; a table headed by years or by types as day lists (`day_list`). A table that continues one on an earlier page without its header takes that header.
- A notice type is mapped by `TYPES`: an older name CAISO's summary counts under a newer one is filed under it (Power Watch as flex_alert, No Touch as rmo). A row whose date cannot be read or whose type is not in `TYPES` is skipped and not counted. A cell "none" or "n/a" is not a notice. A day list whose label names no type, or without its year, is left out and logged.
- Days: a time frame "MM/DD/YYYY HH:MM through MM/DD/YYYY HH:MM" gives every day from the first to the last when they are less than 60 days apart (`span`); a row naming a range of days gives those days (`expand`).
- A notice number and issue time are kept only when the table has one row.
- Repeats: rows are sorted by day, type and page, and a second row with the same day, type, region (lower case) and time frame is dropped.
- The check: CAISO's own yearly day counts per type, from the report's summary tables on pages 1 and 3 (`summary_counts`; 2022 is in both and summed), are compared with the table's distinct days per year and type. Every difference is logged and written to the header; nothing is adjusted.
- Ceiling: more than 20,000 rows (`CEILING`) stops the run.
- The connector does not consult `paused_sources.csv`.

## License

Public, with credit. `license_verdicts.csv` records CAISO, read 3 (`https://www.caiso.com/privacy-terms-of-use`, 12 October 2026): "may be public", for public and for commercial use. The sentence: its materials "may be used by you provided that you keep intact all copyright, trademark and other proprietary notices and that you credit the California ISO when using such materials and/or information." The verdict's note adds that the same page's API terms forbid use "for any other benchmarking or competitive purposes". `sources.csv` flags the source public; `license_tables.csv` lists the table under CAISO. Credit: California ISO, Grid Emergencies History Report.

## Cross-checks (session 2088)

- The counts above were computed from the rows, read past the header lines.
- The header: "214 of 232 year-type counts match". The 18 that do not are listed in the header; the largest are 2004 alert (CAISO 1 day, the table 7), 2004 warning (2, 6) and 2007 rmo (18, 13).
- One row per type, region and day does not hold for every row: 43 (day, type, region) combinations hold more than one row, 141 rows in all, because the repeat rule keeps rows whose time frames differ. 129 of them are records rows (87 in 2020); in 2004, 10 rows are a day read both from the stages tables and from the day lists.
- Days with a notice of any type: 32 in 2024, 3 in 2025, 6 in 2026 to 8 October.

## What it does not hold

- The notices' text beyond the cells read: the reason is cut to 300 characters.
- Megawatts, prices or affected entities: those columns are empty.
- Grid notices of other operators: ERCOT's are `ercot_grid_notices`.
- Any notice CAISO's report does not list.
