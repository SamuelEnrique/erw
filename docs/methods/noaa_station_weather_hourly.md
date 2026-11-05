# Temperature and dew point at 35 airport stations as NOAA measured them, an hour, from 2019 (NOAA NCEI, ISD-Lite and Local Climatological Data)

Energy Research Warehouse (ERW), method note written in session 2256 (chain 102) for a table first written on 6 October 2026 (session 129).

Tables: `noaa_station_weather_hourly`

## Publisher and address

NOAA National Centers for Environmental Information (NCEI). Two products of the same stations' reports:

- ISD-Lite, one file a station and year, 2019 to 2025, used for hours before 2025-08-01T00:00:00Z (NOAA's database ends on 27 August 2025):

  `https://www.ncei.noaa.gov/pub/data/noaa/isd-lite/<year>/<USAF>-<WBAN>-<year>.gz`

- Local Climatological Data, version 2, through NCEI's Access Data Service, used from 2025-08-01T00:00:00Z, and for Minneapolis-St. Paul from 1 April 2020 to 30 November 2022:

  `https://www.ncei.noaa.gov/access/services/data/v1?dataset=local-climatological-data-v2&stations=USW000<WBAN>&startDate=<day>T00:00:00&endDate=<day>T23:59:59&dataTypes=HourlyDryBulbTemperature,HourlyDewPointTemperature&format=csv`

The station list is `https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv`. The User-Agent is "ERW energy research warehouse (https://github.com/SamuelEnrique/erw)". NCEI's robots file disallows `/data*`, `/orders*` and some `/access/crn/` paths, not `/pub/` (read 258 of `warehouse/metadata/license_reads.csv`, session 2107); the connector's paths are under none of them.

Source ids `noaa:isd_lite` and `noaa:lcd_v2`. Connector: `warehouse/connectors/noaa_grid_weather.py` (session 126; this table added in session 129), which writes it with `noaa_grid_weather_hourly`, `noaa_grid_weather_daily` and `noaa_grid_weather_stations`. With this table the grid tables can be rebuilt with other weights on a machine that never held NOAA's files (`noaa_grid_weather.py --from-table`), and `warehouse/derived/demand_weather.py` reads it for its trial of New England on four stations of five. Method: `docs/methods/demand_weather.md` ("The stations' hours as a table").

Schedule: `warehouse/run_data_machine_tables.sh`, step `dm_noaa_weather` (`noaa_grid_weather.py --refresh`), once a week, sourced by `warehouse/run_data_machine.sh`, the data machine's daily run ("ERW data machine daily", `scripts/register_data_machine_daily.ps1`). No line of `warehouse/run_daily.sh` or `.github/workflows/` names the connector, and `warehouse/metadata/run_status.csv` holds no row for it. The table is written only from NOAA's files: a run with `--from-table` leaves it as it is, and a trial (`--out-dir`) writes it only with `ERW_STATION_TABLE_TRIAL=1`.

The first date is that of the commit that first adds the table's coverage row, `d551f114`, 6 October 2026 at 01:09 UTC ("Session 129: demand growth without weather, finished"); session 129's report gives that build 4,714,333 rows. No run log of that day is on the data machine, so the hour of the first write was not established.

## Vintage and revision

Hours 2019-01-01T00:00:00Z to 2026-10-18T03:00:00Z, written by run `20261021T084557Z`; every row's `retrieved_at` is 2026-10-21T08:46:47Z, and `vintage` is empty. `coverage.csv` gives the same 4,747,179 rows, 35 nodes and the same first and last `ts_utc` (last run 2026-10-21T08:45:57Z); `archive_manifest.csv` holds 4,747,179 rows (run `20261021T085120Z-local`).

Each run deletes the table and writes it whole, cut to the hours from 1 January 2019 to the last hour every station reaches, so a station's later hours wait for the slowest station. With `--refresh` the Local Climatological Data is asked again from a week before the newest hour held, and the later answer's hours replace the held ones from its own first hour on.

## Shape and variables

Series, 4,747,179 rows, 35 entities, 2 variables: `temperature_f` (2,373,787 rows) and `dew_point_f` (2,373,392). `entity` `noaa:<GHCN identifier>` (`USW000` and the WBAN); `node` the airport; `ba` the grid the station stands for (ciso, erco, isne, miso, nyis, pjm, swpp), the partition column; `geo` `US-<the station's state>`; `unit` degF; `freq` PT1H; `ts_utc` the hour (the reading taken in the ten minutes up to it); `market` empty. There are no `x_` columns. A value is NOAA's tenth of a degree C times 9/5 plus 32, to two decimals; every one of the 4,747,179 values turns back to a tenth of a degree C exactly. Measured values only: an hour with no reading has no row, and no interpolated value is written.

| Grid | Airport | Entity | `geo` | temperature_f rows | dew_point_f rows |
|---|---|---|---|---|---|
| CAISO | LAX | noaa:USW00023174 | US-CA | 68,165 | 68,117 |
| CAISO | ONT | noaa:USW00003102 | US-CA | 68,143 | 68,096 |
| CAISO | SAN | noaa:USW00023188 | US-CA | 68,148 | 68,125 |
| CAISO | SFO | noaa:USW00023234 | US-CA | 68,140 | 68,134 |
| CAISO | SJC | noaa:USW00023293 | US-CA | 68,080 | 68,055 |
| ERCOT | AUS | noaa:USW00013904 | US-TX | 68,105 | 68,055 |
| ERCOT | DFW | noaa:USW00003927 | US-TX | 68,149 | 68,144 |
| ERCOT | IAH | noaa:USW00012960 | US-TX | 68,187 | 68,185 |
| ERCOT | MFE | noaa:USW00012959 | US-TX | 68,039 | 68,018 |
| ERCOT | SAT | noaa:USW00012921 | US-TX | 68,168 | 68,165 |
| ISO-NE | BDL | noaa:USW00014740 | US-CT | 68,167 | 68,166 |
| ISO-NE | BDR | noaa:USW00094702 | US-CT | 67,855 | 67,841 |
| ISO-NE | BOS | noaa:USW00014739 | US-MA | 68,077 | 68,074 |
| ISO-NE | ORH | noaa:USW00094746 | US-MA | 68,040 | 68,012 |
| ISO-NE | PVD | noaa:USW00014765 | US-RI | 68,049 | 68,001 |
| MISO | DTW | noaa:USW00094847 | US-MI | 64,299 | 64,296 |
| MISO | IND | noaa:USW00093819 | US-IN | 68,185 | 68,182 |
| MISO | MKE | noaa:USW00014839 | US-WI | 68,158 | 68,158 |
| MISO | MSP | noaa:USW00014922 | US-MN | 68,070 | 68,070 |
| MISO | STL | noaa:USW00013994 | US-MO | 68,097 | 68,096 |
| NYISO | ALB | noaa:USW00014735 | US-NY | 68,160 | 68,159 |
| NYISO | BUF | noaa:USW00014733 | US-NY | 64,750 | 64,744 |
| NYISO | LGA | noaa:USW00014732 | US-NY | 68,169 | 68,165 |
| NYISO | ROC | noaa:USW00014768 | US-NY | 64,789 | 64,788 |
| NYISO | SYR | noaa:USW00014771 | US-NY | 68,150 | 68,150 |
| PJM | BWI | noaa:USW00093721 | US-MD | 68,188 | 68,184 |
| PJM | DCA | noaa:USW00013743 | US-VA | 68,156 | 68,152 |
| PJM | ORD | noaa:USW00094846 | US-IL | 68,157 | 68,153 |
| PJM | PHL | noaa:USW00013739 | US-PA | 68,154 | 68,152 |
| PJM | PIT | noaa:USW00094823 | US-PA | 68,180 | 68,178 |
| SPP | ICT | noaa:USW00003928 | US-KS | 68,125 | 68,121 |
| SPP | MCI | noaa:USW00003947 | US-MO | 68,170 | 68,159 |
| SPP | OKC | noaa:USW00013967 | US-OK | 68,156 | 68,152 |
| SPP | OMA | noaa:USW00014942 | US-NE | 68,023 | 68,017 |
| SPP | TUL | noaa:USW00013968 | US-OK | 68,139 | 68,128 |

The span holds 68,332 hours. Every station's last hour is 2026-10-18T03:00:00Z; its first is 2019-01-01T00:00:00Z, except MFE, OMA, ONT, ORH and SJC, whose first reading is at 01:00. Detroit (4,033), Buffalo (3,582) and Rochester (3,543) lack the most hours, an hour or a few on most days in ISD-Lite at the same hours of the clock. Rows by year run from 602,474 (2025) to 611,330 (2020); 2026 holds 484,362 to 18 October.

Temperature: mean 58.46 F, lowest -27.94 (MSP, 2019-01-30 13:00 UTC), highest 116.96 (ONT, 2020-09-05 22:00 UTC). Dew point: mean 45.91 F, lowest -36.94 (MSP, 2026-01-23 07:00 UTC), highest 82.94 (MCI, 2023-07-27 01:00 UTC).

`source` is `noaa:isd_lite` in 3,967,189 rows and `noaa:lcd_v2` in 779,990, of which 46,730 are Minneapolis-St. Paul's from April 2020 to November 2022 (23,365 hours, as the header says). `source_url` is the ISD-Lite directory of the hour's year, or the Access Data Service's address without its station and dates.

The counts in this note were computed in session 2256 with pandas from the rows of `warehouse/output/noaa_station_weather_hourly.csv` on the data machine, read past its 51 header lines as strings; no (entity, variable, ts_utc) is given twice.

## Checks the connector makes

- Before any request, `iso_prices.paused("noaa")`; a paused publisher ends the run with exit 1 and no request. NOAA is not paused. `iso_prices.paused_host()` is not asked.
- NOAA's station list must hold each of the 35 stations exactly once, or the run stops.
- A saved file is read from `warehouse/raw/noaa_grid_weather/` and not asked again. Each request is tried up to four times, 5, 10 and 15 seconds apart (`ip.with_retries`); an HTTP 404 is not retried. 0.4 seconds after each request.
- An answer of the Access Data Service that does not begin with its header, or whose newest report is more than 21 days before the last day asked, is counted against the ceiling, not used, and asked again, up to four times; the fourth stops the run.
- Only reports whose type begins "FM" are read; a value NOAA marks with a letter or star, or leaves blank, is not read and is counted. Local standard time is moved to UTC, and an hour takes the report from ten minutes before it up to it, the closest. In ISD-Lite, -9999 is no reading.
- The seam: a station whose two products agree to a tenth of a degree C in fewer than 90 percent of the shared hours outside the eight synoptic hours stops the run, and nothing is written; each station's agreement is in the header's "Stations" lines (AUS agrees in 28.57 percent of the synoptic hours, every station in at least 99.89 percent of the others).
- Ceiling: 5,000,000 rows for this table; above it the table is not written. 6,000,000 rows a UTC year of NOAA's answers (`ceiling.json`), checked with an estimate before each request.
- The write needs the data lock (`ip.write_csv`).

## License

The header: "License: public. U.S. stations only. NOAA NCEI's record for the database gives a citation and two statements of liability and names no license; its readme restricts only non-U.S. data (WMO Resolution 40)." with the two citations: NOAA National Centers for Environmental Information (2001), Global Surface Hourly [ISD-Lite]; and Kantor, Casey, Menne and Buddenberg (2023), Local Climatological Data (LCD), Version 2, https://doi.org/10.25921/96dw-mb77. `license_verdicts.csv` gives NOAA NCEI "may be public" (read 9). `license_tables.csv` names NOAA NCEI as the one publisher; `docs/licenses.md` gives the ERW verdict public; `coverage.csv`: public. The table is under `catalogue_hold` in `warehouse/supabase/live_set.yaml`, not loaded.

## Cross-checks (session 2256)

- Each station's `temperature_f` rows equal its `hours_measured` in `noaa_grid_weather_stations`, 35 of 35, and the counts in the header's "Stations" lines.
- `noaa_grid_weather_hourly`'s temperature, in every hour no station is interpolated, is the weighted mean of these rows to within 0.005 F.

## Found while writing this note

- `iso_prices.paused_host()` is not asked before a request; `paused("noaa")` is.
- The connector's docstring opens with "Three series tables" and lists three; this table is the fourth, named later in the docstring (session 129).
- `docs/methods/demand_weather.md` still gives each station's hours measured from the build of 6 October 2026 (Dallas-Fort Worth 67,680, for one); this table and the stations table now hold 68,149 for it, to 18 October 2026.

## What it does not hold

- Interpolated hours: the grid tables fill runs of at most three hours and count them; this table holds none.
- Hours after the last hour every station reaches, though a station's own file may hold them.
- Wind, cloud, pressure, precipitation, or any station beyond the 35; hours before 2019.
