# Anguilla's electricity generation a month, 1995 to 2025 (the Anguilla Statistics Department's Table 2.4.2-1, ANGLEC's figures)

Energy Research Warehouse (ERW), method note written in session 2642 (chain 131) for a table first written on 25 October 2026 (session 2642). The chain's notes session (2639) ran before the table existed, so its note is written with it.

Tables: `statai_anguilla_electricity_monthly`

## Publisher and address

The Anguilla Statistics Department, Energy Statistics workbook, sheet "Table 2.4.2-1", "Electricity Generation, Month: 1995 - 2026", whose source is the Anguilla Electricity Company (ANGLEC): `https://statistics.gov.ai/AllDocuments/2.4.2%20Energy%20Statistics.xlsx`, linked from the Department's Energy page (`https://statistics.gov.ai/StatisticsDept/Energy2_4_2`). One GET, no key. Source id `statai_ai:energy_statistics_table_2_4_2_1`. Connector: `warehouse/connectors/statai_anguilla_electricity.py` (session 2642), whose raw store is `warehouse/raw/statai_ai/`. statistics.gov.ai has no robots file (HTTP 404, read 1294).

## Vintage and revision

Written by run `20261025T080827Z` (the write under the lock, offline), which read the workbook saved at 2026-10-25T08:06:16Z. `vintage` is its last-modified time, 2026-06-08T03:28:43Z. The workbook's contents sheet says it was published on 26 May 2026. The Department replaces the file as months are added.

## Shape and variables

Series, 372 rows, 1 entity, each month of 1995 to 2025. `entity` `statai:ai:anglec`; `variable` `generation`; `unit` MWh (the table's kWh divided by 1,000); `ts_utc` the month's first day; `freq` P1M; `geo` AI; `node` the table's label.

The year's generation was 23,205.5 MWh in 1995 and 110,181.8 MWh in 2025. September to December 2017 are low (1,401.8 MWh in September); the table gives no reason.

**Two oddities, kept as printed:**
- 2026's three months (January to March) are left out: the run writes whole years only, and February's and March's figures repeat 2025's exactly (the table's own % change is 0), so they cannot be told from placeholders.
- January 2022 and January 2023 carry the same figure (8,363,036 kWh); it is written for both, as printed.

## Reading the source

- The run stops at once, asking nothing, while `statai_ai` or statistics.gov.ai is paused.
- One request a run; `--offline` reads the saved workbook.
- **The sheet** "Table 2.4.2-1" is read by its title cell ("Electricity Generation") and its header row: "Month", then the years from 1995 without a gap, then "% Change". The twelve month rows follow in order, then "Total".
- **Whole years only:** a year whose twelve months are not all figures is left out.
- **Check:** each year's twelve months add to its Total within 1 kWh.
- The run stops, and no file is written, for: the title or header not found once, years not a run from 1995, a month row out of place, a check missed.

Nothing is filled. Not taken: the annual % change; the workbook's other sheets (revenue in XCD, petroleum product imports).

## License

Internal. The Department's site (read 1295) reads, after a copyright sign and 2026, "Anguilla Statistics Department, GOA . All rights reserved.", with no terms of reuse linked. Verdict: needs written permission. The figures are ANGLEC's. Held from the live set and from Redivis.

## Cross-check

EIA's world table holds no Anguilla. Within the workbook, each year's Total row equals its months' sum (the run's check).
