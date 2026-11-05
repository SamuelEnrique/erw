# Session 520 report: EIA-861M's back years

21 October 2026, from 20:26 UTC, on lab-desktop (the data machine), the fifth session of `queue/done/027-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **`eia861m_utility_sales_monthly` now runs from January 2017 to July 2026**: 1,145,088 rows, 371 utilities. Session 511 held 2025 and 2026 only.
- **The reader**: EIA names its 2017 to 2020 files `retail_sales_<year>.xlsx` and later ones `sales_ult_cust_<year>.xlsx`. `file_urls` finds both. Every year's sheets have the same headings, and the reader, which finds columns by heading, read them all without a change. The ceiling is now the page and ten years (11).
- **Cross-check, every year, against `eia861_utility_sales`** (`runs/s520/crosscheck.py` on the data machine): each utility-state's twelve months, summed, against the annual total sales.

  | Year | Utility-states | Median | Within 2% | Over 10% apart |
  |---|---|---|---|---|
  | 2017 | 560 | 1.0000 | 82.0% | 12.5% |
  | 2020 | 590 | 1.0000 | 79.2% | 13.9% |
  | 2023 | 583 | 1.0000 | 85.8% | 11.0% |
  | 2024 | 607 | 1.0000 | 77.3% | 18.1% |
  | 2025 | 600 | 1.0000 | 81.2% | 13.3% |

  Every year has the same shape: most agree exactly, and a tenth or more are over 10% apart. Session 521 reads why.
- **Written under the data lock** (20:27 UTC) with `--offline`, from the trial's saved page and files (0 requests). The validator, coverage and archive exited 0 (964,927 new rows archived; 2025 and 2026 were already there).
- **The release package's row for the table** (row count, first and last month) was replaced from a fresh regeneration; its variables are unchanged. The table stays held from `/data` and Redivis v1 until uploaded.
- Tests: `tests/test_session520.py`, 3.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.eia.gov | 9 of 10 | the page; the files of 2017 to 2024 (2025 and 2026 reused from session 511) |

## Files

- New: `tests/test_session520.py`, this report. Changed: `warehouse/connectors/eia861m_sales.py`, `docs/redivis/release-v1/tables.csv`, `docs/coverage.md`, `docs/licenses.md`, `warehouse/metadata/{coverage,archive_manifest,sources,license_tables}.csv`.
