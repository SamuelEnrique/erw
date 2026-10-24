# Session 2264 report: what the utilities and the hosting industry take in (the Census Bureau's Quarterly Services Survey)

24 October 2026, from 04:40 UTC, on lab-desktop (the data machine), a session of `queue/done/102-day-5-november-data-poland-belgium-new-zealand-columbia.md`, the third source of the session's own choosing. Model spend USD 0.

Pulls: 7 requests of 20:
- the QSS historical data page and the current release's all-tables workbook (six quarters only);
- the economic time series search page (its form is built by script);
- the benchmark datasets page;
- www2.census.gov's robots file, in a call of its own (rules for named crawlers only);
- the 2024 benchmark's read-me and its dataset.

The trial and the write ran offline.

## Why this source

The ERW holds the data center industry's establishments and payroll (`census_cbp_hosting_annual`), its construction (session 2258) and its power demand. It held no measure of the industry's revenue, nor of the utilities' revenue as the Census Bureau measures it. The Quarterly Services Survey gives both every quarter. It is a work of the U.S. government (the Census Bureau's verdict on record).

## Read these first

- **One series table, `census_qss_utilities_hosting_quarterly`:** 784 quarterly figures from the QSS 2024 benchmark dataset, in USD (millions times 1,000,000), each with the coefficient of variation QSS gives:
  - total revenue, adjusted and not, for the utilities (NAICS 22), electric power (2211), natural gas distribution (2212) and water (2213), from 2010;
  - data processing, hosting and related services (518): total revenue from the fourth quarter of 2003, and revenue from businesses, governments and households.
- **What the figures show (whole years, not adjusted):** data processing and hosting revenue rose from 131 billion USD in 2015 to 375 billion in 2024; electric power's from 463 to 579 billion; the utilities' from 575 to 746 billion.
- **The cross-check** (`runs/c102/s2264/cross.py`): each year's not adjusted quarters sum to within 0.5 percent of four times the mean of its adjusted quarters, for every industry but gas distribution (2 percent).
- **Not taken:**
  - percent changes;
  - 121 figures QSS marks S (below publication standards);
  - the quarters after the benchmark's last, the fourth quarter of 2024. They are in the current release's workbook, and a later session can add them, or take the next benchmark.
- **Registered:**
  - the sector rule (`power;gas;datacenters`);
  - both holds;
  - the release package's rows;
  - the license tables (licenses check: 0 problems; release check: 0 differences).

  The test is `tests/test_session2264.py` (3 tests).

## Errors

- **A request spent on the time series search page,** whose options are filled by script.

## Decisions made without you

- **This source chosen,** for the reason above.
- **The benchmark dataset alone,** which reaches the fourth quarter of 2024, rather than piecing quarters from release workbooks.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/census_qss.py`, `tests/test_session2264.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`, `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c102/s2264/`.
