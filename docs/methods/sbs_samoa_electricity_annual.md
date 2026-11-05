# Samoa's electricity a year: production by source and EPC's sales by category (SBS's Electricity Statistics 2025)

Energy Research Warehouse (ERW), method note written in session 2583 (chain 127) for a table first written on 25 October 2026 (session 2574).

Tables: `sbs_samoa_electricity_annual`

## Publisher and address

The Samoa Bureau of Statistics (SBS), Environment Statistics: Electricity Statistics 2025, tables E1 and E3, from the Electric Power Corporation (EPC): `https://www.sbs.gov.ws/documents/social/Environment/2025/Electricity-Statistics-2025.xlsx`. One GET, no key. Source id `sbs_ws:electricity_statistics_2025`. Connector: `warehouse/connectors/sbs_samoa_electricity.py` (session 2574). www.sbs.gov.ws's robots file closes /wp-admin/ only (read 1093).

## Vintage and revision

Written by run `20261025T022051Z` (the write under the lock, offline), which read the workbook saved at 2026-10-25T02:18:20Z. `vintage` is its last-modified time, 2026-07-13T02:04:20Z. Each year's workbook has its own address (2022 to 2025 are listed on SBS's Environment page).

## Shape and variables

Series, 288 rows, 16 entities, all in MWh as SBS gives them; `ts_utc` the year's first day; `freq` P1Y; `geo` WS; `node` SBS's label; `x_table` the table.

| `variable` | Table | Entities (`sbs:ws:<item>`) | Years | Figures |
|---|---|---|---|---|
| `production` | E1 | total, diesel, hydro, coconut, solar, wind, biomass | 2008 to 2025 (126 rows) | total 115.5 GWh in 2008, 226.6 GWh in 2025; solar 27.3 GWh in 2025 |
| `sales` | E3 | commercial, domestic, government, hotels, industrial, religious, schools, local_consumption, street_lights, total | 2008 to 2024 (162 rows) | in 2024 domestic 66.5 GWh, commercial 59.5 GWh, total 193.8 GWh |

The totals hold their parts.

## Reading the source

- The run stops at once, asking nothing, while `sbs_ws` or www.sbs.gov.ws is paused.
- One request a run; `--offline` reads the saved workbook.
- **E1:** the sources found by their header names, each with "MWh" under it (the share columns beside them are not taken); each year's sources add to its total within 1 MWh; the years run without a gap.
- **E3:** the years' row found by its run of years; each category row found by its label (the map lists all nine, and a row not in the map stops the run). **Its TOTAL row is written only for a year where it equals the categories' sum within 1 MWh:** for 2008 to 2015 the workbook prints one figure, 153,987.5 MWh, every year, which its categories do not add to (96.5 GWh in 2008), so those eight totals are not written; 2016 to 2024 are.
- Table E2 (diesel against renewable) repeats E1 and is not taken.
- The run stops, and no file is written, for: a sheet, title, header or unit not found, a row not in the map, a negative figure, a sum missed, a year missing.

Nothing is filled.

## License

Internal. SBS's pages read "(c) 2022 | Samoa Bureau of Statistics, All Right Reserved." (read 1097); no terms of reuse found. Verdict: needs written permission (ZIMSTAT's precedent). Held from the live set and from Redivis.

## Cross-check

EIA's Samoa (`eia_world_electricity_annual`, read past its header lines): 2019 generation 164.8 GWh against SBS's 169.3; hydro 45.0 against 49.8; for 2024, EIA's 162.5 GWh (an estimate) against SBS's 220.5.
