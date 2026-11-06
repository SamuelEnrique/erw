# Each grid's weighted temperature, dew point, heating and cooling degrees, an hour, from 2019 (NOAA NCEI, ISD-Lite and Local Climatological Data)

Energy Research Warehouse (ERW), method note written in session 2256 (chain 102) for a table first written on 5 October 2026 (session 126).

Tables: `noaa_grid_weather_hourly`

## Publisher and address

NOAA National Centers for Environmental Information (NCEI). Two products of the same airport stations' reports, five stations a grid, 35 in all:

- ISD-Lite, the hourly cut of the Integrated Surface Database, one file a station and year, 2019 to 2025, used for hours before 2025-08-01T00:00:00Z (NOAA's database ends on 27 August 2025):

  `https://www.ncei.noaa.gov/pub/data/noaa/isd-lite/<year>/<USAF>-<WBAN>-<year>.gz`

- Local Climatological Data, version 2, through NCEI's Access Data Service, asked from 1 July 2025 and used from 2025-08-01T00:00:00Z:

  `https://www.ncei.noaa.gov/access/services/data/v1?dataset=local-climatological-data-v2&stations=USW000<WBAN>&startDate=<day>T00:00:00&endDate=<day>T23:59:59&dataTypes=HourlyDryBulbTemperature,HourlyDewPointTemperature&format=csv`

The station list is `https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv`. The User-Agent is "ERW energy research warehouse (https://github.com/SamuelEnrique/erw)". NCEI's robots file disallows `/data*`, `/orders*` and some `/access/crn/` paths, not `/pub/` (read 258 of `warehouse/metadata/license_reads.csv`, session 2107); the connector's paths are under none of them.

Source ids `noaa:isd_lite` and `noaa:lcd_v2`. Connector: `warehouse/connectors/noaa_grid_weather.py` (session 126), which writes this table with `noaa_grid_weather_daily`, `noaa_grid_weather_stations` and `noaa_station_weather_hourly`. Method: `docs/methods/demand_weather.md`.

Read by `warehouse/derived/demand_weather.py` (`eia930_demand_weather`), which takes `variable`, `ts_utc`, `value` and `ba` and fits each grid's hourly demand on the heating and cooling degrees of the hour and of the 24 hours before, and on the dew point above 60 F where the rule adopts it. Its two trials (four stations of five for ISO-NE, and five equal weights) do not read this table: they rebuild the grid hours from `noaa_station_weather_hourly` or from the saved files.

Schedule: `warehouse/run_data_machine_tables.sh`, step `dm_noaa_weather` (`noaa_grid_weather.py --refresh`), once a week (the first run of each ISO week, or any run with WEEKLY=1), sourced by `warehouse/run_data_machine.sh`, the data machine's daily run ("ERW data machine daily", registered by `scripts/register_data_machine_daily.ps1`). No line of `warehouse/run_daily.sh` or `.github/workflows/` names the connector, and `warehouse/metadata/run_status.csv` holds no row for it.

The first date is from the commit that first adds the table's coverage row, `32204327`, 5 October 2026 at 18:10 UTC (session 126), and from the table's header ("(session 126)").

## Vintage and revision

Hours 2019-01-01T00:00:00Z to 2026-10-18T03:00:00Z (the last hour every station reaches), written by run `20261021T084557Z`; every row's `retrieved_at` is 2026-10-21T08:46:47Z, and `vintage` is empty. `coverage.csv` gives the same 1,907,625 rows, 7 nodes and the same first and last `ts_utc` (last run 2026-10-21T08:45:57Z); `archive_manifest.csv` holds 1,907,625 rows (run `20261021T085120Z-local`).

Each run deletes the table and writes it whole, from the saved files or, with `--from-table`, from `noaa_station_weather_hourly`. With `--refresh` the Local Climatological Data is asked again from a week before the newest hour held, and the later answer's hours replace the held ones from its own first hour on. Weights are taken again from `census_metro_population` each run.

## Shape and variables

Series, 1,907,625 rows, 7 entities, 4 variables. `entity` `iso:<grid>` (`iso:caiso`, `iso:ercot`, `iso:isone`, `iso:miso`, `iso:nyiso`, `iso:pjm`, `iso:spp`); `node` the grid's name; `ba` its EIA-930 code (ciso, erco, isne, miso, nyis, pjm, swpp), the partition column and the join to the EIA-930 tables; `geo` the states the grid serves, as a list; `unit` degF; `freq` PT1H; `ts_utc` the hour (the reading taken in the ten minutes up to it); `market` empty; `x_interpolated` how many of the five stations' temperatures in the hour are interpolated.

| `variable` | Rows | What it is | Mean | Lowest | Highest |
|---|---|---|---|---|---|
| temperature_f | 476,924 | the weighted mean of the five stations' temperatures | 58.73 | -13.78 (MISO, 2019-01-30 13:00 UTC) | 106.35 (ERCOT, 2023-08-20 21:00 UTC) |
| dew_point_f | 476,853 | the weighted mean of the dew points, when all five hold one | 45.82 | -29.38 (ISO-NE, 2023-02-04 11:00 UTC) | 78.38 (ERCOT, 2024-05-27 16:00 UTC) |
| heating_degrees_f | 476,924 | the weighted mean of max(65 - T, 0) | 10.89 | 0 | 78.78 (MISO, 2019-01-30 13:00 UTC) |
| cooling_degrees_f | 476,924 | the weighted mean of max(T - 65, 0) | 4.62 | 0 | 41.35 (ERCOT, 2023-08-20 21:00 UTC) |

T is each station's temperature in degrees F (NOAA's tenths of a degree C times 9/5 plus 32); values are rounded to two decimals. 113,032 grid-hours have both heating and cooling degrees above 0, because the degrees are taken at each station before weighting.

