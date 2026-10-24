# Portugal's public net electricity production by type, load and cross-border trading, an hour, 1 January 2020 to 22 October 2026 (Energy-Charts.info, Fraunhofer ISE, API public_power)

Energy Research Warehouse (ERW), method note written in session 2289 (chain 104) for a table first written on 24 October 2026 (session 2282 of chain 104, its report `archive/sessions/SESSION_2282_REPORT.md`).

Tables: `energy_charts_portugal_power`

## Publisher and address

Energy-Charts.info, run by the Fraunhofer Institute for Solar Energy Systems ISE, its API's public net production for Portugal, one request a calendar year of Portuguese local days:

`https://api.energy-charts.info/public_power?country=pt&start=<year>-01-01&end=<year>-12-31` (2020 to 2025), and `...&start=2026-01-01&end=2026-10-22`.

Source id `energy_charts:public_power_pt`. The endpoint "Returns the public net electricity production in Megawatt (MW) for a given country for each production type", and "All timestamps returned by the API mark the beginning of the period the value refers to" (the API's description, read 471 in session 2281; `energy_charts_italy_power.md` quotes more of it). Each answer is JSON: `unix_seconds`, `production_types` (a name and a list of values, a null where there is none) and `deprecated` (false in all seven). The description names no upstream publisher; the table's load equals REN's consumption (below).

The table stands in for Japan's areas' demand, which session 2282 could not take: OCCTO's site has no robots file (read 472) but serves its area data through its interactive system; TEPCO's host answers HTTP 403 to its robots file (read 473); Kansai Transmission and Distribution's site terms (read 476) ask prior permission for reposting. Session 2282's probe (`runs/c104/s2282/probe.csv`) made 12 requests: those five (reads 472 to 476) and the seven years of Portugal (HTTP 200, 704,699 to 910,534 bytes, 05:08:12Z to 05:11:38Z, 34 or 35 seconds apart). All twelve are saved in `runs/license_reads/s2282/`; the seven answers were seeded into the raw store, and the trial and the write read them offline.

Connector: `warehouse/connectors/energy_charts_portugal.py` (session 2282), built as `energy_charts_italy.py`, with which it differs only in the country, names and docstring: `[--first 2020] [--last 2026] [--end 2026-10-22] [--offline] [--out-dir DIR]`, one request a year, 31 seconds between them; every type in snake case but the three the API derives (residual load, the renewable shares); the same stops (fields missing, uneven intervals, a value not a number, an interval twice). **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. `warehouse/supabase/live_set.yaml` lists it under `catalogue_hold`.

## Vintage and revision

One write, run `20261024T051350Z` ("This run wrote 725799 rows: 725799 new, 0 replacing earlier rows ...; 0 rows are kept from earlier runs"), from the seven saved answers. `retrieved_at` is each answer's download time (2020 at 2026-10-24T05:08:12Z, 2021 05:08:46Z, 2022 05:09:20Z, 2023 05:09:55Z, 2024 05:10:29Z, 2025 05:11:03Z, 2026 05:11:38Z), as header line 4 lists them; `vintage` is blank in every row.

The API marks no value as provisional or final; whether Energy-Charts revises a figure after it is first served, the answers do not say. A later run merges by (entity, variable, ts_utc): a changed value replaces the old one, but an interval the API later gives as null writes no row, so the earlier value would be kept.

## Shape and variables

Series, 725,799 rows, one entity `energy_charts:PT`, `node` Portugal, `geo` PT, `unit` MW, `freq` PT1H throughout (every answer, 2026 included, is hourly), `market` blank. 59,687 hours from 2020-01-01T00:00:00Z to 2026-10-22T22:00:00Z. Thirteen variables, twelve of the API's types and load:

| Variable | Rows | First ts_utc | Last ts_utc | Mean | Lowest | Highest | Zeros |
|---|---|---|---|---|---|---|---|
| load | 59,687 | 2020-01-01T00:00Z | 2026-10-22T22:00Z | 5,818.6 | 90.3 (2025-04-28T12:00Z) | 10,176.6 (2026-01-20T19:00Z) | 0 |
| wind_onshore | 59,687 | 2020-01-01T00:00Z | 2026-10-22T22:00Z | 1,473.4 | 0 | 5,062.4 (2025-03-19T10:00Z) | 7 |
| fossil_gas | 59,687 | 2020-01-01T00:00Z | 2026-10-22T22:00Z | 1,275.4 | 14.5 (2025-04-28T12:00Z) | 4,353.3 (2021-01-05T21:00Z) | 0 |
| cross_border_electricity_trading | 59,687 | 2020-01-01T00:00Z | 2026-10-22T22:00Z | 939.4 | -4,410.0 (2025-01-29T06:00Z) | 5,570.9 (2026-09-04T08:00Z) | 147 |
| hydro_run_of_river | 59,687 | 2020-01-01T00:00Z | 2026-10-22T22:00Z | 805.0 | 0 | 2,718.1 (2021-02-25T21:00Z) | 6 |
| hydro_pumped_storage | 59,687 | 2020-01-01T00:00Z | 2026-10-22T22:00Z | 567.3 | 0 | 3,344.4 (2025-05-29T20:00Z) | 11,025 |
| solar | 59,687 | 2020-01-01T00:00Z | 2026-10-22T22:00Z | 436.3 | 0 | 3,814.8 (2026-08-10T12:00Z) | 16,250 |
| biomass | 59,687 | 2020-01-01T00:00Z | 2026-10-22T22:00Z | 351.4 | 74.7 (2025-04-28T12:00Z) | 452.5 (2022-03-04T19:00Z) | 0 |
| hydro_water_reservoir | 59,687 | 2020-01-01T00:00Z | 2026-10-22T22:00Z | 332.7 | 0 | 1,727.9 (2025-03-12T20:00Z) | 62 |
| fossil_hard_coal | 16,080 | 2020-01-01T00:00Z | 2021-11-30T23:00Z | 183.6 | 0 | 1,757.5 (2020-09-01T19:00Z) | 10,022 |
| others | 59,687 | 2020-01-01T00:00Z | 2026-10-22T22:00Z | 25.3 | 0.8 (2025-11-19T07:00Z) | 39.0 (2020-12-30T23:00Z) | 0 |
| wind_offshore | 53,162 | 2020-05-31T22:00Z | 2026-10-22T22:00Z | 8.8 | 0 | 25.0 (2020-08-01T14:00Z) | 9,936 |
| hydro_pumped_storage_consumption | 59,687 | 2020-01-01T00:00Z | 2026-10-22T22:00Z | -431.2 | -3,055.1 (2026-08-23T12:00Z) | 0 | 11 |

MW; means rounded to one decimal; where a lowest or highest value recurs, its first hour is given. Values carry one decimal (most of them a fraction of a MW); the 11 zeros of the pumping are written `-0.0`.

- **Signs.** The pumping is 0 or negative in every row; the trading is positive (a net import) in 42,548 hours, negative in 16,992 and 0 in 147. Every other type is 0 or positive.
- **The types change.** The answers hold 16 types (with the three derived) in 2020 and 2021 and 15 from 2022: hard coal's last row is 2021-11-30T23:00:00Z. Hard coal has no row in April 2020 but one hour (719 null) and none in December 2021 (744 null); wind offshore none from January to April 2021 (2,879 null hours) and none before 2020-05-31T22:00:00Z (3,646 null hours in 2020).
- **28 April 2025.** Load falls from 5,813.5 MW at 09:00Z to 3,299.5 at 10:00Z and 92.4 at 11:00Z, is 90.3 at 12:00Z (its lowest), and is back above 4,000 MW only at 21:00Z; the lowest biomass, gas, run-of-river and onshore wind are in the same hours.
- A UTC year's energy (MW times one hour, TWh), 2020 and 2025: load 48.809 and 53.036; fossil gas 16.608 and 7.721; wind onshore 12.023 and 13.417; run-of-river 7.541 and 8.839; pumped storage 3.350 and 6.329; solar 1.266 and 6.104; trading 1.396 and 9.544; pumping -2.037 and -5.179.

**Against REN's yearly balance** (`ren_portugal_balance_annual`, internal; session 2289, `runs/c104/s2289/pt_ren.py` and `pt_ren2.py`). A Lisbon year and a UTC year begin at the same instant, so the sums compare directly. Load against REN's consumption differs by -3.6, -0.3, -23.8, 0.1, -0.4 and 0.1 GWh (2020 to 2025). Solar is within 0.5 GWh in 2021 to 2025 (-3.7 in 2020), wind onshore plus offshore within 0.5 GWh but 2022 (-23.7), biomass within 1.3 GWh from 2022 (15.6 in 2020, -13.6 in 2021). The hydro split is not REN's: run-of-river plus reservoir is 0.9 to 2.5 TWh below REN's hydro (which REN defines as natural inflow), and pumped storage 1.0 to 2.6 TWh above REN's pumped-storage production, while the three together are within 52 to 64 GWh of REN's two. Gas is 29 to 61 GWh above REN's natural gas, the pumping 49 to 60 GWh above REN's, and the trading -333 to +462 GWh from REN's net imports.

## Placing values in time, and what is filled

`ts_utc` is the hour's start in UTC, from the answer's `unix_seconds`; the API says its timestamps mark the beginning of the period. Each year was asked as Portuguese local days; in winter Portuguese time is UTC, so each year's first hour is 00:00Z on 1 January. The span is complete: 59,687 hours (2020 and 2024 of 8,784, 2021 to 2023 and 2025 of 8,760, 2026 of 7,079 to 22 October), evenly spaced in each answer, so the changes of hour leave no gap in UTC. A null has no row; nothing is filled. Whether a value is a mean over the hour or a reading at its start, the description does not say.

## License

Header: "License: public, CC BY 4.0 (the API's description). Source: Energy-Charts.info. The values are reshaped from wide to long; none is changed." `docs/licenses.md` and `warehouse/metadata/license_verdicts.csv`: read 442 (the API's description, read by chain 102's session 2253, the verdict recorded in session 2257; session 2281's read of the same page is read 471), "Unless stated otherwise, the data provided by the Energy-Charts API is licensed under the CC BY 4.0 license. Proper attribution to Energy-Charts.info as the source is required.", verdict "may be public", if the ERW sells anything "may be public". The table's row: flag public, "agrees", ERW verdict public. The figures are REN's in load (above), and REN's own pages state no terms (`ren_portugal_balance_annual` is internal); session 2282's report puts to Samuel whether Energy-Charts' statement or the operator's governs.

## Checks (session 2289)

The figures in this note were computed from the rows of `warehouse/output/energy_charts_portugal_power.csv`, read past its 10 header lines (counted), and from the saved answers, read only (scripts `runs/c104/s2289/ec.py`, `ec_gaps.py`, `pt_ren.py` and `pt_ren2.py`, outputs `ec_portugal.out`, `ec_portugal_gaps.out`, `pt_ren.out` and `pt_ren2.out` beside them).

- 725,799 rows, 13 variables, `ts_utc` from 2020-01-01T00:00:00Z to 2026-10-22T22:00:00Z, PT1H 59,687 intervals as header line 3 states; one entity; no (entity, variable, ts_utc) twice; no blank value; unit MW, freq PT1H and geo PT throughout.
- **Against the answers:** the seven answers hold 725,799 values that are not null, outside the three derived types, and each type's values in each answer equal the table's rows (0 types differ).
- **The trial against the table:** `runs/c104/s2282/trial/energy_charts_portugal_power.csv` (run `20261024T051253Z`) has the same rows past its header, byte for byte; the headers differ only in the run's name and log.
- Session 2282's cross-check (`runs/c104/s2282/cross.py`; its docstring says "Ember's Italian demand", its code reads Portugal's), run again from the main checkout with the written table as argument 1 (output `runs/c104/s2289/portugal_cross.out`): identical to the saved `cross.out`, which was run on the trial. Load against Ember's Portuguese demand: 0.924 (2020), 0.917, 0.905, 0.899, 0.890 and 0.877 (2025); production, storage and trading less load over 59,687 hours: median 6 MW, 5th percentile -406, 95th 469, a median 0.11 percent of load; solar 1.3 TWh in 2020 to 6.1 in 2025; load against REN's consumption 48.809 against 48.813 TWh (2020), 49.470 and 49.470, 50.308 and 50.332, 50.703 and 50.703, 51.407 and 51.407, 53.036 and 53.036.

## Where the description and the data disagree

1. **Load equals REN's consumption to the GWh in four years, not five.** The report says "to the GWh in five of six years, and within 0.05% in the other (2022 ...)". 2020 differs too: 48,809.4 against 48,813 GWh, 3.6 GWh apart; 2022 is 23.8 GWh apart. The cross-check rounds to three decimals of a TWh, which shows 2020's gap (48.809 against 48.813).
2. **Energy-Charts' types are not all REN's.** The report concludes "Energy-Charts republishes REN's figures". Load, solar and wind agree with REN's within a GWh in most years; the hydro does not: Energy-Charts' pumped storage exceeds REN's pumped-storage production by 1.0 to 2.6 TWh a year and its run-of-river and reservoir fall short of REN's natural-inflow hydro by as much, and gas, pumping and trading differ by tens to hundreds of GWh. A reader should not take `hydro_pumped_storage` for REN's pumped-storage production.
3. **The year requests were not 31 seconds apart.** The connector waits 31 seconds; the probe's times give 34 and 35 seconds.
4. **The reads' numbers in the report's file list.** The report's text gives reads 472 to 476 and the CC BY verdict as read 471; its file list says "`warehouse/metadata/license_reads.csv` (441 to 445)". Since the merge of chain 102 (commit ef284545) these reads are 472 to 476, and the verdict row in force is read 442.

Compared besides, with no contradiction found: the header's and docstring's counts, span, frequency (header: "each file's own interval"; every answer hourly), entity, unit, variables, the derived series left out, the signs and "nothing is filled" against the rows and the answers.

Not acted on: this note changes no file but itself.

Recorded, not changed in session 2289: Energy-Charts splits hydro differently from REN; its load, solar and wind equal REN's. Session 2289's report corrects session 2282's "five of six years" (four), its 31 seconds and its read numbers.

## The session report against the table

Every figure of `SESSION_2282_REPORT.md` checked against the table, the saved answers and the rerun cross-check holds (2020 to 22 October 2026, 725,799 rows, hourly, MW, 2022's 50.308 against 50.332 TWh, the same 0.877 to 0.924 of Ember's demand as REN's, a median 6 MW or 0.11 percent of load, solar 1.3 TWh in 2020 and 6.1 in 2025, 12 requests of 15, reads 472 to 476 as numbered now), except:

- "Energy-Charts' Portuguese load equals REN's consumption ... to the GWh in five of six years": four (disagreement 1).
- "So Energy-Charts republishes REN's figures": for load, solar and wind, not for the hydro split (disagreement 2).
- "31 seconds apart": 34 or 35 seconds (disagreement 3).
- Files: "`license_reads.csv` (441 to 445)": renumbered 472 to 476 at the merge (disagreement 4).

## What it does not hold

- The API's derived series (residual load, the renewable shares), prices, installed power and forecasts; the Azores and Madeira (the load is REN's mainland consumption); REN's own monthly figures; anything before 2020 or after 22 October 2026; and the hours and types the answers give as null.
