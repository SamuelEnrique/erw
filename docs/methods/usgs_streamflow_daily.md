# The rivers below eight large hydropower plants, a day's mean flow (USGS, NWIS daily values, discharge)

Energy Research Warehouse (ERW), method note written in session 2116 (chain 069) for a table first written on 23 October 2026 (session 2113).

Tables: `usgs_streamflow_daily`

## Publisher and address

U.S. Geological Survey (USGS), National Water Information System (NWIS), the daily values service, tab-delimited (rdb), parameter 00060 (discharge) and statistic 00003 (daily mean), from 1 January 2015, one request a gauge:

`https://waterservices.usgs.gov/nwis/dv/?format=rdb&sites=<site>&parameterCd=00060&statCd=00003&startDT=2015-01-01`

The User-Agent is "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)". Source id `usgs:nwis_daily_values`. Connector: `warehouse/connectors/usgs_streamflow.py` (session 2113), its only table. waterservices.usgs.gov has no robots file (HTTP 404). Session 2113 chose this service over its successor, api.waterdata.usgs.gov, because it still answers, needs no key and gives the qualification codes; a code chain moves the connector when the USGS retires it.

The table is not scheduled: no line of `warehouse/run_daily.sh`, the other `warehouse/*.sh` scripts, `scripts/` or `.github/workflows/` names the connector (searched in session 2116), and `run_status.csv` holds no row for it. It was written once, by run `20261023T223937Z` on the data machine.

## Vintage and revision

