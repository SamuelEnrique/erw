# Day-ahead reserve clearing prices, New England as a whole, an hour (ISO-NE ISO Express, daasreservedata)

Energy Research Warehouse (ERW), method note written in session 2110 (chain 069) for a table first written on 4 October 2026 (session 85).

Tables: `isone_as_prices`

## Publisher and address

ISO New England (ISO-NE), ISO Express report "Day-Ahead Hourly Reserve Requirements Prices Designations and Forecast", one request a calendar month (cut at the window's first and last day):

`https://www.iso-ne.com/transform/csv/daasreservedata?start=<YYYYMMDD>&end=<YYYYMMDD>`

Report page `https://www.iso-ne.com/isoexpress/web/reports/pricing/-/tree/ancillary-daas-hourly-rr`. ISO-NE answers the CSV only to a session that has first opened one of its report pages, so the connector opens `https://www.iso-ne.com/isoexpress/web/reports/operations/-/tree/gen-fuel-mix` once (the page gridstatus uses for the same cookie), with the User-Agent "Mozilla/5.0 (Energy Research Warehouse)", and asks in that session. The file's lines are "H" (the column row), "D" (data) and "T" (a total line). Source id `isone:daasreservedata`. Connector: `warehouse/connectors/isone_as_prices.py` (session 85), its only table, with the loop it shares with the NYISO, MISO and SPP reserve price connectors in `warehouse/connectors/iso_as_common.py`; method `docs/methods/capacity_and_ancillary.md` (the section on the four grids' day-ahead reserve prices).

It is on no schedule: no line of `warehouse/run_daily.sh`, `warehouse/refresh_*.sh`, `warehouse/run_data_machine.sh` or `.github/workflows/` runs it. Session 85's report: "The four connectors are not in the daily run. You asked for the tables from 2024-09-01, not for a schedule." The first date is from the rows and the report together: every row's `retrieved_at` is 4 October 2026, 03:36:46 to 04:09:43 UTC, and session 85's report says it ran on 2026-10-04 from about 03:25 to 04:45 UTC.

## Vintage and revision

Eastern operating days 1 March 2025 to 4 October 2026 (1 March 2025 05:00 UTC to 5 October 2026 03:00 UTC) in the file on the data machine, from one run, `20261004T040940Z`, restored from the Redivis draft (energy_research_warehouse_internal) by `scripts/sync.py`, as its last header line says. Its header: "Window: operating days 2025-03-01 to 2026-10-04 (America/New_York). Never filled: ... 0 are left out of this run." All 55,964 rows were retrieved on 4 October 2026, from 20 addresses: one for each month from March 2025 to September 2026, and one for 1 to 4 October 2026. `coverage.csv` gives the same 55,964 rows and dates (last run 2026-10-04T04:09:40Z).

A month is asked of ISO-NE again on every run until two days after its last day; after that it is "settled" and read from the raw file a run kept (`warehouse/raw/isone_as_prices/`, by `iso_prices.raw_cached`), never asked again, so a later revision by ISO-NE of a settled month is not taken. `iso_prices.write_csv` merges the rows into the file on (entity, variable, ts_utc): an hour read again replaces the held one. As the connector has not run since 4 October 2026, the table ends there.

## Shape and variables

Series, 55,964 rows: one entity, four variables of 13,991 hours each (583 Eastern days: 580 of 24 hours, 9 March 2025 and 8 March 2026 of 23, 2 November 2025 of 25). `entity` `isone:7000`, the report's one Location ID, New England as a whole; `unit` USD/MW-hour (the file's unit row reads "$": US dollars per MW held for the hour); `freq` PT1H; `ts_utc` the hour's start in UTC, from the file's Local Date and Hour Ending (Eastern); `market` `isone_dam`; `geo` US-CT,US-MA,US-ME,US-NH,US-RI,US-VT; `node` 7000; `vintage` empty.

| Variable | ISO-NE column | Mean | Median | Lowest | Highest |
|---|---|---|---|---|---|
| `as_price_dam_tmsr` | Ten Minute Spinning Reserve Clearing Price | 19.011 | 8.56 | 0.06 (first on 1 May 2025, 13:00 UTC) | 851.09 (2 July 2026, 20:00 UTC) |
| `as_price_dam_tmr10` | Ten Minute Reserve Clearing Price | 17.571 | 7.58 | 0.06 (first on 1 May 2025, 13:00 UTC) | 851.09 (2 July 2026, 20:00 UTC) |
| `as_price_dam_tmr30` | Total Thirty Reserve Clearing Price | 16.101 | 7.36 | 0.04 (first on 11 May 2025, 13:00 UTC) | 851.09 (2 July 2026, 20:00 UTC) |
| `as_price_dam_fer` | FER Price (the forecast energy requirement) | 5.062 | 0 | 0 (8,189 hours) | 578.51 (27 January 2026, 14:00 UTC) |

