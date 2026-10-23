# Each US power reactor's power level, a day (the NRC's Power Reactor Status Reports)

Energy Research Warehouse (ERW), method note written in session 2046 (chain 059) for a table first written on 6 October 2026 (session 133).

Tables: `nrc_reactor_status`

## Publisher and address

U.S. Nuclear Regulatory Commission (NRC), Power Reactor Status Reports (`https://www.nrc.gov/reading-rm/doc-collections/event-status/reactor-status/index`), read from the pipe-delimited text files the NRC publishes (`ReportDt|Unit|Power`): the last 365 days, `https://www.nrc.gov/reading-rm/doc-collections/event-status/reactor-status/powerreactorstatusforlast365days.txt`, and each whole year, `https://www.nrc.gov/reading-rm/doc-collections/event-status/reactor-status/<YYYY>/<YYYY>powerstatus.txt`. Source id `nrc:power_reactor_status`. Connector: `warehouse/connectors/nrc_reactor_status.py` (session 133).

A full run asks for the 365-day file, then each year from the last one back to 2019; the current year's own file is never asked, its days come from the 365-day file. The scheduled runs (`warehouse/refresh_mix.sh`, `warehouse/run_data_machine_tables.sh`) pass `--recent`: the 365-day file only.

## Vintage and revision

1 January 2020 to 23 October 2026 in the file on the data machine, last written by run `20261023T173306Z` (23 October 2026), a `--recent` run. Header: "Files read this run: 1 of 1. None was refused."; "Rows read: 34,770 of the 300,000 ceiling"; "This run wrote 34770 rows: 95 new, 34675 replacing earlier rows ...; 200235 rows are kept from earlier runs."

The file is not deleted: each run merges its rows on (entity, variable, ts_utc), so a day the NRC restates replaces the old row and the years read by earlier full runs stay. Within one run the 365-day file is read first and wins over a yearly file for the same day. The 365-day file is downloaded at every run; a yearly file is taken from the saved raw files when an earlier run saved it. No 2019 row is in the table: session 133's report records that the NRC refused its 2019 file, and the header, which describes only the latest run, no longer says so.

By source file: the 365-day file 36,385 rows (6 October 2025 to 23 October 2026), 2020 35,502, 2021 34,649, 2022 33,828, 2023 34,078, 2024 34,404, 2025 26,159.

## Shape and variables

Series, 235,005 rows: 99 reactors over 2,488 days. `entity` `nrc:<unit>`, the NRC's unit name lower-cased with each run of other characters as one underscore (`D.C. Cook 1` is `nrc:d_c_cook_1`); `variable` `power_pct`, the reactor's power as a percent of its licensed power on the report's morning; `unit` pct, whole numbers from 0 to 100; `ts_utc` the report date at 00:00:00Z; `freq` P1D; `geo` US; `node` the NRC's unit name as written; `market` and `vintage` empty.

From 92 to 97 reactors a day. Duane Arnold and Three Mile Island 1 end on 22 March 2021, Indian Point 2 and 3 on 28 September 2021; Vogtle 3 begins on 13 October 2022 and Vogtle 4 on 21 August 2023. Palisades is absent from 18 June 2022 to 8 September 2025 and listed again from 9 September 2025, at 0 every day since. On 23 October 2026: 95 reactors, 71 at 100, 17 at 0, a mean of 80.26.

## Reading the source

- A file whose first three columns are not `ReportDt`, `Unit`, `Power`, or a power that is not a number from 0 to 100, stops the run. A line with an empty unit is dropped.
- A file the NRC's server refuses is logged, skipped and named in the header; a run in which no file answers stops.
- Ceiling: 300,000 rows read in a run. Before each file, a run that has read more than 264,000 (300,000 less a year's allowance of 36,000) does not ask for it, and the header names it. Each download is followed by a 3-second pause, and each request is tried up to four times.

## License

`license_verdicts.csv` records the NRC, read 16: "may be public", for public and for commercial use. The sentence: "NRC's website constitutes a U.S. Government Work under federal copyright law and as such, it is not subject to copyright. It is freely available for non-exclusive rights in publication or reproduction for any purpose, in any form, and there are no restrictions on use." Its note: the NRC "would appreciate the courtesy of credit". `license_tables.csv` lists the table under the NRC. Cite: U.S. Nuclear Regulatory Commission, Power Reactor Status Reports.

## Cross-checks (session 2046)

- The counts above were computed from the rows, read past the header lines. No (entity, variable, ts_utc) is given twice; each entity has one `node`.
- The 2,488 days run without a gap from 1 January 2020 to 23 October 2026 (2,488 calendar days). The seven source files' rows sum to the 235,005.
- 83.5 percent of rows are at 100 and 18,545 at 0; the fleet's daily mean ran from 75.52 (26 October 2021) to 99.84 (5 July 2024).

## What it does not hold

- Megawatts: a percent of licensed power only. Each unit's capacity is in `nrc_power_reactors` (keyed by docket number, not by this table's unit name).
- Any column of the NRC's files after the first three.
- Days before 2020, and reactors not in the NRC's daily report.
