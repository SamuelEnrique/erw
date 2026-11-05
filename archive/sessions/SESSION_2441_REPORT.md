# Session 2441 report: a second source of the session's own choosing (Canada's annual supply and disposition of electric power, Statistics Canada 25-10-0021-01), public

24 October 2026, from 11:45 UTC to 11:49 UTC, on lab-desktop (the data machine), chain 117, unattended. Precheck passed (`runs/c117/pre2441.out`). Model spend USD 0. Pulls: 2 requests of 20 (the robots file, and the fetch the connector reads offline).

## Read these first

- **Why this source:** each province's yearly balance of electricity, the companion of session 2440's table:
  - generation;
  - imports from and exports to the United States (firm, secondary and exchanged);
  - interprovincial receipts and deliveries;
  - the electricity available;
  - the producers' own use;
  - sales to ultimate customers by sector (residential, mining and manufacturing, agriculture, other industries).

  The ERW's monthly trade table (25-10-0016-01) gives no sales by sector. No chain has taken this table (main and chains 114's and 115's branches searched).
- **www150.statcan.gc.ca's robots file**, asked again in this session's own call, disallows paths ending in `.csv` and names no AI agent (read 807).
- **A new table, `statcan_power_disposition_annual`** (series, 3,909 rows, 21 components, `power`): quantities in MWh by province and territory, 2005 to 2025.
  - **Not taken:** the estimate "Electricity value" (2,153 rows in Canadian dollars), a foreign currency's values being a standing question for the owner. It is counted in the header.
  - StatCan's ".." (867) have no row. Revisions are kept in `x_revised`.
  - Written, validated (0 errors, 0 warnings), archived, and held from the Redivis storage and the live set.
- **Public.** The Statistics Canada Open Licence; StatCan's verdict is on record.

## Cross-checks

- **Within the table, Canada:** generation plus imports less exports equals the electricity available in every year but 2015 (1.0065).
- **Against session 2440's `statcan_generation_class_annual`:** total generation equals its total of all classes and types in every year, 1.000.
- **Against `statcan_electricity_trade_monthly`:** exports to the United States are 0.968 to 1.011 of its twelve-month sums of US deliveries, 2008 to 2025. The exception is 1.087 in 2015, the same year as the balance's gap.
- **Canada's exports to the United States, TWh:** 73.0 in 2015, 47.8 in 2023, 36.1 in 2024 and 31.9 in 2025.

## Requests (2 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | www150.statcan.gc.ca/robots.txt | 200: `.csv` closed |
| 2 | 25100021-eng.zip (the fetch) | 200, 105,168 bytes, last modified 16 October 2026 |

Reads recorded: 807 (on this branch).

## Decisions made without you

- **Quantities only;** the dollar values are left out under the chain's rule on foreign currencies.
- **A second Canadian table,** for its balance and its sales by sector, close to U.S. markets.

## For Samuel's ruling

- None.

## Files

- New: `warehouse/connectors/statcan_power_disposition.py`, `tests/test_session2441.py`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`;
  - `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`;
  - the license record (read 807) and `docs/redivis/release-v1/` (the table's rows).
- On the data machine only: `runs/c117/s2441/`, `warehouse/raw/statcan_power_disposition/`, `warehouse/output/statcan_power_disposition_annual.csv`.
