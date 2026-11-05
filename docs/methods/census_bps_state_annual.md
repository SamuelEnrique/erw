# New housing authorized by building permits, units, buildings and value by state and structure type, a year (U.S. Census Bureau, Building Permits Survey)

Energy Research Warehouse (ERW), method note written in session 2157 (chain 092) for a table first written on 23 October 2026 (session 2154).

Tables: `census_bps_state_annual`

## Publisher and address

U.S. Census Bureau, Building Permits Survey (BPS), the annual state files (plain text, comma separated), one a year:

`https://www2.census.gov/econ/bps/State/st<year>a.txt` (2015 to 2025)

The User-Agent is "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)". Source id `census:bps_state_annual`. Connector: `warehouse/connectors/census_bps.py` (session 2154), its only table. www2.census.gov's robots file names only some crawlers, none of them every reader. Session 2154's report: 13 requests of 15 (the robots file in a call of its own, the state directory's listing and the eleven annual files, 2024's first as a probe). Months were not taken: the monthly files are one a month (about 140 from 2015), past a session's ceiling.

The table is not scheduled: no line of `warehouse/run_daily.sh`, the other `warehouse/*.sh` scripts, `scripts/` or `.github/workflows/` names the connector (searched in session 2157), and `run_status.csv` holds no row for it. It was written once, by run `20261023T235703Z` on the data machine.

## Vintage and revision

