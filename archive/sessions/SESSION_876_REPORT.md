# Session 876 report: EIA-861's short form, the small utilities' sales

23 October 2026, from 03:42 UTC, on lab-desktop (the data machine), a session of `queue/done/047-night-23-october-data-utilities-plants.md` (the second of its two "more sources"). Model spend USD 0. Pulls: none (the saved EIA-861 zips).

## Read these first

- **`eia861_short_form` is written: 44,170 rows, 1,721 utilities, 2015 to 2025 (EIA gives no short-form file for 2019)**: each small utility's total revenue (USD), sales (MWh) and customers as it reported them on Form EIA-861S, with the programs it marks (water heaters, net metering, demand-side management, time-based rates). Validated, archived, in coverage (sector power, public), in the release package, both holds.
- **Why this source:** `eia861_utility_sales` takes observed rows only and leaves out the short-form utilities, which EIA imputes there; none of the short form's utility-state-years is in that table. EIA moved more utilities onto the short form in 2020: the file's sales are 27 to 28 TWh a year to 2018 and 87 to 93 TWh from 2020.
- **The cross-check:** the sales table's observed rows (parts A, B, D) plus the short form reach 99.1 to 99.5 percent of EIA's U.S. retail sales from 2020 (2024: 3,952 of 3,975 TWh), against about 97 percent without the short form.

## Decisions made without you

- A table of its own, not rows added to `eia861_utility_sales` (session 853's rule: a table a page reads is not widened from another file).

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia861_short_form.py`, `tests/test_session876.py` (2 tests), this report. Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`. On the data machine only: `runs/c047/s876/`, `runs/s876*`.
