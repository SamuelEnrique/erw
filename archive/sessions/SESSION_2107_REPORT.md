# Session 2107 report: the sunlight solar runs on (NOAA's Climate Reference Network, in place of NASA POWER)

23 October 2026, from 21:29 UTC, on lab-desktop (the data machine), a session of `queue/done/069-day-27-october-data-public-lands-sunlight-spending-streams.md`. Model spend USD 0. Pulls: 14 requests of 15 (power.larc.nasa.gov's robots file; www.ncei.noaa.gov's robots file, the monthly01 listing, a headers address that answered 404, headers.txt, readme.txt and eight stations' files), and 3 to Supabase for the lock.

## Read these first

- **NASA POWER was not asked for data:** its robots file (asked in a call of its own, 21:29:59 UTC) allows only `/api/pages/` and disallows `/api/` for every reader, so the daily point API (`/api/temporal/daily/point`) is closed to the ERW's reader. It also disallows `/` to `anthropic-ai`, `Claude-Web` and other AI crawlers. **power.larc.nasa.gov's `/api/` joins the hosts not asked again without a ruling**; session 2119 writes it into chain 079's rules.
- **In its place, NOAA's U.S. Climate Reference Network** (USCRN, www.ncei.noaa.gov, whose robots file disallows `/data*` and `/orders*`, not `/pub/`): the monthly01 product's average daily total global solar radiation, measured on the ground. **One series table, `noaa_uscrn_solar_monthly`:** 2,025 station-months at eight stations near the grids' solar fleets, from each station's start (2008 for Fallbrook) to September 2026. The stations are Fallbrook, Merced, Stovepipe Wells and Redding (CAISO, `ba` ciso) and Monahans, Austin, Bronte and Edinburg (ERCOT, `ba` erco). The period runs from each station's start, not from 2020 as the file asked for NASA's data: the whole file costs one request a station.
- **A new unit, `MJ/m2-day` (Decision 63),** in the standard and the validator together (megajoules a square meter a day; 1 MJ/m2-day is 0.2778 kWh/m2-day). It is not the file's kWh a square meter a day: NOAA publishes MJ, and the table keeps the publisher's unit.
- **NOAA's missing months** (-9999.0, a month that fails note H's rule of fewer than 4 consecutive and at most 5 total days missing) have no row and are counted in the header: Merced 15, Edinburg 8, Redding 6, Stovepipe Wells 4, Monahans 4, Bronte 3, Fallbrook 2, Austin 1 (the current month, October 2026, is among them).
- **The cross-check** (`runs/c069/s2107/cross.py`), the mean of a grid's stations against California's and Texas's monthly solar generation (`state_generation_mix_monthly`), ranked within each year to set the fleet's growth aside. In California, Spearman runs from 0.86 to 0.99 in every year from 2015 to 2025, and the month of most generation is the month of most sunlight in 8 of 12 years. In Texas, Spearman is 0.70 to 0.94 in every year but 2016, when it is 0.10: Texas's solar fleet grew within that year, and generation peaked in October. Mean radiation peaks in June in California (26.7) and in July in Texas (23.8).
- **Registered:** the sector rule (`power`, as the grid weather tables; there is no solar sector), the live set's hold and the release's storage hold, the release package's rows, the license tables (licenses check 0 problems, release check 0 differences); no row twice. The test: `tests/test_session2107.py` (4 tests).

## Errors

- **The first headers address was wrong** (`HEADERS.txt`; the file is `headers.txt`): one request answered 404, read from the listing after.

## Decisions made without you

- **NOAA's network in place of NASA POWER,** a public U.S. source the ERW did not hold, on a host it already reads, under NOAA NCEI's verdict (read 9: its restriction concerns the non-U.S. data in ISD).
- **Monthly, not daily:** monthly01 is one file a station, so eight stations fit the ceiling; USCRN's daily files are one a station a year.
- **The unit kept as NOAA's** (`MJ/m2-day`), not converted to kWh.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/noaa_uscrn.py`, `tests/test_session2107.py`, this report.
- Changed: `docs/datastandard.md`, `warehouse/validate/erw_validate.py`, `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`, `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c069/s2107/`.
