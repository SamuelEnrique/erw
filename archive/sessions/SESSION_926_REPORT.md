# Session 926 report: the World Bank's commodity prices (the Pink Sheet)

23 October 2026, from 09:56 UTC, on lab-desktop (the data machine), a session of `queue/done/052-day-23-october-data-world-oil-reactors-stocks.md`. Model spend USD 0. Pulls: 8 requests of 10, each robots file asked alone and read before its host's next request (www.worldbank.org's; the Commodity Markets page; the robots path of thedocs.worldbank.org, HTTP 404, no file; the Terms of Use for Datasets, which answered with the World Bank's general terms; data.worldbank.org's robots file; its Summary Terms of Use; the monthly workbook; the connector's page).

## Read these first

- **One table written, validated, archived, in coverage (sectors oil, gas, coal and metals, public), in the release package, both holds:** `wb_commodity_prices_monthly`, 11,139 rows, 15 series, January 1960 to September 2026, from the World Bank's CMO Historical Data Monthly workbook (updated 2 October 2026): crude oil (the average, Brent, Dubai, WTI, USD/bbl), coal (Australian, South African, USD/t), natural gas (U.S., Europe, USD/MMBtu) and Japan's LNG (USD/MMBtu), and the base metals per metric ton (aluminum, copper, lead, tin, nickel, zinc).
- **The cross-checks:**
  - Copper and nickel against `imf_commodity_prices`: within 1 percent in all 93 months both hold (2019 to 2026).
  - WTI, Brent and Henry Hub against EIA's daily spot prices (`eia_fuel_spot_prices`) averaged by month: WTI within 3 percent in 487 of 489 months since 1986, Brent in 464 of 472, Henry Hub in 350 of 357; each median within 0.12 percent.
- **The license:** the World Bank's Summary Terms of Use: "Unless indicated otherwise in the data or indicator metadata, you are free to copy, distribute, adapt, display or include the data in other products for commercial or noncommercial purposes at no cost under a Creative Commons Attribution 4.0 International License". The verdict is for session 928 (the licenses' sixth round) to record.

## Decisions made without you

- **Energy and the base metals only,** as the queue file asked for energy and the IMF table holds metals to compare. Not taken: the natural gas index (2010=100, no index unit), the agricultural and fertilizer prices, iron ore ($/dmtu) and the precious metals ($/troy oz), named in the header.
- **The note mark "**" removed from the South African coal series' name** and named in the header (the workbook's Description sheet explains it).

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/wb_pink_sheet.py`, `tests/test_session926.py` (3 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c052/s926/`, `runs/license_reads/s926/`, `runs/s926*`, `warehouse/raw/wb_pink_sheet/`.
