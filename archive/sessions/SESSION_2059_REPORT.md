# Session 2059 report: the hurricanes' tracks (the National Hurricane Center's HURDAT2)

23 October 2026, from 20:08 UTC, on lab-desktop (the data machine), a session of `queue/done/066-day-25-october-data-disasters-loans-drought-assistance.md`. Model spend USD 0. Pulls: 4 requests of 10 (www.nhc.noaa.gov's robots file, asked in a call of its own: it disallows nothing; the `/data/hurdat/` listing; the two basins' latest files through the connector). The write reused the saved files (`--offline`).

## Read these first

- **One table written, validated, archived, in coverage (sectors power, oil and gas), in the release package, both holds:** `nhc_hurdat2_track_points`, 27,812 rows: every six-hourly fix of the 973 cyclones of the Atlantic (`hurdat2-1851-2025-092326.txt`) and the Northeast and North Central Pacific (`hurdat2-nepac-1949-2025-092926.txt`) from the 2000 season to 2025, with the status, position, maximum wind (knots) and minimum pressure (millibars, empty where the file has -999), and the files' record marks: 509 landfalls (`x_landfall` 1).
- **One events table, fixes and landfalls together** (the chain file allowed a series table, or landfall events with the fixes as a series: say which): knots and millibars are not ERW units, so the figures stay in `x_` columns of one events table, a row a fix, and a landfall is a fix marked L. No new unit.
- **Its license:** NOAA's National Weather Service pages are public domain (read 8); `scripts/licenses.py` maps the table to the NWS verdict through its publisher's name: may be public.

## The cross-check

Each Atlantic landfall since 2015 inside a box around the U.S. Gulf and East coasts (24 to 46 N, 98 to 66 W) against session 2056's FEMA Hurricane and Tropical Storm declarations open that day and chain 059's NCEI hurricane and tropical storm events within a day, `runs/c066/s2059/cross.py`: 79 landfall fixes (39 at hurricane strength); 56 with a FEMA declaration open that day (38 of the 39 hurricanes), 72 with NCEI events within a day (37 of the 39; 2025's storms have no NCEI events yet). The box is crude: it reaches the Bahamas, so a few matches are by date only (Melissa's 2025 fix, for one).

## Errors

- None.

## Decisions made without you

- **From the 2000 season,** as the chain asked; the files run from 1851 and 1949.
- **The wind radii columns not taken.**
- **One events table,** above.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/nhc_hurdat2.py`, `tests/test_session2059.py` (3 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c066/s2059/`, `runs/license_reads/s2059/`, `runs/s2059*`, `warehouse/raw/nhc_hurdat2/`.
