# The Maldives' public electricity production by island a month, and Male's use by sector a year (NBS's Statistical Yearbook 2026, tables 12.2 and 12.1)

Energy Research Warehouse (ERW), method note written in session 2569 (chain 126) for a table first written on 25 October 2026 (session 2562).

Tables: `nbs_maldives_electricity`

## Publisher and address

The Maldives Bureau of Statistics (NBS), its Statistical Yearbook of Maldives 2026, both tables from the State Electric Company Limited (STELCO):

- table 12.2, "Monthly Electricity Production by Public Sector, 2025": `https://statisticsmaldives.gov.mv/yearbook/2026/wp-content/uploads/sites/13/2026/06/12.2.xlsx`;
- table 12.1, "Electricity Utilization in Male', 2010 - 2025" (its columns start at 2009): `https://statisticsmaldives.gov.mv/yearbook/2026/wp-content/uploads/sites/13/2026/06/12.1.xlsx`.

Two GETs, no key. Source ids `nbs_mv:yearbook_2026_table_12_2` and `nbs_mv:yearbook_2026_table_12_1`. Connector: `warehouse/connectors/nbs_maldives_electricity.py` (session 2562). statisticsmaldives.gov.mv's robots file closes /mbs/wp-admin/ only (read 1059).

## Vintage and revision

Written by run `20261025T002414Z` (the write under the lock, offline), which read the workbooks saved at 2026-10-25T00:20:17Z (12.2) and 00:20:10Z (12.1). `vintage` is each workbook's last-modified time, 2026-06-11T11:39:26Z and 11:39:24Z. Each yearbook has its own addresses.

## Shape and variables

Series, 505 rows, 40 entities, two frequencies; `x_table` says which table a row is from.

| `variable` | `entity` | `freq` | Rows | Figures |
|---|---|---|---|---|
| `production` (12.2) | `nbs_mv:<island>`: 35 islands (`k_male`, `k_hulhumale`, `k_vilimale`, ..., `v_rakeedhoo`; NBS's label in lower case, each run of other characters an underscore) | P1M, 2025 | 420 | 907.1 GWh in all; Hulhumale 437.3, Male' 324.1, Maafushi 19.7 |
| `utilization` (12.1) | `nbs_mv:male:<sector>`: `total`, `residential`, `manufacturing_commercial`, `government_buildings`, `public_places_schools` | P1Y, 2009 to 2025 | 85 | the total 187.1 GWh in 2009, 450.3 in 2025 |

`unit` MWh; `ts_utc` the month's or year's first day; `geo` MV; `node` NBS's label. 12.1's total holds its four sectors.

## Reading the source

- The run stops at once, asking nothing, while `nbs_mv` or statisticsmaldives.gov.mv is paused.
- Two requests a run; `--offline` reads the saved workbooks. Each holds one sheet.
- **Table 12.2's unit.** Its heading says "In '000 kWh", but its cells are kWh: K.Male' would otherwise have made 324 TWh in 2025. The connector divides them by 1,000, and checks the unit against table 12.1: the Greater Male' islands' production (K.Male', K.Vilimale', K.Hulhumale; 777.8 GWh in 2025) must fall between one and three times Male's use for the same year (450.3 GWh; 1.73 times), so a workbook corrected to thousands stops the run.
- **Table 12.2** is read from its header row (Total and the twelve months) to its source line; a region's heading (no figures) is passed over. Each island's months must add to its Total within 1 MWh; the Total column is not written.
- **Table 12.1** is read from its "Load Distribution" row (the years) to its shares ("% share"); its total row must say "'000 kWh" (MWh as given), and its four sectors must add to it within 1 MWh each year. The shares, the changes and the Dhivehi labels are not taken.
- The run stops, and no file is written, for: a title or header row not found, a row of 12.1 missing or given twice, an island given twice, a cell that is not a number, a check missed.

Nothing is filled. Not taken: the fuel and lubricating oil tables (12.3, 12.4), Male's consumption table (12.5), the water tables.

## License

Internal. NBS's pages (the yearbook's page, the home page, the Statistics Act and Regulation page; reads 1062 to 1064) state no terms of reuse, and the Maldives Statistics Act (Act 16/2021, its English translation, read 1065) grants none. Verdict: needs written permission (RGGI's precedent). Held from the live set and from Redivis.

## Cross-check

EIA's 2024 generation for the Maldives (855.1 GWh, `eia_world_electricity_annual`) against NBS's 907.1 GWh of public-sector production in 2025, a year later; the resorts' own generation is not in NBS's table.