Of the span's 68,332 hours:

| Grid | Hours held | Missing | Hours with a station interpolated | First hour |
|---|---|---|---|---|
| CAISO | 68,133 | 199 | 152 | 2019-01-01 01:00 UTC |
| ERCOT | 68,137 | 195 | 232 | 2019-01-01 01:00 UTC |
| ISO-NE | 67,881 | 451 | 422 | 2019-01-01 01:00 UTC |
| MISO | 68,190 | 142 | 4,095 | 2019-01-01 00:00 UTC |
| NYISO | 68,206 | 126 | 3,968 | 2019-01-01 00:00 UTC |
| PJM | 68,204 | 128 | 130 | 2019-01-01 00:00 UTC |
| SPP | 68,173 | 159 | 282 | 2019-01-01 01:00 UTC |

Every grid ends on 2026-10-18T03:00:00Z. A grid whose first hour is 01:00 has a station with no reading at 00:00, and a missing run at either end is never filled. The longest run of missing hours in every grid is 30 August 2025 00:00 UTC to 2 September 2025 17:00 or 18:00 UTC (90 or 91 hours): the Local Climatological Data holds no report for those days. Every grid also lacks a run of 11 to 16 hours on 1 December 2024. `x_interpolated` over the 476,924 hours: 0 in 467,643, 1 in 5,910, 2 in 3,073, 3 in 40, 4 in 56 and 5 in 202. MISO's and NYISO's thousands are Detroit's, Buffalo's and Rochester's hours that ISD-Lite lacks at the same hours of most days.

`source` is `noaa:isd_lite` in 1,613,317 rows (hours to 2025-07-31T23:00:00Z) and `noaa:lcd_v2` in 294,308 (from 2025-08-01T00:00:00Z). `source_url` is the ISD-Lite directory of the hour's year, or the Access Data Service's address without its station and dates.

The counts in this note were computed in session 2256 with pandas from the rows of `warehouse/output/noaa_grid_weather_hourly.csv` on the data machine, read past its 15 header lines as strings; no (entity, variable, ts_utc) is given twice.

## Checks the connector makes

