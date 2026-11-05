# Hungary's, Romania's, Greece's and Bulgaria's public net electricity production by type, load, residual load and cross-border trading, a UTC day, 1 January 2020 to 22 October 2026 (Energy-Charts.info, Fraunhofer ISE, API public_power)

Energy Research Warehouse (ERW), method note written in session 2261 (chain 102) for a table first written on 24 October 2026 (session 2259).

Tables: `energy_charts_southeast_europe_daily`

## Publisher and address

Energy-Charts.info, run by the Fraunhofer Institute for Solar Energy Systems ISE (`https://energy-charts.info/charts/power/chart.htm?l=en`), its API's public net production, one request a country from 2020 to the last day asked (`--last-day`, yesterday in UTC by default; 2026-10-23 in this run):

`https://api.energy-charts.info/public_power?country=<hu|ro|gr|bg>&start=2020-01-01&end=<last day>`

The User-Agent is "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)". Source id `energy_charts:public_power_southeast`. Connector: `warehouse/connectors/energy_charts_southeast.py` (session 2259), its only table. api.energy-charts.info has no robots file (HTTP 404, read 441); its OpenAPI description (read 442) states the license and allows 2 requests a minute for each client. Energy-Charts compiles the countries' figures from the operators' publications.

The table is not scheduled: no line of `warehouse/run_daily.sh`, the other `warehouse/*.sh` scripts, `scripts/` or `.github/workflows/` names the connector (searched in session 2261), and `run_status.csv` holds no row for it. It was written once, by run `20261024T043206Z` on the data machine, offline from the session's probe copies.

## Vintage and revision

UTC days from 1 January 2020 to 22 October 2026 (`ts_utc`), 2,487 days. The four answers were retrieved by session 2259's probe at 2026-10-24T04:22:15Z (Hungary), 04:25:34Z (Romania), 04:26:16Z (Greece) and 04:26:54Z (Bulgaria); each row's `retrieved_at` is its country's time as the probe's manifest records it. `vintage` is empty: the API sends no Last-Modified. `coverage.csv` gives the same 128,530 rows, 58 nodes and the same first and last `ts_utc`.

The API's days are the countries' local days, so its first and last UTC days are cut short (Hungary's answer runs from 23:00 UTC on 31 December 2019 to 21:45 UTC on 23 October 2026); those part days are not summed. Each run writes the whole table again (`ip.write_snapshot`), and every country is asked again unless `--offline`.

## Shape and variables

Series, 128,530 rows, 58 entities, 4 variables, 58 series.

- `entity` `energy_charts:<country>:<type>`, Energy-Charts' name as a slug; `variable` `public_net_energy` for a production type, and `load`, `residual_load` or `cross_border_trading` for the other three; `unit` MWh; `freq` P1D; `ts_utc` the UTC day's start; `geo` HU, RO, GR or BG; `market` empty; `node` "<geo>: <name>"; `x_type` Energy-Charts' name; `x_periods` the number of periods summed.
- The value is the day's sum of Energy-Charts' mean power over each period times the period's length. Hungary is in quarter hours throughout (`x_periods` 96), Greece and Bulgaria in hours (24), and Romania in hours in 2020 and 2021 and in quarter hours from 1 January 2022; Romania's 31 December 2021 is summed over 30 periods (22 hours and 8 quarter hours), in its 12 series. Rows by `x_periods`: 24 in 65,574, 96 in 62,944, 30 in 12.

| Country | Rows | Series | Types (beside load, residual load and cross-border trading) |
|---|---|---|---|
| HU | 41,511 | 17 | nuclear, fossil_gas, fossil_brown_coal_lignite, fossil_hard_coal (14 September 2020 to 30 March 2026), fossil_oil, solar, wind_onshore, biomass, waste, geothermal (from 14 September 2020), hydro_run_of_river, hydro_water_reservoir, other_renewables, others |
| BG | 34,473 | 16 | nuclear, fossil_brown_coal_lignite, fossil_gas, fossil_hard_coal, solar, wind_onshore, hydro_run_of_river, hydro_water_reservoir, hydro_pumped_storage, biomass, waste, battery and battery_consumption (from 10 September 2026) |
| RO | 29,842 | 13 | nuclear, fossil_brown_coal_lignite, fossil_gas, fossil_hard_coal, hydro_run_of_river, hydro_water_reservoir, wind_onshore, solar, biomass, battery (from 2 February 2025) |
| GR | 22,704 | 12 | fossil_gas, fossil_brown_coal_lignite, solar, wind_onshore, hydro_water_reservoir, hydro_pumped_storage, hydro_pumped_storage_consumption (from 1 June 2026), battery and battery_consumption (from 17 June 2026) |

Every series runs to 22 October 2026 except Hungary's hard coal. The consumption series are negative, as given. No series is all zero or constant, and no (entity, variable, ts_utc) is given twice.

Load has a row on every day for Bulgaria; Hungary misses 1 day (20 June 2023), Greece 2 (27 October 2024 and 29 March 2026), and Romania 48 (33 of them in 2021, 3 in 2022, 8 in 2023, 1 in 2024 and 3 in 2026). A day with a blank period has no row.

Of the 4,667 zero days, the most are Hungary's oil (1,548), Romania's hard coal (1,163), Bulgaria's pumped storage (994), Hungary's hard coal (380) and geothermal (319), Greece's lignite (176) and Romania's nuclear (53, all in 2026). Romania's nuclear zeros are output, not placeholders: Energy-Charts gives 197.4 GWh for May 2026 and Eurostat 196.0 (`eurostat_electricity_monthly`, `net_production:N9000`).

How the series add up, from the rows: residual_load is load less solar and onshore wind, within 1 MWh on every day for Hungary, Romania and Greece and on all but 5 of Bulgaria's 2,485 (by 1.0 to 1.1 MWh). Load is close to the sum of the production types plus cross-border trading (a median difference of -0.44 percent of load for Hungary, 0.75 for Romania, 1.73 for Greece and 0.64 for Bulgaria), so a positive trading figure is an import. One day recomputed from the raw answer (Hungary's load, 1 June 2024: 96 quarter hours, their sum times 0.25) gives 97,439.35 MWh, the table's figure.

