# Session 904 report: a source the ERW did not hold: the uranium bought by U.S. reactors (EIA's Uranium Marketing Annual)

23 October 2026, from 06:59 UTC, on lab-desktop (the data machine), a session of `queue/done/049-day-23-october-data-margins-schedules-emissions.md`. Model spend USD 0. Pulls: EIA, 6 requests of 20 (the report's page and its five summary workbooks).

## Read these first

- **One table written, validated, archived, in coverage (sector power and uranium, public), in the release package, both holds:** `eia_uranium_marketing_annual`, 763 rows, 2003 to 2025, from the report's summary tables S1a to S3b (Form EIA-858). It holds:
  - the uranium U.S. reactor owners and operators bought, by seller, by origin and by contract type, and its weighted-average price;
  - their feed deliveries, the uranium loaded into reactors, enrichment services bought (U.S. and foreign origin) and their price;
  - foreign purchases and sales and their prices;
  - commercial inventories.
- **Why this source:** the ERW held the nuclear fleet's output and outages but nothing of its fuel. In 2025, owners bought 46.9 million pounds U3O8 equivalent at 58.46 USD/lb on average (spot contracts 75.83); enrichment cost 108.70 USD/SWU. The average price was 44.13 in 2015 and 33.27 in 2020.
- **Decision 55: the units `lb`, `SWU` and `USD/SWU`,** added to the validator and the data standard together.
- **The cross-checks, within EIA's tables:**
  - Enrichment by origin sums to the total in 23 of 23 years, and inventories in 23 of 23.
  - Purchases by origin sum to the total within 0.5 percent in every year where both are given.
  - Spot and long-term contracts together fall short of the total by up to 5.9 percent (2016) and never exceed it; within 0.5 percent in only 9 of 23 years. EIA does not break out the remainder; reported as found.

## Decisions made without you

- **One entity (`eia_uranium:us`)** and a variable for each column, named by its meaning, the heading kept in `node`.
- **The detailed tables (1 to 26: by supplier, origin country, pricing mechanism, contracts, enrichment country, sellers) are not taken:** the summary tables carry the long series; a later session can add them.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia_uranium_marketing.py`, `tests/test_session904.py` (3 tests), this report.
- Changed:
  - `warehouse/validate/erw_validate.py`, `docs/datastandard.md` (Decision 55)
  - `build_coverage.py`, `release_v1.py`, `live_set.yaml`
  - `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`
  - `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`
  - session 903's report (one sentence)
- On the data machine only: `runs/c049/`, `runs/license_reads/s904/`, `runs/s904*`.
