# Session 2369 report: Europe's crude oil imports by country of origin (Eurostat), a third source of the session's own choosing

24 October 2026, from 09:37 UTC, on lab-desktop (the data machine), a session of `queue/done/110-day-12-november-data-pakistan-bangladesh-morocco-kazakhstan.md`. Model spend USD 0.

Pulls: 5 requests of 20:
- ec.europa.eu's robots file;
- nrg_ti_oilm whole (HTTP 413: 29.8 million rows, over the 5 million allowed);
- the crude oil query on the statistics API (HTTP 413, asked to try again later);
- the same query twice more. The first answer was not saved because my script's check was wrong; the second was saved.

The trial and the write ran offline.

## Read these first

- **Why:** Eurostat's monthly oil imports by partner, crude oil only, shows where Europe's crude comes from, the United States among the origins. It sits beside the monthly oil balance (session 2363) and the gas imports by partner the ERW holds. No chain took it.
- **One series table, `eurostat_crude_imports_monthly`:** 565,941 figures, public.
  - **Coverage:** January 2016 to September 2026, 35 importing countries and Eurostat's EU27 and euro area rows.
  - **Partners:** 173, Eurostat's aggregates among them (total, the EU, extra-EU, regions), so a sum over partners double counts; the header says so.
  - **Unit:** `t` (thousand tonnes times 1,000).
  - **Left out:** the United Kingdom, by Eurostat's terms.
- **How the data come:**
  - The whole data set is too large for one extract, so the query is filtered by name (`siec=O4100_TOT`) on Eurostat's statistics API, as JSON-stat.
  - Even that is answered asynchronously, so the connector asks the same address again, a minute apart, at most 10 times.
- **Namibia's partner code is `NA`.** A reader that turns "NA" into a missing value (pandas by default) loses it; the header says so.
- **The checks:**
  - **Against the oil balance:** imports from all partners ("TOTAL") equal `eurostat_oil_monthly`'s crude oil imports in 4,161 of 4,196 country-months to the tonne, and in 4,185 within 1 percent.
  - **The EU's crude from the United States, Mt a year:** 2.8 (2016), 12.0 (2018), 35.7 (2020), 49.3 (2022), 67.3 (2023), 69.6 (2024), 60.0 (2025).
- **Registered:**
  - the sector rule (`oil`), the live-set hold;
  - the release package's held list and its rows (the release check passes);
  - the license tables (licenses check: 510 tables, 0 problems; flag and verdict agree, public);
  - the test, `tests/test_session2369.py` (3 tests).
- **Not in the Stanford draft:** the next draft session uploads it (the release note says so).

## Errors

- **The first saved retry was lost:** my script looked for `"id"` in the answer's first 2,000 bytes, where JSON-stat puts the values first. One more request fetched it again.
- **The test's first fixture placed a value at the wrong index;** corrected.
- **The write's metadata patch did not apply** (the main checkout lags main). The table's own rows were put in by `runs/c102/add_own_rows.py` and checked: one row in each file.

## Decisions made without you

- **Crude oil only,** the other products left out, since the whole data set exceeds Eurostat's extraction limit.
- **Every partner kept,** aggregates included, as published.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eurostat_crude_imports.py`, `tests/test_session2369.py`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`;
  - `docs/redivis/release-v1/`;
  - `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`.
- On the data machine only: `runs/c110/s2369/`, `runs/license_reads/s2369/`, `runs/s2369_*`.
