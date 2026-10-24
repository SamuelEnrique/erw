# Session 2177 report: the incidents on the offshore platforms (BSEE)

24 October 2026, from 00:54 UTC, on lab-desktop (the data machine), a session of `queue/done/097-day-1-november-data-canada-offshore-inspections-supply.md`. Model spend USD 0. Pulls: www.bsee.gov, 13 requests of 15: its robots file in a call of its own, the incident statistics page, the 2024 workbook as a probe, two live trials that stopped early (the page, 2017's and 2018's workbooks), and 2020 to 2023 fetched once. The later trials and the write ran offline. Also Supabase for the locks.

## Read these first

- **One events table, `bsee_offshore_incidents`:** 4,818 incidents reported on the Outer Continental Shelf in calendar years 2018 and 2020 to 2024, from BSEE's workbooks "for public use" (marked "Public Access Level: Public"), their addresses read from the statistics page. Each row is one incident, with:
  - date, operator, region, district, area, block, lease (`entity_ids`), water depth, structure and rig;
  - fatalities and injuries (operator and contractor, every injury class, summed);
  - Y or N flags for fire, explosion, loss of well control (any of four kinds), collision, lifting and gas release;
  - BSEE's own summary.
- **Not taken:** 2019, which the page links no workbook for; 2017's workbook, which holds its fourth quarter only; and the fiscal-year files before it, which are in another form.
- **The workbooks differ by year, each difference read and handled:**
  - 2018 has no serial numbers: its ids are `h` and a hash of the incident's date, time, operator, area, block, lease and summary.
  - 2018 brackets its column descriptions and has one fatalities column; the names are normalised.
  - 2018 has no totals line and a long note in its date column, which now ends the sheet.
  - 2020 calls the summary "Redacted Incident Summary".
  - **Each Y/N count and count sum is checked against BSEE's totals line** in 2022, 2023 and 2024, and all agree. 2018, 2020 and 2021 have no totals line to check.
- **The cross-check** (`runs/c097/s2177/cross.py`), the incidents beside the Gulf's oil production from BOEM's leases (`boem_ogor_lease_production_monthly`, kbbl):
  - Incidents rose from 503 (2018) to 1,042 (2024) while oil stayed near 610 to 680 million barrels a year, so incidents per 100 million barrels roughly doubled (78 to 159).
  - Fatalities ran from 0 to 8 a year (19 in all); injuries 1,117; fires 716.
  - 90 percent of the 683 leases the incidents name are among BOEM's production leases.
  - BSEE's region is "Gulf of Mexico" to 2023 and "Gulf of America" in 2024, kept as written.
- **Registered:** the sector rule (`oil;gas`), both holds, the release package's rows, the license tables (licenses check 0 problems, release check 0 differences); no row twice. BSEE's verdict, the Interior's notice (read 159) as for BLM and ONRR, goes in session 2181's round. The test: `tests/test_session2177.py` (5 tests).

## Errors

- **Two live trials stopped on forms the parser had not met** (2017's quarter-only sheet, then 2018's columns), costing four requests. 2020 to 2023 were then fetched once and every later trial ran offline.
- **The seeding script keeps one directory a session,** so seeding 2024 alone replaced the manifest of 2020 to 2023; all five were seeded together after.
- **My cross-check first read BOEM's oil in the wrong unit** (kbbl taken as barrels); corrected before the figures above.
- **The data lock was held by other chains** for about five minutes at a time; the trials and the write waited.

## Decisions made without you

- **2018 kept with hash ids,** since its incidents are real and complete; the header says which years carry BSEE's serial.
- **2019 and 2017 not taken** for the reasons above.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/bsee_incidents.py`, `tests/test_session2177.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`, `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c097/s2177/`.
