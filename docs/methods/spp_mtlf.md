# SPP's mid-term load forecast beside its actual load (`spp_mtlf_hourly`)

Session 10000 (chain 701), 28 November 2026, for predict data request 19 (window2's cross-check of a third place: SWPP's
day-ahead forecast as filed on EIA-930 sits at 104 to 116 percent of its demand from May 2025, while SPP's own
forecast is said to err near 2 percent).

## The source

SPP's marketplace portal keeps, in its file browser `mtlf-vs-actual` (the page https://portal.spp.org/pages/mtlf-vs-actual),
one file an hour, `OP-MTLF-<YYYYMMDDHH00>.csv`, the hour in central prevailing time. Each holds SPP's mid-term load forecast
(MTLF) for the hours ahead and the averaged actual load of the hours just past. A finished year is one zip of its files
(2013 to 2024 on 28 November 2026); the years since are folders of days. Two layouts:

- the early files (from June 2013): `Interval` (SPP's hour ending, central prevailing time), `MTLF`, `Averaged Actual`,
  for SPP's footprint alone, about a day and a half of hours; some files of 2017 write the hour without seconds;
- the later files: `Interval`, `GMTIntervalEnd`, `MTLF`, `Averaged Actual` and `BAA`, seven days ahead, for SPP's
  footprint (`SPP`) and, from April 2026, its western area (`SWPW`).

SPP's portal has no robots file (`/robots.txt` answers its page shell), nor has www.spp.org (license read 1656). SPP's
terms (license read 1671, verdict row 7) let the files be copied with citation except within a commercial publication,
as for the other portal files the warehouse holds.

## What the table holds

One file a day, the one published at 09:00 central time, before SPP's day-ahead market closes, every row of it:
`load_forecast_mtlf_mw` and `load_actual_mw` (MW) by `spp:<BAA>`, `ts_utc` the hour's start, `vintage` the hour the file
was published (UTC), `x_horizon_hours` from publication to the hour's start (negative for an hour already past),
`x_interval_end_cpt` SPP's own label and `x_file` the file read. Revisions are kept: a forecast once made is never
replaced, and each publication's actuals stand as printed. An empty cell is no row; nothing is filled.

The early files give no UTC time, and at the autumn change their label repeats (two rows labelled 01:00 on 3 November
2013). Their rows run one hour apart, newest first, so the first row's hour is read from its label (a morning hour at a
09:00 publication, never ambiguous) and each row after it is one hour earlier. On 3 November 2013 this puts the hour
ending 00:00 CDT at 05:00 UTC, the first 01:00 (CDT) at 06:00 UTC and the second 01:00 (CST) at 07:00 UTC; all 182
files of 09:00 in 2013 read this way.

The first writing (28 November 2026) read the zips of 2013 to 2024 and the day folders of 2025 and 2026 in runs of at
most 120 requests, each saved file answering the next run. The data machine reads the last 10 days' files each day
(`dm_spp_mtlf`). Some early figures are far below the footprint's load (a minimum of 113 MW in the first run): they are
SPP's as printed and are not removed.
