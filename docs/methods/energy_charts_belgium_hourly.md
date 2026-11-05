# Belgium's public net electricity production by type, load, residual load and cross-border trading, an hour, 1 January 2020 to 23 October 2026 (Energy-Charts.info, Fraunhofer ISE, API public_power)

Energy Research Warehouse (ERW), method note written in session 2261 (chain 102) for a table first written on 24 October 2026 (session 2253).

Tables: `energy_charts_belgium_hourly`

## Publisher and address

Energy-Charts.info, run by the Fraunhofer Institute for Solar Energy Systems ISE, its API's public net production for Belgium (chart page `https://energy-charts.info/charts/power/chart.htm?l=en&c=BE`), one request a calendar year of Belgian local days, from 2020:

`https://api.energy-charts.info/public_power?country=be&start=<year>-01-01&end=<year>-12-31`

The current year is asked to the last Belgian day ended at the run (`--last-day`, yesterday in Brussels by default): `end=2026-10-23` in this run. The User-Agent is "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)". Source id `energy_charts:public_power_be`. Connector: `warehouse/connectors/energy_charts_belgium.py` (session 2253), its only table. api.energy-charts.info has no robots file (HTTP 404, read 441); its OpenAPI description (read 442) states the license and allows 2 requests a minute for each client. Energy-Charts compiles Belgium's figures from the operators' publications.

Energy-Charts is the source in place of Elia, Belgium's operator: opendata.elia.be's robots file (read 437) disallows `/api/` and its download paths to every reader but Google. Austria's APG, tried next, was closed too (reads 438 to 440).

The table is not scheduled: no line of `warehouse/run_daily.sh`, the other `warehouse/*.sh` scripts, `scripts/` or `.github/workflows/` names the connector (searched in session 2261), and `run_status.csv` holds no row for it. It was written by run `20261024T035118Z` (session 2253) and again by run `20261024T041237Z` (session 2257, the same rows, the license made public), both offline from the session's probe copies.

## Vintage and revision

Belgian days from 1 January 2020 to 23 October 2026: `ts_utc` from 23:00 UTC on 31 December 2019 to 21:00 UTC on 23 October 2026. The seven yearly answers were retrieved by session 2253's probe from 2026-10-24T03:46:02Z (2025, asked first) to 03:49:24Z (2026); each row's `retrieved_at` is its year's time as the probe's manifest records it. `vintage` is empty: the API sends no Last-Modified. `coverage.csv` gives the same 908,600 rows, 16 nodes and the same first and last `ts_utc`.

Each run writes the whole table again (`ip.write_snapshot`), and every year is asked again unless `--offline`.

## Shape and variables

Series, 908,600 rows, 16 entities, 4 variables, 16 series. Every one of the 59,711 hours from the first to the last `ts_utc` is present for load; no (entity, variable, ts_utc) is given twice.

- `entity` `energy_charts:be:<type>`, Energy-Charts' name as a slug; `variable` `public_net_power` for the 13 production types, and `load`, `residual_load` or `cross_border_trading` for the other three; `unit` MW, the hour's mean power as Energy-Charts gives it; `freq` PT1H; `ts_utc` the hour's start; `geo` BE; `market` empty; `node` "Belgium: <name>"; `x_type` Energy-Charts' name.

| Entity | Rows | First | Zero | Negative | Mean MW |
|---|---|---|---|---|---|
| nuclear | 56,783 | 31 Dec 2019, 23:00 | 1,715 | 0 | 3,714.8 |
| fossil_gas | 59,711 | 31 Dec 2019, 23:00 | 0 | 0 | 2,246.9 |
| fossil_oil | 59,711 | 31 Dec 2019, 23:00 | 8,869 | 0 | 44.2 |
| solar | 59,711 | 31 Dec 2019, 23:00 | 27,026 | 0 | 867.7 |
| wind_offshore | 59,711 | 31 Dec 2019, 23:00 | 5,744 | 0 | 789.6 |
| wind_onshore | 59,711 | 31 Dec 2019, 23:00 | 0 | 0 | 576.2 |
| biomass | 59,711 | 31 Dec 2019, 23:00 | 0 | 0 | 301.5 |
| waste | 59,711 | 31 Dec 2019, 23:00 | 0 | 0 | 237.6 |
| hydro_run_of_river | 59,711 | 31 Dec 2019, 23:00 | 50 | 0 | 34.8 |
| hydro_pumped_storage | 59,711 | 31 Dec 2019, 23:00 | 32,651 | 0 | 119.9 |
| hydro_pumped_storage_consumption | 59,711 | 31 Dec 2019, 23:00 | 17,345 | 42,366 | -162.2 |
| battery | 15,863 | 31 Dec 2024, 23:00 | 380 | 0 | 65.5 |
| others | 59,711 | 31 Dec 2019, 23:00 | 1,431 | 0 | 178.6 |
| load | 59,711 | 31 Dec 2019, 23:00 | 0 | 0 | 9,286.5 |
| residual_load | 59,711 | 31 Dec 2019, 23:00 | 0 | 9 | 7,052.9 |
| cross_border_electricity_trading | 59,711 | 31 Dec 2019, 23:00 | 2 | 23,655 | 598.1 |

Every series runs to 21:00 UTC on 23 October 2026. Battery is in the answers from 2025 on. Pumped storage consumption is negative, as given. No series is all zero or constant.

