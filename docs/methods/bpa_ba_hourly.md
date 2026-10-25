# The Bonneville Power Administration's balancing authority, its load, generation by fuel and net interchange, an hour (BPA, VER and Balancing Authority Monitoring)

Energy Research Warehouse (ERW), method note written in session 2157 (chain 092) for a table first written on 23 October 2026 (session 2148).

Tables: `bpa_ba_hourly`

## Publisher and address

Bonneville Power Administration (BPA), Transmission Services, VER and Balancing Authority Monitoring: the yearly workbooks of "Total Load, Wind Gen, Wind Forecast, Solar Gen, Solar Forecast, Hydro, Thermal, and Net Interchange" in five-minute values. The connector reads the page

`https://transmission.bpa.gov/Business/Operations/Wind/default.aspx`

and takes from it each year's link,

`https://transmission.bpa.gov/Business/Operations/Wind/OPITabularReports/WindGenTotalLoadYTD_<year>.xls[x]`

(`.xls` for 2020 and 2021, `.xlsx` from 2022), from 2020 to the latest year the page links (2026 in this run). The User-Agent is "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)". Source id `bpa:ba_load_generation`. Connector: `warehouse/connectors/bpa_ba.py` (session 2148), its only table. transmission.bpa.gov has no robots file of its own: its `/robots.txt` is sent on to www.bpa.gov, whose robots file disallows only `/customerportal/` (the docstring). Session 2148's report: 14 requests of 15, among them one 404 at BPA's old address for the yearly files, which the VER page's links replaced.

The table is not scheduled: no line of `warehouse/run_daily.sh`, the other `warehouse/*.sh` scripts, `scripts/` or `.github/workflows/` names the connector (searched in session 2157), and `run_status.csv` holds no row for it. It was written once, by run `20261023T233153Z` on the data machine.

## Vintage and revision

1 January 2020 to 23 October 2026: `ts_utc` 2020-01-01T08:00:00Z (midnight Pacific) to 2026-10-23T06:00:00Z (the hour from 23:00 Pacific daylight time on 22 October). The page and the seven workbooks were retrieved from 2026-10-23T23:26:21Z to 23:27:26Z by the session's probe and reused by the write run (its log says "raw file reused" for each). The rows' `vintage` is each workbook's Last-Modified: 2020's 2021-11-01, 2021's 2022-01-28, 2022's 2024-05-14, 2023's 2024-05-12, 2024's 2025-10-30, 2025's 2026-01-01 and 2026's 2026-10-23T08:40:16Z. `coverage.csv` gives the same 400,261 rows, 1 entity and the same first and last `ts_utc`.

Each run writes the whole table again (`ip.write_snapshot`). BPA's notes, quoted in the header: the figures are the balancing authority's loads and resources, some of them not BPA's; BPA loads served by transfer, scheduled out of the region or served in other balancing authorities (Seattle's, Tacoma's) are not in the load; the values are five-minute interpolated snapshots.

## Shape and variables

