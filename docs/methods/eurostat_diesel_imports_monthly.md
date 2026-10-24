# Eurostat's monthly gas oil and diesel imports by country of origin: 35 European countries and the EU, 173 partners, January 2016 to September 2026 (nrg_ti_oilm, gas/diesel oil)

Energy Research Warehouse (ERW), method note written in session 2471 (chain 119) for a table first written on 24 October 2026 (session 2474 of chain 119, `archive/sessions/SESSION_2474_REPORT.md`). It is built as the crude oil imports by partner are (`docs/methods/eurostat_crude_imports_monthly.md`), from the same data set and flow, another product; Eurostat's terms and country lists are described in `docs/methods/eurostat_renewable_capacity_annual.md` (session 2129). Its companion on the export side is `docs/methods/eurostat_gasoline_exports_monthly.md`.

Tables: `eurostat_diesel_imports_monthly`

## Publisher and address

Eurostat (Statistical Office of the European Union), "Oil and petroleum products imports - monthly data" (`nrg_ti_oilm`), through the statistics API without a key, as JSON-stat 2.0, filtered to gas/diesel oil without its biofuel portion (SIEC `O4671XR5220B`):

- `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_ti_oilm?format=JSON&lang=EN&siec=O4671XR5220B&sinceTimePeriod=2016-01`

The first answer (session 2474, 13:47 UTC) was HTTP 413, "ASYNCHRONOUS_RESPONSE"; the same address asked again by `runs/c119/s2474/retry.py` answered with the data, 8,604,507 bytes, saved as `warehouse/raw/eurostat_diesel_imports_monthly/nrg_ti_oilm_diesel.json` (also `runs/license_reads/s2474/03_nrg_ti_oilm_diesel.json`). Source id `eurostat:nrg_ti_oilm_diesel` (`sources.csv`: license public). ec.europa.eu's robots file, read again in that session, disallows the old `/eurostat/SDMX/diss-web/rest/` path and the search pages, not `/eurostat/api/dissemination/`, and names no AI agent.

Connector: `warehouse/connectors/eurostat_diesel_imports.py`, made from the crude oil imports connector by `runs/c119/s2474/make_connector.py` (the docstring and the product, names and addresses replaced, each replacement checked). Ceiling and stops as the crude oil connector's: the address asked at most 10 times a minute apart; a product other than `O4671XR5220B`, a unit other than THS_T, a frequency not monthly, a value not a number or a key given twice stops the run.

## Schedule and records

Schedule: none. Records: `runs/status/eurostat_diesel_imports_monthly.json`; `archive_manifest.csv` (569,595 rows, run `20261024T135736Z-local`); `coverage.csv` (sector oil, validator pass, public); the release package's held list and its rows; the live set's `catalogue_hold`. Not in the Stanford draft: written after session 2471's upload. Readers: none. `tests/test_session2474.py` (3 tests) tests the connector on JSON-stat built in the test.

## Shape and variables

Series, 569,595 rows, 17 columns (as the crude oil table's), 10 header lines.
- **`entity`:** `eurostat_diesel_imp:<Eurostat geo code>:<partner code>`; `variable` `imports`; `unit` t (thousand tonnes times 1,000); `freq` P1M; January 2016 to September 2026.
- **Areas:** 35 importing countries and EU27_2020 and EA21 (geo blank). The United Kingdom is left out by Eurostat's terms.
- **Partners:** 173, the aggregates named in header line 3 from the answer.
- **Values:** 529,264 rows are zero, as published. Eurostat flags 1,332 "p" (provisional). 18 values are negative, all against `NSP` (not specified), kept as published.
- **The EU's rows end in June 2026;** the countries' run to September.
- **Partner `NA` is Namibia:** read with `keep_default_na=False`.

## Checks

Counted in sessions 2474 and 2471 from the table:
- **Against the oil balance:** imports from all partners equal `eurostat_oil_monthly`'s gas/diesel oil imports (`flow:IMP`) to the tonne in 4,149 of 4,312 country-months, and within 1 percent in 4,281.
- **The EU's imports,** Mt a year:

  | Origin | 2016 | 2019 | 2021 | 2022 | 2023 | 2024 | 2025 |
  |---|---|---|---|---|---|---|---|
  | United States | 8.7 | 5.3 | 1.1 | 1.8 | 5.2 | 8.7 | 5.9 |
  | Russia | 20.2 | 20.7 | 21.8 | 20.2 | 1.7 | 0.1 | 0.0 |
  | Saudi Arabia | 6.1 | 9.3 | 6.4 | 7.2 | 7.5 | 8.5 | 9.0 |
  | India | 4.3 | 3.6 | 2.2 | 2.7 | 6.6 | 6.1 | 3.3 |

  Russia's fall follows the EU's embargo on Russian oil products from February 2023.

## What it cannot say

- **Gas/diesel oil only:** the other products of `nrg_ti_oilm` are not read here (crude oil is `eurostat_crude_imports_monthly`).
- **The latest months:** the EU's rows end in June 2026, and a country's latest months may be revised.
- **How Eurostat assigns the country of origin** is not read here; its metadata page for `nrg_ti_oilm` would say.
