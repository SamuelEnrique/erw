# Cyclones' best-track fixes and landfalls (the National Hurricane Center's HURDAT2)

Energy Research Warehouse (ERW), method note written in session 2066 (chain 066) for a table first written on 23 October 2026 (session 2059).

Tables: `nhc_hurdat2_track_points`

## Publisher and address

NOAA National Weather Service, National Hurricane Center (NHC), HURDAT2, the best track data (`https://www.nhc.noaa.gov/data/#hurdat`), two text files of `https://www.nhc.noaa.gov/data/hurdat/`:

- Atlantic, 1851 to 2025: `hurdat2-1851-2025-092326.txt`
- Northeast and North Central Pacific, 1949 to 2025: `hurdat2-nepac-1949-2025-092926.txt`

Source id `nhc:hurdat2`. Connector: `warehouse/connectors/nhc_hurdat2.py` (session 2059). www.nhc.noaa.gov's robots file (read 222) disallows nothing.

## Vintage and revision

Both files last modified 30 September 2026 (18:37:36 and 18:37:37 UTC), retrieved 23 October 2026 20:09:44 and 20:09:46 UTC and written by run `20261023T202201Z` from the saved files (`--offline`).

The two file names are fixed in the connector (`FILES`), and a file once saved is read from the saved copy on every later run: NHC's next season comes as files of new names, which a session reads from the folder's listing and writes into `FILES`. The table is written whole each time (a snapshot).

## Shape and variables

Events, 27,812 rows, one a fix, of 973 storms of the 2000 to 2025 seasons, 22 May 2000 to 1 November 2025. `event_id` `nhc:<storm id>:<YYYYMMDDHHMM>`, each once; `event_date` the fix's UTC day; `parties` NHC; `entity_ids`, `mw`, `price`, `currency` and `status` empty.

| Basin (`x_basin`) | Storm ids | Storms | Fixes | Landfalls |
|---|---|---|---|---|
| atlantic | AL | 459 | 13,836 | 404 |
| pacific | EP 475, CP 39 | 514 | 13,976 | 105 |
| all | | 973 | 27,812 | 509 |

| `event_type` (HURDAT2 status) | Rows | Maximum wind, kt |
|---|---|---|
| tropical_storm (TS) | 9,720 | 35 to 80 |
| hurricane (HU) | 5,811 | 65 to 185 |
| low (LO) | 5,018 | 10 to 80 |
| tropical_depression (TD) | 4,383 | 15 to 30 |
| extratropical (EX) | 1,834 | 15 to 100 |
| disturbance (DB) | 540 | 15 to 50 |
| subtropical_storm (SS) | 302 | 35 to 60 |
| wave (WV) | 116 | 20 to 40 |
| subtropical_depression (SD) | 88 | 20 to 30 |

| Column | Unit or form |
|---|---|
| x_storm_id, x_storm_name | the storm's ATCF id (basin, number, season) and name as the file writes them (UNNAMED for 37 storms, 365 fixes) |
| x_time_utc | HHMM: 0000, 0600, 1200 or 1800 in 27,310 rows; another hour in 502, each a record the file marks (429 of them landfalls) |
| x_record | the file's record identifier: L 509, I 26, T 13, S 11, P 8, R 8, C 4, W 2, G 1, empty in 27,230 (the docstring names L a landfall, I an intensity peak, P a minimum pressure) |
| x_landfall | 1 where `x_record` is L, else 0 |
| x_lat, x_lon | decimal degrees, north and east positive (latitude 0.4 to 70.7; longitude -180.0 to 179.9, east of 0 in 289 rows: 278 Pacific fixes past the date line and 11 Atlantic fixes east of Greenwich) |
| x_max_wind_kt | knots, multiples of 5, 10 to 185 (Patricia, EP202015, 23 October 2015) |
| x_min_pressure_mb | millibars, 872 to 1,024; empty in 41 Pacific rows where the file writes -999 |

Knots and millibars are not ERW units, so the figures are `x_` columns of an events table (session 2059's decision).

## Reading the files

- The files are read line by line, blank lines passed over. Each storm's header line must begin with an id of two capital letters and six digits and give, in its third field, a number of fix lines, and that many lines must follow; otherwise the run stops.
- A storm whose season (the id's last four digits) is before the start (`--since`, 2000 by default) is left out after its lines are counted.
- A fix line must have at least eight fields, a date of eight digits and a time of four; a status not in the map of nine, a position that does not read as degrees with N, S, E or W, or a wind or pressure that is not a whole number stops the run. A negative wind or pressure is left empty.
- An `event_id` given twice stops the run. The wind radii columns are not taken. Nothing is filled.
- Ceiling: one request a basin's file (two), each tried up to four times, with 2 seconds after each.

## License

May be public: NOAA's National Weather Service pages are in the public domain (read 8, the NWS verdict in `license_verdicts.csv`, which `license_tables.csv` maps to the table through the source registry). The NWS asks that its information not be claimed as one's own, used to imply its endorsement, or modified and presented as official. The table's header: "License: public (NOAA National Weather Service: in the public domain; cite NOAA National Hurricane Center, HURDAT2)."

## Cross-checks (session 2066)

- Session 2059, each Atlantic landfall since 2015 inside a box around the U.S. Gulf and East coasts (24 to 46 N, 98 to 66 W) against FEMA's hurricane and tropical storm declarations open that day and NCEI's hurricane and tropical storm events within a day: 79 landfall fixes, 39 of them at hurricane strength; 56 with a FEMA declaration (38 of the 39), 72 with NCEI events (37 of the 39; 2025's storms have no NCEI events yet). Session 2066 counted the same 79 and 39 from the rows.
- The counts above were computed from the rows, read past the header lines. Read again from the saved files, the Atlantic file holds 1,988 storms, 459 of them from the 2000 season with 13,836 fix lines, and the Pacific file 1,262, 514 of them with 13,976: 459 + 514 = 973 storms and 13,836 + 13,976 = 27,812 fixes, the header's counts.
- Within each storm the fixes at 0000, 0600, 1200 and 1800 are six hours apart in all 26,337 steps (27,310 such fixes less one first fix for each of the 973 storms).
- The status agrees with the usual wind thresholds in nearly every row: every hurricane fix at 64 kt or more, every tropical depression at 33 or less, and 9,718 of the 9,720 tropical storm fixes between 34 and 63; two are higher as the file gives them (EP032013 at 1200 UTC 26 June 2013, 65 kt, and CP012015 at 0600 UTC 22 July 2015, 80 kt).
- Each storm's first fix is in its season's year, and each `event_id` holds the row's own day and time.

## What it does not hold

- Seasons before 2000 (the files run from 1851 and 1949), and the 2026 season, not yet in the files.
- The wind radii: the columns after the pressure on each fix line are not taken.
- Other basins (the western Pacific, the Indian Ocean, the Southern Hemisphere).
- Forecasts, advisories and damage: the best track only. A landfall is a fix the file marks L; `entity_ids` names no state or place.
