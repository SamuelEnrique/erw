# Ontario's generation by fuel, an hour (the IESO's Generator Output by Fuel Type Hourly Report)

Energy Research Warehouse (ERW), method note written in session 2233 (chain 099) for a table first written on 24 October 2026 (session 2224).

Tables: `ieso_generation_fuel_hourly`

## Publisher and address

Independent Electricity System Operator (IESO), Ontario, "Generator Output by Fuel Type Hourly Report", one XML file a year on its public reports site: the listing `https://reports-public.ieso.ca/public/GenOutputbyFuelHourly/` and each year's file at `https://reports-public.ieso.ca/public/GenOutputbyFuelHourly/PUB_GenOutputbyFuelHourly_<YEAR>.xml`. Source id `ieso:gen_output_by_fuel_hourly`. Connector: `warehouse/connectors/ieso_genfuel.py` (session 2224), one step: it asks for (or reuses) each year's file and writes the whole table, under the data lock. reports-public.ieso.ca has no robots file (HTTP 404, sessions 2070 and 2224).

## Vintage and revision

Hours from 1 January 2020 (Ontario's first hour, 2020-01-01T05:00:00Z) to the hour ending 24:00 on 22 October 2026 (2026-10-23T04:00:00Z), seven files, written by run `20261024T020132Z` (24 October 2026). That run read the files saved by the trial (its log: "raw file reused" for each year); the header's "Retrieved: 20261024T020132Z" (written by the connector's line 155) is the run's id, not a retrieval time, and unlike the other tables of chain 099 the header states no retrieval time beside it. The rows' `retrieved_at` gives the retrieval.

| File | Rows | `vintage` (the file's CreatedAt) | `retrieved_at` |
|---|---|---|---|
| 2020 | 52,704 | 2021-01-01T11:50:49Z | 2026-10-24T01:57:52Z |
| 2021 | 52,560 | 2022-01-01T11:50:44Z | 2026-10-24T01:58:04Z |
| 2022 | 52,560 | 2023-01-01T11:50:41Z | 2026-10-24T01:58:15Z |
| 2023 | 52,560 | 2024-01-01T11:50:48Z | 2026-10-24T01:58:25Z |
| 2024 | 52,704 | 2025-01-01T11:50:47Z | 2026-10-24T01:58:36Z |
| 2025 | 59,118 | 2026-01-01T11:50:43Z | 2026-10-24T01:58:47Z |
| 2026 | 49,575 | 2026-10-23T11:50:49Z | 2026-10-24T01:58:57Z |

`vintage` is the file's DocHeader CreatedAt, read as Eastern Standard Time and written in UTC. The server's Last-Modified differs: 23 October 2024 for the files of 2020 to 2023 (the raw manifest), so the IESO has posted those files again after their CreatedAt. The current year's file is asked for again on every run that is not `--offline`; an earlier year's file is reused from `warehouse/raw/ieso_genfuel/` once saved, so a later revision of an earlier year is not read unless its saved file is removed. Each run writes the table again from every year read (`write_snapshot`): the file is replaced, not merged.

## Shape and variables

Series, 371,781 rows, 59,688 hours. `entity` ieso:ontario; `unit` MWh (the hour's energy, the report's Output); `freq` PT1H; `geo` CA-ON; `market` blank; `node` the fuel as the IESO names it; extra column `x_quality`, the report's OutputQuality as published. `ts_utc` is the hour's start in UTC: the IESO's hour is an hour ending in Eastern Standard Time all year, so `ts_utc` is the day's midnight plus the hour less one, plus five hours.

| `variable` | `node` | Rows | First hour |
|---|---|---|---|
| generation_nuclear | NUCLEAR | 59,688 | 2020-01-01T05:00:00Z |
| generation_gas | GAS | 59,688 | 2020-01-01T05:00:00Z |
| generation_hydro | HYDRO | 59,688 | 2020-01-01T05:00:00Z |
| generation_wind | WIND | 59,688 | 2020-01-01T05:00:00Z |
| generation_solar | SOLAR | 59,688 | 2020-01-01T05:00:00Z |
| generation_biofuel | BIOFUEL | 59,688 | 2020-01-01T05:00:00Z |
| generation_other | OTHER | 13,638 | 2025-04-02T18:00:00Z |
| control_actions | CONTROL ACTIONS | 15 | 2026-07-15T14:00:00Z |

TWh a calendar year of UTC hours (2020 holds 8,779 hours, as its first five UTC hours fall before Ontario's first hour; 2026 runs to 23 October):

| Year | Nuclear | Gas | Hydro | Wind | Solar | Biofuel | Other | All |
|---|---|---|---|---|---|---|---|---|
| 2020 | 87.45 | 10.05 | 36.35 | 11.83 | 0.70 | 0.32 | | 146.69 |
| 2021 | 82.45 | 12.58 | 33.74 | 12.06 | 0.70 | 0.35 | | 141.87 |
| 2022 | 78.26 | 15.76 | 37.51 | 13.87 | 0.70 | 0.26 | | 146.35 |
| 2023 | 78.77 | 19.81 | 36.84 | 12.24 | 0.68 | 0.30 | | 148.64 |
| 2024 | 79.44 | 25.47 | 37.34 | 13.38 | 0.69 | 0.29 | | 156.60 |
| 2025 | 77.92 | 32.18 | 37.01 | 14.17 | 0.67 | 0.29 | 0.18 | 162.41 |
| 2026 | 63.01 | 30.50 | 30.14 | 10.30 | 0.59 | 0.21 | 0.61 | 135.35 |

The largest hourly values: nuclear 12,208, gas 8,923, hydro 7,999, wind 4,601, other 1,046, solar 433, biofuel 267 MWh. 46,750 rows are 0; none is negative.

`x_quality`, as published (the IESO's schema, which would define the codes, was not read): 0 in 302,581 rows, -1 in 34,937, -2 in 20,014, -3 in 12,590, -4 in 967, -5 in 452, -6 in 226, -7 in 9, -8 in 3, -12 and -30 in 1 each. Gas carries most of the codes other than 0: 0 in only 6,291 of its 59,688 rows. The table does not interpret them.

CONTROL ACTIONS is the IESO's line, not a fuel, and is written as `control_actions`. It appears on one day, 15 July 2026: the file gives it in all 24 hours, with an Output (0 in each) in hours 10 to 24 and none in hours 1 to 9 (OutputQuality -1), so the table holds 15 rows, all 0. Session 2224's report (line 12) says "24 hours, every value given 0": the file gives the line in 24 hours, but a value in only 15 of them.

## Reading the source

- The run stops at once, asking nothing, while `ieso_genfuel` or the host reports-public.ieso.ca is paused (`paused_sources.csv`).
- `--years` defaults to 2020 to the current year; one file a year. The current year's file is fetched fresh unless `--offline`; an earlier year's is reused from the raw files when saved, else fetched. `--offline` never asks; a file not saved stops the run.
- Each request: timeout 180 seconds, 2 seconds' pause after it. HTTP 404 stops the run without a retry; any other failure is tried up to `RETRIES` (4) times, 5, 10 and 15 seconds apart, then stops the run.
- A document whose root is not the IESO's Document of docID GenOutputbyFuelHourly, a DeliveryYear not the file's year, a day of another year, an hour outside 1 to 24, a fuel not one of the eight (`FUELS`: NUCLEAR, GAS, HYDRO, WIND, SOLAR, BIOFUEL, OTHER, CONTROL ACTIONS), a fuel given twice in an hour, an Output that is not a number, a file with no hour, or an hour and fuel given twice across the files stops the run; no file is written.
- A fuel without an Output has no row. Nothing is filled.
- The code counts no row ceiling and no request ceiling beyond one request a year's file.

## License

Public. `license_verdicts.csv` records the IESO, read 225: "may be public", for public and for commercial use. The sentence: "Subject to these Terms of Use and provided that the following is included on all reproductions, [the IESO's copyright notice], you are granted a limited, non-exclusive, non-sublicensable, non-transferrable licence to use and reproduce the Content." The table's header carries the notice: "Copyright (c) 2004-2022 Independent Electricity System Operator, all rights reserved. This information is subject to the Terms of Use set out in the IESO's website (www.ieso.ca)." (the header writes the copyright sign). `sources.csv` flags `ieso:gen_output_by_fuel_hourly` public; `license_tables.csv` lists the table under the IESO.

## Cross-checks (session 2233)

- The written table and session 2224's trial copy (`runs/c099/s2224/trial/`) hold the same 371,781 keys with every column equal, so the session's cross-checks (`runs/c099/s2224/cross.out`) hold for the written rows:
  - every one of the 59,688 hours from 2020-01-01T05:00:00Z is held for the six fuels;
  - in the 15,839 hours shared with `ieso_ontario_demand_hourly`, the hour's generation (the fuels summed) is a median 0.991 of market demand (Ontario demand plus exports), 0.938 to 1.007 from the 5th to the 95th percentile, and a median 1.133 of Ontario demand;
  - nuclear's share falls from 59.6 percent (2020) to 46.5 (2026) while gas's rises from 6.8 to 22.5; hydro 22.3 to 25.6, wind 7.6 to 9.5, solar 0.4 to 0.5.
- The counts and sums above were computed from the rows, read past the header lines, and agree with the header's line of counts.
- The CONTROL ACTIONS hours were counted in the saved 2026 file: 24 entries, 15 with an Output.
- Not run: the chain file's check against `nrc_power_reactors`, which lists U.S. reactors only.

## What it does not hold

- The years 2015 to 2019, though the IESO's listing holds files from 2015.
- Each generator's output: only the IESO's fuel totals are written.
- Imports, exports, demand and prices (demand is in `ieso_ontario_demand_hourly`).
- The meaning of the quality codes.
- OTHER before 2 April 2025, where the files give no such line.
