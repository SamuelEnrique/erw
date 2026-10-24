# NYISO's load by zone, an hour (NYISO's P-58C, Integrated Real-Time Actual Load)

Energy Research Warehouse (ERW), method note written in session 2088 (chain 068) for a table first written on 6 October 2026 (session 138).

Tables: `nyiso_zone_load_hourly`

## Publisher and address

New York Independent System Operator (NYISO), public report P-58C, "Integrated Real-Time Actual Load" (palIntegrated), listed at `http://mis.nyiso.com/public/P-58Clist.htm`. The connector asks for one zip a calendar month, `http://mis.nyiso.com/public/csv/palIntegrated/<YYYYMM>01palIntegrated_csv.zip`, newest first; each zip holds one CSV a day, one line a zone and hour: "Time Stamp", "Time Zone", "Name", "PTID", "Integrated Load". Source id `nyiso:palIntegrated`. Connector: `warehouse/connectors/nyiso_zone_load.py` (session 138), with the frame it shares with the other load connectors in `warehouse/connectors/zone_load.py` (`zone_load.run` writes the table, `zone_load.rows` makes its rows).

## Vintage and revision

1 January 2019 to 10 October 2026 (Eastern) in the file on the data machine: `ts_utc` from 2019-01-01T05:00:00Z to 2026-10-10T13:00:00Z. The file was restored from the Redivis draft by `scripts/sync.py` and carries the header of run `20261010T150225Z` (10 October 2026): "Rows read from the operator in this run: 10,406 ... Rows written by this run: 10,406, 2026-09-01T04:00:00Z to 2026-10-10T13:00:00Z." The table is merged into the one held (`iso_prices.write_csv`): a row with the same (entity, variable, ts_utc) is replaced, every other row is kept.

94 monthly files stand behind the rows, January 2019 to October 2026, one `source_url` each. `vintage` is each file's Last-Modified (`iso_prices.vintage_of`): 2019-02-01T05:04:05Z for January 2019, 2026-10-10T14:22:00Z for October 2026. `retrieved_at` is 7 October 2026 for 92 files and 10 October 2026 for the September and October 2026 files.

This month's file is asked for on every run, last month's too in a month's first seven days; an earlier month is asked for once and its raw file kept (`iso_prices.raw_cached`), so NYISO's later revisions of an older month are not taken. A table whose newest hour is more than 5 days old (`stale_days`) is not written.

## Shape and variables

Series, 749,595 rows: 11 series of 68,145 hours each. `variable` `load`; `unit` MW, NYISO's Integrated Load over the hour; `freq` PT1H; `ts_utc` the hour's start; `geo` US-NY; `market` nyiso_load; `node` NYISO's zone name.

Entities: nyiso:CAPITL, nyiso:CENTRL, nyiso:DUNWOD, nyiso:GENESE, nyiso:HUD VL, nyiso:LONGIL, nyiso:MHK VL, nyiso:MILLWD, nyiso:N.Y.C., nyiso:NORTH, nyiso:WEST (`iso_prices.NYISO_ZONES`). They are the entities of `nyiso_dam_zone_prices` and `nyiso_rtm_zone_prices`, so load and price join on entity (Decision 42). NYISO's file gives no total for the state and none is written.

| Entity | Lowest, MW | Highest, MW |
|---|---|---|
| nyiso:N.Y.C. | 3,604.2 | 10,830.3 |
| nyiso:LONGIL | 1,144.1 | 5,543.3 |
| nyiso:MILLWD | 140.9 | 685.6 |

The eleven zones summed run from 10,731.0 MW (2026-04-26T18:00:00Z) to 31,857.2 MW (2025-06-24T22:00:00Z); that sum is not in the table.

## Reading the source

- The hour. Time Stamp is the hour's start in Eastern time and Time Zone says EDT or EST on every line (`OFFSET`: 4 or 5 hours to UTC), so the 23-hour and 25-hour days need no inference. Any other Time Zone stops the table; so does a Time Stamp not in the form MM/DD/YYYY HH:MM:SS.
- The columns must be exactly `COLS`; any other set stops the table.
- A line not on the hour, a line whose zone is not one of the eleven, and a line with a blank or non-number load are read, not written, and counted in the header ("lines read and not written").
- A zone's hour given twice in a month: one row is kept when the rows agree, none when they differ, and the hours that differ are counted (`zone_load.once`).
- A month NYISO answers with HTTP 404 is not written and is named in the header (`iso_prices.SourceGap`).
- Ceiling: 20,000 rows read a run (`SPEC["ceiling"]`); a month's file is taken to hold `ROWS_A_MONTH` (8,525), and the run stops before a month for which there is no room. A reused raw file is not counted. Past the ceiling the run stops and writes nothing.
- Each request is tried up to four times (`iso_prices.with_retries`, the waits growing by 5 seconds); HTTP 404 is not retried. A pause of `PAUSE` (2) seconds follows each request. The run asks nothing while NYISO is in `paused_sources.csv`.
- A run asks for the months from the month of `--from` (or of `--days`, 10 by default) to the current month, and writes every hour of each file it reads.

## License

Needs a license. The connector's docstring and `sources.csv` say public, with a caution: NYISO's legal notice grants no license, and its prohibition names "any image or video on this website as a stand-alone file", not data. `license_verdicts.csv` records NYISO, read 5 (`https://www.nyiso.com/legal-notice`, 12 October 2026): "needs written permission", for public and for commercial use. The sentence: "Access to this Web site does not confer any license or ownership interest in either the form or content of the Web site, including any confidential or proprietary information or intellectual property of any kind or nature, and the NYISO hereby expressly reserves such rights and property in its entirety." `license_status.csv` marks the table "license needed" from 21 October 2026. `license_tables.csv` lists it under NYISO.

## Cross-checks (session 2088)

- The counts above were computed from the rows, read past the header lines. No (entity, variable, ts_utc) is given twice, and no hour of the range is missing for any zone: 68,145 hours, each with all eleven.
- Against EIA-930's NYIS demand (`eia930_all_demand`, `demand_mw`) in the 1,022 hours both hold (2026-08-27T00:00:00Z to 2026-10-10T13:00:00Z), the eleven zones' sum equals EIA's figure to within 0.005 percent in every hour. Moved by an hour either way, the median difference is 2.97 or 2.96 percent, so the two tables place the hours alike.
- The entities are the same eleven as `nyiso_dam_zone_prices`.

## What it does not hold

- A total for New York: the file gives none, and none is summed.
- Months before 2019, and the hours after 10 October 2026 13:00 UTC (the newest run on the data machine).
- NYISO's other reports: only P-58C is read.
- Any name in NYISO's files other than the eleven zones: such lines are counted and not written.
