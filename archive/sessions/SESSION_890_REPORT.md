# Session 890 report: a source the ERW did not hold: USGS's U.S. Large-Scale Solar Photovoltaic Database

23 October 2026, from 05:18 UTC, on lab-desktop (the data machine), a session of `queue/done/048-night-23-october-data-utility-files-products.md`. Model spend USD 0. Pulls: 5 requests of 20 (one to PHMSA, four to USGS).

## Read these first

- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `uspvdb_solar_facilities`, 6,611 ground-mounted solar facilities of 1 MW (AC) and more, 131,574 MW AC, from USGS's U.S. Large-Scale Solar Photovoltaic Database (with LBNL), through USGS's public API. Each facility has its outline's centroid and area, AC and DC capacity, technology, tracking, azimuth and tilt, battery (375 facilities), agrivoltaics, site and system type, image date and EIA plant id (all 6,611).
- **Why this source:** it is the solar sibling of the U.S. Wind Turbine Database the ERW holds (`uswtdb_wind_turbines`). It places each solar facility by its outline, which EIA's tables give only as a plant's coordinates, and it describes the design (tracking, DC to AC ratio, agrivoltaics).
- **The cross-check, against `eia860_solar_generators` (session 885, EIA-860 2025, operable), by EIA plant id:**
  - 6,569 of the 6,611 facilities (99.4 percent) are EIA-860 solar plants;
  - their AC capacity agrees within 1 percent in 6,042 and within 5 percent in 6,199; in total 131,186 MW against EIA's 131,738;
  - 728 of EIA's 7,256 solar plants of 1 MW and more are not in the database. The database's newest year holds 217 facilities against 647 in 2024, so its 2025 is not yet complete.
- **One image date is no calendar date:** USGS gives 20240231. The date column is left empty for it, and USGS's value is kept in `image_date_usgs` (every row) and named in the header. Nothing is mended.
- **The license:** its publisher, "U.S. Geological Survey (USGS), with LBNL", resolves by session 888's name rule to USGS's verdict (read 87, public domain): "may be public", agreeing with the flag.
- **PHMSA, tried first and left:** the pipeline safety office's host (www.phmsa.dot.gov) answered HTTP 403 to its robots file, so nothing else was asked. Its incident data stay outside the ERW.

## Decisions made without you

- **A facility is an entity of type `plant`,** with its AC capacity as `capacity_mw`, as EIA rates a solar plant.
- **A USGS value that is no date is left empty in the date column, never mended.** The run does not stop: unlike the wind database's connector, which stops on a bad date, this one keeps every facility.

## For Samuel's ruling

- None new.

## Files

- New:
  - `warehouse/connectors/uspvdb.py`
  - `tests/test_session890.py` (3 tests)
  - this report
- Changed:
  - `build_coverage.py`, `release_v1.py`, `live_set.yaml`
  - `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`
  - `license_tables.csv`, `docs/licenses.md`
  - `docs/redivis/release-v1/`
- On the data machine only:
  - `runs/c048/s890/`
  - `runs/license_reads/s890/`

## Corrected by session 891

The method notes' checks (session 891) found these against the code, the tables and EIA's files:

- The database is not "every ground-mounted facility of 1 MW (AC) and more": as written, 52 facilities are under 1 MW AC (each 1 MW DC or more) and 619 have a system type that is not ground (rooftop 407, canopy 148, canopy and rooftop 62, floating 2). Session 891 corrected the docstring and the header, which now count both, and wrote the table again, the same rows.