2015 to 2025 (`ts_utc` 1 January of each year). The files were retrieved from 2026-10-23T23:53:30Z (2024's, the probe) to 23:55:56Z by the session's probe and trials, and reused by the write run. The rows' `vintage` is each file's Last-Modified: 2015's 2016-09-30, 2016's 2017-05-01, 2017's 2018-05-01, 2018's 2019-06-20, 2019's 2020-05-01, 2020's 2021-05-03, 2021's 2022-04-27, 2022's 2024-04-23, 2023's 2025-05-01, 2024's 2025-09-18, 2025's 2026-05-14. `coverage.csv` gives the same 6,984 rows, 54 entities and the same first and last `ts_utc`.

Each run writes the whole table again (`ip.write_snapshot`). The figures are the Bureau's estimates, which impute for permit offices that did not report, not its reported-only columns.

## Shape and variables

Series, 6,984 rows, 54 areas, twelve variables. `entity` `census_bps:<postal code, lower case>`; variables `buildings_<type>` and `units_<type>` (count) and `value_<type>` (USD, the Bureau's thousands of dollars times 1,000), type `1_unit`, `2_units`, `3_4_units` or `5_plus_units`; `freq` P1Y; `ts_utc` 1 January; `geo` US-<state>; `market` empty; `node` the area as the Bureau names it; `x_fips` the FIPS code; `x_code` the code the year's file gives it.

Areas a year: 53 (the 50 states, DC, Puerto Rico, the Virgin Islands) in most years, 52 in 2017 and 2020 (the files hold no Puerto Rico line), 54 in 2025 (American Samoa added). For the 50 states and DC, 561 rows a variable:

| Variable | Unit | Mean a state-year | Lowest | Highest |
|---|---|---|---|---|
| `buildings_1_unit` | count | 17,587.4 | 112 (DC, 2018) | 179,620 (Texas, 2021) |
| `units_1_unit` | count | 17,587.4 | 112 (DC, 2018) | 179,620 (Texas, 2021) |
| `value_1_unit` | USD | 4,751,667,335 | 26,302,000 (DC, 2018) | 46,062,625,000 (Texas, 2024) |
| `buildings_2_units` | count | 266.0 | 5 (New Mexico, 2016) | 3,178 (Texas, 2025) |
| `units_2_units` | count | 532.1 | 10 (New Mexico, 2016) | 6,356 (Texas, 2025) |
| `value_2_units` | USD | 81,257,185 | 1,175,000 (New Mexico, 2016) | 1,005,942,000 (Texas, 2025) |
| `buildings_3_4_units` | count | 103.2 | 0 (5 rows, DC 2025 among them) | 865 (Texas, 2022) |
| `units_3_4_units` | count | 370.9 | 0 (5 rows) | 3,302 (Texas, 2022) |
| `value_3_4_units` | USD | 54,979,526 | 0 (5 rows) | 423,540,000 (Texas, 2022) |
| `buildings_5_plus_units` | count | 330.7 | 3 (Rhode Island, 2015) | 2,864 (Texas, 2022) |
| `units_5_plus_units` | count | 9,486.9 | 39 (Rhode Island, 2015) | 100,834 (Texas, 2022) |
| `value_5_plus_units` | USD | 1,300,344,262 | 4,743,000 (Rhode Island, 2015) | 12,097,257,000 (Texas, 2022) |

`buildings_1_unit` equals `units_1_unit` in every row. The states and DC permitted 1,182,582 units in 2015, 1,736,982 in 2021 (the most), 1,680,368 in 2022 and 1,431,616 in 2025; single-family units 695,998 (2015), 1,115,360 (2021) and 911,903 (2025); the value 223.6 billion dollars (2015), 384.6 billion (2024) and 379.1 billion (2025). Texas, Florida and California permitted the most units in 2015, 2021 and 2025 (Texas 175,443, 265,955 and 210,217).

The territories: the Virgin Islands hold every year (6 single-family units in 2020, 207 in 2023); Puerto Rico has no row in 2017 and 2020, is 0 in every variable in 2021, and gives the same figures in 2016, 2018 and 2019 (1,554 single-family units valued at 107,067,000 dollars, 915 units in buildings of five or more); American Samoa, from 2025, has 3 single-family units and 41 units in buildings of five or more, each valued at 0. Puerto Rico's 2022 values are taken up under "Found while writing this note". The counts were computed in session 2157 from the rows, read past the 10 header lines; no (entity, variable, ts_utc) is given twice.

## Checks the connector makes

- Before any request, www2.census.gov is checked against `warehouse/metadata/paused_sources.csv` by connector and by host; a paused publisher stops the run with no request. It is not paused.
- Each file's two header rows must be as read; a line must have the header's number of fields and the survey date `<year>99`.
- Every figure among the estimates (four types of buildings, units and value) must be a whole number; an area name not in the map, an area given twice, a state or DC missing, or no United States row stops the run, and nothing is written. Areas are matched by the Bureau's names, since its codes changed.
- The 50 states and DC must sum to the United States row exactly in every count, and in value within 10 thousand dollars (the Bureau rounds each area's value); the header gives the largest difference met, 5 thousand dollars. The territories are not in the sum. The United States row is checked and not kept; the regions and divisions are not kept.
- Nothing is filled. Months, and the current year's year-to-date file, are not taken.
- Ceiling: one request a year, eleven in this run (2015 to 2025 by default, `--first` and `--last`), by the code's shape rather than a counter. A file saved in `warehouse/raw/census_bps/` is reused on every run, offline or not. Each address is tried up to four times, 5, 10 and 15 seconds apart (`ip.with_retries`); an HTTP 404 is not retried. Two seconds after each request.

## The cross-check

Session 2154 set each state's permitted units against the next year's growth in its residential electricity customers (`eia861_utility_sales`), 510 state-years from 2015 to 2024, in `runs/c092/s2154/cross.py` (on the data machine, not in git): Pearson 0.48 across state-years and 0.63 over each state's total, with about one new customer a permitted unit where most growth is (Texas 1.14, Florida 1.05, Georgia 0.98, North Carolina 0.94, Arizona 1.12). California's 5.95 the report puts down, likely, to EIA-861 counting a choice customer twice as community choice aggregation grew, a cause the check does not test.

## License

The header: "License: may be public (the Census Bureau, see license_verdicts.csv; its name is not to imply endorsement). Cite the U.S. Census Bureau, Building Permits Survey." `license_verdicts.csv` gives the Census Bureau "may be public" (read 17, the terms of its API; the same if the ERW sells anything), and `docs/licenses.md` gives the ERW verdict public. `sources.csv` and `coverage.csv`: public. Session 2154's report holds the table in the live set's catalogue hold and the release's storage hold, with the release package's rows.

## Found while writing this note

- Puerto Rico's 2022 values are a thousand times too large for their units, as far as the rows show. The Bureau's 2022 file gives Puerto Rico 506,472,827 in the single-family value column (thousands of dollars, as for every area) for 3,754 units; the table holds 506,472,827,000 USD, about 134.9 million dollars a unit, where the highest of the other areas in 2022 is Wyoming's about 531 thousand. Its 2 unit, 3 and 4 unit and 5 or more values (512,998,000, 477,870,000 and 51,625,685,000 USD) are alike, and so 559.1 billion dollars sits in Puerto Rico's 2022 rows; Puerto Rico's 2023 value is 433,561,000 USD for 2,941 single-family units. The figures look like dollars written in the thousands column. The territories are not in the sum check, so nothing stopped them, and they are the table's highest in three of the four value variables.
- The docstring says each file "must hold" the states, DC, Puerto Rico and the Virgin Islands. The 2017 and 2020 files hold no Puerto Rico line, and the run passed: the code requires only the 50 states and DC. The header's "54 areas: the states, DC, Puerto Rico, the Virgin Islands and, from 2025, American Samoa" does not say so.
- The docstring and session 2154's report say Puerto Rico is 43 and the Virgin Islands 52 "in the 2015 file, 72 and 78 later". The rows' `x_code`: Puerto Rico 43 in 2015, 2016, 2018, 2019 and 2021 and 72 from 2022; the Virgin Islands 52 from 2015 to 2021 and 78 from 2022.
- The docstring says "The regions, divisions and the United States are checked and not kept". The code skips the regions and divisions without a check; only the United States row is checked.
- The docstring says a saved file is reused because "a past year's file does not change". The rows' vintages show files last modified long after their year (2022's on 23 April 2024, 2024's on 18 September 2025); if the Bureau replaces a year's file, the connector, which never asks a saved year again, does not see it.
- Session 2154's report says "The nation's permits peaked at 1,737,150 units in 2021". That sum includes Puerto Rico and the Virgin Islands (its `cross.py` says so); the 50 states and DC, which the Bureau's United States row equals, give 1,736,982.
- The docstring's first lines name "session 2149's chain 092, session 2154"; chain 092 is not session 2149's, and the table is session 2154's.

**Acted on in session 2157:** the territories are no longer kept (Puerto Rico's lines repeat in 2016, 2018 and 2019, are missing in 2017 and 2020, are zero in 2021 and a thousand times the other years' values in 2022, and no national total checks them), so the table holds the states and DC, 6,732 rows; the docstring's session, its old codes and its regions and divisions (skipped, not checked) are corrected, and every year's file is asked again unless `--offline`. The figures above that count the territories are from before this change. Session 2154's report carries an addendum (the 2021 peak is 1,736,982 units for the states and DC).

## What it does not hold

- Months, and the current year's year-to-date figures.
- The reported-only columns, and counties, metropolitan areas and places.
- Housing started or completed: these are units authorized by permit.
