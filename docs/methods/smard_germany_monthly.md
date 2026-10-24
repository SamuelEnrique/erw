# Germany's generation by source and grid load, a month (the Bundesnetzagentur's SMARD market data)

Energy Research Warehouse (ERW), method note written in session 2233 (chain 099) for a table first written on 24 October 2026 (session 2230).

Tables: `smard_germany_monthly`

## Publisher and address

Bundesnetzagentur, SMARD (Strommarktdaten), market data. One POST to SMARD's download centre, the form behind its Data download page (`https://www.smard.de/en/downloadcenter/download-market-data`), at `https://www.smard.de/nip-download-manager/nip/download/market-data`, which answers a zip of two semicolon-separated CSV files: "Actual_generation_..._Month_1.csv" (Start date, End date, one column a source) and "Actual_consumption_..._Month_2.csv" (Start date, End date, grid load). Source id `smard:market_data_month`. Connector: `warehouse/connectors/smard_germany.py` (session 2230). www.smard.de has no robots file (HTTP 404, session 2230). SMARD's figures are the transmission system operators' as ENTSO-E receives them, verified by the Bundesnetzagentur (its data use page).

## Vintage and revision

January 2015 to September 2026, written by run `20261024T024634Z` (24 October 2026), which read the saved answer (its log). The answer was retrieved at 2026-10-24T02:45:34Z (`retrieved_at` in every row): a zip of 12,963 bytes whose files are named `Actual_generation_201501010000_202610240445_Month_1.csv` and `Actual_consumption_201501010000_202610240445_Month_2.csv`. `vintage` is blank in every row: SMARD's answer states none. The header's "Retrieved: 20261024T024634Z" is the write's run id; it also states the answer's time.

Every run that is not `--offline` asks for every month again, saves the answer over `warehouse/raw/smard_germany/market_data_month.zip` (with the query and time in its `.json`), and writes the table again (`write_snapshot`). The answer runs to the current month: October 2026's row was all "-" and has no row.

## Shape and variables

Series, 1,800 rows, 141 months. `entity` smard:de; `variable` generation_<source in snake case> or grid_load; `node` the column's name as SMARD writes it, its "[MWh] Calculated resolutions" dropped; `unit` MWh; `ts_utc` the month's first day at 00:00:00Z (SMARD's Start date, a month in German time, so the month begins an hour or two before `ts_utc`); `freq` P1M; `geo` DE; `market` blank; extra column `x_file`, the CSV file's name.

Eleven of the twelve sources and the grid load hold 141 months each; nuclear holds 108 (January 2015 to December 2023: 0 from May to December 2023, then "-" from January 2024, which has no row). 8 values are 0 (those nuclear months); none is negative. The saved answer holds 46 "-" cells: 33 nuclear months and October 2026's 13.

TWh a year (the months summed here for this note):

| `variable` | 2015 | 2018 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|
| generation_lignite | 133.8 | 128.3 | 77.8 | 71.0 | 67.2 |
| generation_hard_coal | 81.1 | 71.5 | 39.8 | 27.3 | 28.2 |
| generation_fossil_gas | 15.2 | 42.9 | 51.1 | 56.9 | 60.5 |
| generation_nuclear | 84.4 | 71.8 | 6.7 | 0.0 | 0.0 |
| generation_other_conventional | 10.4 | 15.7 | 16.4 | 15.8 | 14.4 |
| generation_hydro_pumped_storage | 8.2 | 8.8 | 10.2 | 10.4 | 9.9 |
| generation_wind_onshore | 71.2 | 89.3 | 119.0 | 112.6 | 106.8 |
| generation_wind_offshore | 8.2 | 19.1 | 23.5 | 25.7 | 26.2 |
| generation_photovoltaics | 34.7 | 41.2 | 55.5 | 63.1 | 73.8 |
| generation_biomass | 39.8 | 39.5 | 37.3 | 36.2 | 35.9 |
| generation_hydropower | 14.1 | 15.5 | 15.0 | 17.6 | 14.2 |
| generation_other_renewable | 1.8 | 1.5 | 1.2 | 1.1 | 1.0 |
| grid_load | 502.0 | 509.2 | 458.4 | 465.5 | 465.8 |

The twelve sources summed (the header's figure): 502.9 TWh (2015), 545.2 (2018), 453.6 (2023), 437.7 (2024), 437.9 (2025); January to September 2026, 342.4, with a grid load of 346.1. The six renewable sources are 33.8 percent of the twelve in 2015 and 58.9 percent in 2025.

## Reading the source

- The run stops at once, asking nothing, while `smard_germany` or the host www.smard.de is paused.
- One request a run: a POST of `body()`, the thirteen module ids of `MODULES` (twelve sources and the grid load), region DE, resolution month, from 1 January 2015 at 00:00 German time (2014-12-31T23:00:00Z) to the moment of the run; timeout 120 seconds; tried once. An answer other than HTTP 200, or one that is not a zip, stops the run. The POST is saved by the connector itself, not by the raw capture.
- `--offline` reads the saved zip and its `.json`, and stops if the zip is missing.
- A zip without exactly one generation and one consumption file, a header not beginning "Start date;End date", a column not "<name> [MWh] Calculated resolutions", a Start date not of the form "Jan 1, 2015" or not the first of a month, a value that is not a number once its thousands commas are dropped, no month at all, or a month given twice stops the run; no file is written. A cell "-" or blank has no row; nothing is filled.
- The code counts no row ceiling.

## License

Public. `license_verdicts.csv` records the Bundesnetzagentur (SMARD), read 368 (session 2229): "may be public", for public and for commercial use. The sentence, on SMARD's Data use page: "Data from the section Market data visuals, which can be downloaded showing longer periods of time from the Download section, is licensed under a Creative Commons Attribution 4.0 International Licence." The header carries the attribution "Bundesnetzagentur | SMARD.de". `sources.csv` flags `smard:market_data_month` public; `license_tables.csv` lists the table under the Bundesnetzagentur (SMARD).

## Cross-checks (session 2233)

- The written table and session 2230's trial copy hold the same 1,800 keys with every column equal, so the session's results (`runs/c099/s2230/cross.out`, full years 2016 to 2025) hold for the written rows:
  - the twelve sources summed (pumped storage among them, as SMARD gives it) over Eurostat's net production TOTAL for Germany (`eurostat_electricity_monthly`): 0.894 (2017) to 0.995 (2020 and 2023);
  - grid load over `owid_ember_electricity_annual`'s German demand: 0.853 (2016) to 0.901 (2021).
  - Both are steady and below. The table is SMARD's measure, the operators' figures through ENTSO-E, not a national total; the gaps are not explained here.
- The "-" cells were counted in the saved zip; the counts and sums above were computed from the rows, read past the header lines.
- The connector's docstring, the table's header and session 2230's report were read against the code and the rows; no claim of theirs was found contradicted.

## What it does not hold

- Months before January 2015, and any resolution but the month.
- Any SMARD module but the thirteen of `MODULES`: no price, capacity, cross-border flow or forecast is asked.
- Nuclear after December 2023, which SMARD marks "-".
- A national total: the figures are SMARD's, beside Eurostat's in `eurostat_electricity_monthly`, not reconciled to them.
