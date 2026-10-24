# ERCOT's native load by weather zone and ERCOT's total, an hour (ERCOT's Hourly Load Data Archives)

Energy Research Warehouse (ERW), method note written in session 2088 (chain 068) for a table first written on 6 October 2026 (session 138).

Tables: `ercot_zone_load_hourly`

## Publisher and address

Electric Reliability Council of Texas (ERCOT), "Hourly Load Data Archives", native load by weather zone. The connector reads the page that lists the yearly files (`https://www.ercot.com/gridinfo/load/load_hist`), takes each year's address from it with the pattern `LINK` (`https://www.ercot.com/files/docs/<date>/Native_Load_<YYYY>...zip`, `.xlsx` or `.xls`; since session 202 anything may stand between the year and the extension, as in `Native_Load_2026-1-.zip`), then asks for one file a year, newest first. Each file is one workbook, one line an hour: Hour Ending, COAST, EAST, FWEST, NORTH, NCENT, SOUTH, SCENT, WEST, ERCOT. Source id `ercot:load_hist`. Connector: `warehouse/connectors/ercot_zone_load.py` (session 138), with the frame it shares with the other load connectors in `warehouse/connectors/zone_load.py` (`zone_load.run` writes the table, `zone_load.rows` makes its rows). Requests carry the agent `zone_load.UA` (session 136's, from `dam_cleared.py`).

## Vintage and revision

1 January 2015 to 30 September 2026 (Central) in the file on the data machine: `ts_utc` from 2015-01-01T06:00:00Z to 2026-10-01T04:00:00Z. The header is run `20261019T113456Z` (19 October 2026), which reused the 2026 file kept by run `20261013T030138Z`: "Rows read from the operator in this run: 0 ... Rows written by this run: 58,959, 2026-01-01T06:00:00Z to 2026-10-01T04:00:00Z." The table is merged into the one held (`iso_prices.write_csv`): a row with the same (entity, variable, ts_utc) is replaced, every other row is kept.

Twelve files stand behind the rows, 2015 to 2026. `vintage` is each file's Last-Modified (`iso_prices.vintage_of`): 13 November 2021 for the files of 2015 to 2020, then 7 January 2022 (2021), 31 January 2023 (2022), 8 January 2024 (2023), 10 January 2025 (2024), 4 February 2026 (2025) and 8 October 2026 (the 2026 file). `retrieved_at` is 7 October 2026 (01:43:07Z to 01:43:59Z) for the eleven past years and 2026-10-13T03:01:41Z for 2026.

A past year's file is asked for once and its raw file kept (`iso_prices.raw_cached`), so a later revision of a past year by ERCOT is not taken. The current year's file, which ERCOT extends month by month, is asked for again when the kept copy is `KEEP_DAYS` (13) days old or more. A table whose newest hour is more than 75 days old (`stale_days`) is not written.

## Shape and variables

Series, 926,838 rows: 9 series of 102,982 hours each. `variable` `load`; `unit` MW, ERCOT's native load over the hour; `freq` PT1H; `ts_utc` the hour's start; `geo` US-TX; `market` ercot_load; `node` the column's name in ERCOT's file.

| Entity | ERCOT's column | `node` |
|---|---|---|
| ercot:COAST, ercot:EAST, ercot:NORTH, ercot:WEST | the same names | the same names |
| ercot:FWEST | FWEST (FAR_WEST in the files of 2015 and 2016) | FWEST, FAR_WEST |
| ercot:NCENT | NCENT (NORTH_C) | NCENT, NORTH_C |
| ercot:SOUTH | SOUTH (SOUTHERN) | SOUTH, SOUTHERN |
| ercot:SCENT | SCENT (SOUTH_C) | SCENT, SOUTH_C |
| ercot:system | ERCOT, ERCOT's own total | ERCOT |

The four older names stand on 17,543 hours each, 2015 and 2016 (`OLD_NAMES`). ercot:system is ERCOT's column, never a sum made here, and is the entity of `ercot_dam_cleared_energy`. The eight are weather zones, the regions of ERCOT's load forecast, not its load zones or hubs: ercot:NORTH does not join ercot:LZ_NORTH or ercot:HB_NORTH, and no map between them is applied (Decision 42).

