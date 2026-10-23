# Session 882 report: each utility's operations (EIA-861 Operational_Data)

23 October 2026, from 04:29 UTC, on lab-desktop (the data machine), a session of `queue/done/048-night-23-october-data-utility-files-products.md`. Model spend USD 0. Pulls: none (the saved EIA-861 zips).

## Read these first

- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `eia861_operational_data`, 367,768 rows, 3,556 utilities, 2015 to 2025, from `Operational_Data_<year>.xlsx`, by utility and state: summer and winter peak demand (MW); the sources of energy (net generation, wholesale purchases, exchanges and wheeling received, delivered and net, losses of transmission by others, total, MWh); its dispositions (retail sales, sales for resale, furnished and consumed without charge, losses, total, MWh); its revenue by kind (retail sales, delivery customers, sales for resale, credits, transmission, other, total, USD). Ownership, NERC region and EIA's observed or imputed flag on every row.
- **The cross-check, against `eia861_utility_sales`:** each utility's retail sales here equal its total sales there (bundled and energy-only service, delivery-only left out, as EIA counts a sale once) within 0.1 percent in 20,794 of 20,801 utility-years, within 5 percent in 20,799; all utilities: 3,717.6 TWh in 2015 in both tables, 3,610.9 in 2020 in both, 3,931.7 against 3,931.8 in 2025. Within each record, total sources equal total disposition in 22,594 of 22,596.
- **Utilities a year:** about 2,290 from 2015 to 2018, 3,360 in 2019, about 1,715 from 2020: EIA moved the small utilities to the short form from 2020 (as session 881 found for efficiency); `eia861_short_form` holds their sales.
- No record had two values under one key; every row is EIA's "O", observed.

## Decisions made without you

- "Retail Sales" (to 2024) and "Sales to Ultimate Customers" (2025) read as one variable, `retail_sales`; each column is found by its group and its own heading, so "Sales for Resale" (MWh) and "From Sales for Resale" (USD) cannot be confused.
- The key is utility and state, as EIA gives one row each; the Short Form column of 2019 on read past, as session 868 read it past.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia861_operations.py`, `tests/test_session882.py` (5 tests), this report. Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`. On the data machine only: `runs/c048/`, `runs/s882*`.
