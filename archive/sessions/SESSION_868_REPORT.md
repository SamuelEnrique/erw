# Session 868 report: demand response and dynamic pricing by utility

23 October 2026, from 03:08 UTC, on lab-desktop (the data machine), a session of `queue/done/047-night-23-october-data-utilities-plants.md`. Model spend USD 0. Pulls: none (the saved EIA-861 zips).

## Read these first

- **Two tables written, validated, archived, in coverage (sector power, public), in the release package, both holds:**
  - `eia861_demand_response`: 77,073 rows, 533 utilities, 2015 to 2025: by sector, customers enrolled, energy savings (MWh), potential and actual peak savings (MW), customer incentives and other costs (USD). Actual peak savings, all utilities: 13,053 MW in 2015, 10,387 MW in 2020, 13,396 MW in 2025.
  - `eia861_dynamic_pricing`: 33,157 rows, 907 utilities: customers enrolled by sector, with the kinds of program EIA marks (time of use, real time, variable peak, critical peak pricing and rebate) as Y, N or empty by sector.
- **Read by stacked headings** (group, measure, sector): 2017 adds a balancing authority column and 2019 a short-form column; the 2015 and 2016 dynamic pricing files are named without the underscore. The key carries the balancing authority where EIA gives one.
- **No key, left out:** Wabash Valley Power in Indiana gives two rows with different figures in 2015 and in 2016 (before EIA's BA column); both records are left out whole and named in the header (chain 030's rule). A first write kept the figures on which the two rows agreed; this session's test found it, the connector now drops the whole record, and the table was written again (6 rows fewer; the archive records the 6 keys deleted).
- **The cross-check:** each row's total equals the sum of its sectors in 99.0 to 100 percent of rows (customers enrolled exactly; energy savings, peak savings and incentives where a sector is withheld, about 1 percent apart).

## Decisions made without you

- The demand response file's "DSM Program" flags (grid-connected water heaters) not taken; named in the header.
- One connector for both files, as they share their form.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia861_programs.py`, `tests/test_session868.py` (4 tests), this report. Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`. On the data machine only: `runs/c047/s868/`, `runs/c047/write_pair.sh`, `runs/c047/replace_tables.py`, `runs/s868*`.