Nuclear has no row for 2,928 hours, in two blocks: the Belgian months of May and June 2026, and of August and September 2026. All of its 1,715 zeros are in 2026: every hour from 02:00 UTC on 4 April to the end of the Belgian April (644), all but two of the 744 hours of the Belgian July (0.1 MW at 15:00 and 16:00 UTC on 24 July), and 329 of the 552 hours of the Belgian October to date. Eurostat agrees that Belgium's reactors stood: 65 GWh in April 2026 and 0 in May, June and July (`eurostat_electricity_monthly`, `net_production:N9000`), against Energy-Charts' 88.0 GWh for April. These zeros are output, not placeholders.

How the series add up, from the rows: residual_load is load less solar, offshore and onshore wind in every hour, within 0.5 MW. Load is close to the sum of the 13 production types plus cross-border trading (a median difference of -56 MW, from -679.5 to 276.8 MW at the 5th and 95th percentiles), so a positive trading figure is an import.

The counts were computed in session 2261 from the rows, read past the 10 header lines with pandas (every column as text).

Not taken, as the header counts them: 2,928 blank nuclear hours, and 119,422 figures of Energy-Charts' two renewable shares (of load and of generation, its own percentages).

## Checks the connector makes

- Before any request, the connector and api.energy-charts.info are checked against `warehouse/metadata/paused_sources.csv`; a paused publisher stops the run with no request. It is not paused.
- Each answer's hours must be an hour apart (3,600 seconds), and each type's series as long as the hours, or the run stops; so does a type not in the map, or an hour given twice in the table.
- A blank figure has no row and is counted. Nothing is filled.
- Ceiling: one request a year from 2020 (seven in 2026), 35 seconds apart, timeout 180 seconds; each asked again unless `--offline`.

## The cross-check

Session 2253 summed the hours to months and years (MW times 1 hour) in `runs/c102/s2253/cross.py` (on the data machine, not in git), reading the trial copy of the table (the same rows as the table), beside Eurostat's monthly figures for Belgium (`eurostat_electricity_monthly`) for 77 months from January 2020:

| Year | Load to supply for the internal market (`flow:AIM`) | Wind (`RA300`) | Solar (`RA400`) | Nuclear (`N9000`) |
|---|---|---|---|---|
| 2020 | 1.032 | 0.886 | 0.865 | 1.006 |
| 2021 | 1.033 | 0.935 | 0.827 | 1.001 |
| 2022 | 1.066 | 0.952 | 0.965 | 1.003 |
| 2023 | 1.079 | 0.970 | 0.992 | 1.001 |
| 2024 | 1.065 | 0.966 | 0.980 | 1.005 |
| 2025 | 1.054 | 0.951 | 0.980 | 1.008 |
| 2026 | 1.087 | 0.997 | 0.980 | 1.008 |
| All months, median | 1.059 | 0.949 | 0.980 | 1.004 |

Each cell is the median of the year's monthly ratios; wind is offshore plus onshore. The 77 months run from January 2020 to July 2026: May and June 2026 drop out (no nuclear figure to divide), and 2026's nuclear median takes in April (88.0 against 65.0 GWh, 1.35) and July (0.2 MWh against 0, no finite ratio).

Against Ember's yearly demand (`owid_ember_electricity_annual`, BEL), Energy-Charts' load is 92 to 94 percent: 81.20 against 87.96 TWh in 2020, 84.50 against 91.52 in 2021, 81.77 against 86.80 in 2022, 78.98 against 83.77 in 2023, 81.03 against 86.35 in 2024, and 80.23 against 86.56 in 2025.

## License

The header: "License: public (CC BY 4.0, attribution to Energy-Charts.info, the API's description; see license_verdicts.csv). Source: Energy-Charts.info." `license_verdicts.csv` gives Energy-Charts.info (Fraunhofer ISE) "may be public", the same if the ERW sells anything (read 442, recorded in session 2257): "Unless stated otherwise, the data provided by the Energy-Charts API is licensed under the CC BY 4.0 license. Proper attribution to Energy-Charts.info as the source is required." The table was internal until session 2257 recorded the verdict, then written again as public. `docs/licenses.md` and `coverage.csv`: public.

## Found while writing this note

- The docstring says a blank nuclear figure is counted "from its first gap", as if one gap ran to the end. The blanks are two blocks (Belgian May and June, and August and September 2026), and July's and October's hours are present, mostly zero. For the same idle fleet, Energy-Charts writes 0 in some months and leaves others blank.
- fossil_oil is zero in 8,677 of 2020's 8,784 hours (1.4 GWh for the year), then 223.5 to 585.6 GWh a year from 2021 to 2025. Eurostat's oil for Belgium (`net_production:O4000XBIO`) is 6.4 to 14.1 GWh a year over those years. Energy-Charts' oil is not Eurostat's, and its 2020 zeros may stand for a type not yet split out; they are kept as given.
- others moves in steps from year to year: a mean of 614.9 MW in 2020, 0.8 in 2021, 0.9 in 2022, 192.9 in 2023, 4.3 in 2024, 163.4 in 2025 and 293.7 in 2026 to date. That reads like a change in what Energy-Charts puts in the type, not in plant.
- The docstring and the header give no sign for cross-border trading. The balance above shows a positive figure is an import.

Acted on in session 2261: the docstring now names 2026's two blocks of blank nuclear hours and the sign of cross-border trading. The table is unchanged; oil's and Others' breaks between years are Energy-Charts' and are kept as given.

## What it does not hold

- Elia's own figures, which its robots file closes to the ERW's reader.
- Energy-Charts' renewable shares of load and of generation.
- Prices, and the cross-border flows by neighbour.
- Hours before 1 January 2020 (Belgian time), and the Belgian day in progress at the run.
