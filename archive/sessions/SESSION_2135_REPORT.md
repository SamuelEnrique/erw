# Session 2135 report: the geomagnetic storms (GFZ Potsdam's Kp)

23 October 2026, from 23:15 UTC, on lab-desktop (the data machine), chain 090, unattended. Model spend USD 0. Pulls: 5 requests of 15 (4 by the probe, 1 file by the connector's trial; the write ran offline).

## Read these first

- **A new table, `gfz_kp_index_3h`** (series, 277,032 rows, `power`): the planetary geomagnetic index Kp, every three hours from 1 January 1932 to 22 October 2026 21:00 UTC. The source is GFZ Helmholtz Centre for Geosciences' `Kp_ap_since_1932.txt`, the record NOAA's storm scale reads. Kp is in thirds with the unit `index` (no new unit); ap and the status are kept beside it (276,856 definitive, 176 preliminary). No interval is missing. Written, validated (0 errors, 0 warnings), archived, held from the Redivis storage and the live set.
- **The license is stated in the file itself:** its header reads "LICENSE: CC BY 4.0" and names two citations (Matzka et al. 2021, Space Weather; the data publication, doi:10.5880/Kp.0001). Both are in the table's header. GFZ's Data page states no license, and the DOI's host (dataservices.gfz-potsdam.de) timed out at its robots file, so it was not asked further. The verdict waits for the licenses round (session 2139), with read 332 as its read.
- **Why not SWPC's products:** they hold only recent days (the chain file's own alternative). services.swpc.noaa.gov has no robots file (404) and was not asked for data.
- **The cross-check against the storms NOAA names:** Kp reaches 9o on 13 and 14 March 1989, 29 and 30 October 2003 and 11 May 2024 (9- on 10 May). The October 2024 storm reaches 9- on 10 October and 8+ on 11 October. All 376 days with Kp of 8- or more count as G4 or above; 27 reach 9o. Since 2015 there are 22 such days.
- **OE-417 on those days:** of the 19 storm days from 2016, 9 have an OE-417 row (10 May 2024: 3; 12 August 2024, 10 and 11 October 2024, 12 November 2025: 2 each), against a mean of 1.89 rows a day on days with any. No OE-417 row names a geomagnetic or solar cause.
- **NRC on those days:** `nrc_event_notifications` begins in May 2025, and none of its rows falls on the four storm days since then.
- **`tests/test_session205.py`'s bound raised by 40**, with room for this chain's licenses round.

## Requests (5 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | kp.gfz-potsdam.de/robots.txt | 404 |
| 2 | services.swpc.noaa.gov/robots.txt | 404 |
| 3 | kp.gfz-potsdam.de/en/data | 200: the files; no license on the page |
| 4 | dataservices.gfz-potsdam.de/robots.txt | timed out |
| 5 | Kp_ap_since_1932.txt (the trial; redirected to kp.gfz.de) | 200, 16.6 MB, last modified 22 October 23:52 GMT |

Reads recorded: 328 to 332 (probe requests 1, 3, 4 and 2, then the file's header) (renumbered at session 2147's merge, after chains 069 and 079's).

## Decisions made without you

- **GFZ's record rather than SWPC's.** SWPC's products hold only recent days.
- **ap kept as `x_ap` beside Kp, not as a second variable.** GFZ calls it unitless, and it is in units of 2 nT.
- **G4 counted as Kp 8- (7.667) or more**, NOAA's scale read in thirds.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/gfz_kp_index.py`, `tests/test_session2135.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`, the license record, `tests/test_session205.py`.
- On the data machine only: `runs/c090/s2135/`, `warehouse/raw/gfz_kp_index/`, `warehouse/output/gfz_kp_index_3h.csv`.
