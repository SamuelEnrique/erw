# ERCOT wind and solar output and High Sustained Limit, system-wide and by region, an hour (ERCOT NP4-742-CD and NP4-745-CD)

Energy Research Warehouse (ERW), method note written in session 2152 (chain 092) for a table first written on 7 October 2026 (session 144).

Tables: `ercot_wind_solar_hsl_hourly`

## Publisher and address

Electric Reliability Council of Texas (ERCOT), two hourly reports by geographical region on its public reports site, each posted once an hour and holding the 48 hours behind it (and a week of forecast ahead, not read); ERCOT's list keeps seven days of postings:

- NP4-742-CD, "Wind Power Production, Hourly Averaged Actual and Forecasted Values by Geographical Region" (report type 14787). Regions as ERCOT prints them: PANHANDLE, COASTAL, SOUTH, WEST, NORTH.
- NP4-745-CD, "Solar Power Production, Hourly Averaged Actual and Forecasted Values by Geographical Region" (report type 21809). Regions: CenterWest, NorthWest, FarWest, FarEast, SouthEast, CenterEast.

`https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=<14787 or 21809>` (the document list, JSON)

`https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=<DocID>` (each posting, a zip of one CSV)

Columns read: DELIVERY_DATE, HOUR_ENDING, DSTFlag, SYSTEM_WIDE_GEN, SYSTEM_WIDE_HSL, each GEN_<region>, and an HSL_<region> if ERCOT ever prints one (it prints none). The COP_HSL columns (the limit planned in the Current Operating Plan) and the forecasts are never read. Every request goes to the host `www.ercot.com`, under `/misapp/` and `/misdownload/`, paths ERCOT's robots file disallows (read by session 850, and again by session 2002 at 15:11:50 UTC on 23 October 2026, read 170 of `warehouse/metadata/license_reads.csv`), with the User-Agent "Mozilla/5.0 (Energy Research Warehouse; https://github.com/SamuelEnrique/erw)". Source id `ercot:np4_742_745_region`. Connector: `warehouse/connectors/ercot_wind_solar_history.py` (session 144), which also writes `ercot_wind_solar_output_hourly` and the monthly table derived from this one, `ercot_wind_solar_hsl_monthly` (`docs/methods/curtailment.md`).

It is run every day by `warehouse/run_daily.sh` (`pull ercot_wind_solar_history ... --pull --write`, under a pull budget of 15 minutes, `warehouse/pull_budget.py`), which `.github/workflows/daily-prices.yml` runs on GitHub's runner; the runner restores this table first (`warehouse/redivis/config.yaml`) and the run merges the new hours into it. `run_status.csv` records 13 runs that wrote it: every day from 7 to 14 October 2026, none from 15 to 19 October, two on 20 October (00:52 and 06:11 UTC) and one each on 21, 22 and 23 October; each wrote about nine days ("3,360 rows this run, 2026-10-14T05:00:00Z to 2026-10-23T12:00:00Z, 12 areas" on 23 October). The first date is from session 144's report ("Run on 7 October 2026 (UTC)"; this table 3,285 rows, 219 hours) and from the rows: the earliest `retrieved_at` is 7 October 2026 09:32:02 UTC.

## Vintage and revision

Hours 28 September 2026 05:00 UTC (00:00 Central) to 23 October 2026 12:00 UTC in the file on the data machine, rebuilt from the ERW archive by `warehouse/restore_tables.py` as of run `20261023T152740Z-github`, with the header of the connector's run `20261023T144737Z` ("9 solar postings, 9 wind postings read from the saved files"). The rows' `retrieved_at` fall on every day from 7 to 15 October and from 19 to 23 October 2026; each is the time its posting was downloaded, kept by the archive from the run that first archived the value. 76 posting addresses are cited. `vintage` is empty. `coverage.csv` gives the same 9,120 rows, 2026-09-28T05:00:00Z to 2026-10-23T12:00:00Z, 11 nodes: it agrees.

`--pull` asks each list afresh and saves the last posting of each publish day and the newest one (each holds 48 hours, so together they cover every hour the list still reaches), and the oldest posting on the list when no posting as old is already saved. `--write` reads every saved posting, oldest first, and the newest posting that holds an hour gives its value. `ip.write_csv` merges the rows into the table held on (entity, variable, ts_utc), so an hour read again replaces the one held, and the table keeps hours ERCOT's list has dropped. A lapse of more than about seven days between runs loses hours for good; the lapse of 15 to 19 October lost none.

