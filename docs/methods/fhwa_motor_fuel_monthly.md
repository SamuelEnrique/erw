# Gasoline and special fuels each state reports taxed, a month (FHWA's Monthly Motor Fuel data on DOT's DataHub)

Energy Research Warehouse (ERW), method note written in session 2038 (chain 058) for a table first written on 23 October 2026 (session 2035).

Tables: `fhwa_motor_fuel_monthly`

## Publisher and address

U.S. Department of Transportation, Federal Highway Administration (FHWA), Office of Highway Policy Information: the source data of its Monthly Motor Fuel Report, published as two datasets on DOT's DataHub (`data.transportation.gov`, a Socrata site; the DataHub story "Monthly Motor Fuel Report", `https://data.transportation.gov/stories/s/nrec-wf7k`, `STORY`). FHWA's own site stopped publishing the monthly reports after December 2023 (`https://www.fhwa.dot.gov/policyinformation/motorfuelhwy_trustfund.cfm`, the docstring).

| Variable | Dataset | Address | Volume column |
|---|---|---|---|
| `gasoline_volume` | Monthly Motor Fuel - Gasoline Volumes Distributed (`5qxh-t94v`) | `https://data.transportation.gov/api/views/5qxh-t94v/rows.csv?accessType=DOWNLOAD` | VOL GASOLINE |
| `special_fuel_volume` | Monthly Special Fuel Volumes Distributed (`5n49-mh85`) | `https://data.transportation.gov/api/views/5n49-mh85/rows.csv?accessType=DOWNLOAD` | VOL SPEC FUEL |

