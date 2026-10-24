# Austria's, Switzerland's and Czechia's public net production and load, an hour (Energy-Charts)

Energy Research Warehouse (ERW), method note written in session 2275 (chain 103) for a table first written on 24 October 2026 (session 2272).

Tables: `energy_charts_central_europe`

## Publisher and address

Energy-Charts.info (Fraunhofer Institute for Solar Energy Systems ISE), public net electricity production (`https://energy-charts.info/charts/power/chart.htm?l=en`). It is read through the Energy-Charts API (no key), one request a country and calendar year:

    https://api.energy-charts.info/public_power?country=<at|ch|cz>&start=<year>-01-01&end=<year>-12-31

The current year is asked to the last day ended at the run, in Central European time (`--last-day` sets it). Source id `energy_charts:public_power_at_ch_cz`. Connector: `warehouse/connectors/energy_charts_central.py` (session 2272), in the form of chain 102's `energy_charts_belgium.py`. api.energy-charts.info has no robots file (HTTP 404, read 446). The API's description (`https://api.energy-charts.info/openapi.json`, read 447) states the license and a rate limit of 2 requests a minute for each client.

Energy-Charts compiles the countries' figures from the operators' publications. The operators were not asked: APG's transparency platform did not answer (chain 102), and Swissgrid's legal information forbids public or commercial use without consent (session 2272).

## Vintage and revision

31 December 2022 23:00 UTC (the first hour of 1 January 2023 in Central European time) to 23 October 2026 21:00 UTC. Written by run `20261024T042003Z`, which read the twelve saved answers. Those answers were retrieved from 2026-10-24T04:07:03Z to 04:14:11Z (`retrieved_at` in every row; the header lists each). `vintage` is blank: the answers carry no date of their own. In the header's list of requests, "at 2023" is Austria's 2023 answer, not a time.

Every run that is not `--offline` asks for every country and year again, 35 seconds apart, and writes the table again (`write_snapshot`), so Energy-Charts' revisions replace the rows held.

## Shape and variables

Series, 1,419,805 rows, 43 series: Austria 467,698 rows (14 series), Switzerland 334,070 (10), Czechia 618,037 (19).

- `entity`: `energy_charts:<at|ch|cz>:<type as a slug>`.
- `variable`: `public_net_power` for a production type; `load`, `residual_load` or `cross_border_trading` for Energy-Charts' "Load", "Residual load" and "Cross border electricity trading".
- `unit` MW, `freq` PT1H, `ts_utc` the hour's start (Energy-Charts' timestamps mark a period's beginning), `geo` AT, CH or CZ, `market` blank.
- `node`: the country and Energy-Charts' name ("Austria: Solar").
- `x_type`: Energy-Charts' name. `x_resolution`: the spacing of the answer the hour came from, PT1H or PT15M.

The production types, as Energy-Charts names them:

| Country | Types |
|---|---|
| AT | Biomass; Fossil gas; Geothermal; Hydro Run-of-River; Hydro pumped storage; Hydro pumped storage consumption; Hydro water reservoir; Others; Solar; Waste; Wind onshore |
| CH | Hydro Run-of-River; Hydro pumped storage; Hydro water reservoir; Nuclear; Others; Solar; Wind onshore |
| CZ | Biomass; Fossil brown coal / lignite; Fossil coal-derived gas; Fossil gas; Fossil hard coal; Fossil oil; Hydro Run-of-River; Hydro pumped storage; Hydro pumped storage consumption; Hydro water reservoir; Nuclear; Other renewables; Others; Solar; Waste; Wind onshore |

"Hydro pumped storage consumption" is negative, as Energy-Charts gives it: the power the pumps draw. Cross-border trading is negative in hours of net export. Austria's residual load is negative in 97 hours. Czechia's coal-derived gas ends on 30 April 2025 (21:00 UTC); every other series runs to the last hour.

## The hour

Austria's answers are spaced every quarter hour. Switzerland's are hourly. Czechia's are hourly for 2023 and 2024 and quarter-hourly from 2025. A quarter-hour answer's four values are averaged to the hour (rounded to three decimals), and an hour is written only when all four are given. An hourly answer's value is kept as given. At full resolution the table would hold 3,685,971 rows and about 1 GB (session 2272's first trial). The largest table held then, `ercot_sced_esr_hourly`, was 553 MB.

An hour with a blank figure, or with a quarter missing, has no row and is counted in the header. Most are Czechia's: coal-derived gas 8,113 hours, hard coal 745, oil 722, and one hour in each of the other Czech series. Energy-Charts' renewable shares (496,062 figures) are not taken. Nothing is filled.

## Reading the source

- The run stops at once, asking nothing, while `energy_charts_central` or the host api.energy-charts.info is paused.
- Twelve requests a run in 2026 (three countries, 2023 to 2026), each fetched fresh, timeout 180 seconds, 35 seconds' pause after it. HTTP 404 stops the run; any other failure is tried up to `RETRIES` (4) times (`iso_prices.fetch_raw`). `--offline` reads the saved answers and stops if one is missing.
- The run stops, and no file is written, for any of these:
  - an answer without timestamps or production types;
  - a year's timestamps not evenly spaced at an hour or a quarter hour;
  - a type's series not as long as the timestamps;
  - an hour given twice for a series.

## License

Internal, until the verdict reaches this branch. The API's description reads: "Unless stated otherwise, the data provided by the Energy-Charts API is licensed under the CC BY 4.0 license", with attribution to Energy-Charts.info. Chain 102's session 2257 recorded the verdict for Energy-Charts.info (Fraunhofer ISE), may be public, on its branch. This chain wrote no second row (session 2271). `sources.csv` flags the source `internal` until that verdict is on main.

## Cross-checks (session 2272)

Production types are summed without pumped storage's consumption. MW hourly means summed over a year give MWh.

- Every year 2023 to 2025 has all its hours (8,760 or 8,784) in each country.
- Against `eurostat_electricity_monthly`'s net production TOTAL, full years 2023 to 2025:
  - Czechia: 1.008, 0.997 and 1.003. Czech nuclear is 28.72, 28.04 and 30.29 TWh against Eurostat's 28.73, 28.05 and 30.32; Czech wind in 2024 is 0.70 against 0.70.
  - Austria: 0.857, 0.864 and 0.797. Energy-Charts' figures are public net production; Eurostat's total is all net production. Austrian wind in 2024 is 9.37 TWh against Eurostat's 9.13.
- Switzerland has no total in Eurostat's table. Load against `owid_ember_electricity_annual`'s demand, 2023 to 2025: Switzerland 1.037 to 1.042, Austria 0.781 to 0.821, Czechia 0.914 to 0.921. So `load` is not the same quantity as Ember's demand.

## What it does not hold

- Hours before 2023; the quarter hours themselves; prices; installed capacity.
- Other countries. Chain 102 holds Belgium (`energy_charts_belgium_hourly`) and is writing Hungary, Romania, Greece and Bulgaria. Chain 099 holds Germany from SMARD (`smard_germany_monthly`).