The counts were computed in session 2261 from the rows, read past the 10 header lines with pandas (every column as text).

Not summed, as the header counts them (a type's day each): part days, Hungary 34, Bulgaria 32, Romania 26 and Greece 24 (each type's first and last UTC day); days with a blank, Bulgaria 5,319, Greece 7,140, Romania 2,489 and Hungary 768 (most of them days before a series begins or after it ends: the batteries, Greece's pumped storage consumption, Hungary's hard coal and geothermal). Energy-Charts' two renewable shares are not taken.

## Checks the connector makes

- Before any request, the connector and api.energy-charts.info are checked against `warehouse/metadata/paused_sources.csv`; a paused publisher stops the run with no request. It is not paused.
- Every step between the answer's periods must be 15 or 60 minutes, or the run stops; so does a type not in the map, a series not as long as the periods, or a day given twice in the table.
- A day is summed for a type only when its periods cover the whole day (86,400 seconds) and none is blank; any other day has no row for that type and is counted. The last period's length is taken as the step before it. Nothing is filled.
- Ceiling: four requests, 35 seconds apart, timeout 300 seconds; each asked again unless `--offline`.

## The cross-check

Session 2259 summed the days to months and years in `runs/c102/s2259/cross.py` (on the data machine, not in git), reading the trial copy of the table (the same rows as the table), beside Eurostat's monthly figures (`eurostat_electricity_monthly`, months of 28 days or more of load) and Ember's yearly demand (`owid_ember_electricity_annual`, years of 365 days or more of load):

| Country | Months | Load to supply for the internal market (`flow:AIM`) | Wind (`RA300`) | Solar (`RA400`) | Nuclear (`N9000`) |
|---|---|---|---|---|---|
| Bulgaria | 80 | 1.180 | 0.981 | 0.972 | 1.050 |
| Greece | 80 | 0.970 | 0.876 | 0.987 | none |
| Hungary | 80 | 1.009 | 1.000 | 0.657 | 0.998 |
| Romania | 73 | 1.079 | 0.997 | 0.754 | 1.086 |

Each cell is the median of the monthly ratios. Hungary's and Romania's solar is well under Eurostat's; session 2259 took Energy-Charts' solar there to be what the grid operators see, without the rooftops Eurostat counts.

Load against Ember's demand: Bulgaria 0.981 to 1.037 (2020 to 2025), Romania 0.972 to 1.001 (2020, 2024 and 2025), Greece 0.867 to 0.903 (2020 to 2025) and Hungary 0.884 to 0.921 (2020 to 2022, 2024 and 2025). Romania's 2021 to 2023 and Hungary's 2023 drop out for their missing load days. In 2025: Bulgaria 37.881 against 36.53 TWh, Greece 50.167 against 55.56, Hungary 43.210 against 48.90, Romania 53.560 against 54.39.

## License

The header: "License: public (CC BY 4.0, attribution to Energy-Charts.info, the API's description; see license_verdicts.csv). Source: Energy-Charts.info." `license_verdicts.csv` gives Energy-Charts.info (Fraunhofer ISE) "may be public", the same if the ERW sells anything (read 442, recorded in session 2257): "Unless stated otherwise, the data provided by the Energy-Charts API is licensed under the CC BY 4.0 license. Proper attribution to Energy-Charts.info as the source is required." `docs/licenses.md` and `coverage.csv`: public.

## Found while writing this note

- Session 2259's report says Energy-Charts gives "Romania in quarter hours then hours". The rows show the other order: hours in 2020 and 2021, quarter hours from 1 January 2022 (the docstring says only "quarter hours and hours").
- Session 2259's report gives load against Ember's demand as "0.98 to 1.04 for Bulgaria and Romania". Its cross-check gives Romania 0.972 in 2024, so the range is 0.97 to 1.04.
- The docstring and the header give no sign for cross-border trading. The balance above shows a positive figure is an import.
- Greece's pumped storage consumption begins on 1 June 2026, while its pumped storage production runs from 2020: before June 2026 the table holds the plants' output and none of their pumping.
- Greece's two missing load days, 27 October 2024 and 29 March 2026, are the days its clocks changed.

Acted on in session 2261: the docstring now gives Romania's periods (hours to 2021, quarter hours from 2022) and the sign of cross-border trading; session 2259's report is corrected. The table is unchanged.

## What it does not hold

- The quarter hours and hours as published: only complete UTC days, summed.
- The first and last UTC days of each answer, cut by the countries' local days, and any day with a blank period.
- Energy-Charts' renewable shares, prices, and the cross-border flows by neighbour.
- Other countries of the region (Austria, Switzerland and Czechia were left to chain 103), and days before 2020.