ercot:system runs from 24,337.5 MW (2015-03-29T09:00:00Z) to 91,133.7 MW (2026-07-22T22:00:00Z).

## Reading the source

- The hour. ERCOT gives the hour's end in Central time; `ts_utc` is the hour's start (`zone_load.to_utc`). "24:00" is the hour that ends at midnight. The autumn hour that is in a file twice is placed first in daylight time, then in standard time; the files from 2017 mark the second "DST", and a "DST" mark on a line that is not the second of a repeated hour stops the table. The spring hour that the files of 2015 and 2016 label by its end (hour ending 03:00 after 01:00) is placed by its end. A repeated hour held once only is not placed, not written, and counted in the log and the header.
- The columns must be one hour-ending column (`HOUR_COLS`), the eight zones and ERCOT, after the older names are mapped; any other set stops the table. A zip must hold one workbook. An hour ending not on the hour stops the table.
- A cell that is not a number is read as blank and its row is not written; that is not counted. A zone and hour given twice in a file stops the table (`zone_load.rows`).
- A year the page does not list is not written and is named in the header.
- Ceiling: 80,000 rows read a run (`SPEC["ceiling"]`), counted as nine rows an hour; a year's file is taken to hold `ROWS_A_YEAR` (79,056). A run stops before a file that would pass the ceiling and needs a request; a reused raw file is not counted. Past the ceiling the run stops and writes nothing (`dam_cleared.Counter`).
- Each request is tried up to four times (`iso_prices.with_retries`, the waits growing by 5 seconds); HTTP 404 is not retried. A pause of `PAUSE` (3) seconds follows each request. The run asks nothing while ERCOT is in `paused_sources.csv` (`iso_prices.paused`).
- A run asks for the years from the year of `--from` (or of `--days`, 10 by default) to the current year, and writes every hour of each file it reads, not only the days asked.

## License

Public. `license_verdicts.csv` records ERCOT, read 2 (`https://www.ercot.com/help/terms`, 12 October 2026): "may be public", for public and for commercial use. The sentence: "raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices." The verdict's note: item 6 forbids use that harms the site's performance. `sources.csv` flags `ercot:load_hist` public; `license_tables.csv` lists the table under ERCOT.

## Cross-checks (session 2088)

- The counts above were computed from the rows, read past the header lines. No (entity, variable, ts_utc) is given twice. Each of the nine series holds the same 102,982 hours.
- The range holds 102,983 hours; one is missing in every series: the hour that starts 2016-11-07T05:00:00Z, the line of ERCOT's 2016 workbook stamped "2016-11-07 00:00" (hour ending midnight on 6 November 2016, the day the clocks went back), whose nine cells are blank in the raw file kept on the data machine. So the 2016 file gives 8,783 hours; every other year's file gives 8,760 (8,784 for 2020 and 2024), and the 2026 file 6,551 (to 30 September).
- The eight zones sum to ERCOT's total within 1 MW in every hour but 48: the hours of 17 and 18 May 2021 (Central), where ERCOT's total exceeds the zones' sum by 681.8 to 2,359.8 MW.
- Against EIA-930's ERCO demand (`eia930_all_demand`, `demand_mw`) in the 797 hours both hold (2026-08-27T00:00:00Z to 2026-10-01T04:00:00Z), EIA's figure is within -0.67 to +0.90 percent of ercot:system, median -0.01 percent. Moved by an hour either way, the median difference is 3.26 or 3.40 percent, so the two tables place the hours alike.

## What it does not hold

- ERCOT's load zones and hubs: their prices are in the price tables, and no weather zone joins them.
- Years before 2015, and the hours of 2026 ERCOT has not yet added to its file (October on, as read).
- The 2016 hour named above, and any hour ERCOT left blank.
- A forecast: these are ERCOT's figures after the hour.