- Before any request, `iso_prices.paused("noaa")`; a paused publisher ends the run with exit 1 and no request. NOAA is not paused. `iso_prices.paused_host()` is not asked.
- NOAA's station list must hold each of the 35 stations exactly once, or the run stops.
- A saved file is read from `warehouse/raw/noaa_grid_weather/` and not asked again. Each request is tried up to four times, 5, 10 and 15 seconds apart (`ip.with_retries`); an HTTP 404 is not retried. 0.4 seconds after each request.
- An answer of the Access Data Service that does not begin with its header, or whose newest report is more than 21 days before the last day asked, is counted against the ceiling, not used, and asked again, up to four times; the fourth stops the run.
- Only reports whose type begins "FM" are read; a value NOAA marks with a letter or star, or leaves blank, is not read and is counted. Local standard time is moved to UTC, and an hour takes the report from ten minutes before it up to it, the closest.
- The seam: a station whose two products agree to a tenth of a degree C in fewer than 90 percent of the shared hours outside the eight synoptic hours stops the run, and nothing is written (the least, in the header: 99.89 percent, TUL). Minneapolis-St. Paul from 1 April 2020 to 30 November 2022 is read from the Local Climatological Data.
- Filling: a run of at most three missing hours between two measured hours is interpolated on a straight line, temperature and dew point each; a longer run, or one at either end, stays missing. A grid's hour is written only when all five stations hold a temperature, and its dew point only when all five hold one. The five weights must add to 1 within 0.000000001, or the build stops.
- Ceiling: 6,000,000 rows a UTC year of NOAA's answers (`warehouse/raw/noaa_grid_weather/ceiling.json`), checked with an estimate before each request; the header's count for 2026 is 2,829,911.
- The write needs the data lock (`ip.write_csv`).

## License

The header: "License: public. U.S. stations only. NOAA NCEI's record for the database gives a citation and two statements of liability and names no license; its readme restricts only non-U.S. data (WMO Resolution 40)." with the two citations: NOAA National Centers for Environmental Information (2001), Global Surface Hourly [ISD-Lite]; and Kantor, Casey, Menne and Buddenberg (2023), Local Climatological Data (LCD), Version 2, https://doi.org/10.25921/96dw-mb77. `license_verdicts.csv` gives NOAA NCEI "may be public" (read 9). `license_tables.csv` names NOAA NCEI as the one publisher; `docs/licenses.md` gives the ERW verdict public; `coverage.csv`: public. The table is under `catalogue_hold` in `warehouse/supabase/live_set.yaml`, not loaded; `/demand?view=weather` (in review) reads `site/data/demand_weather.json`, and since session 331 its downloads name this table.

## Cross-checks (session 2256)

- In every grid, each hour in which no station is interpolated (64,095 to 68,074 hours a grid) was recomputed from `noaa_station_weather_hourly` and the weights in `noaa_grid_weather_stations`: the table agrees to within 0.005 F, the rounding to two decimals, in every hour.
- `noaa_grid_weather_daily`, recomputed from this table by local day, agrees to within 0.005 on every day and variable.

## Found while writing this note

- `iso_prices.paused_host()` is not asked before a request; `paused("noaa")` is.
- `source` and `source_url` say `noaa:isd_lite` for MISO's hours from April 2020 to November 2022, though Minneapolis-St. Paul's hours in that stretch (weight 0.2533) are read from the Local Climatological Data; `noaa_station_weather_hourly` labels the same station hours `noaa:lcd_v2`.
- The header says `x_interpolated` counts the stations whose temperature is interpolated. Dew points are interpolated by the same rule (`fill_short` on `dew_c`), and no column counts them.
- The connector's docstring opens with "Three series tables"; it writes four.
- The docstring of `demand_weather.py` gives the fit as seven terms without dew point ("every kind of hour its own seven numbers"); the code also fits the dew point terms and keeps them by the rule of `adopt_dew()`, as `docs/methods/demand_weather.md` says (session 129).

## What it does not hold

- A grid's hour with any station missing for more than three hours: none is filled from four stations.
- The stations' own hours (`noaa_station_weather_hourly`), their weights and counts (`noaa_grid_weather_stations`), or days (`noaa_grid_weather_daily`).
- Wind, cloud, humidity beyond the dew point, precipitation; hours before 2019.
