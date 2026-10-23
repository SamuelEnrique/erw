# Session 2071 report: Alberta's market (the AESO's Historical Pool Price report)

23 October 2026, from 20:08 UTC, on lab-desktop (the data machine), the second session of `queue/done/067-day-25-october-data-neighbours-emitters-disasters-world-oil.md`. Model spend USD 0. Pulls: 6 requests of 15 (ets.aeso.ca's and www.aeso.ca's robots files, each in a call of its own, both HTTP 404; the Historical Pool Price report for 2025 and for 31 December 2025 to 23 October 2026, as CSV; the annual market statistics page and the 2025 statistics PDF). The trial and the write reused the two saved reports (`--offline`).

## Read these first

- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `aeso_alberta_load_hourly`, 15,853 rows: Alberta internal load (AIL) in MW, an hour, from 1 January 2025 (07:00 UTC, Alberta's midnight) to 23 October 2026, continuous.
- **The pool price is not taken,** for want of a Canadian dollar unit (the standing question, as in session 2070); the saved reports hold it.
- **Alberta's hours:** the report gives an hour ending in local time with daylight saving: the spring day has 23 lines (no "02") and the autumn day 25 ("02" then "02*"). Each hour is placed by its order within its local day, from the day's local midnight in UTC; a day whose hours are not the AESO's 23, 24 or 25 in order stops the run (only the report's last day may stop short, its future hours written "-").
- **The AESO's verdict stands** (read 46): may be public for non-commercial and educational use, unmodified, with its copyright notices; a commercial use needs its written permission. The table's flag is public. (Session 2079's note corrected an earlier line here, which said "as the AESO's other table is": the AESO's other source feeds `large_load_waits`, which is held internal.)

## The cross-check

The table's 2025, Alberta's local year (8,760 hours), against the AESO's 2025 Annual Market Statistics (`runs/c067/s2071/cross.py`): **average AIL 10,316.3 MW (the AESO: 10,316 MW), winter peak 12,785 MW on 11 December at 17:00 MST (the AESO: 12,785 MW, December), summer peak 12,005 MW (the AESO: 12,005 MW).** All three agree.

## Errors

- **The first trial stopped on an hour given twice:** it read an hour ending h as starting at local h-1, which on the spring day put "03" on the same UTC hour as "04". Hours are now placed by their order within the day, and a test covers the spring and autumn days.
- **The test's first expectation for the autumn day was an hour late** (the day's midnight is still daylight time, 06:00 UTC); the test was corrected, not the code.

## Decisions made without you

- **Load only, the price left for a `CAD` unit.**
- **Two requests a run** (last year, then this year to tomorrow): the report is asked a year at a time at most, its end date not included.

## For Samuel's ruling

- None new (the `CAD` unit, session 2070).

## Files

- New: `warehouse/connectors/aeso_load.py`, `tests/test_session2071.py` (3 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_reads.csv` (199, 200), `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c067/s2071/`, `runs/license_reads/s2071/`, `runs/s2071*`, `warehouse/raw/aeso_load/`.
