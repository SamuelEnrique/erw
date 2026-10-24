# Session 2155 report: EV charging by state (a source of the session's choosing)

24 October 2026, from 23:59 UTC on the 23rd, on lab-desktop (the data machine), a session of `queue/done/092-day-30-october-data-bpa-snowpack-access-outlook-permits.md`. Model spend USD 0. Pulls: afdc.energy.gov, 9 requests of 20: its robots file in a call of its own (no rule), the station counts by state page, the historical workbook, and three trials of two each (the page and the workbook, asked again since AFDC adds a year at the same address). Also Supabase for the locks.

## Read these first

- **Why this source:** public charging is a new and fast-growing load on the grid, and the ERW held AFDC's EV registrations (`afdc_vehicle_registrations_annual`) but not the chargers. No chain had planned it.
- **One series table, `afdc_ev_charging_state_annual`:** 3,060 rows, the 50 states and DC, 2014 to 2025, from AFDC's workbook of historical station counts (`/files/docs/historical-station-counts.xlsx`, its address read from the station counts page). It holds the public and private (non-residential) EV charging stations and their ports, and Level 1, Level 2 and DC fast ports, near the end of December each year. Other fuels are not taken; the years before 2014 have no EV detail.
- **AFDC's notes, in the header:** legacy chargers are included and residential charging is not; counts are openings net of closures. In 2021 NREL moved to the OCPI hierarchy, so from then an outlet is a port (vehicles that can charge at once), where before it was a connector, and 2021's jump is partly the new counting.
- **Checked as read:** the states and DC sum to each year's Total row in every column. A state's three levels do not always sum to its ports, as AFDC prints them: one to four states a year, mostly California, Connecticut and Michigan by a few ports, and Georgia in 2016, whose levels exceed its ports (2,892 against 1,493). Both are kept and the header lists each.
- **The cross-check** (`runs/c092/s2155/cross.py`), ports against registered EVs by state (`afdc_vehicle_registrations_annual`), 510 state-years from 2016 to 2025: Pearson 0.96. Nationally, EVs a port rose from 6.3 (2016) to 21.0 (2025), and DC fast ports from 1,494 (2014) to 68,599 (2025). New York has the fewest EVs a port among the largest states (10.3), New Jersey the most (33.5).
- **Registered:** the sector rule (`power`), both holds, the release package's rows, the license tables (DOE, read 54, as for the registrations; the publisher named as in that table's source row so the verdict applies); no row twice. The test: `tests/test_session2155.py` (4 tests).

## Errors

- **The first trial stopped** on Montana's 2014 levels (8 of 10 ports). The rule now keeps unequal levels as printed and lists them, since AFDC's own totals agree with the states'.
- **The publisher's name** first differed from the registrations' source row (`U.S. Department of Energy (DOE)`), which would have left the verdict unmatched; corrected before the write.

## Decisions made without you

- **AFDC's chargers as this session's source,** said above.
- **Unequal levels kept as printed,** not corrected or dropped.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/afdc_ev_charging.py`, `tests/test_session2155.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`, `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c092/s2155/`.
