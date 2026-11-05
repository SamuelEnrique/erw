# Each grid's weighted temperature, dew point and degree days, a local day, from 2019 (NOAA NCEI, ISD-Lite and Local Climatological Data)

Energy Research Warehouse (ERW), method note written in session 2256 (chain 102) for a table first written on 5 October 2026 (session 126).

Tables: `noaa_grid_weather_daily`

## Publisher and address

NOAA National Centers for Environmental Information (NCEI). Two products of the same airport stations' reports, five stations a grid, 35 in all:

- ISD-Lite, the hourly cut of the Integrated Surface Database, one file a station and year, 2019 to 2025, used for hours before 2025-08-01T00:00:00Z (NOAA's database ends on 27 August 2025):

  `https://www.ncei.noaa.gov/pub/data/noaa/isd-lite/<year>/<USAF>-<WBAN>-<year>.gz`

- Local Climatological Data, version 2, through NCEI's Access Data Service, asked from 1 July 2025 and used from 2025-08-01T00:00:00Z:

  `https://www.ncei.noaa.gov/access/services/data/v1?dataset=local-climatological-data-v2&stations=USW000<WBAN>&startDate=<day>T00:00:00&endDate=<day>T23:59:59&dataTypes=HourlyDryBulbTemperature,HourlyDewPointTemperature&format=csv`

The station names and places are read from `https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv`. The User-Agent is "ERW energy research warehouse (https://github.com/SamuelEnrique/erw)". NCEI's robots file disallows `/data*`, `/orders*` and some `/access/crn/` paths, not `/pub/` (read 258 of `warehouse/metadata/license_reads.csv`, session 2107); the connector's paths, `/pub/data/noaa/` and `/access/services/data/v1`, are under none of them.

Source ids `noaa:isd_lite` and `noaa:lcd_v2`. Connector: `warehouse/connectors/noaa_grid_weather.py` (session 126), which writes this table with `noaa_grid_weather_hourly`, `noaa_grid_weather_stations` and `noaa_station_weather_hourly`. This table is built from the grid's hours of the same run, the rows of `noaa_grid_weather_hourly` before rounding. The weights are the Census Bureau's, read from `census_metro_population` (session 129). Method: `docs/methods/demand_weather.md`.

Schedule: `warehouse/run_data_machine_tables.sh`, step `dm_noaa_weather` (`noaa_grid_weather.py --refresh`), once a week (the first run of each ISO week, or any run with WEEKLY=1). That file is sourced by `warehouse/run_data_machine.sh`, the data machine's daily run, a Windows scheduled task ("ERW data machine daily") registered by `scripts/register_data_machine_daily.ps1`. No line of `warehouse/run_daily.sh` or `.github/workflows/` names the connector, and `warehouse/metadata/run_status.csv` holds no row for it.

The first date is from the commit that first adds the table's coverage row, `32204327`, 5 October 2026 at 18:10 UTC ("Session 126: the four tables built, validated, in coverage, archived and in the Redivis draft"), and from the table's own header ("(session 126)").

## Vintage and revision

Local days 1 January 2019 to 17 October 2026, written by run `20261021T084557Z`; every row's `retrieved_at` is 2026-10-21T08:46:47Z, and `vintage` is empty. `coverage.csv` gives the same 118,630 rows, 7 nodes, the same first and last `ts_utc`, and last run 2026-10-21T08:45:57Z; `archive_manifest.csv` holds 118,630 rows (run `20261021T085120Z-local`).

Each run deletes the table and writes it whole from the saved files (or, with `--from-table`, from `noaa_station_weather_hourly`), so a day is recomputed every run. ISD-Lite is closed. With `--refresh` the Local Climatological Data is asked again from a week before the newest hour held, and the later answer's hours replace the held ones from its own first hour on: a value NCEI revises within that week is taken, one revised earlier is not.

## Shape and variables

Series, 118,630 rows, 7 entities, 6 variables. `entity` `iso:<grid>` (`iso:caiso`, `iso:ercot`, `iso:isone`, `iso:miso`, `iso:nyiso`, `iso:pjm`, `iso:spp`); `node` the grid's name (CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP); `ba` its EIA-930 code (ciso, erco, isne, miso, nyis, pjm, swpp), the partition column; `geo` the states the grid serves, as a list (US-TX for ERCOT, US-CA for CAISO, US-NY for NYISO, longer lists for the others); `freq` P1D; `ts_utc` the grid's local day at 00:00:00Z (America/Chicago for ERCOT, MISO and SPP, America/Los_Angeles for CAISO, America/New_York for NYISO, ISO-NE and PJM); `market` empty; `x_hours` the hours of that local day (24 in 118,000 rows, 23 in 336, 25 in 294).

| `variable` | `unit` | Rows | What it is | Mean | Lowest | Highest |
|---|---|---|---|---|---|---|
| temperature_f | degF | 19,774 | the mean of the day's weighted hours | 58.75 | -8.871 (MISO, 30 January 2019) | 94.11 (ERCOT, 20 August 2023) |
| temperature_max_f | degF | 19,774 | the day's warmest weighted hour | 66.52 | -5.198 (MISO, 30 January 2019) | 106.348 (ERCOT, 20 August 2023) |
| temperature_min_f | degF | 19,774 | the day's coldest weighted hour | 51.63 | -13.78 (MISO, 30 January 2019) | 83.184 (ERCOT, 8 August 2023) |
| dew_point_f | degF | 19,760 | the mean of the day's weighted dew points, written only when every hour has one | 45.83 | -20.996 (ISO-NE, 4 February 2023) | 76.32 (SPP, 22 August 2023) |
| heating_degree_days | degF-day | 19,774 | the sum of the hours' heating degrees (base 65 F) over 24 | 10.88 | 0 | 73.871 (MISO, 30 January 2019) |
| cooling_degree_days | degF-day | 19,774 | the sum of the hours' cooling degrees (base 65 F) over 24 | 4.63 | 0 | 29.11 (ERCOT, 20 August 2023) |

Values are rounded to three decimals. A grid's heating and cooling degrees are taken at each station and then weighted, so a day can hold both.

| Grid | Days | Last day | Days missing inside the span | Days without a dew point |
|---|---|---|---|---|
| CAISO | 2,825 | 16 October 2026 | 21 | 1 |
| ERCOT | 2,824 | 16 October 2026 | 22 | 3 |
| ISO-NE | 2,785 | 17 October 2026 | 62 | 10 |
| MISO | 2,833 | 16 October 2026 | 13 | 0 |
| NYISO | 2,837 | 17 October 2026 | 10 | 0 |
| PJM | 2,837 | 17 October 2026 | 10 | 0 |
| SPP | 2,833 | 16 October 2026 | 13 | 0 |

Every grid begins on 1 January 2019. The last hour every station reaches is 2026-10-18T03:00:00Z, 23:00 on 17 October in New York and 22:00 in Chicago, so 17 October is whole only in the Eastern grids. Nine days are missing in every grid: 1, 3 and 18 December 2024, 29 August to 2 September 2025 (no grid holds an hour from 30 August 2025 00:00 UTC to 2 September 2025 17:00 UTC, 90 or 91 hours by grid: the Local Climatological Data holds no report for those days), and 26 March 2026. ISO-NE misses 23 days in 2025 and 19 in 2026. Since 1 January 2025 its Bridgeport station (BDR) has 25 runs of more than three missing hours, 259 hours in all, and Worcester (ORH) 8 runs, 142 hours; a run that long is never filled.

`source` is `noaa:isd_lite` in 100,456 rows and `noaa:lcd_v2` in 18,174; the switch is at the local day of 31 July 2025 in every grid. `source_url` is the ISD-Lite directory of the day's year, or the Access Data Service's address without its station and dates.

The counts in this note were computed in session 2256 with pandas from the rows of `warehouse/output/noaa_grid_weather_daily.csv` on the data machine, read past its 15 header lines as strings; no (entity, variable, ts_utc) is given twice.

## Checks the connector makes

- Before any request, `iso_prices.paused("noaa")`; a paused publisher ends the run with exit 1 and no request. NOAA is not paused. `iso_prices.paused_host()` is not asked.
- NOAA's station list must hold each of the 35 stations (USAF and WBAN) exactly once, or the run stops.
- A saved ISD-Lite file or station list is read from `warehouse/raw/noaa_grid_weather/` and not asked again. Each request is tried up to four times, 5, 10 and 15 seconds apart (`ip.with_retries`); an HTTP 404 is not retried. 0.4 seconds after each request.
- An answer of the Access Data Service that does not begin with its header, or whose newest report is more than 21 days before the last day asked, is counted against the ceiling, not used, and asked again, up to four times (20, 40 and 60 seconds apart); the fourth stops the run.
- Only reports whose type begins "FM" are read. A value NOAA marks with a letter or star, or leaves blank, is not read and is counted in the log. Local standard time is moved to UTC, and an hour takes the report from ten minutes before it up to it, the closest (ISD-Lite's rule).
- The seam: over 1 July 2025 to the end of ISD-Lite the two products are compared at every station; a station that agrees to a tenth of a degree C in fewer than 90 percent of the hours outside the eight synoptic hours stops the run, and nothing is written. The header gives the least agreement as 99.89 percent (TUL).
- Minneapolis-St. Paul from 1 April 2020 to 30 November 2022 is read from the Local Climatological Data, where ISD-Lite holds little more than the synoptic hours.
- Filling: a run of at most three missing hours between two measured hours is interpolated on a straight line; a longer run, or a run at either end, stays missing. A grid's hour is held only when all five stations hold a temperature; a day is written only when every hour of the local day is held (23 or 25 on the days the clocks change), and its dew point only when every hour has one.
- Ceiling: 6,000,000 rows a UTC year of NOAA's answers, kept in `warehouse/raw/noaa_grid_weather/ceiling.json`; before each request the year's rows and an estimate are checked against it. The header: "rows NOAA sent in 2026: 2,829,911 of the ceiling of 6,000,000 a year".
- The write needs the data lock (`ip.write_csv`). `--out-dir` writes a trial elsewhere and leaves the run status and the source registry alone.

## License

The header: "License: public. U.S. stations only. NOAA NCEI's record for the database gives a citation and two statements of liability and names no license; its readme restricts only non-U.S. data (WMO Resolution 40)." with the two citations: NOAA National Centers for Environmental Information (2001), Global Surface Hourly [ISD-Lite]; and Kantor, Casey, Menne and Buddenberg (2023), Local Climatological Data (LCD), Version 2, https://doi.org/10.25921/96dw-mb77. `license_verdicts.csv` gives NOAA NCEI "may be public" (read 9; the same if the ERW sells anything). `license_tables.csv` names NOAA NCEI as the table's one publisher, from the source registry; `docs/licenses.md` gives the ERW verdict public; `coverage.csv`: public. `warehouse/supabase/live_set.yaml` holds the table under `catalogue_hold`: it is not loaded, and the review page reads the site's own copy (`site/data/demand_weather.json`).

## Cross-checks (session 2256)

- Each figure recomputed from `noaa_grid_weather_hourly`, the hours grouped by the grid's local day: on every day of every grid the table agrees with the recomputed mean, highest, lowest and degree days to within 0.005, the rounding of the hourly table to two decimals.

## Found while writing this note

- `iso_prices.paused_host()` is not asked before a request; `paused("noaa")` is.
- `source` and `source_url` say `noaa:lcd_v2` for the local day of 31 July 2025 in every grid, though most of its hours are ISD-Lite's: the code names a day by the source of its last hour (`last < SEAM`), and that day's last hour falls on or after 2025-08-01T00:00:00Z.
- `source` says `noaa:isd_lite` for MISO's days from April 2020 to November 2022, though Minneapolis-St. Paul's hours in that stretch (its weight 0.2533) are read from the Local Climatological Data. `noaa_station_weather_hourly` labels those station hours `noaa:lcd_v2`; the grid tables do not.
- The docstring opens with "Three series tables" and lists three; the connector writes four (`noaa_station_weather_hourly` since session 129, named later in the same docstring).
- The docstring keeps session 126's "Ceiling: 3,000,000 rows" beside session 271's 6,000,000 a year, and the first line of run `20261021T084557Z`'s log says "ceiling 6,000,000 rows (34,951 read by the session's trials are counted)", as if session 126's trial reads counted against a year's ceiling. The code counts the year's rows in `ceiling.json` and adds the trial reads only to the run's own figure of rows read.

## What it does not hold

- Hours: each grid's are in `noaa_grid_weather_hourly`, each station's in `noaa_station_weather_hourly`.
- A day not whole: any local day with an hour no grid weather is held for, including the nine days missing in every grid.
- Humidity beyond the dew point, wind, cloud, precipitation, and any station beyond the 35.
- Days before 1 January 2019.
