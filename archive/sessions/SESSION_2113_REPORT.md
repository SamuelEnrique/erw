# Session 2113 report: the rivers behind the dams (the USGS's streamflow)

23 October 2026, from 22:35 UTC, on lab-desktop (the data machine), a session of `queue/done/069-day-27-october-data-public-lands-sunlight-spending-streams.md`. Model spend USD 0. Pulls: waterservices.usgs.gov, 9 requests of 15 (its robots address, 404, there is no robots file; then one request a gauge, eight gauges, the first a probe whose saved copy the trial reused), and 3 to Supabase for the lock.

## Read these first

- **One series table, `usgs_streamflow_daily`:** 33,421 rows, the daily mean discharge (parameter 00060, statistic 00003) at eight gauges below large hydropower plants, from 1 January 2015 to 22 October 2026. The service is the USGS's NWIS daily values (`/nwis/dv/`, tab-delimited). The gauges are:
  - the Columbia at The Dalles (below The Dalles Dam) and at Grand Coulee;
  - the Colorado below Hoover Dam and at Lees Ferry (below Glen Canyon);
  - the Missouri at Bismarck (below Garrison);
  - the Snake at Hells Canyon Dam;
  - the Sacramento at Keswick (below Shasta);
  - the Feather at Oroville.
- **A new unit, `ft3/s` (Decision 64),** in the standard and the validator together; the write ran with the branch's validator. Chain 079's agent numbers its Decisions from 65.
- **The USGS's codes kept** in `x_qual`: A approved (24,772), A:R approved and revised (6,074), P provisional (1,240), A:e approved and estimated (1,232), P:e (103). Provisional values are released by the USGS without liability and may be revised; the header says so. No day was written as a code (Ice, Eqp and the like); the parser counts them if they come. Some gauges have days with no line at all, so they have fewer rows: Oroville 3,926, Hells Canyon 3,935, Hoover 4,054, of 4,313 days.
- **The cross-check** (`runs/c069/s2113/cross.py`), each gauge's yearly mean flow against the yearly net generation of the Reclamation plant above it (`usbr_hydropower_monthly`, full years 2015 to 2024): Hoover Pearson 0.96 (Spearman 0.95), Glen Canyon 0.96 (0.95), Grand Coulee 0.98 (0.95), Shasta 0.94 (0.89). Wetter years are bigger years: Glen Canyon's 2022 (9,727 cfs, 2,540 GWh) and Shasta's 2022 (3,691 cfs, 766 GWh) are each plant's lowest of the ten. The other four plants (The Dalles, Garrison, Hells Canyon, Oroville) are not Reclamation's and were not checked here.
- **Geo:** Hoover's gauge is on the Arizona and Nevada line and Hells Canyon's on the Idaho and Oregon line; each is given one state (US-AZ and US-OR), and the gauge's name in `node` says both.
- **Registered:** the sector rule (`power`), the live set's hold and the release's storage hold, the release package's rows, the license tables (USGS, read 87; licenses check 0 problems, release check 0 differences); no row twice. The test: `tests/test_session2113.py` (4 tests).

## Errors

- **The docstring first listed three codes;** the rows hold a fourth, R (revised), now named in the docstring and the header.

## Decisions made without you

- **waterservices.usgs.gov, not its successor** (api.waterdata.usgs.gov): the old service still answers, needs no key and gives the codes. A code chain moves the connector when the USGS retires it.
- **Eight gauges, from 2015,** one request each.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/usgs_streamflow.py`, `tests/test_session2113.py`, this report.
- Changed: `docs/datastandard.md`, `warehouse/validate/erw_validate.py`, `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`, `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c069/s2113/`.
