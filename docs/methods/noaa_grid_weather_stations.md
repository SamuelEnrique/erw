# The 35 NOAA airport stations behind each grid's weighted weather: weights and hours held

Energy Research Warehouse (ERW), method note written in session 2074 (chain 067) for a table first written on 5 October 2026 (session 126).

Tables: `noaa_grid_weather_stations`

## Publisher and address

NOAA National Centers for Environmental Information (NCEI). Two products of the same stations' reports: ISD-Lite (`https://www.ncei.noaa.gov/pub/data/noaa/isd-lite/<year>/<USAF>-<WBAN>-<year>.gz`, 2019 to 2025, used for hours before 2025-08-01T00:00:00Z; NOAA's database ends on 27 August 2025), and Local Climatological Data version 2 through NCEI's Access Data Service (`https://www.ncei.noaa.gov/access/services/data/v1?dataset=local-climatological-data-v2`, stations `USW000<WBAN>`, used from 2025-08-01). Station names and positions are from `https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv`. Source ids `noaa:isd_lite` and `noaa:lcd_v2`. Connector: `warehouse/connectors/noaa_grid_weather.py` (session 126), which writes this table with `noaa_grid_weather_hourly`, `noaa_grid_weather_daily` and `noaa_station_weather_hourly`; `warehouse/run_data_machine_tables.sh` runs it weekly with `--refresh`. The populations are the Census Bureau's, from `census_metro_population`. Method: `docs/methods/demand_weather.md`.

## Vintage and revision

Last written by run `20261021T084557Z` (21 October 2026); every row's `retrieved_at` is 2026-10-21T08:46:47Z. The counts run over `x_hours` = 68,332 hours, from 2019-01-01T00:00:00Z to `x_through` 2026-10-18T03:00:00Z, the last hour every station reaches. Header: "Rows read: 2,794,810, the session's trial reads included; rows NOAA sent in 2026: 2,829,911 of the ceiling of 6,000,000 a year (session 271)."

Each run deletes the table and writes it whole (it is small), so every count is recounted over the whole span and the weights are taken again from `census_metro_population`.

## Shape and variables

Series, 245 rows: 35 stations, seven variables each, all at `ts_utc` 2019-01-01T00:00:00Z (the start of the span counted). `entity` `noaa:<GHCN identifier>` (`USW000` and the WBAN); `node` the grid (CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP) and `ba` its EIA-930 code (ciso, erco, isne, miso, nyis, pjm, swpp), five stations each; `geo` `US-<the station's state>`; `freq`, `market` and `vintage` empty.

| `variable` | `unit` | What it is |
|---|---|---|
| weight | ratio | the station's area's population over the sum of its grid's five, to six decimals |
| population_base_2020 | count | the Census Bureau's estimates base of the area `x_cbsa` |
| hours_measured | count | hours with a temperature from NOAA |
| hours_interpolated | count | hours filled on a straight line inside a run of at most 3 missing hours |
| hours_missing | count | hours still without a temperature |
| longest_gap_hours | count | the longest run of missing hours before filling |
| dew_point_hours_missing | count | hours without a dew point after the same filling |

`x_airport` the airport code, `x_station` NOAA's USAF-WBAN, `x_name`, `x_lat` and `x_lon` NOAA's, `x_metro` the area the station stands for, `x_cbsa` the Census code (35620:36 for LaGuardia: New York's area counted by its part in New York State).

Largest weight in each grid: LaGuardia 0.7763 (NYISO), Boston 0.5160 (ISO-NE), Los Angeles 0.4740 (CAISO), Dallas-Fort Worth 0.3726 (ERCOT), Kansas City 0.3508 (SPP), Chicago O'Hare 0.3465 (PJM), Detroit 0.3015 (MISO). Smallest: Syracuse 0.0390 (NYISO). Hours measured run from 64,299 (Detroit, 3,918 interpolated) to 68,188 (Baltimore); hours missing from 97 to 327 (Bridgeport); `longest_gap_hours` is 90 or 91 at every station.

Seven `x_metro` values keep the names the connector's station list gave in session 126, not the Census Bureau's name for the same code: IAH "Houston-The Woodlands-Sugar Land" (the Bureau: Houston-Pasadena-The Woodlands), AUS, SFO, BDL, BDR, IND and OMA likewise. Every row's `source` is `noaa:isd_lite` and `source_url` the ISD-Lite directory, although the hours from August 2025 are counted from the Local Climatological Data.

## Reading the source

- An hour takes the report from ten minutes before the hour up to the hour, the closest to it (ISD-Lite's rule, applied to the Local Climatological Data after its times are moved from local standard time to UTC).
- Over 1 July 2025 to ISD-Lite's end the two products are compared at every station; a station that agrees to a tenth of a degree C in fewer than 90 percent of the hours outside the eight synoptic hours stops the run. Each station's agreement is in the header.
- Minneapolis-St. Paul from 2020-04-01 to 2022-11-30 is read from the Local Climatological Data, where ISD-Lite holds little more than the synoptic hours.
- A station NOAA's station list does not hold stops the run. Ceiling: 6,000,000 rows a UTC year of NOAA's answers; before each request the year's rows and an estimate are checked against it.

## License

`license_verdicts.csv` records NOAA NCEI, read 9: "may be public", for public and for commercial use. The sentence: "IMPORTANT NOTE: The non-U.S. data in ISD are subject to WMO Resolution 40 restrictions, and cannot be redistributed to other users or customers." Its note: the ERW's weather tables hold U.S. stations only, and the readme names no license for U.S. data. `license_tables.csv` lists the table under NOAA NCEI; `docs/licenses.md` gives "may be public", flag public, ERW verdict public. The header's citations: NOAA NCEI (2001), Global Surface Hourly [ISD-Lite]; Kantor, Casey, Menne and Buddenberg (2023), Local Climatological Data (LCD), Version 2, https://doi.org/10.25921/96dw-mb77.

## Cross-checks (session 2074)

- The counts above were computed from the rows, read past the header lines. At every station hours measured, interpolated and missing add to 68,332; each grid's five weights add to 1 within 0.000001.
- Each station's `population_base_2020` equals `census_metro_population` in 35 of 35, and the weights recomputed from those populations match to within 0.0000005. Each `hours_measured` equals the count of that station's `temperature_f` rows in `noaa_station_weather_hourly` up to 2026-10-18T03:00:00Z in 35 of 35.

## What it does not hold

- The hours themselves: each station's in `noaa_station_weather_hourly`, each grid's in `noaa_grid_weather_hourly` and `noaa_grid_weather_daily`.
- A station for Kiryas Joel-Poughkeepsie-Newburgh, NY (698,330), larger than Syracuse (662,063), whose station is kept; the header and `docs/methods/demand_weather.md` say so.
- Session 126's stated twentieths, kept in the connector's station list and used for nothing.
