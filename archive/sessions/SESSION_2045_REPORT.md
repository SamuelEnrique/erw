# Session 2045 report: the states' climate (NOAA's nClimDiv, the data behind Climate at a Glance)

23 October 2026, from 18:49 UTC, on lab-desktop (the data machine), the fourth session of `queue/done/059-night-24-october-data-storms-reactor-events-lng-climate.md`. Model spend USD 0. Pulls: 8 requests of 15 (www.ncei.noaa.gov's robots file, asked again in a call of its own and read first, unchanged since session 2042; the nClimDiv directory's listing; its `state-readme.txt` and `normals-readme.txt`; then the trial's four files). The write, at 18:52 UTC, reused the saved files (`--offline`), with the branch's validator copied into the main checkout for the one run (the new unit) and main's put back.

## Read these first

- **Not Climate at a Glance's pages, but the files they are drawn from:** Climate at a Glance offers one CSV a state and variable, 96 requests for the 48 states' temperature and precipitation against a ceiling of 15. NCEI's nClimDiv directory holds every state's monthly average temperature and precipitation in one file each, and the means of special periods in two more, so the 48 states and the nation took four files.
- **One table written, validated, archived, in coverage (sectors power and gas, public), in the release package, both holds:** `noaa_climdiv_state_monthly`, 31,458 rows: the 48 contiguous states' and the contiguous nation's monthly average temperature (degF) and precipitation (inches), January 2000 to September 2026, each with **the 1901 to 2000 mean NCEI publishes** for that state and calendar month (the normals file's period 0031, the 20th century base Climate at a Glance's anomalies use). Hawaii, Alaska and the regions are not taken.
- **A new unit, `in`** (precipitation in inches, Decision 60), added to `docs/datastandard.md` and the validator together. Chain 058 has taken Decision 59 (`gal`) on its own branch, so this one is numbered 60; until this chain lands, writes, Method-cell runs and uploads of the table run with the branch's validator copied in.
- **NCEI's state codes are its own,** 001 Alabama to 048 Wyoming and 110 the contiguous United States (not FIPS); the entity keeps NCEI's code (`noaa_climdiv:041`, Texas), `node` the state's name and `geo` its ISO code.
- **The latest year's unprocessed months** (-99.90 and -9.99 in NCEI's files) are omitted rows; a missing value in any earlier month stops the run.

## The cross-check

Each state's monthly average temperature against CPC's population-weighted degree days (`noaa_cpc_degree_days_daily`, chain 056) summed to the month, January 2024 to September 2026, 1,584 state-months of the 48 states (`runs/c059/s2045/cross.py`):

- **June to September, temperature against cooling degree days:** correlation by state, median 0.988, lowest 0.906 (California, whose area average is pulled by its hot interior while its population, and so CPC's weights, sit on the cooler coast).
- **December to March, temperature against heating degree days:** median -0.982, weakest -0.923 (Washington).
- **The warmest of a state's four summer months is its month of most cooling degree days in 138 of 144 state-summers.**
- For example, Texas: January 2025 42.8 F with 615 heating degree days; July 2025 82.2 F with 543 cooling degree days.

## Errors

- None.

## Decisions made without you

- **nClimDiv's files in place of Climate at a Glance's pages,** the same data within the ceiling.
- **NCEI's own 1901 to 2000 means read from its normals file,** not computed, and kept beside each month (`x_mean_1901_2000`); no anomaly column (a subtraction anyone can make).
- **From 2000,** as the chain file asked; the files hold 1895 on, and `--first-year` takes them.
- **The contiguous nation kept** (code 110) beside the 48 states; the regions, Hawaii and Alaska not.
- **Decision 60, not 59,** so this chain and chain 058 can land in either order.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/noaa_climdiv_states.py`, `tests/test_session2045.py` (4 tests), this report.
- Changed: `docs/datastandard.md` (Decision 60), `warehouse/validate/erw_validate.py`, `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c059/s2045/`, `runs/license_reads/s2045/`, `runs/s2045*`, `warehouse/raw/noaa_climdiv_states/`.