1 January 2015 to 22 October 2026 (`ts_utc`). The answers were retrieved from 2026-10-23T22:37:20Z (The Dalles, the session's probe, reused) to 22:38:29Z (the trial run `20261023T223816Z`), and reused by the write run; `vintage` is empty. `coverage.csv` gives the same 33,421 rows, 8 entities and the same first and last `ts_utc`.

Each run writes the whole table again (`ip.write_snapshot`). Provisional values (code P) are released by the USGS without liability and can be revised; approved values revised later carry R. The USGS's daily values are local calendar days; `ts_utc` is the day written at 00:00 UTC.

## Shape and variables

Series, 33,421 rows, eight gauges, one variable. `entity` `usgs_gauge:<site number>`; `variable` `discharge`; `unit` `ft3/s` (cubic feet a second, Decision 64; a day's volume is the rate times 86,400 seconds); `freq` P1D; `geo` US-<state> (Hoover's gauge, on the Arizona and Nevada line, is US-AZ; Hells Canyon's, on the Idaho and Oregon line, US-OR; the gauge's name in `node` says both); `market` empty; `node` the gauge's name as the USGS gives it; `x_site`; `x_plant` the plant above the gauge; `x_qual` the USGS's codes.

| Gauge (`x_plant`) | Days | First | Last | Mean ft3/s | Lowest | Highest |
|---|---|---|---|---|---|---|
| 14105700 Columbia River at The Dalles, OR (The Dalles) | 4,311 | 1 Jan 2015 | 22 Oct 2026 | 161,571 | 62,300 (23 Sep 2018) | 513,000 (21 May 2018) |
| 12436500 Columbia River at Grand Coulee, WA (Grand Coulee) | 4,259 | 1 Jan 2015 | 31 Aug 2026 | 99,533 | 34,600 (23 Sep 2023) | 283,000 (13 May 2018) |
| 09421500 Colorado River below Hoover Dam, AZ-NV (Hoover) | 4,054 | 1 Jan 2015 | 5 Feb 2026 | 11,804 | 1,280 (27 Nov 2025) | 26,200 (30 Apr 2015) |
| 09380000 Colorado River at Lees Ferry, AZ (Glen Canyon) | 4,310 | 1 Jan 2015 | 22 Oct 2026 | 11,377 | 4,170 (19 Mar 2021) | 39,600 (25 Apr 2023) |
| 06342500 Missouri River at Bismarck, ND (Garrison) | 4,313 | 1 Jan 2015 | 22 Oct 2026 | 21,999 | 12,000 (20 Nov 2015) | 61,100 (29 Jun 2018) |
| 13290450 Snake River at Hells Canyon Dam, ID-OR (Hells Canyon) | 3,935 | 1 Jan 2015 | 9 Oct 2025 | 15,684 | 6,570 (14 May 2015) | 72,500 (31 Mar 2017) |
| 11370500 Sacramento River at Keswick, CA (Shasta) | 4,313 | 1 Jan 2015 | 22 Oct 2026 | 7,984 | 2,910 (23 Dec 2022) | 79,000 (14 Feb 2017) |
| 11407000 Feather River at Oroville, CA (Oroville) | 3,926 | 1 Jan 2015 | 30 Sep 2025 | 2,018 | 505 (4 Nov 2023) | 105,000 (14 Feb 2017) |

From 1 January 2015 to 22 October 2026 there are 4,313 days; Garrison and Shasta hold every one. Days missing inside a gauge's span: Glen Canyon 3 (30 June, 10 and 11 October 2026), Grand Coulee 2 (30 April and 31 December 2021), The Dalles 2 (30 September and 1 October 2026). Hoover, Hells Canyon and Oroville have no day missing inside their spans; their series end early (5 February 2026, 9 October 2025, 30 September 2025), and Grand Coulee's ends on 31 August 2026. `x_qual`: A 24,772, A:R 6,074 (Grand Coulee 2,895, Hoover 2,449, Oroville 730), P 1,240, A:e 1,232 (Garrison 1,006), P:e 103; provisional rows (P or P:e) 1,343, as the header says. No value is 0 or negative, and no day was written as a code. The counts were computed in session 2116 from the rows, read past the 10 header lines; no (entity, variable, ts_utc) is given twice.

## Checks the connector makes

- Before any request, waterservices.usgs.gov is checked against `warehouse/metadata/paused_sources.csv` by connector and by host; a paused publisher stops the run with no request. It is not paused.
- Each answer must name the one gauge asked ("USGS <site> <name>") in its comment lines, and hold the columns agency_cd, site_no, datetime and one 00060_00003 value column with its `_cd` column, or the run stops.
- A line of the wrong number of fields, a line of another gauge, a day that does not read or is given twice, an answer with no day, a gauge with no value, or a key given twice stops the run, and nothing is written.
- A day the USGS writes as a code instead of a number (Ice, Eqp, Ssn, Dis and the like) has no row and is counted in the header (none in this run). Provisional values are kept with their P code. Nothing is filled.
- Ceiling: one request a gauge, eight a run, by the code's shape rather than a counter; two seconds after each request. Each address is tried up to four times, 5, 10 and 15 seconds apart (`ip.with_retries`); an HTTP 404 is not retried.

## The cross-check

Session 2113 set each gauge's yearly mean flow against the yearly net generation of the Reclamation plant above it (`usbr_hydropower_monthly`, full years 2015 to 2024) in `runs/c069/s2113/cross.py` (on the data machine, not in git). The Pearson correlations are Hoover 0.96, Glen Canyon 0.96, Grand Coulee 0.98 and Shasta 0.94 (Spearman 0.95, 0.95, 0.95 and 0.89), with wetter years the bigger years; the other four plants are not Reclamation's and were not checked.

## License

The header: "License: may be public (USGS: USGS-authored or produced data and information are in the public domain; see license_verdicts.csv). Cite the U.S. Geological Survey." `license_verdicts.csv` gives the USGS "may be public" (read 87, session 496; the same if the ERW sells anything), and `docs/licenses.md` gives the ERW verdict public. `coverage.csv`: public. Session 2113's report holds the table in the live set's catalogue hold and the release's storage hold.

## Found while writing this note

- Session 2113's report says "some gauges have days with no line at all, so they have fewer rows: Oroville 3,926, Hells Canyon 3,935, Hoover 4,054, of 4,313 days". The rows show no day missing inside those three gauges' spans: each series ends early (Oroville on 30 September 2025, Hells Canyon on 9 October 2025, Hoover on 5 February 2026). The days missing inside a span are at Glen Canyon (3), Grand Coulee (2, and its series ends on 31 August 2026) and The Dalles (2).
- The docstring says the answers are "saved in warehouse/raw/usgs_streamflow/ and reused offline". The code calls `ip.fetch_raw` without `fresh`, which reuses a saved copy on every run, offline or not: a later run reads the answers of 23 October 2026 again and gains no day, and no revised value, until the raw files are moved.
**Acted on in session 2116:** the connector now asks for its documents again unless `--offline` (`fresh=not args.offline`), so a later run sees a newer day and a revised value; the source registry's license word is now `public`. Session 2113's sentence on the shorter gauges is corrected in an addendum to its report.

## What it does not hold

- Gauge height, reservoir storage or water temperature: discharge only.
- Instantaneous (15-minute) values: daily means only.
- Days before 2015, and gauges other than these eight.
- The generation of The Dalles, Garrison, Hells Canyon and Oroville, which are not Reclamation's plants.
