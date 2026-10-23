# Session 2149 report: the snow behind the West's dams (NRCS SNOTEL)

23 October 2026, from 23:36 UTC, on lab-desktop (the data machine), a session of `queue/done/092-day-30-october-data-bpa-snowpack-access-outlook-permits.md`. Model spend USD 0. Pulls: 11 requests of 15. Those were wcc.sc.egov.usda.gov's robots address (404, no robots file); www.nrcs.usda.gov's robots file and its policies address (404); two station lists and two data probes from NRCS's AWDB service (one malformed, 400); and the trial's four (the stations' metadata and one a basin). Also 3 to Supabase for the lock.

## Read these first

- **One series table, `nrcs_snotel_swe_daily`:** 86,241 rows, the daily snow water equivalent (NRCS's WTEQ, in inches, Decision 60) at twenty SNOTEL stations, 1 January 2015 to 23 October 2026, no day missing. The stations are the highest of each basin's with a record from before October 2014:
  - above Lake Powell, nine in the Colorado headwaters, the White and Yampa, the Green and the lower Green;
  - on the Columbia, seven in the Kootenai and Pend Oreille, the upper Columbia and the Yakima;
  - in California, four in the Sacramento and San Joaquin.

  They were chosen from NRCS's station list (729 stations in eight states). The service needs no key; one request a basin.
- **Internal until its verdict:** NRCS's policies page was not found (404), and the record has no verdict for NRCS. `sources.csv` says `internal` (the standard's word), and session 2153's licenses round takes NRCS first.
- **The cross-check** (`runs/c092/s2149/cross.py`), each basin's 1 April snow water equivalent (the stations' mean) against the April to September net generation of the Reclamation plant downstream (`usbr_hydropower_monthly`, 2015 to 2025):
  - **California and Shasta:** Pearson 0.72, Spearman 0.76. The drought years 2015, 2021 and 2022 had the least snow and the least generation (1.2, 20.0 and 12.2 inches; 690, 628 and 416 GWh).
  - **The Columbia and Grand Coulee:** Pearson 0.43.
  - **The Colorado and Glen Canyon:** Pearson 0.26. Lake Powell's releases follow the annual operating tables rather than the year's snow, so the weak tie is the river's management, not the data. 2023's big snow (24.7 inches) did give Glen Canyon's best summer (2,191 GWh).
- **Registered:** the sector rule (`power`) and the live set's hold. Not in the release's storage hold or the release package, since the table is internal. License tables: licenses check 0 problems. No row twice. The test: `tests/test_session2149.py` (4 tests).

## Errors

- **A trial ran while another chain held the data lock.** At 23:38 UTC chain 079's session 2133 held it for its `erw_coverage` refresh, with its branch's metadata copied into the main checkout. My command did not wait: it copied the new connector into the main checkout for about a minute and ran it with `--out-dir`. The connector was a new, untracked file, removed at once, and the trial wrote only under `runs/` (a trial updates no metadata). Chain 079's agent was told. Trials now run through `runs/c092/trial.sh`, which waits for the lock. The write after took the lock in turn, and its metadata patch holds only this table's rows.
- **Two requests lost to my addresses:** the probe's list file is CSV, so the commas of the first station list cut it (chain 066's fault, known), and `printf` turned the first data address's `%2C` into spaces (400). Both were asked again.

## Decisions made without you

- **Twenty stations, the highest of each basin,** as the file allowed (at most twenty).
- **The table internal** until NRCS's verdict.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/nrcs_snotel.py`, `tests/test_session2149.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`.
- On the data machine only: `runs/c092/s2149/`, `runs/c092/trial.sh`.
