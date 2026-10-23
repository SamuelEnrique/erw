# Crude oil moved by pipeline between PAD districts, a month (EIA)

Energy Research Warehouse (ERW), method note written in session 2018 (chain 057) for a table first written on 26 September 2026 (session 8).

Tables: `eia_padd_crude_pipeline_flows`

## Publisher and address

U.S. Energy Information Administration (EIA), Movements by Pipeline between PAD Districts (crude oil), page `https://www.eia.gov/dnav/pet/pet_move_pipe_dc_r10-r20_mbbl_m.htm`, through the EIA API v2 route `petroleum/move/pipe`: `https://api.eia.gov/v2/petroleum/move/pipe/data/?api_key=REDACTED&frequency=monthly&data[0]=value&sort[0][column]=period&sort[0][direction]=asc&sort[1][column]=series&sort[1][direction]=asc&offset=0&length=5000&facets[product][]=EPC0` (decoded here, as the rows keep it in `source_url`), pages of 5,000. The facet is product EPC0 (crude oil); no series is named, so every crude series of the route comes back. The connector's docstring records the choice: the pipeline-only route, where `docs/price-sources.md` named `petroleum/move/ptb`, which combines pipeline, tanker, barge and rail. Source id `eia:petroleum/move/pipe`. Connector: `warehouse/connectors/eia_series.py` (session 7; this table session 8). The key comes from `EIA_API_KEY` and is written `REDACTED` in the address each row keeps.

## Vintage and revision

January 1986 to July 2026 in the file on the data machine, read by run `20261010T143359Z` (10 October 2026) and restored from the Redivis draft by `scripts/sync.py`, as its header says; every row's `retrieved_at` is 10 October 2026. Header: "Dates EIA lists without a value, omitted: 0". `coverage.csv` gives the same 4,558 rows and dates.

Each run asks for the full history and `ip.write_csv` merges it into the file on (entity, variable, ts_utc): a month EIA revises is replaced, and a row EIA stops giving is kept from an earlier run. The file's header line "every run replaces all of it" is the older wording; the code's header has said otherwise since session 865 (23 October 2026), after this file was written. A table whose newest month is more than 150 days old is not written.

## Shape and variables

Series, 4,558 rows: 11 series. `entity` `eia:<EIA series id>`; `variable` `pipeline_receipts`; `unit` kbbl (EIA's thousand barrels received in the month, not a daily rate); `ts_utc` the month's first day; `freq` P1M; `geo` US on every row; `market`, `node` and `vintage` empty (EIA's series names are in the header's "Series:" line).

| Series | Receiving district, from | Rows | Months | July 2026, kbbl |
|---|---|---|---|---|
| MCRMPP1P21 | PADD 1 (East Coast) from PADD 2 (Midwest) | 487 | 1986-01 to 2026-07 | 264 |
| MCRMP_R10-R30_1 | PADD 1 from PADD 3 (Gulf Coast) | 246 | 2004-01 to 2024-06 | |
| MCRMPP2P11 | PADD 2 from PADD 1 | 475 | 1986-01 to 2026-07, 12 months missing | 108 |
| MCRMPP2P31 | PADD 2 from PADD 3 | 487 | 1986-01 to 2026-07 | 26,825 |
| MCRMPP2P41 | PADD 2 from PADD 4 (Rocky Mountain) | 487 | 1986-01 to 2026-07 | 29,117 |
| MCRMPP3P11 | PADD 3 from PADD 1 | 462 | 1986-01 to 2024-06 | |
| MCRMPP3P21 | PADD 3 from PADD 2 | 487 | 1986-01 to 2026-07 | 44,778 |
| MCRMPP3P41 | PADD 3 from PADD 4 | 476 | 1986-01 to 2026-07, 11 months missing | 275 |
| MCRMPP3P51 | PADD 3 from PADD 5 (West Coast) | 204 | 1986-01 to 2002-12 | |
| MCRMPP4P21 | PADD 4 from PADD 2 | 487 | 1986-01 to 2026-07 | 8,180 |
| MCRMP_R40-R30_1 | PADD 4 from PADD 3 | 260 | 2004-01 to 2026-07, 11 months missing | 0 |

730 rows are a value of 0, as EIA lists them; PADD 4's receipts from PADD 3 are 0 in all 260 of its rows, PADD 3's from PADD 5 have no value above 0 after February 2000, and PADD 3's from PADD 1 none after April 2024.

## Reading the API

- The rows read must equal the total the API reports, or the table is not written; an empty answer stops it too.
- A unit not in the connector's map, or a (series, month) given twice, stops the table. Every row here is EIA's MBBL.
- A value that is not a number stops the table, except an empty value, "none" and "Not Available", which are omitted and counted (none here).
- The series are asked by facet, not by series id, so the connector's check that each series asked for came back does not cover them.
- No ceiling is stated. A page is tried up to four times; pages are 0.5 seconds apart.

## License

Public: a work of the U.S. government (record 1 of `license_reads.csv`). The header: "License: public domain (EIA)"; `coverage.csv`: public.

## Cross-checks (session 2018)

- The counts above were computed from the rows, read past the 12 header lines; no (entity, variable, ts_utc) is given twice, no value is negative, and the 11 entities are the 11 series the header names.
- The table holds no total, so no sum is checked against one. The eight series with a July 2026 row sum to 109,547 kbbl; the largest flow, PADD 3's receipts from PADD 2, is 44,778 kbbl (1,444 kbbl a day over the month's 31 days).
- The connector has no cross-check of its own beyond its reading rules.

## What it does not hold

- Petroleum products, and crude moved by tanker, barge or rail: those movements are `eia_padd_rail_barge_movements_monthly` (`eia_padd_movements.py`).
- Movements within a district, and pipeline flows across the border.
- A month EIA does not list for a series (34 months in all inside the spans above).