## Shape and variables

Series, 9,120 rows, fifteen series of 608 hours. `entity` `ercot:system` (ERCOT's SYSTEM_WIDE columns), `ercot:wind:<REGION>` or `ercot:solar:<Region>`; `variable` `<fuel>_generation_mw` (ERCOT's GEN, the hourly average of actual output) or `<fuel>_hsl_mw` (SYSTEM_WIDE_HSL, the hourly average of the High Sustained Limit, system-wide only); `unit` MW; `freq` PT1H; `ts_utc` the hour's start, from DELIVERY_DATE and HOUR_ENDING (Central) less one hour, DSTFlag Y marking the repeated autumn hour; `market` empty; `geo` US-TX; `node` the region (empty for `ercot:system`); `vintage` empty.

| Entity | Variable | Hours | Mean MW | Lowest | Highest |
|---|---|---|---|---|---|
| `ercot:system` | `wind_generation_mw` | 608 | 11,872 | 1,022.89 (8 October 2026, 14:00 UTC) | 26,491.91 (16 October 2026, 13:00 UTC) |
| `ercot:system` | `wind_hsl_mw` | 608 | 12,730 | 1,159.52 (8 October 2026, 15:00 UTC) | 32,198.98 (16 October 2026, 17:00 UTC) |
| `ercot:system` | `solar_generation_mw` | 608 | 9,041 | 0.07 (7 October 2026, 04:00 UTC) | 32,938.09 (17 October 2026, 16:00 UTC) |
| `ercot:system` | `solar_hsl_mw` | 608 | 9,423 | 0.54 (18 October 2026, 07:00 UTC) | 33,464.82 (17 October 2026, 17:00 UTC) |
| `ercot:wind:COASTAL` | `wind_generation_mw` | 608 | 1,414 | 0.06 (28 September 2026, 12:00 UTC) | 3,820.23 (17 October 2026, 01:00 UTC) |
| `ercot:wind:NORTH` | `wind_generation_mw` | 608 | 1,028 | 1.51 (21 October 2026, 18:00 UTC) | 2,799.99 (16 October 2026, 13:00 UTC) |
| `ercot:wind:PANHANDLE` | `wind_generation_mw` | 608 | 1,466 | 0.49 (4 October 2026, 10:00 UTC) | 3,561.23 (12 October 2026, 05:00 UTC) |
| `ercot:wind:SOUTH` | `wind_generation_mw` | 608 | 1,245 | 33.27 (18 October 2026, 19:00 UTC) | 3,219.78 (16 October 2026, 17:00 UTC) |
| `ercot:wind:WEST` | `wind_generation_mw` | 608 | 6,720 | 50.15 (17 October 2026, 22:00 UTC) | 16,383.94 (11 October 2026, 05:00 UTC) |
| `ercot:solar:CenterEast` | `solar_generation_mw` | 608 | 1,225 | 0.00 (43 hours) | 4,757.92 (17 October 2026, 15:00 UTC) |
| `ercot:solar:CenterWest` | `solar_generation_mw` | 608 | 1,208 | 0.00 (199 hours) | 4,549.39 (10 October 2026, 15:00 UTC) |
| `ercot:solar:FarEast` | `solar_generation_mw` | 608 | 3,716 | 0.03 (2 hours, 5 and 20 October 2026, 01:00 UTC) | 13,673.97 (17 October 2026, 15:00 UTC) |
| `ercot:solar:FarWest` | `solar_generation_mw` | 608 | 1,362 | 0.00 (250 hours) | 5,106.09 (1 October 2026, 20:00 UTC) |
| `ercot:solar:NorthWest` | `solar_generation_mw` | 608 | 640 | 0.00 (237 hours) | 2,375.16 (17 October 2026, 15:00 UTC) |
| `ercot:solar:SouthEast` | `solar_generation_mw` | 608 | 890 | 0.00 (39 hours) | 3,243.79 (17 October 2026, 17:00 UTC) |

No autumn clock change falls in the window (it comes on 1 November 2026).

## Reading ERCOT's reports site

