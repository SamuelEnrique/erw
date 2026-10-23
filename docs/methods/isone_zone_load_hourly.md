# ISO New England's real-time demand by load zone and the control area's total, an hour (ISO-NE's SMD Hourly Data), internal

Energy Research Warehouse (ERW), method note written in session 2088 (chain 068) for a table first written on 6 October 2026 (session 138).

Tables: `isone_zone_load_hourly`

## Publisher and address

ISO New England (ISO-NE), "Zonal Information" (`https://www.iso-ne.com/isoexpress/web/reports/load-and-demand/-/tree/zone-info`), the yearly workbook "SMD Hourly Data". The connector reads the page's file list as JSON (`https://www.iso-ne.com/isoexpress/web/reports/download/docWidgetGetMore?start=<N>&treenode=zone-info`, pages of `LIST_STEP` (40), at most `LIST_PAGES` (3)), keeps the addresses that match `FILE` (`/static-assets/documents/<folder>/<YYYY>_smd_hourly.xlsx`) with the list's publish date, then asks for one workbook a year, newest first. A workbook has a sheet for the control area (ISO NE CA) and one a load zone; the connector reads Date, Hr_End and RT_Demand from each. Source id `isone:smd_hourly`. Connector: `warehouse/connectors/isone_zone_load.py` (session 138), with the frame it shares with the other load connectors in `warehouse/connectors/zone_load.py` (`zone_load.run` writes the table, `zone_load.rows` makes its rows).

The docstring records that on 6 October 2026 the page, its list and each workbook answered a plain request (HTTP 200), with no cookie, no account and no CAPTCHA. The page's own several-files download form carries a CAPTCHA; that form is not used.

## Vintage and revision

1 January 2025 to 31 August 2026 (Eastern) in the file on the data machine: `ts_utc` from 2025-01-01T05:00:00Z to 2026-09-01T03:00:00Z. The file was restored from the internal Redivis draft (`energy_research_warehouse_internal`) by `scripts/sync.py` and carries the header of run `20261010T150238Z` (10 October 2026): "Rows read from the operator in this run: 52,479 ... Rows written by this run: 52,479, 2026-01-01T05:00:00Z to 2026-09-01T03:00:00Z." The table is merged into the one held (`iso_prices.write_csv`).

Two workbooks stand behind the rows: `2025_smd_hourly.xlsx` (78,840 rows, retrieved 2026-10-07T01:44:08Z) and `2026_smd_hourly.xlsx` (52,479 rows, retrieved 2026-10-10T15:02:44Z). `vintage` is empty in every row: it would be the workbook's Last-Modified (`iso_prices.vintage_of`), and none was recorded. The history asked for was kept to 2025 and 2026 (the docstring: "the history asked for here is modest").

A year's workbook is asked for again only when the list's publish date for it is later than the kept copy's retrieval, so ISO-NE's re-posting of a year is taken. ISO-NE extends the current year's workbook about once a month (the header). A table whose newest hour is more than 100 days old (`stale_days`) is not written.

## Shape and variables

Series, 131,319 rows: 9 series of 14,591 hours each. `variable` `load`; `unit` MW (RT_Demand is MWh for the hour, which is MW over the hour); `freq` PT1H; `ts_utc` the hour's start; `geo` "US-CT,US-MA,US-ME,US-NH,US-RI,US-VT"; `market` isone_load; `node` the sheet's name.

| Entity | Sheet (`node`) |
|---|---|
| isone:.Z.MAINE | ME |
| isone:.Z.NEWHAMPSHIRE | NH |
| isone:.Z.VERMONT | VT |
| isone:.Z.CONNECTICUT | CT |
| isone:.Z.RHODEISLAND | RI |
| isone:.Z.SEMASS | SEMA |
| isone:.Z.WCMASS | WCMA |
| isone:.Z.NEMASSBOST | NEMA |
| isone:system | ISO NE CA, ISO-NE's own total |

