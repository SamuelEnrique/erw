# Session 2120 report: the next file, and the earthquakes the oil fields set off (the USGS's earthquake catalog)

23 October 2026, from 22:22 UTC, on lab-desktop (the data machine), the first session of `queue/done/079-day-28-october-data-quakes-credits-rates-world-renewables.md`, unattended. Model spend USD 0. Pulls: 5 requests of 15 (below).

## Read these first

- **Chain 079 taken** at 22:22 UTC by chain 059's agent when chain 067 landed (the owner's instruction for that run: run the file the queue step prints). Chain 069, whose continuation this file is, still runs beside it (another agent, sessions 2106 to 2119), and chain 068 (a third). Chain 069's agent was told and sent what its session 2119 would have written into this file: its hosts not asked again (power.larc.nasa.gov below `/api/`, apps.bea.gov's `/regional/zip/`), the tables it has written, and the numbers: chain 069's data standard decisions are 062 to 064, so this chain's start at 065.
- **The next file first,** pushed to main on its own before any other work: `queue/next/090-day-29-october-data-wildfires-geomagnetic-inventory-carbon.md` (sessions 2134 to 2147, machine: data): NIFC's wildfire perimeters, NOAA SWPC's geomagnetic index, EPA's national greenhouse gas inventory, NOAA GML's carbon dioxide, DOE's LEAD Tool (chain 069's gap) and the rest. 090 was the next free number (078 to 089 taken); 2134 to 2147 were free. Snapshots `s2120-q-before`/`-after`: 0 differences; Vercel rate limited, nothing deployed.
- **Two of this chain's sources were taken by chain 068 first:** IRENA's capacity statistics (`irena_capacity_annual`, session 2085) and the IRS's residential energy credits (`irs_soi_energy_credits_annual`, session 2087). As the file says, sessions 2121 and 2123 take other public sources the ERW does not hold.
- **One table written, validated, archived, in coverage (sectors oil and gas), in the release package, both holds:** `usgs_comcat_earthquakes_south_central`, every earthquake of magnitude 2.5 and above in the bounding box of Oklahoma, Kansas, Texas and New Mexico from 1 January 2010 to 22 October 2026: 16,000 events, magnitude 2.50 to 5.80. The catalog's own count for the same query is 16,000 (16,050 with the quarry blasts and explosions the query leaves out), under the service's 20,000 a query, so one request took them all.
  - By the state the place names: Oklahoma 9,488, Texas 2,822, New Mexico 2,167, Kansas 1,004, Colorado 373, Mexico 107, a few in Louisiana, Utah and Arizona, 5 naming none.
  - The box is not cut to the state lines: a place names its nearest town, which can lie across a line, so `x_place_state` says which state the place names and a reader filters.
- **The cross-check** (`runs/c079/s2120/cross.py`, beside `eia_crude_production_state_monthly`): Oklahoma's earthquakes of magnitude 2.5 and up a year rose from 141 (2010) and 254 (2013) to 1,883 (2014) and **2,764 in 2015**, then fell to 2,003, 924, 572, 217 and 75 by 2022 and 28 in 2025. Of magnitude 3 and up: 585 in 2014, **885 in 2015**, 639 in 2016. The Oklahoma Geological Survey's widely cited counts are 585 and 903; it counts within the state line, this table by the place, which accounts for the difference.
  - Oklahoma's crude production did not fall with them: 165.5 million barrels in 2015, 165.9 in 2017, 217.5 in 2019. The fall follows the state's injection limits of 2015 and 2016, not the oil.
  - The largest, Pawnee's M5.8 of 3 September 2016, is the catalog's largest in the box; sixteen events of M5 and above in all, among them Prague (M5.7, 2011) and the Permian Basin's since 2020.

## The pulls

1. `earthquake.usgs.gov/robots.txt` (read 237): HTTP 404, the host has no robots file.
2. The count for the box (all event types): 16,050.
3. The service's parameter list (`application.json`).
4. The count, earthquakes only: 16,000.
5. The connector's trial: the query (2.9 MB CSV), saved and reused by the write (`--offline --end 2026-10-23`).

The USGS's terms are the record's (read 87, may be public: USGS-authored data are in the public domain).

## Errors

- **The first trial left 34 places blank** that end in a postal code ("2 km E of Choctaw, OK"); the codes were added and the trial run again offline (5 left blank, border regions and one named event).
- **This chain's first read was numbered 255** at chain 069's request, to keep clear of its reads; `tests/test_session152` requires the record numbered without a gap, so it is 237 and the chain that lands second renumbers. Chain 069's agent was told.

## Decisions made without you

- **Chain 079 taken while chain 069 runs**, under the owner's instruction; chain 069's agent's additions applied.
- **The four states' bounding box kept whole,** with the place's state as a column, rather than cut by a state polygon the ERW does not hold.
- **Earthquakes only** (the query's `eventtype=earthquake`): quarry blasts and explosions left out.
- **The origin time to the second as `event_date`** (the standard allows a UTC time when the time matters), the milliseconds kept in `x_time_utc`.
- **Sectors oil and gas,** the industry whose wastewater injection the table follows.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/usgs_earthquakes.py`, `tests/test_session2120.py`, this report; on main, `queue/next/090-day-29-october-data-wildfires-geomagnetic-inventory-carbon.md`.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `warehouse/metadata/license_reads.csv` (237), the coverage, sources, archive manifest and license files, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c079/` (the probe, the trial, the cross-check), `runs/license_reads/s2120/`, `runs/s2120_*`, `warehouse/raw/usgs_earthquakes/`.
