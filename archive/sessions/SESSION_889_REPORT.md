# Session 889 report: a source the ERW did not hold: the Federal Reserve's output and capacity utilization of utilities

23 October 2026, from 05:12 UTC, on lab-desktop (the data machine), a session of `queue/done/048-night-23-october-data-utility-files-products.md`. Model spend USD 0. Pulls: 10 requests of 20 (five to the Census Bureau, five to the Federal Reserve).

## Read these first

- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `frb_utility_output_monthly`, 15,365 rows, 19 series, to September 2026, from the Federal Reserve's G.17 release (Industrial Production and Capacity Utilization), seasonally adjusted:
  - the output of electric and gas utilities: electric power; its generation by fossil fuel, nuclear, hydroelectric, and renewables and other; transmission and distribution; residential, commercial and other, and industrial electricity sales; gas distribution and its sales;
  - for comparison, all industrial production and energy in total;
  - the capacity utilization of the utilities (percent).
- **Why this source:** it is the only monthly federal measure of the power sector's output by kind of sale, revised with each release and published to September, a month ahead of EIA's.
- **Decision 53: the unit `index`**, an index number on its source's base period (G.17: 2017 = 100), added to the validator and the data standard together. An index is never summed.
- **The cross-check, against EIA's retail sales (`eia_retail_sales_monthly`), growth from 2017:**
  - Residential: 1.102 against 1.099 in 2025, 1.062 against 1.062 in 2020.
  - Industrial: 1.066 against 1.059 in 2025.
  - Commercial: apart. The Board's "commercial and other sales" grew 21.7 percent from 2017 to 2025, EIA's commercial sales 10.4 percent, so the Board's category is wider.
  - The generation index (value added) runs below EIA's net generation in 2024 and 2025 (1.038 against 1.097 in 2025).
  - The utilities' capacity utilization was 73.0 percent in September 2026, against 77.5 in 2017.
- **Census Bureau, tried first and left:**
  - api.census.gov answered "Request Rejected" to its robots file, so its API was not asked.
  - www.census.gov has no robots file (HTTP 404); its construction spending page read; the private construction history file answered HTTP 500.
  - The release workbook holds only the latest months (power construction, private, USD 165.9 billion a year in August 2026, seasonally adjusted).
  - A table of a few months was not written.

## Decisions made without you

- The G.17 text files (the whole release) rather than the Board's data download, which needs a series package built on its pages.
- Only the utilities' series (NAICS 2211 and 2212) and two totals for comparison.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/frb_utility_output.py`, `tests/test_session889.py` (3 tests), this report.
- Changed: `warehouse/validate/erw_validate.py` and `docs/datastandard.md` (Decision 53); `build_coverage.py`, `release_v1.py`, `live_set.yaml`; `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`; `license_tables.csv`, `docs/licenses.md`; `docs/redivis/release-v1/`.
- On the data machine only: `runs/c048/s889/`, `runs/license_reads/s889/`.
