# Session 867 report: each utility's regions and markets (EIA-861 Utility_Data)

23 October 2026, from 03:02 UTC, on lab-desktop (the data machine), the first session of `queue/done/047-night-23-october-data-utilities-plants.md`. Model spend USD 0. Pulls: none (the saved EIA-861 zips).

## Read these first

- **Chain 048 written and pushed first** (`queue/next/048-night-23-october-data-utility-files-products.md`, sessions 881 to 894, `19a17541`, 03:03 UTC), as chain 045's rule asks; snapshots before and after, 0 differences (Vercel rate-limited the deployment).
- **`eia861_utility_data` is written: 22,716 rows, 3,542 utilities, 2015 to 2025**: each utility's NERC region, the other NERC regions and the RTOs it operates in, and its activities (generation, transmission, distribution, marketing and the rest), every flag as EIA gives it (Y, N or empty), and `x_rtos`, the RTOs marked Y. Validated, archived, in coverage (sector power, public), in the release package, both holds.
- **What EIA's file is:** one row a utility a year, under one state, though a utility may sell in several (the sales table has a row for each state). EIA names a NERC region and an RTO both "SPP"; the group heading above tells them apart. EIA's aggregates 88888 (Withheld) and 99999 are left out, as the sales connector leaves them; 10 rows EIA gives with no state have `geo` `US`.
- **The cross-checks:** by utility and year, 99.0 percent of `eia861_utility_sales`' utilities are here (by utility, state and year only 62 percent, since EIA lists one state); the ERCOT flag falls on Texas in 1,382 rows (the rest are retail marketers registered elsewhere), CAISO's on California in 722.

## Decisions made without you

- One column a flag, as EIA gives it, rather than lists alone, so that N and an empty cell stay apart; `x_rtos` added for reading.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia861_utility_data.py`, `tests/test_session867.py` (3 tests), this report. Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`; `queue/next/048-*.md` (on main). On the data machine only: `runs/c047/s867/`, `runs/s867_*`.
