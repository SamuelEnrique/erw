# Earthquakes of magnitude 2.5 and above in the box around Oklahoma, Kansas, Texas and New Mexico, from 2010 (USGS ComCat)

Energy Research Warehouse (ERW), method note written in session 2129 (chain 079) for a table first written on 23 October 2026 (session 2120, `archive/sessions/SESSION_2120_REPORT.md`).

Tables: `usgs_comcat_earthquakes_south_central`

## Publisher and address

U.S. Geological Survey (USGS) Earthquake Hazards Program, ANSS Comprehensive Earthquake Catalog (ComCat), through the FDSN event web service (no key), one query answered as CSV:

`https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&eventtype=earthquake&orderby=time-asc&starttime=2010-01-01&endtime=2026-10-23&minmagnitude=2.5&minlatitude=25.8&maxlatitude=40.0&minlongitude=-109.06&maxlongitude=-93.5`

Source id `usgs:comcat`. The answer (2,928,888 bytes) is saved under `warehouse/raw/usgs_earthquakes/`.

Connector: `warehouse/connectors/usgs_earthquakes.py` (session 2120): `[--end YYYY-MM-DD] [--offline] [--out-dir DIR]`; the end day defaults to today (UTC) and is not included. Ceiling one request. An answer of 20,000 rows (the service's limit a query) stops the run. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. `coverage.csv` gives the sectors oil and gas.

## Vintage and revision

One run, `20261023T222922Z`, reading the answer retrieved at 2026-10-23T22:27:51Z (the service's last-modified time 2026-10-23T22:27:43Z); every row carries that `retrieved_at` and the one query address. The table is a snapshot: each run replaces it whole ("the previous file held 0 rows"). `x_updated_utc` keeps each event's last update in the catalog, so a later run takes whatever the catalog then holds.

## Shape and columns

Events, 16,000 rows, one an earthquake. `event_id` `usgs_comcat:<the catalog's preferred id>`; `event_date` the origin time in UTC to the second; `event_type` earthquake in every row; `status` the catalog's review status (reviewed 15,997, automatic 3); `parties`, `entity_ids`, `mw`, `price` and `currency` empty. The `x_` columns, as published:

| Column | What it holds | Blank in |
|---|---|---|
| `x_time_utc` | the origin time with the catalog's milliseconds | 0 |
| `x_latitude`, `x_longitude` | degrees: 25.8001 to 39.9889, -109.0587 to -93.5339 | 0 |
| `x_depth_km` | km: -1.25 to 56.21 | 0 |
| `x_magnitude`, `x_magnitude_type` | 2.5 to 5.8; ml 13,240, mb_lg 1,521, mwr 670, mblg 188, md 166, ml(texnet) 145, others 70 | 0 |
| `x_place` | the catalog's place, usually "N km DIR of Town, State" | 0 |
| `x_place_state` | the state or country the place names (below) | 5 |
| `x_net` | the contributing network: us 11,550, tx 3,715, ok 646, ismpkansas 75, uu 11, nm 3 | 0 |
| `x_location_source`, `x_magnitude_source` | the catalog's sources | 0 |
| `x_stations`, `x_gap_degrees` | station count, azimuthal gap | 10,278 and 626 |
| `x_horizontal_error_km`, `x_depth_error_km`, `x_magnitude_error` | errors as published | 2,629, 714 and 8,456 |
| `x_updated_utc` | the event's last update in the catalog | 0 |

`x_place_state` counts: Oklahoma 9,488, Texas 2,822, New Mexico 2,167, Kansas 1,004, Colorado 373, Mexico 107, Louisiana 11, Utah 10, Arizona 5, Arkansas 3, Nebraska 3, Missouri 2, none 5. The box is the four states' bounding box and is not cut to state lines: a place names its nearest town, which can lie across a line, so a reader filters on `x_place_state` (or on the coordinates).

## Placing events in time

`event_date` is the catalog's `time` cut to the second with a `Z`; it equals the first 19 characters of `x_time_utc` in all 16,000 rows. The query asks `starttime=2010-01-01` and `endtime` the run's day, both read by the service as UTC.

## What is and is not filled

- Earthquakes only (`eventtype=earthquake`): quarry blasts and explosions are not asked for.
- `x_place_state`: the text after the place's last comma when it is a state (or Mexico) or one of the postal codes in the code; otherwise a place that is a state's name, or a direction followed by a state's name ("western Texas"); otherwise blank. The five blanks: "Texas-Chihuahua border region" (2), "Texas Panhandle region", "Arkansas-Oklahoma border region", "2024 North of Tarzan, Texas Earthquake".
- Values as published; blanks stay blank; nothing is filled. A header not the catalog's, an event twice, a time not the catalog's form or a magnitude below 2.5 stops the run.

## License

Header: "License: USGS-authored data, in the U.S. public domain. Cite: U.S. Geological Survey, Earthquake Hazards Program, ANSS Comprehensive Catalog (ComCat), doi:10.5066/F7MS3QZH." `license_verdicts.csv` records the USGS, read 87: "may be public", for public and for commercial use. `docs/licenses.md`: "may be public", flag public, ERW verdict public.

## Checks (session 2129)

The figures in this note were computed from the rows of `warehouse/output/usgs_comcat_earthquakes_south_central.csv`, read past its 10 header lines (scripts in `runs/c079/s2129/`).

- 16,000 rows, 16,000 distinct `event_id`; `event_date` from 2010-01-01T18:45:51Z to 2026-10-22T05:48:51Z, matching the header's "16000 earthquakes, magnitude 2.50 to 5.80". Every point lies inside the query's box.
- Magnitude 3 and above: 4,973 events; 4 and above: 271; 5 and above: 16. The largest is M5.8, 14 km NW of Pawnee, Oklahoma, 2016-09-03T12:02:44Z.
- Events a year, all states: 182 (2010), 272, 138, 377, 2,104 (2014), 3,092 (2015), 2,115, 1,150, 807, 474, 498, 897, 972, 893, 771, 665 (2025), 593 (2026 to 22 October).
- Session 2120's cross-check (`runs/c079/s2120/cross.py`), run again: its output is identical to the saved `cross.out`. Oklahoma (by the place's state), magnitude 2.5 and up a year: 141, 149, 80, 254, 1,883, **2,764 (2015)**, 2,003, 924, 572, 217, 126, 117, 75, 53, 65, 28, 37; magnitude 3 and up: 41, 63, 34, 103, 585, **885 (2015)**, 639, 264, 164, 55, 36, 27, 15, 16, 23, 6, 8. Beside Oklahoma's crude production (`eia_crude_production_state_monthly`, thousand barrels summed over the year): 165,548 in 2015, 165,891 in 2017, 217,484 in 2019, 147,467 in 2025. The 16 events of M5 and above are listed there, from Valdez, Colorado (M5.3, 2011-08-23) to Spearman, Texas (M5.0, 2026-07-23).

## Where the description and the data disagree

1. **16,050.** The docstring says "the count for the box was 16,050 on 23 October 2026". The query the connector sends (earthquakes only) returns 16,000 rows; session 2120's report gives 16,050 as the count with quarry blasts and explosions, which the query leaves out.
2. **Places that name one state but are blank.** The docstring says a place "that names no single state ("Texas-Chihuahua border region") is blank". Two blanks name Texas alone: "Texas Panhandle region" and "2024 North of Tarzan, Texas Earthquake" (its last comma leaves "Texas Earthquake", which the code does not match).
3. **The header's list by state stops at ten.** Header line 3 names ten groups summing to 15,992; Arkansas (3), Nebraska (3) and Missouri (2) are left out because the code prints only the first ten (`by.head(10)`).

## The session report against the table

Every figure of `SESSION_2120_REPORT.md` checked against the table and the rerun cross-check holds (16,000 events, magnitudes 2.50 to 5.80, the by-state counts it names, the Oklahoma counts and production figures, sixteen events of M5 and above, Pawnee's M5.8 the largest, the 2.9 MB answer), except:

- "a few in Louisiana, Utah and Arizona, 5 naming none": the table also holds 3 in Arkansas, 3 in Nebraska and 2 in Missouri.
- "5 left blank, border regions and one named event": three are border regions and one a named event; the fifth, "Texas Panhandle region", is neither.

The Oklahoma Geological Survey's counts (585 and 903) and the catalog's 16,050 are outside the table and were not checked.

Acted on in session 2129: the docstring now gives the earthquakes' count, 16,000 (16,050 with the blasts and explosions), and names the places left blank; the header now lists every state the places name, not the first ten (the table was written again offline, its rows unchanged); session 2120's report is corrected on the small states and the blanks.

## What it does not hold

- Events below magnitude 2.5, before 2010, outside the box, or of another type (quarry blasts, explosions).
- Injection wells, volumes or any production figure (those are other tables).
