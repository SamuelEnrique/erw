# Norway's electricity balance, a month (Statistics Norway table 14091)

Energy Research Warehouse (ERW), method note written in session 2233 (chain 099) for a table first written on 24 October 2026 (session 2227).

Tables: `ssb_norway_electricity_monthly`

## Publisher and address

Statistics Norway (SSB), table 14091, "Electricity balance (MWh), by production and consumption, contents and month" (`https://www.ssb.no/en/statbank/table/14091`), through SSB's PxWeb API (no key): the table's metadata by GET and one JSON query by POST, both at `https://data.ssb.no/api/v0/en/table/14091`. Source id `ssb:14091`. Connector: `warehouse/connectors/ssb_electricity.py` (session 2227). The chain file named table 08307; SSB's monthly tables 08583 and 12824 are closed series (2010 to 2019 and 2010 to 2023), and SSB's table search led to 14091, the current one (session 2227's report). data.ssb.no/robots.txt redirects to SSB's API page, www.ssb.no/api; www.ssb.no's robots file disallows /a/kostra/stt only.

## Vintage and revision

January 1993 to September 2026, written by run `20261024T023926Z` (24 October 2026), which read the saved metadata and answer (its log). The query was answered at 2026-10-24T02:25:07Z (`retrieved_at` in every row); `vintage` is SSB's "updated" in the answer, 2026-10-19T06:00:00Z, in every row. The header's "Retrieved: 20261024T023926Z" is the write's run id; it also states the answer's time.

Every run that is not `--offline` asks for the metadata and the whole table again, saves both over `warehouse/raw/ssb_electricity/query_14091.json`, and writes the table again (`write_snapshot`): SSB's revisions replace the rows held.

## Shape and variables

Series, 5,550 rows: 26 lines over 405 months; 4,980 of the answer's 10,530 cells are empty (SSB's ".." in each) and have no row. `entity` ssb:norway; `variable` the line's English name in snake case; `node` the name as SSB writes it; `unit` MWh, as SSB gives it; `ts_utc` the month's first day; `freq` P1M; `geo` NO; `market` blank; extra column `x_code`, SSB's code for the line (1, 1.1 to 1.4, 2 to 7, 7.1 to 7.4, 7.21 to 7.25, 7.231 to 7.234, 7.41 and 7.42; the connector's docstring, line 17, writes "1, 1.1, ..., 7.41", but the last code is 7.42, cottages and holiday houses). Totals are SSB's lines, never sums made here. No value is 0 or negative.

The lines' spans: from January 1993 (405 months) total, hydro and thermal generation, import, export, gross consumption, pump storage consumption, and consumption in power intensive manufacturing; wind from January 1999 (333); the four power intensive industries (pulp and paper, industrial chemicals, iron, steel and ferro alloys, aluminium and other metals) and the extraction of crude petroleum and natural gas from January 2010 (201); solar, grid loss and statistical difference, net consumption, the primary, secondary and tertiary industries, mining, other manufacturing, electricity supply and construction, households, dwellings, and cottages and holiday houses from January 2020 (81).

TWh a year (the twelve months summed here for this note):

| Line (`x_code`) | 1993 | 2010 | 2025 |
|---|---|---|---|
| total_electricity_generation (1) | 120.00 | 124.45 | 161.79 |
| hydro_power_generation (1.1) | 119.51 | 117.94 | 145.47 |
| wind_power_generation (1.2) | | 0.89 | 13.90 |
| solar_power_generation (1.3) | | | 0.35 |
| thermal_power_generation (1.4) | 0.49 | 5.61 | 2.07 |
| import (2) | 0.59 | 14.67 | 11.51 |
| export (3) | 8.38 | 7.12 | 34.31 |
| gross_electricity_consumption (4) | 112.22 | 132.00 | 138.99 |
| pump_storage_consumption (5) | 1.46 | 1.19 | 1.40 |
| grid_loss_and_statistical_difference (6) | | | 7.53 |
| net_electricity_consumption (7) | | | 130.07 |
| consumption_in_power_intensive_manufacturing (7.23) | 28.33 | 34.63 | 37.41 |
| consumption_in_households (7.4) | | | 40.41 |

January to September 2026: total generation 108.63 TWh.

## Reading the source

- The run stops at once, asking nothing, while `ssb_electricity` or the host data.ssb.no is paused.
- Two requests a run. The metadata GET is fetched fresh (timeout 60 seconds, 1 second's pause after it); HTTP 404 stops the run and any other failure is tried up to `RETRIES` (4) times, 5, 10 and 15 seconds apart. The metadata must have exactly the three variables Produk2, ContentsCode and Tid, else the run stops. The POST asks for every value of all three (timeout 180 seconds); it is tried once, and an answer other than HTTP 200 stops the run.
- `--offline` reads `query_14091.json` (the metadata, the query, the answer and its time) and stops if it is missing.
- An answer without the columns Produk2 and Tid or without data, a month not of the form YYYYMmm, a line code not in the metadata, a value that is not a number, an answer with no value, or a line and month given twice stops the run; no file is written. A cell of ".", "..", "...", ":", "-" or blank is counted empty and has no row; a 0 SSB gives would be kept. Nothing is filled.
- The code counts no row ceiling.

## License

Public. `license_verdicts.csv` records Statistics Norway, read 365 (session 2229): "may be public", for public and for commercial use. The sentence, on SSB's API page: "I likhet med resten av ssb.no benytter API-ene lisensen CC BY 4.0" (like the rest of ssb.no, the APIs use the CC BY 4.0 license). The header cites "Statistics Norway, table 14091". `sources.csv` flags `ssb:14091` public; `license_tables.csv` lists the table under Statistics Norway.

## Cross-checks (session 2233)

- The written table and session 2227's trial copy hold the same 5,550 keys with every column equal, so the session's results (`runs/c099/s2227/cross.out`, full years 2016 to 2025) hold for the written rows:
  - against `eurostat_electricity_monthly` (Norway): total generation over Eurostat's net production TOTAL 1.0290 in 2016 (149.53 against 145.32 TWh) and 0.9999 to 1.0005 from 2017; imports 0.9982 to 1.0019 in every year; exports 1.0248 in 2016 and 1.0000 from 2017;
  - gross consumption over `owid_ember_electricity_annual`'s demand: 0.9991 to 1.0114.
- Computed from the rows here: total generation equals hydro, wind, solar and thermal generation within 1 MWh in all 405 months; gross consumption equals total generation plus import less export exactly in all 405; gross consumption less pump storage, grid loss and net consumption is within 1 MWh in the 81 months from 2020.

## What it does not hold

- Months before January 1993; SSB's closed tables 08583 and 12824, and table 08307.
- The consumption lines before 2010 or 2020, where SSB leaves the cells empty; net consumption and grid loss before 2020.
- Prices, capacity, and Norway's bidding zones: the table is national.
