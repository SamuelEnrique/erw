# The planetary geomagnetic index Kp, every three hours from 1932 (GFZ Potsdam's Kp and ap since 1932)

Energy Research Warehouse (ERW), method note written in session 2143 (chain 090) for a table first written on 23 October 2026 (session 2135).

Tables: `gfz_kp_index_3h`

## Publisher and address

GFZ Helmholtz Centre for Geosciences, Potsdam: the Kp index as its Geomagnetic Observatory Niemegk produces it (the file's SOURCE line), the record NOAA's Space Weather Prediction Center's storm scale reads. One text file, `https://kp.gfz-potsdam.de/fileadmin/files_for_gfz_cms/Kp_ap_since_1932.txt`, listed on the Kp Data page `https://kp.gfz-potsdam.de/en/data`. The address answers from `https://kp.gfz.de/fileadmin/files_for_gfz_cms/Kp_ap_since_1932.txt`: the raw manifest records the file under both. Source id `gfz:kp_ap_since_1932`. Connector: `warehouse/connectors/gfz_kp_index.py` (session 2135), one step: it asks, reads and writes in one run, or reads the saved file only with `--offline`.

## Vintage and revision

Intervals from 1 January 1932 00:00 UTC to 22 October 2026 21:00 UTC, 277,032 of them, none absent between. The table was first written by run `20261023T231855Z` (23 October 2026, session 2135). The file on the data machine was written again by run `20261023T233741Z` (session 2136, offline, under `runs/c090/rewrite.sh`): its header's license word changed to `public`, and its rows are unchanged ("the previous file held 277032 rows"). Both runs read the file that session 2135's trial saved (run `20261023T231700Z`, 16,623,882 bytes): every row's `retrieved_at` is 2026-10-23T23:17:02Z and its `vintage` 2026-10-22T23:52:43Z, the file's Last-Modified.

GFZ marks each interval definitive or preliminary. 276,856 rows are definitive, to 30 September 2026 21:00 UTC; 176 are preliminary, 1 to 22 October 2026. GFZ revises the latest intervals as observatories report, and each run replaces the table whole (`iso_prices.write_snapshot`), so a preliminary value becomes the definitive one at the next run after GFZ's. No job runs the connector: neither `warehouse/run_daily.sh` nor `warehouse/run_data_machine_tables.sh` names it, so the 176 preliminary intervals stay as they are until it is run again.

## Shape and variables

Series, 277,032 rows: one series. `entity` gfz:kp; `variable` kp; `unit` index; `freq` PT3H; `ts_utc` the interval's start (00, 03, ..., 21 UTC); `geo` and `market` empty; `node` planetary. The value is Kp in thirds, as GFZ writes it (5- is 4.667, 5o 5.000, 5+ 5.333): 28 values from 0 to 9, mean 2.172, median 2.0. Extra columns: `x_ap`, the interval's ap (unitless; GFZ's file: "can be multiplied by 2 nT to yield the average geomagnetic disturbance at 50 degree geomagnetic latitude"), from 0 to 400 and never empty; `x_status` definitive or preliminary.

| Decade | Intervals | Mean Kp | Intervals at 9o | Days with Kp 8- or more | Days with Kp 9o |
|---|---|---|---|---|---|
| 1930s | 23,376 | 1.94 | 1 | 25 | 1 |
| 1940s | 29,224 | 2.35 | 7 | 58 | 6 |
| 1950s | 29,216 | 2.62 | 4 | 69 | 4 |
| 1960s | 29,224 | 2.09 | 6 | 49 | 5 |
| 1970s | 29,216 | 2.34 | 2 | 37 | 2 |
| 1980s | 29,224 | 2.50 | 5 | 36 | 5 |
| 1990s | 29,216 | 2.32 | 0 | 40 | 0 |
| 2000s | 29,224 | 1.95 | 4 | 36 | 3 |
| 2010s | 29,216 | 1.62 | 0 | 9 | 0 |
| 2020s (to 22 October 2026) | 19,896 | 1.86 | 2 | 17 | 1 |

A day is a UTC day; Kp 8- (7.667) or more is NOAA's G4 or above, as session 2135 read the scale in thirds. In all, 31 intervals and 27 days reach 9o; the last such day is 11 May 2024. 6.92 percent of all intervals have Kp of 5- or more.

## Reading the source

- The run stops at once, asking nothing, while `gfz_kp_index` is in `paused_sources.csv` or kp.gfz-potsdam.de is a paused host (kp.gfz.de, where the file is answered from, is not asked about).
- The file goes through `iso_prices.fetch_raw`, asked fresh unless `--offline` (then only the saved copy is read). A request not answered with HTTP 200 is tried up to four times (`iso_prices.with_retries`, the waits 5, 10 and 15 seconds); HTTP 404 is not retried. Timeout 180 seconds; 1 second after the request. One document a run.
- `parse` keeps the lines beginning with `#` apart; the `# LICENSE:` and `# SOURCE:` lines (up to four) are copied into the table's header. Every other line must match `LINE`: the date, the interval's start and middle hour, the days since 1932 at each, Kp, ap and a one-digit status. A line not of that form, a status not 0 or 1, a start hour not on a three-hour boundary, or an interval not three hours after the one before stops the run, and no file is written.
- An interval GFZ marks missing (Kp below 0, GFZ's -1.000) is not written and is counted in the header (0 in this file). An ap below 0 is written as an empty `x_ap` (none in this file). A file with no interval, or an interval given twice, stops the run. Nothing is filled. The code counts no row ceiling.

## License

Public. `license_verdicts.csv` records GFZ Helmholtz Centre for Geosciences (Potsdam), read 299 (the header of `Kp_ap_since_1932.txt`, 23 October 2026): "may be public", for public and for commercial use. The sentence: "LICENSE: CC BY 4.0". The file asks two citations, both in the table's header: Matzka, Stolle, Yamazaki, Bronkalla and Morschhauser (2021), Space Weather, doi:10.1029/2020SW002641, and the data publication, GFZ Data Services, doi:10.5880/Kp.0001. The registry's word for an open license is `public`, which `sources.csv` gives `gfz:kp_ap_since_1932` since session 2136; `license_tables.csv` lists the table under GFZ. GFZ's Data page states no license (read 296). The read numbers are the branch's; the session reports say they are renumbered when the chain lands.

## Cross-checks (session 2143)

- The counts above were computed from the rows, read past the header lines. The file's rows are identical to the trial file `runs/c090/s2135/trial/gfz_kp_index_3h.csv` that session 2135's cross-check read, and the saved file holds 277,032 data lines, every one written. Every interval is three hours after the one before, and none is given twice.
- Each interval's ap against GFZ's fixed conversion of Kp to ap (0o 0, 0+ 2, ..., 9- 300, 9o 400): equal in all 277,032 rows.
- The storms NOAA names, in the rows: the highest Kp is 9o on 13 and 14 March 1989, on 29 and 30 October 2003 and on 11 May 2024; 8+ (8.333) on 31 October 2003 and on 11 October 2024; 9- (8.667) on 10 May 2024, 10 October 2024 and 12 November 2025. Session 2135's report (`archive/sessions/SESSION_2135_REPORT.md`, line 10) says "8+ on 10 May" and "The October 2024 storm reaches 8+ on 10 October"; the rows give 9- on both days. The report's other numbers agree with the rows: 376 days of Kp 8- or more, 27 of 9o, 22 since 2015 and 19 since 2016.
- Session 2135's comparison with OE-417 (`runs/c090/s2135/cross.out`): 9 of the 19 storm days from 2016 have a row in `doe_oe417_events`, and none of its rows names a geomagnetic or solar cause; `nrc_event_notifications` has no row on the four storm days since it begins (May 2025).

## What it does not hold

- Intervals after 22 October 2026 21:00 UTC, and the definitive values of the 176 preliminary intervals, until the connector is run again.
- The daily Ap, the day's mean of ap as the file defines it: it is not written, and can be computed from `x_ap`.
- NOAA SWPC's own estimated Kp and forecasts: SWPC's products hold only recent days (session 2135).
