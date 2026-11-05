# Session 910 report: Canada's natural gas trade with the U.S. (Canada Energy Regulator)

23 October 2026, from 08:00 UTC, on lab-desktop (the data machine), a session of `queue/done/051-day-23-october-data-world-gas-hydro.md`. Model spend USD 0. Pulls: 7 requests of 20. The CER's robots file, asked alone first (the same as session 887's); a statistics address that answered with the CER's "HTTP 403" page; the natural gas page; the Natural Gas Trade Summary page; its workbook; the robots file of apps.cer-rec.gc.ca (the Commodity Statistics host), which reset the connection and was not asked again; and the connector's page.

## Read these first

- **One table written, validated, archived, in coverage (sector gas, public), in the release package, both holds:** `cer_gas_trade`, 1,427 rows, from the CER's Natural Gas Trade Summary workbook (updated March 2026, last modified 1 April 2026). It holds, each month:
  - Canada's pipeline exports to the U.S., January 2010 to December 2025 (Mcf), and the same exports by the U.S. region of the border crossing (West, Midwest, East);
  - Canada's LNG exports (gaseous equivalent, from 2013; 110.9 Bcf in 2025, the first year of LNG Canada, against at most 2.6 Bcf a year before);
  - the export price (USD/MMBtu);
  - Canada's imports from the U.S. and their price, January 2010 to December 2022.
- **Not by port:** the workbook groups the border crossings into three U.S. regions. The ports are in the CER's Commodity Statistics application, whose host reset the connection to its robots file; it was not asked again.
- **The cross-checks:**
  - The three regions summed equal the total exports within 0.02 percent in every one of 192 months (exactly in 183), and the months summed equal the workbook's own annual sheet in 16 of 16 years.
  - **The CER's exports against EIA's U.S. pipeline imports from Canada** (`eia_gas_trade_country_monthly`, two countries' records of one flow): 192 months, 144 within 3 percent, median 1.7 percent above EIA's. By year (Bcf, CER and EIA): 2010 3,243 and 3,280; 2015 2,682 and 2,625; 2020 2,504 and 2,500; 2024 3,206 and 3,128; 2025 3,200 and 3,149.
  - **The CER's imports against EIA's U.S. pipeline exports to Canada:** 156 months to December 2022, median 3.0 percent below EIA's, wider from 2020 (2020: 805 and 904 Bcf).
  - The CER's export price against EIA's price of U.S. imports from Canada (USD/MMBtu against USD/Mcf): median ratio 0.986; 2025 means 2.58 and 2.71.
- **Imports taken to December 2022 only:** the page says "the import data after December 2022 has been removed from the website", but its archived sheet runs to December 2024. Those later months fall away from EIA's record of the same flow (88 percent of it in 2023, 45 percent in 2024, 14 percent in December 2024, against 92 percent in 2022), so the 48 import and import price figures after December 2022 are left out and counted in the header.

## Decisions made without you

- **Mcf and USD/MMBtu, the CER's own columns, as given.** The CER's cubic metres, its values in Canadian dollars and its Canadian dollar prices per GJ are not taken (no such units in the data standard; session 887's question of a `CAD` unit stands).
- **The archived sheet's LNG import columns are not taken:** they repeat its gas import columns figure for figure (66.6 Bcf in January 2010, all of Canada's imports, not LNG).
- **The imports cut at December 2022,** as above.
- **Table flagged `public`,** under the CER's verdict of session 887 (non-commercial reproduction with the title, author and the not-endorsed statement, which the header carries).

## For Samuel's ruling

- None new (a `CAD` unit, session 887's, would also bring the CER's gas values and Canadian dollar prices).

## Files

- New: `warehouse/connectors/cer_gas_trade.py`, `tests/test_session910.py` (3 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c051/s910/`, `runs/license_reads/s910/`, `runs/s910*`, `warehouse/raw/cer_gas_trade/`.
