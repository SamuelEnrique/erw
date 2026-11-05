# Wildfires of 1,000 acres or more from 2015, each fire's discovery, place, size and cause (NIFC's WFIGS Incident Locations)

Energy Research Warehouse (ERW), method note written in session 2143 (chain 090) for a table first written on 23 October 2026 (session 2134).

Tables: `wfigs_wildfires`

## Publisher and address

National Interagency Fire Center (NIFC), Wildland Fire Interagency Geospatial Services (WFIGS), "Incident Locations", which NIFC's open data site publishes (`https://data-nifc.opendata.arcgis.com/`). The connector asks the feature service's query address, `https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/WFIGS_Incident_Locations/FeatureServer/0/query`, with the filter `FireDiscoveryDateTime >= DATE '2015-01-01' AND IncidentTypeCategory = 'WF' AND COALESCE(FinalAcres,IncidentSize) >= 1000`, 15 fields (`FIELDS`), ordered by OBJECTID, `PAGE` (2,000) records a page, no geometry. Source id `nifc:wfigs_incident_locations`. Connector: `warehouse/connectors/wfigs_wildfires.py` (session 2134), one step: it asks, reads and writes in one run, or reads the saved pages only with `--offline`. `--min-acres` (default 1000) sets the threshold, which the header states. The open data site itself is not asked by the connector: its robots file (read 323) asks a 60-second crawl delay.

## Vintage and revision

6,222 fires discovered from 18 January 2015 (19:03 UTC) to 21 October 2026 (19:40 UTC). The file on the data machine was written by run `20261023T231301Z` (23 October 2026), offline, from the four pages that session 2134's trial saved (run `20261023T230959Z`). A run a minute earlier, `20261023T231224Z`, had written the same 6,222 rows first (its log: "previous file 0 rows"); the last run's header says "the previous file held 6222 rows". The session report names only the last run.

Every row's `retrieved_at` is its page's download: 2026-10-23T23:10:00Z, 23:10:03Z and 23:10:05Z (2,000 rows each) and 23:10:08Z (222). Every row's `vintage` is 2026-10-23T23:06:52Z, the Last-Modified the service gave all four pages. Each run replaces the table whole (`iso_prices.write_snapshot`): a fire whose record WFIGS changes (a final size, a containment or fire-out time) changes at the next run, and the record is operational, which the session report notes the service does not check after a fire is declared out. No job runs the connector: neither `warehouse/run_daily.sh` nor `warehouse/run_data_machine_tables.sh` names it, so the table holds the service as it stood on 23 October 2026.

## Shape and variables

Events, 6,222 rows, one a fire. `event_id` wfigs:<IRWIN id> (the IRWIN id lower case, its braces dropped); `event_date` the discovery's UTC day (equal to the date of `x_discovered_utc` in every row); `event_type` wildfire; `parties`, `entity_ids`, `mw`, `price` and `currency` empty in every row; `status` out (4,513 rows, a fire-out time given), contained (470, a containment time and no fire-out time), empty (1,239, neither; 250 of them discovered in 2026); `source_url` the layer's address. Extra columns: `x_name`, `x_state` (US-<state> as WFIGS writes POOState: 42 states, none empty; Alaska 737, California 597, Idaho 517, Arizona 428, Oklahoma 416), `x_county` (none empty), `x_latitude` and `x_longitude` (InitialLatitude and InitialLongitude, given for 5,086 fires), `x_final_acres` (given for 493), `x_incident_size_acres` (given for 6,198; both for 469, which differ in 29), `x_cause_general` (given for 1,151, of which 337 and 395 in 2021 and 2020), `x_cause` (given for 6,075), `x_discovered_utc`, `x_contained_utc` (4,582), `x_out_utc` (4,513), `x_unique_fire_id`.

| Year | Fires | Acres (final, else incident size) | Largest fire, acres |
|---|---|---|---|
| 2015 | 630 | 11,812,060 | 498,043 |
| 2016 | 508 | 4,213,427 | 367,740 |
| 2017 | 665 | 9,910,420 | 662,700 |
| 2018 | 560 | 7,482,782 | 416,821 |
| 2019 | 379 | 4,395,766 | 308,923 |
| 2020 | 509 | 10,284,058 | 589,368 |
| 2021 | 428 | 6,987,434 | 963,309 |
| 2022 | 543 | 6,843,982 | 341,735 |
| 2023 | 365 | 2,184,760 | 135,000 |
| 2024 | 584 | 8,389,787 | 1,054,150 |
| 2025 | 461 | 4,467,912 | 145,504 |
| 2026 (to 21 October) | 590 | 8,321,062 | 642,029 |