Both have the columns STATE, YEAR, MONTH, the volume, DATA TYPE and DATE MODIFIED. Two requests a run, a pause of 1.5 seconds after each (the DataHub's robots file asks one second), timeout 120 seconds, with the ERW's user agent (`UA`). Source id `fhwa:monthly_motor_fuel`. Connector: `warehouse/connectors/fhwa_motor_fuel.py` (session 2035).

## Vintage and revision

The file on the data machine was written by run `20261023T194440Z` (23 October 2026), as its header says, from the two files session 2035 saved and the write reused offline. `retrieved_at` 2026-10-23T19:42:07Z (gasoline) and 2026-10-23T19:42:12Z (special fuels); `vintage`, the files' Last-Modified, 2026-09-29T21:01:49Z and 2026-09-29T21:04:18Z.

The two files are fetched fresh on every run that is not `--offline` (`ip.fetch_raw` with `fresh`), so FHWA's revisions and new months are taken. Each run replaces the table whole (`ip.write_snapshot`). `x_date_modified` gives each row's DATE MODIFIED as published (12/14/2023 12:00:00 AM, for one): it falls in 2023 on 3,744 rows, 2024 on 1,248 and 2026 on 3,006. No age check is made.

## Shape and variables

Series, 7,998 rows: 52 places, two variables, 104 series, January 2020 to May 2026 (77 months), 3,999 rows of each variable. 102 series have all 77 months; North Carolina's two have 72, ending December 2025 (its five months of 2026 are "Not Published", below). No value is 0.

- `entity` `fhwa_mf:<state code>`; `geo` US-<state code>: the 50 states, the District of Columbia and Puerto Rico; `node` the place as FHWA names it.
- `variable` `gasoline_volume` or `special_fuel_volume` (special fuels: diesel, mostly, and alternative fuels); unit `gal`, the gallons the state reports taxed, as FHWA compiles them (Decision 59 of `docs/datastandard.md`).
- `ts_utc` the month's first day; `freq` P1M; `market` empty.
- `x_data_type` the dataset's DATA TYPE:

| `x_data_type` | `gasoline_volume` | `special_fuel_volume` |
|---|---|---|
| Actual | 3,962 | 3,924 |
| Estimate | 35 | 75 |
| Gas Holiday | 2 | 0 |

Gas Holiday is Georgia's April and May 2026, the months its gasoline tax was suspended; the volumes are those still taxed. The most estimated series is Oregon's special fuels, 41 months.

## Reading the source

- A dataset without its six columns stops the run.
- A place not in `PLACES` (the 50 states, DC, Puerto Rico), a month name or year not known, a data type other than Actual, Estimate, Gas Holiday or Not Published, a volume not a number (commas allowed), or a state and month given twice stops the run.
- Two kinds of row are not written, and are counted in the header: a "Not Published" row, whose volume is a 0 that measures nothing (5 a variable, North Carolina's January to May 2026); and every row of a month in which every place reads 0 (364 a variable, June to December 2026: the datasets carry the rest of the current year before the states report). Nothing is filled.
- Each request is tried up to 4 times (`iso_prices.with_retries`), waiting 5 seconds times the attempt number after each failure; HTTP 404 is a `SourceGap`, not retried; any answer but HTTP 200 is a failure.
- Ceiling: two requests. No row ceiling is set in the code.
- Any failure is recorded as a failure, and no file is written.
- The connector does not call `iso_prices.paused()`; FHWA and DOT are not in `warehouse/metadata/paused_sources.csv`.

## License

Public. `sources.csv` has `public` for `fhwa:monthly_motor_fuel`; the header: "License: public (each dataset's metadata: "Public Domain"; cite "FHWA, Office of Highway Policy Information")." `license_verdicts.csv`, U.S. Department of Transportation, Federal Highway Administration (FHWA), read 210 (the special fuel dataset's record on DOT DataHub, `https://data.transportation.gov/api/views/5n49-mh85.json`, read 23 October 2026): "Public Domain U.S. Government". Verdict: may be public, and may be public for commercial use. Its note: the record's terms link is `https://www.usa.gov/government-works`; the gasoline dataset's record gives "Public Domain"; attribution to FHWA, Office of Highway Policy Information.

Robots (session 2035): read 208, `www.fhwa.dot.gov`'s file, a one-second crawl delay, `/policyinformation/travel_monitoring/` and other paths disallowed, not `/policyinformation/motorfuel`; read 209, `data.transportation.gov`'s file, a one-second crawl delay, only its browse, search and facet paths disallowed.

## Cross-checks (session 2038)

- The counts above were computed from the rows, read past the header lines; no (entity, variable, ts_utc) appears twice, and the rows of each variable equal the header's.
- Session 2035's cross-check, recomputed: the 50 states and DC summed to the year (Puerto Rico left out), against `eia_product_supplied_monthly`'s U.S. product supplied (thousand barrels at 42 gallons, twelve months each year):

| Year | FHWA gasoline, billion gal | EIA finished motor gasoline (`MGFUPUS1`) | Ratio | FHWA special fuels | EIA distillate fuel oil (`MDIUPUS1`) | Ratio |
|---|---|---|---|---|---|---|
| 2020 | 127.89 | 123.73 | 1.034 | 42.06 | 58.19 | 0.723 |
| 2021 | 140.09 | 135.14 | 1.037 | 45.31 | 60.89 | 0.744 |
| 2022 | 139.63 | 135.06 | 1.034 | 45.30 | 61.71 | 0.734 |
| 2023 | 141.91 | 137.13 | 1.035 | 45.17 | 60.03 | 0.752 |
| 2024 | 141.59 | 137.83 | 1.027 | 45.71 | 58.29 | 0.784 |
| 2025 | 141.35 | 136.97 | 1.032 | 45.55 | 59.91 | 0.760 |

  The special fuels are a part of EIA's distillate, which also counts heating oil and the rail, marine and off-road diesel the states' highway taxes do not (session 2035's reading, not tested here).

## What it does not hold

- Months before January 2020: FHWA's monthly workbooks of January 2012 to December 2023 were not taken.
- Gallons by use, tax rates or receipts: each dataset read gives one volume a state and month.
- The months the datasets carry as zeros before the states report, and the months marked Not Published.
- U.S. product supplied: `eia_product_supplied_monthly`.