Series, 400,261 rows, one entity, seven variables. `entity` `bpa:bpat`; `unit` MW (an hour's mean of BPA's five-minute values, so equal to the hour's MWh); `freq` PT1H; `ts_utc` the hour's start; `geo` empty (the area spans Oregon, Washington, Idaho and Montana); `market` empty; `node` "BPA balancing authority"; `ba` bpat; `x_intervals` the five-minute values in the hour (12 when full); `x_format` old (2020 and 2021 files, Pacific local time put into UTC; 105,264 rows, to 2022-01-01T07:00:00Z) or new (BPA's UTC column, from 2022; 294,997 rows). Every file, the new ones too, runs from midnight Pacific on 1 January.

| Variable | Rows | Mean MW | Lowest | Highest | Notes |
|---|---|---|---|---|---|
| `load` | 59,687 | 6,598.1 | 4,116.5 (2020-09-28 09:00 UTC) | 11,426.0 (2025-02-12 15:00 UTC) | |
| `hydro_generation` | 59,686 | 7,380.8 | 2,837.75 (2026-10-17 19:00 UTC) | 14,914.5 (2022-06-25 02:00 UTC) | |
| `wind_generation` | 59,686 | 777.5 | 0 (151 hours) | 2,848.139 (2026-05-29 21:00 UTC) | |
| `solar_generation` | 42,142 | 54.7 | 0 (13,155 hours) | 457.417 (2026-06-11 20:00 UTC) | from 2022-01-01T08:00:00Z |
| `thermal_generation` | 59,686 | 778.9 | 55.167 (2026-06-20 06:00 UTC) | 1,275.667 (2022-12-22 10:00 UTC) | BPA's fossil and biomass |
| `nuclear_generation` | 59,687 | 1,034.5 | 0 (4,156 hours) | 1,183.417 (2020-02-04 15:00 UTC) | |
| `net_interchange` | 59,687 | 3,422.2 | -2,117.75 (2024-01-16 09:00 UTC) | 11,020.25 (2022-06-28 13:00 UTC) | positive an export; 784 hours below 0 |

Hours: every hour from the first to the last is present for load, net interchange and nuclear. Hydro, wind, solar and thermal lack one, 2026-09-23 02:00 UTC, where BPA's five-minute values are empty. `x_intervals` is 12 in 400,177 rows; the 84 short rows (11 values in 56, 10 in 13, 7 in 7, 5 in 4, 4 in 4) fall in 13 hours: 2021-11-10 20:00 (six variables), 2022-01-11 16:00, 2022-02-02 00:00, 2022-04-23 02:00, 2022-06-23 21:00, 2022-07-18 19:00, 2022-09-19 09:00, 2022-10-10 22:00, 2024-12-19 18:00, 2025-05-01 14:00 and 15:00 (all seven each), and 2026-09-23 01:00 and 03:00 (hydro, wind, solar and thermal). Nuclear is 0 for 61 hours in Pacific year 2020, 1,171 in 2021, 1,063 in 2023, 1,729 in 2025 and 132 in 2026. Net interchange is below 0 in 1 hour of 2021, 176 of 2023, 165 of 2024, 158 of 2025 and 284 of 2026 to date, none in 2020 or 2022.

Summed by Pacific year (TWh): load 54.96 (2020), 57.23 (2022), 58.23 (2024), 60.02 (2025); hydro 73.54 (2020), 74.35 (2022), 56.52 (2023), 56.21 (2024), 59.72 (2025); net interchange 41.96 (2020), 40.50 (2022), 22.31 (2023), 21.77 (2024), 21.75 (2025). The counts above were computed in session 2157 from the rows, read past the 10 header lines; no (entity, variable, ts_utc) is given twice.

## Checks the connector makes

- Before any request, BPA is checked against `warehouse/metadata/paused_sources.csv` by connector and by host (`ip.paused`, `ip.paused_host`); a paused publisher stops the run with no request. BPA is not paused.
- The page must link at least one `WindGenTotalLoadYTD_<year>` workbook. Every sheet but "Details" must hold a header row beginning "Date/Time"; a file whose sheets mix the old and new formats stops the run.
- Each variable's column is found by BPA's words (upper case, spaces squeezed), forecast columns excluded; a variable with no column, or with two, stops the run, except solar, which the old format lacks.
- A cell that is not a number, a time given twice, a step that is not five minutes (in UTC, so the old format's clock changes pass), or an old-format time outside its year stops the run, and nothing is written. The old format's November repeated hour is placed by order (`ambiguous="infer"`), the second time through. An (entity, variable, ts_utc) given twice across files stops the run.
- An empty five-minute value takes no part in its hour's mean; an hour with no value of a variable has no row. Forecasts (base schedules and basepoints) are not taken. Nothing is filled.
- Ceiling: the page and one workbook a year from 2020 to the latest linked, eight in this run, by the code's shape rather than a counter. The page and the latest year's workbook are asked again unless `--offline`; an earlier year's workbook is reused from `warehouse/raw/bpa_ba/` when one is saved. Each address is tried up to four times, 5, 10 and 15 seconds apart (`ip.with_retries`); an HTTP 404 is not retried. One second after the page, two after each workbook.

## The cross-check

Session 2148 set BPA's load, summed to the day, against EIA-930's BPAT daily demand (`eia930_daily_demand`) in `runs/c092/s2148/cross.py` (on the data machine, not in git): over 2,477 full days the median ratio was 0.987 (5th and 95th percentiles 0.97 and 1.02), on Pacific and UTC days alike, so BPA's own load runs about 1.3 percent below EIA's figure. It also found BPA's balance closes: in 2024 generation less load was 21.75 TWh against a net interchange of 21.76 TWh.

## License

The header: "License: may be public (BPA is a power marketing administration of the Department of Energy, whose notice puts government information on its websites in the public domain and asks that the Department be acknowledged; see license_verdicts.csv). Cite the Bonneville Power Administration." `license_verdicts.csv` gives BPA "may be public" (the Department of Energy's notice, read 54, taken for BPA in session 2047; the same if the ERW sells anything), and `docs/licenses.md` gives the ERW verdict public. `sources.csv` and `coverage.csv`: public. Session 2153 confirmed the verdict. Session 2148's report holds the table in the live set's catalogue hold (`warehouse/supabase/live_set.yaml`) and the release's storage hold (`warehouse/redivis/release_v1.py`), with the release package's rows.

## Found while writing this note

- The docstring says the latest year's file is asked again "(they change)" and "an earlier year's file is reused". The rows' vintages show BPA rewrites a year's workbook after the year ends: 2022's on 14 May 2024, 2023's on 12 May 2024, 2024's on 30 October 2025, 2025's on 1 January 2026. A later run reuses the saved copy of every earlier year and so misses such a rewrite. In 2027 the latest linked year becomes 2027, and the 2026 workbook saved on 23 October 2026 would be reused: the table would not gain 23 October to 31 December 2026 until the raw file is moved or the rule changed.
- The header says the 84 short hours are "empty values, or the year's last hours". None of them is at a year's end: all 84 are inside the series, where BPA's five-minute values are empty.

**Acted on in session 2157:** the connector now asks for every year's workbook again unless `--offline` (BPA rewrites past years' files), and the header says the 84 short hours come from empty values in BPA's files; the table was written again offline.

## What it does not hold

- BPA's forecasts (wind and solar forecasts, base schedules, basepoints).
- The five-minute values themselves: hourly means only (the five-minute rows would be about 4.8 million).
- Years before 2020, and other balancing authorities (EIA-930 holds BPAT among them).
