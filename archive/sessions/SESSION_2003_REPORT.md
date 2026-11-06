# Session 2003 report: Reclamation's hydropower (RISE held by its robots file; the plant workbook taken)

23 October 2026, from 15:13 UTC, on lab-desktop (the data machine), a session of `queue/done/056-evening-23-october-data-jobs-reactors-large-loads-hydro.md`. Model spend USD 0. Pulls: 11 requests of 15 (data.usbr.gov's robots file, asked in a call of its own and read first; its sitemap index and sitemap; a catalog record and a catalog item; www.usbr.gov's robots file, read first for that host; the Reports and Data page; the "10 year monthly generation by facility" workbook, HTTP 404; the plant workbook; the trial's page and workbook). The write, at 16:28 UTC when the lock was free, reused the saved files.

## Read these first

- **RISE serves its data only under paths its robots file disallows:** data.usbr.gov's file disallows `/rise/api`, `/time-series?`, `/time-series/selection`, `/time-series/output` and the catalog's searches. Its catalog pages (allowed) describe each item but carry no data; "Query Data" leads to the disallowed paths. Nothing was taken from RISE.
- **Reclamation's own plant workbook taken instead,** from www.usbr.gov's Power Resources Office page (robots: only `/pn-bin` and `/gp-bin` disallowed): "Active USBR Facilities, Operated and Maintained by Reclamation, Monthly and Annual Performance Data" (`Plant_Data_11_2025.xlsx`, generated 7 November 2025).
- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `usbr_hydropower_monthly`, 31,702 rows: the 55 plants' installed capacity (MW) and gross generation, plant auxiliary use and net generation (MWh), a month, October 2013 to September 2025 (one row of October 2025), each with Reclamation's region. 932 months of net generation below zero are kept as written. The workbook's annual sheet is a check, not a table: 659 of 660 plant fiscal years equal the sum of their months within 0.1 percent.
- **The cross-checks:** 52 of the 55 plants match a Reclamation-owned plant of `ornl_eha_hydropower_plants` by name, 47 of them within 10 percent of ORNL's capacity; for January to September 2025, 46 of 50 plants are within 5 percent of `eia923_plant_fuel_monthly`'s net generation by EIA plant id (Grand Coulee 12,360,602 and 12,270,940 MWh; Shasta 2,063,176 and 2,063,178). Hoover differs (2,313,685 against 1,603,965): EIA reports its Arizona and Nevada plants apart.
- **The license:** Reclamation's Disclaimer page defers to the Department of the Interior's notice; session 2005 recorded the verdict "may be public".

## Errors

- **The metadata patch conflicted with session 2001's lines and brought main's stale `usgs_mcs_critical_minerals` row back** (692 rows, "blocked", from before chain 055 lands), next to this table's in alphabetical order; `runs/union_resolve.py` kept both sides. The stale rows were removed from `coverage.csv`, `archive_manifest.csv` and `docs/coverage.md`, and the license record and release check run again (0 problems). A table written next to a row main holds stale must be looked for twice after every resolve, as session 983 said.

## Decisions made without you

- **The plant workbook in place of RISE:** the chain asked for "monthly generation where RISE gives it as a catalogued item"; RISE gives it only through disallowed paths, and the Power Resources Office publishes the same plants' generation as a file.
- **No state:** the workbook names no state, and none is inferred from the plant's name.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/usbr_power.py`, `tests/test_session2003.py` (4 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c056/s2003/`, `runs/license_reads/s2003/`, `runs/s2003*`, `warehouse/raw/usbr_power/`.
