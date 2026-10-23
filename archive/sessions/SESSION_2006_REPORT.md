# Session 2006 report: population-weighted degree days (NOAA's Climate Prediction Center)

23 October 2026, from 15:20 UTC, on lab-desktop (the data machine), the first of `queue/done/056-evening-23-october-data-jobs-reactors-large-loads-hydro.md`'s two sessions of a source of its own choosing. Model spend USD 0. Pulls: 16 requests of 20 (ftp.cpc.ncep.noaa.gov's robots file, asked in a call of its own: none, HTTP 404; the daily data folder; the 2026 folder; one file, to read its form; then the trial's twelve files, three of them before a heading stopped the first trial and nine after). The write, at 16:30 UTC when the lock was free, reused the saved files.

## Read these first

- **Why this source:** the ERW holds station temperatures and its grids' degree days, but not the population-weighted heating and cooling degree days analysts use for gas and power demand, by state and census division, which CPC publishes each day.
- **One table written, validated, archived, in coverage (sectors power and gas, public), in the release package, both holds:** `noaa_cpc_degree_days_daily`, 118,900 rows: CPC's population-weighted heating and cooling degree days (degF-day, at 65 F), a day, for the 48 contiguous states, the nine census divisions (as CPC numbers them, `cpc_dd:division_1` to `_9`) and the contiguous United States, 1 January 2024 to 21 October 2026.
- **The cross-check against the ERW's grid weather** (`noaa_grid_weather_daily`, 2025): the days move together (daily correlations 0.84 to 0.99: ERCOT and Texas 0.990 and 0.980), while the totals differ by weighting (a grid's stations against a state's people: ERCOT's cooling 3,619 against Texas's 2,926). The contiguous states' 2025 totals: 4,175 heating and 1,326 cooling degree days.

## Errors

- **The first trial stopped on the Population files' region line,** "CPC::Regions::CensusDivisions", where the connector expected the file's name; the connector now holds each file's region set. Three requests were spent before the stop.
- **The divisions were first written `cpc_dd:1` to `cpc_dd:9`** (the files number them); session 2009 renamed them `cpc_dd:division_<n>` before the write. The files do not name the divisions, and none is named here.

## Decisions made without you

- **2024 to 2026 only,** within the ceiling (four files a year); CPC's daily files run from 1981. The fuel-weighted heating degree days (utility gas, electricity and the rest) and the climate divisions are not taken.
- **The current year's files fetched again on each run** (they grow each day); earlier years' are kept.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/noaa_cpc_degree_days.py`, `tests/test_session2006.py` (3 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c056/s2006/`, `runs/license_reads/s2006/`, `runs/s2006*`, `warehouse/raw/noaa_cpc_degree_days/`.