The year is the discovery's. The largest fires are Smokehouse Creek (Texas, discovered 26 February 2024, 1,054,150 acres) and DIXIE (California, 14 July 2021, 963,309). The fire counts agree with the header's line by year.

Four unique fire identifiers are each given under two IRWIN records, and both records are kept: 2015-WAYAA-000157 (Cougar Creek and COUGAR CREEK, 53,523 and 53,534 acres), 2016-MTLCF-000011 (ELK HILL, 1,089 both), 2016-NMN3S-000040 (Bruton, 2,337 and 2,331) and 2018-OKECU-180143 (SIX THOUSAND, 3,900 both). A sum of acres over the table counts these four twice.

## Reading the source

- The run stops at once, asking nothing, while `wfigs_wildfires` is in `paused_sources.csv` or services3.arcgis.com is a paused host.
- Each page goes through `iso_prices.fetch_raw`, asked fresh unless `--offline` (then only a saved page is read, and a page not saved is an error). A page not answered with HTTP 200 is tried up to four times (`iso_prices.with_retries`, the waits 5, 10 and 15 seconds); HTTP 404 is not retried. Timeout 120 seconds; 2 seconds after each page asked.
- The next page starts at the records read so far. The run ends at the first page that does not say `exceededTransferLimit`, or at an empty page. After a page the run stops when more than 20 pages have been read: a 21st page that says more remain stops it, and no file is written. The docstring's ceiling, "one request a page (four for 2015 to October 2026)", names no page limit.
- `rows_of` stops the run when the service answers an error, when a page has no features, when a record lacks any of the 15 fields, when a record has no IRWIN id or no discovery time, or when a time is not a number of milliseconds. After all pages, an IRWIN id given twice stops it. A unique fire identifier given twice does not; the header counts those (4).
- Numbers are written as published (`%g`); nothing is filled. The code counts no row ceiling.

## License

Public. `license_verdicts.csv` records National Interagency Fire Center (NIFC), read 326 (the WFIGS item's license and access information on ArcGIS Online, 23 October 2026): "may be public", for public and for commercial use. The sentence: "The National Interagency Fire Center shall not be held liable for improper or incorrect use of the data described and/or contained herein." The verdict's note: the license field is a disclaimer of liability and places no restriction on use (session 2139). The header asks the citation "National Interagency Fire Center, WFIGS". `sources.csv` flags `nifc:wfigs_incident_locations` public; `license_tables.csv` lists the table under NIFC. The read numbers are the branch's; the session reports say they are renumbered when the chain lands.

## Cross-checks (session 2143)

- The counts above were computed from the rows, read past the header lines. The file's rows are identical to the trial file `runs/c090/s2134/trial/wfigs_wildfires.csv` that session 2134's cross-check read.
- Every `event_id` appears once. Every fire's acres (the final acres, else the incident size, the filter's own rule) is at least 1,000; one fire has an incident size under 1,000 and a final size at or above it. No containment time is before its discovery; among the 4,582 fires with one, the median is 10.2 days after discovery.
- Against NIFC's yearly acres for fires of every size (www.nifc.gov, read in session 2134, `runs/c090/s2134/cross.out`): the table holds 76.5 percent (2016) to 116.7 percent (2015) of each year's acres from 2015 to 2025. The fires under 1,000 acres are not in the table, so a share under 100 percent is expected; a share over it means the two records count acres differently, not checked fire by fire.
- Session 2134's script found 5,086 fires with a point of origin, 736 of them within 10 km of a plant in `eia860_plants_annual` and 223 within 10 km of a turbine in `uswtdb_wind_turbines`. The script's docstring says the plants of the latest year; its code and its output use the plants of every year.

## What it does not hold

- Fires under 1,000 acres, and incidents other than wildfires (prescribed fires and others the service types apart).
- Fires discovered before 2015.
- The fire perimeters: no geometry is asked.
- Fires discovered after 21 October 2026, and later changes to the records held, until the connector is run again.