The FER price is above 0 in 5,802 hours; the three reserve prices are never 0. By Eastern year the means are: 2025 (from 1 March) TMSR 15.253, TMR10 14.485, TMR30 13.650, FER 4.716; 2026 (to 4 October) TMSR 23.163, TMR10 20.981, TMR30 18.808, FER 5.444.

## Reading ISO Express

- The "H" line must be exactly the sixteen columns session 85 read (H, Local Date, Hour Ending, Location ID, the four requirements, the four prices, the four designated MW), or the run stops ("layout changed"). The "T" line must say "<n> lines" for the number of "D" lines read, or the run stops. A Location ID other than 7000 stops the run.
- An answer that is not HTTP 200 with a CSV content type is tried up to four times, 5, 10 and 15 seconds apart (`iso_prices.with_retries`; no retry once a pull budget has passed), and then the run stops and nothing is written. An HTTP 404 is treated the same: the connector's own fetch never raises the shared loop's `SourceGap`. The cookie page is asked once; its answer is not checked or retried.
- The hour. A day is read as given only when its hour-ending labels are exactly the day's, in order (01 to 24; the autumn day repeats 02; the spring day has no 03). Otherwise only the labels the day has once and the file gives once are kept, the day is logged, and the complete-day rule below leaves it out.
- An empty cell gives no row. A cell that is not a number stops the run.
- Never filled: a (region, variable, Eastern day) is written only with every hour of the day exactly once (24, or 23 and 25 at the clock changes); a day short of it is left out, logged, counted in the header and written as a gap row of the run's status. A (region, variable, hour) given twice stops the run.
- Ceiling: 500,000 rows a run (`iso_as_common.CEILING`, session 85). ISO-NE has no narrowing step: past the ceiling nothing is written. The run of 4 October wrote 55,964.
- Two seconds after each request ISO-NE answered (none after a raw file reused). No test of the newest day's age. ISO-NE is checked against `warehouse/metadata/paused_sources.csv` before any request (`iso_as_common.run`; it is not paused). `--start` may not be before 2024-09-01 and is raised to 2025-03-01; `--until` defaults to tomorrow (Eastern); `--offline` reads the raw files only.

## License

The header: "License: internal. ISO-NE's terms (https://www.iso-ne.com/legal-privacy): "Any duplication of the Content or non-personal use may violate copyright, trademark, and other laws."" `coverage.csv`: internal. `license_tables.csv` names ISO-NE as the table's one publisher (from the source registry); `license_verdicts.csv` gives ISO-NE "needs written permission" (read 4 of `license_reads.csv`, 12 October 2026), the same if the ERW sells anything. `docs/licenses.md`: flag and verdict agree; ERW verdict internal.

## Cross-checks (session 2110)

- The counts above were computed from the rows, read past the 13 header lines; no (entity, variable, ts_utc) is given twice.
- Hours complete: every one of the 2,332 (variable, Eastern day) groups holds exactly the day's hours, and no day from 1 March 2025 to 4 October 2026 is missing.
- The reserve cascade holds in every one of the 13,991 hours: TMSR is at least TMR10, TMR10 at least TMR30, and TMR30 at least the FER price. In 6,905 hours the three reserve prices are equal, the highest hour among them (2 July 2026, 20:00 UTC: 851.09 each).
- The connector has no cross-check of its own beyond its reading rules.

## What it does not hold

- The requirements, the forecast MW and the designated MW in the same file (quantities, not prices), and the strike prices (another report).
- Real-time reserve prices: day-ahead only.
- Days before 1 March 2025: ISO-NE's day-ahead ancillary services market began that day, and session 85 found the report answers no row for 1 February 2025.
- Days after 4 October 2026: the table has not been refreshed.

## Found while writing this note

- `iso_as_common.py`'s docstring says "A document the source does not hold (HTTP 404) is a gap." `isone_as_prices.py` passes its own `fetch`, which raises a plain error for any answer other than HTTP 200 with a CSV, so for ISO-NE a 404 is retried four times and stops the run; it is never a gap.
- `iso_as_common.py`'s docstring describes the spec with keys `regions, variables` (what a complete day must hold) and documents that carry "days"; the code reads `spec["wanted"]`, and ISO-NE's documents carry no "days" key.
