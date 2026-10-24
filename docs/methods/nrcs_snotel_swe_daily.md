# The snow above the West's reservoirs, a day's snow water equivalent at twenty SNOTEL stations (NRCS, Air and Water Database)

Energy Research Warehouse (ERW), method note written in session 2157 (chain 092) for a table first written on 23 October 2026 (session 2149).

Tables: `nrcs_snotel_swe_daily`

## Publisher and address

USDA Natural Resources Conservation Service (NRCS), National Water and Climate Center, the Air and Water Database (AWDB) REST service, no key. One request for the stations' metadata and one a basin:

`https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1/stations?stationTriplets=<the twenty>&returnForecastPointMetadata=false&returnReservoirMetadata=false&returnStationElements=false`

`https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1/data?stationTriplets=<a basin's>&elements=WTEQ&duration=DAILY&beginDate=2015-01-01&endDate=<today, UTC>`

The User-Agent is "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)". Source id `nrcs:awdb_snotel`. Connector: `warehouse/connectors/nrcs_snotel.py` (session 2149), its only table. wcc.sc.egov.usda.gov has no robots file (HTTP 404). Session 2149 chose the stations from NRCS's station list (729 stations in eight states): the highest of each basin's with a record from before October 2014, at most twenty.

The table is not scheduled: no line of `warehouse/run_daily.sh`, the other `warehouse/*.sh` scripts, `scripts/` or `.github/workflows/` names the connector (searched in session 2157), and `run_status.csv` holds no row for it. It was written once, by run `20261023T234102Z` on the data machine.

## Vintage and revision

1 January 2015 to 22 October 2026 (`ts_utc`). The run asked to 23 October 2026 (`endDate=2026-10-23`); the answers hold no row for that day. The answers were retrieved from 2026-10-23T23:39:45Z to 23:39:56Z by the session's trial and reused by the write run; `vintage` is empty. `coverage.csv` gives the same 86,241 rows, 20 entities and the same first and last `ts_utc`.

Each run writes the whole table again (`ip.write_snapshot`), and every request is asked again unless `--offline`, since the addresses stay as days are added. The header: NRCS's values are provisional for the current water year and revised by its quality control. SNOTEL's days are the station's local standard time; `ts_utc` is the day written at 00:00 UTC.

## Shape and variables

