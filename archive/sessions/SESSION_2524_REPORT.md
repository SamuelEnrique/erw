# Session 2524 report: Kosovo's electricity a month, January 2022 to July 2026 (the Kosovo Agency of Statistics' ASKdata), the session's own choice, internal

24 October 2026, about 19:16 to 19:20 UTC for the reads and the connector; the table written under the data lock at 19:23 UTC. On lab-desktop (the data machine), chain 123, unattended. Precheck passed (`runs/c123/pre2524.out`). Model spend USD 0. Pulls: 9 requests of 20 (8 by the probe, 1 by the connector's query).

## Read these first

- **Why Kosovo:** a grid the ERW held only in EIA's world table and in Eurostat's tables, which leave it out of commercial reuse; ASK publishes a monthly table through a PxWeb API.
- **The Kosovo Agency of Statistics (ASK):** askdata.rks-gov.net and ask.rks-gov.net answer HTTP 404 for a robots file (reads 956, 962). The API's listings (reads 957 to 960) lead to "Electricity production and consumption" (tab01, read 961): 13 items a month, 2022M01 to 2026M07.
- **A new table, `ask_kosovo_electricity_monthly`** (series, 715 rows, 11 entities, `power`): gross production (thermal, hydro, wind and solar), imports, exports, gross electricity available, and consumption by sector (households, commercial, industry, public lighting and others, 220-110 kV consumers, mining) and in total.
  - **The scale:** the dimension is named "MWH", but its figures carry three decimals (px decimals 3) and a year's gross electricity available sums to about 7.3 thousand. Read as thousands of MWh, its 2024 imports and exports equal `eia_world_electricity_annual`'s Kosovo to the MWh (3,159,876 and 2,622,204), and its gross production is 0.96 of EIA's generation (6.75 against 7.02 TWh). The connector multiplies by 1,000 to MWh and says so.
  - Months are labelled "2026M07" or "202308"; both are read.
  - Written by run `20261024T192332Z`, validated (0 errors, 0 warnings), archived, held from the Redivis storage and the live set.
- **Internal, not settled.** No terms of reuse were found: ask.rks-gov.net/en/ answers HTTP 404 (read 963), and a web search found only Kosovo's administrative instruction 02/2023 on selling statistical data and Eurostat's GEOSTAT conditions (Kosovo's data its office's, commercial use by approval).

## Cross-checks

- Gross production, TWh, whole years: 6.98 (2022), 6.33 (2023), 6.75 (2024), 5.86 (2025).
- Against EIA's 2024 figures for Kosovo (above): imports and exports equal; gross production 0.96 of EIA's generation.

## Requests (9 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | askdata.rks-gov.net/robots.txt | 404 |
| 2 to 5 | the API's listings down to the monthly energy tables | 200 |
| 6 | tab01's metadata | 200 |
| 7 | ask.rks-gov.net/robots.txt | 404 |
| 8 | ask.rks-gov.net/en/ | 404 |
| 9 | tab01 by POST, every value selected | 200 |

Reads recorded: 956 to 963 (on this branch). One web search for the terms reached no publisher's host.

## Decisions made without you

- **Kosovo as the session's own choice; internal** until ASK's terms are read.
- **The figures read as thousands of MWh,** on their decimals and EIA's totals, and the reading stated in the header.

## For Samuel's ruling

- **ASK's terms of reuse,** which a letter could settle.

## Files

- New: `warehouse/connectors/ask_kosovo_electricity.py`, `tests/test_session2524.py`, this report.
- Changed: the registration; the metadata files; the license record (reads 956 to 963).
- On the data machine only: `runs/c123/s2524/`, `warehouse/raw/ask_kosovo_energy/`, `warehouse/output/ask_kosovo_electricity_monthly.csv`.
