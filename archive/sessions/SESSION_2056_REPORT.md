# Session 2056 report: chain 067 written, and the disasters declared (FEMA's OpenFEMA)

23 October 2026, from 19:51 UTC, on lab-desktop (the data machine), the first session of `queue/done/066-day-25-october-data-disasters-loans-drought-assistance.md`, taken by chain 057's agent at that chain's end. Model spend USD 0. Pulls: 3 requests of 15 (www.fema.gov's robots file, asked in a call of its own: it disallows nothing under `/api/open/` and asks a crawl delay of 15 seconds, which every request kept; OpenFEMA's terms and conditions; the data set's CSV, through the connector's trial). The write reused the saved file (`--offline`).

## Read these first

- **Chain 067 written and pushed first:** `queue/next/067-day-25-october-data-neighbours-emitters-disasters-world-oil.md` (sessions 2070 to 2083: Ontario's and Alberta's markets, EPA's greenhouse gas reporting across sectors, NOAA's billion-dollar disasters, JODI's oil data, the Energy Institute's Statistical Review, the licenses' fifteenth round and the rest), committed alone and pushed to main (`20cfa871`); snapshot before `q067-before`, against chain 057's after snapshot: 0 differences (Vercel rate limited, nothing deployed). Chain 059's agent took it at its own chain's end and is running it.
- **This chain's branch** is `wip/2056-2069-data` in `erw-c066`, cut from chain 057's merged branch (`fef13276`) while it landed; its license reads follow chain 057's last (195).
- **One table written, validated, archived, in coverage (sectors power, gas and oil), in the release package, both holds:** `fema_disaster_declarations`, 26,199 rows of OpenFEMA's 70,572: every declaration and designated area declared from 1 January 2015, one event a row (14,950 rows of major disasters, 10,470 of emergencies, 779 of fire management), with the incident type, title, area, incident dates, the programs declared, the disaster number and the region.
- **Its license:** OpenFEMA's terms ask the endpoint and the time to be cited and a statement made ("This product uses the Federal Emergency Management Agency's OpenFEMA API, but is not endorsed by FEMA. ..."), and forbid FEMA's and DHS's logos; the table's header carries the statement. The verdict waits for session 2061's round (the terms page read here is its source), so the table is "not settled" until then.

## The cross-check

FEMA's hurricane and severe storm major disasters (358 with incident dates, 2015 to 2026) against chain 059's NCEI storm events and chain 058's DOE-417 events, `runs/c066/s2056/cross.py`: 334 (93 percent) have NCEI storm events in the same state within the incident's dates; 132 (37 percent) have a DOE-417 weather event naming the state, as expected, since DOE-417 reports only large outages. By year of declaration: 0 to 13 hurricane and 13 to 40 severe storm major disasters a year, 40 severe storms in 2024 the most.

## Errors

- None.

## Decisions made without you

- **From 2015 only,** as the chain asked; FEMA's set runs from 1953.
- **One row a declaration and designated area,** the statewide and tribal rows included; entity_ids the state and, where FEMA names one, the county's FIPS.
- **Status open or closed** by FEMA's closeout date.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/fema_disasters.py`, `tests/test_session2056.py` (3 tests), this report; on main, the chain 067 file.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c066/s2056/`, `runs/license_reads/s2056/`, `runs/s2056*`, `warehouse/raw/fema_disasters/`.
