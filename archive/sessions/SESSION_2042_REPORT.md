# Session 2042 report: storms (NOAA's Storm Events Database), chain 066 written

23 October 2026, from 18:19 UTC, on lab-desktop (the data machine), the first session of `queue/done/059-night-24-october-data-storms-reactor-events-lng-climate.md`. Model spend USD 0. Pulls: 15 requests of 15 (www.ncei.noaa.gov's robots file, asked in a call of its own and read first; the Storm Events Database's page; the bulk directory's listing; then the trial's twelve yearly details files, 2015 to 2026). The write, at 18:30 UTC, reused the saved files (`--offline`) and the probe's saved listing.

## Read these first

- **Chain 066 written and pushed first:** `queue/next/066-day-25-october-data-disasters-loans-drought-assistance.md` (sessions 2056 to 2069: FEMA's disaster declarations, DOE's Loan Programs Office, the U.S. Drought Monitor, the National Hurricane Center's HURDAT2, HHS's LIHEAP, fueleconomy.gov, the NRC's license renewals and uprates, the licenses' fourteenth round and the rest), committed alone and pushed to main (`c21595d1`). 066 was the next free number: 060 to 065 and 070 to 078 are the code machine's, 080 to 084 the portable laptop's, and 066 to 069 were never used. Sessions 2056 to 2069 were free on main, on chains 056 and 057's branches and in chains 057 and 058's worktrees. Chain 059's own queue move (`0e85cc49`, pushed at 18:19 UTC; `chain_queue.py next` commits and does not push) went first. Snapshots: `c059-take-before` (before the move), `s2042-before` (before 066) and `s2042-after`: **0 differences in all** (25 pages, both comparisons). Vercel's status for both commits was "Deployment rate limited", so nothing deployed.
- **Chain 059 runs beside chains 057 and 058 on this machine** (the owner's instruction), in its own worktree `erw-c059` on `wip/2042-2055-data`. Chain 056 landed at 18:21 UTC (`bdf7367a`, check run 40001414007) before this chain's branch was cut, so this branch is cut from main (`c21595d1`), not from another chain's branch. Its reads would number after 174, chain 056's last; chains 057 and 058 number from 175 too, so the later chain to land renumbers its rows at the merge.
- **The writes wait for the data lock** through `runs/c059/write_table.sh` (chain 058's `runs/c058/write_table.sh`, copied: the lock waited for with `duty.py beat`, and released only after the main checkout's metadata files are diffed and put back).
- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `noaa_ncei_storm_events`, 411,139 events from 1 January 2015 to 30 June 2026 (the 2026 file, created 18 September, ends with June) of the 19 types that take lines down or strain the grid: thunderstorm wind 206,586, high wind 43,770, winter storm 33,217, heavy snow 24,870, heat 18,695, tornado 17,479, excessive heat 15,469, strong wind 12,448, extreme cold 10,601, cold 7,360, blizzard 6,182, wildfire 4,039, lightning 3,458, tropical storm 3,190, ice storm 2,662, storm surge 494, hurricane (typhoon) 379, tropical depression 239, hurricane 1 (NCEI keeps "Hurricane" and "Hurricane (Typhoon)" apart, and so does the table). Each with NCEI's event and episode identifiers, the begin time in UTC, the state (name, FIPS and ISO code), county or forecast zone, the forecast office, the end time, property and crop damage in dollars, injuries and deaths, the magnitude and the tornado's scale and path, and the begin and end points.
- **NCEI's times are local standard time** in the zone `CZ_TIMEZONE` names (`EST-5`, `CST-6` and the rest), with no daylight saving: the connector subtracts the zone's own offset; `x_begin_local` keeps NCEI's time. A zone not in that form stops the run (none did).
- **Not taken:** hail, floods, marine events and the other types (about 340,000 more rows), and the narratives.

## The cross-check

NOAA's ice storms and hurricanes against chain 058's DOE-417 weather events (`doe_oe417_events`, written by session 2028 at 18:21 UTC), by state and day, a day either side (`runs/c059/s2042/cross.py`):

| Year | Ice storm state-days | With a DOE-417 weather event | Hurricane state-days | With a DOE-417 weather event |
|---|---|---|---|---|
| 2016 | 24 | 0 | 6 | 6 |
| 2017 | 36 | 2 | 6 | 6 |
| 2018 | 19 | 8 | 9 | 6 |
| 2019 | 36 | 2 | 3 | 3 |
| 2020 | 22 | 2 | 11 | 11 |
| 2021 | 43 | 14 | 3 | 2 |
| 2022 | 50 | 8 | 2 | 2 |
| 2023 | 45 | 8 | 2 | 0 |
| 2024 | 24 | 0 | 6 | 6 |
| 2025 | 35 | 1 | 0 | 0 |

A hurricane's state-day nearly always has a reported disturbance (42 of 48); an ice storm's seldom does (45 of 334): most of NOAA's ice storms are a zone's glaze that leaves no reportable outage, and a DOE-417 report needs 50,000 customers out or a loss of 300 MW. 2021's 14 are February's winter storm in Texas and the South. The year 2025 had no hurricane landfall in the United States, and NOAA's file has none. The other way, 867 of the 878 DOE-417 weather events whose area names a state have a NOAA event of these types in that state within a day (113 more name no state the check could read).

## Errors

- **The first test expected the events in the wrong order:** the table is sorted by the UTC time, and the test's Florida event, five hours behind UTC, comes before the Texas one. The test was corrected, not the code.
- **The metadata patch did not apply cleanly to `sources.csv`:** the main checkout still stood at `0e85cc49`, before chain 056's landing, and its row beside the new one differed. Resolved with `runs/union_resolve.py` (both sides kept); no row twice in `sources.csv`, `coverage.csv` or the archive manifest.

## Decisions made without you

- **The grid's types only** (19 of NCEI's 55), in NCEI's own words; the rest can be added by extending `TYPES`.
- **No terms page asked:** the Storm Data are the National Weather Service's records, under NWS's public domain notice (read 8); the request it would have cost was the last of the fifteen. `scripts/licenses.py` maps the table to NOAA NCEI (read 9: "may be public"), whose one restriction is on ISD's non-U.S. stations.
- **The listing read from the probe's saved copy for the trial and the write** (`--listing`), so the trial did not ask for it a second time; a daily run asks for it fresh.
- **Damage figures in dollars** from NCEI's `K`, `M` and `B`; `K` alone, NCEI's form for none, is 0; an empty cell stays empty.
- **The UTC begin time as `event_date`**, the local time kept beside it.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/noaa_storm_events.py`, `tests/test_session2042.py` (4 tests), `queue/next/066-day-25-october-data-disasters-loans-drought-assistance.md` (on main), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c059/`, `runs/license_reads/s2042/`, `runs/s2042*`, `warehouse/raw/noaa_storm_events/`.
