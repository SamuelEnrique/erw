# U.S. crude oil imports by country of origin, a month (EIA)

Energy Research Warehouse (ERW), method note written in session 2018 (chain 057) for a table first written on 26 September 2026 (session 8).

Tables: `eia_crude_imports_by_country`

## Publisher and address

U.S. Energy Information Administration (EIA), U.S. Imports by Country of Origin (crude oil), page `https://www.eia.gov/dnav/pet/pet_move_impcus_a2_nus_ep00_im0_mbbl_m.htm`, through the EIA API v2 route `petroleum/move/impcus`: `https://api.eia.gov/v2/petroleum/move/impcus/data/?api_key=REDACTED&frequency=monthly&data[0]=value&sort[0][column]=period&sort[0][direction]=asc&sort[1][column]=series&sort[1][direction]=asc&offset=0&length=5000&facets[product][]=EPC0&facets[process][]=IM0` (decoded here, as the rows keep it in `source_url`), pages of 5,000. The facets are product EPC0 (crude oil) and process IM0 (imports); no series is named, so every origin EIA lists comes back. Source id `eia:petroleum/move/impcus`. Connector: `warehouse/connectors/eia_series.py` (session 7; this table session 8), one of its thirteen tables. The key comes from `EIA_API_KEY` and is written `REDACTED` in the address each row keeps.

## Vintage and revision

January 1920 to July 2026 in the file on the data machine, read by run `20261010T143359Z` (10 October 2026) and restored from the Redivis draft by `scripts/sync.py`, as its header says; every row's `retrieved_at` is 10 October 2026. Header: "Dates EIA lists without a value, omitted: 0". `coverage.csv` gives the same 22,633 rows and dates.

Each run asks for the full history and `ip.write_csv` merges it into the file on (entity, variable, ts_utc): a month EIA revises is replaced, and a row EIA stops giving is kept from an earlier run. The file's header line "every run replaces all of it" is the older wording; the code's header has said otherwise since session 865 (23 October 2026), after this file was written. A table whose newest month is more than 150 days old is not written.

## Shape and variables

Series, 22,633 rows: 82 series. `entity` `eia:<EIA series id>`; `variable` `imports`; `unit` kbbl/d (EIA's thousand barrels a day, whole numbers as published); `ts_utc` the month's first day at 00:00:00Z; `freq` P1M; `geo` US on every row; `market`, `node` and `vintage` empty (EIA's series names are in the header's "Series:" line).

| Series | What | Rows | Months |
|---|---|---|---|
| MCRIMUS2 | U.S. imports of crude oil, all origins | 1,279 | 1920-01 to 2026-07, none missing |
| MCRIMXX2 | from OPEC countries | 643 | 1973-01 to 2026-07 |
| MCRIMUSVV2 | from non-OPEC countries | 403 | 1993-01 to 2026-07 |
| MCRIMUSPG2 | from Persian Gulf countries | 402 | 1993-01 to 2026-06 |
| 78 others | one origin each, as EIA names it (countries, and Netherlands Antilles, Puerto Rico and the Virgin Islands) | 1 to 643 each | from 1973-01 at the earliest |

Before 1973 the table holds the total only. The largest origin series: Canada (MCRIMUSCA2), 643 months, 4,155 kbbl/d in July 2026. 5,699 rows are a value of 0, as EIA lists them, and many origin series have months inside their span with no row at all (Netherlands MCRIMUSNL2: 299 rows over a span of 611 months). The aggregates hold their parts: a sum takes one level.

## Reading the API

- The rows read must equal the total the API reports, or the table is not written; an empty answer stops it too.
- Rows whose unit is not EIA's MBBL/D are dropped before any other check (`keep_units`), so the table holds the per-day series only. The first run, 26 September 2026, read 37,102 rows and kept 22,615 (its log, `warehouse/output/logs/eia_series_20260926T001438Z.log`).
- A unit not in the connector's map, or a (series, month) given twice, stops the table.
- A value that is not a number stops the table, except an empty value, "none" and "Not Available", which are omitted and counted (none here).
- The origins are asked by facet, not by series id, so the connector's check that each series asked for came back does not cover them.
- No ceiling is stated. A page is tried up to four times; pages are 0.5 seconds apart.

## License

Public: a work of the U.S. government (record 1 of `license_reads.csv`). The header: "License: public domain (EIA)"; `coverage.csv`: public.

## Cross-checks (session 2018)

- The counts above were computed from the rows, read past the 12 header lines; no (entity, variable, ts_utc) is given twice.
- OPEC plus non-OPEC equals the total within 1 kbbl/d in all 403 months from January 1993 (July 2026: 788 + 5,436 = 6,224).
- The seven Persian Gulf origins (Saudi Arabia, Iraq, Kuwait, Qatar, United Arab Emirates, Bahrain, Iran) sum to MCRIMUSPG2 within 2 kbbl/d in all 402 of its months.
- The 78 origin series sum to the total within 5 kbbl/d in 265 of the 271 months from January 2004 (largest gap 22 kbbl/d, January 2015; July 2026: 6,225 against 6,224). Earlier they differ more often: 40 months from January 1993 differ by more than 5 kbbl/d (up to 228), most of them in 1993, 1994 and 2003, and from 1973 to 1992 the difference reaches 558 kbbl/d (August 1992).
- The connector has no cross-check of its own beyond its reading rules.

## What it does not hold

- Imports of petroleum products, and any series of the route in a unit other than thousand barrels a day (dropped by the unit filter).
- A row for a month EIA does not list: July 2026 has no Persian Gulf row, and the Persian Gulf origins' latest rows are June 2026 or earlier.
- Destinations, ports, companies and grades: those are `eia_crude_imports_detail_monthly`. Weekly imports are `eia_petroleum_trade_weekly`; exports by destination are `eia_petroleum_exports_by_destination`.
