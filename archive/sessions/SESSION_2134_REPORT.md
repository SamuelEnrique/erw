# Session 2134 report: the fires near the grid (NIFC's WFIGS wildfires)

23 October 2026, from 23:03 UTC, on lab-desktop (the data machine), the first session of `queue/done/090-day-29-october-data-wildfires-geomagnetic-inventory-carbon.md`, unattended, run by chain 058's agent beside chains 069 and 079 under other agents. Model spend USD 0. Pulls: 13 requests of 15 (9 by the probe, 4 pages by the connector's trial; the write ran offline).

## Read these first

- **The next file first:** `queue/next/092-day-30-october-data-bpa-snowpack-access-outlook-permits.md` (sessions 2148 to 2161) written, committed alone and pushed to main (`bf722ed1`) before any other work.
- **A new table, `wfigs_wildfires`** (events, 6,222 rows, `power`): every wildfire of 1,000 acres or more discovered from 18 January 2015 to 21 October 2026, from the Wildland Fire Interagency Geospatial Services' Incident Locations feature service, which the National Interagency Fire Center publishes. Each fire has its discovery day and time, its containment and fire-out times where given, its state and county of origin, the point of origin, the final acres and incident size as published, and the cause. Written, validated (0 errors, 0 warnings), archived (6,222 rows), held from the Redivis storage and the live set. Its license is unsettled until the licenses round (session 2139): the item's license field is a disclaimer of liability, not a restriction.
- **Cross-check against NIFC's yearly totals** (www.nifc.gov's Wildfires and Acres page, all fires of every size). From 2015 to 2025 the table's fires hold between 76 and 117 percent of NIFC's acres: 98.8 percent in 2017, 101.6 in 2020, 98.1 in 2021, 94.0 in 2024, but 76.5 in 2016 and 116.7 in 2015. The fires below 1,000 acres explain the years under 100 percent. In 2015, the excess is consistent with operational records the service says are "not QA/QC'd after a fire is declared out". That is a reading of the numbers, not a check of each record.
- **The fires near the grid:** 5,086 of the 6,222 fires give a point of origin. Of those, 736 started within 10 km of a plant in `eia860_plants_annual` (any year), most in California (131), Washington (90), Texas (88), Idaho (80) and Oregon (76); 223 started within 10 km of a turbine in `uswtdb_wind_turbines`.
- **The table was written twice** (found by session 2143): the first write, run `20261023T231224Z`, wrote the file, then stopped at the coverage step (the fault below), and the second, run `20261023T231301Z`, wrote it again with its coverage and archive. The rows are the same.
- **A fault fixed in `build_coverage.py --only`:** a new table whose name falls after the last table in `docs/coverage.md` had no place there (`wfigs_wildfires` was the first such name). It now goes in after the last line.

## The source

- `https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/WFIGS_Incident_Locations/FeatureServer/0/query`, filtered on `FireDiscoveryDateTime >= DATE '2015-01-01' AND IncidentTypeCategory = 'WF' AND COALESCE(FinalAcres,IncidentSize) >= 1000`, in pages of 2,000 ordered by OBJECTID: four pages (2,000, 2,000, 2,000 and 222).
- The layer holds 97 fields. A count query gave 6,222 before the pull, and the pull returned 6,222.
- Without the 1,000-acre threshold the service holds tens of thousands of fires a year, more than the ceiling's pages allow. The threshold is written in the table's header.
- **Four fire identifiers each appear under two IRWIN records.** Examples: COUGAR CREEK 2015 (53,534 and 53,523 acres), SIX THOUSAND 2018, Bruton 2016. The IRWIN ids are unique and none is empty, so the table is keyed on `wfigs:<IRWIN id>`; the unique fire identifier is kept in `x_unique_fire_id`. The header counts the doubles, and both records are kept as published.

## Requests (13 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | data-nifc.opendata.arcgis.com/robots.txt | 200: Crawl-delay 60; disallows site paths, not the services |
| 2 | services3.arcgis.com/robots.txt | 403 Invalid URL (an API host) |
| 3 | the layer's metadata | 200: 97 fields, maxRecordCount 2000 |
| 4 | the count query | 200: 6,222 |
| 5 | the service root | 200: its item id |
| 6 | www.arcgis.com/robots.txt | 200: no Disallow line |
| 7 | the item on ArcGIS Online | 200: the license and access information |
| 8 | www.nifc.gov/robots.txt | 200: site administration paths only |
| 9 | www.nifc.gov's Wildfires and Acres page | 200: the yearly totals, 1983 to 2025 |
| 10 to 13 | the connector's four pages (trial) | 200 each |

Reads recorded in `warehouse/metadata/license_reads.csv`: 302 to 306 (probe requests 1, 2, 6, 7 and 8; 256 to 260 on the branch, then 290 to 294renumbered at session 2147's merge, after chains 069 and 079's).

## Decisions made without you

- **The 1,000-acre threshold.** It keeps the session within its ceiling, and it keeps the large fires that reach lines and plants.
- **Keyed on the IRWIN id.** The unique fire identifier is given twice for four fires; both records are kept rather than one chosen.
- **The status:** `out` where a fire-out time is given, `contained` where a containment time is, else empty.
- **The `build_coverage.py --only` fix** (above), made on the branch.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/wfigs_wildfires.py`, `tests/test_session2134.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py` (the sector rule, the placement fix), `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`, the license record (`license_reads.csv`, `license_tables.csv`, `docs/licenses.md`).
- On the data machine only: `runs/c090/s2134/`, `warehouse/raw/wfigs_wildfires/`, `warehouse/output/wfigs_wildfires.csv`.
