# Session 2154 report: the new homes that add load (the Census Bureau's building permits)

23 October 2026, from 23:53 UTC, on lab-desktop (the data machine), a session of `queue/done/092-day-30-october-data-bpa-snowpack-access-outlook-permits.md`. Model spend USD 0. Pulls: www2.census.gov, 13 requests of 15: its robots file in a call of its own (it names only some crawlers, none of them every reader), the state directory's listing, and the annual files 2015 to 2025 (2024's first as a probe). Also Supabase for the locks.

## Read these first

- **One series table, `census_bps_state_annual`:** 6,984 rows, 2015 to 2025, from the Building Permits Survey's annual state files (`/econ/bps/State/st<year>a.txt`). It covers 54 areas: the states, DC, Puerto Rico, the Virgin Islands and, from 2025, American Samoa. For each of four structure types (1 unit, 2 units, 3 and 4, 5 or more) it holds buildings, units (count) and value (USD, the Bureau's thousands times 1,000). These are the Bureau's estimates, which impute for permit offices that did not report, not its reported-only columns.
- **Years, not months:** the monthly files are one a month (about 140 from 2015), past the session's ceiling of 15, and the 2026 year-to-date file is not mixed into a yearly series. The file asked for months; a later session with a larger ceiling can add them.
- **Checked as read:** the states and DC sum to the United States row in every count and year, and in value within the Bureau's rounding (at most 5 thousand dollars in a year; the check allows 10). Areas are matched by the Bureau's names, since its codes changed: Puerto Rico is 43 and the Virgin Islands 52 in the 2015 file, 72 and 78 later. The file's own code is kept in `x_code`. The regions, divisions and nation are checked and not kept.
- **The cross-check** (`runs/c092/s2154/cross.py`), each state's permitted units against the next year's growth of its residential electricity customers (`eia861_utility_sales`), 510 state-years from 2015 to 2024:
  - Pearson 0.48 across state-years and 0.63 over each state's total.
  - About one new customer a permitted unit where most growth is: Texas 1.14, Florida 1.05, North Carolina 0.94, Georgia 0.98, Arizona 1.12.
  - California's 5.95 likely reflects EIA-861 counting a choice customer under both energy-only and delivery-only service as community choice aggregation grew; session 2108 met the same question in Ohio and Illinois. This check does not test that cause.

  The nation's permits peaked at 1,737,150 units in 2021.
- **Registered:** the sector rule (`power`), both holds, the release package's rows, the license tables (the Census Bureau, read 17; licenses check 0 problems, release check 0 differences); no row twice. The test: `tests/test_session2154.py` (3 tests).

## Errors

- **Three trials stopped before one ran clean,** each on something the files hold that the first parser did not expect:
  - 2015's older territory codes, now matched by name;
  - the values' rounding against the nation's row, now within 10 thousand dollars, counts still exact;
  - American Samoa, new in 2025, now in the map.

## Decisions made without you

- **Years, from the annual files,** within the ceiling; months left for a later session.
- **The estimates, not the reported-only columns.**

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/census_bps.py`, `tests/test_session2154.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`, `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c092/s2154/`.