The eight zone entities are those of `isone_dam_zone_prices` and `isone_rtm_zone_prices`, so load and price join on entity (Decision 42). isone:system is ISO-NE's own sheet, never a sum made here. It runs from 7,577.1 MW (2025-04-20T18:00:00Z) to 26,085.9 MW (2025-06-24T22:00:00Z). The workbook's other columns (day-ahead demand, prices, temperatures) are read and not written.

## Reading the source

- The hour. Hr_End is the hour ending, 1 to 24, Eastern; `ts_utc` is the hour's start (`zone_load.to_utc`). "02X" marks the second 01:00 to 02:00 hour of the autumn clock change. The spring day's 23 lines go 01, 03: the line labelled 03 is placed by its end. A repeated hour held once only is not placed, not written, and counted in the log and the header.
- A workbook that does not begin as a zip (`PK`) stops the table, and so does one without all nine sheets (`SHEETS`), a sheet without Date, Hr_End and RT_Demand, or an hour ending outside 1 to 24.
- An RT_Demand that is not a number is read as blank and its row is not written; that is not counted. A zone and hour given twice in a workbook stops the table (`zone_load.rows`).
- A year the list does not hold is not written and is named in the header.
- Ceiling: 80,000 rows read a run (`SPEC["ceiling"]`); a year's workbook is taken to hold `ROWS_A_YEAR` (79,056). A run stops before a workbook that would pass the ceiling and needs a request; a reused raw file is not counted. Past the ceiling the run stops and writes nothing.
- Each request is tried up to four times (`iso_prices.with_retries`, the waits growing by 5 seconds); HTTP 404 is not retried. A pause of `PAUSE` (3) seconds follows each request. The run asks nothing while ISO-NE is in `paused_sources.csv`.
- A run asks for the years from the year of `--from` (or of `--days`, 10 by default) to the current year, and writes every hour of each workbook it reads.

## License

Internal: the table is not published, in no public dataset and no download (Decision 42; `sources.csv` flags `isone:smd_hourly` internal). `license_verdicts.csv` records ISO-NE, read 4 (`https://www.iso-ne.com/legal-privacy`, 12 October 2026): "needs written permission", for public and for commercial use. The sentence: "You are also hereby put on notice that the Content is protected by copyright under United States laws. Any duplication of the Content or non-personal use may violate copyright, trademark, and other laws." The contact the verdict names: info@iso-ne.com. `license_tables.csv` lists the table under ISO-NE.

## Cross-checks (session 2088)

- The counts above were computed from the rows, read past the header lines. No (entity, variable, ts_utc) is given twice, and no hour of the range is missing for any of the nine series.
- The eight zones sum to isone:system within 0.002 MW in every one of the 14,591 hours.
- Against EIA-930's ISNE demand (`eia930_all_demand`, `demand_mw`) in the 148 hours both hold (2026-08-26T00:00:00Z to 2026-09-01T03:00:00Z), EIA's figure is within 1 percent of isone:system in 12 hours only; the differences run from -12.89 to +13.81 percent, median +1.48. Moving EIA's hours by one either way does not bring them together (median difference 4.31 or 8.58 percent, against 4.34 unmoved). The two figures differ in these hours, and this note does not explain why.

## What it does not hold

- Years before 2025, and the hours ISO-NE has not yet added to its 2026 workbook (September on, as read).
- The workbook's day-ahead demand, prices and temperatures.
- A public copy: the table is internal.

## Found by session 2110 (chain 069), which described this table the same evening

- The usage line and the frame's help give `--days N` as "how many days back to ask for", and the frame's "stale at source" test looks for no hour on or after that first day. For ISO-NE the days only choose which years' workbooks are read: every hour of each workbook is written, so that test can fire only on a workbook with no hour at all.
- Neither docstring says what becomes of text where a number should be: the code drops such a cell without a word (`pd.to_numeric(..., errors="coerce")`), where the other ISO-NE connectors stop the run.
