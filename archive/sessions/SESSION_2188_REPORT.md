# Session 2188 report: the Department of Energy's budget and obligations (USAspending.gov)

24 October 2026, from 02:28 UTC, on lab-desktop (the data machine), a session of `queue/done/097-day-1-november-data-canada-offshore-inspections-supply.md`, the third source of the session's own choosing, run beside session 2185. Model spend USD 0. Pulls: 17 requests of 20:
- api.usaspending.gov's robots address (HTTP 404) and www.usaspending.gov's robots file, each in a call of its own;
- three probes (DOE's budgetary resources, its fiscal 2025 award categories, the toptier agencies list);
- the API's landing page;
- the trial's 11 live requests.

The write ran offline. Also Supabase, for the locks and the archive.

## Why this source

The ERW held no record of the federal money behind DOE's programmes. Its grant and loan programmes grew under the infrastructure law and the Inflation Reduction Act, and the 2025 and 2026 figures show how that money moves. USAspending.gov is the federal record of it. No chain had taken it, and no note named it.

## Read these first

- **One series table, `usaspending_doe_obligations`:** 163 figures, fiscal years 2017 to 2026:
  - DOE's budgetary resources, obligations and outlays a year;
  - its obligations to date at each reporting period (monthly from fiscal 2022, quarterly before);
  - its award obligations by category (contracts, grants, loans, direct payments, IDVs, other).
- **The checks pass:** each year's last obligations-to-date figure equals its obligated total, and the award categories are 77 to 89 percent of the year's obligations (the rest is outside awards).
- **What the figures show:**
  - Budgetary resources stood at 49 to 61 billion USD a year to fiscal 2021, then 130 billion in fiscal 2022 and 141 to 153 billion since.
  - Obligations rose from 41.6 to 98.5 billion (fiscal 2025).
  - **Grants rose from about 3 billion a year to 28.8 billion in fiscal 2025, and stand at 2.6 billion in fiscal 2026 to August.**
- **License: internal.** USAspending is the Treasury's Bureau of the Fiscal Service, and the Treasury's terms are the standing question already put for `treasury_1603_awards` (chain 069). The API's landing page states no terms (read 365), so no verdict is added and the table stays internal until the ruling. It is not in the release package.
- **Not taken:** obligations by state. They need a POST to USAspending's search API, and the ERW's fetch helper asks by GET only.
- **Registered and recorded:**
  - the sector rule (`power;deals`) and the live-set hold;
  - reads 362 to 365;
  - `tests/test_session205.py`'s bound raised by 20 (324 later reads against 342);
  - the license tables (licenses check: 0 problems);
  - a method note (`docs/methods/usaspending_doe_obligations.md`) and its Method cell;
  - the package's and the site's records rebuilt (453 tables, 0 differences).

  No row is given twice. The test is `tests/test_session2188.py` (5 tests).

## Errors

- **Two saved probe answers were seeded into the raw store, then asked again,** since the trial ran live and the connector asks each address fresh. That is two requests more than needed, counted above.

## Decisions made without you

- **This source chosen,** for the reason above.
- **The table internal,** under the standing Treasury question.

## For Samuel's ruling

- **The Treasury's terms** (the standing question from `treasury_1603_awards`) now cover `usaspending_doe_obligations` too. Should a federal work under 17 U.S.C. 105 with no stated terms be public?

## Files

- New: `warehouse/connectors/usaspending_doe.py`, `tests/test_session2188.py`, `docs/methods/usaspending_doe_obligations.md`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py` and `warehouse/supabase/live_set.yaml`;
  - `docs/coverage.md`, `coverage.csv`, `sources.csv` and `archive_manifest.csv`;
  - `license_reads.csv`, `license_tables.csv` and `docs/licenses.md`;
  - `tests/test_session205.py`;
  - `package/src/erw/data/tables.csv`.
- On the data machine only: `runs/c097/s2188/`.
