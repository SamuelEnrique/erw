# Session 2073 report: the billion-dollar disasters (NOAA's retired record)

23 October 2026, from 20:18 UTC, on lab-desktop (the data machine), the fourth session of `queue/done/067-day-25-october-data-neighbours-emitters-disasters-world-oil.md`. Model spend USD 0. Pulls: 3 requests of 10 (www.ncei.noaa.gov's robots file, asked again in a call of its own and read first, unchanged since session 2042; the product's page; its events file). The trial and the write reused the saved file (`--offline`).

## Read these first

- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `noaa_ncei_billion_disasters`, the 403 U.S. weather and climate disasters of a billion dollars or more, 1980 to 2024, as NCEI last published them (the product was retired in 2025): each event's name, type (severe storm 203, tropical cyclone 67, flooding 45, drought 32, winter storm 24, wildfire 23, freeze 9), begin and end dates, cost in dollars adjusted for inflation and unadjusted, and deaths. USD 2.918 trillion in all, CPI-adjusted.
- **The page is drawn by script;** the events file its application downloads (`events-US-1980-2024.csv`) is read directly, with the citation the page gives (DOI 10.25921/stkw-7w73).
- **The file names no state an event touched:** the product's maps did, and are not taken, so the chain file's states and its cross-check against chain 066's FEMA declarations (not yet written: chain 066 runs beside this chain) are not made. The cross-check below is against this machine's storm events instead.
- **NOAA NCEI's verdict holds** (read 9, and read 182 of chain 059's round).

## The cross-check

Each tropical cyclone of 2015 to 2024 against the hurricane, tropical storm and storm surge damage `noaa_ncei_storm_events` records between the cyclone's begin day less one and its end day plus two (`runs/c067/s2073/cross.py`): **27 of the 29 cyclones have storm events in their days; the two costs correlate at 0.611; Storm Data's damage sums to 13 percent of NCEI's unadjusted cost.** Hurricane Ian of September 2022, for example: NCEI's USD 111.8 billion against 175 storm events with USD 15.4 billion of recorded damage. The billions estimate all losses, insured and not; Storm Data's damage is what the forecast offices entered. The two without events of these four types in their days are Tropical Storm Imelda (2019, Texas, a flood) and Hurricane Fiona (2022, Puerto Rico); Hurricane Beryl (2024) has 10 events that record no damage.

## Errors

- None.

## Decisions made without you

- **An identifier of our own** (begin date and a hash of the name): NCEI gives the events none.
- **NCEI's millions written as dollars,** the inflation adjustment as NCEI published it (to the record's last year).
- **The cross-check against the storm events,** the FEMA table not yet held.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/noaa_billion_disasters.py`, `tests/test_session2073.py` (3 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_reads.csv` (198), `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c067/s2073/`, `runs/license_reads/s2073/`, `runs/s2073*`, `warehouse/raw/noaa_billion_disasters/`.
