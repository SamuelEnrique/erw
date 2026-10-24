# Session 2483 report: a second source of the session's own choosing (Canada's manufacturing industries' energy use by fuel, Statistics Canada 25-10-0025-01), public

24 October 2026, from 13:35 UTC to 13:41 UTC, on lab-desktop (the data machine), chain 120, unattended. Precheck passed (`runs/c120/pre2483.out`). Model spend USD 0. Pulls: 2 requests of 20 (the robots file, and the fetch the connector reads offline).

## Read these first

- **Why this source:** the industrial load beside the U.S. markets: each manufacturing industry's yearly use of electricity, natural gas and the other fuels, 1995 to 2024. No ERW table gives a country's energy use by manufacturing industry, and no chain has taken this table (main and chains 118's and 119's branches searched).
- **www150.statcan.gc.ca's robots file**, asked in this session's own call, disallows paths ending in `.csv` and names no AI agent (read 822).
- **A new table, `statcan_manufacturing_energy_annual`** (series, 15,326 rows, 103 industries, 15 fuels, `power`): consumption in MWh, StatCan's gigajoules divided by 3.6, Canada only.
  - StatCan's quality grade (A to E) is kept in `x_quality`.
  - Figures marked ".." (272), "x" (4,219, confidential) or "F" (977, too unreliable) have no row and are counted.
  - Industries nest (all manufacturing, subsectors, groups): a sum takes one level.
  - Written, validated (0 errors, 0 warnings), archived, and held from the Redivis storage and the live set.
- **Public.** The Statistics Canada Open Licence; StatCan's verdict is on record.
- **The raw folder was renamed** from the fetch's working name to the connector's (`warehouse/raw/statcan_manufacturing_energy/`), so the connector finds it. Its manifest is unchanged.

## Cross-checks

- All manufacturing's electricity, TWh: 173.5 (1995), 201.3 (2005), 166.0 (2015), 172.4 (2024).
- Over `statcan_power_disposition_annual`'s sales to mining and manufacturing: 1.013 to 1.204, 2005 to 2024. Manufacturing's use exceeds the utilities' sales by industry's own generation, which those sales leave out. Mining in the sales works the other way, so the ratio is a bound, not an identity.

## Requests (2 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | www150.statcan.gc.ca/robots.txt | 200: `.csv` closed |
| 2 | 25100025-eng.zip (the fetch) | 200, 313,313 bytes, last modified 29 October 2025 |

Reads recorded: 822 (on this branch).

## Decisions made without you

- **Gigajoules written as MWh** (divided by 3.6), as chain 112's energy balance wrote terajoules, every fuel in one unit.
- **StatCan's "F" figures left out** like its suppressed ones; its grades A to E kept.

## For Samuel's ruling

- None.

## Files

- New: `warehouse/connectors/statcan_manufacturing_energy.py`, `tests/test_session2483.py`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`;
  - `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`;
  - the license record (read 822) and `docs/redivis/release-v1/` (the table's rows).
- On the data machine only: `runs/c120/s2483/`, `warehouse/raw/statcan_manufacturing_energy/`, `warehouse/output/statcan_manufacturing_energy_annual.csv`.
