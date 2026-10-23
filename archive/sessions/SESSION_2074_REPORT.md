# Session 2074 report: six held tables described

23 October 2026, from 20:22 UTC, on lab-desktop (the data machine), the fifth session of `queue/done/067-day-25-october-data-neighbours-emitters-disasters-world-oil.md`. Model spend USD 0. Pulls: none.

## Read these first

- **Six notes written,** for public source tables of publishers other than EIA and the ISOs that no note described and that chains 057, 058 and 066 had not taken (their worktrees' notes checked first), by a helper agent in this chain's worktree and checked by this session:
  - `docs/methods/census_metro_population.md` (1,650 rows: 387 metro areas and 438 state parts, 2020 and 2025)
  - `docs/methods/datacenter_operator_sites.md` (275 sites of 9 operators, one snapshot of 12 October 2026)
  - `docs/methods/impact_tax_rules.md` (49 rows: 42 rules held, 7 "no rule held")
  - `docs/methods/lbnl_interconnection_queue.md` (38,201 requests, queue dates 1995 to 2025)
  - `docs/methods/noaa_grid_weather_stations.md` (245 rows: 35 stations, 7 variables)
  - `docs/methods/weather_obs_hourly.md` (10,627 rows, 21 September to 23 October 2026)
- **Each note's checks ran on the data,** among them: every metro area's state parts add to the area (774 of 774); the LBNL queue's capacity is its three MW columns' sum in all 38,201 rows, and its requests agree with `interconnection_queue_summary` in all 9 regions; each weather station's hours measured, interpolated and missing add to 68,332; NWS's hour against NOAA's at the same seven airports differs by 0.67 F on average.
- **Seven points where a description and the code or the data disagree:**
  - Corrected (in session 2079, when this session's notes and the next were checked together): `weather_nws.py` said its values are "NWS quality-controlled", and the code takes every non-null value without reading the API's `qualityControl` flag; `lbnl_queues.py`'s docstring left `unknown` out of its status map.
  - Recorded in the notes, not changed: the LBNL file on this machine keeps a trailing ".0" in every filled `fips_code`, `q_year` and `prop_year`, which the code strips (the file was rebuilt by `restore_tables.py` and restored by `sync.py`; the cause is not established); `noaa_grid_weather_stations` names only `noaa:isd_lite` as its source, though hours from August 2025 come from `noaa:lcd_v2`; 7 of its 35 `x_metro` names are session 126's, not the Census names its header gives; `datacenter_operator_sites`' header says "License: public" where the license record has the operators' tables ruled "license needed" (a ruling of 21 October, already in `docs/licenses.md`).
  - Not a fault: `census_metro_population`'s header line about rewriting is `scripts/sync.py`'s restore line, and the connector does write a fresh header.
- **The Method cells** of the six are filled in `docs/coverage.md` (with session 2079's four).

## Decisions made without you

- **The notes written by a helper agent and checked by this session,** as sessions 2004, 2046 and 2052 did.
- **The LBNL file's ".0" and the stations' source column left as found:** both concern tables other connectors write each day; a fix belongs to a session that can run them.

## For Samuel's ruling

- None new.

## Files

- New: the six notes above, this report.
- Changed: `docs/coverage.md` (the Method cells).