- Before any request the pull asks `ip.paused("ercot")` (ERCOT is not paused); a paused publisher is a log line and no request.
- Each list is asked afresh every pull; only postings whose name ends `_csv` are considered, and a posting already saved and on disk is not asked again.
- Each request: a timeout of 180 seconds, up to three tries, 10, 20 and 30 seconds after each failure; HTTP 401 or 403, or a body that is not a zip where a posting should be, stops the pull (an access control, never worked around), and no table is written that run. Two seconds after each request.
- Ceiling: 2,000,000 rows of these series read, over every run and probe, counted in the manifest's `series_rows`; before each posting the pull checks that 500 more rows would not pass it; if they would, the pull stops and no table is written that run.
- A posting must hold exactly one CSV with DELIVERY_DATE, HOUR_ENDING, SYSTEM_WIDE_GEN, SYSTEM_WIDE_HSL and at least one regional column, or it stops the run. A blank is no row; anything else that is not a number stops the run; a value in an hour the spring clock change skips stops it; an hour twice in one posting stops it.
- `--write` checks each saved posting against its manifest sha256. Each table is its own stage: a failure of one does not stop the others.
- `--check` compares the hourly rows, summed by Central day, with `ercot_wind_solar_hsl_daily` (read from ERCOT's system-wide reports), allowing 0.5 MWh a day; it is not part of the scheduled run.
- `--out-dir` and `--raw-dir` write a trial elsewhere.

## License

The header: "License: public. ERCOT's terms: "raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices." (https://www.ercot.com/help/terms, read 6 October 2026). Cite "ERCOT"." `coverage.csv`: public. `license_tables.csv` names ERCOT as the table's one publisher (from the source registry); `license_verdicts.csv` gives ERCOT "may be public" (read 2 of `license_reads.csv`, 12 October 2026). `docs/licenses.md`: flag and verdict agree; ERW verdict public.

## Cross-checks (session 2152)

- The counts above were computed from the rows, read past the 17 header lines; no hour is given twice.
- Hours complete: each of the fifteen series holds every hour from 28 September 2026 05:00 to 23 October 2026 12:00 UTC (608).
- In every hour, `ercot:system` generation equals the sum of its regions to within 0.000000000004 MW, for wind and for solar.
- Output above the limit: system-wide solar generation is above `solar_hsl_mw` in 107 of the 608 hours, 96 of them between 07:00 and 12:59 Central, by up to 3,115.02 MW (7 October 2026, 13:00 UTC, 08:00 Central); summed over the hours, 88,836.77 MWh above the limit against 320,972.60 MWh below it. Wind is above in 18 hours (by up to 230.55 MW), 2,132.23 MWh above against 523,791.57 MWh below. The docstring reported the same pattern for the first nine days (44 of 219 solar hours, up to 2,921 MW).
- Against the actual output of `ercot_wind_solar_forecast`, read from ERCOT's system-wide reports, in the 608 hours both hold: the two differ in 330 wind hours and 327 solar hours, by at most 0.03 MW.
- The connector's `--check` against `ercot_wind_solar_hsl_daily` was not run for this note.

## Found while writing this note

- The docstring says a file "is saved once ... and never asked for again", and counts the ceiling "over every run". The scheduled run is on GitHub's runner, which keeps no `warehouse/raw/` between runs: each daily run starts with an empty manifest, asks for about nine postings of each report (and the three yearly workbooks) again, and counts only its own rows against the ceiling. Each run's status row covers about nine days, and the data machine's manifest holds 35 entries, all of 7 October 2026.
- The docstring of `check()` says ERCOT prints the same hour's system-wide figure "up to 0.02 MW apart" in its system-wide and by-region reports. Against `ercot_wind_solar_forecast` (system-wide reports) one hour of each fuel differs by 0.03 MW (wind 9 October 2026 01:00 UTC, solar 8 October 2026 00:00 UTC). The check's allowance of 0.5 MWh a day is not passed by it.
- The connector asks `/misapp/` and `/misdownload/` on `www.ercot.com`, paths ERCOT's robots file disallows (read 23 October 2026, session 2002). Neither its docstring nor its header says so.

## What it does not hold

- A High Sustained Limit by region: ERCOT prints the actual HSL system-wide only; COP HSL is never read or put in its place.
- Hours before 28 September 2026: the history of these reports sits behind ERCOT's Data Access Portal, which needs a signed-in account and a key, and is not used.
- Curtailment: output below the limit is the ERW's estimate, in `ercot_wind_solar_hsl_monthly` and `ercot_wind_solar_hsl_daily` (`docs/methods/curtailment.md`), not a figure in this table.
- ERCOT's eight weather zones: the regions are ERCOT's wind and solar regions.
