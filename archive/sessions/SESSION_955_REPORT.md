# Session 955 report: renewable energy projects on public lands (the Bureau of Land Management, California)

23 October 2026, from 12:40 UTC, on lab-desktop (the data machine), a session of `queue/done/054-day-23-october-data-federal-royalties-wind-costs-minerals.md`. Model spend USD 0. Pulls: 13 requests of 15 (gis.blm.gov's robots file: none, HTTP 404; its service folders and the `lands` folder; www.arcgis.com's robots file, asked in a call of its own, and two searches of its catalogue; services1.arcgis.com's robots file: none, "Invalid URL"; the rights-of-way planning tool's group layer; two land records services that answered with their root list; BLM California's service; its two layers).

## Read these first

- **No national layer of BLM's renewable projects was found.** gis.blm.gov's public folders hold none; the rights-of-way planning tool's "Rights of Way" group layer (BLM's national one on ArcGIS Online) holds transmission corridors and no-surface-occupancy areas, not projects; the land records services that hold every right-of-way case answer the public with their root list only. What BLM does publish is California's: the state office's "BLM CA Renewable Energy Projects", verified and preliminary rights-of-way, on gis.blm.gov.
- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `blm_ca_renewable_rows`, 57 rights-of-way (46 verified, 11 preliminary): 32 authorized, 23 pending, 2 closed; 41 wind (19 of them meteorological test sites) and 16 solar (7 concentrating, 6 PV, 3 not typed). Each with BLM's serial number, case type, disposition, application, effective and expiration dates, project and BLM acres, data source and remarks. BLM gives no megawatts.
- **The cross-check, by name in California (read by hand):** of the 8 authorized solar rights-of-way, 5 are facilities of `uspvdb_solar_facilities`: Desert Sunlight, Stateline and McCoy, which BLM types as PV, and Blythe and Desert Harvest, which BLM still types as concentrating solar (as they were authorized; both were built as PV); Soda Mountain (PV) is not; Ivanpah and Genesis are solar thermal plants, outside a PV database. 14 of the 24 authorized wind rights-of-way (18 facilities, 6 test sites) name a project of `uswtdb_wind_turbines` (Alta, Cabazon, Cameron Ridge, Mesa, Mountain View, Ocotillo, San Gorgonio Farms, Tule, Whitewater Hill).

## Decisions made without you

- **California's layer taken as the session's table,** named as such in the header, rather than none.
- **`status` empty, BLM's disposition kept in `x_disposition`** (Decision 20): "Authorized", "Pending" and "Closed" are a right-of-way's, not a plant's.
- **BLM's dates read as UTC days** from its epoch milliseconds (they fall on the Pacific day's start, 07:00 or 08:00 UTC, so the day is the same).

## For Samuel's ruling

- None new. (A national list would need BLM's land records system, MLRS, whose public services this session could not open.)

## Files

- New: `warehouse/connectors/blm_renewable.py`, `tests/test_session955.py` (4 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c054/s955/`, `runs/license_reads/s955/`, `runs/s955*`, `warehouse/raw/blm_renewable/`.
