# Session 2058 report: drought (the U.S. Drought Monitor)

23 October 2026, from 20:04 UTC, on lab-desktop (the data machine), a session of `queue/done/066-day-25-october-data-disasters-loans-drought-assistance.md`. Model spend USD 0. Pulls: 8 requests of 15 (droughtmonitor.unl.edu's robots file, asked in a call of its own: it disallows `/data/`, `/nadmdata/`, `/webfiles/` and `/DmData/DataArchive.aspx`, none asked; usdmdataservices.unl.edu's robots file, a new host, in a call of its own: none, HTTP 404; the web service page; two tests of the state statistics, the first of them sent as `aoi=53` alone, below; the three spans through the connector). The write reused the saved answers (`--offline`).

## Read these first

- **One table written, validated, archived, in coverage (sector power), in the release package, both holds:** `usdm_drought_state_weekly`, 177,696 rows: the percent of each of the 48 contiguous states' area in each drought category (none, D0 to D4), a week, from the map of 30 December 2014 to that of 20 October 2026 (617 weeks), in the Monitor's traditional form: each category is cumulative, so `d1` is the area in moderate drought or worse. Every row's none plus D0 is 100, and D0 to D4 never rise, or the run stops.
- **Three requests for twelve years:** the state statistics take every state's FIPS code in one request (the service page names one state an `aoi`; a test showed a list works), and the connector asks four years a span. A span's start date returns the week before it too, so 288 rows two spans gave alike are kept once (and a difference would stop the run).
- **Its license:** the Monitor asks credit to the National Drought Mitigation Center, USDA and NOAA; the header carries it. The verdict waits for session 2061's round.

## The cross-check

Each western state's yearly mean area in moderate drought or worse against its yearly conventional hydroelectric generation (`eia_state_generation_monthly`, HYC), 2015 to 2025, `runs/c066/s2058/cross.py`:

| State | Correlation | Driest year (d1) | Its hydro | Wettest year | Its hydro |
|---|---|---|---|---|---|
| California | -0.83 | 2022, 99.6% | 17.6 TWh | 2024, 5.7% | 29.5 TWh (2017: 14.4%, 42.4 TWh) |
| Washington | -0.35 | 2015, 64.0% | 73.4 TWh | 2016, 4.4% | 78.3 TWh |
| Oregon | -0.22 | 2015, 91.6% | 31.3 TWh | 2017, 3.8% | 38.3 TWh |

California's hydropower follows its own drought closely. Washington's and Oregon's follow it less, as the Columbia's flow comes from snowpack upstream, much of it in Canada and Idaho (my reading, not checked against a source).

## Errors

- **My first test request went out as `aoi=53` alone:** the probe's list file is a CSV, and the address's commas split it; the server reset the stream. The commas were then sent encoded (`%2C`). One request lost.
- **The first trial stopped on a column named "None":** pandas renames it when it makes tuples; rows are read as dicts.

## Decisions made without you

- **The traditional (cumulative) statistics,** the Monitor's usual form; the categorical are not taken.
- **The 48 contiguous states,** not Alaska, Hawaii or Puerto Rico, as the chain asked.
- **The week before 2015's first** kept (the map of 30 December 2014), as the service returns it.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/usdm_drought.py`, `tests/test_session2058.py` (4 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c066/s2058/`, `runs/license_reads/s2058/`, `runs/s2058*`, `warehouse/raw/usdm_drought/`.
