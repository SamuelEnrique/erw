# Session 2109 report: California's total system power (the Energy Commission)

23 October 2026, from 21:43 UTC, on lab-desktop (the data machine), a session of `queue/done/069-day-27-october-data-public-lands-sunlight-spending-streams.md`. Model spend USD 0. Pulls: www.energy.ca.gov, 4 requests of 15 (the robots file in a call of its own, the 2024 page, the download page `/media/7311`, the workbook), and 3 to Supabase for the lock.

## Read these first

- **One series table, `cec_total_system_generation_annual`:** 795 rows, 47 series, 2009 to 2025, from the Commission's workbook "Total System Electric Generation 2009 to 2025 with totals" (posted October 2026; the Energy Almanac's latest page is still 2024's). It gives in-state generation by fuel (`in_state_generation`), imports from the Northwest and the Southwest by fuel (`imports`), and the total system by fuel (`total_system_power`), in MWh from the Commission's GWh. The workbook's address is read from the download page.
- **Checked as read:** each region's fuels sum to its total row, the two import regions to Total Imports, each fuel of the Total block to the three regions' (oil and other combined, as the Commission combines them), and the Total block to the Grand Total, all within 1 GWh. The total rows are not kept. Four cells have no row: three dashes and one blank, all in 2025 (Northwest oil and other, Southwest oil and other).
- **The cross-check** (`runs/c069/s2109/cross.py`), in-state generation against EIA's California net generation summed to the year (`eia_state_generation_monthly`, all sectors, full years only): the ratio is 0.985 to 1.012 in every year from 2009 to 2025. In 2025 the fuels match closely: solar 55,528 GWh against EIA's 54,888 (1.012), wind 1.005, gas 1.000, nuclear 1.001, geothermal 1.001, coal 1.042. Neither figure includes EIA's small-scale solar (34,407 GWh in 2025). Imports' share of total system power fell from about 0.33 (2012 to 2015) to 0.22 to 0.23 (2023 to 2025).
- **The license:** the Commission has no verdict of its own in `license_verdicts.csv`. The header names the State of California's conditions of use (read 10, the same notice CARB's verdict rests on), and `sources.csv` records "may be public". The Commission's verdict is for session 2111's round, which takes this chain's publishers first.
- **Registered:** the sector rule (`power`), the live set's hold and the release's storage hold, the release package's rows, the license tables (licenses check 0 problems, release check 0 differences); no row twice. The test: `tests/test_session2109.py` (4 tests).

## Errors

- **Three trials stopped before one ran clean,** each on a part of the workbook the parser had not met: a blank cell (2025, Southwest other), the Total block's empty row, and the note in the second column. Each is now handled in the connector and held by the test.

## Decisions made without you

- **The whole workbook (2009 to 2025),** not the yearly pages, since its totals let every figure be checked.
- **2025 kept as the workbook gives it,** although the Almanac's page for 2025 is not yet published; the header gives the workbook's posting.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/cec_total_system.py`, `tests/test_session2109.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`, `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c069/s2109/`.
