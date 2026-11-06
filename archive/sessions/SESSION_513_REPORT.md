# Session 513 report: OE-417 not found again; EIA's U.S. nuclear outages pulled in its place

21 October 2026, from 19:37 UTC, on lab-desktop (the data machine), the fourth session of `queue/done/026-night-21-october-sources.md`. Model spend USD 0.

## Read these first

- **DOE's OE-417 (now DOE-417) summaries: still no file to pull.**
  - A web search names only the old host, `www.oe.netl.doe.gov`, whose annual summaries page lists 2000 to 2023. The host still does not resolve (a name error, as in session 508).
  - EIA's Electric Power Monthly carries the form's major disturbances as Table B.1. Its file (`electricity/monthly/xls/table_b_1.xlsx`, Last-Modified 21 May 2024) holds only January to March 2024, so it is stale and was not taken.
- **In its place, by the chain's rule: EIA's status of U.S. nuclear outages** (API v2, route `nuclear-outages/us-nuclear-outages`), as `warehouse/connectors/eia_nuclear_outages.py` and the series table `eia_nuclear_outages_daily`.
  - 21,702 rows: every day from 1 January 2007 to 21 October 2026 (7,234 days), each with the fleet's capacity (MW), its outage (MW) and the outage's share (a ratio, from EIA's percent).
  - EIA estimates these from the NRC's daily power reactor status reports. They are EIA's figures as published, and nothing is filled.
- **Robots and terms**: EIA's API is allowed, and EIA's terms are record 1 of `license_reads.csv` (public).
- **Cross-checks** (`runs/s513/crosscheck.py` on the data machine):
  - Against `nrc_reactor_status`, the NRC's own reactor status: 2,486 days in both (2020 to 2026, a median of 94 reactors a day). EIA's outage share averages 0.088, and the reactors' unweighted mean outage 0.093. The daily difference has a median of -0.0035, 95% of days are within 0.024, and the correlation is 0.989. EIA's share is weighted by capacity and the reactors' mean is not, which may explain the gap; that was not measured.
  - EIA's fleet capacity on 21 October 2026, 100,057 MW, against EIA-860M's operating nuclear nameplate of 103,698 MW (96 generators).
- **Written under the data lock** (19:39 UTC) with `--offline`, from the trial's two saved pages (0 requests). The validator, coverage and archive exited 0.
- **Held** from `/data`'s catalogue and Redivis v1 until uploaded. Not in the live set.
- Sector rule (`power;uranium`, as `nrc_reactor_status`). Tests: `tests/test_session513.py`, 5, on real records.
- The plants' own outages (routes `facility-nuclear-outages` and `generator-nuclear-outages`, daily from 2007) would take about 80 pages each, more than this session's ceiling. They are put in the next file.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.oe.netl.doe.gov | 1 of 8 | robots file (the name does not resolve) |
| www.eia.gov | 1 of 8 | Table B.1 |
| api.eia.gov | 4 + 2 of 8 | the route and its three child routes' metadata; the two pages of the trial; the write reused them |

## Decisions made without you

1. The U.S. total only, within the ceiling; the plants' outages are left for a session with its own ceiling.

## Files

- New: `warehouse/connectors/eia_nuclear_outages.py`, `tests/test_session513.py`, this report. Changed: `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`, `docs/redivis/release-v1/`, `docs/coverage.md`, `docs/licenses.md`, `warehouse/metadata/{coverage,archive_manifest,sources,license_tables}.csv`.