Series, 86,241 rows, twenty stations, one variable. `entity` `snotel:<station id>:<state, lower case>`; `variable` `snow_water_equivalent`; `unit` `in` (inches of water, NRCS's WTEQ, Decision 60); `freq` P1D; `geo` US-<state>; `market` empty; `node` the station's name; `x_basin` colorado, columbia or california (the group the station was chosen for); `x_huc` the 12-digit hydrologic unit; `x_elevation_ft`; `x_lat`; `x_lon`.

| Station (`x_basin`) | State | Elevation ft | Days | Mean in | Highest in | Days at 0 |
|---|---|---|---|---|---|---|
| 485 Fremont Pass (colorado) | CO | 11,310 | 4,313 | 6.79 | 28.1 (29 May 2019) | 1,368 |
| 335 Berthoud Summit (colorado) | CO | 11,300 | 4,313 | 6.87 | 25.3 (25 Apr 2020) | 1,489 |
| 1186 Fool Creek (colorado) | CO | 11,130 | 4,313 | 7.87 | 25.7 (26 Apr 2020) | 1,391 |
| 505 Grizzly Peak (colorado) | CO | 11,110 | 4,313 | 6.28 | 23.4 (1 May 2019) | 1,556 |
| 825 Tower (colorado) | CO | 10,610 | 4,313 | 16.44 | 58.0 (28 May 2019) | 1,341 |
| 717 Ripple Creek (colorado) | CO | 10,340 | 4,313 | 9.75 | 37.3 (7 Apr 2023) | 1,497 |
| 1117 Spirit Lk (colorado) | UT | 10,240 | 4,313 | 4.46 | 23.3 (26 Apr 2023) | 1,766 |
| 790 Steel Creek Park (colorado) | UT | 10,140 | 4,313 | 5.81 | 22.7 (25 Apr 2023) | 1,606 |
| 1249 Sunflower Flat (colorado) | UT | 10,010 | 4,313 | 3.95 | 25.8 (3 Apr 2023) | 2,001 |
| 313 Barker Lakes (columbia) | MT | 8,250 | 4,313 | 5.61 | 22.4 (16 Apr 2018) | 1,377 |
| 727 Saddle Mtn. (columbia) | MT | 7,890 | 4,313 | 8.90 | 35.7 (16 Apr 2018) | 1,481 |
| 850 Warm Springs (columbia) | MT | 7,840 | 4,313 | 9.43 | 40.0 (3 May 2018) | 1,303 |
| 606 Lyman Lake (columbia) | WA | 5,990 | 4,313 | 20.76 | 75.9 (5 May 2017) | 1,361 |
| 502 Green Lake (columbia) | WA | 5,920 | 4,312 | 7.21 | 31.1 (31 Mar 2016) | 1,885 |
| 692 Pigtail Peak (columbia) | WA | 5,800 | 4,313 | 17.15 | 69.1 (7 Apr 2020) | 1,416 |
| 832 Trough (columbia) | WA | 5,480 | 4,313 | 3.49 | 19.0 (21 Mar 2016) | 2,174 |
| 1067 Carson Pass (california) | CA | 8,360 | 4,313 | 9.67 | 68.3 (6 Apr 2023) | 1,941 |
| 356 Blue Lakes (california) | CA | 8,060 | 4,295 | 10.27 | 74.4 (8 Apr 2023) | 1,932 |
| 391 Cedar Pass (california) | CA | 7,060 | 4,313 | 4.76 | 29.6 (4 Apr 2023) | 2,147 |
| 428 Css Lab (california) | CA | 6,890 | 4,313 | 10.31 | 77.5 (8 Apr 2023) | 2,130 |

The lowest of every station is 0; no value is negative. The mean over all rows is 8.79 inches; the highest is 77.5 inches at Css Lab on 8 April 2023. From 1 January 2015 to 22 October 2026 there are 4,313 days: eighteen stations hold every one. Blue Lakes lacks 8 to 25 October 2015 (18 days) and Green Lake 8 September 2021: 19 station-days with no row.

The stations' mean on 1 April, by basin (inches): California 1.2 in 2015 (the least), 61.2 in 2023 (the most) and 4.9 in 2026; the Colorado headwaters 15.4 in 2015, 24.7 in 2023 (the most) and 9.9 in 2026 (the least); the Columbia 18.3 in 2015 (the least), 33.1 in 2018 (the most) and 23.9 in 2026. The counts were computed in session 2157 from the rows, read past the 10 header lines; no (entity, variable, ts_utc) is given twice.

## Checks the connector makes

- Before any request, NRCS's host is checked against `warehouse/metadata/paused_sources.csv` by connector and by host; a paused publisher stops the run with no request. It is not paused.
- The stations' metadata must list all twenty stations; each basin's answer must hold exactly the stations asked.
- Each station must hold one WTEQ series, stored in inches; a day given twice, a station with no day, or an (entity, variable, ts_utc) given twice stops the run, and nothing is written.
- A day NRCS returns with an empty value has no row and is counted in the header (none in this run). Nothing is filled.
- Ceiling: four requests a run (the metadata and one a basin), by the code's shape rather than a counter, all asked again unless `--offline`. Each address is tried up to four times, 5, 10 and 15 seconds apart (`ip.with_retries`); an HTTP 404 is not retried. One second after the metadata, two after each basin. `--end` sets the last day asked.

## The cross-check

Session 2149 set each basin's 1 April snow water equivalent (the stations' mean) against the April to September net generation of the Reclamation plant downstream (`usbr_hydropower_monthly`, 2015 to 2025) in `runs/c092/s2149/cross.py` (on the data machine, not in git). California against Shasta gave Pearson 0.72 (Spearman 0.76), with the drought years 2015, 2021 and 2022 lowest in both; the Columbia against Grand Coulee 0.43; the Colorado against Glen Canyon 0.26, which the report puts down to Lake Powell's releases following the annual operating tables rather than the year's snow.

## License

Internal. The header: "License: not settled (NRCS's terms were not found in session 2149; for the licenses round), held internal until a verdict. Cite the USDA Natural Resources Conservation Service." `sources.csv` and `coverage.csv`: internal. `license_verdicts.csv` holds no verdict for NRCS, and `docs/licenses.md` lists NRCS among the publishers not read ("not settled (needs written permission by default)", ERW verdict internal). Why: NRCS's policies address answered 404 in session 2149, and in session 2153's licenses round NRCS's site linked its policies on www.usda.gov, whose robots file refused the ERW's reader (HTTP 403); www.usda.gov is not asked again without a ruling. Session 2153 put the question to Samuel: is a federal agency's own data public under 17 U.S.C. 105 when its terms cannot be read, or should NRCS be asked? The table is in the live set's catalogue hold, not in the release's storage hold or the release package.

## Found while writing this note

- The header says "Days with no value have no row: 0", and session 2149's report says "no day missing". 19 station-days have no row: Blue Lakes (356:CA) 8 to 25 October 2015 and Green Lake (502:WA) 8 September 2021. The connector counts only the days NRCS returns with an empty value; a day NRCS does not return at all is not counted.
- Session 2149's report gives the range as "1 January 2015 to 23 October 2026". The rows, the header's first line and `coverage.csv` end on 22 October 2026; 23 October was asked and not returned.

**Acted on in session 2157:** the connector now counts the days with no entry at all inside a station's span beside the days NRCS returns empty, and the header names them (Green Lake 1, Blue Lakes 18: the 19 station-days this note found); the table was written again offline. Session 2149's report carries an addendum (the rows end on 22 October).

## What it does not hold

- Snow depth, precipitation, temperature or soil moisture: WTEQ only.
- NRCS's forecasts and its basin indexes.
- Stations other than these twenty, and days before 2015.
